"""Run a reproducible single-case pool boiling demo analysis.

This script captures the lightweight, non-interactive path used for the
Boiling-417 demo. It reads the raw LVM files, computes the notebook's core
temperature/pressure/heat-flux metrics, and writes summary files plus a few
representative plots.
"""

from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyXSteam.XSteam import XSteam
from scipy.signal import correlate, correlation_lags, detrend, find_peaks, get_window, spectrogram, welch
import matplotlib.ticker as mticker


TC_LOCATION_M = np.array([0, 2.54, 5.08, 7.62]) * 1e-3
SURFACE_LOCATION_FLAT_CU_M = 13.1826e-3
CU_THERMAL_CONDUCTIVITY_W_MK = 392
LVM_SKIP_ROWS = 22


def read_lvm(folder: Path, filename: str) -> pd.DataFrame:
    return pd.read_csv(folder / filename, skiprows=LVM_SKIP_ROWS, sep="\t")


def parse_lvm_start_time_seconds(path: Path) -> float:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line_number == 11:
                token = re.split(r"\s+", line.strip(), maxsplit=1)[1]
                if "." in token:
                    hhmmss, frac = token.split(".", 1)
                    token = f"{hhmmss}.{frac[:6]}"
                hour, minute, second = token.split(":")
                return int(hour) * 3600 + int(minute) * 60 + float(second)
    raise ValueError(f"Could not read start time from {path}")


def first_max_index(values: np.ndarray, candidate_indices: np.ndarray, time: np.ndarray) -> int:
    segment = values[candidate_indices]
    candidates = candidate_indices[np.where(segment == np.nanmax(segment))[0]]
    return int(candidates[np.argmin(time[candidates])])


def top2_with_gap(
    time_s: np.ndarray,
    heat_flux: np.ndarray,
    chf_t_start: float = 50.0,
    chf_t_end: float = 100.0,
    gap_s: float = 200.0,
) -> tuple[int, int]:
    finite = np.isfinite(time_s) & np.isfinite(heat_flux)
    chf_candidates = np.where(finite & (time_s >= chf_t_start) & (time_s <= chf_t_end))[0]
    if chf_candidates.size == 0:
        raise ValueError("No data points found inside the CHF marker search window.")

    chf_idx = first_max_index(heat_flux, chf_candidates, time_s)
    nbr_candidates = np.where(finite & (time_s >= time_s[chf_idx] + gap_s))[0]
    if nbr_candidates.size == 0:
        raise ValueError("No data points found after CHF marker + gap.")

    nbr_idx = first_max_index(heat_flux, nbr_candidates, time_s)
    return chf_idx, nbr_idx


def detect_dnb_time(
    time_s: np.ndarray,
    heat_flux: np.ndarray,
    search_end_s: float,
    drop_window_s: float = 5.0,
) -> tuple[int, int]:
    return detect_heat_flux_drop_peak_time(
        time_s,
        heat_flux,
        search_start_s=0.0,
        search_end_s=search_end_s,
        drop_window_s=drop_window_s,
    )


def detect_heat_flux_drop_peak_time(
    time_s: np.ndarray,
    heat_flux: np.ndarray,
    search_start_s: float,
    search_end_s: float,
    drop_window_s: float = 5.0,
) -> tuple[int, int]:
    finite = np.isfinite(time_s) & np.isfinite(heat_flux)
    if np.sum(finite) < 3:
        raise ValueError("Need at least three finite heat-flux samples for drop detection.")

    sample_spacing_s = float(np.nanmedian(np.diff(time_s[finite])))
    drop_points = max(1, int(round(drop_window_s / sample_spacing_s)))
    if len(time_s) <= drop_points:
        raise ValueError("Drop detection window is longer than the heat-flux series.")

    delta_q = heat_flux[drop_points:] - heat_flux[:-drop_points]
    drop_start_time = time_s[:-drop_points]
    drop_candidates = np.where(
        finite[:-drop_points]
        & finite[drop_points:]
        & (drop_start_time >= search_start_s)
        & (drop_start_time <= search_end_s)
    )[0]
    if drop_candidates.size == 0:
        raise ValueError("No heat-flux samples found inside the drop search window.")

    drop_start_idx = int(drop_candidates[np.nanargmin(delta_q[drop_candidates])])
    pre_drop_candidates = np.where(
        finite & (time_s >= search_start_s) & (time_s <= time_s[drop_start_idx])
    )[0]
    if pre_drop_candidates.size == 0:
        raise ValueError("No heat-flux samples found before the sudden heat-flux drop.")

    peak_idx = first_max_index(heat_flux, pre_drop_candidates, time_s)
    return peak_idx, drop_start_idx


def detect_wall_temperature_peak_time(
    time_s: np.ndarray,
    surface_temperature: np.ndarray,
    search_start_s: float,
    search_end_s: float,
) -> int:
    finite = np.isfinite(time_s) & np.isfinite(surface_temperature)
    candidates = np.where(
        finite & (time_s >= search_start_s) & (time_s <= search_end_s)
    )[0]
    if candidates.size == 0:
        raise ValueError("No wall-temperature samples found inside the peak search window.")
    return first_max_index(surface_temperature, candidates, time_s)


def compute_temperature_quantities(temp: pd.DataFrame) -> dict[str, np.ndarray]:
    time_s = temp["Time (sec)"].to_numpy(dtype=float)
    thermocouples = np.column_stack(
        [
            temp["Thermo-couple_1"].to_numpy(dtype=float),
            temp["Thermo-couple_2"].to_numpy(dtype=float),
            temp["Thermo-couple_3"].to_numpy(dtype=float),
            temp["Thermo-couple_4"].to_numpy(dtype=float),
        ]
    )

    n_tc = len(TC_LOCATION_M)
    slope_denominator = n_tc * np.sum(TC_LOCATION_M**2) - np.sum(TC_LOCATION_M) ** 2
    slope_numerator = (
        n_tc * np.sum(thermocouples * TC_LOCATION_M, axis=1)
        - np.sum(TC_LOCATION_M) * np.sum(thermocouples, axis=1)
    )
    slope = slope_numerator / slope_denominator
    intercept = (np.sum(thermocouples, axis=1) - slope * np.sum(TC_LOCATION_M)) / n_tc
    heat_flux = -CU_THERMAL_CONDUCTIVITY_W_MK * slope / 1e4
    surface_temperature = slope * SURFACE_LOCATION_FLAT_CU_M + intercept

    predicted = slope[:, None] * TC_LOCATION_M + intercept[:, None]
    measured_mean = np.mean(thermocouples, axis=1, keepdims=True)
    r2 = 1 - np.sum((thermocouples - predicted) ** 2, axis=1) / np.sum(
        (thermocouples - measured_mean) ** 2, axis=1
    )

    return {
        "time_s": time_s,
        "thermocouples": thermocouples,
        "heat_flux": heat_flux,
        "surface_temperature": surface_temperature,
        "r2": r2,
    }


def save_line_plot(path: Path, x, y, title: str, xlabel: str, ylabel: str, color: str) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(x, y, color=color, linewidth=2.2, linestyle="-")
    ax.set_title(title)
    ax.set_xlabel(xlabel, fontsize=18, fontname="Arial")
    ax.set_ylabel(ylabel, fontsize=18, fontname="Arial")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.tick_params(axis="both", which="major", labelsize=15, direction="in", top=True, right=True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Arial")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def add_event_markers(
    ax: plt.Axes,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> None:
    ymin, ymax = ax.get_ylim()
    lower_label_y = ymin + 0.06 * (ymax - ymin)
    peak_label_y = ymin + 0.18 * (ymax - ymin)
    if dnb_time_s is not None:
        ax.axvline(dnb_time_s, color="black", linestyle="--", linewidth=1.3)
        ax.text(
            dnb_time_s,
            lower_label_y,
            r"$t_{\mathrm{DNB}}$",
            rotation=90,
            va="bottom",
            ha="right",
            fontsize=13,
            fontname="Arial",
            color="black",
        )
    if peak_time_s is not None:
        ax.axvline(peak_time_s, color="tab:red", linestyle=":", linewidth=1.5)
        ax.text(
            peak_time_s,
            peak_label_y,
            r"$t_{\mathrm{peak}}$",
            rotation=90,
            va="bottom",
            ha="right",
            fontsize=13,
            fontname="Arial",
            color="tab:red",
        )
    if off_time_s is not None:
        ax.axvline(off_time_s, color="0.35", linestyle="--", linewidth=1.3)
        ax.text(
            off_time_s,
            lower_label_y,
            r"$t_{\mathrm{off}}$",
            rotation=90,
            va="bottom",
            ha="right",
            fontsize=13,
            fontname="Arial",
            color="0.35",
        )


def save_temperature_profile_plot(
    path: Path,
    time_s: np.ndarray,
    thermocouples: np.ndarray,
    surface_temperature: np.ndarray,
    title: str,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    linewidth = 1.6
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    for index, color in enumerate(colors):
        ax.plot(
            time_s,
            thermocouples[:, index],
            color=color,
            linewidth=linewidth,
            linestyle="-",
            label=rf"$T_{{\mathrm{{TC{index + 1}}}}}$",
        )
    ax.plot(
        time_s,
        surface_temperature,
        color="tab:purple",
        linewidth=linewidth,
        linestyle="-",
        label=r"$T_{\mathrm{w}}$",
    )
    ax.set_xlim(0, float(time_s[-1]))
    ax.set_title(title)
    ax.set_xlabel("Time, $t$ (s)", fontsize=18, fontname="Arial")
    ax.set_ylabel("Temperature, $T$ ($^\\circ$C)", fontsize=18, fontname="Arial")
    ax.grid(True, linestyle="--", alpha=0.4)
    add_event_markers(ax, dnb_time_s=dnb_time_s, peak_time_s=peak_time_s, off_time_s=off_time_s)
    ax.tick_params(axis="both", which="major", labelsize=15, direction="in", top=True, right=True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Arial")
    ax.legend(frameon=False, fontsize=13, ncol=1, loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_heat_flux_power_plot(
    path: Path,
    time_s: np.ndarray,
    heat_flux: np.ndarray,
    dc_time_s: np.ndarray | None,
    power_w: np.ndarray | None,
    title: str,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> None:
    fig, ax_heat_flux = plt.subplots(figsize=(14, 6))
    linewidth = 1.6
    heat_flux_line = ax_heat_flux.plot(
        time_s,
        heat_flux,
        color="tab:red",
        linewidth=linewidth,
        linestyle="-",
        label=r"$q''$",
    )
    ax_heat_flux.set_xlim(0, float(time_s[-1]))
    ax_heat_flux.set_title(title)
    ax_heat_flux.set_xlabel("Time, $t$ (s)", fontsize=18, fontname="Arial")
    ax_heat_flux.set_ylabel("Heat flux, $q''$ (W/cm$^2$)", fontsize=18, fontname="Arial")
    ax_heat_flux.grid(True, linestyle="--", alpha=0.4)
    add_event_markers(
        ax_heat_flux,
        dnb_time_s=dnb_time_s,
        peak_time_s=peak_time_s,
        off_time_s=off_time_s,
    )
    ax_heat_flux.tick_params(
        axis="both",
        which="major",
        labelsize=15,
        direction="in",
        top=True,
    )

    lines = heat_flux_line
    if dc_time_s is not None and power_w is not None:
        ax_power = ax_heat_flux.twinx()
        power_line = ax_power.plot(
            dc_time_s,
            power_w,
            color="tab:blue",
            linewidth=linewidth,
            linestyle="-",
            label=r"$P_{\mathrm{load}}$",
        )
        ax_power.set_ylabel(
            "Power load, $P_{\\mathrm{load}}$ (W)",
            fontsize=18,
            fontname="Arial",
        )
        ax_power.tick_params(
            axis="y",
            which="major",
            labelsize=15,
            direction="in",
            right=True,
        )
        ax_power.set_xlim(0, float(time_s[-1]))
        for label in ax_power.get_yticklabels():
            label.set_fontname("Arial")
        lines += power_line

    for label in ax_heat_flux.get_xticklabels() + ax_heat_flux.get_yticklabels():
        label.set_fontname("Arial")
    ax_heat_flux.legend(
        lines,
        [line.get_label() for line in lines],
        frameon=False,
        fontsize=13,
        loc="upper right",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def integrate_band_power(
    frequencies: np.ndarray,
    times: np.ndarray,
    psd: np.ndarray,
    band_min_hz: float,
    band_max_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    band_mask = (frequencies >= band_min_hz) & (frequencies <= band_max_hz)
    if not np.any(band_mask):
        raise ValueError(
            f"No PSD frequency bins found between {band_min_hz:g} and {band_max_hz:g} Hz"
        )

    band_integrated_power = np.trapezoid(psd[band_mask, :], frequencies[band_mask], axis=0)
    band_integrated_power_db = 10 * np.log10(band_integrated_power + np.finfo(float).tiny)
    if len(times) != len(band_integrated_power):
        raise ValueError("PSD time axis length does not match integrated power length.")
    return band_integrated_power, band_integrated_power_db


def characteristic_frequencies(
    frequencies: np.ndarray,
    psd: np.ndarray,
    band_min_hz: float,
    band_max_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    band_mask = (frequencies > 0) & (frequencies >= band_min_hz) & (frequencies <= band_max_hz)
    if not np.any(band_mask):
        raise ValueError(
            f"No PSD frequency bins found between {band_min_hz:g} and {band_max_hz:g} Hz"
        )

    band_frequencies = frequencies[band_mask]
    band_psd = psd[band_mask, :]
    spectral_power = np.sum(band_psd, axis=0)
    valid = spectral_power > 0

    peak_frequency = np.full(band_psd.shape[1], np.nan)
    centroid_frequency = np.full(band_psd.shape[1], np.nan)
    bandwidth = np.full(band_psd.shape[1], np.nan)

    if np.any(valid):
        peak_indices = np.nanargmax(band_psd[:, valid], axis=0)
        peak_frequency[valid] = band_frequencies[peak_indices]
        centroid_frequency[valid] = (
            np.sum(band_frequencies[:, None] * band_psd[:, valid], axis=0)
            / spectral_power[valid]
        )
        variance = (
            np.sum(
                ((band_frequencies[:, None] - centroid_frequency[valid]) ** 2)
                * band_psd[:, valid],
                axis=0,
            )
            / spectral_power[valid]
        )
        bandwidth[valid] = np.sqrt(variance)

    return peak_frequency, centroid_frequency, bandwidth


def save_characteristic_frequency_analysis(
    prefix: str,
    times: np.ndarray,
    frequencies: np.ndarray,
    psd: np.ndarray,
    output_dir: Path,
    plots_dir: Path,
    band_min_hz: float,
    band_max_hz: float,
    color: str,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> dict[str, object]:
    peak_frequency, centroid_frequency, bandwidth = characteristic_frequencies(
        frequencies,
        psd,
        band_min_hz=band_min_hz,
        band_max_hz=band_max_hz,
    )

    pd.DataFrame(
        {
            "Time (s)": times,
            "Peak frequency (Hz)": peak_frequency,
            "Spectral centroid (Hz)": centroid_frequency,
            "Spectral bandwidth (Hz)": bandwidth,
        }
    ).to_csv(output_dir / f"{prefix}_characteristic_frequencies.csv", index=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times, peak_frequency / 1e3, color=color, linewidth=1.2, alpha=0.7, label="Peak")
    ax.plot(
        times,
        centroid_frequency / 1e3,
        color="black",
        linewidth=1.8,
        alpha=0.9,
        label="Centroid",
    )
    ax.set_xlim(times[0], times[-1])
    ax.set_xlabel("Time, $t$ (s)", fontsize=20, fontname="Arial")
    ax.set_ylabel("Frequency, $f$ (kHz)", fontsize=20, fontname="Arial")
    ax.grid(True, linestyle="--", alpha=0.4)
    add_event_markers(ax, dnb_time_s=dnb_time_s, peak_time_s=peak_time_s, off_time_s=off_time_s)
    ax.legend(frameon=False, fontsize=15)
    ax.tick_params(axis="both", which="major", labelsize=16, direction="in", top=True, right=True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Arial")
    fig.subplots_adjust(left=0.13, bottom=0.18, right=0.98, top=0.95)
    fig.savefig(plots_dir / f"{prefix}_characteristic_frequencies.png", dpi=180)
    plt.close(fig)

    return {
        f"{prefix}_characteristic_band_min_Hz": float(band_min_hz),
        f"{prefix}_characteristic_band_max_Hz": float(band_max_hz),
        f"{prefix}_median_peak_frequency_Hz": float(np.nanmedian(peak_frequency)),
        f"{prefix}_median_spectral_centroid_Hz": float(np.nanmedian(centroid_frequency)),
        f"{prefix}_median_spectral_bandwidth_Hz": float(np.nanmedian(bandwidth)),
    }


def power_centroid_alignment(
    time_s: np.ndarray,
    power_db: np.ndarray,
    centroid_hz: np.ndarray,
    window_start_s: float,
    window_end_s: float,
    max_lag_s: float = 30.0,
) -> dict[str, float | int]:
    mask = (
        (time_s >= window_start_s)
        & (time_s <= window_end_s)
        & np.isfinite(time_s)
        & np.isfinite(power_db)
        & np.isfinite(centroid_hz)
    )
    selected_time = time_s[mask]
    selected_power = power_db[mask]
    selected_centroid = centroid_hz[mask]
    if len(selected_time) < 8:
        raise ValueError(
            f"Need at least 8 samples between {window_start_s:g} and {window_end_s:g} s "
            "for power-centroid alignment analysis."
        )

    sample_spacing_s = float(np.median(np.diff(selected_time)))
    power_signal = detrend(selected_power - np.nanmean(selected_power), type="linear")
    centroid_signal = detrend(selected_centroid - np.nanmean(selected_centroid), type="linear")
    power_std = float(np.nanstd(power_signal))
    centroid_std = float(np.nanstd(centroid_signal))
    if power_std == 0 or centroid_std == 0:
        raise ValueError("Power and centroid signals must vary for alignment analysis.")

    power_z = (power_signal - np.nanmean(power_signal)) / power_std
    centroid_z = (centroid_signal - np.nanmean(centroid_signal)) / centroid_std
    zero_lag_correlation = float(np.nanmean(power_z * centroid_z))

    cross_correlation = correlate(centroid_z, power_z, mode="full") / len(power_z)
    lags_s = correlation_lags(len(centroid_z), len(power_z), mode="full") * sample_spacing_s
    lag_mask = np.abs(lags_s) <= max_lag_s
    best_index = int(np.nanargmax(np.abs(cross_correlation[lag_mask])))
    best_lag_s = float(lags_s[lag_mask][best_index])
    best_correlation = float(cross_correlation[lag_mask][best_index])

    min_peak_spacing_samples = max(1, int(round(8.0 / sample_spacing_s)))
    power_peak_indices, _ = find_peaks(
        power_z,
        distance=min_peak_spacing_samples,
        prominence=0.5,
    )
    power_valley_indices, _ = find_peaks(
        -power_z,
        distance=min_peak_spacing_samples,
        prominence=0.5,
    )

    return {
        "samples": int(len(selected_time)),
        "zero_lag_correlation": zero_lag_correlation,
        "best_correlation": best_correlation,
        "best_lag_s": best_lag_s,
        "mean_centroid_z_at_power_peaks": float(np.nanmean(centroid_z[power_peak_indices]))
        if len(power_peak_indices)
        else float("nan"),
        "mean_centroid_z_at_power_valleys": float(np.nanmean(centroid_z[power_valley_indices]))
        if len(power_valley_indices)
        else float("nan"),
        "power_peak_count": int(len(power_peak_indices)),
        "power_valley_count": int(len(power_valley_indices)),
    }


def save_power_centroid_overlay(
    prefix: str,
    time_s: np.ndarray,
    power_db: np.ndarray,
    centroid_hz: np.ndarray,
    plots_dir: Path,
    window_start_s: float,
    window_end_s: float,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> dict[str, object]:
    mask = (
        (time_s >= window_start_s)
        & (time_s <= window_end_s)
        & np.isfinite(power_db)
        & np.isfinite(centroid_hz)
    )
    selected_time = time_s[mask]
    selected_power_db = power_db[mask]
    selected_centroid_khz = centroid_hz[mask] / 1e3
    if len(selected_time) < 2:
        raise ValueError("Need at least 2 samples for power-centroid overlay plot.")

    fig, ax_power = plt.subplots(figsize=(12, 6))
    ax_centroid = ax_power.twinx()
    power_line = ax_power.plot(
        selected_time,
        selected_power_db,
        color="tab:blue",
        linewidth=1.6,
        label="Band-integrated power",
    )
    centroid_line = ax_centroid.plot(
        selected_time,
        selected_centroid_khz,
        color="black",
        linewidth=1.8,
        label="Spectral centroid",
    )
    ax_power.set_xlim(window_start_s, window_end_s)
    ax_power.set_xlabel("Time, $t$ (s)", fontsize=20, fontname="Arial")
    ax_power.set_ylabel("Band-integrated power (dB re V$^2$)", fontsize=18, fontname="Arial")
    ax_centroid.set_ylabel("Spectral centroid, $f_c$ (kHz)", fontsize=18, fontname="Arial")
    ax_power.grid(True, linestyle="--", alpha=0.35)
    add_event_markers(
        ax_power,
        dnb_time_s=dnb_time_s,
        peak_time_s=peak_time_s,
        off_time_s=off_time_s,
    )
    ax_power.tick_params(axis="both", which="major", labelsize=15, direction="in", top=True)
    ax_centroid.tick_params(axis="y", which="major", labelsize=15, direction="in", right=True)
    for label in (
        ax_power.get_xticklabels()
        + ax_power.get_yticklabels()
        + ax_centroid.get_yticklabels()
    ):
        label.set_fontname("Arial")
    lines = power_line + centroid_line
    ax_power.legend(
        lines,
        [line.get_label() for line in lines],
        loc="lower left",
        frameon=False,
        fontsize=14,
    )
    fig.subplots_adjust(left=0.14, bottom=0.17, right=0.86, top=0.96)
    fig.savefig(plots_dir / f"{prefix}_power_centroid_overlay.png", dpi=180)
    plt.close(fig)

    alignment = power_centroid_alignment(
        time_s,
        power_db,
        centroid_hz,
        window_start_s=window_start_s,
        window_end_s=window_end_s,
    )
    return {
        f"{prefix}_power_centroid_window_start_s": float(window_start_s),
        f"{prefix}_power_centroid_window_end_s": float(window_end_s),
        f"{prefix}_power_centroid_samples": alignment["samples"],
        f"{prefix}_power_centroid_zero_lag_correlation": alignment["zero_lag_correlation"],
        f"{prefix}_power_centroid_best_correlation": alignment["best_correlation"],
        f"{prefix}_power_centroid_best_lag_s": alignment["best_lag_s"],
        f"{prefix}_mean_centroid_z_at_power_peaks": alignment[
            "mean_centroid_z_at_power_peaks"
        ],
        f"{prefix}_mean_centroid_z_at_power_valleys": alignment[
            "mean_centroid_z_at_power_valleys"
        ],
        f"{prefix}_power_peak_count": alignment["power_peak_count"],
        f"{prefix}_power_valley_count": alignment["power_valley_count"],
    }


def band_power_oscillation_spectrum(
    time_s: np.ndarray,
    power_db: np.ndarray,
    window_start_s: float,
    window_end_s: float,
    max_frequency_hz: float,
) -> tuple[np.ndarray, np.ndarray, float, float, int]:
    mask = (
        (time_s >= window_start_s)
        & (time_s <= window_end_s)
        & np.isfinite(time_s)
        & np.isfinite(power_db)
    )
    selected_time = time_s[mask]
    selected_power = power_db[mask]
    if len(selected_time) < 8:
        raise ValueError(
            f"Need at least 8 samples between {window_start_s:g} and {window_end_s:g} s "
            "for oscillation analysis."
        )

    sample_spacing_s = float(np.median(np.diff(selected_time)))
    sampling_frequency_hz = 1.0 / sample_spacing_s
    y = detrend(selected_power - np.nanmean(selected_power), type="linear")
    nperseg = min(len(y), max(64, int(round(len(y) / 2))))
    frequencies, psd = welch(
        y,
        fs=sampling_frequency_hz,
        window="hann",
        nperseg=nperseg,
        noverlap=nperseg // 2,
        scaling="density",
    )
    min_frequency_hz = 1.0 / max(selected_time[-1] - selected_time[0], sample_spacing_s)
    frequency_mask = (frequencies >= min_frequency_hz) & (frequencies <= max_frequency_hz)
    if not np.any(frequency_mask):
        raise ValueError("No oscillation frequency bins found in the requested range.")

    plot_frequencies = frequencies[frequency_mask]
    plot_psd = psd[frequency_mask]
    dominant_index = int(np.nanargmax(plot_psd))
    dominant_frequency_hz = float(plot_frequencies[dominant_index])
    dominant_period_s = float(1.0 / dominant_frequency_hz)
    return plot_frequencies, plot_psd, dominant_frequency_hz, dominant_period_s, len(selected_time)


def save_band_power_oscillation_analysis(
    prefix: str,
    label: str,
    time_s: np.ndarray,
    power_db: np.ndarray,
    output_dir: Path,
    plots_dir: Path,
    window_start_s: float,
    window_end_s: float,
    max_frequency_hz: float,
) -> dict[str, object]:
    frequencies, psd, dominant_frequency_hz, dominant_period_s, n_samples = (
        band_power_oscillation_spectrum(
            time_s,
            power_db,
            window_start_s=window_start_s,
            window_end_s=window_end_s,
            max_frequency_hz=max_frequency_hz,
        )
    )

    pd.DataFrame(
        {
            "Frequency (Hz)": frequencies,
            "PSD of band-integrated power (dB^2/Hz)": psd,
            "Period (s)": 1.0 / frequencies,
        }
    ).to_csv(output_dir / f"{prefix}_band_power_oscillation_spectrum.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(frequencies, psd, color="tab:purple", linewidth=1.8)
    ax.axvline(dominant_frequency_hz, color="tab:red", linestyle="--", linewidth=1.4)
    ax.set_xlabel("Oscillation frequency (Hz)", fontsize=18, fontname="Arial")
    ax.set_ylabel("PSD of band-integrated power (dB$^2$/Hz)", fontsize=18, fontname="Arial")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.tick_params(axis="both", which="major", labelsize=14, direction="in", top=True, right=True)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontname("Arial")
    fig.subplots_adjust(left=0.15, bottom=0.17, right=0.98, top=0.95)
    fig.savefig(plots_dir / f"{prefix}_band_power_oscillation_spectrum.png", dpi=180)
    plt.close(fig)

    return {
        f"{prefix}_oscillation_window_start_s": float(window_start_s),
        f"{prefix}_oscillation_window_end_s": float(window_end_s),
        f"{prefix}_oscillation_samples": int(n_samples),
        f"{prefix}_dominant_oscillation_frequency_Hz": dominant_frequency_hz,
        f"{prefix}_dominant_oscillation_period_s": dominant_period_s,
        f"{prefix}_oscillation_label": label,
    }


def save_hydrophone_analysis(
    folder: Path,
    plots_dir: Path,
    band_min_hz: float,
    band_max_hz: float,
    oscillation_start_s: float,
    oscillation_end_s: float,
    oscillation_max_frequency_hz: float,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> dict[str, object]:
    path = folder / "Hydrophones.lvm"
    if not path.exists():
        return {"hydrophone_available": False}

    hydrophones = pd.read_csv(
        path,
        skiprows=23,
        header=None,
        names=["Time", "Voltage", "Comment"],
        sep=r"\s+",
        engine="python",
    )[["Time", "Voltage"]]
    hydrophones["Time"] = pd.to_numeric(hydrophones["Time"], errors="coerce")
    hydrophones["Voltage"] = pd.to_numeric(hydrophones["Voltage"], errors="coerce")
    hydrophones = hydrophones.dropna(subset=["Time", "Voltage"])

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(hydrophones["Time"], hydrophones["Voltage"], linewidth=0.8)
    ax.set_xlabel("Time (s)", fontsize=16)
    ax.set_ylabel("Voltage (V)", fontsize=16)
    ax.set_title("Raw Hydrophone Signal vs Time", fontsize=18)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.tick_params(axis="both", labelsize=13, direction="in", top=True, right=True)
    fig.tight_layout()
    fig.savefig(plots_dir / "hydrophone_raw.png", dpi=180)
    plt.close(fig)

    hydro_time = hydrophones["Time"].to_numpy(dtype=float)
    hydro_voltage = hydrophones["Voltage"].to_numpy(dtype=float)
    sampling_frequency = 1 / np.mean(np.diff(hydro_time))
    nperseg = 4096 * 2
    noverlap = nperseg // 2
    frequencies, times, sxx = spectrogram(
        hydro_voltage,
        sampling_frequency,
        scaling="spectrum",
        nperseg=nperseg,
        noverlap=noverlap,
    )
    sxx_log = 10 * np.log10(sxx)
    freq_mask = frequencies <= 6e3
    masked_frequencies = frequencies[freq_mask]
    masked_sxx_log = sxx_log[freq_mask, :]

    fig, ax = plt.subplots(figsize=(16, 7), constrained_layout=True)
    spectrogram_image = ax.imshow(
        masked_sxx_log,
        extent=[times[0], times[-1], masked_frequencies[-1] / 1e3, masked_frequencies[0] / 1e3],
        interpolation="bilinear",
        cmap="viridis",
        aspect="auto",
        vmin=-120,
        vmax=-40,
    )
    ax.invert_yaxis()
    ax.set_ylabel("Frequency, $f$ (kHz)", fontsize=24, fontname="Arial")
    ax.set_xlabel("Time, $t$ (s)", fontsize=24, fontname="Arial")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))
    add_event_markers(ax, dnb_time_s=dnb_time_s, peak_time_s=peak_time_s, off_time_s=off_time_s)
    colorbar = fig.colorbar(spectrogram_image, ax=ax, fraction=0.035, pad=0.03)
    colorbar.set_label("Power (dB)", fontsize=22, fontname="Arial")
    colorbar.ax.tick_params(labelsize=18)
    ax.tick_params(axis="both", which="major", labelsize=20)
    for label in ax.get_xticklabels() + ax.get_yticklabels() + colorbar.ax.get_yticklabels():
        label.set_fontname("Arial")
    fig.savefig(plots_dir / "hydrophone_spectrogram.png", dpi=180)
    plt.close(fig)

    psd_frequencies, psd_times, psd = spectrogram(
        hydro_voltage,
        sampling_frequency,
        scaling="density",
        nperseg=nperseg,
        noverlap=noverlap,
    )
    band_integrated_power, band_integrated_power_db = integrate_band_power(
        psd_frequencies,
        psd_times,
        psd,
        band_min_hz=band_min_hz,
        band_max_hz=band_max_hz,
    )

    band_power_df = pd.DataFrame(
        {
            "Time (s)": psd_times,
            "Band-integrated hydrophone power proxy (V^2)": band_integrated_power,
            "Band-integrated hydrophone power proxy (dB re V^2)": band_integrated_power_db,
        }
    )
    band_power_df.to_csv(plots_dir.parent / "hydrophone_band_integrated_power.csv", index=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(psd_times, band_integrated_power_db, color="tab:blue", linewidth=1.8)
    ax.set_xlim(times[0], times[-1])
    ax.set_xlabel("Time, $t$ (s)", fontsize=20, fontname="Arial")
    ax.set_ylabel("Band-integrated power (dB re V²)", fontsize=20, fontname="Arial")
    ax.grid(True, linestyle="--", alpha=0.4)
    add_event_markers(ax, dnb_time_s=dnb_time_s, peak_time_s=peak_time_s, off_time_s=off_time_s)
    ax.tick_params(axis="both", which="major", labelsize=16, direction="in", top=True, right=True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Arial")
    fig.subplots_adjust(left=0.16, bottom=0.18, right=0.98, top=0.95)
    fig.savefig(plots_dir / "hydrophone_band_integrated_power.png", dpi=180)
    plt.close(fig)

    summary = {
        "hydrophone_available": True,
        "hydrophone_rows": int(len(hydrophones)),
        "hydrophone_sampling_frequency_Hz": float(sampling_frequency),
        "hydrophone_band_min_Hz": float(band_min_hz),
        "hydrophone_band_max_Hz": float(band_max_hz),
        "hydrophone_band_power_time_bins": int(len(psd_times)),
        "hydrophone_band_power_min_V2": float(np.nanmin(band_integrated_power)),
        "hydrophone_band_power_max_V2": float(np.nanmax(band_integrated_power)),
        "hydrophone_band_power_mean_V2": float(np.nanmean(band_integrated_power)),
    }
    summary.update(
        save_characteristic_frequency_analysis(
            "hydrophone",
            psd_times,
            psd_frequencies,
            psd,
            plots_dir.parent,
            plots_dir,
            band_min_hz=band_min_hz,
            band_max_hz=band_max_hz,
            color="tab:blue",
            dnb_time_s=dnb_time_s,
            peak_time_s=peak_time_s,
            off_time_s=off_time_s,
        )
    )
    _, hydrophone_centroid_frequency, _ = characteristic_frequencies(
        psd_frequencies,
        psd,
        band_min_hz=band_min_hz,
        band_max_hz=band_max_hz,
    )
    summary.update(
        save_power_centroid_overlay(
            "hydrophone",
            psd_times,
            band_integrated_power_db,
            hydrophone_centroid_frequency,
            plots_dir,
            window_start_s=oscillation_start_s,
            window_end_s=oscillation_end_s,
            dnb_time_s=dnb_time_s,
            peak_time_s=peak_time_s,
            off_time_s=off_time_s,
        )
    )
    summary.update(
        save_band_power_oscillation_analysis(
            "hydrophone",
            "Hydrophone",
            psd_times,
            band_integrated_power_db,
            plots_dir.parent,
            plots_dir,
            window_start_s=oscillation_start_s,
            window_end_s=oscillation_end_s,
            max_frequency_hz=oscillation_max_frequency_hz,
        )
    )
    return summary


def read_ae_hit(path: Path) -> pd.DataFrame:
    columns = [
        "ID",
        "AE_Hit_Time",
        "PARA1",
        "CH",
        "RISE",
        "COUN",
        "ENER",
        "DURATION",
        "A-FRQ",
        "RMS",
        "PCNTS",
        "THR",
        "R-FRQ",
        "I-FRQ",
        "SIG-STRNGTH",
        "ABS-ENERGY",
        "FRQ-C",
        "P-FRQ",
        "AMP",
        "ASL",
    ]
    return pd.read_csv(path, skiprows=8, header=None, names=columns, sep=r"\s+", engine="python")


def read_ae_time(path: Path) -> pd.DataFrame:
    rows = []
    current_time = None
    current_para1 = None
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            match_main = re.match(r"^\s*\d+\s+([\d.]+)\s+([\d.]+)\s*$", line)
            if match_main:
                current_time = float(match_main.group(1))
                current_para1 = float(match_main.group(2))
                continue
            match_ch = re.match(
                r"^\s*1:\[\s*([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s*\]",
                line,
            )
            if match_ch and current_time is not None:
                rows.append(
                    {
                        "AE_Time": current_time,
                        "PARA1": current_para1,
                        "RMS": float(match_ch.group(1)),
                        "THR": float(match_ch.group(2)),
                        "ABS-ENERGY": float(match_ch.group(3)),
                        "ASL": float(match_ch.group(4)),
                    }
                )
    return pd.DataFrame(rows)


def save_ae_analysis(folder: Path, plots_dir: Path) -> dict[str, object]:
    summary: dict[str, object] = {
        "ae_hit_available": (folder / "AE_Hit.TXT").exists(),
        "ae_time_available": (folder / "AE_Time.TXT").exists(),
    }

    if summary["ae_hit_available"]:
        ae_hit = read_ae_hit(folder / "AE_Hit.TXT")
        plot_columns = [
            "PARA1",
            "RISE",
            "COUN",
            "ENER",
            "DURATION",
            "A-FRQ",
            "RMS",
            "PCNTS",
            "R-FRQ",
            "I-FRQ",
            "SIG-STRNGTH",
            "ABS-ENERGY",
            "FRQ-C",
            "P-FRQ",
            "AMP",
            "ASL",
        ]
        fig, axes = plt.subplots(4, 4, figsize=(20, 16), sharex=False)
        for ax, column in zip(axes.ravel(), plot_columns):
            ax.scatter(ae_hit["AE_Hit_Time"], ae_hit[column], s=0.5, alpha=0.7)
            ax.set_title(f"{column} vs AE_Time", fontsize=12)
            ax.set_xlabel("AE_Time (s)", fontsize=10)
            ax.set_ylabel(column, fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.tick_params(axis="both", labelsize=9)
        fig.suptitle("AE Hit Parameters", fontsize=16, y=1.02)
        fig.tight_layout()
        fig.savefig(plots_dir / "ae_hit_parameters.png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        summary["ae_hit_rows"] = int(len(ae_hit))

    if summary["ae_time_available"]:
        ae_time = read_ae_time(folder / "AE_Time.TXT")
        ae_time = ae_time.dropna(subset=["AE_Time", "PARA1", "RMS", "ABS-ENERGY", "ASL"])
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
        series = [("PARA1", "PARA1"), ("RMS", "RMS"), ("ABS-ENERGY", "ABS-ENERGY"), ("ASL", "ASL")]
        for ax, (column, ylabel) in zip(axes.ravel(), series):
            ax.plot(ae_time["AE_Time"], ae_time[column], linewidth=1)
            ax.set_title(f"{column} vs AE_Time", fontsize=13)
            ax.set_ylabel(ylabel, fontsize=11)
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.tick_params(axis="both", labelsize=10)
        axes[1, 0].set_xlabel("AE_Time (s)", fontsize=11)
        axes[1, 1].set_xlabel("AE_Time (s)", fontsize=11)
        fig.suptitle("AE Time Parameters", fontsize=16, y=1.02)
        fig.tight_layout()
        fig.savefig(plots_dir / "ae_time_parameters.png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        summary["ae_time_rows"] = int(len(ae_time))

    return summary


def find_wfs_file(folder: Path) -> Path | None:
    candidates = sorted(folder.glob("*.wfs")) + sorted(folder.glob("*.WFS"))
    return candidates[0] if candidates else None


def sparse_windowed_spectrogram(
    raw_signal: np.ndarray,
    sampling_frequency: float,
    nperseg: int,
    n_time_bins: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    """Compute a display-oriented spectrogram from very large continuous AE streams."""
    raw_signal = np.asarray(raw_signal, dtype=np.float32)
    n_samples = len(raw_signal)
    if n_samples == 0:
        raise ValueError("AE waveform signal is empty.")

    chunk_size = max(1, n_samples // max(1, n_time_bins))
    nperseg = max(8, min(int(nperseg), chunk_size))
    if nperseg % 2:
        nperseg -= 1
    if nperseg < 8:
        nperseg = min(chunk_size, 8)

    window = get_window("hann", nperseg)
    window_norm = float((window**2).sum() * sampling_frequency)

    n_bins_actual = max(1, (n_samples - nperseg) // chunk_size + 1)
    stride = raw_signal.strides[0]
    segments = np.lib.stride_tricks.as_strided(
        raw_signal,
        shape=(n_bins_actual, nperseg),
        strides=(chunk_size * stride, stride),
        writeable=False,
    )

    windowed = segments * window[np.newaxis, :]
    ffts = np.fft.rfft(windowed, axis=1)
    sxx = (np.abs(ffts) ** 2 / window_norm).T
    frequencies = np.fft.rfftfreq(nperseg, d=1.0 / sampling_frequency)
    times = (np.arange(n_bins_actual) * chunk_size + nperseg / 2) / sampling_frequency
    return frequencies, times, sxx, chunk_size, nperseg


def save_wfs_ae_spectrogram(
    folder: Path,
    plots_dir: Path,
    channel: int,
    max_freq_hz: float,
    band_min_hz: float,
    band_max_hz: float,
    oscillation_start_s: float,
    oscillation_end_s: float,
    oscillation_max_frequency_hz: float,
    vmin_db: float,
    vmax_db: float,
    dnb_time_s: float | None = None,
    peak_time_s: float | None = None,
    off_time_s: float | None = None,
) -> dict[str, object]:
    wfs_path = find_wfs_file(folder)
    if wfs_path is None:
        return {"ae_wfs_available": False}

    try:
        from decode_wfs import decode_wfs, load_continuous
    except ImportError as exc:
        raise ImportError(
            "AE waveform spectrograms require the 'decode-wfs' package. "
            "Install repo dependencies with `python -m pip install -r requirements.txt`."
        ) from exc

    raw, time_s, sampling_rate = load_continuous(wfs_path, channel=channel)
    raw = np.asarray(raw)
    time_s = np.asarray(time_s)
    sampling_rate = float(sampling_rate)

    first_record = decode_wfs(wfs_path, max_records=1).waveforms[0]
    samples_per_record = len(first_record.samples)

    fig_dpi = 150
    fig_width = 16
    fig_height = 7
    px_wide = int(fig_width * fig_dpi)
    px_tall = int(fig_height * fig_dpi)
    nperseg = max(8, samples_per_record * 2)

    frequencies, times, sxx, chunk_size, nperseg_used = sparse_windowed_spectrogram(
        raw,
        sampling_frequency=sampling_rate,
        nperseg=nperseg,
        n_time_bins=px_wide,
    )
    sxx_db = 10 * np.log10(np.maximum(sxx, np.finfo(float).tiny))
    band_integrated_power, band_integrated_power_db = integrate_band_power(
        frequencies,
        times,
        sxx,
        band_min_hz=band_min_hz,
        band_max_hz=band_max_hz,
    )

    band_power_df = pd.DataFrame(
        {
            "Time (s)": times,
            "Band-integrated AE waveform power proxy (V^2)": band_integrated_power,
            "Band-integrated AE waveform power proxy (dB re V^2)": band_integrated_power_db,
        }
    )
    band_power_df.to_csv(plots_dir.parent / "ae_wfs_band_integrated_power.csv", index=False)

    freq_mask = frequencies <= max_freq_hz
    if not np.any(freq_mask):
        raise ValueError(f"No AE waveform frequency bins found below {max_freq_hz:g} Hz.")
    plot_frequencies = frequencies[freq_mask]
    plot_sxx_db = sxx_db[freq_mask, :]

    freq_step = max(1, plot_sxx_db.shape[0] // px_tall)
    plot_sxx_db = plot_sxx_db[::freq_step, :]
    plot_frequencies = plot_frequencies[::freq_step]

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=fig_dpi, constrained_layout=True)
    image = ax.imshow(
        plot_sxx_db,
        extent=[times[0], times[-1], plot_frequencies[-1] / 1e3, plot_frequencies[0] / 1e3],
        interpolation="bilinear",
        cmap="viridis",
        aspect="auto",
        vmin=vmin_db,
        vmax=vmax_db,
    )
    ax.invert_yaxis()
    ax.set_ylabel("Frequency, $f$ (kHz)", fontsize=24, fontname="Arial")
    ax.set_xlabel("Time, $t$ (s)", fontsize=24, fontname="Arial")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, _: f"{value:.1f}"))
    add_event_markers(ax, dnb_time_s=dnb_time_s, peak_time_s=peak_time_s, off_time_s=off_time_s)
    ax.tick_params(axis="both", which="major", labelsize=20)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    colorbar.set_label("Power (dB)", fontsize=22, fontname="Arial")
    colorbar.ax.tick_params(labelsize=18)
    for label in ax.get_xticklabels() + ax.get_yticklabels() + colorbar.ax.get_yticklabels():
        label.set_fontname("Arial")
    fig.savefig(plots_dir / "ae_wfs_spectrogram.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times, band_integrated_power_db, color="tab:green", linewidth=1.8)
    ax.set_xlim(times[0], times[-1])
    ax.set_xlabel("Time, $t$ (s)", fontsize=20, fontname="Arial")
    ax.set_ylabel("Band-integrated power (dB re V$^2$)", fontsize=20, fontname="Arial")
    ax.grid(True, linestyle="--", alpha=0.4)
    add_event_markers(ax, dnb_time_s=dnb_time_s, peak_time_s=peak_time_s, off_time_s=off_time_s)
    ax.tick_params(axis="both", which="major", labelsize=16, direction="in", top=True, right=True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname("Arial")
    fig.subplots_adjust(left=0.16, bottom=0.18, right=0.98, top=0.95)
    fig.savefig(plots_dir / "ae_wfs_band_integrated_power.png", dpi=180)
    plt.close(fig)

    summary = {
        "ae_wfs_available": True,
        "ae_wfs_file": str(wfs_path),
        "ae_wfs_channel": int(channel),
        "ae_wfs_samples": int(len(raw)),
        "ae_wfs_duration_s": float(time_s[-1] - time_s[0]) if len(time_s) else None,
        "ae_wfs_sampling_frequency_Hz": sampling_rate,
        "ae_wfs_samples_per_record": int(samples_per_record),
        "ae_wfs_spectrogram_time_bins": int(len(times)),
        "ae_wfs_spectrogram_frequency_bins": int(len(plot_frequencies)),
        "ae_wfs_spectrogram_chunk_size": int(chunk_size),
        "ae_wfs_spectrogram_nperseg": int(nperseg_used),
        "ae_wfs_spectrogram_max_frequency_Hz": float(max_freq_hz),
        "ae_wfs_band_min_Hz": float(band_min_hz),
        "ae_wfs_band_max_Hz": float(band_max_hz),
        "ae_wfs_band_power_time_bins": int(len(times)),
        "ae_wfs_band_power_min_V2": float(np.nanmin(band_integrated_power)),
        "ae_wfs_band_power_max_V2": float(np.nanmax(band_integrated_power)),
        "ae_wfs_band_power_mean_V2": float(np.nanmean(band_integrated_power)),
    }
    summary.update(
        save_characteristic_frequency_analysis(
            "ae_wfs",
            times,
            frequencies,
            sxx,
            plots_dir.parent,
            plots_dir,
            band_min_hz=band_min_hz,
            band_max_hz=band_max_hz,
            color="tab:green",
            dnb_time_s=dnb_time_s,
            peak_time_s=peak_time_s,
            off_time_s=off_time_s,
        )
    )
    summary.update(
        save_band_power_oscillation_analysis(
            "ae_wfs",
            "AE waveform",
            times,
            band_integrated_power_db,
            plots_dir.parent,
            plots_dir,
            window_start_s=oscillation_start_s,
            window_end_s=oscillation_end_s,
            max_frequency_hz=oscillation_max_frequency_hz,
        )
    )
    return summary


def analyze_case(args: argparse.Namespace) -> dict[str, object]:
    test_id = args.test_id if args.test_id.startswith("Boiling-") else f"Boiling-{args.test_id}"
    folder = Path(args.raw_root) / test_id
    output_dir = Path(args.output_dir)
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    temp = read_lvm(folder, "Temperature.lvm").rename(columns={"X_Value": "Time (sec)"})
    pressure_df = read_lvm(folder, "Pressure.lvm").rename(
        columns={"X_Value": "Time (sec)", "Voltage": "Pressure (kPa)"}
    )

    temp_data = compute_temperature_quantities(temp)
    time_s = temp_data["time_s"]
    heat_flux = temp_data["heat_flux"]
    surface_temperature = temp_data["surface_temperature"]
    r2 = temp_data["r2"]

    pressure = pressure_df["Pressure (kPa)"].to_numpy(dtype=float)
    pressure_mean_kpa = float(
        Decimal(str(np.nanmean(pressure))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )
    t_sat_c = XSteam(XSteam.UNIT_SYSTEM_BARE).tsat_p(pressure_mean_kpa / 1000.0) - 273.15
    htc = heat_flux / (surface_temperature - t_sat_c)

    chf_idx, nbr_idx = top2_with_gap(
        time_s,
        heat_flux,
        chf_t_start=args.chf_marker_start_s,
        chf_t_end=args.chf_marker_end_s,
        gap_s=args.nbr_gap_s,
    )
    dnb_idx, dnb_drop_start_idx = detect_dnb_time(
        time_s,
        heat_flux,
        search_end_s=args.dnb_search_end_s,
        drop_window_s=args.dnb_drop_window_s,
    )
    peak_idx = detect_wall_temperature_peak_time(
        time_s,
        surface_temperature,
        search_start_s=0.0,
        search_end_s=args.dnb_search_end_s,
    )
    dnb_time_s = float(time_s[dnb_idx])
    peak_time_s = float(time_s[peak_idx])
    q_min_idx = int(np.nanargmin(heat_flux[chf_idx : nbr_idx + 1]) + chf_idx)

    summary: dict[str, object] = {
        "test_id": test_id,
        "raw_folder": str(folder),
        "applied_heat_load_W_cm2": args.applied_heat_load,
        "input_subcooling_C": args.subcooling,
        "duration_s": float(np.nanmax(time_s) - np.nanmin(time_s)),
        "pressure_mean_kPa": pressure_mean_kpa,
        "pressure_std_kPa": float(np.nanstd(pressure, ddof=1)),
        "pressure_rmse_vs_target_kPa": float(np.sqrt(np.nanmean((pressure - args.target_pressure) ** 2))),
        "T_sat_C": float(t_sat_c),
        "mean_vapour_temp_C": float(np.nanmean(temp["Vapour Temp"].to_numpy(dtype=float))),
        "mean_liquid_temp_C": float(np.nanmean(temp["Liquid Temp"].to_numpy(dtype=float))),
        "max_surface_temp_C": float(np.nanmax(surface_temperature)),
        "time_at_max_surface_temp_s": float(time_s[np.nanargmax(surface_temperature)]),
        "max_heat_flux_W_cm2": float(np.nanmax(heat_flux)),
        "time_at_max_heat_flux_s": float(time_s[np.nanargmax(heat_flux)]),
        "dnb_time_s": dnb_time_s,
        "dnb_heat_flux_W_cm2": float(heat_flux[dnb_idx]),
        "dnb_drop_start_time_s": float(time_s[dnb_drop_start_idx]),
        "dnb_search_end_s": float(args.dnb_search_end_s),
        "dnb_drop_window_s": float(args.dnb_drop_window_s),
        "peak_time_s": peak_time_s,
        "peak_surface_temp_C": float(surface_temperature[peak_idx]),
        "peak_heat_flux_W_cm2": float(heat_flux[peak_idx]),
        "peak_search_end_s": float(args.dnb_search_end_s),
        "chf_proxy_time_s": float(time_s[chf_idx]),
        "chf_proxy_W_cm2": float(heat_flux[chf_idx]),
        "htc_at_chf_proxy_W_cm2K": float(htc[chf_idx]),
        "nbr_time_s": float(time_s[nbr_idx]),
        "nbr_W_cm2": float(heat_flux[nbr_idx]),
        "q_min_between_chf_nbr_W_cm2": float(heat_flux[q_min_idx]),
        "q_min_time_s": float(time_s[q_min_idx]),
        "mean_R2_linear_fit": float(np.nanmean(r2)),
        "min_R2_linear_fit": float(np.nanmin(r2)),
        "plots_dir": str(plots_dir),
    }

    dc_path = folder / "DC_power.lvm"
    dc_time = None
    power = None
    shut_time = None
    if dc_path.exists():
        dc = read_lvm(folder, "DC_power.lvm")
        dc = dc.rename(
            columns={
                dc.columns[0]: "Time (sec)",
                dc.columns[1]: "Set Voltage (V)",
                dc.columns[2]: "Set Current (A)",
                dc.columns[3]: "Output Voltage (V)",
                dc.columns[4]: "Output Current (A)",
                dc.columns[5]: "Output Power (W)",
            }
        )
        power = dc["Output Power (W)"].to_numpy(dtype=float)
        dc_time = dc["Time (sec)"].to_numpy(dtype=float) + (
            parse_lvm_start_time_seconds(dc_path) - parse_lvm_start_time_seconds(folder / "Temperature.lvm")
        )
        near_zero = (power >= -0.5) & (power <= 0.5)
        start_idx = np.where(~near_zero)[0][0]
        off_candidates = np.where(near_zero & (dc_time > dc_time[start_idx]))[0]
        shut_time = float(dc_time[off_candidates[0]]) if off_candidates.size else None
        summary.update(
            {
                "dc_start_time_s": float(dc_time[start_idx]),
                "surface_temp_at_dc_start_C": float(
                    np.interp(dc_time[start_idx], time_s, surface_temperature)
                ),
                "dc_shutoff_time_s": shut_time,
                "surface_temp_at_dc_shutoff_C": (
                    float(np.interp(shut_time, time_s, surface_temperature)) if shut_time else None
                ),
            }
        )
        save_line_plot(
            plots_dir / "magnadc_power.png",
            dc_time,
            power,
            f"{test_id} MagnaDC Power",
            "Time (s)",
            "Power (W)",
            "tab:orange",
        )

    save_line_plot(
        plots_dir / "pressure_profile.png",
        pressure_df["Time (sec)"].to_numpy(dtype=float),
        pressure,
        f"{test_id} Pressure Profile",
        "Time (s)",
        "Pressure (kPa)",
        "tab:blue",
    )
    save_heat_flux_power_plot(
        plots_dir / "heat_flux_vs_time.png",
        time_s,
        heat_flux,
        dc_time,
        power,
        f"{test_id} Heat Flux vs Time",
        dnb_time_s=dnb_time_s,
        peak_time_s=peak_time_s,
        off_time_s=shut_time,
    )
    save_temperature_profile_plot(
        plots_dir / "surface_temperature.png",
        time_s,
        temp_data["thermocouples"],
        surface_temperature,
        f"{test_id} Temperature vs Time",
        dnb_time_s=dnb_time_s,
        peak_time_s=peak_time_s,
        off_time_s=shut_time,
    )

    if not args.skip_sensors:
        summary.update(
            save_hydrophone_analysis(
                folder,
                plots_dir,
                band_min_hz=args.hydrophone_band_min_hz,
                band_max_hz=args.hydrophone_band_max_hz,
                oscillation_start_s=args.oscillation_start_s,
                oscillation_end_s=args.oscillation_end_s,
                oscillation_max_frequency_hz=args.oscillation_max_frequency_hz,
                dnb_time_s=dnb_time_s,
                peak_time_s=peak_time_s,
                off_time_s=shut_time,
            )
        )
        summary.update(save_ae_analysis(folder, plots_dir))
        if args.include_wfs:
            summary.update(
                save_wfs_ae_spectrogram(
                    folder,
                    plots_dir,
                    channel=args.wfs_channel,
                    max_freq_hz=args.wfs_max_freq_hz,
                    band_min_hz=args.wfs_band_min_hz,
                    band_max_hz=args.wfs_band_max_hz,
                    oscillation_start_s=args.oscillation_start_s,
                    oscillation_end_s=args.oscillation_end_s,
                    oscillation_max_frequency_hz=args.oscillation_max_frequency_hz,
                    vmin_db=args.wfs_vmin_db,
                    vmax_db=args.wfs_vmax_db,
                    dnb_time_s=dnb_time_s,
                    peak_time_s=peak_time_s,
                    off_time_s=shut_time,
                )
            )

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_summary_markdown(output_dir / "summary.md", summary)
    return summary


def write_summary_markdown(path: Path, summary: dict[str, object]) -> None:
    rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in summary.items())
    path.write_text(
        "# Single-Case Analysis Summary\n\n"
        "Notebook marker values are reproduced for comparison. If the test log says "
        "CHF was not reached, interpret `chf_proxy_*` as the notebook's current "
        "fixed-window marker rather than a confirmed CHF event.\n\n"
        "| Quantity | Value |\n"
        "| --- | --- |\n"
        f"{rows}\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-id", default="Boiling-417")
    parser.add_argument("--raw-root", default=r"Y:\0_Ishraq\New Pool Boiling Video")
    parser.add_argument("--output-dir", default=r"demos\Boiling-417\generated")
    parser.add_argument("--subcooling", type=float, default=57.6)
    parser.add_argument("--applied-heat-load", type=float, default=250.0)
    parser.add_argument("--target-pressure", type=float, default=97.7)
    parser.add_argument("--chf-marker-start-s", type=float, default=50.0)
    parser.add_argument("--chf-marker-end-s", type=float, default=100.0)
    parser.add_argument("--nbr-gap-s", type=float, default=200.0)
    parser.add_argument(
        "--dnb-search-end-s",
        type=float,
        default=250.0,
        help="End time for finding the early sudden heat-flux drop used to identify DNB.",
    )
    parser.add_argument(
        "--dnb-drop-window-s",
        type=float,
        default=5.0,
        help="Time interval used to detect the sudden DNB heat-flux drop.",
    )
    parser.add_argument(
        "--hydrophone-band-min-hz",
        type=float,
        default=0.0,
        help="Lower frequency bound for band-integrated hydrophone PSD.",
    )
    parser.add_argument(
        "--hydrophone-band-max-hz",
        type=float,
        default=6000.0,
        help="Upper frequency bound for band-integrated hydrophone PSD.",
    )
    parser.add_argument(
        "--skip-sensors",
        action="store_true",
        help="Skip hydrophone and acoustic-emission analysis plots.",
    )
    parser.add_argument(
        "--oscillation-start-s",
        type=float,
        default=300.0,
        help="Start time for band-power oscillation frequency analysis.",
    )
    parser.add_argument(
        "--oscillation-end-s",
        type=float,
        default=700.0,
        help="End time for band-power oscillation frequency analysis.",
    )
    parser.add_argument(
        "--oscillation-max-frequency-hz",
        type=float,
        default=0.2,
        help="Maximum oscillation frequency to include in band-power spectrum plots.",
    )
    parser.add_argument(
        "--include-wfs",
        action="store_true",
        help="Decode any .wfs waveform file and save an AE waveform spectrogram.",
    )
    parser.add_argument(
        "--wfs-channel",
        type=int,
        default=1,
        help="Waveform channel to decode from the .wfs file.",
    )
    parser.add_argument(
        "--wfs-max-freq-hz",
        type=float,
        default=250000.0,
        help="Upper frequency limit for the AE waveform spectrogram.",
    )
    parser.add_argument(
        "--wfs-band-min-hz",
        type=float,
        default=0.0,
        help="Lower frequency bound for band-integrated AE waveform PSD.",
    )
    parser.add_argument(
        "--wfs-band-max-hz",
        type=float,
        default=250000.0,
        help="Upper frequency bound for band-integrated AE waveform PSD.",
    )
    parser.add_argument(
        "--wfs-vmin-db",
        type=float,
        default=-180.0,
        help="Lower color scale limit for the AE waveform spectrogram.",
    )
    parser.add_argument(
        "--wfs-vmax-db",
        type=float,
        default=-40.0,
        help="Upper color scale limit for the AE waveform spectrogram.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = analyze_case(args)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
