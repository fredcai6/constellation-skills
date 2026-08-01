# Triage Recommendation: Map instantiation revisit trigger (record only)

## Classification
missing architecture packet (deliberately deferred)

## Source checklist/artifact
- Issue 87 "Map revisit trigger (record, no action)"

## Structural anchor
docs/architecture/ (absent by design); first packet = scripts/checklist_engine.py

## Cartographer mismatch class
none

## Problem
This repo runs Constellation on itself but carries no Cartographer map; Commander runs shrink their mission frames with a stated reason each time.

## Current truth
No docs/architecture/. Issue 87 records the trigger: instantiate the map when a third crew backend or a new engine verb class appears; first packet should cover checklist_engine.py.

## Desired/future concern
When the trigger fires, run Cartographer to instantiate the map starting from the engine packet.

## Evidence
- Issue 87 body, "Map revisit trigger" section
- issue-87 MISSION_FRAME.md (frame shrunk, reason stated)

## Impact
Keeps map-first doctrine honest without paying map maintenance before the structure warrants it.

## Suggested scope
None now — record only, per issue 87.

## Non-goals
Filing an issue; instantiating the map this run.

## Acceptance criteria
- [ ] Trigger recorded durably (this recommendation, archived with the run)

## Recommended priority
low

**Reason:** explicitly record-only by the issue's own instruction.

## Related artifacts
- .agent-work/issue-87/MISSION_FRAME.md

## Disposition
recommend-and-defer

**Detail:** issue 87 explicitly instructs record-only, no issue.

## Issue creation authority
issue-ready only
