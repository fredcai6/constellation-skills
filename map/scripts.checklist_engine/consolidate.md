# scripts.checklist_engine:consolidate
function, scripts/checklist_engine.py:1831, 21 lines

```python
def consolidate(cl: dict, verdict: str | None, summary: str | None, override_reason: str | None) -> str
```

HOLE: no docstring

calls internal: EngineError x3
calls stdlib: builtins.len
reads internal: SURVEY, TERMINAL
reads stdlib: builtins.dict
writes internal: consolidate.cl[]
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
