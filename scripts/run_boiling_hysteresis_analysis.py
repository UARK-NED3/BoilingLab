"""Analyze subatmospheric boiling hysteresis from the 30-case thesis dataset.

This runner reproduces the analysis used for the boiling-hysteresis manuscript:

* pressure and surface trends in CHF/HTC and hysteresis,
* stretched-exponential thermal-maturity fits,
* NBR wall-superheat diagnostics,
* Rohsenow sensitivity for q''_NBR(T_NBR),
* flat-surface minimum-film-boiling regime checks,
* held-out 10 kPa post-CHF protocol tests, and
* BubbleID side-view vapor-fraction summaries.

The script intentionally reads the organized spreadsheet rather than raw LVM
files. It is therefore a manuscript-level analysis layer on top of the thermal
single-case and multi-case tools already present in BoilingLab.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

try:
    from CoolProp.CoolProp import PropsSI
except ImportError as exc:  # pragma: no cover - exercised by user environment
    raise SystemExit(
        "CoolProp is required for the water-property calculations. "
        "Install repo dependencies with `python -m pip install -r requirements.txt`."
    ) from exc


DEFAULT_DATA = Path(
    r"C:\Users\hanhu\Box\NED3_Share\Abrar Hoq Fahim\BubbleID-FineTuning\MS Thesis Data_30cases_abrar.xlsx"
)
DEFAULT_SHEET = "MS Thesis"
G = 9.80665

SURFACE_STYLE = {
    "Flat Cu": {"label": "Flat Cu", "color": "#4f9d57", "marker": "s"},
    "MC Cu": {"label": "MC Cu", "color": "#ef4444", "marker": "^"},
    "MP Cu": {"label": "MP Cu", "color": "#4f63ff", "marker": "o"},
}


@dataclass(frozen=True)
class FitResult:
    model: str
    h_min: float
    scale: float
    m: float
    r2: float
    rmse: float


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 15,
            "axes.labelsize": 17,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "legend.fontsize": 12,
            "axes.linewidth": 1.1,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )


def style_grid(ax: plt.Axes) -> None:
    ax.set_axisbelow(True)
    ax.grid(True, color="0.86", zorder=0)


def clean_col(name: object) -> str:
    return " ".join(str(name).replace("\n", " ").split()).strip()


def canonical_surface(value: object) -> str:
    text = str(value).strip()
    if text in {"New MC Cu", "MC", "Microchannel Cu", "Microchannel"}:
        return "MC Cu"
    if text in {"MP", "Micro pin fin Cu", "Micro-pin-fin Cu"}:
        return "MP Cu"
    return text


def first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    normalized = {clean_col(c).lower(): c for c in df.columns}
    for candidate in candidates:
        key = clean_col(candidate).lower()
        if key in normalized:
            return normalized[key]
    raise KeyError(f"None of these columns were found: {list(candidates)}")


def load_hysteresis_dataset(path: Path, sheet_name: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet_name)
    cols = {
        "test_id": first_existing_column(raw, ["Boiling ID"]),
        "pressure_kpa": first_existing_column(raw, ["Mean Pressure (kPa)", "Pressure"]),
        "surface": first_existing_column(raw, ["Surface"]),
        "q_chf": first_existing_column(raw, ["CHF (W/cm^2)", "CHF"]),
        "htc_chf": first_existing_column(raw, ["HTC at CHF (W/cm^2K)", "HTC at CHF"]),
        "q_nbr": first_existing_column(raw, ["NBR (W/cm^2)", "NBR"]),
        "t_nbr": first_existing_column(raw, ["Temperature at NBR"]),
        "tmax": first_existing_column(raw, ["T_surface Max (degC)", "T_surface Max"]),
        "tsat": first_existing_column(raw, ["Saturation Temperature (degC)", "Saturation Temperature"]),
    }
    optional = {}
    for out_name, candidates in {
        "heater_power_W": ["MagnaDC Power (W)"],
        "t_chf_s": ["Time (sec) at CHF"],
        "t_nbr_s": ["Time (sec) at NBR"],
        "q_min_W_cm2": ["q_min (between NBR and CHF)"],
        "rusting_days": ["Rusting (Days)"],
        "protocol_note": ["Unnamed: 38"],
        "onb_vf": ["ONB_vf"],
        "chf_vf": ["CHF_vf"],
        "nbr_vf": ["NBR_vf"],
        "onb_count": ["ONB_count"],
        "chf_count": ["CHF_count"],
        "nbr_count": ["NBR_count"],
    }.items():
        try:
            optional[out_name] = first_existing_column(raw, candidates)
        except KeyError:
            pass

    data = pd.DataFrame(
        {
            "test_id": raw[cols["test_id"]].astype(str),
            "pressure_kpa": pd.to_numeric(raw[cols["pressure_kpa"]], errors="coerce"),
            "surface": raw[cols["surface"]].map(canonical_surface),
            "q_chf_W_cm2": pd.to_numeric(raw[cols["q_chf"]], errors="coerce"),
            "htc_chf_W_cm2K": pd.to_numeric(raw[cols["htc_chf"]], errors="coerce"),
            "q_nbr_W_cm2": pd.to_numeric(raw[cols["q_nbr"]], errors="coerce"),
            "T_nbr_C": pd.to_numeric(raw[cols["t_nbr"]], errors="coerce"),
            "T_max_C": pd.to_numeric(raw[cols["tmax"]], errors="coerce"),
            "T_sat_C": pd.to_numeric(raw[cols["tsat"]], errors="coerce"),
        }
    )
    for out_name, col in optional.items():
        if out_name == "protocol_note":
            data[out_name] = raw[col].astype("string")
        elif out_name == "rusting_days":
            data[out_name] = raw[col].astype("string")
        else:
            data[out_name] = pd.to_numeric(raw[col], errors="coerce")

    data = data.dropna(
        subset=["pressure_kpa", "surface", "q_chf_W_cm2", "q_nbr_W_cm2", "T_max_C", "T_sat_C"]
    ).copy()
    data["H"] = data["q_nbr_W_cm2"] / data["q_chf_W_cm2"]
    data["DeltaT_max_K"] = data["T_max_C"] - data["T_sat_C"]
    data["DeltaT_NBR_K"] = data["T_nbr_C"] - data["T_sat_C"]
    if {"chf_vf", "nbr_vf"}.issubset(data.columns):
        data["nbr_vf_over_chf_vf"] = data["nbr_vf"] / data["chf_vf"]
        data["delta_vf_chf_to_nbr"] = data["nbr_vf"] - data["chf_vf"]
    if {"chf_count", "nbr_count"}.issubset(data.columns):
        data["delta_count_chf_to_nbr"] = data["nbr_count"] - data["chf_count"]
    if {"t_chf_s", "t_nbr_s"}.issubset(data.columns):
        data["post_chf_to_nbr_s"] = data["t_nbr_s"] - data["t_chf_s"]
    data = data.sort_values(["surface", "pressure_kpa"]).reset_index(drop=True)
    return data


def load_protocol_validation(path: Path, sheet_name: str) -> pd.DataFrame:
    """Load the five 10 kPa flat-Cu tests with deliberately extended heating.

    These cases are not included in the 30-case fit. They perturb the post-CHF
    thermal history at approximately fixed pressure, surface, and heater power.
    """
    data = load_hysteresis_dataset(path, sheet_name)
    data = data[data["test_id"].str.extract(r"(\d+)$", expand=False).isin(["420", "421", "422", "423", "424"])].copy()
    if len(data) != 5:
        raise ValueError(f"Expected protocol cases Boiling-420--424; found {len(data)} rows in {path}")
    targets = {
        "Boiling-420": np.nan,
        "Boiling-421": 100.0,
        "Boiling-422": 150.0,
        "Boiling-423": 200.0,
        "Boiling-424": 250.0,
    }
    labels = {
        "Boiling-420": "baseline",
        "Boiling-421": "100 °C target",
        "Boiling-422": "150 °C target",
        "Boiling-423": "200 °C target",
        "Boiling-424": "250 °C target",
    }
    data["target_Tmax_C"] = data["test_id"].map(targets)
    data["protocol_label"] = data["test_id"].map(labels)
    return data.sort_values("T_max_C").reset_index(drop=True)


def hysteresis_constant_scale(delta_t: np.ndarray, h_min: float, delta_t_s: float, m: float) -> np.ndarray:
    x = np.maximum(np.asarray(delta_t, dtype=float), 0.0) / max(delta_t_s, 1e-12)
    return h_min + (1.0 - h_min) * np.exp(-(x**m))


def hysteresis_tref_scale(inputs: tuple[np.ndarray, np.ndarray], h_min: float, t_ref_c: float, m: float) -> np.ndarray:
    tmax_c, tsat_c = inputs
    denominator = np.maximum(t_ref_c - tsat_c, 1e-9)
    x = np.maximum((tmax_c - tsat_c) / denominator, 0.0)
    return h_min + (1.0 - h_min) * np.exp(-(x**m))


def fit_models(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    y = data["H"].to_numpy(float)
    dt = data["DeltaT_max_K"].to_numpy(float)
    tmax = data["T_max_C"].to_numpy(float)
    tsat = data["T_sat_C"].to_numpy(float)

    popt_const_fixed, _ = curve_fit(
        lambda x, delta_t_s, m: hysteresis_constant_scale(x, 0.0, delta_t_s, m),
        dt,
        y,
        p0=(160.0, 2.0),
        bounds=([1.0, 0.1], [1000.0, 8.0]),
        maxfev=100_000,
    )
    popt_const = np.array([0.0, *popt_const_fixed])
    pred_const = hysteresis_constant_scale(dt, *popt_const)

    popt_tref_fixed, _ = curve_fit(
        lambda inputs, t_ref_c, m: hysteresis_tref_scale(inputs, 0.0, t_ref_c, m),
        (tmax, tsat),
        y,
        p0=(260.0, 2.0),
        bounds=([float(np.nanmax(tsat) + 1.0), 0.1], [600.0, 8.0]),
        maxfev=100_000,
    )
    popt_tref = np.array([0.0, *popt_tref_fixed])
    pred_tref = hysteresis_tref_scale((tmax, tsat), *popt_tref)

    def score(name: str, params: tuple[float, float, float], pred: np.ndarray) -> FitResult:
        resid = y - pred
        ss_res = float(np.sum(resid**2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot
        rmse = float(np.sqrt(np.mean(resid**2)))
        return FitResult(name, float(params[0]), float(params[1]), float(params[2]), r2, rmse)

    rows = [
        score("constant_deltaT_scale", tuple(popt_const), pred_const),
        score("pressure_dependent_Tref_scale", tuple(popt_tref), pred_tref),
    ]
    table = pd.DataFrame([r.__dict__ for r in rows])
    predictions = {"constant": pred_const, "tref": pred_tref}
    return table, predictions


def water_saturation_props(pressure_kpa: float) -> dict[str, float]:
    p = pressure_kpa * 1000.0
    tsat_k = PropsSI("T", "P", p, "Q", 0, "Water")
    rho_l = PropsSI("D", "P", p, "Q", 0, "Water")
    rho_v = PropsSI("D", "P", p, "Q", 1, "Water")
    h_l = PropsSI("H", "P", p, "Q", 0, "Water")
    h_v = PropsSI("H", "P", p, "Q", 1, "Water")
    sigma = PropsSI("I", "P", p, "Q", 0, "Water")
    mu_l = PropsSI("V", "P", p, "Q", 0, "Water")
    cp_l = PropsSI("C", "P", p, "Q", 0, "Water")
    k_l = PropsSI("L", "P", p, "Q", 0, "Water")
    mu_v = PropsSI("V", "P", p, "Q", 1, "Water")
    k_v = PropsSI("L", "P", p, "Q", 1, "Water")
    return {
        "pressure_kpa": pressure_kpa,
        "tsat_c": tsat_k - 273.15,
        "rho_l": rho_l,
        "rho_v": rho_v,
        "h_fg": h_v - h_l,
        "sigma": sigma,
        "mu_l": mu_l,
        "cp_l": cp_l,
        "k_l": k_l,
        "mu_v": mu_v,
        "k_v": k_v,
    }


def zuber_chf_w_m2(props: dict[str, float]) -> float:
    return (
        0.131
        * props["h_fg"]
        * props["rho_v"] ** 0.5
        * (props["sigma"] * G * (props["rho_l"] - props["rho_v"])) ** 0.25
    )


def berenson_minimum_heat_flux_w_m2(props: dict[str, float]) -> float:
    """Classical hydrodynamic minimum film boiling heat-flux scale.

    The prefactor varies across presentations of Berenson/Zuber-type minimum
    heat-flux correlations. This form is used here only as an order-of-magnitude
    lower-bound diagnostic for H_min, not as a fitted model.
    """
    return (
        0.09
        * props["rho_v"]
        * props["h_fg"]
        * (props["sigma"] * G * (props["rho_l"] - props["rho_v"]) / (props["rho_l"] + props["rho_v"]) ** 2)
        ** 0.25
    )


def rohsenow_q_w_m2(props: dict[str, float], delta_t_k: np.ndarray, c_sf: float = 0.0128, n: float = 1.0) -> np.ndarray:
    pr_l = props["cp_l"] * props["mu_l"] / props["k_l"]
    dt = np.asarray(delta_t_k, dtype=float)
    return (
        props["mu_l"]
        * props["h_fg"]
        * np.sqrt(G * (props["rho_l"] - props["rho_v"]) / props["sigma"])
        * ((props["cp_l"] * dt) / (c_sf * props["h_fg"] * pr_l**n)) ** 3
    )


def berenson_mfb_temperature_c(props: dict[str, float]) -> tuple[float, float]:
    """Berenson hydrodynamic minimum-film-boiling temperature."""
    rho_delta = props["rho_l"] - props["rho_v"]
    delta_t_b = (
        0.127
        * props["rho_v"]
        * props["h_fg"]
        / props["k_v"]
        * (G * rho_delta / (props["rho_l"] + props["rho_v"])) ** (2.0 / 3.0)
        * (props["sigma"] / (G * rho_delta)) ** 0.5
        * (props["mu_v"] / (G * rho_delta)) ** (1.0 / 3.0)
    )
    return props["tsat_c"] + delta_t_b, delta_t_b


def henry_copper_mfb_temperature_c(props: dict[str, float], t_berenson_c: float, delta_t_b_k: float) -> float:
    """Henry wall-effusivity correction for an oxygen-free copper heater."""
    rho_cu = 8960.0
    k_cu = 391.0
    cp_cu = 385.0
    effusivity_ratio = np.sqrt(
        props["rho_l"] * props["k_l"] * props["cp_l"] / (rho_cu * k_cu * cp_cu)
    )
    correction = 0.5 * delta_t_b_k * (
        effusivity_ratio * props["h_fg"] / (props["cp_l"] * delta_t_b_k)
    ) ** 0.6
    return t_berenson_c + correction


def temperature_model_curves() -> pd.DataFrame:
    rows = []
    for pressure_kpa in np.linspace(1.0, 110.0, 220):
        props = water_saturation_props(float(pressure_kpa))
        t_berenson_c, delta_t_b_k = berenson_mfb_temperature_c(props)
        rows.append(
            {
                "pressure_kpa": pressure_kpa,
                "T_sat_C": props["tsat_c"],
                "DeltaT_MFB_Berenson_K": delta_t_b_k,
                "T_MFB_Berenson_C": t_berenson_c,
                "T_MFB_Henry_Cu_C": henry_copper_mfb_temperature_c(props, t_berenson_c, delta_t_b_k),
            }
        )
    return pd.DataFrame(rows)


def add_surface_points(ax: plt.Axes, data: pd.DataFrame, x_col: str, y_col: str, label: bool = True) -> None:
    for surface, style in SURFACE_STYLE.items():
        subset = data[data["surface"] == surface]
        ax.scatter(
            subset[x_col],
            subset[y_col],
            s=58,
            marker=style["marker"],
            facecolor=style["color"],
            edgecolor="black",
            linewidth=0.7,
            label=style["label"] if label else None,
            zorder=10,
        )


def savefig(fig: plt.Figure, output_dir: Path, name: str) -> None:
    fig.savefig(output_dir / f"{name}.png", dpi=300)
    fig.savefig(output_dir / f"{name}.pdf")
    plt.close(fig)


def make_plots(
    data: pd.DataFrame,
    fit_table: pd.DataFrame,
    output_dir: Path,
    protocol_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8), constrained_layout=True)
    add_surface_points(axes[0], data, "pressure_kpa", "q_chf_W_cm2")
    axes[0].set_xlabel("Pressure, P (kPa)")
    axes[0].set_ylabel(r"CHF, $q''_{\mathrm{CHF}}$ (W/cm$^2$)")
    axes[0].set_ylim(0, 200)
    style_grid(axes[0])
    add_surface_points(axes[1], data, "pressure_kpa", "htc_chf_W_cm2K")
    axes[1].set_xlabel("Pressure, P (kPa)")
    axes[1].set_ylabel(r"HTC at CHF (W/cm$^2\cdot$K)")
    axes[1].set_ylim(0, 12.5)
    style_grid(axes[1])
    axes[0].legend(loc="upper left")
    savefig(fig, plots_dir, "fig01_chf_htc_vs_pressure")

    fig, ax = plt.subplots(figsize=(5.4, 4.8), constrained_layout=True)
    add_surface_points(ax, data, "pressure_kpa", "H")
    ax.set_xlabel("Pressure, P (kPa)")
    ax.set_ylabel(r"Boiling hysteresis, $q''_{\mathrm{NBR}}/q''_{\mathrm{CHF}}$")
    ax.set_ylim(0.4, 1.1)
    style_grid(ax)
    ax.legend(loc="upper right")
    savefig(fig, plots_dir, "fig02_hysteresis_vs_pressure")

    const = fit_table.loc[fit_table["model"] == "constant_deltaT_scale"].iloc[0]
    xfit = np.linspace(0, max(260.0, data["DeltaT_max_K"].max() * 1.05), 400)
    yfit = hysteresis_constant_scale(xfit, const.h_min, const.scale, const.m)
    fig, ax = plt.subplots(figsize=(5.4, 4.8), constrained_layout=True)
    add_surface_points(ax, data, "DeltaT_max_K", "H")
    ax.plot(xfit, yfit, color="black", lw=2.0, label="Present model", zorder=4)
    ax.set_xlabel(r"Maximum wall superheat, $T_{\mathrm{max}}-T_{\mathrm{sat}}$ (K)")
    ax.set_ylabel(r"Boiling hysteresis, $q''_{\mathrm{NBR}}/q''_{\mathrm{CHF}}$")
    ax.set_ylim(0.4, 1.1)
    style_grid(ax)
    ax.legend(loc="upper right")
    savefig(fig, plots_dir, "fig03_hysteresis_constant_scale_fit")

    fig, ax = plt.subplots(figsize=(5.4, 4.8), constrained_layout=True)
    add_surface_points(ax, data, "pressure_kpa", "DeltaT_NBR_K")
    mean = float(data["DeltaT_NBR_K"].mean())
    std = float(data["DeltaT_NBR_K"].std(ddof=1))
    ax.axhspan(mean - std, mean + std, color="0.85", alpha=0.7, label=r"Mean $\pm$ 1 SD")
    ax.axhline(mean, color="black", ls="--", lw=1.8, label=f"Mean = {mean:.1f} K")
    ax.set_xlabel("Pressure, P (kPa)")
    ax.set_ylabel(r"NBR wall superheat, $T_{\mathrm{NBR}}-T_{\mathrm{sat}}$ (K)")
    ax.set_ylim(0, 40)
    ax.set_xticks(np.arange(10, 111, 20))
    style_grid(ax)
    ax.legend(loc="upper right")
    savefig(fig, plots_dir, "fig04_nbr_wall_superheat_vs_pressure")

    qmodel_rows = []
    for _, row in data.dropna(subset=["DeltaT_NBR_K"]).iterrows():
        props = water_saturation_props(float(row["pressure_kpa"]))
        q_roh = rohsenow_q_w_m2(props, np.array([row["DeltaT_NBR_K"]]), c_sf=0.0128)[0] / 1e4
        q_roh_alt = rohsenow_q_w_m2(props, np.array([row["DeltaT_NBR_K"]]), c_sf=0.0107)[0] / 1e4
        qmodel_rows.append(
            {
                "test_id": row["test_id"],
                "surface": row["surface"],
                "pressure_kpa": row["pressure_kpa"],
                "q_NBR_exp_W_cm2": row["q_nbr_W_cm2"],
                "q_NBR_rohsenow_Csf_0p0128_W_cm2": q_roh,
                "q_NBR_rohsenow_Csf_0p0107_W_cm2": q_roh_alt,
            }
        )
    qmodel = pd.DataFrame(qmodel_rows)
    qmodel.to_csv(output_dir / "qnbr_rohsenow_comparison.csv", index=False)

    sensitivity_rows = []
    for c_sf, column in [
        (0.0128, "q_NBR_rohsenow_Csf_0p0128_W_cm2"),
        (0.0107, "q_NBR_rohsenow_Csf_0p0107_W_cm2"),
    ]:
        for surface in [*SURFACE_STYLE, "All"]:
            subset = qmodel if surface == "All" else qmodel[qmodel["surface"] == surface]
            ratio = subset["q_NBR_exp_W_cm2"] / subset[column]
            sensitivity_rows.append(
                {
                    "C_sf": c_sf,
                    "surface": surface,
                    "n": len(subset),
                    "median_exp_over_model": ratio.median(),
                    "min_exp_over_model": ratio.min(),
                    "max_exp_over_model": ratio.max(),
                    "n_within_30pct": int(((ratio >= 0.7) & (ratio <= 1.3)).sum()),
                }
            )
    pd.DataFrame(sensitivity_rows).to_csv(output_dir / "qnbr_rohsenow_sensitivity_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.55), constrained_layout=True)
    lim = [0, 115]
    for panel, (ax, c_sf, column) in enumerate(
        zip(
            axes,
            [0.0128, 0.0107],
            ["q_NBR_rohsenow_Csf_0p0128_W_cm2", "q_NBR_rohsenow_Csf_0p0107_W_cm2"],
        )
    ):
        for surface, style in SURFACE_STYLE.items():
            subset = qmodel[qmodel["surface"] == surface]
            ax.scatter(
                subset[column],
                subset["q_NBR_exp_W_cm2"],
                s=50,
                marker=style["marker"],
                facecolor=style["color"],
                edgecolor="black",
                linewidth=0.7,
                label=style["label"],
                zorder=10,
            )
        ax.fill_between(lim, [0.7 * v for v in lim], [1.3 * v for v in lim], color="0.9", zorder=1)
        ax.plot(lim, lim, color="black", lw=1.6, label="Rohsenow model", zorder=3)
        ax.plot(lim, [1.3 * v for v in lim], color="black", ls="--", lw=1.0, zorder=2)
        ax.plot(lim, [0.7 * v for v in lim], color="black", ls="--", lw=1.0, zorder=2)
        ax.text(
            78,
            1.3 * 78 + 2,
            "+30%",
            rotation=np.degrees(np.arctan(1.3)),
            fontsize=7.5,
            ha="center",
            va="bottom",
            zorder=4,
        )
        ax.text(
            96,
            0.7 * 96 - 3,
            "-30%",
            rotation=np.degrees(np.arctan(0.7)),
            fontsize=7.5,
            ha="center",
            va="top",
            zorder=4,
        )
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_box_aspect(1 / 1.125)
        ax.set_xlabel(r"Model-predicted $q''_{\mathrm{NBR}}(T_{\mathrm{NBR}})$ (W/cm$^2$)", fontsize=10)
        ax.set_ylabel(r"Experimental $q''_{\mathrm{NBR}}$ (W/cm$^2$)", fontsize=10)
        ax.tick_params(labelsize=9)
        ax.text(0.03, 0.97, f"({chr(97 + panel)})", transform=ax.transAxes, va="top", fontsize=9)
        ax.text(0.04, 0.87, rf"$C_{{\mathrm{{sf}}}}={c_sf:.4f}$", transform=ax.transAxes, ha="left", fontsize=9)
        style_grid(ax)
    axes[1].legend(loc="lower right", fontsize=7.5)
    savefig(fig, plots_dir, "fig05_qnbr_rohsenow_parity")

    temp_models = temperature_model_curves()
    temp_models.to_csv(output_dir / "flat_mfb_temperature_models.csv", index=False)
    flat = data[data["surface"] == "Flat Cu"].copy()
    flat["series"] = "standard 30-case design"
    flat_points = [flat]
    if protocol_data is not None and not protocol_data.empty:
        protocol_flat = protocol_data[protocol_data["surface"] == "Flat Cu"].copy()
        protocol_flat["series"] = "10 kPa protocol validation"
        flat_points.append(protocol_flat)
    pd.concat(flat_points, ignore_index=True).to_csv(output_dir / "flat_mfb_regime_points.csv", index=False)

    fig, ax = plt.subplots(figsize=(5.4, 4.8), constrained_layout=True)
    ax.plot(temp_models["pressure_kpa"], temp_models["T_sat_C"], color="black", ls=":", lw=1.8, label=r"IAPWS $T_{\mathrm{sat}}$")
    ax.plot(temp_models["pressure_kpa"], temp_models["T_MFB_Berenson_C"], color="#d97706", lw=2.0, label=r"Berenson $T_{\mathrm{MFB}}$")
    ax.plot(temp_models["pressure_kpa"], temp_models["T_MFB_Henry_Cu_C"], color="#7c3aed", lw=2.0, label=r"Henry-Cu $T_{\mathrm{MFB}}$")
    ax.scatter(flat["pressure_kpa"], flat["T_max_C"], s=58, marker="s", facecolor=SURFACE_STYLE["Flat Cu"]["color"], edgecolor="black", linewidth=0.7, label=r"Standard flat Cu, $T_{\mathrm{max}}$", zorder=10)
    if protocol_data is not None and not protocol_data.empty:
        ax.scatter(protocol_flat["pressure_kpa"], protocol_flat["T_max_C"], s=66, marker="D", facecolor="0.65", edgecolor="black", linewidth=0.8, label=r"Protocol validation, $T_{\mathrm{max}}$", zorder=11)
    ax.set_xlim(1, 110)
    ax.set_ylim(0, 280)
    ax.set_xlabel("Pressure, P (kPa)")
    ax.set_ylabel("Temperature, T (°C)")
    style_grid(ax)
    ax.legend(loc="upper left", fontsize=9)
    savefig(fig, plots_dir, "fig07_flat_mfb_regime_check")

    if {"onb_vf", "chf_vf", "nbr_vf"}.issubset(data.columns):
        vf_long = data.melt(
            id_vars=["test_id", "surface", "pressure_kpa", "H"],
            value_vars=["onb_vf", "chf_vf", "nbr_vf"],
            var_name="stage",
            value_name="vapor_fraction",
        ).dropna(subset=["vapor_fraction"])
        vf_long["stage"] = vf_long["stage"].map({"onb_vf": "ONB", "chf_vf": "CHF", "nbr_vf": "NBR"})
        vf_long.to_csv(output_dir / "bubbleid_vapor_fraction_long.csv", index=False)

        bdf = data.dropna(subset=["onb_vf", "chf_vf", "nbr_vf", "nbr_vf_over_chf_vf", "H"]).copy()
        bubble_summary = []
        for group_name, group_df in [("All image-analyzed cases", bdf)] + [
            (style["label"], bdf[bdf["surface"] == surface]) for surface, style in SURFACE_STYLE.items()
        ]:
            if group_df.empty:
                continue
            row = {"group": group_name, "n": int(len(group_df))}
            for col in ["onb_vf", "chf_vf", "nbr_vf", "nbr_vf_over_chf_vf", "delta_vf_chf_to_nbr"]:
                if col in group_df:
                    row[f"{col}_mean"] = float(group_df[col].mean())
                    row[f"{col}_std"] = float(group_df[col].std(ddof=1)) if len(group_df) > 1 else np.nan
            bubble_summary.append(row)
        pd.DataFrame(bubble_summary).to_csv(output_dir / "bubbleid_vapor_fraction_summary.csv", index=False)

        stages = ["ONB", "CHF", "NBR"]
        stage_cols = ["onb_vf", "chf_vf", "nbr_vf"]
        x_stage = np.arange(len(stages))
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.65), constrained_layout=True)
        for _, row in bdf.iterrows():
            style = SURFACE_STYLE[row["surface"]]
            y = [row[col] for col in stage_cols]
            ax1.plot(x_stage, y, color=style["color"], lw=1.0, alpha=0.30, zorder=2)
            ax1.scatter(
                x_stage,
                y,
                s=44,
                marker=style["marker"],
                facecolor=style["color"],
                edgecolor="black",
                linewidth=0.6,
                zorder=10,
            )
        means = bdf[stage_cols].mean().to_numpy(float)
        stds = bdf[stage_cols].std(ddof=1).to_numpy(float)
        ax1.errorbar(
            x_stage,
            means,
            yerr=stds,
            color="black",
            marker="D",
            ms=5,
            lw=2.0,
            capsize=4,
            label=r"Mean $\pm$ SD",
            zorder=12,
        )
        for surface, style in SURFACE_STYLE.items():
            ax1.scatter(
                [],
                [],
                s=44,
                marker=style["marker"],
                facecolor=style["color"],
                edgecolor="black",
                label=style["label"],
            )
        ax1.set_xticks(x_stage, stages)
        ax1.set_ylabel("Side-view vapor fraction", fontsize=12)
        ax1.tick_params(labelsize=11)
        ax1.set_ylim(0, 0.85)
        style_grid(ax1)
        ax1.set_box_aspect(1 / 1.125)
        ax1.legend(framealpha=0.92, loc="lower right", fontsize=8)
        ax1.text(0.03, 0.97, "(a)", transform=ax1.transAxes, va="top", ha="left", fontsize=9, fontweight="normal")

        for surface, style in SURFACE_STYLE.items():
            subset = bdf[bdf["surface"] == surface]
            ax2.scatter(
                subset["nbr_vf_over_chf_vf"],
                subset["H"],
                s=54,
                marker=style["marker"],
                facecolor=style["color"],
                edgecolor="black",
                linewidth=0.7,
                label=style["label"],
                zorder=10,
            )
        spearman_r = bdf["nbr_vf_over_chf_vf"].corr(bdf["H"], method="spearman")
        ax2.text(0.03, 0.97, "(b)", transform=ax2.transAxes, va="top", ha="left", fontsize=9, fontweight="normal", zorder=10)
        ax2.text(
            0.04,
            0.91,
            f"Spearman r = {spearman_r:.2f}",
            transform=ax2.transAxes,
            va="top",
            ha="left",
            fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2.0},
            zorder=10,
        )
        ax2.set_xlabel(r"Vapor persistence, $VF_{\mathrm{NBR}}/VF_{\mathrm{CHF}}$", fontsize=12)
        ax2.set_ylabel(r"Boiling hysteresis, $H$", fontsize=12)
        ax2.tick_params(labelsize=11)
        ax2.set_xlim(0.55, 1.2)
        ax2.set_ylim(0.45, 1.05)
        style_grid(ax2)
        ax2.set_box_aspect(1 / 1.125)
        ax2.legend(framealpha=0.92, loc="lower left", fontsize=8)
        savefig(fig, plots_dir, "fig06_bubbleid_vapor_fraction_by_stage")

    return qmodel


def write_model_diagnostics(
    data: pd.DataFrame,
    fit_table: pd.DataFrame,
    output_dir: Path,
    input_path: Path,
    protocol_data: pd.DataFrame | None = None,
    protocol_path: Path | None = None,
) -> None:
    pressure_grid = np.linspace(10.0, 100.0, 91)
    rows = []
    for pressure in pressure_grid:
        props = water_saturation_props(float(pressure))
        q_chf = zuber_chf_w_m2(props) / 1e4
        q_mhf = berenson_minimum_heat_flux_w_m2(props) / 1e4
        rows.append(
            {
                "pressure_kpa": pressure,
                "T_sat_C": props["tsat_c"],
                "q_CHF_Zuber_W_cm2": q_chf,
                "q_MHF_Berenson_scale_W_cm2": q_mhf,
                "H_min_hydrodynamic_scale": q_mhf / q_chf,
            }
        )
    pd.DataFrame(rows).to_csv(output_dir / "theoretical_hmin_diagnostic.csv", index=False)

    summary = {
        "input_file": str(input_path.resolve()),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "n_cases": int(len(data)),
        "surfaces": sorted(data["surface"].dropna().unique().tolist()),
        "pressure_range_kPa": [float(data["pressure_kpa"].min()), float(data["pressure_kpa"].max())],
        "deltaT_NBR_mean_K": float(data["DeltaT_NBR_K"].mean()),
        "deltaT_NBR_std_K": float(data["DeltaT_NBR_K"].std(ddof=1)),
        "fit_results": fit_table.to_dict(orient="records"),
    }
    if protocol_data is not None and protocol_path is not None:
        summary["protocol_validation_file"] = str(protocol_path.resolve())
        summary["protocol_validation_sha256"] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        summary["n_protocol_validation_cases"] = int(len(protocol_data))
    (output_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def write_readme(output_dir: Path) -> None:
    text = """# Boiling Hysteresis Analysis Outputs

This folder is generated by `scripts/run_boiling_hysteresis_analysis.py`.

## Input

The input is the organized 30-case spreadsheet (`MS Thesis Data_30cases.xlsx`).
The runner reads thermal summary quantities, NBR temperature, and optional
BubbleID side-view vapor-fraction / bubble-count columns.

An optional five-case flat-copper protocol spreadsheet can be supplied with
`--protocol-data`. Those approximately 10 kPa cases are written separately and
are not included in the 30-case parameter fits.

## Core Models

The manuscript-level hysteresis coordinate is

```text
H = q''_NBR / q''_CHF
```

and the constant-superheat baseline is

```text
H = H_min + (1 - H_min) exp[-((T_max - T_sat) / DeltaT_s)^m].
```

The public runner also fits the pressure-dependent reference-temperature form,

```text
H = H_min + (1 - H_min) exp[-((T_max - T_sat) / (T_ref - T_sat))^m].
```

For submission diagnostics, run
`scripts/run_boiling_hysteresis_submission_diagnostics.py`. That script fixes
`H_min = 0` as a parsimonious boundary condition, compares candidate models by
AICc and held-out validation, tests residual structure, profiles `H_min`, and
generates 2,000 pressure-block bootstrap intervals. It also evaluates the
locked fits against the optional protocol cases. The preferred model uses
`(T_max - T_sat)/(T_ref - T_sat)`; it should be treated as a semi-empirical
interpolation, not as a universal stability law.

The diagnostic
`theoretical_hmin_diagnostic.csv` compares it against a hydrodynamic
`q''_MHF / q''_CHF` scale from Berenson/Zuber-type limiting heat fluxes.

## Main Figures

- `fig01_chf_htc_vs_pressure`: heating-branch performance summary.
- `fig02_hysteresis_vs_pressure`: pressure trend in boiling hysteresis.
- `fig03_hysteresis_constant_scale_fit`: global collapse versus maximum wall
  superheat.
- `fig04_nbr_wall_superheat_vs_pressure`: NBR wall-superheat band, supporting
  temperature-controlled rewetting.
- `fig05_qnbr_rohsenow_parity`: sensitivity of q''_NBR(T_NBR) to the
  Rohsenow liquid-surface coefficient (`C_sf = 0.0128` and `0.0107`).
- `fig06_bubbleid_vapor_fraction_by_stage`: two-panel BubbleID diagnostic
  showing (a) side-view vapor fraction at ONB, CHF, and NBR and (b) vapor
  persistence, `VF_NBR/VF_CHF`, versus the boiling hysteresis ratio.
- `fig07_flat_mfb_regime_check`: flat-copper regime check against Berenson and
  Henry minimum-film-boiling temperatures; structured surfaces are omitted
  because no validated geometry-specific MFB model is available.

## Notes

BubbleID vapor fraction is a side-view projected metric. It is useful as a
regime diagnostic but should not be interpreted as the true wall dry-area
fraction. The current fine-tuned model used all 24 labeled images for training,
so these optical quantities are descriptive rather than held-out validation
metrics. The thermal design contains one test per pressure--surface condition;
cross-validation does not replace repeat experiments or a propagated
measurement-uncertainty budget.
"""
    (output_dir / "README.md").write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Organized hysteresis spreadsheet.")
    parser.add_argument("--sheet", default=DEFAULT_SHEET, help="Worksheet name in the spreadsheet.")
    parser.add_argument(
        "--protocol-data",
        type=Path,
        default=None,
        help="Optional workbook containing held-out cases Boiling-420--424.",
    )
    parser.add_argument("--protocol-sheet", default=DEFAULT_SHEET, help="Worksheet for protocol validation data.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("manuscripts/boiling_hysteresis_subatmospheric/generated"),
        help="Output directory for generated CSV files and plots.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    set_style()
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_hysteresis_dataset(args.data, args.sheet)
    data.to_csv(output_dir / "processed_hysteresis_data.csv", index=False)
    protocol_data = None
    if args.protocol_data is not None:
        protocol_data = load_protocol_validation(args.protocol_data, args.protocol_sheet)
        protocol_data.to_csv(output_dir / "protocol_validation_data.csv", index=False)
    fit_table, _ = fit_models(data)
    fit_table.to_csv(output_dir / "hysteresis_fit_summary.csv", index=False)
    make_plots(data, fit_table, output_dir, protocol_data=protocol_data)
    write_model_diagnostics(
        data,
        fit_table,
        output_dir,
        args.data,
        protocol_data=protocol_data,
        protocol_path=args.protocol_data,
    )
    write_readme(output_dir)
    print(f"Wrote hysteresis analysis outputs to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
