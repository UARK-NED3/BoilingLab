# MEB Mechanism Figure Notes

The MP4 files are encoded at 30 fps from 150 fps high-speed recordings. Frame extraction therefore uses `video_time = experimental_time * 5`.

## Representative frames

The selected frames compare low and high visually screened microbubble-density states in the developed oscillatory interval. The hydrophone-power percentile at each selected time is reported because a single video frame need not coincide exactly with the center of an acoustic burst.

| case | window_start_s | window_end_s | low_visual_time_s | low_visual_hydrophone_power_percentile | high_visual_time_s | high_visual_hydrophone_power_percentile |
| --- | --- | --- | --- | --- | --- | --- |
| Case C | 321.6 | 640.2 | 601.6 | 37.3 | 326.6 | 72.1 |
| Case D | 308.0 | 640.2 | 588.0 | 55.1 | 513.0 | 89.1 |

## Storage-release model

The model is a conceptual driven, damped, thresholded LC-like relaxation oscillator. A storage state is charged by constant input and discharged through an inertial release coordinate when a threshold is exceeded. It is not fitted to the experiments; it demonstrates how instantaneous heat release and acoustic bursts can exceed the nominal input scale when stored energy is released intermittently.
