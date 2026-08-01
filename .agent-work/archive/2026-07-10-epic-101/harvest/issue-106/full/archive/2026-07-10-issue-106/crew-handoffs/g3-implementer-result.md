# IMPLEMENTER_RESULT — g3 (runner live-launch wiring, #106)

## Completed slice
Filled the two inert g2 stubs in `scripts/run_skill_eval.py` with the real live-launch layer, on top of the frozen g2 core. No g2-frozen pure logic changed.

- `temp_install(worktree, temp_root)` — installs the candidate corpus ONCE into `<temp_root>/skills` by reusing `install_constellation.discover_skills` + `install_skills` (full-set, non-dry, non-force, silenced `out`). `worktree` selects the source root: `<worktree>/skills` when given, else this worktree's `skills/` (`install_constellation.SOURCE_ROOT`). Never edits `install_constellation.py` or the source skills.
- `launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout)` — the ONE real subprocess, implemented on `subprocess.run` (mirroring `run_crew.launch_process`), `cwd=<run>/workspace`, stdout/stderr captured to the given paths, `timeout` honored. `LaunchOutcome` is populated fully so the g2 infra-fence fires:
  - normal return -> `exit_code` + `stderr_text` (tail, for `is_infra_marker`);
  - `subprocess.TimeoutExpired` -> `timed_out=True` (fenced inconclusive);
  - `FileNotFoundError`/`OSError` spawn failure -> `launch_error=True` (fenced errored).
  - Corpus-mismatch stays handled upstream by the g2 `assert_corpus` path in `_run_once`.
- Added helper `_read_stderr_tail` (best-effort, never raises) so a stderr read hiccup can never mis-fence a run.

## Files changed
- `scripts/run_skill_eval.py` — two stubs filled + `_read_stderr_tail` helper (+ `_STDERR_TAIL_BYTES`). No other behavior touched.
- `tests/test_run_skill_eval.py` — replaced the two now-obsolete "inert stub" tests with the g3 live-layer tests (see below).

## Test mode satisfied
TDD/test-alongside. The fake-subprocess end-to-end tests are the gate's green check and they pass. Added:
- `test_temp_install_real_installs_corpus` — REAL `temp_install` installs a throwaway corpus, source tree unmutated.
- `test_end_to_end_pass_with_real_temp_install_and_fake_launch` — WHOLE pipeline (real temp-install -> corpus id+marker+per-run assert -> fake launch seam -> transcript -> checks -> classify -> N-of-M) => PASS (3 completed, fenced=0); answer check recorded but non-gating.
- `test_end_to_end_fail_with_real_temp_install_and_fake_launch` — broken workspace, exit 0 => completed-fail => FAIL, fenced=0.
- `test_launch_agent_timeout_maps_to_fenced_inconclusive` — REAL `launch_agent` on a python sleep past a 0.5s timeout -> `timed_out` -> `classify_run` = inconclusive.
- `test_launch_agent_spawn_failure_maps_to_fenced_errored` — REAL `launch_agent` on a nonexistent binary -> `launch_error` -> `classify_run` = errored.
- `test_all_fenced_run_scenario_is_inconclusive_not_fail` — all-timeout loop => INCONCLUSIVE (never FAIL a corpus that never ran).
- `test_agent_free_guard_still_bites_on_launch_agent` — a real `claude` argv is blocked by the autouse guard before any spawn.

NO committed test launches a real `claude`. The agent-free tests use `python`/a nonexistent binary; the claude-argv test is intercepted by the guard.

## Agent-free guard — unchanged, still bites
I implemented `launch_agent` on `subprocess.run` (NOT Popen/os.exec*), so the existing autouse guard that wraps `subprocess.run` intercepts it with no extension needed. Guard (unchanged):

```python
@pytest.fixture(autouse=True)
def _no_real_agent(monkeypatch):
    real_run = subprocess.run
    def guarded_run(cmd, *args, **kwargs):
        argv0 = cmd[0] if isinstance(cmd, (list, tuple)) and cmd else cmd
        base = os.path.basename(str(argv0)).lower()
        assert not base.startswith("claude"), f"blocked real agent subprocess: {cmd!r}"
        return real_run(cmd, *args, **kwargs)
    monkeypatch.setattr(subprocess, "run", guarded_run)
    yield
```

Proof it bites on the live seam (guard's `AssertionError` is neither `TimeoutExpired` nor `OSError`, so it propagates out of `launch_agent`):

```python
def test_agent_free_guard_still_bites_on_launch_agent(tmp_path):
    argv = rse.build_eval_argv("claude", prompt="do it", model="sonnet")
    with pytest.raises(AssertionError, match="blocked real agent subprocess"):
        rse.launch_agent(argv, cwd=str(tmp_path), env=dict(os.environ),
                         stdout_path=str(tmp_path / "o.txt"),
                         stderr_path=str(tmp_path / "e.txt"), timeout=10)
```
This test passes — the guard blocks a real `claude` launch through the now-live seam.

## Evidence (pasted)

### `py -m pytest tests/test_run_skill_eval.py -q` (tail)
```
..............................................                           [100%]
46 passed in 4.32s
```

### New g3 tests, verbose (`-k "end_to_end or guard_still_bites or timeout_maps or spawn_failure or temp_install_real or all_fenced" -v`)
```
collected 46 items / 38 deselected / 8 selected
tests\test_run_skill_eval.py ........                                    [100%]
====================== 8 passed, 38 deselected in 2.27s =======================
```

### `py -m pytest -q` (full-suite summary)
```
513 passed, 2 skipped, 152 subtests passed in 19.99s
```

### `git status --porcelain` (clean of temp paths — only committed-class edits)
```
 M scripts/run_skill_eval.py
 M tests/test_run_skill_eval.py
```
`git check-ignore scripts/run_skill_eval.py tests/test_run_skill_eval.py` exits 1 (both correctly committed-class, not ignored). No `constellation-eval-*` temp artifact appears — temp installs go to the system temp dir via `TemporaryDirectory`/the test `tmp_path`, structurally uncommittable.

## Assumptions
- `temp_install` reuses `install_constellation`'s module-level `REPO_ROOT`/`SHARED_REFERENCE_ROOT` for bundle sources (they resolve to this worktree); the throwaway skill used in tests is in no bundle, so install copies exactly the source dir — hermetic and fast.
- Default `worktree=None` means "this worktree's `skills/`" (contract §(c)); an explicit `--worktree` points at a dir containing `skills/`.
- `stderr_text` tail is capped at 8192 bytes — ample to catch a usage/rate-limit banner for `is_infra_marker`.

## Stop conditions
None hit. `install_skills`' real signature satisfied the contract without any out-of-scope change; the agent-free guarantee held with `subprocess.run` (no Popen/exec, no guard extension needed).

## Out-of-scope observations
- No real `claude` launch is exercised anywhere in the committed suite — that is deliberately deferred to g5 (live acceptance + broken-variant falsification), per the contract.
- g4 still owns authoring `evals/<name>/` scenarios + `evals/README.md`; none authored here.

## Workflow feedback
Clean handoff: the frozen contract + committed g2 core made the live-wiring boundary unambiguous. The one genuine trap flagged (subprocess.run vs Popen re: the guard) was real and correctly called out — staying on `subprocess.run` kept the mechanical agent-free guarantee intact with zero guard changes.
