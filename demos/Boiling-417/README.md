# Boiling-417 Demo Case

This demo uses `Boiling-417` as a single-case example for
`notebooks/Single_case_analysis_Subcooled.ipynb`.

## Inputs

- Test ID: `Boiling-417`
- Raw data folder: `Y:\0_Ishraq\New Pool Boiling Video\Boiling-417`
- Liquid subcooling input: `57.6 °C`
- Applied heat-load input: `250 W/cm^2`
- Test-log status: `Failure: CHF not reached`
- Test-log context: transient, open to atmosphere, DI water, flat Cu surface,
  VEO 710 camera, 600 fps, 512 x 512 resolution.

## Run Notes

The notebook currently contains interactive `raise Exception` checkpoints and
animation/video cells. For this demo run, the static analysis cells were run
with the checkpoint cells skipped and the animation cells omitted.

The reproducible lightweight demo runner is:

```powershell
python scripts\run_single_case_demo.py
```

That command writes generated outputs to `demos\Boiling-417\generated`,
including hydrophone and acoustic-emission plots when those raw files are
present. The hydrophone scalar plot uses the PSD integrated over frequency,
reported as a band-limited voltage-squared acoustic-power proxy. Use
`--skip-sensors` for a faster thermal-only run.

The notebook's current heat-flux marker logic searches for a maximum in a fixed
time window and labels the result as `CHF`. Because the test log marks
`Boiling-417` as `Failure: CHF not reached`, the `CHF` value reported below
should be interpreted as the notebook's current marker/proxy, not as a confirmed
physical CHF event.

## Key Results

| Quantity | Value |
| --- | ---: |
| Duration | `988.9 s` |
| Mean pressure | `97.51 kPa` |
| Pressure standard deviation | `0.058 kPa` |
| RMSE vs. 97.7 kPa target | `0.197 kPa` |
| Saturation temperature from mean pressure | `98.903 °C` |
| Mean vapour temperature | `49.93 °C` |
| Mean liquid temperature | `57.60 °C` |
| Maximum surface temperature | `172.87 °C at 132.40 s` |
| Maximum heat flux | `277.96 W/cm^2 at 608.40 s` |
| Notebook CHF proxy | `177.26 W/cm^2 at 100.00 s` |
| HTC at notebook CHF proxy | `5.487 W/cm^2-K` |
| NBR marker | `277.96 W/cm^2 at 608.40 s` |
| Minimum heat flux between proxy CHF and NBR | `131.81 W/cm^2 at 132.00 s` |
| Mean R2 of linear temperature fit | `0.9943` |
| Minimum R2 of linear temperature fit | `0.8042` |
| MagnaDC start | `5.228 s`, surface temperature `67.33 °C` |
| MagnaDC shutoff | `673.893 s`, surface temperature `130.90 °C` |

The full CSV export from the notebook was written to:

```text
Y:\0_Ishraq\New Pool Boiling Video\Boiling-417\Boiling-417_csv_data.csv
```

## Representative Plots

- [Temperature profile](plots/temperature_profile.png)
- [Surface temperature](plots/surface_temperature.png)
- [Heat flux vs. time](plots/heat_flux_vs_time.png)
- [Pressure profile](plots/pressure_profile.png)
- [MagnaDC profile](plots/magnadc_profile.png)
- [Hydrophone spectrogram](plots/hydrophone_spectrogram.png)

Regenerated script outputs include:

- `generated/plots/hydrophone_raw.png`
- `generated/plots/hydrophone_spectrogram.png`
- `generated/plots/hydrophone_band_integrated_power.png`
- `generated/plots/ae_hit_parameters.png`
- `generated/plots/ae_time_parameters.png`
