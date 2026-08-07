# scripts.run_crew:result_fresh
function, scripts/run_crew.py:175, 20 lines

```python
def result_fresh(result: str | os.PathLike[str], root: Path, since: str) -> bool
```

Whether the expected result artifact exists AND is FRESH relative to the

crew's dispatch time `since` (an ISO-8601 string — the registry entry's
`started_at`). This is the ONE canonical freshness definition; every result
check reuses it, so a stale leftover result from a prior attempt at the same
path can never pass as success and the definition can never fork.

Fresh means the artifact's mtime is at/after `since` floored to whole seconds.
A missing file is never fresh (existence is a precondition of freshness). The
floor keeps coarse filesystem mtime resolution from falsely flagging a result
written in the same second as dispatch. Single machine, no clock skew: both
the mtime and `since` are POSIX-based, so the comparison is
timezone-independent.

calls stdlib: datetime.datetime.fromisoformat, pathlib.Path
reads stdlib: datetime.datetime
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
