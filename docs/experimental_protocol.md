# Experimental Protocol: Subatmospheric Pool Boiling

These notes summarize the experimental facility and procedure used for
Ishraq Hossain's subatmospheric pool-boiling thesis experiments. They are meant
to connect the physical experiment to the BoilingLab metadata and analysis
scripts. They are not a standalone laboratory safety SOP.

## Scope

The thesis experiments used transient, quasi-steady pool boiling of deionized
water over a target pressure range of 10 to 100 kPa. Three upward-facing copper
test surfaces were studied:

- flat copper,
- straight copper microchannels, and
- square copper micro-pin-fins.

The main experimental outputs are boiling curves, CHF and HTC trends, boiling
hysteresis during post-CHF cooling, and optical vapor-state diagnostics.

## Facility

The pressure-controlled pool-boiling chamber is a 304 stainless-steel vessel
with approximate internal dimensions of 200 mm x 180 mm x 180 mm. The chamber
uses reinforced glass viewports on two opposite side faces for optical access.
The ceiling includes ports for fluid filling, the vacuum connection, a reflux
condenser, and the inlet and outlet of an internal condenser loop. The base
includes the heating-element-enclosure port and a drain valve.

Vapor management uses two condenser paths. A Graham reflux condenser mounted at
the top of the chamber returns condensed vapor by gravity and helps preserve a
constant water inventory during degassing and boiling. An internal coiled copper
condenser near the chamber ceiling provides finer pressure control during
boiling. Both condenser paths are connected to a chiller loop. Vessel pressure
is regulated manually with the continuously running vacuum pump valve and the
internal-condenser coolant flow valve.

The chamber contains two bulk-environment thermocouples. The lower
thermocouple records liquid-pool temperature and the upper thermocouple records
vapor-space temperature. Vapor pressure is measured near the top of the vessel
with a DwyerOmega PX409 pressure transducer with a 0 to 210 kPa range. Two
side-wall immersion heaters, each rated at 250 W, are powered through a VARIAC
and are used to degas the water and control the bulk liquid temperature.

## Heating Element Enclosure

The heating element enclosure is inserted through the chamber base. It uses
concentric PEEK structures, a glass-mica ceramic support, and chopped-fiber
insulation around the copper block to suppress radial heat loss and promote
one-dimensional conduction toward the boiling surface.

The copper specimen is heated from below by nine 50 W cartridge heaters powered
by a MagnaDC programmable DC power supply. The exposed boiling area is
10 mm x 10 mm. The rear ceramic layer thermally isolates the copper block from
the PEEK structure.

The thesis specimens were oxygen-free copper 101 blocks fabricated as flat,
microchannel, and micro-pin-fin surfaces. Four T-type thermocouples are embedded
along the central conduction axis beneath the surface. The holes are
approximately 0.9 mm in diameter and 5 mm deep; the thermocouple nearest the
surface is approximately 5.5 mm below the boiling interface, and the axial
spacing is 2.54 mm. The surface is horizontal and upward-facing.

The edge between the exposed copper surface and the PEEK top is sealed with a
high-temperature silicone inner layer and an epoxy outer layer. This seal both
limits leakage and reduces perimeter nucleation that would not be representative
of the intended test surface.

## Data Acquisition And Imaging

Temperature and pressure are recorded with a National Instruments cDAQ-9178
chassis. The thermocouples are wired through NI 9210 modules and logged at
3 Hz. The pressure transducer is logged through an NI 9239 module at 25 kHz and
uses a separate BK Precision excitation supply.

Two LabVIEW virtual instruments are used during tests:

- a custom facility VI that logs sensor data, displays real-time wall
  temperature and heat flux estimates, and writes `.lvm` files for
  post-processing; and
- a modified MagnaDC VI that controls and logs voltage, current, and input
  power.

High-speed visualization is performed through the side viewport with a Phantom
VEO 710L camera, a rectangular LED backlight, and a Nikon 60 mm macro lens. The
thesis protocol reports 300 frames/s at 512 x 512 pixels for the pressure/surface
matrix; retain the frame rate from the test log for each specific run because
some BoilingLab demo cases use different camera settings.

## Test Preparation

Use the `Test ID` as the primary identifier from the beginning of setup through
post-processing. The same ID should appear in the raw-data folder, the metadata
spreadsheet, generated summaries, and any manuscript analysis tables.

Before testing, prepare the surface:

1. For flat copper, wet-sand the surface from grit `#320` through `#2500`.
   Translate the surface in a straight line under light uniform pressure, rotate
   the block by 90 degrees between passes, and repeat to reduce directional
   scratches.
2. For microchannel and micro-pin-fin surfaces, avoid mechanical polishing so
   the microstructure dimensions are preserved.
3. Chemically rinse the surface with acetone, ethanol, isopropanol, and DI
   water.
4. After assembly, apply MAAS metal polish to the exposed copper using
   Kimwipes where appropriate.
5. Bolt the assembled HEE to the chamber base and allow the silicone and epoxy
   seal to cure overnight before filling.

Fill the chamber from the top with deionized water to about half the internal
height, giving roughly 70 mm of liquid above the copper surface. The fill level
should provide enough pool height above the heater while keeping the liquid
surface below the internal condenser coil during boiling.

Degas the liquid before each test. Heat the water near its atmospheric
saturation temperature with the immersion heaters and boil vigorously for
1 hour. Operate the Graham condenser during this period so vapor and gas mixture
leaving the pool are condensed or purged.

## Environmental Control

After degassing, adjust the immersion-heater power so the liquid and vapor
temperatures approach the saturation temperature for the selected pressure. The
defense presentation summarizes the control target as:

- vapor pressure within `+/- 0.5 kPa` of the setpoint, and
- liquid and vapor temperatures within `+/- 1 deg C` of the saturation
  temperature.

Pressure control is manual. Use the vacuum-pump valve and internal-condenser
coolant flow together. The control strategy is grouped by pressure range:

- low pressure: 10 to 30 kPa,
- medium pressure: 40 to 60 kPa, and
- high pressure: 70 to 100 kPa.

The reported pressure is vapor-space pressure measured near the top of the
vessel. The local heater pressure is slightly higher because of the liquid head
above the surface. For a 70 mm water column, the hydrostatic contribution is
less than 0.7 kPa. This is small compared with the total wall-superheat range
but most relevant at 10 kPa, where it can shift saturation temperature by about
1.3 deg C.

## Heat-Load Selection

The thesis used step heat-load tests. Before the main matrix, perform
preliminary tests for each pressure band and surface type to identify the
minimum heat load that can trigger CHF. The selected transient heat load should
be slightly above that threshold:

- if the heat load is too high, the measured CHF becomes strongly affected by
  transient thermal inertia;
- if the heat load is too low, CHF may not trigger during the run.

The defense deck notes that open-chamber atmospheric tests were used for initial
heat-load calibration. Chapter 3 then applies pressure-band-specific load
selection for flat copper, microchannel copper, and micro-pin-fin copper.

## Test Sequence

A typical transient pool-boiling run follows this sequence:

1. Verify the chamber seal, condenser flow path, vacuum connection, drain valve,
   immersion-heater state, DAQ channels, camera view, and light source.
2. Confirm the target pressure and saturation-temperature conditions.
3. Start LabVIEW logging for temperature and pressure.
4. Start MagnaDC logging and high-speed video capture.
5. Apply the selected step power to the cartridge heaters.
6. Monitor the real-time wall-temperature and heat-flux estimates in LabVIEW.
   These are especially important in low-pressure flat-copper tests, where the
   thermocouple temperature increase at CHF can be mild.
7. Identify the CHF trigger by the sharp heater-block temperature rise and
   accompanying wall-temperature or heat-flux signature.
8. Shut off the MagnaDC power supply at the CHF trigger.
9. Continue logging through transition boiling and the return to nucleate
   boiling during cooling.
10. End the run after the copper surface temperature approaches the saturation
    temperature.

The expected qualitative regime path is:

```text
ONB -> NB -> CHF -> TB -> NBR -> NB
```

where `ONB` is onset of nucleate boiling, `NB` is nucleate boiling, `CHF` is
critical heat flux, `TB` is transition boiling, and `NBR` is nucleate boiling
return.

## Raw Data And Metadata

BoilingLab assumes that large raw files remain outside git. For each test,
preserve at least:

- `Temperature.lvm`: embedded copper thermocouples plus liquid and vapor
  temperatures,
- `Pressure.lvm`: vessel pressure record,
- `DC_power.lvm`: MagnaDC voltage, current, and power log when available,
- high-speed video or selected frame exports when optical interpretation is
  needed, and
- metadata in `metadata/Pool Boiling Test Log.xlsx`.

The metadata row should record pressure target, surface type, liquid, date,
operator, chamber configuration, camera settings, resolution, frame rate, power
load, test status, and notes about anomalies such as missed CHF, leaks, sensor
dropout, or nonstandard heat-load selection.

## Quality Checks

At minimum, check these items before using a run for analysis:

- pressure remains near the setpoint for the active test interval;
- liquid and vapor temperatures remain near the pressure-dependent saturation
  temperature;
- `DC_power.lvm` is time-aligned with `Temperature.lvm`;
- the thermocouple linear fit gives a high `R2` during the main heating and
  event windows;
- high-speed video covers the surface and captures ONB, CHF/transition, and NBR
  when optical interpretation is required;
- the test status in the metadata agrees with how `CHF`, `NBR`, and any proxy
  markers are interpreted; and
- structured-surface temperatures are treated as base-temperature metrics, not
  local fin-tip, sidewall, or microlayer temperatures.
