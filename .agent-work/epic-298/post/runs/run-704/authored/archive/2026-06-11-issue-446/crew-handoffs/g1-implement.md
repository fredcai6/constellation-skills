# Implementer Handoff

## Gate
g1 — Scoring primitives + report schema

## Task
Build the pure, dependency-light core of a trajectory grading harness in a NEW submodule
`src/preprocessing/trajectory_grading/`. This gate is PURE: operate on plain numpy arrays /
dataclasses only — NO fastf1 and NO database IO (those arrive in g2). Deliver five things:

1. **Candidate-trajectory contract** — a dataclass/Protocol representing a candidate per-lap
   trajectory product: time-sampled arc-length `s(t)` samples (1D arrays of session-time and
   arc-length), a reported covariance / per-sample variance on the relevant residual quantity,
   and accessors for (a) arc-length at a given time and (b) integrated-speed arc length. Include
   per-lap structure (lap index → sample slice) and the position-derived arc length per lap.
   Document units (seconds, metres) explicitly.

2. **Sector-anchor gate primitive** — `score_sector_anchor(candidate, official_splits, tol_s=0.050)`.
   Official input: per-lap per-sector split DURATIONS (sector1/2/3, seconds). Sector-loop
   arc-length positions along the track are NOT published, so they are FREE CALIBRATION
   PARAMETERS: co-estimate the per-circuit sector-loop anchor arc-lengths (and start/finish
   line) that best reproduce the official sector splits given the candidate's `s(t)`, and report
   the fitted anchors WITH UNCERTAINTY. Return predicted-vs-official sector-crossing residuals
   (per lap/sector) and a pass/fail at the configurable tolerance (default 50 ms). Anchors are
   NEVER hard-coded constants — they are estimated/supplied inputs.

3. **Covariance-consistency gate primitive** — `score_covariance_consistency(residuals, covariance, band=(...))`.
   Compute reduced chi-square of the residuals against the candidate's reported covariance and
   pass/fail when it falls in a configurable band around 1. The covariance must honestly
   describe the error.

4. **Cross-residual DIAGNOSTIC primitive (NOT a gate)** — `diagnose_cross_residual(candidate)`.
   Per lap, fit a free inter-stream time offset; compare integrated-speed arc length vs
   position-derived arc length with the lap-closure constraint. Return the fitted per-lap
   offsets and arc-length residuals. NEVER returns a pass/fail — it is reporting only. Do NOT
   assume the two streams' clock pathologies are independent.

5. **JSON report schema** — frozen dataclasses for the full grading report (session id,
   per-lap/per-sector anchor-gate results, covariance-gate result, cross-residual diagnostic
   block, fitted anchors+uncertainty, tolerances used) with a `to_dict()`/serializer producing
   stable JSON. PLUS `docs/report_schemas/trajectory_grading_report.md` documenting every field
   (producer + schema doc move together — repo policy).

## Protected Intent
The harness must DISCRIMINATE: a good trajectory passes, a pathological one (e.g. the strawman
arriving in g2) shows structured residuals / dishonest covariance. Covariance honesty matters
more than point accuracy. Anchors-as-parameters and cross-residual-as-diagnostic are inviolable.

## Test Mode
TDD required. The scoring primitives are the testable heart; write truth-anchored tests first.

## Close Criteria
- All five deliverables exist in `src/preprocessing/trajectory_grading/`.
- Truth-anchored unit tests in `tests/unit/preprocessing/test_trajectory_grading.py`:
  - **L1/L2 known-answer:** a synthetic candidate built with KNOWN sector-loop anchors and a
    KNOWN inter-stream offset → the gate recovers the anchors (within stated uncertainty) and
    the diagnostic recovers the offset.
  - **Covariance honesty:** white-noise residuals with matching covariance → reduced chi-square
    ≈ 1 (passes); inflated/deflated covariance → chi-square departs from 1 (fails).
  - **L3 degenerate/limit:** e.g. zero-variance, single-lap, missing-sector inputs handled with
    explicit validation errors (naming field/expectation/actual), not silent NaN.
- `py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q` is GREEN.
- `py -m src.utils.simplification_limits` passes on every touched `src/`/`tests/` path.

## Allowed Scope
`src/preprocessing/trajectory_grading/` (new), `tests/unit/preprocessing/` (new test file),
`docs/report_schemas/trajectory_grading_report.md` (new).

## Specific Exclusions
- No fastf1 import, no DB IO, no network — pure core only (those are g2).
- Do NOT touch `src/preprocessing/windowed_estimator.py`, `src/physics/`, or any evo module.
- No estimator/filter work — this is grading only.

## Constraints
- Physics region only: NO imports from `src/evo_predictor`, `src/latent_power`, `src/compound_prior`.
- Anchor sector-loop positions are calibration parameters with uncertainty, never hard-coded.
- Cross-residual is a diagnostic, never a gate.
- Truth-anchored L1-L4 evidence; units, bounds, invariants explicit.
- Committed report schema needs producer + `docs/report_schemas/` doc together.
- `py`, never `python`. Tests via `py -m pytest`.

## Map Anchors (inbound)
- **Structural:** `struct:preprocessing` — `src/preprocessing/trajectory_grading/` (new submodule), container.
- **Capability:** trajectory grading — the three scoring primitives + report schema.
- **Constraints/assumptions:** constraint:physics-region-isolation; constraint:report-schema-atomicity;
  assumption:anchors-are-calibration-parameters; assumption:cross-residual-is-diagnostic-not-gate.
- **Decision anchors:** physics-primary, grading-field-first (spec 2026-06-10). The committed
  report schema becomes the Phase 0b/1 contract — design it stably.
- **Evidence expectations:** L1/L2 synthetic known-answer tests recover anchors/offset; white-noise
  reduced chi-square ≈ 1.

## Required Evidence
- `py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q` output (green).
- `py -m src.utils.simplification_limits <touched paths>` output (pass).
- A short note in IMPLEMENTER_RESULT on how the known-answer test proves recovery (not a tautology).

## Verification Commands
```bash
py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q
py -m src.utils.simplification_limits src/preprocessing/trajectory_grading tests/unit/preprocessing/test_trajectory_grading.py
```

## Suggested Model Tier
stronger — reason: numerical scoring primitives + anchor co-estimation + covariance statistics
need care; the schema is a durable contract.

## Authority
Module placement, JSON schema fields, anchor co-estimation method, and tolerance bands are
yours to decide within the constraints above (Commander latitude delegated). You may NOT: cross
into the data/evo regions, hard-code anchor positions, turn the cross-residual into a gate, or
add estimator/filter logic. Surface anything needing those.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; an exclusion must be touched; the
known-answer test cannot be made to recover anchors/offset (report what blocks it — that is
itself a finding); a decision outside your authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write it to `.agent-work/issue-446/crew-handoffs/g1-implement-RESULT.md`):
completed slice, files changed, test mode satisfied, evidence produced (paste the green test
summary + simplification-limits result), assumptions used, stop conditions hit, out-of-scope
observations, and workflow feedback (what in this handoff/workflow made the work harder).
