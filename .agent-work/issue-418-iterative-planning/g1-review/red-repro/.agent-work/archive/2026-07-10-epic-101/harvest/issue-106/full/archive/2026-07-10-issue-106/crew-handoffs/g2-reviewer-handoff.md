# Reviewer Handoff

## Gate
g2 (runner core + agent-free unit tests)

## Survey State Location
Create your review survey at `.agent-work/issue-106/g2-review/review.json` (under the issue workbench, never the worktree root).

## What Was Implemented
The PURE, agent-free core of `scripts/run_skill_eval.py` (schema parse, check execution, infra-fence classification, N-of-M verdict math, corpus provenance, `--dry-run`/`--dry-run-fail`, injectable `launch=`/`installer=` seams; real `launch_agent`/`temp_install` are inert `NotImplementedError` stubs "wired at g3") + `tests/test_run_skill_eval.py` (41 agent-free tests). Frozen contract: `.agent-work/issue-106/design/runner-contract.md`. Implementer result: `.agent-work/issue-106/crew-handoffs/g2-implementer-result.md`.

## How to Inspect the Diff
Review target is the UNCOMMITTED working tree in this worktree (C:\Programs\constellation-wt-106), NOT `git diff main...HEAD`. Use `git status --porcelain` then `git diff` (untracked-safe). New files (`scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py`) are untracked; `git diff` won't show untracked content — read them directly. `.gitignore` has one added line (`evals/**/_runs/`, sanctioned).

## Task Statement
Build the runner's pure agent-free logic test-first per the frozen contract; the unit layer must launch no agent; `--dry-run`/`--dry-run-fail` must work end-to-end; live wiring deferred to g3.

## Close Criteria (each becomes a review check)
- Pure logic matches the frozen contract (schema, N/M=2/3, infra-fence table, provenance, dry-run).
- Tests are AGENT-FREE: grep the test file for any real `claude` subprocess launch = a defect; confirm the mechanical guard (an autouse fixture / collection-time assertion) actually hard-fails if a real `claude` subprocess is attempted.
- The KNOWN-BAD canned fixture (a check that actually inspects the workspace) scores FAIL; the KNOWN-GOOD scores PASS — this is the permanent agent-free falsification.
- Verdict math: 2-of-3 => PASS; 1-of-3 => FAIL; 1 completed + 2 fenced => INCONCLUSIVE (never FAIL).
- Infra-fence: timeout / usage-limit marker => inconclusive, EXCLUDED from the tally; distinct from FAIL.
- Structural T3: the verdict gate reads ONLY `checks/*.py`; `checks/answer/*.py` never move it; zero process checks is a hard config error.
- Full suite green: reproduce `py -m pytest -q` yourself (Commander already saw 508 passed, 2 skipped).

## SPECIFIC REVIEW FOCUS (Commander-flagged — you are EMPOWERED to reopen g1)
The Commander independently observed: `classify_run` treats `exit_code == 0` as "completed" and then decides pass/fail SOLELY from the scenario's `process_results`; it does NOT itself gate on the runner's own completion-artifact probe (`_probe_completion` is used only for the completed-vs-errored liveness split). Consequence: `--dry-run-fail` (which synthesizes a broken workspace with NO completion artifact) still yields PASS if the scenario's process checks don't actually inspect completion (Commander reproduced this with a deliberately-vacuous throwaway spine check). 

Rule on whether this matches the intended contract:
- IF the intended design is "the runner's completion probe = liveness only; verifying the spine/completion is the SCENARIO's process-check responsibility" (delegated verification, consistent with the plain-scripts contract) — then this is CORRECT, but it makes the falsification floor check-dependent, so confirm (a) the unit-tested known-bad fixture uses a check that actually bites, and (b) note that g4 scenarios MUST include a completion/spine process check that genuinely inspects, and g5's live falsification must use biting checks. Record this as an inbound constraint for g4/g5.
- IF you judge the contract intended the runner to gate on completion presence as a baseline (so a missing completion artifact is always a fail regardless of scenario checks) — then `classify_run` deviates from the contract: BLOCK and this reopens g1 for a contract clarification. Your call; cite the contract text.

## Allowed Scope
`scripts/run_skill_eval.py`, `tests/test_run_skill_eval.py`, one `.gitignore` line. `install_constellation.py`/`run_crew.py` read/imported only.

## Specific Exclusions (flag if touched)
Any edit to other skills, `_shared/`, `run_crew.py`, `install_constellation.py`, install bundles, or real `evals/<name>/` scenarios (g4's job) or live launch wiring (g3's job).

## Constraints the Implementation Must Respect
- Repo tool not a skill; nothing gates on evals; runner never launches agents from default pytest collection.
- Process checks carry verdict (T3, structural); N-of-M contractual (T4); infra-fence keeps flake from failing a good corpus.
- Source repo authority; no edits to installed copies; temp-install semantics under system temp.

## Map Anchors (inbound)
- **Structural:** scripts/run_skill_eval.py, tests/test_run_skill_eval.py (NEW); scripts/run_crew.py::build_crew_argv, scripts/install_constellation.py (RELIED ON).
- **Constraints:** T3 structural, T4 contractual, agent-free unit layer.
- **Decision anchors:** runner contract frozen at g1.
- **Evidence expectations:** claim "runner logic correct independent of agents" — the agent-free suite green.

## Evidence Produced
See the implementer result: `py -m pytest tests/test_run_skill_eval.py -q` = 41 passed; `py -m pytest -q` = 508 passed, 2 skipped; `--dry-run` exit 0, `--dry-run-fail` exit 1 (on the implementer's own biting-check scenario); `git check-ignore` = exit 1 (not ignored) for both deliverables. Reproduce what you rely on. Target postcondition: `g2-integrate.c1` (full suite green) + `g2-integrate.c2` (this APPROVE verdict).

## Suggested Model Tier
stronger — the T3/infra-fence correctness and the classify_run contract-interpretation call are load-bearing.

## Stop Conditions
BLOCK if: the diff/files can't be accessed, the agent-free guarantee is unverifiable or violated, evidence doesn't reproduce, or the classify_run point requires a contract decision you judge is a genuine deviation (which reopens g1).

## Return Format
Write your REVIEW_RESULT to `.agent-work/issue-106/crew-handoffs/g2-reviewer-result.md`: verdict (APPROVE or BLOCK), per-check findings, the ruling on the classify_run focus item, blockers, out-of-scope observations, workflow feedback. Your final message must be your complete REVIEW_RESULT before you idle.
