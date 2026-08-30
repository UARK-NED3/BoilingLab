# LabVIEW

LabVIEW is used in our boiling experiment for data acquisition and monitoring of pressure and temperature through the NI DAQ system.

## Hardware Check

Before starting the LabVIEW setup:

1. Check the NI-DAQmx driver  to make sure everything is connected to the tested ports.
2. Check the power source connection to the sensor.

## Initial Setup

### Training Video

The training video is provided to familiarize yourself with the LabVIEW user interface and the initial testing setup. Watch the video first to understand the initial setup and operation.

```text
Training_Video/Thermocouple_LabVIEW_Ishraq_recording.mkv
```

### Demo Setup

A demo LabVIEW setup has been prepared to familiarize yourself with the user interface and to build and test the initial setup.

```text
Demo_Setup/final temp pressure rec.vi
```

### Pressure Calibration

In case of a convertible variable such as pressure, use the calibration data provided in the sensor user manual and plot the calibration data in Excel to obtain the calibration curve/coordinates. Use the obtained calibration values in LabVIEW.

```text
Pressure_calibration/
```

## Script

After obtaining the data file, you can use this Python script to process the data and generate the output graph.

```text
Script/Pressure Temp.py
```

## Output

The output folder contains the graphs generated from the experimental data after processing.

```text
Output/pressure_vs_time.png
Output/temperature_distribution.png
```

## File Types

- `.py` — Python script
- `.vi` — LabVIEW Virtual Instrument
- `.xlsx` — Excel calibration/data file
- `.mp4` — Training video
- `.png` — Output graph