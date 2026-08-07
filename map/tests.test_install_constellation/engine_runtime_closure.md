# tests.test_install_constellation:engine_runtime_closure
function, tests/test_install_constellation.py:1207, 18 lines

```python
def engine_runtime_closure(entry: str, scripts_root: Path) -> set[str]
```

Everything `entry` drags in at runtime, TRANSITIVELY, minus itself.

Transitive because the shipping unit is the closure, not the first hop:
`episode_capture.py` alone would still crash on an install missing
`agent_work_root.py`. Cycles are normal here (`context_manifest` imports
`checklist_engine` back) and are absorbed by the visited set.

calls internal: _direct_runtime_siblings
calls stdlib: builtins.set
reads stdlib: builtins.set, builtins.str
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
