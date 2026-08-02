# Pilot Checklist: `issue-253-curriculum-holdout`

Work file: `.agent-work/issue-253-curriculum-holdout/PILOT_CHECKLIST.md`

## Workflow State

**LOCAL_TODO:** current  
**Intent protected:** Complete remaining #253 prerequisites so a coherent big training run can be launched  
**Scope:** #275 artifact naming, #277 compound prior data run, #253 holdout diagnostic modes (4 modes), #209 time-gap features as model inputs (minimal set), gold training run 2018–2024/2025  
**Not scope:** #270 Q leakage fix (deferred), #211 calibration by mode (after stable artifacts), #265 Gaussian mixture, #255 learned gates, 2026 eval year  
**Specific exclusions:** gold_defaults.toml train/eval config; JSON payload schemas; exotic #209 features (pair continuity, substitute flags)

## Ambiguity / Authority

**Resolved ambiguities:** Evidence windows confirmed implemented; holdout modes confirmed missing; time-gap features confirmed missing  
**Remaining ambiguities:** Priority order between #270 and #209; whether holdout modes require new TOML config or can be inline  
**Assumptions:** none yet

## Checklist

| Step | Status | Evidence / note |
|---|---|---|
| 0. Load project context | complete | Prior conversation + codebase survey |
| 1. Interrogate request | complete | grill-me resolved 6 questions: run is 2018–2024/2025 gold backtest; #270 deferred; holdout modes eval-only; #209 features as model inputs; #275 in before run; #277 data-run pre-step; user confirmed all-in |
| 2. Bound problem | complete | see Scope/Not-scope below |
| 3. Decide whether Constellation adds value | complete | 6 gates, Crew handoffs needed for each; Constellation justified |
| 4. Establish structural baseline | complete | skipped — prior read-only survey sufficient; event_date confirmed in DB; feature_dim data-driven |
| 5. Build gated plan | complete | `.agent-work/issue-253-curriculum-holdout/GATED_PLAN.md` |
| 6. Dispatch Crew | in-progress | ready to dispatch Gate 1 |
| 7. Integrate evidence | pending | |
| 8. Check architecture reconciliation | pending | |
| 9. Collect Triage candidates | pending | |
| 10. Semantic closeout | pending | |

## Project Mechanics Status

| Hook | Status | Evidence / link |
|---|---|---|
| Issues created/linked | pending | |
| PRs | pending | |

## Triage Candidates For Closeout

_None identified yet._

## Semantic Closeout

- [ ] all gates complete, cancelled, or redirected with reason
- [ ] required evidence recorded
- [ ] reviewer evidence integrated
- [ ] assumptions still hold or were resolved
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed or none
- [ ] project-required repo actions approved and evidenced
- [ ] Workbench artifact closeout complete
