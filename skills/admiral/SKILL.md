---
name: constellation-admiral
description: Run an epic as the human's delegate — confirm latitude, dispatch Commanders in waves, adjudicate and merge, close with lessons and architecture audits. Use when handed work spanning multiple issues.
---

# Constellation Admiral

Run one epic end to end as the human's delegate. The Admiral **never commands an issue itself**: it dispatches Commanders, adjudicates what they float, merges their results, and logs every ruling. Rigor concentrates at the bookends — latitude in, lessons out — and the middle is free.

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

Operating doctrine, learned from field fleets:

- One Commander per issue, each in its own worktree you **provision explicitly** with `git worktree add` — the Agent-tool `isolation:"worktree"` flag is a silent no-op on Windows — and verify with `verify_worktree_isolation.py` before the wave; pick model tier per issue complexity — least-powerful model that works, escalating only when complexity, ambiguity, or risk demands it — and record it in the launch order's required Budget model-tier slot. Never two commanders in one worktree — stop/confirm-dead the original before launching a continuation into its worktree. See `references/fleet-doctrine.md`, "Worktree isolation is a harness no-op on Windows".
- Every dispatch carries a completed `templates/LAUNCH_ORDER.template.md`. Paste prior-wave verdict text — pointers are weak, commanders start cold. Pre-rule foreseeable ambiguities (marked overridable). A measured negative is a complete, successful deliverable: say so.
- Right-size the dispatch: for small, bounded autonomous work, dispatch an implementer-with-plan directly rather than standing up a full Commander — reserve the Commander's understand/plan/execute/reconcile spine for work that actually needs it.
- One writer per shared document per wave; assign findings files explicitly.
- Status to the user per the contract: default stop-and-present at wave checkpoints; run ahead only when cleared.
- Merge green, reviewed PRs sequentially; **gate merges on check exit codes, never chain** a merge after a watch command. Verify main before each wave dispatch. Hold rebases to wave boundaries; if ground shifts under a running Commander, stop-and-relaunch on fresh ground rather than steering mid-flight.
- A Commander that dies or stalls: inspect its worktree (commits, workbench state, orphan processes) before acting; relaunch a continuation into the same worktree resuming from its engine state — don't restart from zero. Log every incident and recovery. An **idle** commander (`idle_notification`, `idleReason: available`) that has produced complete artifacts is *done*, not stalled: verify from the artifact set (branch/commit/PR/files) + a clean-room reviewer subagent and accept the work — never block waiting on a verdict message it may have dropped. This judges the verdict, not liveness: still confirm it dead before you reuse or sweep its worktree. See `references/fleet-doctrine.md`, "Adjudication invariants".
- **Field your Commanders' queries — you are their reachable tier.** A delegated Commander cannot reach the human; it floats decisions and **queries you for context** it lacks (a clarification, an epic-level fact, a read on intent its launch order didn't settle). Answer from your epic-level knowledge, then **continue** the Commander (it returned with context intact — a return-and-relaunch round-trip, not a host-process resume, so this is distinct from the dead-Commander recovery drill). A delegate is not a replacement: when your own knowledge and granted latitude run out, **"I need to talk to my human" is a first-class move, not a failure** — reach the human out-of-band (the latitude contract's out-of-taxonomy / expiry escalation provides for exactly this) before continuing the Commander.
- **Surviving long detached compute is platform doctrine, not project lore** — the three kill vectors, watcher-sleep, the "completed"-but-sleeping hazard, detach + state-note-first, and the recovery drill live in `references/fleet-doctrine.md`. State-note-first is now engine-enforced — the spine refuses to start `execute` until `.agent-work/<epic-id>/STATE_NOTE.md` is filled (precondition p2). Carry its launch-execution rules into every launch order and follow its recovery drill when a ship dies; keep `.agent-work/LESSONS.md` for genuinely project-specific fleet rules rather than relearning the platform doctrine there.
- The project's playbook (`.agent-work/LESSONS.md` Active section) and platform invariants ride in every launch order's inherited-context block.

## Closeout (second bookend — the improvement engine)

The run cannot close with unrouted observations. Engine-enforced:

1. Dispatch a fresh-context subagent invoking `constellation-lessons-auditor` with a compiled run brief; every returned candidate gets a routed disposition (template delta / playbook delta / Charter nomination / constellation export / retire / drop-with-reason). Apply playbook deltas only via `apply_lessons_delta.py`. When the epic runs against this repo (constellation-skills) itself — self-maintenance/dogfooding — the run brief additionally includes a fresh `collect_feedback.py` sweep over the known dogfood project roots, so the cross-project feedback loop cannot go dormant between epics; see `docs/DEBT_SWEEP_CADENCE.md` for the current roots list and exact invocation. In any other consuming repo this bullet is a no-op (no `docs/DEBT_SWEEP_CADENCE.md` there, nothing to sweep).
2. Append the epic retrospective to `.agent-work/AGENT_FEEDBACK.md`; the feedback invariant check must pass.
3. Architecture audit: hand the epic's net change to `constellation-cartographer` for reconcile.
4. **Harvest before sweep (mandated substep, ordered before `git worktree remove`).** For each commander worktree, collect its durable trio into the shared durable `.agent-work/` at the main checkout **before** the worktree is swept: the lessons-delta (applied via `apply_lessons_delta.py`), the `AGENT_FEEDBACK.md` entry, and the `CONSTELLATION_FEEDBACK.md` exports. Harvest first, **then** remove — a worktree swept before its trio is collected silently drops that run's learning. When applying the harvested deltas, sibling lesson ids raised from **different worktrees for the same defect** are `confirm`s of the existing lesson (or an `amend` to reword it), **not** new `add`s — a new slug for the same defect forks its identity and breaks recurrence counting. g1's git-common-dir resolution now points the durable trio at one shared root, so this harvest is **mostly automatic**; the manual collection above is the fallback for consuming projects on older scripts (or any hand reconciliation).
5. Post-merge ripe lessons: once the wave's PRs are merged, apply/export/retire the ripe lessons whose fixes shipped in those merged PRs. A per-issue commander worktree cannot settle an **epic-level** ripe lesson (issue-48) — its fix spans issues it never saw; only the Admiral, post-merge with the whole epic in view, can close them out.
6. Repo hygiene: branches merged or dispositioned, worktrees swept (`git worktree remove` + `git worktree prune`, only after merge or confirmed-dead **and after the harvest substep above**), ADMIRAL_LOG archived to main under `.agent-work/archive/`.
7. Present the epic summary; user acceptance closes the run.

**Unchanged-tree shortcut.** Re-running the full suite once per merged PR is often redundant when a wave batches several merges before a single close — the sanctioned pattern is to batch the merges and re-verify once, on the final merged main, in a fresh worktree, rather than per-PR. The shortcut only substitutes for a redundant re-run when its evidence contract holds: `git rev-parse HEAD` matches the hash recorded with the last green run, AND `git status --porcelain` is empty, AND the prior green output is pasted alongside the matched hash. Any tree change — a different HEAD or a dirty tree — voids the shortcut and forces a fresh run; this is doctrine and evidence shape only, no engine or script change.

Templates: `templates/ADMIRAL_SPINE.template.json`, `templates/LATITUDE_CONTRACT.template.md`, `templates/LAUNCH_ORDER.template.md`, `templates/ADMIRAL_LOG.template.md`. References: `references/fleet-doctrine.md` (platform/harness survival doctrine). Engine: workbench `references/checklist-engine.md`.
