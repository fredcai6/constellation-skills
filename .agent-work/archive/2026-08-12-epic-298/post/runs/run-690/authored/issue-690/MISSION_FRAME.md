# Mission Frame — issue #690

Per-class G σ⁺ band scale. Map-first frame authored from `docs/architecture/index.md` (RESOLVED,
76 anchors) and `docs/architecture/packets/physics.md` before any gate was cut.

**Anchor-citation note.** The map inventory `verify-frame` checks against is built from
`docs/architecture/index.md` alone. Several ids that genuinely govern this run live one level down —
as graded decision bullets and claim names inside `packets/physics.md`, or in
`overlays/constraints.yml` — and therefore are **not** in that inventory. They are named below in
back-ticked plain form (no `kind:` prefix) so the frame does not assert an inventory membership it
does not have; each says where it actually lives. This is a known map-model gap (packet-level
anchors are invisible to the index-scoped checker), not a citation of something unread.

## Intent

Make the one-sided grip σ⁺ that pipeline stage **E** attaches to each per-CLASS transit-time deficit
a **per-class** quantity instead of the whole-lap pace σ it is today, so that stage **G**
(`fingerprint.fit._compose_sigma`) stops quadrature-adding a lap-scale uncertainty into every
`(driver, class)` cell — and so W2's scored band-distribution artifact is expressed in units that can
be read at all. The frame is NOT skipped: this lands on a joined, mapped pipeline edge (D→E→G) with a
settled decision governing it.

## Affected Capabilities

The map's capability overlay still uses the deprecated `purpose:`/`serves` ontology (an open triage
row in `index.md`), so these are named in that file's own form:

- `purposes.yml` → `physics_utilization` (child of `physics_estimation`) — the driver/class
  utilization layer. Today it emits a per-class deficit wrapped in a lap-scale band; this run makes
  the band's width class-local. The deficit itself is untouched.
- `purposes.yml` → `physics_estimation` — parent. Only the uncertainty channel moves; no estimate,
  fit, or ceiling changes.

## Examples / Events

- **Pipeline stage E → G edge** (`index.md`: `E(driver_class_observables) → G(fingerprint.fit…)`):
  the concrete carrier of the defect. `fit.py` reads `g_sigma_onesided` per row, recency-weights it
  per `(driver, class)` cell, and quadrature-adds it into `sigma_cell`. A lap-scale σ in that slot
  inflates every cell equally — the dominant cause of #712/#670's vacuity at the median.
- **Observed instance** (real archived #670 store, `refutil_season_2023.db`): `g_sigma_onesided` is
  identical across all six classes for all 381 rows/class, while `time_deficit_s` spans
  −0.0015 s … 3.7457 s. The per-class weights that fix it are *already persisted* beside them in
  `reference_laps.time_shares_json` (Australia-Q: straight 0.531 / braking_zone 0.154 / c0 0.162 /
  c1 0.001 / c2 0.137 / c3 0.015).

## Structural Anchors

- `struct:physics.utilization` — `src/physics/utilization/`, component level. The work lands here:
  `class_utilization_observable.py` (the wrap point; stage E, and the real stage-D grip consumer),
  `class_ledger.py` (g1 — supplies `time_share_by_class`; read, not rewritten),
  `reference_utilization_store.py` (persists the column; `format_version` provenance).
- `struct:physics.layer2` — `src/physics/layer2/`, component level. Read-only dependency:
  `grip_store.get_grip_at` (stage D). **Not modified** — its caller-chosen-x contract and its
  negative-evidence tests must need zero edits (the same proof #721 used).
- `struct:physics.fingerprint` — `src/physics/fingerprint/`, component level. The downstream
  consumer (`fit.py::_compose_sigma`, `(driver, class)` cells, `severity:%` filter). Its behaviour
  changes because its input changes; its code should not need to.

## Governing Constraints / Assumptions

- `constraint:physics_region_no_evo_import` — the physics region imports nothing from
  evo / latent_power / compound_prior. Nothing here crosses that line; the new reporter is a
  physics-region script over physics stores.
- `overlays/constraints.yml` → `db_only_data_access` — analysis reads the canonical stores, never
  FastF1/live. The measurement gate opens archived SQLite stores read-only (`mode=ro`) and copies
  them to scratch before any write.
- **Anti-circularity (#628, the observable module's own binding contract):** every deficit stays
  ABSOLUTE, never a ratio. The σ⁺ weight is a lap-time **share** applied to σ only — it never divides
  an observed quantity by a capability quantity, and it never touches the deficit.
- **Pure-core assumption:** `class_utilization_observable` is a smoother-agnostic pure numeric core
  with no DB/session/store I/O. The weights must therefore be computed from the arrays already passed
  in, not fetched back from `reference_laps`.

## Decision Anchors & Decision Pressure

- `decision:class-attribution-membership-faithful` — attribution is membership-faithful through `W`,
  never an argmax collapse.
  `@grade: settled/measured · leans g1-implement`
  → The σ weights must come through the same `Wᵀ·(per-segment quantity)` reduction as every other
  class quantity. An argmax "dominant class" split of the σ would violate this anchor.
- `decision:c1_driver_utilization_design` — the C1 utilization design (causal through-`W` prior;
  single canonical sim path).
  `@grade: settled/measured · leans g1-implement,g2-implement`
  → Constrains where the change may land: inside the existing canonical path, no second path.
- `decision:grip_estimate_record_session_level_pk` — grip records are keyed at session level.
  `@grade: settled/measured · leans g1-implement`
  → This is *why* the σ arrives as one whole-lap scalar per session at all. The record is not being
  re-keyed here (that is #678's step 3); the split happens on the consumer side.
- `packets/physics.md` → `g-one-sided-directed-uncertainty` (packet-level decision bullet, graded
  there as `settled/inherited`) — the deficit carries a one-sided directed uncertainty (μ=0, σ⁺ only,
  half/truncated Student-t).
  `@grade: settled/inherited · leans g1-implement`
  → **Not unsettled by this run.** The posture is untouched; only the *scale* becomes class-local. A
  gate that finds itself wanting to move μ or two-side the band must STOP and float, not revise in
  place.

**Decision pressure this run forces (candidates, ungraded until ruled — carried into the plan):**

- **The weight definition** — class transit-time share vs. a grip-sensitivity weighting that
  down-weights straights. Ruled D1 (time share) in `PROBLEM_STATEMENT.md`.
- **The composition law** — linear (`w_c·σ`, common-mode) vs. quadrature (`√w_c·σ`, independent).
  Ruled D2 (linear). Durable: it fixes what the widths mean and which invariant holds.
- **Column semantics** — repurpose `g_sigma_onesided` per-class with a `FORMAT_VERSION` bump vs. a
  second column. Ruled D4 (repurpose; one canonical path).

## Claims / Evidence Surfaces

- `packets/physics.md` → `deficits-sum-to-lap` (packet-level claim) — per-class time deficits sum to
  the lap deficit, structurally, via `W` row-sums. **This run adds its direct sibling:** per-class σ⁺
  sums to the lap-level σ⁺ under the linear law. Every gate re-confirms the original claim untouched
  (byte-identical deficits) and proves the new one by unit test.
- `packets/physics.md` → `attribution-robust` (packet-level claim) — attribution is stable under the
  jackknife. Unchanged: this run reuses `W`, it does not re-derive attribution.
- **New evidence surface:** the band-distribution report — median / p90 / vacuous count /
  plausible-|D| count, plus retained-session fraction and substrate provenance — W2's separately
  scored artifact per the confirmed spec's T7 / IF15 / T19 / T20 amendments.

## Map Confidence / Staleness / Disputes

- `struct:physics.utilization` and the `struct:physics.layer2` grip leaves — **high confidence,
  fresh.** Reconciled 2026-07-27 for epic #659 closeout, re-verified 2026-08-01 by #721's own
  Cartographer pass (`9fae4c9d`, a logged no-op). No scout gate needed.
- **Honest-NULL carried in the map, not a defect to fix here:** the grip node's g4 held-out regressed
  +155.5 % RMS and g5 separability was 31.9 % (FAIL) — recorded as a disclosed null. It means the σ
  this run re-scales may itself still be untrustworthy, which is exactly why acceptance is the
  *scaling* and its invariant, **not** the number the band lands at (#724 owner ruling: deficit scale
  is aspiration, not bar).
- **Stale-adjacent, verified before use:** the issue text predates #721 and is stale in two of its
  three claims. Reconciled at the context step against `main`; the plan is cut against `main`, not
  against the issue's framing and not against this worktree's detached `3541d292`.
- **Map-model gap (recorded, not worked around silently):** packet-level decision/claim ids are
  invisible to the index-scoped `verify-frame` inventory — see the citation note at the top. Raised
  as a triage candidate, not fixed here.

## Out of Scope

Re-fitting or re-keying G (#678, #687); moving μ off zero (#678); the flying-lap gate on grip's lap
reader (#679); condition regressors — track temp, overnight gap, continuous wetness (#686, #688); the
final σ consumer contract (#712, the owner's decision at W2's close); `get_grip_at`'s
caller-chosen-x contract; `compose_and_persist_weekend`'s pre-existing complexity debt (#722); any
evo-region file; any change to the point deficits, to `W`, or to the ideal-lap ceiling.
