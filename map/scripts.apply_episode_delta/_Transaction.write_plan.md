# scripts.apply_episode_delta:_Transaction.write_plan
method, scripts/apply_episode_delta.py:1041, 21 lines

```python
def write_plan(self) -> tuple[dict[Path, str], set[Path]]
```

Renders every touched episode to its FINAL destination path. Returns

(path -> text to write, paths to delete) — deletes only happen for a retire,
where the file moves into the archive and the old active/ path must go.

C6, half-retirement, is answered here first and by construction: a retirement's
field update and its move are not two operations that could disagree. The updated
CONTENT is only ever rendered to the NEW path, so "fields updated but file not
moved" has no representation in this plan at all, and neither does "moved but
fields not updated" — there is exactly one entry, and it carries both halves.
What remains is only whether that entry, plus its paired delete, lands as a unit;
commit() below makes it do so.

calls internal: destination_for, render_episode
calls stdlib: builtins.set
reads internal: _Transaction.loaded, _Transaction.original_paths, _Transaction.root
reads stdlib: pathlib.Path x2, builtins.dict, builtins.set, builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
