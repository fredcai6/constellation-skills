# scripts.verify_cycles:verify_cycles
function, scripts/verify_cycles.py:26, 26 lines

```python
def verify_cycles(root: Path, work_id: str) -> None
```

HOLE: no docstring

calls internal: CyclesVerificationError x2, cycles_dir
calls stdlib: builtins.isinstance, builtins.sorted, json.loads
reads stdlib: json (module) x2, builtins.OSError, builtins.dict, builtins.list, builtins.str, json.JSONDecodeError
unresolved: 11 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
