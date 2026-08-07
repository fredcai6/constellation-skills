# scripts.run_skill_eval:dry_run_launch
function, scripts/run_skill_eval.py:863, 32 lines

```python
def dry_run_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome
```

Fake launcher that synthesizes a REAL passing workspace — a non-empty

`solution.py`, a green `test_solution.py`, the completion artifact, and an
engine-shaped terminal `spine.json` — so the gating process checks
(`artifact_present`, `tests_green`, `spine_completed`) each bite STRICTLY on a
real deliverable, with no sentinel stand-in (issue #115 tc1) and with the engine
provenance `spine_completed` now demands (issue #127). Spawns NOTHING — the CI
smoke for the runner itself and caller #2's live target. The test is
self-contained (imports nothing from the workspace) so it stays green under any
pytest import mode.

calls internal: LaunchOutcome, _dry_run_engine_spine, _write_transcript
calls stdlib: json.dumps, pathlib.Path
reads internal: COMPLETION_ARTIFACT
reads stdlib: json (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
