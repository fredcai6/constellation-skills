# Plan Critic — adversarial review of the minimal-diff candidate

Scope: `.agent-work/w3-door/plan-candidate-minimal-diff.md` as the plan being adopted,
checked against the actual current code in `scripts/run_crew.py` (lines 1260-1362) and
`tests/test_crew_launcher.py`. No fixes applied; findings only.

## Findings

- **[REAL ISSUE — test-coverage, high severity]** Two tests in a *different* class than the
  one the plan names — `ParentLeaseHeartbeatTests.test_dispatch_skips_parent_heartbeat_in_shared_spine_case`
  (tests/test_crew_launcher.py:4525-4576) and
  `test_resume_skips_parent_heartbeat_in_shared_spine_case` (tests/test_crew_launcher.py:4578-4624)
  — both dispatch/resume with `spine=None` while the test process's own ambient
  `SPINE_FILE`/`SPINE_SESSION` are set to real values, then assert the CHILD's env carries
  the SAME ambient pair (`observed["env"]["SPINE_FILE"] == str(spine)`,
  `observed["env"]["SPINE_SESSION"] == session`) and that no parent-heartbeat thread starts
  (the "shared spine, skip the redundant writer" branch of `_parent_lease_heartbeat`,
  run_crew.py:1793-1798, which compares `child_env.get("SPINE_FILE") == spine_file`). This
  is the exact ambient-inheriting-on-`spine=None` behavior the fix removes, exercised from
  a second, unrelated angle the plan's author never named or grepped for. Post-fix: (a) both
  assertions on `observed["env"]["SPINE_FILE"/"SPINE_SESSION"]` fail outright (`KeyError` or
  mismatch, since those keys will no longer exist in the child env at all), and (b) the
  underlying scenario each test exercises — "a `spine=None` dispatch/resume from a
  door-bound parent shares the parent's exact pair" — becomes structurally impossible after
  the fix (a cleared child env can never equal a non-empty parent env), so
  `_parent_lease_heartbeat`'s "differs" branch will now *always* fire for a `spine=None`
  dispatch from a door-bound parent, meaning every such dispatch newly starts a parent
  heartbeat thread that the old contract correctly judged redundant. This is a genuine,
  unnamed second-order behavior change from the fix, not just two more tests to flip. The
  gate plan must either (1) rewrite these two tests to trigger the "shared spine" case via
  an explicit matching `--spine` instead of `spine=None` (since `spine=None` no longer means
  "shares the parent's spine," it means "no spine at all"), or (2) explicitly accept and
  document that a `spine=None` dispatch from a door-bound parent now always heartbeats the
  parent's lease, and update these two tests' assertions accordingly. Either way, the
  current plan's "flip one test, add one new test" gate list is incomplete — verified by
  reading the tests myself, not by trusting the plan's silence on them.

- **[REAL ISSUE — docstring correctness, moderate]** `_crew_door_env`'s current docstring
  (run_crew.py:1332-1339) ends: "No `spine` means the inherited-environment route is
  genuinely untouched, both variables together, exactly as `crew_env()`'s own contract
  already promises." The plan's instruction is "update the docstring to state the new
  contract: no spine means the crew gets NO door — both vars are actively cleared, not
  inherited," but it never names this specific trailing clause for removal. Under
  minimal-diff, `crew_env`'s own contract is deliberately left unchanged ("leave untouched
  when omitted") — the entire point of the minimal-diff seam is that `_crew_door_env` now
  *diverges* from `crew_env`'s contract for the `spine=None` branch, not matches it. An
  implementer who adds a new sentence about "actively cleared" without also striking "...
  exactly as `crew_env()`'s own contract already promises" will leave two directly
  contradictory claims adjacent in the same docstring. The plan should name this exact
  sentence for deletion, not just "state the new contract."

- **[REAL ISSUE — stale cross-reference, minor]** The plan says to rename
  `test_dispatch_without_spine_leaves_ambient_pair_untouched` to
  `test_dispatch_without_spine_gets_no_door` and "update its docstring/comment accordingly"
  (i.e. the renamed test's own comment). It does not mention that a *different* test,
  `test_dispatch_without_spine_binds_neither_var` (tests/test_crew_launcher.py:1922-1928),
  contains a hand-written cross-reference comment naming the OLD test by its exact name:
  "... (the bootstrap-mismatch the Admiral ruled against) — see
  `test_dispatch_without_spine_leaves_ambient_pair_untouched`." Renaming the target test
  without updating this comment leaves a dangling reference to a test name that no longer
  exists anywhere in the file — not a functional break, but doc rot the plan should name
  explicitly (grepped and confirmed: this is the only other reference to that test name in
  non-archived, non-plan files).

- **[REAL ISSUE — under-specification, minor]** The plan's instruction to "add one new test
  exercising `resume` ... without a stored spine, confirming the same clearing applies" does
  not specify that this new test must set REAL (non-empty) ambient `SPINE_FILE`/
  `SPINE_SESSION` values before calling `resume_crew`, mirroring the flipped dispatch test's
  control shape. The nearest existing resume-without-spine test,
  `test_resume_of_legacy_entry_without_spine_key_does_not_crash`
  (tests/test_crew_launcher.py:2046-2068), uses `no_ambient_spine_env()` to strip ambient
  vars to nothing FIRST — under that shape, "assert absent" is trivially true both before
  and after this fix and proves nothing about active clearing. An implementer who copies the
  neighboring pattern (the path of least resistance) instead of the flipped dispatch test's
  pattern (real ambient values set, then asserted gone) would add a test that looks like new
  coverage but does not actually exercise clearing. The plan should say explicitly: set
  non-empty ambient `SPINE_FILE`/`SPINE_SESSION` before the resume call, not
  `no_ambient_spine_env()`.

- **[NON-ISSUE, verified]** `env.pop("SPINE_FILE", None)` / `env.pop("SPINE_SESSION", None)`
  called after `crew_env(...)` returns is correctly ordered and safe. `crew_env` builds
  `env = dict(os.environ if base_env is None else base_env)` — a fresh dict, never a live
  reference to `os.environ` — before doing anything else (run_crew.py:1309). Its only other
  effects are `PYTHONUTF8`/`PYTHONIOENCODING` via `setdefault`, and `SPINE_PARENT`/
  `CREW_SCRATCH_DIR` via conditional assignment (lines 1310-1319) — none of these four keys
  overlap with the two being popped, and none of them can be reintroduced by popping the
  spine pair. No other key `crew_env` sets needs clearing for this branch.

- **[NON-ISSUE, verified]** The plan's claim "`crew_env` has exactly one caller in the
  entire repo" holds up under an independent repo-wide grep for `crew_env(`. The only
  production call sites are the two inside `_crew_door_env` itself (run_crew.py:1355-1356).
  Test files (`tests/test_crew_launcher.py`) call `RC.crew_env(...)` directly to unit-test
  `crew_env`'s own contract, but minimal-diff explicitly leaves that contract and its tests
  untouched, so this doesn't undermine the claim in the sense the plan means it (no
  *production* caller besides `_crew_door_env`).

- **[NON-ISSUE, verified with history]** `crew_env`'s docstring line 1279-1280 — "(this is
  what lets the Admiral's own bootstrap, which passes `base_env` but no `--spine`, keep
  working)" — traces (via `.agent-work/archive/2026-08-12-epic-418-followon-closeout/`) to a
  one-time issue-#418 bootstrapping technique: a dispatch script exported `SPINE_FILE`/
  `SPINE_SESSION` into ITS OWN process env and called `run_crew.py` with no `--spine`,
  relying on inheritance, to test the door-binding feature before `--spine` existed. Grepped
  all non-archived scripts/skills for "export SPINE_FILE" or an equivalent live pattern —
  none found. Dropping this framing per the plan is safe; it does not silently break a
  still-relied-upon operational path. (Minor, non-blocking suggestion: the replacement text
  could say *why* it's being dropped — historical/obsolete bootstrap trick, not a live
  caller — so the next reader isn't left wondering, but this is a nicety, not a defect.)

- **[NON-ISSUE, verified]** The test-shape question ("is `assertNotIn(\"SPINE_FILE\", env)`
  / `assertNotIn(\"SPINE_SESSION\", env)` the right assertion, or could scratch_dir/parent
  logic re-add one of these keys?") — no. `scratch_dir` only ever sets `CREW_SCRATCH_DIR`;
  parent resolution only ever sets `SPINE_PARENT`; neither can reintroduce `SPINE_FILE` or
  `SPINE_SESSION` under any input, including edge cases (empty string parent, missing
  scratch_dir). The proposed assertion shape is correct and sufficient.

## What I tried that did not pan out

Also checked, found nothing wrong: whether any test directly calling `RC.crew_env(...)` at
the unit level (`CrewEnvSpineBindingTests`, `ParentEnvBindingTests`) implicitly depends on
`_crew_door_env`'s spine=None clearing behavior — they don't; they test `crew_env` in
isolation and are correctly left alone by minimal-diff. Also checked
`test_whitespace_only_parent_binds_unknown_in_the_door_env` (line 599-605), which calls
`_crew_door_env(..., spine=None, ...)` directly — it only asserts `SPINE_PARENT`, never
`SPINE_FILE`/`SPINE_SESSION`, so it is unaffected. Also checked
`DoorHijackRealEngineControlTests.test_child_claims_its_own_spine_dispatcher_lease_untouched`
(line 2810) and the `ExternalDispatchTests`/`FinalizeFromExitCodeTests` classes — all
dispatch with an explicit (non-`None`) spine or exercise unrelated code paths
(`finalize_from_exit_code`, `build_entry`'s `door_bound` field), none touch the `spine=None`
ambient-inheritance contract.

## Dispositions (Commander, post-critique)

- **Finding 1 (ParentLeaseHeartbeatTests, high)** — CONFIRMED, and traced one level
  deeper: `assignment_session_name()` always derives a 4-segment
  `constellation/<work_id>/<gate>/<role>` session for an EXPLICIT `--spine`, which
  structurally can never equal a bare commander-shaped ambient session like
  `constellation/w/commander` (3 segments). The two tests' "shared spine" scenario was
  therefore only ever reachable through the exact `spine=None`-inherits-verbatim defect
  this mission removes — it was a symptom of the bug, not independent coverage of a
  reachable good-path case. Disposition: REWRITE both tests to assert the NEW correct
  behavior (a `spine=None` dispatch/resume from a door-bound parent now ALWAYS starts the
  parent heartbeat, since the child gets no door and cannot maintain any lease itself);
  rename off "shared_spine_case" since that case no longer applies to `spine=None`. Do
  NOT modify `_parent_lease_heartbeat`'s own comparison logic — it stays generically
  correct, just structurally unreachable via `spine=None` now. Filed as a triage
  candidate: whether the "shared spine, skip" branch is reachable via ANY real caller at
  all post-fix, or is now dead code — not fixed here (behavior-preserving discipline,
  wave-3 concurrent-lane caution). Folded into g1 below.
- **Finding 2 (docstring, moderate)** — CONFIRMED. g1's imperative names the exact
  trailing clause for deletion.
- **Finding 3 (stale cross-reference, minor)** — CONFIRMED. g1's imperative names the
  comment at line ~1928 for update.
- **Finding 4 (new resume test under-specified, minor)** — CONFIRMED. g1's imperative
  specifies real ambient values, not `no_ambient_spine_env()`.
- Non-issues: accepted as verified; no action.
