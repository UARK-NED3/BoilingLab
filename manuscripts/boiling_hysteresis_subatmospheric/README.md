# Subatmospheric Boiling Hysteresis Analysis

This folder documents the manuscript-level analysis for the subatmospheric
pool-boiling hysteresis study. It complements the existing BoilingLab
single-case and multi-case thermal/acoustic analysis tools by starting from the
organized 30-case summary spreadsheet rather than raw `.lvm` files.

## Dataset

Default local input:

```text
C:\Users\hanhu\Box\NED3_Share\Abrar Hoq Fahim\BubbleID-FineTuning\MS Thesis Data_30cases_abrar.xlsx
```

Worksheet:

```text
MS Thesis
```

The spreadsheet is expected to contain thermal summary columns including
pressure, surface, CHF, HTC at CHF, NBR heat flux, maximum wall temperature,
saturation temperature, and NBR wall temperature. Optional BubbleID columns
(`ONB_vf`, `CHF_vf`, `NBR_vf`, `ONB_count`, `CHF_count`, and `NBR_count`) are
used when present.

## Reproduce the Analysis

From the repository root:

```powershell
python scripts\run_boiling_hysteresis_analysis.py
python scripts\run_boiling_hysteresis_submission_diagnostics.py
```

To use a different spreadsheet:

```powershell
python scripts\run_boiling_hysteresis_analysis.py `
  --data "C:\path\to\MS Thesis Data_30cases.xlsx" `
  --sheet "MS Thesis"
```

Generated files are written to:

```text
manuscripts\boiling_hysteresis_subatmospheric\generated
```

## Analysis Summary

The boiling hysteresis ratio is defined as

```text
H = q''_NBR / q''_CHF
```

where `q''_CHF` is the heating-branch critical heat flux and `q''_NBR` is the
cooling-branch heat flux at which the boiling curve returns to the nucleate
boiling branch.

The constant-superheat baseline uses the maximum post-CHF wall superheat:

```text
H = H_min + (1 - H_min) exp[-((T_max - T_sat) / DeltaT_s)^m].
```

For the current dataset, the free-asymptote constant-scale fit reaches the
lower bound. The submission analysis therefore fixes `H_min = 0` as a
parsimonious boundary condition and tests its identifiability separately.

The preferred manuscript model uses a pressure-adjusted reference-temperature
coordinate:

```text
xi = (T_max - T_sat) / (T_ref - T_sat)
H = exp[-xi^m].
```

The diagnostics script compares this model with constant-superheat,
pressure-only, explicit pressure-correction, surface-offset, and free-asymptote
alternatives. It reports AICc, leave-one-case-out error, leave-one-pressure-out
and leave-one-surface-out validation, residual tests, a profile analysis for
`H_min`, and 2,000 stratified bootstrap resamples.

Parameters in the general stretched-exponential form are interpreted as:

- `H_min` is the unresolved lower hysteresis asymptote for a fully matured
  dry/vapor state.
- `DeltaT_s` is the wall-superheat scale over which the post-CHF dry/vapor
  state matures.
- `m` is a shape/cooperativity exponent for the thermal-maturity process.

NBR temperature is analyzed as a complementary output through
`T_NBR - T_sat`. A narrow NBR wall-superheat band supports the interpretation
that return to nucleate boiling is a temperature-controlled rewetting event,
not simply CHF in reverse.

## Generated Figures

- `fig01_chf_htc_vs_pressure`: CHF and HTC at CHF versus pressure for flat Cu,
  microchannel Cu, and micro-pin-fin Cu.
- `fig02_hysteresis_vs_pressure`: hysteresis ratio versus pressure.
- `fig03_hysteresis_constant_scale_fit`: global hysteresis collapse versus
  `T_max - T_sat`.
- `fig03_hysteresis_model_comparison`: constant-superheat baseline and the
  preferred pressure-adjusted model with bootstrap intervals.
- `fig04_nbr_wall_superheat_vs_pressure`: NBR wall superheat versus pressure.
- `fig05_qnbr_rohsenow_parity`: experimental `q''_NBR` versus
  Rohsenow-predicted `q''_NBR(T_NBR)` using `C_sf = 0.0128`.
- `fig06_bubbleid_vapor_fraction_by_stage`: two-panel BubbleID diagnostic
  showing (a) side-view vapor fraction at ONB, CHF, and NBR and (b) vapor
  persistence, `VF_NBR/VF_CHF`, versus the boiling hysteresis ratio.

## Generated Tables

- `processed_hysteresis_data.csv`: cleaned analysis table with derived
  `H`, `T_max - T_sat`, and `T_NBR - T_sat`.
- `hysteresis_fit_summary.csv`: fitted parameters and goodness-of-fit metrics.
- `qnbr_rohsenow_comparison.csv`: Rohsenow predictions for `C_sf = 0.0128` and
  `C_sf = 0.0107`.
- `theoretical_hmin_diagnostic.csv`: hydrodynamic lower-bound diagnostic using
  Zuber CHF and a Berenson-type minimum-heat-flux scale.
- `analysis_summary.json`: compact machine-readable summary of the run.
- `submission_model_diagnostics.csv`: candidate-model comparison with AICc and
  leave-one-case-out error.
- `hysteresis_cross_validation.csv`: held-out pressure and surface predictions.
- `submission_residual_diagnostics.csv`: residual pressure and surface tests.
- `hmin_profile_likelihood.csv`: profile analysis for the lower asymptote.
- `hysteresis_*_bootstrap_curve.csv`: bootstrap curve intervals.
- `submission_diagnostics.md`: concise numerical audit used for the manuscript.

## Interpretation Caveat

BubbleID vapor fraction is a projected side-view quantity. It is useful for
regime classification and for comparing ONB/CHF/NBR image states, but it is not
a direct measurement of wall dry-area fraction. The current fine-tuned model
used all 24 labeled images during training, so the optical metrics are
descriptive and are not an independently validated segmentation benchmark.

The thermal dataset contains one test at each pressure--surface condition.
Grouped validation measures interpolation across the design but does not
replace experimental replication or a propagated measurement-uncertainty
budget.
