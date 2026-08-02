# Implementer Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`tc3: backfill_estimate_store.py missing session_type (Admiral cleanup ruling)`

## Completed slice
Threaded `session_type=session_type` and `db_path=str(Config.db_path_for_year(year))` into the
`estimate_session(...)` call inside `scripts/backfill_estimate_store.py::backfill_year` (was lines
140-143, omitting both) — mirrors `estimate_batch.run_estimate_batch`'s already-fixed
`session_type=session_type` threading (`src/physics/layer2/estimate_batch.py` lines 84-87), and
additionally threads `db_path` so `estimate_session`'s FP-mass-resolution seam
(`_resolve_session_mass` → `_resolve_fp_mass`, gained in #513 g5) can read the season DB. Before the
fix, a real FP backfill silently fell back to `quali_mass(year)` because `session_type` never reached
`_resolve_session_mass`'s `session_type.startswith("FP")` branch.

## Scope
**Files changed:**
- `scripts/backfill_estimate_store.py` — added `from src.utils.config import Config` import; added
  `session_type=session_type, db_path=str(Config.db_path_for_year(year))` to the `estimate_session(...)`
  call in `backfill_year`.
- `tests/unit/physics/layer2/test_backfill_estimate_store.py` — new RED-first capture test (2 tests:
  FP2 and default-Q).
- `tests/unit/scripts/test_backfill_estimate_store.py` — extended `_fake_estimate` and the local
  `flaky_estimate` fixture to accept the two new kwargs (`session_type=None, db_path=None`,
  accepted-and-ignored) so the pre-existing 9-test suite keeps passing after the real call gained them.

**Specific exclusions touched:** yes — `tests/unit/scripts/test_backfill_estimate_store.py` is outside
the handoff's literal Allowed Scope (`scripts/backfill_estimate_store.py` + a test file under
`tests/unit/physics/layer2/`). It required a minimal, additive-only touch (two fixture signatures
gained optional kwargs, no assertions changed) because the handoff's own Close Criteria required
"existing backfill tests green," and that file's fake would otherwise reject the new kwargs with a
`TypeError`. See Workflow Feedback.

## Behavior changed
Yes. `backfill_year` (and therefore `run_backfill`/`main`) now passes `session_type` and `db_path`
through to `estimate_session` on every call. Default/Q behavior is unchanged in outcome (verified by
`test_q_backfill_default_session_type_and_db_path_unchanged`): `session_type="Q"` still resolves via
`quali_mass(year)` inside `estimate_session` regardless of `db_path` being non-`None`, because
`_resolve_session_mass` only consults `db_path` on the `session_type.startswith("FP")` branch. A real FP
backfill (`--session-type FP1/FP2/FP3`) will now correctly resolve FP mass via
`_resolve_fp_mass`/`extract_fp_lap_latent` instead of silently using `quali_mass`.

## Map Impact
- **Structural anchors touched:** `scripts/backfill_estimate_store.py::backfill_year` — call-site fix,
  no signature/shape change to the function itself.
- **Capabilities added/changed/affected:** FP backfill via `scripts/backfill_estimate_store.py
  --session-type FP1/FP2/FP3` now actually resolves FP mass (previously silently used `quali_mass`) —
  this is the fix that "unblocks a clean #646 re-pop" per the handoff.
- **Constraints/assumptions touched:** relies on the existing `Config.db_path_for_year(year)` →
  `data/f1_data_{year}.db` convention (already used identically by `scripts/backfill_weather.py`,
  `scripts/backfill_compound_c_number.py`, `scripts/race_week.py`, etc.) — no new convention introduced.
- **Claims/evidence produced:** RED→GREEN pair in
  `tests/unit/physics/layer2/test_backfill_estimate_store.py` proving the bug existed and is fixed;
  9/9 green in the pre-existing `tests/unit/scripts/test_backfill_estimate_store.py`.
- **Triage candidates:** none — this was the single, fully-scoped fix named by the Admiral cleanup
  ruling.

## Test mode
**Required:** `test-first (TDD, RED-first)`
**Satisfied:** yes — new test written and run against the unfixed script first (observed RED), then the
fix applied, then the same test re-run (observed GREEN).

## Evidence

```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_backfill_estimate_store.py tests/unit/scripts/test_backfill_estimate_store.py -q
```
**Result:** `11 passed in 1.84s` (2 new + 9 pre-existing).

```bash
cd /c/Programs/f1-513 && py -m src.utils.simplification_limits --baseline --paths scripts/backfill_estimate_store.py
```
**Result:** `PASS (1 files checked)`

```bash
cd /c/Programs/f1-513 && git status --short data/
```
**Result:** empty output — clean, no `data/*.db` writes/reads during this run.

## TDD evidence, if required

- Failing test observed (pre-fix, against the unfixed `estimate_session(...)` call):
  ```
  tests\unit\physics\layer2\test_backfill_estimate_store.py:95: in test_fp_backfill_threads_session_type_and_db_path_into_estimate_session
      assert captured["session_type"] == "FP2"
  E   AssertionError: assert None == 'FP2'
  ...
  tests\unit\physics\layer2\test_backfill_estimate_store.py:112: in test_q_backfill_default_session_type_and_db_path_unchanged
      assert captured["session_type"] == "Q"
  E   AssertionError: assert None == 'Q'
  ============================== 2 failed in 1.89s ==============================
  ```
- Passing test observed (post-fix):
  ```
  tests\unit\physics\layer2\test_backfill_estimate_store.py ..             [ 18%]
  tests\unit\scripts\test_backfill_estimate_store.py .........             [100%]
  ============================= 11 passed in 1.84s ==============================
  ```
- Refactor while green: no — one-line-scoped fix, no refactor needed.

## Docs/contracts touched
- none — no interface/contract shape changed; `estimate_session`'s signature was already extended by
  #513 g5 before this task started.

## Assumptions
- `Config.db_path_for_year(year)` is the correct per-year season-DB path to hand `estimate_session` for
  FP mass resolution — confirmed by cross-referencing the identical pattern in
  `scripts/backfill_weather.py`, `scripts/backfill_compound_c_number.py`, `scripts/race_week.py`, and the
  production usage proof in `tests/unit/physics/layer2/test_session_estimator_fp.py::test_fp_session_with_db_path_uses_fastest_clean_lap_through_full_estimate_session`.

## Stop conditions hit
- none.

## Out-of-scope observations
- none beyond the fixture-touch already logged under Scope/Workflow Feedback.

## Workflow Feedback

- **Handoff gaps:** the Allowed Scope list (`scripts/backfill_estimate_store.py` + a test file under
  `tests/unit/physics/layer2/`) didn't anticipate that fixing the call signature would break the
  *pre-existing* fake in `tests/unit/scripts/test_backfill_estimate_store.py` (its `_fake_estimate` and
  local `flaky_estimate` had fixed keyword-only params with no `**kwargs`, so adding `session_type=`/
  `db_path=` to the real call would raise `TypeError` there). The Close Criteria's "existing backfill
  tests green" implicitly required touching that file too. Worth naming explicitly in future
  session_type/db_path-style call-signature handoffs: "also extend any fake in existing test suites
  whose signature doesn't already accept the new kwarg."
- **Context rediscovered:** had to independently confirm the `db_path` convention
  (`Config.db_path_for_year(year)` → `data/f1_data_{year}.db`) by grepping sibling scripts and the FP
  production test (`test_session_estimator_fp.py`) — the handoff named that `estimate_session` "gained
  db_path" but not which value a backfill script should supply. Worth a one-line pointer in future
  handoffs when a new required-for-correctness kwarg has an established repo convention.
- **Instructions improvised around:** none — the engine/plan/template mechanics fit the task cleanly.
- **What would have made this easier:** naming the `Config.db_path_for_year` convention directly in the
  handoff's Close Criteria (it was discoverable but took a few greps to nail down with confidence).

## Return status
`complete`
