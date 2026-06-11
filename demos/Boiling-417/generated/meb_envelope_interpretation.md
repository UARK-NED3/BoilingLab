# Boiling-417 MEB Envelope Analysis

## Scope

This analysis quantifies whether the oscillation amplitude increases and begins
to saturate during the active-heating MEB interval. The requested window was
`300-700 s`, but Boiling-417 power shuts off at `t_off = 673.893 s`; therefore
the fitted MEB envelope window is `308.0-673.893 s`, starting at the first
thermal oscillation peak `t_osc`.

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
5. Fits a first-order asymptotic growth model,
   `A(t) = A_inf - (A_inf - A_0) exp(-(t - t_osc) / tau)`, to the smoothed
   envelope and reports the fitted percent change, time constant `tau`, and
   saturation fraction at the end of the window.

The complete per-time envelope data are in `meb_envelope_analysis.csv`; the
growth metrics are in `meb_envelope_metrics.csv`.

## Results

| Signal | Fitted envelope start | Fitted envelope end | Percent change | `tau` | Saturation | R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `T_w` | `6.015 C` | `16.050 C` | `166.8%` | `239.1 s` | `78%` | `0.935` |
| `q''` | `14.129 W/cm^2` | `35.279 W/cm^2` | `149.7%` | `247.8 s` | `77%` | `0.938` |
| Hydrophone power | `1.472e-2 V^2` | `3.537e-2 V^2` | `140.2%` | `7308.8 s` | `5%` | `0.588` |

The temperature and heat-flux envelopes show a strong increase that is already
slowing by shutoff. Their fitted saturation fractions are about 77-78%, so the
thermal oscillation amplitude is moving toward a quasi-steady MEB envelope but
has not fully saturated before power is turned off. The hydrophone-power
envelope increases, but the fitted `tau` is much longer than the observation
window and the R2 is lower; this indicates that a single asymptotic growth curve
is a weak description of the acoustic power envelope, likely because it contains
intermittent burst-like structure in addition to the MEB oscillation amplitude.

## Physical Interpretation

The synchronized growth in thermal and acoustic envelopes suggests that the
MEB oscillation is becoming more energetic over time while power remains on, but
the asymptotic fit suggests the thermal response is approaching a finite
oscillation amplitude. A plausible mechanism is progressive strengthening and
spatial synchronization of the vapor-bubble growth/collapse cycle until the
near-wall liquid replenishment, condensation rate, vapor generation rate, and
applied heat input approach a dynamic balance. As the vapor structure oscillates
more violently, it can produce larger wall-temperature and heat-flux excursions
and larger pressure/acoustic emission during collapses. The acoustic power need
not saturate on the same time scale because it is more sensitive to intermittent
collapse intensity and sensor-band coupling.

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
