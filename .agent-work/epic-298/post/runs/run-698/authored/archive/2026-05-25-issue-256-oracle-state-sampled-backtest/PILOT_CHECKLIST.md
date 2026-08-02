# Pilot Checklist: `issue-256-oracle-state-sampled-backtest`

Work file: `.agent-work/issue-256-oracle-state-sampled-backtest/PILOT_CHECKLIST.md`

Status values: `pending | in-progress | blocked | complete | skipped`

## Workflow State

**LOCAL_TODO:** `current`  
**Intent protected:** `Add oracle-state sampled backtest modes that isolate prediction-stage error without violating DB-only data access or silently falling back.`  
**Scope:** `Evo sampled runtime/backtest mode selection, CLI flag, serialization diagnostics, focused docs/tests.`  
**Not scope:** `New training, artifact regeneration, gold promotion, sampled-predict behavior, ingestion changes.`  
**Specific exclusions:** `No FastF1 access from evo code; no compatibility aliases beyond the four issue modes; no changes to dead paths.`

## Ambiguity / Authority

**Resolved ambiguities:** `GitHub issue 256 defines four modes. Code/docs establish DB Q classification as current grid/quali state and race_start_order as target-lap state.`  
**Remaining ambiguities:** `none blocking`  
**Assumptions:** `Missing oracle state skips the event with explicit diagnostics rather than substituting sampled state.`

## Checklist

| Step | Status | Evidence / note |
|---|---|---|
| 0. Load project context | complete | `AGENTS instructions, README.md, TESTING.md, docs/architecture/index.md, docs/DOCUMENTATION.md, Orchestrator/Crew context loaded` |
| 1. Interrogate request | complete | `grill-me invoked by reading skill; code/docs answered blocking questions; no user question needed` |
| 2. Bound problem | complete | `scope/not-scope/specific exclusions above` |
| 3. Decide whether Constellation adds value | complete | `non-trivial evo behavior with TDD, review, evidence, and stage-isolation semantics; use one gated Crew cycle` |
| 4. Establish structural baseline | complete | `architecture index identifies struct:evo.sampled_runtime and DB-only constraint; no Cartographer baseline needed` |
| 5. Build gated plan | complete | `.agent-work/issue-256-oracle-state-sampled-backtest/GATED_PLAN.md` |
| 6. Dispatch Crew | complete | `implementer Crew Raman; reviewer Crew Bohr` |
| 7. Integrate evidence | complete | `evidence/gate-1-implementer-integration.md; evidence/gate-1-reviewer-integration.md` |
| 8. Check architecture reconciliation | complete | `no structural map action; change remains inside struct:evo.sampled_runtime` |
| 9. Collect Triage candidates | complete | `none` |
| 10. Semantic closeout | complete | `Gate 1 closed; tests green; docs updated` |

## Project Mechanics Status

| Hook | Status | Evidence / link |
|---|---|---|
| branch | complete | `codex/issue-256-oracle-state-sampled-backtest` |
| issue 256 | skipped | `no issue comment requested; push/PR/close require approval` |

## Triage Candidates For Closeout

None.

## Semantic Closeout

- [x] all gates complete, cancelled, or redirected with reason
- [x] required evidence recorded
- [x] reviewer evidence integrated; reviewer approval alone is insufficient
- [x] assumptions still hold or were resolved
- [x] architecture reconciliation checked
- [x] Triage candidates routed, dropped because `reason`, or none
- [x] project-required repo actions approved and evidenced
- [x] Workbench artifact closeout `complete`
