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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, y, color=color, linewidth=2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


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
    save_line_plot(
        plots_dir / "heat_flux_vs_time.png",
        time_s,
        heat_flux,
        f"{test_id} Heat Flux vs Time",
        "Time (s)",
        "Heat Flux (W/cm^2)",
        "tab:red",
    )
    save_line_plot(
        plots_dir / "surface_temperature.png",
        time_s,
        surface_temperature,
        f"{test_id} Surface Temperature",
        "Time (s)",
        "Surface Temperature (degC)",
        "tab:purple",
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
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = analyze_case(args)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
