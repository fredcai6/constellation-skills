# scripts.context_manifest:write_manifest
function, scripts/context_manifest.py:438, 12 lines

```python
def write_manifest(manifest: Mapping[str, Any], path: Any) -> Path
```

Write the manifest with LF line endings, always.

`newline="\n"` is load-bearing on Windows, not hygiene: without it Python
translates every `\n` to `\r\n` on write, and the file this record is about
would not survive its own identity function.

calls internal: encode
calls stdlib: builtins.open, pathlib.Path
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
