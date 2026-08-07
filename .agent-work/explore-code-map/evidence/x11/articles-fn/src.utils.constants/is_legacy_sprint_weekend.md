# src.utils.constants:is_legacy_sprint_weekend
function, src/utils/constants.py:302, 3 lines

```python
def is_legacy_sprint_weekend(year: int, gp_name: str) -> bool
```

Sprint weekend using 2021 format: FP1+FP2 practice (no SQ/S sessions exist).

calls internal: is_sprint_weekend
reads internal: LEGACY_SPRINT_YEARS

referenced by: 1 sites in 1 modules (src.evo_predictor.module_training_evidence_modes)
