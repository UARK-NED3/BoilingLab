# Reviewer-Author Loop Response Log

Target journal: Applied Thermal Engineering

Manuscript: `manuscripts/meb_multimodal_diagnostics/manuscript_draft.md`

## Round 1 Author Response Log

| ID | Reviewer concern | Author action | Location | Status | Residual risk |
|---|---|---|---|---|---|
| R1-M1 | Clarify whether the paper is primarily about boiling hysteresis or MEB diagnostics. | Framed the manuscript as a time-resolved MEB diagnostics paper, with heating/cooling hysteresis treated as a supporting boiling-curve observation rather than the central claim. | Abstract; Introduction; Results 3.1 | Resolved | Full-history hysteresis panels may still be useful as supplementary material. |
| R1-M2 | Strengthen operational MEB classification. | Added an explicit bridge from the local "developed oscillatory MEB-like" criteria to literature MEB signatures: fine microbubble emission, vapor collapse in subcooled liquid, high heat flux, acoustic activity, and oscillatory vapor/thermal behavior. | Section 2; Table 3 discussion | Resolved | Classification remains operational because the dataset has four tests. |
| R1-M3 | Add hydrophone band-sensitivity check for the 0-6 kHz integration band. | Ran a focused sensitivity analysis from raw hydrophone LVM files for Cases C and D using 0-3, 0-6, and 0-10 kHz integration bands. Added the stable modulation-frequency result to methods, results, limitations, and conclusions. Saved the table as `generated/publication_analysis/hydrophone_band_sensitivity_publication.csv`. | Sections 2, 3.3, 4-5; generated sensitivity CSV | Resolved | The sensitivity check covers developed cases only, which is appropriate because lower-power cases are not assigned MEB modulation frequencies. |
| R1-M4 | Make video-frame selection reproducible. | Added frame count, screening interval, fixed ROI statement, sampling interval, metric components, metric ranges, and hydrophone-power percentile ranges from generated screening CSVs. | Section 3.6; Fig. 8 caption | Resolved | Visual metric remains a ranking metric, not bubble-volume segmentation. |
| R1-M5 | Caveat heat-flux overshoot beyond nominal load. | Reframed overshoot as reconstructed transient wall heat-flux excursions from embedded thermocouple gradients; added direct caution that it is not direct calorimetric proof of cycle-averaged heat removal above input and identified cycle energy balance as final quantitative check. | Sections 3.1, 3.6, 4; Conclusion | Resolved for wording; partial for quantitative proof | A cycle-integrated energy-balance analysis would strengthen the claim. |
| R1-M6 | Separate acoustic power from calibrated acoustic power. | Replaced broad acoustic-power language with "band-integrated voltage-PSD power proxy" or "relative acoustic-power proxy" throughout abstract, methods, results, captions, and conclusions. | Abstract; Sections 2, 3.3-3.6, 4-5; Figs. 4-6 captions | Resolved | Absolute acoustic comparison still needs calibration. |
| R1-M7 | Avoid overinterpreting the LC/storage-release model. | Labeled the model as conceptual and illustrative, stated parameters are not fitted, and clarified it is consistent with observations rather than evidence for the mechanism. | Section 3.6; Fig. 9 caption; Limitations | Resolved | Predictive model requires future parameter identification. |
| R1-M8 | Connect uncertainty to figures and conclusions. | Added Figure 1 caption instruction to include `T_w` and `q''` uncertainty bars/bands from Table 6 and retained calibration-limited caveats in conclusions. | Fig. 1 caption; Section 4; Conclusion | Partial | Figure files themselves still need uncertainty rendering before final submission. |
| R1-M9 | Distinguish verified/digitized/provisional literature values. | Revised literature comparison text to distinguish text-reported, digitized, range-endpoint, and figure-verification-needed values; called for visually distinct legend categories. | Section 3.7; Fig. 7 caption | Partial | Figure legend may need regeneration if current panel does not visually separate all source-status categories. |
| R1-M10 | Resolve encoding/formatting issues and unit consistency. | Confirmed manuscript source uses proper degree symbols in the file search; verifier should check final LaTeX/PDF rendering. | Nomenclature; Table 1; Table 6 | Pending verifier | Console output may display `Â°C` even when UTF-8 source is correct. |

## Human-Pause Candidates

The following items should not be invented in prose and may require additional analysis before the loop can reach full submission readiness:

1. Cycle-integrated transient energy-balance sanity check for reconstructed heat-flux overshoot.
2. Regenerated publication figures with uncertainty bars/bands and final source-status legend categories.

## Round 1 Verifier Notes

- Regenerated `overleaf/main.tex` from `manuscript_draft.md`.
- Rebuilt the Elsevier `elsarticle` PDF with `pdflatex -> bibtex -> pdflatex -> pdflatex`.
- Final LaTeX log check found no unresolved citations, unresolved references, LaTeX errors, emergency stops, or fatal errors.
- Abstract word count is 250 words using the verification tokenizer.
- Source scan found no `Â°C` encoding artifact in the Markdown or regenerated LaTeX source.
- Hydrophone band-sensitivity table was generated from raw hydrophone LVM files and saved as `manuscripts/meb_multimodal_diagnostics/generated/publication_analysis/hydrophone_band_sensitivity_publication.csv`.

## Round 1 Re-Review Decision

Recommendation after author revision and verification: **Minor Revision / Human-Pause for final submission polish**.

The revision resolves the most important manuscript-level risks: the paper identity is clearer, MEB-like classification is tied to literature signatures, acoustic metrics are consistently treated as voltage-PSD proxies, video-frame screening is reproducible, hydrophone band sensitivity is now analyzed, and the storage-release model is clearly conceptual. The remaining items are not fatal to the manuscript argument, but they should be completed before submission if the goal is a polished Applied Thermal Engineering package:

1. Add uncertainty bars/bands to the final publication figure files where available, especially boiling-curve or maximum-heat-flux comparisons.
2. Ensure Fig. 7 visually distinguishes text-reported, digitized, range-endpoint, and figure-verification-needed literature values.
3. Decide whether to add a short cycle-integrated energy-balance sanity check or keep the current caveated language for reconstructed heat-flux overshoot.

The manuscript is now scientifically more defensible, but the loop should pause before final submission because item 3 is partly an author-positioning decision: either invest in an additional energy-balance analysis or keep the claim explicitly qualitative and filtered/reconstructed.

## Round 2 Author Response Log

| ID | Reviewer concern | Author action | Location | Status | Residual risk |
|---|---|---|---|---|---|
| R2-M1 | Final figures should carry uncertainty/source-status rigor rather than only caption promises. | Regenerated the Figure 1 plotting logic to add representative expanded uncertainty bars (`k = 2`) at each case's maximum reconstructed heat flux. Regenerated Figure 7 plotting logic so marker shape identifies source status while color identifies source/study. | `scripts/make_manuscript_draft_figures.py`; Fig. 1 and Fig. 7 captions | Resolved pending render verification | Figure 7 remains a screening comparison, not a formal meta-analysis. |
| R2-M2 | Heat-flux overshoot explanation is plausible but needs either an energy-balance check or a more conservative framing. | Kept the storage-release explanation as a physical interpretation, but explicitly stated that overshoot is supporting evidence from filtered reconstructed heat flux rather than direct calorimetric proof. Added the cycle-integrated energy balance as the next quantitative step. | Section 3.6; Conclusions | Resolved by conservative framing | A future cycle-integrated energy-balance closure would strengthen the mechanism claim. |
| R2-M3 | Title should better signal a diagnostics-workflow contribution. | Revised title from a broad time-resolved diagnostics title to a synchronized thermal-acoustic diagnostic workflow title. | Title | Resolved | None. |
| R2-M4 | Video evidence is qualitative and should not overclaim. | Clarified Table 3 video support as screened frames that support intermittent release. Retained text that the frame metric ranks frames and is not a bubble-volume measurement. | Table 3; Section 3.6 | Resolved | Quantitative segmentation remains future work. |
| R2-M5 | Literature comparison should remain contextual and source-status categories should stay visible. | Revised Fig. 7 caption and results text to state that source colors identify studies and marker shapes identify reported/extracted values, range endpoints, and present reduced data. | Section 3.7; Fig. 7 caption; plotting code | Resolved pending render verification | Highest-priority points should still be verified against source figures before final scaling claims. |
| R2-M6 | Acoustic proxy terminology needs to stay precise. | Revised Table 6 entries to "Hydrophone voltage-PSD power proxy" and "AE waveform voltage-PSD power proxy" and described them as acoustic activity metrics rather than calibrated acoustic power. | Table 6 | Resolved | Absolute acoustic intensity still requires calibration. |
| R2-M7 | Data availability should be journal-facing. | Added explicit language that processed data and code are available through repositories and raw data can be made available upon reasonable request subject to archive-access constraints. | Data and Code Availability | Resolved | Final wording may need coauthor/institutional approval before submission. |

## Round 2 Verifier Notes

- Regenerated draft manuscript figures. Figure 1 now includes representative expanded uncertainty bars, and Figure 7 uses source-status marker shapes.
- Regenerated `overleaf/main.tex` from `manuscript_draft.md` and copied the revised figure PDFs into the Overleaf folder.
- Rebuilt the Elsevier `elsarticle` PDF with `pdflatex -> bibtex -> pdflatex -> pdflatex`.
- Final LaTeX log scan found no unresolved citations, unresolved references, LaTeX errors, emergency stops, fatal errors, overfull boxes, or UTF-8 encoding artifacts.
- Rebuilt the Overleaf upload package at `manuscripts/meb_multimodal_diagnostics/overleaf/meb_multimodal_ate_overleaf.zip`.

## Round 2 Re-Review Decision

Recommendation after author revision and verification: **Accept after minor editorial/coauthor polish**.

The manuscript now addresses the actionable reviewer concerns with revised text, regenerated figures, and an auditable response log. Remaining risks are appropriate for final human/coauthor review rather than another automated revision loop: raw-data availability wording should be approved by the group, and the heat-flux overshoot mechanism remains intentionally framed as a conservative storage-release interpretation pending a future cycle-integrated energy-balance closure.

## Round 3 Author Response Log

| ID | Reviewer concern | Author action | Location | Status | Residual risk |
|---|---|---|---|---|---|
| R3-M1 | Add a nomenclature. | Expanded the Markdown nomenclature and updated the Overleaf converter so the nomenclature is included before the Introduction. Added reduced-order model symbols and storage-release heat-flux terms. | Nomenclature; `scripts/convert_manuscript_to_overleaf.py`; `overleaf/main.tex` | Resolved | Final symbol set should be checked by coauthors before submission. |
| R3-M2 | Fig. 1 should not show error bars on the curves; show only a maximum-error marker. | Replaced per-case curve uncertainty bars with a single maximum expanded-uncertainty marker in the lower-right corner of each Fig. 1 panel. | `scripts/make_manuscript_draft_figures.py`; Fig. 1 | Resolved | Marker represents maximum `k = 2` thermal uncertainty, not point-by-point uncertainty. |
| R3-M3 | Fig. 1 should use current Fig. 1b as Fig. 1a and add full-history heating/cooling Fig. 1b. | Rebuilt Fig. 1 as heating-only wall-superheat boiling curves in panel (a) and full-history curves in panel (b), with dashed cooling branches. | Fig. 1; Section 3.1 | Resolved | Full-history branch is interpreted as hysteresis/cooldown, not active boiling performance. |
| R3-M4 | Discuss heating/cooling discrepancy and MEB entry/return. | Added a hysteresis discussion explaining entry into developed oscillatory MEB-like behavior during heating and non-retracing cooling after shutoff because of vapor collapse, rewetting, liquid replenishment, and stored thermal energy. | Section 3.1; Conclusions | Resolved | Mechanistic interpretation remains qualitative. |
| R3-M5 | Explain why both Figs. 2 and 3 are needed. | Added text that Fig. 2 shows the highest-power developed case, while Fig. 3 tests reproducibility at the lower developed power and reveals different oscillation-window and envelope-saturation behavior. | Section 3.2 | Resolved | None. |
| R3-M6 | Move `P_load` labels out of spectrograms and into panel labels. | Removed in-panel spectrogram overlays and added power-load text to external panel labels for hydrophone and AE spectrogram panels. | Figs. 4-5; plotting code; captions | Resolved | None. |
| R3-M7 | Add a raw-data figure showing the envelope extraction. | Added new Fig. 6 showing detrended raw thermal oscillations, Hilbert envelopes, and asymptotic envelope fits; moved compact envelope metrics to Fig. 7. | Figs. 6-7; Section 3.5 | Resolved | Current showcase focuses on thermal signals; acoustic metrics remain in Fig. 7. |
| R3-M8 | Equation alignment is inconsistent. | Converted the storage-release equation block from a standalone `align` environment to centered `equation` + `aligned`. | `scripts/convert_manuscript_to_overleaf.py`; Eq. storage-release | Resolved | Verified by LaTeX build. |
| R3-M9 | Greek letter Xi was not rendered properly. | Added converter mappings for `xi`, `Theta`, `Phi`, `H`, `K_eff`, and `R_eff`; verified no stale `\texttt{xi}` or related literal rendering remains in `main.tex`. | Converter; `overleaf/main.tex` | Resolved | Verified by source scan and PDF build. |
| R3-M10 | Fig. 8 is weak; fit the model to data if possible. | Replaced the standalone conceptual model figure with a data-constrained oscillatory surrogate fit using the measured asymptotic envelope and a least-squares slow oscillation frequency. Added the fit metrics CSV. | Fig. 8; Section 3.6; `fig08_storage_release_fit_metrics.csv` | Resolved with conservative scope | R^2 values are modest; text frames the result as a consistency test, not a calibrated predictive model. |
| R3-M11 | Literature comparison should use full boiling curves where papers report them. | Revised literature section to state that the current plot is a first-pass screening compilation and that many papers should be digitized branch-by-branch before cross-study scaling. Added full boiling-curve trace as a literature-compiler field. | Section 3.7; Table 5; Fig. 9 caption | Partially resolved / human-pause | Full curve digitization from the literature remains a separate manual extraction task. |

## Round 3 Verifier Notes

- Regenerated manuscript figures with the mounted raw data. Figure 1 now includes heating-only and full-history panels; Figures 4-5 use external power-load panel labels; Figure 6 shows raw envelope extraction; Figure 8 shows the fitted oscillatory surrogate.
- Regenerated `overleaf/main.tex` and copied active figure PDFs into the Overleaf folder.
- Built the Elsevier `elsarticle` PDF as `main_revised.pdf` because `main.pdf` was locked by another application.
- Final LaTeX log scan found no unresolved citations, unresolved references, LaTeX errors, emergency stops, fatal errors, or overfull boxes.
- Source scan found no stale literal `\texttt{xi}`, old representative-frame Fig. 8 reference, or old storage-release model Fig. 9 reference.

## Round 3 Re-Review Decision

Recommendation after author revision and verification: **Minor editorial/coauthor review before submission**.

The latest comments are substantially addressed. The main remaining human-pause item is full digitization of published MEB boiling curves, which should be treated as a separate literature-compilation task before making stronger cross-study claims.

## Round 4 Author Response Log: Option B Literature-Curve Extraction

| ID | Reviewer/user concern | Author action | Location | Status | Residual risk |
|---|---|---|---|---|---|
| R4-M1 | The literature comparison should not merely admit that full published boiling curves remain undigitized; it should extract more data from the available literature and improve the figure. | Added `literature_digitized_curves.csv` with 60 approximate curve points digitized from rendered local PDFs for Ando et al. 2016, Zhu et al. 2014, Horiuchi et al. 2021, and Zhao et al. 2025. The new rows include curve IDs, system group, subcooling, geometry, branch, extraction method, status, confidence, and notes. | `literature-compiler/examples/test2_meb/data/literature_digitized_curves.csv` | Resolved for screening manuscript comparison | Points are manual render-based digitizations and should be redigitized with calibrated axes before regression or formal meta-analysis. |
| R4-M2 | The manuscript figure should show literature curve traces, not only individual literature points. | Updated the publication-analysis and draft-figure scripts to merge digitized curve rows, connect source-digitized curve traces, use source-specific citation labels, and show dotted traces for geometry-separated microchannel context. | `scripts/run_manuscript_publication_analysis.py`; `scripts/make_manuscript_draft_figures.py`; regenerated Fig. 9 | Resolved | Fig. 9 remains a screening/context panel rather than a finalized systematic-review plot. |
| R4-M3 | The manuscript text should actively interpret the improved literature comparison. | Revised Section 3.7, Fig. 9 caption, and limitations to state which studies were digitized, how the present data compare with published pool-boiling and microchannel curves, and what metadata are still needed for quantitative cross-study scaling. | `manuscripts/meb_multimodal_diagnostics/manuscript_draft.md`; regenerated `overleaf/main.tex` | Resolved | Final wording should be checked by coauthors after calibrated literature redigitization. |
| R4-M4 | The literature-compiler case should preserve provenance. | Updated the `test2_meb` README and screening notes to describe the new curve table and distinguish reported text, range endpoints, approximate figure-digitized curves, and future calibrated redigitization needs. | `literature-compiler/examples/test2_meb/README.md`; `screening_notes.md` | Resolved | Local rendered PDF crops remain uncommitted reference artifacts. |

## Round 4 Verifier Notes

- `literature_digitized_curves.csv` schema check passed: 60 rows, four source studies, eight curve IDs, numeric wall-superheat, heat-flux, and confidence fields.
- Python syntax compilation passed for `run_manuscript_publication_analysis.py`, `make_manuscript_draft_figures.py`, and `convert_manuscript_to_overleaf.py`.
- Regenerated publication-analysis tables and draft figures from the raw BoilingLab data and the updated `test2_meb` literature compilation.
- Visually checked the regenerated `fig09_literature_context.png`; it now includes connected literature boiling-curve traces, source-specific labels, and a source-status legend.
- Regenerated the Elsevier Overleaf source. Direct `main.pdf` output was locked by another application, so LaTeX was compiled as `main_optionb.pdf`.
- `main_optionb.pdf` built successfully with `pdflatex -> bibtex -> pdflatex -> pdflatex`; the final log scan found no unresolved references, undefined citations, LaTeX errors, emergency stops, or fatal errors. One small 1.57 pt overfull hbox remains in prose and is cosmetic.
- Rebuilt `overleaf/meb_multimodal_ate_overleaf.zip` from the current `main.tex`, references, highlights, Elsevier class/style files, and updated figure PDFs.
