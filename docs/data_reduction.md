# Thermal Data Reduction And Event Definitions

This document records the methodology behind the thermal BoilingLab scripts and
the thesis analysis. The implementation constants for the current demo workflow
live in `scripts/run_single_case_demo.py`.

## Input Signals

The single-case and multi-case workflows expect raw data folders keyed by
`Test ID`, such as `Boiling-417`. The core files are:

- `Temperature.lvm`: time, four embedded copper thermocouples, liquid
  temperature, and vapor temperature;
- `Pressure.lvm`: time and pressure-transducer voltage converted to kPa by the
  LabVIEW acquisition workflow;
- `DC_power.lvm`: MagnaDC set/output voltage, current, and power; and
- optional optical or acoustic files used by specialized analyses.

The metadata spreadsheet, `metadata/Pool Boiling Test Log.xlsx`, links each
`Test ID` to the physical run conditions.

## Thermocouple Geometry

The copper block uses four embedded thermocouples along the axial conduction
path beneath the boiling surface. The current analysis uses positions relative
to the lowest thermocouple:

```text
x1 = 0 mm
x2 = 2.54 mm
x3 = 5.08 mm
x4 = 7.62 mm
```

For the flat copper geometry used by the current single-case runner, the
boiling-surface location is:

```text
xs = 13.1826 mm
```

If a future script analyzes a different copper-block geometry or surface-stack
definition, update the surface-location constant before comparing wall
temperature, wall superheat, HTC, or CHF values.

## Linear Conduction Fit

At each time step, the four embedded temperatures are fit with a one-dimensional
linear model:

```text
T(x) = m x + b
```

where `m` is the axial temperature gradient and `b` is the fitted temperature at
`x = 0`. For `n = 4` thermocouples,

```text
m = [n sum(xi Ti) - sum(xi) sum(Ti)]
    / [n sum(xi^2) - (sum(xi))^2]

b = [sum(Ti) - m sum(xi)] / n
```

The wall temperature is extrapolated to the boiling surface:

```text
T_surface = m xs + b
```

The scripts also compute the coefficient of determination, `R2`, for the
four-point linear fit. Low `R2` values flag departures from the one-dimensional
conduction assumption, sensor issues, or event windows where the fitted
gradient is less reliable.

## Heat Flux, Wall Superheat, And HTC

The current workflow uses a constant copper thermal conductivity:

```text
k_Cu = 392 W/(m K)
```

Heat flux toward the boiling surface is calculated by Fourier's law:

```text
q'' = -k_Cu m
```

The scripts convert from `W/m^2` to `W/cm^2` by dividing by `1e4`.

Saturation temperature is calculated from the mean vessel pressure for the run
using `pyXSteam` in the single-case and multi-case scripts. Wall superheat is:

```text
DeltaT_wall = T_surface - T_sat
```

The heat-transfer coefficient is evaluated as:

```text
h = q'' / DeltaT_wall
```

For structured surfaces, `T_surface` is a base-temperature estimate at the
projected 10 mm x 10 mm heater area. It should not be interpreted as the local
temperature of fin tips, channel sidewalls, or microlayers.

## Pressure And Saturation Assumptions

The pressure signal is measured in the vapor space near the top of the vessel.
The heater surface is at a slightly higher static pressure because of the
liquid column above it. For the thesis fill level, this hydrostatic offset is
less than 0.7 kPa. It is most important at the lowest pressure condition and
should be included in the interpretation uncertainty for 10 kPa tests.

The thesis protocol treats saturated operation as established when both liquid
and vapor temperatures remain within `+/- 1 deg C` of the saturation
temperature associated with the target pressure. Pressure control is considered
acceptable when the vessel pressure remains within about `+/- 0.5 kPa` of the
target during the relevant interval.

## Heating-Branch Filtering

`scripts/run_multi_case_comparison.py` aligns `DC_power.lvm` to
`Temperature.lvm` using the LVM file start times. It interpolates DC output
power onto the temperature time base and keeps samples whose aligned power is
greater than the configured threshold, `0 W` by default.

This heating-only branch is appropriate for comparing active boiling curves.
It intentionally removes the cooling path after power shutoff, which is used
separately for hysteresis analysis.

## Event Definitions

The thesis and defense deck describe the qualitative sequence:

```text
ONB -> NB -> CHF -> TB -> NBR -> NB
```

Use these operational definitions in BoilingLab notes and generated summaries:

- `ONB`: onset of nucleate boiling, identified from visual evidence and the
  beginning of sustained boiling heat-transfer behavior.
- `CHF`: critical heat flux during active heating. Experimentally, the heater
  power is shut off when a sharp heater-block temperature rise and the real-time
  heat-flux or wall-temperature signature indicate boiling crisis.
- `TB`: transition boiling after the CHF event.
- `NBR`: nucleate boiling return during cooling, when the vapor/transition state
  breaks back into nucleating bubbles and the cooling branch rejoins nucleate
  boiling behavior.

The historical notebook and `run_single_case_demo.py` also retain marker names
used for exploratory analysis:

- `chf_proxy_*`: a fixed-window maximum from the original notebook. If the test
  log says `CHF not reached`, interpret this only as a notebook marker, not a
  confirmed physical CHF.
- `dnb_*`: an early heat-flux maximum before a sudden drop, used as a
  transition-associated marker in the thermal-acoustic workflow.
- `peak_*`: the wall-temperature peak during the transition event.
- `oscillation_peak_*`: the first sustained oscillation peak in the configured
  post-transition window.
- `dc_shutoff_*`: the time when the MagnaDC output returns near zero.

Keep the test-log status with every summary so confirmed CHF/NBR events are not
mixed with proxy markers.

## Boiling Hysteresis Metrics

The manuscript-level hysteresis runner starts from an organized spreadsheet
rather than raw LVM files. It expects pressure, surface, `CHF`, `NBR`,
`T_surface Max`, `T_sat`, `Temperature at NBR`, and optional BubbleID columns.

The primary hysteresis ratio is:

```text
H = q''_NBR / q''_CHF
```

The main thermal-maturity collapse is:

```text
H = H_min + (1 - H_min) exp[-((T_max - T_sat) / DeltaT_s)^m]
```

where `H_min` is the unresolved lower hysteresis asymptote, `DeltaT_s` is the
wall-superheat scale for post-CHF vapor-state maturation, and `m` is a shape
exponent. The runner also fits a pressure-dependent reference-temperature form:

```text
H = H_min + (1 - H_min) exp[-((T_max - T_sat) / (T_ref - T_sat))^m]
```

`T_NBR - T_sat` is analyzed separately to determine whether return to nucleate
boiling is concentrated in a wall-superheat band.

## Optical Vapor-State Metrics

When BubbleID columns are present, the hysteresis runner summarizes side-view
vapor fraction and bubble count at `ONB`, `CHF`, and `NBR`:

```text
ONB_vf, CHF_vf, NBR_vf
ONB_count, CHF_count, NBR_count
```

The vapor persistence ratio,

```text
VF_NBR / VF_CHF
```

is used as a projected optical diagnostic for how much vapor remains visible at
NBR compared with CHF. It is not a direct wall dry-area fraction and should not
be treated as a calibrated interfacial area measurement.

## Minimum Reproducibility Checks

Before reporting a new case or adding it to a manuscript-level table, verify:

- the `Test ID` matches the raw folder and metadata row;
- pressure and saturation-temperature control are within the intended bands;
- the DC power trace is aligned to the temperature trace;
- the thermocouple extrapolation `R2` is acceptable in the event windows;
- wall temperature and heat flux use the correct surface-location constant;
- the projected heater area is 10 mm x 10 mm unless explicitly documented
  otherwise;
- event markers are labeled as confirmed events or proxies; and
- generated CSV/JSON summaries retain pressure, `T_sat`, surface type, test
  status, and marker times.
