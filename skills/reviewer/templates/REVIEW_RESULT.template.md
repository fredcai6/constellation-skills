# Review Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `references/status-model.md`.

Omit optional sections when empty.

A finished review uses Return status `complete`, including a finished BLOCK or COMMENT; `blocked` means the review could not be finished. Use APPROVE when required criteria are met; optional nonblocking suggestions may accompany it. Judge semantic equivalence, not literal repetition of source wording.

> **Concise-authoring guidance:** Reference the implementation result and the task, plan, and source evidence you actually relied on by path rather than restating their content; you need not enumerate or reread every original document, and Provenance is cited only if you opened it. For routine passing checks, one line per check with check name, outcome, and evidence pointer is sufficient. Exception-focused: blockers and COMMENT findings retain trigger, evidence, impact, and repair criteria. Re-reviews reference prior findings by stable ID and original artifact path; carry the current index forward without repeating earlier narratives. Mandatory Workflow Feedback must name specific gaps or confirm none after explicitly checking — a bare `none` is rejected.
> **No simplification of checks:** do not waive evidence, required fields, or authority verification. Required headings, status values, and Result verdict (APPROVE/BLOCK/COMMENT) are contractual and must not be omitted.

## Assigned Gate
`<gate id/title>`

## Result
`APPROVE | BLOCK | COMMENT`

## Handoff compliance
`<assigned intent, scope, required evidence, stop conditions satisfied?>`

Reference coverage of the handed-off objective and each required criterion: recorded assessment/check, evidence location and disposition, or an explicit not-checked reason. Reuse existing check IDs and survey/result artifacts rather than duplicating the survey. This lets the Commander verify review coverage and traceability while technical validity remains your responsibility.

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

## Finding index
When findings exist in this or earlier rounds, this result is the current index for the gate. Keep the same IDs; link to each finding's original report/heading and the latest repair response, then record your independent check and disposition. Keep earlier results unchanged. Omit this section when the gate has no finding history.

| ID | Kind (blocker / observation) | State (open / resolved) | Original finding | Repair / evidence | Reviewer check / reason |
| --- | --- | --- | --- | --- | --- |
| `<F1>` | `<kind>` | `<state>` | `<path#finding-id>` | `<response and evidence paths, or pending>` | `<independent outcome, limits or nonblocking reason>` |

## Blockers
For each new blocker, use its stable ID as the heading and state the failure trigger, evidence location, impact on the intended outcome, and behavior/evidence required for resolution. On later rounds link to the original rather than repeating it. An unresolved or disputed blocker stays open until independently assessed.

- `<ID + finding, or none>`

## Out-of-scope observations
Use the same stable IDs and finding fields for observations; explain why each does not block this scope and route it for triage when appropriate.

- `<ID + finding for Commander or none>`

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** `<what concrete wording in the handoff confused you, or which field was missing/wrong — name the field>`
- **Context rediscovered:** `<context you had to dig up that the anchors, evidence, or handoff should have carried>`
- **Instructions improvised around:** `<skill/template/engine instruction that did not cover the situation, and what you did instead>`
- **What would have made this easier:** `<one concrete change to the handoff, templates, or skill — or none>`

## Return status
`complete | partial | blocked | out-of-scope | failed`
