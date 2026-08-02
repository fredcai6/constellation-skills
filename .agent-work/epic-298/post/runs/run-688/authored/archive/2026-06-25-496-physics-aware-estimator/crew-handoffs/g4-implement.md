# Implementer Handoff — G4 Verdict + Done-Done + Remainder

## Gate
g4-implement (work-id 496-physics-aware-estimator, branch feat/physics-aware-estimator-496, MAIN checkout)

## Task
Close the #509 done-done bar for the #496/#507 physics-aware filter rebuild by writing the
GO/CONTEXTUAL/NO-GO **VERDICT** and confirming the bar is honestly met. This is an assembly + judgment
gate over the already-landed G1–G3 work — NOT new estimator code.

## Inputs (read these)
- `.agent-work/496-physics-aware-estimator/crew-handoffs/g3-implement-result.md` (the synthesis result
  + scoreboard table + retire-assessment + decision candidates).
- `.agent-work/496-physics-aware-estimator/crew-handoffs/g3-review-result.md` (Opus APPROVE; PE-invariance
  verified numerically).
- `.agent-work/496-physics-aware-estimator/SPIKE_COMPARISON.md` (the G2 portfolio finding).
- `.agent-work/496-physics-aware-estimator/PROBLEM_STATEMENT.md` (the run's goal + #507 acceptance).
- Landed code: `src/physics/layer2/decoupled_longitudinal.py`, `scripts/prove_synthesis_496.py`,
  `reports/physics/synthesis_proof_2023Q.{json,png}`.

## Close Criteria (each proven)
1. **Full focused suite green:** `py -m pytest tests/unit/physics tests/unit/preprocessing -q` (confirm;
   it passed at g3-integrate — re-confirm and capture the count).
2. **Single canonical path confirmed:** one decoupled-longitudinal estimator in `[E_total, F_vehicle]`
   coordinates; no `[v,a]` shim; the 2D `StintSmoother` + `clean_longitudinal_from_raw` untouched
   (MEASURED-not-wired). State this plainly with the grep/inspection you did.
3. **Traceable dashboard:** confirm `reports/physics/synthesis_proof_2023Q.png` regenerates from the
   committed code via `py scripts/prove_synthesis_496.py` (data→plot traceable). Re-run it; confirm exit 0
   and the 3-circuit table reproduces.
4. **Write `.agent-work/496-physics-aware-estimator/VERDICT.md`** — the GO/CONTEXTUAL/NO-GO verdict keyed
   to the **#507 acceptance**: "knee tracks the raw sensor on BOTH a hard-braking (Bahrain) AND a
   short-straight (Monaco) circuit; Monaco non-throttle ringing under the raw ceiling." Include:
   - the verdict + a one-paragraph justification grounded in the scoreboard numbers;
   - the 3-circuit acceptance table (Bahrain gap +1.15 / Monaco ring_ok / Belgium no-regress);
   - the honest scope of the claim: single driver (VER), 3 circuits, 2023 Q, default HPs
     (NOT per-session-calibrated), MEASURED-not-wired;
   - what the run did NOT do (production wiring, multi-session calibration, the retire, the
     gravity-corrected F_vehicle frontier metric) and WHERE it is tracked (#518 + follow-ons);
   - the `clean_longitudinal_from_raw` retire-assessment conclusion (do NOT retire here; #518
     side-by-side — carry the deciding numbers from the g3 result);
   - the two durable decision candidates (decoupled-1D-longitudinal; total-energy/force frame) for the
     Cartographer/user to ratify.
   The verdict must be HONEST: GO is justified IF you judge the #507 acceptance met on the tested scope;
   if you judge the single-driver/default-HP scope makes it CONTEXTUAL, say so and justify — do not
   inflate. (Recommended read: GO on the #507 acceptance for the tested scope, with production-readiness
   explicitly deferred to #518. But form your own judgment from the evidence.)
5. **Enumerate the set-aside remainder** as a clear list in VERDICT.md (it routes to Triage next):
   #518 C1 re-eval + wiring + retire side-by-side + multi-session HP calibration + the F_vehicle frontier
   metric + terrain-on-the-scoreboard-seam; plus the pre-existing validate_refine_505 cleanup (#504
   territory) and the M8≥10Hz revival. (Several are already engine triage candidates tc1–tc5 — list them
   so nothing is silent.)

## Allowed Scope
- NEW `.agent-work/496-physics-aware-estimator/VERDICT.md`.
- Re-run the proof + the suite to confirm (no code changes).
- Do NOT modify `src/` or wire anything. Do NOT retire `clean_longitudinal_from_raw`.

## Constraints
`py` launcher; honest verdict (NO-GO/CONTEXTUAL acceptable); dashboard traceable; single canonical path.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (the estimator); `struct:physics.utilization` (the #518 consumer).
- **Decision:** `decision:ideal_lap_sim_two_sided_evaluator` (the under-call signal the verdict reads);
  the two new decision candidates above.
- **Evidence:** the 3-circuit scoreboard + the suite + the dashboard.

## Required Evidence
- `py -m pytest tests/unit/physics tests/unit/preprocessing -q` (count).
- `py scripts/prove_synthesis_496.py` (exit 0 + table).
- The written VERDICT.md.

## Verification Commands
```bash
py -m pytest tests/unit/physics tests/unit/preprocessing -q
py scripts/prove_synthesis_496.py
```

## Suggested Model Tier
simple-bounded (Sonnet) — assembly + verdict over already-reviewed evidence; the judgment is bounded by
the scoreboard numbers.

## Authority
The verdict criteria (#507 acceptance) and the MEASURED-not-wired scope are decided. You judge GO vs
CONTEXTUAL from the evidence and justify it. You may NOT: wire into production, retire
`clean_longitudinal_from_raw`, or claim production-readiness beyond the tested scope.

## Stop Conditions
Stop and return if: the suite or proof does NOT reproduce green, or the evidence does not support any
honest verdict (escalate).

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/496-physics-aware-estimator/crew-handoffs/g4-implement-result.md`:
the verdict + justification, the confirmed done-done checklist (suite/single-path/dashboard), the
remainder list, assumptions, stop conditions, out-of-scope, and Workflow Feedback. Reference VERDICT.md.
