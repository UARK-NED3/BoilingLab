# Manuscript Publication Analysis

Target journal: Applied Thermal Engineering.

This folder contains publication-facing summary tables and plots generated from
BoilingLab intermediates and the `literature-compiler/examples/test2_meb` dataset.
Case labels are used for manuscript-facing outputs.

## Data coverage

| case | thermal_available | hydrophone_intermediate_available | ae_waveform_available | notes |
| --- | --- | --- | --- | --- |
| Case A | True | True | False | No AE waveform file available for this case. |
| Case B | True | True | False | No AE waveform file available for this case. |
| Case C | True | True | True | AE waveform analysis limited to Cases C-D. |
| Case D | True | True | True | AE waveform analysis limited to Cases C-D. |

Thermal comparison is available for all four cases. Hydrophone analysis is
available for all four cases after regenerating Case A from raw data.
AE waveform analysis is intentionally limited to Cases C and D because those
are the only cases with AE waveform files available in the current dataset.

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
| Case A | 150 | True | 0.000648 | 0.00321 | 975 | 1.4e+03 | 0.0247 | 0 | -0.85 |
| Case B | 180 | True | 0.00409 | 0.0232 | 980 | 1.1e+03 | 0.005 | 0 | -0.803 |
| Case C | 230 | True | 0.0081 | 0.0595 | 919 | 1.06e+03 | 0.05 | 0.64 | 0.824 |
| Case D | 250 | True | 0.0157 | 0.344 | 917 | 1.06e+03 | 0.08 | -0.64 | 0.637 |

## AE waveform summary

| case | nominal_power_W | band_power_mean_V2 | band_power_max_V2 | median_peak_frequency_Hz | median_centroid_frequency_Hz | dominant_slow_modulation_Hz |
| --- | --- | --- | --- | --- | --- | --- |
| Case C | 230 | 5.35e-06 | 5.34e-05 | 8.42e+03 | 8.57e+03 | 0.055 |
| Case D | 250 | 4.85e-06 | 4.99e-05 | 8.42e+03 | 8.49e+03 | 0.0801 |

## First-pass uncertainty and quality diagnostics

| case | nominal_power_W | pressure_std_kPa | temperature_heat_flux_fit_mean_R2 | temperature_heat_flux_fit_min_R2 | hydrophone_band_power_cv | hydrophone_time_bin_s | hydrophone_centroid_iqr_Hz | hydrophone_peak_frequency_iqr_Hz | ae_waveform_available | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Case A | 150 | 0.0586 | 0.979 | 0.0567 | 0.33 | 0.32 | 138 | 15.6 | False | Data-derived diagnostic; add manufacturer/calibration uncertainty before submission. |
| Case B | 180 | 0.0586 | 0.991 | 0.517 | 1.14 | 0.32 | 159 | 32.8 | False | Data-derived diagnostic; add manufacturer/calibration uncertainty before submission. |
| Case C | 230 | 0.0582 | 0.985 | 0.0361 | 1.05 | 0.32 | 168 | 306 | True | Data-derived diagnostic; add manufacturer/calibration uncertainty before submission. |
| Case D | 250 | 0.0582 | 0.994 | 0.804 | 1.43 | 0.32 | 158 | 189 | True | Data-derived diagnostic; add manufacturer/calibration uncertainty before submission. |

## Literature digitization priority

| priority | ref_id | target_data | figure_or_table_target | submission_use | status |
| --- | --- | --- | --- | --- | --- |
| 1 | tang_2016_transition_to_meb | MEB transition heat flux, wall superheat, bubble-collapse/growth frequency | transition boiling curves and microbubble tracking figures | Primary comparison for transition from nucleate boiling to MEB | needs figure-level digitization |
| 1 | horiuchi_2019_transient_nucleate_to_meb | Transient MEB onset heat flux and wall superheat | reported transition/onset data and transient boiling curves | Compare event markers and transient heating pathway | needs figure-level digitization |
| 1 | horiuchi_2021_spatial_temporal_thermal_fluid | C-MEB/S-MEB heat flux ranges, wall superheat ranges, sound frequencies | MEB state map, heat-flux ranges, sound-frequency figures | Interpret oscillatory state and frequency definitions | needs range verification |
| 1 | ono_2023_acoustic_state_detection_meb | Acoustic state labels, hydrophone sampling/bandwidth, heat flux range | state-detection and heat-transfer condition tables | Benchmark acoustic-classification context | needs table/figure verification |
| 2 | kobayashi_2022_on_homogeneity_of_vapor_bubble | Boiling sound frequency, vapor-bubble oscillation homogeneity, heat-transfer state | boiling sound and heat-transfer characteristic figures | Separate high-frequency sound/bubble metrics from slow envelope modulation | needs frequency-definition verification |
| 2 | tang_2018_sound_emission_subcooled_pool | Sound spectral peaks, subcooling, heater size, boiling state | sound-emission spectra and boiling-condition tables | Hydrophone/sound comparison for spectral content | needs source-key/name verification and figure digitization |
| 2 | zhu_2014_visualized_meb | Visualized MEB heat flux, subcooling, boiling-sound peak | visualized MEB condition figures and sound result | Mechanistic visualization context | needs figure-level digitization |
| 2 | unno_2022_surface_properties_meb_onset | MEB onset wall superheat versus surface condition | onset wall-superheat plots/tables | Surface-condition sensitivity and onset comparison | needs source-specific uncertainty notes |
| 2 | unno_2025_reduced_pressure_confined_meb | Reduced-pressure confined-vessel MEB onset pressure and heat-transfer condition | reduced-pressure onset figures/tables | Compare subatmospheric/reduced-pressure relevance | needs figure-level digitization |
| 3 | zhao_2025_open_microchannel_meb | Flow MEB heat flux and wall superheat in open microchannels | microchannel boiling curves and durability plots | Context only; different geometry from pool boiling | needs geometry-separated extraction |
