# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` (issue #604, race-week staged pipeline — Candidate C design)

## Completed slice
Built `scripts/race_week_stages.py` in the worktree `C:/Programs/f1Brainz/.claude/worktrees/604-build`:
checkpoint read/write helpers, `compute_stage_inputs_hash`, `should_skip_stage`, and the four pure
stage functions (`discover_sessions_stage`, `predict_stage`, `optimize_stage`, `explain_stage`) for
the `race-week` staged pipeline. All four stage functions are unit-tested as pure functions over
fixture checkpoint dicts in `tests/unit/scripts/test_race_week_stages.py` (31 tests, all mocking
`DatabaseManager`/`cmd_sampled_predict`/`generate_report` — no real DB, FastF1, or model inference).
`scripts/race_week.py` (the CLI, G2) was NOT created, per the handoff's exclusion.

## Scope
**Files changed:**
- `scripts/race_week_stages.py` (new)
- `tests/unit/scripts/test_race_week_stages.py` (new)

**Specific exclusions touched:** no — `scripts/race_week.py` was not created (even as a stub);
no `src/` files were touched; `write_beam_search_report` is never imported/called directly by this
module (verified below).

## Behavior changed
Yes — new capability. `scripts/race_week_stages.py` did not exist before; it now provides the
library core the future `scripts/race_week.py` CLI (G2) will drive: session-shape discovery against
landed data, in-process `sampled-predict` invocation, beam-search lineup optimization with a
lane-restricted selection, and a best-effort explainer copy that never blocks the hard gate.

## Map Impact
- **Structural anchors touched:** `struct:scripts` (script-level, no Cartographer map node) — new
  file `scripts/race_week_stages.py`; consumes `struct:evo_predictor` (`run.py:cmd_sampled_predict`,
  unmodified) and `struct:fantasy_scoring` (`artifacts.py:generate_report`, unmodified) exactly as
  the seam design anticipated. No new `src/` package, no new map-visible structural node.
- **Capabilities added/changed/affected:** session-shape discovery + partial-data poll
  (`discover_sessions_stage`), in-process sampled-predict invocation (`predict_stage`),
  beam-search report generation + lane selection (`optimize_stage`), best-effort explainer copy
  (`explain_stage`) — all four now exist as real, tested functions, not just design-doc prose.
- **Constraints/assumptions touched:** per-year DB-path threading correctness is honored by
  construction — `predict_stage` never defaults `db_path` (tested explicitly, see
  `test_predict_stage_never_defaults_db_path`); DB-only analysis is honored (no FastF1/live-API
  imports in this module); compound-prior-root-is-required is honored by letting
  `_compound_normalizer_for_sampled_predict`'s own `ValueError` propagate unswallowed (tested in
  `test_predict_stage_propagates_compound_normalizer_valueerror`).
- **Decision candidates / resolved decisions:** confirms the Candidate C checkpoint shape (Wave 1,
  PR #612) is buildable as specified; confirms the `--lane` 3-choice restriction
  (mean/risk/balanced, no `best_max`) as the correct, buildable boundary — `FantasyBeamSearchResult`
  genuinely has no `best_max` field (re-verified at `beam_search.py:52-63`), so the design doc's
  stray mention of a 4th "max" lane (`docs/design/race_week_seam.md:26,218`) is confirmed stale
  against the handoff's (correct) 3-lane restriction.
- **Claims/evidence produced:** `generate_report` (`artifacts.py:200-228`) confirmed at the cited
  lines to call `write_beam_search_report` internally (line 227) — `race_week_stages.py` never
  imports that symbol (`hasattr(rws, 'write_beam_search_report') == False`, asserted by
  `test_optimize_stage_does_not_import_write_beam_search_report` and demonstrated live below).
- **Trust limitations / drift found:** the handoff's own "Verification Commands" section
  (line 63) is stale against the actual `src/utils/simplification_limits.py` CLI — see Workflow
  Feedback below.
- **Triage candidates:** none beyond the already-filed, explicitly out-of-scope
  `sampled-predict --db-path` default-fallback bug named in the handoff's Specific Exclusions.

## Test mode
**Required:** `test-after` (no pre-existing test surface for this new module; every stage function
must be unit-tested as a pure function before the gate closes)
**Satisfied:** yes — `tests/unit/scripts/test_race_week_stages.py` written and green (31/31),
covering checkpoint I/O, the hash/skip primitive, and all four stage functions, including the
ValueError-on-unknown-lane and never-raises-on-failure contracts called out in the handoff.

## Evidence

### Full pytest output (tests/unit/scripts/test_race_week_stages.py -v)

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Programs\f1Brainz\.claude\worktrees\604-build
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collecting ... collected 31 items

tests/unit/scripts/test_race_week_stages.py::test_write_then_read_checkpoint_roundtrip PASSED [  3%]
tests/unit/scripts/test_race_week_stages.py::test_read_checkpoint_missing_file_returns_none PASSED [  6%]
tests/unit/scripts/test_race_week_stages.py::test_compute_stage_inputs_hash_is_deterministic PASSED [  9%]
tests/unit/scripts/test_race_week_stages.py::test_compute_stage_inputs_hash_changes_with_content PASSED [ 12%]
tests/unit/scripts/test_race_week_stages.py::test_compute_stage_inputs_hash_is_sha256_hex PASSED [ 16%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_no_existing_checkpoint PASSED [ 19%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_existing_checkpoint_missing_hash PASSED [ 22%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_matching_hash_skips PASSED [ 25%]
tests/unit/scripts/test_race_week_stages.py::test_should_skip_stage_stale_hash_reruns PASSED [ 29%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_complete_normal_weekend PASSED [ 32%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_partial PASSED [ 35%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_missing PASSED [ 38%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_sprint_weekend_shape PASSED [ 41%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_unknown_gp_raises PASSED [ 45%]
tests/unit/scripts/test_race_week_stages.py::test_discover_sessions_stage_no_checkpoint_path_does_not_write PASSED [ 48%]
tests/unit/scripts/test_race_week_stages.py::test_predict_stage_builds_matching_namespace_and_calls_in_process PASSED [ 51%]
tests/unit/scripts/test_race_week_stages.py::test_predict_stage_never_defaults_db_path PASSED [ 54%]
tests/unit/scripts/test_race_week_stages.py::test_predict_stage_propagates_compound_normalizer_valueerror PASSED [ 58%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_does_not_import_write_beam_search_report PASSED [ 61%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_calls_generate_report_once_and_writes_lane_used PASSED [ 64%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_default_lane_is_balanced PASSED [ 67%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[max] PASSED [ 70%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[best_mean] PASSED [ 74%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[] PASSED [ 77%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[MEAN] PASSED [ 80%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_unknown_lane_raises_valueerror[None] PASSED [ 83%]
tests/unit/scripts/test_race_week_stages.py::test_optimize_stage_embeds_stage_inputs_hash_of_upstream PASSED [ 87%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_copies_markdown_twin_on_success PASSED [ 90%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_missing_markdown_writes_stub_and_does_not_raise PASSED [ 93%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_unexpected_exception_never_raises PASSED [ 96%]
tests/unit/scripts/test_race_week_stages.py::test_explain_stage_always_returns_a_dict_with_status PASSED [100%]

============================= 31 passed in 0.20s ==============================
```

**Result:** pass (31/31)

Also ran the pre-existing import-smoke guard scoped to the new file, to confirm it doesn't break
`tests/unit/scripts/test_scripts_importable.py`:

```
$ py -m pytest tests/unit/scripts/test_scripts_importable.py -k race_week_stages -v
tests/unit/scripts/test_scripts_importable.py::test_script_first_party_imports_resolve[race_week_stages.py] PASSED [100%]
====================== 1 passed, 179 deselected in 0.17s ======================
```

### `py -m src.utils.simplification_limits` output

The handoff's literal Verification Command (`py -m src.utils.simplification_limits
scripts/race_week_stages.py`) does not match the actual CLI — it has no positional path argument,
only `--paths` (see Workflow Feedback). Ran the corrected invocation:

```bash
cd C:/Programs/f1Brainz/.claude/worktrees/604-build
py -m src.utils.simplification_limits --paths scripts/race_week_stages.py
```
```
PASS (1 files checked)
```

**Result:** pass, no split plan needed.

## TDD evidence, if required
Not required — test mode is test-after (no pre-existing test surface for this new module). Every
stage function was written, then unit-tested as a pure function over fixture dicts; no RED step was
recorded per the template's test-after collapse guidance.

## Required-note evidence (per handoff "Required Evidence")

**(a) No `write_beam_search_report` double-call.** `race_week_stages.py` never imports
`write_beam_search_report` at all — `optimize_stage` calls `generate_report`
(`src/fantasy_scoring/artifacts.py:200-228`), which already calls `write_beam_search_report`
internally at line 227 and writes both `<stem>.json` and `<stem>.md`. `optimize_stage` then
re-writes `<stem>.json` a second time using its own plain `json.dump`-based `write_checkpoint`
helper (not `write_beam_search_report`) solely to patch in `lane_used`/`stage_inputs_hash`. Live
check:
```
>>> hasattr(rws, 'write_beam_search_report')
False
```
Also covered by `test_optimize_stage_does_not_import_write_beam_search_report` and
`test_optimize_stage_calls_generate_report_once_and_writes_lane_used` (asserts `generate_report`
is called exactly once).

**(b) `explain_stage` never raises.** The entire function body is wrapped in a broad
`try/except Exception`, and even the fallback stub-write is itself wrapped in a nested
`try/except Exception: pass`, so no path out of `explain_stage` can propagate an exception. Covered
by `test_explain_stage_missing_markdown_writes_stub_and_does_not_raise` (missing `.md` twin) and
`test_explain_stage_unexpected_exception_never_raises` (monkeypatches `shutil.copyfile` to raise
`OSError` — the function still returns cleanly with `status: "stub"`).

**(c) Unknown `lane` raises `ValueError` at the `optimize_stage` boundary.** The check happens
before `generate_report` is ever called. Live check:
```
>>> called = {'n': 0}
>>> rws.generate_report = lambda **kwargs: (called.__setitem__('n', called['n']+1), {})[1]
>>> rws.optimize_stage('does/not/matter.json', year=2023, round_num=1, output_stem='x', lane='max')
ValueError: lane must be one of ('mean', 'risk', 'balanced'), got 'max'
>>> called['n']
0
```
Also covered by the parametrized `test_optimize_stage_unknown_lane_raises_valueerror` (cases:
`"max"`, `"best_mean"`, `""`, `"MEAN"`, `None`), each asserting `generate_report` was never invoked.

## Docs/contracts touched
- none — no `src/` files, no `docs/report_schemas/`, no committed schema changed.

## Assumptions
- `discover_sessions_stage`'s 01-checkpoint status semantics: `"complete"` iff every expected
  session has landed, `"partial"` iff some but not all have landed, `"missing"` iff none have. The
  handoff left the functional meaning of `partial` to Wave 2 (Known Limit #5 in the design doc);
  this gate only produces the classification, it does not gate on it.
- `optimize_stage`'s `stage_inputs_hash` field (hash of the upstream 02 checkpoint) was not
  explicitly required by the close criteria for stage 3 (only `lane_used` was named) but was added
  for consistency with the general checkpoint-resumption convention described in the design doc;
  this is exactly the kind of "extra diagnostic field" the handoff's Authority section leaves to the
  implementer.
- `explain_stage`'s second parameter is the full intended `04_explainer.md` path (not a directory);
  the STUB path is derived from it (`04_explainer.md` -> `04_explainer.STUB.md`) via
  `Path.with_name`. Not specified exactly this way in the handoff; chosen because it lets the
  caller (G2) control the exact checkpoint directory without this module hardcoding
  `outputs/race_week/...` path construction itself.
- `predict_stage` and `optimize_stage` both accept an explicit file path/checkpoint dict from the
  caller rather than resolving `outputs/race_week/<year>/<round>/...` paths themselves — per the
  handoff's constraint that "this gate does not need to create the directory tree itself beyond
  what its own file-write calls require," directory-tree convention ownership is left to G2's CLI.

## Stop conditions hit
None of the three named stop conditions were hit:
- No cited seam signature mismatched source — all were re-verified and matched exactly
  (`get_practice_session_types` at `constants.py:312`, `has_session_classification` at
  `_metadata_session.py:506`, round-num pattern at `collector.py:232`, `cmd_sampled_predict` at
  `run.py:544`, parser fields at `run.py:792-814`, `generate_report` at `artifacts.py:200-228`
  (writes both files internally, confirmed), `FantasyBeamSearchResult` at `beam_search.py:52-63`
  (no `best_max`, confirmed)).
- Neither `generate_report` nor `cmd_sampled_predict` behaved in a way that made the stage split
  impossible.
- No `src/` change was found to be genuinely required.

(A separate, non-blocking issue *was* found and self-corrected mid-run — see Workflow Feedback: the
handoff's literal simplification-limits verification command doesn't match the actual CLI. This
did not meet the bar for a stop-and-return since the fix was a one-line, unambiguous CLI syntax
correction with no design implications, not a seam/contract mismatch.)

## Out-of-scope observations
- None beyond what the handoff already named as out-of-scope (the `sampled-predict --db-path`
  default-fallback bug).

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** The "Verification Commands" section (handoff line 63) reads
  `py -m src.utils.simplification_limits scripts/race_week_stages.py` — this fails with an argparse
  error (exit 2, "unrecognized arguments") because `src/utils/simplification_limits.py`'s `main()`
  has no positional path argument, only `--paths` (nargs="*"). The correct invocation is
  `py -m src.utils.simplification_limits --paths scripts/race_week_stages.py`. This is a small,
  mechanical fix, but it cost a real stop-fix-continue cycle (including an engine `skip` +
  `amend --delta` to correct the plan's baked-in postcondition command, since the step had already
  moved past `pending` by the time I discovered the syntax error). Future handoffs citing this
  module's CLI should use the `--paths` form.
- **Context rediscovered:** None beyond ordinary seam re-verification the handoff already told me
  to do — every other cited signature (session discovery, DB polling, predict/optimize contracts)
  matched exactly as written, which is worth naming explicitly since it means the handoff's careful
  line-cited verification work paid off everywhere except the one CLI-syntax slip above.
- **Instructions improvised around:** The engine's `rescope` (via `amend`) only applies to
  `pending` gates, and `append` is restricted to survey checklists — so correcting an already
  `in-progress` gated postcondition's command required `skip`-ing the flawed step and `amend
  --delta {"ops":[{"op":"add", ...}]}`-ing a corrected sibling item after it, rather than editing
  the flawed step in place. This worked cleanly and is arguably the intended path (amend's own docs
  describe `add` for exactly this), but it's worth naming: a plan step whose check command has a
  syntax bug and is already `start`-ed cannot be fixed by amending itself — it must be skipped and
  replaced.
- **What would have made this easier:** Fixing the handoff's `--paths` flag omission in
  `src/utils/simplification_limits`'s Verification Command line for future handoffs referencing
  this module.

## Return status
`complete`
