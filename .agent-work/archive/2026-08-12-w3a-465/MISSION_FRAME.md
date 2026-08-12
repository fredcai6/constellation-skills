# Mission Frame — w3a-465

## Intent

Close the gap between three instructions and the machinery behind them, in `skills/reviewer/` and
`scripts/checklist_engine.py`: give the `r6-fowler` fill an engine verb and name it, stop the
engine's own writer from rewriting line endings, and correct the `SKILL.md` sentence that
contradicts the engine's `--override-reason`.

**Map status: DEGRADED-NO-MAP.** This repo ships no `docs/architecture/`. The context step
discharged the degraded verdict with two hash-pinned substitutes, and this frame's anchors are cut
from those substitutes, not from a map inventory that does not exist.

## Structural Anchors

- `docs/agents/ORCHESTRATOR_CONTEXT.md` — hash-pinned substitute. Names workflow mechanisms and
  verifiers as a "strengthened durable system" needing "targeted automated verification plus the
  relevant broader suite". Both changes here are mechanism changes and inherit that bar.
- `docs/agents/GLOSSARY.md` — hash-pinned substitute. Fixes the vocabulary this run works in:
  `spine`, `gate`, `projection`, `two-bin rule`, `scoped null`.

## Governing Constraints / Assumptions

- `docs/agents/GLOSSARY.md` — `two-bin rule`: every enforced invariant is checked by a command or
  attested by a named human; prose alone enforces nothing. This is why the `r6-fowler` command
  postcondition cannot simply be deleted.
- `docs/agents/GLOSSARY.md` — `spine`: "Read and change it only through the engine, never by hand."
  This is the constraint the current `r6-fowler` imperative pushes an agent to break.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — mechanism changes require targeted tests plus the broader
  suite.

## Decision Anchors & Decision Pressure

- **retext-check lifts to survey** — `amend`'s `retext-check` op becomes available on survey
  checklists; `add`/`drop`/`rescope` stay gated-only.
  `@grade: settled/read · leans g1 · settle: NOT yet observed -- g1 must capture the live refusal to red/amend-refusal.txt before the change and the working op after`
- **engine writes bytes** — `save()` preserves the file's existing line ending and writes
  bytes.
  `@grade: settled/inherited · leans g2 · settle: LF and CRLF fixtures, red before green`
- **prose moves, not the affordance** — `SKILL.md` learns about `--override-reason`;
  `consolidate()` is unchanged.
  `@grade: settled/observed · leans g3 · settle: docs/CHECKLIST_SCHEMA.md:276 documents the override as intentional`
- **Decision pressure —** extending a shared engine verb's reach is an interface change. Surfaced to
  the Admiral in the return, per LAUNCH_ORDER "Inherited Latitude".

## Claims / Evidence Surfaces

- **the placeholder is executed** — `record(result="pass")` runs `command`-kind postconditions, so
  the unfilled placeholder blocks the reviewer's own pass. Read in
  `scripts/checklist_engine.py:1887-1911`; the live refusal is still to be captured by g1.
- **no verb can fill it** — `amend` refuses a non-gated checklist. To be checked by running `amend`
  against a real survey and capturing the refusal to `red/amend-refusal.txt`. Not yet run.
- **the engine rewrites line endings** — one engine call on an LF checklist rewrites every line to
  CRLF on Windows. To be checked by a fixture test that g1 must observe red before the fix. Not yet run.

## Map Confidence / Staleness / Disputes

- Whole map absent (`DEGRADED-NO-MAP`, receipt `.agent-work/w3a-465/map-orientation.json`). The plan
  compensates by grounding every claim in an observed command result rather than in a structural
  assertion — nothing here is trusted because the map said so, because the map said nothing.

## Out of Scope

- `skills/interrogator/**` — carries the identical placeholder defect at `zc-consolidate`. Outside
  the fence; raised as a triage candidate.
- `consolidate()`'s override semantics — the affordance stays exactly as it is.
- The rest of the reviewer skill. LAUNCH_ORDER: "Do not turn this into a review of the whole
  reviewer skill."
