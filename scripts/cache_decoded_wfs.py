"""Decode one AE waveform channel once and persist a memory-mappable cache."""

from __future__ import annotations

import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    from scripts.run_single_case_demo import find_wfs_file, resolve_case_file
    from scripts.time_alignment import (
        make_clock_alignment,
        parse_lvm_start_datetime,
        parse_wfs_filename_start_datetime,
    )
except ImportError:  # Supports `python scripts/cache_decoded_wfs.py`.
    from run_single_case_demo import find_wfs_file, resolve_case_file
    from time_alignment import make_clock_alignment, parse_lvm_start_datetime, parse_wfs_filename_start_datetime


def cache_waveform(raw_dir: Path, processed_dir: Path, channel: int) -> dict[str, object]:
    wfs_path = find_wfs_file(raw_dir)
    if wfs_path is None:
        raise FileNotFoundError(f"No .wfs file found in {raw_dir}")
    temperature_path = resolve_case_file(raw_dir, "Temperature.lvm")
    temperature_clock = parse_lvm_start_datetime(temperature_path)
    alignment = make_clock_alignment(
        "acoustic_emission_waveform",
        wfs_path,
        temperature_path,
        parse_wfs_filename_start_datetime(wfs_path),
        temperature_clock,
        method="wfs_filename_clock",
    )
    try:
        from decode_wfs import load_continuous
    except ImportError as exc:
        raise ImportError("Install `decode-wfs` from requirements.txt before caching waveform data.") from exc

    raw, time_s, sampling_rate = load_continuous(wfs_path, channel=channel)
    # Preserve the decoder's native integer sample representation. Casting a
    # billion-sample channel to float32 doubles storage and can exceed the
    # available allocation before the cache is written.
    waveform = np.asarray(raw)
    time_values = np.asarray(time_s)
    processed_dir.mkdir(parents=True, exist_ok=True)
    stem = f"ae_wfs_channel_{channel}"
    waveform_path = processed_dir / f"{stem}_waveform.npy"
    metadata_path = processed_dir / f"{stem}_metadata.json"
    np.save(waveform_path, waveform, allow_pickle=False)
    metadata = {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_wfs": str(wfs_path),
        "source_size_bytes": wfs_path.stat().st_size,
        "source_modified_time": datetime.fromtimestamp(wfs_path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "channel": int(channel),
        "dtype": str(waveform.dtype),
        "samples": int(waveform.size),
        "sampling_frequency_Hz": float(sampling_rate),
        "native_time_start_s": float(time_values[0]) if time_values.size else None,
        "native_time_end_s": float(time_values[-1]) if time_values.size else None,
        "temperature_reference_clock_offset_s": float(alignment.applied_offset_s or 0.0),
        "alignment": alignment.as_dict(),
        "decoder": "decode-wfs.load_continuous",
        "python": platform.python_version(),
        "memory_map_example": f"np.load('{waveform_path.name}', mmap_mode='r')",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"waveform_path": str(waveform_path), "metadata_path": str(metadata_path), **metadata}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--processed-dir", type=Path, required=True)
    parser.add_argument("--channel", type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(cache_waveform(args.raw_dir, args.processed_dir, args.channel), indent=2))


if __name__ == "__main__":
    main()
