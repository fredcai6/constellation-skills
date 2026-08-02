# Wave 9 · #629 Verdict — Phase 5: as-of-stamped feature view

**Commander:** ShipJ-629 (delegated). **Worktree:** `C:/Programs/f1-629`, branch
`feat/629-feature-view`, base `main` `72577cef` (merged forward to `b97a58e1` before PR-open,
clean fast-forward, no conflicts). **Epic:** #601 physics-as-feature-engine.

## Summary

Built the Phase-5 product contract: a new sibling component `src/physics/feature_view/`
exposing four record types through one append-only store and one read API
(`read_feature_view`, the sole evo-facing surface). Packaging/plumbing over Phases 2-4's
already-built machinery — no new estimation/modeling landed in this run.

## The four record types + status handling

1. **`WeekendStateRecord`** (per event, session, car) — composed from `WeekendStateModel`'s
   fitted L1-L4 output (`build_weekend_state.py`). Per-axis `axis_status` is a REAL per-row,
   per-axis check (resolved iff both car_signal value and sigma are present), reusing
   `effective_axis_sigma`/`normalize_axis_status` for the explicit-unknown widening — never a
   blanket default.
2. **`CarBasisPosteriorRecord`** (per constructor, session) — composed from
   `EstimateStore` rows (`build_car_basis.py`); the 9-name `AXIS_STATUS_NAMES` fan out to the
   11 physical axes via a verified mapping table; `cross_view_covariance` is a faithful
   passthrough of Phase 3's already-fused terms (never re-derived — `fuse_dual_cda` is not
   imported). Session-chained over `SESSION_ORDER = (FP1, FP2, FP3, Q)` via `chain_position`/
   `prior_session` (nearest-present policy, explicit + tested). Two fields are EXPLICIT
   RESERVED SLOTS, `__post_init__`-guarded to always stay `None`: `process_noise_link` (no
   intra-weekend process-noise fit exists anywhere in the codebase — discovered mid-run, not
   pre-known) and `parc_ferme_step` (bounded-deferred per #513). **Both reserved per Admiral
   ruling** (2026-07-24): fitting either is new modeling, out of #629's packaging charter, same
   class as each other. Follow-on filed: **issue #654**.
3. **`LapEvidenceRecord`** (per driver, lap) — composed from `FpLapLatent` (mass/mode
   posteriors: mass_kg/mass_sigma_kg/run_purpose/compound, straight copies) +
   `fp_representativeness.observation_weight`/`observation_features` (the representativeness
   weight, computed via the real functions, never approximated). `unit_class_residuals` is an
   EXPLICIT RESERVED SLOT (`__post_init__`-guarded) — the real per-lap telemetry extractor
   (`fp_gate_real_extractor.RealGateExtractor`) is itself flagged G7-deferred/compute-deferred
   in the codebase; never fabricated.
4. **`FeatureViewRow`** (per event, car) — THE ONLY evo-facing surface. Composed
   (`build_feature_view.py`) from the primary `car_basis_posterior` source (most-recent-present
   session at-or-before the as-of cutoff) refined per-axis by a `weekend_state` row only where
   that row's own axis is genuinely resolved (never blanket-overwritten).
   `circuit_conditional_composite` is an EXPLICIT RESERVED SLOT (nothing in Phases 2-4 computes
   a circuit-conditional composite yet — the closest artifact, #512's regime-capability vector,
   was found circuit-conditional/fine-margin, not a clean composite to fold in). **Reserved
   transition-σ widening (Admiral ruling)**: `transition_axis_status` (new additive field) marks
   every axis `"unresolved"` and widens its sigma (flat, via
   `effective_axis_sigma(value, sigma, "unresolved")`, `max()`-guarded against narrowing) when
   `as_of_session != SESSION_ORDER[-1]` ("Q", the terminal/target session) — i.e. whenever the
   composite stands in for a not-yet-observed Q reading across the reserved `process_noise_link`.
   Deliberately flat/non-scaling (no hop-count or clock-distance term — that IS #654's future
   modeling work, per the Admiral's explicit "keep it simple" ruling).

Constructor-grain is a NAMED round-1 approximation (per-entry/two-car divergence banked, not
solved — documented in the module docstring, not silently assumed).

## Gate results (append-only + as-of-leakage, by construction)

- **Append-only**: every store table's natural key includes `model_version` (or
  `as_of_session` for the feature-view table) under a real SQLite `UNIQUE` constraint, enforced
  via plain `INSERT` (never `INSERT OR REPLACE` — a deliberate divergence from the existing
  `EstimateStore.upsert` idiom, called out explicitly). A duplicate-key write raises a real
  `sqlite3.IntegrityError`. Proven with synthetic fixtures (G1) AND re-proven on REAL
  G2/G3-composed data end-to-end (G5's `test_e2e_integration.py`).
- **As-of leakage**: `FeatureViewStore.load_as_of` builds an explicit `session_type IN (...)`
  WHERE clause from `SESSION_ORDER`/`session_ordinal` — never a superset-then-filter. The gate
  test inspects the ACTUAL SQL TEXT of every executed statement (via `sqlite3.Connection.
  set_trace_callback`), not just bound parameters — a cold plan critic found the bound-param-only
  version has a real bypass (a session-unfiltered query that happens not to echo a later
  sentinel), which is why the shipped test checks WHERE-clause structure instead, plus a
  deliberate negative-control query proven to correctly FAIL the check. Two independent
  reviewers each constructed their own bypass attempts (INSERT OR REPLACE, weakened UNIQUE key,
  hardcoded-all-sessions IN-clause, cross-entity leaks) — none slipped through. Re-proven on
  real composed data in G5.

## DB-only / sole evo-facing surface

- `read_feature_view` (`read.py`, `__all__ = ["read_feature_view"]`) is the only function
  evo may call — a direct key lookup against the already-written, already-as-of-scoped
  `feature_view_rows` table.
- Bidirectional import-boundary enforcement: `constraint:physics_region_no_evo_import`
  (feature_view never imports evo_predictor, whole-package scan) AND a NEW forward-looking test
  (`test_evo_import_boundary.py`) scanning all 118 `src/evo_predictor/` files, sanctioning ONLY
  `from src.physics.feature_view.read import read_feature_view` — vacuously true today (no evo
  code touches this package yet, Phase 6/#630 is out of scope), designed to trip the moment a
  future evo module reaches past `read.py` (pre-empts the `regime_readiness.py`-vs-
  `estimate_store._cov_list` boundary-drift shape already present elsewhere in the repo).

## Structural decision: new sibling component (Admiral-ratified)

`struct:physics.feature_view` is a NEW top-level component under `struct:physics`, mirroring
the Phase-2 `weekend_state` precedent. Design-it-twice ran two candidates (new component vs.
layer2-embedded `feature_view_*.py` module-leaves); converged on the new component for
seam-legibility ("the ONLY evo-facing surface" deserves a discoverable home, and layer2 is
already a 55+ file directory), while folding in the layer2-embedded candidate's reuse strength
(every new module imports, never reimplements, `effective_axis_sigma`/
`UNRESOLVED_AXIS_SIGMA_FRAC`/`normalize_axis_status`; `cross_view_covariance` is a passthrough).
The Admiral initially ruled a hybrid (layer2-embedded records/store/build + only `read.py`
promoted), then formally RATIFIED the subpackage after review — recorded here as the final
decision. No new component/edge cost on the reuse axis either way.

## Exact test counts (verified independently by the commander at every gate)

- G1: 27 (records/store/append-only/as-of-leakage).
- G2: +6 (33 total).
- G3: +15 (48 total).
- G4: +9 (57 total).
- G5 base: +19 (76 total).
- G5 addendum (σ-widening + forward import test): +8 (84 total).
- Commander fix (read.py transition_axis_status round-trip regression test): +1 (**85 total**).
- `py -m pytest tests/unit/physics/feature_view -q`: **85 passed**.
- `py -m pytest tests/unit/physics/layer2 tests/unit/physics/weekend_state -q` (the required
  regression slice over the two consumed regions): **959 passed, 0 failed** (2 pre-existing,
  unrelated warnings), 19m08s runtime — this box's physics-fit suite is genuinely slow, not
  stuck (confirmed twice by completed runs with identical clean results).
- `py -m src.utils.simplification_limits --paths src/physics/feature_view`: PASS (8 files).

## DB clean

`git status data/` — no output (no `data/*.db` touched or staged). All new store code targets
a NEW standalone `data/feature_view.db` (untracked, matches the `physics_estimates.db`/
`fit_store`/`wear` precedent), never committed.

## Cartographer map impact

`struct:physics.feature_view` (new component) recorded in `docs/architecture/index.md` +
`docs/architecture/packets/physics.md`, mirroring the `weekend_state` entry's format. See the
reconcile commit for the exact diff.

## Triage candidates routed this run

1. `load_as_of`'s SQL-shape checker (in the SHIPPED test suite) verifies WHERE-clause structure
   but not bound-VALUE correctness in isolation — non-blocking (row-content assertions in the
   same tests independently catch the gap; defense-in-depth holds). G1 reviewer finding.
2. `_none_if_nan` duplicated verbatim between `build_weekend_state.py` and `build_car_basis.py`
   — non-blocking, candidate for a shared-helper extraction once a third occurrence appears.
   G3 reviewer finding.
3. `test_evo_import_boundary.py`'s second "sanctioned form" (bare `import ...read` +
   qualified-attribute usage) false-positives on its own usage-line pattern — over-strict, not
   under-strict; never lets a real violation through. G5 reviewer finding.
4. (Resolved during this run, not a residual candidate) `g5-implementer-result.md` was
   genuinely missing from disk (the original G5 implementer stalled mid-verification and never
   wrote it) — commander authored the reconstruction from the plan's attestation trail plus
   direct re-verification; not carried forward as an open item.

## Decisions made / floated / ruled this run

- **Floated**: whether the intra-weekend process-noise-link gap (discovered mid-plan, not
  pre-named by the launch order) should be reserved (like the parc-fermé step) or fit now.
  **Ruling**: reserve BOTH — same new-modeling-out-of-packaging-scope class; filed as issue
  #654.
- **Floated/corrected in the open**: structural placement (new component vs. hybrid
  layer2-embedded). **Ruling**: RATIFIED the subpackage (commander's Candidate-A reasoning
  stood on review) after an initial hybrid ruling that queued past the point of use — no rework
  needed since the ratification landed after all code was already built the winning way.
- **Ruled (mechanical, no float needed)**: the reserved transition-σ widening — flat,
  non-scaling, reuses `effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC`, kept separable via
  the new `transition_axis_status` field. Implemented exactly per the ruling.
- **Ruled (must-fix, not a defer)**: `read.py` dropping `transition_axis_status` on
  reconstruction defeated the σ-ruling's intent (a widening evo can't see does no work) — fixed
  directly by the commander, with a new regression test.

## PR

Base `main`, branch `feat/629-feature-view`. NOT merged (Admiral's gate). Link: (added at
PR-open).
