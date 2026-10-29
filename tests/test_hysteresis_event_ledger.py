"""Regression checks for the manuscript-level CHF/NBR event ledger."""

from pathlib import Path
import sys

import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import run_boiling_hysteresis_analysis as analysis


def test_default_data_path_honors_portable_environment_override(monkeypatch) -> None:
    supplied = r"D:\released-data\MS Thesis Data_30cases.xlsx"
    monkeypatch.setenv("BOILINGLAB_HYSTERESIS_DATA", supplied)

    assert analysis.default_data_path() == Path(supplied)


def test_event_ledger_preserves_selected_event_fields(tmp_path: Path) -> None:
    data = pd.DataFrame(
        {
            "test_id": ["Boiling-285"],
            "surface": ["Flat Cu"],
            "pressure_kpa": [10.07],
            "heater_power_W": [60.0],
            "t_chf_s": [117.25],
            "t_nbr_s": [142.10],
            "q_chf_W_cm2": [38.10],
            "q_nbr_W_cm2": [37.83],
            "T_max_C": [71.17],
            "T_nbr_C": [66.88],
            "T_sat_C": [45.944],
            "H": [0.9929133858],
            "DeltaT_max_K": [25.226],
            "DeltaT_NBR_K": [20.936],
            "post_chf_to_nbr_s": [24.85],
        }
    )

    ledger = analysis.write_event_ledger(data, tmp_path, series="standard_30_case")

    assert (tmp_path / "event_ledger_standard_30_case.csv").exists()
    assert ledger.loc[0, "test_id"] == "Boiling-285"
    assert ledger.loc[0, "event_status"] == "archived_selected_events"
    assert ledger.loc[0, "search_window_status"] == "not_retained"
    assert ledger.loc[0, "post_chf_to_nbr_s"] == 24.85
    assert set(
        [
            "q_chf_W_cm2",
            "q_nbr_W_cm2",
            "T_max_C",
            "T_nbr_C",
            "t_chf_s",
            "t_nbr_s",
        ]
    ).issubset(ledger.columns)


def test_protocol_csv_loader_accepts_retained_processed_summary(tmp_path: Path) -> None:
    source = tmp_path / "protocol_summary.csv"
    pd.DataFrame(
        {
            "test_id": ["Boiling-420", "Boiling-421", "Boiling-422", "Boiling-423", "Boiling-424"],
            "pressure_kpa": [9.96, 9.92, 10.02, 9.99, 9.98],
            "surface": ["Flat Cu"] * 5,
            "q_chf_W_cm2": [51.31, 50.11, 50.24, 48.86, 43.34],
            "q_nbr_W_cm2": [48.57, 42.92, 36.43, 30.89, 19.66],
            "T_nbr_C": [73.30, 70.07, 69.90, 67.94, 94.15],
            "T_max_C": [75.58, 101.71, 150.46, 198.68, 250.14],
            "T_sat_C": [45.729, 45.651, 45.847, 45.788, 45.768],
        }
    ).to_csv(source, index=False)

    protocol = analysis.load_protocol_validation_csv(source)

    assert protocol["test_id"].tolist() == [
        "Boiling-420",
        "Boiling-421",
        "Boiling-422",
        "Boiling-423",
        "Boiling-424",
    ]
    assert protocol.loc[protocol["test_id"] == "Boiling-424", "target_Tmax_C"].item() == 250.0
    assert protocol.loc[protocol["test_id"] == "Boiling-420", "protocol_label"].item() == "baseline"
    assert protocol["H"].notna().all()
