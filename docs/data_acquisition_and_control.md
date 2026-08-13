# Data Acquisition and Control Workflow

This page documents the data-acquisition and control workflow reported for the
subatmospheric pool-boiling experiments. It makes the interface between the
physical facility and BoilingLab's analysis code explicit. It is not an
electrical drawing, a safety procedure, or an executable replacement for the
original LabVIEW VIs.

## Evidence and Scope

The following configuration is **reported** from Chapter 2 of Ishraq Hossain's
MSME thesis (PDF pages 11--12) and the experimental-setup and environmental-
control slides in the supplied defense presentation. The original custom
facility LabVIEW VI and modified MagnaDC VI were not found in this repository;
therefore, their source code, channel configuration, scaling equations,
calibration records, timing implementation, and safety interlocks are not
released or independently verified here.

## Acquisition Channels and Outputs

| Measurement or output | Reported hardware and rate | Intended recorded product |
| --- | --- | --- |
| Copper-block, liquid, and vapor temperatures | NI cDAQ-9178 chassis with NI 9210 thermocouple modules; 3 Hz | `Temperature.lvm` |
| Vapor-space pressure | DwyerOmega PX409-030A5V, externally excited by a BK Precision 1550 supply; NI 9239; 25 kHz | `Pressure.lvm` |
| DC heater voltage, current, and input power | MagnaDC SL200-7.5/UI+LXI programmable DC supply, controlled/logged by a modified OEM VI | `DC_power.lvm` when available |
| Side-view visualization | Phantom VEO 710L, Nikon 60 mm macro lens, rectangular LED backlight; thesis reports 150 or 300 frames/s at 512 x 512 pixels | High-speed video or selected frames |

The four embedded T-type thermocouples are used by downstream analysis to
estimate a one-dimensional copper-block temperature gradient. The lower and
upper vessel thermocouples represent the bulk-liquid and vapor-space
temperatures, respectively. The pressure instrument measures vapor-space
pressure near the top of the vessel; it is not a direct measurement of the
static pressure at the heater surface.

## Control Responsibilities

The experiment combined operator-adjusted environmental controls with software
logging and power-supply control:

1. The two 250 W immersion heaters, supplied through a VARIAC, conditioned the
   DI-water pool near the saturation temperature for the selected pressure.
2. A continuously running vacuum pump and the coolant-flow valve of the
   internal copper condenser were adjusted manually to regulate vapor pressure.
3. The custom facility VI acquired temperatures and pressure, displayed
   real-time reconstructed wall temperature and heat flux, and wrote sensor
   data to `.lvm` files.
4. The modified MagnaDC VI remotely set and logged the cartridge-heater
   voltage, current, and input power.
5. The test operator used the real-time thermal signatures to identify CHF and
   manually switched off the MagnaDC supply. This is an operator decision in
   the reported workflow, not a documented automatic trip.

The reported operating targets were vapor pressure within +/- 0.5 kPa of the
setpoint and bulk-liquid and vapor temperatures within +/- 1 deg C of the
pressure-dependent saturation temperature. These are experimental control
targets, not uncertainty statements or guarantees for every individual run.

## Run-Time Ordering and Event Handoff

The documented sequence is: establish the pressure and saturation condition;
start facility-DAQ logging; start DC-power logging and high-speed video; apply
the selected single-step heater power; identify CHF from the real-time thermal
response; turn off DC heater power; and continue recording through transition
boiling and nucleate-boiling return. The expected regime path is
`ONB -> NB -> CHF -> TB -> NBR -> NB`.

The facility VI's displayed wall-temperature and heat-flux estimates were
especially important for 10--30 kPa flat-copper tests, where the raw
thermocouple rise at CHF could be mild. The repository's analysis documentation
defines how thermal reconstruction and event markers are interpreted after
acquisition; it does not reproduce the LabVIEW real-time calculation.

## Data Handoff to BoilingLab

For each test, retain a common `Test ID` in the raw-data directory, the test
log, and generated outputs. The current scripts consume the recorded `.lvm`
products and metadata, then align the DC-power record to the temperature record
using the file start times. See [data reduction](data_reduction.md) for those
post-processing assumptions and checks.

Before treating two streams as synchronized, verify their start times, time
bases, channel identities, units, and any dropped or restarted acquisition.
The thesis materials do not establish a hardware trigger, clock-drift budget,
or video-to-DAQ synchronization method; those remain required metadata for a
future reproducible acquisition-code release.

## What Is Released and What Remains Needed

Released in BoilingLab:

- analysis scripts and notebooks that read the acquired products;
- a metadata log and documented file roles; and
- the facility and procedure descriptions in this documentation set.

Not presently released or verified in this checkout:

- the LabVIEW VI source or compiled executable;
- cDAQ task/channel configuration, pressure-voltage scaling, and calibration
  records;
- MagnaDC VI source, command interface, and electrical protection logic; and
- automated synchronization, CHF detection, or shutdown control code.

Any future control-code release should include an I/O map with units and safe
states, versioned LabVIEW project files/dependencies, a simulator or dry-run
mode, calibration/scaling provenance, sample `.lvm` outputs, a defined
operator-to-automatic-trip authority boundary, and a testable timebase/
synchronization specification.
