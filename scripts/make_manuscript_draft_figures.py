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
from matplotlib.lines import Line2D
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
CASE_NAMES = {
    "Boiling-412": "Case A",
    "Boiling-413": "Case B",
    "Boiling-416": "Case C",
    "Boiling-417": "Case D",
}
CASE_COLORS = {
    "Boiling-412": "#0072B2",
    "Boiling-413": "#D55E00",
    "Boiling-416": "#009E73",
    "Boiling-417": "#CC79A7",
}
CASE_BY_POWER_LABEL = {label: test_id for test_id, label in CASE_LABELS.items()}
SOURCE_LABELS = {
    "horiuchi_2019_transient_nucleate_to_meb": "Horiuchi et al. 2019",
    "horiuchi_2021_spatiotemporal_meb": "Horiuchi et al. 2021",
    "inada_2016_cavitation_bubble_blow_pit": "Inada et al. 2016",
    "sinha_2021_deep_learning_sound_boiling": "Sinha et al. 2021",
    "tang_2016_transition_to_meb": "Ando et al. 2016",
    "horiuchi_2021_spatial_temporal_thermal_fluid": "Horiuchi et al. 2021",
    "zeigarnik_2012_microbubble_emission_nature": "Zeigarnik et al. 2012",
    "zhu_2014_visualized_meb": "Zhu et al. 2014",
    "ono_2023_acoustic_state_detection_meb": "Ono et al. 2023",
    "kobayashi_2022_homogeneity_boiling_sound_meb": "Kobayashi et al. 2022",
    "zhou_2018_sound_emission_subcooled_pool": "Zhou et al. 2018",
    "kobayashi_2024_reduced_pressure_confined_meb": "Kobayashi et al. 2024",
    "zhao_2025_open_microchannel_meb": "Zhao et al. 2025",
}
THERMOCOUPLE_LABELS = [r"$T_{\mathrm{TC1}}$", r"$T_{\mathrm{TC2}}$", r"$T_{\mathrm{TC3}}$", r"$T_{\mathrm{TC4}}$"]
SOURCE_STATUS_STYLES = {
    "reported_text_or_first_pass_extraction": ("o", "reported/extracted"),
    "literature_reported_or_first_pass_extraction": ("o", "reported/extracted"),
    "reported_range_endpoint": ("^", "range endpoint"),
    "figure_digitized_or_curve_point": ("D", "figure digitized"),
    "present_work_reduced_data": ("s", "present work"),
}


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
    ax.annotate(
        label,
        xy=(0.0, 1.0),
        xycoords="axes fraction",
        xytext=(-30, 8),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=10,
        annotation_clip=False,
    )


def add_external_panel_labels(fig: plt.Figure, axes, labels: list[str] | None = None) -> None:
    fig.canvas.draw()
    flat_axes = np.asarray(axes, dtype=object).ravel()
    for i, ax in enumerate(flat_axes):
        label = labels[i] if labels and i < len(labels) else f"({chr(97 + i)})"
        add_external_panel_label(fig, ax, label)


def load_thermal_uncertainties(repo_root: Path) -> dict[str, dict[str, float]]:
    path = (
        repo_root
        / "manuscripts"
        / "meb_multimodal_diagnostics"
        / "generated"
        / "publication_analysis"
        / "uncertainty_budget_publication.csv"
    )
    if not path.exists():
        return {}
    uncertainty = pd.read_csv(path)
    out: dict[str, dict[str, float]] = {}
    for test_id, case_name in CASE_NAMES.items():
        rows = uncertainty[uncertainty["case"] == case_name]
        if rows.empty:
            continue
        out[test_id] = {
            str(row["quantity"]): float(row["value"])
            for _, row in rows.iterrows()
            if row["quantity"] in {"wall_temperature", "heat_flux"}
        }
    return out


def source_status_style(status: str, *, present: bool = False) -> tuple[str, str]:
    if present:
        return SOURCE_STATUS_STYLES["present_work_reduced_data"]
    return SOURCE_STATUS_STYLES.get(status, ("D", "needs verification"))


def add_uncertainty_key(ax: plt.Axes, uncertainties: dict[str, dict[str, float]]) -> None:
    finite_tw = [case.get("wall_temperature") for case in uncertainties.values() if "wall_temperature" in case]
    finite_q = [case.get("heat_flux") for case in uncertainties.values() if "heat_flux" in case]
    if not finite_tw or not finite_q:
        return
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x = xlim[0] + 0.84 * (xlim[1] - xlim[0])
    y = ylim[0] + 0.16 * (ylim[1] - ylim[0])
    ax.errorbar(
        x,
        y,
        xerr=max(finite_tw),
        yerr=max(finite_q),
        fmt="none",
        ecolor="0.2",
        elinewidth=0.9,
        capsize=2.5,
        zorder=5,
    )
    ax.text(
        x,
        y + 0.08 * (ylim[1] - ylim[0]),
        r"max. $k=2$ uncertainty",
        ha="center",
        va="bottom",
        fontsize=6.8,
        color="0.2",
    )


def save_png_pdf(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def figure_1_boiling_curves(raw_root: Path, repo_root: Path, output_dir: Path) -> None:
    curves = pd.read_csv(repo_root / "demos" / "Boiling-412-413-416-417" / "generated" / "curves.csv")
    curves["case"] = curves["test_id"].map(CASE_LABELS)
    uncertainties = load_thermal_uncertainties(repo_root)
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
    for test_id in CASE_IDS:
        case = CASE_LABELS[test_id]
        data = curves[curves["test_id"] == test_id].copy()
        color = CASE_COLORS[test_id]
        axes[0].plot(data["wall_superheat_C"], data["heat_flux_W_cm2"], color=color, linewidth=1.6, label=case)
        summary = load_summary(repo_root, test_id)
        full = load_thermal_case(raw_root, test_id)
        wall_superheat = full["surface_temperature_C"] - float(summary.get("T_sat_C", np.nan))
        t_off = float(summary.get("dc_shutoff_time_s", np.nan))
        heating = full["time_s"] < t_off if np.isfinite(t_off) else np.ones(len(full["time_s"]), dtype=bool)
        axes[1].plot(
            wall_superheat[heating],
            full["heat_flux_W_cm2"][heating],
            color=color,
            linestyle="-",
            linewidth=1.45,
            label=case,
        )
        if np.any(~heating):
            axes[1].plot(
                wall_superheat[~heating],
                full["heat_flux_W_cm2"][~heating],
                color=color,
                linestyle="--",
                linewidth=1.15,
                alpha=0.95,
            )
    axes[0].set_xlabel(r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)")
    axes[1].set_xlabel(r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)")
    for ax in axes:
        ax.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W cm$^{-2}$)")
        ax.grid(True, linestyle=":", alpha=0.45)
    for ax in axes:
        add_uncertainty_key(ax, uncertainties)
    axes[0].legend(frameon=False, ncol=1, loc="upper left")
    axes[1].legend(frameon=False, ncol=1, loc="upper left", title="solid: heating\n dashed: cooling", title_fontsize=6.6)
    add_external_panel_labels(fig, axes)
    save_png_pdf(fig, output_dir / "fig01_heating_boiling_curves")


def figure_1b_hysteresis_boiling_curves(raw_root: Path, repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
    for test_id in CASE_IDS:
        summary = load_summary(repo_root, test_id)
        data = load_thermal_case(raw_root, test_id)
        t_off = float(summary.get("dc_shutoff_time_s", np.nan))
        if not np.isfinite(t_off):
            power_on = np.interp(data["time_s"], data["dc_time_s"], data["dc_power_W"], left=0.0, right=0.0) > 0.0
            t_off = float(np.nanmax(data["time_s"][power_on])) if np.any(power_on) else float(np.nanmax(data["time_s"]))
        heating = data["time_s"] < t_off
        cooling = ~heating
        wall_superheat = data["surface_temperature_C"] - float(summary.get("T_sat_C", np.nan))
        label = CASE_LABELS[test_id]
        color = CASE_COLORS[test_id]
        for ax, x in zip(axes, [data["surface_temperature_C"], wall_superheat]):
            ax.plot(
                x[heating],
                data["heat_flux_W_cm2"][heating],
                color=color,
                linestyle="-",
                linewidth=1.5,
                label=f"{label}, heating",
            )
            if np.any(cooling):
                ax.plot(
                    x[cooling],
                    data["heat_flux_W_cm2"][cooling],
                    color=color,
                    linestyle="--",
                    linewidth=1.2,
                    alpha=0.9,
                    label=f"{label}, cooling",
                )
    axes[0].set_xlabel(r"Wall temperature, $T_{\mathrm{w}}$ ($^\circ$C)")
    axes[1].set_xlabel(r"Wall superheat, $\Delta T_{\mathrm{w}}$ (K)")
    for ax in axes:
        ax.set_ylabel(r"Heat flux, $q^{\prime\prime}$ (W cm$^{-2}$)")
        ax.grid(True, linestyle=":", alpha=0.45)
    axes[1].legend(frameon=False, ncol=1, loc="best", fontsize=5.6)
    add_external_panel_labels(fig, axes)
    save_png_pdf(fig, output_dir / "fig01b_full_history_boiling_curves")


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
    add_external_panel_labels(fig, axes)
    for i, ax in enumerate(axes):
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
    fig, axes = plt.subplots(3, 2, figsize=(7.25, 7.2), constrained_layout=True)
    for ax, test_id in zip(axes[:2].ravel(), CASE_IDS):
        image = mpimg.imread(repo_root / "demos" / test_id / "generated" / "plots" / "hydrophone_spectrogram.png")
        ax.imshow(image)
        ax.axis("off")
    for test_id in CASE_IDS:
        case = CASE_LABELS[test_id]
        power, freq = load_power_and_frequency(repo_root, test_id, "hydrophone")
        axes[2, 0].plot(power["Time (s)"], power["power_db"], color=CASE_COLORS[test_id], linewidth=0.8, label=case)
        axes[2, 1].plot(
            freq["Time (s)"],
            freq["Spectral centroid (Hz)"] / 1000.0,
            color=CASE_COLORS[test_id],
            linewidth=0.8,
            label=case,
        )
    axes[2, 0].set_xlabel(r"Time, $t$ (s)")
    axes[2, 0].set_ylabel(r"Band-integrated power (dB re V$^2$)")
    axes[2, 1].set_xlabel(r"Time, $t$ (s)")
    axes[2, 1].set_ylabel(r"Centroid frequency, $f_{\mathrm{c}}$ (kHz)")
    for ax in axes[2]:
        ax.set_xlim(0, 800)
        ax.grid(True, linestyle=":", alpha=0.45)
    axes[2, 1].legend(frameon=False, ncol=2, loc="best")
    add_external_panel_labels(
        fig,
        axes,
        [
            f"(a) {CASE_LABELS['Boiling-412']}",
            f"(b) {CASE_LABELS['Boiling-413']}",
            f"(c) {CASE_LABELS['Boiling-416']}",
            f"(d) {CASE_LABELS['Boiling-417']}",
            "(e)",
            "(f)",
        ],
    )
    save_png_pdf(fig, output_dir / "fig04_hydrophone_diagnostics")


def figure_5_ae(repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.2), constrained_layout=True)
    for col, test_id in enumerate(["Boiling-416", "Boiling-417"]):
        case = CASE_LABELS[test_id]
        image = mpimg.imread(repo_root / "demos" / test_id / "generated" / "plots" / "ae_wfs_spectrogram.png")
        axes[0, col].imshow(image)
        axes[0, col].axis("off")
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
    add_external_panel_labels(
        fig,
        axes,
        [f"(a) {CASE_LABELS['Boiling-416']}", f"(b) {CASE_LABELS['Boiling-417']}", "(c)", "(d)"],
    )
    save_png_pdf(fig, output_dir / "fig05_ae_waveform_diagnostics")


def figure_6_envelope_showcase(repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.0), sharex="col", constrained_layout=True)
    signal_styles = {
        "wall_temperature": (r"$T_{\mathrm{w}}$", "C", "#0072B2"),
        "heat_flux": (r"$q^{\prime\prime}$", r"W cm$^{-2}$", "#D55E00"),
    }
    for col, test_id in enumerate(["Boiling-416", "Boiling-417"]):
        data = pd.read_csv(repo_root / "demos" / test_id / "generated" / "meb_envelope_analysis.csv")
        for row, (signal_key, (label, unit, color)) in enumerate(signal_styles.items()):
            ax = axes[row, col]
            frame = data[data["Signal key"] == signal_key].copy()
            if frame.empty:
                continue
            # Decimate only for plotting; fits are read from the full analysis CSV.
            step = max(1, len(frame) // 1400)
            plot_frame = frame.iloc[::step]
            t0 = float(frame["Time (s)"].iloc[0])
            ax.plot(
                plot_frame["Time (s)"] - t0,
                plot_frame["Detrended signal"],
                color="0.55",
                linewidth=0.55,
                label="detrended signal",
            )
            ax.plot(
                plot_frame["Time (s)"] - t0,
                plot_frame["Envelope"],
                color=color,
                linewidth=0.75,
                alpha=0.55,
                label="Hilbert envelope",
            )
            ax.plot(
                plot_frame["Time (s)"] - t0,
                plot_frame["Asymptotic envelope fit"],
                color=color,
                linewidth=1.25,
                label="asymptotic fit",
            )
            ax.plot(
                plot_frame["Time (s)"] - t0,
                -plot_frame["Asymptotic envelope fit"],
                color=color,
                linewidth=1.0,
                linestyle=":",
                alpha=0.85,
                label="_nolegend_",
            )
            ax.set_ylabel(f"{label} fluctuation ({unit})")
            ax.grid(True, linestyle=":", alpha=0.45)
            if row == 1:
                ax.set_xlabel(r"Time after $t_{\mathrm{osc}}$, $t-t_{\mathrm{osc}}$ (s)")
    axes[0, 0].legend(frameon=False, loc="upper right", fontsize=6.4)
    add_external_panel_labels(
        fig,
        axes,
        [
            f"(a) {CASE_LABELS['Boiling-416']}",
            f"(b) {CASE_LABELS['Boiling-417']}",
            f"(c) {CASE_LABELS['Boiling-416']}",
            f"(d) {CASE_LABELS['Boiling-417']}",
        ],
    )
    save_png_pdf(fig, output_dir / "fig06_envelope_showcase")


def figure_7_envelope_metrics(repo_root: Path, output_dir: Path) -> None:
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
    add_external_panel_labels(fig, axes)
    save_png_pdf(fig, output_dir / "fig07_envelope_growth")


def fit_enveloped_oscillation(frame: pd.DataFrame) -> tuple[np.ndarray, float, float]:
    t = frame["Time (s)"].to_numpy(dtype=float)
    y = frame["Detrended signal"].to_numpy(dtype=float)
    envelope = frame["Asymptotic envelope fit"].to_numpy(dtype=float)
    finite = np.isfinite(t) & np.isfinite(y) & np.isfinite(envelope)
    t = t[finite]
    y = y[finite]
    envelope = envelope[finite]
    t_rel = t - t[0]
    best_model = np.zeros_like(y)
    best_freq = np.nan
    best_sse = np.inf
    for freq in np.linspace(0.025, 0.12, 240):
        omega_t = 2.0 * np.pi * freq * t_rel
        x = np.column_stack([envelope * np.cos(omega_t), envelope * np.sin(omega_t)])
        coeff, *_ = np.linalg.lstsq(x, y, rcond=None)
        model = x @ coeff
        sse = float(np.sum((y - model) ** 2))
        if sse < best_sse:
            best_sse = sse
            best_model = model
            best_freq = freq
    denom = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - best_sse / denom if denom > 0 else np.nan
    return best_model, best_freq, r2


def figure_8_storage_release_fit(repo_root: Path, output_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.0), sharex="col", constrained_layout=True)
    rows = [("wall_temperature", r"$T_{\mathrm{w}}$ fluctuation ($^\circ$C)"), ("heat_flux", r"$q^{\prime\prime}$ fluctuation (W cm$^{-2}$)")]
    fit_rows = []
    for col, test_id in enumerate(["Boiling-416", "Boiling-417"]):
        data = pd.read_csv(repo_root / "demos" / test_id / "generated" / "meb_envelope_analysis.csv")
        for row, (signal_key, ylabel) in enumerate(rows):
            ax = axes[row, col]
            frame = data[data["Signal key"] == signal_key].copy()
            if frame.empty:
                continue
            model, freq, r2 = fit_enveloped_oscillation(frame)
            t = frame["Time (s)"].to_numpy(dtype=float)
            y = frame["Detrended signal"].to_numpy(dtype=float)
            t_rel = t - t[0]
            step = max(1, len(frame) // 1500)
            ax.plot(t_rel[::step], y[::step], color="0.55", linewidth=0.55, label="experiment")
            ax.plot(t_rel[::step], model[::step], color=CASE_COLORS[test_id], linewidth=1.25, label="fitted surrogate")
            ax.text(
                0.03,
                0.92,
                rf"$f$ = {freq:.3f} Hz, $R^2$ = {r2:.2f}",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=7.0,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 1.5},
            )
            ax.set_ylabel(ylabel)
            ax.grid(True, linestyle=":", alpha=0.45)
            if row == 1:
                ax.set_xlabel(r"Time after $t_{\mathrm{osc}}$, $t-t_{\mathrm{osc}}$ (s)")
            fit_rows.append(
                {
                    "test_id": test_id,
                    "case": CASE_LABELS[test_id],
                    "signal_key": signal_key,
                    "frequency_Hz": freq,
                    "r2": r2,
                }
            )
    axes[0, 0].legend(frameon=False, loc="lower right", fontsize=6.5)
    add_external_panel_labels(
        fig,
        axes,
        [
            f"(a) {CASE_LABELS['Boiling-416']}",
            f"(b) {CASE_LABELS['Boiling-417']}",
            f"(c) {CASE_LABELS['Boiling-416']}",
            f"(d) {CASE_LABELS['Boiling-417']}",
        ],
    )
    pd.DataFrame(fit_rows).to_csv(output_dir / "fig08_storage_release_fit_metrics.csv", index=False)
    save_png_pdf(fig, output_dir / "fig08_storage_release_fit")


def figure_7_literature(repo_root: Path, output_dir: Path) -> None:
    base = repo_root / "manuscripts" / "meb_multimodal_diagnostics" / "generated" / "publication_analysis"
    lit = pd.read_csv(base / "literature_digitized_boiling_points_publication.csv")
    present = pd.read_csv(base / "literature_boiling_curve_points_publication.csv")
    signatures = pd.read_csv(base / "literature_onset_signature_values_publication.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)
    literature_palette = [
        "#0072B2",
        "#D55E00",
        "#009E73",
        "#CC79A7",
        "#6A3D9A",
        "#8C564B",
        "#E69F00",
        "#56B4E9",
    ]
    source_names = [SOURCE_LABELS.get(paper_id, paper_id.replace("_", " ")) for paper_id in lit["paper_id"].dropna()]
    source_color_map = {
        source: literature_palette[index % len(literature_palette)]
        for index, source in enumerate(dict.fromkeys(source_names))
    }
    shown_sources: set[str] = set()
    for _, (paper_id, data) in enumerate(lit.groupby("paper_id", sort=False)):
        source_label = SOURCE_LABELS.get(paper_id, paper_id.replace("_", " "))
        color = source_color_map[source_label]
        label_used = source_label in shown_sources
        for _, curve in data.groupby("curve_id", sort=False):
            curve = curve.sort_values("wall_superheat_K")
            status = str(curve["digitization_status"].iloc[0])
            marker, _ = source_status_style(status)
            is_digitized_curve = status == "figure_digitized_or_curve_point" and len(curve) >= 3
            if is_digitized_curve:
                linestyle = ":" if curve["recommended_use"].str.contains("geometry-separated", case=False, na=False).any() else "-"
                axes[0].plot(
                    curve["wall_superheat_K"],
                    curve["heat_flux_W_cm2"],
                    color=color,
                    linestyle=linestyle,
                    linewidth=1.1,
                    alpha=0.9,
                    label=source_label if not label_used else "_nolegend_",
                )
                label_used = True
                shown_sources.add(source_label)
            axes[0].scatter(
                curve["wall_superheat_K"],
                curve["heat_flux_W_cm2"],
                color=color,
                marker=marker,
                edgecolor="black" if marker in {"^", "D", "s"} else "none",
                linewidth=0.35,
                s=18 if is_digitized_curve else 24,
                alpha=0.85,
                label=source_label if not label_used else "_nolegend_",
            )
            label_used = True
            shown_sources.add(source_label)
    present_points = present[present["source_group"] == "Present work"]
    for paper_id, data in present_points.groupby("paper_id", sort=False):
        test_id = paper_id.replace("boilinglab_boiling_", "Boiling-")
        marker, _ = source_status_style("", present=True)
        axes[0].scatter(
            data["wall_superheat_K"],
            data["heat_flux_W_cm2"],
            color=CASE_COLORS.get(test_id, "#F58518"),
            marker=marker,
            edgecolor="black",
            linewidth=0.25,
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
        marker, _ = source_status_style(str(data["digitization_status"].iloc[0]))
        axes[1].scatter(
            data["frequency_Hz"],
            data["heat_flux_W_cm2"],
            color=literature_palette[index % len(literature_palette)],
            marker=marker,
            edgecolor="black" if marker == "^" else "none",
            linewidth=0.4,
            s=24,
            label=SOURCE_LABELS.get(source_id, source_id.replace("_", " ")),
        )
    present_sig = present_sig[np.isfinite(present_sig["frequency_Hz"]) & np.isfinite(present_sig["heat_flux_W_cm2"])]
    for source_id, data in present_sig.groupby("source_id", sort=False):
        test_id = source_id.replace("boilinglab_boiling_", "Boiling-")
        marker, _ = source_status_style("", present=True)
        axes[1].scatter(
            data["frequency_Hz"],
            data["heat_flux_W_cm2"],
            color=CASE_COLORS.get(test_id, "#F58518"),
            marker=marker,
            edgecolor="black",
            linewidth=0.25,
            s=32,
            label=CASE_LABELS.get(test_id, r"$P_{\mathrm{load}}$"),
        )
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Reported frequency or modulation scale (Hz)")
    axes[1].set_ylabel(r"$q^{\prime\prime}$ (W cm$^{-2}$)")
    for ax in axes:
        ax.grid(True, linestyle=":", alpha=0.45)
        ax.legend(frameon=False, loc="best", fontsize=5.7)
    add_external_panel_labels(fig, axes)
    save_png_pdf(fig, output_dir / "fig09_literature_context")


def write_caption_draft(output_dir: Path) -> None:
    captions = [
        "# Draft Manuscript Figure Captions",
        "",
        "Fig. 1. Boiling curves labeled by power load. Panel (a) includes only active-heating samples with positive DC power. Panel (b) includes the full thermal history; solid lines show active heating before power shutoff and dashed lines show cooling after shutoff. A single maximum expanded uncertainty marker is shown in each panel.",
        "",
        "Fig. 2. 250 W thermal time histories with heat flux, power load, embedded thermocouple temperatures, extrapolated wall temperature, and event markers.",
        "",
        "Fig. 3. 230 W thermal time histories plotted with the same format as Fig. 2.",
        "",
        "Fig. 4. Hydrophone diagnostics. Top four panels show current single-case spectrogram drafts for all power loads; bottom panels show band-integrated hydrophone power and centroid frequency for all power loads.",
        "",
        "Fig. 5. AE waveform diagnostics for 230 W and 250 W only. AE is limited to these cases because waveform files are unavailable for 150 W and 180 W.",
        "",
        "Fig. 6. Raw detrended oscillations, Hilbert envelopes, and asymptotic envelope fits for the developed high-power tests.",
        "",
        "Fig. 7. Envelope analysis for the developed high-power tests, including normalized envelope histories and fitted time constants.",
        "",
        "Fig. 8. Data-constrained oscillatory surrogate fitted to detrended thermal and heat-flux oscillations using the asymptotic envelope from Fig. 6.",
        "",
        "Fig. 9. Literature context from the `test2_meb` compilation. Panel (a) includes source-reported points, range endpoints, and newly digitized boiling-curve traces from the available literature PDFs; dotted traces denote geometry-separated flow-microchannel context. Panel (b) compares reported characteristic frequency scales. Source colors identify studies and marker shapes identify extraction status.",
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

    figure_1_boiling_curves(raw_root, repo_root, output_dir)
    figure_thermal_case(raw_root, repo_root, output_dir, "Boiling-417", "fig02_case_d_thermal_time_histories")
    figure_thermal_case(raw_root, repo_root, output_dir, "Boiling-416", "fig03_case_c_thermal_time_histories")
    figure_4_hydrophone(repo_root, output_dir)
    figure_5_ae(repo_root, output_dir)
    figure_6_envelope_showcase(repo_root, output_dir)
    figure_7_envelope_metrics(repo_root, output_dir)
    figure_8_storage_release_fit(repo_root, output_dir)
    figure_7_literature(repo_root, output_dir)
    write_caption_draft(output_dir)
    print(f"Wrote draft manuscript figures to {output_dir}")


if __name__ == "__main__":
    main()
