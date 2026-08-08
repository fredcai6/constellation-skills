## What

`scripts/checklist_engine.py`'s `amend()` is 215 lines. Fowler long-method smell, flagged not
overridden by #465 (which added to it, since it was already the right place for the survey
`retext-check` change).

## Why it matters

`global-crew.md`'s "split a unit when its intent blurs" agrees with the smell. `amend()` now
carries at least six op kinds (`add`, `drop`, `rescope`, `retext-check`, plus whatever else lives
there) in one function; each op's branch is fairly self-contained, which is a reasonable split
seam.

## Evidence

- `.agent-work/w3a-465/RESULT.md` section 7, item 5
- `scripts/checklist_engine.py` `amend()` (currently ~line 2128 onward)
- `docs/agents/GLOSSARY.md` / `global-crew.md` long-method doctrine

## Suggested scope

Split `amend()` by op kind (e.g. one function per op, `amend()` dispatches), preserving the
all-or-nothing commit semantics the function currently relies on (ops build a deep-copied
candidate state before committing). Needs full-suite coverage since `amend()` is exercised by many
existing tests.

## Out of scope

Changing `amend()`'s external CLI/behavior — this is a pure internal refactor.

## Origin

Raised during #465 (epic #418 wave 3) while extending `amend()`'s `retext-check` op to run on
surveys.
