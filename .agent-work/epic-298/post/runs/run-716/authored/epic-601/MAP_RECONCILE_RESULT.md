# Epic #601 closeout — architecture map reconcile result

Run via the `constellation-cartographer` skill's gated checklist
(`.agent-work/epic-601/carto-reconcile/CARTOGRAPHER.json`, session `carto-601`).
Scope: verify the map at final merged main `299313cf` (branch `main`), re-checking the
existing partial reconcile at `b97a58e1` and closing the gap it predates.

## What was already correct (verified, no change needed)

- **#628 §9 driver-utility** (Phase 3b, `27b6eac9`) and **#513 Phase 4 FP-session fits**
  (`72577cef`) — both fully covered by the `b97a58e1` reconcile (`packets/physics.md`'s
  "Driver-utility latent" subsection under `struct:physics.utilization`, and the "FP
  (practice) session support" subsection under `struct:physics.layer2`). Confirmed via
  `git show --stat` that neither `2e4fd5ef` (#629) nor `299313cf` (#630) touched any file
  under `src/physics/utilization/` or `src/physics/layer2/`, so this content is unaffected
  by the two commits that landed after the base reconcile — still accurate, no drift.
- **#626 Phase 2 weekend-state** and **#627 (+#506) Phase 3 unified-basis** — both were
  already reconciled *before* `b97a58e1` (dated 2026-07-18 entries further down
  `index.md`), landed cleanly, and remain correct.
- **#630's own self-reconcile** (done in the same commit as the code, `299313cf`) was
  thorough and accurate as far as it went: the `struct:evo -> struct:physics` `depends-on`
  edge (the first evo→physics edge, correctly directioned against
  `constraint:physics_region_no_evo_import`), the `physics_feature_injection.py` /
  `PhysicsFeatureInjectionConfig` / `sampled_runtime.py` wiring entries in
  `packets/evo_predictor.md`, and the one-paragraph correction to `packets/physics.md`'s
  container intro (retracting the old "nothing outside `src/physics/` imports it" claim).
  None of this needed correction — it was extended, not fixed (see below).

## What was missing or stale (the gap this pass closes)

Confirmed by grep across `docs/architecture/` that `struct:physics.feature_view` had
**zero** prior references anywhere in the map — not in `index.md`'s catalog, not as a
`packets/physics.md` component section, not in any overlay. `#629` (`2e4fd5ef`, Phase 5 —
`src/physics/feature_view/`, 7 modules / 1,306 lines / 22 files incl. tests) touched **no**
`docs/architecture/` file at all; `#630`'s self-reconcile added a pointer sentence and the
consumer-side edge but never gave the new package its own structural node or packet
section. This matches the gap the run brief predicted exactly.

Also missing: the boundary the run brief specifically flagged — `read.py`'s
`read_feature_view`/`read_feature_view_at` as the sole sanctioned evo-facing surface,
enforced in both directions by `test_import_boundary.py` (physics-must-not-import-evo) and
the forward-looking `test_evo_import_boundary.py` (#629 G5 addendum) — had no map anchor at
all. This is exactly the "real, test-enforced architectural edge" the map-model's Inclusion
Rule calls for (boundary correctness + trust).

Two smaller pre-existing omissions found opportunistically while touching the same
paragraph: `packets/physics.md`'s container-level bullet list (which points readers at each
component's "see its node below") was missing `struct:physics.weekend_state` and
(necessarily) `struct:physics.feature_view` — only `layer2` and `utilization` were listed.
Fixed both since the edit was already in the same paragraph.

## What was changed

- **`docs/architecture/index.md`**
  - New `struct:physics.feature_view` catalog node (component level, `parent:
    struct:physics`), inserted immediately after the sibling `struct:physics.weekend_state`
    node, following the same yaml-block + "See:" pointer pattern.
  - Enriched the existing `struct:evo -> struct:physics` `depends-on` edge's evidence with a
    pointer to the new claim (below).
  - Prepended a new top-of-file "Reconciled 2026-07-24 for epic #601 closeout" log entry
    naming what was verified-still-accurate, what was added, and the one deliberate
    no-action decision (#644, below).
- **`docs/architecture/packets/physics.md`**
  - New `## Component: feature_view` section (mirrors the `weekend_state`/`layer2`
    precedent): yaml struct block + per-module prose for all 7 source files
    (`records.py`, `store.py`, `build_weekend_state.py`, `build_car_basis.py`,
    `build_lap_evidence.py`, `build_feature_view.py`, `read.py`) including the four record
    shapes, the append-only store contract, the reserved/never-fabricated fields
    (`process_noise_link`, `parc_ferme_step`, `unit_class_residuals`,
    `circuit_conditional_composite`) and their named follow-ons (#654, G7, #513-bound), the
    addendum's transition-sigma widening, and a dedicated "test-enforced boundary" callout
    naming both test files. Plus a `### Dependencies (feature_view sub-package)` subsection.
  - Updated the container intro paragraph to point forward to the new section (instead of
    describing the package only inline) and added the two missing container-level bullets.
- **`docs/architecture/overlays/constraints.yml`**
  - New `claim:feature_view_evo_import_boundary` node — the sole-read-surface / both-
    directions-test-enforced boundary, evidenced by `test_import_boundary.py`,
    `test_evo_import_boundary.py`, and `read.py`'s `__all__`.
  - Two new relationship edges anchoring `struct:physics.feature_view`: `constrained-by ->
    constraint:physics_region_no_evo_import` and `verified-by -> claim:feature_view_evo_import_boundary`.

All content is grounded in direct source reads (`records.py`, `store.py` header + method
list, `read.py` in full, `test_evo_import_boundary.py` in full) plus the `#629` archive's
per-gate implementer results at `.agent-work/archive/2026-07-24-629-feature-view/`
(`g1`–`g5` + the `g5` addendum), cross-checked against `git show --stat` for both `2e4fd5ef`
and `299313cf` to confirm file-level scope.

## Drift found but deliberately not fixed

- **#644 (`61b1c76e`, headless BLAS/OMP/torch thread cap at `src/physics/__init__.py`
  import)** is not documented anywhere in the map, and I left it that way. It's a
  behavioral-only addition to a package `__init__` (env-var defaults + a defensive
  `torch.set_num_threads(1)` call) with no new structural node, dependency direction, or
  boundary — it mirrors the #623 fix in `src/evo_predictor/run.py`, which itself was never
  given map documentation either (grep-confirmed: no `#623` reference anywhere in
  `docs/architecture/`). Consistent treatment, recorded as a deliberate no-action call in
  the new `index.md` log entry rather than silently skipped.
- **`altitude_assumed_flat` hardcoded `False` in `session_estimator`** — pre-existing,
  already flagged as a triage item in `packets/physics.md`'s Known Limits (line ~2694-2697);
  untouched by this pass, not re-litigated.
- **The corner-regime point-aligned utilization confound** — pre-existing Known Limit
  already routed to Triage; untouched.
- Did not add a new Known Limits bullet for feature_view's reserved fields
  (`process_noise_link`/`parc_ferme_step`/`unit_class_residuals`/
  `circuit_conditional_composite`) beyond what's already in the new component section's
  prose — each is already explicitly framed as reserved-not-fabricated with its own named
  follow-on (#654, G7-compute-deferred, #513-bounded) inline; a duplicate Known Limits entry
  would be a second registry for the same fact, which the map-model doctrine (packets are
  the primary durable page; index/overlays are navigation, not a second packet registry)
  argues against.

## Verification

- `check_arch_map.py` (via `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`):
  **green**, before and after — `Parsed 44 catalog nodes, 22 packets, 13 overlay nodes. OK:
  architecture map is consistent.` (was 43/22/12 before this pass — net +1 catalog node,
  +1 overlay node, 0 packet-file count change since `physics.md` already existed).
- Per the project memory that a green mechanical check is necessary but not sufficient
  (content drift is out of its scope), the reconcile itself was done by direct source
  reads (not from the archive's prose alone) — `records.py` and `read.py` read in full,
  `store.py`'s docstring + method signatures read directly, `test_evo_import_boundary.py`
  read in full to confirm the sanctioned-pattern regexes match what the packet claims.
- Changes are staged/unstaged in the working tree only, not committed, per instruction —
  the Admiral commits.

## Engine trail

Driven end-to-end through the Cartographer gated checklist (`context` → `packets` →
`index-overlays` → `map-compliance`), each gate's `attest`/`advance --why` calls recorded in
`.agent-work/epic-601/carto-reconcile/CARTOGRAPHER.json` (+ its `.journal`). No triage
candidates or blockers raised — the two smaller drift items above are pre-existing and
already tracked in the packet's own Known Limits / this report's "not fixed" section, not
new discoveries needing a fresh triage ticket.
