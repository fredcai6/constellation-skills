# scripts.context_manifest:resolve
function, scripts/context_manifest.py:204, 66 lines

```python
def resolve(entry: Mapping[str, Any], roots: Mapping[str, Any]) -> str
```

Absolute filesystem path for one declaration entry.

The returned path is for *reading only* — it is environment-varying and never
reaches the manifest content, where the row keeps the root token and the
declared relative path instead.

calls internal: DeclarationError x11
calls stdlib: os.path.normcase x4, builtins.isinstance x2, os.path.abspath x2, builtins.any, builtins.str, os.path.join, pathlib.PurePosixPath
reads internal: ROOT_TOKENS x2
reads stdlib: os (module) x8, os.path x7, builtins.str, os.sep, typing.Mapping
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
