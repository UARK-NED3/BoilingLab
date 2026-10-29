"""Analyze the five controlled post-CHF heating tests at approximately 10 kPa.

This runner is intentionally separate from the 30-case boiling-hysteresis
correlation workflow.  It reconstructs protocol timing directly from each
case's processed thermal time series, while retaining the manuscript-selected
CHF, NBR, and maximum-temperature events from the reviewed event ledger.

The resulting figures are candidate replacements for manuscript diagnostics;
they are not used to refit the 30-case correlation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


DEFAULT_DATA_ROOT = Path(r"Z:\ned3-019-BoilingHysteresis10kPa")
DEFAULT_EVENT_LEDGER = Path(
    r"C:\Users\hanhu\Documents\BoilingLab\manuscripts\boiling_hysteresis_subatmospheric"
    r"\generated\protocol_validation_data.csv"
)
DEFAULT_OUTPUT_DIR = Path(
    r"C:\Users\hanhu\Documents\BoilingLab\manuscripts\boiling_hysteresis_subatmospheric"
    r"\generated\protocol_diagnostics"
)

CASE_DIRECTORIES = {
    "B-420": "1-Tmax_at_CHF",
    "B-421": "2_Tmax_100C",
    "B-422": "3_Tmax_150C",
    "B-423": "4_Tmax_200C",
    "B-424": "5_Tmax_250C",
}
CASE_LABELS = {
    "B-420": r"CHF cutoff",
    "B-421": r"100 $^\circ$C target",
    "B-422": r"150 $^\circ$C target",
    "B-423": r"200 $^\circ$C target",
    "B-424": r"250 $^\circ$C target",
}
CASE_COLORS = ["#3b82f6", "#16a34a", "#d97706", "#dc2626", "#7c3aed"]

TIME = "time_reference_temperature_s"
POWER = "dc_power_W_interpolated"
TEMPERATURE = "surface_temperature_C"
HEAT_FLUX = "heat_flux_W_cm2"
HYDROPHONE_TIME = "Time (s)"
HYDROPHONE_DB = "Band-integrated hydrophone power proxy (dB re V^2)"


def set_style() -> None:
    """Apply the manuscript plotting style and preserve marker visibility."""
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 12,
            "axes.labelsize": 14,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 9,
            "axes.linewidth": 1.0,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )


def style_axis(axis: plt.Axes) -> None:
    axis.grid(True, color="#d9d9d9", linewidth=0.7, zorder=0)
    axis.set_axisbelow(True)
    axis.tick_params(direction="out")
    axis.set_box_aspect(1 / 1.125)


def normalize_test_id(value: object) -> str:
    text = str(value).strip().upper().replace("_", "-")
    if text.startswith("BOILING-"):
        text = "B-" + text.split("-", maxsplit=1)[1]
    if text.startswith("B") and not text.startswith("B-"):
        text = "B-" + text[1:]
    return text


def load_selected_events(path: Path) -> pd.DataFrame:
    """Read and validate manuscript-selected post-CHF events."""
    events = pd.read_csv(path)
    events = events.rename(
        columns={
            "T_max_C": "t_max_C",
            "T_sat_C": "tsat_C",
            "T_nbr_C": "t_nbr_C",
            "DeltaT_max_K": "delta_tmax_C",
        }
    )
    if "t_max_s" not in events:
        events["t_max_s"] = np.nan
    events["test_id"] = events["test_id"].map(normalize_test_id)
    required = {
        "test_id",
        "t_chf_s",
        "t_nbr_s",
        "t_max_s",
        "t_max_C",
        "q_chf_W_cm2",
        "q_nbr_W_cm2",
        "q_min_W_cm2",
        "tsat_C",
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Selected-event ledger is missing columns: {sorted(missing)}")
    events = events.set_index("test_id", drop=False)
    missing_cases = set(CASE_DIRECTORIES).difference(events.index)
    if missing_cases:
        raise ValueError(f"Selected-event ledger is missing cases: {sorted(missing_cases)}")
    return events.loc[list(CASE_DIRECTORIES)].copy()


def read_thermal_timeseries(case_directory: Path) -> pd.DataFrame:
    """Read the sole processed thermal time series from one extended test."""
    matches = sorted(case_directory.rglob("thermal_timeseries.csv"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected one processed thermal time series under {case_directory}; found {len(matches)}."
        )
    thermal = pd.read_csv(matches[0])
    missing = {TIME, POWER, TEMPERATURE, HEAT_FLUX}.difference(thermal.columns)
    if missing:
        raise ValueError(f"{matches[0]} is missing columns: {sorted(missing)}")
    thermal = thermal.sort_values(TIME).reset_index(drop=True)
    return thermal


def find_power_shutoff_index(
    thermal: pd.DataFrame,
    t_chf_s: float,
    persistence_samples: int = 2,
) -> tuple[int, float]:
    """Locate the first sustained low-power state after selected CHF.

    The threshold is the larger of 0.5 W and 1% of peak positive DC power.
    A persistent state avoids classifying a transient controller dip as the
    deliberate switch-off command.
    """
    if persistence_samples < 1:
        raise ValueError("persistence_samples must be at least one.")
    time = thermal[TIME].to_numpy(dtype=float)
    power = thermal[POWER].to_numpy(dtype=float)
    peak_power = np.nanmax(power)
    if not np.isfinite(peak_power) or peak_power <= 0:
        raise ValueError("Cannot identify a shutoff in a non-positive power trace.")
    threshold = max(0.5, 0.01 * peak_power)
    candidates = np.flatnonzero((time >= float(t_chf_s)) & (power <= threshold))
    for index in candidates:
        final_index = min(index + persistence_samples, len(power))
        if final_index - index < persistence_samples:
            continue
        if np.all(power[index:final_index] <= threshold):
            return int(index), float(threshold)
    raise ValueError("No persistent low-power state was found after selected CHF.")


def interpolate_at_time(thermal: pd.DataFrame, column: str, time_s: float) -> float:
    time = thermal[TIME].to_numpy(dtype=float)
    values = thermal[column].to_numpy(dtype=float)
    return float(np.interp(float(time_s), time, values))


def centered_rolling_median(values: np.ndarray, window_samples: int) -> np.ndarray:
    """Return a centered median trend without interpreting isolated spikes as a state change."""
    if window_samples < 1:
        raise ValueError("window_samples must be positive.")
    return (
        pd.Series(np.asarray(values, dtype=float))
        .rolling(window_samples, center=True, min_periods=1)
        .median()
        .to_numpy()
    )


def read_hydrophone_proxy(case_directory: Path) -> pd.DataFrame:
    """Read the processed band-integrated hydrophone voltage-squared proxy."""
    matches = sorted(case_directory.rglob("hydrophone_band_integrated_power.csv"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected one hydrophone band-power table under {case_directory}; found {len(matches)}."
        )
    hydrophone = pd.read_csv(matches[0])
    missing = {HYDROPHONE_TIME, HYDROPHONE_DB}.difference(hydrophone.columns)
    if missing:
        raise ValueError(f"{matches[0]} is missing columns: {sorted(missing)}")
    return hydrophone.sort_values(HYDROPHONE_TIME).reset_index(drop=True)


def derive_case_metrics(
    thermal: pd.DataFrame, selected: Mapping[str, float | str]
) -> dict[str, float | str]:
    """Combine selected manuscript events with raw protocol-response metrics."""
    cutoff_index, threshold = find_power_shutoff_index(thermal, float(selected["t_chf_s"]))
    cutoff_time = float(thermal.loc[cutoff_index, TIME])
    t_chf = float(selected["t_chf_s"])
    t_nbr = float(selected["t_nbr_s"])
    if cutoff_time <= t_chf:
        raise ValueError("Detected cutoff precedes or coincides with selected CHF.")
    if t_nbr <= cutoff_time:
        raise ValueError("Selected NBR must occur after detected heater cutoff.")

    time = thermal[TIME].to_numpy(dtype=float)
    temperature = thermal[TEMPERATURE].to_numpy(dtype=float)
    trajectory = (time >= t_chf) & (time <= t_nbr)
    if not np.any(trajectory):
        raise ValueError("No raw samples fall between selected CHF and NBR.")
    peak_index = int(np.flatnonzero(trajectory)[np.nanargmax(temperature[trajectory])])
    tmax_raw = float(temperature[peak_index])
    tmax_raw_time = float(time[peak_index])
    cutoff_temperature = float(temperature[cutoff_index])
    cutoff_heat_flux = float(thermal.loc[cutoff_index, HEAT_FLUX])
    power_mask = (time >= t_chf) & (time <= cutoff_time)
    post_chf_energy = float(
        np.trapezoid(thermal.loc[power_mask, POWER], thermal.loc[power_mask, TIME])
    )

    q_chf = float(selected["q_chf_W_cm2"])
    q_nbr = float(selected["q_nbr_W_cm2"])
    q_min = float(selected["q_min_W_cm2"])
    target_temperature = selected.get("target_Tmax_C", np.nan)
    if not np.isfinite(float(target_temperature)):
        target_temperature = float(selected["t_max_C"])
    return {
        "test_id": normalize_test_id(selected["test_id"]),
        "t_chf_s": t_chf,
        "t_cutoff_s": cutoff_time,
        "t_nbr_s": t_nbr,
        "tmax_selected_C": float(selected["t_max_C"]),
        "tmax_selected_time_s": float(selected["t_max_s"]),
        "protocol_target_temperature_C": float(target_temperature),
        "tmax_raw_C": tmax_raw,
        "tmax_raw_time_s": tmax_raw_time,
        "tmax_raw_minus_selected_C": tmax_raw - float(selected["t_max_C"]),
        "tsat_C": float(selected["tsat_C"]),
        "cutoff_temperature_C": cutoff_temperature,
        "cutoff_heat_flux_W_cm2": cutoff_heat_flux,
        "cutoff_power_threshold_W": threshold,
        "post_chf_heating_s": cutoff_time - t_chf,
        "cutoff_to_tmax_s": tmax_raw_time - cutoff_time,
        "cutoff_to_nbr_s": t_nbr - cutoff_time,
        "tmax_overshoot_C": tmax_raw - cutoff_temperature,
        "post_chf_electrical_energy_J": post_chf_energy,
        "q_chf_selected_W_cm2": q_chf,
        "q_nbr_selected_W_cm2": q_nbr,
        "q_min_selected_W_cm2": q_min,
        "H_selected": q_nbr / q_chf,
        "qmin_over_qchf_selected": q_min / q_chf,
        "delta_tmax_C": float(selected["t_max_C"]) - float(selected["tsat_C"]),
    }


def save_figure(figure: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_dir / f"{stem}.png", bbox_inches="tight")
    figure.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(figure)


def add_event_markers(
    axis: plt.Axes,
    thermal: pd.DataFrame,
    metrics: pd.Series,
    color: str,
    y_column: str,
) -> None:
    events = [
        (metrics["t_chf_s"], "o"),
        (metrics["t_cutoff_s"], "s"),
        (metrics["tmax_raw_time_s"], "^"),
        (metrics["t_nbr_s"], "D"),
    ]
    for time_s, marker in events:
        axis.scatter(
            time_s - metrics["t_chf_s"],
            interpolate_at_time(thermal, y_column, time_s),
            s=35,
            marker=marker,
            color=color,
            edgecolor="black",
            linewidth=0.55,
            zorder=5,
        )


def plot_post_chf_trajectories(
    metrics: pd.DataFrame, thermals: Mapping[str, pd.DataFrame], output_dir: Path
) -> None:
    """Plot the full selected CHF-to-NBR trajectories for the five tests."""
    figure, axes = plt.subplots(1, 2, figsize=(9.2, 4.25), constrained_layout=True)
    left, right = axes
    for (test_id, row), color in zip(metrics.iterrows(), CASE_COLORS):
        thermal = thermals[test_id]
        mask = (thermal[TIME] >= row["t_chf_s"]) & (thermal[TIME] <= row["t_nbr_s"])
        subset = thermal.loc[mask]
        delta_t = subset[TEMPERATURE] - row["tsat_C"]
        left.plot(delta_t, subset[HEAT_FLUX], color=color, linewidth=1.45, zorder=2)
        for event_time, marker in [
            (row["t_chf_s"], "o"),
            (row["t_cutoff_s"], "s"),
            (row["tmax_raw_time_s"], "^"),
            (row["t_nbr_s"], "D"),
        ]:
            left.scatter(
                interpolate_at_time(thermal, TEMPERATURE, event_time) - row["tsat_C"],
                interpolate_at_time(thermal, HEAT_FLUX, event_time),
                s=38,
                marker=marker,
                color=color,
                edgecolor="black",
                linewidth=0.55,
                zorder=5,
            )
        right.plot(
            subset[TIME] - row["t_chf_s"],
            delta_t,
            color=color,
            linewidth=1.45,
            zorder=2,
        )
        add_event_markers(right, thermal, row, color, TEMPERATURE)

    for axis in axes:
        style_axis(axis)
    left.set_xlabel(r"Apparent wall superheat, $T_\mathrm{w}-T_\mathrm{sat}$ ($^\circ$C)")
    left.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W/cm$^2$)")
    left.set_xlim(0, 220)
    left.set_ylim(0, 60)
    right.set_xlabel(r"Time after selected CHF (s)")
    right.set_ylabel(r"Apparent wall superheat, $T_\mathrm{w}-T_\mathrm{sat}$ ($^\circ$C)")
    right.set_xlim(left=0)
    right.set_ylim(0, 220)

    case_handles = [
        Line2D([0], [0], color=color, lw=1.8, label=CASE_LABELS[test_id])
        for test_id, color in zip(metrics.index, CASE_COLORS)
    ]
    event_handles = [
        Line2D([0], [0], marker=marker, color="white", markerfacecolor="white", markeredgecolor="black",
               linestyle="None", markersize=6, label=label)
        for marker, label in [("o", "selected CHF"), ("s", "heater cutoff"), ("^", r"$T_\mathrm{max}$"), ("D", "selected NBR")]
    ]
    left.legend(handles=case_handles, loc="upper right", frameon=True, title="Protocol")
    right.legend(handles=event_handles, loc="lower right", frameon=True, title="Event")
    save_figure(figure, output_dir, "fig_post_chf_controlled_trajectories")


def plot_protocol_response_summary(metrics: pd.DataFrame, output_dir: Path) -> None:
    """Summarize protocol fidelity, state maturation, and recovery time scales."""
    figure, axes = plt.subplots(2, 2, figsize=(9.0, 8.0), constrained_layout=True)
    colors = CASE_COLORS

    axis = axes[0, 0]
    axis.plot(
        metrics["delta_tmax_C"],
        metrics["post_chf_electrical_energy_J"] / 1000.0,
        "-o",
        color="#7c3aed",
        mfc="white",
        zorder=2,
    )
    for (_, row), color in zip(metrics.iterrows(), colors):
        axis.scatter(
            row["delta_tmax_C"],
            row["post_chf_electrical_energy_J"] / 1000.0,
            s=45,
            color=color,
            edgecolor="black",
            linewidth=0.55,
            zorder=5,
        )
    axis.set_xlabel(r"Maximum superheat, $\Delta T_\mathrm{max}$ ($^\circ$C)")
    axis.set_ylabel("Electrical input after CHF (kJ)")

    axis = axes[0, 1]
    axis.plot(metrics["delta_tmax_C"], metrics["H_selected"], "-o", color="#1f77b4", mfc="white", label=r"$H$", zorder=2)
    axis.plot(metrics["delta_tmax_C"], metrics["qmin_over_qchf_selected"], "-s", color="#d97706", mfc="white", label=r"$q^{\prime\prime}_\mathrm{min}/q^{\prime\prime}_\mathrm{CHF}$", zorder=2)
    axis.set_xlabel(r"Maximum superheat, $\Delta T_\mathrm{max}$ ($^\circ$C)")
    axis.set_ylabel("Normalized heat flux (-)")
    axis.set_ylim(0, 1.05)
    axis.legend(loc="upper right", frameon=True)

    axis = axes[1, 0]
    axis.plot(metrics["delta_tmax_C"], metrics["post_chf_heating_s"], "-s", color="#d97706", mfc="white", label="heater on after CHF", zorder=2)
    axis.plot(metrics["delta_tmax_C"], metrics["cutoff_to_nbr_s"], "-o", color="#1f77b4", mfc="white", label="cutoff to selected NBR", zorder=2)
    axis.set_xlabel(r"Maximum superheat, $\Delta T_\mathrm{max}$ ($^\circ$C)")
    axis.set_ylabel("Duration (s)")
    axis.legend(loc="upper left", frameon=True)

    axis = axes[1, 1]
    axis.plot(metrics["cutoff_temperature_C"], metrics["tmax_overshoot_C"], "-o", color="#16a34a", mfc="white", label=r"$T_\mathrm{max}-T_\mathrm{cutoff}$", zorder=2)
    for (_, row), color in zip(metrics.iterrows(), colors):
        axis.scatter(row["cutoff_temperature_C"], row["tmax_overshoot_C"], s=45, color=color, edgecolor="black", linewidth=0.55, zorder=5)
    axis.set_xlabel(r"Temperature at heater cutoff ($^\circ$C)")
    axis.set_ylabel(r"Post-cutoff overshoot ($^\circ$C)")
    axis.set_ylim(bottom=0)
    axis.legend(loc="upper right", frameon=True)

    for axis in axes.flat:
        style_axis(axis)
    for label, axis in zip(["(a)", "(b)", "(c)", "(d)"], axes.flat):
        axis.text(-0.16, 1.04, label, transform=axis.transAxes, fontsize=14,
                  fontweight="normal", va="bottom", ha="left")
    save_figure(figure, output_dir, "fig_post_chf_protocol_response_summary")


def plot_hydrophone_context(
    metrics: pd.DataFrame,
    thermals: Mapping[str, pd.DataFrame],
    data_root: Path,
    output_dir: Path,
) -> None:
    """Compare acoustic context for a short- and a long-wait protocol trace.

    This sensor-voltage-squared proxy is useful for within-trace visual context,
    but it is neither calibrated acoustic pressure nor an independent vapor-film
    or wetting measurement.
    """
    selected_cases = ["B-421", "B-424"]
    figure, axes = plt.subplots(2, 2, figsize=(9.2, 6.0), sharex="col", constrained_layout=True)
    event_styles = [
        ("t_cutoff_s", "--", "heater cutoff"),
        ("tmax_raw_time_s", ":", r"$T_\mathrm{max}$"),
        ("t_nbr_s", "-.", "selected NBR"),
    ]
    for column, test_id in enumerate(selected_cases):
        row = metrics.loc[test_id]
        thermal = thermals[test_id]
        hydrophone = read_hydrophone_proxy(data_root / CASE_DIRECTORIES[test_id])
        t_chf = row["t_chf_s"]
        thermal_mask = (thermal[TIME] >= t_chf) & (thermal[TIME] <= row["t_nbr_s"])
        hydrophone_mask = (hydrophone[HYDROPHONE_TIME] >= t_chf) & (
            hydrophone[HYDROPHONE_TIME] <= row["t_nbr_s"]
        )
        upper = axes[0, column]
        lower = axes[1, column]
        thermal_subset = thermal.loc[thermal_mask]
        upper.plot(
            thermal_subset[TIME] - t_chf,
            thermal_subset[TEMPERATURE] - row["tsat_C"],
            color="#dc2626",
            linewidth=1.35,
            label=r"$T_\mathrm{w}-T_\mathrm{sat}$",
            zorder=2,
        )
        flux_axis = upper.twinx()
        flux_axis.plot(
            thermal_subset[TIME] - t_chf,
            thermal_subset[HEAT_FLUX],
            color="#2563eb",
            linewidth=1.15,
            label=r"$q^{\prime\prime}$",
            zorder=2,
        )
        hydrophone_subset = hydrophone.loc[hydrophone_mask]
        acoustic_time = hydrophone_subset[HYDROPHONE_TIME].to_numpy(dtype=float) - t_chf
        acoustic_db = hydrophone_subset[HYDROPHONE_DB].to_numpy(dtype=float)
        dt = np.nanmedian(np.diff(acoustic_time))
        window_samples = max(3, int(round(10.0 / dt)))
        lower.plot(acoustic_time, acoustic_db, color="#9ca3af", linewidth=0.5, alpha=0.55, label="raw proxy", zorder=1)
        lower.plot(
            acoustic_time,
            centered_rolling_median(acoustic_db, window_samples),
            color="#111827",
            linewidth=1.25,
            label="10 s median",
            zorder=3,
        )
        for event_key, linestyle, _ in event_styles:
            event_time = row[event_key] - t_chf
            upper.axvline(event_time, color="#4b5563", linestyle=linestyle, linewidth=0.9, zorder=1)
            lower.axvline(event_time, color="#4b5563", linestyle=linestyle, linewidth=0.9, zorder=1)
        upper.set_title(CASE_LABELS[test_id])
        upper.set_ylabel(r"$T_\mathrm{w}-T_\mathrm{sat}$ ($^\circ$C)", color="#dc2626")
        upper.tick_params(axis="y", labelcolor="#dc2626")
        flux_axis.set_ylabel(r"$q^{\prime\prime}$ (W/cm$^2$)", color="#2563eb")
        flux_axis.tick_params(axis="y", labelcolor="#2563eb")
        lower.set_xlabel("Time after selected CHF (s)")
        lower.set_ylabel("Hydrophone proxy (dB re V$^2$)")
        lower.set_ylim(-50, -18)
        for axis in (upper, lower):
            axis.grid(True, color="#d9d9d9", linewidth=0.7, zorder=0)
            axis.set_axisbelow(True)
            axis.tick_params(direction="out")
        upper.text(
            -0.15,
            1.05,
            f"({chr(ord('a') + column)})",
            transform=upper.transAxes,
            fontsize=14,
            fontweight="normal",
            va="bottom",
            ha="left",
        )
    axes[0, 0].legend(loc="upper left", frameon=True)
    axes[1, 0].legend(loc="lower left", frameon=True)
    axes[1, 1].legend(
        handles=[
            Line2D([0], [0], color="#4b5563", linestyle=style, label=label)
            for _, style, label in event_styles
        ],
        loc="lower right",
        frameon=True,
        title="Event",
    )
    save_figure(figure, output_dir, "fig_post_chf_hydrophone_context")


def write_summary(metrics: pd.DataFrame, output_dir: Path) -> None:
    lines = [
        "# Extended 10 kPa Post-CHF Protocol Diagnostics",
        "",
        "## Provenance",
        "",
        "- Selected CHF, NBR, minimum-flux, and maximum-temperature values are read from the manuscript protocol-event table; the companion event ledger records CHF/NBR event provenance.",
        "- Heater shutoff, cutoff temperature, raw thermal peak, and time partitions are derived from the processed thermal time series in `Z:\\ned3-019-BoilingHysteresis10kPa`.",
        "- The electrical energy is input energy integrated from selected CHF to heater cutoff. It is not a stored-energy measurement.",
        "",
        "## Observed range",
        "",
        f"- $H$ decreases from {metrics['H_selected'].max():.3f} to {metrics['H_selected'].min():.3f} across the controlled sequence.",
        f"- Heater-on duration after selected CHF increases from {metrics['post_chf_heating_s'].min():.1f} to {metrics['post_chf_heating_s'].max():.1f} s.",
        f"- Cutoff-to-selected-NBR duration increases from {metrics['cutoff_to_nbr_s'].min():.1f} to {metrics['cutoff_to_nbr_s'].max():.1f} s.",
        f"- Raw post-cutoff temperature overshoot spans {metrics['tmax_overshoot_C'].min():.2f} to {metrics['tmax_overshoot_C'].max():.2f} $^\\circ$C.",
        "",
        "## Interpretation boundary",
        "",
        "These five cases are a controlled within-apparatus protocol perturbation near 10 kPa. They demonstrate the response to longer post-CHF heating, but do not provide independent replication across pressure or surface architecture.",
        "The hydrophone context figure uses a band-integrated sensor-voltage-squared proxy aligned by archived clock offsets. It is not calibrated acoustic pressure and cannot independently identify vapor-film continuity or wall wetting.",
    ]
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(data_root: Path, event_ledger: Path, output_dir: Path) -> pd.DataFrame:
    set_style()
    events = load_selected_events(event_ledger)
    thermals: dict[str, pd.DataFrame] = {}
    records: list[dict[str, float | str]] = []
    for test_id, directory_name in CASE_DIRECTORIES.items():
        thermal = read_thermal_timeseries(data_root / directory_name)
        thermals[test_id] = thermal
        records.append(derive_case_metrics(thermal, events.loc[test_id].to_dict()))
    metrics = pd.DataFrame(records).set_index("test_id", drop=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output_dir / "post_chf_protocol_metrics.csv", index=False)
    plot_post_chf_trajectories(metrics, thermals, output_dir)
    plot_protocol_response_summary(metrics, output_dir)
    plot_hydrophone_context(metrics, thermals, data_root, output_dir)
    write_summary(metrics, output_dir)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--event-ledger", type=Path, default=DEFAULT_EVENT_LEDGER)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = run(arguments.data_root, arguments.event_ledger, arguments.output_dir)
    print(result.to_string(index=False))
