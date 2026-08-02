# Reviewer Handoff — G1 (#675 diagnosis + frozen-constant pre-registration)

## Gate
g1-review (issue #666, epic #659)

## Survey State Location
Create your review survey at `.agent-work/666-driver-fingerprint/g1-review/review.json` (NOT the worktree root).

## What Was Implemented
A new `src/physics/fingerprint/` package's pre-registered frozen constants (`FINGERPRINT_FROZEN`), a #675
class-axis coverage diagnostic `scripts/fingerprint_class_coverage_675.py` (reproduces #665's coverage method
on the real bounded slice), a verdict JSON, and `tests/unit/physics/fingerprint/test_frozen_constants.py`.

## How to Inspect the Diff
Review the UNCOMMITTED working tree of `C:/Programs/f1brainz-wt/epic659-666` (NOT `git diff main...HEAD`).
`git status --porcelain` then `git diff` (untracked-safe). New files under `src/physics/fingerprint/`,
`scripts/`, `tests/unit/physics/fingerprint/`. Read the implementer result at
`.agent-work/666-driver-fingerprint/crew-handoffs/g1-implement-result.md` and the verdict at
`.agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json` (Local-only — intentionally NOT in
the diff; do not flag as missing). The read-only input slice DB is
`.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db` (also Local-only).

## Task Statement
Build the pre-registered `FINGERPRINT_FROZEN` set (4 exact commander-set values) and a #675 coverage diagnostic
that faithfully reproduces #665's method on the REAL slice's support structure, emitting a per-channel verdict.

## Close Criteria (each becomes a review check)
- `FINGERPRINT_FROZEN` holds EXACTLY: NOMINAL_COVERAGE_LEVEL=0.80, UNDER_COVERAGE_BOUND=0.60,
  RECENCY_HALFLIFE_ROUNDS=5.0, UNRESOLVED_SUPPORT_FLOOR=1.0 — each documented as pre-registered (F12). NO extra
  constants; NO value tuned to the slice; NO duplicate inline literal of these anywhere in the new code.
- The coverage harness FAITHFULLY reproduces #665's method (compare against `scripts/pooling_imbalance_validation_665.py`):
  synthetic-recovery with KNOWN injected truth; per-cell support counts taken from the REAL slice; `fit_two_way`
  driver×class; each axis wrapped in `predictive_t(eff, sem, n_eff, nu_loss=4.0, rule=FormulaRule())` where
  **`n_eff` = summed observation count, NOT the pooled group `.n` count** (verify this specific line); level 0.80;
  N_REPS>=200; BOTH channels + BOTH axes; empirical coverage reported WITH a binomial CI.
- The verdict JSON's per-channel `generalizes` flag = (class-axis coverage CI upper < 0.60) and the
  `shared_floor_recommendation` follow from the numbers.
- `test_frozen_constants.py` passes (re-run it).
- No `pooling.py`/`student_t.py`/`driver_utility.py` edit; no `data/`/`.agent-work/` blob staged.

## Allowed Scope
New files under `src/physics/fingerprint/`, `scripts/fingerprint_class_coverage_675.py`,
`tests/unit/physics/fingerprint/`. Read-only consumption of pooling/student_t/#665 harness.

## Specific Exclusions
Do not require the store/vocabulary/fit (those are G2/G3). The driver-axis under-coverage caveat is a KNOWN,
commander-adjudicated finding (bounded few-groups artifact) — not a defect of this gate.

## Constraints the Implementation Must Respect
- Interpreter PIN + `PYTHONPATH=.` from worktree root. `from src...` import style.
- 4 values pre-registered (not data-tuned); no inline-literal duplication.
- #675 forbids editing pooling.py/student_t.py/driver_utility.py.
- No data/.agent-work blob in the diff.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` fit_two_way/pool_random_effects; `struct:common` predictive_t/FormulaRule; NEW `struct:physics.fingerprint`.
- **Constraints/assumptions:** frozen constants F12 (pre-register before first real fit).
- **Decision anchors:** `decision:pooled_sigma_shared_systematic_floor` — shared_floor is the class-axis lever.
  `@grade: settled/measured · leans g1-implement,g3-implement`
- **Evidence expectations:** `claim: #675-coverage`.

## Evidence Produced
Implementer result (path above) with the pasted verdict JSON + `test_frozen_constants.py` 4/4 pass. Commander
independently re-ran the test (4/4) and confirmed the tree is clean. Verify against `g1-integrate.c1` (the
frozen-constants pytest command) and `g1-integrate.c2` (this APPROVE verdict).

## Suggested Model Tier
Stronger — the #665 method-fidelity check (n_eff semantics especially) is the load-bearing review point.

## Stop Conditions
BLOCK if: the coverage harness deviates from #665's method in a way that changes the verdict (esp. n_eff =
group count instead of summed obs count); a frozen value is wrong or data-tuned; a forbidden file was edited;
evidence unverifiable.

## Return Format
Return REVIEW_RESULT: verdict APPROVE or BLOCK, per-check findings, blockers, out-of-scope observations,
workflow feedback. Deliver the REVIEW_RESULT via SendMessage to cmdr-666 before ending your turn, and write it
to `.agent-work/666-driver-fingerprint/crew-handoffs/g1-review-result.md`.
