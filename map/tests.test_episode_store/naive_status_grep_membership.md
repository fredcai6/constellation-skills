# tests.test_episode_store:naive_status_grep_membership
function, tests/test_episode_store.py:1936, 15 lines

```python
def naive_status_grep_membership(root)
```

The ORIGINAL trap, kept and adapted: ordinary search as a content-parsing

operation over the `status` field, the way the REJECTED Option-B adapter would have
had to do it. Unanchored, because that is how it gets written — and any episode whose
free text merely QUOTES a status line is then silently excluded from ordinary search
while being entirely active.

EPISODE_STORE.md §7 named this exposure as the reason Option B needed a line-anchored
filter. Option A needs no filter at all, so the exposure is gone rather than
mitigated. This function exists to demonstrate that difference, not to be used.

calls internal: read_exact
calls stdlib: builtins.sorted x2, pathlib.Path
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
