# scripts.verify_context_declaration:check_checklist
function, scripts/verify_context_declaration.py:139, 16 lines

```python
def check_checklist(data: dict, source: str = '<checklist>') -> list[str]
```

One human-readable problem string per (task, offending path). Empty

means every task's declaration agrees with its own prose.

calls internal: offenders_in_task
calls stdlib: builtins.isinstance x2
reads stdlib: builtins.dict x2, builtins.list, builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
