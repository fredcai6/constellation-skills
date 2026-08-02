# Local Work Todo: Lane A — Tire-wear / Compound-Prior Production Hardening

## Task summary

Make the tire-wear compound-prior solver pristine enough to be trusted as an evo regularizer.
Three sub-items: (A1) reconcile and close/rewrite GitHub issues #49/#50 against current implementation; (A2) create/formalize a real-race validation harness; (A3) make the production artifact bridge from full run bundle → compact runtime prior explicit and time-safe.

## Source context

**Work ID:** `20260525-lane-a-tire-hardening`
**Role:** conductor
**Route/gate:** initial setup — interrogation in progress
**Handoff/framing source:** user Lane A brief (2026-05-25 session)
**Authority:** user decision

## Definition of done

- [ ] A1: #49 and #50 either closed with evidence or rewritten into specific gap issues
- [ ] A2: validation harness script exists, runs deterministically, saves report, asserts no leakage
- [ ] A3: production bridge script/code makes run-bundle → compact artifact path explicit; time-safe selection verified; tests pass
- [ ] All gates reviewed and evidenced
- [ ] Triage candidates packaged for future work

## Todo

- [ ] Step 0: Load project context (architecture index, compound_prior module, existing tests)
- [ ] Step 1: Interrogate request via grill-me
- [ ] Step 2: Bound problem
- [ ] Step 3: Decide Constellation value
- [ ] Step 4: Establish structural baseline
- [ ] Step 5: Build gated plan
- [ ] Step 6: Dispatch Crew gates
- [ ] Step 7: Integrate evidence
- [ ] Step 8: Architecture reconciliation
- [ ] Step 9: Collect Triage candidates
- [ ] Step 10: Semantic closeout

## Work log

### Step 0: Workbench initialization

**Status:** completed
**What happened:** Created LOCAL_TODO and CONDUCTOR_CHECKLIST; confirmed .agent-work/ exists.
**Evidence:** files written
**Follow-up:** proceed to grill-me interrogation

## Current state

**Last completed step:** Workbench initialization
**Current blocker:** none
**Next recommended action:** invoke grill-me for Step 1 interrogation
**Files/artifacts touched:** `.agent-work/20260525-lane-a-tire-hardening/LOCAL_TODO.md`, `CONDUCTOR_CHECKLIST.md`
**Open assumptions:** none yet
