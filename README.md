# BoilingLab

Research toolkit for pool boiling experimental protocols, data acquisition
codes, and multimodal data synchronization and analysis codes.

## Current Contents

- `notebooks/Single_case_analysis_Subcooled.ipynb`: student-developed
  Python notebook for single-test analysis of subatmospheric-pressure
  subcooled pool boiling experiments.
- `metadata/Pool Boiling Test Log.xlsx`: experiment log and metadata table.
  The `Test ID` column is the primary key for each unique test.
- `docs/experimental_protocol.md`: subatmospheric pool-boiling facility,
  heater enclosure, environmental-control, surface-preparation, degassing,
  heat-load-selection, and test-sequence documentation consolidated from the
  MSME thesis materials.
- `docs/data_acquisition_and_control.md`: documented DAQ, control, logging,
  synchronization, and operator-decision workflow for the thesis facility.
- `hardware-system/`: visual facility reference with authorized thesis figures,
  hardware identities/specifications, and component-level DAQ/control notes.
- `docs/data_reduction.md`: thermal reconstruction, heat-flux calculation,
  pressure/saturation assumptions, event definitions, heating-branch filtering,
  hysteresis metrics, BubbleID vapor-state metrics, and reproducibility checks.
- `demos/Boiling-417`: example single-case run using raw data from
  `X:\0_Ishraq\New Pool Boiling Video\Boiling-417`.
- `scripts/run_boiling_hysteresis_analysis.py`: manuscript-level analysis for
  the subatmospheric boiling hysteresis study using the organized 30-case
  spreadsheet.
- `manuscripts/boiling_hysteresis_subatmospheric`: documentation and generated
  outputs for the boiling hysteresis manuscript analysis.

## Data Organization

Raw high-speed video and related acquisition files are stored outside this
repository:

```text
X:\0_Ishraq\New Pool Boiling Video
```

Each folder under that raw-data root represents one test. The folder name is
the `Test ID`, for example:

```text
X:\0_Ishraq\New Pool Boiling Video\Boiling-145
```

Use `Test ID` to connect:

1. the raw-data folder under `X:\0_Ishraq\New Pool Boiling Video`,
2. the corresponding row in `metadata/Pool Boiling Test Log.xlsx`, and
3. the analysis case selected in `notebooks/Single_case_analysis_Subcooled.ipynb`.

The Excel log also includes experiment descriptors such as pressure, personnel,
date, surface, liquid, frame rate, resolution, chamber configuration, camera,
and acquisition notes.

## Experimental Protocol Documentation

The `docs` folder records the experimental-method context needed to interpret
the raw files and generated analysis outputs:

- [Experimental protocol](docs/experimental_protocol.md) describes the
  pressure-controlled boiling chamber, heating element enclosure, copper
  surface preparation, DI-water degassing, saturation and pressure control,
  transient heat-load selection, and the ONB -> NB -> CHF -> TB -> NBR -> NB
  test sequence.
- [DAQ and control workflow](docs/data_acquisition_and_control.md) identifies
  the documented hardware, sampling rates, acquisition products, manual
  controls, and the boundary between this repository's analysis code and the
  LabVIEW control VIs.
- [Data reduction](docs/data_reduction.md) documents the four-thermocouple
  linear conduction model, wall-temperature extrapolation, Fourier-law heat
  flux calculation, wall superheat, HTC, heating-branch filtering, CHF/NBR
  marker conventions, boiling hysteresis ratio, thermal-maturity model, and
  BubbleID side-view vapor-fraction metrics.

These files were added to make the analysis scripts traceable to the
experimental methodology in Ishraq Hossain's MSME thesis draft and defense
presentation. They intentionally avoid storing raw videos, large acquisition
outputs, or private local source paths in git.

## Hardware System Reference

[`hardware-system/`](hardware-system/README.md) provides the visual hardware
reference: annotated facility and chamber images, copper test-surface drawings,
the LabVIEW monitoring screen, saturation/pressure-control evidence, heat-load
selection evidence, and component-level specifications. The equipment identity
and figures are reported from the supplied thesis and defense presentation;
they are not a current inventory, wiring diagram, safety SOP, or calibration
record.

## Environment Setup

Create and activate a local Python environment, then install the repo
dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The notebook requires the same scientific Python stack listed in
`requirements.txt`, including `pyXSteam` for saturation temperature,
`scipy` for signal processing, and Jupyter packages for notebook execution.

## Reproduce the Boiling-417 Demo

With the raw-data drive mounted, run:

```powershell
python scripts\run_single_case_demo.py
```

The default command analyzes `Boiling-417` from
`X:\0_Ishraq\New Pool Boiling Video\Boiling-417` and writes generated summary
files and plots to `demos\Boiling-417\generated`. A complete single-case run
generates these eight required figures:

- `generated\plots\heat_flux_vs_time.png`
- `generated\plots\surface_temperature.png`
- `generated\plots\hydrophone_spectrogram.png`
- `generated\plots\hydrophone_band_integrated_power.png`
- `generated\plots\hydrophone_characteristic_frequencies.png`
- `generated\plots\ae_wfs_spectrogram.png`
- `generated\plots\ae_wfs_band_integrated_power.png`
- `generated\plots\ae_wfs_characteristic_frequencies.png`

The generated outputs also include pressure/DC plots, hydrophone raw plots, and
acoustic-emission hit/time parameter plots when the corresponding raw files are
present. The hydrophone and AE waveform analyses compute band-integrated PSD
scalars over time by integrating the PSD over frequency; these are
voltage-squared acoustic-power proxies unless the sensors are calibrated to
physical acoustic pressure.

Every run additionally exports `thermal_timeseries.csv`,
`thermal_timeseries.npz`, `critical_events.csv`, and `time_alignment.json`.
Temperature is the unshifted reference time axis; pressure, DC power,
hydrophone, and AE records are offset from their recorded clock starts when
available. See [multimodal time alignment](docs/multimodal-time-alignment.md)
for the equation, tolerance, and limits. The default `chf_proxy` event is not a
confirmed CHF event unless the analyst explicitly records that status.

## BoilingBench-3 legacy-DAQ case

BoilingBench-3 uses a generic six-channel temperature export, a singular
`Hydrophone.lvm` filename, a separate `Microphone.lvm`, and legacy MISTRAS USB
AE data without a continuous `.wfs` stream. Run it with:

```powershell
python scripts\run_single_case_demo.py --test-id BoilingBench-3 --case-folder <raw-directory> --analysis-mode saturated --target-pressure-kpa 101.325 --subcooling 0 --applied-heat-load 0 --skip-wfs
```

The default four-probe geometry is 0, 2.54, 5.08, and 7.62 mm with the heated
surface at 13.1826 mm; verify those positions against the case calibration
before using the reconstructed heat flux quantitatively. Because this legacy
case has no pressure or DC-power file, the command records atmospheric pressure
as a user-supplied fallback and does not invent a power or shutoff trace.
Hydrophone and microphone analyses are retained as separate synchronized
outputs; continuous AE waveform spectrograms are unavailable for this case.

## Reproduce the Boiling-424 Transient Thermal Reduction

The transient notebook corresponds to the 9.98 kPa / 60 W case currently
stored in `Boiling-424`. The following thermal-only command preserves that
case metadata while avoiding an expensive waveform decode during an initial
check:

```powershell
python scripts\run_single_case_demo.py --test-id Boiling-424 --analysis-mode transient --target-pressure-kpa 10 --applied-heat-load 60 --skip-sensors
```

`--target-pressure-kpa` and `--applied-heat-load` are run metadata supplied by
the analyst; they are not inferred from the reconstructed heat-flux trace.
Confirm them against the experiment record before reporting them. Remove
`--skip-sensors` when the full hydrophone and AE analyses are required.

For a documented benchmark whose raw files sit directly in one directory and
use a unique dataset prefix (for example, `BoilingBench-1_Temperature.lvm`),
use `--case-folder <raw-directory>`. The runner resolves the uniquely prefixed
versions of the standard modality filenames without renaming the raw files.

To persist a decoded waveform for reuse, run
`scripts\cache_decoded_wfs.py --raw-dir <raw-directory> --processed-dir
<processed-directory> --channel 1`. This writes a lossless, memory-mappable
NumPy waveform and JSON acquisition metadata. Use `np.load(..., mmap_mode="r")`
for later feature extraction without decoding the raw stream again.

To create a case-level hysteresis report from a processed run, use
`scripts\run_case_hysteresis_analysis.py --processed-dir <processed-directory>`.
The command writes `hysteresis_summary.csv`, `hysteresis_analysis.xlsx`,
`hysteresis_timeseries.csv`, and two plots. Its `q_NBR/q_CHF` value is labeled a
screening proxy when the upstream CHF marker is not independently confirmed.
MEB-specific outputs are appropriate for subcooled cases such as BoilingBench-1;
they are not generated for saturated BoilingBench-2.

The default run decodes the continuous acoustic-emission waveform from a `.wfs`
stream file with `decode-wfs`, uses channel 1 by default, and writes the AE
spectrogram, band-integrated power trace, and characteristic-frequency trace.
Use `--wfs-channel` to select a different waveform channel, `--wfs-max-freq-hz`
to change the plotted frequency range, and `--wfs-band-min-hz` /
`--wfs-band-max-hz` to change the integrated PSD band. Use `--skip-wfs` when a
faster run without continuous AE waveform plots is needed.

For a faster thermal-only run:

```powershell
python scripts\run_single_case_demo.py --skip-sensors
```

Use `--hydrophone-band-min-hz` and `--hydrophone-band-max-hz` to change the
frequency band used for the integrated PSD time trace.

The single-case runner also analyzes slow oscillations in the band-integrated
power traces. By default, it uses the `300-700 s` interval and reports the
dominant modulation frequency and period in `summary.json` / `summary.md`. It
also saves the oscillation spectra as CSV and PNG files. Use
`--oscillation-start-s`, `--oscillation-end-s`, and
`--oscillation-max-frequency-hz` to adjust this analysis window.

For time-resolved spectral content, the runner computes characteristic
frequencies from each spectrogram time bin. The generated CSV files include
peak frequency, spectral centroid, and spectral bandwidth; the companion PNGs
plot peak frequency and spectral centroid over time for hydrophone and AE
waveform data.

For the hydrophone signal, the runner also creates a focused `300-700 s`
double-axis overlay of band-integrated power and spectral centroid. The summary
reports their zero-lag correlation plus a short-lag cross-correlation estimate
to indicate whether power peaks align with centroid peaks or valleys.

## Compare Multiple Cases

To compare boiling curves for the default heat-load sweep
(`Boiling-412`, `Boiling-413`, `Boiling-416`, and `Boiling-417`), run:

```powershell
python scripts\run_multi_case_comparison.py
```

The script reads the raw folders under
`X:\0_Ishraq\New Pool Boiling Video`, looks up metadata in
`metadata\Pool Boiling Test Log.xlsx`, and writes combined plots plus CSV/JSON
summaries to `demos\Boiling-412-413-416-417\generated`. By default, only the
heating portion of each case is included: temperature samples are kept when the
aligned last column of `DC_power.lvm` is greater than `0 W`.

To compare a different set of cases:

```powershell
python scripts\run_multi_case_comparison.py --test-ids Boiling-145 Boiling-146 Boiling-147
```

Use `--power-threshold-w` if a different positive-power cutoff is needed.

## Reproduce the Boiling Hysteresis Manuscript Analysis

The boiling hysteresis study uses an organized 30-case spreadsheet rather than
raw LVM files. With the Box drive mounted, run:

```powershell
python scripts\run_boiling_hysteresis_analysis.py
```

By default the runner reads:

```text
C:\Users\hanhu\Box\NED3_Share\Zulkar Nain Prince\MS Thesis Data_30cases.xlsx
```

and writes processed tables, fit summaries, and publication-style figures to:

```text
manuscripts\boiling_hysteresis_subatmospheric\generated
```

The analysis defines boiling hysteresis as
`H = q''_NBR / q''_CHF`, fits stretched-exponential thermal-maturity models
against `T_max - T_sat`, analyzes the NBR wall-superheat band
`T_NBR - T_sat`, compares `q''_NBR(T_NBR)` against the Rohsenow correlation,
and summarizes BubbleID side-view vapor-fraction diagnostics when those columns
are present in the spreadsheet. See
`manuscripts\boiling_hysteresis_subatmospheric\README.md` for equations,
figure descriptions, and interpretation notes.

## Notes for Contributors

- Keep raw videos and large acquisition outputs outside git.
- Commit notebooks and lightweight metadata that are needed to reproduce or
  understand the analysis workflow.
- When adding a new test analysis, make sure its `Test ID` matches both the raw
  data folder name and the row in the test log.
- When changing copper-block geometry, thermocouple locations, surface
  definitions, event-picking logic, or hysteresis metrics, update the docs and
  generated summaries together so the repo remains methodologically traceable.
