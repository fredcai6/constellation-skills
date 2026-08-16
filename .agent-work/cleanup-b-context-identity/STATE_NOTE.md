# Crash-resume state note — cleanup-b-context-identity

- **step:** execute · gate g1-implement (dispatching the implementer crew) · leg 2
- **slug:** cleanup-b-context-identity · branch `cleanup/b-context-identity` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
- **next command:** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py /home/tommy/.claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/cleanup-b-context-identity/execute.json current` — then, if no crew is running, `py /home/tommy/.claude/skills/constellation-commander/scripts/recover_crews.py cleanup-b-context-identity` before any relaunch
- **pid:** g1 implementer crew RUNNING, pid `3094608`, registry id `None`; stdout at `.agent-work/cleanup-b-context-identity/crew-runs/g1-implementer-attempt-1.stdout.txt`. Do not relaunch it — run `recover_crews.py cleanup-b-context-identity` first and resume or explicitly abandon what it flags
- **expected artifact:** `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-result.md`
- **spine session id:** `commander-cleanup-b-context-identity` — re-claim it, do **not** `--force`; #601 re-stamps `claimed_at` on a re-claim, so a relaunch does not inherit the previous leg's context reading
- **governing docs, in order:** `ADMIRAL_RULING-1.md` (R1–R5, supersedes the frozen order where they disagree) → `LAUNCH_ORDER-2.md` → `LAUNCH_ORDER.md` → revised `MISSION_FRAME.md` and `execute.json`
- **do not redo:** the measurement (`notes-b.md` §1–2b, `measurement/`), the `SessionStart` bind-on-resume finding, `DESIGN_500.md`, `CRITIC_TRIAGE.md`'s 11 triaged findings. All accepted by the Admiral — cite them.

_Updated: 2026-08-16T13:20:00Z (leg 2)_
