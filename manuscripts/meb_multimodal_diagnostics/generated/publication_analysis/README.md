# Manuscript Publication Analysis

Target journal: Applied Thermal Engineering.

This folder contains publication-facing summary tables and plots generated from
BoilingLab intermediates and the `literature-compiler/examples/test2_meb` dataset.
Case labels are used for manuscript-facing outputs.

## Data coverage

| case | thermal_available | hydrophone_intermediate_available | ae_waveform_available | notes |
| --- | --- | --- | --- | --- |
| Case A | True | False | False | No AE waveform file available for this case. |
| Case B | True | True | False | No AE waveform file available for this case. |
| Case C | True | True | True | AE waveform analysis limited to Cases C-D. |
| Case D | True | True | True | AE waveform analysis limited to Cases C-D. |

Thermal comparison is available for all four cases. Hydrophone analysis is
included where generated hydrophone intermediate CSV files are present.
AE waveform analysis is intentionally limited to Cases C and D because those
are the only cases with AE waveform files available in the current dataset.

## Regeneration note

Generated hydrophone intermediate files are missing for: Case A. Regenerate the single-case workflow from raw data when the raw-data
drive is mounted to complete the fully consistent four-case hydrophone analysis.

## Key thermal summary

| case | nominal_power_W | mean_pressure_kPa | pressure_std_kPa | mean_liquid_temperature_C | saturation_temperature_C | subcooling_K | maximum_heat_flux_W_cm2 | maximum_wall_temperature_C | heating_duration_s | mean_power_during_heating_W |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Case A | 150 | 97.3 | 0.0586 | 58.8 | 98.8 | 40 | 142 | 113 | 537 | 150 |
| Case B | 180 | 97.3 | 0.0586 | 52.4 | 98.8 | 46.5 | 163 | 159 | 568 | 179 |
| Case C | 230 | 97.5 | 0.0582 | 57.3 | 98.9 | 41.6 | 267 | 167 | 753 | 228 |
| Case D | 250 | 97.5 | 0.0582 | 57.6 | 98.9 | 41.3 | 278 | 173 | 670 | 248 |

## Hydrophone summary

| case | nominal_power_W | hydrophone_available | band_power_mean_V2 | band_power_max_V2 | median_peak_frequency_Hz | median_centroid_frequency_Hz | dominant_slow_modulation_Hz | power_centroid_best_lag_s | power_centroid_best_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Case A | 150 | False |  |  |  |  |  |  |  |
| Case B | 180 | True | 0.00409 | 0.0232 | 980 | 1.1e+03 | 0.005 | 0 | -0.803 |
| Case C | 230 | True | 0.0081 | 0.0595 | 919 | 1.06e+03 | 0.05 | 0.64 | 0.824 |
| Case D | 250 | True | 0.0157 | 0.344 | 917 | 1.06e+03 | 0.08 | -0.64 | 0.637 |

## AE waveform summary

| case | nominal_power_W | band_power_mean_V2 | band_power_max_V2 | median_peak_frequency_Hz | median_centroid_frequency_Hz | dominant_slow_modulation_Hz |
| --- | --- | --- | --- | --- | --- | --- |
| Case C | 230 | 5.35e-06 | 5.34e-05 | 8.42e+03 | 8.57e+03 | 0.055 |
| Case D | 250 | 4.85e-06 | 4.99e-05 | 8.42e+03 | 8.49e+03 | 0.0801 |
