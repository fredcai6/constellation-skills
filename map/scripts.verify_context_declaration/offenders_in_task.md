# scripts.verify_context_declaration:offenders_in_task
function, scripts/verify_context_declaration.py:118, 19 lines

```python
def offenders_in_task(task: dict) -> list[str]
```

Declared paths in `task` that do not appear verbatim in its own

`imperative` string. Empty means the task is clean, including the normal
case of carrying no declaration at all.

calls internal: _appears_at_path_boundary
calls stdlib: builtins.isinstance x3, builtins.repr
reads internal: DECLARATION_KEY
reads stdlib: builtins.str x2, builtins.dict
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
