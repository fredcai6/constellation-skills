# Triage Recommendation: Merge parallel gold module-cycle schema docs

## Classification
`missing doc`, `cleanup`

## Source checklist/artifact
- reconcile.json tc3 / reconcile-summary.md T3

## Structural anchor
`docs/evo/gold_module_training_cycle_report_schema.md`, `docs/report_schemas/gold_module_training_cycle.md`

## Problem
Two parallel canonical-style docs describe gold module training cycle fields. Issue-292 updated `docs/report_schemas/`; the generated `docs/evo/` doc may lag or duplicate.

## Current truth
- `docs/report_schemas/gold_module_training_cycle.md` — concise schema guide, updated issue-292 (2018–2024, gate ownership cross-links)
- `docs/evo/gold_module_training_cycle_report_schema.md` — generated from `gold_report_schema.py`, detailed field defs

## Desired/future concern
Agents and humans should not need to guess which doc is authoritative for a given field.

## Evidence
- reconcile-summary.md T3
- gold producer emits `schema_doc_path` pointing at docs/evo variant

## Impact
Doc drift causes wrong assumptions during validation, fusion, and agent work.

## Suggested scope
Decide single entry point (likely report_schemas as human guide + generated detail as appendix, or explicit cross-links and ownership table). Update producer `schema_doc_path` if needed.

## Non-goals
- Changing report JSON schema version
- Regenerating all gold artifacts

## Acceptance criteria
- [ ] One documented primary schema reference for gold module cycle
- [ ] Secondary doc clearly labeled as generated/detail or merged
- [ ] No contradictory train_years or field ownership between docs

## Recommended priority
`low`

**Reason:** Documentation hygiene; not blocking runtime.

## Issue creation authority
`ask user`
