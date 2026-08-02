# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` (513-fp-fits — cumulative_track_laps unlock, execute.json gate g3-implement)

## Completed slice
Landed the per-car `cumulative_track_laps` unlock into `session_estimates`, in three parts per the
handoff: (1) an additive, self-healing `EstimateRecord.cumulative_track_laps` column; (2) a
`session_cumulative_track_laps` helper in `session_race.py` that resolves the constructor's
representative (fastest clean) lap and reuses `compute_cumulative_track_laps` unchanged; (3) an
optional `record_from_estimate` kwarg plus a demo-scoped `populate_cumulative_track_laps_for_demo`
helper. No real backfill was run; `data/` is untouched.

## Post-review fix (g3 review BLOCK resolution)
The review returned BLOCK on one finding: my test additions pushed
`tests/unit/physics/layer2/test_estimate_store.py` over the project's `simplification_limits`
1000-line file gate (888 -> 1005 lines). Fix applied: split the five NEW `#513 G3
cumulative_track_laps` test functions (self-heal, default-None, kwarg round-trip, two
demo-populate tests) into a new companion file
`tests/unit/physics/layer2/test_estimate_store_cumulative.py`, mirroring the repo's existing
companion-test-file precedent (e.g. `test_cross_view.py` alongside `estimate_store`'s other
split-out test concerns) and matching `test_estimate_batch.py`'s own local-fixture-copy pattern
(the new file carries local copies of `_view`/`_fake_estimate`/`_make_legacy_table` rather than
importing across test files -- no cross-test-file coupling was introduced). Result:
`test_estimate_store.py` is now 895 lines, `test_estimate_store_cumulative.py` is 194 lines, both
under the 1000-line gate. `session_race.py`'s pre-existing test-file violation (1563 lines before
this gate, 1678 lines now) was explicitly left untouched per the review's own instruction (out of
scope for g3) -- it was already over the limit before any g3 work began.
`session_race.py`'s pre-existing `test_fit_quality_metadata_populated_and_round_trips` cyclomatic-
complexity=26 finding is likewise pre-existing (confirmed via `--baseline`, grandfathered) and was
not introduced by this gate; left untouched.

## Scope
**Files changed:**
- `src/physics/layer2/estimate_store.py` — `EstimateRecord.cumulative_track_laps` field (next to
  `mass_kg_assumed`); `record_from_estimate(..., cumulative_track_laps=None)` optional kwarg;
  `populate_cumulative_track_laps_for_demo(store_path, db_path, weekends)`.
- `src/physics/layer2/session_race.py` — `_constructor_drivers`, `_fastest_clean_lap_number`
  (private helpers), `session_cumulative_track_laps` (public). `compute_cumulative_track_laps`
  itself is **byte-unchanged** — confirmed via `git diff` (no hunk touches it).
- `tests/unit/physics/layer2/test_estimate_store.py` — extended, then the #513-specific block was
  moved out to the companion file below (post-review fix); net +7 lines (a pointer comment).
- `tests/unit/physics/layer2/test_estimate_store_cumulative.py` — **new file** (post-review fix):
  the five #513 G3 tests (self-heal, default-None, kwarg round-trip, two demo-populate tests) plus
  local fixture copies, split out to satisfy the file_lines gate.
- `tests/unit/physics/layer2/test_session_race.py` — extended `_make_db`/`_insert_laps` with a
  `session_classifications` table + `lap_time` column + a new `_insert_classification` helper,
  plus a `TestSessionCumulativeTrackLaps` class (5 tests).

**Specific exclusions touched:** no — did not run any real backfill/estimate_batch over real
data, did not touch `session_estimator.py` or the views, never opened any `data/*.db` (all tests
use `tmp_path` sqlite copies), `compute_cumulative_track_laps` unmodified.

## Behavior changed
Yes, additively: `EstimateRecord` gains one new field (default `None`, self-heals on legacy DBs);
`record_from_estimate` gains one new optional kwarg (default `None`, so every existing call site —
including `estimate_batch.py`, which passes no such kwarg — is byte-identical); two new functions
exported from `session_race.py` and `estimate_store.py`. No existing behavior changed for any
default-arg caller (verified: full `test_estimate_batch.py` still green unmodified).

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — `estimate_store.py::EstimateRecord`
  gains `cumulative_track_laps`; `estimate_store.py::record_from_estimate` gains an optional
  kwarg; `estimate_store.py::populate_cumulative_track_laps_for_demo` is a new module-level
  function; `session_race.py::compute_cumulative_track_laps` is the reused (unchanged) seam;
  `session_race.py::session_cumulative_track_laps` is a new public function (plus two new private
  helpers `_constructor_drivers`/`_fastest_clean_lap_number`).
- **Capabilities added/changed/affected:** new capability — a caller can now ask "how much rubber
  had this constructor's cars seen, as of their representative lap, in session X" without a whole-
  store backfill. This is the capability #626 (within-session evolution latent) was blocked on.
- **Constraints/assumptions touched:** `constraint: DB hygiene #632` — honored (no `data/*.db`
  read/written by this gate; `git status --short data/` confirmed empty). `assumption:
  cumulative_track_laps definition` — implemented exactly as DECIDED in the handoff (rubber-at-
  representative-lap, FIELD laps not own-car laps, "lap_number < anchor" convention) — no
  deviation.
- **Decision candidates / resolved decisions:** `decision: constructor->driver resolution seam` —
  `lap_times` carries no team/constructor column, so `_constructor_drivers` resolves via
  `session_classifications.team` (best-effort, returns `[]` on absence, never raises). This seam
  choice was not spelled out in the handoff; flagged here for Cartographer/Commander visibility
  since #646 (the real backfill) will depend on this same resolution path and its coverage of
  `session_classifications` for the target weekends.
- **Trust limitations / drift found:** none found; both target modules and their test files read
  cleanly and matched the described precedent (`mass_kg_assumed` self-heal pattern).
- **Triage candidates:** the demo populate helper's constructor->driver resolution depends on
  `session_classifications` being populated for the same (year, gp, session_type) the caller
  names — #646 (real backfill) should confirm/verify that coverage before relying on this path at
  scale; not a defect here (demo-scoped, as required), just a forward dependency worth flagging.

## Test mode
**Required:** `test-first (TDD)`
**Satisfied:** yes — every slice (m1 schema field, m2 session helper, m3 kwarg+populate) was
red-observed before implementation, per the plan's TDD postconditions.

## Evidence

```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_session_race.py tests/unit/physics/layer2/test_estimate_batch.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-513
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 131 items

tests\unit\physics\layer2\test_estimate_store.py ....................... [ 17%]
..............................                                           [ 40%]
tests\unit\physics\layer2\test_session_race.py ......................... [ 59%]
...............................................                          [ 95%]
tests\unit\physics\layer2\test_estimate_batch.py ......                  [100%]

============================= 131 passed in 6.10s =============================
```

```bash
cd /c/Programs/f1-513 && git status --short data/
```
Output: **empty** (nothing to show — `data/` untouched).

**Result:** pass.

### Post-review fix evidence (file split)

```bash
cd /c/Programs/f1-513 && wc -l tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_estimate_store_cumulative.py
```
```
  895 tests/unit/physics/layer2/test_estimate_store.py
  194 tests/unit/physics/layer2/test_estimate_store_cumulative.py
```

```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_estimate_store_cumulative.py tests/unit/physics/layer2/test_session_race.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-513
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 125 items

tests\unit\physics\layer2\test_estimate_store.py ....................... [ 18%]
.........................                                                [ 38%]
tests\unit\physics\layer2\test_estimate_store_cumulative.py .....        [ 42%]
tests\unit\physics\layer2\test_session_race.py ......................... [ 62%]
...............................................                          [100%]

============================= 125 passed in 6.46s =============================
```
125 total = same as before the split (48 + 5 new #513 tests + 72 session_race, previously
53 + 72 = 125) — no test was lost or duplicated by the split.

```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_estimate_store_cumulative.py tests/unit/physics/layer2/test_session_race.py
```
```
FAIL (2 violations, 3 files checked)
tests/unit/physics/layer2/test_estimate_store.py test_fit_quality_metadata_populated_and_round_trips: cyclomatic_complexity=26 (limit: <20)
tests/unit/physics/layer2/test_session_race.py: file_lines=1678 (limit: <1000)
```
Both remaining findings are **pre-existing, not introduced by this gate** (confirmed: the
complexity finding is grandfathered under `--baseline`; `test_session_race.py` was already 1563
lines at `HEAD` before any g3 edits — over the limit before this gate started, out of scope per
the review's own instruction). The **file_lines violation this gate introduced** is resolved —
confirmed narrowly:
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_estimate_store_cumulative.py --file-lines-only
```
```
PASS (2 files checked)
```

```bash
cd /c/Programs/f1-513 && git status --short data/
```
Output: **empty** — `data/` still untouched after the fix.

## TDD evidence, if required

- **m1 (schema field) red:** `PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_estimate_store.py -q -k cumulative_track_laps` →
  ```
  AssertionError: assert 'cumulative_track_laps' in {'A0_status', ...}
  AttributeError: 'EstimateRecord' object has no attribute 'cumulative_track_laps'
  2 failed, 48 deselected
  ```
  green after implementing: `2 passed, 48 deselected`.
- **m2 (session helper) red:** `PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_session_race.py -q -k cumulative_track_laps` →
  ```
  ImportError: cannot import name 'session_cumulative_track_laps' from 'src.physics.layer2.session_race'
  1 error during collection
  ```
  green after implementing (verified via the accurate selector, since the plan's `-k
  cumulative_track_laps` under-selects — see Workflow Feedback): `-k SessionCumulativeTrackLaps` →
  `5 passed, 67 deselected`.
- **m3 (kwarg + demo populate) red:** `PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_estimate_store.py -q -k "kwarg_round_trips or populate_cumulative_track_laps"` →
  ```
  TypeError: record_from_estimate() got an unexpected keyword argument 'cumulative_track_laps'
  AttributeError: module 'src.physics.layer2.estimate_store' has no attribute 'populate_cumulative_track_laps_for_demo'
  3 failed, 50 deselected
  ```
  green after implementing: full `test_estimate_store.py` → `53 passed` (pre-split count; those
  same 5 #513 tests now live in `test_estimate_store_cumulative.py` post-review-fix — see the
  Post-review fix evidence block above for the post-split 125-total re-verification).
- **Refactor while green:** the post-review file split (moving the 5 #513 tests + local fixture
  copies into a new companion file) is the one refactor-while-green pass this gate took — done
  after all tests were green, verified not to change the green count (125 before == 125 after).

## Docs/contracts touched
- none beyond the two modules' own docstrings (both `EstimateRecord.cumulative_track_laps` and
  `session_cumulative_track_laps` carry inline docstrings documenting the pooling approximation,
  per the handoff's explicit requirement). No `docs/` files touched.

## Assumptions
- The constructor->driver mapping for `session_cumulative_track_laps` is resolved via
  `session_classifications.team` (exact string match against the `constructor` argument), since
  `lap_times` carries no team/constructor column and the handoff did not name a specific
  resolution seam. This mirrors the existing `session_classifications` schema and is the same
  table the evo_predictor's DB layer already treats as the per-driver team source of truth.
- "Clean lap" for the representative-lap anchor is read literally from the handoff's own
  parenthetical — `valid_lap=1` only (not the four-condition `_is_clean` used elsewhere in
  `session_race.py` for the race-stint smoother path, which also requires no pit-in/out and
  `track_status='1'`). The handoff explicitly wrote "fastest clean (`valid_lap=1`) lap," equating
  the two terms in this context, so I took that as the intended, narrower definition rather than
  importing the race-side four-condition filter.
- `populate_cumulative_track_laps_for_demo` only ever UPDATEs rows that already exist in
  `session_estimates` for the named weekend; it never creates rows and never invokes
  `estimate_batch`/`estimate_session`. This matches "demo-scoped populate only — NO real backfill"
  literally: it is a thin, targeted write over already-fitted rows.

## Stop conditions hit
- none. Scope was not exceeded, no real backfill was required, and the self-heal stayed additive
  throughout (confirmed against the `mass_kg_assumed` precedent).

## Out-of-scope observations
- `estimate_batch.py`'s `_group_by_team` derives constructor pairs from the live FastF1 `session`
  object (`_list_drivers`), not from `session_classifications`. My new
  `_constructor_drivers`/`session_cumulative_track_laps` deliberately uses the DB-only
  `session_classifications` seam instead (physics-region: no fastf1 imports). These two
  constructor-resolution paths are NOT guaranteed to agree in every edge case (e.g. a
  classification row with a different `team` spelling than FastF1's `TeamName`, or a session
  missing from `session_classifications` but present in FastF1). Worth a triage note for #646 (the
  real backfill) to verify `session_classifications` coverage/naming consistency against
  `estimate_batch`'s constructor keys for every target weekend before relying on this seam at
  scale — not a defect in this gate (demo-scoped, explicit in the docstring), just a forward risk.

## Workflow Feedback
- **Handoff gaps:** the handoff's file path `tests/unit/physics/test_estimate_store.py` does not
  exist — the actual (and only) test file is `tests/unit/physics/layer2/test_estimate_store.py`
  (confirmed via `find`/`Glob`; the handoff's "Verification Commands" block has the same stale
  path). I used the real path throughout and the same correction likely needs to propagate to any
  other g3-adjacent docs.
- **Context rediscovered:** the handoff's "reusing `compute_cumulative_track_laps`" language
  implies the count is straightforward, but nothing in the handoff names WHERE a constructor's
  driver list comes from for a DB-only (non-FastF1) call — `lap_times` has no team column. I had
  to trace `estimate_batch.py`'s `_group_by_team`/`_list_drivers` (FastF1-based, not usable here
  under the physics-region constraint) before finding `session_classifications.team` as the only
  DB-native seam. Worth naming explicitly in a future handoff for this same axis.
- **Instructions improvised around:** my own plan's `m2-session-helper` postcondition `c2` used a
  command check `-k cumulative_track_laps`, which — because my new test class is named
  `TestSessionCumulativeTrackLaps` (CamelCase, no underscores) — only matched 2 of the 5 new
  tests by substring. I did not hand-edit the checklist JSON's check text (that would blur "fix a
  check" into "game a check"); instead I independently ran the accurate selector
  (`-k SessionCumulativeTrackLaps`, confirmed 5/5 green), `attach`ed a note documenting the gap and
  the broader run as evidence (`e-m2-session-helper-1`), and let the literal (narrower but still
  truthful) check pass on its own — then had `m4-evidence`'s full-file run re-verify everything as
  the authoritative final check. No check was faked; the plan-authoring imprecision is now
  documented in both the engine's evidence trail and here.
- **What would have made this easier:** when authoring a plan's command-check `-k` filter, match
  it against the test file's actual naming convention (class vs. function, CamelCase vs.
  snake_case) BEFORE writing the check text — I should have grepped the target test file's
  existing class-naming style first rather than assuming a snake_case substring would catch a new
  `Test<CamelCase>` class.
- **Missed check (post-review):** my own plan's `m4-evidence` gate never ran
  `py -m src.utils.simplification_limits` on the touched paths, even though `docs/agents/
  CREW_CONTEXT.md` names it an explicit review blocker ("Review blocker when skipped or failing on
  in-scope Python"). My plan authoring pulled the required-evidence list straight from the
  handoff's own "Required Evidence" section, which itself didn't name this check — the handoff
  under-specified a project-wide gate that CREW_CONTEXT.md makes mandatory. For future handoffs
  touching `tests/` or `src/`, the plan's evidence gate should always include the simplification
  check by default (baseline mode at minimum, strict `--paths` on touched files ideally),
  independent of whether the handoff happens to mention it — CREW_CONTEXT.md already makes it
  universal, so a handoff's silence on it should never be read as "skip it."

## Return status
`complete`
