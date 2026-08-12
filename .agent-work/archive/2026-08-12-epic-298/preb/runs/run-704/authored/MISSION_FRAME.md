# Mission Frame — issue #704

Authored map-first from `docs/architecture/index.md` + `docs/architecture/packets/physics.md`
(instrument_panel section, reconciled 2026-07-27 at epic-659 closeout) before authoring
`execute.json`.

**Frame kept, not skipped.** The change itself is mechanical, but the map is not decoration here:
it is what establishes that this module carries three `settled` decision anchors and a signed
frozen-constant set that a "cosmetic" edit could brush against. The frame is short; it is not empty.

## Intent

Remove the duplicated axis-grouping pass inside `struct:physics.instrument_panel`'s
`replication.py` behind one **private** helper, changing no capability, no public interface, and no
numeric output — a structure-only change entirely inside one module node, with the map's decision
anchors left exactly as they stand.

## Affected Capabilities

The map uses the deprecated `purpose:`/`serves` overlay rather than `capability:`/`supports`
(recorded as an Open Structural Question, `docs/architecture/index.md:1023`). Reading it in that
ontology:

- **Stage PANEL of the epic-659 `C→D→E→G→H→PANEL` chain** — a read-only diagnostic panel that
  *sizes* the pipeline's signal (no hard gate). This run **relies on** it and changes nothing about
  it: Instruments 2+3 still measure split-half replication of driver-utilization via double-centering.
- No `purpose:` overlay entry names `instrument_panel` directly (`purposes.yml` has no panel entry),
  so there is no `serves` edge for this run to touch.

## Examples / Events

- `run_panel` (`scripts/instrument_panel_668_report.py`) → emits
  `docs/physics/instrument_panel_668_gb2023q_report.md`. **Byte-identical behavior means this
  artifact must not need regeneration** — that is the run's sharpest observable success test.
- `scripts/run_season_panel_670.py` — season-level consumer of the same frozen rules.
- `src/physics/pilot/pipeline.py::run_stage_panel` — lazy transitive importer (#669 pilot).

## Structural Anchors

- `struct:physics.instrument_panel` — `src/physics/instrument_panel/`, **level: component**,
  status current, **confidence: high**. The only node this run lands in.
- `src/physics/instrument_panel/replication.py` — module leaf under that component; the sole file
  whose source changes.
- `struct:physics.layer2` (`frozen_constants.py`) — *depended on, untouched*: `replication.py` reads
  the `REPLICATION_*` set through the single `frozen_replication_thresholds()` seam.
- Non-map script nodes: `scripts/instrument_panel_668_report.py`, `scripts/run_season_panel_670.py`.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — the component carries this edge
  (`docs/architecture/overlays/constraints.yml:54`). The dedup adds **no import at all**, so the
  edge is trivially preserved; the reviewer should still confirm it rather than assume it.
- **F12-independence (module-level invariant, `replication.py:35-44`)** — the pure core imports no
  frozen `REPLICATION_*` constant; thresholds are injected. The new helper takes `grid` only and
  imports nothing.
- **Bit-exact float ordering (the run's own hard constraint, discovered at `understand`)** — the
  helper must preserve grid-iteration order per axis, the grand mean must keep its own single
  left-to-right pass, and per-axis list order must survive because `_main_effect_se` feeds
  `np.std(ddof=1)`. Violating this silently changes the last ulp of a signed instrument's output.
- **Project evidence rule** — `docs/agents/ORCHESTRATOR_CONTEXT.md`: a Python refactor in `src/`
  requires `py -m src.utils.simplification_limits` on touched paths (strict).

## Decision Anchors & Decision Pressure

All three packet anchors are **inherited read-only** by this run; none is revised, and each is
`settled`, so a contradiction is a STOP-and-float, not a local revision.

- `decision:golf-correction-is-double-centering` — the correction is the two-way ANOVA interaction
  residual, not per-driver demeaning.
  `@grade: settled/measured · leans g1-implement,g1-review`
- `decision:split-half-unit-cross-circuit-2v2` — the split unit is injected, pre-registered 2-vs-2.
  `@grade: settled/human · leans g1-review`
- `decision:replication-frozen-set-signed` — the `REPLICATION_*` set is owner-signed.
  `@grade: settled/human · leans g1-implement` (out of scope per #704, and the gate must not touch it)

New decisions this run forces, resolved at `understand` under the engagement's standing no-human
order and carried as **plan decisions, not map anchors** (they govern one private helper inside one
module — the Decision-candidates rule excludes choices obvious from current structure, and none of
these would change how a future agent plans):

- `decision:axis-helper-returns-grouped-lists` — the shared helper returns grouped per-axis value
  lists, not sums+counts; `_axis_means` keeps its own pass for the grand mean.
  `@grade: settled/human · leans g1-implement` (engagement standing instruction; owner may revisit)
- `decision:proceed-with-surgical-diff` — proceed despite #704's own review-cost warning, holding
  the diff to one private helper + two call sites + zero public-surface change.
  `@grade: settled/human · leans g1-implement,g1-review`
- **Decision pressure (no grade — a candidate, not an anchor):** whether `per_driver_demean` should
  stop paying for the grand/class computation it discards. Declined this run as diff-widening on a
  Protected-Intent module; surfaced at `triage` rather than decided here.

## Claims / Evidence Surfaces

- `claim:instrument_panel_reads_cells_directly` — the panel reads un-aggregated fingerprint cells
  directly, NOT via the #667 join (verified: no `join` symbol imported). This run must not change
  the import set, so the claim must still hold verbatim afterwards — re-confirm by import diff.
- **Numerical-identity evidence (this run mints it):** exact equality of `grand_two_way_center`,
  `per_driver_demean`, and `main_effect_margin_uncertainty` outputs before vs. after, on ragged,
  unbalanced, and singleton-row grids. `==`, not `approx`.
- **Existing guard tests:** all six files under `tests/unit/physics/instrument_panel/`, incl.
  `test_panel_corpus.py`'s source-text guard and `test_replication_frozen_constants.py`.
- **Project checks:** `simplification_limits` (strict) on the touched path; pyright with no new
  errors vs. base (`scripts/pyright_baseline_diff.py`).

## Map Confidence / Staleness / Disputes

- `struct:physics.instrument_panel` — **confidence: high**, reconciled 2026-07-27 at epic-659
  closeout. No scout gate needed; the plan may trust it.
- `docs/architecture/overlays/purposes.yml` — **known-stale ontology** (`purpose:`/`serves` instead
  of `capability:`/`supports`), already tracked as an Open Structural Question. It carries **no**
  entry for `instrument_panel`, so this run neither depends on it nor is blocked by it. Recorded so
  the gap is not mistaken for something this run introduced.
- **Not a map issue but the run's real staleness risk:** the "instrument_panel tests are green"
  premise in #704's acceptance is **unverified by this planning run** — every test invocation was
  permission-blocked. The plan answers this with a dedicated baseline gate (`g0`) rather than
  assuming it.

## Out of Scope

- The signed `REPLICATION_*` frozen set, `ReplicationThresholds`, `r_floor`, and the
  double-centering formula itself (#704 states this; the map grades two of them `settled/human`).
- Every public name in `replication.py.__all__` — signatures, semantics, and the export list are
  frozen.
- The other two instruments (`variance_decomposition.py`, `sector_scorecard.py`) and both consumer
  scripts.
- Regenerating any panel report artifact — byte-identical output means none is stale.
- Any architecture-map edit: a private in-module helper is below map resolution, so `reconcile` is
  expected to be a reasoned no-op.
