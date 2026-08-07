# scripts.run_skill_eval:_run_once
function, scripts/run_skill_eval.py:963, 94 lines

```python
def _run_once(scenario: Scenario, index: int, temp_root: Path, skills_dir: Path, corpus_id: str, launch, permission_mode: str | None = None, launcher: str = DEFAULT_LAUNCHER) -> RunResult
```

Execute (and score) ONE attempt into `run-<index>/`. Fabricates the run-dir

shape, copies the corpus into an isolated `workspace/.claude/skills` and
asserts its id, launches via the injected seam, probes completion, then runs
the process (gating) and answer (advisory, recorded-not-gating) checks.

Also computes the two signals the permission-block fence (issue #115 tc3)
consumes: a content fingerprint of the seeded workspace taken BEFORE the launch
vs. AFTER (byte-unchanged?), and whether a permission-denial marker appears in
the transcript or stderr. Both true ⇒ the environment blocked the agent, fenced
rather than tallied.

calls internal: _write_meta x2, compute_corpus_id x2, is_permission_denial x2, run_check x2, LaunchOutcome, _probe_completion, _read_text_tail, _run_once.launch, build_eval_argv, classify_run, stable_corpus_id, wrap_prompt
calls stdlib: builtins.str x3, shutil.copytree x2, time.time x2, builtins.dict, builtins.list, json.loads, shutil.ignore_patterns
reads internal: Scenario.fixture_dir x2, Scenario.id x2, Scenario.timeout_seconds x2, Scenario.answer_checks, Scenario.model, Scenario.process_checks, Scenario.task_prompt
reads stdlib: shutil (module) x3, builtins.list x2, time (module) x2, builtins.OSError, builtins.ValueError, json (module), os (module), os.environ
unresolved: 3 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base), 1 writes (dispatch-unknown-base)

referenced by: 1 sites, this module only
