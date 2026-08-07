# tests.test_worktree_precondition_wiring:EnumerationDeliberateBreakage._write_broken_copy
method, tests/test_worktree_precondition_wiring.py:68, 23 lines

```python
def _write_broken_copy(self) -> Path
```

Copy the real COMMANDER_SPINE.template.json into the tmp fixture

at the same relative path the coverage script expects, with the c0
precondition stripped from the `init` gate -- reproducing the #329
pre-fix state (an omitted precondition), not a hypothetical shape.

calls stdlib: json.loads x2, builtins.any, json.dumps
reads internal: EnumerationDeliberateBreakage.tmp_root, REAL_TEMPLATE, TEMPLATE_REL_PATH
reads stdlib: json (module) x3
unresolved: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
