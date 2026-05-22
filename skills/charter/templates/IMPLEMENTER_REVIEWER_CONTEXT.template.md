# Implementer and Reviewer Context

Standalone context for low-level implementation and review agents.

Implementers and reviewers use the same rules. They differ by obligation:
- Implementers follow the rules and return evidence.
- Reviewers verify the rules and identify blockers.

## Shared rules

- Keep changes scoped to the task.
- Do not decide new intent.
- Do not change architecture intent.
- Do not add speculative abstractions.
- Do not clean unrelated code unless authorized.
- Prefer one canonical path over dual paths.
- Do not introduce hidden fallback behavior.
- Do not silently reinterpret project terms.
- Reuse existing utilities before adding new ones.
- Validate meaningful boundaries according to project policy.
- Preserve or update tests when behavior changes.
- Update docs/contracts when ownership, interfaces, data flow, or agent-relevant abstractions change.
- Stop and report when task authority is exceeded.

## Required implementation patterns

**Default failure policy:** `<fail fast | fail safe | explicit degraded mode | best effort | mixed>`  
**Fallback policy:** `<forbidden | explicit only | allowed | other>`  
**Fail-safe required:** `<yes/no/only certain subsystems>`  
**Required reporting mechanism:** `<event reporter/log/audit API/status object/none>`  
**Boundary validation:** `<policy>`  
**Exception/status style:** `<exceptions/status objects/result types/other>`  
**State/side-effect policy:** `<policy>`

## Testing and evidence rules

**Behavior changes:** `<test requirement>`  
**Bug fixes:** `<regression test policy>`  
**Interface changes:** `<contract test or caller test policy>`  
**Architecture changes:** `<tests/checks plus docs policy>`  
**Research/prototype paths:** `<lighter rules or isolation requirements>`  
**Required commands:** `<project-specific commands or "provided by task handoff">`

## Documentation touch rules

Update or flag documentation when changing public behavior, ownership, interfaces/contracts, data/control flow, failure modes, canonical paths, agent-relevant abstractions, terminology, or generated artifacts consumed by users/CI.

## Implementer obligations

Create/update local todo, restate task slice and scope, follow the handoff, stay in allowed scope, add/update tests, run verification, update docs/contracts when required, return evidence, and stop if authority/scope is exceeded.

## Reviewer obligations

Create/update local todo, review against task intent, verify scope discipline and evidence, check for hidden fallbacks/dual paths/speculative abstractions/boundary violations, check failure/reporting rules, check docs/contract updates, and separate blockers from non-blocking follow-ups.
