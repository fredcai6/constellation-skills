# Reviewer Handoff

## Gate
`g4` — held-out-weekend DIAGNOSTIC (strictly-pre). THE leakage-critical gate. Review rigor: HIGH (subtle-and-silent correctness).

## Survey State Location
`.agent-work/670-season-run/g4-review/review.json`

## What Was Implemented
NEW `scripts/run_heldout_diagnostic_670.py` + `tests/unit/physics/fingerprint/test_heldout_diagnostic.py`. For each held-out weekend W (round R), predicts each driver's composition-weighted weekend utilization via 3 arms and scores vs the ACTUAL: (1) fingerprint×composition = join(W field-composition, cells@R-1); (2) driver-overall-only = join(uniform composition, same cells) [T7-1 baseline]; (3) golf null = per-class field mean pooled over rounds<R (no driver term) × W composition. Implementer result: `.agent-work/670-season-run/crew-results/g4-implementer-result.md`.

Headline results (real slice, rounds 6-22 resolved, 4-5 thin, 3 unresolvable): |resid| — fingerprint×comp 0.854, driver-overall 1.143, golf null 0.830. Log-score is confounded (see below).

## How to Inspect the Diff
Both files NEW/untracked — inspect directly (`git status --porcelain`, read the two files). Not `git diff main...HEAD`.

## Task Statement
Strictly-pre 3-arm held-out diagnostic composing LANDED pieces (join_weekend_prior, fit_driver_fingerprints); build no new model. Full task: `.agent-work/670-season-run/handoffs/g4-implementer-handoff.md`.

## Close Criteria (each a review check — verify INDEPENDENTLY)
- **LEAKAGE GUARD 1 (fingerprint fit):** the fit runs at as_of_round = R-1 and NO round ≥ R row enters. `fit_cells_as_of` derives the cutoff INTERNALLY (a caller cannot pass a leaking one) — confirm that, run the guard test, AND reason about the SQL (`round_idx <= as_of_round` INCLUSIVE ⇒ R-1 excludes R). Confirm the test is DISCRIMINATING (a leaking cutoff would fail it — the implementer claims a counterfactual proof; verify it).
- **LEAKAGE GUARD 2 (golf-null pool):** the field pool SQL is `round_idx < R` (excludes R). Run that guard test; confirm discriminating.
- **COMPOSITION = FIELD ROW (Admiral D1c):** the composition read targets `reference_id="__field__"` (field-median across constructors), NEVER a driver's own row; shared identically across all 3 arms. Verify the structural assert + test (v).
- **T7-1 baseline identity:** join under uniform composition == unweighted resolved-cell mean (the documented baseline). Verify the test.
- **Student-t σ preserved on ALL arms** (PredictiveT/predictive_t; no normal approximation). No new model — composes landed pieces only; join.py/fit.py/store.py/frozen sets UNTOUCHED (confirm zero diff on those).
- **The σ-artifact finding is REAL, not masking a bug (SCRUTINIZE):** the implementer reports log-score is non-equal-footing because arms 1/2 carry the landed #666 fit's predictive σ folding in the grip term `g_sigma_onesided` (~1e9, vs time_deficit ~0.1s), inflating intervals to vacuously wide (coverage 1.0) and tanking log-score — so the report LEADS with the σ-robust point metric |resid|. Independently confirm: (i) the g_sigma_onesided magnitude claim is true (spot-check the slice); (ii) leading with |resid| over the handoff-mandated log-score is an HONEST response to a real artifact, NOT a metric-shopping workaround to hide a bad result; (iii) the report presents BOTH metrics honestly with the artifact caveat.
- **Conclusions correctly + honestly stated (no-frame-kill):** composition-weighting HELPS (arm1 |resid| < arm2); the whole driver term is THIN/near-null vs the golf null on the 2023 slice — reported as a COMPLETE result routing to structural work (multi-season, σ calibration), NOT as failure. Early rounds (3-5) thin/unresolved reported honestly.
- Tests real; re-run: `-m pytest tests/unit/physics/fingerprint/test_heldout_diagnostic.py -q` and `-m pytest tests/unit/physics/fingerprint -q`.
- OFFLINE; read-only slice; pinned 3.14 interpreter; pyright-0.

## Allowed Scope
NEW `scripts/run_heldout_diagnostic_670.py`, `tests/unit/physics/fingerprint/test_heldout_diagnostic.py`. (Imports from fingerprint/utilization/pilot modules are sanctioned reuse.)

## Specific Exclusions (flag if touched)
No edit to join.py/fit.py/store.py/frozen sets; no new model; no round≥R data in any driver input; no docs/architecture/* edit; no FastF1/online.

## Constraints
Zero leakage (both guards); Student-t preserved; one documented baseline; OFFLINE; pinned 3.14 interpreter.

## Map Anchors (inbound)
- **Structural:** `run_heldout_diagnostic_670.py::{fit_cells_as_of (as_of=R-1 internal), golf_null_field_pool (round_idx<R), _field_composition (__field__ row)}`; imported join_weekend_prior/fit_driver_fingerprints/predictive_t.
- **Decision anchors:** decision:diagnostic-baseline — join T7-1 uniform-composition. `@grade: guess · settle: report justification per #667 TC-1.` · decision:composition-source — field-reference shared track-geometry. `@grade: settled/human (Admiral D1).`
- **Evidence expectations:** both leakage guards discriminating; composition=field row; T7-1 identity; Student-t; σ-artifact real.
- **Map confidence flags:** subtle-and-silent leakage — this is the OPUS-tier gate; scrutinize the guards hardest.

## Evidence Produced
5/5 diagnostic tests; 108 passed/13 skipped fingerprint suite; pyright-0; real-run per-arm scores above. Re-run to confirm. Target integrate postcondition: `g4-integrate.c1`.

## Suggested Model Tier
`stronger` — reason: this is the leakage-critical gate; the σ-artifact adjudication (real artifact vs metric-shopping) is a judgment call.

## Stop Conditions
BLOCK if: EITHER leakage guard is non-discriminating or a driver input can include round≥R data; composition is a driver row not the field row; Student-t is dropped for a normal approximation; join/fit/frozen sets were edited; OR the σ-artifact framing is masking a genuine defect rather than surfacing a real landed-fit property. If a leakage hole exists, BLOCK — do not soften it.

## Return Format
Write REVIEW_RESULT to `.agent-work/670-season-run/crew-results/g4-reviewer-result.md` (verdict APPROVE or BLOCK, the leakage-guard adjudication for BOTH guards, the σ-artifact adjudication, per-check findings, blockers, workflow feedback). Then SendMessage cmdr-670 a thin pointer (verdict + leakage verdict + path) before ending your turn.
