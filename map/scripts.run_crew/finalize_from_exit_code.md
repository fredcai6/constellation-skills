# scripts.run_crew:finalize_from_exit_code
function, scripts/run_crew.py:379, 32 lines

```python
def finalize_from_exit_code(entry: dict, *, exit_code: int, result: str, root: Path, since: str) -> int
```

Finalize a spawned attempt's entry from the child exit code and result

freshness since dispatch. The ONE tail both `CliBackend.dispatch` and
`CliBackend.resume` call — no copy-paste of the completed/failed rule.

Sets `completed_at`/`last_heartbeat` (now), `status`, `exit_code`,
`result_present`, and `result_fresh`, and returns the process-level exit code
to report. Reuses the single canonical `result_fresh` (`since` is the entry's
dispatch time): a child that exits 0 but leaves only a STALE prior-attempt
result at the path (mtime predates dispatch) is `failed`, not `completed`.

calls internal: _now, result_exists, result_fresh
writes internal: finalize_from_exit_code.entry[] x7

referenced by: 2 sites, this module only
