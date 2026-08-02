# Pilot Checklist: 20260526-compound-c-number-backfill

Work file: `.agent-work/20260526-compound-c-number-backfill/PILOT_CHECKLIST.md`

## Workflow State

**LOCAL_TODO:** current  
**Intent protected:** 2018–2021 `lap_times` rows have correct `compound_c_number`; compound prior pipeline
can generate priors for all 4 early years.  
**Scope:** (1) collect 3 missing 2021 sprint sessions; (2) fix `_compound_string_to_c_number` for 2018
era; (3) backfill `compound_c_number` in 2018–2022 DBs  
**Not scope:** running compound prior pipeline; full FastF1 re-collection; Spain/Spanish naming fix  
**Specific exclusions:** 2020 Emilia Romagna FP2/FP3 (confirmed never happened, not a collection gap)

## Ambiguity / Authority

**Resolved ambiguities:**
- compound column is fully populated (0% NULL) in 2018–2020, 1% in 2021 → DB backfill is primary fix
- Only 3 genuine missing sessions found: 2021 sprint races (GB, Italy, Brazil)
- 2020 Emilia Romagna FP2/FP3: confirmed non-events (COVID compressed format)
- Russia 2021 FP3: already in KNOWN_UNAVAILABLE_SESSIONS (officially cancelled)
- 2018-era compound names are absolute (SUPERSOFT/ULTRASOFT/HYPERSOFT), not relative like 2019+

**Remaining ambiguities:** none blocking

**Assumptions:**
- FastF1 carries 2021 sprint session data (reasonable — 2021 is recent)
- compounds.yaml 2018–2021 entries are correct (they were already audited)

## Checklist

| Step | Status | Evidence / note |
|---|---|---|
| 0. Load project context | complete | Charter + architecture docs reviewed; CLAUDE.md loaded |
| 1. Interrogate request | complete | `INTERROGATOR_QUESTIONS.md`; resolved DB backfill primary; 3 sprint sessions missing; 2018-era compound naming issue identified |
| 2. Bound problem | complete | Scope above |
| 3. Decide whether Constellation adds value | complete | 2 implementation gates + review; Crew dispatch adds value |
| 4. Establish structural baseline | complete | Existing collector.py, compound_adapter.py, compounds.yaml reviewed; DB schema confirmed |
| 5. Build gated plan | complete | `GATED_PLAN.md` |
| 5a. Plan consistency check | complete | `PLAN_CONSISTENCY_CHECK.md` — verdict: ready for Crew |
| 6. Dispatch Crew | complete | Gate 1 implementer + Gate 2 implementer + reviewer all dispatched and closed |
| 7. Integrate evidence | complete | `evidence/gate-1-implementer-integration.md`, `evidence/gate-2-implementer-integration.md`, `evidence/gate-2-reviewer-integration.md` |
| 8. Check architecture reconciliation | complete | data-layer only; no structural changes; `_compound_string_to_c_number` signature backward-compatible |
| 9. Collect Triage candidates | complete | 2 candidates captured in checklist below; spawned as background tasks |
| 10. Semantic closeout | complete | see Semantic Closeout section |

## Project Mechanics Status

| Hook | Status | Evidence / link |
|---|---|---|
| Gate 1 — sprint collection | pending | |
| Gate 2 — code fix + backfill script | pending | |
| Gate 2 review | pending | |
| PR to main | pending | user to authorize |

## Triage Candidates For Closeout

### Triage candidate: 2020 Emilia Romagna FP2/FP3 in KNOWN_UNAVAILABLE_SESSIONS

**Reason:** missing implementation  
**Current work anchor:** gate 1 audit  
**Structural anchor:** `src/utils/constants.py:119`  
**Current truth:** `KNOWN_UNAVAILABLE_SESSIONS` has Russia 2021 FP3 but not 2020 Emilia Romagna FP2/FP3;
`get_weekend_sessions(2020, 'Emilia Romagna')` returns FP2/FP3 that never happened  
**Future concern:** `find_missing_sessions` and `is_session_complete` report false gaps for 2020 Imola  
**Evidence:** DB has only FP1/Q/R for 2020 Emilia Romagna (confirmed); Imola 2020 was a 1-day compressed format  
**Recommended Triage action:** Add (2020, 'Emilia Romagna', 'FP2') and (2020, 'Emilia Romagna', 'FP3')
to `KNOWN_UNAVAILABLE_SESSIONS` with reason "Compressed COVID format — practice reduced to FP1 only"

### Triage candidate: Spain vs. Spanish naming inconsistency (2018/2019)

**Reason:** unresolved decision — data stored as "Spain", calendar key is "Spanish"  
**Current work anchor:** gate 1 audit  
**Structural anchor:** `src/utils/constants.py` (F1_CALENDARS) + `data/f1_data_2018.db`, `data/f1_data_2019.db`  
**Current truth:** `F1_CALENDARS[2018]` and `[2019]` list "Spanish"; DBs have sessions under "Spain"  
**Future concern:** `find_missing_sessions` shows these as both missing AND extra; any lookup by gp_name
that uses the calendar as source of truth will fail to find them  
**Evidence:** audit output — MISSING: Spanish FP1, EXTRA: Spain FP1 for 2018 and 2019  
**Recommended Triage action:** Normalize calendar entry OR migrate DB rows to "Spanish" — needs decision
on canonical name

---

## Semantic Closeout

- [x] all gates complete, cancelled, or redirected with reason
- [x] plan consistency check completed
- [x] required evidence recorded
- [x] reviewer evidence integrated; reviewer approved Gate 2
- [x] assumptions still hold (FastF1 had 2021 sprint data; compounds.yaml was correct)
- [x] architecture reconciliation checked — data layer only, no structural changes
- [x] Triage candidates routed (spawned as background tasks via mcp__ccd_session__spawn_task)
- [x] no template update candidates
- [x] no repo actions required (no commits/PRs — user to decide)
- [x] Workbench artifact closeout: package moved to archive after this entry
