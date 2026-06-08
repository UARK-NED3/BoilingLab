# Boiling-412/413/416/417 Multi-Case Demo

This demo compares boiling curves for four subcooled, open-to-atmosphere,
flat-copper tests:

- `Boiling-412`: `150 W`
- `Boiling-413`: `180 W`
- `Boiling-416`: `230 W`
- `Boiling-417`: `250 W`

Run the comparison from the repository root:

```powershell
python scripts\run_multi_case_comparison.py
```

Generated outputs are written to:

```text
demos\Boiling-412-413-416-417\generated
```

The two primary comparison plots are:

- heat flux vs. wall temperature
- heat flux vs. wall superheat

The test log marks all four demo cases as `Failure: CHF not reached`, so these
plots are for comparing curve shape and heat-load response rather than ranking
confirmed CHF values.
