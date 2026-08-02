# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Route a concrete interface/field fix through the closeout `Template Update Candidates` table; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing. The useful entries name the exact step, field, or instruction that was ambiguous, missing, contradictory, or routinely improvised around. A `none` bullet requires a run-specific reason (`none — confirmed after review: <what you checked>`); entries whose signal sections are all bare `none` fail the feedback invariant check.

Newest entries on top.

---

## `<date>` — `<work-id>`

**Run shape:** `<commander | charter | ad-hoc>` · `<gates closed / steps run>` · `<subagent model tier(s) used>`

**Instruction adherence:** `<fully followed | minor deviations | material deviations>`
- `<where a skill / handoff / checklist was followed exactly, or where you had to improvise and why the instructions did not cover it>`

**Friction / unclear:**
- `<step, template field, context doc, or engine behavior that was ambiguous, missing, contradictory, or slowed the run>`

**Crew-reported friction:**
- `<lesson candidates harvested from Implementer/Reviewer Workflow Feedback sections at each gN-integrate — handoff gaps, rediscovered context, improvised instructions; or none reported>`

**What worked:**
- `<part of the workflow that carried its weight and should be kept as-is>`

**Improvement signals:**
- `<concrete change to a skill, template, context doc, or the engine that would have helped>` → disposition: `<none | logged as closeout template-update-candidate | route to Charter refresh | needs user decision>`

---
