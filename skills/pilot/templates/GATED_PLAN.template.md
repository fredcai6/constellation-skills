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
| Before gate | `<issue comment / branch / worktree / none / ask>` | `<Pilot unless assigned>` | `<link/id/branch/approval>` |
| After gate evidence accepted | `<commit / issue comment / none / ask>` | `<Pilot unless assigned>` | `<commit SHA/link>` |
| Before closeout | `<archive workflow artifacts / none / ask>` | `<Pilot unless assigned>` | `<archive path/approval>` |
| After archive | `<commit archived workflow artifacts / push / PR / merge / close / none / ask>` | `<Pilot unless assigned>` | `<commit SHA/URL/approval>` |

## Gates

Each gate is the smallest chunk that can be assigned, reviewed, proven with evidence, and stopped independently.

### Gate 1: `<name>`

**Purpose:** `<why this gate exists>`  
**Crew cycle:** `implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close`  
**Implementer handoff:** `<required | not applicable because <reason>>`  
**Reviewer handoff:** `<required | skipped because <reason>>`  
**Suggested model tier:** `<simple bounded | stronger broad/ambiguous, because <reason>>`  
**Test mode:** `<same as plan | override because <reason>>`  
**Allowed scope:** `<same as plan | narrowed files/regions>`  
**Specific exclusions:** `<same as plan | narrowed exclusions | none>`  

**Close criteria:**  
- [ ] `<observable condition that must be true>`
- [ ] `<implementation evidence integrated>`
- [ ] `<review evidence integrated, or skipped because <reason>>`

**Required evidence:**  
- `<test command | content assertion | diff inspection | render/build output | review result | Cartographer verification | user decision>`

**Stop conditions:** `<when this gate must return to Pilot/user>`  
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
- [ ] each implementation gate completed its Crew cycle; do not batch review at final closeout
- [ ] evidence satisfies close criteria; reviewer approval alone is insufficient
- [ ] assumptions still hold
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed, dropped because `<reason>`, or none
