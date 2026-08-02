# Submission diagnostics for the 30-case hysteresis model

## Parameter identifiability and parsimony
- The free-asymptote fit reaches the lower bound H_min = 0. Its AICc is -184.508.
- The constant-superheat baseline with H_min = 0 gives AICc = -186.986, RMSE = 0.0412, and LOOCV RMSE = 0.0443.
- The pressure-adjusted T_ref model with H_min = 0 is preferred: AICc = -199.382, RMSE = 0.0335, and LOOCV RMSE = 0.0359.
- The explicit pressure-correction model is competitive (Delta AICc = 1.655) but uses one additional parameter and has LOOCV RMSE = 0.0372.
- The approximate 95% profile upper bounds are H_min = 0.437 for the constant scale and 0.484 for the preferred T_ref scale; neither family identifies a nonzero asymptote.
- Adding surface offsets to the preferred model gives Delta AICc = 0.191; leave-one-surface-out validation is intentionally not reported for this form because an unseen surface coefficient cannot be estimated.
- Adding the archived nonzero water/air exposure indicator gives Delta AICc = 1.563 and coefficient 0.0202. This screening term is confounded with pressure and test sequence and is not interpreted causally.
- Pressure-block bootstrap median DeltaT_s = 162.69 K (95% interval 153.87-183.82 K).
- Pressure-block bootstrap median m = 1.931 (95% interval 1.609-2.263).
- For the preferred T_ref model, the bootstrap median T_ref = 264.85 °C (95% interval 256.78-283.07 °C).
- The preferred-model bootstrap median m = 1.650 (95% interval 1.466-1.854).

## Held-out validation
| scheme | model | mean_RMSE | mean_MAE |
| --- | --- | --- | --- |
| leave_one_pressure_out | Tref_Hmin0 | 0.033394 | 0.030094 |
| leave_one_pressure_out | Tref_Hmin_free | 0.034876 | 0.031144 |
| leave_one_pressure_out | Tref_plus_conditioning | 0.033623 | 0.029785 |
| leave_one_pressure_out | Tref_plus_power | 0.034781 | 0.031309 |
| leave_one_pressure_out | Tref_plus_pressure | 0.035921 | 0.031806 |
| leave_one_pressure_out | Tref_plus_surface | 0.034197 | 0.029556 |
| leave_one_pressure_out | linear_DeltaTmax | 0.046978 | 0.042582 |
| leave_one_pressure_out | linear_pressure | 0.093548 | 0.083875 |
| leave_one_pressure_out | ordinary_exponential_Hmin0 | 0.064512 | 0.059079 |
| leave_one_pressure_out | pressure_plus_surface | 0.036233 | 0.030528 |
| leave_one_pressure_out | stretched_Hmin0 | 0.040197 | 0.036993 |
| leave_one_pressure_out | stretched_Hmin_free | 0.040197 | 0.036993 |
| leave_one_pressure_out | thermal_plus_power | 0.042107 | 0.038217 |
| leave_one_pressure_out | thermal_plus_pressure | 0.037079 | 0.033389 |
| leave_one_pressure_out | thermal_plus_surface | 0.039045 | 0.033637 |
| leave_one_surface_out | Tref_Hmin0 | 0.042559 | 0.035898 |
| leave_one_surface_out | Tref_Hmin_free | 0.042279 | 0.035581 |
| leave_one_surface_out | Tref_plus_conditioning | 0.04824 | 0.039807 |
| leave_one_surface_out | Tref_plus_power | 0.05831 | 0.051227 |
| leave_one_surface_out | Tref_plus_pressure | 0.044114 | 0.035895 |
| leave_one_surface_out | linear_DeltaTmax | 0.072861 | 0.065984 |
| leave_one_surface_out | linear_pressure | 0.13064 | 0.12476 |
| leave_one_surface_out | ordinary_exponential_Hmin0 | 0.066883 | 0.056813 |
| leave_one_surface_out | stretched_Hmin0 | 0.052353 | 0.044205 |
| leave_one_surface_out | stretched_Hmin_free | 0.052434 | 0.044261 |
| leave_one_surface_out | thermal_plus_power | 0.075815 | 0.06792 |
| leave_one_surface_out | thermal_plus_pressure | 0.046367 | 0.039254 |

Surface-specific models are excluded from leave-one-surface-out summaries because the held-out surface coefficient is not estimable from the training set.

## Held-out 10 kPa protocol perturbation
| model | n | RMSE | MAE | bias_observed_minus_predicted |
| --- | --- | --- | --- | --- |
| stretched_Hmin0 | 5 | 0.15242 | 0.11661 | 0.099308 |
| Tref_Hmin0 | 5 | 0.039478 | 0.036461 | 0.0036862 |

## Residual diagnostics
| model | diagnostic | value | p_value |
| --- | --- | --- | --- |
| stretched_Hmin0 | residual_vs_pressure_linear_slope_per_kPa | -0.00069138 | 0.0068149 |
| stretched_Hmin0 | residual_vs_pressure_spearman_r | -0.36795 | 0.045447 |
| stretched_Hmin0 | residual_surface_one_way_ANOVA_F | 3.1049 | 0.06114 |
| stretched_Hmin0 | DeltaT_s_K | 162.09 | nan |
| stretched_Hmin0 | m | 1.9563 | nan |
| stretched_Hmin0 | mean_residual_Flat Cu | -0.019467 | nan |
| stretched_Hmin0 | mean_residual_New MC Cu | 0.021978 | nan |
| stretched_Hmin0 | mean_residual_MP Cu | -0.010195 | nan |
| Tref_Hmin0 | residual_vs_pressure_linear_slope_per_kPa | -0.00018444 | 0.40352 |
| Tref_Hmin0 | residual_vs_pressure_spearman_r | -0.12666 | 0.50481 |
| Tref_Hmin0 | residual_surface_one_way_ANOVA_F | 2.4212 | 0.10785 |
| Tref_Hmin0 | T_ref_C | 264.59 | nan |
| Tref_Hmin0 | m | 1.6593 | nan |
| Tref_Hmin0 | mean_residual_Flat Cu | -0.0022737 | nan |
| Tref_Hmin0 | mean_residual_New MC Cu | 0.015771 | nan |
| Tref_Hmin0 | mean_residual_MP Cu | -0.016096 | nan |

## Interpretation boundary
The stretched exponential is an empirical collapse over the measured range. H_min = 0 is a parsimonious boundary choice, not proof that the physical minimum heat-flux ratio is exactly zero. Pressure and surface terms are tested as residual corrections; they should not be described as absent merely because their addition is not supported by this 30-case dataset.
