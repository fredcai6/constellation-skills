# State note — epic418-h-447 (issue #447, epic-418 workstream H)

Crash-resume state. If this run dies, a fresh Commander cold-starts from `current` alone plus this file.

- **step:** OUTER spine (`spine.json`) closeout — execute.json is DONE (all six gates) and its lease exec-447 is RELEASED
- **slug:** epic418-h-447
- **worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447`
- **branch:** `epic-418/h-447-episodes-retirement` (base `cbd9aee`)
- **engine session-id:** `cmdr-447-episodes-retirement` (lease active on `spine.json`)
- **pid:** in-context agent, no detached process; crews are Agent-tool subagents, not background PIDs
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic418-h-447/spine.json current` (lease `cmdr-447-episodes-retirement`)
- **expected artifact:** a terminal `archive` on `spine.json`, then `RETURN.md` at the worktree root.
- **commits so far:** bf8819a g1, dbf9a23 g2, 100a33c g3, 77e428d g4, fd7ef60 g5, f2dd40a g6.
- **state:** `verify_retirement.py` exits 0 / zero bytes; suite 1622 passed, 0 failed. All 8 crews COMPLETE, 0 unresolved.
- **NOT done, and NOT mine:** push, PR, merge. The launch order reserves those for the Admiral.

## Two things a resuming agent must not re-derive or get wrong

1. **`durable_root()` resolves to THIS WORKTREE, not the main checkout** — `scripts/agent_work_root.py:136-140`
   redirects to the fallback whenever an active Admiral epic lease exists, and epic #418 holds one. So this
   run's own `feedback`/`archive` gate reads *this worktree's* `.agent-work/AGENT_FEEDBACK.md`. g4 therefore
   uses `git rm --cached`, never `git rm`. Deleting the working-tree copy strands the closeout, and the only
   exits are recreating the retired file (#308's exact failure shape) or a human override with no human
   reachable. See `CRITIC_TRIAGE.md` T1.
2. **The frozen artifacts are** `PROBLEM_STATEMENT.md`, `MISSION_FRAME.md`, `PLAN_ALTERNATIVES.md`,
   `CRITIC_TRIAGE.md`. Read `CRITIC_TRIAGE.md` before trusting the other three — it records two claims in
   `PROBLEM_STATEMENT.md` §5 and §2.4 that the cold panel falsified and that I re-verified false at source.

## Gate order

g1 guard (proven RED first) → g2 replacement capture verifier → g3 rewire spines + install bundles →
g4 carry 6 lessons + untrack the 2 files + delete the machinery → g5 prose + doctrine tombstone →
g6 flip the guard green, full suite.

## Standing constraints

`python` not `py`. Opus or lower on every dispatch, model named, no Fable. Surgical raw-text edits to the
compact spine JSON, never a `json.dump` round-trip. `RETURN.md` at the worktree root is workstream A's
inherited file until I overwrite it with mine.
