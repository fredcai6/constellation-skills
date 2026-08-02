# Plan Consistency Check: 20260526-compound-c-number-backfill

## Inputs

| Input | Path / Source | Status | Notes |
|---|---|---|---|
| User request | conversation args | present | "data collection first; DB backfill primary; FastF1 for holes" |
| Problem interrogation result | `INTERROGATOR_QUESTIONS.md` | present | Q4 resolved via design; all decisions captured |
| Pilot checklist | `PILOT_CHECKLIST.md` | present | |
| Gated plan | `GATED_PLAN.md` | present | |
| Structural baseline | collector.py, compound_adapter.py, compounds.yaml, DB schema reviewed | present | no Cartographer needed — scope is isolated to data layer |
| Orchestrator context | not checked (project-level only) | not applicable | |
| Crew context | not checked | not applicable | |

## Consistency Checks

### Intent and Scope

- [x] Intent Protected is present and consistent: compound_c_number populated → priors work
- [x] Scope/Not Scope/Exclusions agree: sprint collection first, backfill second, prior pipeline out of scope
- [x] No deferred work pulled into gates
- [x] Rejected alternative recorded: FastF1 full re-collection rejected in favour of DB backfill (faster, no API calls)

### Authority and Assumptions

- [x] All actions are non-destructive (UPDATE WHERE NULL — idempotent) or additive (new session rows)
- [x] Sprint collection follows existing collector path — no new patterns
- [x] No PR/merge/push authority needed until user confirms; Crew does not merge

### Gate Quality

- [x] Gate 1 (sprint collection) independently stoppable — if FastF1 unavailable, Gate 2 can still proceed
- [x] Gate 2 (code fix + backfill) independently stoppable — idempotent UPDATE, dry-run flag
- [x] Both gates have close criteria and required evidence
- [x] Gate 2 has reviewer handoff planned
- [x] No hidden intent inference required

### Architecture / Structural Baseline

- [x] No structural changes — data layer only
- [x] `_compound_string_to_c_number` signature change (adds optional `year` param) is backward compatible
- [x] Backfill script reads from existing data; no schema migration
- [x] Triage candidates don't block gates

### Verification / Evidence

- [x] Gate 1 evidence: SQL count queries per sprint session
- [x] Gate 2 evidence: before/after NULL counts + spot-check compounds for specific races
- [x] Reviewer approval insufficient alone — requires verified NULL-count evidence
- [x] Evidence integration path clear

## Findings

| ID | Finding | Severity | Required action | Status |
|---|---|---|---|---|
| PC-001 | Gate 2 backfill script needs to JOIN lap_times → sessions to get (year, gp_name) per row | note | already in plan | resolved |
| PC-002 | `_compound_string_to_c_number` year param must default to None (backward compat) | note | already in plan | resolved |
| PC-003 | 2022 residual NULLs (10.9%) — wet compounds, correctly NULL; backfill should not force-fill these | note | plan specifies "compound NOT IN (wet/intermediate/unknown)" condition | resolved |

## Verdict

`ready for Crew`

## Required Edits Before Dispatch

none

## Pilot Decision

`dispatch Crew`

**Reason:** Intent clear, scope bounded, both gates independently stoppable with inspectable evidence.
No structural risk. Triage candidates captured for post-closeout routing.
