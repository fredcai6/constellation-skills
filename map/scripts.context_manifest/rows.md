# scripts.context_manifest:rows
function, scripts/context_manifest.py:286, 23 lines

```python
def rows(declaration: Sequence[Mapping[str, Any]], roots: Mapping[str, Any], reader: Callable[[str], bytes | None] = read_bytes) -> list[dict]
```

One `{root, path, rev}` row per declared entry, in declaration order.

Declaration order is emitted verbatim — never sorted, never enumerated from the
filesystem. `required` stays in the declaration and is deliberately not copied
into the row: the manifest records what was delivered, not what was asked for.

calls internal: resolve, rev, rows.reader
reads stdlib: builtins.dict, builtins.list
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
