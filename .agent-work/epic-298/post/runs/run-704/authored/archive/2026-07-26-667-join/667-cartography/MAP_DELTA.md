# Map delta — #667 the join (for the epic #659 CLOSEOUT cartographer reconcile)

**Map FENCE respected:** no `docs/architecture/*` edits made this run (per LAUNCH_ORDER-667). This
delta is staged for the single epic-closeout cartographer reconcile, alongside the sibling
#660–#666 deltas.

## New structure (physics region)
- **NEW leaf module** `src/physics/fingerprint/join.py`
  - `join_weekend_prior(composition: Mapping[str,float], cells: Sequence[FingerprintCell],
    vocabulary: ClassVocabulary, *, as_of_round, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule(),
    map_version=None) -> WeekendUtilizationPrior` — a PURE function.
  - `WeekendUtilizationPrior` frozen dataclass (driver, channel, prior: PredictiveT|None, mean,
    corner_share, class_ids, weights, resolved_mask, thin_classes, weight_on_thin, as_of_round,
    vocabulary_version, map_version, share_provenance="time").
- **NEW** `scripts/join_bounded_validation_667.py` (season-capable offline validation harness).
- **NEW** `tests/unit/physics/fingerprint/test_join.py` (18 tests — the T7 correctness gate) +
  `tests/unit/physics/fingerprint/test_join_bounded_validation.py` (synthetic smoke + skip-if-absent).

## New capability node
- `weekend-utilization-prior` — composes the #664 circuit per-class corner TIME-share composition
  (`reference_laps` field-reference `fingerprint`/`class_ids`) with the #666 driver
  `DriverFingerprintStore` cells into a per-weekend, quali-side Student-t utilization prior, for both
  channels (utilization + energy). The join is a **normalized weighted average** over the k severity
  classes (weights = comp/Σcomp; corner_share = Σcomp, NOT renormalized to 1.0), with honest
  quadrature σ propagation (thin/unresolved cells fatten, never cap, the tail).

## Edges (import-level)
- `join.py` imports (types/functions only, PURE — no DB/FastF1): `src.common.student_t`
  (predictive_t, PredictiveT, FormulaRule, TailRule, DEFAULT_NU_LOSS, NU_FLOOR),
  `src.physics.fingerprint.store` (FingerprintCell — value-object type), `src.physics.fingerprint.vocabulary`
  (ClassVocabulary).
- `scripts/join_bounded_validation_667.py` imports `fit_driver_fingerprints`, `DriverFingerprintStore`,
  `ReferenceUtilizationStore`, `join_weekend_prior`, `ClassVocabulary`/`era_key`.

## Consumer boundary (decision to record)
- `decision:join-consumer-boundary` — the join is reserved for the **practice-update + fusion
  summaries**; the **race simulator and the #668 instrument panel read UN-AGGREGATED cells directly**
  (the cell store's direct-read API is untouched). @grade: settled/inherited (LAUNCH_ORDER-667).
- `decision:join-is-normalized-weighted-average` @grade: settled/inherited (DESIGN_SPEC line 132 + T7).

## Structural findings for the map (from the build)
- `reference_laps.map_version` is **per-circuit** (`2023-Great Britain-Q:v1`); the fingerprint fit is
  therefore season-wide (`map_version=None`, pools all circuits ≤ as_of_round) and only the
  composition is per-circuit — the join re-weights season-pooled capability cells by each circuit's
  corner-severity mix. This is the intended per-weekend prior shape.
- The fingerprint store records **no per-cell fit cutoff**; the join carries `as_of_round` for
  provenance but cannot independently re-verify a cell's strictly-pre status (triage candidate #3).

## physics.md packet note
The physics.md packet predates the #660–#666 fingerprint subtree; `join.py` is another new leaf to
fold in at the epic-closeout reconcile. No content in the packet is contradicted by this run.
