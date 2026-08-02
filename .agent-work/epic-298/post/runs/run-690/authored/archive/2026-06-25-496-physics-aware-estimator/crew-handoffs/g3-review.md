# Reviewer Handoff — G3 Synthesis + Land (M7 + M3, total-energy reframe)

## Gate
g3-review (work-id 496-physics-aware-estimator, MAIN checkout, branch feat/physics-aware-estimator-496)

## What Was Implemented
A new decoupled longitudinal estimator `src/physics/layer2/decoupled_longitudinal.py` composing the
two G2 winners, reframed (per user direction relayed mid-build) into **total mechanical energy /
vehicle-force coordinates**: state `[E_total, F_vehicle]` over distance `s`, `E_total = ½mv² + mgz(s)`,
identity `dE_total/ds = F_vehicle` (gravity-free vehicle force). M3 = 1-D decoupled filter (no 2D
ringing); M7 = TV/IRLS edge-preserving denoise of raw `a_long`, gravity-corrected to a tight soft
FORCE obs on the braking arc. Reports `a_long = F_vehicle/m − g·sinθ` (+ per-sample `sigma_a`) so the
G1 scoreboard grades it. Terrain `z`/`θ` from the #497 z-map with a loud flat-fallback.
Full result: `.agent-work/496-physics-aware-estimator/crew-handoffs/g3-implement-result.md`.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz
git status --short                 # new (untracked): the module, its test, the proof script
cat src/physics/layer2/decoupled_longitudinal.py
cat tests/unit/physics/layer2/test_decoupled_longitudinal.py
cat scripts/prove_synthesis_496.py
cat reports/physics/synthesis_proof_2023Q.json
```

## Task Statement
Productionize the M7+M3 synthesis into one canonical, covariance-bearing longitudinal estimator that
PASSES BOTH acceptance circuits at once (deep Bahrain knee AND Monaco ring_ok) without regressing
Belgium, with L1–L4 evidence — MEASURED-not-wired. (Full handoff: `crew-handoffs/g3-implement.md`.)

## Close Criteria (each a review check — VERIFY, don't trust)
- **Re-run the proof yourself:** `py scripts/prove_synthesis_496.py` → confirm the 3-circuit table:
  Bahrain synthesis knee ≈ −51 (gap ≤ ~1.2, baseline +12.7), Monaco `ring_ok == True` (roc ≤ 0,
  baselines RING +7.5), Belgium knee ≈ −38.5 not worse than kind3 (−37.4). All three PASS together.
- **Physics correctness of the reframe.** Confirm in code:
  - `E_total = ½ m v² + m g z`; the process identity `dE_total/ds = F_vehicle`; output
    `a_long = F_vehicle/m − g·sinθ`.
  - The **PE-invariance claim** (the load-bearing honesty point): because `F_vehicle = m·a + m·g·sinθ`,
    the reported `a_long = F_vehicle/m − g·sinθ = a` — i.e. the a_long the scoreboard sees is the
    actual on-track acceleration, INDEPENDENT of the PE term. Confirm the implementation actually
    round-trips this consistently (the gravity correction added into the force is removed on output),
    so the result the claim rests on is real, not a coincidence of one circuit. The terrain payoff
    legitimately lives in the `F_vehicle` channel (for #518), not the a_long acceptance metric.
- **Honest covariance first-class:** `sigma_a = √(P_s[1,1])/m` from the SAME smoothed posterior;
  finite > 0 at every sample; `a_long` never exposed without `sigma_a`.
- **Single canonical path:** ONLY the total-energy `[E_total, F_vehicle]` formulation exists — no
  leftover `[v,a]` shim / dual estimator.
- **L1–L4 sound and HONEST:** L1 synthetic step recovery within tol; L2 σ positivity + TV
  edge-preservation; L3 limits; L4 the scoreboard. Specifically confirm the **L3 test reframe** was an
  honest physics correction (the energy-only limit over-shoots at the 40 Hz synthetic rate; the
  real-session shallowness is the ~4 Hz bandwidth effect) and NOT a test bent to pass.
- **Two-cycle invariant extension** (`decision:two_cycle_external_anchor_design`): anchor magnitude is
  the TV-denoised RAW `a_long` (+ external z-map gravity term), never re-read from a smoothed
  trajectory; onset-arc placement extension is justified. Confirm it stays external & un-biased.
- **MEASURED-not-wired:** nothing imports the estimator into production `braking_view`/ceiling/evo;
  the 2D `StintSmoother` and `clean_longitudinal_from_raw` are untouched.
- `py -m pytest tests/unit/physics/layer2 -q` green (no regressions; ~152 tests); test file green (26);
  `py -m src.utils.simplification_limits --paths src/physics/layer2/decoupled_longitudinal.py tests/unit/physics/layer2/test_decoupled_longitudinal.py scripts/prove_synthesis_496.py` PASS;
  `constraint:physics_region_no_evo_import` honored.

## Allowed Scope / Exclusions
Review the new module + test + proof script; re-run the proof + the tests. Do NOT modify src/ or land
anything. The retire of `clean_longitudinal_from_raw` is correctly DEFERRED to #518 (not this gate) —
confirm the estimator did not silently retire/replace it.

## Constraints
`py` launcher; cache `C:/Programs/f1Brainz/data/telemetry`; honest covariance; physics L1–L4 with
units/bounds; single canonical path; no evo import.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (new module); reads `struct:preprocessing.trajectory`
  (scoreboard seam only), `src.physics.terrain` (#497), `src.physics.longitudinal_fit.MASS_KG`.
- **Decisions:** `decision:two_cycle_external_anchor_design` (verify extension stays raw/un-biased);
  `decision:smoother_rounds_braking_knee` (the root cause; the decoupled-1D candidate aligns with it).
- **Evidence:** scoreboard passes all 3 together; honest σ_a; L1–L4.
- **Confidence flag:** physics packet Open Question (loaders/artifact boundary) — confirm the estimator
  did not silently re-plumb loaders.

## Evidence Produced (re-verify)
26-test green; 152 layer2 green; simplification PASS; proof PASS (exit 0); the 3-circuit table; L1
synthetic err −1.93; σ_a min ≈ 0.09. Re-run the proof + tests; spot-check the a_long round-trip math.

## Suggested Model Tier
stronger (Opus) — pivotal correctness gate; verify the total-energy physics + the PE-invariance claim,
honest covariance, and that the L3 reframe was a correction not a fudge.

## Stop Conditions
BLOCK if: the proof does NOT pass all three circuits on your re-run; the PE-invariance claim is wrong
or the round-trip is inconsistent (a_long contaminated by the PE term); σ_a is absent/non-positive or
bolted-on; a `[v,a]` shim remains (dual path); an L-level test was bent to pass rather than corrected;
the estimator silently wired into production or retired `clean_longitudinal_from_raw`; tests/
simplification fail; or an evo import exists. Otherwise APPROVE.

## Return Format
Return REVIEW_RESULT to `.agent-work/496-physics-aware-estimator/crew-handoffs/g3-review-result.md`
with `verdict: APPROVE` or `verdict: BLOCK`, per-check findings (incl. your re-run proof numbers and
your verdict on the PE-invariance claim), blockers, out-of-scope observations, and Workflow Feedback.
