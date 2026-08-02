# Reviewer Handoff — G2 Lateral Units Fix review (#522)

## Gate
g2-review (verify the lateral units fix — a SHARED production physics change with inverted-convention risk)

## What Was Implemented
A lateral-grip units fix (same class as #518 G5). `LateralView` produces A0/A2 as g-unit grip coefficients; consumers read them as m/s². The implementer added a single `G_MS2 = 9.81` in `physics_data_models.py` and applied ×g + dropped the spurious ×ρ across: `LateralParameters.lateral_capability` (root), `physics_simulator._compute_speed_caps` + `_gsat_ceiling` (inline), `capability_envelope` ceiling-trust headroom check. `friction_coupling`/`apex_extract` delegate to the root. 9 test files re-baselined (inputs changed A0≈30 m/s² → A0≈3 g-units), incl. 4 known-answer tests. Result: `.agent-work/522-phase-align-utilization/crew-handoffs/g2-implement-result.md` + `g2/audit-findings.md`.

## How to Inspect the Diff
Uncommitted on `feat/522-phase-align-utilization` (main checkout `C:/Programs/f1Brainz`): `git --no-pager diff -- src/physics tests` and `git status`. Run from repo root; `py` launcher.

## Task Statement
Apply ×g and drop the spurious ρ across all lateral consumers with one canonical convention, truth-anchored (corrected Monaco/VER tunnel cap ~63–66 m/s, not 16), re-baselining tests to physical truth — correcting the #485 production envelope, physics-only blast radius.

## Close Criteria (each a review check)
- ×g + drop-ρ applied correctly and consistently at every lateral consumer; ceiling units consistent; **no double-correction**; single canonical `G_MS2`.
- Corrected tunnel cap ~63–66 m/s (truth-anchored against VER's actual 63.3); the truth-anchor tests genuinely RED pre-fix / GREEN post-fix.
- Re-baselined tests assert PHYSICAL truth (~3–5 g lateral), not mechanically-scaled old numbers.
- The FULL physics region is green (not just the g2 nine-file list).

## TWO TOP-RISK CHECKS (the core review value — do these rigorously)

### RISK 1 — the inverted-convention / runtime-disjointness claim (MAKE-OR-BREAK)
The fix **inverts** which unit convention `lateral_capability` is correct for. Pre-fix it was correct for **convention A** (m/s², `LateralEnvelopeFit`/`ParameterEstimator`→`FitStore` `session_fits`, `default_A0=30`); post-fix it is correct for **convention B** (g-units, `lateral_view`→`session_estimates` store→`car_prior`, A0≈1.6–5.0). The implementer asserts convention A is **runtime-disjoint** — never flows a convention-A `LateralParameters` (A0≈30 m/s²) into the now-fixed `lateral_capability`/simulator/envelope at runtime. **If that claim is wrong, any live convention-A path now computes ~30×9.81 ≈ 294 m/s² (30 g) — catastrophically wrong.** Verify it independently:
- Enumerate every LIVE producer of a `LateralParameters` (or anything that reaches `CapabilityEnvelope.from_parameters` / `lateral_capability` / `_compute_speed_caps`). Trace `session_fit.fit_driver`, `parameter_estimator`, `FitStore`/`session_fits`, and the five-view `estimate_session`/`car_prior` path.
- Confirm the ONLY runtime path into the fixed consumer is convention B (g-unit store). If `fit_driver`/convention-A results can reach `lateral_capability` or the sim in any non-test code path, that is a **BLOCK** (the fix would need a conversion at the convention-A boundary, or the legacy path retired in-scope).
- State your evidence (the call chains you traced).

### RISK 2 — known-answer re-baselining anchored to PUBLISHED truth
4 tests in `tests/known_answer/test_published_f1_data.py` were re-baselined. The implementer says they previously **saturated the Gsat clamp** (every grip value gave the same 96.59 s lap → no grip directionality), and the fix RESTORES directionality with Monza staying in the published 60–120 s band. Verify:
- The re-baselined expectations still match PUBLISHED F1 truth (lap-time bands, grip→laptime directionality), NOT loosened to pass.
- The "previously saturating" claim is real (i.e. the old test was masking a bug, the fix is a genuine improvement) — not the fix degrading a real known-answer check.
- If any known-answer expectation was weakened below published truth → BLOCK.

## Other checks
- Ceiling units: implementer resolved `lateral.ceiling` to m/s² (traced to `lateral_envelope._detect_ceiling`); the only mixed-unit site was the `capability_envelope` headroom check, now `(ceiling − A0·g_track·G_MS2)`. Confirm consistent.
- `friction_coupling.compute_friction_utilization` (dimensionless ratio) and `apex_extract._on_limit` (delegates) — confirm invariant to ×g, no stranded compensation.
- Independent truth-anchor: recompute one corrected cap from real producer A0 (e.g. VER Monaco A0≈3.2, κ≈0.011) → ~63–66 m/s.

## Allowed Scope (of the change under review)
`src/physics/physics_data_models.py`, `physics_simulator.py`, `capability_envelope.py`, and tests under `tests/unit/physics/`, `tests/known_answer/`, `tests/property/`. Producer `lateral_view.py`, store schema, and `regime_utilization.py` logic must be UNTOUCHED — flag if changed.

## Constraints
- `py` launcher; physics-model change → highest-applicable L1–L4 truth evidence.
- `constraint:physics_region_no_evo_import` honored.
- Read-only store/cache via absolute main-checkout paths for any independent fit.

## Map Anchors (inbound)
Inherits g2-implement anchors: `struct:physics` (lateral_capability / _compute_speed_caps / _gsat_ceiling / capability_envelope), `struct:physics.layer2.lateral_view` (g-unit producer of truth), `decision:ideal_lap_sim_two_sided_evaluator` (sibling of #518 G5).

## Evidence Produced
g2 suite 124 passed/2 skipped; full `tests/unit/physics/` 607 passed/6 skipped; g2+blast (incl known_answer+property) 215 passed/2 skipped; truth anchors RED→GREEN. Re-run to confirm.

## Verification Commands
```bash
git --no-pager diff -- src/physics tests
py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q
```

## Suggested Model Tier
Stronger (opus) — inverted-convention disjointness trace + known-answer truth judgment on shared production physics.

## Stop Conditions
BLOCK if: a live convention-A path reaches the fixed consumer; any known-answer expectation was weakened below published truth; the fix math is wrong at any site; or a double-correction/stranded compensation exists.

## Return Format
REVIEW_RESULT to exactly `.agent-work/522-phase-align-utilization/crew-handoffs/g2-review-result.md`: verdict (APPROVE/BLOCK), per-check findings, the RISK-1 disjointness trace evidence, the RISK-2 known-answer judgment, blockers, out-of-scope observations, workflow feedback.
