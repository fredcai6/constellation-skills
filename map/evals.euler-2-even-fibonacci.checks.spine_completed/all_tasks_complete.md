# evals.euler-2-even-fibonacci.checks.spine_completed:all_tasks_complete
function, evals/euler-2-even-fibonacci/checks/spine_completed.py:102, 13 lines

```python
def all_tasks_complete(data: dict) -> bool
```

True iff the engine's gated form has a non-empty ``tasks`` map with EVERY

task ``complete``. The bare ``{"status": ...}`` form is deliberately NOT
accepted here (it carries no provenance).

calls stdlib: builtins.isinstance x2, builtins.all, builtins.bool
reads stdlib: builtins.dict x2
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
