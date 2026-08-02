# Implementer Handoff — G4 supplant scoring + per-axis verdict rubric

## Gate
g4 (issue #511 W3 tyre-age capstone). Worktree `C:/Programs/f1Brainz-511`. `py`, never `python`. Run all compute FOREGROUND (no background — dies on idle here; bounded work). Suggested model tier: **stronger (Opus-class)** — anti-circular + LOO design is subtle.

## Task
New evo-free module `src/physics/layer2/tyre_supplant.py` + `tests/unit/physics/layer2/test_tyre_supplant.py`. Run the ratified SUPPLANT test: does physics μ_tyre(age) beat the incumbent lap-time compound estimators on per-(race,compound) degradation ordering?

Components:
1. **Truth cells** — pure helper `build_truth_cells(...)` that, from `lap_times` (read-only sqlite, per-year DB), computes per-(race, compound) the **within-race centred lap-time degradation slope** (clean green laps: `valid_lap=1`, `track_status='1'`, no pit; regress `lap_time` on `tyre_life` per (driver,stint); aggregate to (gp_name, compound) cells) + a **weight** = lap count. This is the INDEPENDENT truth channel (lap-time, NOT telemetry grip). Return a DataFrame with columns `gp_name, compound, deg_slope, lap_count` (+ a `race` alias for the neutral metric's `race_col`).
2. **Physics prediction** per (race, compound): the measured physics decay. PRIMARY = per-(gp_name, compound) **mean lateral_k** from the `race_stint_estimates` store (dry compounds, ok rows). Also support a SECONDARY variant = the G3 season-pooled per-compound k (a global ordering) scored **LOO** (predict race r from the pool fit EXCLUDING race r) — the season-pooled variant is self-weighted, so LOO is mandatory (`lesson:loo-residual-diagnostic`).
3. **Scoring core** — pure `score_predictor(cells_df, predicted, ...)` using the NEUTRAL `src/common/pairwise_ordering.pairwise_ordering_accuracy` (within-race P) + a magnitude **R²** (predicted-deg vs truth-deg) + an **honest covariance overlap** check (do the physics per-compound k intervals overlap the incumbents'?). Score physics AND each INJECTED incumbent array on the SAME cells.
4. **`classify_axis_verdict(...)`** pure function → per-axis **GO / CONTEXTUAL / NO-GO** from {coverage, G3 separability, supplant-beat (physics P vs best incumbent), LOO-honesty}. **2σ = reference, NOT a gate** (fine-margin). Honest-null axes return NO-GO/CONTEXTUAL — that is a valid, complete verdict.

INCUMBENTS ARE INJECTED ARRAYS — the module imports NO evo package. The dashboard (G5) reads the evo incumbents and passes their per-cell prediction arrays in. The scoring core just takes `predicted: np.ndarray | pd.Series` aligned to `cells_df` (exactly the neutral-metric contract).

## Protected Intent
Phase-C MEASURED-not-wired. No evo wiring. Anti-circular: physics prediction is the structural-prior separation/measured-k ONLY — NO #443 empirical magnitudes; truth (lap-time slope) is independent of the physics feature (telemetry grip decay). Judge **degradation-estimation quality, NOT finish-ranking** (#443 POC: finish-ranking is car-dominated → Phase-P #450).

## Test Mode
Test-after acceptable; load-bearing tests are synthetic: truth-cell builder (planted slopes recovered), P ordering (a predictor that matches truth scores high, a reversed one scores low), verdict classification (each branch), evo-free import. The real-data supplant run is reported in the result (the dashboard G5 wires the live incumbents).

## Close Criteria
- `tyre_supplant.py` imports NO evo-region package (AST-verify).
- `build_truth_cells` returns per-(race,compound) lap-time deg-slope + lap-count weight from clean green laps; pure scoring core uses the neutral metric unchanged.
- Physics prediction = per-(race,compound) measured lateral_k (primary) + LOO season-pooled variant.
- Incumbents are INJECTED arrays (no evo import in this module).
- `classify_axis_verdict` → per-axis GO/CONTEXTUAL/NO-GO; 2σ reference not gate.
- LOO/out-of-sample for any self-weighted diagnostic.
- Unit tests green; `simplification_limits --paths` clean; no W2/quali/store/G3 mutation.

## Allowed Scope
`src/physics/layer2/tyre_supplant.py` (new), `tests/unit/physics/layer2/test_tyre_supplant.py` (new). Read-only: `lap_times` (per-year DB), `race_stint_estimates` store, `tyre_separation` (G3), `src/common/pairwise_ordering`.

## Specific Exclusions
No evo import. No #443 empirical magnitudes in the physics prediction. No modification of W2/quali/store/G3/pooling/common modules. No committed .db.

## Constraints
- `constraint:physics_region_no_evo_import` — incumbents INJECTED, not imported.
- Neutral metric only (`src/common/pairwise_ordering`). Anti-circular. LOO for self-weighted diagnostics. 2σ reference not gate. `py` not `python`.

## Verified Seams (re-verify from source)
- `src/common/pairwise_ordering.pairwise_ordering_accuracy(cells_df, predicted, truth_col, weight_col, race_col="race") -> float`. Within-race pairwise ordering accuracy, weighted by min(weight). Skips tied/NaN pairs; returns nan if no pairs. The truth ordering and predicted ordering are compared by sign — so for DEGRADATION, ensure predicted and truth are in the SAME direction (more degradation = larger value for both).
- `race_stint_estimates`: `RaceStintStore(db_path)` opens write-mode (CREATE TABLE IF NOT EXISTS) — to read read-only, mirror G3's `file:…?mode=ro` SELECT helper (or reuse `tyre_separation.load_stores_ro` / `_read_ro`). Columns: `lateral_k, lateral_k_sigma, compound, gp_name, driver, fit_status, lateral_g0`. Canonical DB `C:/Programs/f1Brainz/data/race_stint_estimates.db`.
- `lap_times` (per-year DB `C:/Programs/f1Brainz/data/f1_data_2023.db`, sessions.session_type='R'): columns `lap_number, compound, lap_time, tyre_life, stint_id, valid_lap, track_status, pit_in_time, pit_out_time, driver_id, session_id, compound_c_number`. (`compound_c_number` is a DB integer — reading it is NOT an evo import; it is the substrate the dashboard's absolute-C# incumbent uses.) Clean-lap filter mirrors `session_race._is_clean`: `valid_lap=1 AND pit_in_time IS NULL AND pit_out_time IS NULL AND track_status='1'`.
- G3 `src/physics/layer2/tyre_separation.py`: READ IT for the exact API — `separate_axis(race_df, quali_df, axis, *, prior=None) -> AxisSeparation`, `load_stores_ro(race_db_path, quali_db_path, year=2023)`, plus `separate_all`/`summarize` (per the G3 result). `CompoundEffect`/`AxisSeparation` carry per-compound pooled k + sigma. Use these for the season-pooled-k LOO variant and the separability input to the verdict.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `tyre_supplant.py` (new); `struct:common` — `pairwise_ordering.py` (neutral).
- **Constraints:** `constraint:physics_region_no_evo_import`; anti-circular (#443 circular-target trap); `lesson:loo-residual-diagnostic`.
- **Decision:** `decision:regime_readiness_rubric` (#512). Decision pressure (candidate): the neutral-boundary INJECTION pattern for physics-vs-evo supplant comparison.
- **Evidence:** #443 LOO P=0.8032 cross-check bar; neutral within-race P; magnitude R²; honest covariance overlap.

## Required Evidence
1. Unit tests green (paste): truth-cell recovery, P ordering (matched high / reversed low), verdict branches, evo-free.
2. evo-free assertion (paste).
3. `simplification_limits --paths` clean (paste).
4. Real-data supplant report (paste): physics per-(race,compound) k → within-race P vs truth; LOO season-pooled-k P; magnitude R²; the truth-cell summary (n races, n cells). (The LIVE incumbent comparison is wired in G5; here, demonstrate the scoring core on physics + a synthetic/placeholder incumbent so the pipeline is proven end-to-end.)

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_tyre_supplant.py -q
py -m src.utils.simplification_limits --paths src/physics/layer2/tyre_supplant.py tests/unit/physics/layer2/test_tyre_supplant.py
```

## Suggested Model Tier
Stronger (Opus-class) — anti-circular truth/feature independence + LOO + verdict rubric.

## Authority
Commander decided: neutral pairwise-P metric, truth=lap-time slope (independent channel), physics=measured-k (anti-circular), incumbents INJECTED (evo-free module), LOO for self-weighted, 2σ reference not gate, judge degradation not finish-ranking. You own: cell-construction mechanics, the R²/overlap details, verdict thresholds, test fixtures. Do NOT decide to import evo, bake #443 magnitudes, judge finish-ranking, or widen scope. If the supplant DESIGN needs a material reshape (e.g. the truth channel or the prediction target must change to be meaningful), STOP and return it — the commander floats a material supplant reshape to the Admiral.

## Stop Conditions
Stop and return if: a meaningful supplant requires importing evo into this module; the truth channel cannot be made independent of the physics feature (circular); the design needs a material reshape; a W2/quali/store/G3 module must be modified.

## Return Format
IMPLEMENTER_RESULT to `C:/Programs/f1Brainz-511/.agent-work/511/crew-handoffs/g4-implementer-result.md`: completed slice, files changed, test mode satisfied, the 4 evidence blocks, the supplant finding (physics P vs the placeholder incumbent + LOO P; does physics carry real degradation-ordering signal?), assumptions, stop conditions, out-of-scope observations, Workflow Feedback.
