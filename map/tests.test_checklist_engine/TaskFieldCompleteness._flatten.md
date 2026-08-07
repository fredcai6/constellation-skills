# tests.test_checklist_engine:TaskFieldCompleteness._flatten
static method, tests/test_checklist_engine.py:4008, 17 lines

```python
def _flatten(value)
```

Best-effort text extraction for str / [str] / {category: [str]}

shapes -- the shapes anchors/constraints actually carry in the live
corpus. Anything else (list-of-dict, bool, int, None) yields [].

calls stdlib: builtins.isinstance x7, builtins.all, builtins.list
reads stdlib: builtins.str x4, builtins.list x2, builtins.dict
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
