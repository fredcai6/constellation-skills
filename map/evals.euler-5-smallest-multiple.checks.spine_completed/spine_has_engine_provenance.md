# evals.euler-5-smallest-multiple.checks.spine_completed:spine_has_engine_provenance
function, evals/euler-5-smallest-multiple/checks/spine_completed.py:197, 14 lines

```python
def spine_has_engine_provenance(data: dict) -> tuple[bool, str]
```

Composite gate: terminal gated shape AND engine_session plausibility AND

engine evidence grammar. Returns (ok, reason).

calls internal: all_tasks_complete, engine_session_plausible, evidence_grammar_ok
calls stdlib: builtins.isinstance
reads stdlib: builtins.dict

referenced by: 1 sites, this module only
