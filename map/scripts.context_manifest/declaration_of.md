# scripts.context_manifest:declaration_of
function, scripts/context_manifest.py:272, 12 lines

```python
def declaration_of(task: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]
```

The task's ordered `context_refs`, or an empty tuple.

Absent is the normal case and is never an error: every spine authored before
this field existed keeps working, and simply projects nothing.

calls internal: DeclarationError
calls stdlib: builtins.isinstance x2, builtins.tuple
reads internal: DECLARATION_KEY x2
reads stdlib: builtins.bytes, builtins.str, typing.Sequence
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
