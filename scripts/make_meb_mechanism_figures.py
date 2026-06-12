"""Generate mechanism figures for the MEB manuscript discussion.

This script connects slow hydrophone-power oscillations to representative
high-speed-video frames and creates a compact storage-release oscillator model.
The video files are encoded at 30 fps from 150 fps high-speed recordings, so
experimental time is mapped to video playback time with a factor of five.
"""

from __future__ import annotations

import argparse
import shutil
import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageFilter
from scipy.signal import find_peaks, savgol_filter


CASE_INFO = {
    "Boiling-416": {"case": "Case C", "power_label": r"$P_{\mathrm{load}}$ = 230 W", "color": "#2ca02c"},
    "Boiling-417": {"case": "Case D", "power_label": r"$P_{\mathrm{load}}$ = 250 W", "color": "#d62728"},
}
HIGH_SPEED_FPS = 150.0
MP4_FPS = 30.0
VIDEO_SLOWDOWN = HIGH_SPEED_FPS / MP4_FPS


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
    return json.loads((repo_root / "demos" / test_id / "generated" / "summary.json").read_text(encoding="utf-8"))


def ffmpeg_duration_s(ffmpeg: str, video_path: Path) -> float:
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(video_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    text = proc.stderr + proc.stdout
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if not match:
        raise RuntimeError(f"Could not read duration from ffmpeg output for {video_path}")
    hours, minutes, seconds = match.groups()
    return 3600.0 * float(hours) + 60.0 * float(minutes) + float(seconds)


def smooth_power(time_s: np.ndarray, power_v2: np.ndarray) -> np.ndarray:
    y = np.log10(np.maximum(power_v2, np.finfo(float).tiny))
    if len(y) < 31:
        return y
    dt = float(np.nanmedian(np.diff(time_s))) if len(time_s) > 1 else 1.0
    window = int(round(7.5 / max(dt, 1e-9)))
    window = max(11, window | 1)
    window = min(window, len(y) - 1 if (len(y) - 1) % 2 else len(y) - 2)
    return savgol_filter(y, window_length=window, polyorder=2)


def select_peak_valley(repo_root: Path, raw_root: Path, test_id: str) -> dict[str, float | str]:
    summary = load_summary(repo_root, test_id)
    video_path = raw_root / test_id / f"{test_id}_video.mp4"
    duration_exp_s = ffmpeg_duration_s(imageio_ffmpeg.get_ffmpeg_exe(), video_path) / VIDEO_SLOWDOWN

    power_path = repo_root / "demos" / test_id / "generated" / "hydrophone_band_integrated_power.csv"
    power = pd.read_csv(power_path)
    time = power["Time (s)"].to_numpy(dtype=float)
    power_v2 = power["Band-integrated hydrophone power proxy (V^2)"].to_numpy(dtype=float)
    y = smooth_power(time, power_v2)

    window_start = max(float(summary.get("oscillation_peak_time_s", 300.0)), 300.0)
    window_end = min(float(summary.get("dc_shutoff_time_s", duration_exp_s)), duration_exp_s - 2.0)
    mask = (time >= window_start) & (time <= window_end)
    if np.count_nonzero(mask) < 20:
        raise RuntimeError(f"Insufficient hydrophone samples in mechanism window for {test_id}")

    t_win = time[mask]
    y_win = y[mask]
    dt = float(np.nanmedian(np.diff(t_win)))
    distance = max(1, int(round(6.0 / max(dt, 1e-9))))
    prominence = max(0.05, 0.20 * float(np.nanstd(y_win)))
    peak_indices, _ = find_peaks(y_win, distance=distance, prominence=prominence)
    valley_indices, _ = find_peaks(-y_win, distance=distance, prominence=prominence)
    if len(peak_indices) == 0 or len(valley_indices) == 0:
        peak_index = int(np.nanargmax(y_win))
        valley_index = int(np.nanargmin(y_win))
    else:
        peak_index = int(peak_indices[np.nanargmax(y_win[peak_indices])])
        before = valley_indices[valley_indices < peak_index]
        after = valley_indices[valley_indices > peak_index]
        if len(before):
            valley_index = int(before[np.nanargmin(np.abs(before - peak_index))])
        elif len(after):
            valley_index = int(after[np.nanargmin(np.abs(after - peak_index))])
        else:
            valley_index = int(np.nanargmin(y_win))

    return {
        "test_id": test_id,
        "case": CASE_INFO[test_id]["case"],
        "power_label": CASE_INFO[test_id]["power_label"].replace(r"$", ""),
        "window_start_s": window_start,
        "window_end_s": window_end,
        "peak_time_s": float(t_win[peak_index]),
        "peak_power_log10_V2": float(y_win[peak_index]),
        "valley_time_s": float(t_win[valley_index]),
        "valley_power_log10_V2": float(y_win[valley_index]),
        "video_slowdown_factor": VIDEO_SLOWDOWN,
        "mp4_path": str(video_path),
    }


def extract_frame(ffmpeg: str, video_path: Path, exp_time_s: float, output_path: Path) -> None:
    video_time_s = exp_time_s * VIDEO_SLOWDOWN
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{video_time_s:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-y",
            str(output_path),
        ],
        check=True,
    )


def extract_screening_frames(
    ffmpeg: str,
    video_path: Path,
    output_dir: Path,
    window_start_s: float,
    window_end_s: float,
    sample_dt_exp_s: float = 5.0,
) -> list[tuple[float, Path]]:
    frame_dir = output_dir / "screening_frames"
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True, exist_ok=True)
    video_start_s = window_start_s * VIDEO_SLOWDOWN
    video_duration_s = max(0.0, (window_end_s - window_start_s) * VIDEO_SLOWDOWN)
    fps = 1.0 / (sample_dt_exp_s * VIDEO_SLOWDOWN)
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{video_start_s:.3f}",
            "-i",
            str(video_path),
            "-t",
            f"{video_duration_s:.3f}",
            "-vf",
            f"fps={fps:.8f}",
            "-y",
            str(frame_dir / "frame_%04d.png"),
        ],
        check=True,
    )
    frames = sorted(frame_dir.glob("frame_*.png"))
    return [(window_start_s + i * sample_dt_exp_s, path) for i, path in enumerate(frames)]


def visual_microbubble_metric(frame_path: Path) -> float:
    image = Image.open(frame_path).convert("L")
    width, height = image.size
    # Central plume above the heater, avoiding the overexposed vapor cap.
    roi = image.crop((int(0.28 * width), int(0.48 * height), int(0.74 * width), int(0.86 * height)))
    arr = np.asarray(roi, dtype=float) / 255.0
    edges = np.asarray(roi.filter(ImageFilter.FIND_EDGES), dtype=float) / 255.0
    dark_fraction = float(np.mean(arr < np.nanpercentile(arr, 35)))
    texture = float(np.nanstd(arr))
    edge_density = float(np.nanmean(edges))
    return 0.45 * edge_density + 0.35 * texture + 0.20 * dark_fraction


def nearest_power_percentile(repo_root: Path, test_id: str, time_s: float) -> float:
    power = pd.read_csv(repo_root / "demos" / test_id / "generated" / "hydrophone_band_integrated_power.csv")
    t = power["Time (s)"].to_numpy(dtype=float)
    p = power["Band-integrated hydrophone power proxy (V^2)"].to_numpy(dtype=float)
    value = float(np.interp(time_s, t, p))
    return float(100.0 * np.mean(p <= value))


def select_visual_frames(
    ffmpeg: str,
    repo_root: Path,
    raw_root: Path,
    test_id: str,
    acoustic_selection: dict[str, float | str],
    output_dir: Path,
) -> dict[str, float | str]:
    video_path = raw_root / test_id / f"{test_id}_video.mp4"
    case_dir = output_dir / "screening" / test_id
    frames = extract_screening_frames(
        ffmpeg,
        video_path,
        case_dir,
        float(acoustic_selection["window_start_s"]),
        float(acoustic_selection["window_end_s"]),
    )
    rows = []
    for time_s, path in frames:
        rows.append(
            {
                "time_s": time_s,
                "path": str(path),
                "visual_microbubble_metric": visual_microbubble_metric(path),
                "hydrophone_power_percentile": nearest_power_percentile(repo_root, test_id, time_s),
            }
        )
    metrics = pd.DataFrame(rows)
    metrics.to_csv(case_dir / "visual_frame_screening.csv", index=False)
    if metrics.empty:
        raise RuntimeError(f"No screening frames extracted for {test_id}")
    high_pool = metrics[metrics["hydrophone_power_percentile"] >= 60.0]
    high = high_pool.loc[high_pool["visual_microbubble_metric"].idxmax()] if not high_pool.empty else metrics.loc[metrics["visual_microbubble_metric"].idxmax()]
    low_pool = metrics[
        (metrics["hydrophone_power_percentile"] <= 40.0)
        & (metrics["time_s"].sub(float(high["time_s"])).abs() > 20.0)
    ]
    if low_pool.empty:
        low_pool = metrics[
            (metrics["hydrophone_power_percentile"] <= 60.0)
            & (metrics["time_s"].sub(float(high["time_s"])).abs() > 20.0)
        ]
    if low_pool.empty:
        low_pool = metrics[metrics["time_s"].sub(float(high["time_s"])).abs() > 20.0]
    low = low_pool.loc[low_pool["visual_microbubble_metric"].idxmin()] if not low_pool.empty else metrics.loc[metrics["visual_microbubble_metric"].idxmin()]
    selected = {
        **acoustic_selection,
        "low_visual_time_s": float(low["time_s"]),
        "low_visual_metric": float(low["visual_microbubble_metric"]),
        "low_visual_hydrophone_power_percentile": float(low["hydrophone_power_percentile"]),
        "high_visual_time_s": float(high["time_s"]),
        "high_visual_metric": float(high["visual_microbubble_metric"]),
        "high_visual_hydrophone_power_percentile": float(high["hydrophone_power_percentile"]),
    }
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(str(low["path"])), frames_dir / f"{test_id}_low_visual.png")
    shutil.copyfile(Path(str(high["path"])), frames_dir / f"{test_id}_high_visual.png")
    cache_dir = case_dir / "screening_frames"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    return selected


def add_external_panel_label(ax: plt.Axes, label: str) -> None:
    ax.annotate(
        label,
        xy=(0.0, 1.0),
        xycoords="axes fraction",
        xytext=(-28, 8),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=10,
        annotation_clip=False,
    )


def plot_frame_panel(output_dir: Path, selections: list[dict[str, float | str]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 6.2), constrained_layout=True)
    for row, selection in enumerate(selections):
        test_id = str(selection["test_id"])
        for col, state in enumerate(["low_visual", "high_visual"]):
            path = output_dir / "frames" / f"{test_id}_{state}.png"
            ax = axes[row, col]
            ax.imshow(mpimg.imread(path))
            ax.set_axis_off()
            event_time = float(selection[f"{state}_time_s"])
            title = "fewer visible microbubbles" if state == "low_visual" else "many visible microbubbles"
            percentile = float(selection[f"{state}_hydrophone_power_percentile"])
            ax.set_title(f"{selection['case']}, {title}\n$t$ = {event_time:.1f} s; hydrophone {percentile:.0f}th pct.", fontsize=9)
            add_external_panel_label(ax, f"({chr(97 + row * 2 + col)})")
    fig.savefig(output_dir / "fig08_representative_microbubble_frames.png", bbox_inches="tight")
    fig.savefig(output_dir / "fig08_representative_microbubble_frames.pdf", bbox_inches="tight")
    plt.close(fig)


def storage_release_model() -> pd.DataFrame:
    dt = 0.02
    time = np.arange(0.0, 430.0 + dt, dt)
    displacement = np.zeros_like(time)
    release_velocity = np.zeros_like(time)
    displacement[0] = 0.02

    input_flux = 1.0
    threshold = 1.8
    natural_frequency_hz = 0.065
    omega = 2.0 * np.pi * natural_frequency_hz
    feedback_max = 0.045
    development_tau = 145.0

    for i in range(1, len(time)):
        feedback = feedback_max * (1.0 - np.exp(-time[i] / development_tau))
        acceleration = feedback * (1.0 - displacement[i - 1] ** 2) * release_velocity[i - 1]
        acceleration -= omega**2 * displacement[i - 1]
        release_velocity[i] = release_velocity[i - 1] + acceleration * dt
        displacement[i] = displacement[i - 1] + release_velocity[i] * dt

    positive_release = np.maximum(release_velocity, 0.0)
    positive_release /= max(float(np.nanmax(positive_release)), np.finfo(float).eps)
    envelope = 1.0 - np.exp(-time / development_tau)
    storage = threshold + 0.50 * displacement
    heat_flux_out = input_flux + 1.15 * envelope * positive_release**1.5 - 0.25 * envelope * np.maximum(-release_velocity, 0.0)
    acoustic_proxy = (envelope * positive_release) ** 2

    return pd.DataFrame(
        {
            "time_s": time,
            "nominal_input_flux": input_flux,
            "stored_energy_state": storage,
            "oscillator_displacement": displacement,
            "release_velocity_state": release_velocity,
            "wall_heat_flux_proxy": heat_flux_out,
            "acoustic_power_proxy": acoustic_proxy,
        }
    )


def plot_model(output_dir: Path) -> None:
    model = storage_release_model()
    model.to_csv(output_dir / "storage_release_model.csv", index=False)
    fig, axes = plt.subplots(3, 1, figsize=(7.25, 5.6), sharex=True, constrained_layout=True)
    axes[0].plot(model["time_s"], model["stored_energy_state"], color="#4C78A8", linewidth=1.6)
    axes[0].axhline(1.8, color="0.35", linestyle="--", linewidth=0.9, label="release threshold")
    axes[0].set_ylabel("Storage state")
    axes[0].legend(frameon=False, loc="upper left")

    axes[1].plot(model["time_s"], model["wall_heat_flux_proxy"], color="#C44E52", linewidth=1.4, label="released heat-flux proxy")
    axes[1].axhline(1.0, color="0.25", linestyle=":", linewidth=1.0, label="constant input")
    axes[1].set_ylabel(r"$q^{\prime\prime}$ proxy")
    axes[1].legend(frameon=False, loc="upper left")

    axes[2].plot(model["time_s"], model["acoustic_power_proxy"], color="#2ca02c", linewidth=1.2)
    axes[2].set_ylabel("Acoustic proxy")
    axes[2].set_xlabel(r"Time, $t$ (s)")
    for ax in axes:
        ax.grid(True, linestyle=":", alpha=0.45)
    for i, ax in enumerate(axes):
        add_external_panel_label(ax, f"({chr(97 + i)})")
    fig.savefig(output_dir / "fig09_storage_release_model.png", bbox_inches="tight")
    fig.savefig(output_dir / "fig09_storage_release_model.pdf", bbox_inches="tight")
    plt.close(fig)


def write_captions(output_dir: Path, selections: list[dict[str, float | str]]) -> None:
    rows = pd.DataFrame(selections)
    rows.to_csv(output_dir / "selected_representative_frames.csv", index=False)
    display_cols = [
        "case",
        "window_start_s",
        "window_end_s",
        "low_visual_time_s",
        "low_visual_hydrophone_power_percentile",
        "high_visual_time_s",
        "high_visual_hydrophone_power_percentile",
    ]
    table_rows = ["| " + " | ".join(display_cols) + " |", "| " + " | ".join(["---"] * len(display_cols)) + " |"]
    for _, row in rows[display_cols].iterrows():
        values = []
        for col in display_cols:
            value = row[col]
            values.append(f"{value:.1f}" if isinstance(value, float) else str(value))
        table_rows.append("| " + " | ".join(values) + " |")
    lines = [
        "# MEB Mechanism Figure Notes",
        "",
        "The MP4 files are encoded at 30 fps from 150 fps high-speed recordings. Frame extraction therefore uses `video_time = experimental_time * 5`.",
        "",
        "## Representative frames",
        "",
        "The selected frames compare low and high visually screened microbubble-density states in the developed oscillatory interval. The hydrophone-power percentile at each selected time is reported because a single video frame need not coincide exactly with the center of an acoustic burst.",
        "",
        "\n".join(table_rows),
        "",
        "## Storage-release model",
        "",
        "The model is a conceptual driven, damped, thresholded LC-like relaxation oscillator. A storage state is charged by constant input and discharged through an inertial release coordinate when a threshold is exceeded. It is not fitted to the experiments; it demonstrates how instantaneous heat release and acoustic bursts can exceed the nominal input scale when stored energy is released intermittently.",
        "",
    ]
    (output_dir / "captions.md").write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--raw-root", default=r"Y:\0_Ishraq\New Pool Boiling Video")
    parser.add_argument(
        "--output-dir",
        default=r"manuscripts\meb_multimodal_diagnostics\generated\publication_analysis\mechanism",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    set_style()
    repo_root = Path(args.repo_root).resolve()
    raw_root = Path(args.raw_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    selections: list[dict[str, float | str]] = []
    for test_id in CASE_INFO:
        acoustic_selection = select_peak_valley(repo_root, raw_root, test_id)
        selection = select_visual_frames(ffmpeg, repo_root, raw_root, test_id, acoustic_selection, output_dir)
        selections.append(selection)

    plot_frame_panel(output_dir, selections)
    plot_model(output_dir)
    write_captions(output_dir, selections)
    print(f"Wrote MEB mechanism figures to {output_dir}")


if __name__ == "__main__":
    main()
