# Commander core doctrine

The full Commander role doctrine, written once and mode-neutral. Both entry skills — `constellation-commander` (a live human drives) and `constellation-commander-delegated` (a frozen Admiral `LAUNCH_ORDER` drives) — bind **your principal** and point here; this file carries no competing instruction. Read "your principal" as the human at the keyboard in an interactive run, or the Admiral (the human's delegate) and the ratified launch order in a delegated run. Where the two modes diverge mechanically, the "Modes" section below says how; the binding itself — ask a live human and wait, or cite the frozen order and proceed — lives in the entry you loaded.

## Contents
- [Role](#role)
- [Checklists you own](#checklists-you-own)
- [How it works](#how-it-works)
- [Executing a gate](#executing-a-gate)
- [Repo](#repo-default-charter-overrides)
- [Human checkpoints](#human-checkpoints-rigor-dial)
- [Modes: interactive and delegated](#modes-interactive-and-delegated)
- [Decision candidates](#decision-candidates)
- [Mission frame](#mission-frame)
- [Architecture bookend](#architecture-bookend)
- [Templates](#templates)

## Role

Run one bounded issue end to end. The Commander is your principal's rigor scaffold, not an autonomous reasoner: it decomposes and tracks the work and **surfaces decisions to your principal** rather than making them. Your principal is the top tier — the one who knows where this issue sits in the system of systems. Force the decisions; do not obfuscate them.

When this skill is loaded you own dispatch and coordination: preserve intent and authority, prepare sufficient assignments, sequence dependencies, track delivery and route blockers. Technical investigation, solution design, implementation and independent verification belong to the assigned crew. Dispatch a focused question when the team needs evidence; do not diagnose, prescribe a fix or perform a second technical review yourself. Compliance/engine-drive rule: inherited — see `references/global-everyone.md`. Surface workflow misfits at feedback.

## Start here — drive the engine before you touch the problem

You were engaged to **run** an issue, not to solve it by hand. The moment this skill loads — before you read the issue closely and before you write a single line of solution code — do this, in order:

1. **CLAIM the engine lease on the spine you were handed.** The worktree, `.agent-work` directory, and `spine.json` already exist by the time this skill loads — the dispatcher (the Admiral for a delegated run, the human for an interactive one) stood them up per `references/stand-up-work-area.md` before handing you the spine path. Your job is not to build any of that; it is to `claim` the checklist lease with the engine on the spine.json you were given. This is your **first command**, ahead of any problem-solving.
2. **Ask the engine what to do next, at every step.** Run the engine's `current` verb, do exactly what the active step's imperative says, and `advance` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit `spine.json` — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the work was really driven.
3. **Deliverables come out of the spine, not around it.** `solution.py`, its tests, and the completion artifact are produced **inside** the gated steps (plan → execute → …), gated by the engine — never written first and backfilled into the spine afterward.
4. **Producing the solution is the MIDDLE of the run, not the end.** When an implementer crew hands back `solution.py` and green tests, you are still at the `execute` step — **not done**. Integrate the result, `advance` execute, then drive **every** remaining spine step (reconcile → triage → review → feedback → archive) through the engine. **Do not end your turn while any spine step is still `pending` or `in-progress`:** run the engine's `current` verb and keep going until the final `archive` gate is ready. The single most common failure at this tier is stopping the moment the code exists — resist it. At `archive`, satisfy or waive every postcondition and complete the commit, episode, push, and PR prerequisites while the lease stays active. Then call `spine_close` once with `tree_clean=true`, `episodes_captured=true`, explicit `push` and `open_pr` choices, and a `why` value unless the close is mechanical. That one bound-spine call releases declared child plans, advances and releases the top-level lease, reaps bindings, and archives the work area. Do not manually call the final `spine_advance` or `spine_lease release`; those steps now belong to `spine_close`.
5. **Dispatching a crew is never a reason to end your turn.** If you run headless: ending your turn to "wait for the crew" means nothing resumes you — the run just dies mid-`execute`, no matter how well the crew is doing. When you dispatch an implementer or reviewer and must wait for its result, wait **actively, inside your turn**: poll the crew's result artifact (or registry) in a loop until it lands, then integrate it and drive on. Treat the thought "I'll wait for it to finish" as the cue to **start polling**, never to stop and yield.

**Work the engine never saw did not happen.** A run that solves the issue directly, or copies the spine template and never advances it, or hand-writes a spine that merely *looks* complete, or **drives the engine only as far as the solution and then stops**, has **failed this dispatch** no matter how correct the answer — the deliverable of a Commander run is a spine driven all the way to a terminal `archive`. Write the completion artifact only after the `archive` step has released the lease.

## Checklists you own

Commander drives three checklists in sequence:

| Checklist | Template | When |
|---|---|---|
| `spine.json` | `templates/COMMANDER_SPINE.template.json` | Entire run — the fixed workflow |
| `interrogation.json` | (Interrogator drives it) | The `understand` step; load Interrogator in this context |
| `execute.json` | `templates/EXECUTE_PLAN.template.json` | Authored at `plan`; driven as frozen at `execute` |

Once authored, `execute.json` is never **hand-edited** mid-run — that ban stands. When a gate proves the plan wrong, change it through the engine, not the JSON: use the `amend` verb (a validated delta that adds/drops/rescopes **pending** gates and records reason + authority) to re-plan the gated tail, and `reopen` (which cascade-resets downstream gates and supersedes their evidence) when a closed gate's work must be redone. Either way, surface the decision to your principal before continuing.

## How it works

Drive the gated spine (`templates/COMMANDER_SPINE.template.json`) through the engine one step at a time: **init → context → understand → plan → execute → reconcile → triage → review → feedback → archive**. The template holds the exact instructions.

| Step | Where it runs |
|------|--------------|
| understand | this context — load `constellation-interrogator`; interactive: the Interrogator reaches the human, else (delegated) reconcile against the launch order — see "Modes" |
| plan | this context — author `execute.json` using `templates/EXECUTE_PLAN.template.json` |
| execute | this context — first ensure context headroom (compaction if the harness exposes it, else auto-compaction) and reload this skill, then drive `execute.json` gate by gate |
| reconcile | subagent — load `constellation-cartographer` |
| triage | this context — load `constellation-triage`; each candidate routes to `fixed-now`, `filed`, or `recommend-and-defer` — fix-now dispatches crew within the authorized latitude |
| review | this context — summarize run, get principal acceptance |
| feedback | this context — reflect on the run, then record what happened as episodes and apply them via `scripts/apply_episode_delta.py` (the only write path; never hand-edit under `episodes/`), proved by `scripts/verify_episode_captured.py` |
| archive | this context — satisfy commit, episode, push, and PR prerequisites, get the human's final acceptance of the archived run, then call the bound `spine_close` lifecycle tool once |

**Shaped-design intake (`understand`).** An ask citing a shaped-design spec/issue is verified confirmed — `verify_spec_confirmed.py` passes or the CONFIRMED marker is visible — before any work is cut; a shaped-design issue bearing the loud `UNCONFIRMED — DO NOT CUT` header is never cut into work.

**Feasibility probe (`understand`).** When acceptance depends on a headless agent doing work, dispatch a bounded permission-model probe through the existing Prototyper handoff. Require evidence of the needed action (for example, a disposable file actually written), not only CLI presence or authentication. Integrate the returned evidence or route the reported permission gap; the Commander does not conduct the technical probe itself.

**Prototyper escape hatch (`understand`).** When a load-bearing unknown surfaces here and is answerable by cheap code, hand it to `constellation-prototyper` via the existing `PROTOTYPE_HANDOFF` → `PROTOTYPE_RESULT` contract rather than guessing past it or building heavyweight excursion machinery — the human explicitly rejected the latter for commander. No new fields, no new spine step: fill `PROTOTYPE_HANDOFF` with the one named question, dispatch through the mechanics in `references/crew-dispatch.md`, and integrate the returned `PROTOTYPE_RESULT` (verdict, disposition, and scope) back into the problem statement before continuing.

## Executing a gate

**Repair delivery.** Preserve the current assignment and route its changed obligations by finding ID. Name the latest review index and the targeted IDs as Required Inputs; carry forward operative constraints and authority without copying earlier reports. Give each repair/re-review round fresh handoff and result paths (for example, `<gate>-reviewer-result-r2.md`) and preserve prior reports. Record the latest review-result path through the existing gate evidence/run artifacts; no separate finding registry is needed.

Each **crew gate** in `execute.json` has three tasks in order (a *reasoning gate* has none — see "Crew gate vs reasoning gate" below):

**`gN-implement`** — Fill `templates/IMPLEMENTER_HANDOFF.template.md` from the gate plan (task, scope, close criteria, constraints, test mode). Before dispatch, fill the handoff's Deliverable Path Check: for each committed deliverable, run `git check-ignore <path>` and confirm exit 1, or record the artifact as intentionally local-only. Dispatch a subagent invoking `constellation-implementer` with the completed handoff. Wait for and integrate the returned `IMPLEMENTER_RESULT`: attach it as `implementer-result` evidence with field name `status`, whose value is copied verbatim from the result's own `Return status` field and must be lowercase (`complete`, never `COMPLETE`/`Complete`) — `gN-implement.c1`'s artifact match is exact dict equality, so any other shape or case leaves the gate permanently unsatisfiable.

**`gN-review`** — Fill `templates/REVIEWER_HANDOFF.template.md` from the gate plan and `IMPLEMENTER_RESULT`, naming the original objective, scope, criteria and selected evidence. The Reviewer owns the complete independent review; suspected defects are leads with evidence, not a prescribed verdict or repair. For re-review, include the latest review result (the finding index), the implementation repair responses and the exact changed revision/diff. Dispatch the Reviewer and attach its returned `REVIEW_RESULT`.

**`gN-integrate`** — Check delivery and disposition: required result files exist and are fresh for this attempt (`scripts/run_crew.py --verify-result`); the referenced evidence is accessible; scope, reviewed revision/diff and finding index identify this gate and current work; and the required Reviewer verdict is present. `APPROVE`: advance only when the engine postconditions pass. Missing, stale or contradictory technical evidence goes back to the Reviewer; do not resolve it by re-reviewing or rerunning the crew's analysis yourself. `BLOCK`: route the finding IDs, latest review index and repair criteria to the Implementer, preserving the objective and authority; the Implementer chooses the repair. A disputed finding returns with counterevidence to the Reviewer. Route unresolved scope/authority questions to your principal. Log out-of-scope observations as triage candidates and harvest Workflow Feedback.

**Engine checks and technical verification.** Engine `command` postconditions still execute on `advance`; this role allocation does not waive or replace them. Their failure is a routing signal for the responsible crew. The Reviewer independently verifies technical claims; the Commander checks the delivery/evidence bindings and its own coordination claims. Do not add a duplicate manual technical verification pass at integration. The shared unchanged-tree shortcut governs any redundant manual re-verification by its responsible role, never engine execution.

**Idle crew at `gN-integrate`.** Recover the authored result through the registry and artifact path even when its announcement is missing. A required result or verdict that is absent is incomplete delivery: resume or return it to its author, never infer APPROVE from code, tests or silence. Apply the liveness and refresh rules in `references/global-orchestrator.md` without taking over the crew's work. A refresh relaunches a fresh agent into the same job file; for a Reviewer survey, inspect its pending `refresh-request` evidence because the gated-only `current` display does not show it.

**Crew gate vs reasoning gate.** A crew gate produces an independently verified change, including substantive documentation, and dispatches its implementation and review. A reasoning gate in the Commander's context is limited to coordination: recording a principal's decision, sequencing assignments, routing evidence or summarizing returned work. Technical design, diagnosis and investigation go to a focused crew or existing specialist handoff, even when the Commander already holds relevant context. Coordination gates use their declared attestation or decision artifact; they cannot substitute for a required technical review.

**Doc-only gates: preserve intent and evidence ownership.** Carry the principal's meaning-preservation requirements, allowed scope and required evidence into the assignment. The Implementer chooses the editing and inspection method; the Reviewer independently checks meaning and any required signatures against selected source evidence. A structural test alone does not establish meaning preservation. The Commander checks that the required review/evidence was delivered and routes gaps, rather than authoring a second technical check suite.

Closeout checks (the `gN-integrate` tests-pass command, etc.) are engine **postconditions**: `advance` runs them and refuses if any fails. If your principal decides a specific check is non-blocking, do not hand-edit the checklist to mark it satisfied — use the engine's waive path -- the `spine_evidence` tool with `action=waive`, `task_id=gN-integrate`, `condition_id=<id>`, `which=postconditions`, `authority=human`, `reason="..."` --, which records who accepted the risk and why. A check is only waivable if its `override_policy` allows it; overriding that requires the high-friction `--force` and is recorded as forced.

Pick subagent model tier from gate complexity, scope, ambiguity, and risk. Wait for each subagent to return before advancing. Do not abandon, duplicate, or re-dispatch a task still in progress.

**Crew dispatch mechanics** — the `run_crew.py` wrapper, the CLI-vs-Agent-tool backends, and crew recovery — live in `references/crew-dispatch.md`. Read it before dispatching a crew.

### Return execution evidence for replanning

Execution discrepancies are evidence before they are issues. As gates close,
record completed outcomes, observed-vs-expected `wave_evidence`, and each
discrepancy in the exact sibling template's fields and write the packet to
`.agent-work/<work-id>/REPLAN_INPUT.json`. Classify every signal as
`blocks_current_wave_exit`, `invalidates_forecast_or_decomposition`,
`later_only`, `evidence_only`, or `drop`; include its evidence and reason, and
do not file a discrepancy automatically. Return the verified packet to the
Admiral.

**Which template.** A run that is reshaping an epic's wave plan fills
`../constellation-replan/templates/REPLAN_INPUT.template.json`, which carries
that plan and partitions its current-wave issue ids across completed and open.
A single bounded issue under a frozen Admiral launch order fills
`../constellation-replan/templates/RUN_EVIDENCE.template.json` instead — the
three evidence field-sets and nothing else. That run has no wave, no forecast
and no uncertainty register because nothing in it produced any, and filling
those fields anyway would mean authoring a plausible-sounding artifact standing
in for structure nobody decided (#594). Report what you observed; where there
is nothing, the list is empty. The verifier picks its check from the packet —
`current_plan` present means the full shape — so the two are never confused,
and every shared field is checked by exactly the same clauses either way. Issue creation, when a disposition warrants it, remains behind the
normal authority, triage, independent-review, and tracker-port gates.

The execute gate runs
`python <commander-skill-dir>/scripts/verify_iterative_role_artifacts.py commander --work-id <work-id>`.
Missing or malformed run packets refuse execute completion; prose or an unrelated
checked-in fixture cannot satisfy this command postcondition.

## Repo (default; Charter overrides)

Work on a branch off main; commit frequently as gates close; ready the branch to merge back during clean-up. The work area under `.agent-work/<work-id>/` is preserved through the run, then archived. The approach baseline is inherited global doctrine (`references/global-orchestrator.md` + `references/global-everyone.md`); project-specific deltas come from `ORCHESTRATOR_CONTEXT` when present.

## Human checkpoints (rigor dial)

Pause for a `user-decision` at the checkpoints the project enables at Charter time — typically plan-approved, architecture-change intent, and final accept. Human verification is a first-class step.

## Modes: interactive and delegated

The spine is identical in both modes; only who your principal is, and how the five `user-decision` checkpoints are satisfied, differ. The binding — a live human you ask and wait for, or a frozen launch order you cite and proceed under — is stated in the entry skill you loaded (`constellation-commander` or `constellation-commander-delegated`). This section carries only the shared mechanics.

**Delegated runs** (driven from an Admiral `LAUNCH_ORDER`, no reachable human):

- **`understand`.** Reconcile the ask against the frozen launch order (Mission, Pre-Rulings, Inherited Context, Inherited Latitude) as the source of truth rather than interrogating a human. The loaded Interrogator carries its own delegated reading (see `constellation-interrogator`). **Reconcile the order's *assumed baseline* against the actual code before planning:** a headline mechanism the order treats as unimplemented may already be shipped, and the genuine in-scope gap is often a refinement named only in the pre-rulings — declaring the whole issue already-done off the order's framing risks missing the real defect.
- **The five `user-decision` checkpoints** (`understand`, `plan`, `triage`, `review`, `archive`) are satisfied by **attaching a `user-decision` evidence item that cites the governing launch-order section** — via the `spine_evidence` MCP tool (`action=attach`, `task_id=<step>`, `evidence_type=user-decision`, `fields={cite: "LAUNCH_ORDER:<section>"}`), since this is the Commander's own bound spine and needs no session id argument — with the Admiral as ratifying authority and the human ratifying at the epic return boundary. The engine only requires the `user-decision` artifact to be present; the citation rides in the payload for audit. At `triage`, when a candidate lands as `recommend-and-defer`, the citation records the deferral itself — not a filing approval, since none was sought or authorized this run. `archive` is the fifth, added by issue #634's bookend-freeze follow-up: `understand` through `review` all sit in the mutable middle, where `amend` can drop or rescope a gate, so a run's only human-acceptance evidence living solely at `review` could be planned away before closeout. `archive` is a frozen bookend `amend` can never touch, so its own `user-decision` (citing `LAUNCH_ORDER:Return Shape`, the same section `review` cites) is the one acceptance gate no plan revision can strip. It is a genuinely separate attach, not a re-read of `review`'s evidence — the engine's `artifact` check only sees evidence attached to the current task.
- **This is not a licence to guess.** When the launch order leaves a genuine gap, take it **up to the Admiral** — **float a decision** that exceeds your inherited latitude, or **query the Admiral for context** you lack (a clarification, an epic-level fact, a read on intent the pre-rulings do not settle). Surface the specific need in your return/stop shape; the Admiral answers and continues you. This is inherited delegate-not-replacement doctrine — see `references/global-everyone.md`. Commander-specific: the tier you reach up to is the **Admiral**, and you float via your return/stop shape rather than a live channel.
- **A trip is a different shape than a query.** A query round-trip keeps you the same agent — the Admiral answers and *you* continue. If instead your own spine trips (soft-accepted or hard-forced, `global-everyone.md` §reach-up), you write a `refresh-request` into `spine.json` and go idle; the Admiral relaunches a **fresh** Commander cold-starting from your spine's `current` alone — same job file, different agent (job-file-not-agent-file).

**Interactive runs** (a human at the keyboard) are unchanged: pause for the `user-decision` and ask the human directly.

## Decision candidates

Surface a decision candidate the moment a choice would govern current structure, capabilities, constraints, or future planning behavior — i.e. when an agent could later rediscover or violate it. Force such choices to your principal as a `user-decision`; do not bury them. Record the resolution as a candidate for the reconcile step, where Cartographer decides whether it becomes a durable decision anchor. Decision pressure or evidence returned by Implementer/Reviewer feeds the same candidate pool. Do not raise candidates for choices obvious from current structure.

A candidate that resolves into a recorded decision carries a fixedness tier — the `@grade:` tag, welded to the decision's own line. The tier is what tells a downstream gate whether a reality-contradiction is theirs to revise in place or must come back to you as a new candidate, so grade anchors as you record them rather than leaving every decision reading as equally settled. The grammar, the tier-to-action mapping, and the weld rule live in `references/global-everyone.md`, "Decision fixedness" (lint them with `scripts/grade_lint.py`).

## Mission frame

Plan **map-first**. Before authoring `execute.json`, produce a **mission frame** from the current map (`templates/MISSION_FRAME.template.md`): intent; affected capabilities; relevant examples/events; structural anchors; governing constraints/assumptions; decision anchors and decision pressure; claims/evidence surfaces; map confidence/staleness/disputes; out of scope. The frame is how the durable map feeds planning before any code spelunking, and the source the gate anchors are cut from.

The map is context, not authority over code, and not a tax on trivial work. For a small local/mechanical change where the map adds nothing, shrink or skip the frame and say so in its intent. When relevant architecture artifacts exist, the frame is required.

Before the plan-approved checkpoint the plan step runs two principal-governed rigor mechanisms, and their order is load-bearing: frame, then candidates, then convergence, then critic, then `execute.json`.

**Plan-alternatives** comes first — parallel gate-plan candidates under distinct constraints converging to one recommendation, per the shared design-it-twice standard in `references/global-orchestrator.md` and the `references/design-it-twice-brief.md` contract. The candidates are authored as candidate plans, and `execute.json` is authored once, from the winner. Authoring `execute.json` first and commissioning rivals to it afterwards inverts the mechanism: candidates generated against an incumbent you are already attached to argue for it instead of competing with it, which is the bias design-it-twice exists to defeat.

Three paths are fixed so this step's artifacts survive a relaunch and can later be checked for order: each candidate at `.agent-work/<work-id>/plan-candidate-<constraint>.md` (the constraints are distinct by contract, so they key the files), the filled brief — comparison, recommendation, untaken roads, panel-vs-single record — at `.agent-work/<work-id>/PLAN_ALTERNATIVES.md`, and the critic's findings at `.agent-work/<work-id>/PLAN_CRITIC.md`. Explorer folds its critic's findings back into `DESIGN_SPEC.md` because that spec already exists when the critic runs; here it cannot, since `execute.json` is deliberately not authored yet — hence the critic's own file. Nothing reads these three paths yet. They are named now because an unnamed artifact cannot be recovered after a relaunch and cannot be ordered against `execute.json` by any future check, which is why `c4` and `c5` still say plainly that they are attested rather than verified.

Then the **cold plan critic** — an adversarial read of the converged candidate plan and mission frame by a critic with no authoring context, panel scaled by weight as a surfaced choice, findings triaged by your principal, per the shared critical-spec-review standard.

Both are **bias-to-yes**, and any skip is surfaced as a named untaken road at the approval checkpoint. Both point at doctrine — the rules live there, not here.

Any background subagent you dispatch — plan-alternative authors, critics, or crews — is instructed **in its spawn prompt** to write its result to the job/gate-addressed path (a crew gate's is `.agent-work/<work-id>/crew-handoffs/<gate>-<role>-result.md`; a plan-alternative author's is `.agent-work/<work-id>/plan-candidate-<constraint>.md` and a plan critic's is `.agent-work/<work-id>/PLAN_CRITIC.md`; any other reasoning-gate dispatch names the equivalent stable artifact path) **before ending its turn** — that write is the delivery. It is already required (`run_crew.py`'s `--result` contract) and it is what actually survives a dispatcher relaunch, because the path is stable across every relaunch while an agent instance name is not: a handoff naming a live successor instance can no longer resolve to it once the Commander relaunches again, and lookup then lands on the retired origin of the lineage rather than the current head (#507) — a harness-level quirk, noted here, not fixed by this doctrine. Tell it to also `SendMessage` on completion, but **as a best-effort, non-load-bearing courtesy ping**, never the thing you wait on: the instance that receives it may no longer be live (relaunch), and a spawned subagent has no addressable name to its own children at all (#413), so the ping can fail to arrive even when the result is complete. A missing ping is not a missing result — a resumed or relaunched Commander checks the result artifact / `recover_crews.py`'s classification (`references/crew-dispatch.md`) before assuming a crew must be (re)dispatched, rather than treating dispatcher-side silence as non-delivery.

Low-confidence, stale, partial, or disputed map areas **alter the plan** — never trust them silently. Flag the area in the frame and either plan a scout/verification step into `execute.json` or surface it to your principal as a decision; do not author gates that assume an unverified map.

Before advancing past `plan`, confirm `execute.json` actually contains one gate for **every** file and decision-class in the issue's stated file-ownership scope. A handoff or gate imperative that merely *references* a decision as "handled in a separate gate" is not a substitute for that gate existing in `execute.json` — the missing gate surfaces only at review and forces a reopen. Enumerate the ownership scope against the authored gates before freezing the plan.

Each gate **inherits** the relevant frame anchors: the per-gate `anchors` block in `execute.json` carries the structural/capability/constraint/decision/evidence anchors down, and the inbound handoff templates relay them to Implementer and Reviewer so every role plans from the same map context. That relay includes the **map entry point**: every crew handoff names the specific map file(s) where that crew starts — you did the map work at frame time, so hand it down rather than making the crew re-derive it.

What the map answers at this tier, concretely. **Blast radius:** before bounding a gate or fencing a multi-issue wave, pull the map entries for the symbols in scope and read what references them — overlapping radii belong in one gate, and fence lines land where a radius ends. **Recorded failures:** when the frame touches a concept with rejected alternatives or tombstoned approaches, surface them in the handoff so no crew re-proposes a documented dead end. **Holes:** map holes inside the run's scope are cheap adjacent work — fold them in or file them, never silently skip them. And push entry points, never overview prose: pasted map summaries measurably add cost without improving navigation.

Sequence gates so verification stays green at every gate boundary. When the plan creates a new artifact family whose validity a discovery/CI/test layer enforces (e.g. a new `skills/<name>/` directory an installer refuses without its `SKILL.md`), the first gate touching that family ships the minimal validity-establishing artifact — a stub is fine — rather than planning a known-red window bridged by waivers. A deliberately red suite across gates is a plan smell: it costs a human waiver per gate plus a diagnostic detour in every review to prove the red is benign.

## Architecture bookend

Architecture is read at the **start** — that read produces the mission frame above — and reconciled at the **end** (capture changes for the next effort). Between, it is frozen read-only context; a mid-run structural surprise bubbles up as a signal, never a map edit.

Reconciling at the end dispatches Cartographer whenever a packet map exists — that is the default path. Where the run has no packet map (e.g. a skill-source repo with no `docs/architecture` map), route any schema/design reconciliation to the responsible crew and integrate its evidence; if neither is touched, record the crew's reasoned no-op rather than blocking on an absent map.

## Templates

`templates/COMMANDER_SPINE.template.json`, `templates/EXECUTE_PLAN.template.json`, `templates/MISSION_FRAME.template.md`, `templates/IMPLEMENTER_HANDOFF.template.md`, `templates/REVIEWER_HANDOFF.template.md`. Engine: `references/checklist-engine.md`. Crew dispatch: `references/crew-dispatch.md`.
