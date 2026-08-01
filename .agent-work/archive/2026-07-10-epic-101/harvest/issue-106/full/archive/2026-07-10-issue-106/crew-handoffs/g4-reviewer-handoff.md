# Reviewer Handoff

## Gate
g4 (pilot Euler scenarios + bar README)

## Survey State Location
`.agent-work/issue-106/g4-review/review.json`.

## What Was Implemented
3 graded Euler scenarios (`evals/euler-1-multiples`, `euler-2-even-fibonacci`, `euler-5-smallest-multiple`) to the frozen directory-is-schema, each with 3 process checks (`spine_completed.py`, `artifact_present.py`, `tests_green.py`) + advisory `checks/answer/answer_matches.py` + `fixture/README.md` + `task.md`, plus `evals/README.md`. Frozen contract: `.agent-work/issue-106/design/runner-contract.md`. Implementer result: `.agent-work/issue-106/crew-handoffs/g4-implementer-result.md`.

## How to Inspect the Diff
Review target = UNCOMMITTED working tree. `git status --porcelain` (expect untracked `evals/**`), read the files directly (`find evals -type f`).

## Task Statement
Author 2–3 graded Euler scenarios with GENUINELY BITING process checks + a bar README transcribing governance verbatim + the named-but-not-built next scenario.

## Close Criteria (each a review check)
- 2–3 scenarios follow the frozen schema; `checks/*.py` are process (gating), `checks/answer/*.py` advisory.
- For EACH scenario: `python scripts/run_skill_eval.py --dry-run evals/<name>` exits 0 AND `--dry-run-fail evals/<name>` exits 1. Reproduce all six yourself.
- `evals/README.md`: bar verbatim; run instructions + exit codes; N-of-M smoke-not-guarantee; the two stated limitations; the named next scenario (delegated-commander selection, NOT built); transcripts-for-diagnosis note.
- Full suite green (`py -m pytest -q`); `evals/` not committed as agent-launching tests.
- `git check-ignore evals/<file>` exits 1 (committed).

## CENTRAL REVIEW DECISION (Commander-flagged — you rule; you may BLOCK)
The `artifact_present.py` and `tests_green.py` checks have a documented **sentinel fallback**: they PASS if the real deliverable exists (primary branch) OR if `workspace/eval-complete.txt` exists (fallback). The fallback exists because the runner's frozen `dry_run_launch` synthesizes only the sentinel + a terminal spine (no real solution/test), so without the fallback `--dry-run` could not return PASS.

The residual hole: a LIVE run that drives the spine to completion and writes the sentinel but produces NO real solution/test would PASS `artifact_present`+`tests_green` (only `spine_completed`, which has no fallback, still bites). "Spine completes but no deliverable" is a plausible corpus regression the harness arguably SHOULD catch.

Rule between:
- **ACCEPT** the fallback as a bounded, documented FLOOR limitation: `spine_completed` is the strict primary gate, the hole is narrow (requires a terminal spine AND a sentinel AND no deliverable), and the g5 live broken-variant (spine template removed → spine_completed fails) is the contractual CEILING. If you accept, confirm the docs (checks + README limitation 1) state the hole honestly, and record it as a g5 focus.
- **BLOCK** to close the hole: require the checks be STRICT (drop the sentinel fallback — require a real non-empty solution `.py` and a real written+green test) AND correspondingly have `dry_run_launch` synthesize a minimal real `solution.py` + `test_*.py` so `--dry-run` still returns PASS. This touches `scripts/run_skill_eval.py` (the runner) — a bounded change the Commander will route back to a runner-gate rework. Choose this if you judge the vacuous-PASS mode unacceptable for the harness's core purpose.

Give your reasoning and cite the contract. This is a genuine judgment call; either verdict is defensible with a stated rationale.

## Allowed Scope
`evals/**`, `evals/README.md`. Runner/tests read-only.

## Specific Exclusions (flag if touched)
The delegated-commander scenario must be NAMED only, not built. Runner, tests, other skills, `_shared/`, install bundles unchanged.

## Constraints
- Directory-is-schema per contract §(a); checks plain scripts (exit 0 = pass); process checks must BITE; answer checks never gate (structural T3); nothing gates on evals.

## Map Anchors (inbound)
- **Structural:** evals/<name>/, evals/README.md (NEW); scripts/run_skill_eval.py (RELIED ON).
- **Constraints:** process-checks-carry-verdict AND must bite (T3); nothing gates on evals.
- **Evidence:** `--dry-run` PASS + `--dry-run-fail` FAIL per scenario.

## Evidence Produced
Implementer: all 3 scenarios `--dry-run` exit 0 / `--dry-run-fail` exit 1; per-check biting proof on a captured broken run-dir; live-like run-dir proof; `py -m pytest -q` = 513 passed, 2 skipped; `git check-ignore` exit 1. Reproduce what you rely on. Target postconditions: `g4-integrate.c1` (dry-run validate + suite green) + `g4-integrate.c2` (this APPROVE).

## Suggested Model Tier
stronger — the sentinel-fallback decision is load-bearing for whether the harness actually catches a broken corpus.

## Stop Conditions
BLOCK if: a scenario's checks don't bite under `--dry-run-fail`, the README misses required governance, evidence doesn't reproduce, or you judge the vacuous-PASS hole unacceptable (per the central decision).

## Return Format
Write REVIEW_RESULT to `.agent-work/issue-106/crew-handoffs/g4-reviewer-result.md`: verdict (APPROVE/BLOCK), per-check findings, your ruling on the central decision with rationale, blockers, out-of-scope observations, workflow feedback. Final message = complete REVIEW_RESULT before idling.
