# scripts.checklist_engine:release
function, scripts/checklist_engine.py:1015, 16 lines

```python
def release(cl: dict, session_id: str, force: bool = False, reason: str | None = None) -> str
```

Close the lease (`status: released`). Only the owning session may release,

unless `--force --reason` is given. After release, a new `claim` succeeds.

calls internal: EngineError x3, _now
calls stdlib: builtins.isinstance
reads stdlib: builtins.dict
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
