# scripts.install_constellation:remove_existing_constellation_set
function, scripts/install_constellation.py:521, 14 lines

```python
def remove_existing_constellation_set(target_root: Path) -> None
```

HOLE: no docstring

calls internal: InstallError, ensure_target_is_inside_root
calls stdlib: shutil.rmtree
reads stdlib: shutil (module)
unresolved: 6 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
