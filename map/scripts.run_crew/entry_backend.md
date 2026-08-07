# scripts.run_crew:entry_backend
function, scripts/run_crew.py:413, 8 lines

```python
def entry_backend(entry: dict) -> str
```

The backend that owns a recorded entry. New entries carry `backend`

explicitly; a legacy entry without one is inferred — `dispatch == "external"`
-> external, else cli (Decision 5, backward compatible).

reads internal: BACKEND_CLI x2, BACKEND_EXTERNAL x2, DISPATCH_EXTERNAL
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
