# Implementation Result

## Assigned gate
g1

## Completed slice
`_crew_door_env` (in `scripts/run_crew.py`) now actively clears `SPINE_FILE` and
`SPINE_SESSION` from the returned env when `spine is None`, instead of leaving
whatever the dispatching process's own ambient environment happens to carry. A
crew dispatched (or resumed) with no `--spine` now gets NO door at all — it can
never appear to silently share a spine it does not own. Both vars are cleared
together (`decision:clear-both-or-neither`), never one alone. `crew_env` itself
is unchanged — the fix lives entirely inside `_crew_door_env`, after it calls
into `crew_env`.

Both affected docstrings (`crew_env`'s and `_crew_door_env`'s) were updated to
state the new contract and drop the specific clauses the close criteria named
as contradictory. The test suite was extended/rewritten per the close criteria:
one rename+rewrite, one new test (`CliBackend().resume` no-stored-spine case),
and two heartbeat tests rewritten because the fix makes their old "shared
spine via `spine=None`" scenario structurally impossible.

## Scope
**Files changed:**
- `scripts/run_crew.py`
- `tests/test_crew_launcher.py`

**Specific exclusions touched:** no — `crew_env`'s signature/behavior,
`--spine`'s meaning, `SPINE_PARENT`, `CREW_SCRATCH_DIR`, the registry schema,
and `_parent_lease_heartbeat`'s comparison logic are all untouched. Verified
`tests/test_in_harness_crew_isolation.py` (which references `_crew_door_env`
by name in a mock-patch target string only, never asserting its return value)
still passes unmodified under the full suite run — no edit was needed there.

## Behavior changed
Yes — `_crew_door_env(spine=None, ...)` now returns an env with neither
`SPINE_FILE` nor `SPINE_SESSION` present, where it previously left both
inherited from the dispatching process's ambient environment (or from
`os.environ` when `base_env` was not overridden). This affects both
`CliBackend.dispatch` (fresh dispatch with no `--spine`) and
`CliBackend.resume` (resuming an entry with no stored `spine`, including
legacy entries with no `spine` key at all).

## Map Impact
Map is DEGRADED-UNPARSEABLE per the inbound anchors — no citable map entry to
reconcile against. Recording narrative-only notes for whenever the map is
rebuilt:

- **Structural anchors touched:** `scripts/run_crew.py::_crew_door_env`
  (~line 1326) — body's `spine is None` branch now actively clears
  `SPINE_FILE`/`SPINE_SESSION` instead of leaving them inherited;
  `scripts/run_crew.py::crew_env` (~line 1264) — docstring only, no
  behavior change.
- **Decision candidates / resolved decisions:** `decision:clear-both-or-neither`
  is now implemented in code (previously documented intent only, per the
  handoff's decision anchor) — SPINE_FILE and SPINE_SESSION are cleared as a
  pair, never one alone, whenever `spine is None`.
- **Claims/evidence produced:** confirmed by direct call (see Evidence below)
  that `_crew_door_env(spine=None, ...)` clears both vars even when a real
  non-empty ambient pair is set in `os.environ` — the exact "Honest-Null"
  scenario the close criteria required proof against.
- **Trust limitations / drift found:** none new; the map was already
  DEGRADED-UNPARSEABLE going in.
- **Triage candidates:** `map/INDEX.md`'s committed entity count (5723) is now
  stale against a fresh `python -m scripts.code_map build --root .` (would
  read 5724, one new test method added) — see Out-of-scope observations below;
  this is a mechanical wave-closeout regen, not something this lane should do
  mid-wave against three sibling lanes' concurrent test-file edits.

## Test mode
**Required:** test-after (behavior change to an existing, already-tested
function; the test surface already exists and is extended/corrected in the
same gate).
**Satisfied:** yes — all renamed/rewritten/new tests pass; full
`tests/test_crew_launcher.py` run is green (262/262).

## Evidence

```bash
$ python3 -m pytest -q tests/test_crew_launcher.py
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 82%]
..............................................                           [100%]
262 passed in 2.21s
```

```bash
$ python3 -m unittest tests.test_crew_launcher.DispatchDoorBindingTests tests.test_crew_launcher.ParentLeaseHeartbeatTests -v
test_dispatch_explicit_spine_overrides_ambient_dispatcher_binding ... ok
test_dispatch_without_spine_binds_neither_var ... ok
test_dispatch_without_spine_gets_no_door ... ok
test_fresh_dispatch_binds_own_spine_and_assignment_session ... ok
test_resume_of_legacy_entry_without_spine_key_does_not_crash ... ok
test_resume_rebinds_door_to_the_stored_spine ... ok
test_resume_via_cli_backend_with_no_stored_spine_gets_no_door ... ok
test_child_env_without_pair_keeps_parent_heartbeat ... ok
test_dispatch_heartbeats_parent_lease_when_child_pair_differs ... ok
test_dispatch_heartbeats_parent_lease_when_spine_is_none ... ok
test_heartbeat_exception_is_swallowed_not_propagated ... ok
test_noop_when_ambient_vars_unset ... ok
test_noop_when_only_one_ambient_var_set ... ok
test_resume_heartbeats_parent_lease_when_spine_is_none ... ok
test_thread_advances_last_heartbeat_while_active ... ok
test_thread_is_joined_before_context_manager_returns ... ok

Ran 16 tests in 0.355s

OK
```

```bash
$ python3 -m pytest -q
[... 3729 passed lines omitted ...]
=================================== FAILURES ===================================
_ MapTreeFreshnessTests.test_map_tree_freshness_root_index_matches_a_fresh_build _
AssertionError: '# co[223 chars], 5724 entities\n...' != '# co[223 chars], 5723 entities\n...'
map/INDEX.md is stale: rerun `python -m scripts.code_map build --root .` and commit the result
=========================== short test summary info ============================
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 3729 passed, 9 skipped, 1277 subtests passed in 212.14s (0:03:32)
```

Confirmed via `git stash` / `git stash pop` that this ONE failure does not exist
on the pre-change baseline (`git stash; pytest -q tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build` → `1 passed`) — it is a direct, mechanical
consequence of this gate adding one new test method (`test_resume_via_cli_backend_with_no_stored_spine_gets_no_door`)
to `tests/test_crew_launcher.py`, which bumps the map's committed entity count
by exactly one (5723 → 5724). See Out-of-scope observations.

Confirmatory direct check (not load-bearing, per the handoff):
```bash
$ python3 -c "
import sys, os
sys.path.insert(0, 'scripts')
import run_crew as RC
os.environ['SPINE_FILE'] = '/tmp/ambient-spine.json'
os.environ['SPINE_SESSION'] = 'constellation/ambient/commander'
env = RC._crew_door_env(work_id='w', gate='g1', role='implementer', spine=None,
                         root=__import__('pathlib').Path('.'), parent='test-parent')
assert 'SPINE_FILE' not in env
assert 'SPINE_SESSION' not in env
print('OK: spine=None gets no door even with real ambient pair set')
"
OK: spine=None gets no door even with real ambient pair set
```

**Result:** pass — `tests/test_crew_launcher.py` fully green (262/262); full
suite green except the one pre-existing-class, self-inflicted map-freshness
check described above (3729 passed, 9 skipped, 1 failed — the map-staleness
check, not a behavioral regression).

## Docs/contracts touched
- `scripts/run_crew.py` — `crew_env` and `_crew_door_env` docstrings (see diff
  below; both contradictory clauses named in the close criteria are deleted,
  not merely supplemented).

```diff
diff --git a/scripts/run_crew.py b/scripts/run_crew.py
index edd42775..aeccb674 100644
--- a/scripts/run_crew.py
+++ b/scripts/run_crew.py
@@ -1276,8 +1276,11 @@ def crew_env(
     tail). Both are optional so a caller with no spine to bind (e.g. a legacy
     registry entry recorded before this field existed) still gets a valid
     environment — when omitted (`None`), the inherited-environment route is left
-    exactly as it is (this is what lets the Admiral's own bootstrap, which passes
-    `base_env` but no `--spine`, keep working).
+    exactly as it is. This generic "leave inherited when omitted" contract is
+    unchanged here; `_crew_door_env` (the crew-dispatch door specifically) no
+    longer relies on it for its `spine=None` branch -- it actively clears
+    `SPINE_FILE`/`SPINE_SESSION` from the env this function returns in that
+    case, so a crew dispatched without `--spine` gets no door at all.
 
     When a binding IS given, it is ASSIGNED, not `setdefault`-ed: an explicit
     `spine_file`/`spine_session` is more specific than whatever the DISPATCHING
@@ -1332,11 +1335,14 @@ def _crew_door_env(
     `spine_file` and `spine_session` are bound as a PAIR, and ONLY when `spine`
     was given. Deriving `spine_session` unconditionally (even with `spine=None`)
     used to hand a no-`--spine` child a mismatched pair: whatever SPINE_FILE the
-    DISPATCHING process happened to have ambient (left untouched, correctly) next
-    to a freshly-derived SPINE_SESSION belonging to a different spine entirely —
-    a file/identity pair that never matched each other. No `spine` means the
-    inherited-environment route is genuinely untouched, both variables together,
-    exactly as `crew_env()`'s own contract already promises.
+    DISPATCHING process happened to have ambient next to a freshly-derived
+    SPINE_SESSION belonging to a different spine entirely — a file/identity pair
+    that never matched each other. No `spine` means NO door at all: SPINE_FILE
+    and SPINE_SESSION are actively CLEARED from the child's env, together,
+    never left to whatever the DISPATCHING process's own ambient environment
+    happens to carry -- a crew dispatched without `--spine` must never be able
+    to silently drive a spine it does not own, its dispatcher's
+    (`decision:clear-both-or-neither`).
 
     `SPINE_PARENT`, unlike the spine pair, is bound UNCONDITIONALLY -- every
     crew this launches gets a definitive answer, `parent` if given else
@@ -1352,7 +1358,10 @@ def _crew_door_env(
     benefit, since there is exactly one caller-known path either way."""
     resolved_parent = _normalize_parent(parent) or UNKNOWN_PARENT
     if spine is None:
-        return crew_env(parent=resolved_parent, scratch_dir=scratch_dir)
+        env = crew_env(parent=resolved_parent, scratch_dir=scratch_dir)
+        env.pop("SPINE_FILE", None)
+        env.pop("SPINE_SESSION", None)
+        return env
     return crew_env(
         spine_file=_resolve_optional_path(spine, root),
         spine_session=assignment_session_name(work_id, gate, role),
```

Full diff stat: `scripts/run_crew.py | 25 +++++++----` and
`tests/test_crew_launcher.py | 106 +++++++++++++++++++++++++++++++-------------`
(92 insertions, 39 deletions total across both files).

## Assumptions
- The new `CliBackend().resume(...)` test (no stored spine) uses
  `RC.build_entry(...)` without passing `spine=` (default `None`, recorded as
  `None` per `build_entry`'s own documented "recorded null, not omitted"
  shape) to construct a registry entry with no stored spine, matching the
  handoff's "no stored spine on the registry entry" wording — this reads as
  equivalent to (and slightly more realistic than) a legacy entry with the
  key entirely absent, since it exercises the same `entry.get("spine")` →
  `None` path through `_crew_door_env`.
- For the two rewritten `ParentLeaseHeartbeatTests`, mirrored the exact
  assertion shape of `test_dispatch_heartbeats_parent_lease_when_child_pair_differs`
  as instructed, adapted to assert the child's env has NEITHER `SPINE_FILE`
  nor `SPINE_SESSION` (rather than "differs") inside the launch callback,
  since a spine=None child now gets no door at all rather than a differing one.
- Interpreted "the exact assertion shape to mirror for the heartbeats case" as
  applying to the heartbeat-advanced / thread-liveness assertions specifically
  (`assertGreater(last_heartbeat, before)`, `assertFalse(heartbeat_thread_alive())`
  after return), not to the env content assertions, which necessarily differ
  (no-door vs. differing-pair).

## Stop conditions hit
None. No allowed-scope exceedance, no specific-exclusion touch, and no
caller found that legitimately depends on the old inherited-pair behavior
(the Honest-Null clause) — the mission's Protected Intent (a crew dispatched
without `--spine` must never silently drive a spine it does not own) is the
governing contract, and no caller relies on the opposite.

## Out-of-scope observations
- `map/INDEX.md`'s committed entity count is now stale by exactly one
  (5723 → 5724) purely because this gate added one new test method inside
  its own allowed scope (`tests/test_crew_launcher.py`). This trips
  `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  in the full-suite run — confirmed via `git stash`/`git stash pop` that the
  pre-change baseline passes this specific test. Regenerating
  `map/INDEX.md` (`python -m scripts.code_map build --root .`) is out of this
  lane's file ownership this wave (`scripts/run_crew.py` /
  `tests/test_crew_launcher.py` only), and three sibling lanes are editing
  other files concurrently this wave — a per-lane map regen now would race
  their own test-count changes. Recommend a single map regen once, at wave
  closeout after all three lanes land, rather than per-lane. Flagging for
  Commander/Cartographer rather than fixing myself.

## Workflow Feedback
- **Handoff gaps:** none — the Close Criteria section named every test by
  exact string, gave a concrete mirror-test to copy the assertion shape from,
  and named the exact structural reason the two heartbeat tests become
  impossible. This was unusually precise and left little to interpret.
- **Context rediscovered:** had to read `CliBackend.dispatch`/`resume` bodies
  directly (lines ~1895-2053) to confirm both call `_crew_door_env` the same
  way and that `entry.get("spine")` is the resume-path analog of dispatch's
  `spec.spine` — the handoff's Map Anchors named the line ranges but the map
  itself was DEGRADED-UNPARSEABLE, so this was source-reading, not map-reading,
  exactly as the anchor note warned.
- **Instructions improvised around:** the constellation-implementer skill's
  default engine-drive workflow (claim a checklist lease, drive `current`/
  `advance`) does not apply here — the dispatching harness explicitly stated
  I have no `mcp__spine__*` tool on my surface and this is a plain
  implement-and-report task, not a spine-driving one. Followed that explicit
  instruction over the skill's default first-command instinct, and skipped
  straight to reading the handoff and implementing.
- **What would have made this easier:** nothing concrete — the one genuine
  surprise (the map-freshness test tripping on an unrelated file this lane
  doesn't own) is a wave-shape issue (concurrent lanes + a suite-wide
  freshness check keyed on a file no single lane should touch), not a gap in
  this handoff specifically. Worth Commander/Admiral knowing this pattern will
  recur for every lane in this wave that adds/removes a test method, though —
  each lane will independently trip the same freshness check unless it's
  suppressed or deferred to wave closeout.

## Return status
`complete`
