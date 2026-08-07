# tests.test_episode_store:naive_select_substring
function, tests/test_episode_store.py:920, 10 lines

```python
def naive_select_substring(root, field, value)
```

A second naive select: a bare substring search over the file text. This one does

not omit — it over-returns, matching any episode whose field value merely CONTAINS
the query (so a query for a value that is a prefix of another episode's value drags
that episode in too). The exact-match primitive must do neither.

calls stdlib: builtins.sorted x2, pathlib.Path
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
