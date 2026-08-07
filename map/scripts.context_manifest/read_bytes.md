# scripts.context_manifest:read_bytes
function, scripts/context_manifest.py:188, 14 lines

```python
def read_bytes(abs_path: str) -> bytes | None
```

Read `abs_path`, or return None if it does not exist.

Absence is normal here — a declared doctrine overlay is legitimately absent in
a skill-source repo — so it yields `rev: null` with the row retained. A file
that *is* there but cannot be read (permissions, is-a-directory, a path
component that is not a directory) raises, so that `null` keeps meaning exactly
one thing: the file was not there.

calls stdlib: builtins.open
reads stdlib: builtins.FileNotFoundError
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
