# Crash-resume state note — commander-315-native

**The run is BLOCKED on an Admiral ruling, not on context and not on a crash.** The lease is left
**HELD** under session id `commander-315-native`. A same-id re-claim is idempotent.

- **step:** `execute` → **blocked** (bubbled from `execute.json` gate `g1-implement`, also blocked)
- **slug:** commander-315-native · branch `epic-568/c2-native-isolation` · worktree `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`
- **next command:** `cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native && py /home/tommy/projects/constellation-skills/scripts/checklist_engine.py --file .agent-work/commander-315-native/spine.json current`
- **pid:** none — both crews resolved COMPLETE, nothing is running
- **expected artifact:** `.agent-work/commander-315-native/COMMANDER_RESULT.md` — **written**

## What is done

- Implemented and committed: `a04d7828` (the change), `ed25bf8f` (review records and the block).
- **PR #577** open against `main`, **not merged**: https://github.com/fredcai6/constellation-skills/pull/577
- Independent reviewer: **APPROVE** on integrity (jobs 1-7), **NOT READY** to merge.
- Suite at `ed25bf8f`: 2959 passed, 6 skipped, **1 failed**. Failure-set difference against `main`'s
  0-failed Linux baseline is exactly `{tests/test_mcp_lifecycle.py}`.
- Triage candidates `tc6`-`tc12` filed on the spine. `REPLAN_INPUT.json` passes the G2 check.

## What blocks it — needs the Admiral, not another implementer

`spine_open` creates a **new** worktree and stamps `origin.worktree` to it; the next verb on that
spine is `claim`, issued in-process through `scripts/mcp_spine_server.py:361`, which never chdirs.
The door's process cannot already stand inside a directory that did not exist a moment earlier, so
**`spine_open` → `claim` in one session is now impossible through the door, by construction.**

Rejected on measurement, not preference: adjusting the verb scope (the round trip drives `start`,
`attach`, `advance` — all in `MUTATING_VERBS`); and having the door supply `SPINE.parent`'s
toplevel as the measured side (measured **equal** to the stamped `origin.worktree` by construction
— the `X == X` tautology this issue exists to avoid).

Every remaining fix changes **who sets cwd**, in `scripts/run_crew.py` or
`scripts/mcp_spine_server.py` — both outside allowed scope, both production behaviour.

**The Commander's own launch-order reason #1 was FALSE:** `run_crew.launch_process`
(`scripts/run_crew.py:676`) passes no `cwd=`, so a dispatched crew inherits the *dispatcher's* cwd,
not its spine's worktree. Verified three times independently.

## Do NOT

- Do **not** re-run the implementer. The slice is complete except the blocked item; it needs a
  ruling, not a re-implementation.
- Do **not** merge PR #577.
- Do **not** enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`.

## Read first

`.agent-work/commander-315-native/COMMANDER_RESULT.md` — the full account, including the three
options for the Admiral and the Commander's recommendation (option 1 **plus** option 2).

_Updated: 2026-08-13T06:22:00Z_
