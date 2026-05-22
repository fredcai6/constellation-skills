# Ground Rule Decisions

This file records decisions used to generate project agent context. It is an audit trail, not required runtime context for agents.

## Project calibration

**Project name:** `<project name>`  
**Date generated:** `<YYYY-MM-DD>`  
**Existing artifacts assumed true:** `<list or none>`  
**Project type/posture:** `<prototype | research | internal tool | production | safety/security/privacy-sensitive | mixed>`  
**Repo/tooling baseline:** `<Git/Markdown/issue tracker/test runner/docs explorer/etc.>`  
**Primary users:** `<who uses this>`  
**Maintainers/reviewers:** `<who maintains or audits this>`  
**Primary outputs:** `<reports | automation | library | model | decisions | control actions | other>`  
**Output authority:** `<suggestion | diagnostic | canonical record | automated action | user-facing claim | other>`  
**Failure cost summary:** `<what happens if wrong/stale/unavailable/misleading>`

## Decision index

| Area | Decision | Selected policy | Strength |
|---|---|---|---|
| `<area>` | `<decision>` | `<policy>` | `<strength>` |

## Decision: `<short name>`

**Decision area:** `<scope / architecture / testing / etc.>`  
**Scenario:** `<concrete conflict used to elicit the decision>`  
**Selected policy:** `<what the user chose>`  
**Strength:** `strong | default | case-by-case | don't-care-selected-default | unresolved`  
**Applies to:** `<where this policy applies>`  
**Exceptions:** `<explicit exceptions, or "None stated">`  
**Default source:** `user preference | conservative default | project risk posture | existing artifact`  
**High-level implication:** `<what high-level agents should do>`  
**Low-level implication:** `<what low-level agents should do>`  
**Open questions:** `<remaining ambiguity, or "None">`

## Contradictions and resolutions

### Tension: `<short name>`

**Observed tension:** `<describe conflict>`  
**Resolution:** `<resolved policy or "unresolved">`  
**Default until revisited:** `<default>`  
**Affected agents:** `<conductor | cartographer | crew | triage | all>`

## Defaults selected because the user did not care

| Decision | Selected default | Why this default |
|---|---|---|
| `<decision>` | `<default>` | `<reason>` |
