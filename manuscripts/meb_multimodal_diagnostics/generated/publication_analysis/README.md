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

| case | power_label | nominal_power_W | mean_pressure_kPa | pressure_std_kPa | mean_liquid_temperature_C | saturation_temperature_C | subcooling_K | maximum_heat_flux_W_cm2 | q_DNB_raw_W_cm2 | q_DNB_plot_W_cm2 | t_DNB_s | dnb_resolved_for_plot | maximum_wall_temperature_C | heating_duration_s | mean_power_during_heating_W |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Case A | $P_{\mathrm{load}}$ = 150 W | 150 | 97.3 | 0.0586 | 58.8 | 98.8 | 40 | 142 | -1.02 |  | 1.2 | False | 113 | 537 | 150 |
| Case B | $P_{\mathrm{load}}$ = 180 W | 180 | 97.3 | 0.0586 | 52.4 | 98.8 | 46.5 | 163 | 152 | 152 | 178 | True | 159 | 568 | 179 |
| Case C | $P_{\mathrm{load}}$ = 230 W | 230 | 97.5 | 0.0582 | 57.3 | 98.9 | 41.6 | 267 | 188 | 188 | 151 | True | 167 | 753 | 228 |
| Case D | $P_{\mathrm{load}}$ = 250 W | 250 | 97.5 | 0.0582 | 57.6 | 98.9 | 41.3 | 278 | 191 | 191 | 125 | True | 173 | 670 | 248 |

## Hydrophone summary

| case | nominal_power_W | hydrophone_available | developed_meb_modulation | band_power_mean_V2 | band_power_max_V2 | median_peak_frequency_Hz | median_centroid_frequency_Hz | dominant_slow_modulation_Hz | meb_power_envelope_frequency_Hz | power_centroid_best_lag_s | power_centroid_best_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Case A | 150 | True | False | 0.000648 | 0.00321 | 975 | 1.4e+03 | 0.0247 |  | 0 | -0.85 |
| Case B | 180 | True | False | 0.00409 | 0.0232 | 980 | 1.1e+03 | 0.005 |  | 0 | -0.803 |
| Case C | 230 | True | True | 0.0081 | 0.0595 | 919 | 1.06e+03 | 0.05 | 0.05 | 0.64 | 0.824 |
| Case D | 250 | True | True | 0.0157 | 0.344 | 917 | 1.06e+03 | 0.08 | 0.08 | -0.64 | 0.637 |

## AE waveform summary

| case | nominal_power_W | band_power_mean_V2 | band_power_max_V2 | median_peak_frequency_Hz | median_centroid_frequency_Hz | dominant_slow_modulation_Hz |
| --- | --- | --- | --- | --- | --- | --- |
| Case C | 230 | 5.35e-06 | 5.34e-05 | 8.42e+03 | 8.57e+03 | 0.055 |
| Case D | 250 | 4.85e-06 | 4.99e-05 | 8.42e+03 | 8.49e+03 | 0.0801 |

## First-pass uncertainty and quality diagnostics

| case | nominal_power_W | pressure_std_kPa | pressure_instrument_standard_uncertainty_kPa | temperature_heat_flux_fit_mean_R2 | temperature_heat_flux_fit_min_R2 | hydrophone_band_power_cv | hydrophone_time_bin_s | hydrophone_centroid_iqr_Hz | hydrophone_peak_frequency_iqr_Hz | ae_waveform_available | note | wall_temperature_standard_uncertainty_C | wall_temperature_expanded_uncertainty_C_k2 | heat_flux_temperature_standard_uncertainty_W_cm2 | heat_flux_k_standard_uncertainty_W_cm2 | heat_flux_combined_standard_uncertainty_W_cm2 | heat_flux_expanded_uncertainty_W_cm2_k2 | heat_flux_position_sensitivity_W_cm2_per_C |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Case A | 150 | 0.0586 | 0.097 | 0.979 | 0.0567 | 0.33 | 0.32 | 138 | 15.6 | False | Data-derived diagnostic with pre-submission instrument assumptions; replace with calibration-certificate values before submission. | 0.862 | 1.72 | 3.45 | 2.84 | 4.47 | 8.94 | 0.0894 |
| Case B | 180 | 0.0586 | 0.097 | 0.991 | 0.517 | 1.14 | 0.32 | 159 | 32.8 | False | Data-derived diagnostic with pre-submission instrument assumptions; replace with calibration-certificate values before submission. | 0.862 | 1.72 | 3.45 | 3.26 | 4.75 | 9.5 | 0.0894 |
| Case C | 230 | 0.0582 | 0.097 | 0.985 | 0.0361 | 1.05 | 0.32 | 168 | 306 | True | Data-derived diagnostic with pre-submission instrument assumptions; replace with calibration-certificate values before submission. | 0.862 | 1.72 | 3.45 | 5.34 | 6.36 | 12.7 | 0.0894 |
| Case D | 250 | 0.0582 | 0.097 | 0.994 | 0.804 | 1.43 | 0.32 | 158 | 189 | True | Data-derived diagnostic with pre-submission instrument assumptions; replace with calibration-certificate values before submission. | 0.862 | 1.72 | 3.45 | 5.56 | 6.54 | 13.1 | 0.0894 |

## Propagated uncertainty budget

| case | quantity | value | unit | coverage | basis | source_status |
| --- | --- | --- | --- | --- | --- | --- |
| Case A | wall_temperature | 1.72 | degC | expanded k=2 | linear extrapolation of four thermocouples; Type-T/DAQ standard uncertainty assumed 0.50 degC | pre-submission assumption |
| Case A | heat_flux | 8.94 | W/cm^2 | expanded k=2 | Fourier-law propagation from thermocouple uncertainty plus 2% copper thermal-conductivity standard uncertainty | pre-submission assumption |
| Case A | event_time | 1 | s | expanded k=2 | wall-clock synchronization and time-bin/event-picking allowance | pre-submission assumption |
| Case A | hydrophone_band_power | 0.463 | relative | expanded k=2 | voltage PSD power proxy; combines voltage, sensitivity, and PSD-estimator terms | pre-submission assumption |
| Case A | hydrophone_characteristic_frequency | 3.12 | Hz | resolution-scale | larger of time-window resolution and spectrogram bin-scale floor | data-derived |
| Case B | wall_temperature | 1.72 | degC | expanded k=2 | linear extrapolation of four thermocouples; Type-T/DAQ standard uncertainty assumed 0.50 degC | pre-submission assumption |
| Case B | heat_flux | 9.5 | W/cm^2 | expanded k=2 | Fourier-law propagation from thermocouple uncertainty plus 2% copper thermal-conductivity standard uncertainty | pre-submission assumption |
| Case B | event_time | 1 | s | expanded k=2 | wall-clock synchronization and time-bin/event-picking allowance | pre-submission assumption |
| Case B | hydrophone_band_power | 0.463 | relative | expanded k=2 | voltage PSD power proxy; combines voltage, sensitivity, and PSD-estimator terms | pre-submission assumption |
| Case B | hydrophone_characteristic_frequency | 3.12 | Hz | resolution-scale | larger of time-window resolution and spectrogram bin-scale floor | data-derived |
| Case C | wall_temperature | 1.72 | degC | expanded k=2 | linear extrapolation of four thermocouples; Type-T/DAQ standard uncertainty assumed 0.50 degC | pre-submission assumption |
| Case C | heat_flux | 12.7 | W/cm^2 | expanded k=2 | Fourier-law propagation from thermocouple uncertainty plus 2% copper thermal-conductivity standard uncertainty | pre-submission assumption |
| Case C | event_time | 1 | s | expanded k=2 | wall-clock synchronization and time-bin/event-picking allowance | pre-submission assumption |
| Case C | hydrophone_band_power | 0.463 | relative | expanded k=2 | voltage PSD power proxy; combines voltage, sensitivity, and PSD-estimator terms | pre-submission assumption |
| Case C | hydrophone_characteristic_frequency | 3.12 | Hz | resolution-scale | larger of time-window resolution and spectrogram bin-scale floor | data-derived |
| Case D | wall_temperature | 1.72 | degC | expanded k=2 | linear extrapolation of four thermocouples; Type-T/DAQ standard uncertainty assumed 0.50 degC | pre-submission assumption |
| Case D | heat_flux | 13.1 | W/cm^2 | expanded k=2 | Fourier-law propagation from thermocouple uncertainty plus 2% copper thermal-conductivity standard uncertainty | pre-submission assumption |
| Case D | event_time | 1 | s | expanded k=2 | wall-clock synchronization and time-bin/event-picking allowance | pre-submission assumption |
| Case D | hydrophone_band_power | 0.463 | relative | expanded k=2 | voltage PSD power proxy; combines voltage, sensitivity, and PSD-estimator terms | pre-submission assumption |
| Case D | hydrophone_characteristic_frequency | 3.12 | Hz | resolution-scale | larger of time-window resolution and spectrogram bin-scale floor | data-derived |
| Case C | ae_band_power | 0.233 | relative | expanded k=2 | AE waveform voltage PSD proxy; combines voltage-chain and PSD-estimator terms. Waveform files are available only for Cases C-D. | pre-submission assumption |
| Case C | ae_characteristic_frequency | 3.12 | Hz | resolution-scale | spectrogram/characteristic-frequency bin-scale floor. Waveform files are available only for Cases C-D. | data-derived |
| Case D | ae_band_power | 0.233 | relative | expanded k=2 | AE waveform voltage PSD proxy; combines voltage-chain and PSD-estimator terms. Waveform files are available only for Cases C-D. | pre-submission assumption |
| Case D | ae_characteristic_frequency | 3.12 | Hz | resolution-scale | spectrogram/characteristic-frequency bin-scale floor. Waveform files are available only for Cases C-D. | data-derived |
| Case C | wall_temperature_envelope_asymptote | 3.77 | Wall temperature (C) | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | wall_temperature_envelope_time_constant_s | 20.7 | s | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | wall_temperature_envelope_saturation_fraction_at_end | 0.195 | fraction | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | heat_flux_envelope_asymptote | 7.6 | Heat flux (W/cm$^2$) | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | heat_flux_envelope_time_constant_s | 21.2 | s | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | heat_flux_envelope_saturation_fraction_at_end | 0.194 | fraction | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | hydrophone_power_envelope_asymptote | 0.00756 | Band-integrated power (V$^2$) | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | hydrophone_power_envelope_time_constant_s | 154 | s | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case C | hydrophone_power_envelope_saturation_fraction_at_end | 0.0776 | fraction | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | wall_temperature_envelope_asymptote | 3.77 | Wall temperature (C) | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | wall_temperature_envelope_time_constant_s | 47.8 | s | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | wall_temperature_envelope_saturation_fraction_at_end | 0.157 | fraction | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | heat_flux_envelope_asymptote | 8.31 | Heat flux (W/cm$^2$) | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | heat_flux_envelope_time_constant_s | 49.6 | s | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | heat_flux_envelope_saturation_fraction_at_end | 0.154 | fraction | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | hydrophone_power_envelope_asymptote | 0.0876 | Band-integrated power (V$^2$) | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | hydrophone_power_envelope_time_constant_s | 1.46e+03 | s | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |
| Case D | hydrophone_power_envelope_saturation_fraction_at_end | 0.00975 | fraction | expanded k=2 | asymptotic envelope-fit parameter; provisional 10% standard fit-uncertainty floor pending bootstrap/covariance refinement | pre-submission assumption |

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

## Normalized literature extraction tables

`literature_digitized_boiling_points_publication.csv` contains normalized
wall-superheat and heat-flux values from the current `test2_meb`
compilation, with status labels that distinguish source-reported values,
range endpoints, and any figure-digitized curve points.
`literature_onset_signature_values_publication.csv` contains onset and
frequency/signature values used to compare literature MEB behavior with
the present hydrophone modulation metrics.

| paper_id | curve_id | figure_id | wall_superheat_K | heat_flux_W_cm2 | digitization_status | recommended_use | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| horiuchi_2019_transient_nucleate_to_meb | transition_subcooling_20K | Fig. text | 19.8 | 256 | reported_text_or_first_pass_extraction | Use as boiling-curve/onset comparison after source verification | Reported average wall superheat and heat flux before/near MEB transition. |
| horiuchi_2019_transient_nucleate_to_meb | transition_subcooling_20K | Fig. text | 28.1 | 282 | reported_text_or_first_pass_extraction | Use as boiling-curve/onset comparison after source verification | Reported average wall superheat and heat flux before/near MEB transition. |
| horiuchi_2019_transient_nucleate_to_meb | transition_subcooling_20K | Fig. text | 53.4 | 338 | reported_text_or_first_pass_extraction | Use as boiling-curve/onset comparison after source verification | Reported average wall superheat and heat flux before/near MEB transition. |
| horiuchi_2021_spatiotemporal_meb | C_MEB_range_high | C-MEB range | 80 | 320 | reported_range_endpoint | Use as regime envelope only | Endpoint of reported C-MEB q and wall-superheat range; pair used as range envelope, not exact curve point. |
| horiuchi_2021_spatiotemporal_meb | C_MEB_range_low | C-MEB range | 40 | 220 | reported_range_endpoint | Use as regime envelope only | Endpoint of reported C-MEB q and wall-superheat range; pair used as range envelope, not exact curve point. |
| horiuchi_2021_spatiotemporal_meb | S_MEB_range_high | S-MEB range | 80 | 100 | reported_range_endpoint | Use as regime envelope only | Reported S-MEB heat-flux oscillation amplitude is about 1 MW/m^2 while wall superheat ranges 50-80 K. |
| horiuchi_2021_spatiotemporal_meb | S_MEB_range_low | S-MEB range | 50 | 100 | reported_range_endpoint | Use as regime envelope only | Reported S-MEB heat-flux oscillation amplitude is about 1 MW/m^2 while wall superheat ranges 50-80 K. |
| inada_2016_cavitation_bubble_blow_pit | pool_boiling_MEB_context | Fig. 5 text | 100 | 1.1e+03 | reported_text_or_first_pass_extraction | Use as boiling-curve/onset comparison after source verification | Pool-boiling system heat flux reported at wall superheat 100 K; specialized system, context only for upper MEB capability. |
| sinha_2021_deep_learning_sound_boiling | plain_copper_chf_context | Fig. 1/2 text | 16 | 145 | reported_text_or_first_pass_extraction | Use as boiling-curve/onset comparison after source verification | Plain copper/water CHF acoustic-boiling context, not MEB-specific. |
| tang_2016_transition_to_meb | tracked_microbubble_meb | microbubble tracking case | 53.6 | 559 | reported_text_or_first_pass_extraction | Use as boiling-curve/onset comparison after source verification | Reported time-averaged wall superheat and heat flux for tracked MEB microbubbles. |

| source_id | source_type | wall_superheat_K | heat_flux_W_cm2 | frequency_Hz | digitization_status | notes |
| --- | --- | --- | --- | --- | --- | --- |
| boilinglab_boiling_412 | user_experiment | 13.9 | 142 |  | present_work_reduced_data | Lower-power BoilingLab case; no developed MEB envelope analysis yet. |
| boilinglab_boiling_413 | user_experiment | 60.3 | 163 | 0.005 | present_work_reduced_data | Lower-power case with weak/slow hydrophone modulation. |
| boilinglab_boiling_416 | user_experiment | 68.1 | 267 | 0.05 | present_work_reduced_data | Developed thermal-acoustic oscillatory case; AE WFS dominant modulation 0.055 Hz; thermal envelope tau about 103-106 s. |
| boilinglab_boiling_417 | user_experiment | 74 | 278 | 0.08 | present_work_reduced_data | Developed thermal-acoustic oscillatory case; AE WFS dominant modulation 0.080 Hz; thermal envelope tau about 239-248 s. |
| zeigarnik_2012_microbubble_emission_nature | reported_text |  |  |  | literature_reported_or_first_pass_extraction | Reports microbubble-emission heat-flow ranges up to 0.8-33 MW/m^2 across prior studies; use as historical mechanism context. |
| horiuchi_2021_spatiotemporal_meb | reported_text |  |  |  | literature_reported_or_first_pass_extraction | Reports C-MEB q range 2.2-3.2 MW/m^2, S-MEB heat-flux oscillation amplitude about 1 MW/m^2, and sound-frequency shifts. |
| tang_2016_transition_to_meb | reported_text |  |  |  | literature_reported_or_first_pass_extraction | Reports transition from nucleate boiling to MEB and high-frequency repetitive vapor-bubble collapse. |
| zhu_2014_visualized_meb | reported_text |  |  | 2.7e+03 | literature_reported_or_first_pass_extraction | Reports visualized MEB at several heat flux/subcooling conditions and a boiling-sound peak near 2700 Hz. |
| ono_2023_acoustic_state_detection_meb | reported_text |  |  | 4.8e+04 | literature_reported_or_first_pass_extraction | Uses cepstrum/DNN acoustic state detection; reports max heat flux 6.2 MW/m^2 and hydrophone sampling at 48 kHz. |
| kobayashi_2022_homogeneity_boiling_sound_meb | reported_text |  | 1.3e+03 |  | literature_reported_or_first_pass_extraction | Reports boiling sound peak narrowing around 300-500 Hz in developed MEB and bubble passage frequency about 40 Hz. |
| zhou_2018_sound_emission_subcooled_pool | reported_text |  |  |  | literature_reported_or_first_pass_extraction | Reports MEB sound peaks around 1 kHz and 10 kHz and high-subcooling components up to/beyond 50 kHz. |
| kobayashi_2024_reduced_pressure_confined_meb | reported_text |  | 311 |  | literature_reported_or_first_pass_extraction | Reports maximum removed heat flux 311 W/cm^2 at reduced pressure with confined vessel; strong comparison target for BoilingLab subatmospheric pressure. |

## Final ATE panels

- `final_ate_panels/fig01_ate_case_heat_flux_and_hydrophone_modulation.png`
- `final_ate_panels/fig02_ate_envelope_metrics.png`
- `final_ate_panels/fig03_ate_literature_boiling_curve_context.png`
- `mechanism/fig08_representative_microbubble_frames.png`
- `mechanism/fig09_storage_release_model.png`
- `final_ate_panels/captions.md`
