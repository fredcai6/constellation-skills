# Reviewer Handoff — #525 G1 audit (evidence-only)

## Gate
g1-review (audit verification) — issue #525, branch `feat/physics-units-audit-525`

## What Was Implemented
NO code. An evidence-only units-convention audit producing two artifacts:
- `.agent-work/525/AUDIT_MAP.md` — producer→consumer unit-convention map, 6 channels +
  shared constants + a one-line producer/consumer matrix.
- `.agent-work/525/AUDIT_DISPOSITIONS.md` — 7 overloaded-term inventory + A-vs-B canonical
  lateral recommendation (recommends **B**, m/s² at consumer) + ρ-in-aero disposition
  (recommends **pure representation, no refit**).
- Result: `.agent-work/525/crew-handoffs/g1-implement-result.md`.

## How to Inspect (no diff — this is an audit verification)
Read the two audit artifacts, then **independently verify their claims against source**.
Confirm no code changed: `git status --porcelain src/ tests/` must be empty.

## Task Statement
Audit every physics model parameter's unit convention producer→consumer across all channels,
treating the architecture packet as an index not ground truth, and recommend (not decide) the
canonical lateral convention with an honest blast-radius + the ρ refit-vs-representation call.
The audit feeds a human decide-fix checkpoint that rules on scope.

## Close Criteria (each a review check — verify against source)
1. **Map completeness:** every channel (lateral, longitudinal/power, braking, traction,
   coast, terrain) covers each producer and each consumer with `file:symbol` + unit. No
   force channel missing.
2. **Map accuracy — spot-check by reading the cited code (at minimum):**
   - the **lateral two-producer seam**: `lateral_view.py` (g-units, `μ=A0+A2·v²`, no ρ) vs
     `lateral_envelope.py` / `physics_data_models.py:lateral_capability` (m/s², `A2·ρ·v²`);
     and `car_prior._assemble_lateral` (the B→A `A0·G`, `A2·G/ρ`, Jacobian conversion).
   - the **longitudinal `p_max`/`theta_P` seam**: store `p_max` in **watts** vs consumer
     W/kg; `car_prior._build_longitudinal` `p_max/MASS_KG` (#518).
   - the **`G_MS2` claim**: confirm the audit's *correction* — `G_MS2` is defined ONCE
     (`braking_fit.py`) but mis-homed/unused-locally, and the real duplication is scattered
     `9.81`/`_G` literals (the issue's "duplicated G_MS2" framing was slightly off).
3. **Blast-radius honesty (LOAD-BEARING):** independently confirm from source whether the
   live `sim_evaluator` / `fit_batch` path consumes the shared `LateralParameters` consumer
   and whether it routes through `car_prior` / the g-unit EstimateStore. The audit claims it
   does NOT (flows `fit_batch → fit_driver → session_fit.fit_session_full → LateralEnvelopeFit`,
   m/s², never car_prior). **Verify this — it is the fact that determines A-vs-B blast radius
   and that got #522's from-memory fix blocked.**
4. **ρ call soundness:** confirm ρ is absent from the lateral fit (so removing/adding it is a
   symbolic identity, not a refit) — i.e. the "pure representation, no refit" verdict holds.
5. **Recommend-not-decide respected:** the artifacts recommend; they do not pick the
   convention or declare scope.

## Allowed Scope
Read-only verification across `src/physics/**` and the two audit artifacts. Write only your
REVIEW_RESULT.

## Specific Exclusions
Do not propose or make code changes; do not pick the convention. This is verification of the
audit's accuracy + honesty, not the fix.

## Constraints the Audit Must Respect
- Evidence-only: no src/tests changes (verify clean).
- Every convention claim cites source.
- Physics-region only.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (physics_data_models, physics_simulator, sim_evaluator,
  lateral_envelope, longitudinal_fit, braking_fit, capability_envelope), `struct:physics.layer2`
  (lateral_view, estimate_store, the views), `struct:physics.utilization` (car_prior).
- **Constraints:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator`,
  `claim:lateral_car_prior_boundary_conversion` (the surface G2 may retire/generalize).
- **Map confidence flags:** packet reconciled #522 (high) but verify against source.

## Evidence Produced
The two artifacts + result file; `git status --porcelain src/ tests/` reported empty by the
implementer (re-verify).

## Suggested Model Tier
stronger (Opus) — verifying audit accuracy against source + independently re-confirming the
blast-radius fact is judgment-heavy and load-bearing for the human's checkpoint.

## Stop Conditions
BLOCK if: the map is materially incomplete/inaccurate against source, the blast-radius claim
is wrong (the live sim path DOES route through car_prior), the ρ call is unsound, or any
src/tests file was changed.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (1–5 above, each with
the source you verified), blockers, out-of-scope observations, and Workflow Feedback (`none`
needs a run-specific reason).
