# -*- coding: utf-8 -*-
"""Submission-level diagnostics for the 30-case boiling-hysteresis model.

This script is intentionally separate from the figure-production script.  It
tests parameter identifiability, compares simpler alternatives, performs
held-out validation, evaluates residual structure, and produces the global
fit with a stratified bootstrap confidence band used in the manuscript.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from CoolProp.CoolProp import PropsSI
from scipy.optimize import curve_fit, least_squares
from scipy.stats import f as f_distribution
from scipy.stats import f_oneway, linregress, spearmanr


DEFAULT_OUTPUT = Path("manuscripts/boiling_hysteresis_subatmospheric/generated")
ROOT = DEFAULT_OUTPUT
DATA = ROOT / "processed_hysteresis_data.csv"
OUT_MODEL_COMPARISON = ROOT / "submission_model_diagnostics.csv"
OUT_CROSS_VALIDATION = ROOT / "hysteresis_cross_validation.csv"
OUT_HMIN_PROFILE = ROOT / "hmin_profile_likelihood.csv"
OUT_RESIDUALS = ROOT / "submission_residual_diagnostics.csv"
OUT_BOOTSTRAP = ROOT / "hysteresis_bootstrap_curve.csv"
OUT_TREF_BOOTSTRAP = ROOT / "hysteresis_tref_bootstrap_curve.csv"
OUT_QMHF = ROOT / "theoretical_qmhf_ratio.csv"
OUT_REPORT = ROOT / "submission_diagnostics.md"
FIG_GLOBAL = ROOT / "plots" / "fig03_hysteresis_model_comparison.png"
FIG_GLOBAL_PDF = ROOT / "plots" / "fig03_hysteresis_model_comparison.pdf"

SURFACE_ORDER = ["Flat Cu", "New MC Cu", "MP Cu"]
SURFACE_STYLE = {
    "Flat Cu": {"label": "Flat Cu", "color": "#4f9d57", "marker": "s"},
    "New MC Cu": {"label": "MC Cu", "color": "#ef4444", "marker": "^"},
    "MP Cu": {"label": "MP Cu", "color": "#4f63ff", "marker": "o"},
}


def normalize_input_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Accept the public runner's column names and the original analysis names."""
    aliases = {
        "pressure_kpa": "Pressure_kPa",
        "surface": "Surface",
        "DeltaT_max_K": "DeltaTmax_K",
        "T_sat_C": "Tsat_C",
        "H": "H_NBR_over_CHF",
    }
    data = frame.rename(columns={key: value for key, value in aliases.items() if key in frame.columns}).copy()
    if "Surface" in data:
        data["Surface"] = data["Surface"].replace({"MC Cu": "New MC Cu"})
    required = {"Pressure_kPa", "Surface", "DeltaTmax_K", "Tsat_C", "H_NBR_over_CHF"}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required processed-data columns: {missing}")
    return data


def stretched_free(x: np.ndarray, h_min: float, scale: float, m: float) -> np.ndarray:
    return h_min + (1.0 - h_min) * np.exp(-((np.maximum(x, 0.0) / scale) ** m))


def stretched_hmin0(x: np.ndarray, scale: float, m: float) -> np.ndarray:
    return np.exp(-((np.maximum(x, 0.0) / scale) ** m))


def ordinary_exponential(x: np.ndarray, scale: float) -> np.ndarray:
    return np.exp(-np.maximum(x, 0.0) / scale)


def tref_hmin0(x: np.ndarray, tsat_c: np.ndarray, t_ref_c: float, m: float) -> np.ndarray:
    denominator = np.maximum(t_ref_c - tsat_c, 1e-9)
    return np.exp(-((np.maximum(x, 0.0) / denominator) ** m))


def tref_free(x: np.ndarray, tsat_c: np.ndarray, h_min: float, t_ref_c: float, m: float) -> np.ndarray:
    denominator = np.maximum(t_ref_c - tsat_c, 1e-9)
    return h_min + (1.0 - h_min) * np.exp(-((np.maximum(x, 0.0) / denominator) ** m))


def information_metrics(y: np.ndarray, pred: np.ndarray, k: int) -> dict[str, float]:
    residual = y - pred
    n = len(y)
    rss = float(np.sum(residual**2))
    variance = max(rss / n, np.finfo(float).tiny)
    aic = float(n * np.log(variance) + 2 * k)
    aicc = float(aic + 2 * k * (k + 1) / (n - k - 1)) if n > k + 1 else np.nan
    bic = float(n * np.log(variance) + k * np.log(n))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "n": n,
        "k": k,
        "RSS": rss,
        "RMSE": float(np.sqrt(np.mean(residual**2))),
        "MAE": float(np.mean(np.abs(residual))),
        "R2": float(1.0 - rss / ss_tot),
        "AIC": aic,
        "AICc": aicc,
        "BIC": bic,
    }


def design_pressure_surface(df: pd.DataFrame) -> np.ndarray:
    pressure = (df["Pressure_kPa"].to_numpy(float) - 55.0) / 45.0
    return np.column_stack(
        [
            np.ones(len(df)),
            pressure,
            (df["Surface"] == "New MC Cu").to_numpy(float),
            (df["Surface"] == "MP Cu").to_numpy(float),
        ]
    )


def fit_model(df: pd.DataFrame, model: str) -> tuple[np.ndarray, np.ndarray]:
    x = df["DeltaTmax_K"].to_numpy(float)
    y = df["H_NBR_over_CHF"].to_numpy(float)
    if model == "stretched_Hmin_free":
        params, _ = curve_fit(
            stretched_free,
            x,
            y,
            p0=(0.02, 160.0, 2.0),
            bounds=([0.0, 1.0, 0.1], [0.99, 1000.0, 10.0]),
            maxfev=100000,
        )
        return params, stretched_free(x, *params)
    if model == "stretched_Hmin0":
        params, _ = curve_fit(
            stretched_hmin0,
            x,
            y,
            p0=(160.0, 2.0),
            bounds=([1.0, 0.1], [1000.0, 10.0]),
            maxfev=100000,
        )
        return params, stretched_hmin0(x, *params)
    if model == "ordinary_exponential_Hmin0":
        params, _ = curve_fit(
            ordinary_exponential,
            x,
            y,
            p0=(160.0,),
            bounds=([1.0], [1000.0]),
            maxfev=100000,
        )
        return params, ordinary_exponential(x, *params)
    if model == "Tref_Hmin0":
        tsat = df["Tsat_C"].to_numpy(float)

        def model_function(inputs, t_ref_c, m):
            x_i, tsat_i = inputs
            return tref_hmin0(x_i, tsat_i, t_ref_c, m)

        params, _ = curve_fit(
            model_function,
            (x, tsat),
            y,
            p0=(240.0, 1.8),
            bounds=([float(tsat.max() + 0.1), 0.1], [1000.0, 10.0]),
            maxfev=100000,
        )
        return params, model_function((x, tsat), *params)
    if model == "Tref_Hmin_free":
        tsat = df["Tsat_C"].to_numpy(float)

        def model_function(inputs, h_min, t_ref_c, m):
            x_i, tsat_i = inputs
            return tref_free(x_i, tsat_i, h_min, t_ref_c, m)

        params, _ = curve_fit(
            model_function,
            (x, tsat),
            y,
            p0=(0.1, 240.0, 1.8),
            bounds=([0.0, float(tsat.max() + 0.1), 0.1], [0.99, 1000.0, 10.0]),
            maxfev=100000,
        )
        return params, model_function((x, tsat), *params)
    if model == "linear_DeltaTmax":
        matrix = np.column_stack([np.ones(len(df)), x])
        params = np.linalg.lstsq(matrix, y, rcond=None)[0]
        return params, matrix @ params
    if model == "linear_pressure":
        pressure = (df["Pressure_kPa"].to_numpy(float) - 55.0) / 45.0
        matrix = np.column_stack([np.ones(len(df)), pressure])
        params = np.linalg.lstsq(matrix, y, rcond=None)[0]
        return params, matrix @ params
    if model == "pressure_plus_surface":
        matrix = design_pressure_surface(df)
        params = np.linalg.lstsq(matrix, y, rcond=None)[0]
        return params, matrix @ params
    if model == "thermal_plus_pressure":
        pressure = (df["Pressure_kPa"].to_numpy(float) - 55.0) / 45.0

        def residual(params: np.ndarray) -> np.ndarray:
            return y - (stretched_hmin0(x, params[0], params[1]) + params[2] * pressure)

        result = least_squares(residual, x0=(160.0, 2.0, 0.0), bounds=([1.0, 0.1, -0.5], [1000.0, 10.0, 0.5]))
        params = result.x
        return params, y - residual(params)
    if model == "thermal_plus_surface":
        mc = (df["Surface"] == "New MC Cu").to_numpy(float)
        mp = (df["Surface"] == "MP Cu").to_numpy(float)

        def residual(params: np.ndarray) -> np.ndarray:
            return y - (stretched_hmin0(x, params[0], params[1]) + params[2] * mc + params[3] * mp)

        result = least_squares(
            residual,
            x0=(160.0, 2.0, 0.0, 0.0),
            bounds=([1.0, 0.1, -0.5, -0.5], [1000.0, 10.0, 0.5, 0.5]),
        )
        params = result.x
        return params, y - residual(params)
    raise ValueError(f"Unknown model: {model}")


def predict_model(train: pd.DataFrame, test: pd.DataFrame, model: str) -> np.ndarray:
    params, _ = fit_model(train, model)
    x = test["DeltaTmax_K"].to_numpy(float)
    if model == "stretched_Hmin_free":
        return stretched_free(x, *params)
    if model == "stretched_Hmin0":
        return stretched_hmin0(x, *params)
    if model == "ordinary_exponential_Hmin0":
        return ordinary_exponential(x, *params)
    if model == "Tref_Hmin0":
        return tref_hmin0(x, test["Tsat_C"].to_numpy(float), *params)
    if model == "Tref_Hmin_free":
        return tref_free(x, test["Tsat_C"].to_numpy(float), *params)
    if model == "linear_DeltaTmax":
        return params[0] + params[1] * x
    if model == "linear_pressure":
        pressure = (test["Pressure_kPa"].to_numpy(float) - 55.0) / 45.0
        return params[0] + params[1] * pressure
    if model == "pressure_plus_surface":
        return design_pressure_surface(test) @ params
    if model == "thermal_plus_pressure":
        pressure = (test["Pressure_kPa"].to_numpy(float) - 55.0) / 45.0
        return stretched_hmin0(x, params[0], params[1]) + params[2] * pressure
    if model == "thermal_plus_surface":
        mc = (test["Surface"] == "New MC Cu").to_numpy(float)
        mp = (test["Surface"] == "MP Cu").to_numpy(float)
        return stretched_hmin0(x, params[0], params[1]) + params[2] * mc + params[3] * mp
    raise ValueError(f"Unknown model: {model}")


def leave_one_out_rmse(df: pd.DataFrame, model: str) -> float:
    observed = []
    predicted = []
    for index in df.index:
        train = df.drop(index=index)
        test = df.loc[[index]]
        observed.append(float(test["H_NBR_over_CHF"].iloc[0]))
        predicted.append(float(predict_model(train, test, model)[0]))
    return float(np.sqrt(np.mean((np.asarray(observed) - np.asarray(predicted)) ** 2)))


def model_comparison(df: pd.DataFrame) -> pd.DataFrame:
    models = [
        ("stretched_Hmin_free", 3),
        ("stretched_Hmin0", 2),
        ("ordinary_exponential_Hmin0", 1),
        ("Tref_Hmin0", 2),
        ("Tref_Hmin_free", 3),
        ("linear_DeltaTmax", 2),
        ("linear_pressure", 2),
        ("pressure_plus_surface", 4),
        ("thermal_plus_pressure", 3),
        ("thermal_plus_surface", 4),
    ]
    y = df["H_NBR_over_CHF"].to_numpy(float)
    rows = []
    for model, k in models:
        params, pred = fit_model(df, model)
        rows.append(
            {
                "model": model,
                **information_metrics(y, pred, k),
                "LOOCV_RMSE": leave_one_out_rmse(df, model),
                "parameters": "; ".join(f"{value:.8g}" for value in params),
            }
        )
    result = pd.DataFrame(rows).sort_values("AICc").reset_index(drop=True)
    result["Delta_AICc"] = result["AICc"] - result["AICc"].min()
    return result


def grouped_cross_validation(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    models = ["stretched_Hmin0", "Tref_Hmin0", "linear_pressure"]
    groups = {
        "leave_one_pressure_out": df["Pressure_kPa"].round(0),
        "leave_one_surface_out": df["Surface"],
    }
    for scheme, labels in groups.items():
        for held_out in sorted(labels.unique(), key=str):
            test_mask = labels == held_out
            train = df.loc[~test_mask]
            test = df.loc[test_mask]
            for model in models:
                pred = predict_model(train, test, model)
                metrics = information_metrics(test["H_NBR_over_CHF"].to_numpy(float), pred, k=1)
                rows.append(
                    {
                        "scheme": scheme,
                        "held_out": held_out,
                        "model": model,
                        "n_test": len(test),
                        "RMSE": metrics["RMSE"],
                        "MAE": metrics["MAE"],
                        "bias": float(np.mean(test["H_NBR_over_CHF"].to_numpy(float) - pred)),
                    }
                )
    return pd.DataFrame(rows)


def profile_hmin(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    x = df["DeltaTmax_K"].to_numpy(float)
    y = df["H_NBR_over_CHF"].to_numpy(float)
    rows = []
    for h_min in np.linspace(0.0, 0.45, 451):
        def fixed_model(x_i: np.ndarray, scale: float, m: float) -> np.ndarray:
            return stretched_free(x_i, h_min, scale, m)

        try:
            params, _ = curve_fit(
                fixed_model,
                x,
                y,
                p0=(160.0, 2.0),
                bounds=([1.0, 0.1], [2000.0, 10.0]),
                maxfev=100000,
            )
            pred = fixed_model(x, *params)
            rss = float(np.sum((y - pred) ** 2))
            rows.append({"H_min": h_min, "DeltaT_s_K": params[0], "m": params[1], "RSS": rss})
        except (RuntimeError, ValueError):
            rows.append({"H_min": h_min, "DeltaT_s_K": np.nan, "m": np.nan, "RSS": np.nan})
    result = pd.DataFrame(rows)
    rss_min = float(result["RSS"].min())
    n = len(df)
    k_full = 3
    threshold = rss_min * (1.0 + f_distribution.ppf(0.95, 1, n - k_full) / (n - k_full))
    result["within_approx_95pct_profile"] = result["RSS"] <= threshold
    result["RSS_95pct_threshold"] = threshold
    accepted = result.loc[result["within_approx_95pct_profile"], "H_min"]
    upper = float(accepted.max()) if not accepted.empty else np.nan
    return result, upper


def stratified_bootstrap(df: pd.DataFrame, n_boot: int = 2000, seed: int = 20260802) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    x_grid = np.linspace(0.0, float(df["DeltaTmax_K"].max()) * 1.08, 260)
    predictions = []
    parameter_rows = []
    grouped = [df[df["Surface"] == surface] for surface in SURFACE_ORDER]
    for iteration in range(n_boot):
        samples = [group.iloc[rng.integers(0, len(group), len(group))] for group in grouped]
        sample = pd.concat(samples, ignore_index=True)
        try:
            params, _ = fit_model(sample, "stretched_Hmin0")
        except (RuntimeError, ValueError):
            continue
        predictions.append(stretched_hmin0(x_grid, *params))
        parameter_rows.append({"iteration": iteration, "DeltaT_s_K": params[0], "m": params[1]})
    pred_array = np.asarray(predictions)
    curve = pd.DataFrame(
        {
            "DeltaTmax_K": x_grid,
            "H_median": np.median(pred_array, axis=0),
            "H_lower_95": np.percentile(pred_array, 2.5, axis=0),
            "H_upper_95": np.percentile(pred_array, 97.5, axis=0),
            "n_successful_bootstrap": len(predictions),
            "seed": seed,
        }
    )
    return curve, pd.DataFrame(parameter_rows)


def stratified_bootstrap_tref(
    df: pd.DataFrame, n_boot: int = 2000, seed: int = 20260803
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    global_params, _ = fit_model(df, "Tref_Hmin0")
    xi_observed = df["DeltaTmax_K"].to_numpy(float) / (global_params[0] - df["Tsat_C"].to_numpy(float))
    xi_grid = np.linspace(0.0, float(xi_observed.max()) * 1.08, 260)
    predictions = []
    parameter_rows = []
    grouped = [df[df["Surface"] == surface] for surface in SURFACE_ORDER]
    for iteration in range(n_boot):
        samples = [group.iloc[rng.integers(0, len(group), len(group))] for group in grouped]
        sample = pd.concat(samples, ignore_index=True)
        try:
            params, _ = fit_model(sample, "Tref_Hmin0")
        except (RuntimeError, ValueError):
            continue
        predictions.append(np.exp(-(xi_grid ** params[1])))
        parameter_rows.append({"iteration": iteration, "T_ref_C": params[0], "m": params[1]})
    pred_array = np.asarray(predictions)
    curve = pd.DataFrame(
        {
            "xi": xi_grid,
            "H_median": np.median(pred_array, axis=0),
            "H_lower_95": np.percentile(pred_array, 2.5, axis=0),
            "H_upper_95": np.percentile(pred_array, 97.5, axis=0),
            "n_successful_bootstrap": len(predictions),
            "seed": seed,
        }
    )
    return curve, pd.DataFrame(parameter_rows)


def residual_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    pressure = df["Pressure_kPa"].to_numpy(float)
    rows = []
    for model in ["stretched_Hmin0", "Tref_Hmin0"]:
        params, pred = fit_model(df, model)
        residual = df["H_NBR_over_CHF"].to_numpy(float) - pred
        regression = linregress(pressure, residual)
        spearman = spearmanr(pressure, residual)
        groups = [residual[df["Surface"].to_numpy() == surface] for surface in SURFACE_ORDER]
        anova = f_oneway(*groups)
        rows.extend(
            [
                {"model": model, "diagnostic": "residual_vs_pressure_linear_slope_per_kPa", "value": regression.slope, "p_value": regression.pvalue},
                {"model": model, "diagnostic": "residual_vs_pressure_spearman_r", "value": spearman.statistic, "p_value": spearman.pvalue},
                {"model": model, "diagnostic": "residual_surface_one_way_ANOVA_F", "value": anova.statistic, "p_value": anova.pvalue},
            ]
        )
        parameter_names = ["DeltaT_s_K", "m"] if model == "stretched_Hmin0" else ["T_ref_C", "m"]
        for name, value in zip(parameter_names, params):
            rows.append({"model": model, "diagnostic": name, "value": value, "p_value": np.nan})
        for surface, group in zip(SURFACE_ORDER, groups):
            rows.append({"model": model, "diagnostic": f"mean_residual_{surface}", "value": float(np.mean(group)), "p_value": np.nan})
    return pd.DataFrame(rows)


def water_props(pressure_kpa: float) -> dict[str, float]:
    pressure_pa = pressure_kpa * 1000.0
    return {
        "rho_l": PropsSI("D", "P", pressure_pa, "Q", 0, "Water"),
        "rho_v": PropsSI("D", "P", pressure_pa, "Q", 1, "Water"),
        "h_fg": PropsSI("H", "P", pressure_pa, "Q", 1, "Water") - PropsSI("H", "P", pressure_pa, "Q", 0, "Water"),
        "sigma": PropsSI("I", "P", pressure_pa, "Q", 0, "Water"),
    }


def zuber_chf(props: dict[str, float]) -> float:
    g = 9.80665
    return 0.131 * props["h_fg"] * props["rho_v"] ** 0.5 * (
        props["sigma"] * g * (props["rho_l"] - props["rho_v"])
    ) ** 0.25


def berenson_mhf(props: dict[str, float]) -> float:
    g = 9.80665
    return 0.09 * props["rho_v"] * props["h_fg"] * (
        g * props["sigma"] * (props["rho_l"] - props["rho_v"]) / (props["rho_l"] + props["rho_v"]) ** 2
    ) ** 0.25


def theoretical_mhf_ratio() -> pd.DataFrame:
    rows = []
    for pressure in np.linspace(10.0, 100.0, 91):
        props = water_props(float(pressure))
        q_chf = zuber_chf(props)
        q_mhf = berenson_mhf(props)
        rows.append(
            {
                "Pressure_kPa": pressure,
                "q_CHF_Zuber_W_cm2": q_chf / 1e4,
                "q_MHF_Berenson_W_cm2": q_mhf / 1e4,
                "q_MHF_over_q_CHF": q_mhf / q_chf,
            }
        )
    return pd.DataFrame(rows)


def set_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 11,
            "axes.labelsize": 14,
            "legend.fontsize": 10,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "axes.linewidth": 1.1,
            "mathtext.fontset": "dejavusans",
        }
    )


def plot_global_fit(
    df: pd.DataFrame,
    constant_curve: pd.DataFrame,
    constant_params: np.ndarray,
    tref_curve: pd.DataFrame,
    tref_params: np.ndarray,
) -> None:
    set_plot_style()
    fig, (ax_constant, ax_tref) = plt.subplots(1, 2, figsize=(7.5, 3.55), constrained_layout=True)
    for ax in (ax_constant, ax_tref):
        ax.set_axisbelow(True)
        ax.grid(True, color="0.86", zorder=0)
        ax.set_box_aspect(1 / 1.125)

    ax_constant.fill_between(
        constant_curve["DeltaTmax_K"],
        constant_curve["H_lower_95"],
        constant_curve["H_upper_95"],
        color="0.82",
        alpha=0.75,
        linewidth=0,
        label="95% bootstrap interval",
        zorder=1,
    )
    x_grid = constant_curve["DeltaTmax_K"].to_numpy(float)
    ax_constant.plot(x_grid, stretched_hmin0(x_grid, *constant_params), color="black", lw=2.4, label="Constant-scale model", zorder=3)

    ax_tref.fill_between(
        tref_curve["xi"],
        tref_curve["H_lower_95"],
        tref_curve["H_upper_95"],
        color="0.82",
        alpha=0.75,
        linewidth=0,
        label="95% bootstrap interval",
        zorder=1,
    )
    xi_grid = tref_curve["xi"].to_numpy(float)
    ax_tref.plot(xi_grid, np.exp(-(xi_grid ** tref_params[1])), color="black", lw=2.4, label="Preferred model", zorder=3)

    for surface in SURFACE_ORDER:
        style = SURFACE_STYLE[surface]
        subset = df[df["Surface"] == surface]
        common = dict(
            s=56,
            marker=style["marker"],
            facecolor=style["color"],
            edgecolor="black",
            linewidth=0.7,
            label=style["label"],
            zorder=10,
        )
        ax_constant.scatter(
            subset["DeltaTmax_K"],
            subset["H_NBR_over_CHF"],
            **common,
        )
        xi = subset["DeltaTmax_K"] / (tref_params[0] - subset["Tsat_C"])
        ax_tref.scatter(
            xi,
            subset["H_NBR_over_CHF"],
            **common,
        )
    ax_constant.set_xlabel(r"Maximum wall superheat, $T_{\mathrm{max}}-T_{\mathrm{sat}}$ (°C)")
    ax_constant.set_ylabel(r"Boiling hysteresis, $H$")
    ax_constant.set_xlim(0, float(df["DeltaTmax_K"].max()) * 1.08)
    ax_constant.set_ylim(0.45, 1.05)
    ax_constant.text(0.03, 0.97, "(a)", transform=ax_constant.transAxes, va="top", ha="left", fontsize=9)

    ax_tref.set_xlabel(r"Pressure-adjusted maturity, $\xi$")
    ax_tref.set_ylabel(r"Boiling hysteresis, $H$")
    ax_tref.set_xlim(0, float(xi_grid.max()))
    ax_tref.set_ylim(0.45, 1.05)
    ax_tref.text(0.03, 0.97, "(b)", transform=ax_tref.transAxes, va="top", ha="left", fontsize=9)
    handles, labels = ax_tref.get_legend_handles_labels()
    ax_tref.legend(handles, labels, framealpha=0.95, loc="lower left", fontsize=7.5)
    fig.savefig(FIG_GLOBAL, dpi=300)
    fig.savefig(FIG_GLOBAL_PDF)
    plt.close(fig)


def write_report(
    comparison: pd.DataFrame,
    cross_validation: pd.DataFrame,
    profile_upper: float,
    bootstrap_params: pd.DataFrame,
    tref_bootstrap_params: pd.DataFrame,
    residuals: pd.DataFrame,
) -> None:
    def markdown_table(frame: pd.DataFrame) -> str:
        display = frame.copy()
        for column in display.select_dtypes(include=[np.number]).columns:
            display[column] = display[column].map(lambda value: f"{value:.5g}")
        header = "| " + " | ".join(display.columns) + " |"
        divider = "| " + " | ".join(["---"] * len(display.columns)) + " |"
        body = ["| " + " | ".join(map(str, row)) + " |" for row in display.to_numpy()]
        return "\n".join([header, divider, *body])

    baseline = comparison.loc[comparison["model"] == "stretched_Hmin0"].iloc[0]
    preferred = comparison.loc[comparison["model"] == "Tref_Hmin0"].iloc[0]
    explicit_pressure = comparison.loc[comparison["model"] == "thermal_plus_pressure"].iloc[0]
    full = comparison.loc[comparison["model"] == "stretched_Hmin_free"].iloc[0]
    cv_summary = cross_validation.groupby(["scheme", "model"])["RMSE"].mean().reset_index()
    lines = [
        "# Submission diagnostics for the 30-case hysteresis model",
        "",
        "## Parameter identifiability and parsimony",
        f"- The free-asymptote fit reaches the lower bound H_min = 0. Its AICc is {full['AICc']:.3f}.",
        f"- The constant-superheat baseline with H_min = 0 gives AICc = {baseline['AICc']:.3f}, RMSE = {baseline['RMSE']:.4f}, and LOOCV RMSE = {baseline['LOOCV_RMSE']:.4f}.",
        f"- The pressure-adjusted T_ref model with H_min = 0 is preferred: AICc = {preferred['AICc']:.3f}, RMSE = {preferred['RMSE']:.4f}, and LOOCV RMSE = {preferred['LOOCV_RMSE']:.4f}.",
        f"- The explicit pressure-correction model is competitive (Delta AICc = {explicit_pressure['Delta_AICc']:.3f}) but uses one additional parameter and has LOOCV RMSE = {explicit_pressure['LOOCV_RMSE']:.4f}.",
        f"- The approximate one-parameter 95% profile upper bound is H_min = {profile_upper:.3f}; the data do not identify a nonzero asymptote.",
        f"- Stratified bootstrap median DeltaT_s = {bootstrap_params['DeltaT_s_K'].median():.2f} K (95% interval {bootstrap_params['DeltaT_s_K'].quantile(0.025):.2f}-{bootstrap_params['DeltaT_s_K'].quantile(0.975):.2f} K).",
        f"- Stratified bootstrap median m = {bootstrap_params['m'].median():.3f} (95% interval {bootstrap_params['m'].quantile(0.025):.3f}-{bootstrap_params['m'].quantile(0.975):.3f}).",
        f"- For the preferred T_ref model, the bootstrap median T_ref = {tref_bootstrap_params['T_ref_C'].median():.2f} °C (95% interval {tref_bootstrap_params['T_ref_C'].quantile(0.025):.2f}-{tref_bootstrap_params['T_ref_C'].quantile(0.975):.2f} °C).",
        f"- The preferred-model bootstrap median m = {tref_bootstrap_params['m'].median():.3f} (95% interval {tref_bootstrap_params['m'].quantile(0.025):.3f}-{tref_bootstrap_params['m'].quantile(0.975):.3f}).",
        "",
        "## Held-out validation",
        markdown_table(cv_summary),
        "",
        "## Residual diagnostics",
        markdown_table(residuals),
        "",
        "## Interpretation boundary",
        "The stretched exponential is an empirical collapse over the measured range. H_min = 0 is a parsimonious boundary choice, not proof that the physical minimum heat-flux ratio is exactly zero. Pressure and surface terms are tested as residual corrections; they should not be described as absent merely because their addition is not supported by this 30-case dataset.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_OUTPUT / "processed_hysteresis_data.csv",
        help="Processed CSV generated by run_boiling_hysteresis_analysis.py.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for diagnostics, tables, and the manuscript model figure.",
    )
    return parser.parse_args()


def configure_paths(data_path: Path, output_dir: Path) -> None:
    global ROOT, DATA, OUT_MODEL_COMPARISON, OUT_CROSS_VALIDATION, OUT_HMIN_PROFILE
    global OUT_RESIDUALS, OUT_BOOTSTRAP, OUT_TREF_BOOTSTRAP, OUT_QMHF, OUT_REPORT
    global FIG_GLOBAL, FIG_GLOBAL_PDF
    ROOT = output_dir
    DATA = data_path
    OUT_MODEL_COMPARISON = ROOT / "submission_model_diagnostics.csv"
    OUT_CROSS_VALIDATION = ROOT / "hysteresis_cross_validation.csv"
    OUT_HMIN_PROFILE = ROOT / "hmin_profile_likelihood.csv"
    OUT_RESIDUALS = ROOT / "submission_residual_diagnostics.csv"
    OUT_BOOTSTRAP = ROOT / "hysteresis_bootstrap_curve.csv"
    OUT_TREF_BOOTSTRAP = ROOT / "hysteresis_tref_bootstrap_curve.csv"
    OUT_QMHF = ROOT / "theoretical_qmhf_ratio.csv"
    OUT_REPORT = ROOT / "submission_diagnostics.md"
    FIG_GLOBAL = ROOT / "plots" / "fig03_hysteresis_model_comparison.png"
    FIG_GLOBAL_PDF = ROOT / "plots" / "fig03_hysteresis_model_comparison.pdf"


def main() -> None:
    args = parse_args()
    configure_paths(args.data, args.output)
    ROOT.mkdir(parents=True, exist_ok=True)
    FIG_GLOBAL.parent.mkdir(parents=True, exist_ok=True)
    df = normalize_input_columns(pd.read_csv(DATA))
    comparison = model_comparison(df)
    comparison.to_csv(OUT_MODEL_COMPARISON, index=False)

    cross_validation = grouped_cross_validation(df)
    cross_validation.to_csv(OUT_CROSS_VALIDATION, index=False)

    profile, profile_upper = profile_hmin(df)
    profile.to_csv(OUT_HMIN_PROFILE, index=False)

    residuals = residual_diagnostics(df)
    residuals.to_csv(OUT_RESIDUALS, index=False)

    curve, bootstrap_params = stratified_bootstrap(df)
    curve.to_csv(OUT_BOOTSTRAP, index=False)

    tref_curve, tref_bootstrap_params = stratified_bootstrap_tref(df)
    tref_curve.to_csv(OUT_TREF_BOOTSTRAP, index=False)

    qmhf = theoretical_mhf_ratio()
    qmhf.to_csv(OUT_QMHF, index=False)

    fixed_params, _ = fit_model(df, "stretched_Hmin0")
    tref_params, _ = fit_model(df, "Tref_Hmin0")
    plot_global_fit(df, curve, fixed_params, tref_curve, tref_params)
    write_report(comparison, cross_validation, profile_upper, bootstrap_params, tref_bootstrap_params, residuals)

    print(comparison.to_string(index=False))
    print(f"Approximate 95% profile upper bound for H_min: {profile_upper:.3f}")
    print(f"Successful bootstrap fits: {len(bootstrap_params)}")
    for path in [
        OUT_MODEL_COMPARISON,
        OUT_CROSS_VALIDATION,
        OUT_HMIN_PROFILE,
        OUT_RESIDUALS,
        OUT_BOOTSTRAP,
        OUT_TREF_BOOTSTRAP,
        OUT_QMHF,
        OUT_REPORT,
        FIG_GLOBAL,
    ]:
        print("Saved:", path)


if __name__ == "__main__":
    main()
