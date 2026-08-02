# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` (rework 1) — per-round fault isolation in the season runner (epic #659 Wave 6, #670 season-scale run)

## Completed slice
Wrapped each round's `run_circuit_fn(...)` call (and its subsequent `check_round_vocabulary`) in
`scripts/run_season_670.py::run_season` in a `try/except Exception`. On any exception the round is
now PARKED — `status="parked"`, `reason=f"round failed at run_circuit: {type(exc).__name__}: {exc}"`,
`round_idx` recorded, circuit appended to `parked_rounds` — and the loop `continue`s to the next
round instead of letting the exception propagate and kill the whole season. This was the root cause
found at g2-run first launch: round 1 (Bahrain) has no strictly-prior sessions, so E emits only ERROR
rows, `reference_laps` has no `severity:*` classes, and `derive_pilot_vocabulary([])` raises inside
`run_circuit` — previously fatal to all 22 rounds.

## Scope
**Files changed:**
- `scripts/run_season_670.py` (`run_season` loop only — added the try/except around the existing
  `run_circuit_fn` + `check_round_vocabulary` block; nothing else in the file touched)
- `tests/unit/physics/pilot/test_season_runner.py` (2 new tests added)

**Specific exclusions touched:** no — `src/physics/pilot/pipeline.py`, frozen sets, stage/gating
logic, the panel, join, and fingerprint fit were not touched; no real season compute was run;
`docs/architecture/*` untouched.

## Behavior changed
Yes. `run_season` no longer propagates an exception raised by `run_circuit_fn` (or by
`check_round_vocabulary` on its result) — that round is parked with a diagnostic reason instead, and
every other round in the slate still runs. The pre-existing empty-driver-grid park path is unchanged
(separate branch, taken before `run_circuit_fn` is ever called, with its own unmodified reason text
`"no session_classifications rows for ..."`), so the two park reasons remain distinguishable by a
downstream reader of `season_results.json`.

## Map Impact
- **Structural anchors touched:** `scripts/run_season_670.py::run_season` — the per-round loop body
  now has two distinct park paths: (1) pre-existing empty-grid park (before `run_circuit_fn` runs),
  (2) NEW run-failure park (`try/except` around `run_circuit_fn` + `check_round_vocabulary`,
  `reason` names the exception type + message).
- **Capabilities added/changed/affected:** capability:season-scale-run gains fault isolation — a
  single round's stage failure (e.g. round 1/2 lacking strictly-prior data) no longer kills the
  unattended overnight G2 run; the season completes over every working round regardless of how many
  early/thin rounds park.
- **Constraints/assumptions touched:** offline-only (honored, unchanged); no-tracked-db-write
  (honored, unchanged — this rework touches no DB-path logic); "a per-round failure PARKS, never
  crashes the season" (the constraint this rework directly satisfies, per the handoff's Map Anchors).
- **Decision candidates / resolved decisions:** decision:round1-2-genuinely-park (round 1/2 legitimately
  lack strictly-prior data per the handoff's own root-cause finding; parking them is correct, honest
  behavior — NOT a bug to "fix" by inventing fallback data) was implemented exactly as specified; no
  attempt was made to give E synthetic prior-session data.
- **Claims/evidence produced:** claim:round-failure-parks-and-continues
  (`test_run_season_parks_round_that_raises_and_continues` — 3-round slate, round 1 raises, rounds
  2-3 still covered, round 1's reason names the exception type+message, `run_season` itself never
  raises); claim:park-reasons-distinguishable
  (`test_run_season_run_failure_park_distinguishable_from_empty_grid_park` — one round parks via the
  old empty-grid path, the other via the new run-failure path, asserted on the differing reason text).
- **Trust limitations / drift found:** none new — the vocabulary-guard detective-not-preventive
  caveat recorded in the original G1 result still applies unchanged; this rework does not touch that
  logic.
- **Triage candidates:** none raised this gate.

## Test mode
**Required:** `test-first (TDD red -> green)` per the handoff's Close Criteria ("New test ... a
`run_circuit_fn` that RAISES for one round ... succeeds for others").
**Satisfied:** yes — both new tests were written first and observed failing (RED) against the
pre-fix `run_season` (the exception propagated uncaught out of `pytest`, which is the correct RED
signature for this change — there was no partial/wrong-value failure mode to assert against, only
"crashes vs. doesn't crash"), then the try/except was implemented and both tests observed passing
(GREEN), confirmed by the full test-file run below.

## Evidence

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot/test_season_runner.py -q
```
**Result:** pass — `17 passed in 0.84s` (15 pre-existing + 2 new; zero regressions)

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/pilot -q
```
**Result:** pass — `46 passed in 9.11s` (44 pre-existing across the whole pilot suite + 2 new)

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pyright scripts/run_season_670.py tests/unit/physics/pilot/test_season_runner.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations`

## TDD evidence, if required
- Failing test observed (RED, pre-fix): both `test_run_season_parks_round_that_raises_and_continues`
  and `test_run_season_run_failure_park_distinguishable_from_empty_grid_park` raised their injected
  `ValueError`/`RuntimeError` straight through `pytest` (`2 failed, 15 deselected in 0.54s` when
  filtered to just the two new tests), because pre-fix `run_season` had no try/except around
  `run_circuit_fn` — confirms the exception genuinely propagates without the fix.
- Passing test observed (GREEN, post-fix): `tests/unit/physics/pilot/test_season_runner.py -q` ->
  `17 passed in 0.84s`.
- Refactor while green: no refactor needed — the change is a single localized try/except; the
  surrounding loop body was reindented one level with no logic edits inside the block.

## Docs/contracts touched
- none — `docs/architecture/*` out of scope for this gate (map fence, #671); no committed report
  schema or doc changed. `season_results.json`'s shape gained no new top-level keys (a run-failure
  park uses the same `{status, round_idx, reason}` shape as the existing empty-grid park; both land
  in the existing `rounds`/`parked_rounds` structure).

## Assumptions
- **A run-failure park reuses the existing `{status, round_idx, reason}` round-entry shape** (no
  `n_drivers`/`vocabulary`/`result` keys, since the round never reached the point where those values
  exist) — matching the existing empty-grid park entry's shape exactly, so a consumer already
  handling `status=="parked"` needs no new branch, only the `reason` text differs.
- **One shared `parked_rounds` list** (not a separate "failed" list) records both park kinds, per the
  handoff's explicit "(or a sibling list)" latitude and the Close Criteria's requirement that
  `season_results.json` "remains well-formed with covered + parked rounds both present" — a single
  list already satisfies that with no schema growth. A reader distinguishes the two kinds by
  inspecting each round's own `reason` text (`"no session_classifications rows"` vs `"round failed at
  run_circuit:"`), which is exactly the distinguishability the Close Criteria asks for.
- **`except Exception` (not a narrower type)** — the handoff says "On ANY exception from a round,
  PARK that round," and the discovered failure modes span at least `ValueError`
  (`derive_pilot_vocabulary([])`) and a data-shape error from E ("array of sample points is empty");
  a narrower catch would risk missing the next round-2-style failure the handoff explicitly wants
  covered.

## Stop conditions hit
- none — isolating per-round failures required no change to `run_circuit` or E; the catch lives
  entirely at the `run_season` loop level as instructed.

## Out-of-scope observations
- none new — see the original G1 result's vocabulary-guard caveat, unchanged by this rework.

## Workflow Feedback
- **Handoff gaps:** none blocking. The handoff's example diagnosis text
  (`f"round failed at run_circuit: {type(exc).__name__}: {exc}"`) was followed verbatim rather than
  paraphrased, since it was given as a literal f-string, not just an illustrative shape.
- **Context rediscovered:** none beyond what the handoff's own root-cause section (round
  1 = `derive_pilot_vocabulary([])` raises; round 2 = "array of sample points is empty") already
  supplied — no additional digging was needed to write realistic synthetic exceptions for the tests.
- **Instructions improvised around:** none. The TDD red step for this change has no meaningfully
  "wrong value" failure mode (pre-fix, the round just crashes the whole process) — the RED evidence
  is "test raises the injected exception uncaught," which is what got captured above instead of a
  conventional assertion-failure traceback; flagging this in case a future reviewer expects a
  standard `assert ... == ...` AssertionError as the RED artifact.
- **What would have made this easier:** nothing — this handoff was unusually precise (literal
  f-string, exact test file, exact scope line range) and needed no clarification.

## Return status
`complete`
