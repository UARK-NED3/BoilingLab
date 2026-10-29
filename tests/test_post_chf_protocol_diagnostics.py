"""Regression tests for the extended 10 kPa post-CHF protocol diagnostics."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_post_chf_protocol_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("post_chf_protocol_diagnostics", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
protocol = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(protocol)


def test_find_power_shutoff_requires_a_persistent_low_power_state() -> None:
    thermal = pd.DataFrame(
        {
            "time_reference_temperature_s": [0, 1, 2, 3, 4, 5, 6, 7],
            "dc_power_W_interpolated": [0.0, 60.0, 60.0, 0.2, 60.0, 0.2, 0.1, 0.0],
        }
    )

    index, threshold = protocol.find_power_shutoff_index(
        thermal, t_chf_s=2.0, persistence_samples=2
    )

    assert index == 5
    assert threshold == 0.6


def test_derive_case_metrics_uses_selected_events_and_raw_cutoff_response() -> None:
    thermal = pd.DataFrame(
        {
            "time_reference_temperature_s": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "dc_power_W_interpolated": [60.0, 60.0, 60.0, 60.0, 0.2, 0.1, 0.0, 0.0, 0.0],
            "surface_temperature_C": [50.0, 55.0, 60.0, 70.0, 74.0, 76.0, 75.0, 70.0, 65.0],
            "heat_flux_W_cm2": [40.0, 42.0, 45.0, 44.0, 40.0, 35.0, 30.0, 32.0, 38.0],
        }
    )
    selected = {
        "test_id": "B999",
        "t_chf_s": 2.0,
        "t_nbr_s": 8.0,
        "t_max_s": 5.0,
        "t_max_C": 76.0,
        "tsat_C": 45.0,
        "q_chf_W_cm2": 45.0,
        "q_nbr_W_cm2": 38.0,
        "q_min_W_cm2": 30.0,
    }

    result = protocol.derive_case_metrics(thermal, selected)

    assert result["t_cutoff_s"] == 4.0
    assert result["tmax_raw_C"] == 76.0
    assert result["tmax_overshoot_C"] == 2.0
    assert result["cutoff_to_tmax_s"] == 1.0
    assert result["post_chf_heating_s"] == 2.0
    assert result["cutoff_to_nbr_s"] == 4.0
    assert np.isclose(result["post_chf_electrical_energy_J"], 90.1)
    assert np.isclose(result["H_selected"], 38.0 / 45.0)
    assert result["protocol_target_temperature_C"] == 76.0


def test_centered_rolling_median_suppresses_isolated_acoustic_spikes() -> None:
    values = np.array([-36.0, -36.0, -20.0, -36.0, -36.0])

    smoothed = protocol.centered_rolling_median(values, window_samples=3)

    assert np.allclose(smoothed[1:-1], [-36.0, -36.0, -36.0])
