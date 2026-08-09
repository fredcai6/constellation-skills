## What

`amend`'s type applicability (which ops work on a gated checklist vs. a survey) is restated in six
places across code and docs, rather than defined once and pointed at. #465's own first implementer
return shipped without updating five of the six prose sites — only the code and one doc were
initially touched — and the reviewer had to catch the gap before the fix could ship coherently
(see `.agent-work/w3a-465/RESULT.md` section 6, "A fence was extended, deliberately").

## Why it matters

Six independent restatements of the same fact is a structure that guarantees recurrence: the next
change to `amend`'s type applicability will very likely repeat #465's own near-miss (a true fix
that ships an inconsistent story across the corpus) unless the restatement is consolidated.

## Evidence

- `.agent-work/w3a-465/RESULT.md` section 7, item 6, and section 6 (the fence-extension story)
- The six sites: `scripts/checklist_engine.py` (the enforcement), `docs/CHECKLIST_SCHEMA.md`,
  `skills/workbench/references/checklist-engine.md`, `skills/reviewer/SKILL.md`,
  `skills/reviewer/templates/REVIEW_SURVEY.template.json`, and (per this candidate's sibling tc1)
  `skills/interrogator/templates/INTERROGATION.template.json`

## Suggested scope

Pick one canonical statement of `amend`'s type-applicability rule (likely
`docs/CHECKLIST_SCHEMA.md`, since it's the schema doc) and make the other five sites point at it
instead of restating it, the same consolidation pattern `constellation-curator` already applies to
duplicated doctrine prose elsewhere in the corpus.

## Out of scope

Changing the applicability rule itself — this is a pure duplication/pointer cleanup.

## Origin

Raised during #465 (epic #418 wave 3), observed directly from the run's own near-miss.
