# tests.test_episode_store:naive_history_inclusive_forgetting_the_union
function, tests/test_episode_store.py:1910, 9 lines

```python
def naive_history_inclusive_forgetting_the_union(root)
```

Trap 2 — a history-inclusive enumeration that forgets to union both directories.

The tempting shape: "history-inclusive means I also want the archive", written as a
scan of the archive alone, or (as here) a scan that reaches for the ordinary set and
never adds the archive to it. The caller explicitly ASKED for history and gets half
of it back, silently. This one is nastier than trap 1 because the answer is
non-empty and looks plausible.

calls stdlib: builtins.sorted, pathlib.Path
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
