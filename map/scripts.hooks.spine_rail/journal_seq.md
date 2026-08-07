# scripts.hooks.spine_rail:journal_seq
function, scripts/hooks/spine_rail.py:259, 15 lines

```python
def journal_seq(spine_path) -> int
```

Progress signal: count of non-blank lines in <spine_path>.journal.

0 if the journal is absent or unreadable. NEVER raises.

calls stdlib: builtins.open, builtins.str
reads stdlib: builtins.Exception
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
