# src.utils.constants:is_modern_sprint_weekend
function, src/utils/constants.py:307, 3 lines

```python
def is_modern_sprint_weekend(year: int, gp_name: str) -> bool
```

Sprint weekend using 2022+ format: FP1+SQ+S practice (no FP2/FP3 exist).

calls internal: is_sprint_weekend
reads internal: LEGACY_SPRINT_YEARS

referenced by: 1 sites in 1 modules (src.evo_predictor.module_training_evidence_modes)
