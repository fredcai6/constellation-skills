# Crash-resume state note — cleanup-b-context-identity

- **step:** execute · leg 3 · gate `g1-review` **in-progress**, reviewer crew dispatched and running (`e0-context`, `g0-measure`, `g1-implement` closed; `g1-implement` committed at `3bc87e93` — **do not rerun the g1 implementer**)
- **slug:** cleanup-b-context-identity · branch `cleanup/b-context-identity` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
- **next command:** `py /home/tommy/.claude/skills/constellation-commander/scripts/recover_crews.py cleanup-b-context-identity` FIRST — the reviewer's result may already be on disk. If it is, integrate it and `advance g1-review`; if the crew is `resumable`, `run_crew.py --resume constellation/cleanup-b-context-identity/g1-review/reviewer/attempt-1`. **Do not blind-redispatch.**
- **pid:** `3475314` (reviewer crew, `cli` backend; wrapper pid `3475311`). Legs 1 and 2 of this lane are now explicitly ABANDONED in the registry and no longer block a launch; attempt-3 is this session.
- **expected artifact:** `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-result.md` (crew stdout/stderr under `crew-runs/g1-review-reviewer-attempt-1.*`)

## Leg 3 facts a fresh agent needs

- **lease:** `commander-cleanup-b-context-identity`, re-claimed at leg 3 start (claim re-stamped by #601). **Never `--force`** — the lease is this lane's own.
- **main is merged:** `ccb8b8d8` merges `main` (`d7b911a7`, which carries lane C `df6f951b` and lane D) into the branch. `map/INDEX.md` conflicted and was resolved by regenerating it with `py -m scripts.code_map build`, not by hand.
- **gate-time baseline, re-measured after the merge with `__pycache__` cleared:** `3104 passed, 6 skipped, 0 failed` (125s). The stale 3057 in the frozen order and the 3089 in `LAUNCH_ORDER-3.md` are both superseded by this reading.
- **read first:** `LAUNCH_ORDER-3.md` → `ADMIRAL_RULING-2.md` → `ADMIRAL_RULING-1.md` → `LEG2_DIGEST.md` → `LAUNCH_ORDER-2.md` → `LAUNCH_ORDER.md`.
- **do not redo:** the measurement (`notes-b.md` §1–2b, `measurement/`), the `SessionStart` bind-on-resume finding, `DESIGN_500.md`, `CRITIC_TRIAGE.md`'s 11 findings, leg 2's shipped #600 change. Cite them.
- **still owed:** `g1-review`; `g1-integrate` (retire `measurement/probe_cross_key.py`, lane C #549 re-measurement); `REPLAN_INPUT.json` (execute's postcondition refuses completion without it); `g2-implement-500` under R5 **only if context allows** — a third hand-back of `DESIGN_500.md` is an accepted outcome, running long to avoid it is not.
- **park at `archive`. Do not merge** — publication is the Admiral's class.

_Updated: 2026-08-16T14:35:00Z (leg 3, before `resume execute`)_
