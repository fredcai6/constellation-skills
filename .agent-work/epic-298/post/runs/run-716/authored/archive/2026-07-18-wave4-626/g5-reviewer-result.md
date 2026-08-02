# Review Result

## Assigned Gate
`g5` — F6 held-out gate harness (`gate_f6.py`) + Phase-2 writeup + JSON. Emitted VERDICT = PASS (9/11 covered axis-beats). Reviewed adversarially: the PASS was scrutinized hardest of all.

## Result
`APPROVE` — the PASS is honest and survives adversarial scrutiny.

## Handoff compliance
Every close criterion met. Headline: I independently re-ran `gate_f6.run_gate()` against the live store and it reproduces the committed `626-f6-holdout-gate.json` **exactly** — verdict=PASS, covered_beats=9, n_beats_frozen=9, median ratio 0.399889, accuracy 268/888 (30.18%), ablation Δ {full 0, −L1 0, −L2 0, −L3 7, −L4 9}. The JSON is a genuine product of this run, not stale or hand-edited.

## Scope drift
None. Only the 4 allowed new files. `git status` shows no g1–g4 module edits, no `gate_spec` change, no `data/*.db`, nothing staged. grep confirms zero `evo_predictor`/`evo` imports in `gate_f6.py`+`gate_spec.py`; no DB writes. Docs under `docs/physics/` (not gitignored `reports/`).

## Evidence verdict
13/13 tests pass (~26s), re-run confirmed. The test **does not require PASS**: `test_emits_a_valid_verdict_either_way` accepts `{PASS, DID-NOT-BEAT-FLOOR}`, and `test_verdict_follows_from_covered_beats_and_threshold` derives the verdict from the covered-beat count vs the frozen threshold in whichever branch the run lands — an honest null is an equally valid completion. Independent reproduction is the load-bearing evidence, and it matches.

## Code/doc quality
The seven adversarial checks were each verified in **source**, not taken from the writeup:

1. **Frozen rule, not re-tuned** — `gate_f6` imports `gate_spec.{BEAT_THRESHOLD_AXES, BOOTSTRAP_N, BOOTSTRAP_SEED, NOISE_MARGIN_ALPHA}` and the `evaluate_gate`/`evaluate_axis` composition. The verdict is `covered_beats >= gate_spec.BEAT_THRESHOLD_AXES`. The only added constant, `MIN_COVERED_CAR_SEASONS=5`, is a strictly *tightening* gate: `covered_beat = r.beats AND coverage>=5` — it can only turn a beat OFF, never on. A higher floor makes PASS *harder*, so it cannot be gaming toward PASS. On this run tc1 removed no beat (both non-beats already fail the frozen rule), so the verdict is immaterial to the tc1 value.
2. **No leakage** — `model.fit(train_df)` learns all hyperparameters on train only; `transform` applies stored params row-wise (`apply_layer4` is per-row, output depends only on the row's own reading + train pool). Split is the frozen `holdout.split` (`round_idx % 3 == 0`). Ablation pools (`pools_noL1`, `pools_noL3`) are fit on TRAIN and applied to held-out — same discipline.
3. **[F2] Paired floor** — `paired_holdout_floor_per_car_season(holdout_df, axis)` recomputes `weekend_relative` on the held-out subset per car-season; it does **not** touch `floor.per_axis_stats`/the 624 full-sample table (which the docstring names as the reproduction target only).
4. **[F1] Guard gates the beats** — `evaluate_axis` intersects `floor ∩ model ∩ guard_pass_index`; `_axis_coverage` does the same. Reproduced the −L3 result: shrinking the L1 residual directly tightens *numerically harder* (ratio 0.087) but the guard rejects it on 9/11 axes → 2 beats. That is the over-shrinker being correctly rejected — the guard is real, not decorative.
5. **[tc1] Coverage floor ≥5** — applied in `_evaluate_variant` and locked by `test_every_covered_beat_meets_the_coverage_floor`. `max_power_w` (cov=3) is correctly excluded.
6. **[F4] Ablation real** — −L1/−L3/−L4 rebuild genuine held-out columns by reusing the frozen layer functions. −L2 aliases `full` **because model L2's delta is provably 0** (`_apply_layer2` sets delta=0, passes L1 residual through), so removing it is an exact no-op — the aliasing is a valid optimization, transparently disclosed in code + writeup, not a hidden shortcut. Δ0 is reported, not buried.
7. **Honesty** — The 30% accuracy-preservation caveat is **bolded** ("Overall: 268/888 (30%)") with the "~70% fail the guard, excluded from the count" explanation. Per-axis nulls (`max_power_w` 3/80 with negative bootstrap lower-q; `coast_drag_area_m2` 0/81) appear in the result table, a dedicated "two non-beats are honest" section, the accuracy table, and the Honest-status section. The verdict line itself flags "three load-bearing caveats that keep the PASS from being over-read." The PASS is represented fairly — it does not read stronger than the data supports.

Fowler pass: `verify_fowler_pass.py` exits 0 (12 smells; flagged=[duplicated-code]; overridden=[data-clumps, primitive-obsession] with logged standard+reason each).

## Map impact verdict
- **Evidence supports claimed change:** Yes — JSON + green tests + independent reproduction back "beats the paired held-out floor on 9/11 covered axes."
- **Constraints not violated:** `physics_region_no_evo_import` asserted (and test-enforced); no-leakage honored; no `data/*.db` write; docs in `docs/physics/`.
- **Notes match the diff:** Yes — structural anchors, capability, and decision-realized notes all match what the diff touched; nothing overstated.
- **Decision candidates surfaced:** N/A — no authority-exceeding decision; the frozen rule was pinned upstream in g1.
- **Durable context routed:** Trust limitations (narrow 30% PASS, L4-concentrated, per-axis nulls) honestly flagged as triage in the implementer result.

## Reconciliation check
No architecture divergence requiring Commander reconcile. New module composes frozen g1 rule + g4 model with no new edge into evo.

## Blockers
- none — confirmed after independent reproduction: no criterion failed.

## Out-of-scope observations
- (low severity, non-blocking) `gate_f6._axis_coverage` re-derives the `floor ∩ model ∩ guard-pass` intersection that `gate_spec.evaluate_axis` already computes internally (`common2`). It stays correct today because both use the same frozen primitives, but exposing the covered-car-season count from `evaluate_axis` would remove the duplication and any future drift risk. Flagged as tc1 triage candidate.

## Workflow Feedback
- **Handoff gaps:** none material — the handoff's per-check breakdown (frozen rule / paired floor / guard / coverage floor / ablation / honesty) mapped cleanly onto verifiable source checks and named the exact anti-gaming traps to test.
- **Context rediscovered:** minor — the handoff asserts "−L2 Δ0 confirms g3 FLOAT" without noting that `_variant_model_cols` *aliases* −L2 to full (so Δ0 is exact-by-construction, resting on model.py's L2-delta-0, not a fresh re-run). Had to open `model._apply_layer2` to confirm the aliasing is a valid no-op rather than a skipped ablation. Worth one line in the handoff.
- **Instructions improvised around:** none — engine `current` verb rejects `--session-id` (read-only), unlike mutating verbs; briefly tripped on it. Cosmetic.
- **What would have made this easier:** a one-line pointer in the handoff that the JSON is regenerable via `gate_f6.run_gate()` (I derived it) would speed the independent-reproduction step.

## Return status
`complete`
