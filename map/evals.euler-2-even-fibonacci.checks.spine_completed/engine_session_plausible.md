# evals.euler-2-even-fibonacci.checks.spine_completed:engine_session_plausible
function, evals/euler-2-even-fibonacci/checks/spine_completed.py:117, 32 lines

```python
def engine_session_plausible(data: dict) -> tuple[bool, str]
```

Whether the spine carries an engine-written ``engine_session`` lease with a

monotonic claim->heartbeat(->release) lifecycle. The template ships without
this block, so its mere presence-in-engine-shape is the load-bearing signal.

calls internal: _parse_iso x3
calls stdlib: builtins.isinstance x2
reads internal: SESSION_FIELDS
reads stdlib: builtins.dict, builtins.str
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
