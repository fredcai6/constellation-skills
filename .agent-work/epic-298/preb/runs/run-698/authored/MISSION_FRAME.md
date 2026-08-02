# Mission Frame — issue #698 (cmdr-698)

Authored map-first from `docs/architecture/index.md`, `docs/architecture/packets/physics.md`
(`struct:physics.fingerprint`), and `docs/architecture/overlays/{purposes,constraints}.yml`, before
authoring `execute.json`.

**Not shrunk.** H2/H3 alone would be trivial-mechanical and would justify skipping the frame, but H1 retypes
the public signature of a keystone state store that three production call sites and ~44 tests bind to — an
architecture-boundary change under `ORCHESTRATOR_CONTEXT.md`'s evidence table. The map is required.

## Intent

Close the **read-side address-validation asymmetry** on `struct:physics.fingerprint`'s store boundary by
typing all three store entry points on a validated address value object, with **zero observable change** to
the store's four invariants or to any fit/coverage number; and repair two artifact-hygiene defects on the
`scripts/` edge of the same component. `purpose:weekend_utilization_prior` behaves identically before and
after — this run changes *what the boundary refuses*, never *what it computes*.

## Affected Capabilities

- **`purpose:weekend_utilization_prior`** — served by `struct:physics.fingerprint`
  (`overlays/purposes.yml:128-132`). Today: stage G fits driver cells into the store; stage H composes them
  with #664's field-reference into the per-weekend Student-t prior. This run touches only the *addressing* of
  the G↔store boundary. **The prior's values must not move.**
- **`purpose:pilot_orchestration`** — served by `struct:physics.pilot`. Consumes the store at two call sites
  (`pilot/pipeline.py:257`, `:325`); both migrate to the new address object. No orchestration semantics change.

## Examples / Events

- **The defect, concretely:** `store.get_fingerprint("", era, vocab, "utilization", "deficit")` returns
  exactly k `status="unresolved"` cells today — a well-formed-looking answer to a malformed question,
  indistinguishable from a legitimately not-yet-fitted driver. Same for `driver="VER|X"` (a driver code
  carrying the reserved `cell_key` delimiter). After this run both raise at address construction.
- **The edge that must NOT change:** `get_fingerprint` for a *legitimately absent* driver still returns k
  unresolved cells. The miss-synthesis path (`store.py:277-285`) is an invariant, not a bug.
- **The edge that must stay refused:** `era != vocabulary.rules_era` still raises
  `EraVocabularyMismatchError`. The convenience constructor derives `era` from the vocabulary and so cannot
  produce a mismatch — that dissolves the failure class for well-behaved callers — but the explicit
  constructor and the guard both remain, guard-tested.
- **H2's failure event:** a bare `py scripts/fingerprint_class_coverage_675.py` inside a worktree resolves
  `from src.physics... import` against the MAIN checkout via the editable finder — silently wrong module, or
  `ModuleNotFoundError` when the module is unmerged there.
- **H3's failure event:** the same bare run `mkdir -p`s and writes
  `<cwd>/.agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json` — resurrecting a work area
  that was archived on 2026-07-26, at an un-ignored path inside a tracked tree.

## Structural Anchors

- **`struct:physics.fingerprint`** — `src/physics/fingerprint/`, component. Primary landing zone.
  - `address.py` — `CellAddress`, `CELL_KEY_DELIMITER`, `FINGERPRINT_CHANNELS`, `DEFAULT_WHAT_MEASURE`,
    `RESERVED_WHAT_MEASURES`. Gains `SlotAddress`; `CellAddress` re-expressed as slot + `class_id`.
  - `store.py` — `DriverFingerprintStore` (`write_fingerprint`, `get_fingerprint`, `row_count`). The retyped
    boundary.
  - `fit.py` — `fit_driver_fingerprints`, the only production writer (`:356`).
- **`struct:physics.pilot`** — `src/physics/pilot/pipeline.py`, the two production readers.
- **Non-map script nodes:** `scripts/fingerprint_class_coverage_675.py` (H2 + H3),
  `scripts/fingerprint_bounded_validation.py:124`, `scripts/join_bounded_validation_667.py:173` (call-site
  migration only).
- **Test surface:** `tests/unit/physics/fingerprint/{test_address,test_store,test_fit,test_bounded_validation}.py`.

## Governing Constraints / Assumptions

- **`constraint:physics_region_no_evo_import`** — `constraints.yml:293-297`; evidence line asserts no
  `src.evo_predictor` / `src.latent_power` / `src.compound_prior` import anywhere under
  `src/physics/fingerprint/`. A new `address.py` symbol must not reach across regions. Trivially satisfied by
  the planned change, but re-confirmed as gate evidence.
- **No fit-on-read** — `store.py` must continue to import nothing from a fit/pooling/observables module. The
  new value object lives in `address.py`, which `store.py` already imports; no new dependency direction.
- **Assumption (verified, not inherited):** the editable install's finder is **appended** to `sys.meta_path`,
  so a `sys.path.insert(0, repo_root)` guard wins. Verified by reading
  `site-packages/__editable___f1brainz_0_2_0_finder.py`'s `install()`. Had it inserted at position 0, H2's
  prescribed fix would have been inert.
- **Assumption (verified):** `.agent-work/` is **tracked**; only `*.pkl` / `*.npz` / `*.db` / `scratch/` /
  `ckpt/` / `backtests/` and four named legacy subpaths are ignored under it. Archived work-area JSONs are
  committed evidence by convention.
- Project rules in force: *"Prefer one clear execution path over compatibility shims"*; *"Validate public and
  meaningful internal inputs with failure messages naming field, expectation, and actual value"* (the new
  validation must name the field — `CellAddress.__post_init__` already does, and the shared validator
  inherits that shape); `py -m src.utils.simplification_limits` strict on every touched path.

## Decision Anchors & Decision Pressure

Existing anchors on this structure (`packets/physics.md:2722-2733`) — all inherited, none revised here:

- `decision:join-consumer-boundary` — the race sim and the #668 panel read un-aggregated cells directly, not
  the aggregated join.
  `@grade: settled/inherited`
- `decision:join-is-normalized-weighted-average`.
  `@grade: settled/inherited`
- `decision:fingerprint-era-key` — the era key partitions cells by regulation era; not a raw season int.
  `@grade: guess · leans g1-address · settle: none needed this run — the slot object carries era as an opaque validated string and does not touch how the key is derived`

New anchor this run **records** (durable-structure choice, surfaced as a decision candidate for reconcile):

- `decision:fingerprint-slot-vs-cell-address` — the store's read/write surface addresses a **slot** of k cells,
  not a single cell; `SlotAddress` is the five-field identity and `CellAddress` is slot + `class_id`. This is
  what makes the k-cells-always-populated invariant expressible in the type rather than only in prose.
  `@grade: guess/reasoned · leans g1-address · settle: g3 review confirms every store call site reads more naturally and no caller wanted a single-cell read`

**Decision pressure** (choices this run forces, carried to `triage` / the reconcile candidate pool — no grade,
not yet anchors):

- Whether the read path should eventually refuse a **reserved** `what_measure` as the write path does. Ruled
  out of scope here (behaviour change); routed to triage.
- Whether the repo should enforce the `scripts/` `sys.path` convention mechanically (51 scripts non-compliant).
  Routed to triage as a lint/CI candidate.

## Claims / Evidence Surfaces

- **`claim:instrument_panel_reads_cells_directly`** — packet asserts `instrument_panel` reads
  `fingerprint.store.get_fingerprint` cells directly. **Re-confirm and correct at reconcile:** no store import
  exists under `src/physics/instrument_panel/`; the call lives in `src/physics/pilot/pipeline.py:325`. The edge
  is real, the attribution is imprecise. Does not alter the plan.
- **Store invariant claims** — the four invariants at `store.py:10-32`, backed by `test_store.py`'s five guard
  classes (`TestKCellsAlwaysPopulated`, `TestIdempotencyAndReplaceOnRerun`, `TestLoudRefusal`,
  `TestNoFitOnRead`, `TestFormatVersionAndMustExist`). **Every gate touching the store must re-run these
  unchanged** — the consumed-frozen-module lesson, which is exactly about extending a ratified module and
  verifying only your own new tests.
- **Region constraint evidence** — `constraints.yml:297`'s no-evo-import line, re-confirmed by grep.
- **Numeric no-op evidence** — `test_fit.py` + `test_bounded_validation.py` are the fit-value guard; they must
  pass **byte-identically in verdict**, since the issue forbids any fit/coverage behaviour change.

## Map Confidence / Staleness / Disputes

- `struct:physics.fingerprint` — **confidence: high**, `status: current`, dated 2026-07-27. Trustworthy; **no
  scout gate needed**.
- `claim:instrument_panel_reads_cells_directly` — **imprecise, not stale**: the reading component is named
  wrongly (pilot, not instrument_panel). Recorded above for reconcile; it does not touch the gate plan because
  both candidate call sites are in the migration set either way.
- No low-confidence, partial, or disputed area is load-bearing for this run.

## Out of Scope

- Any change to fit numerics, the coverage method, `frozen_constants.py`, or the store's on-disk schema /
  `FORMAT_VERSION`.
- Read-side refusal of a **reserved** `what_measure` (behaviour change → triage).
- The other 50 `scripts/*.py` missing a `sys.path` guard (→ triage, wants a lint/CI check).
- cmdr-666 `tc4` — the vocabulary-drift migrate/purge API gap on the same surface.
- `join.py`, `vocabulary.py`, the #667 join, the #668 panel, and everything outside the physics region.
- `.gitignore` rules beyond the one narrow live-artifact path (no blanket `*.json` rule).
