# Mission Frame — #668 Instrument Panel

Map-first frame. New instrument family over the epic-659 Build-1 substrate; the map carries
the consumed inputs but nothing yet for the panel itself (a new component).

## Intent
Add a **read-only diagnostic instrument panel** (new component under `src/physics/`) that SIZES
the driver-utilization signal on the GB-2023-Q slice via four fixed instruments, consuming the
already-built #660/#664/#666 substrate and the already-frozen constants, minting only the
pre-registered `REPLICATION_*` frozen set. No change to any existing producer; no gate on Build 2/3.

## Affected Capabilities
- **driver-utilization measurement** (`src/physics/utilization/`, `src/physics/fingerprint/`) —
  the panel READS its outputs (reference laps #664, fingerprint cells #666), never mutates them.
- **frozen-constant discipline (F12)** — the panel EXTENDS `src/physics/layer2/frozen_constants.py`
  with the deferred `REPLICATION_*` named set (owner-signature gated).
- **composed-sector validation** — new: segment predictions → FIA sector sums vs on-disk official
  sector times (`data/f1_data_2023.db` `lap_times`).

## Structural Anchors
- `struct: src/physics/fingerprint/store.py` — `DriverFingerprintStore.get_fingerprint` (un-aggregated cell read API), file-level.
- `struct: src/physics/fingerprint/fit.py` — hierarchical Student-t fit; the golf-correction reasons about its additive pool.
- `struct: src/physics/utilization/reference_lap_product.py` + `reference_utilization_store.py` — car-reference (`reference_laps`) + `driver_class_observables` table (un-aggregated substrate).
- `struct: src/physics/layer2/pooling.py` — `TwoWayPool` (additive, no interaction) / `fit_two_way` / `pool_random_effects`.
- `struct: src/common/student_t.py` — `predictive_t` / `PredictiveT.interval` / `.cdf` (non-Gaussian coverage seam).
- `struct: src/physics/layer2/frozen_constants.py` — #660 set (consume scorecard triple; append REPLICATION_* here).
- `struct: src/physics/fingerprint/frozen_constants.py` — #666 set (consume coverage level/floor).
- `struct: src/physics/segment_map/derivation/sector_nesting.py` — distance→FIA-sector-line mapping (offline).
- `struct: src/data/database/` — `DatabaseManager.get_lap_times` (official sector times).
- NEW: `struct: src/physics/instrument_panel/` (proposed new package for the four instruments + report).

## Governing Constraints / Assumptions
- **constraint:db-only** — no FastF1/online; all reads from on-disk DBs/stores.
- **constraint:own-db (#632)** — any new artifact writes its own path, NEVER an `f1_data_*.db`.
- **constraint:strictly-pre (#666 crown invariant 1)** — cells read as-of `as_of_round`; no sector-outcome leakback into predictions being scored.
- **constraint:no-inline-literals** — consume #660/#666 frozen constants; mint only the pre-registered REPLICATION_* set.
- **constraint:lowest-dimensionality (owner ruling 4)** — EXACTLY four instruments; no interaction terms, no bespoke model.
- **constraint:no-baked-normality (owner ruling 5)** — Student-t coverage throughout.
- **constraint:no-frame-kill (owner ruling 1)** — the panel sizes; a small/zero size is a complete result.
- **assumption:bounded-slice** — GB-2023-Q is one session; cross-session split-half is unavailable → within-session lap split (registered in F12).

## Decision Anchors & Decision Pressure
- decision:c1-driver-utilization-design (`docs/architecture/decisions/c1-driver-utilization-design.md`) — the anti-circular absolute time-deficit + strictly-pre causal ceiling that the panel's inputs obey.
  @grade: settled/inherited · leans g2,g3,g5
- decision:replication-deferred (#660 module) — REPLICATION_* set deferred to this panel, owner-signature gated.
  @grade: settled/human · leans g1,g3
- decision:golf-correction-is-per-driver-demean — remove overall skill by subtracting each driver's own mean across its k classes before replicating the per-class residual (justified by the additive no-interaction pool).
  @grade: guess · leans g3 · settle: cold-critic review of correctness + synthetic recovery (skill-only signal must replicate at ~0 after correction)
- decision pressure (→ F12 float): the `REPLICATION_THRESHOLD` value, the `r_floor(n)` support-scaling formula, `REPLICATION_MIN_SUPPORT_N`, the channel-comparison decision rule + tie margin, and the within-session split-half unit — ALL surfaced to the Admiral/owner for signature before the real-data run.

## Claims / Evidence Surfaces
- claim:golf-correction-removes-skill — a synthetic signal that is PURE overall skill (no class shape) must replicate at ~0 after correction; a synthetic per-class shape must replicate at ~its injected strength. Verified by synthetic tests (reuse #665 generative model).
- claim:coverage-is-distribution-not-gaussian — σ-honesty + scorecard coverage computed via `predictive_t.interval`/`.cdf`, not ±1.96σ. Verified by test asserting heavy-tail path is exercised.
- claim:no-leakback — the scorecard's predicted sectors are built from strictly-pre inputs; official sector times enter only as the post-hoc comparison target. Verified by review + an as-of-threading test.
- claim:position-sum-construction — segment predictions sum EXACTLY to the composed FIA sector (a construction identity). Verified by an exact-sum test.

## Map Confidence / Staleness / Disputes
- The panel component is NEW — no existing map node; reconcile adds it at closeout (map fence: stage `notes-668.md` + `668-cartography/`, do not touch `docs/architecture/*`).
- `driver_class_observables` GB-2023-Q slice population: confirmed 64 cells (16×4) in the #675 slice DB; **single session** — verified, drives the within-session split-half decision.

## Out of Scope
Any Build-2/3 halting gate; full season run (#670); correlation-aware σ (#700); fit-cutoff (#701);
G μ-off-zero (#678); 3-circuit regeneration (#670); mutating any #660/#664/#666 producer.
