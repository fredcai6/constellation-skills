# Run Summary — issue #446 (Phase 0a trajectory grading harness)

## Verdict
**Harness built and DISCRIMINATING.** Not a null. The permanent trajectory grading harness
exists in the physics region, its scoring primitives are truth-anchored unit-tested, and the
≥3-session strawman run proves the harness separates a pathological trajectory from a good one
via the sector-anchor gate, while surfacing a sharp, honest Phase-0b finding about the
covariance gate's tolerance.

## Gates closed (3, all reviewer-APPROVED)
- **g1 — scoring primitives + report schema.** Candidate-trajectory contract; sector-anchor gate
  (co-estimates anchors, never hard-coded); covariance-consistency gate (reduced chi-square);
  cross-residual diagnostic (per-lap inter-stream offset, NOT a gate); frozen JSON report schema +
  `docs/report_schemas/trajectory_grading_report.md`. 47 unit tests. **One BLOCK → rework:**
  reviewer caught s3 anchor not actually co-estimated (zero gradient) + a tautological s3 test;
  fixed and re-approved (guard now: 650m injected delta vs 50ms tol fails old code).
- **g2 — loaders + strawman + runner.** Offline raw-stream loader (car_data/pos_data only);
  read-only DB truth loader (`file:?mode=ro`); strawman wrapping merged `get_telemetry` (the one
  sanctioned exception); runner → JSON report. 19 integration tests. Reviewer independently
  verified the decimetre arc-length scaling (6941.6m vs FastF1's 6949.5m on Spa).
- **g3 — multi-session strawman run + verdict.** 3 sessions (2023 Belgium Q, 2023 Belgium R,
  2022 Spain R — 1 quali + 2 race, 2022-2023). Reviewer independently confirmed every verdict
  number against the raw reports.

## Key numbers (strawman, tol 50ms)
| Session | anchor gate | max resid | RMS resid | reduced chi-sq | cov gate | offset range |
|---|---|---|---|---|---|---|
| 2023 Belgium Q | FAIL | 1.505s | 0.300s | 11.14 | PASS | [-0.20, +0.41]s |
| 2023 Belgium R | FAIL | 1.067s | 0.158s | 3.07 | PASS | [-0.23, +0.03]s |
| 2022 Spain R | FAIL | 0.296s | 0.070s | 0.60 | PASS | [-0.08, +0.36]s |

## Interpretation
- **Discrimination via gate (a):** the strawman fails the sector-anchor gate in all 3 sessions
  by 6-30x the 50ms threshold. Free-anchor co-estimation absorbs the mean bias but NOT the
  per-lap variance of sector-crossing times — that variance is the discriminating signal.
- **Honest Phase-0b finding on gate (b):** with the current loose band [0.01, 100] the strawman
  PASSES the covariance gate despite chi-squares 0.60-11.14, so gate (b) does not yet discriminate.
  Tightening toward ~[0.5, 2.0] against a characterized error model is the headline 0b task.
- **Cross-residual diagnostic (c):** fitted inter-stream offsets sit in ~[-0.23, +0.41]s and
  WANDER per lap (not a stable bias) → quantified jitter, exactly the diagnostic 0b consumes.

## Map impact
- New submodule `src/preprocessing/trajectory_grading/` (11 modules) under `struct:preprocessing`.
- New committed report schema `docs/report_schemas/trajectory_grading_report.md` (Phase 0b/1 contract).
- New overlay constraint `constraint:physics_region_no_evo_import` + `constrained-by` edge.
- index.md reconciled 2026-06-11; `check_arch_map.py` green (37 nodes, 16 packets, 11 overlays).

## Triage (6 candidates, filing floated to Admiral)
tc1 (s_finish free?) + tc6 (covariance band) → fold into Phase 0b. tc2 (scipy dep), tc3 (decimetre
doc), tc4 (GP-name normalization), tc5 (FastF1 version guard) → optional consolidated hygiene issue.

## Acceptance
Delivers exactly the launch order's required shape (harness + strawman, discrimination proven,
machine-readable reports, unit-tested primitives, honest secondary null on gate b). Accepted on
the Admiral's delegated authority; PR to be opened (not merged), verdict to be posted on #446.
