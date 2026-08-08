## What

`scripts/checklist_engine.py`'s journal append (`jp.open("a", encoding="utf-8")`, near line 2762)
is still text-mode — the same defect class #465 just fixed in `save()`: on Windows, a text-mode
write can churn `\n` into `\r\n` on append, corrupting an existing journal's line endings the same
way `save()` used to corrupt a checklist file's.

## Why it matters

The journal is the durable audit trail the engine's own doctrine points to ("the journal, not your
prose, is the proof"). A byte-faithful `save()` sitting next to a text-mode journal append is an
inconsistency in the same file that a future reader will trust unevenly.

## Evidence

- `.agent-work/w3a-465/RESULT.md` section 7, item 2
- `scripts/checklist_engine.py` — journal append near line 2762
- `scripts/checklist_engine.py` `save()` (fixed in #465, commit `6774e75e`) as the pattern to mirror
- `tests/test_engine_survey_retext_and_newlines.py` — the LF/CRLF fixture shapes #465 shipped for
  `save()` are a template for a journal-append equivalent

## Suggested scope

Make the journal append byte-faithful the same way `save()` now is: preserve the existing file's
line ending, write bytes, default new files to LF. Needs its own red-before-green fixture pair
(the journal is append-only, so the fixture/assertion shape differs slightly from `save()`'s).

## Out of scope

Any other engine writer (see the sibling triage candidate for the six repo JSON writers missing
`newline=`).

## Origin

Raised during #465 (epic #418 wave 3), deliberately fenced out of that gate's scope (`save()`
only).
