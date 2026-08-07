# scripts.run_skill_eval:_stamp_meta_heartbeat
function, scripts/run_skill_eval.py:650, 24 lines

```python
def _stamp_meta_heartbeat(run_dir) -> None
```

Best-effort liveness stamp into a run's launch meta.json while its subject

is in flight. Records `heartbeat_at` (wall-clock now) and `elapsed_seconds`
(now minus the recorded `launched_at`) so an independent watcher — or a
resuming re-invocation — can distinguish a live runner from a dead one without
waiting the full deadline (issue #130). Never raises: a missing/unreadable/
non-`launched` meta is silently skipped, so a stat hiccup cannot perturb a run.
Only a still-`launched` meta is stamped, so a heartbeat can never overwrite a
meta the finalizer already resolved to a terminal status.

calls stdlib: builtins.isinstance, builtins.round, json.dumps, json.loads, pathlib.Path, time.time
reads stdlib: json (module) x2, builtins.OSError, builtins.ValueError, builtins.float, builtins.int, time (module)
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
