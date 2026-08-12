# cmdr-698 — Problem Statement

**Issue:** #698 — #666 follow-on hardening: store-API primitive-obsession, script `.pth` path, gitignore.
**Engagement:** PLANNING ONLY. No source/test/doc edits, no commit/push/PR, no issue comment.
**Interrogation:** `.agent-work/cmdr-698/INTERROGATION_RECORD.json` (8 questions, rail exit 0, instructed self-sign-off).

## The ask, in behavior terms

Three independent hardening items over the `src/physics/fingerprint/` package (#666, epic #659 stage G).
None blocked the #666 merge; all are recommend-and-defer debt now being paid.

**H1 — the real work.** Today `DriverFingerprintStore`'s three public methods
(`write_fingerprint`, `get_fingerprint`, `row_count`, `store.py:193/255/298`) take four bare
`str` identity arguments plus a `ClassVocabulary`. The six-field validation that `CellAddress`
performs (`address.py:88-104`: non-empty `str`, no `|` delimiter, known `what_measure`) is
reached only at `store.py:233` — **inside** the per-class write loop, after the store has already
committed to a row set — and on the read path is never reached at all. After H1, an ill-formed
identity is refused **at the call**, before any store work.

**H2.** `scripts/fingerprint_class_coverage_675.py` lacks the worktree-first `sys.path` insertion its
three sibling scripts have, so a bare direct-file run inside a git worktree resolves
`from src.physics...` against the MAIN checkout via the editable-install `.pth`.

**H3.** Confirm no regenerable artifact from this family lands in a tracked path on a non-epic run.

## Two premises I was handed that are false

Both were checked against source rather than accepted, and both change what the plan does.

1. **H1's acceptance wording is unattainable as literally written.** `CellAddress` has six fields
   and addresses **one cell**; the store's unit of work is the **k-cell group**. `class_id` is the
   fan-out axis (`store.py:225`, `:275`) and `vocabulary_version` is read off the vocabulary
   (`store.py:234`), so neither is a store argument. Passing a `CellAddress` with a sentinel
   `class_id` would violate the value object's own documented invariant. The honest target is the
   address **prefix** — which `store.py`'s own docstring already calls a *slot* (`:22-23`, `:186`, `:301`).

2. **H3's premise "already ignored via `.agent-work/`" is false.** `.gitignore` carries no
   `.agent-work/` rule; the tree is **deliberately tracked** (engine-config `rules_root`: commit
   Commander logs once archived), and the #666 artifacts are committed on purpose. The real
   exposure is elsewhere — see below.

A third correction, found while sizing the blast radius: `docs/architecture/packets/physics.md:2753`
says `instrument_panel` "reads `fingerprint.store.get_fingerprint` cells directly." Against source
that is **false as a call claim** — no `instrument_panel` module or its report script references the
store at all. The panel *receives* cells; the pilot fetches them. Read literally it would have sent
an implementer hunting a call site that does not exist.

## Rulings (no human reachable; recorded, decided, and graded)

- **Slot shape.** Frozen `FingerprintSlot(driver, era, channel, what_measure)` in `address.py`
  beside `CellAddress`, sharing its exact validator, exposing
  `address_for(class_id, vocabulary) -> CellAddress` as the sole `CellAddress` constructor on the
  store path. `ClassVocabulary` stays the single authority for `vocabulary_version` + `class_ids`.
  Rejected: a per-cell API (destroys the k-cells-always-populated and no-fit-on-read invariants,
  which are #666 Protected Intent and live *in* the fan-out); a slot that also carries
  `vocabulary_version` (asserts it twice, buys nothing, costs a second refusal path).
  `@grade: settled/inherited` for the shape; `@grade: guess` for the name alone.
- **Tightening.** CellAddress parity only. **No** channel-set membership check — `CellAddress`
  never enforces `FINGERPRINT_CHANNELS` either, and `fit.py:347-350` already validates channel
  independently → triage. The dormant reserved `what_measure` slot stays **constructible but
  refused at write** (epic #659 ruling 4; `test_store.py:153-161` asserts the error type).
  Slot construction stays **vocabulary-blind** so era disagreement keeps raising
  `EraVocabularyMismatchError`, not a construction `ValueError`. `@grade: settled/inherited`.
- **Evidence.** Scoped to the closed importer set, never a blanket suite
  (`lesson:scope-self-authored-regression-to-import-graph`). Store is a consumed frozen module, so
  its own pre-existing tests re-run with every refusal raising the **same** exception type
  (`lesson:consumed-frozen-module-run-guard-tests`). `@grade: settled/inherited`.

## Protected intent — what must not move

The four keystone invariants stated at `store.py:10-32`: non-NULL `cell_key`; k-cells-always-populated;
loud refusal with no silent substitution; **no fit-on-read**. Plus every number `fit.py` produces —
this is a type/seam refactor, so no `mean`, `sigma`, `support_n`, `status`, or coverage verdict changes.
`constraint:physics_region_no_evo_import` continues to hold (nothing here reaches toward evo).

## Blast radius (closed by grep over `src/ scripts/ tests/`)

| Kind | Site |
|---|---|
| production writer | `src/physics/fingerprint/fit.py:356` (the only writer anywhere) |
| production readers | `src/physics/pilot/pipeline.py:257`, `:325` |
| scripts | `scripts/fingerprint_bounded_validation.py:124`, `scripts/join_bounded_validation_667.py:173` |
| tests | `test_store.py` (~20 sites), `test_fit.py:160`, `test_bounded_validation.py:173,:267,:326,:333` |
| **not** affected | `instrument_panel/*` (never touches the store), `fingerprint/__init__.py` (re-exports nothing) |

## H3, reframed to what is actually exposed

- **`data/driver_fingerprint.db`** (`store.py:50` `DEFAULT_DB_PATH`) is **absent from `.gitignore`**,
  while every sibling own-DB is present (`/data/reference_utilization.db` #664,
  `/data/segment_maps.db` #662, `/data/driver_utility_observables.db` + `/data/driver_utility.db` #628).
  A default-path fit run drops an untracked **binary SQLite DB** into `data/` — precisely the artifact
  class the archive step's own deny-globs exist to stop. This is the highest-value item in H3 and the
  issue's JSON framing missed it.
- Three scripts write regenerable JSON to hardcoded **live** `.agent-work/666-driver-fingerprint/artifacts/`
  paths with no `--out` flag (`fingerprint_class_coverage_675.py:123` — argparse at `:472-473` offers
  only `--slice-db`/`--n-reps`; `fingerprint_bounded_validation.py:48`; `join_bounded_validation_667.py:70`).
  A re-run outside an epic work area stages them under `git add -A`.

## Out of scope

Any behavior change to the fit or the coverage diagnostic (issue's own exclusion). Channel-set
enforcement. Adding `--out` flags to the three scripts. Rewriting the store to a per-cell API.
Correcting the `instrument_panel` packet prose (reconcile/triage, not a code gate).
