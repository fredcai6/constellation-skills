# scripts.recover_crews:_behavior_for
function, scripts/recover_crews.py:155, 9 lines

```python
def _behavior_for(entry: dict, state: str) -> str
```

Human-readable behavior text for one classified entry. Uniform per state,

except a RESUMABLE entry's resume ACTION is backend-aware (Decision 6): the
`cli` action keeps the stored-session `run_crew.py --resume` text; an
`external` entry gets the unrecoverable-by-wrapper guidance instead. The state
itself (the classification) is unchanged — only the action text differs.

reads internal: run_crew x2, STATE_RESUMABLE, _BEHAVIOR, _EXTERNAL_RESUME_ACTION
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
