"""Build a self-contained Overleaf package for the MEB manuscript.

The manuscript is drafted in Markdown because it is convenient during analysis.
This script converts the current draft into an Elsevier `elsarticle`
one-column package following the common `elstest-1p` style, with copied figure
PDFs, BibTeX styles, class file, highlights, and a BibTeX database.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIR = ROOT / "manuscripts" / "meb_multimodal_diagnostics"
SOURCE_MD = MANUSCRIPT_DIR / "manuscript_draft.md"
OVERLEAF_DIR = MANUSCRIPT_DIR / "overleaf"
ELSARTICLE_TEMPLATE_DIR = ROOT / "vendor" / "elsarticle"
ELSARTICLE_FILES = [
    "elsarticle.cls",
    "elsarticle-num.bst",
    "elsarticle-num-names.bst",
    "elsarticle-harv.bst",
]


FIGURES = {
    "1": (
        "fig01_heating_boiling_curves.pdf",
        "Boiling curves for the four cases. Panel (a) shows heating-only "
        "$q''$ versus wall superheat using samples with positive DC power. "
        "Panel (b) shows the full thermal history; solid lines are heating "
        "before power shutoff and dashed lines are cooling after shutoff. "
        "The corner marker gives the maximum expanded uncertainty ($k=2$) "
        "for $T_w$ and $q''$ among the four cases.",
    ),
    "2": (
        "fig02_case_d_thermal_time_histories.pdf",
        "Thermal time histories for the highest-power case. Panel (a) shows "
        "heat flux and power load versus time. Panel (b) shows embedded "
        "thermocouple temperatures and extrapolated wall temperature. Dashed "
        "vertical markers identify $t_{\\mathrm{DNB}}$, $t_{\\mathrm{peak}}$, "
        "$t_{\\mathrm{osc}}$, and $t_{\\mathrm{off}}$; $t_{\\mathrm{DNB}}$ "
        "is used as an operational transition-associated heat-flux maximum.",
    ),
    "3": (
        "fig03_case_c_thermal_time_histories.pdf",
        "Thermal time histories for the second developed high-power case, "
        "plotted with the same definitions and event markers as Fig.~\\ref{fig:2}.",
    ),
    "4": (
        "fig04_hydrophone_diagnostics.pdf",
        "Hydrophone diagnostics for the active-heating cases. The panels "
        "summarize spectrograms, band-integrated PSD power, and characteristic "
        "frequencies. The band-integrated power is computed by integrating the "
        "linear voltage PSD over 0--6 kHz before any logarithmic display. "
        "Slow MEB modulation frequencies are interpreted only for the developed "
        "high-power cases.",
    ),
    "5": (
        "fig05_ae_waveform_diagnostics.pdf",
        "Acoustic-emission waveform diagnostics for the two cases with available "
        "waveform files. The panels summarize AE spectrograms, band-integrated "
        "PSD power, and characteristic frequencies using the same event-window "
        "logic as the hydrophone analysis.",
    ),
    "6": (
        "fig06_envelope_showcase.pdf",
        "Raw detrended oscillations and envelope extraction for the developed "
        "high-power cases. Gray traces are detrended thermal signals; colored "
        "curves show the Hilbert envelope and the fitted asymptotic envelope. "
        "The negative fitted envelope is shown as a dotted guide to visualize "
        "the oscillation amplitude.",
    ),
    "7": (
        "fig07_envelope_growth.pdf",
        "Oscillation-envelope growth and saturation metrics for the developed "
        "high-power cases. Normalized envelopes show the different thermal "
        "and acoustic growth behavior, while the bar chart compares fitted "
        "time constants.",
    ),
    "8": (
        "fig08_storage_release_fit.pdf",
        "Data-constrained oscillatory surrogate for the developed MEB-like "
        "regime. The fitted surrogate uses the asymptotic envelope from "
        "Fig.~\\ref{fig:6} multiplied by a sinusoidal release coordinate and "
        "is compared with detrended wall-temperature and heat-flux oscillations. "
        "The fit is phenomenological and is used to test whether the proposed "
        "storage-release picture can reproduce the observed slow oscillation "
        "scale.",
    ),
    "9": (
        "fig09_literature_context.pdf",
        "Source-status-labeled literature context for the present data. "
        "The heat-transfer panel includes reported values, range endpoints, "
        "approximate figure-digitized boiling-curve traces from selected "
        "published MEB studies, and present reduced data. Dotted traces denote "
        "geometry-separated context. The signature panel separates heat-transfer "
        "quantities from acoustic or oscillatory quantities because reported "
        "frequencies may describe different physical scales.",
    ),
}


FIGURE_SOURCES = {
    name: MANUSCRIPT_DIR / "generated" / "draft_figures" / name
    for name, _caption in FIGURES.values()
}


BIBTEX = r"""
@article{tang_2016_transition_to_meb,
  author = {Ando, J. and Horiuchi, K. and Saiki, T. and Kaneko, T. and Ueno, I.},
  title = {Transition process leading to microbubble emission boiling on horizontal circular heated surface in subcooled pool},
  journal = {International Journal of Heat and Mass Transfer},
  year = {2016},
  doi = {10.1016/j.ijheatmasstransfer.2016.05.050}
}

@article{baek_2017_ae_water_boiling_cladding,
  author = {Baek, W. P. and others},
  title = {Acoustic emission monitoring of water boiling on fuel cladding surface at 1 bar and 130 bar},
  journal = {Measurement},
  year = {2017},
  doi = {10.1016/j.measurement.2017.05.042}
}

@article{brennen_2002_fission_cavitation,
  author = {Brennen, C. E.},
  title = {Fission of collapsing cavitation bubbles},
  journal = {Journal of Fluid Mechanics},
  volume = {472},
  pages = {153--166},
  year = {2002}
}

@book{carey_2020_phase_change,
  author = {Carey, V. P.},
  title = {Liquid-Vapor Phase-Change Phenomena: An Introduction to the Thermophysics of Vaporization and Condensation Processes in Heat Transfer Equipment},
  edition = {3},
  publisher = {CRC Press},
  year = {2020}
}

@article{elele_2018_single_bubble_boiling,
  author = {Elele, E. and others},
  title = {Single-bubble water boiling on small heater under Earth's and low gravity},
  journal = {npj Microgravity},
  year = {2018},
  doi = {10.1038/s41526-018-0055-y}
}

@techreport{gunther_1950_subcooled_bubble_photography,
  author = {Gunther, F. C. and Kreith, F.},
  title = {Photographic study of bubble formation in heat transfer to subcooled water},
  institution = {Jet Propulsion Laboratory},
  type = {Progress Report},
  year = {1950}
}

@article{horiuchi_2021_spatial_temporal_thermal_fluid,
  author = {Horiuchi, K. and others},
  title = {Spatial-temporal thermal-fluid behaviors of microbubble emission boiling (MEB)},
  journal = {AIChE Journal},
  year = {2021},
  doi = {10.1002/aic.17193}
}

@article{inada_1981_subcooled_pool_boiling,
  author = {Inada, S. and Miyasaka, Y. and Izumi, R. and Owase, Y.},
  title = {A study on boiling curves in subcooled pool boiling},
  journal = {Transactions of the Japan Society of Mechanical Engineers},
  volume = {47},
  pages = {852--861},
  year = {1981}
}

@article{inada_2016_cavitation_bubble_blow_pit,
  author = {Inada, S. and Shinagawa, K. and Illias, S. B. and Sumiya, H. and Jalaludin, H. A.},
  title = {Micro-bubble emission boiling with the cavitation bubble blow pit},
  journal = {Scientific Reports},
  year = {2016},
  doi = {10.1038/srep33454}
}

@inproceedings{ivey_1966_subcooled_chf,
  author = {Ivey, H. J. and Morris, D. J.},
  title = {Critical heat flux of saturation and subcooled pool boiling in water at atmospheric pressure},
  booktitle = {Proceedings of the Third International Heat Transfer Conference},
  year = {1966}
}

@article{kawakami_2025_high_frequency_oscillation,
  author = {Kawakami, T. and others},
  title = {High-frequency oscillation of coalesced vapor bubbles and resultant ambient liquid motion in microbubble emission boiling in subcooled pool},
  journal = {International Journal of Heat and Mass Transfer},
  year = {2025},
  doi = {10.1016/j.ijheatmasstransfer.2025.126832}
}

@article{kobayashi_2022_on_homogeneity_of_vapor_bubble,
  author = {Kobayashi, H. and Hayashi, M. and Kurose, K. and Ueno, I.},
  title = {On homogeneity of vapor bubbles' oscillation and corresponding heat transfer characteristics and boiling sound in microbubble emission boiling (MEB)},
  journal = {International Journal of Heat and Mass Transfer},
  year = {2022},
  doi = {10.1016/j.ijheatmasstransfer.2022.122564}
}

@article{li_2022_oscillating_vapor_film,
  author = {Li, X. and Tang, J. G. and Hu, R. and Sun, L. C. and Bao, J. J.},
  title = {Investigation on interaction between an oscillating vapor film and its surrounding liquid in microbubble emission boiling},
  journal = {Applied Thermal Engineering},
  year = {2022},
  doi = {10.1016/j.applthermaleng.2022.119012}
}

@article{liang_2018_chf_review,
  author = {Liang, G. and Mudawar, I.},
  title = {Pool boiling critical heat flux (CHF) -- Part 1: Review of mechanisms, models, and correlations},
  journal = {International Journal of Heat and Mass Transfer},
  volume = {117},
  pages = {1352--1367},
  year = {2018}
}

@article{litvintsova_2020_boiling_onset_fluctuations,
  author = {Litvintsova, A. and others},
  title = {Diagnostics of coolant boiling onset based on the analysis of fluctuations of thermohydraulic parameters},
  journal = {Journal of Physics: Conference Series},
  year = {2020},
  doi = {10.1088/1742-6596/1689/1/012042}
}

@article{liu_2020_pin_cluster_nucleation,
  author = {Liu, P. and others},
  title = {Enhanced nucleate pool boiling by coupling the pinning act and cluster bubble nucleation of micro-nano composited surfaces},
  journal = {International Journal of Heat and Mass Transfer},
  year = {2020},
  doi = {10.1016/j.ijheatmasstransfer.2020.119979}
}

@article{mao_2021_flow_boiling_instabilities_review,
  author = {Mao, Y. and others},
  title = {A critical review on measures to suppress flow boiling instabilities in microchannels},
  journal = {Heat and Mass Transfer},
  year = {2021},
  doi = {10.1007/s00231-020-03009-2}
}

@article{ono_2023_acoustic_state_detection_meb,
  author = {Ono, J. and Aoki, Y. and Unno, N. and Yuki, K. and Suzuki, K. and Ueki, Y. and Satake, S.},
  title = {Acoustic state detection of microbubble emission boiling using a deep neural network based on cepstrum analysis},
  journal = {International Journal of Multiphase Flow},
  year = {2023},
  doi = {10.1016/j.ijmultiphaseflow.2023.104512}
}

@article{sinha_2020_audio_visual_thermal_transition,
  author = {Sinha, K. N. R. and Kumar, V. and Kumar, N. and Thakur, A. and Raj, R.},
  title = {Simultaneous audio-visual-thermal characterization of transition boiling regime},
  journal = {Experimental Thermal and Fluid Science},
  year = {2020},
  doi = {10.1016/j.expthermflusci.2020.110162}
}

@article{sinha_2021_deep_learning_sound_boiling,
  author = {Sinha, K. N. R. and Kumar, V. and Kumar, N. and Thakur, A. and Raj, R.},
  title = {Deep learning the sound of boiling for advance prediction of boiling crisis},
  journal = {Cell Reports Physical Science},
  year = {2021},
  doi = {10.1016/j.xcrp.2021.100382}
}

@article{tang_2023_bubble_induced_oscillating_flow,
  author = {Tang, J. and Li, X. and Xu, L. and Sun, L.},
  title = {Bubble-induced oscillating flow in microbubble emission boiling under highly subcooled conditions},
  journal = {Journal of Fluid Mechanics},
  year = {2023},
  doi = {10.1017/jfm.2023.285}
}

@article{tang_2019_transient_nucleate_to_meb,
  author = {Tang, J. and Sun, L. and Du, M. and Liu, H. and Mo, Z. and Bao, J.},
  title = {Experimental investigation of transition process from nucleate boiling to microbubble emission boiling under transient heating modes},
  journal = {AIChE Journal},
  year = {2019},
  doi = {10.1002/aic.16555}
}

@article{tang_2018_sound_emission_subcooled_pool,
  author = {Tang, J. and Xie, G. and Bao, J. and Mo, Z. and Liu, H. and Du, M.},
  title = {Experimental study of sound emission in subcooled pool boiling on a small heating surface},
  journal = {Chemical Engineering Science},
  year = {2018},
  doi = {10.1016/j.ces.2018.05.002}
}

@article{unno_2022_surface_properties_meb_onset,
  author = {Unno, N. and Noma, R. and Yuki, K. and Satake, S. and Suzuki, K.},
  title = {Effects of surface properties on wall superheat at the onset of microbubble emission boiling},
  journal = {International Journal of Multiphase Flow},
  year = {2022},
  doi = {10.1016/j.ijmultiphaseflow.2022.104196}
}

@article{unno_2025_reduced_pressure_confined_meb,
  author = {Unno, N. and Yuki, K. and Suzuki, K.},
  title = {Onset of microbubble emission boiling at reduced pressure using a confined vessel for subcooled pool boiling},
  journal = {International Journal of Heat and Mass Transfer},
  year = {2025},
  doi = {10.1016/j.ijheatmasstransfer.2024.126600}
}

@article{ueki_2024_acoustic_state_cucrzr_divertor,
  author = {Ueki, Y. and others},
  title = {Acoustic state sensing of subcooled boiling heat transfer on a CuCrZr surface using a deep neural network for divertor application},
  journal = {Fusion Science and Technology},
  year = {2024},
  doi = {10.1080/15361055.2024.2435193}
}

@article{zeigarnik_2012_microbubble_emission_nature,
  author = {Zeigarnik, Y. A. and Platonov, D. N. and Khodakov, K. A. and Shekhter, Y. L.},
  title = {The nature of microbubble emission under subcooled water boiling},
  journal = {High Temperature},
  year = {2012},
  doi = {10.1134/S0018151X12010208}
}

@article{zhao_2025_open_microchannel_meb,
  author = {Zhao, Q. and Lu, M. and Zhang, Y. and Li, Q. and Chen, X.},
  title = {Flow microbubble emission boiling (MEB) in open microchannels for durable and efficient heat dissipation},
  journal = {International Journal of Heat and Mass Transfer},
  year = {2025},
  doi = {10.1016/j.ijheatmasstransfer.2024.126506}
}

@article{zhu_2014_visualized_meb,
  author = {Zhu, G. and Sun, L. and Tang, J. and Mo, Z. and Liu, H.},
  title = {A visualized study of micro-bubble emission boiling},
  journal = {International Communications in Heat and Mass Transfer},
  year = {2014},
  doi = {10.1016/j.icheatmasstransfer.2014.10.003}
}

@article{zuber_1958_stability,
  author = {Zuber, N.},
  title = {On the stability of boiling heat transfer},
  journal = {Transactions of the ASME},
  volume = {80},
  pages = {711--714},
  year = {1958}
}

@techreport{zuber_1959_hydrodynamic,
  author = {Zuber, N.},
  title = {Hydrodynamic aspects of boiling heat transfer},
  institution = {University of California, Los Angeles},
  year = {1959}
}
""".strip()


MATH_MAP = {
    "A": "$A$",
    "A_0": "$A_0$",
    "A_inf": "$A_\\infty$",
    "C_eff": "$C_{\\mathrm{eff}}$",
    "f": "$f$",
    "L_eff": "$L_{\\mathrm{eff}}$",
    "P_load": "$P_{\\mathrm{load}}$",
    "q''": "$q''$",
    "T": "$T$",
    "T_sat": "$T_{\\mathrm{sat}}$",
    "T_w": "$T_w$",
    "t_DNB": "$t_{\\mathrm{DNB}}$",
    "t_off": "$t_{\\mathrm{off}}$",
    "t_osc": "$t_{\\mathrm{osc}}$",
    "t_peak": "$t_{\\mathrm{peak}}$",
    "tau": "$\\tau$",
    "Theta": "$\\Theta$",
    "xi": "$\\xi$",
    "H": "$H$",
    "Phi": "$\\Phi$",
    "K_eff": "$K_{\\mathrm{eff}}$",
    "R_eff": "$R_{\\mathrm{eff}}$",
}


def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def convert_inline(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"@@PLACEHOLDER{len(placeholders) - 1}@@"

    def code_repl(match: re.Match[str]) -> str:
        content = match.group(1)
        if content in MATH_MAP:
            return stash(MATH_MAP[content])
        if "/" in content or "\\" in content:
            return stash(r"\path{" + content.replace("\\", "/") + "}")
        return stash(r"\texttt{" + escape_latex(content) + "}")

    text = re.sub(r"`([^`]+)`", code_repl, text)
    text = text.replace("W/cm^2", stash(r"W/cm$^2$"))
    text = text.replace("V^2", stash(r"V$^2$"))
    text = text.replace("R^2", stash(r"$R^2$"))
    text = text.replace("degC", stash(r"$^\circ$C"))

    def cite_repl(match: re.Match[str]) -> str:
        keys = match.group(1)
        if "_" not in keys:
            return match.group(0)
        key_list = [part.strip() for part in re.split(r"[;,]", keys) if part.strip()]
        if not key_list:
            return match.group(0)
        return stash(r"\citep{" + ",".join(key_list) + "}")

    text = re.sub(r"\[([A-Za-z0-9_,; ]+)\]", cite_repl, text)
    text = escape_latex(text)
    text = text.replace("microbubble emission boiling (MEB)", "microbubble emission boiling (MEB)")
    text = text.replace("--", r"--")
    for idx, value in enumerate(placeholders):
        text = text.replace(f"@@PLACEHOLDER{idx}@@", value)
    return text


def strip_heading_number(heading: str) -> str:
    return re.sub(r"^\d+(\.\d+)?\.?\s*", "", heading).strip()


def figure_environment(fig_no: str) -> str:
    filename, caption = FIGURES[fig_no]
    return (
        "\\begin{figure}[H]\n"
        "  \\centering\n"
        f"  \\includegraphics[width=\\linewidth]{{{filename}}}\n"
        f"  \\caption{{{caption}}}\n"
        f"  \\label{{fig:{fig_no}}}\n"
        "\\end{figure}"
    )


def convert_table(caption: str | None, table_lines: list[str]) -> str:
    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    col_count = len(rows[0])
    align = "l" + "c" * (col_count - 1)
    out = ["\\begin{table}[t]", "  \\centering"]
    if caption:
        out.append(f"  \\caption{{{convert_inline(caption)}}}")
    out.append("  \\resizebox{\\textwidth}{!}{%")
    out.append(f"  \\begin{{tabular}}{{{align}}}")
    out.append("    \\toprule")
    out.append("    " + " & ".join(convert_inline(cell) for cell in rows[0]) + r" \\")
    out.append("    \\midrule")
    for row in rows[1:]:
        out.append("    " + " & ".join(convert_inline(cell) for cell in row) + r" \\")
    out.append("    \\bottomrule")
    out.append("  \\end{tabular}")
    out.append("  }")
    out.append("\\end{table}")
    return "\n".join(out)


def convert_nomenclature(md: str) -> str:
    try:
        section = extract_between(md, "## Nomenclature", r"^## 1\. Introduction")
    except ValueError:
        return ""
    table_lines = [line for line in section.splitlines() if line.startswith("|")]
    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    out = [
        "\\section*{Nomenclature}",
        "\\begin{center}",
        "\\small",
        "\\begin{tabular}{@{}p{0.16\\textwidth}p{0.56\\textwidth}p{0.16\\textwidth}@{}}",
        "\\toprule",
        "    " + " & ".join(convert_inline(cell) for cell in rows[0]) + r" \\",
        "\\midrule",
    ]
    for row in rows[1:]:
        out.append("    " + " & ".join(convert_inline(cell) for cell in row) + r" \\")
    out.extend(["\\bottomrule", "\\end{tabular}", "\\end{center}", "\\normalsize"])
    return "\n".join(out)


def convert_equation_block(lines: list[str]) -> str:
    joined = "\n".join(line.strip() for line in lines)
    if "A(t)" in joined:
        return (
            "\\begin{equation}\n"
            "A(t) = A_{\\infty} - \\left(A_{\\infty} - A_0\\right)"
            "\\exp\\left[-\\frac{t-t_{\\mathrm{osc}}}{\\tau}\\right].\n"
            "\\label{eq:envelope}\n"
            "\\end{equation}"
        )
    if "q''_out" in joined:
        return (
            "\\begin{equation}\n"
            "q''_{\\mathrm{out}} = q''_{\\mathrm{in}} - "
            "\\frac{\\mathrm{d}E_{\\mathrm{stored}}}{\\mathrm{d}t} - q''_{\\mathrm{loss}} .\n"
            "\\label{eq:energy-balance}\n"
            "\\end{equation}"
        )
    if "C_eff" in joined:
        return (
            "\\begin{equation}\n"
            "\\begin{aligned}\n"
            "C_{\\mathrm{eff}}\\frac{\\mathrm{d}\\Theta}{\\mathrm{d}t} &= "
            "q''_{\\mathrm{in}} - q''_{\\mathrm{release}}(\\Theta,\\xi) - q''_{\\mathrm{loss}}, \\\\\n"
            "L_{\\mathrm{eff}}\\frac{\\mathrm{d}^2\\xi}{\\mathrm{d}t^2} + "
            "R_{\\mathrm{eff}}\\frac{\\mathrm{d}\\xi}{\\mathrm{d}t} + "
            "K_{\\mathrm{eff}}\\xi &= F(\\Theta,\\xi), \\\\\n"
            "q''_{\\mathrm{release}} &= H(\\Theta-\\Theta_c)\\Phi\\left(\\xi,"
            "\\frac{\\mathrm{d}\\xi}{\\mathrm{d}t}\\right) .\n"
            "\\end{aligned}\n"
            "\\label{eq:storage-release}\n"
            "\\end{equation}"
        )
    return "\\begin{verbatim}\n" + "\n".join(lines) + "\n\\end{verbatim}"


def extract_between(md: str, start: str, end_pattern: str) -> str:
    start_index = md.index(start) + len(start)
    end_match = re.search(end_pattern, md[start_index:], flags=re.MULTILINE)
    end_index = start_index + end_match.start() if end_match else len(md)
    return md[start_index:end_index].strip()


def convert_body(md: str) -> str:
    body = extract_between(md, "## 1. Introduction", r"^## Data and Code Availability")
    body = "## 1. Introduction\n\n" + body
    lines = body.splitlines()
    out: list[str] = []
    pending_table_caption: str | None = None
    in_code = False
    code_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("```text"):
            in_code = True
            code_lines = []
            i += 1
            continue
        if in_code:
            if line.startswith("```"):
                out.append(convert_equation_block(code_lines))
                in_code = False
            else:
                code_lines.append(line)
            i += 1
            continue
        if not line:
            i += 1
            continue
        if line.startswith("## "):
            out.append(f"\\section{{{convert_inline(strip_heading_number(line[3:]))}}}")
        elif line.startswith("### "):
            out.append(f"\\subsection{{{convert_inline(strip_heading_number(line[4:]))}}}")
        elif line.startswith("**Table "):
            pending_table_caption = re.sub(r"^\*\*Table\s+\d+\.\s*(.*?)\.\*\*$", r"\1.", line)
        elif line.startswith("|"):
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            out.append(convert_table(pending_table_caption, table_lines))
            pending_table_caption = None
            continue
        elif line.startswith("**Figure "):
            fig_match = re.match(r"\*\*Figure\s+(\d+)\.", line)
            if fig_match and fig_match.group(1) in FIGURES:
                out.append(figure_environment(fig_match.group(1)))
        elif re.match(r"^\d+\.\s", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i]):
                items.append(re.sub(r"^\d+\.\s*", "", lines[i].strip()))
                i += 1
            out.append("\\begin{enumerate}")
            for item in items:
                out.append(f"  \\item {convert_inline(item)}")
            out.append("\\end{enumerate}")
            continue
        else:
            out.append(convert_inline(line))
        i += 1
    return "\n\n".join(out)


def build_main_tex(md: str) -> str:
    title_match = re.search(r"^#\s+(.+)", md, flags=re.MULTILINE)
    title = convert_inline(title_match.group(1).strip()) if title_match else (
        "Coupled Thermal and Acoustic Characterization of Energy Storage-Release Dynamics in Microbubble Emission Boiling"
    )
    abstract = extract_between(md, "## Abstract", r"^\*\*Keywords:")
    keywords_match = re.search(r"\*\*Keywords:\*\*\s*(.+)", md)
    keywords = keywords_match.group(1).strip() if keywords_match else ""
    keyword_tex = r" \sep ".join(convert_inline(part.strip()) for part in keywords.split(";"))
    nomenclature = convert_nomenclature(md)
    body = convert_body(md)
    data_availability = extract_between(md, "## Data and Code Availability", r"^## References")

    return rf"""\documentclass[final,1p,times]{{elsarticle}}

\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}
\usepackage{{siunitx}}
\usepackage{{adjustbox}}
\usepackage{{float}}
\usepackage{{hyperref}}

\journal{{Applied Thermal Engineering}}
\bibliographystyle{{elsarticle-num}}

\begin{{document}}

\begin{{frontmatter}}

\title{{{title}}}

\author[inst1]{{Mohamamd Ishraq Hossain}}
\author[inst1]{{Stephen Pierson}}
\author[inst1]{{Han Hu}}
\affiliation[inst1]{{organization={{Department of Mechanical Engineering, University of Arkansas}}, city={{Fayetteville}}, state={{AR}}, postcode={{72701}}, country={{USA}}}}
% \cortext[cor1]{{Corresponding author.}}
% \ead{{corresponding.author@example.edu}}

\begin{{abstract}}
{convert_inline(abstract)}
\end{{abstract}}

\begin{{keyword}}
{keyword_tex}
\end{{keyword}}

\input{{highlights}}

\end{{frontmatter}}

{nomenclature}

{body}

\section*{{Data and Code Availability}}

{convert_inline(data_availability)}

\section*{{Declaration of Competing Interest}}

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

\section*{{Acknowledgements}}

Acknowledgements and funding information will be added before submission.

\section*{{CRediT Authorship Contribution Statement}}

Author contributions will be finalized before submission using the CRediT taxonomy.

\section*{{Funding}}

Funding information will be added before submission in the standard Elsevier format.

\bibliography{{references}}

\end{{document}}
"""


def write_highlights() -> str:
    return r"""\begin{highlights}
\item Thermal-acoustic diagnostics identify developed microbubble emission boiling.
\item Hydrophone data separate slow regime modulation from collapse-frequency content.
\item Acoustic-emission waveforms confirm high-power modulation through a second path.
\item Envelope fits quantify growth and saturation of thermal oscillations.
\item Video frames support a vapor/thermal storage-release mechanism.
\end{highlights}
"""


def write_readme() -> str:
    return """# Overleaf package

This folder is generated from `../manuscript_draft.md` by running:

```powershell
python ../../../scripts/convert_manuscript_to_overleaf.py
```

Upload the full contents of this folder to Overleaf. The source uses the
Elsevier `elsarticle` class in the common `final,1p,times` layout corresponding
to the `elstest-1p.pdf` example from the Elsevier article template bundle.

Notes:
- `elsarticle.cls` and the Elsevier `.bst` files are included so the package is
  self-contained on Overleaf.
- Figure PDFs are copied to the same folder as `main.tex`. Elsevier's LaTeX
  submission instructions note that Editorial Manager cannot process figure
  subfolders reliably.
- `highlights.tex` is input inside the `frontmatter`, matching the Elsevier
  template convention for Highlights.
- The author list, funding, acknowledgements, and calibration-specific
  uncertainty language remain placeholders for final submission.
- Internal workflow sections from the Markdown draft, such as the remaining
  work list and draft figure plan, are intentionally omitted from `main.tex`.
"""


def main() -> None:
    md = SOURCE_MD.read_text(encoding="utf-8")
    OVERLEAF_DIR.mkdir(parents=True, exist_ok=True)
    old_figure_dir = OVERLEAF_DIR / "figures"
    if old_figure_dir.exists():
        shutil.rmtree(old_figure_dir)

    for filename, source in FIGURE_SOURCES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, OVERLEAF_DIR / filename)

    for filename in ELSARTICLE_FILES:
        source = ELSARTICLE_TEMPLATE_DIR / filename
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, OVERLEAF_DIR / filename)

    (OVERLEAF_DIR / "main.tex").write_text(build_main_tex(md), encoding="utf-8")
    (OVERLEAF_DIR / "references.bib").write_text(BIBTEX + "\n", encoding="utf-8")
    (OVERLEAF_DIR / "highlights.tex").write_text(write_highlights(), encoding="utf-8")
    (OVERLEAF_DIR / "README.md").write_text(write_readme(), encoding="utf-8")


if __name__ == "__main__":
    main()
