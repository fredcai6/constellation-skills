# Crash-resume state note — epic-418-followon (Admiral)

## WHERE THE RUN IS (rewritten 2026-08-12 at the refresh handoff)

- **step:** `closeout` **[pending]**, refresh requested and recorded on the spine as `e-closeout-1`.
  `execute` is **complete**. The engine refused `start closeout` at 23% context and asked for a fresh
  agent to begin it. Nothing was routed around that refusal.
- **next command:** relaunch a fresh Admiral into this same spine
  (`.agent-work/epic-418-followon/spine.json`) and cold-start it from `current` alone. Re-claim the
  lease with the same session id — it is idempotent. Then `start closeout` and work the list below.
- **lease:** `717403d3-70be-436f-bc06-ce9ac3e34e05`, **still held**, released last and only last.
- **main:** green at the tip. **2933 passed, 4 skipped, 1121 subtests.** Template sweep **23 fault
  lines across 8 files**.

## The one thing that will bite the next agent immediately

**This session's MCP door was bound to a wave-1 scratch demo spine, not to this epic's spine.** The
Admiral drove its own closeout through the engine directly because the door pointed elsewhere — the
exact defect this epic exists to remove, landing on the Admiral at its own closeout. Check
`spine_status` before assuming the door is yours; if it names someone else's gates, the dispatch did
not bind `SPINE_FILE`. This is owed as an episode and is not yet written.

## Closeout, in order, with what is already true

1. **Episodes (c1, c2).** `.agent-work/epic-418-followon/episode-delta.json` holds **14 ready `create`
   ops**, dry-run clean, covering the epic through wave 6. **Not yet applied.** Add the ones this
   session produced before applying: the Admiral's own door misbinding above; C3 clearing its own
   block and taking two forbidden outward-facing acts; cold review refusing a merge that five
   APPROVEs had passed; `close_work` failing on its own first real use; the crew-inherits-the-
   dispatcher's-lease measurement; and R0 implementing before it reproduced and saying so.
   Apply with `apply_episode_delta.py --delta ... --store-root episodes`, then
   `verify_episode_captured.py epic-418-followon --store-root episodes --phase feedback`.
   **Never hand-edit anything under `episodes/`.** C3's own 8 episodes are already committed there.
2. **Architecture reconcile (c3).** This repo has **no packet map**: `docs/architecture/` is absent
   and `map/ids.jsonl` is empty. C3 measured that and orients degraded because of it. A reasoned
   no-op is the compliant answer here — record why rather than blocking on an absent map.
3. **Dogfood feedback sweep.** This epic ran against this repo itself, so run a fresh
   `collect_feedback.py` over the roots in `docs/DEBT_SWEEP_CADENCE.md`.
4. **Hygiene (c4).** One worktree remains: `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
   on branch `epic-559/c3-lifecycle`, merged. **Harvest its `CONSTELLATION_FEEDBACK.md` BEFORE
   `git worktree remove`** — look in both the worktree root and
   `.agent-work/staged-feedback/<work-id>/`. Then remove, prune, and archive `ADMIRAL_LOG.md` under
   `.agent-work/archive/`.
5. **Summary and acceptance (c5).** Present the epic summary and attach the human's decision as
   evidence.
6. **Release the lease last.** After closeout's final `advance`, never before it.

## What this epic did, for the summary

Thirteen workstreams merged. All eighteen engine verbs reach through nine door tools; a spine is
compiled from a typed spec and the generator refuses to write anything the oracle would reject; a
crew that cannot satisfy a check blocks to its recorded parent; and wave 7 made the work lifecycle
one thing — one call opens branch, worktree, work area and spine together, the closing advance
archives that work area spine-last and says ready to PR, and a gate's dispatch is declared in the
spec and checked against the registry.

**Four of the five done-conditions hold. The fifth does not:** agent-facing instruction still names
the engine CLI in 11 files — 15 fallback clauses and 8 live `<engine>` tokens, all three orchestrator
spine templates among them. The human chose to **file it rather than run it**: #559 carries the full
re-measurement and the guard it needs, and **#565** argues the cause is that the workbench skill
teaches what the door's tools now carry, which is why the clauses keep growing back.

## Rulings still in force

1. Agents do not know about the CLI; anything reachable only through the CLI is a defect.
2. Hardcoding this host's interpreter is allowed, provided every hardcode is recorded on **#539**.
3. Judgment goes up: a greater claim requires greater review.
4. Crews fail up one rung at a time, to their recorded parent.
5. Prefer Sonnet crews; a Commander on Opus is an Admiral escalation and is logged.
6. Tool consolidation is deferred to a round at the end.
7. Do not narrate mistake lists back to the human.

## Operating facts that have each cost time once

- **Run crew commands FROM THE WORKTREE.** `run_crew.py` never sets the child's cwd.
- **`pgrep -f "<work-id>"` matches the checking shell's own command line.** Use `ps -p`.
- **Never `git add -A`**, and a pathspec-scoped `-A` is still `-A`. `.agent-work/` is tracked.
- **Run the suite as `python -m pytest`**, and run it in a **foreign checkout** before believing a
  green number — that is what caught the one defect five reviews missed.
- **The installer rewrites the tracked `.mcp.json`.** Revert after. Recorded on #539.
- **Windows is deferred by human decision.** Main is red on Windows CI since 08-11; the measurement
  is on the record and no one is working it.
