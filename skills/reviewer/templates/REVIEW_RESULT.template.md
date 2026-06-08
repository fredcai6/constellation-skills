# Review Result

Status values follow `skills/workbench/references/status-model.md`.

Omit optional sections when empty.

## Assigned Gate
`<gate id/title>`

## Result
`APPROVE | BLOCK | COMMENT`

## Handoff compliance
`<assigned intent, scope, required evidence, stop conditions satisfied?>`

## Scope drift
`<Did implementation change only allowed scope? Any specific exclusions touched?>`

## Evidence verdict
`<Do supplied evidence and test mode satisfy required evidence? If TDD required, did evidence show red-green-refactor and behavior-focused tests?>`

## Code/doc quality
`<code quality and doc quality: minimal, maintainable, tested, and project-rule compliant?>`

## Map impact verdict
Check the implementer's `Map Impact` notes against the diff and evidence so durable context reaches Cartographer reconcile intact. Skip for trivial local edits with no structural/capability/constraint/decision impact.

- **Evidence supports claimed change:** `<does the produced evidence actually back the claimed behavior/capability change?>`
- **Constraints not violated:** `<were inbound constraints/assumptions honored, not silently broken?>`
- **Notes match the diff:** `<do the map-impact notes match what the diff actually touched — no missing or overstated structural/capability/event impact?>`
- **Decision candidates surfaced:** `<were decision candidates surfaced when the change required authority the implementer lacked?>`
- **Durable context routed:** `<is durable context / triage candidates routed to Cartographer or Triage rather than dropped?>`

BLOCK when graph-impact claims are materially wrong or missing for architecture-significant work (structural, capability, constraint, or decision impact). Do not block trivial local edits for absent notes.

## Reconciliation check
`<docs/contracts/structural baseline concerns?>`

## Blockers
- `<blocker or none>`

## Out-of-scope observations
- `<finding for Commander or none>`

## Return status
`complete | partial | blocked | out-of-scope | failed`
