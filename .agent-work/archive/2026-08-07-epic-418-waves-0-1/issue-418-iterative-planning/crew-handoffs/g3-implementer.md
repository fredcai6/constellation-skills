# Implementer Handoff

## Gate

`g3`

## Task

Wire the approved G1 initial-cut and G2 replanning contracts into the live Explorer, Commander, and Admiral role doctrine. Use `constellation-implementer`. The complete G3 imperative in `.agent-work/issue-418-iterative-planning/execute.json` is frozen and contractual.

## Protected Intent

The system shapes just enough to launch one coherent wave, learns from execution evidence, and explicitly chooses one of four exits before any next launch. Forecast is provisional. Discrepancies return as evidence, not automatically filed issues. Fixed intent and human authority remain protected.

## Test Mode

TDD required. Add `tests/test_iterative_planning_doctrine.py` and any necessary Explorer-template assertions before doctrine edits. Use the identical focused command for causal red and green:

```bash
uv run python -m pytest -q tests/test_explorer_templates.py tests/test_iterative_planning_doctrine.py
```

The red must fail on missing parsed doctrine/template invariants or a public seam—not marker trivia, import, or setup.

## Required Contracts

- Explorer's executable confirmed output is the exact G1 `SHAPED_BRIEF.template.json`; no separate prose-only execution handoff. It retains ideas/evidence and applies critic/design-it-twice weight only to irreversible or load-bearing initial commitments.
- The direct Explorer template → initial-cut verifier/renderer seam remains green and field-preserving.
- Commander records observed discrepancies/evidence into the exact G2 `REPLAN_INPUT` fields and classifications without auto-filing them.
- Admiral consumes exact checked-in `REPLAN_INPUT`/`REPLAN_RESULT`, treats forecast as provisional, invokes replan at each wave boundary and material exception, records exactly one `advance|repair|replan|stop` exit before launch, holds forecast under repair, and renders updated current-truth epic body plus wave-review comment.
- Direct `gh`/network mutation is forbidden. Future posting is only through the existing authorized tracker port after normal authority/review gates.
- Beyond-latitude fixed changes escalate; existing reviewer, checklist-engine, recovery, audit, and human checkpoints remain intact.

## Allowed Scope

Live doctrine/templates for `skills/explorer/**`, `skills/commander/**`, `skills/admiral/**`; `tests/test_explorer_templates.py`; new `tests/test_iterative_planning_doctrine.py`; current role context/docs/indexes only where necessary for the operative invariant chain. Prefer references/templates over duplicating schema prose.

## Specific Exclusions

No engine redesign, tracker implementation, direct GitHub/network mutation, automatic discrepancy filing, compatibility alias, archive/history/external provenance edits, G1/G2 schema changes, or demo artifacts (G4). Do not weaken human checkpoints or independent review.

## Evidence and Quality

- Parse live Markdown/templates to prove the operative chain, not mere phrase presence.
- Exercise a public seam showing a Commander-shaped discrepancy packet validates as exact G2 input and an Admiral-consumed result observes one exit/repair hold/render behavior.
- Re-run the G1 direct seam and relevant G2 contract tests confirmatorily.
- Scoped wiring search for every named template/path/helper; zero real consumers is a stop condition unless an executable doctrine test proves intended manual-agent consumption.
- `git diff --check`, JSON parsing, and no-network/`gh` audit for the inventory.

## Deliverable Path Check

- **Committed:** live role doctrine/templates and focused tests; representative paths are not ignored.
- **Local-only:** `.agent-work/issue-418-iterative-planning/g3-implement/IMPLEMENTER_RESULT.md`.

## Result

Write the result with `gate_id: g3`, `red_exit: 1`, `green_exit: 0`, tests-before-doctrine evidence, identical red/green command/output, ordinal path+byte digest/inventory/helper, scope/map impact, and workflow feedback. Drive the implementer checklist terminal and release its lease, then report to `/root`.
