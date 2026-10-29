# Extended 10 kPa Post-CHF Protocol Diagnostics

## Provenance

- Selected CHF, NBR, minimum-flux, and maximum-temperature values are read from the manuscript protocol-event table; the companion event ledger records CHF/NBR event provenance.
- Heater shutoff, cutoff temperature, raw thermal peak, and time partitions are derived from the processed thermal time series in `Z:\ned3-019-BoilingHysteresis10kPa`.
- The electrical energy is input energy integrated from selected CHF to heater cutoff. It is not a stored-energy measurement.

## Observed range

- $H$ decreases from 0.947 to 0.454 across the controlled sequence.
- Heater-on duration after selected CHF increases from 15.5 to 442.6 s.
- Cutoff-to-selected-NBR duration increases from 9.5 to 619.0 s.
- Raw post-cutoff temperature overshoot spans 0.48 to 2.47 $^\circ$C.

## Interpretation boundary

These five cases are a controlled within-apparatus protocol perturbation near 10 kPa. They demonstrate the response to longer post-CHF heating, but do not provide independent replication across pressure or surface architecture.
The hydrophone context figure uses a band-integrated sensor-voltage-squared proxy aligned by archived clock offsets. It is not calibrated acoustic pressure and cannot independently identify vapor-film continuity or wall wetting.
