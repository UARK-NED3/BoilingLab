# Multi-Case Boiling Curve Comparison

This generated comparison plots heat flux against wall temperature and wall superheat for the selected tests. For these demo cases, the test log marks CHF as not reached, so the plots are intended for curve-shape comparison rather than CHF ranking.

| Test ID | Power (W) | Status | Mean pressure (kPa) | Mean liquid temp (C) | Max heat flux (W/cm^2) | Max surface temp (C) |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Boiling-412 | 150 | Failure: CHF not reached | 97.28 | 58.83 | 142.02 | 112.74 |
| Boiling-413 | 180 | Failure: CHF not reached | 97.30 | 52.38 | 163.12 | 159.18 |
| Boiling-416 | 230 | Failure: CHF not reached | 97.47 | 57.27 | 267.24 | 166.97 |
| Boiling-417 | 250 | Failure: CHF not reached | 97.51 | 57.60 | 277.96 | 172.87 |

Only samples with positive DC output power are included in these generated curves.

Generated plots:

- [Heat flux vs wall temperature](plots/heat_flux_vs_wall_temperature.png)
- [Heat flux vs wall superheat](plots/heat_flux_vs_wall_superheat.png)
