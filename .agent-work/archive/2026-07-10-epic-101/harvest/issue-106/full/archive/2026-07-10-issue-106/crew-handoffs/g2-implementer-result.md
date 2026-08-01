# IMPLEMENTER_RESULT — issue-106 / g2 (runner core + agent-free unit tests)

Session: `constellation/issue-106/g2/implementer/attempt-1`
Worktree: `C:\Programs\constellation-wt-106` (branch `constellation/issue-106`)

## Completed slice
Built the PURE, agent-free core of `scripts/run_skill_eval.py` test-first, fully
covered by `tests/test_run_skill_eval.py`. Every frozen-contract decision was
implemented as written; nothing was re-decided. The unit layer launches NO agent,
and `--dry-run`/`--dry-run-fail` work end-to-end now through the injectable
`launch=`/`installer=` seams.

Functions implemented per the contract's module seam map:
- `load_scenario(scenario_dir) -> Scenario` — PURE/total directory-is-schema parse.
  `checks/*.py` globbed sorted = process checks (>=1 REQUIRED — zero is
  `EvalConfigError`); `checks/answer/*.py` = advisory; `task.md` required; optional
  `fixture/` and `scenario.toml` (tomllib, all keys defaulted: n=2, m=3,
  timeout=1800, model=`DEFAULT_MODEL="sonnet"` pilot tier, id=dir name).
- `build_eval_argv(launcher, *, prompt, model)` — PURE; `[launcher,"-p",prompt]`
  then `+= ["--model",model]` if model. Mirrors `run_crew.build_crew_argv`.
- `run_check(script_path, run_dir, *, is_answer=False) -> CheckResult` — runs
  `sys.executable <script> <run-dir>` (a CHECK subprocess, not an agent); exit 0
  => passed; first stdout line = evidence.
- `is_infra_marker(text)` + `classify_run(outcome, *, completion_present,
  completion_fresh, process_results) -> RunResult` — PURE infra-fence table
  (timeout/marker => inconclusive; launch-error/corpus-mismatch/nonzero-exit-no-
  completion => errored; exit-0-or-fresh-completion + all process pass =>
  completed-pass; else completed-fail).
- `verdict(run_results, *, n, m, corpus_id=None, source_commit=None) -> Verdict` —
  PURE tally over COMPLETED runs only; `completed<n`=>INCONCLUSIVE(2),
  `passed>=n`=>PASS(0), else FAIL(1).
- `compute_corpus_id` / `write_corpus_marker` / `assert_corpus` — sha256 over
  sorted `(rel_posix, _hash_file(p))`, reusing `install_constellation._hash_file`
  (imported, never edited). `CORPUS.json` excluded from the hash so the marker
  can't perturb the id it records.
- `run_scenario(scenario, *, temp_root, worktree=None, launch=None, installer=None,
  max_attempts=None)` — completion-seeking M-run loop (default `max_attempts=m+2`)
  with the run-dir contract shape (`workspace/`, `spine.json`, `transcript.txt`,
  `meta.json`); per-run corpus copy + `assert_corpus`; answer checks executed and
  RECORDED on the per-run record but appended AFTER classify so they never gate.
- Seams resolve at CALL time (run_crew pattern): `launch = launch or launch_agent`,
  `installer = installer or temp_install`.
- `launch_agent` and `temp_install` are INERT stubs raising
  `NotImplementedError("... wired at g3 (#106)")`.
- `dry_run_launch` (passing workspace) / `dry_run_fail_launch` (broken workspace,
  exit 0 => completed-fail not fenced) / `_dry_installer` (minimal valid corpus) —
  the dry-run path never touches the stubbed `temp_install`.
- `main()` implements the frozen CLI signature; exit 0/1/2 PASS/FAIL/INCONCLUSIVE,
  exit 3 on schema/usage error (EvalConfigError, or `--dry-run`+`--dry-run-fail`).

## Files changed
- `scripts/run_skill_eval.py` — NEW (untracked; not ignored). Committed-class.
- `tests/test_run_skill_eval.py` — NEW (untracked; not ignored). Committed-class.
- `.gitignore` — added defensive `evals/**/_runs/` line (allowed by handoff).
All three are UNTRACKED/modified-unstaged (`git status --porcelain`: ` M .gitignore`,
`?? scripts/run_skill_eval.py`, `?? tests/test_run_skill_eval.py`) — not yet staged.

## Test mode satisfied
TDD. `tests/test_run_skill_eval.py` written first, then the implementation to green.
AGENT-FREE, mechanically enforced. Close-criteria coverage:
- KNOWN-GOOD canned run-dir scored PASS by the check engine
  (`test_run_check_known_good_passes`).
- KNOWN-BAD canned run-dir scored FAIL (`test_run_check_known_bad_fails`).
- INFRA-ABORT: timeout AND usage-limit marker classified `inconclusive` and
  EXCLUDED from the tally, distinct from FAIL (`test_classify_timeout_*`,
  `test_classify_usage_limit_marker_*`,
  `test_verdict_one_completed_two_fenced_is_inconclusive_not_fail`).
- verdict math: 2-of-3 => PASS; 1-of-3 => FAIL; 1 completed + 2 fenced =>
  INCONCLUSIVE (not FAIL) — all three asserted.
- Answer checks never move the verdict: `test_answer_only_failure_still_passes`
  (process passes + answer fails => PASS, answer recorded non-gating); zero
  process checks => config error at load AND via CLI (exit 3).
- No-agent guard: autouse fixture wraps `subprocess.run` and HARD-FAILS on any
  argv whose basename starts with `claude`; the real `launch_agent`/`temp_install`
  proven inert (raise NotImplementedError "g3"). Module import has no side effects.
- `--dry-run` exits 0, `--dry-run-fail` exits 1 against a tmp scenario built inside
  the test (`test_dry_run_exits_zero`, `test_dry_run_fail_exits_one`,
  `test_dry_run_fail_is_completed_fail_not_fenced`).

## Evidence produced (pasted)

`py -m pytest tests/test_run_skill_eval.py -q` (tail):
```
.........................................                                [100%]
41 passed in 1.64s
```

`py -m pytest -q` (full-suite summary):
```
508 passed, 2 skipped, 152 subtests passed in 14.06s
```

`--dry-run` / `--dry-run-fail` against a throwaway scenario (built under the
session scratchpad, NOT committed):
```
=== --dry-run ===
VERDICT: PASS (exit 0)
  completed=3 passed=3 fenced=0
  corpus_id=sha256:8d454566485c0cb9b32b35e6f3eba4617ebe1d38f8ecd2fe88b0ee5091128ffd
  ...
EXIT=0
=== --dry-run-fail ===
VERDICT: FAIL (exit 1)
  completed=3 passed=0 fenced=0
  ...
EXIT=1
```

`git check-ignore` (expect exit 1 = NOT ignored):
```
runner want-1: 1
test want-1: 1
```

## Assumptions (implementation details within the frozen contract)
- `DEFAULT_MODEL = "sonnet"` as the "pilot tier one below prod" string (contract
  named the tier, not the literal; sonnet is one below opus/prod).
- Completion probe = `workspace/eval-complete.txt` present + fresh (mtime floored
  to whole seconds, the run_crew freshness convention). A run also counts as
  "completed" on exit 0 with no spine terminal, per the classify table.
- `run_check` uses `sys.executable` (not the literal `python`/`py`) for the check
  subprocess — portable and passes the no-agent guard.
- `_dry_installer` synthesizes a minimal valid corpus so provenance runs
  end-to-end; it is dry-run scaffolding, explicitly NOT `temp_install` (which
  stays an inert g3 stub).
- `install_constellation` is loaded via importlib and REGISTERED in `sys.modules`
  before `exec_module` (Python 3.12+ dataclass KW_ONLY probe dereferences
  `sys.modules[cls.__module__]`) — import-only, the file is never edited.
- `verdict` keeps the contract signature `(run_results, *, n, m)` and adds optional
  `corpus_id`/`source_commit` kwargs so `run_scenario` can stamp the Verdict's
  provenance fields without changing the required call shape.

## Stop conditions hit
None. No blocker; the frozen contract had no hole requiring g1 reopen. Allowed
scope was not exceeded (only the two NEW files + the sanctioned `.gitignore` line;
`install_constellation.py`/`run_crew.py` were read/imported, never edited).

## Out-of-scope observations (for g3/g4, not acted on)
- g3 fills `launch_agent` (real headless subprocess, timeout + stderr marker
  capture into `LaunchOutcome`) and `temp_install` (reusing
  `install_constellation.install_skills`, scope=project into the temp skills dir),
  plus fake-subprocess end-to-end tests driving pass AND fail transcripts.
- The `LaunchOutcome` flags (`timed_out`, `launch_error`, `corpus_mismatch`,
  `stderr_text`) are the exact surface g3's `launch_agent` must populate for the
  infra-fence to fire correctly — worth stating in the g3 handoff.
- `_probe_completion` currently keys on `COMPLETION_ARTIFACT`; if the live
  workflow's real terminal artifact differs, g3 should thread the expected
  artifact name from the scenario/contract rather than hard-coding it.

## Workflow feedback
The handoff + frozen contract were precise and internally consistent; the
`temp_install` inert-stub-vs-"dry-run runs install end-to-end" tension resolves
cleanly by treating the installer as an injectable seam (the contract's module
seam map already lists `temp_install (injectable installer)`), which the handoff's
`launch=` seam guidance generalizes to. No re-decisions were needed.
