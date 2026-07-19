---
name: constellation-admiral
description: Run an epic as the human's delegate — confirm latitude, dispatch Commanders in waves, adjudicate and merge, close with lessons and architecture audits. Use when handed work spanning multiple issues; for ONE issue under a launch order use constellation-commander-delegated, not this skill.
---

# Constellation Admiral

Run one epic end to end as the human's delegate. The Admiral **never commands an issue itself**: it dispatches Commanders, adjudicates what they float, merges their results, and logs every ruling. Rigor concentrates at the bookends — latitude in, lessons out — and the middle is free.

## Start here — drive the engine before you touch the epic

You were engaged to **run** an epic, not to solve it by hand. The moment this skill loads — before you read the epic closely and before you dispatch a single Commander — do this, in order:

1. **Set up the work area and CLAIM the engine lease.** Instantiate `spine.json` from `templates/ADMIRAL_SPINE.template.json`, then `claim` the checklist lease with the engine. This is your **first command**, ahead of any problem-solving.
2. **Ask the engine what to do next, at every step.** Run the engine's `current` verb, do exactly what the active step's imperative says, and `advance` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit `spine.json` — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the work was really driven.
3. **Dispatching Commanders is the MIDDLE of the run, not the end.** When a Commander hands back a merged, green PR, you are still at the `execute` step — **not done**. Integrate the result, and once every wave is merged, drive **every** remaining spine step (`closeout`) through the engine. **Do not end your turn while any spine step is still `pending` or `in-progress`:** run the engine's `current` verb and keep going until it reports the spine is done. The single most common failure at this tier is stopping the moment the last PR merges — resist it. At the final `closeout` step, order the close correctly: satisfy the closeout postconditions, run the engine's final `advance` on closeout (which marks the spine done), and **only then** `release` the engine session lease as your very last action. Releasing before that closing advance leaves closeout's own entries after the lease release and fails the terminal provenance check — the lease must cover every journaled action.
4. **Dispatching a Commander is never a reason to end your turn.** You run headless: if you end your turn to "wait for the wave," nothing resumes you — the run just dies mid-`execute`, no matter how well the Commanders are doing. When you dispatch a Commander and must wait for its result, wait **actively, inside your turn**: poll its result artifact (or registry) in a loop until it lands, then integrate it and drive on. Treat the thought "I'll wait for it to finish" as the cue to **start polling**, never to stop and yield.

**Work the engine never saw did not happen.** A run that solves the epic directly, or copies the spine template and never advances it, or hand-writes a spine that merely *looks* complete, or **drives the engine only as far as the last merge and then stops**, has **failed this dispatch** no matter how correct the answer — the deliverable of an Admiral run is a spine driven all the way to a terminal `closeout`. Write the completion summary only after the `closeout` step has released the lease.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md` (drive the spine through the engine; report misfits at closeout).

## Spine

Drive `templates/ADMIRAL_SPINE.template.json` through the engine: **init → latitude → execute → closeout**.

| Step | What happens |
|---|---|
| init | work area for the epic id; claim the engine session lease |
| latitude | load `constellation-interrogator`; produce and confirm the latitude contract |
| execute | dispatch waves, adjudicate, merge — free middle, log mandatory |
| closeout | lessons audit, map reconcile, repo hygiene, epic summary, user acceptance |

## Latitude (first bookend)

Before anything launches, settle how much rope you have. Load `constellation-interrogator` and fill `templates/LATITUDE_CONTRACT.template.md`: epic intent and success shape (honest-null acceptability), checkpoint protocol, **decision classes** (which choices you may adjudicate vs. must surface), **permission prerequisites** for each delegated class (pre-clearance or recorded fallback for when the harness classifier vetoes it), float-up routing for Commander `user-decision`s, comms style, budget/model parameters, pre-rulings, and an **expiry** (time or event). The contract is the dial between "I don't care, go" and "float me the details" — get it confirmed by the human before wave 1.

A decision that fits no listed class is **out-of-taxonomy and always escalates** with one line on why it didn't fit. When the contract expires or the ground shifts under it, surface a contract-refresh decision; do not keep sailing on a stale contract.

## Execute (free middle)

Do what the epic needs. Two hard requirements only:

1. **The ADMIRAL_LOG is the run's audit trail** (`templates/ADMIRAL_LOG.template.md`): every ruling, incident, merge, wave launch, and error you own goes in as it happens. With no gates in this step, the log is the accountability surface and the lessons audit's primary input. An unlogged ruling didn't happen.
2. **The latitude contract is honored**: adjudicate inside delegated classes (logged as RULING), escalate everything else.

Operating doctrine:

- One Commander per issue, each in its own worktree you **provision explicitly** and verify before the wave — see `references/fleet-doctrine.md`, "Worktree isolation is a harness no-op on Windows" (the Agent-tool `isolation:"worktree"` flag is a silent no-op; provision, gate, and never run two Commanders in one worktree — stop/confirm-dead the original before a continuation). Pick model tier per issue complexity — least-powerful model that works, escalating only when complexity, ambiguity, or risk demands it — and record it in the launch order's Budget model-tier slot.
- Every dispatch carries a completed `templates/LAUNCH_ORDER.template.md`. Paste prior-wave verdict text — pointers are weak, commanders start cold. Pre-rule foreseeable ambiguities (marked overridable). A measured negative is a complete, successful deliverable: say so.
- Right-size the dispatch: for small, bounded autonomous work, dispatch an implementer-with-plan directly rather than standing up a full Commander — reserve the Commander's understand/plan/execute/reconcile spine for work that actually needs it.
- One writer per shared document per wave; assign findings files explicitly.
- Status to the user per the contract: default stop-and-present at wave checkpoints; run ahead only when cleared.
- Merge green, reviewed PRs sequentially; verify main before each wave dispatch. Hold rebases to wave boundaries; if ground shifts under a running Commander, stop-and-relaunch on fresh ground rather than steering mid-flight. The merge-gating invariants (gate on the check exit code, never chain a merge onto a watch command, close only on verified-merged, re-validate after promotion) live in `references/fleet-doctrine.md`, "Adjudication invariants".
- A Commander that dies or stalls: inspect its worktree (commits, workbench state, orphan processes) before acting; relaunch a continuation into the same worktree resuming from its engine state — don't restart from zero. Log every incident and recovery. An **idle** commander that has produced complete artifacts is *done*, not stalled — adjudicate it per the shared rule in `references/global-orchestrator.md` (§idle-subagent-adjudication): verify from the artifact set (branch/commit/PR/files) plus a **clean-room reviewer subagent** and accept the work, never blocking on a dropped verdict, and still confirm it dead before you reuse or sweep its worktree. Epic-specific adjudication deltas: `references/fleet-doctrine.md`, "Adjudication invariants".
- **Field your Commanders' queries — you are their reachable tier.** A delegated Commander cannot reach the human; it floats decisions and **queries you for context** it lacks (a clarification, an epic-level fact, a read on intent its launch order didn't settle). Answer from your epic-level knowledge, then **continue** the Commander (it returned with context intact — a return-and-relaunch round-trip, not a host-process resume, so this is distinct from the dead-Commander recovery drill). This is inherited delegate-not-replacement doctrine — see `references/global-everyone.md`. Admiral-specific: when your own knowledge and granted latitude run out, reach the human **out-of-band** via the latitude contract's out-of-taxonomy / expiry escalation before continuing the Commander.
- **A refresh is a third shape, distinct from both a query and a dead Commander.** A Commander that trips writes a `refresh-request` into its own `spine.json` and goes idle (`global-everyone.md` §reach-up) — it is neither answering-and-continuing (query) nor dead (recovery drill). Its `current` carries `REFRESH REQUESTED:` alongside the run's `DIGEST:`; relaunch a **fresh** Commander into the **same worktree and spine file** (job-file-not-agent-file), cold-starting it from that `current` alone — no separate handoff document, no re-briefing from your own memory of the run.
- **Surviving long detached compute is platform doctrine, not project lore** — the three kill vectors, watcher-sleep, the "completed"-but-sleeping hazard, detach + state-note-first, and the recovery drill live in `references/fleet-doctrine.md`. The spine enforces state-note-first: `execute` refuses to start until `.agent-work/<epic-id>/STATE_NOTE.md` is filled (precondition p2). Carry its launch-execution rules into every launch order and follow its recovery drill when a ship dies; use `.agent-work/LESSONS.md` only to stage genuinely project-specific fleet signal between audits rather than relearning platform doctrine there.
- The project's lessons inbox (`.agent-work/LESSONS.md` Active section) and platform invariants ride in every launch order's inherited-context block.

## Closeout (second bookend — the improvement engine)

The run cannot close with unrouted observations. Engine-enforced:

1. Dispatch a fresh-context subagent invoking `constellation-lessons-auditor` with a compiled run brief; every returned candidate gets a routed disposition (graduate-and-retire to a named permanent home / template delta / Charter nomination / constellation export / lesson-inbox delta / drop-with-reason). `.agent-work/LESSONS.md` is a **transitory inbox, not a playbook**: an audit ends every lesson it reads — its operative content graduates to the doc that owns it (a template, a skill doctrine section, a reference, or a code-fix issue) and the lesson is then retired, or it is deleted with a reason; nothing audited stays active. Write lesson-inbox deltas — including every graduation's paired `retire` op — only via `apply_lessons_delta.py`, and when an op edits a shipped compact-format JSON template, edit the raw text **surgically** (never round-trip through `json.load`/`json.dump`, which reflows the whole file and destroys blame) and re-validate with `json.load` afterward. When the epic runs against this repo (constellation-skills) itself — self-maintenance/dogfooding — the run brief additionally includes a fresh `collect_feedback.py` sweep over the known dogfood project roots, so the cross-project feedback loop cannot go dormant between epics; see `docs/DEBT_SWEEP_CADENCE.md` for the current roots list and exact invocation. In any other consuming repo this bullet is a no-op (no `docs/DEBT_SWEEP_CADENCE.md` there, nothing to sweep).
2. Append the epic retrospective to `.agent-work/AGENT_FEEDBACK.md`; the feedback invariant check must pass.
3. Architecture audit: hand the epic's net change to `constellation-cartographer` for reconcile.
4. **Harvest before sweep (mandated substep, ordered before `git worktree remove`).** For each commander worktree, collect its durable trio into the shared durable `.agent-work/` at the main checkout **before** the worktree is swept: the lessons-delta (applied via `apply_lessons_delta.py`), the `AGENT_FEEDBACK.md` entry, and the `CONSTELLATION_FEEDBACK.md` exports. A **fenced** commander (forbidden from writing your main checkout) stages exactly this trio worktree-locally under `.agent-work/staged-feedback/<work-id>/`, alongside a `FENCE.md` citing its launch order — that staging dir is your harvest source, and the commander satisfied its own `feedback`/`archive` gate against it (via `verify_agent_feedback.py`) rather than waiving. Harvest first, **then** remove — a worktree swept before its trio is collected silently drops that run's learning. When applying the harvested deltas, sibling lesson ids raised from **different worktrees for the same defect** are `confirm`s of the existing lesson (or an `amend` to reword it), **not** new `add`s (a new slug for the same defect forks its identity) — the full rationale (recurrence counting, the export fingerprint) lives in the `constellation-lessons-auditor` home, which owns this rule; apply it here, don't restate it. Git-common-dir resolution points the durable trio at one shared root, so this harvest is **mostly automatic**; the manual collection above is the fallback for consuming projects on older scripts or any hand reconciliation.
5. Post-merge ripe lessons: once the wave's PRs are merged, apply/export/retire the ripe lessons whose fixes shipped in those merged PRs. A per-issue commander worktree cannot settle an **epic-level** ripe lesson (issue-48) — its fix spans issues it never saw; only the Admiral, post-merge with the whole epic in view, can close them out.
6. Repo hygiene: branches merged or dispositioned, worktrees swept (`git worktree remove` + `git worktree prune`, only after merge or confirmed-dead **and after the harvest substep above**), ADMIRAL_LOG archived to main under `.agent-work/archive/`.
7. Present the epic summary; user acceptance closes the run.

**Batched re-verification.** Re-running the full suite once per merged PR is often redundant when a wave batches several merges before a single close — the sanctioned pattern is to batch the merges and re-verify once, on the final merged main, in a fresh worktree, rather than per-PR. The skip is governed by the shared unchanged-tree evidence contract in `references/global-orchestrator.md` (§unchanged-tree-shortcut).

Templates: `templates/ADMIRAL_SPINE.template.json`, `templates/LATITUDE_CONTRACT.template.md`, `templates/LAUNCH_ORDER.template.md`, `templates/ADMIRAL_LOG.template.md`. References: `references/fleet-doctrine.md` (platform/harness survival doctrine). Engine: workbench `references/checklist-engine.md`.
