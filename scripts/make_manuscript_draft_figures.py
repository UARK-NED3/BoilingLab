"""Generate draft manuscript figures for the MEB diagnostics paper.

The figures in this script follow the manuscript figure plan. They are intended
as review drafts, not the final camera-ready artwork.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_single_case_demo import compute_temperature_quantities, parse_lvm_start_time_seconds, read_lvm


CASE_IDS = ["Boiling-412", "Boiling-413", "Boiling-416", "Boiling-417"]
CASE_LABELS = {
    "Boiling-412": r"$P_{\mathrm{load}}$ = 150 W",
    "Boiling-413": r"$P_{\mathrm{load}}$ = 180 W",
    "Boiling-416": r"$P_{\mathrm{load}}$ = 230 W",
    "Boiling-417": r"$P_{\mathrm{load}}$ = 250 W",
}
CASE_COLORS = {
    "Boiling-412": "#3B6688",
    "Boiling-413": "#756483",
    "Boiling-416": "#BF6B85",
    "Boiling-417": "#F2697A",
}
CASE_BY_POWER_LABEL = {label: test_id for test_id, label in CASE_LABELS.items()}
SOURCE_LABELS = {
    "horiuchi_2019_transient_nucleate_to_meb": "Horiuchi et al. 2019",
    "horiuchi_2021_spatiotemporal_meb": "Horiuchi et al. 2021",
    "inada_2016_cavitation_bubble_blow_pit": "Inada et al. 2016",
    "sinha_2021_deep_learning_sound_boiling": "Sinha et al. 2021",
    "tang_2016_transition_to_meb": "Ando et al. 2016",
    "zeigarnik_2012_microbubble_emission_nature": "Zeigarnik et al. 2012",
    "zhu_2014_visualized_meb": "Zhu et al. 2014",
    "ono_2023_acoustic_state_detection_meb": "Ono et al. 2023",
    "kobayashi_2022_homogeneity_boiling_sound_meb": "Kobayashi et al. 2022",
    "zhou_2018_sound_emission_subcooled_pool": "Zhou et al. 2018",
    "kobayashi_2024_reduced_pressure_confined_meb": "Kobayashi et al. 2024",
    "zhao_2025_open_microchannel_meb": "Zhao et al. 2025",
}
THERMOCOUPLE_LABELS = [r"$T_{\mathrm{TC1}}$", r"$T_{\mathrm{TC2}}$", r"$T_{\mathrm{TC3}}$", r"$T_{\mathrm{TC4}}$"]


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 9,
            "axes.labelsize": 10,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "savefig.dpi": 300,
        }
    )


def load_summary(repo_root: Path, test_id: str) -> dict[str, object]:
    path = repo_root / "demos" / test_id / "generated" / "summary.json"
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
        "thermocouples": temp_data["thermocouples"],
        "surface_temperature_C": temp_data["surface_temperature"],
        "heat_flux_W_cm2": temp_data["heat_flux"],
        "dc_time_s": dc_time[finite][order],
        "dc_power_W": dc_power[finite][order],
    }


def add_event_lines(ax: plt.Axes, summary: dict[str, object]) -> None:
    ymax = ax.get_ylim()[1]
    ymin = ax.get_ylim()[0]
    y = ymin + 0.08 * (ymax - ymin)
    for key, label, dx, ha in [
        ("dnb_time_s", r"$t_{\mathrm{DNB}}$", -2.0, "right"),
        ("peak_time_s", r"$t_{\mathrm{peak}}$", 2.0, "left"),
        ("oscillation_peak_time_s", r"$t_{\mathrm{osc}}$", 2.0, "left"),
        ("dc_shutoff_time_s", r"$t_{\mathrm{off}}$", -2.0, "right"),
    ]:
        value = summary.get(key)
        if value is None or not np.isfinite(float(value)):
            continue
        x = float(value)
        ax.axvline(x, color="0.25", linestyle="--", linewidth=0.8, alpha=0.8, label="_nolegend_")
        ax.text(x + dx, y, label, rotation=90, va="bottom", ha=ha, fontsize=8, color="0.2")


def add_external_panel_label(fig: plt.Figure, ax: plt.Axes, label: str) -> None:
    bbox = ax.get_position()
    fig.text(
        max(0.005, bbox.x0 - 0.052),
        min(0.995, bbox.y1 + 0.01),
        label,
        ha="left",
        va="bottom",
        fontsize=10,
    )


def save_png_pdf(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def figure_1_boiling_curves(repo_root: Path, output_dir: Path) -> None:
    curves = pd.read_csv(repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "curves.csv")
    curves["case"] = curves["test_id"].map(CASE_LABELS)
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
    for test_id in CASE_IDS:
        case = CASE_LABELS[test_id]
        data = curves[curves["test_id"] == test_id]
        axes[0].plot(data["surface_temperature_C"], data["heat_flux_W_cm2"], color=CASE_COLORS[test_id], label=case)
        axes[1].plot(data["wall_superheat_C"], data["heat_flux_W_cm2"], color=CASE_COLORS[test_id], label=case)
    axes[0].set_xlabel(r"Wall temperature, $T_{\mathrm{w}}$ ($^\circ$C)")
    axes[1].set_xlabel(r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)")
    for i, ax in enumerate(axes):
        ax.text(0.02, 0.98, f"({chr(97 + i)})", transform=ax.transAxes, ha="left", va="top")
        ax.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W cm$^{-2}$)")
        ax.grid(True, linestyle=":", alpha=0.45)
    axes[1].legend(frameon=False, ncol=1, loc="best")
    save_png_pdf(fig, output_dir / "fig01_heating_boiling_curves")


def figure_thermal_case(raw_root: Path, repo_root: Path, output_dir: Path, test_id: str, figure_name: str) -> None:
    summary = load_summary(repo_root, test_id)
    data = load_thermal_case(raw_root, test_id)
    fig, axes = plt.subplots(2, 1, figsize=(7.25, 5.2), sharex=True, constrained_layout=True)
    heat_line = axes[0].plot(
        data["time_s"],
        data["heat_flux_W_cm2"],
        color="#C44E52",
        linewidth=1.0,
        label=r"$q^{\prime\prime}$",
    )
    axp = axes[0].twinx()
    power_line = axp.plot(data["dc_time_s"], data["dc_power_W"], color="0.2", linewidth=0.85, label=r"$P_{\mathrm{load}}$")
    axes[0].set_ylabel(r"$q^{\prime\prime}$ (W cm$^{-2}$)")
    axp.set_ylabel(r"$P_{\mathrm{load}}$ (W)")
    axes[0].grid(True, linestyle=":", alpha=0.45)
    add_event_lines(axes[0], summary)
    lines = heat_line + power_line
    axes[0].legend(lines, [line.get_label() for line in lines], frameon=False, loc="upper right")

    for i, label in enumerate(THERMOCOUPLE_LABELS):
        axes[1].plot(data["time_s"], data["thermocouples"][:, i], linewidth=0.8, label=label)
    axes[1].plot(
        data["time_s"],
        data["surface_temperature_C"],
        color="black",
        linewidth=1.1,
        label=r"$T_{\mathrm{w}}$",
    )
    axes[1].set_ylabel(r"Temperature, $T$ ($^\circ$C)")
    axes[1].set_xlabel(r"Time, $t$ (s)")
    axes[1].grid(True, linestyle=":", alpha=0.45)
    axes[1].legend(frameon=False, loc="upper right", ncol=1)
    add_event_lines(axes[1], summary)
    fig.canvas.draw()
    for i, ax in enumerate(axes):
        add_external_panel_label(fig, ax, f"({chr(97 + i)})")
        ax.set_xlim(0, float(np.nanmax(data["time_s"])))
    save_png_pdf(fig, output_dir / figure_name)


def load_power_and_frequency(repo_root: Path, test_id: str, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = repo_root / "demos" / test_id / "generated"
    if prefix == "hydrophone":
        power = pd.read_csv(base / "hydrophone_band_integrated_power.csv")
        freq = pd.read_csv(base / "hydrophone_characteristic_frequencies.csv")
        power = power.rename(
            columns={
                "Band-integrated hydrophone power proxy (dB re V^2)": "power_db",
                "Band-integrated hydrophone power proxy (V^2)": "power_v2",
            }
        )
    else:
        power = pd.read_csv(base / "ae_wfs_band_integrated_power.csv")
        freq = pd.read_csv(base / "ae_wfs_characteristic_frequencies.csv")
        power = power.rename(
            columns={
                "Band-integrated AE waveform power proxy (dB re V^2)": "power_db",
                "Band-integrated AE waveform power proxy (V^2)": "power_v2",
            }
        )
    return power, freq


def figure_4_hydrophone(repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.2), constrained_layout=True)
    for ax, test_id in zip(axes[0], ["Boiling-416", "Boiling-417"]):
        image = mpimg.imread(repo_root / "demos" / test_id / "generated" / "plots" / "hydrophone_spectrogram.png")
        ax.imshow(image)
        ax.axis("off")
        ax.text(
            0.03,
            0.93,
            CASE_LABELS[test_id],
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8,
            color="black",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.65, "pad": 1.5},
        )
    for test_id in CASE_IDS:
        case = CASE_LABELS[test_id]
        power, freq = load_power_and_frequency(repo_root, test_id, "hydrophone")
        axes[1, 0].plot(power["Time (s)"], power["power_db"], color=CASE_COLORS[test_id], linewidth=0.8, label=case)
        axes[1, 1].plot(
            freq["Time (s)"],
            freq["Spectral centroid (Hz)"] / 1000.0,
            color=CASE_COLORS[test_id],
            linewidth=0.8,
            label=case,
        )
    axes[1, 0].set_xlabel(r"Time, $t$ (s)")
    axes[1, 0].set_ylabel(r"Band-integrated power (dB re V$^2$)")
    axes[1, 1].set_xlabel(r"Time, $t$ (s)")
    axes[1, 1].set_ylabel(r"Centroid frequency, $f_{\mathrm{c}}$ (kHz)")
    for ax in axes[1]:
        ax.set_xlim(0, 800)
        ax.grid(True, linestyle=":", alpha=0.45)
    axes[1, 1].legend(frameon=False, ncol=2, loc="best")
    save_png_pdf(fig, output_dir / "fig04_hydrophone_diagnostics")


def figure_5_ae(repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.2), constrained_layout=True)
    for col, test_id in enumerate(["Boiling-416", "Boiling-417"]):
        case = CASE_LABELS[test_id]
        image = mpimg.imread(repo_root / "demos" / test_id / "generated" / "plots" / "ae_wfs_spectrogram.png")
        axes[0, col].imshow(image)
        axes[0, col].axis("off")
        axes[0, col].text(
            0.03,
            0.93,
            case,
            transform=axes[0, col].transAxes,
            ha="left",
            va="top",
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.65, "pad": 1.5},
        )
        power, freq = load_power_and_frequency(repo_root, test_id, "ae")
        axes[1, 0].plot(power["Time (s)"], power["power_db"], color=CASE_COLORS[test_id], linewidth=0.8, label=case)
        axes[1, 1].plot(
            freq["Time (s)"],
            freq["Spectral centroid (Hz)"] / 1000.0,
            color=CASE_COLORS[test_id],
            linewidth=0.8,
            label=case,
        )
    axes[1, 0].set_xlabel(r"Time, $t$ (s)")
    axes[1, 0].set_ylabel(r"Band-integrated power (dB re V$^2$)")
    axes[1, 1].set_xlabel(r"Time, $t$ (s)")
    axes[1, 1].set_ylabel(r"Centroid frequency, $f_{\mathrm{c}}$ (kHz)")
    for ax in axes[1]:
        ax.set_xlim(0, 800)
        ax.grid(True, linestyle=":", alpha=0.45)
    axes[1, 1].legend(frameon=False, loc="best")
    save_png_pdf(fig, output_dir / "fig05_ae_waveform_diagnostics")


def figure_6_envelope(repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
    signal_labels = {
        "wall_temperature": r"$T_{\mathrm{w}}$",
        "heat_flux": r"$q^{\prime\prime}$",
        "hydrophone_power": "Hydrophone",
    }
    line_styles = {CASE_LABELS["Boiling-416"]: "-", CASE_LABELS["Boiling-417"]: "--"}
    for test_id in ["Boiling-416", "Boiling-417"]:
        case = CASE_LABELS[test_id]
        data = pd.read_csv(repo_root / "demos" / test_id / "generated" / "meb_envelope_analysis.csv")
        for key, label in signal_labels.items():
            frame = data[data["Signal key"] == key]
            if frame.empty:
                continue
            axes[0].plot(
                frame["Time (s)"],
                frame["Normalized envelope"],
                linestyle=line_styles[case],
                linewidth=1.0,
                label=f"{case}, {label}",
            )
    metrics = pd.read_csv(
        repo_root / "manuscripts" / "meb_multimodal_diagnostics" / "generated" / "publication_analysis" / "envelope_metrics_publication.csv"
    )
    keep = metrics[metrics["Signal key"].isin(signal_labels)].copy()
    keep["case"] = keep["case"].replace(
        {
            "Case C": CASE_LABELS["Boiling-416"],
            "Case D": CASE_LABELS["Boiling-417"],
        }
    )
    keep["plot_label"] = keep["Signal key"].map(signal_labels)
    xlabels = list(dict.fromkeys(keep["plot_label"]))
    x = np.arange(len(xlabels))
    width = 0.35
    for offset, case in [(-width / 2, CASE_LABELS["Boiling-416"]), (width / 2, CASE_LABELS["Boiling-417"])]:
        data = keep[keep["case"] == case].set_index("plot_label")
        axes[1].bar(
            x + offset,
            [data.loc[label, "envelope_time_constant_s"] for label in xlabels],
            width=width,
            color=CASE_COLORS[CASE_BY_POWER_LABEL[case]],
            label=case,
        )
    axes[0].set_xlabel(r"Time, $t$ (s)")
    axes[0].set_ylabel("Normalized envelope")
    axes[0].grid(True, linestyle=":", alpha=0.45)
    axes[0].legend(frameon=False, ncol=1, fontsize=6.5)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(xlabels)
    axes[1].set_ylabel(r"Envelope time constant, $\tau$ (s)")
    axes[1].grid(True, axis="y", linestyle=":", alpha=0.45)
    axes[1].legend(frameon=False, loc="best")
    for i, ax in enumerate(axes):
        ax.text(0.02, 0.98, f"({chr(97 + i)})", transform=ax.transAxes, ha="left", va="top")
    save_png_pdf(fig, output_dir / "fig06_envelope_growth")


def figure_7_literature(repo_root: Path, output_dir: Path) -> None:
    base = repo_root / "manuscripts" / "meb_multimodal_diagnostics" / "generated" / "publication_analysis"
    lit = pd.read_csv(base / "literature_digitized_boiling_points_publication.csv")
    present = pd.read_csv(base / "literature_boiling_curve_points_publication.csv")
    signatures = pd.read_csv(base / "literature_onset_signature_values_publication.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
    literature_colors = plt.get_cmap("tab10")
    for index, (paper_id, data) in enumerate(lit.groupby("paper_id", sort=False)):
        axes[0].scatter(
            data["wall_superheat_K"],
            data["heat_flux_W_cm2"],
            color=literature_colors(index % 10),
            s=24,
            label=SOURCE_LABELS.get(paper_id, paper_id.replace("_", " ")),
        )
    present_points = present[present["source_group"] == "Present work"]
    for paper_id, data in present_points.groupby("paper_id", sort=False):
        test_id = paper_id.replace("boilinglab_boiling_", "Boiling-")
        axes[0].scatter(
            data["wall_superheat_K"],
            data["heat_flux_W_cm2"],
            color=CASE_COLORS.get(test_id, "#F58518"),
            marker="s",
            s=14,
            alpha=0.8,
            label=CASE_LABELS.get(test_id, r"$P_{\mathrm{load}}$"),
        )
    axes[0].set_xlabel(r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)")
    axes[0].set_ylabel(r"$q^{\prime\prime}$ (W cm$^{-2}$)")

    lit_sig = signatures[signatures["source_type"] != "user_experiment"].copy()
    present_sig = signatures[signatures["source_type"] == "user_experiment"].copy()
    lit_sig = lit_sig[np.isfinite(lit_sig["frequency_Hz"]) & np.isfinite(lit_sig["heat_flux_W_cm2"])]
    for index, (source_id, data) in enumerate(lit_sig.groupby("source_id", sort=False)):
        axes[1].scatter(
            data["frequency_Hz"],
            data["heat_flux_W_cm2"],
            color=literature_colors(index % 10),
            s=24,
            label=SOURCE_LABELS.get(source_id, source_id.replace("_", " ")),
        )
    present_sig = present_sig[np.isfinite(present_sig["frequency_Hz"]) & np.isfinite(present_sig["heat_flux_W_cm2"])]
    for source_id, data in present_sig.groupby("source_id", sort=False):
        test_id = source_id.replace("boilinglab_boiling_", "Boiling-")
        axes[1].scatter(
            data["frequency_Hz"],
            data["heat_flux_W_cm2"],
            color=CASE_COLORS.get(test_id, "#F58518"),
            marker="s",
            s=32,
            label=CASE_LABELS.get(test_id, r"$P_{\mathrm{load}}$"),
        )
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Reported frequency or modulation scale (Hz)")
    axes[1].set_ylabel(r"$q^{\prime\prime}$ (W cm$^{-2}$)")
    for i, ax in enumerate(axes):
        ax.text(0.02, 0.98, f"({chr(97 + i)})", transform=ax.transAxes, ha="left", va="top")
        ax.grid(True, linestyle=":", alpha=0.45)
        ax.legend(frameon=False, loc="best", fontsize=6.4)
    save_png_pdf(fig, output_dir / "fig07_literature_context")


def write_caption_draft(output_dir: Path) -> None:
    captions = [
        "# Draft Manuscript Figure Captions",
        "",
        "Fig. 1. Heating-only boiling curves labeled by power load. Only samples with positive DC power are included.",
        "",
        "Fig. 2. 250 W thermal time histories with heat flux, power load, embedded thermocouple temperatures, extrapolated wall temperature, and event markers.",
        "",
        "Fig. 3. 230 W thermal time histories plotted with the same format as Fig. 2.",
        "",
        "Fig. 4. Hydrophone diagnostics. Top panels show current single-case spectrogram drafts for 230 W and 250 W; bottom panels show band-integrated hydrophone power and centroid frequency for all power loads.",
        "",
        "Fig. 5. AE waveform diagnostics for 230 W and 250 W only. AE is limited to these cases because waveform files are unavailable for 150 W and 180 W.",
        "",
        "Fig. 6. Envelope analysis for the developed high-power tests, including normalized envelope histories and fitted time constants.",
        "",
        "Fig. 7. Literature context from the first-pass `test2_meb` compilation, with source-specific brief citation labels. Literature rows marked as reported text or range endpoints require final figure/table verification before submission.",
        "",
    ]
    (output_dir / "captions.md").write_text("\n".join(captions), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--raw-root", default=r"Y:\0_Ishraq\New Pool Boiling Video")
    parser.add_argument(
        "--output-dir",
        default=r"manuscripts\meb_multimodal_diagnostics\generated\draft_figures",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    set_style()
    repo_root = Path(args.repo_root).resolve()
    raw_root = Path(args.raw_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    figure_1_boiling_curves(repo_root, output_dir)
    figure_thermal_case(raw_root, repo_root, output_dir, "Boiling-417", "fig02_case_d_thermal_time_histories")
    figure_thermal_case(raw_root, repo_root, output_dir, "Boiling-416", "fig03_case_c_thermal_time_histories")
    figure_4_hydrophone(repo_root, output_dir)
    figure_5_ae(repo_root, output_dir)
    figure_6_envelope(repo_root, output_dir)
    figure_7_literature(repo_root, output_dir)
    write_caption_draft(output_dir)
    print(f"Wrote draft manuscript figures to {output_dir}")


if __name__ == "__main__":
    main()
