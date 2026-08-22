---
name: constellation-<short-name>
description: <what inquiry this runs to a consolidated verdict>. Use when <triggering condition — visit-every-item inquiry that ends in one verdict>. Not <confusable skill> (<why different>).
invoker: <human | agent | both>
---

# Constellation <Title>

<Leading line: the inquiry this skill runs and the verdict it consolidates, in one sentence.>

Drive a `survey` checklist. When this survey *is* the spine this process's door is bound to, drive it through the MCP door's `spine_status`/`spine_survey_result`/`spine_evidence` tools (see `references/checklist-engine.md` — MCP door). A crew that must drive its own survey is dispatched so that it HAS its own door — its own process, its own `SPINE_FILE`/`SPINE_SESSION`, the same engine through a different door. An in-session subagent sharing its dispatcher's process has none: one door drives one spine at a time, and it refuses to rebind while its owner still holds that spine's lease. If no door is bound to your survey, you were dispatched in a way that cannot give you one — surface that to the tier that launched you rather than driving a door pointed at their spine. **Visit every item, append more from context, record each check (a failure is recorded, never blocks), then consolidate into one verdict.** Work the engine never saw did not happen; full doctrine: `_shared/global-everyone.md`.

## The checklist

Build a `survey` plan from `templates/<NAME>_CHECKLIST.template.json`:

1. **<criterion one>** — `record` pass/fail with a finding.
2. **<criterion two>** — `record` pass/fail with a finding.
3. Append any context-specific checks as flat siblings, then `spine_survey_result` with `action=consolidate` and `verdict=<APPROVE|BLOCK|...>`.

## Verdict + independence

This skill runs in a **fresh, independent context** — never grading its own author's work. It renders a verdict (`APPROVE`/`BLOCK` + findings), it does not fix. Route real faults out. Schema: `references/<x>.md`.
