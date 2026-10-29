# Subatmospheric Boiling Hysteresis Analysis

This folder documents the manuscript-level analysis for the subatmospheric
pool-boiling hysteresis study. It complements the existing BoilingLab
single-case and multi-case thermal/acoustic analysis tools by starting from the
organized 30-case summary spreadsheet rather than raw `.lvm` files.

The analysis also accepts a separate five-case flat-copper protocol dataset.
Those approximately 10 kPa tests vary the post-CHF target temperature and are
kept out of parameter fitting for a fixed-parameter, within-apparatus transfer
evaluation. They are not an external validation across facilities or heaters.

## Dataset

Original-workstation input candidates:

```text
C:\Users\hanhu\Box\NED3_Share\Abrar Hoq Fahim\BubbleID-FineTuning\MS Thesis Data_30cases_abrar.xlsx
C:\Users\hanhu\Box\NED3_Share\Zulkar Nain Prince\MS Thesis Data_30cases.xlsx
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

The source spreadsheet is distributed separately from this repository. A
portable clone should pass `--data` or set `BOILINGLAB_HYSTERESIS_DATA`; the
runner only chooses a default when one of the original-workstation paths is
present.

## Reproduce the Analysis

From the repository root:

```powershell
python scripts\run_boiling_hysteresis_analysis.py
python scripts\run_boiling_hysteresis_submission_diagnostics.py
python scripts\run_post_chf_protocol_diagnostics.py
```

To use a different spreadsheet:

```powershell
python scripts\run_boiling_hysteresis_analysis.py `
  --data "C:\path\to\MS Thesis Data_30cases.xlsx" `
  --sheet "MS Thesis" `
  --protocol-data "C:\path\to\MS Thesis Data.xlsx"
```

When only the retained processed five-case summary is available, use it as a
reproducible protocol input instead of a missing source workbook:

```powershell
python scripts\run_boiling_hysteresis_analysis.py `
  --data "C:\path\to\MS Thesis Data_30cases.xlsx" `
  --sheet "MS Thesis" `
  --protocol-csv "manuscripts\boiling_hysteresis_subatmospheric\generated\protocol_validation_data.csv"
```

Generated files are written to:

```text
manuscripts\boiling_hysteresis_subatmospheric\generated
```

`run_post_chf_protocol_diagnostics.py` additionally requires the mounted
five-case raw/processed dataset at `Z:\ned3-019-BoilingHysteresis10kPa`. It
uses the selected manuscript event table for CHF, NBR, and the post-CHF heat
flux minimum, then reconstructs heater cutoff from the processed DC-power
trace. It writes a traceable metrics table and two candidate manuscript figures
to `generated\protocol_diagnostics`. The derived post-CHF electrical energy is
input energy between selected CHF and cutoff; it is not a stored-energy
measurement.

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
`H_min`, and 2,000 pressure-block bootstrap resamples. Each bootstrap block is
the three-surface triplet at one nominal pressure. Optional heater-power,
surface-offset, and archived nonzero water/air-exposure terms are evaluated as
confounding checks. Surface-specific models are not assigned a
leave-one-surface-out score because their unseen-surface coefficient cannot be
estimated from the training set.

The five protocol cases are evaluated only after fitting the standard 30-case
dataset. Their fixed-parameter transfer predictions and aggregate RMSE, MAE, and bias are written to
`protocol_validation_predictions.csv` and `submission_diagnostics.md`.

## Event-Selection Provenance

The manuscript-level scripts start from the organized event summary; they do
not silently re-detect CHF or NBR. The original thermal workflow used the
following operational sequence:

1. Select a bounded CHF search interval and take its maximum heat flux.
2. Exclude the immediate post-CHF collapse with a case-specific time gap.
3. Select the largest subsequent recovery peak as the NBR candidate.
4. Confirm that the heat-flux--wall-superheat trajectory rejoins and remains on
   the pre-CHF nucleate-boiling branch; use synchronized video when available
   to reject an isolated transition-boiling excursion.

The organized workbook does not retain all case-specific windows and gaps, and
the raw `.lvm` files are not part of this local analysis package. A full
event-window sensitivity study therefore cannot be reproduced from the summary
file alone. This is a documented limitation, not an uncertainty value inferred
after the fact.

Parameters in the general stretched-exponential form are interpreted as:

- `H_min` is the unresolved lower hysteresis asymptote for a fully matured
  dry/vapor state.
- `DeltaT_s` is the wall-superheat scale over which the post-CHF dry/vapor
  state matures.
- `m` is a descriptive shape exponent for the fitted thermal-history relation.

NBR temperature is analyzed as a complementary output through
`T_NBR - T_sat`. A narrow apparent base-wall-superheat band is compatible with
recovery over a limited wall-temperature range; it does not establish a unique
rewetting mechanism or resolve liquid--solid contact.

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
  Rohsenow-predicted `q''_NBR(T_NBR)` using `C_sf = 0.0128` and `0.0107`.
- `fig06_bubbleid_vapor_fraction_by_stage`: two-panel BubbleID diagnostic
  showing (a) side-view vapor fraction at ONB, CHF, and NBR and (b) vapor
  persistence, `VF_NBR/VF_CHF`, versus the boiling hysteresis ratio.
- `fig07_flat_mfb_regime_check`: flat-copper `T_max` compared with Berenson
  and Henry minimum-film-boiling temperature predictions; the structured
  surfaces are intentionally omitted from this flat-surface model check.
- `protocol_diagnostics\fig_post_chf_controlled_trajectories`: selected CHF,
  cutoff, maximum-temperature, and NBR trajectories for the five controlled
  extended-heating tests.
- `protocol_diagnostics\fig_post_chf_protocol_response_summary`: cutoff
  fidelity, normalized recovery response, and protocol time scales for the
  same five tests.
- `protocol_diagnostics\fig_post_chf_hydrophone_context`: qualitative
  hydrophone context for a short-wait and a long-wait test. It uses an
  integrated PSD voltage-squared proxy and is not a calibrated acoustic or
  wall-wetting measurement.

## Generated Tables

- `processed_hysteresis_data.csv`: cleaned analysis table with derived
  `H`, `T_max - T_sat`, and `T_NBR - T_sat`.
- `hysteresis_fit_summary.csv`: fitted parameters and goodness-of-fit metrics.
- `qnbr_rohsenow_comparison.csv`: Rohsenow predictions for `C_sf = 0.0128` and
  `C_sf = 0.0107`.
- `qnbr_rohsenow_sensitivity_summary.csv`: measured/model ratios and counts
  within the +/-30% band for both `C_sf` values and each surface.
- `protocol_validation_data.csv`: cleaned five-case protocol dataset excluded
  from fitting.
- `protocol_validation_predictions.csv`: locked-model predictions for the
  separate excluded protocol cases.
- `flat_mfb_temperature_models.csv` and `flat_mfb_regime_points.csv`:
  flat-surface MFB curves and the standard/protocol points used in the regime
  check.
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
- `protocol_diagnostics\post_chf_protocol_metrics.csv`: selected event values
  combined with reconstructed cutoff, overshoot, time partitions, and
  post-CHF input-energy metrics for the five-case protocol series.

## Interpretation Caveat

BubbleID vapor fraction is a projected side-view quantity. It is useful for
regime classification and for comparing ONB/CHF/NBR image states, but it is not
a direct measurement of wall dry-area fraction. The current fine-tuned model
used all 24 labeled images during training, so the optical metrics are
descriptive and are not an independently validated segmentation benchmark.

The thermal dataset contains one test at each pressure--surface condition.
Grouped validation measures interpolation across the design but does not
replace experimental replication or a propagated measurement-uncertainty
budget. Several high-pressure structured-surface tests also have nonzero
archived water/air exposure histories. Because exposure is confounded with
pressure and run order, its fitted indicator is a screening diagnostic and not
a causal aging correction.
