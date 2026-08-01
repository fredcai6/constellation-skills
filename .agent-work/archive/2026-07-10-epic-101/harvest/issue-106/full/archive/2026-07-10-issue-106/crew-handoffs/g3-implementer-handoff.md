# Implementer Handoff

## Gate
g3 (runner live-launch wiring)

## Task
Fill the two inert stubs in `scripts/run_skill_eval.py` with the REAL live-launch layer, on top of the g2-tested core. Frozen contract: `.agent-work/issue-106/design/runner-contract.md` (READ IT). The g2 core is committed (97edde8); do not re-decide anything g2 froze.

Implement:
- `temp_install(worktree, temp_root) -> Path` — install the candidate corpus ONCE from `worktree` (default: this worktree's `skills/`) into `<temp_root>/skills` by reusing `install_constellation.install_skills(...)` (import it; read its signature — the g2 core already imports the module for `_hash_file`). Project scope. Return the skills dir. Never edit install_constellation.py or the source skills.
- `launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome` — the ONE real subprocess. Spawn `claude -p "<prompt>" [--model X]` (argv already built by `build_eval_argv`) with `cwd=<run>/workspace`, capturing stdout/stderr to the given paths, honoring `timeout`. Populate `LaunchOutcome` fully so the g2 infra-fence fires correctly: `exit_code`, `timed_out` (on `subprocess.TimeoutExpired`), `launch_error` (on spawn failure / FileNotFoundError), and `stderr_text` (tail, so `is_infra_marker` can sniff usage/rate-limit). Corpus-mismatch is already handled by the g2 `assert_corpus` path in `_run_once`.
- **AGENT-FREE GUARD (binding, from g2-review):** implement `launch_agent` on `subprocess.run` so the existing autouse guard (which wraps `subprocess.run`) still intercepts it. If you must use `subprocess.Popen`/`os.exec*`, you MUST extend the agent-free guard in the test file to wrap that too — the mechanical "no test launches a real claude" guarantee must stay intact. Verify the guard still bites after your change.
- **Fake-subprocess end-to-end tests** (add to `tests/test_run_skill_eval.py`, still agent-free): drive `run_scenario(...)` with a FAKE `launch=` and the REAL `temp_install` (installing from a tiny throwaway source skill tree, or the real `skills/` if fast enough — your call, keep it fast) through the WHOLE pipeline — temp-install -> corpus id + marker + per-run assert -> launch-seam -> transcript -> checks -> classify -> N-of-M verdict — for BOTH a PASSING transcript (fake writes a completing workspace + biting check passes -> PASS) and a FAILING transcript (fake writes a broken workspace -> completed-fail -> FAIL). This closes the live-path test window honestly (the IO path is TESTED with a fake, not left untested) and is g3's real green check. Also add a fake that raises/timeouts to confirm `launch_agent`'s error mapping feeds the infra-fence.

## Protected Intent
The runner actually installs and launches against the candidate-under-test corpus (provenance asserted); environment flake is fenced (never fails a good corpus); the agent-free guarantee stays mechanically enforced; transcripts are captured for diagnosis, never judged by the runner.

## Test Mode
TDD/test-alongside — the fake-subprocess end-to-end tests are the gate's deliverable and green check.

## Close Criteria
- `temp_install` and `launch_agent` implemented per the contract; no other g2 behavior changed.
- Fake-subprocess end-to-end tests drive the whole run for PASS and FAIL with NO real agent; `launch_agent`'s timeout/launch-error mapping feeds the infra-fence (tested).
- Agent-free guard still bites (verify; extend to Popen if you used it).
- Temp-install target is under system temp / gitignored, never committed; source skills never edited.
- Full suite green: `py -m pytest -q`.

## Allowed Scope
EDIT: `scripts/run_skill_eval.py` (the two stubs + any small helper), `tests/test_run_skill_eval.py` (add end-to-end tests + guard extension if needed). Import/read only: `scripts/install_constellation.py`, `scripts/run_crew.py`.

## Specific Exclusions
- Do NOT author real `evals/<name>/` scenarios (g4, #106).
- Do NOT change the g2-frozen pure logic (classify_run, verdict, load_scenario, provenance) except to fill the stubs.
- Do NOT edit other skills, `_shared/`, `run_crew.py`, `install_constellation.py`, or install bundles.
- Do NOT run a real `claude` agent in any committed test.

## Constraints
- Reuse `install_constellation.install_skills` (do not reinvent install); reuse the `claude -p` form via the existing `build_eval_argv`.
- Temp dir via `tempfile.mkdtemp`/`TemporaryDirectory` under the system temp dir — structurally uncommittable.
- POSIX-form verification; `py` launcher.

## Map Anchors (inbound)
- **Structural:** scripts/run_skill_eval.py (live layer); scripts/install_constellation.py (RELIED ON, import-only).
- **Capability:** corpus eval — live launch.
- **Constraints:** nothing gates on evals; temp-install gitignored; agent-free guard intact.
- **Decision anchors:** dry-run/live seam fixed at g1+g2.
- **Evidence expectations:** dry-run smoke stays green; the fake-subprocess e2e tests are the new green check; real launch proven at g5.

## Deliverable Path Check
- **Committed** — `scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py` (already tracked after g2 commit; your edits are committed-class). Confirm `git check-ignore` exits 1.
- **Local-only** — this handoff + your result under `.agent-work/`.

## Required Evidence
- `py -m pytest tests/test_run_skill_eval.py -q` tail (show the new e2e tests).
- `py -m pytest -q` full-suite summary.
- A short note proving the agent-free guard still bites (paste the guard code + a line showing it raises on a fake `claude` argv), and whether you used `subprocess.run` (guard unchanged) or extended it.
- Confirm no temp artifact is committed (`git status --porcelain` after a dry/e2e run is clean of temp paths).

## Verification Commands
```bash
cd /c/Programs/constellation-wt-106
py -m pytest tests/test_run_skill_eval.py -q
py -m pytest -q
git status --porcelain
```

## Suggested Model Tier
stronger — reason: correct `LaunchOutcome` population is what makes the infra-fence fire; the agent-free-guard-vs-Popen subtlety is a real trap.

## Authority
Contract frozen at g1; g2 core frozen. You decide only the live-wiring implementation details. If `install_skills`' real signature can't satisfy the contract without an out-of-scope change, STOP and return it as a blocker.

## Stop Conditions
Stop and return if: scope must be exceeded, the agent-free guarantee can't be kept, or `install_skills` needs changes outside your scope.

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/issue-106/crew-handoffs/g3-implementer-result.md`: completed slice, files changed, test mode satisfied, evidence (pasted), assumptions, stop conditions, out-of-scope observations, workflow feedback. Your final message must be your complete IMPLEMENTER_RESULT before you idle.
