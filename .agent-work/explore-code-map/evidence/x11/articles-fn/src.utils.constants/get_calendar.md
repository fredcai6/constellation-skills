[map index](../INDEX.md) / [`src.utils.constants`](INDEX.md)

# `get_calendar`
*function* [s] · [`src/utils/constants.py:263`](C:/Programs/f1Brainz/src/utils/constants.py#L263) · 16 lines [s]

**Signature** [s]

```python
def get_calendar(year: int) -> List[str]
```

> Get F1 calendar for a specific year.
>
> Args:
>     year: Season year
>
> Returns:
>     List of GP names in calendar order
>
> Raises:
>     KeyError: If year is not in calendars

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.KeyError`, `builtins.list` |
| reads | internal | `F1_CALENDARS` x3 |

*Not shown: 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 20 site(s) across 14 module(s) — src.evo_predictor.module_training_orchestration x3, src.evo_predictor.pipeline x3, src.data.collector x2, src.evo_predictor.recency_features x2, src.evo_predictor.data_adapter._build, src.evo_predictor.data_adapter._helpers, src.evo_predictor.data_adapter._memory, src.evo_predictor.module_training_evidence_modes, src.evo_predictor.sampled_backtest, src.physics.fit_batch, src.physics.ideal_lap.residuals, src.physics.layer2.estimate_batch, src.physics.layer2.grip_batch, src.physics.wear.batch


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
