# scripts.verify_context_declaration:discover_templates
function, scripts/verify_context_declaration.py:157, 5 lines

```python
def discover_templates(root: Path) -> list[Path]
```

Every real, committed checklist template under `root` -- never sorted

by anything but path, and never a reason on its own to skip a file; a file
that fails to parse is still reported, not silently dropped.

calls stdlib: builtins.sorted
reads internal: DEFAULT_GLOB
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
