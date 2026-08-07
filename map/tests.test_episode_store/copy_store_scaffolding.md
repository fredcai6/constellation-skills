# tests.test_episode_store:copy_store_scaffolding
function, tests/test_episode_store.py:97, 20 lines

```python
def copy_store_scaffolding(dest)
```

Reproduce the REAL tracked store's non-episode files inside a throwaway store

root, and return how many were copied.

Read from `episodes/` rather than hand-written here, so a test store carries whatever
scaffolding the repository actually ships — if someone adds, renames or removes a
placeholder, the tests inherit it instead of drifting away from it. Real episode files
(there are none today) are skipped so the temp store still starts empty. Copy only:
the real store is never written to by any test.

calls internal: classifier x2
calls stdlib: builtins.sorted, pathlib.Path, shutil.copyfile
reads internal: STORE_TEMPLATE x2
reads stdlib: shutil (module)
writes internal: copy_store_scaffolding.dest
unresolved: 6 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
