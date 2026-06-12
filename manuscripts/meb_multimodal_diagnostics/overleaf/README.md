# Overleaf package

This folder is generated from `../manuscript_draft.md` by running:

```powershell
python ../../../scripts/convert_manuscript_to_overleaf.py
```

Upload `main.tex`, `references.bib`, and the `figures/` folder to Overleaf. The
source uses the Elsevier `elsarticle` class for an Applied Thermal Engineering
preprint-style draft.

Notes:
- Figure PDFs are copied into `figures/` so the package is self-contained.
- The author list, funding, acknowledgements, and calibration-specific
  uncertainty language remain placeholders for final submission.
- Internal workflow sections from the Markdown draft, such as the remaining
  work list and draft figure plan, are intentionally omitted from `main.tex`.
