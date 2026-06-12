# Time-Resolved Thermal and Acoustic Diagnostics of Microbubble Emission Boiling Under Subcooled Pool Boiling Conditions

**Draft status:** journal-facing manuscript draft, June 12, 2026
**Article type:** experimental heat-transfer and diagnostics paper
**Target journal:** Applied Thermal Engineering
**Data/code repositories:** `UARK-NED3/BoilingLab` and `hanhuark/literature-compiler`

## Abstract

Microbubble emission boiling (MEB) can remove heat fluxes beyond conventional pool-boiling limits, but its onset and development remain difficult to diagnose because wall heat transfer, vapor collapse, liquid replenishment, and acoustic emission evolve together. This study develops a time-resolved thermal-acoustic analysis workflow for subcooled pool boiling on a flat copper surface and applies it to four active-heating tests near 97-98 kPa with electrical power levels from approximately 150 to 250 W. Wall temperature and heat flux are reconstructed from embedded thermocouple data for all four cases, hydrophone signals are analyzed where generated intermediates are available, and acoustic-emission (AE) waveform analysis is performed for the two cases with available waveform files. The maximum reconstructed heat flux increases from 142 to 278 W/cm^2 across the power sweep. The two high-power cases exhibit persistent post-transition thermal and acoustic oscillations, whereas the lower-power cases do not show the same developed oscillatory state. Event markers separate the DNB-associated heat-flux drop, the transition wall-temperature peak, the first sustained oscillation peak, and power shutoff. In the high-power cases, hydrophone and AE waveform data show consistent low-frequency envelope modulation near 0.05 and 0.08 Hz. These frequencies are not bubble-collapse carrier frequencies; they quantify slow modulation of the MEB-like state, while literature-reported bubble and sound frequencies typically lie from tens of Hz to several kHz. A Hilbert-envelope analysis with a first-order asymptotic growth model shows that one high-power case reaches thermal-envelope saturation rapidly, with `tau = 103-106 s` and saturation fraction near 97%, while the highest-power case develops more slowly, with `tau = 239-248 s` and saturation fraction of 77-78% before shutoff. The acoustic power envelopes grow less smoothly than the thermal envelopes, indicating intermittent collapse bursts in addition to slow regime modulation. Together with a first-pass literature compilation of MEB heat-transfer and acoustic signatures, these results show that synchronized thermal-acoustic diagnostics can identify MEB development even when the dataset is too small to establish universal heat-transfer scaling.

**Keywords:** microbubble emission boiling; subcooled pool boiling; boiling sound; hydrophone; acoustic emission; heat flux; oscillation envelope; wall temperature

## Nomenclature

| Symbol | Definition | Unit |
| --- | --- | --- |
| `A` | oscillation envelope amplitude | signal-dependent |
| `A_0` | fitted envelope amplitude at the first sustained oscillation peak | signal-dependent |
| `A_inf` | fitted asymptotic envelope amplitude | signal-dependent |
| `C_eff` | effective thermal/vapor storage capacitance in reduced-order model | J/K or normalized |
| `f` | frequency | Hz |
| `L_eff` | effective inertial element for vapor-film/liquid response | normalized |
| `P_load` | electrical power load | W |
| `q''` | heat flux | W/cm^2 |
| `T` | temperature | degC |
| `T_sat` | saturation temperature | degC |
| `T_w` | extrapolated wall temperature | degC |
| `t_DNB` | heat-flux maximum before the DNB-associated drop | s |
| `t_off` | time when DC power is turned off | s |
| `t_osc` | first sustained wall-temperature oscillation peak in the analysis window | s |
| `t_peak` | wall-temperature peak during the transition event | s |
| `tau` | asymptotic envelope growth time constant | s |

## 1. Introduction

Boiling heat transfer is attractive because phase change can remove heat fluxes far beyond those accessible to single-phase convection. Its practical use, however, is constrained by boiling crisis: vapor accumulation near the wall can interrupt liquid contact, reduce heat-transfer effectiveness, and produce rapid wall-temperature excursions. Classical hydrodynamic treatments of critical heat flux (CHF), including the work of Zuber [zuber_1958_stability; zuber_1959_hydrodynamic], established the importance of vapor-liquid interfacial instability, and later texts and reviews organized CHF mechanisms, correlations, and subcooling effects for engineering design [carey_2020_phase_change; liang_2018_chf_review]. These foundations remain essential, but they do not fully describe regimes in highly subcooled liquids where condensation, vapor collapse, liquid replenishment, and acoustic emission evolve together after departure from ordinary nucleate boiling.

Microbubble emission boiling (MEB) sits in this unsettled part of the boiling map. Early subcooled-boiling observations showed that strong subcooling changes bubble growth and collapse [gunther_1950_subcooled_bubble_photography; ivey_1966_subcooled_chf], and subsequent studies identified the emission of fine bubbles from near-wall vapor structures as a distinct high-heat-flux behavior [inada_1981_subcooled_pool_boiling; zeigarnik_2012_microbubble_emission_nature]. The important point is not only that MEB can be associated with large heat fluxes. It is that MEB appears to operate through a coupled cycle: vapor structures form or coalesce, collapse rapidly in subcooled liquid, emit microbubbles and sound, and drive liquid motion back toward the wall. Visualized MEB experiments, transition studies, and spatiotemporal surface-temperature measurements support this interpretation by showing rapid vapor collapse, nonuniform surface-temperature fields, and boiling-sound signatures during MEB development [zhu_2014_visualized_meb; tang_2016_transition_to_meb; tang_2019_transient_nucleate_to_meb; horiuchi_2021_spatial_temporal_thermal_fluid]. Recent measurements that connect bubble-induced oscillating flow and vapor-film motion to heat transfer further suggest that MEB should be treated as a coupled thermal-fluid oscillatory regime rather than only as a point on a boiling curve [li_2022_oscillating_vapor_film; tang_2023_bubble_induced_oscillating_flow].

That physical picture creates an urgent diagnostics problem. If the key process is coupled and unsteady, then a boiling curve alone cannot tell whether a case is entering MEB, whether the oscillatory state is strengthening, or whether acoustic activity is synchronized with wall-temperature and heat-flux changes. Yet many available comparisons emphasize heat flux, onset wall superheat, visualization snapshots, or acoustic classification separately. Surface-condition studies show that MEB onset depends on surface properties as well as heat flux and subcooling [unno_2022_surface_properties_meb_onset], and reduced-pressure or confined-vessel studies indicate that onset can shift under conditions relevant to subatmospheric operation [unno_2025_reduced_pressure_confined_meb]. Specialized configurations such as cavitation-assisted boiling, open microchannels, and engineered surfaces demonstrate the breadth of MEB-like heat-transfer behavior but also make clear that geometry, confinement, pressure, surface preparation, and regime definition must be preserved before literature heat-flux values can be compared meaningfully [inada_2016_cavitation_bubble_blow_pit; zhao_2025_open_microchannel_meb; elele_2018_single_bubble_boiling; liu_2020_pin_cluster_nucleation]. The missing need is not another isolated heat-flux number; it is a time-resolved way to connect thermal response, acoustic response, event timing, and MEB-state development in one record.

Acoustic measurements are a natural candidate for that role because MEB is often loud, intermittent, and collapse-driven. Sound-emission studies in subcooled pool boiling have reported spectral features associated with MEB [tang_2018_sound_emission_subcooled_pool], and hydrophone-based acoustic state detection has shown that boiling sound can classify MEB states [ono_2023_acoustic_state_detection_meb; ueki_2024_acoustic_state_cucrzr_divertor]. Broader boiling-crisis studies have also used audio-visual-thermal measurements and deep-learning classifiers to identify regime transitions [sinha_2020_audio_visual_thermal_transition; sinha_2021_deep_learning_sound_boiling], while AE monitoring has demonstrated that boiling-induced elastic waves can carry regime information through a heated structure [baek_2017_ae_water_boiling_cladding]. These results show that acoustic signals contain useful information, but they also expose a trap: a single reported frequency can mean very different things. Bubble-collapse or boiling-sound carrier frequencies may lie from tens of Hz to several kHz [tang_2016_transition_to_meb; zhu_2014_visualized_meb; horiuchi_2021_spatial_temporal_thermal_fluid; kobayashi_2022_on_homogeneity_of_vapor_bubble], whereas band-integrated acoustic power can oscillate much more slowly as the boiling state grows, saturates, or intermittently bursts. Without synchronized thermal data, these frequency scales can be confused.

The present study addresses that gap by developing a reproducible thermal-acoustic workflow for subcooled pool boiling on a flat copper surface. Four active-heating cases are analyzed in order of increasing imposed electrical power and are referred to as Cases A-D rather than by internal test identifiers. Wall temperature and heat flux are reconstructed from embedded thermocouples for all four cases. Hydrophone signals are reduced to spectrograms, band-integrated power, and characteristic frequencies for all four cases. AE waveform analysis is included only for Cases C and D, because those are the cases with available waveform files. The analysis defines event times for the DNB-associated heat-flux drop, the wall-temperature peak during transition, the first sustained oscillation peak, and power shutoff. It then uses these events to compare heating-only boiling curves, aligned thermal-acoustic time histories, slow acoustic modulation, and asymptotic growth of oscillation envelopes. A first-pass MEB literature compilation is used not as a stand-alone review, but as context for two questions that remain unresolved: how MEB onset and heat-transfer scale should be compared across very different experiments, and how acoustic frequencies should be interpreted when carrier, bubble-cycle, and slow-envelope scales coexist.

## 2. Experimental Data and Analysis Workflow

The experimental dataset consists of four subcooled pool-boiling tests on a flat copper surface. The cases were conducted near 97-98 kPa with water as the working fluid. The imposed electrical power was increased across the matrix from approximately 150 W to 250 W. Table 1 summarizes the operating conditions and primary thermal outcomes. The values come from the reproducible BoilingLab multi-case analysis, which retains only the active-heating portion of each test.

The experiments were performed in a pressure-controlled stainless-steel pool-boiling chamber with optical access through reinforced glass viewports. The chamber was fitted with a reflux condenser and an internal coiled condenser loop connected to a temperature-controlled chiller so that vapor generation during boiling could be balanced by condensation. Pressure was adjusted with a vacuum pump and condenser-flow control, while the bulk liquid and vapor-space temperatures were monitored with T-type thermocouples. A dedicated facility paper will describe the chamber, pressure-control approach, and operating procedure in detail; only the elements needed to interpret the present thermal-acoustic data are summarized here.

The heated specimen was mounted in a heating-element enclosure inserted through the chamber base. For the cases considered here, the boiling surface was a flat, upward-facing copper surface with a projected area of 10 mm by 10 mm. Four T-type thermocouples were embedded along the copper centerline below the surface at uniform axial spacing. Their temperatures were used to estimate the wall temperature and heat flux by a one-dimensional conduction model. Electrical heat input was supplied by cartridge heaters powered by a programmable DC power supply, and the power-supply voltage, current, and power were logged during each test.

**Table 1. Summary of active-heating cases used in this draft.**

| Case | Nominal power (W) | Mean pressure (kPa) | Mean liquid temperature (degC) | `T_sat` (degC) | Maximum `q''` (W/cm^2) | Maximum `T_w` (degC) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 150 | 97.28 | 58.83 | 98.84 | 142.0 | 112.7 |
| B | 180 | 97.30 | 52.38 | 98.84 | 163.1 | 159.2 |
| C | 230 | 97.47 | 57.27 | 98.89 | 267.2 | 167.0 |
| D | 250 | 97.51 | 57.60 | 98.90 | 278.0 | 172.9 |

The dataset is intentionally interpreted as a pilot study. Cases A and B provide lower-power references. Cases C and D contain the strongest evidence of developed coupled thermal-acoustic oscillations and have the most complete acoustic analysis, including hydrophone and AE waveform processing. Thermal data are available for all four cases; AE waveform files are available only for Cases C and D. The limited number of tests does not support a universal MEB scaling law, but it is sufficient to demonstrate a synchronized analysis method and to identify physically meaningful differences between lower- and higher-power responses.

Thermal quantities are reconstructed from the embedded thermocouple array. Temperatures are read from LVM files and used to reconstruct the surface temperature by extrapolating embedded thermocouple measurements through the copper block. Heat flux is calculated from the inferred temperature gradient and the copper thermal conductivity. The approach assumes one-dimensional conduction over the thermocouple line used for extrapolation. The quality of the linear fit through the thermocouple data is stored in the generated summaries and provides a check on the conduction approximation.

The multi-case boiling curves include only heating data. Samples are retained when the aligned DC-power signal is positive. This definition removes the cooling path after power shutoff, which would otherwise mix active boiling behavior with post-heating thermal relaxation. It also makes the comparison more consistent with literature boiling curves that represent increasing or active heat input.

Event times define the analysis windows. Four event times are extracted from each developed case. The DNB-associated time `t_DNB` is defined as the heat-flux maximum before the sudden heat-flux drop during transition. The wall-temperature peak `t_peak` identifies the thermal overshoot during that transition. The first sustained oscillation marker `t_osc` is extracted from the first wall-temperature oscillation peak after the nominal start of the oscillatory window. The shutoff time `t_off` is defined from the DC-power signal when the power load returns to near zero.

These definitions intentionally separate transition and sustained oscillation. The heat-flux drop and wall-temperature peak occur early in the record and describe the departure from the preceding boiling path. The later `t_osc` marker defines the start of the envelope-analysis interval for the sustained MEB-like oscillatory state.

Acoustic sensing is treated as a synchronized but sensor-dependent diagnostic. Two acoustic pathways were used. A High-Tech HTI-96-MIN hydrophone was immersed in the liquid pool to sense pressure fluctuations and boiling sound transmitted through the working fluid. The hydrophone signal was acquired with a National Instruments NI-9230 module using LabVIEW. A MISTRAS R3a acoustic-emission sensor was mounted on the outside wall of the stainless-steel chamber to sense structure-borne acoustic activity generated by boiling and transmitted through the vessel. The AE sensor was connected to a MISTRAS EasyAE system and recorded with AEWin software. The thermal, power, hydrophone, and AE records were synchronized through wall-clock time stamps before post-processing in BoilingLab.

Hydrophone data are analyzed with spectrograms and PSD-based band integration. The band-integrated hydrophone power is obtained by integrating PSD over frequency in linear units. This produces a voltage-squared band-power proxy. Direct averaging of dB values is avoided because dB is logarithmic and does not preserve linear acoustic power. The publication-analysis tables record the current data coverage explicitly: generated hydrophone intermediates are available for all four cases, while AE waveform files are available only for Cases C and D.

Characteristic acoustic frequencies are extracted from each spectrogram time bin. The peak frequency identifies the largest PSD bin in the selected band. The spectral centroid gives the power-weighted frequency, and the bandwidth measures the spread around the centroid. These metrics are plotted over time and compared with the integrated acoustic power to determine whether amplitude bursts align with shifts in spectral content.

AE waveform files are processed with the same overall logic for Cases C and D. The AE sensor responds through a different transmission path than the hydrophone, so agreement between hydrophone and AE modulation is meaningful. It indicates that the slow oscillatory behavior is not an artifact of one sensor alone. Because the AE sensor is mounted on the chamber wall rather than immersed in the liquid, AE power is interpreted as a structure-path-weighted voltage proxy rather than an absolute acoustic intensity.

The oscillation-amplitude analysis uses a Hilbert-transform envelope. For each signal, the active MEB window is selected, a slow baseline is removed using a 75 s Savitzky-Golay smoother, and the Hilbert envelope of the detrended signal is smoothed with a 35 s Savitzky-Golay window. The smoothed envelope is fitted with a first-order asymptotic growth model:

```text
A(t) = A_inf - (A_inf - A_0) exp(-(t - t_osc) / tau)
```

Here `A_0` is the fitted envelope amplitude at `t_osc`, `A_inf` is the asymptotic envelope amplitude, and `tau` is the growth time constant. The fitted saturation fraction at the end of the window is `(A_end - A_0)/(A_inf - A_0)`. The model is not intended to prove a universal first-order process. It is used as a compact metric for whether the envelope continues to grow linearly, approaches a finite amplitude, or is poorly described by smooth saturation.

The literature comparison is maintained in the sibling `literature-compiler` repository under `examples/test2_meb`. The case includes MEB-related Zotero sources, screening notes, first-pass heat-flux and wall-superheat values, and a separate table of MEB-specific acoustic and oscillatory signatures. The compilation is used in this manuscript as a structured context rather than as a finalized systematic review. Values marked as reported text or range endpoints should be checked against the original figures and tables before submission.

The compilation also records frequency type. This field is essential because the literature contains several different frequency quantities: bubble oscillation frequency, boiling sound peak frequency, pressure fluctuation frequency, hydrophone sampling rate, and slow envelope modulation. The present work reports slow envelope modulation of thermal and acoustic power, so comparisons to high-frequency sound or bubble-collapse values must be made through mechanism rather than by direct numerical equality.

## 3. Results and Discussion

### 3.1 Heating-only boiling curves identify the power range where the oscillatory state appears

Figure 1 shows the heating-only boiling curves for Cases A-D. The heat flux increases with wall temperature during early heating and then separates by input power. Cases A and B reach maximum reconstructed heat fluxes of 142 and 163 W/cm^2, respectively. Cases C and D reach substantially higher values, 267 and 278 W/cm^2. The higher-power cases also show a different time-domain response, with persistent post-transition oscillations in wall temperature and heat flux.

The figure has two roles in the manuscript. First, it establishes that the four tests are not identical repeats but a power sweep across lower- and higher-intensity boiling responses. Second, it shows why a boiling curve alone is insufficient for this dataset. Cases C and D are close in maximum heat flux, but their time-domain envelope metrics differ strongly. Case C approaches a saturated thermal oscillation amplitude more rapidly, while Case D continues to develop more slowly until power shutoff. That difference is invisible if the data are reduced only to maximum heat flux or a single curve envelope.

Physically, the progression from Cases A/B to Cases C/D is consistent with increasing vapor generation and stronger interaction between near-wall vapor structures and subcooled liquid. The higher-power cases likely provide enough vapor generation to sustain repeated vapor collapse and liquid replenishment, while the lower-power cases remain weaker or less organized. This interpretation agrees with literature that connects MEB to high subcooling, high heat flux, bubble collapse, and oscillating liquid motion [zhu_2014_visualized_meb; tang_2016_transition_to_meb; tang_2023_bubble_induced_oscillating_flow].

**Figure 1. Heating-only boiling curves for the four active-heating cases.** Panel (a) should show `q''` versus `T_w`, and panel (b) should show `q''` versus wall superheat. The plotted data should be labeled as Cases A-D rather than internal test IDs. The caption should state that only positive-power heating data are included.

### 3.2 Event markers distinguish transition from sustained oscillatory MEB-like behavior

Figure 2 shows the high-power Case D time histories with event markers. The heat flux initially increases, reaches a local maximum before a sudden drop, and then recovers into a sustained oscillatory regime. The DNB-associated marker occurs at 124.8 s, and the wall-temperature peak occurs at 132.4 s. The first sustained oscillation peak used for envelope analysis occurs later at 308.0 s, while power is turned off at 673.9 s.

This sequence indicates that the transition event and the sustained oscillatory state are separated in time. The early heat-flux drop and wall-temperature peak are consistent with a departure from a nucleate-boiling-like path and a transient vapor-coverage or dryout event. The later oscillatory interval is different: wall temperature and heat flux oscillate repeatedly while power remains on. This behavior is closer to the MEB descriptions in which vapor structures repeatedly grow, condense, collapse, and interact with the surrounding liquid.

Figure 3 shows the same analysis for Case C. In this case, the DNB-associated marker occurs at 150.8 s, the wall-temperature peak occurs at 160.8 s, the first sustained oscillation peak occurs at 321.6 s, and power shutoff occurs at 757.8 s. Compared with Case D, Case C begins its sustained oscillatory interval slightly later but has a longer active-heating duration after `t_osc`. This longer window partly explains why its thermal envelope approaches saturation more completely.

The event markers make the analysis auditable. Without them, the envelope window could be chosen subjectively, and transition overshoot could be mixed with sustained oscillation. The markers also create a bridge to the literature. Prior MEB transition studies often focus on the abrupt transition or visual onset [tang_2016_transition_to_meb; tang_2019_transient_nucleate_to_meb], while acoustic state studies focus on regime classification [ono_2023_acoustic_state_detection_meb]. The present marker set links those perspectives by defining both the transition and the later oscillatory state in one synchronized record.

**Figure 2. Case D thermal time histories with event markers.** Panel (a) should show heat flux and power load versus time. Panel (b) should show thermocouple temperatures and extrapolated wall temperature versus time. Labels should mark `t_DNB`, `t_peak`, `t_osc`, and `t_off`.

**Figure 3. Case C thermal time histories with event markers.** The layout should match Figure 2 so the timing and saturation behavior of the two high-power cases can be compared directly.

### 3.3 Hydrophone spectra and band-integrated power show slow modulation of the developed regime

Figure 4 shows the hydrophone diagnostics. The spectrogram identifies the frequency content of the acoustic signal, while the band-integrated power converts the PSD into a scalar power proxy over time. The characteristic-frequency plot shows how peak frequency and spectral centroid evolve during the same interval. Hydrophone metrics are now available for all four cases. Cases A and B provide lower-power acoustic references, while Cases C and D show stronger band-integrated hydrophone power and clearer sustained oscillatory behavior during the developed MEB-like regime.

The lower-power cases do not show sustained MEB-like oscillations, so their mechanically extracted low-frequency components are not interpreted as MEB modulation frequencies. The developed high-power cases do show a repeatable slow envelope frequency: approximately 0.05 Hz for Case C and 0.08 Hz for Case D. AE waveform analysis gives nearly the same modulation values for the two developed high-power cases, approximately 0.055 Hz and 0.080 Hz. The agreement between hydrophone and AE modulation is important because the two sensors have different coupling paths. The hydrophone senses pressure waves in the liquid, whereas AE senses elastic/acoustic activity transmitted through the solid structure. Agreement between them suggests that the slow modulation in Cases C and D is a real boiling-state feature rather than a single-sensor artifact.

The frequency interpretation must be handled carefully. Literature-reported MEB sound and bubble frequencies often lie at much higher values. Horiuchi et al. [horiuchi_2021_spatial_temporal_thermal_fluid] and Kobayashi et al. [kobayashi_2022_on_homogeneity_of_vapor_bubble] reported sound or bubble-related frequencies from tens to hundreds of Hz and up to approximately 1000 Hz depending on MEB state. Ando et al. [tang_2016_transition_to_meb] reported repetitive vapor-bubble collapse on the order of 800-2000 Hz, and Zhu et al. [zhu_2014_visualized_meb] reported a boiling-sound peak near 2700 Hz. The present 0.05-0.08 Hz high-power values do not contradict those studies because they describe slow envelope modulation of integrated acoustic power, not the high-frequency carrier generated by individual collapse events.

This distinction provides one of the main contributions of the paper. Acoustic diagnostics should not reduce MEB to one frequency number unless the meaning of that number is specified. A spectrogram may contain high-frequency bubble-collapse or sound content, while the band-integrated power may rise and fall on a much slower regime-development time scale. The slow modulation is useful because it aligns with thermal oscillation amplitude and can be tracked even when high-frequency details depend on sensor bandwidth or coupling.

**Figure 4. Hydrophone diagnostics for the four active-heating cases.** Each case should include a spectrogram, band-integrated power, and characteristic frequencies. The caption should state the band used for PSD integration, distinguish weak lower-power modulation from developed high-power modulation, and separate slow power modulation from high-frequency spectral content.

### 3.4 AE waveform analysis confirms the slow modulation observed by the hydrophone

Figure 5 presents the AE waveform diagnostics. The AE spectrogram shows frequency content transmitted through the structure, while AE band-integrated power and characteristic frequencies provide time-resolved scalar metrics. For Cases C and D, the AE waveform analysis detects the same low-frequency modulation scale as the hydrophone. This agreement increases confidence that the observed modulation is tied to the boiling process.

The AE data also highlight a measurement challenge. AE sensors are sensitive to mounting, structural transmission paths, resonances, and background mechanical noise. A peak in AE power is therefore not automatically a direct measure of bubble-collapse energy. It is a sensor-path-weighted response to boiling-induced elastic waves. The hydrophone, by contrast, measures pressure/acoustic activity in the liquid but also has its own frequency response and placement sensitivity. The value of using both sensors is not that either one is perfect, but that common features across both channels are more likely to be physically meaningful.

The AE and hydrophone results are consistent with prior acoustic boiling studies. Tang et al. [tang_2018_sound_emission_subcooled_pool] reported that MEB sound contains identifiable spectral peaks, while Ono et al. [ono_2023_acoustic_state_detection_meb] showed that acoustic features can classify MEB states. The present work extends this logic by aligning acoustic metrics with reconstructed wall temperature and heat flux. That alignment is needed if acoustic sensing is to be used for mechanistic interpretation rather than only regime classification.

**Figure 5. AE waveform diagnostics for the developed high-power cases.** Each case should include an AE spectrogram, band-integrated AE power, and characteristic frequencies. The caption should state the AE channel, sampling assumptions, and frequency band used for integration.

### 3.5 Asymptotic envelope analysis quantifies how the oscillatory state develops

Figure 6 shows the oscillation-envelope analysis for Cases C and D. The smoothed thermal envelopes are fitted well by the asymptotic growth model, while the acoustic-power envelopes are more intermittent. The fitted values are summarized in Table 2.

**Table 2. Asymptotic envelope metrics for the developed high-power cases.**

| Case | Signal | Percent change (%) | `tau` (s) | Saturation fraction at window end | R^2 |
| --- | --- | ---: | ---: | ---: | ---: |
| C | `T_w` | 2042 | 103.4 | 0.974 | 0.970 |
| C | `q''` | 1531 | 105.8 | 0.972 | 0.963 |
| C | Hydrophone power | 313 | 769.9 | 0.388 | 0.848 |
| D | `T_w` | 167 | 239.1 | 0.783 | 0.935 |
| D | `q''` | 150 | 247.8 | 0.771 | 0.938 |
| D | Hydrophone power | 140 | 7308.8 | 0.049 | 0.588 |

Case C reaches its fitted thermal asymptote more rapidly than Case D. The `T_w` and `q''` time constants are 103-106 s in Case C, and the saturation fractions are approximately 97% by the end of the analysis window. In Case D, the thermal time constants are 239-248 s and the saturation fractions are 77-78% before power shutoff. Thus, despite having the highest nominal power and maximum heat flux, Case D does not fully saturate its thermal oscillation envelope before heating ends.

The fitted percent change is large in Case C because the fitted initial envelope at `t_osc` is small. The more physically useful comparison is therefore the time constant and saturation fraction rather than percent change alone. The thermal `tau` values indicate how quickly the MEB-like oscillatory state develops after the first sustained peak, while the saturation fraction indicates whether the test duration is long enough to observe a quasi-steady oscillation amplitude.

Hydrophone power behaves differently from the thermal envelopes. In Case C, the hydrophone-power envelope grows but has a much longer time constant than the thermal signals. In Case D, the fitted hydrophone time constant is far longer than the experimental window and the R^2 is low. This result should not be treated as a failed acoustic measurement. It indicates that the band-integrated acoustic power contains intermittent bursts superimposed on slow modulation. These bursts are expected if individual vapor-collapse events vary in intensity and if the sensor band emphasizes particular collapse or structural-transmission events.

Physically, the thermal envelopes likely represent the growth of the regime-scale oscillation amplitude after transition. The acoustic power envelopes represent both that slow growth and the intermittency of collapse events. This interpretation is consistent with MEB literature that links heat transfer to oscillating vapor structures and liquid motion, while also reporting strong boiling-sound signatures [horiuchi_2021_spatial_temporal_thermal_fluid; kobayashi_2022_on_homogeneity_of_vapor_bubble; tang_2023_bubble_induced_oscillating_flow].

**Figure 6. Oscillation-envelope growth and saturation.** Panel groups should show detrended thermal/acoustic signals, smoothed envelopes, asymptotic fits, and normalized envelope comparisons. The figure should report `tau`, saturation fraction, and R^2 in the annotation rather than emphasizing linear slope.

### 3.6 Representative video frames and a storage-release model explain the oscillatory mechanism

The high-speed video provides a direct visual basis for interpreting the low-frequency acoustic and thermal oscillations. The oscillation is not a uniform emission of small bubbles. Instead, the developed high-power cases show intervals with fewer visible microbubbles followed by intervals with dense microbubble release above the heated surface. Figure 8 shows representative frames selected from the MP4 videos using visual plume activity and annotated with the corresponding hydrophone-power percentile. The frames support a storage-and-release interpretation: vapor accumulates or reorganizes near the wall, the near-wall vapor/liquid system reaches a release condition, and a burst of microbubbles is emitted into the subcooled liquid.

This interpretation also explains why the reconstructed instantaneous heat flux can exceed the nominal load-based heat-flux scale during the oscillatory region. The electrical input is approximately steady, but the wall/vapor/liquid system is not in instantaneous steady state. During the storage part of the cycle, energy is retained in the heated solid, vapor structure, and adjacent superheated liquid. During release, collapse, rewetting, and microbubble ejection discharge part of that stored energy over a shorter time scale. In a local transient energy balance,

```text
q''_out = q''_in - dE_stored/dt - q''_loss
```

so `q''_out` can exceed `q''_in` whenever `dE_stored/dt` is negative and the stored energy is being released. The capacitor analogy is therefore useful, provided it is not interpreted as a literal electrical circuit.

Figure 9 formalizes the analogy with a reduced-order storage-release oscillator. The model treats the near-wall vapor/thermal state as an effective capacitance, `C_eff`, charged by the imposed heat input. Vapor-film motion, liquid inertia, and collapse/replenishment are represented by an inertial coordinate, `L_eff`, with damping and nonlinear feedback. In nondimensional form, the conceptual model can be written as

```text
C_eff dTheta/dt = q''_in - q''_release(Theta, xi) - q''_loss
L_eff d2xi/dt2 + R_eff dxi/dt + K_eff xi = F(Theta, xi)
q''_release = H(Theta - Theta_c) Phi(xi, dxi/dt)
```

where `Theta` is a stored thermal/vapor energy state, `xi` is an effective vapor-film or release coordinate, `H` is a threshold-like activation, and `Phi` represents nonlinear release. The plotted implementation is intentionally semi-analytical rather than fitted: it uses an LC-like oscillator with slowly increasing nonlinear feedback to show how a constant input can produce growing heat-release and acoustic-power bursts before the oscillation reaches a finite amplitude. The model should be read as a mechanism sketch and a guide for future fitting, not as a validated predictive correlation.

The model is helpful because it separates three time scales. The kHz-scale acoustic content comes from local collapse and sound generation. The 0.05-0.08 Hz envelope comes from repeated storage and release of the MEB state. The envelope-growth time constant, reported in Table 2, describes how the oscillatory state strengthens after the first sustained peak. This hierarchy of time scales is consistent with prior visual and acoustic MEB studies, but the present dataset connects it to synchronized wall-temperature, heat-flux, hydrophone, AE, and high-speed-video observations.

**Figure 8. Representative high-speed-video frames during developed MEB-like oscillations.** Panels compare fewer-bubble and many-bubble frames for Cases C and D. Frames are selected from MP4 videos encoded at 30 fps from 150 fps high-speed recordings using `video_time = 5 t`. The caption should state that the frames are visually screened representatives and give the hydrophone-power percentile at each selected time.

**Figure 9. Reduced-order storage-release oscillator for the MEB regime.** The model is a conceptual LC-like, driven, damped, nonlinear oscillator. It shows a stored thermal/vapor state, transient heat-release proxy, and acoustic-power proxy. The caption should state that the model is not fitted to the data and is used to explain how constant input can produce growing oscillatory release and transient heat flux above the nominal input scale.

### 3.7 Literature comparison positions the present dataset as a diagnostics contribution

Figure 7 compares the present cases with the first-pass MEB literature compilation. The literature spans subcooled pool boiling, reduced-pressure confined MEB, open-microchannel MEB, visualized transition studies, acoustic state detection, and specialized high-heat-flux MEB configurations. Reported heat-flux scales range from approximately 140-320 W/cm^2 in reduced-pressure or microchannel contexts to much higher values in specialized microbubble-emission or cavitation-assisted configurations. The present high-power cases fall within the lower-to-middle part of this broad range.

This comparison is useful because it prevents overclaiming. The present dataset does not demonstrate record-setting MEB heat flux. Its contribution is the synchronized time-resolved diagnostic view: wall-temperature extrapolation, reconstructed heat flux, hydrophone power, AE waveform response where available, characteristic frequencies, and envelope saturation are analyzed on consistent event windows. That combination is less common in the literature than boiling curves, visual snapshots, or acoustic classification alone.

The literature comparison also identifies what should be extracted next. For heat-transfer comparison, the key quantities are MEB onset wall superheat, heat flux at onset, heat flux during stable MEB, pressure, subcooling, heater diameter or area, surface material, surface preparation, and confinement. For acoustic comparison, the key quantities are sensor type, sensor placement, bandwidth, sampling rate, frequency-definition type, spectral peak, and whether the frequency describes bubble oscillation, sound pressure, pressure fluctuation, or slow envelope modulation. Without these metadata, acoustic values from different papers can appear contradictory even when they describe different physical scales.

**Figure 7. Literature comparison from the first-pass MEB compilation.** Panel (a) should compare heat-flux and wall-superheat points where available. Panel (b) should compare MEB signature metrics, including heat-flux scale and frequency scale, with clear symbols for frequency type. The caption should state that the literature compilation is a screening dataset and that reported-text values require figure-level verification.

## 4. Limitations and Uncertainty

The present manuscript is built on a small number of experiments. Four cases are enough to demonstrate the workflow and to identify differences between lower- and higher-power behavior, but they are not enough to establish a universal onset criterion or heat-transfer correlation. Thermal quantities are compared across all four cases. Hydrophone time histories currently cover all four cases, but MEB power-envelope frequencies are interpreted only for the developed high-power cases. AE waveform analysis is limited to the two high-power cases because those are the only cases with waveform files. Additional repeats and intermediate power levels are needed to determine whether the observed envelope time constants are repeatable and how they scale with heat load, subcooling, pressure, and surface condition.

The thermal reconstruction has its own limits. Wall temperature is extrapolated from embedded thermocouples, so high-frequency surface-temperature fluctuations are filtered by conduction through the copper block and by thermocouple response. The reconstructed heat flux should therefore be interpreted as a filtered wall heat-flux estimate rather than an instantaneous local surface heat flux. This limitation is common in conduction-based boiling measurements, but it is especially important when comparing to high-speed visual or acoustic measurements.

The acoustic measurements are reported as voltage-based proxies rather than calibrated pressure or acoustic power. Hydrophone band-integrated power has units of V^2 because it is derived from the measured voltage PSD. AE waveform power is similarly sensor-path dependent. Calibration, sensor frequency response, coupling, placement, and background noise must be documented before the acoustic metrics can be compared quantitatively across laboratories. The present results are strongest for within-test synchronization and relative development, not absolute acoustic intensity.

The literature compilation is also preliminary. The current dataset contains first-pass reported-text values and range endpoints. Before submission, the highest-priority MEB boiling curves and onset data should be digitized with calibrated axes, uncertainty estimates, and source-specific notes. The unpublished manuscript reviewed by the authors was used only to identify potentially relevant published references. It is not cited and does not serve as evidence in this paper.

The storage-release model is intentionally a reduced-order interpretation. It demonstrates a plausible mechanism by which constant input can generate growing heat-release and acoustic bursts, but its parameters are not yet fitted to measured vapor-film thickness, bubble counts, or calibrated acoustic pressure. Future work should couple frame-resolved bubble/plume metrics, calibrated acoustic power, and transient conduction inversion to identify model parameters and test whether the same storage-release structure predicts repeated experiments.

## 5. Conclusions

This study develops and applies a synchronized thermal-acoustic workflow for diagnosing MEB-like development in subcooled pool boiling on a flat copper surface. The main conclusions are as follows.

1. Heating-only boiling curves separate lower-power reference behavior from higher-power oscillatory behavior. Maximum reconstructed heat flux increases from 142 W/cm^2 in the lowest-power case to 278 W/cm^2 in the highest-power case.

2. Event markers identify distinct stages of the process. The DNB-associated heat-flux drop and transition wall-temperature peak occur early, while the first sustained oscillation peak occurs later and defines the start of the MEB-envelope analysis window.

3. Hydrophone measurements are now available for all four cases. The lower-power cases provide acoustic references but are not interpreted as having resolved MEB modulation. The developed high-power cases show consistent hydrophone and AE slow envelope modulation. The modulation frequencies are approximately 0.05-0.055 Hz in Case C and 0.08 Hz in Case D. These values describe slow regime modulation, not high-frequency bubble-collapse or boiling-sound carrier frequencies.

4. Thermal oscillation envelopes are well described by a first-order asymptotic growth model. Case C reaches near-saturation within the active-heating window (`tau = 103-106 s`, saturation fraction near 97%), whereas Case D develops more slowly (`tau = 239-248 s`, saturation fraction near 77-78% before shutoff).

5. Hydrophone power envelopes grow but remain more intermittent than the thermal envelopes. This behavior indicates that acoustic power contains burst-like collapse dynamics in addition to the slow development of the MEB-like thermal oscillation.

6. Representative high-speed-video frames show that microbubble release is temporally nonuniform. A storage-release interpretation explains this observation and provides a physical reason that reconstructed heat flux can transiently exceed the nominal input scale during the oscillatory MEB-like regime.

7. The first-pass literature comparison shows that the present dataset is best positioned as a multimodal diagnostics contribution rather than a record-heat-flux study. Its value is the synchronized connection among wall temperature, heat flux, hydrophone response, AE response, high-speed-video evidence, and envelope growth.

## 6. Work Needed Before Submission

Several tasks remain before submission to *Applied Thermal Engineering*, but the publication-analysis package now contains the first complete pre-submission pass for the highest-priority items. A propagated uncertainty budget has been generated for wall temperature, heat flux, event times, hydrophone band power, characteristic frequency, AE waveform quantities where available, and envelope-fit parameters. These values combine data-derived diagnostics with source-labeled instrument assumptions; calibration-certificate values for the thermocouples, DAQ modules, pressure transducer, hydrophone chain, and AE chain should replace the current assumptions before final submission. The `test2_meb` compilation has also been normalized into publication-facing boiling-curve and onset/signature tables, with status labels that distinguish source-reported values, range endpoints, and entries requiring final figure digitization. Final Applied Thermal Engineering review panels have been generated with case labels, consistent typography, uncertainty representation where available, and captions that state the data-reduction choices. AE waveform analysis remains limited to Cases C and D because those are the only cases with waveform files.

## Data and Code Availability

The analysis workflow and generated figures are maintained in the BoilingLab repository. Manuscript-facing tables and draft publication figures are generated under `manuscripts/meb_multimodal_diagnostics/generated/publication_analysis`. The first-pass MEB literature compilation is maintained in the literature-compiler repository under `examples/test2_meb`. Raw experimental data are stored outside the public repository in the laboratory data archive and are linked internally by test metadata. Restricted PDFs and publisher figures are not committed.

## Draft Figure Plan

| Figure | Proposed content | Manuscript purpose |
| --- | --- | --- |
| Fig. 1 | Heating-only boiling curves for Cases A-D | Establish power sweep and heat-flux range |
| Fig. 2 | Case D heat flux, power load, and temperature time histories | Demonstrate full event sequence in the highest-power case |
| Fig. 3 | Case C heat flux, power load, and temperature time histories | Compare high-power cases and motivate envelope analysis |
| Fig. 4 | Hydrophone spectrogram, band-integrated power, and characteristic frequencies | Show liquid acoustic response and slow power modulation |
| Fig. 5 | AE spectrogram, band-integrated power, and characteristic frequencies | Confirm modulation through a second acoustic pathway |
| Fig. 6 | Oscillation envelope analysis and normalized envelope comparison | Quantify growth, saturation, and acoustic intermittency |
| Fig. 7 | Literature-compiler MEB comparison | Position the local data against published MEB ranges and diagnostics |
| Fig. 8 | Representative high-speed-video frames at fewer-bubble and many-bubble states | Visual evidence for nonuniform microbubble release |
| Fig. 9 | Storage-release oscillator model | Mechanistic explanation for low-frequency modulation and transient heat-flux overshoot |

## References

Ando, J., Horiuchi, K., Saiki, T., Kaneko, T., and Ueno, I. (2016). Transition process leading to microbubble emission boiling on horizontal circular heated surface in subcooled pool. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2016.05.050

Baek, W. P., et al. (2017). Acoustic emission monitoring of water boiling on fuel cladding surface at 1 bar and 130 bar. *Measurement*. https://doi.org/10.1016/j.measurement.2017.05.042

Brennen, C. E. (2002). Fission of collapsing cavitation bubbles. *Journal of Fluid Mechanics*, 472, 153-166.

Carey, V. P. (2020). *Liquid-Vapor Phase-Change Phenomena: An Introduction to the Thermophysics of Vaporization and Condensation Processes in Heat Transfer Equipment* (3rd ed.). CRC Press.

Elele, E., et al. (2018). Single-bubble water boiling on small heater under Earth's and low gravity. *npj Microgravity*. https://doi.org/10.1038/s41526-018-0055-y

Gunther, F. C., and Kreith, F. (1950). Photographic study of bubble formation in heat transfer to subcooled water. Jet Propulsion Laboratory Progress Report.

Horiuchi, K., et al. (2021). Spatial-temporal thermal-fluid behaviors of microbubble emission boiling (MEB). *AIChE Journal*. https://doi.org/10.1002/aic.17193

Inada, S., Miyasaka, Y., Izumi, R., and Owase, Y. (1981). A study on boiling curves in subcooled pool boiling. *Transactions of the Japan Society of Mechanical Engineers*, 47, 852-861.

Inada, S., Shinagawa, K., Illias, S. B., Sumiya, H., and Jalaludin, H. A. (2016). Micro-bubble emission boiling with the cavitation bubble blow pit. *Scientific Reports*. https://doi.org/10.1038/srep33454

Ivey, H. J., and Morris, D. J. (1966). Critical heat flux of saturation and subcooled pool boiling in water at atmospheric pressure. Third International Heat Transfer Conference.

Kawakami, T., et al. (2025). High-frequency oscillation of coalesced vapor bubbles and resultant ambient liquid motion in microbubble emission boiling in subcooled pool. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2025.126832

Kobayashi, H., Hayashi, M., Kurose, K., and Ueno, I. (2022). On homogeneity of vapor bubbles' oscillation and corresponding heat transfer characteristics and boiling sound in microbubble emission boiling (MEB). *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2022.122564

Li, X., Tang, J. G., Hu, R., Sun, L. C., and Bao, J. J. (2022). Investigation on interaction between an oscillating vapor film and its surrounding liquid in microbubble emission boiling. *Applied Thermal Engineering*. https://doi.org/10.1016/j.applthermaleng.2022.119012

Liang, G., and Mudawar, I. (2018). Pool boiling critical heat flux (CHF) - Part 1: Review of mechanisms, models, and correlations. *International Journal of Heat and Mass Transfer*, 117, 1352-1367.

Litvintsova, A., et al. (2020). Diagnostics of coolant boiling onset based on the analysis of fluctuations of thermohydraulic parameters. *Journal of Physics: Conference Series*. https://doi.org/10.1088/1742-6596/1689/1/012042

Liu, P., et al. (2020). Enhanced nucleate pool boiling by coupling the pinning act and cluster bubble nucleation of micro-nano composited surfaces. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2020.119979

Mao, Y., et al. (2021). A critical review on measures to suppress flow boiling instabilities in microchannels. *Heat and Mass Transfer*. https://doi.org/10.1007/s00231-020-03009-2

Ono, J., Aoki, Y., Unno, N., Yuki, K., Suzuki, K., Ueki, Y., and Satake, S. (2023). Acoustic state detection of microbubble emission boiling using a deep neural network based on cepstrum analysis. *International Journal of Multiphase Flow*. https://doi.org/10.1016/j.ijmultiphaseflow.2023.104512

Sinha, K. N. R., Kumar, V., Kumar, N., Thakur, A., and Raj, R. (2020). Simultaneous audio-visual-thermal characterization of transition boiling regime. *Experimental Thermal and Fluid Science*. https://doi.org/10.1016/j.expthermflusci.2020.110162

Sinha, K. N. R., Kumar, V., Kumar, N., Thakur, A., and Raj, R. (2021). Deep learning the sound of boiling for advance prediction of boiling crisis. *Cell Reports Physical Science*. https://doi.org/10.1016/j.xcrp.2021.100382

Tang, J., Li, X., Xu, L., and Sun, L. (2023). Bubble-induced oscillating flow in microbubble emission boiling under highly subcooled conditions. *Journal of Fluid Mechanics*. https://doi.org/10.1017/jfm.2023.285

Tang, J., Sun, L., Du, M., Liu, H., Mo, Z., and Bao, J. (2019). Experimental investigation of transition process from nucleate boiling to microbubble emission boiling under transient heating modes. *AIChE Journal*. https://doi.org/10.1002/aic.16555

Tang, J., Xie, G., Bao, J., Mo, Z., Liu, H., and Du, M. (2018). Experimental study of sound emission in subcooled pool boiling on a small heating surface. *Chemical Engineering Science*. https://doi.org/10.1016/j.ces.2018.05.002

Unno, N., Noma, R., Yuki, K., Satake, S., and Suzuki, K. (2022). Effects of surface properties on wall superheat at the onset of microbubble emission boiling. *International Journal of Multiphase Flow*. https://doi.org/10.1016/j.ijmultiphaseflow.2022.104196

Unno, N., Yuki, K., and Suzuki, K. (2025). Onset of microbubble emission boiling at reduced pressure using a confined vessel for subcooled pool boiling. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2024.126600

Ueki, Y., et al. (2024). Acoustic state sensing of subcooled boiling heat transfer on a CuCrZr surface using a deep neural network for divertor application. *Fusion Science and Technology*. https://doi.org/10.1080/15361055.2024.2435193

Zeigarnik, Y. A., Platonov, D. N., Khodakov, K. A., and Shekhter, Y. L. (2012). The nature of microbubble emission under subcooled water boiling. *High Temperature*. https://doi.org/10.1134/S0018151X12010208

Zhao, Q., Lu, M., Zhang, Y., Li, Q., and Chen, X. (2025). Flow microbubble emission boiling (MEB) in open microchannels for durable and efficient heat dissipation. *International Journal of Heat and Mass Transfer*. https://doi.org/10.1016/j.ijheatmasstransfer.2024.126506

Zhu, G., Sun, L., Tang, J., Mo, Z., and Liu, H. (2014). A visualized study of micro-bubble emission boiling. *International Communications in Heat and Mass Transfer*. https://doi.org/10.1016/j.icheatmasstransfer.2014.10.003

Zuber, N. (1958). On the stability of boiling heat transfer. *Transactions of the ASME*, 80, 711-714.

Zuber, N. (1959). Hydrodynamic aspects of boiling heat transfer. University of California, Los Angeles.
