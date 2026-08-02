# Reviewer Handoff

## Gate
g1 — Scoring primitives + report schema (review)

## What Was Implemented
A new pure submodule `src/preprocessing/trajectory_grading/` with: a candidate-trajectory
contract (`contract.py`), sector-anchor gate (`sector_anchor.py`, co-estimates anchors via
scipy least_squares), covariance-consistency gate (`covariance_gate.py`, reduced chi-square),
cross-residual diagnostic (`cross_residual.py`, per-lap inter-stream offset fit), frozen JSON
report schema (`report_schema.py`), and `docs/report_schemas/trajectory_grading_report.md`.
47 unit tests in `tests/unit/preprocessing/test_trajectory_grading.py`.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-446
git show 3ee04fe -- src/ tests/ docs/
```
(Ignore the `.agent-work/` scratch files in the commit — review only `src/`, `tests/`, `docs/`.)
Full implementer report: `.agent-work/issue-446/crew-handoffs/g1-implement-RESULT.md`.

## Task Statement
Build the pure scoring core of a trajectory grading harness: the three scoring primitives
(sector-anchor gate, covariance-consistency gate, cross-residual diagnostic) + a frozen JSON
report schema + schema doc, with truth-anchored L1/L2 unit tests. No fastf1/DB IO this gate.
Full task: `.agent-work/issue-446/crew-handoffs/g1-implement.md`.

## Close Criteria (each becomes a review check)
- Three primitives match the issue contract.
- Sector-loop anchor positions are CO-ESTIMATED free parameters with reported uncertainty —
  NOT hard-coded constants anywhere.
- Cross-residual is a DIAGNOSTIC with NO pass/fail field — never a gate.
- Covariance-consistency gate computes reduced chi-square and is honest (matching covariance
  → ≈1 passes; mismatched → departs from 1 fails).
- Truth-anchored tests genuinely RECOVER injected known anchors/offset (NOT tautological:
  confirm the test injects a known value and asserts recovery of that value, not a round-trip
  of the same computed quantity).
- Report schema producer + `docs/report_schemas/trajectory_grading_report.md` move together
  and the doc matches the dataclass fields.
- Input validation names field/expectation/actual; degenerate inputs raise, not silent-NaN.
- `py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q` is GREEN.
- `py -m src.utils.simplification_limits` passes on touched paths.
- No imports from `src/evo_predictor`, `src/latent_power`, `src/compound_prior`; no fastf1/DB.

## Allowed Scope
`src/preprocessing/trajectory_grading/`, `tests/unit/preprocessing/`,
`docs/report_schemas/trajectory_grading_report.md`.

## Specific Exclusions
No fastf1/DB/network; no touch to `windowed_estimator.py`, `src/physics/`, or evo modules;
no estimator/filter logic. Flag if any were touched.

## Constraints the Implementation Must Respect
- Physics-region isolation (no evo imports).
- Anchors are calibration parameters with uncertainty, never hard-coded.
- Cross-residual is a diagnostic, never a gate.
- Report-schema atomicity (producer + doc together).
- Physics evidence bar: truth-anchored, units/bounds/invariants explicit.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing` — `src/preprocessing/trajectory_grading/`, container.
- **Capability:** trajectory grading — three scoring primitives + report schema.
- **Constraints/assumptions:** physics-region-isolation; report-schema-atomicity;
  anchors-are-calibration-parameters; cross-residual-is-diagnostic-not-gate.
- **Decision anchors:** physics-primary, grading-field-first — schema is the Phase 0b/1 contract.
- **Evidence expectations:** L1/L2 known-answer recovery; white-noise reduced chi-square ≈ 1.

## Evidence Produced
- `py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q` → 47 passed in 0.29s.
- `py -m src.utils.simplification_limits ...` → PASS (7 files checked).
Re-run both to confirm; spot-check at least the known-answer recovery test and the
covariance-honesty test for substance.

## Suggested Model Tier
stronger — reason: numerical correctness of anchor co-estimation + chi-square honesty +
durable-schema judgement; tautology risk in known-answer tests needs a careful read.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, evidence is absent/unverifiable, a primitive
violates a constraint (hard-coded anchors / cross-residual-as-gate / evo import), or a known-
answer test is tautological. Otherwise APPROVE.

## Return Format
Return REVIEW_RESULT to `.agent-work/issue-446/crew-handoffs/g1-review-RESULT.md`: verdict
(APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
