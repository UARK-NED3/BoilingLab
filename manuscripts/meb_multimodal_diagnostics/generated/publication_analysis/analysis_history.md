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

3. Generated/updated these manuscript-facing plots:

- `plots/fig01a_boiling_curve_wall_temperature.png`
- `plots/fig01b_boiling_curve_wall_superheat.png`
- `plots/fig02_thermal_hydrophone_four_case_summary.png`
- `plots/fig06_envelope_metric_summary.png`
- `plots/fig07a_literature_boiling_curve_comparison.png`
- `plots/fig07b_literature_frequency_scale_comparison.png`

4. Data-coverage checkpoint:

- Thermal comparison: Cases A-D.
- Hydrophone comparison: Cases A-D after Case A regeneration.
- AE waveform comparison: Cases C-D only.
- Literature comparison: first-pass `test2_meb` compilation; still needs final figure/table digitization and source-specific uncertainty notes before submission.
- A source-by-source digitization queue is saved as `literature_digitization_priority_publication.csv`.

5. Uncertainty checkpoint:

A first-pass data-derived uncertainty/quality diagnostics table was generated as `uncertainty_diagnostics_publication.csv`. It includes pressure stability, thermal linear-fit diagnostics, hydrophone power variability, hydrophone time-bin spacing, and frequency-spread diagnostics. Manufacturer calibration and full uncertainty propagation remain a pre-submission task.
