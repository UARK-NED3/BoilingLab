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
files and lightweight plots to `demos\Boiling-417\generated`.

## Notes for Contributors

- Keep raw videos and large acquisition outputs outside git.
- Commit notebooks and lightweight metadata that are needed to reproduce or
  understand the analysis workflow.
- When adding a new test analysis, make sure its `Test ID` matches both the raw
  data folder name and the row in the test log.
