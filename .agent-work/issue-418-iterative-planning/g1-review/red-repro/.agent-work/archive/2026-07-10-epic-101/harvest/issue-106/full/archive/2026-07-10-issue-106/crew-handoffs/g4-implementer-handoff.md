# Implementer Handoff

## Gate
g4 (pilot Euler scenarios + bar README)

## Task
Author 2–3 graded Project Euler scenarios under `evals/<name>/` to the FROZEN directory-is-schema (`.agent-work/issue-106/design/runner-contract.md` §(a)), plus `evals/README.md`. The runner (`scripts/run_skill_eval.py`) is committed and live; validate every scenario under `--dry-run`. This gate creates the `evals/` artifact family — nothing else installs from it, so there is no red window.

Scenarios (graded difficulty; at least 2, up to 3):
- e.g. `evals/euler-1-multiples/` (easy: multiples of 3 or 5 below 1000; answer 233168)
- e.g. `evals/euler-2-even-fibonacci/` (easy-medium: sum of even Fibonacci < 4,000,000; answer 4613732)
- optionally `evals/euler-5-smallest-multiple/` (medium: smallest number divisible by 1..20; answer 232792560)

Each scenario directory:
- `task.md` — the prompt driving a REAL constellation workflow: a commander (delegated) solving "Project Euler #N with tests" as a bounded issue, running the engine spine and dispatching implementer/reviewer crew. The prompt must instruct the agent to work in the fixture repo, produce a solution file + a test file, run the tests green, drive an engine spine to completion, and (recommended) write a completion sentinel `eval-complete.txt` as the final step (the runner's liveness probe looks for `workspace/eval-complete.txt`, though an exit-0 run is also treated as completed — the verdict is still carried by the process checks below).
- `checks/` — PROCESS checks (gating). **BINDING CONSTRAINT (from g2-review, non-negotiable):** at least one process check MUST genuinely INSPECT the workspace for workflow completion — a present-but-non-biting check silently PASSes a broken run because the runner delegates completion-verification to these checks. Author these biting process checks:
  - `spine_completed.py` — finds an engine spine JSON under the workspace's `.agent-work/**` and asserts its steps/status reached a terminal/complete state; FAIL (non-zero) if absent or incomplete. It must actually parse and check, not just stat a path.
  - `artifact_present.py` — asserts the solution file exists and is non-empty.
  - `tests_green.py` — asserts a test file was WRITTEN and that `pytest` (or the repo's test runner) passes in the workspace; FAIL if no test written or tests red.
- `checks/answer/` — `answer_matches.py` (ADVISORY only, never gates): checks the computed Euler answer equals the known value. This exists to show answer-correctness is recorded but weak-never-sufficient (T3).
- `fixture/` — the seed repo state the agent starts from (e.g. a minimal README or an empty-ish project; `fixture/` absent => empty git repo is also fine). Keep fixtures tiny.
- `scenario.toml` (optional) — only if you override defaults (n=2, m=3, model, timeout). Pilots run one model tier down; you MAY set `model` to a cheap tier.

`evals/README.md` MUST (transcribe governance verbatim; do NOT author policy):
- The situational bar, verbatim intent: "new skill or behavior-changing rewrite → ≥1 scenario execution (itself N sub-runs) before install; mechanical edits → existing suite + git review; nothing gates on evals. No Iron Law."
- How to run the harness (`python scripts/run_skill_eval.py evals/<name>`), what the exit codes mean (0 PASS / 1 FAIL / 2 INCONCLUSIVE), and that N-of-M is a regression-vs-variance smoke, NOT a statistical guarantee (per contract §(iii)).
- The two STATED LIMITATIONS: (1) the broken-variant falsification is a FLOOR not a ceiling — it catches gross breakage; a subtly-regressed corpus that still completes the spine can still pass; subtle-regression sensitivity is curator portfolio-growth work. (2) Project Euler exercises workflow machinery (spines, handoffs, evidence discipline), NOT architecture judgment, so the portfolio MUST diversify.
- The named NEXT scenario, NOT built here: the delegated-commander selection scenario (cluster F's first non-Euler pilot) — document it as the named next portfolio addition.
- That transcripts are kept for diagnosis, never judged by the runner.

## Protected Intent
The verdict is carried by biting PROCESS checks; a scenario whose checks don't actually inspect the workflow defeats the whole harness. Answer-correctness is advisory only.

## Test Mode
Inspection + dry-run validation — the deliverable is scenario data + a doc; prove each scenario parses and both dry-run modes behave.

## Close Criteria
- 2–3 scenarios exist under `evals/<name>/`, each following the frozen schema, each with ≥1 genuinely-biting process check.
- `python scripts/run_skill_eval.py --dry-run evals/<name>` exits 0 (PASS) for each scenario; `--dry-run-fail evals/<name>` exits 1 (FAIL) for each — proving the checks bite the synthesized broken workspace. If a scenario's `--dry-run-fail` does NOT return FAIL, its checks are non-biting: FIX them (this is the binding constraint).
- `evals/README.md` covers the bar (verbatim), run instructions + exit codes, the two limitations, the named next scenario, and the transcripts-for-diagnosis note.
- Full suite still green: `py -m pytest -q` (the runner's own tests are unaffected; evals/ is not collected as agent-launching tests).
- `git check-ignore evals/euler-1-multiples/task.md` exits 1 (evals/ is committed, not ignored).

## Allowed Scope
CREATE under `evals/**` only, plus `evals/README.md`. Read (never edit) `scripts/run_skill_eval.py`, the contract note.

## Specific Exclusions
- Do NOT build the delegated-commander selection scenario — only NAME it in README.
- Do NOT edit the runner, tests, other skills, `_shared/`, or install bundles.
- Do NOT wire evals into default pytest collection.
- Do NOT commit any temp/run output (`evals/**/_runs/` is gitignored).

## Constraints
- Directory-is-schema exactly per contract §(a): `task.md` required; `checks/*.py` = process (≥1); `checks/answer/*.py` = advisory; optional `fixture/`, `scenario.toml`.
- Checks are plain executable scripts: `python checks/<name>.py <run-dir>`, exit 0 = pass, one stdout evidence line; they read the run-dir contract shape (`<run-dir>/workspace/`, `<run-dir>/spine.json` if written there — NOTE: read the runner's `_run_once` to see exactly where workspace + artifacts land, so checks look in the right place).
- Process checks must be robust (a spine check must parse and verify status, not vacuously pass on a missing key).

## Map Anchors (inbound)
- **Structural:** evals/<name>/ (NEW), evals/README.md (NEW); scripts/run_skill_eval.py (RELIED ON — validates scenarios).
- **Capability:** corpus eval — scenario portfolio.
- **Constraints:** process-checks-carry-verdict (T3, and they must BITE); nothing gates on evals.
- **Decision anchors:** scenario schema + N/M defaults frozen at g1.
- **Evidence expectations:** scenarios parse/validate under the runner dry-run; `--dry-run-fail` returns FAIL (checks bite).

## Deliverable Path Check
- **Committed** — `evals/**` (not ignored): confirm `git check-ignore` exits 1.
- **Local-only** — this handoff + your result under `.agent-work/`.

## Required Evidence
- For EACH scenario: `python scripts/run_skill_eval.py --dry-run evals/<name>; echo EXIT=$?` (want 0) and `--dry-run-fail evals/<name>; echo EXIT=$?` (want 1). Paste all.
- `py -m pytest -q` summary.
- `git check-ignore evals/<one-file>; echo $?` (want 1).
- Read `scripts/run_skill_eval.py::_run_once` and confirm your checks look where the runner actually puts the workspace/artifacts — state what you confirmed.

## Verification Commands
```bash
cd /c/Programs/constellation-wt-106
for d in evals/euler-*; do echo "== $d =="; py scripts/run_skill_eval.py --dry-run "$d"; echo "dry-run EXIT=$?"; py scripts/run_skill_eval.py --dry-run-fail "$d"; echo "dry-run-fail EXIT=$?"; done
py -m pytest -q
```

## Suggested Model Tier
stronger — reason: the biting-check requirement is subtle (a vacuous check silently defeats the harness); the task prompt must actually drive a real constellation workflow.

## Authority
Schema + N/M frozen; the bar text is epic-dispositioned (transcribe, don't author). You decide: which 2–3 Euler problems, fixture shape, exact check implementations, task prompt wording. If the run-dir contract can't be inspected by a plain check without a runner change, STOP and return it (this reopens g1/g3).

## Stop Conditions
Stop and return if: scope must be exceeded, a scenario's checks can't be made to bite under `--dry-run-fail`, or the schema can't express a needed scenario.

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/issue-106/crew-handoffs/g4-implementer-result.md`: scenarios authored, files created, per-scenario dry-run/dry-run-fail evidence (pasted), the _run_once inspection confirmation, README coverage checklist, assumptions, stop conditions, out-of-scope observations, workflow feedback. Final message = complete IMPLEMENTER_RESULT before idling.
