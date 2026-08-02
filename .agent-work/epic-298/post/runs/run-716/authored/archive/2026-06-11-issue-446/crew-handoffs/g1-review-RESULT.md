# Review Result

## Assigned Gate
`g1 — Scoring primitives + report schema (RE-REVIEW after rework commit 579dbca)`

## Result
`APPROVE`

## Handoff compliance
Both blockers from the prior BLOCK review are genuinely and completely fixed. The change does exactly what the rework handoff required and stays within the allowed scope. All original close criteria are satisfied.

## Scope drift
Clean. Commit 579dbca touches exactly two files: `src/preprocessing/trajectory_grading/sector_anchor.py` and `tests/unit/preprocessing/test_trajectory_grading.py`. No `.agent-work/` files counted; no schema, docs, contract, covariance_gate, cross_residual, or other files touched.

## Evidence verdict
Both required evidence commands independently re-run and confirmed:
- `py -m pytest tests/unit/preprocessing/test_trajectory_grading.py -q` → **47 passed in 0.19s** ✓
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory_grading tests/unit/preprocessing/test_trajectory_grading.py` → **PASS (7 files)** ✓

Evidence is present and demonstrates correct behavior.

## Code/doc quality

**Defect 1 — s3 anchor co-estimation (FIXED):**

`_build_residuals_fn` (lines 129–145): `s3_est = x[2]` is now used to compute `t_s3 = _interp_time_at_arc(s3_est, s_arr, t_arr)` (line 138), and the sector-3 residual is `(t_s3 - t_s2) - off["s3"]` (line 143). This gives s3_est a real gradient through `_interp_time_at_arc`; `least_squares` can and does move it.

`_compute_lap_residuals` (lines 150–172): same pattern applied — `t_s3 = _interp_time_at_arc(s3_fit, s_arr, t_arr)` (line 165) and `"s3": (t_s3 - t_s2) - off["s3"]` (line 170). The call site in `score_sector_anchor` threads `s3_fit` in (line 220). Both sites fixed, as required.

The prior BLOCK review's out-of-scope observation ("_compute_lap_residuals similarly does not use s3_fit") is also addressed — this was a necessary collateral fix, confirmed present.

**Defect 2 — s3 known-answer test guard (FIXED + GUARD PROVEN):**

`_make_known_anchor_scenario`: `known_anchors[3] = 0.72 * lap_length_m` (was 0.85). With `lap_length_m=5000m`, expected s3 = 3600m; optimizer initial guess `x0[2] = 0.85 * 5000 = 4250m`. Gap = 650m >> 50m tolerance.

`_make_official_splits`: `"s3": t_s3 - t_s2` (was `t_lap_end - t_s2`). This aligns the helper's formula with the corrected residual formula in `_build_residuals_fn`. The optimizer's residual for sector 3 is zero iff `s3_est` crosses at the true s3 arc-length; the official splits are synthesised from that same crossing time, so the system is internally consistent and uniquely solved at `s3 = 3600m`.

**Guard proof (analytical):** With the old buggy residual `(t_end - t_s2) - off["s3"]`, the gradient w.r.t. `s3_est` is zero; `least_squares` returns `s3_fit = 4250m` (initial guess) regardless of data. The test asserts `|fitted - expected| < 50m` → `|4250 - 3600| = 650m` → test FAILS on buggy code. With the fix, the optimizer has a non-zero gradient and finds `s3_fit ≈ 3600m` → test PASSES. The guard is real and catches the original defect.

**Collateral change: `test_sector_anchor_fails_for_bad_candidate`**

The old test corrupted all sector splits uniformly (+200ms on every sector of every lap). With s3 now having a real gradient, the optimizer absorbs uniform-across-all-laps corruption by shifting all anchors forward uniformly — no lap-inconsistency, so residuals go to zero and the test would incorrectly pass.

The new test corrupts lap 0 only (+200ms on all sectors). Anchors are shared across all laps (only 3 free parameters for N_laps×3 residuals). Moving anchors to absorb lap-0 corruption introduces equal-and-opposite errors on laps 1–3. With 4 laps × 3 sectors = 12 residuals and only 3 free parameters, the per-lap-inconsistent corruption is mathematically inabsorbable. The assertion `not result.passed` is sound. This is a genuine FAIL-verdict test, and the soundness argument is correct.

**No regressions:**
- s1 and s2 co-estimation: unchanged and correct.
- Cross-residual: no `passed` field in `CrossResidualDiagnostic` or its serialized output; unaffected by rework.
- Covariance gate: unaffected.
- No `src.evo_predictor`, `src.latent_power`, `src.compound_prior`, `fastf1`, or DB imports anywhere in the new module.
- Schema/doc: no changes; still consistent.

## Map impact verdict

- **Evidence supports claimed change:** Yes. The test suite with the non-tautological s3 recovery check (650m gap from initial guess, 50m tolerance) constitutes evidence that s3 is genuinely estimated. Analytical guard proof confirms the test catches the original defect.
- **Constraints not violated:** All constraints honored: `anchors-are-calibration-parameters` now holds for s3; `cross-residual-is-diagnostic-not-gate`, `report-schema-atomicity`, `physics-region-isolation` all unchanged and still honored.
- **Notes match the diff:** Yes. The rework report accurately describes both fixes, the collateral `_compute_lap_residuals` change, the `_make_official_splits` update, and the `test_sector_anchor_fails_for_bad_candidate` motivation.
- **Decision candidates surfaced:** N/A for this rework (no new design decisions; fixes were precisely specified).
- **Durable context routed:** The original implementer's triage candidates (s_finish free-parameter question, scipy dep) carry over; no new durable context generated by the rework.

## Reconciliation check
No architecture baseline drift. The rework is a correctness fix within an already-approved structural boundary; no Cartographer reconciliation needed.

## Blockers
None.

## Out-of-scope observations
- The `except Exception: pass` broad-catch in `_estimate_anchor_uncertainty` (noted as a secondary concern in the prior review) was not addressed in this rework. This is correct scoping — the rework was bounded to the two BLOCK items. The concern stands as a future hardening candidate: a broad-catch that falls back to `0.01 * lap_length_m` could mask genuine optimizer failures. Triage candidate if hardening is desired.
- `test_sector_anchor_custom_tolerance` with `tol_s=0.0` still makes no assertion about pass/fail beyond "it doesn't crash." Noted previously; unchanged; not a blocker.

## Workflow Feedback

- **Handoff gaps:** The re-review handoff was precise and complete. The two blockers were described with exact function names, line numbers, expected fix form (`t_s3 = _interp_time_at_arc(s3_est, ...)`), and the guard-proof specification (rollback the buggy residual, confirm test FAILS). No ambiguity encountered.
- **Context rediscovered:** The guard-proof instruction said to "temporarily revert the s3 residual" to verify, or to reason analytically if unsafe. I chose the analytical path: the 650m vs 50m gap and zero-gradient argument is airtight and required no code mutation. The handoff correctly identified this as the primary guard-proof mechanism.
- **Instructions improvised around:** The `references/checklist-engine.md` file does not exist in the installed skill directory (same gap as prior review). I drove the survey from the template JSON structure and SKILL.md directly. No impact on review quality.
- **What would have made this easier:** None — the re-review handoff was well-specified. The prior review's workflow feedback about sharpening the "CO-ESTIMATED free parameters — including s3" check was incorporated in the re-review brief, which is exactly the right feedback loop.

## Return status
`complete`
