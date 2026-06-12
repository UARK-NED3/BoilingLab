"""Build publication-facing MEB manuscript analysis products.

This script assembles generated BoilingLab outputs and the sibling
literature-compiler ``test2_meb`` dataset into case-labeled tables and figures
for a journal manuscript. It intentionally uses manuscript case labels rather
than internal test IDs in plot legends and summary tables.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_single_case_demo import compute_temperature_quantities, parse_lvm_start_time_seconds, read_lvm


TC_LOCATION_M = np.array([0, 2.54, 5.08, 7.62]) * 1e-3
SURFACE_LOCATION_FLAT_CU_M = 13.1826e-3
CU_THERMAL_CONDUCTIVITY_W_MK = 392.0

# Pre-submission uncertainty assumptions. Replace these with calibration
# certificate values before final journal submission if available.
THERMOCOUPLE_STANDARD_UNCERTAINTY_C = 0.50
TC_POSITION_STANDARD_UNCERTAINTY_M = 0.05e-3
CU_THERMAL_CONDUCTIVITY_REL_STANDARD_UNCERTAINTY = 0.02
PRESSURE_TRANSDUCER_FULL_SCALE_KPA = 210.0
PRESSURE_TRANSDUCER_ACCURACY_FRACTION_FULL_SCALE = 0.0008
TIME_ALIGNMENT_STANDARD_UNCERTAINTY_S = 0.50
HYDROPHONE_VOLTAGE_REL_STANDARD_UNCERTAINTY = 0.03
HYDROPHONE_SENSITIVITY_REL_STANDARD_UNCERTAINTY = 0.10
PSD_ESTIMATOR_REL_STANDARD_UNCERTAINTY = 0.10
ENVELOPE_FIT_FLOOR_REL_STANDARD_UNCERTAINTY = 0.10

CASE_MAP = {
    "Boiling-412": {"case": "Case A", "power_W": 150.0},
    "Boiling-413": {"case": "Case B", "power_W": 180.0},
    "Boiling-416": {"case": "Case C", "power_W": 230.0},
    "Boiling-417": {"case": "Case D", "power_W": 250.0},
}

CASE_ORDER = list(CASE_MAP)
CASE_COLORS = {
    "Case A": "#1f77b4",
    "Case B": "#ff7f0e",
    "Case C": "#2ca02c",
    "Case D": "#d62728",
}


def linear_temperature_weights() -> tuple[np.ndarray, np.ndarray]:
    x = TC_LOCATION_M
    x_mean = float(np.mean(x))
    denominator = float(np.sum((x - x_mean) ** 2))
    slope_weights = (x - x_mean) / denominator
    intercept_weights = np.full_like(x, 1.0 / len(x)) - x_mean * slope_weights
    wall_temperature_weights = intercept_weights + SURFACE_LOCATION_FLAT_CU_M * slope_weights
    heat_flux_weights = -CU_THERMAL_CONDUCTIVITY_W_MK * slope_weights / 1e4
    return wall_temperature_weights, heat_flux_weights


def propagated_thermal_uncertainty(max_heat_flux_w_cm2: float) -> dict[str, float]:
    wall_weights, heat_flux_weights = linear_temperature_weights()
    wall_temperature_standard_c = float(
        np.sqrt(np.sum((wall_weights * THERMOCOUPLE_STANDARD_UNCERTAINTY_C) ** 2))
    )
    heat_flux_from_temperature_standard = float(
        np.sqrt(np.sum((heat_flux_weights * THERMOCOUPLE_STANDARD_UNCERTAINTY_C) ** 2))
    )
    heat_flux_from_k_standard = abs(max_heat_flux_w_cm2) * CU_THERMAL_CONDUCTIVITY_REL_STANDARD_UNCERTAINTY
    heat_flux_combined_standard = float(
        np.sqrt(heat_flux_from_temperature_standard**2 + heat_flux_from_k_standard**2)
    )
    # Position uncertainty is estimated by finite perturbation of the TC pitch.
    perturbed = TC_LOCATION_M + np.linspace(-1, 1, len(TC_LOCATION_M)) * TC_POSITION_STANDARD_UNCERTAINTY_M
    x_mean = float(np.mean(perturbed))
    denominator = float(np.sum((perturbed - x_mean) ** 2))
    slope_weights_perturbed = (perturbed - x_mean) / denominator
    heat_flux_weights_perturbed = -CU_THERMAL_CONDUCTIVITY_W_MK * slope_weights_perturbed / 1e4
    position_sensitivity = float(np.linalg.norm(heat_flux_weights_perturbed - heat_flux_weights))
    return {
        "wall_temperature_standard_uncertainty_C": wall_temperature_standard_c,
        "wall_temperature_expanded_uncertainty_C_k2": 2.0 * wall_temperature_standard_c,
        "heat_flux_temperature_standard_uncertainty_W_cm2": heat_flux_from_temperature_standard,
        "heat_flux_k_standard_uncertainty_W_cm2": heat_flux_from_k_standard,
        "heat_flux_combined_standard_uncertainty_W_cm2": heat_flux_combined_standard,
        "heat_flux_expanded_uncertainty_W_cm2_k2": 2.0 * heat_flux_combined_standard,
        "heat_flux_position_sensitivity_W_cm2_per_C": position_sensitivity,
    }


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 14,
            "axes.labelsize": 16,
            "xtick.labelsize": 13,
            "ytick.labelsize": 13,
            "legend.fontsize": 12,
            "axes.linewidth": 1.1,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )


def case_label(test_id: str) -> str:
    return CASE_MAP[test_id]["case"]


def power_label_from_case(case: str) -> str:
    for value in CASE_MAP.values():
        if value["case"] == case:
            return rf"$P_{{\mathrm{{load}}}}$ = {value['power_W']:.0f} W"
    return case


def power_label(test_id: str) -> str:
    return rf"$P_{{\mathrm{{load}}}}$ = {CASE_MAP[test_id]['power_W']:.0f} W"


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_thermal_case(raw_root: Path, test_id: str) -> dict[str, np.ndarray]:
    folder = raw_root / test_id
    temp = read_lvm(folder, "Temperature.lvm").rename(columns={"X_Value": "Time (sec)"})
    temp_data = compute_temperature_quantities(temp)
    dc = read_lvm(folder, "DC_power.lvm")
    dc_time = dc.iloc[:, 0].to_numpy(dtype=float)
    dc_power = dc.iloc[:, -1].to_numpy(dtype=float)
    offset = parse_lvm_start_time_seconds(folder / "DC_power.lvm") - parse_lvm_start_time_seconds(
        folder / "Temperature.lvm"
    )
    dc_time = dc_time + offset
    finite = np.isfinite(dc_time) & np.isfinite(dc_power)
    order = np.argsort(dc_time[finite])
    return {
        "time_s": temp_data["time_s"],
        "surface_temperature_C": temp_data["surface_temperature"],
        "heat_flux_W_cm2": temp_data["heat_flux"],
        "dc_time_s": dc_time[finite][order],
        "dc_power_W": dc_power[finite][order],
    }


def add_external_panel_label(fig: plt.Figure, ax: plt.Axes, label: str) -> None:
    ax.annotate(
        label,
        xy=(0.0, 1.0),
        xycoords="axes fraction",
        xytext=(-30, 8),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=plt.rcParams.get("font.size", 8.0),
        annotation_clip=False,
    )


def add_external_panel_labels(fig: plt.Figure, axes) -> None:
    fig.canvas.draw()
    for i, ax in enumerate(np.asarray(axes, dtype=object).ravel()):
        add_external_panel_label(fig, ax, f"({chr(97 + i)})")


def load_case_summaries(repo_root: Path) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    multi_summary_path = repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "summary.csv"
    multi_summary = pd.read_csv(multi_summary_path)
    summaries: dict[str, dict[str, object]] = {}
    for test_id in CASE_ORDER:
        summaries[test_id] = load_json(repo_root / "demos" / test_id / "generated" / "summary.json")
    return multi_summary, summaries


def write_publication_case_summary(
    output_dir: Path,
    multi_summary: pd.DataFrame,
    summaries: dict[str, dict[str, object]],
) -> pd.DataFrame:
    rows = []
    for _, row in multi_summary.iterrows():
        test_id = str(row["test_id"])
        summary = summaries.get(test_id, {})
        dnb_time_s = pd.to_numeric(summary.get("dnb_time_s", np.nan), errors="coerce")
        dnb_heat_flux = pd.to_numeric(summary.get("dnb_heat_flux_W_cm2", np.nan), errors="coerce")
        dnb_resolved = bool(np.isfinite(dnb_time_s) and np.isfinite(dnb_heat_flux) and dnb_time_s > 20.0 and dnb_heat_flux > 0.0)
        rows.append(
            {
                "case": case_label(test_id),
                "power_label": power_label(test_id),
                "nominal_power_W": CASE_MAP[test_id]["power_W"],
                "mean_pressure_kPa": row["pressure_mean_kPa"],
                "pressure_std_kPa": row["pressure_std_kPa"],
                "mean_liquid_temperature_C": row["mean_liquid_temp_C"],
                "saturation_temperature_C": row["T_sat_C"],
                "subcooling_K": row["T_sat_C"] - row["mean_liquid_temp_C"],
                "maximum_heat_flux_W_cm2": row["max_heat_flux_W_cm2"],
                "q_DNB_raw_W_cm2": dnb_heat_flux,
                "q_DNB_plot_W_cm2": dnb_heat_flux if dnb_resolved else np.nan,
                "t_DNB_s": dnb_time_s,
                "dnb_resolved_for_plot": dnb_resolved,
                "maximum_wall_temperature_C": row["max_surface_temp_C"],
                "heating_duration_s": row["heating_duration_s"],
                "mean_power_during_heating_W": row["mean_dc_power_during_heating_W"],
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "case_summary_publication.csv", index=False)
    return table


def write_sensor_availability(
    output_dir: Path,
    summaries: dict[str, dict[str, object]],
    repo_root: Path,
) -> pd.DataFrame:
    rows = []
    for test_id in CASE_ORDER:
        summary = summaries[test_id]
        case_dir = repo_root / "demos" / test_id / "generated"
        rows.append(
            {
                "case": case_label(test_id),
                "thermal_available": (repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "curves.csv").exists(),
                "hydrophone_intermediate_available": (
                    case_dir / "hydrophone_band_integrated_power.csv"
                ).exists()
                and (case_dir / "hydrophone_characteristic_frequencies.csv").exists(),
                "ae_waveform_available": bool(summary.get("ae_wfs_available", False)),
                "notes": (
                    "AE waveform analysis limited to Cases C-D."
                    if test_id in {"Boiling-416", "Boiling-417"}
                    else "No AE waveform file available for this case."
                ),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "sensor_availability_publication.csv", index=False)
    return table


def write_acoustic_summary(
    output_dir: Path,
    summaries: dict[str, dict[str, object]],
    repo_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    hydro_rows = []
    ae_rows = []
    for test_id in CASE_ORDER:
        summary = summaries[test_id]
        case_dir = repo_root / "demos" / test_id / "generated"
        hydro_power_path = case_dir / "hydrophone_band_integrated_power.csv"
        hydro_freq_path = case_dir / "hydrophone_characteristic_frequencies.csv"
        hydro_available = hydro_power_path.exists() and hydro_freq_path.exists()
        hydro_rows.append(
            {
                "case": case_label(test_id),
                "nominal_power_W": CASE_MAP[test_id]["power_W"],
                "hydrophone_available": hydro_available,
                "band_power_mean_V2": summary.get("hydrophone_band_power_mean_V2", np.nan),
                "band_power_max_V2": summary.get("hydrophone_band_power_max_V2", np.nan),
                "median_peak_frequency_Hz": summary.get("hydrophone_median_peak_frequency_Hz", np.nan),
                "median_centroid_frequency_Hz": summary.get("hydrophone_median_spectral_centroid_Hz", np.nan),
                "dominant_slow_modulation_Hz": summary.get(
                    "hydrophone_dominant_oscillation_frequency_Hz", np.nan
                ),
                "power_centroid_best_lag_s": summary.get("hydrophone_power_centroid_best_lag_s", np.nan),
                "power_centroid_best_correlation": summary.get(
                    "hydrophone_power_centroid_best_correlation", np.nan
                ),
            }
        )
        if summary.get("ae_wfs_available", False):
            ae_rows.append(
                {
                    "case": case_label(test_id),
                    "nominal_power_W": CASE_MAP[test_id]["power_W"],
                    "band_power_mean_V2": summary.get("ae_wfs_band_power_mean_V2", np.nan),
                    "band_power_max_V2": summary.get("ae_wfs_band_power_max_V2", np.nan),
                    "median_peak_frequency_Hz": summary.get("ae_wfs_median_peak_frequency_Hz", np.nan),
                    "median_centroid_frequency_Hz": summary.get(
                        "ae_wfs_median_spectral_centroid_Hz", np.nan
                    ),
                    "dominant_slow_modulation_Hz": summary.get(
                        "ae_wfs_dominant_oscillation_frequency_Hz", np.nan
                    ),
                }
            )
    hydro = pd.DataFrame(hydro_rows)
    ae = pd.DataFrame(ae_rows)
    hydro.to_csv(output_dir / "hydrophone_summary_publication.csv", index=False)
    ae.to_csv(output_dir / "ae_waveform_summary_publication.csv", index=False)
    return hydro, ae


def write_envelope_summary(
    output_dir: Path,
    repo_root: Path,
) -> pd.DataFrame:
    rows = []
    for test_id in ("Boiling-416", "Boiling-417"):
        path = repo_root / "demos" / test_id / "generated" / "meb_envelope_metrics.csv"
        if not path.exists():
            continue
        table = pd.read_csv(path)
        table.insert(0, "case", case_label(test_id))
        rows.append(table)
    envelope = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    if not envelope.empty:
        envelope.to_csv(output_dir / "envelope_metrics_publication.csv", index=False)
    return envelope


def write_uncertainty_diagnostics(
    output_dir: Path,
    summaries: dict[str, dict[str, object]],
    repo_root: Path,
    multi_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    multi_by_id = {str(row["test_id"]): row for _, row in multi_summary.iterrows()}
    for test_id in CASE_ORDER:
        summary = summaries[test_id]
        row = multi_by_id[test_id]
        case_dir = repo_root / "demos" / test_id / "generated"
        hydro_power_path = case_dir / "hydrophone_band_integrated_power.csv"
        hydro_freq_path = case_dir / "hydrophone_characteristic_frequencies.csv"

        hydro_power_cv = np.nan
        hydro_time_bin_s = np.nan
        if hydro_power_path.exists():
            hydro_power = pd.read_csv(hydro_power_path)
            power = hydro_power["Band-integrated hydrophone power proxy (V^2)"].to_numpy(dtype=float)
            time = hydro_power["Time (s)"].to_numpy(dtype=float)
            mean_power = float(np.nanmean(power))
            hydro_power_cv = float(np.nanstd(power) / mean_power) if mean_power else np.nan
            hydro_time_bin_s = float(np.nanmedian(np.diff(time))) if len(time) > 1 else np.nan

        centroid_iqr_hz = np.nan
        peak_iqr_hz = np.nan
        if hydro_freq_path.exists():
            hydro_freq = pd.read_csv(hydro_freq_path)
            centroid = hydro_freq["Spectral centroid (Hz)"].to_numpy(dtype=float)
            peak = hydro_freq["Peak frequency (Hz)"].to_numpy(dtype=float)
            centroid_iqr_hz = float(np.nanpercentile(centroid, 75) - np.nanpercentile(centroid, 25))
            peak_iqr_hz = float(np.nanpercentile(peak, 75) - np.nanpercentile(peak, 25))

        rows.append(
            {
                "case": case_label(test_id),
                "nominal_power_W": CASE_MAP[test_id]["power_W"],
                "pressure_std_kPa": row["pressure_std_kPa"],
                "pressure_instrument_standard_uncertainty_kPa": (
                    PRESSURE_TRANSDUCER_FULL_SCALE_KPA
                    * PRESSURE_TRANSDUCER_ACCURACY_FRACTION_FULL_SCALE
                    / np.sqrt(3)
                ),
                "temperature_heat_flux_fit_mean_R2": summary.get("mean_R2_linear_fit", np.nan),
                "temperature_heat_flux_fit_min_R2": summary.get("min_R2_linear_fit", np.nan),
                "hydrophone_band_power_cv": hydro_power_cv,
                "hydrophone_time_bin_s": hydro_time_bin_s,
                "hydrophone_centroid_iqr_Hz": centroid_iqr_hz,
                "hydrophone_peak_frequency_iqr_Hz": peak_iqr_hz,
                "ae_waveform_available": bool(summary.get("ae_wfs_available", False)),
                "note": "Data-derived diagnostic with pre-submission instrument assumptions; replace with calibration-certificate values before submission.",
                **propagated_thermal_uncertainty(row["max_heat_flux_W_cm2"]),
            }
        )
    diagnostics = pd.DataFrame(rows)
    diagnostics.to_csv(output_dir / "uncertainty_diagnostics_publication.csv", index=False)
    return diagnostics


def write_uncertainty_budget(
    output_dir: Path,
    uncertainty_diagnostics: pd.DataFrame,
    ae_summary: pd.DataFrame,
    envelope: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for _, row in uncertainty_diagnostics.iterrows():
        case = row["case"]
        rows.extend(
            [
                {
                    "case": case,
                    "quantity": "wall_temperature",
                    "value": row["wall_temperature_expanded_uncertainty_C_k2"],
                    "unit": "degC",
                    "coverage": "expanded k=2",
                    "basis": "linear extrapolation of four thermocouples; Type-T/DAQ standard uncertainty assumed 0.50 degC",
                    "source_status": "pre-submission assumption",
                },
                {
                    "case": case,
                    "quantity": "heat_flux",
                    "value": row["heat_flux_expanded_uncertainty_W_cm2_k2"],
                    "unit": "W/cm^2",
                    "coverage": "expanded k=2",
                    "basis": "Fourier-law propagation from thermocouple uncertainty plus 2% copper thermal-conductivity standard uncertainty",
                    "source_status": "pre-submission assumption",
                },
                {
                    "case": case,
                    "quantity": "event_time",
                    "value": 2.0 * TIME_ALIGNMENT_STANDARD_UNCERTAINTY_S,
                    "unit": "s",
                    "coverage": "expanded k=2",
                    "basis": "wall-clock synchronization and time-bin/event-picking allowance",
                    "source_status": "pre-submission assumption",
                },
                {
                    "case": case,
                    "quantity": "hydrophone_band_power",
                    "value": 2.0
                    * np.sqrt(
                        (2 * HYDROPHONE_VOLTAGE_REL_STANDARD_UNCERTAINTY) ** 2
                        + (2 * HYDROPHONE_SENSITIVITY_REL_STANDARD_UNCERTAINTY) ** 2
                        + PSD_ESTIMATOR_REL_STANDARD_UNCERTAINTY**2
                    ),
                    "unit": "relative",
                    "coverage": "expanded k=2",
                    "basis": "voltage PSD power proxy; combines voltage, sensitivity, and PSD-estimator terms",
                    "source_status": "pre-submission assumption",
                },
                {
                    "case": case,
                    "quantity": "hydrophone_characteristic_frequency",
                    "value": max(row["hydrophone_time_bin_s"] ** -1 if row["hydrophone_time_bin_s"] else 0.0, 3.125),
                    "unit": "Hz",
                    "coverage": "resolution-scale",
                    "basis": "larger of time-window resolution and spectrogram bin-scale floor",
                    "source_status": "data-derived",
                },
            ]
        )
    for _, row in ae_summary.iterrows():
        case = row["case"]
        rows.extend(
            [
                {
                    "case": case,
                    "quantity": "ae_band_power",
                    "value": 2.0
                    * np.sqrt(
                        (2 * HYDROPHONE_VOLTAGE_REL_STANDARD_UNCERTAINTY) ** 2
                        + PSD_ESTIMATOR_REL_STANDARD_UNCERTAINTY**2
                    ),
                    "unit": "relative",
                    "coverage": "expanded k=2",
                    "basis": "AE waveform voltage PSD proxy; combines voltage-chain and PSD-estimator terms. Waveform files are available only for Cases C-D.",
                    "source_status": "pre-submission assumption",
                },
                {
                    "case": case,
                    "quantity": "ae_characteristic_frequency",
                    "value": 3.125,
                    "unit": "Hz",
                    "coverage": "resolution-scale",
                    "basis": "spectrogram/characteristic-frequency bin-scale floor. Waveform files are available only for Cases C-D.",
                    "source_status": "data-derived",
                },
            ]
        )
    if not envelope.empty:
        for _, row in envelope.iterrows():
            case = row["case"]
            signal_key = row["Signal key"]
            for quantity, unit in [
                ("envelope_asymptote", row["Y label"]),
                ("envelope_time_constant_s", "s"),
                ("envelope_saturation_fraction_at_end", "fraction"),
            ]:
                value = pd.to_numeric(row.get(quantity), errors="coerce")
                if not np.isfinite(value):
                    continue
                rows.append(
                    {
                        "case": case,
                        "quantity": f"{signal_key}_{quantity}",
                        "value": 2.0 * ENVELOPE_FIT_FLOOR_REL_STANDARD_UNCERTAINTY * abs(value),
                        "unit": unit,
                        "coverage": "expanded k=2",
                        "basis": "asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement",
                        "source_status": "pre-submission assumption",
                    }
                )
    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "uncertainty_budget_publication.csv", index=False)
    return table


def plot_boiling_curves(
    repo_root: Path,
    raw_root: Path,
    plots_dir: Path,
    summaries: dict[str, dict[str, object]],
) -> None:
    curves_path = repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "curves.csv"
    curves = pd.read_csv(curves_path)
    curves["case"] = curves["test_id"].map(lambda value: case_label(str(value)))

    for x_col, x_label, filename in [
        ("surface_temperature_C", r"Wall temperature, $T_{\mathrm{w}}$ ($^\circ$C)", "fig01a_heating_boiling_curve_wall_temperature.png"),
        ("wall_superheat_C", r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)", "fig01b_heating_boiling_curve_wall_superheat.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 8))
        for test_id in CASE_ORDER:
            label = case_label(test_id)
            case_curves = curves[curves["test_id"] == test_id]
            ax.plot(
                case_curves[x_col],
                case_curves["heat_flux_W_cm2"],
                label=power_label(test_id),
                color=CASE_COLORS[label],
                linewidth=2.4,
            )
        ax.set_xlabel(x_label)
        ax.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W/cm$^2$)")
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.legend(frameon=False, loc="best")
        fig.tight_layout()
        fig.savefig(plots_dir / filename)
        plt.close(fig)

    for x_key, x_label, filename in [
        ("surface_temperature_C", r"Wall temperature, $T_{\mathrm{w}}$ ($^\circ$C)", "fig01c_full_history_boiling_curve_wall_temperature.png"),
        ("wall_superheat_C", r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)", "fig01d_full_history_boiling_curve_wall_superheat.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 8))
        for test_id in CASE_ORDER:
            label = case_label(test_id)
            summary = summaries[test_id]
            data = load_thermal_case(raw_root, test_id)
            t_off = pd.to_numeric(summary.get("dc_shutoff_time_s", np.nan), errors="coerce")
            if not np.isfinite(t_off):
                power_on = np.interp(data["time_s"], data["dc_time_s"], data["dc_power_W"], left=0.0, right=0.0) > 0.0
                t_off = float(np.nanmax(data["time_s"][power_on])) if np.any(power_on) else float(np.nanmax(data["time_s"]))
            x_values = data["surface_temperature_C"]
            if x_key == "wall_superheat_C":
                x_values = x_values - float(summary.get("T_sat_C", np.nan))
            heating = data["time_s"] < float(t_off)
            cooling = ~heating
            ax.plot(
                x_values[heating],
                data["heat_flux_W_cm2"][heating],
                color=CASE_COLORS[label],
                linestyle="-",
                linewidth=2.6,
                label=f"{power_label(test_id)}, heating",
            )
            if np.any(cooling):
                ax.plot(
                    x_values[cooling],
                    data["heat_flux_W_cm2"][cooling],
                    color=CASE_COLORS[label],
                    linestyle="--",
                    linewidth=2.0,
                    alpha=0.9,
                    label=f"{power_label(test_id)}, cooling",
                )
        ax.set_xlabel(x_label)
        ax.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W/cm$^2$)")
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.legend(frameon=False, loc="best", fontsize=9)
        fig.tight_layout()
        fig.savefig(plots_dir / filename)
        plt.close(fig)


def plot_four_case_summary(case_summary: pd.DataFrame, hydro_summary: pd.DataFrame, plots_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True)
    colors = [CASE_COLORS[c] for c in case_summary["case"]]
    x = np.arange(len(case_summary))
    width = 0.36
    axes[0].bar(
        x - width / 2,
        case_summary["maximum_heat_flux_W_cm2"],
        width=width,
        color=colors,
        label=r"$q^{\prime\prime}_{\max}$",
    )
    axes[0].bar(
        x + width / 2,
        case_summary["q_DNB_plot_W_cm2"],
        width=width,
        color=colors,
        alpha=0.45,
        hatch="//",
        label=r"$q^{\prime\prime}_{\mathrm{DNB}}$",
    )
    for _, row in case_summary[~case_summary["dnb_resolved_for_plot"]].iterrows():
        index = int(case_summary.index[case_summary["case"] == row["case"]][0])
        axes[0].text(index + width / 2, 8, "not resolved", rotation=90, ha="center", va="bottom", fontsize=9)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(case_summary["power_label"], rotation=15, ha="right")
    axes[0].set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W/cm$^2$)")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.3)
    axes[0].legend(frameon=False, loc="best")

    hydro = hydro_summary.copy()
    hydro["dominant_slow_modulation_Hz"] = pd.to_numeric(
        hydro["dominant_slow_modulation_Hz"], errors="coerce"
    )
    missing_cases = []
    for _, row in hydro.iterrows():
        color = CASE_COLORS[row["case"]]
        if np.isfinite(row["dominant_slow_modulation_Hz"]):
            axes[1].scatter(
                row["nominal_power_W"],
                row["dominant_slow_modulation_Hz"],
                s=80,
                color=color,
                label=power_label_from_case(row["case"]),
            )
        else:
            missing_cases.append(power_label_from_case(row["case"]))
    axes[1].set_xlabel(r"Nominal power, $P_{\mathrm{load}}$ (W)")
    axes[1].set_ylabel("Dominant hydrophone slow modulation (Hz)")
    axes[1].grid(True, linestyle="--", alpha=0.3)
    axes[1].legend(frameon=False, loc="best")
    if missing_cases:
        axes[1].text(
            0.04,
            0.05,
            "Hydrophone pending: " + ", ".join(missing_cases),
            transform=axes[1].transAxes,
            fontsize=11,
            ha="left",
            va="bottom",
        )
    fig.savefig(plots_dir / "fig02_thermal_hydrophone_four_case_summary.png")
    plt.close(fig)


def plot_envelope_summary(envelope: pd.DataFrame, plots_dir: Path) -> None:
    if envelope.empty:
        return
    keep = envelope[envelope["Signal key"].isin(["wall_temperature", "heat_flux", "hydrophone_power"])].copy()
    label_map = {
        "wall_temperature": r"$T_{\mathrm{w}}$ envelope",
        "heat_flux": r"$q^{\prime\prime}$ envelope",
        "hydrophone_power": "Hydrophone power envelope",
    }
    keep["plot_label"] = keep["Signal key"].map(label_map)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    x = np.arange(len(keep["plot_label"].unique()))
    width = 0.35
    for offset, case in [(-width / 2, "Case C"), (width / 2, "Case D")]:
        data = keep[keep["case"] == case].set_index("plot_label")
        values = [data.loc[label, "envelope_time_constant_s"] for label in keep["plot_label"].unique()]
        axes[0].bar(x + offset, values, width=width, color=CASE_COLORS[case], label=case)
        sat_values = [
            data.loc[label, "envelope_saturation_fraction_at_end"]
            for label in keep["plot_label"].unique()
        ]
        axes[1].bar(x + offset, sat_values, width=width, color=CASE_COLORS[case], label=case)
    labels = list(keep["plot_label"].unique())
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.grid(True, axis="y", linestyle="--", alpha=0.3)
        ax.legend(frameon=False)
    axes[0].set_ylabel(r"Asymptotic time constant, $\tau$ (s)")
    axes[1].set_ylabel("Saturation fraction at shutoff")
    fig.tight_layout()
    fig.savefig(plots_dir / "fig06_envelope_metric_summary.png")
    plt.close(fig)


def load_literature_tables(literature_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    data_dir = literature_root / "examples" / "test2_meb" / "data"
    return pd.read_csv(data_dir / "combined_points.csv"), pd.read_csv(data_dir / "meb_regime_signatures.csv")


def plot_literature_comparison(
    combined: pd.DataFrame,
    signatures: pd.DataFrame,
    plots_dir: Path,
    output_dir: Path,
) -> None:
    points = combined.copy()
    points["heat_flux_W_cm2"] = np.where(
        points["y_unit"].str.contains("MW", na=False),
        points["y_value"] * 100.0,
        points["y_value"] / 1e4,
    )
    points["wall_superheat_K"] = points["x_value"]
    points["source_group"] = np.where(points["source_type"] == "user_experiment", "Present work", "Literature")
    points[["paper_id", "curve_id", "wall_superheat_K", "heat_flux_W_cm2", "source_group", "notes"]].to_csv(
        output_dir / "literature_boiling_curve_points_publication.csv",
        index=False,
    )

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for group, marker, color, alpha in [
        ("Literature", "o", "#4C78A8", 0.65),
        ("Present work", "s", "#F58518", 0.9),
    ]:
        data = points[points["source_group"] == group]
        ax.scatter(
            data["wall_superheat_K"],
            data["heat_flux_W_cm2"],
            label=group,
            marker=marker,
            color=color,
            alpha=alpha,
            edgecolor="none",
            s=42,
        )
    ax.set_xlabel(r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)")
    ax.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W/cm$^2$)")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(plots_dir / "fig07a_literature_boiling_curve_comparison.png")
    plt.close(fig)

    sig = signatures.copy()
    sig.to_csv(output_dir / "literature_signature_publication.csv", index=False)
    freq_rows = []
    for _, row in sig.iterrows():
        raw = row.get("frequency_Hz")
        if pd.isna(raw) or str(raw).strip() == "":
            continue
        for item in str(raw).replace(">", "").split(","):
            item = item.strip()
            if not item:
                continue
            try:
                freq_rows.append(
                    {
                        "source_type": row["source_type"],
                        "source_id": row["source_id"],
                        "frequency_Hz": float(item),
                        "frequency_type": row["frequency_type"],
                    }
                )
            except ValueError:
                continue
    freq = pd.DataFrame(freq_rows)
    if freq.empty:
        return
    freq["group"] = np.where(freq["source_type"] == "user_experiment", "Present work", "Literature")
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    y_positions = {"Present work": 0, "Literature": 1}
    for group, marker, color in [
        ("Present work", "s", "#F58518"),
        ("Literature", "o", "#4C78A8"),
    ]:
        data = freq[freq["group"] == group]
        jitter = np.linspace(-0.12, 0.12, max(len(data), 1))
        ax.scatter(
            data["frequency_Hz"],
            np.full(len(data), y_positions[group]) + jitter[: len(data)],
            marker=marker,
            color=color,
            alpha=0.8,
            s=58,
            label=group,
        )
    ax.set_xscale("log")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Present work", "Literature"])
    ax.set_xlabel("Reported frequency or modulation scale (Hz)")
    ax.grid(True, axis="x", which="both", linestyle="--", alpha=0.35)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(plots_dir / "fig07b_literature_frequency_scale_comparison.png")
    plt.close(fig)


def plot_final_ate_panels(
    output_dir: Path,
    case_summary: pd.DataFrame,
    hydro_summary: pd.DataFrame,
    envelope: pd.DataFrame,
    uncertainty_diagnostics: pd.DataFrame,
    budget: pd.DataFrame,
    combined: pd.DataFrame,
    signatures: pd.DataFrame,
) -> None:
    panels_dir = output_dir / "final_ate_panels"
    panels_dir.mkdir(parents=True, exist_ok=True)
    u_by_case = uncertainty_diagnostics.set_index("case")
    colors = [CASE_COLORS[c] for c in case_summary["case"]]

    panel_style = {
        "font.family": "Arial",
        "font.size": 8.0,
        "axes.labelsize": 8.5,
        "axes.titlesize": 8.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.2,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.25,
        "savefig.dpi": 600,
    }
    with plt.rc_context(panel_style):
        fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
        x_cases = np.arange(len(case_summary))
        bar_width = 0.36
        axes[0].bar(
            x_cases - bar_width / 2,
            case_summary["maximum_heat_flux_W_cm2"],
            yerr=[
                u_by_case.loc[c, "heat_flux_expanded_uncertainty_W_cm2_k2"]
                for c in case_summary["case"]
            ],
            width=bar_width,
            capsize=3,
            color=colors,
            edgecolor="black",
            linewidth=0.5,
            label=r"$q^{\prime\prime}_{\max}$",
        )
        axes[0].bar(
            x_cases + bar_width / 2,
            case_summary["q_DNB_plot_W_cm2"],
            width=bar_width,
            color=colors,
            alpha=0.45,
            edgecolor="black",
            linewidth=0.5,
            hatch="//",
            label=r"$q^{\prime\prime}_{\mathrm{DNB}}$",
        )
        for _, row in case_summary[~case_summary["dnb_resolved_for_plot"]].iterrows():
            index = int(case_summary.index[case_summary["case"] == row["case"]][0])
            axes[0].text(index + bar_width / 2, 10, "n.r.", ha="center", va="bottom", fontsize=6.8, rotation=90)
        axes[0].set_xticks(x_cases)
        axes[0].set_xticklabels(case_summary["power_label"], rotation=18, ha="right")
        axes[0].set_ylabel(r"$q^{\prime\prime}$ (W cm$^{-2}$)")
        axes[0].grid(True, axis="y", linestyle=":", alpha=0.45)
        axes[0].legend(frameon=False, loc="best", handletextpad=0.3)

        hydro = hydro_summary.copy()
        hydro["dominant_slow_modulation_Hz"] = pd.to_numeric(
            hydro["dominant_slow_modulation_Hz"], errors="coerce"
        )
        for _, row in hydro.iterrows():
            axes[1].scatter(
                row["nominal_power_W"],
                row["dominant_slow_modulation_Hz"],
                s=38,
                color=CASE_COLORS[row["case"]],
                edgecolor="black",
                linewidth=0.4,
                label=power_label_from_case(row["case"]),
            )
        axes[1].set_xlabel(r"$P_{\mathrm{load}}$ (W)")
        axes[1].set_ylabel("Hydrophone modulation (Hz)")
        axes[1].grid(True, linestyle=":", alpha=0.45)
        axes[1].legend(frameon=False, ncol=1, loc="best", handletextpad=0.3)
        add_external_panel_labels(fig, axes)
        fig.savefig(panels_dir / "fig01_ate_case_heat_flux_and_hydrophone_modulation.png")
        fig.savefig(panels_dir / "fig01_ate_case_heat_flux_and_hydrophone_modulation.pdf")
        plt.close(fig)

        if not envelope.empty:
            keep = envelope[
                envelope["Signal key"].isin(["wall_temperature", "heat_flux", "hydrophone_power"])
            ].copy()
            label_map = {
                "wall_temperature": r"$T_{\mathrm{w}}$",
                "heat_flux": r"$q^{\prime\prime}$",
                "hydrophone_power": "Hydrophone",
            }
            keep["plot_label"] = keep["Signal key"].map(label_map)
            labels = list(dict.fromkeys(keep["plot_label"]))
            x = np.arange(len(labels))
            fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.35), constrained_layout=True)
            width = 0.36
            for offset, case in [(-width / 2, "Case C"), (width / 2, "Case D")]:
                data = keep[keep["case"] == case].set_index("plot_label")
                tau = [data.loc[label, "envelope_time_constant_s"] for label in labels]
                tau_err = [ENVELOPE_FIT_FLOOR_REL_STANDARD_UNCERTAINTY * value for value in tau]
                sat = [data.loc[label, "envelope_saturation_fraction_at_end"] for label in labels]
                axes[0].bar(
                    x + offset,
                    tau,
                    yerr=tau_err,
                    width=width,
                    capsize=3,
                    color=CASE_COLORS[case],
                    edgecolor="black",
                    linewidth=0.5,
                    label=case,
                )
                axes[1].bar(
                    x + offset,
                    sat,
                    width=width,
                    color=CASE_COLORS[case],
                    edgecolor="black",
                    linewidth=0.5,
                    label=case,
                )
            for i, ax in enumerate(axes):
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=12, ha="right")
                ax.grid(True, axis="y", linestyle=":", alpha=0.45)
                ax.legend(frameon=False, loc="best", handletextpad=0.3)
            axes[0].set_ylabel(r"$\tau$ (s)")
            axes[1].set_ylabel("Saturation fraction")
            add_external_panel_labels(fig, axes)
            fig.savefig(panels_dir / "fig02_ate_envelope_metrics.png")
            fig.savefig(panels_dir / "fig02_ate_envelope_metrics.pdf")
            plt.close(fig)

        points = combined.copy()
        points["heat_flux_W_cm2"] = np.where(
            points["y_unit"].str.contains("MW", na=False),
            points["y_value"] * 100.0,
            points["y_value"] / 1e4,
        )
        points["source_group"] = np.where(
            points["source_type"] == "user_experiment", "Present work", "Literature"
        )
        fig, ax = plt.subplots(figsize=(3.55, 3.25), constrained_layout=True)
        for group, marker, color in [
            ("Literature", "o", "#4C78A8"),
            ("Present work", "s", "#F58518"),
        ]:
            data = points[points["source_group"] == group]
            ax.scatter(
                data["x_value"],
                data["heat_flux_W_cm2"],
                marker=marker,
                s=18,
                color=color,
                edgecolor="none",
                alpha=0.75,
                label=group,
            )
        ax.set_xlabel(r"$\Delta T_{\mathrm{w}}$ (K)")
        ax.set_ylabel(r"$q^{\prime\prime}$ (W cm$^{-2}$)")
        ax.grid(True, linestyle=":", alpha=0.45)
        ax.legend(frameon=False, loc="best", handletextpad=0.3)
        fig.savefig(panels_dir / "fig03_ate_literature_boiling_curve_context.png")
        fig.savefig(panels_dir / "fig03_ate_literature_boiling_curve_context.pdf")
        plt.close(fig)

    captions = [
        "# Final Applied Thermal Engineering Figure Panels",
        "",
        "These panels are generated by `scripts/run_manuscript_publication_analysis.py` for manuscript review. They use case labels rather than internal test IDs.",
        "",
        "## Fig. 1. Case-level thermal and hydrophone response",
        "",
        "Panel (a) compares the maximum reconstructed heat flux during active heating with the heat flux at the extracted DNB-associated event time. Error bars on `q''_max` show the expanded uncertainty (k = 2) from the pre-submission heat-flux uncertainty budget, including thermocouple propagation and a 2% standard uncertainty assigned to copper thermal conductivity. Unresolved DNB markers are labeled `n.r.` rather than plotted as misleading values. Panel (b) reports the dominant slow modulation frequency extracted from the band-integrated hydrophone power for all four power loads. Hydrophone PSD integration was performed in linear units over the stored hydrophone band before converting any values to dB.",
        "",
        "Files: `final_ate_panels/fig01_ate_case_heat_flux_and_hydrophone_modulation.png` and `.pdf`",
        "",
        "## Fig. 2. Envelope-fit metrics for developed high-power cases",
        "",
        "Panel (a) gives the asymptotic envelope time constant for wall temperature, heat flux, and hydrophone band-integrated power. Error bars show a provisional 10% relative fit-uncertainty floor pending bootstrap or covariance-based refinement. Panel (b) reports the saturation fraction at the end of the active-heating analysis window. AE waveform analysis remains limited to Cases C-D and is used as a separate confirmation of the slow modulation scale.",
        "",
        "Files: `final_ate_panels/fig02_ate_envelope_metrics.png` and `.pdf`",
        "",
        "## Fig. 3. Literature context for MEB heat-transfer scale",
        "",
        "The literature points are first-pass extracted values from `literature-compiler/examples/test2_meb`; values marked as reported text or range endpoints require final figure/table digitization and source-specific uncertainty notes before submission. Present-work points are heating-only BoilingLab values converted to the same wall-superheat and heat-flux units.",
        "",
        "Files: `final_ate_panels/fig03_ate_literature_boiling_curve_context.png` and `.pdf`",
        "",
    ]
    (panels_dir / "captions.md").write_text("\n".join(captions), encoding="utf-8")


def write_literature_digitization_priority(output_dir: Path) -> pd.DataFrame:
    rows = [
        {
            "priority": 1,
            "ref_id": "tang_2016_transition_to_meb",
            "target_data": "MEB transition heat flux, wall superheat, bubble-collapse/growth frequency",
            "figure_or_table_target": "transition boiling curves and microbubble tracking figures",
            "submission_use": "Primary comparison for transition from nucleate boiling to MEB",
            "status": "needs figure-level digitization",
        },
        {
            "priority": 1,
            "ref_id": "horiuchi_2019_transient_nucleate_to_meb",
            "target_data": "Transient MEB onset heat flux and wall superheat",
            "figure_or_table_target": "reported transition/onset data and transient boiling curves",
            "submission_use": "Compare event markers and transient heating pathway",
            "status": "needs figure-level digitization",
        },
        {
            "priority": 1,
            "ref_id": "horiuchi_2021_spatial_temporal_thermal_fluid",
            "target_data": "C-MEB/S-MEB heat flux ranges, wall superheat ranges, sound frequencies",
            "figure_or_table_target": "MEB state map, heat-flux ranges, sound-frequency figures",
            "submission_use": "Interpret oscillatory state and frequency definitions",
            "status": "needs range verification",
        },
        {
            "priority": 1,
            "ref_id": "ono_2023_acoustic_state_detection_meb",
            "target_data": "Acoustic state labels, hydrophone sampling/bandwidth, heat flux range",
            "figure_or_table_target": "state-detection and heat-transfer condition tables",
            "submission_use": "Benchmark acoustic-classification context",
            "status": "needs table/figure verification",
        },
        {
            "priority": 2,
            "ref_id": "kobayashi_2022_on_homogeneity_of_vapor_bubble",
            "target_data": "Boiling sound frequency, vapor-bubble oscillation homogeneity, heat-transfer state",
            "figure_or_table_target": "boiling sound and heat-transfer characteristic figures",
            "submission_use": "Separate high-frequency sound/bubble metrics from slow envelope modulation",
            "status": "needs frequency-definition verification",
        },
        {
            "priority": 2,
            "ref_id": "tang_2018_sound_emission_subcooled_pool",
            "target_data": "Sound spectral peaks, subcooling, heater size, boiling state",
            "figure_or_table_target": "sound-emission spectra and boiling-condition tables",
            "submission_use": "Hydrophone/sound comparison for spectral content",
            "status": "needs source-key/name verification and figure digitization",
        },
        {
            "priority": 2,
            "ref_id": "zhu_2014_visualized_meb",
            "target_data": "Visualized MEB heat flux, subcooling, boiling-sound peak",
            "figure_or_table_target": "visualized MEB condition figures and sound result",
            "submission_use": "Mechanistic visualization context",
            "status": "needs figure-level digitization",
        },
        {
            "priority": 2,
            "ref_id": "unno_2022_surface_properties_meb_onset",
            "target_data": "MEB onset wall superheat versus surface condition",
            "figure_or_table_target": "onset wall-superheat plots/tables",
            "submission_use": "Surface-condition sensitivity and onset comparison",
            "status": "needs source-specific uncertainty notes",
        },
        {
            "priority": 2,
            "ref_id": "unno_2025_reduced_pressure_confined_meb",
            "target_data": "Reduced-pressure confined-vessel MEB onset pressure and heat-transfer condition",
            "figure_or_table_target": "reduced-pressure onset figures/tables",
            "submission_use": "Compare subatmospheric/reduced-pressure relevance",
            "status": "needs figure-level digitization",
        },
        {
            "priority": 3,
            "ref_id": "zhao_2025_open_microchannel_meb",
            "target_data": "Flow MEB heat flux and wall superheat in open microchannels",
            "figure_or_table_target": "microchannel boiling curves and durability plots",
            "submission_use": "Context only; different geometry from pool boiling",
            "status": "needs geometry-separated extraction",
        },
    ]
    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "literature_digitization_priority_publication.csv", index=False)
    return table


def write_literature_digitized_tables(
    output_dir: Path,
    combined: pd.DataFrame,
    signatures: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Write normalized literature tables used by final manuscript figures.

    These tables preserve the current extraction method so first-pass text/range
    values are not confused with completed figure-digitized curves.
    """
    lit_points = combined[combined["source_type"] != "user_experiment"].copy()
    lit_points["wall_superheat_K"] = pd.to_numeric(lit_points["x_value"], errors="coerce")
    lit_points["heat_flux_W_cm2"] = np.where(
        lit_points["y_unit"].str.contains("MW", na=False),
        pd.to_numeric(lit_points["y_value"], errors="coerce") * 100.0,
        pd.to_numeric(lit_points["y_value"], errors="coerce") / 1e4,
    )
    lit_points["digitization_status"] = np.select(
        [
            lit_points["extraction_method"].str.contains("digit", case=False, na=False),
            lit_points["extraction_method"].str.contains("range", case=False, na=False),
        ],
        ["figure_digitized_or_curve_point", "reported_range_endpoint"],
        default="reported_text_or_first_pass_extraction",
    )
    lit_points["recommended_use"] = np.where(
        lit_points["digitization_status"].eq("reported_range_endpoint"),
        "Use as regime envelope only",
        "Use as boiling-curve/onset comparison after source verification",
    )
    point_cols = [
        "paper_id",
        "curve_id",
        "figure_id",
        "wall_superheat_K",
        "heat_flux_W_cm2",
        "digitization_status",
        "recommended_use",
        "notes",
    ]
    lit_points = lit_points[point_cols].sort_values(["paper_id", "curve_id"]).reset_index(drop=True)
    lit_points.to_csv(output_dir / "literature_digitized_boiling_points_publication.csv", index=False)

    onset = signatures.copy()
    if not onset.empty:
        onset["frequency_Hz"] = pd.to_numeric(onset.get("frequency_Hz"), errors="coerce")
        onset["heat_flux_W_cm2"] = pd.to_numeric(onset.get("heat_flux_W_cm2"), errors="coerce")
        onset["wall_superheat_K"] = pd.to_numeric(onset.get("wall_superheat_K"), errors="coerce")
        onset["digitization_status"] = np.where(
            onset["source_type"].eq("user_experiment"),
            "present_work_reduced_data",
            "literature_reported_or_first_pass_extraction",
        )
        onset_cols = [
            col
            for col in [
                "source_id",
                "source_type",
                "signature_type",
                "wall_superheat_K",
                "heat_flux_W_cm2",
                "frequency_Hz",
                "digitization_status",
                "notes",
            ]
            if col in onset.columns
        ]
        onset = onset[onset_cols].reset_index(drop=True)
    onset.to_csv(output_dir / "literature_onset_signature_values_publication.csv", index=False)
    return lit_points, onset


def write_summary_markdown(
    output_dir: Path,
    availability: pd.DataFrame,
    case_summary: pd.DataFrame,
    hydro_summary: pd.DataFrame,
    ae_summary: pd.DataFrame,
    uncertainty_diagnostics: pd.DataFrame,
    digitization_priority: pd.DataFrame,
    uncertainty_budget: pd.DataFrame,
    literature_points: pd.DataFrame,
    literature_onsets: pd.DataFrame,
) -> None:
    def markdown_table(frame: pd.DataFrame, float_format: str | None = None) -> str:
        if frame.empty:
            return ""
        headers = list(frame.columns)
        rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for _, row in frame.iterrows():
            values = []
            for header in headers:
                value = row[header]
                if isinstance(value, float) and float_format is not None and np.isfinite(value):
                    values.append(format(value, float_format))
                else:
                    values.append("" if pd.isna(value) else str(value))
            rows.append("| " + " | ".join(values) + " |")
        return "\n".join(rows)

    unavailable_hydro = availability.loc[
        ~availability["hydrophone_intermediate_available"], "case"
    ].tolist()
    lines = [
        "# Manuscript Publication Analysis",
        "",
        "Target journal: Applied Thermal Engineering.",
        "",
        "This folder contains publication-facing summary tables and plots generated from",
        "BoilingLab intermediates and the `literature-compiler/examples/test2_meb` dataset.",
        "Case labels are used for manuscript-facing outputs.",
        "",
        "## Data coverage",
        "",
        markdown_table(availability),
        "",
        "Thermal comparison is available for all four cases. Hydrophone analysis is",
        "available for all four cases after regenerating Case A from raw data.",
        "AE waveform analysis is intentionally limited to Cases C and D because those",
        "are the only cases with AE waveform files available in the current dataset.",
        "",
    ]
    if unavailable_hydro:
        lines.extend(
            [
                "## Regeneration note",
                "",
                "Generated hydrophone intermediate files are missing for: "
                + ", ".join(unavailable_hydro)
                + ". Regenerate the single-case workflow from raw data when the raw-data",
                "drive is mounted to complete the fully consistent four-case hydrophone analysis.",
                "",
            ]
        )
    lines.extend(
        [
            "## Key thermal summary",
            "",
            markdown_table(case_summary, ".3g"),
            "",
            "## Hydrophone summary",
            "",
            markdown_table(hydro_summary, ".3g"),
            "",
            "## AE waveform summary",
            "",
            markdown_table(ae_summary, ".3g") if not ae_summary.empty else "No AE waveform rows found.",
            "",
            "## First-pass uncertainty and quality diagnostics",
            "",
            markdown_table(uncertainty_diagnostics, ".3g"),
            "",
            "## Propagated uncertainty budget",
            "",
            markdown_table(uncertainty_budget, ".3g"),
            "",
            "## Literature digitization priority",
            "",
            markdown_table(digitization_priority),
            "",
            "## Normalized literature extraction tables",
            "",
            "`literature_digitized_boiling_points_publication.csv` contains normalized",
            "wall-superheat and heat-flux values from the current `test2_meb`",
            "compilation, with status labels that distinguish source-reported values,",
            "range endpoints, and any figure-digitized curve points.",
            "`literature_onset_signature_values_publication.csv` contains onset and",
            "frequency/signature values used to compare literature MEB behavior with",
            "the present hydrophone modulation metrics.",
            "",
            markdown_table(literature_points.head(12), ".3g"),
            "",
            markdown_table(literature_onsets.head(12), ".3g") if not literature_onsets.empty else "",
            "",
            "## Final ATE panels",
            "",
            "- `final_ate_panels/fig01_ate_case_heat_flux_and_hydrophone_modulation.png`",
            "- `final_ate_panels/fig02_ate_envelope_metrics.png`",
            "- `final_ate_panels/fig03_ate_literature_boiling_curve_context.png`",
            "- `final_ate_panels/captions.md`",
            "",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_analysis_history(output_dir: Path) -> None:
    plots = [
        "plots/fig01a_heating_boiling_curve_wall_temperature.png",
        "plots/fig01b_heating_boiling_curve_wall_superheat.png",
        "plots/fig01c_full_history_boiling_curve_wall_temperature.png",
        "plots/fig01d_full_history_boiling_curve_wall_superheat.png",
        "plots/fig02_thermal_hydrophone_four_case_summary.png",
        "plots/fig06_envelope_metric_summary.png",
        "plots/fig07a_literature_boiling_curve_comparison.png",
        "plots/fig07b_literature_frequency_scale_comparison.png",
        "final_ate_panels/fig01_ate_case_heat_flux_and_hydrophone_modulation.png",
        "final_ate_panels/fig02_ate_envelope_metrics.png",
        "final_ate_panels/fig03_ate_literature_boiling_curve_context.png",
    ]
    text = [
        "# Analysis History",
        "",
        "This file records reproducible analysis steps and intermediate outputs used to update the manuscript. It is an audit trail of commands, data coverage, and interpretation checkpoints.",
        "",
        "## 2026-06-12 pre-submission update",
        "",
        "1. Regenerated Case A single-case outputs after the raw-data drive was mounted.",
        "",
        "```powershell",
        "python scripts\\run_single_case_demo.py --test-id Boiling-412 --raw-root \"Y:\\0_Ishraq\\New Pool Boiling Video\" --applied-heat-load 150 --subcooling 40 --skip-wfs",
        "```",
        "",
        "Key result: Case A now has hydrophone spectrogram, band-integrated power, characteristic-frequency CSV, and related hydrophone plots. AE waveform analysis remains unavailable for Cases A-B because waveform files are not present.",
        "",
        "2. Refreshed publication-facing manuscript tables and figures.",
        "",
        "```powershell",
        "python scripts\\run_manuscript_publication_analysis.py",
        "```",
        "",
        "3. Generated/updated these manuscript-facing plots:",
        "",
    ]
    text.extend(f"- `{plot}`" for plot in plots)
    text.extend(
        [
            "",
            "4. Data-coverage checkpoint:",
            "",
            "- Thermal comparison: Cases A-D.",
            "- Hydrophone comparison: Cases A-D after Case A regeneration.",
            "- AE waveform comparison: Cases C-D only.",
            "- Literature comparison: first-pass `test2_meb` compilation; still needs final figure/table digitization and source-specific uncertainty notes before submission.",
            "- A source-by-source digitization queue is saved as `literature_digitization_priority_publication.csv`.",
            "- Normalized literature boiling points and onset/signature values are saved as `literature_digitized_boiling_points_publication.csv` and `literature_onset_signature_values_publication.csv`; status labels distinguish source-reported values, range endpoints, and any figure-digitized values.",
            "",
            "5. Uncertainty checkpoint:",
            "",
            "A pre-submission uncertainty/quality diagnostics table was generated as `uncertainty_diagnostics_publication.csv`. A propagated quantity-level budget is saved as `uncertainty_budget_publication.csv`, including wall temperature, heat flux, event time, hydrophone band power, and characteristic frequency. Manufacturer calibration-certificate values should replace the current source-labeled assumptions before journal submission.",
            "",
            "6. Final figure panel checkpoint:",
            "",
            "Applied Thermal Engineering style review panels were generated in `final_ate_panels/` with case labels, consistent typography, and provisional uncertainty representation where available. Captions are stored in `final_ate_panels/captions.md`.",
            "",
        ]
    )
    (output_dir / "analysis_history.md").write_text("\n".join(text), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--raw-root", default=r"Y:\0_Ishraq\New Pool Boiling Video")
    parser.add_argument(
        "--literature-root",
        default=r"C:\Users\hanhu\Documents\New project 2\literature-compiler",
    )
    parser.add_argument(
        "--output-dir",
        default=r"manuscripts\meb_multimodal_diagnostics\generated\publication_analysis",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    set_style()

    repo_root = Path(args.repo_root).resolve()
    raw_root = Path(args.raw_root).resolve()
    literature_root = Path(args.literature_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    multi_summary, summaries = load_case_summaries(repo_root)
    case_summary = write_publication_case_summary(output_dir, multi_summary, summaries)
    availability = write_sensor_availability(output_dir, summaries, repo_root)
    hydro_summary, ae_summary = write_acoustic_summary(output_dir, summaries, repo_root)
    envelope = write_envelope_summary(output_dir, repo_root)
    uncertainty_diagnostics = write_uncertainty_diagnostics(output_dir, summaries, repo_root, multi_summary)
    uncertainty_budget = write_uncertainty_budget(output_dir, uncertainty_diagnostics, ae_summary, envelope)

    plot_boiling_curves(repo_root, raw_root, plots_dir, summaries)
    plot_four_case_summary(case_summary, hydro_summary, plots_dir)
    plot_envelope_summary(envelope, plots_dir)

    combined, signatures = load_literature_tables(literature_root)
    plot_literature_comparison(combined, signatures, plots_dir, output_dir)
    digitization_priority = write_literature_digitization_priority(output_dir)
    literature_points, literature_onsets = write_literature_digitized_tables(
        output_dir,
        combined,
        signatures,
    )
    plot_final_ate_panels(
        output_dir,
        case_summary,
        hydro_summary,
        envelope,
        uncertainty_diagnostics,
        uncertainty_budget,
        combined,
        signatures,
    )

    write_summary_markdown(
        output_dir,
        availability,
        case_summary,
        hydro_summary,
        ae_summary,
        uncertainty_diagnostics,
        digitization_priority,
        uncertainty_budget,
        literature_points,
        literature_onsets,
    )
    write_analysis_history(output_dir)
    print(f"Wrote publication analysis to {output_dir}")


if __name__ == "__main__":
    main()
