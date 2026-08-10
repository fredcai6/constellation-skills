---
name: constellation-<short-name>
description: <what inquiry this runs to a consolidated verdict>. Use when <triggering condition — visit-every-item inquiry that ends in one verdict>. Not <confusable skill> (<why different>).
invoker: <human | agent | both>
---

# Constellation <Title>

<Leading line: the inquiry this skill runs and the verdict it consolidates, in one sentence.>

Drive a `survey` checklist — by default via the MCP door's `spine_status`/`spine_survey_result`/`spine_evidence` tools (see workbench `references/checklist-engine.md` — MCP door) when this agent owns the process's bound spine, otherwise (and always for an in-session dispatched crew member driving its own survey) the CLI fallback: through `scripts/checklist_engine.py`. **Visit every item, append more from context, record each check (a failure is recorded, never blocks), then consolidate into one verdict.** Work the engine never saw did not happen; full doctrine: `_shared/global-everyone.md`.

## The checklist

Build a `survey` plan from `templates/<NAME>_CHECKLIST.template.json`:

1. **<criterion one>** — `record` pass/fail with a finding.
2. **<criterion two>** — `record` pass/fail with a finding.
3. Append any context-specific checks as flat siblings, then `consolidate --verdict <APPROVE|BLOCK|...>`.

## Verdict + independence

This skill runs in a **fresh, independent context** — never grading its own author's work. It renders a verdict (`APPROVE`/`BLOCK` + findings), it does not fix. Route real faults out. Schema: `references/<x>.md`.
