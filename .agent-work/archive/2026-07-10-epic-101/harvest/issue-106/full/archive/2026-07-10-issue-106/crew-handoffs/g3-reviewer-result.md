# REVIEW_RESULT — g3 (runner live-launch wiring, #106)

## Verdict: APPROVE

Gate: g3 (runner live-launch wiring). Review target: UNCOMMITTED working tree
(` M scripts/run_skill_eval.py`, ` M tests/test_run_skill_eval.py`) on branch
`constellation/issue-106`, g2 core committed at 97edde8. All evidence
independently reproduced; nothing rubber-stamped.

## Independently reproduced evidence
- `py -m pytest tests/test_run_skill_eval.py -q` => **46 passed in 4.36s**.
- `py -m pytest -q` => **513 passed, 2 skipped, 152 subtests passed** (matches
  the Commander/implementer figure exactly).
- The 8 g3 tests verbose => all PASSED; the 2 real-`launch_agent` mapping tests
  (timeout, spawn-failure) PASSED in isolation, exercising the live
  `subprocess.run` path (guard permits non-`claude` binaries).

## Per-check findings

1. **temp_install reuses install_constellation.install_skills (no reinvention).**
   PASS. `scripts/run_skill_eval.py:441-464` calls `_install.discover_skills(
   source_root=...)` + `_install.install_skills(skills, target_root,
   dry_run=False, force=False, full_set=True, restart_message="",
   out=lambda _msg: None)`. Signature verified against
   `scripts/install_constellation.py:333-342` (all keyword-only args supplied).
   Source root = `<worktree>/skills` when given else `_install.SOURCE_ROOT`;
   target under caller-supplied `temp_root/skills`. `git status` shows NO change
   to `install_constellation.py` or `skills/` — source tree untouched.
   `test_temp_install_real_installs_corpus` runs the REAL install into a
   throwaway tree and asserts the source is unmutated.

2. **launch_agent spawns `claude -p` via subprocess.run, honors timeout,
   populates LaunchOutcome so the infra-fence fires.** PASS.
   `scripts/run_skill_eval.py:401-435`: `subprocess.run(argv, cwd=str(cwd),
   env=env, stdin=DEVNULL, stdout=out, stderr=err, timeout=timeout)`. Mapping is
   correct and independently proven against the LIVE code, not a fake:
   - `TimeoutExpired -> LaunchOutcome(exit_code=None, timed_out=True, ...)` and
     `classify_run` (line 275) returns `inconclusive` —
     `test_launch_agent_timeout_maps_to_fenced_inconclusive` drives a real
     `python -c time.sleep(30)` past a 0.5s timeout.
   - `FileNotFoundError/OSError -> LaunchOutcome(launch_error=True)` and
     `classify_run` (line 279) returns `errored` —
     `test_launch_agent_spawn_failure_maps_to_fenced_errored` drives a real
     nonexistent binary.
   - normal return -> `exit_code=proc.returncode` + stderr tail via
     `_read_stderr_tail`, feeding `is_infra_marker` (line 277) for the
     usage/rate-limit -> inconclusive path. `_read_stderr_tail` is best-effort
     and never raises, so a read hiccup cannot mis-fence.
   `_run_once` (line 552) threads the injected `launch` seam's `LaunchOutcome`
   straight into `classify_run` (line 564) — the fence is genuinely wired.

3. **Agent-free guard still mechanically bites the live seam.** PASS. Guard
   (`tests/test_run_skill_eval.py:38-53`) is UNCHANGED and wraps
   `subprocess.run` on the module object. `launch_agent` calls `subprocess.run`
   via module-attribute lookup (`scripts/run_skill_eval.py:419`) — verified there
   is NO `from subprocess import run` bypass and NO Popen/os.exec/os.spawn in the
   source (grep clean). So the monkeypatched guard intercepts every launch with
   no guard extension needed. `test_agent_free_guard_still_bites_on_launch_agent`
   passes a real `claude` argv through the LIVE `launch_agent`; the guard's
   `AssertionError` (neither `TimeoutExpired` nor `OSError`) propagates out — the
   passing `pytest.raises(AssertionError, match="blocked real agent subprocess")`
   proves `launch_agent` actually reached `subprocess.run` before being blocked
   (non-vacuous).

4. **Fake-subprocess end-to-end tests drive the WHOLE run for PASS and FAIL.**
   PASS. `test_end_to_end_pass_...` runs real temp-install -> corpus id + marker
   + per-run `assert_corpus` -> injected fake launch -> transcript -> checks ->
   `classify_run` -> N-of-M => PASS (3 completed, >=2 passed, fenced=0), all runs
   `completed-pass` (proves per-run corpus assertion held), answer check recorded
   but non-gating. `test_end_to_end_fail_...` => FAIL, all `completed-fail`,
   fenced=0. `test_all_fenced_run_scenario_is_inconclusive_not_fail` proves a
   corpus that never ran yields INCONCLUSIVE (exit 2), never FAIL. Both fakes
   spawn nothing.

5. **No g2-frozen pure logic changed except filling the stubs.** PASS. `git
   diff` on the source is a SINGLE hunk at `@@ -378,18 +378,86 @@` (the two-stub
   region): adds `_STDERR_TAIL_BYTES` + `_read_stderr_tail`, fills `launch_agent`
   and `temp_install`. `load_scenario`, `build_eval_argv`, `classify_run`,
   `is_infra_marker`, `verdict`, corpus provenance, `run_check`, `_run_once`,
   `run_scenario` are untouched.

6. **No real claude launch in any committed test.** PASS. Every `claude`
   reference in the test file is either a pure `build_eval_argv` assertion or the
   guard-blocked argv; real subprocesses use `python`/a nonexistent binary. Guard
   is autouse across the whole file.

7. **Full suite green.** PASS. 513 passed, 2 skipped reproduced.

8. **No temp artifact committed; new-file reasoning sound.** PASS. `git status
   --porcelain` shows only the two committed-class files; `git check-ignore`
   exits 1 (not ignored); `git ls-files` has no `constellation-eval-*` / `_runs/`
   entries. Temp installs go to `TemporaryDirectory`/pytest `tmp_path` under the
   system temp dir — structurally uncommittable.

## Blockers
None.

## Out-of-scope observations (non-blocking)
- Stale comment: `_dry_installer` docstring (`scripts/run_skill_eval.py:501-505`)
  still says "NOT temp_install (which stays an inert stub until g3)". temp_install
  is now live; the parenthetical is outdated. Cosmetic only — `_dry_installer`
  behavior is unchanged and correct. Worth a one-line touch-up in a later pass.
- No real `claude` launch is exercised anywhere in the committed suite — correctly
  deferred to g5 (live acceptance + broken-variant falsification) per the contract.
- g4 still owns authoring `evals/<name>/` scenarios + `evals/README.md`; none
  authored here, as scoped.

## Stop conditions
None hit. Files accessible; agent-free guarantee mechanically verified and
non-vacuous; no real claude in any committed test; all relied-upon evidence
reproduced; LaunchOutcome demonstrably feeds the fence via the live seam.

## Workflow feedback
Clean, verifiable handoff. The one load-bearing trap (subprocess.run vs Popen re:
the guard) was correctly identified and correctly resolved by staying on
`subprocess.run`, keeping the agent-free grip mechanical with zero guard change.
The timeout/spawn tests exercising the REAL `launch_agent` (not just fakes) are
what make the LaunchOutcome-population claim independently checkable — good
test design.
