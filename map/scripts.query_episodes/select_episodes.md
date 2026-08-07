# scripts.query_episodes:select_episodes
function, scripts/query_episodes.py:286, 34 lines

```python
def select_episodes(root: Path, field: str, values, include_retired: bool = False) -> list
```

Every episode whose `field` carries at least one of `values` — exact match, set

membership. Nothing is ranked and nothing is scored; the answer is a complete,
unordered candidate set, returned id-sorted only for determinism. Restricted to the
ordinary-search set unless `include_retired` deliberately asks for the archive too.

Matching compares whole parsed values with ==. It never searches the file text, so
it can neither over-return on a prefix nor under-return on an unanchored line
pattern. field_values() is validated once, up front, against the FIRST episode
scanned — and, when the store is empty, still validated below — so an unknown field
name always raises even when no episode would have matched anyway.

`values` must be an iterable of whole values, NOT a bare string. A bare string is
refused rather than wrapped: `set("implementer")` is a set of eleven CHARACTERS, so
accepting one would silently match single-character values and silently miss the value
the caller actually named — a wrong answer with no error, which is the one failure mode
this store is built to avoid. Refusing is safe because the natural caller idiom
(`select_episodes(root, "role", "implementer")`) is exactly the broken one, and #305 /
#308's callers are agent-written.

calls internal: QueryError x2, _selectable_field_reader, enumerate_episodes, field_values
calls stdlib: builtins.set x2, builtins.isinstance, builtins.type
reads stdlib: builtins.bytes, builtins.str
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
