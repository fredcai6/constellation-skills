# Local Work Todo: `Role-specific todos`

## Task summary

Investigate and shape the Workbench local todo behavior so role-specific checklist templates can act as the execution controller while Local Todo remains recoverable state.

## Source context

**Work ID:** `20260525-role-todos`  
**Role:** `implementer`  
**Route/gate:** `documentation/template interface update`  
**Handoff/framing source:** `user request`  
**Authority:** `user decision`

## Definition of done

- [x] Existing local todo and role checklist contracts are understood.
- [x] Tests describe the desired merged behavior before implementation.
- [x] Workbench docs/templates make controller selection, checklist marks, and execution notes explicit.
- [x] Relevant tests pass.

## Todo

- [x] Inspect Workbench, role checklists, operating principles, and current content tests.
- [x] Add content tests for role-specific Workbench todo behavior.
- [x] Update Workbench template/docs and supporting documentation.
- [x] Run tests and revise.

## Work log

### Step 1: Inspect current contracts

**Status:** `completed`  
**What happened:** Workbench owns artifact hygiene and generic Local Todo; Pilot and Cartographer already use role-specific checklist templates as controllers.  
**Evidence:** `skills/workbench/SKILL.md`, `skills/workbench/templates/LOCAL_TODO.template.md`, `skills/pilot/templates/PILOT_CHECKLIST.template.md`, `skills/cartographer/templates/CARTOGRAPHER_CHECKLIST.template.md`  
**Follow-up:** Add tests for the desired interface.

### Step 2: Pin desired behavior in tests

**Status:** `completed`  
**What happened:** Added a content test requiring Workbench and Local Todo to describe role-specific checklist controllers, checkbox discipline, and execution notes.  
**Evidence:** `tests/test_constellation_content.py::test_workbench_merges_local_todo_with_role_checklists`  
**Follow-up:** Update Workbench docs/templates until the test passes.

### Step 3: Update Workbench contract

**Status:** `completed`  
**What happened:** Workbench now says to copy a role-specific checklist when present, treat it as the execution controller, keep checked milestones and execution notes current, and avoid duplicating role checklists in Local Todo.  
**Evidence:** `skills/workbench/SKILL.md`, `skills/workbench/templates/LOCAL_TODO.template.md`, `docs/CONSTELLATION_OVERVIEW.md`, `README.md`  
**Follow-up:** Run content tests.

### Step 4: Verify

**Status:** `completed`  
**What happened:** Targeted tests and full discovery suite passed. `python -m unittest` alone ran zero tests, so discovery is the usable command here.  
**Evidence:** `python -m unittest discover -s tests` passed 68 tests.  
**Follow-up:** Final diff/status pass.

### Step 5: Clarify checklist ownership

**Status:** `completed`  
**Status transitions:** `pending -> completed`  
**What happened:** Confirmed Charter, Pilot, and Cartographer directly reference their own checklists. Adjusted the overview so Workbench is file hygiene/recovery state, while role skills own checklist semantics.  
**Evidence:** `docs/CONSTELLATION_OVERVIEW.md`, `tests/test_constellation_content.py::test_role_checklists_are_direct_role_interfaces_not_workbench_owned`  
**Follow-up:** Re-run targeted and full tests.

### Step 6: Re-verify

**Status:** `completed`  
**Status transitions:** `pending -> completed`  
**What happened:** Ownership clarification tests and full test discovery passed.  
**Evidence:** `python -B -m unittest tests.test_constellation_content.ConstellationContentTests.test_workbench_merges_local_todo_with_role_checklists tests.test_constellation_content.ConstellationContentTests.test_role_checklists_are_direct_role_interfaces_not_workbench_owned`; `python -B -m unittest discover -s tests` passed 69 tests.  
**Follow-up:** none

## Current state

**Last completed step:** `Re-verify`  
**Current blocker:** `none`  
**Next recommended action:** `none`  
**Files/artifacts touched:** `.agent-work/20260525-role-todos/LOCAL_TODO.md`, `tests/test_constellation_content.py`, `skills/workbench/SKILL.md`, `skills/workbench/templates/LOCAL_TODO.template.md`, `docs/CONSTELLATION_OVERVIEW.md`, `README.md`  
**Open assumptions:** `The repo wants this behavior encoded as template/doc contract, not new runtime code.`
