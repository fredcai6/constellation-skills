# Reviewer Handoff

## Gate
g3 (runner live-launch wiring)

## Survey State Location
`.agent-work/issue-106/g3-review/review.json` (under the issue workbench, never worktree root).

## What Was Implemented
The real `temp_install` (reuses `install_constellation.discover_skills`+`install_skills`) and `launch_agent` (real `claude -p` subprocess on `subprocess.run`) filling the g2 inert stubs, plus fake-subprocess end-to-end tests. Frozen contract: `.agent-work/issue-106/design/runner-contract.md`. Implementer result: `.agent-work/issue-106/crew-handoffs/g3-implementer-result.md`. g2 core committed at 97edde8; g3 edits are uncommitted.

## How to Inspect the Diff
Review target = UNCOMMITTED working tree. `git status --porcelain` (expect ` M scripts/run_skill_eval.py`, ` M tests/test_run_skill_eval.py`), then `git diff` for the two modified files.

## Task Statement
Fill the two stubs with the live-launch layer on top of the g2-tested core, populate LaunchOutcome so the infra-fence fires, keep the agent-free guarantee mechanically enforced, and add fake-subprocess end-to-end tests (pass AND fail) as g3's green check.

## Close Criteria (each a review check)
- `temp_install` reuses `install_constellation.install_skills` (no reinvention; source skills + install_constellation.py never edited); target under system temp, uncommittable.
- `launch_agent` spawns `claude -p` via `subprocess.run`, `cwd=<run>/workspace`, honors timeout; populates `LaunchOutcome.exit_code/timed_out/launch_error/stderr_text` so `classify_run`'s infra-fence fires (TimeoutExpired->timed_out; spawn failure->launch_error; usage-marker in stderr_text->inconclusive).
- AGENT-FREE GUARD still bites: confirm `launch_agent` is on `subprocess.run` (guard unchanged) OR the guard was extended to the mechanism used; reproduce the guard-bites test.
- Fake-subprocess end-to-end tests drive the WHOLE run (temp-install -> provenance -> launch-seam -> checks -> verdict) for a PASS and a FAIL transcript with NO real agent; and launch_agent's error mapping is tested.
- No g2-frozen pure logic changed except filling the stubs.
- Full suite green: reproduce `py -m pytest -q` (Commander saw 513 passed, 2 skipped).
- No temp artifact committed; new-file untracked reasoning sound.

## Allowed Scope
`scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py`. Import/read only: install_constellation.py, run_crew.py.

## Specific Exclusions (flag if touched)
Real `evals/<name>/` scenarios (g4), other skills, `_shared/`, `run_crew.py`, `install_constellation.py`, install bundles, any real `claude` launch in a committed test.

## Constraints
- Reuse install + `claude -p` form; temp under system temp; agent-free guard intact; transcripts captured not judged.

## Map Anchors (inbound)
- **Structural:** scripts/run_skill_eval.py (live layer); install_constellation.py (import-only).
- **Constraints:** nothing gates on evals; temp gitignored; agent-free guard intact.
- **Evidence:** the fake-subprocess e2e tests are the new green check; real launch proven at g5.

## Evidence Produced
Implementer: `py -m pytest tests/test_run_skill_eval.py -q` = 46 passed; `py -m pytest -q` = 513 passed, 2 skipped; guard-bites test passes on the live seam; `git status --porcelain` clean of temp paths. Reproduce what you rely on. Target postconditions: `g3-integrate.c1` (e2e + suite green) + `g3-integrate.c2` (this APPROVE).

## Suggested Model Tier
stronger — LaunchOutcome population + infra-fence wiring + the guard-vs-mechanism point are load-bearing.

## Stop Conditions
BLOCK if: files inaccessible, agent-free guarantee unverifiable/violated, a real claude launch is in a committed test, evidence doesn't reproduce, or LaunchOutcome doesn't feed the fence.

## Return Format
Write REVIEW_RESULT to `.agent-work/issue-106/crew-handoffs/g3-reviewer-result.md`: verdict (APPROVE/BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback. Final message = complete REVIEW_RESULT before idling.
