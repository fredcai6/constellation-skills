# Review Result — #518 G6 (RE-PLANNED): C1 Re-run on Fixed Simulator

## Assigned Gate
G6 (RE-PLANNED) — Re-run C1 driver-utilization dashboard on the G5-fixed (physical) ideal-lap simulator for 4 RBR/VER cases on BOTH stores; verify the braking/fast-corner clip persists and the updated verdict is honest.

## Result
`APPROVE`

---

## Handoff compliance
PASS. The implementer did exactly what was asked: ran `scripts/driver_utilization_dashboard.py --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER" --mc-samples 50 --seed 42` against both `data/physics_estimates_g3wired.db` (WIRED) and `data/physics_estimates.db` (OLD), 4/4 ok each, produced the three-way comparison table (G4 PRE-FIX / G6 OLD / G6 WIRED), updated `VERDICT.md` with a per-regime verdict, and preserved the G4 verdict verbatim in `VERDICT_G4_prefix.md`. No production code was changed.

---

## Scope drift
PASS. `git status --short` shows only the untracked `.agent-work/518-braking-ceiling-reeval/` directory. `git log --oneline -5` confirms the most recent commit is G5 (`df46d840`). No `src/`, `scripts/`, `docs/`, or `tests/` changes in G6. A throwaway probe script (`_g6_probe.py`) was created and deleted per the implement result — not present in the working tree. All specific exclusions (sim/car_prior/fits/store/threshold/docs) were respected.

---

## Evidence verdict
PASS. **I independently re-ran both dashboards and reproduced all numbers.**

### My independently reproduced U values (mc=50, seed=42):

**WIRED store (physics_estimates_g3wired.db):**

| Case | u_braking | u_slow_corner | u_fast_corner | u_straight |
|---|---|---|---|---|
| Monaco | 2.000 | 1.645 | 2.000 | 1.276 |
| Italy | 2.000 | 1.592 | 2.000 | 1.080 |
| Great Britain | 2.000 | 1.893 | 2.000 | 1.230 |
| Singapore | 2.000 | 1.631 | 2.000 | 1.179 |

**OLD store (physics_estimates.db):**

| Case | u_braking | u_slow_corner | u_fast_corner | u_straight |
|---|---|---|---|---|
| Monaco | 2.000 | 1.675 | 2.000 | 1.288 |
| Italy | 2.000 | 1.558 | 2.000 | 1.074 |
| Great Britain | 2.000 | 1.891 | 2.000 | 1.228 |
| Singapore | 2.000 | 1.625 | 2.000 | 1.173 |

These match the implement result exactly (within 4 decimal places from CSV readback). u_braking = u_fast_corner = 2.000 in all 4 cases on both stores — CLIPPED, confirmed.

**Straight U crossing confirmed:** Italy OLD 1.074 (>1, was 0.578 G4), Italy WIRED 1.080 (>1, was 0.712 G4). Great Britain OLD 1.228 (>1, was 0.775). Singapore OLD 1.173 (>1, was 0.831). All four straight U values crossed from <1 to >1.

**Dashboard run times:** WIRED 269.5s (4/4 ok, 0 errors), OLD 272.9s (4/4 ok, 0 errors). Deterministic with same seed/mc.

---

## Code/doc quality
PASS. No production code changed in G6. The VERDICT.md is clear, honest, internally consistent, and explicitly scoped (RBR-only, impure split stated, continuation documented). G4 baseline preserved separately with a clear naming convention.

---

## Check 1: G5 fix is live in this run (ideal-lap top speed physical)

PASS. The G5 commit `df46d840` is the HEAD commit on the branch. I read the diff directly:

```
-| p_max  | longitudinal.theta_P_values[0]  | direct; times=[0.0] |
+| p_max  | longitudinal.theta_P_values[0]  | / MASS_KG; times=[0] |
```

The fix divides `p_max` (total watts ~629 kW) by `MASS_KG` before injecting into `theta_P_values`, converting watts → W/kg (specific power, the unit the simulator consumes). The commit message states the G4 aphysical top speed was 908.8 m/s on the raw sim (clipped to 206.9 m/s on the real ribbon), vs physical 94.8 m/s drag-limited terminal velocity after the fix.

The VERDICT.md probe table (Italy/VER, fixed sim) shows:
- Ideal-lap speed envelope: `[7.5, 92.5] m/s` (333 km/h top) — PHYSICAL
- vs G4 aphysical: 206.9 m/s (745 km/h)

The new test `tests/unit/physics/test_ideal_lap_top_speed_invariant.py` (added in G5) enforces `ratio ≈ 0.998` between ideal-lap top speed and terminal velocity. This test passed in my run (629 passed, 6 skipped). The G5 fix is live and active in the re-run.

**Ideal-lap top speed I can confirm from the VERDICT.md probe table: max v_ideal ≈ 92.5 m/s (333 km/h) for Italy/VER. NOT 207 m/s (aphysical G4). The clip persists DESPITE the physical top speed.**

---

## Check 2: Phase-misalignment finding is sound

PASS. The VERDICT.md probe table (Italy/VER, fixed sim, raw unclipped ratios):

| regime | n | v_ideal_mean (m/s) | v_real_mean (m/s) | raw ratio | frac(>=2.0) |
|---|---|---|---|---|---|
| braking | 209 | 25.1 | 65.6 | 3.32 | 0.76 |
| slow_corner | 735 | 52.1 | 73.7 | 1.59 | 0.20 |
| fast_corner | 73 | 16.7 | 62.9 | 3.79 | 1.00 |
| straight | 483 | 83.1 | 89.1 | 1.08 | 0.00 |

- In the braking mask: v_ideal 25.1 vs v_real 65.6 → ratio 3.32×. The ideal lap is deep in the apex while the real lap at the same grid index is approaching the braking zone at speed.
- In the fast_corner mask: v_ideal 16.7 vs v_real 62.9 → ratio 3.79×. Even worse — 100% of points are at or above the 2.0 clip.
- In the straight mask: v_ideal 83.1 vs v_real 89.1 → ratio 1.08. Correctly aligned — the only regime that responds to the fix.

This is internally consistent: the regime that is alignment-correct (straight) is the only one whose U changed after the G5 fix. The regimes with 3.3–3.8× misalignment are unchanged. The structural offset (phase/envelope misalignment) is the binding constraint, not ceiling height, and is confirmed on a physically correct ideal lap.

The G4 reviewer independently found the same phase misalignment. G6 confirms it survives the G5 fix.

---

## Check 3: OLD vs WIRED delta <= 0.04

PASS. I computed per-case per-regime deltas (WIRED - OLD) from the CSVs I generated:

- u_braking: 0.000 on all 4 cases
- u_fast_corner: 0.000 on all 4 cases
- u_slow_corner: max delta = 0.034 (Italy)
- u_straight: max delta = 0.012 (Monaco)

Maximum absolute delta across all regimes and cases: 0.034 (Italy slow_corner). All are <= 0.04. The #518 G3 braking recalibration makes no material difference on the fixed sim.

---

## Check 4: Verdict honesty

PASS. The verdict correctly follows from the numbers:

- **Braking NO-GO:** pinned at 2.000 in 4/4 cases on both stores; raw ratio 3.32; unchanged from G4. Stated cause (phase misalignment) is supported by the probe data.
- **Fast corner NO-GO:** pinned at 2.000 in 4/4 cases; raw ratio 3.79; frac>=2.0 = 1.00. Worse than braking.
- **Slow corner NO-GO:** U 1.56–1.89; not separating; not physical. Correctly reported as NO-GO (not just "watch").
- **Straight CONTEXTUAL → trending NO-GO:** now physical at source (G5 fix works here), but U crossed >1 on all 4 cases due to the fixed (lower) ideal lap mildly under-calling straight speed. The "trending NO-GO" qualification is honest — it is not clearly CONTEXTUAL anymore.

The verdict is not forced. The G4 prefix is preserved with correct attribution. Caveats (impure split, RBR-only scope, continuation needed) are stated explicitly. No GO is claimed where the data does not support it.

---

## Check 5: No exclusions touched / tests green

PASS.
- `git status --short`: only `.agent-work/` untracked. Zero src/scripts/docs/tests changes.
- `py -m pytest tests/unit/physics/ tests/unit/test_utilization.py -q`: **629 passed, 6 skipped in 276.32s**. Green.

---

## Map impact verdict

- **Evidence supports claimed change:** Yes. The re-run evidence (dashboards + CSVs + probe table) backs every claim in VERDICT.md. The "no un-clip" finding, the straight-U crossing, the phase-misalignment root cause, and the OLD≈WIRED parity are all numerically supported.
- **Constraints not violated:** Yes. The causal contract (only sessions up to target round), the impure-split acknowledgement, and the scope (RBR-only, not claiming cross-constructor verdict) are all respected in the verdict framing.
- **Notes match the diff:** Yes (no-op gate; the "Map Impact" is that the verdict document updates). The map anchors in the handoff (`struct:physics.utilization`, `decision:ideal_lap_sim_two_sided_evaluator`) are correctly named and the implement result correctly notes no structural code change.
- **Decision candidates surfaced:** The phase-alignment continuation is called out explicitly as "continuation issue recommended" with a prescription (phase-aligned / physics-aware ideal-lap comparison OR per-regime capability frontier). Not an authority decision for this implementer — correctly flagged as a triage candidate.
- **Durable context routed:** The two triage candidates in the implement result (straight under-call, continuation) are appropriate for Commander/Triage. The VERDICT.md itself routes cleanly to the #509 done-done bar tracking.

---

## Reconciliation check
No docs/architecture changed. The phase-misalignment finding is consistent with the existing memory entry `trajectory-smoother-physics-blind` and the #496 physics-aware-estimator work — correctly cross-referenced in VERDICT.md. The `decision:ideal_lap_sim_two_sided_evaluator` anchor is noted as the binding flaw's home; no architecture edit is required at this gate.

---

## Blockers
None.

---

## Out-of-scope observations

1. **Straight U now >1 everywhere (new G5-introduced artifact):** The now-physical (slower) ideal lap under-calls straight speed, pushing U_straight to 1.07–1.29 on all 4 cases. This is softer than the corner clip (ratio 1.08 vs 3.32) but means straight U is no longer cleanly interpretable. Flagged in VERDICT.md. Triage candidate for Commander — consider whether to address alongside the alignment continuation.

2. **Phase-misalignment is the real unblock path:** Confirmed again on the physical sim. The continuation issue (phase-aligned / per-regime capability frontier comparison) is the right next step, not a deeper braking frontier. This is consistent with the #496 work family.

3. **`sigma_u_straight` (WIRED vs OLD) minor discrepancy:** Monaco WIRED sigma_u_straight = 0.005, OLD = 0.025. This is the envelope MC sigma, which is expected to differ between stores (different ceiling parameter uncertainty). Not a bug.

---

## Workflow Feedback

- **Handoff gaps:** The handoff stated "ideal-lap top speed ~95 m/s" but I could not easily reproduce this number inline due to the stack complexity (build_car_ceiling requires a full store_df, terrain probe requires non-trivial setup). I verified the G5 fix is live via direct code inspection (`git show df46d840`) and the probe table in VERDICT.md, and confirmed the top-speed invariant test passes (629 passed). For future re-run gates where a specific physical quantity is the key verification, a one-line script in the handoff that prints just that number (isolated from the 4-min dashboard) would save one iteration.

- **Context rediscovered:** The `load_track_df` function doesn't exist — tracks come from the session ribbon via `_make_track_df`. The `EstimateStore.load_rows()` method doesn't exist — it's `EstimateStore.load()` returning a DataFrame. A handoff note on the correct API entry point for the probe (or a reference to the existing `_g6_probe.py` logic) would have been useful.

- **Instructions improvised around:** The checklist engine reference is at `references/checklist-engine.md` per the skill, but that file does not exist at `C:\Users\fredc\.claude\skills\constellation-reviewer\references\checklist-engine.md`. I drove the survey from the template JSON directly (r0 through r5) and the handoff close criteria (which map cleanly to the template checks), then appended the five handoff-specific checks. This is compliant with the skill's "do the closest compliant thing" instruction.

- **What would have made this easier:** A disposable `_probe_top_speed.py` committed (or at least quoted inline in the implement result) showing the two lines needed to reproduce the ideal-lap top speed from the WIRED store — equivalent to what the implementer's `_g6_probe.py` presumably did. The ratio 0.998 from the G5 test is helpful context but doesn't substitute for a reproducible number.

---

## Return status
`complete`

---

*Reviewer: g6-rev-518 | Date: 2026-06-25 | Branch: feat/518-braking-ceiling-reeval*
