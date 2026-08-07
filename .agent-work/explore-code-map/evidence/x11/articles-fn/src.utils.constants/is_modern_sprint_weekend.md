[map index](../INDEX.md) / [`src.utils.constants`](INDEX.md)

# `is_modern_sprint_weekend`
*function* [s] · [`src/utils/constants.py:307`](C:/Programs/f1Brainz/src/utils/constants.py#L307) · 3 lines [s]

**Signature** [s]

```python
def is_modern_sprint_weekend(year: int, gp_name: str) -> bool
```

> Sprint weekend using 2022+ format: FP1+SQ+S practice (no FP2/FP3 exist).

**Parameters**

- `year` — *[HOLE] undocumented parameter*
- `gp_name` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| reads | internal | `LEGACY_SPRINT_YEARS` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) — src.evo_predictor.module_training_evidence_modes


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
