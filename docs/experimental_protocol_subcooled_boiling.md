
# Experimental Protocol: Subcooled Pool Boiling

These notes summarize the modifications to the existing pool-boiling procedure for subcooled pool-boiling experiments on a flat copper surface. General facility descriptions, instrumentation, surface preparation, data acquisition, and other procedures are documented in the [Subatmospheric Pool Boiling](experimental_protocol.md) protocol. This document focuses on environmental control and the modified test sequence for subcooled pool boiling. It is not a standalone laboratory safety SOP.

## Scope

This procedure applies to transient pool-boiling experiments using a flat copper surface under open-atmosphere conditions. The primary modification from the existing saturated pool-boiling procedure is the establishment and maintenance of a prescribed bulk-liquid subcooling level before and during the experiment.

## Test Surface

The subcooled pool-boiling experiments described here use the flat copper surface. Follow the surface preparation, assembly, sealing, and instrumentation procedures documented in the existing [Subatmospheric Pool Boiling](experimental_protocol.md) protocol.

## Environmental Control

After degassing the DI water, establish the desired bulk-liquid subcooling condition before starting the boiling experiment.

1. Confirm that the chamber is operating under open-atmosphere conditions and verify the measured chamber pressure.

2. Monitor the bulk-liquid temperature using the liquid thermocouple.

3. Adjust the immersion-heater input through the VARIAC and the chiller-water flow through the internal coiled condenser to bring the bulk-liquid temperature to the desired subcooling level. During the subcooled boiling experiment, route the chiller flow through the internal coiled condenser rather than the Graham condenser, following the approved laboratory configuration.

4. Calculate the degree of liquid subcooling using the measured pressure and bulk-liquid temperature:

   `Subcooling (K) = Saturation temperature at measured pressure (deg C) - Bulk-liquid temperature (deg C)`

   where the saturation temperature is determined from the measured chamber pressure and the bulk-liquid temperature is measured using the liquid thermocouple.

5. Tune the VARIAC setting and chiller-water flow until the bulk-liquid temperature reaches the desired subcooling level and becomes sufficiently stable for the test.

6. Monitor and record the bulk-liquid temperature and chamber pressure throughout the experiment to track changes in the subcooling condition.

The target subcooling level, initial bulk-liquid temperature, measured pressure, VARIAC setting, and condenser configuration should be recorded in the experimental metadata.

A PID (proportional-integral-derivative) controller is currently under development to replace manual VARIAC adjustment and provide more precise and stable control of the bulk-liquid temperature and desired subcooling level during experiments. Until the controller is implemented and validated, the existing manual control procedure will be used according to the approved laboratory operating procedure.

## Test Sequence

A typical transient subcooled pool-boiling run follows this sequence:

1. Verify the chamber seal, condenser flow path, vacuum connection, drain valve, immersion-heater state, DAQ channels, camera view, and light source.

2. Confirm the liquid subcooling and pressure conditions. Verify the bulk-liquid temperature and measured chamber pressure before starting the experiment. Confirm that the chiller flow is routed through the internal coiled condenser and that the bulk-liquid temperature is at the desired subcooling level.

3. Start LabVIEW logging for temperature and pressure.

4. Start MagnaDC logging and high-speed video capture.

5. Adjust the immersion-heater input through the VARIAC as needed to help maintain the desired bulk-liquid temperature and subcooling condition during the experiment. Monitor the bulk-liquid temperature and measured chamber pressure while making adjustments.

6. Apply the selected step power to the cartridge heaters.

7. Monitor the real-time wall-temperature and heat-flux estimates in LabVIEW. These signals help identify changes in boiling behavior, including sustained thermal oscillations and CHF.

8. Identify the observed boiling behavior from the temperature and heat-flux signals. Depending on the degree of subcooling and applied heat load, the response may include sustained thermal oscillations or a CHF event.

9. If CHF is identified, shut off the MagnaDC power supply according to the established experimental procedure.

10. Continue logging the temperature and pressure signals during the subsequent cooling period.

11. For lower heat loads that approach steady-state conditions without a clear CHF event, continue recording the temperature response according to the planned test duration and laboratory procedure.

The expected qualitative regime paths observed in the current experiments are:

```text
Moderate subcooling (approximately 45-50 K), higher heat load:
ONB -> NB -> Sustained thermal oscillations

Higher subcooling (approximately 75 K), higher heat load:
ONB -> NB -> CHF

Lower heat load:
ONB -> NB -> Steady state
```

where `ONB` is onset of nucleate boiling, `NB` is nucleate boiling, and `CHF` is critical heat flux. Sustained thermal oscillations are documented separately and should not automatically be classified as NBR. These paths represent observed behavior under the tested conditions rather than universal boiling-regime sequences.

## Raw Data And Metadata

Follow the raw-data storage and metadata procedures documented in the existing [Subatmospheric Pool Boiling](experimental_protocol.md) protocol.

For each subcooled test, ensure that the metadata includes:

- Test ID and flat copper surface identification.
- Target and initial measured liquid subcooling.
- Bulk-liquid temperature and measured chamber pressure.
- Applied heat load.
- VARIAC setting and chiller-water flow configuration.
- Condenser path used during the experiment.
- Any VARIAC adjustments made during the run and the corresponding bulk-liquid temperature changes.
- Observed boiling behavior, including sustained thermal oscillations, CHF, steady-state conditions, and whether NBR was observed.
- Any deviations from the planned experimental conditions.

## Quality Checks

Before using a run for analysis, verify that:

- The measured chamber pressure and bulk-liquid temperature are available throughout the relevant test interval.
- The initial liquid subcooling is calculated using the measured pressure and liquid temperature.
- The subcooling condition is documented throughout the experiment rather than assumed to remain constant.
- Temperature and DC-power records are time-aligned.
- The observed boiling behavior is supported by the temperature and heat-flux signals.
- CHF are identified only when supported by the experimental evidence.
- The metadata accurately reflects the condenser configuration, heat load, VARIAC adjustments, and observed temperature response.
