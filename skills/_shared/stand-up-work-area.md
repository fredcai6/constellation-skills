# Standing up a worktree and work area (shared reference)

The single instruction set for provisioning a Commander's worktree and `.agent-work` directory before any spine work begins. **Two callers run this, not two versions of it:** the Admiral, provisioning a worktree it will hand to a *delegated* Commander via a launch order; and a human running an *interactive* Commander, standing up their own work area before loading the skill. Same instructions, different hands — issue #610. Wire new callers to this file rather than restating it.

## What "standing up a work area" means

Four steps, in order, performed once per bounded issue, by whoever is dispatching the Commander (never by the Commander itself — see "Why the Commander doesn't do this" below):

1. **Provision the worktree.** `git worktree add <path> -b <branch> <base>` from the main checkout. Verify main freshness before branching. Log the exact command and its outcome — a provisioned worktree is a material action, not a side effect.
2. **Scaffold `.agent-work`.** Create `.agent-work/<work-id>/` inside the new worktree for the spine, checklists, and run artifacts the Commander will produce.
3. **Instantiate `spine.json`.** Resolve `templates/COMMANDER_SPINE.template.json`'s placeholders (via `scripts/init_work_area.py --spine <template> --skill-dir <commander-skill-dir>`) into a real spine at `.agent-work/<work-id>/spine.json`, sitting at its `init` step.
4. **Hand off the spine path.** Give the Commander the absolute path to the spine you just created — in a delegated run, that's the launch order's `## Workspace` field; in an interactive run, it's just where the human tells the Commander to look. The Commander's own first act is no longer to build this — it is to `claim` the engine lease on the spine you handed it.

## Why the Commander doesn't do this

Before #610, `COMMANDER_SPINE.template.json`'s `init` step told the Commander to run `init_work_area.py` on itself — the dispatched process scaffolding the work area it might already be standing in. That collapsed two separate concerns (*who proves the worktree is real and isolated* vs. *who does the work in it*) into one actor, and left every entry skill (`commander`, `commander-delegated`) carrying its own copy of the recipe to keep in sync.

Provisioning is now uniformly the **dispatcher's** job. The Commander's `init` step means exactly one thing: claim the checklist lease on the spine it was handed, so a resumed or duplicated parent can't concurrently drive it. It does not scaffold, and it does not need to — by the time it loads, the worktree, `.agent-work` directory, and spine already exist.

## What this does not replace

**Isolation verification stays where it is.** `verify_worktree_isolation.py`'s gate-mode — the Admiral's pre-wave check across every worktree it just provisioned (`scripts/verify_worktree_isolation.py <path1> <path2> ...`) — is a separate concern from stand-up and is untouched by this doc. It proves the worktree is real, registered, and distinct; it does not create anything. See `references/fleet-doctrine.md` for that mechanism.

The Commander's own `--here` arrival check (`verify_worktree_isolation.py --here <path>`, run as its first step before this issue) is retired as an instruction, not as a script — the check it ran for (a scaffolding step that could land in the wrong directory) no longer exists once the Commander never scaffolds. The script itself is untouched and still available if a future caller needs it.

## Failure mode this fixes

A recipe duplicated across `LAUNCH_ORDER.template.md`, `fleet-doctrine.md`, `COMMANDER_SPINE.template.json`, and every entry skill's own prose drifts: one copy gets fixed, the others don't, and an agent following the stale one ships a contradiction (an instruction to run a script that a sibling doc just retired). Citing this file instead of restating it is the fix — one place to update, every caller current by reference.
