# scripts.checklist_engine:_attestable
function, scripts/checklist_engine.py:1479, 6 lines

```python
def _attestable(kind: str) -> bool
```

`attest` accepts a qualitative (`check: null`) condition unconditionally,

or an `artifact` condition by reference (`--evidence`). `command`/
`git-change-policy` conditions are engine-checked and refuse attest (see
`attest()`), so they never get an attest hint.

referenced by: 2 sites, this module only
