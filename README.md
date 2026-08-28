# BoilingLab

BoilingLab is a research toolkit for pool-boiling experimental protocols, multimodal data synchronization, thermal reconstruction, acoustic analysis, hysteresis analysis, and machine-readable export. It is the processing layer in the NED³ thermal-AI ecosystem.

The repository works with user-supplied data and does not assume a drive letter or machine-specific folder layout.

## Public benchmark examples

Use the public [BoilingBench-Multimodal dataset](https://huggingface.co/datasets/hanhuark/BoilingBench-Multimodal) or its [Zenodo archive](https://doi.org/10.5281/zenodo.22131859). Read each track-specific README before analysis.

| Example | Physical system | Raw-data directory relative to benchmark root | Notes |
| --- | --- | --- | --- |
| BoilingBench-1 | Ambient, subcooled, flat-Cu pool boiling | BoilingBench-1_Ambient_subcooled_flatCu_pool_boiling/BoilingBench-1_Multimodal_Raw | Full multimodal analysis; MEB and hysteresis apply. |
| BoilingBench-2 | Subatmospheric, saturated, flat-Cu pool boiling | BoilingBench-2_Subatmospheric_saturated_flatCu_pool_boiling/BoilingBench-2_Multimodal_Raw | Full multimodal analysis; no MEB products. |
| BoilingBench-3 | Ambient, saturated, Cu-foam pool boiling | BoilingBench-3_Ambient_saturated_CuFoam_pool_boiling/BoilingBench-3_Multimodal_Raw | Legacy MISTRAS USB AE; microphone available; no continuous .wfs stream. |
| BoilingBench-4 | Ambient, saturated, flat-Cu pool boiling | BoilingBench-4_Ambient_saturated_flatCu_pool_boiling/BoilingBench-4_Multimodal_Raw | Legacy MISTRAS USB AE; microphone available; no continuous .wfs stream. |

The full benchmark and Lite profile have different contents. Check the omission manifest before interpreting missing video or waveform files. BoilingLab outputs are derived products, not automatically independent ground truth.

## Ecosystem

- [Thermal AI Commons](https://github.com/UARK-NED3/Thermal-AI-Commons) — contracts, provenance, split rules, compatibility pinning, and evidence reports.
- [BoilingBench-Multimodal](https://github.com/UARK-NED3/BoilingBench-Multimodal) — data profiles, manifests, annotations, and benchmark tasks.
- [BubbleID](https://github.com/cldunlap73/BubbleID) — bubble segmentation and interface features.
- [BubbleID-Flow](https://github.com/UARK-NED3/BubbleID-Flow) — vapor-area and flow-boiling image analysis.
- [SeqReg](https://github.com/cldunlap73/SeqReg) — sequence regression.

## Installation

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

## Single-case analysis

The runner accepts a case directory and output directory. Set these paths to wherever you downloaded the benchmark; do not encode a machine-specific path in source files.

    python scripts/run_single_case_demo.py --test-id BoilingBench-1 --case-folder <BoilingBench-1 raw directory> --output-dir <BoilingBench-1 processed directory> --analysis-mode subcooled --target-pressure-kpa <pressure_kPa> --subcooling <subcooling_K> --applied-heat-load <heat_load_W>

For BoilingBench-2, use saturated mode and do not request MEB:

    python scripts/run_single_case_demo.py --test-id BoilingBench-2 --case-folder <BoilingBench-2 raw directory> --output-dir <BoilingBench-2 processed directory> --analysis-mode saturated --target-pressure-kpa <pressure_kPa> --subcooling 0 --applied-heat-load <heat_load_W>

For BoilingBench-3 and -4, skip continuous waveform decoding because the legacy AE acquisition has no continuous .wfs export:

    python scripts/run_single_case_demo.py --test-id BoilingBench-3 --case-folder <BoilingBench-3 raw directory> --output-dir <BoilingBench-3 processed directory> --analysis-mode saturated --target-pressure-kpa 101.325 --subcooling 0 --applied-heat-load <heat_load_W> --skip-wfs

Use the analogous BoilingBench-4 directories for the fourth track. Verify thermocouple locations, pressure, power, calibration, and surface assumptions against the case README before using reconstructed heat flux quantitatively. For Cu foam, do not silently apply flat-copper conductivity assumptions.

## Outputs

Applicable runs can export thermal_timeseries.csv, thermal_timeseries.npz, critical_events.csv, time_alignment.json, heat-flux and surface-temperature plots, pressure/power plots, hydrophone or microphone spectra, AE products, quality flags, regression statistics, and summary metadata.

Temperature is the reference time axis when declared by the case. Recorded clock offsets do not prove zero trigger latency or absence of clock drift. Acoustic band-integrated power is a voltage-squared proxy unless calibration supports conversion to physical acoustic pressure.

## Waveform caching

For BoilingBench-1 and -2:

    python scripts/cache_decoded_wfs.py --raw-dir <raw directory> --processed-dir <processed directory> --channel 1

The cache is a lossless, memory-mappable NumPy array with acquisition metadata. Do not use this workflow for BoilingBench-3 or -4.

## Hysteresis

    python scripts/run_case_hysteresis_analysis.py --processed-dir <processed directory>

The command writes CSV, Excel, time-series, and plot outputs. q_NBR/q_CHF is a screening proxy unless the upstream CHF marker is independently confirmed. MEB products apply to subcooled BoilingBench-1, not saturated BoilingBench-2, -3, or -4.

## Scientific cautions

Read [data reduction](docs/data_reduction.md), [multimodal time alignment](docs/multimodal-time-alignment.md), and the relevant BoilingBench card. Check thermocouple order and locations, extrapolation distance, conductivity, pressure/saturation assumptions, calibration, units, sign conventions, regression R², quality fields, missing modalities, and alignment residuals.

Raw sensor and video files are measured/source observations. Heat flux, surface temperature, spectral summaries, event markers, MEB indicators, hysteresis metrics, and image-derived quantities are derived or annotated products unless metadata states otherwise.

## Reproducibility and contribution

Record the dataset release or DOI, case/run identifier, input manifest, BoilingLab commit or release, command-line arguments, environment, and output checksums. For benchmark use, split by independent run, specimen, surface, condition, or heat-load path; never distribute adjacent windows from one run across train, validation, and test.

Keep raw data and large acquisition outputs outside Git. Do not add private paths, credentials, restricted data, or unlicensed model weights.

## Citation

Cite the applicable BoilingBench release, relevant experimental publication, and this software repository. For the current Lite snapshot, cite [Zenodo DOI 10.5281/zenodo.22131859](https://doi.org/10.5281/zenodo.22131859) and the [Hugging Face dataset](https://huggingface.co/datasets/hanhuark/BoilingBench-Multimodal).
