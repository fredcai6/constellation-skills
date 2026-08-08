## What

CREW_CONTEXT's "always pass `newline=`" rule now has an unnamed exception:
`scripts/checklist_engine.py`'s `save()` (fixed in #465) deliberately does NOT pass a fixed
`newline=` — instead it reads and preserves whichever line ending the target file already has,
which satisfies the rule's *intent* (byte-faithful, no silent rewrite) more strongly than its
literal prescribed mechanism (a fixed `newline=` argument).

## Why it matters

A rule whose prose doesn't name its own best-known exception invites the next reader to "fix"
`save()` back into non-compliance with the letter of the rule, undoing #465's actual fix. Same
prose-contradicts-code class #465 corrected in `skills/reviewer/SKILL.md`, one tier up (repo-wide
doctrine instead of one skill's prose).

## Evidence

- `.agent-work/w3a-465/RESULT.md` section 7, item 4
- `docs/agents/CREW_CONTEXT.md` (or equivalent) — the always-pass-`newline` rule
- `scripts/checklist_engine.py` `save()` (commit `6774e75e`) as the exception in question

## Suggested scope

Add one sentence to the rule naming `save()`'s file-line-ending-preservation as the sanctioned
exception (a byte-preserving writer earns exactly the same trust the rule is protecting).

## Out of scope

Any other engine writer's compliance with the rule.

## Origin

Raised during #465 (epic #418 wave 3) as a same-class prose gap one level above the issue's own
fix.
