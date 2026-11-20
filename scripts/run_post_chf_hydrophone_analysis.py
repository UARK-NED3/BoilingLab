"""Event-aligned hydrophone analysis for the five extended 10 kPa tests.

The analysis uses manuscript-selected thermal events, archived LVM clock offsets,
and a PSD integral rather than a mean across frequency bins. It reports an
uncalibrated voltage-squared proxy and does not infer acoustic pressure,
vapor-film continuity, or wall wetting from the hydrophone alone.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy import signal

# Permit direct execution and import-by-path during repository tests.
SCRIPTS_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPTS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from run_post_chf_protocol_diagnostics import (
    CASE_COLORS,
    CASE_DIRECTORIES,
    CASE_LABELS,
    HEAT_FLUX,
    TEMPERATURE,
    TIME,
    derive_case_metrics,
    load_selected_events,
    read_thermal_timeseries,
    set_style,
)


DEFAULT_DATA_ROOT = Path(r"Z:\ned3-019-BoilingHysteresis10kPa")
DEFAULT_EVENT_LEDGER = Path(
    r"C:\Users\hanhu\Documents\BoilingLab\manuscripts\boiling_hysteresis_subatmospheric"
    r"\generated\protocol_validation_data.csv"
)
DEFAULT_OUTPUT_DIR = Path(
    r"C:\Users\hanhu\Documents\BoilingLab\manuscripts\boiling_hysteresis_subatmospheric"
    r"\generated\protocol_diagnostics\hydrophone_event_analysis"
)

BAND_MIN_HZ = 40.0
BAND_MAX_HZ = 3000.0
HIGHPASS_HZ = 20.0
WINDOW_S = 2.0
OVERLAP_FRACTION = 0.75
MIN_WINDOW_DURATION_S = 10.0


def find_one(case_directory: Path, relative_path: str) -> Path:
    """Return an expected archived case file with an actionable error."""
    path = case_directory / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Expected {relative_path} under {case_directory}.")
    return path


def hydrophone_offset_seconds(case_directory: Path) -> float:
    """Read the archived hydrophone-to-temperature clock offset."""
    alignment_path = find_one(case_directory, "Processed_data/time_alignment.json")
    document = json.loads(alignment_path.read_text(encoding="utf-8"))
    for record in document.get("records", []):
        if record.get("modality") == "hydrophone":
            offset = record.get("applied_offset_s")
            if offset is None or not np.isfinite(float(offset)):
                raise ValueError(f"No finite hydrophone offset in {alignment_path}.")
            return float(offset)
    raise ValueError(f"No hydrophone record in {alignment_path}.")


def read_lvm_interval(
    path: Path,
    offset_s: float,
    time_start_s: float,
    time_end_s: float,
    chunksize: int = 500_000,
) -> tuple[np.ndarray, np.ndarray]:
    """Read a clock-aligned interval from one sequential hydrophone LVM file."""
    if time_end_s <= time_start_s:
        raise ValueError("time_end_s must exceed time_start_s.")
    raw_start = time_start_s - offset_s
    raw_end = time_end_s - offset_s
    time_parts: list[np.ndarray] = []
    voltage_parts: list[np.ndarray] = []
    for chunk in pd.read_csv(
        path,
        skiprows=23,
        header=None,
        names=["raw_time_s", "voltage_V", "comment"],
        usecols=[0, 1],
        sep=r"\s+",
        engine="python",
        chunksize=chunksize,
    ):
        raw_time = pd.to_numeric(chunk["raw_time_s"], errors="coerce").to_numpy(dtype=float)
        voltage = pd.to_numeric(chunk["voltage_V"], errors="coerce").to_numpy(dtype=float)
        finite = np.isfinite(raw_time) & np.isfinite(voltage)
        raw_time, voltage = raw_time[finite], voltage[finite]
        if raw_time.size == 0:
            continue
        keep = (raw_time >= raw_start) & (raw_time <= raw_end)
        if np.any(keep):
            time_parts.append(raw_time[keep] + offset_s)
            voltage_parts.append(voltage[keep])
        if raw_time[-1] > raw_end:
            break
    if not time_parts:
        raise ValueError(f"No hydrophone samples in [{time_start_s}, {time_end_s}] s from {path}.")
    time_s, voltage_v = np.concatenate(time_parts), np.concatenate(voltage_parts)
    if len(time_s) < 4:
        raise ValueError(f"Insufficient hydrophone samples in [{time_start_s}, {time_end_s}] s.")
    return time_s, voltage_v


def spectral_features(
    time_s: np.ndarray,
    voltage_v: np.ndarray,
    band_min_hz: float = BAND_MIN_HZ,
    band_max_hz: float = BAND_MAX_HZ,
    highpass_hz: float = HIGHPASS_HZ,
    window_s: float = WINDOW_S,
    overlap_fraction: float = OVERLAP_FRACTION,
) -> pd.DataFrame:
    """Calculate time-local PSD-derived hydrophone features.

    The band voltage variance is the integral of voltage PSD over the declared
    band. It is a relative electrical proxy, not acoustic pressure, sound power,
    or bubble-collapse energy.
    """
    time_s = np.asarray(time_s, dtype=float)
    voltage_v = np.asarray(voltage_v, dtype=float)
    dt = np.diff(time_s)
    if np.any(dt <= 0):
        raise ValueError("Hydrophone time must be strictly increasing.")
    sampling_frequency_hz = 1.0 / float(np.median(dt))
    if not np.isfinite(sampling_frequency_hz) or sampling_frequency_hz <= 2.0 * band_max_hz:
        raise ValueError("Sampling frequency is insufficient for the requested analysis band.")
    nperseg = int(round(window_s * sampling_frequency_hz))
    if len(voltage_v) < nperseg:
        raise ValueError("Requested interval is shorter than one spectral window.")
    noverlap = int(round(nperseg * overlap_fraction))
    sos = signal.butter(4, highpass_hz, btype="highpass", fs=sampling_frequency_hz, output="sos")
    filtered = signal.sosfiltfilt(sos, voltage_v)
    frequency_hz, center_time_s, psd_v2_hz = signal.spectrogram(
        filtered,
        fs=sampling_frequency_hz,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="constant",
        scaling="density",
        mode="psd",
    )
    mask = (frequency_hz >= band_min_hz) & (frequency_hz <= band_max_hz)
    if np.count_nonzero(mask) < 3:
        raise ValueError("Requested band has fewer than three PSD bins.")
    f_band, psd_band = frequency_hz[mask], psd_v2_hz[mask, :]
    band_voltage_variance = np.trapezoid(psd_band, f_band, axis=0)
    normalized_psd = psd_band / np.maximum(np.sum(psd_band, axis=0, keepdims=True), np.finfo(float).tiny)
    centroid_hz = np.sum(f_band[:, None] * normalized_psd, axis=0)
    entropy = -np.sum(normalized_psd * np.log(np.maximum(normalized_psd, np.finfo(float).tiny)), axis=0)
    entropy /= np.log(len(f_band))
    psd_db = 10.0 * np.log10(np.maximum(psd_band, np.finfo(float).tiny))
    peak_index = np.argmax(psd_band, axis=0)
    peak_to_median_psd_db = np.max(psd_db, axis=0) - np.median(psd_db, axis=0)
    return pd.DataFrame(
        {
            "time_reference_temperature_s": time_s[0] + center_time_s,
            "band_voltage_variance_V2": band_voltage_variance,
            "band_level_dB_re_V2": 10.0
            * np.log10(np.maximum(band_voltage_variance, np.finfo(float).tiny)),
            "spectral_centroid_Hz": centroid_hz,
            "spectral_entropy": entropy,
            "dominant_frequency_Hz": f_band[peak_index],
            "peak_to_median_psd_dB": peak_to_median_psd_db,
            "prominent_peak_6dB": peak_to_median_psd_db >= 6.0,
            "sampling_frequency_Hz": sampling_frequency_hz,
            "window_s": window_s,
            "overlap_fraction": overlap_fraction,
            "band_min_Hz": band_min_hz,
            "band_max_Hz": band_max_hz,
            "highpass_Hz": highpass_hz,
        }
    )


def event_windows(metrics: pd.Series) -> dict[str, tuple[float, float]]:
    """Return prespecified windows that avoid immediate event neighborhoods."""
    t_chf = float(metrics["t_chf_s"])
    t_cutoff = float(metrics["t_cutoff_s"])
    t_max = float(metrics["tmax_raw_time_s"])
    t_nbr = float(metrics["t_nbr_s"])
    return {
        "pre_CHF": (t_chf - 30.0, t_chf - 10.0),
        "post_CHF_heating": (t_chf + 10.0, t_cutoff - 10.0),
        "post_cutoff": (t_max + 20.0, t_nbr - 40.0),
        "pre_NBR": (t_nbr - 40.0, t_nbr - 10.0),
    }


def summarize_windows(features: pd.DataFrame, metrics: pd.Series) -> pd.DataFrame:
    """Summarize only event windows long enough for descriptive comparison."""
    rows: list[dict[str, object]] = []
    for name, (start_s, end_s) in event_windows(metrics).items():
        duration_s = end_s - start_s
        selected = features.loc[
            (features["time_reference_temperature_s"] >= start_s)
            & (features["time_reference_temperature_s"] <= end_s)
        ]
        usable = duration_s >= MIN_WINDOW_DURATION_S and len(selected) >= 3
        rows.append(
            {
                "test_id": metrics["test_id"],
                "window": name,
                "window_start_s": start_s,
                "window_end_s": end_s,
                "requested_duration_s": duration_s,
                "usable": usable,
                "n_spectral_bins": int(len(selected)) if usable else 0,
                "median_band_level_dB_re_V2": float(selected["band_level_dB_re_V2"].median())
                if usable
                else np.nan,
                "iqr_band_level_dB": float(
                    selected["band_level_dB_re_V2"].quantile(0.75)
                    - selected["band_level_dB_re_V2"].quantile(0.25)
                )
                if usable
                else np.nan,
                "median_centroid_Hz": float(selected["spectral_centroid_Hz"].median())
                if usable
                else np.nan,
                "median_entropy": float(selected["spectral_entropy"].median()) if usable else np.nan,
                "prominent_peak_fraction": float(selected["prominent_peak_6dB"].mean())
                if usable
                else np.nan,
            }
        )
    result = pd.DataFrame(rows)
    baseline = result.loc[result["window"] == "pre_CHF", ["test_id", "median_band_level_dB_re_V2"]]
    baseline = baseline.rename(columns={"median_band_level_dB_re_V2": "pre_CHF_median_dB"})
    result = result.merge(baseline, on="test_id", how="left")
    result["median_level_relative_to_pre_CHF_dB"] = (
        result["median_band_level_dB_re_V2"] - result["pre_CHF_median_dB"]
    )
    low_level_fraction: list[float] = []
    for row in result.itertuples(index=False):
        if not row.usable:
            low_level_fraction.append(np.nan)
            continue
        selected = features.loc[
            (features["time_reference_temperature_s"] >= row.window_start_s)
            & (features["time_reference_temperature_s"] <= row.window_end_s)
        ]
        low_level_fraction.append(
            float((selected["band_level_dB_re_V2"] < row.pre_CHF_median_dB - 6.0).mean())
        )
    result["fraction_6dB_below_pre_CHF"] = low_level_fraction
    return result


def rolling_median(time_s: np.ndarray, values: np.ndarray, window_s: float = 15.0) -> np.ndarray:
    """Use a time-aware rolling median solely to guide trace readability."""
    series = pd.Series(values, index=pd.to_timedelta(time_s, unit="s"))
    return series.rolling(f"{window_s}s", center=True, min_periods=1).median().to_numpy()


def _event_lines(axis: plt.Axes, metrics: pd.Series, reference_s: float) -> None:
    for key, line, _ in [
        ("t_cutoff_s", "--", "heater cutoff"),
        ("tmax_raw_time_s", ":", r"$T_\mathrm{max}$"),
        ("t_nbr_s", "-.", "selected NBR"),
    ]:
        axis.axvline(float(metrics[key]) - reference_s, color="#4b5563", linestyle=line, linewidth=0.9, zorder=1)


def plot_event_aligned_context(
    metrics: pd.DataFrame,
    thermals: dict[str, pd.DataFrame],
    features: dict[str, pd.DataFrame],
    output_dir: Path,
) -> None:
    """Plot thermal trajectory and relative hydrophone level for two contrasting waits."""
    selected_cases = ["B-421", "B-424"]
    figure, axes = plt.subplots(2, 2, figsize=(9.4, 6.0), sharex="col", constrained_layout=True)
    for column, test_id in enumerate(selected_cases):
        row = metrics.loc[test_id]
        thermal = thermals[test_id]
        acoustic = features[test_id]
        t_chf = float(row["t_chf_s"])
        upper, lower = axes[0, column], axes[1, column]
        thermal_subset = thermal.loc[(thermal[TIME] >= t_chf) & (thermal[TIME] <= row["t_nbr_s"])]
        upper.plot(
            thermal_subset[TIME] - t_chf,
            thermal_subset[TEMPERATURE] - row["tsat_C"],
            color="#dc2626",
            linewidth=1.2,
            label=r"$T_\mathrm{w}-T_\mathrm{sat}$",
            zorder=3,
        )
        flux_axis = upper.twinx()
        flux_axis.plot(
            thermal_subset[TIME] - t_chf,
            thermal_subset[HEAT_FLUX],
            color="#2563eb",
            linewidth=1.0,
            label=r"$q^{\prime\prime}$",
            zorder=2,
        )
        acoustic_subset = acoustic.loc[
            (acoustic["time_reference_temperature_s"] >= t_chf)
            & (acoustic["time_reference_temperature_s"] <= row["t_nbr_s"])
        ]
        acoustic_time = acoustic_subset["time_reference_temperature_s"].to_numpy() - t_chf
        level = acoustic_subset["band_level_dB_re_V2"].to_numpy()
        lower.plot(acoustic_time, level, color="#9ca3af", linewidth=0.4, alpha=0.5, zorder=1)
        lower.plot(acoustic_time, rolling_median(acoustic_time, level), color="#111827", linewidth=1.2, zorder=3, label="15 s median")
        for axis in (upper, lower):
            _event_lines(axis, row, t_chf)
            axis.grid(True, color="#d9d9d9", linewidth=0.7, zorder=0)
            axis.set_axisbelow(True)
            axis.tick_params(direction="out")
        upper.set_title(CASE_LABELS[test_id])
        upper.set_ylabel(r"$T_\mathrm{w}-T_\mathrm{sat}$ ($^\circ$C)", color="#dc2626")
        upper.tick_params(axis="y", labelcolor="#dc2626")
        flux_axis.set_ylabel(r"$q^{\prime\prime}$ (W/cm$^2$)", color="#2563eb")
        flux_axis.tick_params(axis="y", labelcolor="#2563eb")
        lower.set_xlabel("Time after selected CHF (s)")
        lower.set_ylabel(r"Hydrophone level (dB re V$^2$)")
        upper.text(-0.15, 1.04, f"({chr(ord('a') + column)})", transform=upper.transAxes, fontsize=14, va="bottom")
    axes[0, 0].legend(loc="upper left", frameon=True)
    axes[1, 0].legend(loc="lower left", frameon=True)
    axes[1, 1].legend(
        handles=[
            Line2D([0], [0], color="#4b5563", linestyle=line, label=label)
            for _, line, label in [
                ("t_cutoff_s", "--", "heater cutoff"),
                ("tmax_raw_time_s", ":", r"$T_\mathrm{max}$"),
                ("t_nbr_s", "-.", "selected NBR"),
            ]
        ],
        loc="lower right",
        frameon=True,
        title="Event",
    )
    figure.savefig(output_dir / "fig_post_chf_hydrophone_event_context.png", dpi=300, bbox_inches="tight")
    figure.savefig(output_dir / "fig_post_chf_hydrophone_event_context.pdf", bbox_inches="tight")
    plt.close(figure)


def plot_window_summary(summary: pd.DataFrame, metrics: pd.DataFrame, output_dir: Path) -> None:
    """Plot descriptive within-case relative hydrophone levels by event window."""
    labels = ["pre_CHF", "post_CHF_heating", "post_cutoff", "pre_NBR"]
    display_labels = ["Pre-CHF", "Heating", "Post-cutoff", "Pre-NBR"]
    figure, axis = plt.subplots(figsize=(7.4, 4.1), constrained_layout=True)
    for (test_id, _), color in zip(metrics.iterrows(), CASE_COLORS):
        subset = summary.loc[(summary["test_id"] == test_id) & summary["usable"]].copy()
        subset["x"] = subset["window"].map({name: i for i, name in enumerate(labels)})
        subset = subset.sort_values("x")
        axis.plot(
            subset["x"],
            subset["median_level_relative_to_pre_CHF_dB"],
            "-o",
            color=color,
            markeredgecolor="black",
            markersize=5,
            linewidth=1.15,
            label=CASE_LABELS[test_id],
            zorder=3,
        )
    axis.axhline(0.0, color="black", linewidth=0.9, linestyle="--", zorder=1)
    axis.set_xticks(range(len(labels)), display_labels)
    axis.set_ylabel(r"Median hydrophone level relative to pre-CHF (dB re V$^2$)")
    axis.grid(True, color="#d9d9d9", linewidth=0.7, zorder=0)
    axis.set_axisbelow(True)
    axis.tick_params(direction="out")
    axis.legend(frameon=True, ncol=2, loc="best", title="Protocol")
    figure.savefig(output_dir / "fig_post_chf_hydrophone_window_summary.png", dpi=300, bbox_inches="tight")
    figure.savefig(output_dir / "fig_post_chf_hydrophone_window_summary.pdf", bbox_inches="tight")
    plt.close(figure)


def write_readme(output_dir: Path, window_summary: pd.DataFrame) -> None:
    """Document signal definition, event selection, and claim limits."""
    usable = int(window_summary["usable"].sum())
    lines = [
        "# Event-Aligned Hydrophone Analysis",
        "",
        "## Scope",
        "",
        "This analysis reprocesses raw hydrophone voltage records from the five extended 10 kPa flat-copper tests. It aligns the records to the temperature clock with archived LVM-header offsets and uses manuscript-selected CHF, heater-cutoff, maximum-temperature, and NBR events. Dataset screening event files are not used.",
        "",
        "## Signal definition",
        "",
        f"For each {WINDOW_S:g} s Hann-windowed segment ({OVERLAP_FRACTION:.0%} overlap), a fourth-order {HIGHPASS_HZ:g} Hz high-pass filter is applied, a voltage PSD is evaluated, and band-integrated voltage variance is calculated as V_band^2(t) = integral_{{{BAND_MIN_HZ:g} Hz}}^{{{BAND_MAX_HZ:g} Hz}} S_VV(f,t) df. The plotted level is 10 log10(V_band^2 / 1 V^2).",
        "",
        "This is an uncalibrated, frequency-bounded sensor-voltage-squared proxy. It is not acoustic pressure, sound power, bubble-collapse energy, a direct vapor-film measurement, or a direct wetting measurement.",
        "",
        "## Event windows",
        "",
        "The descriptive windows are fixed before inspecting the acoustic result: pre-CHF (CHF minus 30 to minus 10 s), post-CHF heating (CHF plus 10 s to cutoff minus 10 s), post-cutoff (raw maximum-temperature time plus 20 s to NBR minus 40 s), and pre-NBR (NBR minus 40 to minus 10 s). Windows shorter than 10 s are marked unusable rather than padded or redefined.",
        "",
        f"The summary contains {usable} usable case-window combinations. Rows are descriptive summaries of serially correlated STFT windows; they are not independent replicates and no inferential p-values are reported.",
        "",
        "## Interpretation limit",
        "",
        "A decrease in the proxy is compatible with a change in the acoustic source and/or transmission path during the post-CHF history. It cannot by itself distinguish fewer collapse events, vapor-mediated attenuation, changing heat flux, sensor coupling, or background noise. The result is synchronized regime context, not independent validation of the thermal hysteresis correlation.",
        "",
    ]
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def run(data_root: Path, event_ledger: Path, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the event-aligned analysis and return feature and window summaries."""
    set_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    events = load_selected_events(event_ledger)
    metrics_records: list[dict[str, float | str]] = []
    thermals: dict[str, pd.DataFrame] = {}
    for test_id, directory_name in CASE_DIRECTORIES.items():
        thermal = read_thermal_timeseries(data_root / directory_name)
        thermals[test_id] = thermal
        metrics_records.append(derive_case_metrics(thermal, events.loc[test_id].to_dict()))
    metrics = pd.DataFrame(metrics_records).set_index("test_id", drop=False)
    all_features: list[pd.DataFrame] = []
    summaries: list[pd.DataFrame] = []
    feature_by_case: dict[str, pd.DataFrame] = {}
    for test_id, directory_name in CASE_DIRECTORIES.items():
        case_directory = data_root / directory_name
        row = metrics.loc[test_id]
        time_s, voltage_v = read_lvm_interval(
            find_one(case_directory, "Raw_data/Hydrophones.lvm"),
            hydrophone_offset_seconds(case_directory),
            float(row["t_chf_s"]) - 35.0,
            float(row["t_nbr_s"]) + 5.0,
        )
        features = spectral_features(time_s, voltage_v)
        features.insert(0, "test_id", test_id)
        features["time_after_selected_CHF_s"] = features["time_reference_temperature_s"] - float(row["t_chf_s"])
        features["time_after_cutoff_s"] = features["time_reference_temperature_s"] - float(row["t_cutoff_s"])
        features["H_selected"] = float(row["H_selected"])
        features["delta_tmax_C"] = float(row["delta_tmax_C"])
        feature_by_case[test_id] = features
        all_features.append(features)
        summaries.append(summarize_windows(features, row))
    all_feature_data = pd.concat(all_features, ignore_index=True)
    window_summary = pd.concat(summaries, ignore_index=True)
    all_feature_data.to_csv(output_dir / "hydrophone_psd_features.csv", index=False)
    window_summary.to_csv(output_dir / "hydrophone_event_window_summary.csv", index=False)
    metrics.to_csv(output_dir / "post_chf_protocol_metrics.csv", index=False)
    plot_event_aligned_context(metrics, thermals, feature_by_case, output_dir)
    plot_window_summary(window_summary, metrics, output_dir)
    write_readme(output_dir, window_summary)
    return all_feature_data, window_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--event-ledger", type=Path, default=DEFAULT_EVENT_LEDGER)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    _, summary = run(arguments.data_root, arguments.event_ledger, arguments.output_dir)
    print(summary.to_string(index=False))
