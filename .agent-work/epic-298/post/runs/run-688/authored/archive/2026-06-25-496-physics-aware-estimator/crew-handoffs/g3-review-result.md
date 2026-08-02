# Review Result — G3 Synthesis (M7+M3, total-energy reframe)

verdict: APPROVE

## Assigned Gate
`g3-review` — 496-physics-aware-estimator, branch `feat/physics-aware-estimator-496`, MAIN checkout.
Target: `src/physics/layer2/decoupled_longitudinal.py` (+ 26-test file + `scripts/prove_synthesis_496.py`).

## Result
`APPROVE`

All 14 survey checks pass; consolidated through the engine (`verdict=APPROVE findings=0`). Every
critical claim was re-run/re-derived independently — not trusted from the pasted result.

## Handoff compliance
Productionized the M7+M3 synthesis into one canonical, covariance-bearing longitudinal estimator in
total-energy/force coordinates, passing all three acceptance circuits at once, MEASURED-not-wired.
Matches the handoff task. The two mid-build coordinator reframes (KE/force → total-energy/PE) fall
inside the implementer's documented "module internals / composition" authority and were surfaced as
G4 decision candidates, not treated as user approval — correct handling.

## Scope drift
Clean. `git diff --stat` is EMPTY — zero tracked files modified. Only three new untracked files
(module, test, proof) plus `.agent-work/`. No `src/` retire; `clean_longitudinal_from_raw` is only
READ by the proof as the raw reference, never modified or retired (correctly deferred to #518); the 2D
`StintSmoother` is untouched.

## Evidence verdict — re-run numbers
**Proof (`py scripts/prove_synthesis_496.py`, exit 0), reproduced EXACTLY:**

| Circuit | synthesis knee | gap_vs_raw | ring_ok (roc) | baselines | verdict |
|---|---|---|---|---|---|
| Bahrain | **−50.98** | **+1.15** ≤ 3.0 | OK (−0.13) | gaussian/kind3 gap +12.6/+12.7, RING | PASS |
| Monaco | −36.88 | +0.63 | **OK (roc −0.09 ≤ 0)** | baselines RING roc +7.50/+7.73 | PASS |
| Belgium | **−38.49** | +0.35 | OK (−0.05) | kind3 −37.41 → regress −1.08 ≤ 0.5 (deeper) | PASS |

All three PASS simultaneously, matching the handoff targets (Bahrain ≈ −51 gap ≤ ~1.2; Monaco
ring_ok True; Belgium ≈ −38.5 not worse than kind3 −37.4). Terrain path reproduced: F_veh shift
0.34/0.74/0.70 m/s² on the brake arc (Bahrain/Monaco/Belgium), sigma_a min ~0.09, flat_flag False.

- **26 tests** (`test_decoupled_longitudinal.py`): 26 passed in 0.22s.
- **152 layer2** (`tests/unit/physics/layer2`): 152 passed in 85.92s — no regressions.
- **simplification_limits** (3 touched files): PASS.

L1 (synthetic step recovery, err −1.93 |err|<5), L2 (σ_a>0 + TV edge-preservation), L3 (limit, see
below), L4 (3-circuit scoreboard) — all present and demonstrate the behavior.

## PE-invariance claim — VERDICT: CORRECT and consistently round-tripped
The load-bearing honesty point. Verified in code AND independently re-derived:
- Code: `e_obs = ½ m v² + m g z` (L405); `f_soft = m(a_tv + g·sinθ)` (L406); output
  `a_long = f_vehicle/m − g·sinθ` (L423).
- Math: `dE_total/ds = m·v·(dv/ds) + m·g·(dz/ds) = m·a + m·g·sinθ = F_vehicle`, since `v·dv/ds = a`
  (chain rule, ds/dt = v) and `dz/ds = sinθ`. So `a_long = F/m − g·sinθ = a` — the actual on-track
  accel, independent of the PE term.
- **Independent round-trip** (synthetic hill, grades 0/+4/+8/−6°): output identity residual
  `a_long − (F/m − g·sinθ) = 0.0e+00` EXACTLY at every grade (gravity added into force, removed on
  output, bit-exact); `max|a_flat − a_terr| ≤ 0.08` (a tiny second-order coupling through the median
  `v_rep` energy-obs std, not the PE term — the a_long scoreboard is genuinely blind to terrain);
  `F_shift/m` grows as `g·sinθ` (0.71@4°, 1.41@8°, 1.06@−6°). The terrain payoff legitimately lives in
  the `F_vehicle` channel (for #518), NOT the a_long acceptance metric. Consistent across all grades —
  not a one-circuit coincidence.

## Honest covariance
`sigma_a = √(max(P_s[1,1], 0))/m` from the SAME RTS posterior (L424/L287); the frozen result
dataclass exposes `a_long` and `sigma_a` together (same shape) and never `a_long` alone; independent
check shows finite, >0 everywhere (min 0.044 synthetic, ~0.09 real), shape-matched. Honest, not
bolted-on.

## L3 reframe — HONEST physics correction, not a fudge
Independently reproduced the premise: at the 40 Hz synthetic rate the no-anchor/energy-only limit
gives knee **−54.37**, which OVER-shoots the true −45 step (RTS ringing on the kink); tight coupling
gives −46.93, tracking the raw. The original test asserted the energy-only limit would be *shallower*
(physically wrong at this bandwidth) → it failed → reframed to "tight tracks raw; removing the anchor
changes the knee materially (|Δ|=7.4 > 2)", the correct limit, with a documented note that the
real-session shallowness is the ~4 Hz bandwidth effect proven on the scoreboard. The test now asserts
a real invariant (anchor controls the result); it was corrected, not bent to pass.

## Single canonical path
Only the `[E_total, F_vehicle]` state exists. No `[v,a]` shim, no `StintSmoother`, no `kind3`/
`gaussian` inside the module. One formulation.

## Map impact verdict
- **Evidence supports claimed change:** yes — scoreboard passes all three together (re-run); honest
  σ_a; L1–L4 all present and reproduced.
- **Constraints not violated:** `decision:two_cycle_external_anchor_design` honored (anchor =
  TV-denoised RAW a_long + external #497 z-map gravity term, never re-read from a smoothed trajectory)
  and reasonably extended to the 1D-filter context (the onset sample is the capability sample, TV
  preserves it). `constraint:physics_region_no_evo_import` honored (imports: numpy, dataclasses,
  typing, `src.physics.longitudinal_fit`).
- **Notes match the diff:** yes — `struct:physics.layer2` new module; reads scoreboard seam + terrain
  + MASS_KG only; no overstated/missing structural impact.
- **Decision candidates surfaced:** yes — decoupled-1D-longitudinal and the total-energy reframe routed
  to G4 for authority (the implementer correctly did not self-authorize them as durable).
- **Durable context routed:** yes — two triage candidates flagged through the engine (below).

## Reconciliation check
No divergence requiring reconciliation beyond the two surfaced G4 decision candidates and the two
triage candidates. No docs/contract changes (MEASURED-not-wired; module docstring is the interim
contract; #518 wiring will update `docs/architecture` + report schemas). No structural baseline
concern.

## Blockers
- none

## Out-of-scope observations (triage candidates — flagged through engine)
- **tc1:** Terrain pool absent from the `CaseInputs` scoreboard seam — `variant_synthesis` runs FLAT on
  the scoreboard (CaseInputs carries one fastest lap, no z-map). #518 wiring needs a terrain handle on
  the seam if the scoreboard is to grade `F_vehicle`.
- **tc2:** The a_long scoreboard is structurally blind to the PE term (round-trip invariance by
  construction). #518 needs a gravity-corrected braking-frontier metric on `F_vehicle` to reward the
  terrain work; the a_long acceptance metric alone never will.

Both are #518 (the C1 ceiling re-eval / consumer) concerns, not this gate. The `clean_longitudinal_from_raw`
retire decision also correctly belongs to #518 with the side-by-side BrakingView comparison the
implementer scoped.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff framed the close criteria precisely (the exact 3-circuit
  table targets, the PE-invariance round-trip as the load-bearing check, the L3-reframe honesty
  question). One minor note: the handoff says σ_a min ≈ 0.09 (Evidence Produced) — that is the
  real-session value; the synthetic unit-test value is ~0.04, which momentarily looked like a
  mismatch until I confirmed both are positive and from the same posterior. Not blocking; a one-word
  "(real-session)" qualifier would remove the ambiguity.
- **Context rediscovered:** the engine script is NOT vendored in this repo's `scripts/` (the reference
  says it "lives at scripts/checklist_engine.py" in the source repo) — `py scripts/checklist_engine.py`
  failed; I had to fall back to the installed skill's absolute path. Worth a one-line note in the
  handoff for the next reviewer, or vendoring the engine.
- **Instructions improvised around:** none — the survey template + engine verb loop covered the gate
  cleanly. I appended seven handoff-specific checks (r6–r12) to the 7-item base template, which the
  skill explicitly invites ("append checks the context warrants").
- **What would have made this easier:** nothing beyond the two notes above. The IMPLEMENTER_RESULT was
  unusually complete (decision candidates, triage candidates, the retire-assessment, and honest
  caveats all pre-stated), which made independent verification fast.

## Return status
`complete`
