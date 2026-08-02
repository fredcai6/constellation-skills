# Local Work Todo: `Issue #253 — Training curriculum: evidence windows and holdout modes`

## Task summary

Plan and execute the remaining implementation work for issue #253 so that a coherent big training run can be launched. This covers: Q leakage fix during training (#270), age/time-gap calendar features for recent-history modules (#209), recent-history holdout modes (same_season_recent, short_gap_holdout, race_holdout, season_boundary_holdout), and ensuring fusion calibration by mode (#211) is sequenced correctly after stable artifacts exist.

## Source context

**Work ID:** `issue-253-curriculum-holdout`  
**Role:** `pilot`  
**Route/gate:** `pilot checklist`  
**Handoff/framing source:** `GitHub issue #253 + prior conversation analysis`  
**Authority:** `user decision`

## Definition of done

- [ ] Q leakage fix during training (#270) implemented and tested
- [ ] Age/time-gap features added to recent-history modules (#209)
- [ ] Recent-history holdout modes implemented (4 scenarios)
- [ ] Training run is ready to launch with coherent configuration
- [ ] All gates reviewed and closed

## Todo

- [ ] Step 0: Context loaded
- [ ] Step 1: Interrogate request (grill-me)
- [ ] Step 2: Bound problem
- [ ] Step 3: Decide Constellation value
- [ ] Step 4: Structural baseline
- [ ] Step 5: Gated plan
- [ ] Step 6: Dispatch Crew gates
- [ ] Steps 7-10: Evidence, reconciliation, closeout

## Work log

### Step 0: Load project context

**Status:** completed  
**What happened:** Prior conversation mapped done/not-done state for #253. Evidence windows fully implemented. Holdout modes, time-gap features, and Q leakage training fix are not implemented.  
**Evidence:** `src/evo_predictor/module_training_orchestration.py` (evidence_mode_eval done), no days_since/season_boundary features found anywhere  
**Follow-up:** Proceed to grill-me interrogation

## Current state

**Last completed step:** Step 0 — project context loaded  
**Current blocker:** none  
**Next recommended action:** Invoke grill-me to interrogate intent and success criteria  
**Files/artifacts touched:** none (read-only survey)  
**Open assumptions:** none
