# Submission diagnostics for the 30-case hysteresis model

## Parameter identifiability and parsimony
- The free-asymptote fit reaches the lower bound H_min = 0. Its AICc is -184.508.
- The constant-superheat baseline with H_min = 0 gives AICc = -186.986, RMSE = 0.0412, and LOOCV RMSE = 0.0443.
- The pressure-adjusted T_ref model with H_min = 0 is preferred: AICc = -199.382, RMSE = 0.0335, and LOOCV RMSE = 0.0359.
- The explicit pressure-correction model is competitive (Delta AICc = 1.655) but uses one additional parameter and has LOOCV RMSE = 0.0372.
- The approximate one-parameter 95% profile upper bound is H_min = 0.437; the data do not identify a nonzero asymptote.
- Stratified bootstrap median DeltaT_s = 162.24 K (95% interval 151.46-183.82 K).
- Stratified bootstrap median m = 1.951 (95% interval 1.604-2.273).
- For the preferred T_ref model, the bootstrap median T_ref = 264.36 °C (95% interval 254.01-280.02 °C).
- The preferred-model bootstrap median m = 1.658 (95% interval 1.491-1.852).

## Held-out validation
| scheme | model | RMSE |
| --- | --- | --- |
| leave_one_pressure_out | Tref_Hmin0 | 0.033394 |
| leave_one_pressure_out | linear_pressure | 0.093548 |
| leave_one_pressure_out | stretched_Hmin0 | 0.040197 |
| leave_one_surface_out | Tref_Hmin0 | 0.042559 |
| leave_one_surface_out | linear_pressure | 0.13064 |
| leave_one_surface_out | stretched_Hmin0 | 0.052353 |

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
