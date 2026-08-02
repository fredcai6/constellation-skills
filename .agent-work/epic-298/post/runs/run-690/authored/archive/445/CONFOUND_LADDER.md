# De-confounding / condition-normalization (epic #445 Phase-3, autonomous 2026-06-14)

User direction (AFK): recast raw measurements (natural units) → NORMALIZED parameters CONDITIONED on
situation, to REMOVE confounds (named: compound degradation). Hypothesis: FP-1/FP-2's regime-shape null
(~87% non-replicating) is because raw capability signatures are confounded by tyre-compound+age (degradation),
track-state (rubbering), and fuel-mass — which vary lap/race in ways unrelated to car identity → look like
noise. De-confound using the models we already have (GRIP-3 μ_tyre(C,age) × T_track[race]; N(v) load; m(lap)),
leaving INTRINSIC car capability → should replicate where raw didn't.

## DC-1 — De-confounded grip → regime replication A/B (worktree expt-dc1, branch expt/448-dc1)
Question: does de-confounding grip (divide out compound-degradation × track-state × load) make the per-car
capability signature REPLICATE across races where the raw signature (FP-2) did not?
Method (LIGHT, reuse FP-2/GRIP-3 harvest — per-sample v, a_lat, lap, compound, tyre-age, track-pos, race):
- INTRINSIC grip per sample: μ_car = a_lat / [ N(v) · μ_tyre(C, age) · T_track(race, t) ], using GRIP-3's
  GLOBAL μ_tyre(compound, age) [b_C, g_C from grip3_pooled_order2.json] and PER-RACE T_track(session_time)
  [tau per race]. N(v)=g+k_df·v². This strips load(downforce), compound, age(degradation), track-rubber →
  residual = car's intrinsic grip multiplier (≈ car_factor, ~speed-flat if model right).
- Build the de-confounded signature: μ_car peak-envelope per speed bin (24 bins), per (car, year). Two
  encodings: (i) field-relative per race; (ii) ABSOLUTE intrinsic multiplier (de-confounding should make
  cars comparable WITHOUT field-relative — test both).
- A/B REPLICATION: split-half (disjoint race subsets) of the de-confounded signature's LEVEL and SHAPE vs
  FP-2's raw (shape split-half was 0.40-0.62, <0.7 bar). Does de-confounding push shape replication >0.7?
  Does the intrinsic LEVEL replicate cleaner than raw?
- Also: residual speed-slope of μ_car per car — if de-confounding leaves a stable per-car speed-trend, THAT
  is the downforce/fast-corner axis (k_df differences), now de-noised of compound/track.
Show: de-confounded vs raw split-half (level + shape); whether shape now replicates >0.7; the stable
per-car structure that emerges (if any); honest-null if de-confounding doesn't help (confounds weren't the
masking cause). Light, single bounded run, EVID under worktree, foreground, no smoother.
Sessions: FP-2's ~6-7 races (need GRIP-3's per-race T_track for those races — use the overlap).
