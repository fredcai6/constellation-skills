# scripts.run_skill_eval:_adjudicate_orphan
function, scripts/run_skill_eval.py:1059, 36 lines

```python
def _adjudicate_orphan(scenario: Scenario, run_dir: Path) -> RunResult
```

Adjudicate a run whose launch meta is still `launched` — a run the runner

process died mid-flight without finalizing (issue #130). This is the
independent wall-clock watchdog: it runs OUTSIDE the dead process (a resuming
re-invocation), so a runner death can no longer strand a run in `launched`
forever.

The verdict is re-derived from the workspace exactly like the timeout
carve-out: the process checks are MONOTONE, so if the orphan's workspace
ALREADY passes every process check the deliverable is real and the run is a
`completed-pass` (the runner died AFTER the work finished but before it could
finalize). Otherwise the run is FENCED (`inconclusive`) — a runner death is an
environment failure, never a corpus FAIL — and the completion-seeking loop will
launch a replacement. Rewrites the run's meta.json to the resolved terminal
status so the record is adjudicable and never re-adopted as an orphan.

calls internal: RunResult x2, _write_meta, run_check
calls stdlib: builtins.all, json.loads, time.time
reads internal: RunResult.reason, RunResult.status, Scenario.id, Scenario.process_checks
reads stdlib: builtins.OSError, builtins.ValueError, json (module), time (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
