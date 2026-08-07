# Excursion Brief: `x1-overread` — measure what agents actually over-read

## The one named question

In recent constellation runs on this machine, which structural/scaffolding files (engine spines, checklist JSON, schema/template docs, skill internals) do agents actually Read even though the engine/workbench was supposed to abstract them away — and roughly how much context does that cost per run?

## Type

research

**Why this type:** facts from local run evidence; nothing to build.

## What "answered" looks like

A short cited report: concrete examples (which file was read, by which role/skill, at which step, how many lines), a rough token-cost estimate per run, and a ranked list of the top over-read surfaces. Also the inverse: cases where the engine's own output would have sufficed. Lands at `.agent-work/explore-design-thrust/excursions/x1-overread-RESULT.md`.

## Budget / stop conditions

- Budget: sample up to ~6 recent transcripts/archived work areas; do not attempt exhaustive coverage. Report back even if evidence is thin.
- Do NOT modify anything; read-only.
- **Scoped nulls:** a null verdict states what was and was NOT examined — it kills this sample under these conditions, never the over-read hypothesis.

## Research excursion

- **Sources:** session transcripts under `C:\Users\fredc\.claude\projects\C--Programs-constellation-skills\` (JSONL, look for Read tool calls targeting spine.json / cycle-*.json / *.template.* / schema/reference docs); archived work areas under `.agent-work/archive/` in `C:\Programs\constellation-skills`; if reachable, the f1brainz dogfood repo's archives. One known live example to include: this very session read all 270 lines of `.agent-work/explore-design-thrust/spine.json` to find two condition ids.
- **Findings format:** each claim cites transcript file + approximate location; counts derived from commands (per repo doctrine: distribution claims come from a command, not eyeballing), command included in the report.
