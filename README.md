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
files and plots to `demos\Boiling-417\generated`. The generated outputs include
thermal/pressure/DC plots plus hydrophone raw/spectrogram plots and acoustic
emission hit/time parameter plots when `Hydrophones.lvm`, `AE_Hit.TXT`, and
`AE_Time.TXT` are present. The hydrophone analysis also computes a
band-integrated PSD scalar over time by integrating the PSD over frequency; this
is a voltage-squared acoustic-power proxy unless the hydrophone signal is
calibrated to pressure.

To include the continuous acoustic-emission waveform spectrogram from a `.wfs`
stream file, install the full requirements and run:

```powershell
python scripts\run_single_case_demo.py --include-wfs
```

This decodes the waveform with `decode-wfs`, uses channel 1 by default, and
writes `generated\plots\ae_wfs_spectrogram.png`. It also integrates the AE
waveform PSD over frequency to create
`generated\ae_wfs_band_integrated_power.csv` and
`generated\plots\ae_wfs_band_integrated_power.png`. Use `--wfs-channel` to
select a different waveform channel, `--wfs-max-freq-hz` to change the plotted
frequency range, and `--wfs-band-min-hz` / `--wfs-band-max-hz` to change the
integrated PSD band.

For a faster thermal-only run:

```powershell
python scripts\run_single_case_demo.py --skip-sensors
```

Use `--hydrophone-band-min-hz` and `--hydrophone-band-max-hz` to change the
frequency band used for the integrated PSD time trace.

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

## Notes for Contributors

- Keep raw videos and large acquisition outputs outside git.
- Commit notebooks and lightweight metadata that are needed to reproduce or
  understand the analysis workflow.
- When adding a new test analysis, make sure its `Test ID` matches both the raw
  data folder name and the row in the test log.
