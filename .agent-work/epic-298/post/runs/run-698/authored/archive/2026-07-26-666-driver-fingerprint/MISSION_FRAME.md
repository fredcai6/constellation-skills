# Mission Frame — #666 DriverFingerprint

## Intent
Add a NEW physics-region package `src/physics/fingerprint/`: a versioned driver-fingerprint cell store
(own DB, #632) + a hierarchical Student-t shrinkage fit over #664's `driver_class_observables`, both
channels, strictly-pre. Consume `fit_two_way` (driver×class) + the canonical `predictive_t` seam. Run
bounded (offline 3–4 circuit 2023-Q slice). Diagnosis-first: resolve #675's class-axis coverage before
freezing the fit's class-interval design.

## Affected Capabilities
- `capability: per-regime driver utilization` (#510/#628 c1-driver-utilization) — the fingerprint is a
  new downstream consumer of the class-grain observables; must inherit `strictly_pre` causal discipline.
- New capability: per-(driver, rules-era) class-cell fingerprint with honest heavy-tailed σ.

## Structural Anchors
- `struct:physics.layer2` — `pooling.fit_two_way` (driver×class), `pooling.pool_random_effects`
  (`shared_floor`), `pool_driver._shared_floor_for_param` (median pattern), `frozen_constants` (#660).
- `struct:physics.utilization` — `reference_utilization_store.driver_class_observables` (#664 fit input).
- `struct:common` — `student_t.predictive_t` / `PredictiveT` / `FormulaRule` (mandated seam; ν=4.0).
- `struct:physics.segment_map` — `VocabularyRef` / `SegmentMap.class_ids` (k=4 severity vocabulary);
  `RegulationEra.for_season` (era key seam).
- NEW: `struct:physics.fingerprint` — `address.py` (CellAddress/cell_key), `vocabulary.py`
  (ClassVocabulary + F12 verdict), `store.py` (versioned cell store), `fit.py` (hierarchical shrinkage).

## Governing Constraints / Assumptions
- `constraint: DB-canonical` — fit input is the observables DB, never live FastF1 (build script is offline).
- `constraint: as-of cutoff` — `as_of_round` REQUIRED, no default; no silent latest fallback (planning invariant).
- `constraint: no race-outcome leakage` (pre-quali ruling).
- `constraint: frozen constants F12` — new thresholds pre-registered as a named FLOAT set before first real fit.
- `constraint: physics/evo boundary` — fingerprint stays in physics region; no evo coupling.
- `constraint: DB-BLOB guard` (#632/#656) — own DB, never commit data blobs, tests use temp DBs.
- `assumption: g_sigma_onesided=0.0` while grip store empty → byte-identical-point invariant under G σ⁺=0.

## Decision Anchors & Decision Pressure
- `decision:pooled_sigma_shared_systematic_floor` (#627) — `shared_floor` is an additive quadrature σ floor
  after shrinkage; the ready-made #675 class-axis lever.
  `@grade: settled/measured · leans g1-diagnose,g3-fit`
- `decision:c1_driver_utilization_design` (#628 ext) — `strictly_pre` is load-bearing; 14.6× leakage
  materiality precedent; the cutoff-leakage keystone test cites it.
  `@grade: settled/measured · leans g3-fit`
- Design-it-twice (CALLER/FLEX/MINIMAL hybrid) — SETTLED in spec, do NOT re-open.
  `@grade: settled/inherited · leans g2-store`
- `decision:fingerprint-era-key` — era dimension derived from `RegulationEra.for_season(season)` as a stable
  string; braking_zone/straight excluded → exactly k=4 severity cells.
  `@grade: guess · leans g2-store · settle: confirm against 'exactly k cells' + observables class set`
- Decision pressure (candidate): the new frozen constant set's names/values (coverage level, under-coverage
  bound, recency half-life, thin-support n floor) — pre-registered at g1 before the first real fit.

## Claims / Evidence Surfaces
- `claim: cutoff-leakage` — `as_of_round=R` fit sees no `round_idx>R` row (g3 keystone test).
- `claim: sigma-priced-once` — thin-cell σ-widening idempotent (g3 test).
- `claim: loud-refusal` — era/vocab mismatch + failed-gate vocab refuse loudly (g2 test).
- `claim: k-cells-populated` — exactly k cells, `unresolved` not missing (g2 test).
- `claim: #675-coverage` — real driver×class class-axis coverage measured; recommendation recorded (g1→g4).
- `claim: G-byte-identical` — G σ⁺=0 leaves point value unchanged (g3 test).

## Map Confidence / Staleness / Disputes
- `ClassVocabulary` + F12-verdict field — NET-NEW (map has no node); building it, not trusting a stale one.
- `sigma_lapsampling` / `g_sigma_onesided` — DORMANT/zero in current data; verified, not assumed.

## Out of Scope
Join #668; race-side push/managed cells (Build 2); low-rank factorization; G μ off 0 (#678); grip-store
populate (#692); full-season run (#670/HITL); any k/vocabulary change (#642). #560 = prose reconciliation only.
