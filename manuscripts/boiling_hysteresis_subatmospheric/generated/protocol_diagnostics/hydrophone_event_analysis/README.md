# Event-Aligned Hydrophone Analysis

## Scope

This analysis reprocesses raw hydrophone voltage records from the five extended 10 kPa flat-copper tests. It aligns the records to the temperature clock with archived LVM-header offsets and uses manuscript-selected CHF, heater-cutoff, maximum-temperature, and NBR events. Dataset screening event files are not used.

## Signal definition

For each 2 s Hann-windowed segment (75% overlap), a fourth-order 20 Hz high-pass filter is applied, a voltage PSD is evaluated, and band-integrated voltage variance is calculated as V_band^2(t) = integral_{40 Hz}^{3000 Hz} S_VV(f,t) df. The plotted level is 10 log10(V_band^2 / 1 V^2).

This is an uncalibrated, frequency-bounded sensor-voltage-squared proxy. It is not acoustic pressure, sound power, bubble-collapse energy, a direct vapor-film measurement, or a direct wetting measurement.

## Event windows

The descriptive windows are fixed before inspecting the acoustic result: pre-CHF (CHF minus 30 to minus 10 s), post-CHF heating (CHF plus 10 s to cutoff minus 10 s), post-cutoff (raw maximum-temperature time plus 20 s to NBR minus 40 s), and pre-NBR (NBR minus 40 to minus 10 s). Windows shorter than 10 s are marked unusable rather than padded or redefined.

The summary contains 17 usable case-window combinations. Rows are descriptive summaries of serially correlated STFT windows; they are not independent replicates and no inferential p-values are reported.

## Interpretation limit

A decrease in the proxy is compatible with a change in the acoustic source and/or transmission path during the post-CHF history. It cannot by itself distinguish fewer collapse events, vapor-mediated attenuation, changing heat flux, sensor coupling, or background noise. The result is synchronized regime context, not independent validation of the thermal hysteresis correlation.
