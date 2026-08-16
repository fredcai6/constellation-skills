# Crash-resume state note — cleanup-b-context-identity

- **step:** execute · gate `g1-review` **not begun** (`g1-implement` closed and committed at `3bc87e93`) · leg 3 picks up here
- **slug:** cleanup-b-context-identity · branch `cleanup/b-context-identity` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
- **next command:** re-claim the lease (`claim --session-id commander-cleanup-b-context-identity`, **never** `--force`), then `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py /home/tommy/.claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/cleanup-b-context-identity/execute.json start g1-review`
- **pid:** none — no crew running. `recover_crews.py cleanup-b-context-identity` at handoff: attempt-1 commander ABANDONED, attempt-2 commander (leg 2, this session) exiting, g1 implementer COMPLETE — do not rerun it
- **expected artifact:** `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-result.md`, dispatched with the already-written `g1-reviewer-handoff.md`
- **read first:** `.agent-work/cleanup-b-context-identity/LEG2_DIGEST.md` — verdict, the R4 departure carried up to the Admiral, four triage candidates, and exactly where to pick up
- **why leg 2 stopped:** the engine refused `start g1-review` at 17% of the 150000 absolute cap. A `refresh-request` is attached (`e-g1-review-1`, seam `g1-review`, `why_ref w-3`), so the guard takes its release path for you
- **spine session id:** `commander-cleanup-b-context-identity` — #601 re-stamps `claimed_at` on a re-claim, so you do not inherit leg 2's reading
- **governing docs, in order:** `ADMIRAL_RULING-1.md` (R1–R5, supersedes the frozen order where they disagree) → `LAUNCH_ORDER-2.md` → `LAUNCH_ORDER.md` → revised `MISSION_FRAME.md` and `execute.json`
- **do not redo:** the measurement (`notes-b.md` §1–2b, `measurement/`), the `SessionStart` bind-on-resume finding, `DESIGN_500.md`, `CRITIC_TRIAGE.md`'s 11 findings, and now leg 2's shipped #600 change. Cite them.
- **still owed:** `REPLAN_INPUT.json` (execute's own postcondition refuses completion without it), retiring `measurement/probe_cross_key.py` at `g1-integrate`, the lane C #549 re-measurement, and `g2-implement-500`

_Updated: 2026-08-16T14:15:00Z (leg 2 handoff)_
