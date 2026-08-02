# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` — REWORK attempt 2 (reopened after REVIEW BLOCK)

## Completed slice
Fixed `explain_stage` in `scripts/race_week_stages.py` (worktree
`C:/Programs/f1Brainz/.claude/worktrees/604-build`, branch `feat/604-race-week-build`) so that
constructing `explainer_path`/`stub_path` can never raise outside the function's own broad
`except Exception` handler, restoring its documented "never blocks the hard gate" contract for
any input, including a malformed `explainer_path` (`None`, `""`, or anything else). Added two
regression tests.

## Scope
**Files changed:**
- `scripts/race_week_stages.py` — `explain_stage` only (plus one new top-level `import tempfile`)
- `tests/unit/scripts/test_race_week_stages.py` — two new tests appended, nothing removed/rewritten

**Specific exclusions touched:** no. `scripts/race_week.py` not touched. No `src/` changes.
`discover_sessions_stage` / `predict_stage` / `optimize_stage` / checkpoint I/O helpers /
`compute_stage_inputs_hash` / `should_skip_stage` were not touched.

## Behavior changed
Yes. `explain_stage(lineup_output_stem, explainer_path)` no longer raises for a malformed
`explainer_path`. Previously `explainer_path = Path(explainer_path)` and
`stub_path = explainer_path.with_name(...)` executed **before** the `try:` block, so a bad
`explainer_path` (`None` -> `TypeError`, `""` -> `ValueError`) propagated uncaught. The fix:

1. Moved both lines **inside** the `try:` block, so any exception raised while constructing
   `explainer_path` or `stub_path` is now caught by the existing broad
   `except Exception as exc:` — same code path as a copy failure.
2. `stub_path` is *derived from* `explainer_path`, so if `explainer_path` construction itself
   fails there is nothing to derive `stub_path` from. Initialized `stub_path: Path | None = None`
   before the `try:`, and in the `except` branch, if `stub_path` is still `None`, fall back to a
   **fixed, always-constructible path**: `Path(tempfile.gettempdir()) / "race_week_explainer.STUB.md"`.
   Chose the OS temp dir (not the repo/cwd) specifically because `tempfile.gettempdir()` is
   guaranteed to exist and be writable on any supported platform, and never risks writing into
   the repository working tree as a side effect of a malformed-input failure path.
3. Added `import tempfile` to the module's stdlib imports.

The inner "even the stub write itself must not raise" `try/except: pass` guard was left
untouched — it already covers the fallback-path write the same way it covered the original one.

## Map Impact
Trivial local edit — no structural, capability, constraint, or decision impact beyond the bug fix
itself. `explain_stage`'s documented contract ("never raises, for any input") is now actually true
instead of aspirational; no seam/interface signature changed.

## Test mode
**Required:** `test-after` (bug fix with reviewer-diagnosed shape, per rework handoff)
**Satisfied:** yes — two new regression tests added covering `explain_stage(<valid stem>, None)`
and `explain_stage(<valid stem>, "")`; full test file re-run green (33/33, up from 31/31).

## Evidence

### Full pytest output — WHOLE test file, post-fix

```
$ py -m pytest tests/unit/scripts/test_race_week_stages.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Programs\f1Brainz\.claude\worktrees\604-build
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collecting ... collected 33 items

tests/unit/scripts/test_race_week_stages.py::test_write_then_read_checkpoint_roundtrip PASSED [  3%]
tests/unit/scripts/test_race_week_stages.py::test_read_checkpoint_missing_file_returns_none PASSED [  6%]
tests/unit/scripts/test_race_week_stages.py::test_compute_stage_inputs_hash_is_deterministic PASSED [  9%]
tests/unit/scripts/test_race_week_stages.py::test_compute_stage_inputs_hash_changes_with_content PASSED [ 12%]
tests/unit/scripts/test_race_week_stages.py::test_compute_stage_inputs_hash_is_sha256_hex PASSED [ 15%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_no_existing_checkpoint PASSED [ 18%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_existing_checkpoint_missing_hash PASSED [ 21%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_matching_hash_skips PASSED [ 24%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_stale_hash_reruns PASSED [ 27%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_complete_normal_weekend PASSED [ 30%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_partial PASSED [ 33%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_missing PASSED [ 36%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_sprint_weekend_shape PASSED [ 39%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_unknown_gp_raises PASSED [ 42%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_no_checkpoint_path_does_not_write PASSED [ 45%]
tests/unit/scripts/test_race_week_stages.py::test_predict_stage_builds_matching_namespace_and_calls_in_process PASSED [ 48%]
tests/unit/scripts/test_race_week_stages.py::test_predict_stage_never_defaults_db_path PASSED [ 51%]
tests/unit/scripts/test_race_week_stages.py::test_predict_stage_propagates_compound_normalizer_valueerror PASSED [ 54%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_does_not_import_write_beam_search_report PASSED [ 57%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_calls_generate_report_once_and_writes_lane_used PASSED [ 60%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_default_lane_is_balanced PASSED [ 63%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[max] PASSED [ 66%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[best_mean] PASSED [ 69%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[] PASSED [ 72%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[MEAN] PASSED [ 75%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[None] PASSED [ 78%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_embeds_stage_inputs_hash_of_upstream PASSED [ 81%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_copies_markdown_twin_on_success PASSED [ 84%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_missing_markdown_writes_stub_and_does_not_raise PASSED [ 87%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_unexpected_exception_never_raises PASSED [ 90%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_always_returns_a_dict_with_status PASSED [ 93%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_none_explainer_path_does_not_raise PASSED [ 96%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_empty_string_explainer_path_does_not_raise PASSED [100%]

============================= 33 passed in 0.21s ==============================
```

(Also captured via `-q`, separately, identical result: `33 passed in 0.23s`.)

### `simplification_limits` re-run

```
$ py -m src.utils.simplification_limits --paths scripts/race_week_stages.py
PASS (1 files checked)
```

**Result:** pass

## Before/after repro snippet

### Before (buggy code, reproduced live by temporarily reverting the fix)

```
>>> rws.explain_stage('some/stem', None)
Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r1 = rws.explain_stage('some/stem', None)
  File "...\scripts\race_week_stages.py", line 289, in explain_stage
    explainer_path = Path(explainer_path)
  File "...\pathlib\__init__.py", line 150, in __init__
    raise TypeError(...)
TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'

>>> rws.explain_stage('some/stem', '')
Traceback (most recent call last):
  File "<string>", line 3, in <module>
    r2 = rws.explain_stage('some/stem', '')
  File "...\scripts\race_week_stages.py", line 290, in explain_stage
    stub_path = explainer_path.with_name(f"{explainer_path.stem}.STUB{explainer_path.suffix}")
  File "...\pathlib\__init__.py", line 413, in with_name
    raise ValueError(f"{self!r} has an empty name")
ValueError: WindowsPath('.') has an empty name
```

This matches the reviewer's live reproduction in the rework handoff exactly (same exception
types/messages, same two source lines).

### After (fixed code)

```
>>> rws.explain_stage('some/stem', None)
{'status': 'stub', 'path': 'C:\\Users\\fredc\\AppData\\Local\\Temp\\race_week_explainer.STUB.md',
 'reason': "TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'"}

>>> rws.explain_stage('some/stem', '')
{'status': 'stub', 'path': 'C:\\Users\\fredc\\AppData\\Local\\Temp\\race_week_explainer.STUB.md',
 'reason': "ValueError: WindowsPath('.') has an empty name"}
```

Both calls now return a `dict` with `status == "stub"` and a `reason` explaining the underlying
exception, with no exception propagating to the caller.

## TDD evidence, if required
Test-after mode (per rework handoff, "bug fix with reviewer-diagnosed shape") — no RED step
required. New tests were written directly against the fixed code and confirmed green; the failing
(pre-fix) behavior was independently confirmed via the before/after repro above rather than via a
by-design-failing pytest run.

- Failing test observed: N/A (test-after mode) — bug behavior confirmed failing via direct repro,
  see "Before" above.
- Passing test observed: `py -m pytest tests/unit/scripts/test_race_week_stages.py -q` -> `33 passed`.
- Refactor while green: no refactor beyond the fix itself was needed.

## Docs/contracts touched
- none — `explain_stage`'s docstring already documented the "never raises" contract; behavior now
  matches the doc instead of the doc needing a change.

## Assumptions
- Fallback stub path chosen as `Path(tempfile.gettempdir()) / "race_week_explainer.STUB.md"` when
  `explainer_path` itself cannot be constructed into a `Path`. Rationale: `tempfile.gettempdir()`
  is guaranteed writable and always constructible (it does not depend on the malformed input at
  all), and deliberately is NOT the repo/cwd, so a malformed-input failure path can never write
  into the working tree.
- Regression tests monkeypatch `rws.tempfile.gettempdir` to point at a `tmp_path` subdirectory so
  the tests stay hermetic (they do not write into the real OS temp dir) while still exercising and
  verifying the real fallback code path.

## Stop conditions hit
- none. The fix stayed entirely inside `explain_stage`; no deeper design problem in the checkpoint
  I/O helpers was uncovered.

## Out-of-scope observations
- none.

## Workflow Feedback
- **Handoff gaps:** none — the rework handoff's Close Criteria section gave the exact fix shape
  (move construction inside `try`, add a hardcoded fallback for when `explainer_path` itself can't
  be constructed) and the exact reviewer repro to match; nothing needed re-deriving.
- **Context rediscovered:** none — `docs/agents/CREW_CONTEXT.md` and the module's own docstring
  were sufficient; no additional digging was needed beyond reading the current source at the cited
  line numbers (which had drifted by exactly one line from the handoff's `288-289` to `289-290` in
  this worktree's checked-out state, presumably from unrelated formatting — trivial, did not affect
  the fix).
- **Instructions improvised around:** none.
- **What would have made this easier:** none — this rework handoff was tightly scoped and the fix
  shape was unambiguous; nothing to improve here.

## Return status
`complete`
