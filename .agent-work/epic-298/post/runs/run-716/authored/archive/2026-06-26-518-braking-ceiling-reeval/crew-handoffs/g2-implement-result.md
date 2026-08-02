# Implementation Result — G2 side-by-side braking adapter (#518)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2 — Side-by-side braking frontier (synthesis F_vehicle vs incumbent raw-speed) + the
decoupled-estimator adapter. MEASUREMENT ONLY — no production wiring.`

## Completed slice
Built the reusable decoupled-estimator braking-frontier adapter and ran the full
6-circuit × VER+PER side-by-side comparison, producing the deciding (a_b, b_b)+cov+ceiling
numbers and a retire/keep recommendation. Both deliverables done; engine plan driven to DONE
(6/6 items complete).

1. **Adapter** `src/physics/layer2/decoupled_braking_input.py` — per-lap `estimate_longitudinal`
   over contiguous classified `KinematicSamples`, terrain θ/z from the #497 z-map, emitting
   per-sample `a_long` / `f_vehicle` / `sigma_a` aligned 1:1 to the classified samples.
2. **`altitude_at_positions`** helper added to `terrain.py` (mirrors `gradient_at_positions`).
3. **Side-by-side** `scripts/braking_sidebyside_518.py` → `reports/physics/braking_sidebyside_2023Q.{json,md}`.

## Scope
**Files changed:**
- `src/physics/layer2/decoupled_braking_input.py` (NEW — adapter)
- `src/physics/terrain.py` (added `altitude_at_positions`; nothing else touched)
- `tests/unit/physics/layer2/test_decoupled_braking_input.py` (NEW — 10 synthetic tests)
- `tests/unit/physics/layer2/test_terrain_altitude.py` (NEW — 3 synthetic tests)
- `scripts/braking_sidebyside_518.py` (NEW — comparison script)
- `reports/physics/braking_sidebyside_2023Q.{json,md}` (NEW — gitignored report)
- `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g2-implement-plan.json` (engine plan)

**Specific exclusions touched:** **no.** `prepare_braking_frontier`, `session_braking`/`session_traction`/
`session_coast`, `BrakingView.fit`, `clean_longitudinal_from_raw`, `EstimateStore`, `car_prior`
are all UNMODIFIED. The adapter is purely additive; it *calls* `clean_longitudinal_from_raw`,
`_driver_samples`, `_to_kinematic_samples` and `estimate_longitudinal` but changes none of them.

## Behavior changed
**No production behavior changed.** Additive measurement seam only. The adapter introduces a new
import path (a per-lap, terrain-aware decoupled estimate of the braking frontier input) that G3 can
later productionize; nothing in the production pipeline calls it yet.

## Gravity counted ONCE — confirmation (the crux)
- **Variant A (synthesis F_vehicle frontier, the new path):** feed `f_vehicle / mass_kg` (already
  gravity-free, gravity removed *inside* the estimator via the per-sample z-map) into `BrakingView.fit`
  with **`theta = 0`** → BrakingView's `-g·sinθ` term is zero, so `y = -(F_vehicle/m) - drag - θ_R`.
  Gravity counted once (in the estimator). ✓
- **Variant B (incumbent):** feed `a_long` (`= F_vehicle/m - g·sinθ`, what the raw sensor reads) with
  the **real θ** → BrakingView's `-g·sinθ` removes gravity once. ✓
- Never fed `F_vehicle/m` with real θ (double subtract) or `a_long` with θ=0 (never subtract). A unit
  test (`test_double_count_trap_diverges`) actively guards the trap: on a 6° grade, feeding `F/m` with
  real θ shifts `a_b` by >0.5 m/s² vs the correct Variant A — i.e. the silent bug is caught.
- A second unit test (`test_variantA_and_variantB_deconflate_equally`) proves A and B de-conflate to the
  SAME `a_b` within 1.5 m/s² on a synthetic downhill braking lap (both count gravity once).

## Evidence — KEY side-by-side numbers (2023 Q, VER+PER pooled, DEFAULT HPs tv_λ=0.10, σ_a_soft_brake=0.10)
Ceiling = `a_brake(80 m/s)` = `a_b + b_b·80²` (m/s²). "deeper" = larger ceiling@80. n identical A vs B
on every circuit (perfect sample alignment): 170/170, 252/252, 227/227, 261/261, 168/168, 197/196.

| Circuit | flat? | θ_brake(°) | A a_b±σ | A b_b | A ceil@80 | B a_b±σ | B b_b | B ceil@80 | deeper | dCeil(A−B) | raw_p99 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bahrain   | False | [−2.64, 1.11] | 34.43±1.22 | 0.00 | 34.43 | 34.41±1.36 | 0.00 | 34.41 | A | +0.02 | 43.80 |
| Monaco    | False | [−4.61, 2.70] | 26.74±2.67 | 1.46e−3 | 36.06 | 25.87±3.19 | 1.90e−3 | 38.05 | B | −1.99 | 41.75 |
| Belgium   | False | [−4.31, 2.67] | 14.18±4.30 | 3.48e−3 | 36.43 | 11.17±4.82 | 4.26e−3 | 38.43 | B | −2.00 | 38.32 |
| Monza     | False | [−0.84, 0.47] | 37.24±1.58 | 2.06e−4 | 38.56 | 32.73±**6.76** | 1.73e−3 | 43.81 | B | −5.25 | 51.34 |
| Singapore | False | [−0.91, 2.17] | 24.10±7.81 | 3.31e−3 | 45.31 | 34.30±2.35 | 5.99e−4 | 38.14 | A | +7.17 | 45.96 |
| Mexico    | False | [−0.83, 0.72] | 23.62±4.74 | 2.70e−3 | 40.92 | 21.58±2.59 | 3.53e−3 | 44.19 | B | −3.27 | 49.64 |

**Reading the numbers:**
- **a_b (mechanical-grip floor): A ≥ B on 5/6** circuits (all but Singapore). A is +0.02/+0.87/+3.01/+4.52/+2.05
  on Bahrain/Monaco/Belgium/Monza/Mexico. The synthesis recovers a **deeper, more stable floor**.
- **a_b calibration: A tighter than B on 4/6** — most dramatically **Monza (A ±1.58 vs B ±6.76)**, the
  highest-speed-braking circuit, where B's tiny over-fit bandwidth (2.19 vs A's 9.57) destabilises the floor.
- **Ceiling@80: B ≥ A on 4/6** — because B's `b_b` (downforce-added-grip term) is systematically larger.
  The incumbent's local-gradient θ removal pushes more of the high-speed decline into `b_b`, inflating the
  extrapolated 80 m/s ceiling; the synthesis attributes less to downforce (flatter frontier).
- **Terrain effect (all 6 ran z-map active, `altitude_assumed_flat=False`):** the hilly braking circuits
  Belgium (θ_brake to −4.31°) and Monaco (−4.61°) show A's a_b notably above B (Belgium +3.01, Monaco +0.87),
  consistent with the estimator's per-sample z-map handling the downhill braking zones (Eau Rouge, Monaco
  descents) more accurately than B's local θ. Mexico (altitude track, but near-flat brake-zone θ ±0.8°) shows
  A a_b +2.05 — the altitude is in the *density* (already modelled), not the brake-zone gradient.
- **Singapore is the inversion:** A picks a steep b_b (3.31e−3) and a low a_b (24.10±7.81) while B picks a high
  a_b (34.30) and near-zero b_b — an a_b↔b_b trade-off (the cov off-diagonal −1.6e−2 is the largest in the set),
  so the *ceiling* diverges +7.17 toward A while the *floor* goes the other way. Not a clean directional win.

## Retire/keep recommendation
**KEEP `clean_longitudinal_from_raw` / do NOT retire the incumbent path in G3 yet** (recommendation only —
the retire decision is the user's; this report is the input).

Deciding numbers: the handoff's bar for A to be *favoured* is "at least as deep AND better-or-equal
calibrated, with the terrain advantage on hilly circuits." The synthesis clears the **floor + calibration**
half convincingly (a_b deeper on 5/6, tighter σ_a_b on 4/6, large Monza calibration win, terrain-correct on
the hilly circuits), but it does **not** clear the **ceiling** half: ceiling@80 is *lower* on 4/6 (Monaco
−1.99, Belgium −2.00, Monza −5.25, Mexico −3.27) and Singapore shows an a_b↔b_b inversion. The A-vs-B gap is
driven by a real, unresolved modelling divergence in **b_b** (how much high-speed decline is downforce vs
utilisation), not by gravity (gravity is correct/once in both). Retiring B now would trade a better-calibrated
floor for a less-deep high-speed ceiling on most circuits — not a strict improvement.

**Recommended G3 path:** treat A as the floor/calibration upgrade it clearly is, but resolve the b_b/ceiling
divergence first (pin b_b from PowerDrag/cross-session downforce so both variants share the downforce term,
then re-compare ceiling). If, with a pinned b_b, A's ceiling matches or beats B, retire; otherwise keep B for
the ceiling and adopt A's floor. The numbers that would flip the decision: A's ceiling@80 ≥ B's on ≥4/6 once
b_b is pinned.

## Test mode
**Required:** `test-after` (adapter pure-logic unit tests; side-by-side is a script + report).
**Satisfied:** **yes** — 13 new synthetic tests (10 adapter + 3 terrain helper), all pass without the FastF1
cache; full layer2 suite green; report produced from real telemetry.

## Evidence (commands run inline — real output)

```bash
py -m pytest tests/unit/physics/layer2/test_terrain_altitude.py -q        # 3 passed (0.20s)
py -m pytest tests/unit/physics/layer2/test_decoupled_braking_input.py -q  # 10 passed (1.21s)
py -m pytest tests/unit/physics/layer2/ -q                                 # 197 passed (87.89s)
py -m src.utils.simplification_limits --paths <5 touched paths>            # exit 0
py scripts/braking_sidebyside_518.py                                       # exit 0, report written
```

**Result: pass.**
- `tests/unit/physics/layer2/ -q` → **197 passed in 87.89s** (incl. the 10 adapter + 3 terrain tests).
- `simplification_limits` on the 5 touched paths → exit 0; the ONLY flagged item is the **pre-existing**
  `terrain.py build_terrain_profile` (105 lines), which I proved exists on the *unmodified* file (git-stash
  measurement) — NOT introduced by my change. My new `altitude_at_positions` and the entire adapter / both
  test files / the script are clean.
- Side-by-side sweep → exit 0; `reports/physics/braking_sidebyside_2023Q.json` (12 KB) + `.md` (1.1 KB) written.
- Belgium real-telemetry smoke (pre-sweep): A and B both yield n=232 braking samples (perfect alignment),
  `altitude_assumed_flat=False`, A a_long[−44.2, 5.8] vs B[−45.1, 6.1], per-sample σ_a 0.09–0.10.

## TDD evidence, if required
Not required (test-after mode). Tests written immediately after each unit and run red→green locally:
the gravity double-count guard (`test_double_count_trap_diverges`) and the de-conflation-equality test
(`test_variantA_and_variantB_deconflate_equally`) were the load-bearing correctness checks and both pass.

## Docs/contracts touched
- None. (Adapter docstring documents its own contract; no architecture doc edited — that is Cartographer's.)

## Assumptions
- **Capability ceiling metric** = `a_brake(v_ref)` at `v_ref = 80 m/s` (a representative high braking-entry
  speed where downforce is loaded). The codebase's `braking_report.py` reports `a_brake` at 30/60/90; I used a
  single high reference for the A-vs-B headline because the comparison is *relative* (both variants share
  v_ref, so the verdict is invariant to the exact reference). `a_b` (the floor) and `b_b` are reported raw, so
  the ceiling at any other speed is reconstructable from the JSON.
- **Per-lap contiguity** obtained by splitting the classified sample list on the `processed["lap_number"]`
  column (classification is row-for-row with the processed telemetry, laps concatenated time-ordered). This
  reuses the production `_driver_samples` loader unchanged rather than re-classifying per lap.
- **Pooled terrain profile** built from BOTH cars' XYZ (matching `prepare_braking_frontier`'s `all_xyz`
  pooling) so θ/z are consistent across the two drivers.
- Mexico A n=197 vs B n=196: a 1-sample difference from the `_DECEL_CEILING` glitch rejection acting on
  slightly different a_long values between the two paths — negligible, does not affect the verdict.

## Stop conditions hit
- **None.** Per-lap estimate aligned cleanly to the classified samples (n identical A vs B on all 6 circuits);
  gravity de-conflation made unambiguous (and unit-guarded); no production view touched; all required evidence
  produced.

## Out-of-scope observations
- **Pre-existing simplification debt:** `terrain.py::build_terrain_profile` is 105 lines (limit <100). It is
  non-gated (canonical run exits 0) and not introduced by me, but it's a decomposition candidate if terrain.py
  is next touched.
- **b_b/ceiling divergence is the real open question** (see recommendation). It is the substantive physics
  finding behind the mixed verdict and the natural next measurement: a b_b-pinned A-vs-B re-run. Flagging as a
  triage candidate for G3.
- **Singapore a_b↔b_b trade-off** (largest cov off-diagonal, −1.6e−2) suggests the Singapore braking cloud is
  weakly identified for the frontier curvature; worth a per-circuit bandwidth-sensitivity check if Singapore is
  ever load-bearing for a decision.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — NEW `decoupled_braking_input.py`
  (`build_decoupled_braking_input`, `estimate_driver_braking`, `estimate_lap_longitudinal`,
  `split_samples_by_lap`, `DecoupledBrakingInput`); `terrain.py` gains `altitude_at_positions` (companion to
  `gradient_at_positions`). Both additive; no edge into production views.
- **Capabilities affected:** physics capability-frontier measurement — a NEW, terrain-aware (#497 z-map),
  per-lap-contiguous braking-frontier input path measured alongside the incumbent. Not wired.
- **Constraints/assumptions touched:** `decision:two_cycle_external_anchor_design` honored (anchor is the
  TV-denoised RAW `a_long` from `clean_longitudinal_from_raw`, never a smoothed trajectory);
  `constraint:physics_region_no_evo_import` honored (no evo/latent_power/compound_prior imports).
- **Decision candidates:** `decision:decoupled_1d_longitudinal` (the G3 wiring this gate measures) and
  `decision:smoother_rounds_braking_knee` — both are informed by this report's numbers; the retire/keep is
  surfaced for the user, not decided here.
- **Claims/evidence produced:** side-by-side `(a_b,b_b)`+cov+ceiling on 6 circuits × 2 cars; gravity-corrected
  F_vehicle frontier metric (Variant A) measured with gravity counted once via the z-map.
- **Triage candidates:** (1) b_b-pinned A-vs-B re-run to resolve the ceiling divergence before any retire;
  (2) `build_terrain_profile` decomposition; (3) Singapore frontier-identifiability check.

## Workflow Feedback
- **Handoff gaps:** The handoff did not name a **capability-ceiling metric** (which `v_ref`, or whether to use
  the house `a_brake @ 30/60/90` convention from `braking_report.py`). I chose `a_brake(80)` + raw `(a_b,b_b)`
  and documented it; a one-line "report ceiling as a_brake@<v>" would have removed the judgment call. This is
  the single concrete field I'd add.
- **Context rediscovered:** The decimetre/metre scaling caveat in the handoff ("raw `spd_d`/`pos_d` XYZ need
  ×0.1") was a near-miss — I had to verify in `loaders.py` that `driver_streams` ALREADY returns metres
  (`* 0.1`), so `_driver_samples`' `xyz` and `KinematicSample.position` are both metres and need NO further
  scaling. The handoff's note is correct *for raw FastF1 reads* but could note that the `_driver_samples` path
  it points me at is already scaled, to pre-empt a double-scale bug.
- **Instructions improvised around:** The implementer template's plan has `record --result` for postconditions,
  but the engine refused it ("record is for survey checklists; use advance") and auto-ran command-checked
  postconditions on `advance`. I drove gates via `advance` (engine runs the check) instead of attest-then-advance
  for engine-checked conditions — correct behavior, but the template's `{"check": {"kind":"command"}}` plus the
  result template's `record` verb read as contradictory until I saw the engine reject `record`.
- **What would have made this easier:** Name the ceiling metric in the handoff Close Criteria, and add the
  one-line "`_driver_samples` xyz is already metres" note next to the decimetre caveat. Both are 1-line additions.

## Return status
`complete`
