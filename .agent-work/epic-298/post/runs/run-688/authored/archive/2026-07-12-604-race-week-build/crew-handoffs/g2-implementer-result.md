# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement`

## Completed slice
Built `scripts/race_week.py`: a thin argparse CLI dispatcher over G1's
`scripts/race_week_stages.py` stage library, with subcommands `collect-check`,
`predict`, `optimize`, `explain`, and `run` (chains all four). Implements the
mandated db-path resolution order (never silently reaching the fixed
`Config.DATABASE_PATH`), the argparse-level 3-lane restriction, round-number
resolution matching the collector's established pattern, hash-based
should_skip_stage resumption for `predict`/`optimize`, and hard/soft gate
ordering in `run` (explain never invoked if predict/optimize fails).

## Scope
**Files changed:**
- `scripts/race_week.py` (new)
- `tests/unit/scripts/test_race_week_cli.py` (new)
- `.agent-work/604-race-week-build/crew-handoffs/g2-implementer-plan.json` (new, engine-owned plan artifact)

**Specific exclusions touched:** no — `scripts/race_week_stages.py` (G1's file) was not modified; no `src/` changes; `collect-check` does not invoke any collector script (verified by an explicit test asserting `"collect_evo_data"` does not appear in the module source).

## Behavior changed
Yes — new CLI entry point for the race-week pipeline. No existing behavior changed; `race_week_stages.py` (G1) is untouched and its own test suite (`test_race_week_stages.py`, 33 tests) still passes unmodified.

## Map Impact
- **Structural anchors touched:** `struct:scripts` — `scripts/race_week.py` added as a new CLI module; imports `scripts/race_week_stages.py` (G1) and reads `src/data/database.DatabaseManager`, `src/utils/config.Config`, `src/utils/constants.get_calendar` (read-only reference, no changes).
- **Capabilities added/changed/affected:** CLI orchestration over G1's stage library is now live: `collect-check` / `predict` / `optimize` / `explain` / `run` subcommands, each independently invocable, plus `run` as the full chain. This is the first end-user-facing entry point for the race-week pipeline (G3's e2e gate will exercise it against real data).
- **Constraints/assumptions touched:** db-path threading correctness (never silently fall to `Config.DATABASE_PATH`) — honored and covered by dedicated regression-style tests, including a deliberately-reintroduced-then-reverted footgun (see TDD evidence below) proving the tests actually catch it. Hard/soft gate ordering (03 durable before 04 attempted) — honored; `run`'s straight-line sequential code (no try/except around predict/optimize) makes `explain` structurally unreachable on a prior-stage failure, and this is proven by two failure-injection tests (predict_stage raising, optimize_stage raising) plus a deliberately-reintroduced-then-reverted regression.
- **Decision candidates / resolved decisions:** `--lane` default `balanced`, exactly 3 choices (`mean`, `risk`, `balanced`) enforced at the argparse level via `choices=stages.VALID_LANES` — resolved as specified, no new decision needed.
- **Claims/evidence produced:** `claim: db_path_for_year(2026)` resolves to `data/f1_data_2026.db` and is never `data/f1_data.db` when neither `--db-path` nor `--db-root` is given — verified by `test_resolve_db_path_default_branch_is_never_the_fixed_database_path` and the threading acceptance test `test_db_path_threading_acceptance_predict_stage_receives_per_year_default` (both pass; both were also shown to genuinely fail against a reintroduced bug — see TDD evidence).
- **Trust limitations / drift found:** none found; G1's frozen signatures matched this handoff's citations exactly on re-verification (see Workflow Feedback).
- **Triage candidates:** none raised — `collect-check`'s non-invocation of a real collector is explicitly in scope for this wave (Known-Limits item 7 per the handoff), not a gap.

## Test mode
**Required:** `test-after allowed (new module, no pre-existing test surface) — but Close Criteria behaviors must be covered by tests/unit/scripts/test_race_week_cli.py before this gate closes, including two regression-shaped tests`
**Satisfied:** yes — `tests/unit/scripts/test_race_week_cli.py` (41 tests) covers argument parsing/defaults, all three db-path resolution branches (including the automated acceptance test), lane validation at the argparse level, resumption skip/rerun for both `--force` and hash-mismatch paths (tested separately, for both `predict` and `optimize`), the failure-injection hard/soft-gate-ordering test (both `predict_stage`-raises and `optimize_stage`-raises variants), and the invalid-`--race` test. No real DB/FastF1/prediction calls — `race_week_stages`'s stage functions and `DatabaseManager` are mocked throughout.

## Evidence

### Full pytest output — `tests/unit/scripts/test_race_week_cli.py` (verbose, not summarized)

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Programs\f1Brainz\.claude\worktrees\604-build
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collecting ... collected 41 items

tests/unit/scripts/test_race_week_cli.py::test_help_exits_zero_for_top_level_and_every_subcommand PASSED [  2%]
tests/unit/scripts/test_race_week_cli.py::test_year_and_race_are_required PASSED [  4%]
tests/unit/scripts/test_race_week_cli.py::test_global_defaults PASSED    [  7%]
tests/unit/scripts/test_race_week_cli.py::test_predict_defaults PASSED   [  9%]
tests/unit/scripts/test_race_week_cli.py::test_optimize_default_lane_is_balanced PASSED [ 12%]
tests/unit/scripts/test_race_week_cli.py::test_force_flag_parses PASSED  [ 14%]
tests/unit/scripts/test_race_week_cli.py::test_lane_accepts_the_three_real_choices[mean] PASSED [ 17%]
tests/unit/scripts/test_race_week_cli.py::test_lane_accepts_the_three_real_choices[risk] PASSED [ 19%]
tests/unit/scripts/test_race_week_cli.py::test_lane_accepts_the_three_real_choices[balanced] PASSED [ 21%]
tests/unit/scripts/test_race_week_cli.py::test_lane_rejects_anything_outside_the_three_choices[max] PASSED [ 24%]
tests/unit/scripts/test_race_week_cli.py::test_lane_rejects_anything_outside_the_three_choices[MEAN] PASSED [ 26%]
tests/unit/scripts/test_race_week_cli.py::test_lane_rejects_anything_outside_the_three_choices[best_mean] PASSED [ 29%]
tests/unit/scripts/test_race_week_cli.py::test_lane_rejects_anything_outside_the_three_choices[] PASSED [ 31%]
tests/unit/scripts/test_race_week_cli.py::test_lane_rejects_anything_outside_the_three_choices[fast] PASSED [ 34%]
tests/unit/scripts/test_race_week_cli.py::test_lane_choices_match_stages_valid_lanes_exactly PASSED [ 36%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_db_path_explicit_db_path_wins PASSED [ 39%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_db_path_db_root_branch PASSED [ 41%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_db_path_default_branch_uses_config_db_path_for_year PASSED [ 43%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_db_path_default_branch_is_never_the_fixed_database_path PASSED [ 46%]
tests/unit/scripts/test_race_week_cli.py::test_db_path_threading_acceptance_predict_stage_receives_per_year_default PASSED [ 48%]
tests/unit/scripts/test_race_week_cli.py::test_db_path_threading_explicit_db_path_overrides_default PASSED [ 51%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_round_num_matches_calendar_index_pattern PASSED [ 53%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_round_num_unknown_gp_raises_valueerror PASSED [ 56%]
tests/unit/scripts/test_race_week_cli.py::test_resolve_round_num_unknown_year_raises_keyerror PASSED [ 58%]
tests/unit/scripts/test_race_week_cli.py::test_cmd_predict_propagates_invalid_race_valueerror PASSED [ 60%]
tests/unit/scripts/test_race_week_cli.py::test_main_reports_invalid_race_as_nonzero_exit_not_a_silent_noop PASSED [ 63%]
tests/unit/scripts/test_race_week_cli.py::test_cmd_collect_check_writes_checkpoint_and_prints_summary PASSED [ 65%]
tests/unit/scripts/test_race_week_cli.py::test_cmd_collect_check_never_invokes_a_collector PASSED [ 68%]
tests/unit/scripts/test_race_week_cli.py::test_predict_skips_when_checkpoint_fresh_and_not_forced PASSED [ 70%]
tests/unit/scripts/test_race_week_cli.py::test_predict_reruns_on_force_even_when_checkpoint_fresh PASSED [ 73%]
tests/unit/scripts/test_race_week_cli.py::test_predict_reruns_on_hash_mismatch_without_force PASSED [ 75%]
tests/unit/scripts/test_race_week_cli.py::test_optimize_skips_when_checkpoint_fresh_and_not_forced PASSED [ 78%]
tests/unit/scripts/test_race_week_cli.py::test_optimize_reruns_on_force PASSED [ 80%]
tests/unit/scripts/test_race_week_cli.py::test_optimize_reruns_on_hash_mismatch_without_force PASSED [ 82%]
tests/unit/scripts/test_race_week_cli.py::test_optimize_missing_upstream_checkpoint_raises_clear_error PASSED [ 85%]
tests/unit/scripts/test_race_week_cli.py::test_run_aborts_and_never_calls_explain_when_predict_stage_raises PASSED [ 87%]
tests/unit/scripts/test_race_week_cli.py::test_run_aborts_and_never_calls_explain_when_optimize_stage_raises PASSED [ 90%]
tests/unit/scripts/test_race_week_cli.py::test_main_exits_nonzero_when_predict_stage_raises_inside_run PASSED [ 92%]
tests/unit/scripts/test_race_week_cli.py::test_explain_stage_itself_always_exits_zero_even_when_it_internally_fails PASSED [ 95%]
tests/unit/scripts/test_race_week_cli.py::test_run_chains_all_four_stages_in_order PASSED [ 97%]
tests/unit/scripts/test_race_week_cli.py::test_run_threads_resolved_db_path_and_lane_through_to_stages PASSED [100%]

============================= 41 passed in 0.23s ==============================
```

### Combined suite — `test_race_week_stages.py` (G1) + `test_race_week_cli.py` (G2)

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1Brainz\.claude\worktrees\604-build
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 74 items

tests\unit\scripts\test_race_week_stages.py ............................ [ 37%]
.....                                                                    [ 44%]
tests\unit\scripts\test_race_week_cli.py ............................... [ 86%]
..........                                                               [100%]

============================= 74 passed in 0.28s ==============================
```

### `py -m src.utils.simplification_limits --paths scripts/race_week.py tests/unit/scripts/test_race_week_cli.py`

```
PASS (2 files checked)
```

### Import-smoke guard (`tests/unit/scripts/test_scripts_importable.py`, `-k race_week`)

```
tests/unit/scripts/test_scripts_importable.py::test_script_first_party_imports_resolve[race_week.py] PASSED
tests/unit/scripts/test_scripts_importable.py::test_script_first_party_imports_resolve[race_week_stages.py] PASSED
============================= 3 passed, 178 deselected in 0.15s ==============
```

### Deliverable-path check (`git check-ignore`, both exit 1 = not ignored)

```
$ git check-ignore scripts/race_week.py; echo "exit: $?"
exit: 1
$ git check-ignore tests/unit/scripts/test_race_week_cli.py; echo "exit: $?"
exit: 1
```

**Result:** pass — all commands above ran clean, zero failures.

## TDD evidence, if required

Test mode is test-after, but per the handoff two of the tests were specifically
called out as regression-shaped tests that "exist because a cold plan critic
flagged their absence as a real gap before any code was written." Since the
implementation was written before the tests (test-after is explicitly
sanctioned here), a literal red-before-green wasn't naturally available from
writing tests against not-yet-written code. Instead, genuine red was proven by
temporarily reintroducing each of the two protected-intent bugs this gate
exists to prevent, confirming the relevant tests actually fail, then
reverting:

**1. DB-path footgun** (`resolve_db_path`'s default branch changed from
`return str(Config.db_path_for_year(year))` to
`return str(Config.DATABASE_PATH)  # DELIBERATE BUG`):

```
tests\unit\scripts\test_race_week_cli.py ..FFF.F   [selected: -k db_path]
FAILED test_resolve_db_path_default_branch_uses_config_db_path_for_year
FAILED test_resolve_db_path_default_branch_is_never_the_fixed_database_path
FAILED test_db_path_threading_acceptance_predict_stage_receives_per_year_default
FAILED test_run_threads_resolved_db_path_and_lane_through_to_stages
4 failed, 3 passed, 34 deselected
```

**2. Hard/soft gate ordering** (`cmd_run` changed to call `_do_explain` from
inside an `except Exception: ...; raise` block around predict/optimize,
i.e. "call explain even when a prior stage failed, then re-raise"):

```
tests\unit\scripts\test_race_week_cli.py  [selected: -k "failure or run_aborts or main_exits_nonzero"]
FAILED test_run_aborts_and_never_calls_explain_when_predict_stage_raises
  AssertionError: Expected 'mock' to not have been called. Called 1 times.
FAILED test_run_aborts_and_never_calls_explain_when_optimize_stage_raises
  AssertionError: Expected 'mock' to not have been called. Called 1 times.
FAILED test_main_exits_nonzero_when_predict_stage_raises_inside_run
  AssertionError: Expected 'mock' to not have been called. Called 1 times.
3 failed, 38 deselected
```

Both bugs were then reverted and the full 41-test suite re-confirmed green
(output above). This demonstrates the tests are not vacuous — they catch
exactly the two protected-intent regressions this gate exists to prevent.

- Failing test observed: yes (both scenarios above, real failures against a real regression).
- Passing test observed: yes (`41 passed` after revert, pasted above).
- Refactor while green: no refactor was needed after the revert; the file was already in its final state.

## Docs/contracts touched
- None — `scripts/race_week_stages.py`'s module docstring already documents the checkpoint dir convention this CLI implements; no doc changes were required.

## Assumptions
- **`--db-root`'s true argparse default is `None`, not the literal string `"data"`.** The handoff's bullet says `--db-root ... default "data"` in the arg-listing prose, but the DB-path resolution order (same bullet, and repeated in the Automated DB-path threading acceptance test) requires the *third* branch (`Config.db_path_for_year(year)`) to be reachable "when neither is given." If `--db-root` literally defaulted to `"data"` at the argparse level, that third branch would be unreachable (the second branch, `<db-root>/f1_data_{year}.db`, would always fire) and, worse, would resolve to a *relative* path that would not equal `str(Config.db_path_for_year(year))` (an absolute, `PROJECT_ROOT`-based path) — failing the explicit acceptance test. Resolved this by giving `--db-root` an actual default of `None`; conceptually it still "ends up using the data/ directory" via the `Config.db_path_for_year` branch, which is exactly what the acceptance test pins down.
- **`collect-check` also carries `--db-path`/`--db-root`.** The handoff's Close Criteria lists `--db-path`/`--db-root` under "predict/run args" only, but `discover_sessions_stage` requires a `DatabaseManager`, which requires a resolved db path — so `collect-check` needs the same flags and the same resolution-order guarantee. Added them to `collect-check`'s subparser (shared `db_parent` parent parser also used by `predict` and `run`).
- **`explain` and `collect-check` have no hash-based skip/resume logic.** The handoff's Resumption bullet says "each subcommand loads its upstream checkpoint(s) via `should_skip_stage`," but `collect-check` (the first stage, polling the DB directly) has no upstream checkpoint to hash against, and `explain_stage`'s own contract (frozen, G1) writes a `.md`/`.STUB.md` file, not a JSON checkpoint with a `stage_inputs_hash` field — there is nothing to compare a hash against without inventing a CLI-only sidecar checkpoint G1 never specified. Implemented `should_skip_stage`-based resumption for `predict` and `optimize` only (the two subcommands with real JSON checkpoints carrying `stage_inputs_hash`), and left `collect-check`/`explain` unconditional (cheap, idempotent, and — for `explain` — explicitly required to "never block/never fail" regardless of resumption state).

## Stop conditions hit
- None. G1's signatures matched this handoff's citations exactly on re-verification (`read_checkpoint`, `write_checkpoint`, `compute_stage_inputs_hash`, `should_skip_stage`, `VALID_LANES`, `discover_sessions_stage`, `predict_stage`, `optimize_stage`, `explain_stage` — all confirmed against `scripts/race_week_stages.py` directly, including the `prediction_checkpoint_path` (path, not dict) vs. `sessions_checkpoint` (dict, not path) calling-convention distinction the handoff specifically flagged). `get_calendar`/`Config` behaved exactly as described (`get_calendar` raises `KeyError` for an unknown year at `src/utils/constants.py:277`; `Config.DATABASE_PATH`/`Config.db_path_for_year` at `src/utils/config.py:32,36`). No `src/` change was needed.

## Out-of-scope observations
- None beyond what the handoff already scoped out (no collector invocation from `collect-check`).

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** the `--db-root ... default "data"` wording (Close Criteria bullet 2) reads as a literal argparse default, but taken literally it contradicts the immediately-following "exact" resolution order and would break the immediately-following automated acceptance test (see Assumptions above — this is the one genuine ambiguity in an otherwise very precise handoff). Also: the "predict/run args" grouping doesn't mention that `collect-check` independently needs `--db-path`/`--db-root` too (it needs a `DatabaseManager` just as much as `predict` does) — not contradictory, just an omission a careful re-read of `discover_sessions_stage`'s signature surfaced.
- **Context rediscovered:** none beyond the above — the "G1's Actual Signatures" section was accurate and saved a full re-read of `race_week_stages.py`'s internals; I still read the full file to confirm scope and the explain_stage/optimize_stage docstrings' finer contract details (e.g. explain_stage's tempfile fallback, optimize_stage's double-write-avoidance note), which weren't strictly necessary for G2 but clarified why certain design choices (e.g. no skip-logic for explain) were safe.
- **Instructions improvised around:** the plan template's TDD-red guidance ("encode the RED step as a check:null postcondition... new test written and observed failing") assumes tests are written before the implementation exists. Because this handoff's test mode is explicitly test-after (implementation-first is sanctioned), I substituted a targeted regression-proof: temporarily reintroduce each of the two protected-intent bugs, confirm the relevant tests fail, then revert and confirm green. This is a legitimate red/green pair (proves the tests are non-vacuous) but isn't the "test written first" flavor of red the template imagines for a test-after gate.
- **What would have made this easier:** clarifying `--db-root`'s literal argparse default vs. its "effective" default (via `Config.db_path_for_year`) directly in the Close Criteria bullet, rather than leaving it to be inferred from the separately-stated resolution order and acceptance test.

## Return status
`complete`
