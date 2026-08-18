# Implementer Handoff

## Gate
g4-verify (proof dispatch — no `--model` given, must resolve from the role's table default)

## Task
Read `scripts/run_crew.py`'s `ROLE_MODEL_TIERS` table and write a one-line
summary of the `"claude"` harness's populated roles and their default tiers
to `.agent-work/567-j/crew-handoffs/g4-verify-proof-note.md`. This is a real,
bounded, verifiable task — not a placeholder — used to prove that a crew
dispatched with no `--model` flag runs at its role's declared default rather
than any host setting.

## Protected Intent
None beyond producing the one artifact — this is a verification dispatch, not
a production change.

## Test Mode
Inspection-only — a one-line summary note, no code change, no test surface.

## Close Criteria
- `.agent-work/567-j/crew-handoffs/g4-verify-proof-note.md` exists and lists
  each populated `"claude"` role from `ROLE_MODEL_TIERS` with its default.

## Allowed Scope
- `.agent-work/567-j/crew-handoffs/g4-verify-proof-note.md` only. Read-only
  everywhere else.

## Specific Exclusions
- Do not modify `scripts/run_crew.py`, any test file, or anything outside the
  one named output path.

## Constraints
- None beyond Allowed Scope.

## Map Anchors (inbound)
No architecture map exists in this repo. Read `scripts/run_crew.py`'s
`ROLE_MODEL_TIERS` directly (added this wave, beside `build_crew_argv`).

## Deliverable Path Check
- **Local-only** — `.agent-work/567-j/crew-handoffs/g4-verify-proof-note.md`;
  intentionally under `.agent-work/`, tracked in this repo per its own
  convention (not gitignored), but not a production deliverable.

## Required Evidence
- The written note's content, pasted in the result.

## Wiring Grep
none — this task adds no callable symbol.

## Verification Commands
```bash
cat .agent-work/567-j/crew-handoffs/g4-verify-proof-note.md
```

## Suggested Model Tier
(intentionally omitted — this dispatch is the proof that omitting `--model`
resolves from the role's declared default, not this field)

## Authority
None beyond the task itself.

## Stop Conditions
None expected — trivial, bounded task.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape. Write it to
`.agent-work/567-j/crew-handoffs/g4-verify-implementer-result.md` before
ending your turn.
