# BoilingLab

Research toolkit for pool boiling experimental protocols, data acquisition
codes, and multimodal data synchronization and analysis codes.

## Current Contents

- `notebooks/Single_case_analysis_Subcooled.ipynb`: student-developed
  Python notebook for single-test analysis of subatmospheric-pressure
  subcooled pool boiling experiments.
- `metadata/Pool Boiling Test Log.xlsx`: experiment log and metadata table.
  The `Test ID` column is the primary key for each unique test.
- `demos/Boiling-417`: example single-case run using raw data from
  `Y:\0_Ishraq\New Pool Boiling Video\Boiling-417`.
- `scripts/run_boiling_hysteresis_analysis.py`: manuscript-level analysis for
  the subatmospheric boiling hysteresis study using the organized 30-case
  spreadsheet.
- `manuscripts/boiling_hysteresis_subatmospheric`: documentation and generated
  outputs for the boiling hysteresis manuscript analysis.

## Data Organization

Raw high-speed video and related acquisition files are stored outside this
repository:

```text
Y:\0_Ishraq\New Pool Boiling Video
```

Each folder under that raw-data root represents one test. The folder name is
the `Test ID`, for example:

```text
Y:\0_Ishraq\New Pool Boiling Video\Boiling-145
```

Use `Test ID` to connect:

1. the raw-data folder under `Y:\0_Ishraq\New Pool Boiling Video`,
2. the corresponding row in `metadata/Pool Boiling Test Log.xlsx`, and
3. the analysis case selected in `notebooks/Single_case_analysis_Subcooled.ipynb`.

The Excel log also includes experiment descriptors such as pressure, personnel,
date, surface, liquid, frame rate, resolution, chamber configuration, camera,
and acquisition notes.

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
`Y:\0_Ishraq\New Pool Boiling Video\Boiling-417` and writes generated summary
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
`Y:\0_Ishraq\New Pool Boiling Video`, looks up metadata in
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
