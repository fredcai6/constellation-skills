# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g4` — Cross-file history-to-current-truth sweep (non-admiral/docent/interrogator files)

## Task
Rewrite three history-framing lines as timeless current truth, meaning-preserving (rule stays, "is now X / not Y-only" origin framing goes). Surgical single-line-ish edits only.

## Protected Intent
Each rule reads as present-tense current truth; no operative content or pointer name lost.

## Test Mode
inspection-only — three surgical edits; verified by grep + full suite green.

## Close Criteria
- The three edits below applied.
- Pointer names preserved: `design-it-twice-brief.md` and `global-orchestrator.md` still present in explorer.
- No forbidden signatures introduced.
- Full suite green: `py -m pytest tests/ -q`.

## Exact edits

### 1. `skills/explorer/SKILL.md` (~line 63)
BEFORE:
> - Design-it-twice is now a tier-wide standard, not an explorer-only move: see `references/global-orchestrator.md` "Design-it-twice (standard, not optional)" and the shared `references/design-it-twice-brief.md` contract — this excursion type is its design-phase form.

AFTER:
> - Design-it-twice is a tier-wide standard (see `references/global-orchestrator.md` "Design-it-twice (standard, not optional)" and the shared `references/design-it-twice-brief.md` contract); this excursion type is its design-phase form.

### 2. `skills/charter/references/rigorous-default.md` (~line 3)
BEFORE:
> The rigorous default posture is now **inherited runtime doctrine**, not a Charter-only reference. It is
> authored once in the global buckets bundled with every skill at install:

AFTER:
> The rigorous default posture is **inherited runtime doctrine**, authored once in the global buckets
> bundled with every skill at install:

### 3. `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` (~line 26)
BEFORE:
> Template/interface and doctrine fixes are now lessons carrying a `target`, settled at the
> Commander `feedback` step by the forced apply-or-defer gate (`verify_lessons_applied.py`) — not
> a separate advisory table. Confirm here only that the gate passed: every ripe lesson was
> applied, exported, or deferred with a reason.

AFTER:
> Template/interface and doctrine fixes are lessons carrying a `target`, settled at the
> Commander `feedback` step by the forced apply-or-defer gate (`verify_lessons_applied.py`), not
> a separate advisory table. Confirm here only that the gate passed: every ripe lesson was
> applied, exported, or deferred with a reason.

(If any BEFORE text has drifted, adapt to current wording, removing only the "is now / are now ... not ...-only" temporal framing and preserving the rule + pointers.)

## Allowed Scope
Exactly these three files: `skills/explorer/SKILL.md`, `skills/charter/references/rigorous-default.md`, `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md`.

## Specific Exclusions
NOT `skills/commander/**` (issue #107), NOT `skills/admiral/**` (g1), NOT `skills/docent/**` (g2), NOT `skills/interrogator/**` (g3), NOT `_shared/**`, NOT `tests/**`, NOT `docs/ROADMAP.md`.

## Constraints
- Meaning-preserving; only the temporal/history framing is removed.
- Explorer pointer names `design-it-twice-brief.md` and `global-orchestrator.md` must survive.
- Do not reflow unrelated text.

## Map Anchors (inbound)
- **Structural:** the three named files/lines.
- **Constraints:** meaning-preserving; pointer names survive; full suite green.

## Deliverable Path Check
- **Committed** — the three files; `git check-ignore` exit 1 each.
- **Local-only** — `.agent-work/issue-103/crew-handoffs/g4-implement-result.md`.

## Required Evidence
- `git --no-pager diff --stat` showing exactly the three files.
- `grep -nE "is now a tier-wide|is now \*\*inherited|are now lessons" skills/explorer/SKILL.md skills/charter/references/rigorous-default.md skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` (expect NO output after edit).
- `grep -oE "design-it-twice-brief.md|global-orchestrator.md" skills/explorer/SKILL.md | sort -u` (expect both present).
- Full suite tail: `py -m pytest tests/ -q`.

## Verification Commands
```bash
cd /c/Programs/constellation-wt-103
git --no-pager diff --stat
grep -nE "is now a tier-wide|is now \*\*inherited|are now lessons" skills/explorer/SKILL.md skills/charter/references/rigorous-default.md skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md
grep -oE "design-it-twice-brief.md|global-orchestrator.md" skills/explorer/SKILL.md | sort -u
py -m pytest tests/ -q
```

## Suggested Model Tier
`simple bounded — three surgical detemporalizations`

## Authority
Edits decided above. Do not sweep additional lines beyond these three (other temporal "now" usages in the corpus are current-state present tense, not history framing, and are out of scope for this gate).

## Stop Conditions
Stop if: an edit would change meaning, a pointer name would be lost, or the full suite reds for a reason outside these edits.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/issue-103/crew-handoffs/g4-implement-result.md` AND final message before idling): three edits done, diff --stat, grep evidence, full-suite tail, assumptions, stop conditions, out-of-scope observations, workflow feedback.
