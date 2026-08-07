# scripts.install_constellation:expand_script_bundle
function, scripts/install_constellation.py:148, 9 lines

```python
def expand_script_bundle(scripts: tuple[str, ...]) -> tuple[str, ...]
```

Add each script's runtime companions, preserving order and de-duplicating.

Applied at discovery so every install path inherits it automatically.

calls stdlib: builtins.tuple
reads internal: SCRIPT_RUNTIME_COMPANIONS
reads stdlib: builtins.list, builtins.str
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
