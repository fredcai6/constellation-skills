# scripts.checklist_engine:_check_condition
function, scripts/checklist_engine.py:763, 72 lines

```python
def _check_condition(cond: dict, t: dict, base_dir: Path | None = None) -> bool
```

Verify one condition. command -> run it; artifact -> presence/match;

git-change-policy -> evaluate the staged/branch diff against an artifact
policy (#8); null -> the agent must have attested it (trust but verify).

A WAIVED condition is honored without re-running its check: a human override
(see `waive`) has accepted the condition, and re-running the command would
overwrite `satisfied` and silently un-waive it at every `advance`.

calls internal: _new_evidence_id x2, EngineError, _collect_changed_files, _run_check_command, evaluate_git_change_policy
calls stdlib: builtins.all, builtins.bool, builtins.len
writes internal: _check_condition.cond[] x7
unresolved: 17 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
