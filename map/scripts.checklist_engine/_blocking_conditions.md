# scripts.checklist_engine:_blocking_conditions
function, scripts/checklist_engine.py:1487, 16 lines

```python
def _blocking_conditions(conds: list[dict]) -> list[dict]
```

The subset of `conds` that WILL make `start()`/`advance()` refuse right

now, from state() alone -- i.e. the conditions a `next:` hint must actually
account for before suggesting the terminal verb (rework 1, g2 review BLOCK:
the pre-fix `_next_verbs()` ignored this and suggested a verb that refused
immediately).

Only `null`/`artifact`-kind conditions qualify: `_check_condition()` never
re-runs them (their `satisfied` flag only moves via `attest`/`waive`), so an
open one here is a GUARANTEED refusal. `command`/`git-change-policy`
conditions are the opposite case: they are engine-checked LIVE inside
`start()`/`advance()` itself, so state() cannot know whether they'd pass
right now without probing them -- and INV-2 forbids that probe. So a
command/git-change-policy condition showing `[unmet]` must NOT suppress the
hint; it may well pass when the suggested verb actually runs.

calls internal: _attestable, _condition_kind, _condition_open

referenced by: 2 sites, this module only
