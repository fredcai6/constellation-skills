# Gated Plan: `<work item>`

## Problem Statement

`<bounded problem this plan will solve>`

## Intent Protected

`<user/system outcome that must remain true>`

## Scope

**Allowed regions/files:** `<paths/regions this plan may modify>`  
**Not scope:** `<deferred/outside work>`  
**Specific exclusions:** `<tempting in-scope-looking areas protected from this plan>`

## Structural Baseline

**Need:** `yes | no | unclear`  
**Status:** `<established | request Cartographer baseline | skipped because <reason>>`  
**Evidence:** `<paths, packets, inspection notes, or Cartographer result>`

## Authority / Assumptions

- `<project rule/user decision/recorded low-risk reversible assumption>`

## Test Mode

**Plan default:** `<from project Orchestrator context; if silent prefer TDD for behavior changes>`  
**Inspection-only rationale:** `<only when no meaningful test surface exists>`

## Project Mechanics Hooks

Project mechanics follow project Orchestrator context; ask if silent.

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| Before gate | `<issue comment / branch / worktree / none / ask>` | `<Conductor unless assigned>` | `<link/id/branch/approval>` |
| After gate evidence accepted | `<commit / issue comment / none / ask>` | `<Conductor unless assigned>` | `<commit SHA/link>` |
| Before closeout | `<push / PR / merge / close / none / ask>` | `<Conductor unless assigned>` | `<URL/approval>` |

## Gates

Each gate is the smallest chunk that can be assigned, reviewed, proven with evidence, and stopped independently.

### Gate 1: `<name>`

**Purpose:** `<why this gate exists>`  
**Assigned Crew role:** `<implementer | reviewer>`  
**Suggested model tier:** `<simple bounded | stronger broad/ambiguous, because <reason>>`  
**Test mode:** `<same as plan | override because <reason>>`  
**Allowed scope:** `<same as plan | narrowed files/regions>`  
**Specific exclusions:** `<same as plan | narrowed exclusions | none>`  

**Close criteria:**  
- [ ] `<observable condition that must be true>`
- [ ] `<review condition if implementation gate; skipped because <reason> if not used>`

**Required evidence:**  
- `<test command | content assertion | diff inspection | render/build output | review result | Cartographer verification | user decision>`

**Stop conditions:** `<when this gate must return to Conductor/user>`  
**Next gate:** `<gate number/name or closeout>`

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|
| `<title>` | `<reason>` | `<gate/file/node>` | `<path/cmd>` | `noted | routed | dropped because <reason>` |

## Plan-Level Stop Conditions

- unresolved human decision affects scope, authority, or evidence
- required evidence cannot be produced
- scope expands beyond allowed regions/files
- specific exclusion must be touched
- structural uncertainty affects ownership, dependency, scope, or evidence

## Final Completion Criteria

- [ ] all gates closed or remaining blockers listed
- [ ] required review complete or skipped with reason
- [ ] evidence satisfies close criteria; reviewer approval alone is insufficient
- [ ] assumptions still hold
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed, dropped because `<reason>`, or none
