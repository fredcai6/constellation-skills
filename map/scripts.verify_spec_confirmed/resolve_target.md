# scripts.verify_spec_confirmed:resolve_target
function, scripts/verify_spec_confirmed.py:174, 11 lines

```python
def resolve_target(target: str, root: Path) -> Path
```

Resolve the CLI target: a path if it exists, else a work-id form.

calls internal: SpecVerificationError
calls stdlib: pathlib.Path
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
