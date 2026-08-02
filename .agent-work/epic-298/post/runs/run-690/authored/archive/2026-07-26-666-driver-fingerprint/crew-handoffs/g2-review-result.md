# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-review` (issue #666, epic #659, Wave 3)

## Result
`APPROVE`

## Handoff compliance
All 6 close criteria satisfied and independently reproduced by this review (not trusted from the
implementer's/commander's pasted output). A fresh, standalone repro script (not the implementer's own tests)
constructed `CellAddress` with `None`/empty values for all six fields (raises `ValueError` naming the field
every time), inspected the store's actual `sqlite3` schema via `PRAGMA table_info` on a freshly-created DB
(`cell_key` is `notnull=1, pk=1`), wrote the same fingerprint twice and confirmed `row_count == k` (not `2k`),
read a never-written driver and got exactly `k=4` synthesized `unresolved` cells, triggered
`EraVocabularyMismatchError` on both write and read for an era/vocabulary mismatch, triggered
`ClassVocabularyNotFittableError` on a `FAIL`-verdict vocabulary (both via the store and directly via
`ClassVocabulary.require_fittable()`), confirmed `allow_unverified=True`/`override=True` correctly bypasses it,
`ast`-parsed `store.py`'s import list and confirmed it contains no fit/pooling/observables module, and confirmed
`RESERVED_WHAT_MEASURES` slots are constructible on `CellAddress` but refused (`ReservedWhatMeasureError`) at the
store's write path. The `era_key` derivation was cross-checked against the real
`src/physics/regulation_era.py:RegulationEra.for_season` flag arithmetic (not just trusted from prose) and
matches every test claim (2013≠2015, 2024==2025, 2024≠2026).

## Scope drift
None. `git status --porcelain` in the worktree shows exactly the 4 new untracked paths expected
(`src/physics/fingerprint/`, `tests/unit/physics/fingerprint/`, `.agent-work/666-driver-fingerprint/`, plus
`scripts/fingerprint_class_coverage_675.py` which is g1-implement's #675 diagnostic sharing the worktree, not
part of this diff — confirmed by its own docstring header). `git diff --stat` on the 4 house/reference modules
the implementer claims to have read-only-consumed (`reference_utilization_store.py`, `grip_store.py`,
`segment_map/identity.py`, `regulation_era.py`) is empty — none were edited. No specific exclusion (no fit
logic, no existing module edited) was violated.

## Evidence verdict
Re-ran, in this review, foreground: `PYTHONPATH=. python -m pytest tests/unit/physics/fingerprint/ -q` → 69
passed (65 g2 tests + 4 pre-existing g1 `test_frozen_constants.py` tests); `python -m
src.utils.simplification_limits --paths src/physics/fingerprint/{address,vocabulary,store}.py` → PASS (3 files
checked); also ran it on the 3 test files myself (implementer only ran it on `src/`) → also PASS. TDD mode
(required per handoff) — implementer's RED→GREEN evidence is consistent with the test structure observed.
Test-DB isolation confirmed: `test_store.py`'s `store` fixture uses `tmp_path` exclusively (grepped, no
hardcoded path); no `data/driver_fingerprint.db` exists on disk after any run; `git status --porcelain` has zero
`.db`/`.parquet` entries; nothing staged (`git diff --cached` empty).

## Code/doc quality
Minimal, maintainable, matches the house store pattern (`must_exist`, `row_factory=sqlite3.Row`,
`_migrate_missing_columns`, `INSERT OR REPLACE`) verified against `reference_utilization_store.py`/`grip_store.py`
source directly. Validation exceptions name field + expectation + actual value throughout, per project
convention. No module-level mutable state / DB singleton. No FastF1/Jolpica import anywhere in the 3 files.

**Fowler refactoring pass** (full 12-smell baseline catalog, rail `scripts/verify_fowler_pass.py` exits 0 —
record at `.agent-work/666-driver-fingerprint/g2-review/fowler_pass.json`):
- 8 absent: long-method, large-class, duplicated-code, feature-envy, shotgun-surgery, divergent-change,
  message-chains, comments-as-deodorant.
- 3 flagged (one root cause): **data-clumps / primitive-obsession / long-parameter-list** — `write_fingerprint`,
  `get_fingerprint`, and `row_count` all take the `(driver, era, vocabulary, channel, what_measure)` 5-tuple as
  loose primitives rather than the `CellAddress`/key value object `address.py` already defines to solve exactly
  this identity problem. The docstring claims to "mirror the house store pattern," which is true for
  schema/migration/idempotency style, but the house precedent's `write()` takes ONE bundled record object
  (`ReferenceLapProduct` / `GripEstimateRecord`), whereas `write_fingerprint` here takes 6 loose params (the read
  shape, by contrast, does match the house `get(year, gp_name, session_type, map_version)` precedent). Not a G2
  blocker — correct and tested — but a design-quality note worth reconciling in G3/G4 once the fit path becomes
  a second real caller (two callers is when a data clump becomes worth a parameter object, per the "one adapter
  is a guess, two is real" doctrine).
- 1 overridden: **speculative-generality** (dormant `channel`/`what_measure` reserved slots) — logged against
  epic #659's binding owner ruling 4 ("dormant slots present-but-unused rather than added later as a breaking
  schema change"); the store actively *refuses* to populate reserved slots (`ReservedWhatMeasureError`) rather
  than half-supporting them, so the override is earned, not a shrug.

## Map impact verdict
- **Evidence supports claimed change:** Yes — every structural/capability claim in the implementer's Map Impact
  section was independently reproduced (see Handoff compliance above), not just read and trusted.
- **Constraints not violated:** Yes — DB-BLOB guard honored (own DB, tmp_path tests only, nothing staged,
  nothing in `data/`); ruling-4 dormant-slot constraint honored (constructible, refused at write).
- **Notes match the diff:** Yes — `git diff --stat` on the 4 claimed read-only-consumed files is empty; the 3
  new src files + 3 new test files match exactly what the notes describe.
- **Decision candidates surfaced:** Yes — `decision:fingerprint-era-key` was resolved this run
  (flag-signature derivation over `str(season)`), regraded `settled/measured`, and independently verified
  against the real `RegulationEra.for_season` source rather than trusted from prose.
- **Durable context routed:** Yes — one triage candidate flagged through the engine (`tc1`, below) rather than
  silently dropped; `docs/architecture/` correctly left untouched (map-fence honored), deferring reconciliation
  to Cartographer/Admiral closeout as this is a genuinely NEW `struct:physics.fingerprint` node (grepped
  `docs/architecture/index.md` for prior "fingerprint" entries — none pre-exist).

## Reconciliation check
No divergence from recorded architecture. `docs/architecture/` untouched (git status/diff confirm). The 4
house/reference modules the implementer read-only-consumed are unmodified. `era_key`'s resolution of
`decision:fingerprint-era-key` is consistent with existing `RegulationEra` semantics as verified directly against
source, not merely the implementer's prose.

## Blockers
- none

## Out-of-scope observations
- **tc1 (flagged via engine `flag-candidate`):** The vocabulary-drift refusal (`EraVocabularyMismatchError` on
  stale `vocabulary_version` rows under the same driver/era/channel/what_measure slot) has no sanctioned
  migration/purge API yet — a caller who genuinely wants to move a driver's fingerprint onto a re-fit taxonomy
  can only be refused, indefinitely. Correctly out of scope for G2 (no such caller exists yet); worth a Triage
  ticket for G3/G4 if a re-fit workflow needs it.
- **Fowler data-clumps/primitive-obsession/long-parameter-list** (see Code/doc quality above) — not a blocker,
  but worth reconciling once the G3 fit path becomes a second real caller of `write_fingerprint`.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's close criteria mapped cleanly 1:1 onto reproducible checks; no
  ambiguity encountered.
- **Context rediscovered:** Had to independently verify the `era_key` claims (2013≠2015, 2024==2025, 2024≠2026)
  against `src/physics/regulation_era.py`'s actual flag arithmetic rather than trusting the vocabulary.py
  docstring's prose — worth noting only because it's exactly the kind of claim a reviewer must reproduce, not
  because the handoff was missing anything; it named the file to check.
- **Instructions improvised around:** none. The Fowler-pass rail (`scripts/verify_fowler_pass.py`) worked exactly
  as documented on the first attempt (12/12 smells visited, override logged, exit 0).
- **What would have made this easier:** none — the handoff's Close Criteria section was unusually precise
  (named the exact invariant, the exact reproduction step, and the exact evidence expectation for each), which
  made independent reproduction fast rather than exploratory.

## Return status
`complete`
