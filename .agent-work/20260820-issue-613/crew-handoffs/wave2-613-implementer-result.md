# Implementation Result

## Assigned gate
`m3 — Record and commit result`

## Completed slice

Removed the redundant parent heartbeat writer when the actual CLI child environment carries the dispatcher's exact ambient `SPINE_FILE` and `SPINE_SESSION` pair. The parent heartbeat still runs for a different child pair or a child environment without that pair.

## Scope

**Files changed:**

- `scripts/run_crew.py`
- `tests/test_crew_launcher.py`
- `.agent-work/20260820-issue-613/implementer-plan.json`
- `.agent-work/20260820-issue-613/plan-amend.json`
- `.agent-work/20260820-issue-613/crew-handoffs/wave2-613-implementer-result.md`

**Specific exclusions touched:** no

## Behavior changed

Yes. `CliBackend.dispatch` and `resume` pass their actual child environment to `_parent_lease_heartbeat`. Exact ambient/child pair equality yields no parent heartbeat thread; different and missing child pairs preserve the existing parent heartbeat, retry/swallow behavior, and join-before-return ordering.

## Map Impact

No inbound Map Anchors were supplied. This is a local liveness constraint change in `scripts/run_crew.py`: the parent and child no longer concurrently write one shared spine/session. No map artifacts were changed.

## Test mode

**Required:** test-first
**Satisfied:** yes

## Evidence

```bash
python -m pytest -q tests/test_crew_launcher.py -k ParentLeaseHeartbeatTests
```

**Result:** red before the implementation: `2 failed, 6 passed, 236 deselected` (the new shared-pair dispatch and resume tests found a live parent heartbeat thread). Green after: `9 passed, 236 deselected`.

```bash
python -m pytest -q tests/test_crew_launcher.py
```

**Result:** `245 passed in 1.95s`.

```bash
python -m pytest -q tests/test_checklist_engine_atomic_save.py
```

**Result:** `15 passed in 1.75s`.

```bash
git diff --check
rg -n "_parent_lease_heartbeat" scripts/run_crew.py tests/test_crew_launcher.py
```

**Result:** both exit 0. The seam search shows the helper definition and only its dispatch/resume call sites, plus tests.

## TDD evidence

- Failing test observed: focused suite against the restored pre-fix helper failed only in shared-pair dispatch and resume because the parent thread was alive.
- Passing test observed: focused suite passed all nine heartbeat tests after the helper compared the actual child environment.
- Refactor while green: yes — the parent-heartbeat test description was made current and the missing-child-pair control was added, then all required checks passed.

## Docs/contracts touched

- `scripts/run_crew.py` helper contract docstring and `ParentLeaseHeartbeatTests` description now state the shared-pair ownership rule.

## Assumptions

- Exact string equality is the required identity comparison; path normalization is not part of the handoff.

## Stop conditions hit

- none

## Out-of-scope observations

- The known full-suite `map/INDEX.md` freshness failure was not run or changed, per handoff.

## Workflow Feedback

- **Handoff gaps:** Map Anchors were absent despite the Implementer skill requiring a map entry point; source/test inspection was used for this explicitly local seam.
- **Context rediscovered:** the child environment is constructed before both call sites, so passing it to the existing helper is sufficient for dispatch and resume.
- **Instructions improvised around:** the MCP spine door was bound to a missing parent file rather than this dispatched plan; per the workbench rule, the bundled CLI engine drove the owned plan. The plan template lacked distinct required verification and durable-result gates, so they were appended through the engine under the frozen launch authority.
- **What would have made this easier:** include the Map Anchors field, even if it explicitly says no applicable map artifact.

## Return status
`complete`
