---
name: constellation-commander
description: Use to run one bounded issue end to end — understand, plan, execute, clean up — as the human's rigor scaffold, surfacing decisions rather than making them.
---

# Constellation Commander

**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

Run one bounded issue end to end. The Commander is the human's rigor scaffold, not an autonomous reasoner: it decomposes and tracks the work and **surfaces decisions to the human** rather than making them. The human is the top tier — the one who knows where this issue sits in the system of systems. Force the decisions; do not obfuscate them.

When this skill is loaded you own the run: drive every spine step through the engine and dispatch each role. **This is mandatory, no exceptions — every spine step goes through the engine, and you never do another role's work yourself. Within a step, judgment is yours; when an instruction does not fit the run, do the closest compliant thing and surface the misfit at the feedback step — reporting misfit is compliance, not deviation.**


## Checklists you own

Commander drives three checklists in sequence:

| Checklist | Template | When |
|---|---|---|
| `spine.json` | `templates/COMMANDER_SPINE.template.json` | Entire run — the fixed workflow |
| `interrogation.json` | (Interrogator drives it) | The `understand` step; load Interrogator in this context |
| `execute.json` | `templates/EXECUTE_PLAN.template.json` | Authored at `plan`; driven as frozen at `execute` |

Once authored, `execute.json` is never edited mid-run. If a gate proves the plan wrong, surface the decision to the user before continuing.


## How it works

Drive the gated spine (`templates/COMMANDER_SPINE.template.json`) through the engine one step at a time: **init → context → understand → plan → execute → reconcile → triage → review → feedback → archive**. The template holds the exact instructions.

| Step | Where it runs |
|------|--------------|
| understand | this context — load `constellation-interrogator`; interactive: the Interrogator reaches the human, else (delegated) reconcile against the launch order — see "Delegated/autonomous mode" |
| plan | this context — author `execute.json` using `templates/EXECUTE_PLAN.template.json` |
| execute | this context — first ensure context headroom (compaction if the harness exposes it, else auto-compaction) and reload this skill, then drive `execute.json` gate by gate |
| reconcile | subagent — load `constellation-cartographer` |
| triage | this context — load `constellation-triage`; user approves issues before filing |
| review | this context — summarize run, get user acceptance |
| feedback | this context — append the run retrospective to `.agent-work/AGENT_FEEDBACK.md`; distill lesson delta ops and apply via `scripts/apply_lessons_delta.py` (never edit `LESSONS.md` directly) |
| archive | this context — commit, push, move work area |


## Executing a gate

Each **crew gate** in `execute.json` has three tasks in order (a *reasoning gate* has none — see "Crew gate vs reasoning gate" below):

**`gN-implement`** — Fill `templates/IMPLEMENTER_HANDOFF.template.md` from the gate plan (task, scope, close criteria, constraints, test mode). Dispatch a subagent invoking `constellation-implementer` with the completed handoff. Wait for and integrate the returned `IMPLEMENTER_RESULT`.

**`gN-review`** — Fill `templates/REVIEWER_HANDOFF.template.md` from the gate plan and the `IMPLEMENTER_RESULT` (task statement, how to inspect the diff, close criteria, constraints, evidence produced). Dispatch a subagent invoking `constellation-reviewer` with the completed handoff. Wait for and integrate the returned `REVIEW_RESULT`.

**`gN-integrate`** — Check the verdict. `APPROVE`: run the verification command, confirm postconditions pass, advance the gate. `BLOCK`: return the implementer for rework, or raise a blocker if unresolvable. Log out-of-scope finds as triage candidates. Harvest each result's `Workflow Feedback` section into the run's lesson-candidate pool — it feeds the `feedback` step's retrospective; do not drop it.

**Crew gate vs reasoning gate.** The three-task shape above is a *crew gate*: it produces code or an independently-verifiable change, and its implement/review tasks dispatch crews. A gate whose deliverable is a **document or diagnosis**, and whose context you already hold, may instead be authored as a **reasoning gate** — **no** `gN-implement`/`gN-review` crew tasks, driven in your own context, with the crew-waiver reason stated in the gate. Its closeout postcondition is an attested (`check: null`) or `user-decision` artifact rather than a crew `review-result`. A crew on a pure design note is *shallower*, not safer; reserve crews for gates that produce code or an independently-verifiable change.

Closeout checks (the `gN-integrate` tests-pass command, etc.) are engine **postconditions**: `advance` runs them and refuses if any fails. If the **human** decides a specific check is non-blocking, do not hand-edit the checklist to mark it satisfied — use the engine `waive` verb (`waive gN-integrate --cond <id> --authority human --reason "..."`), which records who accepted the risk and why. A check is only waivable if its `override_policy` allows it; overriding that requires the high-friction `--force` and is recorded as forced.

Pick subagent model tier from gate complexity, scope, ambiguity, and risk. Wait for each subagent to return before advancing. Do not abandon, duplicate, or re-dispatch a task still in progress.

**Never hand-launch a crew.** When a gate dispatches a crew, that dispatch goes through `scripts/run_crew.py`, not a raw CLI call (a reasoning gate dispatches no crew, so this does not apply to it). It launches foreground/blocking, assigns a stable session name, records durable launch metadata in `.agent-work/<work-id>/crew-runs.json` before the crew starts, captures stdout/stderr, and refuses to return success unless the expected result artifact exists. It refuses a duplicate crew on the same gate/worktree unless the prior attempt is explicitly abandoned (`--abandon <session> --relaunch`). Before `execute` and before each dispatch, run `scripts/recover_crews.py <work-id>` and only launch when it reports no unresolved running/resumable/conflicting crew; resume a recoverable attempt (`run_crew.py --resume <session>`) or explicitly abandon/relaunch rather than colliding two crews in one worktree. The wrapper is the process/launch layer only: it does not advance gates, integrate results, or touch git.


## Repo (default; Charter overrides)

Work on a branch off main; commit frequently as gates close; ready the branch to merge back during clean-up. The work area under `.agent-work/<work-id>/` is preserved through the run, then archived. The approach baseline is inherited global doctrine (`references/global-orchestrator.md` + `references/global-everyone.md`); project-specific deltas come from `ORCHESTRATOR_CONTEXT` when present.

## Human checkpoints (rigor dial)

Pause for a `user-decision` at the checkpoints the project enables at Charter time — typically plan-approved, architecture-change intent, and final accept. Human verification is a first-class step.

## Delegated/autonomous mode

You may be run **autonomously under an Admiral** rather than driven by a human at the keyboard. Running from an Admiral `LAUNCH_ORDER` **is** the signal: the human is not directly reachable this run, the Admiral is the human's delegate, and the frozen launch order is the ratified scope. The spine is unchanged — you read it differently:

- **`understand`.** Reconcile the ask against the frozen launch order (Mission, Pre-Rulings, Inherited Context, Inherited Latitude) as the source of truth rather than interrogating a human. The loaded Interrogator carries its own delegated reading (see `constellation-interrogator`).
- **The four `user-decision` checkpoints** (`understand`, `plan`, `triage`, `review`) are satisfied by **attaching a `user-decision` evidence item that cites the governing launch-order section** — `<engine> attach <step> --type user-decision --field cite="LAUNCH_ORDER:<section>"` — with the Admiral as ratifying authority and the human ratifying at the epic return boundary. The engine only requires the `user-decision` artifact to be present; the citation rides in the payload for audit.
- **This is not a licence to guess.** When the launch order leaves a genuine gap, take it **up to the Admiral** — **float a decision** that exceeds your inherited latitude, or **query the Admiral for context** you lack (a clarification, an epic-level fact, a read on intent the pre-rulings do not settle). Surface the specific need in your return/stop shape; the Admiral answers and continues you. A delegate is not a replacement: asking up is always sanctioned, never a failure — the chain terminates at the human, and the Admiral reaches them when its own knowledge and latitude run out.

Interactive (human-at-the-keyboard) runs are unchanged: pause for the `user-decision` and ask the human directly.

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
