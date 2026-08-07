# tests.test_episode_store:force_rmtree
function, tests/test_episode_store.py:1299, 14 lines

```python
def force_rmtree(path)
```

shutil.rmtree with the Windows read-only escape hatch. Git marks objects under

.git/ read-only, and on Windows a read-only file cannot be unlinked — rmtree raises
PermissionError instead of cleaning up, stranding temp repos. The handler clears the
read-only bit and retries the operation that failed.

- [on_error](force_rmtree.on_error.md) method: HOLE: no docstring

calls stdlib: shutil.rmtree
reads stdlib: shutil (module)

referenced by: 1 sites, this module only
