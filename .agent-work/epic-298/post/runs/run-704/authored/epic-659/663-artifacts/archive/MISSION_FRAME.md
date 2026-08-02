# Mission Frame — #663 Grip baseline module G

## Intent
Build ONE canonical `src/physics/layer2/{grip_baseline.py,grip_store.py,grip_batch.py}` module owning per-weekend/per-session track grip state — an intra-session saturating curve indexed on field-wide cumulative_track_laps plus a free per-session offset — fit from field-pooled pace with tyre_supplant-style compound/tyre-age/fuel correction, Student-t residuals, propagated sigma. Deliver the two GATING acceptance tests (held-out reconciliation on a disjoint driver/lap remainder; synthetic curve+offset recoverability/separability) as real, run evidence, scoped to a representative slice of 2023 sessions (not necessarily the full 22-event season, per Budget latitude).

## Affected Capabilities
- New capability: per-weekend/per-session grip-baseline estimation + query surface (does not exist yet — this run creates it).
- `struct:physics.layer2` (existing component) — G is a new sibling module inside this component, following its estimate-store convention; no existing layer2 module is modified except where a session_type filter is generalized (see Structural Anchors).

## Examples / Events
- A 2023 FP2 session with 20 drivers, several stints per driver on 2-3 dry compounds: G fits one field-pooled saturating curve over that session's cumulative_track_laps plus that session's free offset.
- A rain-flagged session (if present in 2023 slice): G's offset re-estimation widens sigma rather than reusing a dry-session prior.
- A Q session (median 2 laps/stint, single compound in 17/22 2023 events): G falls into the wide-sigma thin-session fallback, still producing a (wide-sigma) offset via within-weekend nearest-neighbor extrapolation rather than a NULL.

## Structural Anchors
- `struct:physics.layer2` — `src/physics/layer2/`, component level. New files: `grip_baseline.py` (fit), `grip_store.py` (artifact + query surface), `grip_batch.py` (batch driver). Read-only reuse (no modification): `session_race.py:268` `compute_cumulative_track_laps` (counting convention reused, vectorized per-session), `tyre_supplant.py` (`_read_clean_race_laps`'s hardcoded `session_type='R'` filter is the actual parameterization site — it feeds `race_degradation_slopes` a pre-filtered DataFrame, so the OLS design in `race_degradation_slopes` itself is unchanged and reused as-is), `src/common/student_t.py` `predictive_t` (Student-t seam, unmodified).
- Peer (untouched): `src/physics/layer2/tyre_separation.py` (`g_track`) — confirmed structurally distinct (per-circuit linear slope, cross-season pooled, race-side decay-separation nuisance term) per `docs/architecture/decisions/tyre-age-g-track-design.md`. Not touched this build; reconciliation filed as a triage candidate.

## Governing Constraints / Assumptions
- `constraint:db-only-analysis` — SQLite is the only source; no live FastF1/Jolpica. G's fit reads `data/f1_data_2023.db` (`sessions`, `lap_times`) exclusively.
- `constraint:no-grip-into-segmentmap` (pre-ruling) — SegmentMap has zero `src/` implementation yet; trivially satisfied — G writes nowhere near it.
- `assumption:student-t-residuals` — project standing principle (no-baked-normality); G's residual model must use `predictive_t`, not a Gaussian.
- `assumption:additive-only-migration` — the estimate-store convention (`_migrate_missing_columns`) never drops/renames columns; G's store follows the same convention.

## Decision Anchors & Decision Pressure
- decision:held-out-not-in-sample — Gate 1 is held-out reconciliation on a disjoint driver/lap remainder; in-sample self-scoring rejected.
  @grade: settled/human · leans g4-implement,g4-review
- decision:synthetic-identifiability — Gate 2 is synthetic curve+offset recovery, must separate.
  @grade: settled/human · leans g5-implement,g5-review
- decision:no-baked-normality — Student-t residuals wherever feasible.
  @grade: settled/human · leans g2-implement
- decision:thin-session-explicit — chosen rule = wide-sigma fallback (floor: >=2 stints of >=4 laps, reusing `MIN_STINT_LAPS`), never silent skip. Resolved at `understand` (interrogation q3), grounded in real 2023 stint-thinness measurement.
  @grade: settled/measured · leans g2-implement · settle: already measured (2023 DB stint-thinness scan)
- decision:no-grip-into-segmentmap — G owns grip; nothing writes into SegmentMap.
  @grade: settled/human
- decision:session-scope-uniform — G's fit runs uniformly across all session types, generalizing tyre_supplant's hardcoded `session_type='R'` filter to a parameter; no blanket per-type exclusion. Resolved at `understand` (interrogation q2), in-latitude.
  @grade: settled/measured · leans g2-implement · settle: already measured (2023 DB per-session-type stint/compound structure)
- decision:heldout-split-axis — driver-based ~50/50 split, stratified by team where available. Resolved at `understand` (interrogation q4), in-latitude.
  @grade: guess · leans g4-implement · settle: run it on the real 2023 slice; if the split proves too coarse (e.g. team stratification skews fit/holdout compound coverage), fall back to plain random 50/50 with a fixed seed
- decision:synthetic-criterion — parameter recovery (>=90% of >=50 replicates within reported 2-sigma) + separability (curve/offset correlation <0.8 threshold). Resolved at `understand` (interrogation q5), in-latitude.
  @grade: guess · leans g5-implement · settle: run the synthetic harness; if the 0.8 correlation threshold proves too strict/loose against the actual fit's natural aliasing behavior, adjust with reasoning recorded before the gate closes (frozen-before-first-real-data-run applies to REAL data, not this synthetic calibration pass)
- decision pressure: G's artifact PK is `(year, gp_name, session_type)` — session-level, not per-constructor (field-pooled). This differs from `EstimateRecord`'s per-constructor PK and is worth flagging as a durable structural choice for Cartographer at reconcile. (Carried explicitly into g6-verdict's triage-candidate list — see execute.json.)

## Claims / Evidence Surfaces
- claim:cumulative-track-laps-reuse — G's intra-session x-axis reuses `compute_cumulative_track_laps`'s exact counting convention; each gate touching the fit re-confirms this by citing `session_race.py:268` in its evidence, not re-deriving the convention.
- claim:tyre-supplant-correction-reused — G's compound/tyre-age/fuel correction is `tyre_supplant.race_degradation_slopes`'s OLS design, generalized only in its session_type filter; g2's evidence must show the design (stint-ordinal FE + standardized fuel*lap_number + per-compound tyre_life slope) is unchanged, not reimplemented.

## Map Confidence / Staleness / Disputes
- `docs/architecture/packets/physics.md` documents `struct:physics.layer2` in depth and already names the `cumulative_track_laps` bridge gap G closes — high confidence, current.
- `src/physics/weekend_state/layer2_evolution.py` (the closest prior floated-not-landed attempt) is NOT touched this build — its "no bridge" Known Limit is closed by G's existence, but wiring layer2_evolution.py to consume G is out of scope (a future integration, not named in issue #663). Flag as a reconcile-time map note, not a plan gate.

## Out of Scope
- Per-class evolution curves (dormant escalation layer per issue).
- Writing grip state into SegmentMap (doesn't exist yet; pre-ruling).
- Reconciling/unifying with `tyre_separation.py`'s `g_track` (peer, untouched — triage candidate).
- Wiring G's output into any live consumer (`layer2_evolution.py`, `physics_data_models.LateralParameters`, `physics_simulator.py`, evo's `physics_feature_injection`) — issue #663 builds the module + its own acceptance gates only; consumer wiring is future work.
- Full 22-event 2023 season fit — Budget latitude allows a representative slice for the GATING evidence; full-season backfill is future work (mirrors the design spec's own Build-1 3-circuit-pilot-before-full-season phasing).
