# Time-Resolved Thermal and Acoustic Diagnostics of Microbubble Emission Boiling Under Subcooled Pool Boiling Conditions

**Draft status:** workspace manuscript draft, June 12, 2026  
**Target article type:** journal article / experimental methods and results  
**Candidate journals:** International Journal of Heat and Mass Transfer; Experimental Thermal and Fluid Science; International Communications in Heat and Mass Transfer  
**Corresponding data/code repositories:** `UARK-NED3/BoilingLab` and `hanhuark/literature-compiler`

Unless otherwise noted, BoilingLab figure and data paths are relative to the BoilingLab repository root. Literature-compilation paths refer to the sibling `literature-compiler` repository in the same workspace.

## Abstract

Microbubble emission boiling (MEB) can sustain heat fluxes beyond conventional boiling limits under highly subcooled conditions, but its onset and development remain difficult to diagnose because heat transfer, vapor-interface motion, and acoustic emission are strongly coupled. This study develops a reproducible thermal-acoustic analysis workflow for subcooled pool boiling experiments and applies it to four flat-copper tests, Boiling-412, Boiling-413, Boiling-416, and Boiling-417, conducted near 97-98 kPa with imposed electrical power levels of approximately 150-250 W. The workflow synchronizes wall-temperature extrapolation, heat-flux reconstruction, power-load timing, hydrophone spectrograms, band-integrated acoustic power, acoustic characteristic frequencies, and acoustic-emission waveform analysis where available. The boiling-curve comparison shows that the maximum reconstructed heat flux increases from 142 W/cm^2 in Boiling-412 to 278 W/cm^2 in Boiling-417, while the high-power cases exhibit persistent thermal and acoustic oscillations during the active-heating period. Event markers identify the DNB-associated heat-flux drop, the wall-temperature peak, the first oscillation peak, and power shutoff. In Boiling-416 and Boiling-417, hydrophone and AE waveform analyses show matching low-frequency envelope modulation, approximately 0.05 Hz and 0.08 Hz, respectively, while literature-reported bubble and sound carrier frequencies typically lie from tens of Hz to several kHz. A Hilbert-envelope analysis fitted with a first-order asymptotic growth model shows that thermal oscillation amplitudes in Boiling-416 approach saturation faster, with time constants of 103-106 s and saturation fractions near 97%, whereas Boiling-417 develops more slowly, with time constants of 239-248 s and saturation fractions of 77-78% before power shutoff. The acoustic power envelopes grow less consistently than the thermal envelopes, indicating that acoustic bursts contain intermittent collapse dynamics in addition to the slowly developing MEB oscillation amplitude. These results position multimodal time-resolved diagnostics as a practical route for identifying MEB development and for connecting laboratory boiling signatures to the broader MEB literature.

**Keywords:** microbubble emission boiling; subcooled pool boiling; hydrophone; acoustic emission; heat flux; oscillation envelope; boiling sound; wall temperature

## Nomenclature

| Symbol | Definition | Unit |
| --- | --- | --- |
| `A` | oscillation envelope amplitude | signal-dependent |
| `A_0` | fitted envelope amplitude at `t_osc` | signal-dependent |
| `A_inf` | fitted asymptotic envelope amplitude | signal-dependent |
| `f` | frequency | Hz |
| `P_load` | electrical power load | W |
| `q''` | heat flux | W/cm^2 |
| `T` | temperature | degC |
| `T_sat` | saturation temperature | degC |
| `T_w` | extrapolated wall temperature | degC |
| `t_DNB` | heat-flux maximum before the DNB-associated drop | s |
| `t_off` | time when DC power load is turned off | s |
| `t_osc` | first wall-temperature oscillation peak in the MEB analysis window | s |
| `t_peak` | wall-temperature peak during the transition event | s |
| `tau` | asymptotic envelope growth time constant | s |

## 1. Introduction

High-heat-flux cooling increasingly requires boiling regimes that remain effective near or beyond the conventional critical heat-flux limit. Microbubble emission boiling is one such regime. In MEB, vapor structures near the heated surface repeatedly grow, condense, collapse, and emit fine bubbles into subcooled liquid. These dynamics can maintain intense liquid-vapor interaction near the wall and support heat fluxes that exceed conventional nucleate-boiling limits. The same dynamics also make MEB difficult to identify from a single measurement channel. A boiling curve can show enhanced heat transfer or hysteresis, but it does not directly reveal whether the regime is sustained by bubble collapse, liquid replenishment, pressure fluctuations, acoustic emission, or some combination of these processes.

Prior MEB studies have established several pieces of the physical picture. Zeigarnik et al. [zeigarnik_2012_microbubble_emission_nature] reviewed microbubble emission under highly subcooled boiling and discussed high heat-flow regimes in which fine bubbles are emitted near the surface. Visual studies by Zhu et al. [zhu_2014_visualized_meb] and Tang et al. [tang_2016_transition_to_meb] showed that the transition from nucleate boiling to MEB involves rapid vapor-bubble collapse and microbubble generation. Horiuchi et al. [horiuchi_2021_spatial_temporal_thermal_fluid] connected spatially nonuniform surface temperature, heat-transfer behavior, and boiling sound in distinct MEB states. Tang et al. [tang_2023_bubble_induced_oscillating_flow] further demonstrated that bubble-induced oscillating liquid flow can contribute directly to MEB heat transfer. These studies collectively indicate that MEB is not just a point on a boiling curve; it is a coupled thermal-fluid oscillatory state.

Acoustic diagnostics provide an additional way to observe this coupled state. Boiling sound and acoustic-emission methods have been used to distinguish boiling regimes, detect transition boiling, and classify MEB-like states. Zhou et al. [zhou_2018_sound_emission_subcooled_pool] reported sound-emission changes in subcooled pool boiling on a small heater, including spectral peaks associated with MEB. Ono et al. [ono_2023_acoustic_state_detection_meb] used hydrophone data and cepstrum-based deep learning to detect MEB acoustic states. Sinha et al. [sinha_2021_deep_learning_sound_boiling] showed that acoustic signatures can predict boiling crisis in water on copper surfaces. These works show that acoustic signals contain regime information, but the relationship between acoustic power, characteristic frequency, wall temperature, and reconstructed heat flux remains underdeveloped for transient MEB development.

The remaining gap is therefore not simply the absence of MEB observations. The gap is the lack of a compact, reproducible framework that synchronizes thermal and acoustic measurements to quantify how an MEB-like oscillatory state develops in time. Most literature values report onset conditions, heat flux, wall superheat, bubble/sound frequency, or visual behavior for selected steady or quasi-steady states. Fewer studies report the time evolution of oscillation amplitude across thermal and acoustic channels during active heating. This is especially important when the number of available tests is limited: a small dataset can still be scientifically useful if it provides synchronized measurements that prior studies did not collect together.

The present work addresses this gap by developing and applying a multimodal analysis workflow to four subcooled pool-boiling tests on flat copper. The work makes four contributions. First, it defines reproducible event markers from the thermal and power-load data: `t_DNB`, `t_peak`, `t_osc`, and `t_off`. Second, it compares heating-only boiling curves for Boiling-412, Boiling-413, Boiling-416, and Boiling-417. Third, it analyzes hydrophone and AE waveform data for developed cases using spectrograms, band-integrated power, characteristic frequency, and power-frequency alignment. Fourth, it quantifies MEB oscillation-amplitude growth with an asymptotic envelope model and positions the local data against a first-pass MEB literature compilation in `literature-compiler/test2_meb`.

## 2. Experimental Data and Analysis Workflow

### 2.1 BoilingLab test cases

The primary experimental dataset consists of four subcooled pool-boiling cases labeled by test ID: Boiling-412, Boiling-413, Boiling-416, and Boiling-417. The raw data folders are organized by test ID under `Y:\0_Ishraq\New Pool Boiling Video`, and metadata are linked through the Pool Boiling Test Log. The tests were conducted near atmospheric pressure on a flat copper surface with water as the working fluid. The four cases form a first heat-load sweep, with mean DC power during heating increasing from approximately 150 W to 248 W.

Table 1 summarizes the present test conditions and primary thermal outcomes. The multi-case values come from `demos/Boiling-412-413-416-417/generated/summary.csv`.

**Table 1. Summary of BoilingLab tests used in this draft.**

| Test ID | Applied power (W) | Mean pressure (kPa) | Mean liquid temperature (degC) | `T_sat` (degC) | Maximum `q''` (W/cm^2) | Maximum `T_w` (degC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Boiling-412 | 150 | 97.28 | 58.83 | 98.84 | 142.0 | 112.7 |
| Boiling-413 | 180 | 97.30 | 52.38 | 98.84 | 163.1 | 159.2 |
| Boiling-416 | 230 | 97.47 | 57.27 | 98.89 | 267.2 | 167.0 |
| Boiling-417 | 250 | 97.51 | 57.60 | 98.90 | 278.0 | 172.9 |

The comparison should be interpreted as a pilot dataset rather than a statistically complete parametric study. Boiling-412 and Boiling-413 provide lower-power reference cases. Boiling-416 and Boiling-417 provide the strongest evidence of developed coupled thermal-acoustic oscillations and have the richest acoustic analysis, including hydrophone and AE waveform results.

### 2.2 Thermal data reduction

The thermal analysis follows the reproducible `BoilingLab` single-case and multi-case scripts. Temperatures are read from the test LVM files, and the surface temperature is extrapolated from embedded thermocouple measurements using a one-dimensional conduction fit through the copper block. Heat flux is reconstructed from the temperature gradient and copper thermal conductivity. The multi-case boiling curves include only the heating portion of each test by retaining samples for which the aligned final column of `DC_power.lvm` is positive. The use of heating-only data is important because the cooling path after power shutoff would otherwise obscure the active-heating boiling curve.

For single-case plots, the analysis marks four event times. The DNB marker `t_DNB` is defined as the heat-flux maximum before the sudden heat-flux drop associated with departure from nucleate boiling. The marker `t_peak` is defined as the wall-temperature peak during the transition event. The marker `t_osc` is the first wall-temperature oscillation peak in the oscillatory MEB analysis window, currently searched from 300 s until the smaller of 700 s and `t_off`. Finally, `t_off` is the time at which the DC power load is turned off.

### 2.3 Hydrophone and AE signal processing

Hydrophone data are processed using spectrograms and power spectral density estimates. The band-integrated hydrophone power is computed by integrating the PSD over frequency in linear units, not by averaging dB values. This distinction matters because integration of PSD over a band produces a physically meaningful band-power proxy, whereas direct averaging of dB values does not preserve linear acoustic power. Characteristic acoustic frequencies are extracted from each spectrogram time bin as peak frequency, spectral centroid, and spectral bandwidth.

For Boiling-416 and Boiling-417, AE waveform files are processed with the same general strategy: a spectrogram is generated from the waveform stream, band-integrated AE power is computed, and characteristic frequencies are extracted. This permits comparison between the hydrophone, which senses pressure/acoustic waves in the liquid, and the AE sensor, which responds to elastic/acoustic activity transmitted through the solid structure and mounting path.

### 2.4 Oscillation envelope model

The MEB oscillation-amplitude analysis uses a Hilbert-transform envelope of detrended oscillatory signals. For each signal, the analysis selects the active MEB window, removes a slow baseline using a 75 s Savitzky-Golay smoother, computes the Hilbert envelope of the detrended signal, and smooths the envelope with a 35 s Savitzky-Golay smoother. The primary envelope fit is a first-order asymptotic growth model,

```text
A(t) = A_inf - (A_inf - A_0) exp(-(t - t_osc) / tau)
```

where `A_0` is the fitted envelope amplitude at `t_osc`, `A_inf` is the asymptotic envelope amplitude, and `tau` is the growth time constant. The fitted saturation fraction at the end of the window is defined as `(A_end - A_0)/(A_inf - A_0)`. A value near one indicates that the envelope is approaching its fitted asymptote within the observed window. A small value indicates that the model predicts continued growth beyond the observed window or that the signal is poorly represented by a single smooth saturation process.

### 2.5 Literature compilation

The literature context is organized in `hanhuark/literature-compiler` as `examples/test2_meb`. That case follows the literature-compiler workflow: define a quantitative question, register sources in `references/sources.yaml`, link case-specific source notes in `papers.yaml`, extract first-pass data into CSV files, and generate comparison plots. The current test2 compilation includes 23 MEB-related source records from the local Zotero-derived packet and separates two types of data. The first, `literature-compiler/examples/test2_meb/data/literature_points.csv`, contains first-pass reported-text values where both wall superheat and heat flux are available. The second, `literature-compiler/examples/test2_meb/data/meb_regime_signatures.csv`, records MEB-specific information that does not fit cleanly into a boiling-curve schema, including reported heat-flux ranges, frequency scale, acoustic sensor type, and notes.

The literature compilation is explicitly a screening dataset. Values marked as reported text or range endpoints should be checked against original figures and tables before final manuscript submission. Nevertheless, the compilation is useful because it clarifies which quantities should be extracted next: onset wall superheat, heat flux at MEB onset and stable MEB, subcooling, pressure, geometry, bubble/sound frequency, acoustic sensor bandwidth, and whether the reported frequency refers to bubble oscillation, boiling sound, pressure fluctuation, sampling rate, or slow envelope modulation.

## 3. Results and Discussion

### 3.1 Heating-only boiling curves show two lower-power reference cases and two high-power oscillatory cases

Figure 1 compares the heating portions of Boiling-412, Boiling-413, Boiling-416, and Boiling-417 as heat flux versus wall temperature and wall superheat. The maximum reconstructed heat flux increases from 142 W/cm^2 in Boiling-412 to 278 W/cm^2 in Boiling-417. The lower-power cases therefore provide a baseline for subcooled boiling without the strongest developed oscillatory behavior, while the higher-power cases enter a regime with large thermal oscillations and synchronized acoustic activity.

**Figure 1. Heating-only boiling curves.**  
Source plots:  
`demos/Boiling-412-413-416-417/generated/plots/heat_flux_vs_wall_temperature.png`  
`demos/Boiling-412-413-416-417/generated/plots/heat_flux_vs_wall_superheat.png`

The most important trend is not only that the high-power cases reach higher heat flux. Boiling-416 and Boiling-417 also show time-dependent oscillatory signatures after the transition event. This distinguishes them from a simple monotonic boiling-curve comparison. A conventional boiling curve compresses the time history into a trajectory in `q''-T_w` space, but the MEB-like state is better understood as an evolving oscillatory process during active heating.

### 3.2 Event markers separate DNB, transition temperature peak, oscillation onset, and power shutoff

Figures 2 and 3 show representative thermal time histories for Boiling-416 and Boiling-417 with the event markers `t_DNB`, `t_peak`, `t_osc`, and `t_off`. In Boiling-417, `t_DNB = 124.8 s`, `t_peak = 132.4 s`, `t_osc = 308.0 s`, and `t_off = 673.9 s`. In Boiling-416, `t_DNB = 150.8 s`, `t_peak = 160.8 s`, `t_osc = 321.6 s`, and `t_off = 757.8 s`.

**Figure 2. Boiling-417 heat flux and temperature time histories with event markers.**  
Source plots:  
`demos/Boiling-417/generated/plots/heat_flux_vs_time.png`  
`demos/Boiling-417/generated/plots/surface_temperature.png`

**Figure 3. Boiling-416 heat flux and temperature time histories with event markers.**  
Source plots:  
`demos/Boiling-416/generated/plots/heat_flux_vs_time.png`  
`demos/Boiling-416/generated/plots/surface_temperature.png`

The event sequence supports a two-stage interpretation. The early transition event, marked by the heat-flux drop and wall-temperature peak, reflects the departure from the preceding nucleate-boiling-like path. The later `t_osc` marker identifies the first peak of the sustained oscillatory region used for envelope analysis. This separation matters because the thermal peak near DNB and the later MEB oscillation are different diagnostic events. Treating them as one event would mix the transition into the subsequent oscillatory state.

### 3.3 Hydrophone and AE measurements identify low-frequency modulation of the developed MEB state

Hydrophone spectrograms and band-integrated power traces show strong oscillatory activity during the MEB-like interval. In Boiling-416, the dominant low-frequency hydrophone modulation is approximately 0.05 Hz, corresponding to a period of about 20 s. In Boiling-417, it is approximately 0.08 Hz, corresponding to a period of about 12.5 s. AE waveform analysis gives consistent low-frequency modulation for the same two cases: approximately 0.055 Hz for Boiling-416 and 0.080 Hz for Boiling-417.

**Figure 4. Hydrophone spectrograms and integrated power/characteristic-frequency diagnostics.**  
Representative source plots:  
`demos/Boiling-417/generated/plots/hydrophone_spectrogram.png`  
`demos/Boiling-417/generated/plots/hydrophone_band_integrated_power.png`  
`demos/Boiling-417/generated/plots/hydrophone_characteristic_frequencies.png`  
`demos/Boiling-416/generated/plots/hydrophone_spectrogram.png`  
`demos/Boiling-416/generated/plots/hydrophone_band_integrated_power.png`  
`demos/Boiling-416/generated/plots/hydrophone_characteristic_frequencies.png`

**Figure 5. AE spectrograms and AE integrated power/characteristic-frequency diagnostics.**  
Representative source plots:  
`demos/Boiling-417/generated/plots/ae_wfs_spectrogram.png`  
`demos/Boiling-417/generated/plots/ae_wfs_band_integrated_power.png`  
`demos/Boiling-417/generated/plots/ae_wfs_characteristic_frequencies.png`  
`demos/Boiling-416/generated/plots/ae_wfs_spectrogram.png`  
`demos/Boiling-416/generated/plots/ae_wfs_band_integrated_power.png`  
`demos/Boiling-416/generated/plots/ae_wfs_characteristic_frequencies.png`

The low-frequency values reported here should not be interpreted as direct bubble-collapse frequencies. They describe slow modulation of acoustic power and thermal oscillation amplitude over the active MEB interval. In contrast, many MEB studies report bubble oscillation, sound, or pressure spectral features from tens of Hz to several kHz. For example, Tang et al. [tang_2016_transition_to_meb] reported repetitive vapor-bubble collapse on the order of 800-2000 Hz, Zhu et al. [zhu_2014_visualized_meb] reported a boiling-sound peak around 2700 Hz, and Horiuchi et al. [horiuchi_2021_spatial_temporal_thermal_fluid] reported boiling-sound fundamental frequencies that shift across MEB states. The present data therefore add a slower envelope-scale diagnostic rather than contradicting the high-frequency literature.

### 3.4 Thermal oscillation envelopes grow toward saturation, but acoustic power remains more intermittent

Figure 6 shows the MEB envelope analysis for Boiling-416 and Boiling-417. The thermal envelopes are fitted well by the asymptotic growth model, whereas the hydrophone power envelope is more intermittent and less consistently represented by a single saturation curve.

**Figure 6. MEB oscillation envelope analysis.**  
Source plots:  
`demos/Boiling-416/generated/plots/meb_envelope_analysis.png`  
`demos/Boiling-417/generated/plots/meb_envelope_analysis.png`  
`demos/Boiling-416/generated/plots/meb_normalized_envelope_comparison.png`  
`demos/Boiling-417/generated/plots/meb_normalized_envelope_comparison.png`

**Table 2. Asymptotic envelope metrics for Boiling-416 and Boiling-417.**

| Case | Signal | Percent change (%) | `tau` (s) | Saturation fraction at window end | R^2 |
| --- | --- | ---: | ---: | ---: | ---: |
| Boiling-416 | `T_w` | 2042 | 103.4 | 0.974 | 0.970 |
| Boiling-416 | `q''` | 1531 | 105.8 | 0.972 | 0.963 |
| Boiling-416 | Hydrophone power | 313 | 769.9 | 0.388 | 0.848 |
| Boiling-417 | `T_w` | 167 | 239.1 | 0.783 | 0.935 |
| Boiling-417 | `q''` | 150 | 247.8 | 0.771 | 0.938 |
| Boiling-417 | Hydrophone power | 140 | 7308.8 | 0.049 | 0.588 |

Boiling-416 approaches its fitted thermal asymptote more quickly than Boiling-417. The `T_w` and `q''` time constants in Boiling-416 are 103-106 s, and the saturation fractions are approximately 97% by the end of the analysis window. In Boiling-417, the corresponding thermal time constants are 239-248 s and the saturation fractions are 77-78% before power shutoff. This indicates that Boiling-417 is still developing toward a saturated thermal oscillation amplitude when heating ends.

The acoustic power envelopes behave differently. Boiling-416 hydrophone power has a time constant of approximately 770 s and a saturation fraction of 39%, while Boiling-417 hydrophone power has a very long fitted time constant and a low R^2. This does not mean the acoustic signal is unimportant. Rather, it indicates that a single smooth growth-to-asymptote model is incomplete for acoustic power. The hydrophone signal is sensitive to intermittent collapses, sensor-band coupling, and burst-like events that can be synchronized with but not identical to the wall thermal envelope.

### 3.5 Literature comparison positions the local data as a transient diagnostics dataset

Figure 7 compares the local data with the first-pass `test2_meb` literature compilation. The literature includes high-heat-flux MEB demonstrations, reduced-pressure confined boiling, open microchannel MEB, visualized MEB transitions, and acoustic state-detection studies. Reported literature heat-flux scales span a wide range, from approximately 140-320 W/cm^2 in some reduced-pressure or open-microchannel comparisons to much higher values in specialized MEB or droplet/cavitation contexts.

**Figure 7. First-pass MEB literature compilation and BoilingLab comparison.**  
Source plots:  
`literature-compiler/examples/test2_meb/summary/test2_meb_boiling_curve_comparison.png`  
`literature-compiler/examples/test2_meb/summary/test2_meb_signature_summary.png`

The comparison clarifies the role of the present dataset. Boiling-416 and Boiling-417 do not currently represent record-setting MEB heat fluxes relative to the highest values reported in the literature. Instead, they provide synchronized thermal, hydrophone, and AE measurements during an evolving MEB-like state. This is the key manuscript positioning. The novelty is not maximum heat flux alone. The novelty is the ability to define event times, track amplitude growth, compare thermal and acoustic envelopes, and distinguish slow envelope modulation from higher-frequency bubble or sound carrier dynamics.

### 3.6 Physical interpretation

The synchronized increase in thermal oscillation amplitude and acoustic activity suggests that the MEB-like regime develops through progressive strengthening of vapor growth, collapse, and near-wall liquid replenishment. After the transition event, vapor structures near the wall likely become more spatially and temporally organized. Their repeated collapse draws or drives subcooled liquid toward the heated surface, increasing heat-transfer excursions while also producing acoustic bursts. As the regime develops, the thermal oscillation amplitude approaches a dynamic balance controlled by applied heat input, vapor generation, condensation, and liquid replenishment.

The difference between thermal and acoustic envelope behavior is physically plausible. Wall temperature and heat flux are spatially and temporally filtered by conduction through the copper block and by the thermocouple response. These quantities are therefore well suited to reveal the slow growth of the regime-scale oscillation amplitude. Hydrophone and AE signals respond more directly to impulsive collapse, pressure waves, structural transmission, and sensor bandwidth. They can show the same slow modulation while retaining intermittent bursts and high-frequency content. This explains why the thermal envelopes are well represented by the asymptotic growth model, while hydrophone power requires additional burst statistics or frequency-resolved metrics for a complete description.

## 4. Limitations

The present draft should be interpreted as a strong pilot manuscript rather than a final statistically complete study. Four tests are not enough to establish universal scaling laws for MEB onset or saturation. Boiling-412 currently contributes through the multi-case heating-only comparison but does not yet have the same complete single-case summary and acoustic/envelope analysis as Boiling-416 and Boiling-417. AE waveform analysis is currently available for the two developed high-power cases, not all four tests. The literature compilation is a first-pass screening dataset and includes reported-text values and range endpoints that require figure-level validation before final submission.

Several measurement limitations should also be addressed before journal submission. Thermocouple-based wall-temperature extrapolation filters high-frequency surface fluctuations, so the thermal oscillation metrics represent low-frequency or filtered MEB development rather than true instantaneous surface-temperature oscillations. Acoustic power is reported as a band-integrated voltage-squared proxy, not calibrated acoustic pressure or sound power. Sensor frequency response, hydrophone placement, AE coupling, and acquisition bandwidth should be documented in the final methods section. Heat losses, uncertainty propagation, and repeatability should also be quantified.

## 5. Conclusions

This work develops a reproducible multimodal workflow for diagnosing MEB-like development in subcooled pool boiling. The main conclusions are:

1. Heating-only boiling curves show a clear progression with applied power: maximum reconstructed heat flux increases from 142 W/cm^2 in Boiling-412 to 278 W/cm^2 in Boiling-417.

2. Boiling-416 and Boiling-417 exhibit persistent thermal-acoustic oscillations after the transition event. The key event markers are `t_DNB`, `t_peak`, `t_osc`, and `t_off`, which separate the early heat-flux/temperature transition from the later oscillatory MEB-like state.

3. Hydrophone and AE waveform analyses give consistent low-frequency modulation for the developed cases: approximately 0.05-0.055 Hz for Boiling-416 and 0.08 Hz for Boiling-417. These values are envelope-scale modulation frequencies, not direct bubble-collapse or boiling-sound carrier frequencies.

4. Thermal oscillation envelopes are well represented by a first-order asymptotic growth model. Boiling-416 approaches saturation faster (`tau = 103-106 s`, saturation fraction near 97%) than Boiling-417 (`tau = 239-248 s`, saturation fraction near 77-78% before shutoff).

5. Hydrophone power envelopes grow but are more intermittent than the thermal envelopes. This suggests that acoustic power contains burst-like collapse dynamics in addition to the slow development of the MEB thermal oscillation.

6. The first-pass literature compilation indicates that the present dataset should be positioned as a time-resolved multimodal diagnostics study, not as a record-heat-flux study. Its value is the synchronized thermal, hydrophone, and AE view of MEB development.

## 6. Recommended Work Before Submission

1. Complete single-case analysis for Boiling-412 with the same eight-figure output used for Boiling-416 and Boiling-417.
2. Run AE waveform analysis for Boiling-412 and Boiling-413 if waveform files are available.
3. Add uncertainty propagation for wall temperature, heat flux, acoustic band power, event times, and envelope fit parameters.
4. Digitize the highest-priority MEB literature curves from Tang, Horiuchi, Kobayashi, Zhu, and Ono papers using calibrated axes and confidence scores.
5. Separate the literature comparison into subgroups: subcooled pool MEB, reduced-pressure confined MEB, flow/open-microchannel MEB, and acoustic classification studies.
6. Add direct video-derived bubble metrics if available, especially bubble-cycle timing, vapor structure size, and microbubble emission intensity.
7. Decide whether the final paper should emphasize experimental diagnostics, MEB mechanism, or a literature-supported data framework. The current strongest angle is experimental diagnostics.

## Data and Code Availability

The analysis workflow, scripts, and generated BoilingLab figures are maintained in `UARK-NED3/BoilingLab`. The first-pass MEB literature compilation is maintained in `hanhuark/literature-compiler` under `examples/test2_meb`. Raw data are stored outside the repository in the laboratory data folder and are linked by test ID. Restricted PDFs and publisher figures are not committed.

## Draft Figure List

| Figure | Proposed content | Current source |
| --- | --- | --- |
| Fig. 1 | Heating-only boiling curves for Boiling-412, 413, 416, 417 | `demos/Boiling-412-413-416-417/generated/plots/` |
| Fig. 2 | Boiling-417 heat flux and temperature time histories with event markers | `demos/Boiling-417/generated/plots/` |
| Fig. 3 | Boiling-416 heat flux and temperature time histories with event markers | `demos/Boiling-416/generated/plots/` |
| Fig. 4 | Hydrophone spectrogram, band-integrated power, characteristic frequencies | `demos/Boiling-416/generated/plots/`, `demos/Boiling-417/generated/plots/` |
| Fig. 5 | AE spectrogram, band-integrated power, characteristic frequencies | `demos/Boiling-416/generated/plots/`, `demos/Boiling-417/generated/plots/` |
| Fig. 6 | MEB oscillation envelope analysis and normalized comparison | `demos/Boiling-416/generated/plots/`, `demos/Boiling-417/generated/plots/` |
| Fig. 7 | Literature-compiler `test2_meb` comparison and signature summary | `literature-compiler/examples/test2_meb/summary/` |

## References

Zeigarnik, Y. A., Platonov, D. N., Khodakov, K. A., and Shekhter, Y. L. (2012). The nature of microbubble emission under subcooled water boiling. *High Temperature*. https://doi.org/10.1134/S0018151X12010208

Zhu, G., Sun, L., Tang, J., Mo, Z., and Liu, H. (2014). A visualized study of micro-bubble emission boiling. *International Communications in Heat and Mass Transfer*. https://doi.org/10.1016/j.icheatmasstransfer.2014.10.003

Ando, J., Horiuchi, K., Saiki, T., Kaneko, T., and Ueno, I. (2016). Transition process leading to microbubble emission boiling on horizontal circular heated surface in subcooled pool. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2016.05.050

Inada, S., Shinagawa, K., Illias, S. B., Sumiya, H., and Jalaludin, H. A. (2016). Micro-bubble emission boiling with the cavitation bubble blow pit. *Scientific Reports*. https://doi.org/10.1038/srep33454

Tang, J., Xie, G., Bao, J., Mo, Z., Liu, H., and Du, M. (2018). Experimental study of sound emission in subcooled pool boiling on a small heating surface. *Chemical Engineering Science*. https://doi.org/10.1016/j.ces.2018.05.002

Tang, J., Sun, L., Du, M., Liu, H., Mo, Z., and Bao, J. (2019). Experimental investigation of transition process from nucleate boiling to microbubble emission boiling under transient heating modes. *AIChE Journal*. https://doi.org/10.1002/aic.16555

Sinha, K. N. R., Kumar, V., Kumar, N., Thakur, A., and Raj, R. (2021). Deep learning the sound of boiling for advance prediction of boiling crisis. *Cell Reports Physical Science*. https://doi.org/10.1016/j.xcrp.2021.100382

Horiuchi, K., et al. (2021). Spatial-temporal thermal-fluid behaviors of microbubble emission boiling (MEB). *AIChE Journal*. https://doi.org/10.1002/aic.17193

Unno, N., Noma, R., Yuki, K., Satake, S., and Suzuki, K. (2022). Effects of surface properties on wall superheat at the onset of microbubble emission boiling. *International Journal of Multiphase Flow*. https://doi.org/10.1016/j.ijmultiphaseflow.2022.104196

Kobayashi, N., et al. (2022). On homogeneity of vapor bubbles' oscillation and corresponding heat transfer characteristics and boiling sound in microbubble emission boiling (MEB). *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2022.122564

Ono, J., Aoki, Y., Unno, N., Yuki, K., Suzuki, K., Ueki, Y., and Satake, S. (2023). Acoustic state detection of microbubble emission boiling using a deep neural network based on cepstrum analysis. *International Journal of Multiphase Flow*. https://doi.org/10.1016/j.ijmultiphaseflow.2023.104512

Tang, J., Li, X., Xu, L., and Sun, L. (2023). Bubble-induced oscillating flow in microbubble emission boiling under highly subcooled conditions. *Journal of Fluid Mechanics*. https://doi.org/10.1017/jfm.2023.285

Unno, N., Yuki, K., and Suzuki, K. (2025). Onset of microbubble emission boiling at reduced pressure using a confined vessel for subcooled pool boiling. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2024.126600

Zhao, Q., Lu, M., Zhang, Y., Li, Q., and Chen, X. (2025). Flow microbubble emission boiling (MEB) in open microchannels for durable and efficient heat dissipation. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2024.126506
