# Map impact — #666 DriverFingerprint (staged for the epic-659 CLOSEOUT cartographer)

Map fence honored: this run did NOT touch `docs/architecture/*`. This prose is the input for the epic's single
closeout cartographer reconcile.

## New structural node
- **`struct:physics.fingerprint`** — a NEW package `src/physics/fingerprint/` (physics region, consumer of
  layer2 pooling + utilization observables + common student_t). Modules:
  - `frozen_constants.py` — `FINGERPRINT_FROZEN` pre-registered named set (nominal coverage 0.80,
    under-coverage bound 0.60, recency half-life 5.0 rounds, unresolved-support floor 1.0). New F12 frozen set.
  - `address.py` — `CellAddress` (driver, era, vocabulary_version, class_id, channel, what_measure) + a canonical
    always-non-NULL `cell_key` (SQLite NULL-PK fix). Dormant `channel` values (utilization/energy) + reserved
    what_measure slots (push/managed/consistency/management_efficiency) present-but-unused (ruling 4).
  - `vocabulary.py` — `ClassVocabulary` (vocabulary_id, rules_era, k, class_ids, **f12_verdict**, f12_provenance);
    `require_fittable()` refuses a non-PASS vocabulary by default; `era_key(season)` derived from
    `RegulationEra.for_season`. NEW type — the F12 stability verdict now has a first-class home (previously only in
    `scripts/f12_held_out_stability.py` output).
  - `store.py` — `DriverFingerprintStore` (own DB #632; table `driver_fingerprint_cells`, PK `cell_key NOT NULL`;
    INSERT OR REPLACE replace-on-rerun; k-cells-always-populated with `unresolved` status; loud
    `EraVocabularyMismatchError` refusals; **NO fit-on-read** structural — imports nothing from fit/pooling).
  - `fit.py` — `fit_driver_fingerprints(...)` slow-offline-loop hierarchical Student-t shrinkage
    (field→driver-overall→class cell + class-across-drivers parent, recency-weighted, both channels, **strictly-pre
    `as_of_round` required no default** over the ENTIRE input set). Consumes `fit_two_way` (driver×class) +
    `pool_random_effects.shared_floor` + `predictive_t`. σ priced ONCE at `_price_sigma_with_shared_floor`.

## New edges (import consumption — for the reverse-import scan)
- `physics.fingerprint.fit` → `physics.layer2.pooling` (`fit_two_way`, `pool_random_effects`), `common.student_t`
  (`predictive_t`, `FormulaRule`, `DEFAULT_NU_LOSS`), `physics.utilization.reference_utilization_store` schema
  (reads `driver_class_observables`), `physics.fingerprint.{store,vocabulary,address,frozen_constants}`.
- `physics.fingerprint.vocabulary` → `physics.regulation_era` (`RegulationEra.for_season`).
- NO edge fingerprint→evo (physics/evo boundary respected).

## Decision anchors touched (existing, not new)
- `decision:pooled_sigma_shared_systematic_floor` (#627) — reused as the class-axis `shared_floor` lever (#675).
- `decision:c1_driver_utilization_design` (#628 ext) — `strictly_pre` discipline inherited; 14.6× precedent cited
  in the cutoff-leakage keystone test.

## Candidate NEW decision anchor for the cartographer to consider recording
- `decision:fingerprint-era-key` — the fingerprint's era dimension is derived from `RegulationEra.for_season`'s
  flag signature (not raw season); k=4 corner-severity cells only (straight + braking_zone excluded).
  `@grade: guess` (settled within this build; a full-season run may refine the era-bucket granularity).

## Scope boundary (built season-capable, ran bounded)
The store + fit are season-capable; only a bounded offline 3–4 circuit 2023-Q slice was RUN (full season = #670/HITL).
No new capability node is promoted as production-live; this is foundational state-store machinery for the epic's
downstream join (#668) + Build-2 race-side cells.
