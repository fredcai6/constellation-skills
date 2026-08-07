# scripts.checklist_engine:EngineError.__init__
method, scripts/checklist_engine.py:127, 8 lines

```python
def __init__(self, message, *, task_id=None, verb=None, status=None, unmet=None, valid_ids=None)
```

HOLE: no docstring

calls stdlib: builtins.super
writes internal: EngineError.status, EngineError.task_id, EngineError.unmet, EngineError.valid_ids, EngineError.verb
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
