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


CASE_MAP = {
    "Boiling-412": {"case": "Case A", "power_W": 150.0},
    "Boiling-413": {"case": "Case B", "power_W": 180.0},
    "Boiling-416": {"case": "Case C", "power_W": 230.0},
    "Boiling-417": {"case": "Case D", "power_W": 250.0},
}

CASE_ORDER = list(CASE_MAP)
CASE_COLORS = {
    "Case A": "#355C7D",
    "Case B": "#6C5B7B",
    "Case C": "#C06C84",
    "Case D": "#F67280",
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


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_case_summaries(repo_root: Path) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    multi_summary_path = repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "summary.csv"
    multi_summary = pd.read_csv(multi_summary_path)
    summaries: dict[str, dict[str, object]] = {}
    for test_id in CASE_ORDER:
        summaries[test_id] = load_json(repo_root / "demos" / test_id / "generated" / "summary.json")
    return multi_summary, summaries


def write_publication_case_summary(output_dir: Path, multi_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in multi_summary.iterrows():
        test_id = str(row["test_id"])
        rows.append(
            {
                "case": case_label(test_id),
                "nominal_power_W": CASE_MAP[test_id]["power_W"],
                "mean_pressure_kPa": row["pressure_mean_kPa"],
                "pressure_std_kPa": row["pressure_std_kPa"],
                "mean_liquid_temperature_C": row["mean_liquid_temp_C"],
                "saturation_temperature_C": row["T_sat_C"],
                "subcooling_K": row["T_sat_C"] - row["mean_liquid_temp_C"],
                "maximum_heat_flux_W_cm2": row["max_heat_flux_W_cm2"],
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


def plot_boiling_curves(repo_root: Path, plots_dir: Path) -> None:
    curves_path = repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "curves.csv"
    curves = pd.read_csv(curves_path)
    curves["case"] = curves["test_id"].map(lambda value: case_label(str(value)))

    for x_col, x_label, filename in [
        ("surface_temperature_C", r"Wall temperature, $T_{\mathrm{w}}$ (°C)", "fig01a_boiling_curve_wall_temperature.png"),
        ("wall_superheat_C", r"Wall superheat, $\Delta T_{\mathrm{w}}$ (°C)", "fig01b_boiling_curve_wall_superheat.png"),
    ]:
        fig, ax = plt.subplots(figsize=(9, 8))
        for test_id in CASE_ORDER:
            label = case_label(test_id)
            case_curves = curves[curves["test_id"] == test_id]
            ax.plot(
                case_curves[x_col],
                case_curves["heat_flux_W_cm2"],
                label=label,
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


def plot_four_case_summary(case_summary: pd.DataFrame, hydro_summary: pd.DataFrame, plots_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True)
    colors = [CASE_COLORS[c] for c in case_summary["case"]]
    axes[0].bar(case_summary["case"], case_summary["maximum_heat_flux_W_cm2"], color=colors)
    axes[0].set_ylabel(r"Maximum heat flux, $q^{\prime\prime}_{\max}$ (W/cm$^2$)")
    axes[0].set_xlabel("Case")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.3)

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
                label=row["case"],
            )
        else:
            missing_cases.append(row["case"])
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


def write_summary_markdown(
    output_dir: Path,
    availability: pd.DataFrame,
    case_summary: pd.DataFrame,
    hydro_summary: pd.DataFrame,
    ae_summary: pd.DataFrame,
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
        "included where generated hydrophone intermediate CSV files are present.",
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
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
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
    literature_root = Path(args.literature_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    multi_summary, summaries = load_case_summaries(repo_root)
    case_summary = write_publication_case_summary(output_dir, multi_summary)
    availability = write_sensor_availability(output_dir, summaries, repo_root)
    hydro_summary, ae_summary = write_acoustic_summary(output_dir, summaries, repo_root)
    envelope = write_envelope_summary(output_dir, repo_root)

    plot_boiling_curves(repo_root, plots_dir)
    plot_four_case_summary(case_summary, hydro_summary, plots_dir)
    plot_envelope_summary(envelope, plots_dir)

    combined, signatures = load_literature_tables(literature_root)
    plot_literature_comparison(combined, signatures, plots_dir, output_dir)

    write_summary_markdown(output_dir, availability, case_summary, hydro_summary, ae_summary)
    print(f"Wrote publication analysis to {output_dir}")


if __name__ == "__main__":
    main()
