# scripts.checklist_engine:_glob_to_regex
function, scripts/checklist_engine.py:483, 38 lines

```python
def _glob_to_regex(pattern: str) -> str
```

Translate a path glob into an anchored regex. `**` matches across path

separators (any number of segments); a single `*` matches within one
segment (no `/`); `?` matches one non-separator char. A trailing `/**` also
matches the directory itself (so `records/**` covers `records/x` and
`records/a/b`). We do NOT use `PurePosixPath.match`: before Python 3.13 it
treats `**` as a single-segment wildcard, so `records/**` would miss
`records/a/b` — exactly the nested record-dump case this policy must catch.

calls stdlib: builtins.len, re.escape
reads stdlib: builtins.list, builtins.str, re (module)
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
