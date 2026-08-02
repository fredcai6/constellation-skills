# Implementer Handoff

## Gate
`g5` — The F6 held-out gate harness + the writeup. The culminating deliverable: run the frozen metric on the full four-layer model's output on the held-out split, produce an HONEST verdict (PASS or DID-NOT-BEAT-FLOOR), and document everything.

## Task
Build `src/physics/weekend_state/gate_f6.py` + `docs/physics/626-phase2-weekend-state-model.md` + `docs/physics/626-f6-holdout-gate.json` + `tests/unit/physics/weekend_state/test_gate_f6.py`.

## gate_f6.py
- IMPORT and apply the g1 FROZEN `gate_spec.py` decision rule (do NOT re-derive or re-tune it — import the constants + functions).
- Fit `model.WeekendStateModel.fit(train_df)` on TRAIN weekends only (g1 `holdout.py` split); compute the model's car-signal on the HELD-OUT weekends (no leakage — the g4 model guarantees this).
- **[F2]** Recompute the raw x4 weekend-relative floor on the IDENTICAL held-out weekends, PAIRED per car-season (use g1 `floor.py` on the held-out subset). The 624 full-sample table is NOT the comparison denominator.
- **[F1]** Score the model's held-out car-signal via the frozen `gate_spec` signal-preservation guard (out-of-sample residual around the train-fit trajectory) so an over-shrinker cannot win — PASS requires faster convergence AND preserved held-out accuracy.
- Produce the per-axis table: model held-out convergence-speed vs the paired held-out floor; count how many of 11 axes beat the floor by a margin OUTSIDE the frozen car-season bootstrap noise (fixed seed from gate_spec).
- **[tc1 — per-axis coverage floor, folded from g1 review]** Report per axis the number of contributing car-seasons on the held-out subset, and require a minimum covered-car-season count for an axis-beat to COUNT (so a thin-coverage axis cannot be gamed into the ≥7/11 tally). Pick a defensible minimum (e.g. ≥5 held-out car-seasons) and state it; report coverage alongside each axis result.
- **[F4]** Held-out LEAVE-ONE-LAYER-OUT ablation: Δ convergence with/without each of the 4 layers, so each layer's marginal contribution is reported and no dead layer is credited. (Expect Layer 2 ≈ 0 marginal — that is the honest confirmation of g3's FLOAT.)
- VERDICT by the frozen rule: `PASS` iff ≥7/11 held-out axes (with adequate coverage) beat the paired floor by a margin outside noise AND held-out accuracy preserved; else `DID-NOT-BEAT-FLOOR` (honest null). Emit both the verdict and the full per-axis table + ablation.

## Writeup — docs/physics/626-phase2-weekend-state-model.md
Cover: the four layers and HOW each is modelled + its σ; specifically how L2 within-session evolution works + WHY it floats on the frozen split (the per-car session-time bridge gap), and how L3 cake-and-eat-it (relative + `fit_drift` re-anchor) works; the F6 held-out result table + verdict + noise margin + per-axis coverage; the per-layer ablation; the Mexico-vs-Monaco density secondary check (from g2); and the honest-null/float status. Match the `624-*`/`625-*` doc precedent. `docs/physics/626-f6-holdout-gate.json` = machine-readable per-axis result + ablation + verdict.

## Protected Intent (the whole run's honesty rests here)
The verdict must be HONEST. Freeze the methodology (it already is — gate_spec is frozen from g1) and do NOT tune anything after seeing held-out numbers. An honest DID-NOT-BEAT-FLOOR with the real numbers is a COMPLETE, valuable outcome — do NOT manufacture a PASS. Report exactly what the held-out data says.

## Test Mode
Test-after allowed. The test asserts the harness runs end-to-end and emits a verdict (PASS or DID-NOT-BEAT-FLOOR) with the per-axis table + ablation — the test MUST NOT require a PASS (honest-null is a valid completion).

## Close Criteria
- `gate_f6.py` imports g1 `gate_spec` (not re-derived), fits model on train only, evaluates on held-out with the paired floor + signal-preservation guard + coverage floor + ablation, emits a verdict.
- The per-axis table, coverage counts, ablation, and verdict are written to `docs/physics/626-f6-holdout-gate.json` and narrated in `docs/physics/626-phase2-weekend-state-model.md`.
- `test_gate_f6.py` passes and does NOT require PASS.
- No evo import; no `data/*.db` staged; docs under `docs/physics/` (NOT `reports/`, which is gitignored).

## Allowed Scope
`src/physics/weekend_state/gate_f6.py`; `tests/unit/physics/weekend_state/test_gate_f6.py`; `docs/physics/626-phase2-weekend-state-model.md`; `docs/physics/626-f6-holdout-gate.json`. MAY read all g1-g4 files + the 624 doc + PLAN_CRITIC_DISPOSITIONS.md.

## Specific Exclusions
Do NOT modify g1-g4 modules, gate_spec's frozen rule, estimator, evo, config. Do NOT commit/modify `data/*.db`. Do NOT re-tune the decision rule.

## Constraints
- Python `py`. Absolute DB paths into `C:/Programs/f1Brainz/data/*`.
- Re-run x4's OWN metric (via floor.py/gate_spec), do NOT invent a new one.
- Held-out split from g1; train-only hyperparameters (no leakage).
- `constraint:physics_region_no_evo_import`.
- The run is FOREGROUND and must be fast (≤ a few min over ~1.6k rows); if a bootstrap is slow, cap iterations sensibly (state the count).

## Map Anchors (inbound)
- Structural: `gate_f6.py` (NEW); `docs/physics/626-*` (NEW); imports g1 `gate_spec`/`floor`/`holdout`, g4 `model`.
- Capability: F6 held-out convergence-speed gate vs x4 floor, verdict either way.
- Constraints: re-run x4 metric not a new one; no-leakage; no db commit; docs in docs/physics.
- Decision: PASS threshold ≥7/11 held-out axes outside noise (F6 pinned) + tc1 coverage floor.
- Evidence: per-axis held-out convergence ratio vs floor; ≥7/11 verdict; per-layer ablation; density secondary.

## Deliverable Path Check
- Committed: `src/physics/weekend_state/gate_f6.py`, `tests/unit/physics/weekend_state/test_gate_f6.py`, `docs/physics/626-phase2-weekend-state-model.md`, `docs/physics/626-f6-holdout-gate.json`. Verify none are gitignored (`git check-ignore` exit 1) — note `reports/` IS gitignored, so use `docs/physics/`.

## Required Evidence
- `py -m pytest tests/unit/physics/weekend_state/test_gate_f6.py -q` → pass.
- The full per-axis held-out table (model vs paired floor, coverage, beat/not-beat, noise margin), the ablation, and the VERDICT — pasted in the result.
- The verdict stated plainly: PASS (≥7/11) or DID-NOT-BEAT-FLOOR, with the count.

## Verification Commands
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_gate_f6.py -q
```

## Suggested Model Tier
Stronger — this is the honest-verdict gate; the reasoning about paired comparison, signal-preservation, coverage floor, and ablation must be exactly right, and the verdict reported without massaging.

## Authority
The frozen decision rule is FROZEN — apply, do not tune. The verdict is whatever the held-out data says. tc1 coverage-floor minimum is yours to set defensibly.

## Stop Conditions
Stop/return if: the held-out split leaves too few car-seasons per axis to evaluate even with the coverage floor (report it — it may itself be the finding), or the model cannot be applied leak-free on held-out (should not happen — g4 verified it).

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/wave4-626/g5-implementer-result.md`: completed slice, files changed, test output, the FULL per-axis held-out table + coverage + ablation + VERDICT (PASS/DID-NOT-BEAT-FLOOR with count), assumptions, stop conditions, out-of-scope observations, workflow feedback.
