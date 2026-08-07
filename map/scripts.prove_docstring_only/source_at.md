# scripts.prove_docstring_only:source_at
function, scripts/prove_docstring_only.py:57, 8 lines

```python
def source_at(rev: str, path: str) -> str
```

File contents at `rev`, or the file on disk when rev is `WORKTREE`.

calls stdlib: pathlib.Path, subprocess.run
reads stdlib: subprocess (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
