# Multimodal clock-time alignment

`scripts/run_single_case_demo.py` uses `Temperature.lvm` as the reference time
axis. Temperature sample time `t = 0 s` remains exactly `t = 0 s`. For each
other modality, the runner reads its acquisition clock and applies

\[
t_{\mathrm{reference}} = t_{\mathrm{source}} +
  (t_{\mathrm{source,start,clock}} - t_{\mathrm{temperature,start,clock}}).
\]

LVM header clocks are used for pressure, DC power, and hydrophone data. The
EasyAE DTA header is used for AE hit/time parameters. A `STREAMYYYYMMDD-HHMMSS-mmm`
waveform filename is used for WFS data when present. The output
`time_alignment.json` records the raw and applied offset, source/reference
clock, method, and a status for every modality.

The default tolerance is 1 ms. A recorded offset whose magnitude is no greater
than that tolerance is set to zero and remains visible as `raw_offset_s`. Use
`--clock-offset-tolerance-s` to change this convention.

This is a clock-offset correction only. It does not estimate clock drift,
trigger latency, sensor response delay, spatial registration, or synchronization
uncertainty. A missing or unparseable source clock is retained as an explicit
non-aligned status rather than guessed.

## Derived-data exports

Each run writes the following non-raw artifacts into its output directory:

- `thermal_timeseries.csv`: temperature-reference time, four block
  thermocouples, reconstructed surface temperature, heat flux, linear-fit R2,
  saturation temperature, wall superheat, HTC, an explicit
  `htc_valid_for_positive_wall_superheat` flag, and pressure/DC traces
  interpolated onto the temperature grid without extrapolation;
- `thermal_timeseries.npz`: the same numeric arrays for direct Python loading;
- `critical_events.csv`: algorithmic event times on the temperature reference
  axis; and
- `time_alignment.json`: the synchronization record.

`chf_proxy` is a fixed-window heat-flux marker. It is emitted with
`not_confirmed` status unless the analyst deliberately supplies
`--chf-event-status confirmed_by_user`. It is not automatically a confirmed
critical-heat-flux event.
