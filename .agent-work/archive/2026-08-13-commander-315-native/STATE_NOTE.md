# Crash-resume state note — commander-315-native

## Final continuation state — 2026-08-13

- `execute.json` is terminal DONE after fresh independent APPROVE and the MCP-owned full suite:
  2,981 passed, 6 skipped.
- Human-ruled crew/MCP cwd repairs are committed at `48f07123`.
- Commander gates execute, reconcile, triage, review, and feedback are complete; archive is the
  active final gate while this note is committed.
- Seven run episodes were applied through the sole writer and pass feedback capture.
- The work area has moved to `.agent-work/archive/2026-08-13-commander-315-native/`.
- Admiral later confirmed `git push` authority for exactly `epic-568/c2-native-isolation` to update
  existing PR #577. Merge remains unauthorized.
- Final summary: `COMMANDER_FINAL_SUMMARY.md`; triage: `TRIAGE_RECOMMENDATIONS.md`; workflow
  reflection: `WORKFLOW_FEEDBACK.md`.

The pre-ruling recovery detail below is retained as historical context and is superseded where it
describes the run as blocked.

**The Admiral ruled options 1 + 2 and the recovered implementation result is complete.** The lease is
**HELD** under session id `commander-315-native`; the fresh Commander re-claimed it idempotently through
the stdio MCP door after `recover_crews.py` reported no unresolved crew.

- **step:** `execute` · `g1-review` in progress · absolute-cwd repair complete · fresh `g1c-review` next
- **slug:** commander-315-native · branch `epic-568/c2-native-isolation` · worktree `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`
- **next command:** `cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native && python scripts/recover_crews.py commander-315-native && python scripts/run_crew.py --work-id commander-315-native --gate g1c-review --role reviewer --model codex --worktree /home/tommy/projects/constellation-skills-wt/epic-568-315-native --handoff .agent-work/commander-315-native/crew-handoffs/g1c-reviewer-handoff.md --result .agent-work/commander-315-native/crew-handoffs/g1c-reviewer-result.md --parent commander-315-native --root . --backend external`
- **pid:** none — external wrapper records the crew; Codex child is resumed through the collaboration harness if interrupted
- **expected artifact:** `.agent-work/commander-315-native/crew-handoffs/g1b-reviewer-result.md`

## What is done

- Implemented and committed: `a04d7828` (the change), `ed25bf8f` (review records and the block).
- **PR #577** open against `main`, **not merged**: https://github.com/fredcai6/constellation-skills/pull/577
- Independent reviewer: **APPROVE** on integrity (jobs 1-7), **NOT READY** to merge.
- Suite at `ed25bf8f`: 2959 passed, 6 skipped, **1 failed**. Failure-set difference against `main`'s
  0-failed Linux baseline is exactly `{tests/test_mcp_lifecycle.py}`.
- Triage candidates `tc6`-`tc12` filed on the spine. `REPLAN_INPUT.json` passes the G2 check.

## Prior block — ruled and implemented

`spine_open` creates a **new** worktree and stamps `origin.worktree` to it; the next verb on that
spine is `claim`, issued in-process through `scripts/mcp_spine_server.py:361`, which never chdirs.
The door's process cannot already stand inside a directory that did not exist a moment earlier, so
**`spine_open` → `claim` in one session is now impossible through the door, by construction.**

Rejected on measurement, not preference: adjusting the verb scope (the round trip drives `start`,
`attach`, `advance` — all in `MUTATING_VERBS`); and having the door supply `SPINE.parent`'s
toplevel as the measured side (measured **equal** to the stamped `origin.worktree` by construction
— the `X == X` tautology this issue exists to avoid).

Every remaining fix changed **who sets cwd**, in `scripts/run_crew.py` and
`scripts/mcp_spine_server.py`. The human ruled options 1 + 2; the recovered `g1b` implementer result
reports both implemented with an empty failure-set difference. Independent review and Commander
reproduction remain before integration.

**The Commander's own launch-order reason #1 was FALSE:** `run_crew.launch_process`
(`scripts/run_crew.py:676`) passes no `cwd=`, so a dispatched crew inherits the *dispatcher's* cwd,
not its spine's worktree. Verified three times independently.

## Do NOT

- Do **not** re-run the completed `g1b` implementer attempt.
- Do **not** merge PR #577 until the amended gate is independently approved and integrated.
- Do **not** enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`.

## Read first

`.agent-work/commander-315-native/COMMANDER_RESULT.md` — the full account, including the three
options for the Admiral and the Commander's recommendation (option 1 **plus** option 2).

_Updated: 2026-08-13T14:15:00Z_
