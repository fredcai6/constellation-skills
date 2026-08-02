# Reviewer Handoff — G4 Verdict + Done-Done + Remainder

## Gate
g4-review (work-id 496-physics-aware-estimator, MAIN checkout, branch feat/physics-aware-estimator-496)

## What Was Implemented
The G4 verdict gate: `.agent-work/496-physics-aware-estimator/VERDICT.md` (GO on the #507 acceptance for
the tested scope; production-readiness deferred to #518) + the done-done confirmation. No `src/` change
— this is an assembly + judgment gate over the already-reviewed G1–G3 work.
Full result: `.agent-work/496-physics-aware-estimator/crew-handoffs/g4-implement-result.md`.

## Task Statement
Close the #509 done-done bar with an honest GO/CONTEXTUAL/NO-GO verdict keyed to the #507 acceptance
(knee tracks raw on a hard-braking AND a short-straight circuit; Monaco ringing under ceiling),
confirm the bar (suite green / single path / traceable dashboard), and enumerate the set-aside remainder.

## How to Inspect
```bash
cat .agent-work/496-physics-aware-estimator/VERDICT.md
cat .agent-work/496-physics-aware-estimator/crew-handoffs/g4-implement-result.md
git status --short      # only .agent-work/ untracked; no src/ change
```

## Close Criteria (each a review check)
- **Verdict is honest, not inflated.** The #507 acceptance is a binary "knee tracks raw on BOTH circuit
  types + Monaco ring under ceiling" bar. Confirm the scoreboard meets it literally (Bahrain gap +1.15,
  Monaco ring_ok roc −0.09, Belgium no-regress) → GO is justified. Confirm the verdict KEEPS
  "acceptance met" separate from "production-ready" and defers the latter to #518 (single driver / 3
  circuits / default HPs / measured-not-wired). It must NOT over-claim production-readiness.
- **Done-done bar real (spot-check, don't trust):** the suite (`py -m pytest tests/unit/physics
  tests/unit/preprocessing -q`) was reported 627 passed / 6 skipped — you need not re-run the full 13-min
  suite, but confirm the proof reproduces: `py scripts/prove_synthesis_496.py` → exit 0 + the 3-circuit
  table. Confirm single canonical path (grep: no `[v,a]` shim; 0 `src/` importers of the estimator;
  `StintSmoother` + `clean_longitudinal_from_raw` untouched). Confirm the dashboard
  `reports/physics/synthesis_proof_2023Q.png` exists and regenerates.
- **Remainder is complete + correctly routed:** #518 owns C1 re-eval + wiring + retire side-by-side +
  multi-session calibration + the F_vehicle frontier metric + the terrain scoreboard-seam; plus the
  pre-existing validate_refine_505 cleanup (#504) and the M8 ≥10 Hz revival. Nothing silently dropped.
- **clean_longitudinal_from_raw NOT retired here** (correctly deferred to #518 side-by-side) — confirm.
- **The two decision candidates** (decoupled-1D-longitudinal; total-energy/force frame) are surfaced for
  ratification, not self-authorized.

## Allowed Scope / Exclusions
Read VERDICT.md + the result; re-run the proof (not the full suite). Do NOT modify src/ or land anything.

## Constraints
`py` launcher; honest verdict; cache `C:/Programs/f1Brainz/data/telemetry`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (estimator); `struct:physics.utilization` (#518 consumer).
- **Decision:** `decision:ideal_lap_sim_two_sided_evaluator`; the two new candidates.
- **Evidence:** the 3-circuit proof + the done-done bar.

## Evidence Produced (re-verify the proof)
627 passed/6 skipped (reported); `prove_synthesis_496.py` exit 0; VERDICT.md. Re-run the proof; spot-check
the verdict's numbers against the proof JSON.

## Suggested Model Tier
simple-bounded (Sonnet) — verification of a verdict doc against already-reviewed evidence + a proof re-run.

## Stop Conditions
BLOCK if: the verdict inflates the claim (claims production-readiness, or GO beyond the tested scope
without deferral); the proof does NOT reproduce; the single-path / measured-not-wired claims are false; a
remainder item is silently dropped; or `clean_longitudinal_from_raw` was actually retired. Otherwise APPROVE.

## Return Format
Return REVIEW_RESULT to `.agent-work/496-physics-aware-estimator/crew-handoffs/g4-review-result.md` with
`verdict: APPROVE` or `verdict: BLOCK`, per-check findings (incl. your proof re-run), blockers,
out-of-scope observations, and Workflow Feedback.
