[map index](../INDEX.md) / [`src.utils.constants`](INDEX.md)

# `get_practice_session_types`
*function* [s] · [`src/utils/constants.py:312`](C:/Programs/f1Brainz/src/utils/constants.py#L312) · 22 lines [s]

**Signature** [s]

```python
def get_practice_session_types(year: int, gp_name: str) -> List[str]
```

> Return the ordered list of practice session types for a race weekend.
>
> Modern sprint weekends (2022+) use FP1 + sprint qualifying (SQ) + sprint race (S).
> Legacy sprint weekends (2021) used FP1 + FP2 — SQ/S session codes did not exist yet.
> Normal weekends use FP1 + FP2 + FP3.
> Q and R are never included — this is the canonical source for practice-only
> session pools used by feature builders and session dropout.
>
> Args:
>     year: Season year
>     gp_name: Grand Prix name
>
> Returns:
>     List of practice session type strings, e.g. ["FP1", "FP2", "FP3"]

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]
- `gp_name` — gp_name: Grand Prix name [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| calls | stdlib | `builtins.list` x3 |
| reads | internal | `LEGACY_SPRINT_PRACTICE_SESSIONS`, `LEGACY_SPRINT_YEARS`, `NORMAL_PRACTICE_SESSIONS`, `SPRINT_PRACTICE_SESSIONS` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 2 site(s) across 2 module(s) — src.evo_predictor.gold_cycle.runner_support, src.evo_predictor.module_training_orchestration


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
