# Overleaf package

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
