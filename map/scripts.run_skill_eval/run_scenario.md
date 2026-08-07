# scripts.run_skill_eval:run_scenario
function, scripts/run_skill_eval.py:1153, 75 lines

```python
def run_scenario(scenario: Scenario, *, temp_root, worktree=None, launch=None, installer=None, max_attempts: int | None = None, permission_mode: str | None = DEFAULT_PERMISSION_MODE, resume: bool = False, launcher: str = DEFAULT_LAUNCHER, max_new_runs: int | None = None) -> Verdict
```

Install the corpus once, then run the completion-seeking M-run loop and

return the Verdict. The `launch`/`installer` seams default to the module-level
`launch_agent`/`temp_install` resolved at CALL time (run_crew's pattern), so a
monkeypatched or CLI-selected seam takes effect. `permission_mode` is passed to
the launcher so a live headless agent can write files (issue #115 tc2); it
defaults to the pinned, operator-visible DEFAULT_PERMISSION_MODE.

Loop is completion-seeking: launch until `completed == m` or
`attempts == max_attempts` (default m+2). Fenced attempts (inconclusive/
errored) do not advance the completed count, so environment flake extends the
loop rather than failing the corpus.

`resume=True` RE-ADOPTS the run-<n>/ dirs already in `temp_root` (issue #130):
the corpus is NOT reinstalled (its id/commit are read back from CORPUS.json),
finalized runs are counted as-is, a run the previous (killed) invocation left
stuck `launched` is adjudicated by the orphan watchdog, and only the remaining
runs are launched. So a kill-9 of the runner mid-measurement is recovered by
re-invoking with the same temp dir.

calls internal: RunResult, _adopt_existing_runs, _read_corpus_marker, _run_once, _source_commit, _write_meta, run_scenario.installer, verdict, write_stable_corpus_marker
calls stdlib: builtins.min, pathlib.Path, time.time
reads internal: Scenario.id, Scenario.m, Scenario.n, launch_agent, temp_install
reads stdlib: builtins.Exception, time (module)
writes internal: run_scenario.installer, run_scenario.launch, run_scenario.max_attempts, run_scenario.temp_root
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
