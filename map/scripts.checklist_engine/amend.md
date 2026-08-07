# scripts.checklist_engine:amend
function, scripts/checklist_engine.py:2040, 187 lines

```python
def amend(cl: dict, delta: dict, reason: str, authority: str, base_dir: Path | None = None) -> str
```

Intentional mid-stream re-planning of a GATED checklist. Apply a delta of

`add`/`drop`/`rescope` ops that touch PENDING gates only, plus a `retext-check`
op that corrects the check TEXT of a PENDING or IN-PROGRESS gate without
satisfying its condition — completed/blocked/skipped gates are never edited, and
no op ever marks a condition satisfied. The whole delta is ALL-OR-NOTHING: it is
validated and built on COPIES, and only committed to `cl` once every op passes,
so a refusal leaves `cl` unmutated (important: `main()` persists `cl` even on
the error path). Records an audit entry to `cl["amendments"]`.

- `add`: insert a new pending gate (`id` kebab-ish and unique; non-empty
  `title`/`imperative`; >=1 postcondition). `after` names an existing gate to
  insert behind (omit to append). The insert may not land before a frozen
  (non-pending) gate.
- `drop`: remove a pending gate.
- `rescope`: overwrite provided fields (title/imperative/pre/postconditions/
  constraints/directives) on a pending gate; postconditions if given stay >=1.
- `retext-check`: correct the check TEXT of one condition on a pending or
  in-progress gate (`command` for a command check, or a same-kind `check`
  object), then reset that condition to unsatisfied — an authoring fix that
  never marks the condition satisfied (that stays `waive`'s job) and never
  changes the check's kind.
Requires non-empty `--reason` and `--authority` (human ratification), same as
`waive`.

- [_floor](amend._floor.md) method: 1 + index of the last non-pending (frozen) gate; 0 if none. A new gate

calls internal: EngineError x28, _build_amend_task, _now, _reset_conditions
calls stdlib: builtins.isinstance x7, copy.deepcopy x4, builtins.len x3, builtins.dict, builtins.list, builtins.next
reads internal: GATED, _AMEND_ID_RE
reads stdlib: builtins.list x4, copy (module) x4, builtins.str x3, builtins.dict x2, builtins.int
writes internal: amend.cl[] x2
unresolved: 40 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
