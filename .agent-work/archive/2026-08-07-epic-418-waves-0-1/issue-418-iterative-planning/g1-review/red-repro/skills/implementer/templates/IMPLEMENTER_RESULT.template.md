# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`<gate id/title>`

## Completed slice
`<what changed>`

## Scope
**Files changed:**
- `<path>`

**Specific exclusions touched:** `<no | yes + explanation>`

## Behavior changed
`<yes/no + summary>`

## Map Impact
Graph-impact notes carried UP so Cartographer reconcile consumes durable context without rediscovering it from scratch. Frame against the inbound Map Anchors using matching vocabulary; cite the diff. Omit a line when the work touched nothing for it. Skip the whole section for trivial local edits (no structural, capability, constraint, or decision impact).

- **Structural anchors touched:** `<struct:id — path/symbol, level — what changed there>`
- **Capabilities added/changed/affected:** `<capability:id or new label — behavior now observable; references "Behavior changed" above>`
- **Events added/changed/affected:** `<event:id or new label — only if architecturally meaningful>`
- **Constraints/assumptions touched:** `<constraint:id | assumption:id — honored, stressed, or newly relied on>`
- **Decision candidates / resolved decisions:** `<decision:id or candidate — rationale that may need authority; surface when a choice was forced>`
- **Claims/evidence produced:** `<claim:id or assertion — backed by the Evidence above; what it verifies>`
- **Trust limitations / drift found:** `<map area now low-confidence/stale/disputed, or manual-traceability gap>`
- **Triage candidates:** `<future work, unresolved decision, or structure/constraint mismatch — for Cartographer to route>`

## Test mode
**Required:** `<test-first | test-after | evidence-only | none>`  
**Satisfied:** `<yes/no + reason>`

## Evidence

```bash
<command>
```

**Result:** `<pass/fail/not run + reason>`

## TDD evidence, if required

- Failing test observed: `<command/output>`
- Passing test observed: `<command/output>`
- Refactor while green: `<yes/no>`

## Docs/contracts touched
- `<path or none with reason>`

## Assumptions
- `<assumption or none>`

## Stop conditions hit
- `<condition or none>`

## Out-of-scope observations
- `<finding for Commander or none>`

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** `<what concrete wording in the handoff confused you, or which field was missing/wrong — name the field>`
- **Context rediscovered:** `<context you had to dig up that the anchors or handoff should have carried>`
- **Instructions improvised around:** `<skill/template/engine instruction that did not cover the situation, and what you did instead>`
- **What would have made this easier:** `<one concrete change to the handoff, templates, or skill — or none>`

## Return status
`complete | partial | blocked | out-of-scope | failed`
