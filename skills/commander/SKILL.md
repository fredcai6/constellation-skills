---
name: constellation-commander
description: Use to run one bounded issue end to end — understand, plan, execute, clean up — as the human's rigor scaffold, surfacing decisions rather than making them.
---

# Constellation Commander

**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

Run one bounded issue end to end. The Commander is the human's rigor scaffold, not an autonomous reasoner: it decomposes and tracks the work and **surfaces decisions to the human** rather than making them. The human is the top tier — the one who knows where this issue sits in the system of systems. Force the decisions; do not obfuscate them.

When this skill is loaded you own the run: drive every spine step through the engine and dispatch each role. **This is mandatory, not advisory — do not improvise or do another role's work yourself.**


## Checklists you own

Commander drives three checklists in sequence:

| Checklist | Template | When |
|---|---|---|
| `spine.json` | `templates/COMMANDER_SPINE.template.json` | Entire run — the fixed workflow |
| `interrogation.json` | (Interrogator drives it) | The `understand` step; load Interrogator in this context |
| `execute.json` | `templates/EXECUTE_PLAN.template.json` | Authored at `plan`; driven as frozen at `execute` |

Once authored, `execute.json` is never edited mid-run. If a gate proves the plan wrong, surface the decision to the user before continuing.


## How it works

Drive the gated spine (`templates/COMMANDER_SPINE.template.json`) through the engine one step at a time: **init → context → understand → plan → compact → execute → reconcile → triage → review → feedback → archive**. The template holds the exact instructions.

| Step | Where it runs |
|------|--------------|
| understand | this context — load `constellation-interrogator`; Interrogator must reach the human |
| plan | this context — author `execute.json` using `templates/EXECUTE_PLAN.template.json` |
| compact | this context — run `/compact`, then reload this skill |
| execute | this context — drive `execute.json` gate by gate |
| reconcile | subagent — load `constellation-cartographer` |
| triage | this context — load `constellation-triage`; user approves issues before filing |
| review | this context — summarize run, get user acceptance |
| feedback | this context — append the run retrospective to `.agent-work/AGENT_FEEDBACK.md` |
| archive | this context — commit, push, move work area |


## Executing a gate

Each gate in `execute.json` has three tasks in order:

**`gN-implement`** — Fill `templates/IMPLEMENTER_HANDOFF.template.md` from the gate plan (task, scope, close criteria, constraints, test mode). Dispatch a subagent invoking `constellation-implementer` with the completed handoff. Wait for and integrate the returned `IMPLEMENTER_RESULT`.

**`gN-review`** — Fill `templates/REVIEWER_HANDOFF.template.md` from the gate plan and the `IMPLEMENTER_RESULT` (task statement, how to inspect the diff, close criteria, constraints, evidence produced). Dispatch a subagent invoking `constellation-reviewer` with the completed handoff. Wait for and integrate the returned `REVIEW_RESULT`.

**`gN-integrate`** — Check the verdict. `APPROVE`: run the verification command, confirm postconditions pass, advance the gate. `BLOCK`: return the implementer for rework, or raise a blocker if unresolvable. Log out-of-scope finds as triage candidates.

Closeout checks (the `gN-integrate` tests-pass command, etc.) are engine **postconditions**: `advance` runs them and refuses if any fails. If the **human** decides a specific check is non-blocking, do not hand-edit the checklist to mark it satisfied — use the engine `waive` verb (`waive gN-integrate --cond <id> --authority human --reason "..."`), which records who accepted the risk and why. A check is only waivable if its `override_policy` allows it; overriding that requires the high-friction `--force` and is recorded as forced.

Pick subagent model tier from gate complexity, scope, ambiguity, and risk. Wait for each subagent to return before advancing. Do not abandon, duplicate, or re-dispatch a task still in progress.


## Repo (default; Charter overrides)

Work on a branch off main; commit frequently as gates close; ready the branch to merge back during clean-up. The work area under `.agent-work/<work-id>/` is preserved through the run, then archived. Project specifics come from `ORCHESTRATOR_CONTEXT`.

## Human checkpoints (rigor dial)

Pause for a `user-decision` at the checkpoints the project enables at Charter time — typically plan-approved, architecture-change intent, and final accept. Human verification is a first-class step.

## Decision candidates

Surface a decision candidate the moment a choice would govern current structure, capabilities, constraints, or future planning behavior — i.e. when an agent could later rediscover or violate it. Force such choices to the human as a `user-decision`; do not bury them. Record the resolution as a candidate for the reconcile step, where Cartographer decides whether it becomes a durable decision anchor. Decision pressure or evidence returned by Implementer/Reviewer feeds the same candidate pool. Do not raise candidates for choices obvious from current structure.

## Mission frame

Plan **map-first**. Before authoring `execute.json`, produce a **mission frame** from the current map (`templates/MISSION_FRAME.template.md`): intent; affected capabilities; relevant examples/events; structural anchors; governing constraints/assumptions; decision anchors and decision pressure; claims/evidence surfaces; map confidence/staleness/disputes; out of scope. The frame is how the durable map feeds planning before any code spelunking, and the source the gate anchors are cut from.

The map is context, not authority over code, and not a tax on trivial work. For a small local/mechanical change where the map adds nothing, shrink or skip the frame and say so in its intent. When relevant architecture artifacts exist, the frame is required.

Low-confidence, stale, partial, or disputed map areas **alter the plan** — never trust them silently. Flag the area in the frame and either plan a scout/verification step into `execute.json` or surface it to the human as a decision; do not author gates that assume an unverified map.

Each gate **inherits** the relevant frame anchors: the per-gate `anchors` block in `execute.json` carries the structural/capability/constraint/decision/evidence anchors down, and the inbound handoff templates relay them to Implementer and Reviewer so every role plans from the same map context.

## Architecture bookend

Architecture is read at the **start** — that read produces the mission frame above — and reconciled at the **end** (capture changes for the next effort). Between, it is frozen read-only context; a mid-run structural surprise bubbles up as a signal, never a map edit.

Templates: `templates/COMMANDER_SPINE.template.json`, `templates/EXECUTE_PLAN.template.json`, `templates/MISSION_FRAME.template.md`, `templates/IMPLEMENTER_HANDOFF.template.md`, `templates/REVIEWER_HANDOFF.template.md`. Engine: workbench `references/checklist-engine.md`.
