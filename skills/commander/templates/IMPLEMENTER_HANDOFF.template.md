# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`<gate id from execute.json, e.g. g1>`

## Task
`<one bounded task — what to build>`

## Protected Intent
`<the user/system outcome this gate must not violate>`

## Test Mode
`<TDD required | test-after allowed | inspection-only — brief reason>`

## Close Criteria
`<what must be true when done; each item the implementer proves>`
- `<criterion>`

## Allowed Scope
`<files, modules, regions, or decisions the implementer may touch>`
When the gate adds or changes a validation, **pre-authorize the test files that already exercise the gated behavior** (their test data/harness, not excluded production code) so a legitimate minimal reconciliation of those tests does not read as an out-of-scope breach.

## Specific Exclusions
`<things that look in-scope but are off-limits; omit section if none>`
In a multi-issue wave, **annotate every fenced / do-not-touch line with the OWNING issue number**, and where two gates' or issues' scopes intersect, name the exclusion explicitly at the intersection.

## Constraints
`<rules the implementation must respect — from project rules or gate-specific needs>`
- `<rule>`

When the task passes an object/dataclass-typed parameter, **name its fields explicitly** rather than leaving the crew to infer the shape from surrounding call sites.

## Map Anchors (inbound)
Map context this gate inherits from the mission frame, so the implementation lands on the right structure and honors recorded rules. Omit a line when the gate carries nothing for it.
- **Structural:** `<struct:id — path/symbol, level — where the work lands or depends>`
- **Capability:** `<capability:id — behavior this gate changes or relies on>`
- **Constraints/assumptions:** `<constraint:id | assumption:id — must not be silently violated>`
- **Decision anchors:** `<decision:id — governs this structure; do not contradict without surfacing a candidate>`
- **Evidence expectations:** `<claim:id or check this gate must re-confirm>`
- **Map confidence flags:** `<node id — low-confidence/stale/disputed area; verify rather than trust; omit if none>`

## Deliverable Path Check
`<required — filled by the commander at gate-planning time, before dispatch. For each of this gate's deliverable artifact path(s), classify it:>`
- **Committed** — `<path>`; verified via `git check-ignore <path>` exiting 1 (not ignored) before dispatch — record the exact command run and its exit code.
- **Local-only** — `<path>`; intentionally gitignored (e.g. under `.agent-work/`) — state this explicitly so the reviewer does not expect it in the diff.

## Required Evidence
`<what to produce: test output, command result, inspection note, generated artifact>`
When the crew must assert a specific return/message string, **quote the EXACT expected string** so the crew asserts equality, not a substring guess; mark any illustrative example string as illustrative.

## Verification Commands

Exact commands to run. Write `none — <reason>` if not applicable.

```bash
<command>
```

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Authority
`<decisions already made and by whom; what the implementer must not decide alone>`

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
