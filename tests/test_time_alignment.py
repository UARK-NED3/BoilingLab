from datetime import datetime
from pathlib import Path

import numpy as np

from scripts.time_alignment import (
    apply_clock_offset,
    make_clock_alignment,
    parse_easy_ae_start_datetime,
    parse_wfs_filename_start_datetime,
)


def test_recorded_clock_offset_is_applied_against_temperature_reference():
    reference = datetime(2026, 5, 10, 18, 2, 20, 416000)
    source = datetime(2026, 5, 10, 18, 2, 19, 709000)
    record = make_clock_alignment(
        "pressure",
        Path("Pressure.lvm"),
        Path("Temperature.lvm"),
        source,
        reference,
        method="lvm_header_clock",
    )

    assert record.raw_offset_s == -0.707
    np.testing.assert_allclose(apply_clock_offset(np.array([0.0, 1.0]), record), [-0.707, 0.293])


def test_small_clock_offset_is_ignored_only_within_declared_tolerance():
    reference = datetime(2026, 5, 10, 18, 2, 20)
    source = datetime(2026, 5, 10, 18, 2, 20, 500)
    record = make_clock_alignment(
        "hydrophone",
        Path("Hydrophones.lvm"),
        Path("Temperature.lvm"),
        source,
        reference,
        method="lvm_header_clock",
        tolerance_s=1e-3,
    )

    assert record.raw_offset_s == 0.0005
    assert record.applied_offset_s == 0.0


def test_wfs_filename_clock_is_parsed_to_millisecond_precision():
    timestamp = parse_wfs_filename_start_datetime(Path("STREAM20260510-180215-533.wfs"))

    assert timestamp == datetime(2026, 5, 10, 18, 2, 15, 533000)


def test_easy_ae_clock_is_found_inside_a_binary_prefixed_line(tmp_path: Path):
    dta = tmp_path / "case.DTA"
    dta.write_bytes(b"header\n\x1a\x00clock: Sun May 10 18:02:12 2026\n")

    assert parse_easy_ae_start_datetime(dta) == datetime(2026, 5, 10, 18, 2, 12)
