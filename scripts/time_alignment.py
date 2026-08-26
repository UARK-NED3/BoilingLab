"""Clock-time alignment utilities for BoilingLab multimodal acquisitions.

Temperature is the reference modality.  Each non-temperature time series keeps
its native sample spacing but is shifted by its recorded acquisition-clock
start-time difference relative to Temperature.lvm.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class ClockAlignmentRecord:
    modality: str
    source_path: str
    reference_path: str
    source_start_clock: str | None
    reference_start_clock: str
    method: str
    raw_offset_s: float | None
    applied_offset_s: float | None
    tolerance_s: float
    status: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _parse_fractional_time(value: str) -> tuple[int, int, int, int]:
    match = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d+))?", value.strip())
    if not match:
        raise ValueError(f"Unsupported clock-time format: {value!r}")
    hour, minute, second, fractional = match.groups()
    microsecond = int((fractional or "")[:6].ljust(6, "0"))
    return int(hour), int(minute), int(second), microsecond


def parse_lvm_start_datetime(path: Path) -> datetime:
    """Read the first LabVIEW LVM header date/time as a local clock timestamp."""
    date_text = None
    time_text = None
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith("***End_of_Header***"):
                break
            fields = line.strip().split("\t", maxsplit=1)
            if len(fields) != 2:
                continue
            key, value = fields
            if key == "Date":
                date_text = value.strip()
            elif key == "Time":
                time_text = value.strip()
    if not date_text or not time_text:
        raise ValueError(f"Could not locate Date/Time in LVM header: {path}")
    date_value = datetime.strptime(date_text, "%Y/%m/%d")
    hour, minute, second, microsecond = _parse_fractional_time(time_text)
    return date_value.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)


def parse_easy_ae_start_datetime(path: Path) -> datetime:
    """Read the EasyAE acquisition start line from a DTA file."""
    pattern = re.compile(
        r"((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4})"
    )
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            match = pattern.search(line)
            if match:
                return datetime.strptime(match.group(1), "%a %b %d %H:%M:%S %Y")
    raise ValueError(f"Could not locate EasyAE start clock in {path}")


def parse_wfs_filename_start_datetime(path: Path) -> datetime:
    """Parse a STREAMYYYYMMDD-HHMMSS-mmm waveform filename timestamp."""
    match = re.search(r"STREAM(\d{8})-(\d{6})-(\d{3})", path.name, re.IGNORECASE)
    if not match:
        raise ValueError(f"WFS filename does not encode a STREAM clock timestamp: {path.name}")
    return datetime.strptime("".join(match.groups()[:2]), "%Y%m%d%H%M%S").replace(
        microsecond=int(match.group(3)) * 1000
    )


def make_clock_alignment(
    modality: str,
    source_path: Path,
    reference_path: Path,
    source_start: datetime,
    reference_start: datetime,
    *,
    method: str,
    tolerance_s: float = 1e-3,
) -> ClockAlignmentRecord:
    """Create a conservative alignment record without inferring unrecorded drift."""
    if tolerance_s < 0:
        raise ValueError("tolerance_s must be non-negative")
    raw_offset_s = (source_start - reference_start).total_seconds()
    applied_offset_s = 0.0 if abs(raw_offset_s) <= tolerance_s else raw_offset_s
    return ClockAlignmentRecord(
        modality=modality,
        source_path=str(source_path),
        reference_path=str(reference_path),
        source_start_clock=source_start.isoformat(),
        reference_start_clock=reference_start.isoformat(),
        method=method,
        raw_offset_s=raw_offset_s,
        applied_offset_s=applied_offset_s,
        tolerance_s=tolerance_s,
        status="recorded_clock_offset",
    )


def unavailable_alignment(
    modality: str, reference_path: Path, reference_start: datetime, reason: str, tolerance_s: float
) -> ClockAlignmentRecord:
    """Record that a modality was intentionally left on its native relative clock."""
    return ClockAlignmentRecord(
        modality=modality,
        source_path="not_available",
        reference_path=str(reference_path),
        source_start_clock=None,
        reference_start_clock=reference_start.isoformat(),
        method="not_available",
        raw_offset_s=None,
        applied_offset_s=None,
        tolerance_s=tolerance_s,
        status=reason,
    )


def apply_clock_offset(time_s: np.ndarray, record: ClockAlignmentRecord) -> np.ndarray:
    """Shift a modality's relative time to the temperature-reference time axis."""
    if record.applied_offset_s is None:
        return np.asarray(time_s, dtype=float)
    return np.asarray(time_s, dtype=float) + record.applied_offset_s
