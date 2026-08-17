# Implementation Result

## Assigned gate
`g2` -- reap + child-plan release (the #552 mechanism). Gate 2 of 3.

## Completed slice
Added `force_reap(project_dir) -> dict | None` and `_release_child_plans(spine_path, work_dir, *, root, reason) -> dict` to `scripts/spine_lifecycle.py`, plus their tests to `tests/test_spine_lifecycle.py`. `force_reap` is a two-line library call into `spine_rail._binding_transaction` with an identity mutate; `_release_child_plans` implements all three shipped safety properties (lineage not proximity, honest non-owner release, escape refusal) and routes every engine call through g1's `_engine_call` choke point.

## Scope
**Files changed:**
- `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease/scripts/spine_lifecycle.py`
- `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease/tests/test_spine_lifecycle.py`

**Specific exclusions touched:** no -- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py` all show an empty `git diff --stat` (evidence below).

## Behavior changed
Yes. `spine_lifecycle.py` gains two new public/private functions:
- `force_reap(project_dir)`: forces an immediate persist of the binding store's already-reaped map, rather than waiting for a future unrelated transaction to trigger the same reap.
- `_release_child_plans(spine_path, work_dir, *, root, reason)`: releases the lease of every child plan a parent spine's tasks structurally declare via `child_checklist`, and reports what was deliberately left alone.

Neither is wired into a production caller yet -- that is g3's `finish_work`, out of this gate's scope (confirmed by the wiring grep below).

## Map Impact
- **Structural anchors touched:** `scripts/spine_lifecycle.py` -- two new module-level functions appended after `_advance_and_release` (g1's closeout primitives section), plus a new `sys.path.insert` for `scripts/hooks/` and a new top-level `import spine_rail`.
- **Capabilities added/changed/affected:** `capability:force-reap` -- immediate binding-store reap, a library call into `spine_rail._binding_transaction`. `capability:release-child-plans` -- structural (lineage-based) child-plan lease release, the mechanism half of #552's "17 stale leases sit inside archive/" defect. Both are currently dormant (no production caller) until g3's `finish_work` composes them.
- **Constraints/assumptions touched:** `constraint:fenced-files-untouched` honored -- `checklist_engine.py`/`mcp_spine_server.py`/`spine_rail.py` all show empty diffs. `constraint:single-engine-choke-point` honored -- `checklist_engine.main` still appears exactly once in the module, inside `_engine_call`; `_release_child_plans` calls `_engine_call`, never `checklist_engine.main` directly.
- **Decision candidates / resolved decisions:** `decision:child-plans-count` (the Map Anchors' inbound decision) is now implemented, not merely designed -- `_release_child_plans` is the mechanism that releases child leases, not just the top-level spine's. `@grade: settled/human` per the handoff's Authority section (lineage-based identification, honest non-owner release, realpath containment refusal, identity-mutate force_reap were all pre-decided; not re-litigated here).
- **Trust limitations / drift found:** the handoff's Map Anchor claimed "release each child... the engine records a forced non-owner release, so the override leaves a real audit trail" implying a journal entry -- this is only true for verbs in `MUTATING_VERBS` (`checklist_engine.py:70-74`); `release` is explicitly NOT a member (handled in the separate claim/heartbeat/release lease-management branch of `dispatch`), so no journal line is written for a release call at all. The audit trail `--force --reason` produces is the persisted `engine_session` state (`status: released`) plus whatever the CALLER (here, the test; in production, a Commander) chooses to log about the call -- not a journal entry. This surprised my own m0-context attestation, which assumed journaling coverage before I read `MUTATING_VERBS` directly; corrected in the m2 why-record. g3 should not assume a journal-based audit trail for the child releases either.
- **Triage candidates:** none found in scope for this gate.

## Test mode
**Required:** test-after (per handoff).
**Satisfied:** yes -- all tests written after each function's implementation, run and green before advancing each gate.

## Evidence

### Full suite, pre/post counts
Pre-change baseline (recorded at m0-context): 95 passed.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q
```
```
........................................................................ [ 69%]
................................                                         [100%]
104 passed in 0.52s
```
Post-change: **104 passed** (95 baseline + 2 `TestForceReap` + 7 `TestReleaseChildPlans`).

### Fenced-file diff -- must be empty
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py
```
Output: **(empty)**. Confirmed by exit code 0 with no stdout.

### force_reap immediacy test (close criterion 1) -- test body and passing output
```python
class TestForceReap:
    def test_innocent_a_released_targets_entry_is_gone_immediately(self, tmp_path):
        # Close criterion: a binding-store entry whose target spine is already
        # `released` is gone IMMEDIATELY after the call -- read via
        # spine_rail.load_binding, not by waiting for another transaction.
        target = _write_binding_target(
            tmp_path / ".agent-work" / "some-work" / "spine.json", status="released"
        )
        # Precondition sanity: the fixture's target really does read
        # "released" before force_reap ever runs -- the reap is conditional on
        # this, not unconditional.
        assert spine_rail.load_spine(target)["engine_session"]["status"] == "released"

        spine_rail.save_binding(tmp_path, {"s1": {str(target): _binding_entry(spine=target)}})
        before = spine_rail.load_binding(tmp_path)
        assert str(target) in before.get("s1", {}), before

        result = sl.force_reap(tmp_path)

        assert result is not None, "fail-open path taken unexpectedly"
        after = spine_rail.load_binding(tmp_path)
        assert str(target) not in after.get("s1", {}), after
```
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q -k ForceReap
```
```
..                                                                       [100%]
2 passed, 102 deselected in 0.12s
```

### NEGATIVE test 1 -- spine outside `work_dir` sharing a `work_id` prefix, never touched (close criterion 3)
```python
def test_violating_a_spine_outside_work_dir_sharing_a_prefix_is_never_touched(self, tmp_path):
    # Property 1 (directory proximity is the WRONG predicate), the sharp
    # form: a sibling directory whose NAME merely shares a string prefix
    # with work_dir ("cmdr-g" vs "cmdr-g2") is not "inside" it by any
    # path-containment test, and must never be scanned at all.
    work_dir = tmp_path / "cmdr-g"
    sibling_dir = tmp_path / "cmdr-g2"
    outside_spine = _write_json(sibling_dir / "spine.json", _leased_plan("sibling-session"))
    spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children([]))

    result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="x")

    assert str(outside_spine) not in result["released"]
    assert str(outside_spine) not in result["unclaimed_active"]
    assert json.loads(outside_spine.read_text())["engine_session"]["status"] == "active"
```

### NEGATIVE test 2 -- unclaimed active-leased JSON left alone and reported (close criterion 4)
```python
def test_violating_unclaimed_active_json_is_left_alone_and_reported(self, tmp_path):
    # Property 1, the ordinary form: an active-leased JSON genuinely
    # UNDER work_dir that no task declares as its child_checklist must be
    # left alone -- releasing it would seize a lease a different,
    # still-working agent genuinely holds.
    work_dir = tmp_path / "cmdr"
    orphan_path = _write_json(work_dir / "some-other-agents-plan.json", _leased_plan("orphan-session"))
    spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children([]))

    result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="x")

    assert result["released"] == []
    assert result["unclaimed_active"] == [str(orphan_path)]
    assert json.loads(orphan_path.read_text())["engine_session"]["status"] == "active"
```

### NEGATIVE test 3 -- symlink escape refused (close criterion 5)
```python
def test_violating_a_symlink_inside_work_dir_escaping_outside_is_refused(self, tmp_path):
    # Property 3: a symlink that lexically sits inside work_dir (and is
    # even DECLARED as a child_checklist) but whose realpath walks
    # outside it must be refused -- the real target's lease survives.
    work_dir = tmp_path / "cmdr"
    outside_dir = tmp_path / "outside"
    real_target = _write_json(outside_dir / "real-spine.json", _leased_plan("outside-session"))

    symlink_path = work_dir / "escape.json"
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        symlink_path.symlink_to(real_target)
    except OSError:
        pytest.skip("symlinks not supported on this platform/permission level")

    spine_path = _write_json(work_dir / "spine.json", _parent_spine_with_children(["escape.json"]))

    result = sl._release_child_plans(spine_path, work_dir, root=tmp_path, reason="x")

    assert str(symlink_path) not in result["released"]
    assert str(real_target) not in result["released"]
    assert json.loads(real_target.read_text())["engine_session"]["status"] == "active"
```

### All three NEGATIVE tests run individually, by name
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -k "ReleaseChildPlans and violating" -v
```
```
tests/test_spine_lifecycle.py::TestReleaseChildPlans::test_violating_a_spine_outside_work_dir_sharing_a_prefix_is_never_touched PASSED [ 33%]
tests/test_spine_lifecycle.py::TestReleaseChildPlans::test_violating_unclaimed_active_json_is_left_alone_and_reported PASSED [ 66%]
tests/test_spine_lifecycle.py::TestReleaseChildPlans::test_violating_a_symlink_inside_work_dir_escaping_outside_is_refused PASSED [100%]

====================== 3 passed, 101 deselected in 0.04s =======================
```

### No read of a child's own `session_id` for use as the caller id (grep own diff, confirmatory)
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && py -c "
import ast
tree = ast.parse(open('scripts/spine_lifecycle.py', encoding='utf-8').read())
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == '_release_child_plans':
        src = ast.get_source_segment(open('scripts/spine_lifecycle.py', encoding='utf-8').read(), node)
        print(src)
" | grep -n "session_id\|session\.get\|data\.get"
```
```
62:        parent_session.get("session_id")
63:        if isinstance(parent_session, dict) and parent_session.get("session_id")
114:        session = data.get("engine_session")
115:        if not isinstance(session, dict) or session.get("status") != "active"
```
Only the PARENT's own `engine_session.session_id` is read (once, before the scan loop, from `spine` -- the dict loaded from `spine_path`). Inside the per-candidate scan loop, `data`/`session` (the loaded child JSON) are read only for `.get("status")`, never `.get("session_id")`.

### git check-ignore -- both files not ignored
```bash
git check-ignore scripts/spine_lifecycle.py   # exit 1
git check-ignore tests/test_spine_lifecycle.py  # exit 1
```
Both confirmed exit 1 (not ignored). Both already tracked; nothing new appears only in `git status` this gate beyond the modification to these two already-tracked files (`.agent-work/...` scaffolding and my own plan/result files are separately untracked working-area artifacts, not deliverables).

## TDD evidence, if required
Test-after per the handoff's Test Mode -- no red step required or produced. Each function was written, then its tests were written and run green in the same working step; no failing-first evidence was generated or is claimed.

## Docs/contracts touched
None. `scripts/spine_lifecycle.py`'s own module docstring was not updated with a new bullet for `force_reap`/`_release_child_plans` -- flagged below as a workflow/consistency note for g3 or a later pass, since the existing docstring's "Pure/impure split" section currently only narrates through `_advance_and_release`.

## Assumptions
- `child_checklist` values are always simple relative filenames sitting directly beside the parent spine (`interrogation.json`, `execute.json`, `g1-implementer-plan.json`, ...), matching every live example found in this repo's `.agent-work/archive/**/spine.json` files (`grep -rn '"child_checklist"'`). An absolute `child_checklist` value is also handled (used as-is before the containment check) though none was found in the wild.
- A declared child whose release the engine still refuses (e.g. an empty `--reason`, though this function never constructs one itself) is reported in `unclaimed_active` rather than raising -- its lease genuinely remains active, and silently dropping it would be the swallowed-refusal defect wearing a different hat. This branch is not exercised by any test, since every test-driven call passes a non-empty `reason`; it is a defensive default, not a proven behavior.
- The caller id passed to `release --session-id` is the PARENT spine's own `engine_session.session_id`, falling back to a synthetic `"parent-closeout:<spine_path>"` label only if the parent spine carries none. The handoff did not prescribe an exact caller-id value, only forbade echoing the child's own id; using the parent's real session id was chosen as the most honest available identity (matches "release each child as the explicit non-owner it is").

## Stop conditions hit
None. Scope was not exceeded, no fenced file needed touching, every parent-spine fixture used in testing carried `child_checklist` fields (real or explicitly absent/null), and all required evidence was producible.

## Out-of-scope observations
- The module docstring at the top of `scripts/spine_lifecycle.py` (lines ~1-46) narrates the pure/impure split through `_advance_and_release` but was not extended to describe `force_reap`/`_release_child_plans`. Left as-is per "make the minimal change" and because g3 will add a third and probably final closeout primitive (`finish_work`) to this same section -- updating the docstring once, after g3 lands, avoids two touches to the same paragraph. Flagged here so g3 (or its reviewer) does not miss it.
- `_release_child_plans` walks `work_dir` with `Path.rglob("*.json")`, which follows directory symlinks during traversal (not just leaf-file symlinks) by Python's own glob semantics. No test exercises a symlinked *directory* escape (only a symlinked *file*, per close criterion 5's exact wording). This is a plausible variant of the same escape class; not fixed here because the handoff's close criteria and required evidence name the file-symlink case specifically, and widening the fixture surface without a named requirement would be scope-creep. Recorded as a triage candidate for g3/reviewer if a directory-symlink escape is judged in-scope for #552's guarantee.

## Workflow Feedback

- **Handoff gaps:** none -- confirmed after review: task, protected intent, allowed scope, exclusions, constraints, map anchors, required evidence, wiring grep, verification commands, authority, and stop conditions were all present and internally consistent. The one factual slip was mine, not the handoff's (see next bullet).
- **Context rediscovered:** the handoff's own prose ("the engine records a forced non-owner release, so the override leaves a real audit trail") reads as implying a journal entry, but `release` is not a member of `checklist_engine.MUTATING_VERBS` (`:70-74`) and so writes no journal line at all -- only `engine_session.status`/`released_at` are persisted. I initially assumed journal coverage in my m0-context why-record and had to correct course when writing the "release never echoes the child's session id" test, switching from a planned journal-read assertion to a spy on `_engine_call`'s argv. Future handoffs touching `release` specifically could save a re-derivation by naming this explicitly (or pointing at `MUTATING_VERBS`) alongside the audit-trail claim.
- **Instructions improvised around:** none beyond the above -- the three safety properties, the caller-id rule, and the exclusion pattern were all directly actionable from the handoff text plus the named map anchors.
- **What would have made this easier:** naming `checklist_engine.py:70-74` (`MUTATING_VERBS`) as a map anchor alongside `release` (`:1133-1147`) would have preempted the journal assumption above -- the two are adjacent facts about the same verb but sit ~1600 lines apart in the source.

## Return status
complete
