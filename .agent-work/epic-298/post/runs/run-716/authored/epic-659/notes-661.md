# notes-661 — SegmentMap (epic #659 Build 1, manifest id B)

Commander: cmdr-661. Worktree: C:/Programs/f1brainz-wt/epic659-661, branch epic659/661-segmentmap.
Worktree isolation: `verify_worktree_isolation.py --here C:/Programs/f1brainz-wt/epic659-661` → `worktree OK: in C:/Programs/f1brainz-wt/epic659-661` (exit 0).

## Consolidated problem statement (reconciled against LAUNCH_ORDER-661 + `gh issue view 661`)

Build the **SegmentMap** module — the substrate every downstream consumer (derivation #662, the join, the MC sim) reads. FROZEN design = the design-it-twice three-way hybrid, NOT to be re-litigated:

- **Runtime = CALLER candidate.** Flat parallel numpy arrays (boundaries_m, length_m, int8 seg_type/sector/turn_direction codes, corner_descriptor (n,2), severity_membership (n,k)). Never a list of objects. `segment_of(distances)` = one `np.searchsorted` with wrap-modulo on the closed loop; out-of-range NEVER raises. MC sim fetches read-only arrays once → zero per-draw cost. `reclassify_severity(mixture)` recomputes membership O(n_corners) without touching geometry, and vice-versa.
- **Identity & persistence = FLEX candidate.** *Labels, never positions.* Memberships persist as tidy rows keyed by `vocabulary_id`/`class_id` strings minted once at fit time (`VocabularyRef` registry). Era refits / k-changes = pure inserts, no migration, no index-shift corruption. At load, labeled rows materialize into the caller-shaped positional matrix + a `class_ids` column map — conversion happens **exactly once per load**.
- **Version axes (Build 1, review S6):** weekend key; layout identity = content-hash of geometry-only cut points (EXCLUDING sector-forced splits); vocabulary fit version. Per-weekend supersede chain trivially v1 in batch mode; format version in the store convention.
- **Lifecycle = MINIMAL candidate, Build-1 phasing (review S3):** ONE deep write entry point carries the whole cold/seeded/superseded compare-and-branch in its *interface signature*, but **Build 1 implements the COLD/historical path only** (seeded/supersede branch = Build 3, interface unchanged now). Three narrow reads with distinct miss-contracts: `current` and `by-version` raise loudly; `latest-for-seeding` returns `None` on a genuine cold start. NO update/patch surface. Supersede requires a recorded contradiction reason. Provenance carries config fingerprint + FIA doc citations.
- **Convergent (adopted without debate):** adjacency computed, never persisted; sub-phases marks-only + dormant (`resolution="subphase"` reserved in the signature, backing store deferred; single-homed HERE, not duplicated in the fingerprint address space, per S5); no aggregate-statistics methods (rollups are consumer-side); NO grip state in the map (grip mutates per-session, map versions per-weekend); severity mixture consumed as a fitted input **behind a Protocol** so a Student-t swap never touches SegmentMap.

### Scope boundary (hard)
- IN: representation (runtime SegmentMap), labeled persistence, the versioned store, the `reclassify_severity` seam, the SeverityMixture Protocol.
- OUT (issue C/#662): the derivation logic itself — applying thresholds to real telemetry to produce geometry. Also OUT: any grip coupling, live seeding.
- Build-1 write entry point therefore accepts an **already-constructed** SegmentMap (geometry arrays supplied by the caller / #662 in production; by synthetic fixtures in Build-1 tests). It mints the vocabulary + labeled memberships from the injected severity mixture, validates, and persists as version 1 (cold path). The seeded/supersede branch is present in the signature but raises `NotImplementedError` (Build 3).

### Acceptance (4 named test areas)
1. `segment_of` searchsorted hot path — incl. wrap (straddle start/finish) and out-of-range (never raises).
2. load-boundary conversion round-trip (labeled rows → positional matrix + class_ids column map, once per load; geometry + membership reproduce).
3. label-stability under a simulated class REORDER — the corruption class this design exists to prevent: reordering mixture component indices must NOT corrupt persisted memberships (they are class_id-keyed, not positional).
4. read miss-contracts — current/by-version raise; latest returns None on cold start.

## Substrate consumed as-is (do NOT refit / no F12 gate here — pre-ruling build1-consumes-638-vocabulary)
- `src/physics/layer2/property_mixture.py` — `MixtureFit` (gmm, k, scaler, bic_scores), `fit_property_mixture`, `posterior_membership(fit, descriptors) -> (N,k)` over RAW `(radius_m, lateral_g)` (log transform encapsulated). k is support-driven (1..4).
- `src/physics/layer2/corner_descriptors.py` — `bin_row_to_descriptor(mu_lat_p90, v_mean) -> (radius_m, lateral_g)`.
- `src/physics/layer2/mixture_stability.py` — #638 F12 gate (validated class vocabulary); NOT run here.
- `src/physics/layer2/estimate_store.py` — SQLite store precedent: schema cols derived from a dataclass's fields, additive `_migrate_missing_columns` (PRAGMA table_info + ALTER ADD), JSON-blob columns, `mode=ro`/`must_exist` read guard, `INSERT OR REPLACE` upsert.

## Placement decision (within-latitude, physics-region-internal)
New package `src/physics/segment_map/` (top-level physics — a cross-cutting representation consumed by utilization + the MC sim, not a layer2 internal). Consumes `layer2.property_mixture` for the Protocol shape. NO evo import (constraint:physics_region_no_evo_import). This is an implementation/placement decision inside the frozen interface, not a cross-region boundary change → no float required.

### SeverityMixture Protocol (decision:severity-mixture-behind-protocol)
`property_mixture.MixtureFit` satisfies it structurally: needs `k: int`, a stable `version: str`, and `posterior_membership`-style query over `(N,2)` raw descriptors. Do NOT hard-import MixtureFit into SegmentMap — define a `Protocol` so a future Student-t swap never touches SegmentMap. Adapter that wraps a MixtureFit + a version tag lives at the write seam.

## Reconciliation verdict
No genuine gap requiring a float. The frozen hybrid is fully buildable from the three excursion RESULTs + the issue spec. All decision pressure (write-entry cold-only phasing, package placement, Protocol shape) is settled by the pre-rulings or falls inside inherited implementation latitude. Proceeding to plan.

## Plan (plan step)

Gate plan = 2 vertical crew gates (execute.json). Model tier for crews: Opus (load-bearing numpy hot path + label-stability correctness, per launch-order budget).
- **G1** — runtime representation + SeverityMixture Protocol (the hot path). Files: src/physics/segment_map/{__init__,protocols,runtime}.py + tests/unit/physics/segment_map/test_runtime.py. Acceptance: searchsorted hot path (wrap + out-of-range never raises), reclassify_severity (geometry untouched), construction invariants.
- **G2** — identity + labeled persistence + versioned store (cold path). Files: src/physics/segment_map/{identity,from_mixture,store}.py + __init__ exports + tests/unit/physics/segment_map/test_store.py. Acceptance: load round-trip (+once-per-load call-count), label-stability under class reorder, read miss-contracts, supersede-needs-reason + seeded-branch-NotImplemented, k-change pure-insert.

### Plan-alternatives (design-it-twice on the gate slicing — panel-vs-single: SINGLE + inline untaken roads)
The SegmentMap *interface* design-it-twice was already run and FROZEN (the caller/flex/min hybrid); only the build-slicing is a live plan choice, so a full parallel-author panel is disproportionate. Compared inline, converged to A:
- **A (chosen) — 2 vertical slices:** G1 runtime, G2 identity+persistence+store+load. Each gate is a tracer-bullet vertical slice that keeps the tree green and independently proves acceptance areas. Load-conversion stays WITH the write it round-trips against.
- **B (untaken) — 3 gates:** runtime / persistence-types+write / reads+load-conversion. Rejected: over-splits tightly-coupled write↔load (the round-trip needs both), buying a red window and an extra review for no locality gain.
- **C (untaken) — types vs behavior:** all dataclasses in G1, all behavior in G2. Rejected: separates types from their behavior, breaks locality, leaves G1 with no real test surface.
Untaken road (panel skip): a full parallel-subagent gate-plan authoring panel — skipped because the interface is frozen and only 2-3 viable slicings exist, comparable inline.

### Cold plan critic disposition (1 critic, bias-to-yes; findings all sharpenings, no rebuild — all folded into execute.json BEFORE freeze, within latitude as implementation refinements inside the frozen interface)
1. [SHOULD-FIX] G1 identity-object layering hazard → FIXED: G1 carries map identity as PRIMITIVE fields only + class_ids as a plain tuple field; no dependency on G2's VocabularyRef/MapVersion, no runtime↔identity cycle. G1 closes green standalone.
2. [SHOULD-FIX] once-per-load not falsifiable by round-trip → FIXED: conversion routed through one named helper; G2 test asserts call-count == 1 (spy/monkeypatch).
3. [SHOULD-FIX] label-stability reorder test can trivially pass; str(range(k)) class_ids collide across fits → FIXED: class_ids minted FULLY-QUALIFIED UNIQUE (taxonomy:era:vN:cI); load rebuilds column order from STORED class_ids not a live mixture; reorder test uses a distinct-vocabulary_id re-fit and must fail if the loader used positional order.
4. [SHOULD-FIX] MixtureFit→Protocol adapter orphaned (MixtureFit has no .version, membership is a module fn) → FIXED: G2 from_mixture.py ships a `MixtureFitAdapter` (the only place MixtureFit is imported); unit-tested to satisfy the Protocol; SegmentMap stays Protocol-only.
5. [NIT] reserve resolution="subphase" kw (G1); FORMAT_VERSION store constant (G2); k-change pure-insert regression test (G2) → all FOLDED in.

Delegated plan approval: satisfied by citing LAUNCH_ORDER:Mission (frozen plan + scope). No plan-invalidating discovery to float.

## Triage candidates (recommend-and-defer — Admiral files per Inherited Latitude)

1. **get_latest filter semantics (DECISION candidate → Build 3 #664).** The frozen MINIMAL spec says `get_latest` returns "the most recent non-historical map," which is self-inconsistent (Build-1 cold maps are `status="historical"`, so a literal exclusion makes the seed resolver dead). Implemented the FUNCTIONAL reading: exclude only superseded (`superseded_by IS NULL`), historical eligible, `None` on cold start — documented + positively tested. Real consumer (seeding) is Build 3. RECOMMENDATION: the Build-3 seeded/supersede gate (#664) confirms this filter semantics before wiring seeding; strict-literal would be a one-line WHERE change. @grade candidate (not yet ruled).
2. **Test-fixture duplication (cosmetic).** `_valid_kwargs()` fixture duplicated across `tests/unit/physics/segment_map/test_runtime.py` and `test_store.py`; a shared `conftest.py` would DRY it. Deferred rather than fixed-now to keep the reviewed+APPROVED test artifact frozen; trivial cleanup for a follow-on.
3. **SeverityMixture Protocol carries no semantic class labels (future design note).** The Protocol exposes only `k` + `version`, so `reclassify_severity` derives synthetic `class_ids` (`f"{version}:c{j}"`) and the store mints the aligned `f"{vocabulary_id}:c{i}"`. If a future consumer needs human-meaningful class labels (e.g. "fast_corner"), the Protocol needs a labels member. Not needed for Build 1; flag for the derivation/consumer gates (#662+).
4. **Map delta to fold** (not a debt issue — reconcile output). `struct:physics.segment_map` node + index catalog node + constraints.yml edge authored at `.agent-work/661-cartography/MAP_DELTA.md`; hand to the Admiral's closeout cartographer fold.
