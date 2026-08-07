# scripts.run_skill_eval:is_permission_denial
function, scripts/run_skill_eval.py:328, 6 lines

```python
def is_permission_denial(text) -> bool
```

Whether `text` carries a permission-sandbox refusal marker (issue #115 tc3).

PURE. A hit is only load-bearing when the workspace was ALSO left byte-unchanged
(see classify_run), so it can never mis-fence a run that legitimately did work.

calls stdlib: builtins.any
reads internal: PERMISSION_MARKERS
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
