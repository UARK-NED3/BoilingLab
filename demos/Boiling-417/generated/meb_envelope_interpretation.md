# Boiling-417 MEB Envelope Analysis

## Scope

This analysis quantifies whether the oscillation amplitude increases during the
active-heating MEB interval. The requested window was `300-700 s`, but Boiling-417
power shuts off at `t_off = 673.893 s`; therefore the fitted MEB envelope window is
`300.0-673.893 s`.

Signals analyzed:

- Extrapolated wall temperature, `T_w`
- Heat flux, `q''`
- Hydrophone band-integrated power proxy, integrated over frequency in linear
  `V^2`

## Method

For each signal, the runner:

1. Selects the active-heating MEB window.
2. Removes a slow baseline using a 75 s Savitzky-Golay smoother.
3. Computes a Hilbert-transform envelope of the detrended oscillatory component.
4. Smooths the envelope with a 35 s Savitzky-Golay smoother.
5. Fits a linear trend to the envelope and reports the fitted percent change.

The complete per-time envelope data are in `meb_envelope_analysis.csv`; the
growth metrics are in `meb_envelope_metrics.csv`.

## Results

| Signal | Fitted envelope start | Fitted envelope end | Percent change | R2 |
| --- | ---: | ---: | ---: | ---: |
| `T_w` | `6.977 C` | `17.217 C` | `146.8%` | `0.896` |
| `q''` | `15.972 W/cm^2` | `37.725 W/cm^2` | `136.2%` | `0.900` |
| Hydrophone power | `1.431e-2 V^2` | `3.551e-2 V^2` | `148.2%` | `0.606` |

The temperature and heat-flux envelopes show a strong monotonic increase over
the active MEB interval. The hydrophone-power envelope also increases strongly,
but with more intermittent bursts, so the linear trend has a lower R2.

## Physical Interpretation

The synchronized growth in thermal and acoustic envelopes suggests that the
MEB oscillation is becoming more energetic over time while power remains on. A
plausible mechanism is progressive strengthening and spatial synchronization of
the vapor-bubble growth/collapse cycle. As the vapor structure oscillates more
violently, it can produce larger wall-temperature and heat-flux excursions and
larger pressure/acoustic emission during collapses.

This interpretation is consistent with published MEB observations that connect
MEB heat transfer to oscillating vapor bubbles, oscillating liquid flow, pressure
fluctuations, and boiling sound. However, this envelope-growth metric is not
commonly reported directly; most prior work emphasizes oscillation frequency,
spectrogram features, pressure-fluctuation amplitude, heat-transfer hysteresis,
or visualized bubble/flow dynamics.

## Literature Context

- Tang et al. report rapid oscillating flow outside a bubble attached to the
  heating surface in MEB and quantify its velocity dependence on subcooling and
  heat flux.
- Kobayashi et al. report MEB hysteresis and connect boiling sound spectrograms
  to synchronous vapor-bubble oscillations; they emphasize fundamental frequency
  variation with heat flux.
- Kumagai and Kawasaki report that pressure-fluctuation peaks correspond to
  bubble collapse in MEB.

These studies support the idea that thermal oscillations and acoustic power can
share a bubble-collapse/oscillating-flow origin. The Boiling-417 envelope result
adds a time-resolved amplitude-growth view of that coupled thermal-acoustic
behavior.
