# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` — season runner + E-budget/refutil plumbing (epic #659 Wave 6, #670 season-scale run, Build-1 culmination)

## Completed slice
Threaded `budget_s` + a `refutil_db` override through `run_circuit -> run_stage_e` in
`src/physics/pilot/pipeline.py` (pure plumbing, defaults unchanged), then built the OFFLINE
season runner (`scripts/run_season_670.py`) and its G2 acceptance check
(`scripts/verify_season_artifacts_670.py`), proven entirely via unit tests with a
synthetic/monkeypatched `run_circuit` — no real E was ever spawned in this gate.

## Scope
**Files changed:**
- `src/physics/pilot/pipeline.py` (plumbing only: `run_circuit` gained keyword-only `budget_s`
  default `E_WALLTIME_BUDGET_S` and `refutil_db` default `None` — falling back to the existing
  per-circuit `make_scratch_layout` path when `None` — both forwarded into its internal
  `run_stage_e(...)` call, which already accepted both params but was not receiving `budget_s`)
- `scripts/run_season_670.py` (NEW): `build_season_slate`, `read_round_grid`,
  `copy_tracked_db_once`, `check_round_vocabulary`, `run_season` (injectable core loop), CLI `main()`
- `scripts/verify_season_artifacts_670.py` (NEW): `verify()` + CLI `main()`
- `tests/unit/physics/pilot/test_season_runner.py` (NEW): 15 tests

**Specific exclusions touched:** no — no frozen constant edited, no stage-function/gating-decider
logic changed, no real season compute run, `docs/architecture/*` untouched.

## Behavior changed
Yes. `run_circuit` now accepts two new optional run-params (`budget_s`, `refutil_db`) with
unchanged defaults — a purely additive signature change, verified against all 29 pre-existing
pilot tests (still pass unmodified). Two new offline scripts added; neither is imported/called by
any existing production path.

## Map Impact
- **Structural anchors touched:** `src/physics/pilot/pipeline.py::run_circuit` — now accepts
  `budget_s`/`refutil_db`, forwarding both to `run_stage_e`; `run_stage_e` itself unchanged (it
  already declared both params). NEW: `scripts/run_season_670.py` (season runner),
  `scripts/verify_season_artifacts_670.py` (G2 acceptance check).
- **Capabilities added/changed/affected:** capability:season-scale-run — the pilot's C→D→E→G→H→PANEL
  chain can now be driven over an arbitrary per-round driver grid against ONE shared consolidated
  slice DB; the runner itself is proven, the real 22-round compute is deferred to G2.
- **Constraints/assumptions touched:** offline-only (honored — no FastF1 call anywhere in the new
  code); no-tracked-db-write (honored — see Evidence); frozen-consumed-not-minted (honored — no
  frozen set touched); budget-is-run-param (honored — `SEASON_BUDGET_S=480` is a script-level
  default, not a frozen constant).
- **Decision candidates / resolved decisions:** decision:consolidated-slice (shared-DB
  accumulation via E's own `INSERT OR REPLACE`, keyed by `(year, gp_name, session_type, ...)` which
  differs per round — verified collision-free by construction and by test) was implemented exactly
  as specified — no hand-rolled merge exists anywhere in `run_season`.
- **Claims/evidence produced:** claim:plumbing-forwards-correctly (test
  `test_run_circuit_forwards_budget_s_and_refutil_db`, both override and default cases);
  claim:shared-db-accumulates-no-dup (test
  `test_shared_refutil_db_accumulates_across_rounds_no_drop_or_dup`, including a same-round rerun
  proving `INSERT OR REPLACE` idempotency); claim:vocabulary-guard-flags
  (`test_run_season_flags_divergent_vocabulary_round` + the direct
  `test_check_round_vocabulary_flags_divergent_k`); claim:tracked-db-never-written
  (`test_tracked_db_never_written_only_scratch_copy_is`, a `sqlite3.connect` guard that raises if
  the tracked path is ever opened).
- **Trust limitations / drift found:** the vocabulary guard is DETECTIVE, not PREVENTIVE — see
  Assumptions below; a downstream consumer of `season_results.json` must actually check
  `vocabulary_divergent`/`vocabulary_guard.flagged_rounds` rather than assume the pooled G/H fit
  was automatically corrected. This is a real, load-bearing caveat for G2/G3 consumers, not a
  documentation nit.
- **Triage candidates:** none raised this gate (the guard design gap above is recorded here for
  the next gate to consume, not filed as a separate issue, since it's explicitly anticipated by
  the handoff's own wording — "flag per-round at collection time").

## Test mode
**Required:** `test-after allowed`
**Satisfied:** yes — all new behavior is covered by `tests/unit/physics/pilot/test_season_runner.py`,
run and green before this gate closed; no real E or FastF1 call anywhere in the test file.

## Evidence

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot/test_season_runner.py -q
```
**Result:** pass — `15 passed in 0.76s`

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot -q
```
**Result:** pass — `44 passed in 9.12s` (29 pre-existing + 15 new; zero regressions)

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pyright src/physics/pilot/pipeline.py scripts/run_season_670.py scripts/verify_season_artifacts_670.py tests/unit/physics/pilot/test_season_runner.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations` (one pre-existing type-annotation fix
needed: `check_round_vocabulary`'s established-vocab param/return typed `Mapping[str, Any] | None`
throughout, not `dict[str, Any] | None`, since the `established` value flows through unchanged
without ever needing dict-only mutation)

**No-tracked-DB-write-path note:** `scripts/run_season_670.py` never imports `sqlite3` directly.
The tracked `f1_data_<year>.db` path (`src_db`, computed only inside `main()`) is passed to exactly
one call in the whole file — `shutil.copy(src_db, ...)` inside `copy_tracked_db_once` (a read of the
source) — never to `DatabaseManager(...)` or any DB-open call. `read_round_grid`'s
`DatabaseManager(db_path=db_path)` always receives the CALLER-supplied path (the scratch copy in
`main()`; a synthetic tmp-path DB in every test). Verified additionally by
`test_tracked_db_never_written_only_scratch_copy_is`, which monkeypatches `sqlite3.connect` to
raise if ever called against the tracked path, then runs the real copy + a real grid-read through
the scratch copy and asserts the tracked file's bytes are unchanged afterward.

## TDD evidence, if required
Test-after (handoff-sanctioned): all tests were written alongside the implementation and run green
together; no separate red-phase artifact was captured (not required by this test mode).

## Docs/contracts touched
- none — `docs/architecture/*` is out of scope for this gate (map fence, #671); no committed
  report schema or doc changed.

## Assumptions
- **Vocabulary guard is detective, not preventive.** `run_circuit`'s internal `run_stage_g` call
  pools across whatever the shared `refutil_db` already holds (via `map_version=None`) BEFORE the
  season script can inspect that round's own severity taxonomy (the taxonomy for round N is only
  knowable AFTER E writes round N's `reference_laps` row inside that same `run_circuit` call).
  Preventing the pool from ever running on a divergent round would require splitting E out of
  `run_circuit`'s single call — explicitly out of scope (`Do NOT modify the stage functions' logic
  ... or the fingerprint fit`). Per the handoff's own escape hatch ("flag per-round at collection
  time"), the guard reads each round's vocabulary back from the consolidated slice AFTER
  `run_circuit` returns and flags (`vocabulary_divergent: true`, `vocabulary_guard.flagged_rounds`)
  rather than silently trusting it. The round is still recorded as `covered` — it is FLAGGED, not
  hidden or dropped.
- **"Missing round/driver" = empty grid.** Implemented as one uniform check:
  `read_round_grid` returning an empty tuple (no `session_classifications` rows for that
  `(year, round_num, session_type)`) PARKS the round. This covers both "the round itself is
  missing" and "the round's driver grid is missing" in one path; no separate partial-grid
  threshold was invented (none was specified, and inventing one would be a guess outside this
  gate's authority).
- **`SEASON_BUDGET_S = 480`** is a script-level default (not a frozen constant), matching the
  handoff's "~480s" figure for a full 20-driver grid vs the pilot's ~180s/4-driver budget.
- **`round_idx` = 1-based position in `get_calendar(year)`'s list**, verified against the landed
  `PILOT_CIRCUITS` anchors (Monaco=6, Great Britain=10, Belgium=12) via a dedicated test
  (`test_build_season_slate_2023_has_22_rounds_matching_pilot_anchors`).
- **Driver grid reading uses `DatabaseManager.get_session_classification`** (per Allowed Scope's
  read-only reference to `src/data/database.py`'s getters), ordered by qualifying position.

## Stop conditions hit
- none — no scope exceedance, no frozen-set edit needed, no stage-logic change required to make
  shared-DB accumulation work (the existing `INSERT OR REPLACE` on a `gp_name`-inclusive primary
  key already made this collision-free), all required evidence was producible, no decision outside
  this gate's authority was needed.

## Out-of-scope observations
- The vocabulary guard's detective (not preventive) nature (see Assumptions) is a real design
  constraint G2/G3 consumers of `season_results.json` must respect — worth a one-line callout in
  whatever G2 runbook/report consumes this runner's output, so a human skimming the season run
  doesn't miss a flagged round buried in per-round JSON.
- `run_stage_panel` (PANEL slot, no hard gate) is exercised for real inside every `run_circuit`
  call in a live G2 run; it degrades gracefully on any exception (already true of the landed pilot
  code, unchanged here) — no action needed, just noting it's still in the season's critical path
  per-round.

## Workflow Feedback
- **Handoff gaps:** none blocking. One judgment call the handoff left implicit: whether the
  vocabulary guard should be preventive or merely detective given the "no stage-logic changes"
  exclusion — the handoff's own alternate phrasing ("read ... and compare before the join/fit
  stage, OR flag per-round at collection time") already anticipates and licenses the detective
  reading taken here, so this is a documented judgment call, not an unresolved gap.
- **Context rediscovered:** `src/data/database.py` is now the package `src/data/database/`
  (`_metadata_session.py` holds the getters, `manager.py`/`__init__.py` re-export
  `DatabaseManager`) — the handoff's file reference predates the package split; anchors should
  probably point at `src/data/database/_metadata_session.py` going forward.
- **Instructions improvised around:** none — the checklist-engine template's TDD red/green
  guidance was collapsed to the single test-after postcondition per the template's own instruction
  for this test mode.
- **What would have made this easier:** naming the exact `src/data/database` sub-module in the
  handoff's Map Anchors (see Context rediscovered above) would have saved one round of `Glob`/`Grep`
  discovery.

## Return status
`complete`
