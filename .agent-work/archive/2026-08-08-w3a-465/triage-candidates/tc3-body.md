## What

Six repo JSON writers pass `encoding` but not `newline`, against CREW_CONTEXT's always-pass-newline
rule:

- `collect_feedback.py:290,365`
- `install_constellation.py:911,1182,1241`
- `build_architecture_map.py:385`

## Why it matters

#465 fixed the same defect class in `scripts/checklist_engine.py`'s `save()` (a text-mode writer
silently rewriting line endings on Windows). These six sites are the same shape of risk in
different files, found by the same pass that found `save()`'s bug.

## Evidence

- `.agent-work/w3a-465/RESULT.md` section 7, item 3
- `docs/agents/CREW_CONTEXT.md` (or equivalent) — the always-pass-`newline` rule
- The six call sites above

## Suggested scope

Audit each of the six sites: does it need `newline=""`/`newline="\n"` per the rule, or does its
context make text-mode intentional? Fix the ones that don't have a documented reason to differ, and
add the missing `newline=` argument. Consider a lint/test that catches a future writer missing it
(see the sibling `{checklist_dir}` substitution-road candidate for a broader structural fix).

## Out of scope

`scripts/checklist_engine.py`'s `save()` (already fixed) and journal append (separate triage
candidate).

## Origin

Raised during #465 (epic #418 wave 3) as an out-of-scope observation while fixing the identical
defect class in `save()`.
