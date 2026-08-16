# IMPLEMENTER_RESULT — g1-implement

## Completed slice

Both changes landed in the same patch, in owned files only:

1. **Mandatory tier at the dispatch seam.** `CrewSpec.__post_init__` (`scripts/run_crew.py`)
   now refuses a falsy `self.model`, raising `CrewLaunchError`, as a third invariant check —
   same style as (and placed immediately after) the two existing checks ("needs a job",
   "needs a completion contract") in the same method:

   ```python
   if not self.model:
       raise CrewLaunchError(
           "a crew needs an explicit tier: refusing a dispatch with no "
           "--model given (no default is invented -- decision:refuse-a-"
           "tierless-dispatch)"
       )
   ```

2. **`reasoning_effort` forwarded as the launcher's real `--effort` flag.**
   `build_crew_argv` gained `effort: str | None = None`, emitting `["--effort", effort]`
   only when truthy, mirroring the existing `model` line exactly. Both `CliBackend.dispatch`
   (fresh) and `CliBackend.resume` now pass `effort=` at their `build_crew_argv` call sites
   (`spec.reasoning_effort` / `entry.get("reasoning_effort")` respectively).

`build_entry`'s `reasoning_effort` docstring note was corrected (the "never emitted as a CLI
flag" claim is now false); its write path (`if reasoning_effort: entry["reasoning_effort"] = …`)
was read, confirmed already correct, and left untouched — no new write path was added.

`--model` stays optional at the `argparse` layer (`build_parser`); the refusal lives entirely
at the `CrewSpec` seam, per Authority.

## Files changed

- `scripts/run_crew.py` — `CrewSpec.__post_init__` (new refusal), `build_crew_argv` (new
  `effort` param + docstring), `CliBackend.dispatch`/`CliBackend.resume` (both now pass
  `effort=` to `build_crew_argv`), `build_entry` docstring correction. No other functions
  touched.
- `tests/test_crew_launcher.py` — reconciliation of every existing test the new mandatory
  `--model` invalidated (full enumeration below), the four named tests flipped from
  `assertNotIn("--reasoning-effort", …)` to asserting `--effort <value>` presence/absence,
  and a new `MandatoryModelTests` class (6 tests) covering the refusal directly.
- `map/INDEX.md` — regenerated via `python -m scripts.code_map build --root .` (mechanical,
  entity-count-only diff: `tests.test_crew_launcher` 287→294 entities from the new test
  methods). This file is not in the handoff's Allowed Scope by name, but the handoff's own
  close criterion "Full clean-env suite green at gate close" required it: the map-freshness
  gate (`tests/test_code_map.py::MapTreeFreshnessTests`) fails on any entity-count drift
  between source and the committed map, and my `tests/test_crew_launcher.py` edits (owned,
  authorized) shifted that count. Confirmed via `git stash`: the map-freshness test passes on
  the unmodified baseline and only fails after my authorized test-file edits — i.e. this is a
  direct, mechanical consequence of the in-scope change, not an unrelated drift I am papering
  over. No hand-editing: the file is 100% tool-generated output, diff limited to entity counts.

## Test mode satisfied

TDD-adjacent / test-after, as directed: every new behavior has a red/green pair.
`MandatoryModelTests` (new class in `tests/test_crew_launcher.py`, right after `LaunchTests`)
covers:
- `test_crew_spec_refuses_falsy_model_directly` — red, direct `CrewSpec` construction.
- `test_fresh_dispatch_with_model_records_it` — green, through `RC.main`, registry carries `model`.
- `test_fresh_dispatch_with_no_model_is_refused_and_writes_no_registry_entry` — red, through
  `RC.main`: exit 1, `REFUSED`, nothing spawned, **registry stays empty** (proves the #525
  ordering: refusal fires before `CliBackend.dispatch` reserves scratch/writes the running entry).
- `test_abandon_relaunch_with_no_model_is_refused_even_though_one_was_stored` — red, pins the
  RULED no-inherit-fallback semantics: a stored `model: "opus"` on the abandoned entry does NOT
  satisfy the new requirement on relaunch.
- `test_resume_needs_no_model_at_all` / `test_bare_abandon_needs_no_model_at_all` — negative
  controls: `--resume` and a bare `--abandon` construct no `CrewSpec` and must keep working with
  no `--model` at all.

`--effort` forwarding red/green (`test_reasoning_effort_is_recorded_and_forwarded_as_effort_flag`,
renamed from `test_reasoning_effort_is_metadata_only_and_recorded` since that claim is now false)
covers `CliBackend.dispatch`; `test_cli_resume_reads_reasoning_effort_from_registry` covers
`CliBackend.resume` — both now assert `--effort <value>` IS present at the right index, and
`test_legacy_resume_without_reasoning_effort_does_not_crash` confirms `--effort` stays absent
when no `reasoning_effort` was ever recorded.

## Evidence produced

**Wiring grep** (per handoff):
```
grep -rn "build_crew_argv(" --include=*.py . | grep -v "def build_crew_argv"
```
→ 22 non-archived matches (2 production call sites in `scripts/run_crew.py:1558,1628` — both
now show `effort=` in the diff — plus 20 direct-call tests in `tests/test_crew_launcher.py`,
unaffected since `build_crew_argv` itself still accepts `model=None`/`effort=None`). A further
~10 matches exist only under `.agent-work/archive/**` (historical harvested copies, not live
call sites — excluded).
```
grep -rn "\.reasoning_effort\b" --include=*.py scripts/run_crew.py tests/test_crew_launcher.py
```
→ 5 matches, all in `scripts/run_crew.py` (the `.attribute` form doesn't match test-file keyword
args): `build_entry(...)` call in `CliBackend.dispatch`, the new `effort=spec.reasoning_effort`
in `build_crew_argv`'s dispatch call, the `ExternalBackend.dispatch` `build_entry` call, the
`--abandon --relaunch` inherit-fallback (`main()`, untouched), and the fresh-launch `main()`
call (untouched).

**Refusal red/green**: `MandatoryModelTests` above, all 6 passing (see full run below).

**`--effort` forwarding red/green on both `CliBackend.dispatch` and `.resume`**: confirmed
passing (`test_reasoning_effort_is_recorded_and_forwarded_as_effort_flag`,
`test_cli_resume_reads_reasoning_effort_from_registry`).

**Full clean-env, cache-cleared suite** (exact command from the handoff):
```
$ find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
...
FAILED tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound
FAILED tests/test_crew_worktree_cwd.py::CrewSpawnCwdTests::test_cli_default_dot_dispatch_passes_an_absolute_repo_cwd
FAILED tests/test_crew_worktree_cwd.py::CrewSpawnCwdTests::test_dispatch_passes_an_absolute_worktree_as_the_child_cwd
FAILED tests/test_crew_worktree_cwd.py::CrewSpawnCwdTests::test_relative_worktree_resolves_against_root_not_the_dispatchers_cwd
FAILED tests/test_crew_worktree_cwd.py::CrewSpawnCwdTests::test_the_registry_records_the_same_worktree_the_spawn_received
FAILED tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_flat_work_id_finalizes_identically
FAILED tests/test_work_id_nesting.py::CrewRegistryAddressingTests::test_nested_work_id_finalizes_its_own_registry
7 failed, 3163 passed, 6 skipped, 1172 subtests passed in 128.34s (0:02:08)
```
Mechanical failure distribution (`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`):
```
      1 FAILED tests/test_crew_launcher.py
      4 FAILED tests/test_crew_worktree_cwd.py
      2 FAILED tests/test_work_id_nesting.py
```
`tests/test_crew_launcher.py` alone (owned file): `1 failed, 211 passed`. That one failure is
**pre-existing and environmental, not caused by this change** — confirmed via `git stash` +
rerun on the unmodified baseline: it fails identically there. Cause: this implementer session
is itself a live crew with `CREW_SCRATCH_DIR` bound in its own ambient environment; the test
inherits `os.environ` into the fake child's env dict and asserts the var is ABSENT, which only
holds when run outside a crew's own scratch-bound session. Not scoped to this gate, not fixed.

The other 6 failures are genuine, caused by this change, and are **callers outside owned files**
(handoff: "Do not fix a caller outside `scripts/run_crew.py`/`tests/test_crew_launcher.py` that
the caller-list survey finds — report it in `IMPLEMENTER_RESULT` instead") — reported below, not
fixed.

## Caller-list survey (full enumeration)

Every call site whose scenario the new mandatory `--model` invalidated:

**`tests/test_crew_launcher.py` (owned — all fixed)**, by class:
- `LaunchTests`: `test_nonzero_child_exit_returns_nonzero_and_marks_failed`,
  `test_missing_result_artifact_returns_nonzero`,
  `test_abandon_relaunch_increments_attempt_and_marks_prior_abandoned` — `model=None`/no
  `--model` → `model="sonnet"`/`--model sonnet` added (unrelated to what each test actually
  exercises).
- `ParentCliTests`: `test_fresh_launch_with_parent_records_it_in_the_registry`,
  `test_fresh_launch_with_no_parent_still_works_and_records_none`,
  `test_abandon_relaunch_inherits_stored_parent_when_not_reasserted`,
  `test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted` (also one of
  the 4 named flips — now asserts `--effort high` is forwarded on the relaunch),
  `test_abandon_relaunch_legacy_registry_without_reasoning_effort_stays_compatible` —
  `--model sonnet` added.
- `DispatchDoorBindingTests` (4 tests), `ParentDoorBindingTests` (2 tests),
  `SpineOnlyDispatchTests` (`test_main_cli_spine_only_dispatch_with_result_still_succeeds`
  via `RC.main`; three `RC.launch_crew` calls via bulk `model=None`→`model="sonnet"`),
  `DoorHijackRealEngineControlTests` (`test_child_claims_its_own_spine_dispatcher_lease_untouched`)
  — all `model=None` → `model="sonnet"` on `RC.launch_crew` kwargs (unrelated to spine/parent
  binding, which is what each test actually exercises).
- `SpineOnlyCompletionContractTests` (4 tests) — `--model sonnet` added to each `RC.main` argv.
- `BlockedOutcomeTests` (2 of 6: `test_blocked_gate_is_recorded_blocked_not_failed`,
  `test_blocked_takes_priority_over_a_given_result_artifact`; the other 4 already picked up
  `--model sonnet` via the bulk fix) — `--model sonnet` added.
- `ExternalDispatchTests` (4 tests: `test_external_dispatch_records_without_spawning`,
  `test_external_dispatch_refuses_spine`, `test_external_duplicate_active_lock_is_refused`,
  `test_verify_result_absent_then_present_marks_completed`) — `--model sonnet` added.
- `ResultFreshnessTests` (`test_verify_result_stale_refuses_and_leaves_running`,
  `test_verify_result_missing_refuses_with_absent_message`; `test_launch_finding_only_stale_result_marks_failed`
  via bulk fix) — `--model sonnet` added.
- `BackendEquivalenceTests`: `test_reasoning_effort_is_metadata_only_and_recorded` (renamed +
  flipped, named test), `test_cli_resume_reads_reasoning_effort_from_registry` (named test,
  `CrewSpec` gained `model="sonnet"`, assertion flipped to check `--effort low` IS present),
  `test_legacy_resume_without_reasoning_effort_does_not_crash` (named test, confirmatory —
  assertion widened to also check `--effort` absent), `test_cli_dispatch_missing_handoff_refuses_with_launch_wording`,
  `test_external_dispatch_missing_handoff_refuses_with_record_wording`,
  `test_external_dispatch_prints_unbound_door_banner` — `CrewSpec(..., model="sonnet")` added
  so each reaches its OWN intended refusal/behavior instead of the new model refusal firing first.
- `BackendFlagRoutingTests` (4 tests) — fixed at the root: `_launch_argv` helper now always
  includes `--model sonnet`.
- `ScratchDirReservationTests`, `ScratchDirCollisionTests`, `ScratchDirResumeTests` (except the
  one pre-existing environmental failure), `ParentLeaseHeartbeatTests` — all via the bulk
  `model=None` → `model="sonnet"` fix on `RC.launch_crew`/`RC.record_external_attempt` kwargs.

Explicitly NOT changed (still `model=None`, correctly): `SessionNameTests`'s 17 direct
`RC.build_crew_argv(...)` calls (pure-function tests, unaffected — `build_crew_argv` itself
still accepts `model=None`) and `BuildEntryTests::test_falsy_model_is_not_stored` (tests
`build_entry`'s own write path directly, bypasses `CrewSpec` entirely, correctly unaffected).

**Found outside owned files — NOT fixed, reported here per the handoff's exclusion**:
- `tests/test_crew_worktree_cwd.py` — loads its own independent copy of `run_crew` and calls
  `RC.launch_crew(...)` with `model=None` at 4 call sites (lines ~97, ~142, ~158, ~219, across
  `test_cli_default_dot_dispatch_passes_an_absolute_repo_cwd`,
  `test_dispatch_passes_an_absolute_worktree_as_the_child_cwd`,
  `test_relative_worktree_resolves_against_root_not_the_dispatchers_cwd`,
  `test_the_registry_records_the_same_worktree_the_spawn_received`). All 4 now fail with the
  new `CrewLaunchError` ("a crew needs an explicit tier").
- `tests/test_work_id_nesting.py` — its `_record_external` helper (line ~80) calls
  `RC.record_external_attempt(..., model=None, ...)`, breaking
  `test_flat_work_id_finalizes_identically` and `test_nested_work_id_finalizes_its_own_registry`.

No production (non-test) caller outside `scripts/run_crew.py` constructs `CrewSpec`,
`build_crew_argv`, or calls `launch_crew`/`record_external_attempt` directly (confirmed by
`grep -rln "CrewSpec(\|record_external_attempt(\|\.launch_crew(" --include=*.py .` excluding
archive/test paths → only `scripts/run_crew.py` itself).

## Confirmatory evidence

- The four named tests all flipped correctly (verified passing, assertions now check `--effort
  <value>` presence/absence): `test_reasoning_effort_is_recorded_and_forwarded_as_effort_flag`
  (renamed from `test_reasoning_effort_is_metadata_only_and_recorded`),
  `test_cli_resume_reads_reasoning_effort_from_registry`,
  `test_legacy_resume_without_reasoning_effort_does_not_crash`,
  `test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted`.
- `build_entry` docstring corrected (`reasoning_effort` note no longer claims "never emitted as
  a CLI flag").

## Assumptions used

- `model="sonnet"` was used as the placeholder tier value everywhere a test needed *some*
  explicit model but wasn't testing model-specific behavior — consistent with existing
  convention already in the file (e.g. `test_records_entry_before_launch_and_completes` already
  used `model="sonnet"` pre-change).
- `map/INDEX.md` regeneration (see Files changed) was treated as a mechanical, required step to
  satisfy the "Full clean-env suite green" close criterion, not a scope expansion — it is
  100% tool-generated, the diff is limited to entity counts, and it was verified stale-on-my-
  change/fresh-on-baseline before touching it.

## Stop conditions hit

None. `claude --help` was checked directly and confirms `--effort <level>` (`low, medium, high,
xhigh, max`) exists on the installed CLI, matching the handoff's Authority. The refusal scopes
cleanly to fresh/relaunch without touching `--resume` or a bare `--abandon` (confirmed by
reading `CliBackend.resume`/`abandon_crew` directly — neither constructs a `CrewSpec` — and by
the two negative-control tests in `MandatoryModelTests`). No caller outside owned files needed a
code fix (both out-of-scope callers found are test files, reported above, not touched). No
decision outside the Authority section was needed.

## Out-of-scope observations

- The two out-of-scope test files above (`tests/test_crew_worktree_cwd.py`,
  `tests/test_work_id_nesting.py`) will need the same mechanical `model=None` → `model="sonnet"`
  (or equivalent) reconciliation before the full suite is clean-green again. This is pure
  mechanical fallout of `decision:refuse-a-tierless-dispatch`, not a design question — likely
  fits this same gate's follow-up or a trivial separate pass, whichever the Commander prefers.

## Workflow feedback

- The handoff's line-number anchors for `CrewSpec`/`build_crew_argv`/`build_entry`/`CliBackend`/
  `main()` were all accurate at execution time — no drift found on re-confirmation.
- The bulk-fix approach (precise line-targeted script for the ~27 `model=None` → `model="sonnet"`
  call sites sharing byte-identical trailing context) was much safer than a blanket `replace_all`,
  which would have silently caught the 17 intentional `build_crew_argv` direct-call tests and the
  one `build_entry` direct-call test that must NOT change. Worth naming as a pattern for future
  large-surface-area test reconciliation gates.
