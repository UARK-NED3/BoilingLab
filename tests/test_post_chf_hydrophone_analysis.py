"""Tests for event-aligned hydrophone feature calculations."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_post_chf_hydrophone_analysis.py"
SPEC = importlib.util.spec_from_file_location("post_chf_hydrophone_analysis", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
hydrophone = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hydrophone)


def test_spectral_features_integrate_voltage_psd_in_requested_band() -> None:
    fs = 12_800.0
    time_s = np.arange(int(8 * fs)) / fs
    voltage = 0.1 * np.sin(2 * np.pi * 500.0 * time_s)
    features = hydrophone.spectral_features(
        time_s,
        voltage,
        band_min_hz=100.0,
        band_max_hz=1000.0,
        highpass_hz=20.0,
        window_s=2.0,
    )
    assert np.isclose(features["sampling_frequency_Hz"].iloc[0], fs)
    assert np.isclose(features["band_voltage_variance_V2"].median(), 0.005, rtol=0.08)
    assert np.isclose(features["dominant_frequency_Hz"].median(), 500.0, atol=1.0)


def test_event_windows_skip_short_intervals_instead_of_relabeling_them() -> None:
    metrics = pd.Series(
        {
            "test_id": "B-420",
            "t_chf_s": 100.0,
            "t_cutoff_s": 115.0,
            "tmax_raw_time_s": 120.0,
            "t_nbr_s": 140.0,
        }
    )
    features = pd.DataFrame(
        {
            "time_reference_temperature_s": np.arange(50.0, 145.0, 1.0),
            "band_level_dB_re_V2": -30.0,
            "spectral_centroid_Hz": 500.0,
            "spectral_entropy": 0.6,
            "prominent_peak_6dB": True,
        }
    )
    summary = hydrophone.summarize_windows(features, metrics).set_index("window")
    assert bool(summary.loc["pre_CHF", "usable"])
    assert not bool(summary.loc["post_CHF_heating", "usable"])
    assert not bool(summary.loc["post_cutoff", "usable"])
    assert bool(summary.loc["pre_NBR", "usable"])
    assert np.isclose(summary.loc["pre_CHF", "fraction_6dB_below_pre_CHF"], 0.0)
