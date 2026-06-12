# Analysis History

This file records reproducible analysis steps and intermediate outputs used to update the manuscript. It is an audit trail of commands, data coverage, and interpretation checkpoints.

## 2026-06-12 pre-submission update

1. Regenerated Case A single-case outputs after the raw-data drive was mounted.

```powershell
python scripts\run_single_case_demo.py --test-id Boiling-412 --raw-root "Y:\0_Ishraq\New Pool Boiling Video" --applied-heat-load 150 --subcooling 40 --skip-wfs
```

Key result: Case A now has hydrophone spectrogram, band-integrated power, characteristic-frequency CSV, and related hydrophone plots. AE waveform analysis remains unavailable for Cases A-B because waveform files are not present.

2. Refreshed publication-facing manuscript tables and figures.

```powershell
python scripts\run_manuscript_publication_analysis.py
```

3. Generated the MEB visual-mechanism screening and storage-release model figures.

```powershell
python scripts\make_meb_mechanism_figures.py
```

4. Generated/updated these manuscript-facing plots:

- `plots/fig01a_heating_boiling_curve_wall_temperature.png`
- `plots/fig01b_heating_boiling_curve_wall_superheat.png`
- `plots/fig01c_full_history_boiling_curve_wall_temperature.png`
- `plots/fig01d_full_history_boiling_curve_wall_superheat.png`
- `plots/fig02_thermal_hydrophone_four_case_summary.png`
- `plots/fig06_envelope_metric_summary.png`
- `plots/fig07a_literature_boiling_curve_comparison.png`
- `plots/fig07b_literature_frequency_scale_comparison.png`
- `final_ate_panels/fig01_ate_case_heat_flux_and_hydrophone_modulation.png`
- `final_ate_panels/fig02_ate_envelope_metrics.png`
- `final_ate_panels/fig03_ate_literature_boiling_curve_context.png`
- `mechanism/fig08_representative_microbubble_frames.png`
- `mechanism/fig09_storage_release_model.png`

5. Data-coverage checkpoint:

- Thermal comparison: Cases A-D.
- Hydrophone time histories: Cases A-D after Case A regeneration. MEB power-envelope frequency is resolved only for the developed high-power cases.
- AE waveform comparison: Cases C-D only.
- High-speed-video representative frames: Cases C-D from MP4 files encoded at 30 fps from 150 fps recordings.
- Literature comparison: first-pass `test2_meb` compilation; still needs final figure/table digitization and source-specific uncertainty notes before submission.
- A source-by-source digitization queue is saved as `literature_digitization_priority_publication.csv`.
- Normalized literature boiling points and onset/signature values are saved as `literature_digitized_boiling_points_publication.csv` and `literature_onset_signature_values_publication.csv`; status labels distinguish source-reported values, range endpoints, and any figure-digitized values.

6. Uncertainty checkpoint:

A pre-submission uncertainty/quality diagnostics table was generated as `uncertainty_diagnostics_publication.csv`. A propagated quantity-level budget is saved as `uncertainty_budget_publication.csv`, including wall temperature, heat flux, event time, hydrophone band power, and characteristic frequency. Manufacturer calibration-certificate values should replace the current source-labeled assumptions before journal submission.

7. Final figure panel checkpoint:

Applied Thermal Engineering style review panels were generated in `final_ate_panels/` with case labels, consistent typography, and provisional uncertainty representation where available. Captions are stored in `final_ate_panels/captions.md`.
