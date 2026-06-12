# Overleaf package

This folder is generated from `../manuscript_draft.md` by running:

```powershell
python ../../../scripts/convert_manuscript_to_overleaf.py
```

Upload `main.tex`, `references.bib`, `highlights.tex`, and the figure PDFs to
Overleaf. The source uses the Elsevier `elsarticle` class in review mode for an
Applied Thermal Engineering submission draft.

Notes:
- Figure PDFs are copied to the same folder as `main.tex`. Elsevier's LaTeX
  submission instructions note that Editorial Manager cannot process figure
  subfolders reliably.
- `highlights.tex` is a separate editable file because Applied Thermal
  Engineering requires Highlights at submission.
- The author list, funding, acknowledgements, and calibration-specific
  uncertainty language remain placeholders for final submission.
- Internal workflow sections from the Markdown draft, such as the remaining
  work list and draft figure plan, are intentionally omitted from `main.tex`.
