# Orchestrator Context — project deltas

## Project Purpose

Continuously improve the active Constellation Skills corpus for clarity and proven effectiveness in real projects.

## Operating Context

**Primary users:** humans and agents using the installed skill corpus in active projects.  
**Output authority:** mixed — skills and their enforced workflow mechanisms are durable operational tooling; feedback is advisory.  
**Failure consequences:** unclear or ineffective guidance, broken workflow mechanics, or lost learning from real work.

## Subsystem Rigor

| Subsystem | Rigor profile | Execution context | Orchestrator implication |
|---|---|---|---|
| Workflow mechanisms and verifiers | strengthened durable system | runtime/test infrastructure | Plan targeted automated verification plus the relevant broader suite. |
| Post-job feedback | pragmatic internal learning loop | reporting | Keep collection light and non-blocking; use real-project feedback, never invented projects, as the effectiveness signal. |

## Repo Action Authority

- Local commits: allowed.
- Pushes, pull requests, and merges to `main`: require explicit human approval, unless the human has pre-approved the action for the specified work.

## Evidence And Verification Map

| Area | Required evidence | Handoff implication |
|---|---|---|
| Mechanism or workflow behavior change | targeted automated tests plus relevant broader suite | name both commands; a genuine no-test-surface exception needs rationale |
| Skill effectiveness | feedback collected from agents after real project work | do not fabricate representative projects or turn feedback into a completion gate |

## Project Engineering Rules

- Solicit lightweight, freeform post-job feedback (“how did it go?”); prompt for positives and negatives where useful.
- Feedback is advisory and may be brief or absent. Record it when available; do not require immediate interpretation or a per-item disposition.
