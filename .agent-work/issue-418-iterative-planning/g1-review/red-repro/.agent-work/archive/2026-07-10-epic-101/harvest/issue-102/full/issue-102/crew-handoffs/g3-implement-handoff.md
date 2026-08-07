# Implementer Handoff

## Gate
g3-implement (issue #102, Move 3 — delete FOLLOW-THIS-SKILL-STRICTLY banners)

## Task
Delete the free-floating banner line `**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**`
(register rule: emphasis only at mechanism-backed gates — this banner is emphasis unattached to a
mechanism) from all 6 carriers. Delete OUTRIGHT — do not relocate.

Carriers (grep-confirmed, one banner each; note explorer's ends with a trailing period inside the bold):
- skills/charter/SKILL.md (line ~31)
- skills/commander/SKILL.md (line ~8)
- skills/explorer/SKILL.md (line ~8, `...RIGOROUSLY.**`)
- skills/implementer/SKILL.md (line ~22)
- skills/interrogator/SKILL.md (line ~18)
- skills/reviewer/SKILL.md (line ~24)

When deleting leaves a dangling blank line or an orphaned heading gap, tidy so the surrounding prose
still reads cleanly (collapse a double-blank to single). Do NOT remove any adjacent mechanism-backed
sentence — only the banner line itself.

## Test Mode
Inspection-only; keep suite green (`py -m pytest tests/ -q`).

## Close Criteria
- `grep -rc "FOLLOW THIS SKILL STRICTLY" skills/*/SKILL.md` → 0 in all files (before: 6 files, one each).
- No mechanism-backed prose collaterally removed; sections still read.
- Full suite green.

## Allowed Scope
Only the 6 SKILL.md files listed. Nothing else.

## Specific Exclusions
The compliance pointer lines from move 1 (leave), any other prose, prototyper, hygiene files (#105).

## Constraints
- Delete outright, do not relocate.
- Only the banner line; preserve everything else.

## Deliverable Path Check
- Committed — the 6 SKILL.md (tracked, not gitignored).
- Local-only — .agent-work/issue-102/crew-handoffs/g3-implement-result.md.

## Required Evidence
`grep -rc "FOLLOW THIS SKILL STRICTLY" skills/*/SKILL.md` before (6) and after (0); suite tail.

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
grep -rn "FOLLOW THIS SKILL STRICTLY" skills/*/SKILL.md   # after: no output (exit 1)
py -m pytest tests/ -q
```

## Suggested Model Tier
simple bounded — mechanical deletion.

## Authority
Deletion is ruled. You decide only whitespace tidy-up.

## Stop Conditions
Stop if deleting the banner would require removing adjacent mechanism-backed content, or the suite goes red.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g3-implement-result.md AND as
your final message): files changed, before/after grep, suite tail, any whitespace tidy, workflow
feedback. Your FINAL MESSAGE must be the complete IMPLEMENTER_RESULT.
