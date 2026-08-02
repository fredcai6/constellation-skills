# Implementer Handoff — G5 tyre-age dashboard + per-axis verdict

## Gate
g5 (issue #511 W3 tyre-age capstone). Worktree `C:/Programs/f1Brainz-511`. `py`, never `python`. FOREGROUND only (no background — dies on idle). Suggested model tier: moderate (wiring + rendering; the hard analysis is in G3/G4).

## Task
New **region-neutral** script `scripts/tyre_age_dashboard.py` (mirror the #512 pattern in `scripts/regime_capability_dashboard.py`). This is the SANCTIONED physics↔evo neutral boundary: the script MAY import both physics (G3/G4 modules, evo-free) AND evo (compound_prior). It reads the populated store, runs the separation + supplant, wires the evo incumbents + #443 cross-check by INJECTION, renders the dashboard, and emits the per-axis verdict.

Pipeline:
1. Run G3 `tyre_separation` over the populated store (per-axis f_tyre + g_track + identifiability + LOO).
2. Build the G4 reshaped truth cells (`tyre_supplant.build_truth_cells` — fuel-corrected cross-stint) + physics predictions (`build_physics_primary_prediction` + `build_physics_pooled_loo_prediction`).
3. Wire the INCUMBENTS as injected per-(race,compound) arrays and score each via `tyre_supplant.score_predictor` on the SAME truth cells:
   - **absolute-C# floor**: per-(gp,compound) `compound_c_number` from `lap_times` (DB int; harder = lower C# = less degradation — align direction so "more degradation = larger value").
   - **compound_prior γ**: from `src.compound_prior` (`load_compound_prior_artifact` / `CompoundNormalizer` — READ runtime_normalization.py for the per-compound γ accessor). The γ degradation coefficient per compound → per-(race,compound) prediction.
   - **#443 cross-check** (comparator, NOT an incumbent): `src.compound_prior.empirical_sensor.predict_compound_degradation` (LOO P=0.8032) — its per-(race,compound) predicted degradation; report its agreement with physics and with the truth.
4. `classify_axis_verdict` per axis → GO/CONTEXTUAL/NO-GO, carrying the modality caveat (physics win/match strong; tie/loss ambiguous vs γ home-field; triangulate with #443).
5. Render the dashboard (matplotlib, like regime_capability_dashboard.py): coverage map, per-axis f_tyre(compound,age) ladders, g_track curves, supplant result table (physics P vs absC# vs γ + #443 agreement, with R²), identifiability map.
6. Emit `tyre_age_verdict.json` to `--out` with per-axis keys `lateral_mech`, `lateral_aero`, `traction` (each: verdict, the metrics, the caveat). Default `--out` to a gitignored/scratch dir; do NOT commit plots or the json.

## Protected Intent
Phase-C MEASURED-not-wired. No evo WIRING into prediction; the dashboard is a diagnostic. The physics modules stay evo-free (the script is the only evo-touching component — the neutral boundary).

## Test Mode
Inspection + end-to-end run. If pure helpers warrant it add focused tests; otherwise the end-to-end run (verified at integrate) is the evidence. Do NOT put evo imports in any src/physics module.

## Close Criteria
- `scripts/tyre_age_dashboard.py` runs end-to-end on the populated store and EMITS `tyre_age_verdict.json` with the three axis keys.
- Evo reads (compound_prior γ, #443) are CONFINED to the script (physics modules remain evo-free — verify tyre_separation.py / tyre_supplant.py still import no evo).
- All predictors scored on the SAME reshaped truth cells via the neutral metric.
- #443 used as CROSS-CHECK only (reported as agreement; not the incumbent).
- Verdict carries the modality caveat; 2σ is a reference not a gate.
- No committed generated artifacts (plots/json to a gitignored/scratch --out).
- `--year`, `--store`, `--out` args.

## Allowed Scope
`scripts/tyre_age_dashboard.py` (new). Optional focused test if pure helpers extracted. Read-only consumption of: race_stint_estimates store, physics_estimates.db, lap_times, tyre_separation, tyre_supplant, src/common/pairwise_ordering, src/compound_prior (γ + empirical_sensor).

## Specific Exclusions
No evo import in ANY src/physics module. No modification of G3/G4/W2/quali/compound_prior modules. No committed .db / plots / verdict json.

## Constraints
- scripts/ are region-neutral (this is the sanctioned boundary). `constraint:physics_region_no_evo_import` is honored BY the evo reads living in the script, not in src/physics.
- artifact policy — no committed generated outputs. `py` not `python`.

## Verified Seams (re-verify from source)
- G3 `src/physics/layer2/tyre_separation.py`: `load_stores_ro(race_db_path, quali_db_path, year=2023)`, `separate_axis(race_df, quali_df, axis, *, prior=None)`, `separate_all`/`summarize` (read the file for exact). `AxisSeparation`/`CompoundEffect`/`TrackEvolution`/`Identifiability`/`LOODiagnostic` dataclasses.
- G4 `src/physics/layer2/tyre_supplant.py`: `build_truth_cells(...)` (fuel-corrected, post-rework), `build_physics_primary_prediction(...)`, `build_physics_pooled_loo_prediction(...)`, `score_predictor(cells_df, predicted, ...)`, `interval_overlap(...)`, `classify_axis_verdict(...)`, `run_supplant(...)`. READ the file for the exact signatures (the truth reshape may have adjusted build_truth_cells' inputs).
- `src/common/pairwise_ordering.pairwise_ordering_accuracy(cells_df, predicted, truth_col, weight_col, race_col)`.
- `src/compound_prior/__init__.py`: `CompoundNormalizer`, `CompoundPriorArtifact`, `load_compound_prior_artifact`, `load_time_safe_compound_prior`. Gold artifact under `params/gold/compound_prior/` (find the 2023 artifact). READ `runtime_normalization.py` for the per-compound γ accessor.
- `src/compound_prior/empirical_sensor.py`: `predict_compound_degradation(...)`, `build_degradation_cells(laps_df)`, `fit_empirical_model(...)`, `load_race_laps(...)`, `EmpiricalDegModel`. READ for exact signatures. (LOO P=0.8032 validated 2022+.)
- `lap_times.compound_c_number` (per-year DB, DB int) for the absolute-C# floor.
- Pattern reference: `scripts/regime_capability_dashboard.py` (#512 dashboard + per-axis readout).

## Map Anchors (inbound)
- **Structural:** `scripts/tyre_age_dashboard.py` (non-map node; neutral boundary); consumes G3 + G4 (physics) and compound_prior (evo).
- **Constraints:** `constraint:physics_region_no_evo_import` (honored by being a script, not src/physics); artifact policy.
- **Decision:** `decision:regime_readiness_rubric` (#512) — dashboard + per-axis verdict pattern. Decision pressure (candidate): neutral-boundary injection wiring lands here.

## Required Evidence
1. End-to-end run (paste): the command + the emitted `tyre_age_verdict.json` (the three axes) + the supplant table (physics P / absC# P / γ P / #443 agreement + R²) against the reshaped truth.
2. evo-free re-assertion on src/physics (paste): tyre_separation.py AND tyre_supplant.py still import no evo.
3. Confirmation no generated artifacts are staged for commit (`git status` — plots/json under the scratch --out, not the repo).

## Verification Commands
```bash
py scripts/tyre_age_dashboard.py --year 2023 --store C:/Programs/f1Brainz/data/race_stint_estimates.db --out C:/Users/fredc/AppData/Local/Temp/claude/tyre_dash_511
py -c "import json,glob; f=glob.glob('C:/Users/fredc/AppData/Local/Temp/claude/tyre_dash_511/*verdict*.json')[0]; v=json.load(open(f)); assert set(v)>= {'lateral_mech','lateral_aero','traction'}; print('axes', list(v))"
```

## Suggested Model Tier
Moderate (wiring + rendering; the analytical heavy lifting is done in G3/G4).

## Authority
Commander decided: dashboard is the neutral boundary (evo reads here only); #443 is cross-check not incumbent; verdict carries modality caveat; 2σ reference; outputs not committed. You own: dashboard layout, plot set, verdict json schema, the γ/#443 prediction extraction mechanics. Do NOT put evo imports in src/physics; do NOT commit generated outputs; do NOT modify G3/G4/compound_prior.

## Stop Conditions
Stop and return if: a physics module would need an evo import to wire an incumbent (it must not — inject instead); the compound_prior γ or #443 accessor cannot produce per-(race,compound) predictions without retraining (report and use what's available); the dashboard cannot emit the per-axis verdict.

## Return Format
IMPLEMENTER_RESULT to `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g5-implementer-result.md`: completed slice, files changed, evidence blocks, the FINAL per-axis verdict (lateral_mech/lateral_aero/traction GO/CONTEXTUAL/NO-GO) + supplant table (physics vs absC# vs γ + #443), assumptions, stop conditions, out-of-scope observations, Workflow Feedback.
