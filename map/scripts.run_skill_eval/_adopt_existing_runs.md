# scripts.run_skill_eval:_adopt_existing_runs
function, scripts/run_skill_eval.py:1097, 39 lines

```python
def _adopt_existing_runs(scenario: Scenario, temp_root: Path) -> tuple[list, int, int]
```

Re-adopt the run-<n>/ dirs an earlier (possibly killed) invocation left in

`temp_root`, so a re-run RESUMES instead of restarting (issue #130). Walks
run-0, run-1, … in order until the first index with no meta.json (the next
free slot). For each existing meta: a terminal status is reconstructed as-is
and counted; a still-`launched` orphan is adjudicated by the watchdog above.
A corrupt/truncated meta.json (#205 — a kill mid-write) is routed through the
SAME watchdog rather than stopping the scan: it is not distinguishable from a
`launched` orphan (the process died before finalizing either way), so
`_adjudicate_orphan` adjudicates it from the workspace and the scan continues
past it, exactly like the `"launched"` branch below.
Returns (run_results, completed_count, next_index).

calls internal: _adjudicate_orphan x2, RunResult
calls stdlib: json.loads
reads stdlib: builtins.OSError, builtins.ValueError, builtins.list, json (module)
unresolved: 7 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
