# Crash-resume state note — issue-308

- **step:** execute · entering gate `g1-build-destination` (spine: init/context/understand/plan complete)
- **slug:** work-id `issue-308`, branch `epic-298/308`, worktree `C:/Programs/constellation-skills-wt/e298-308`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-308/spine.json current --session-id commander-308-e298` — then drive `.agent-work/issue-308/execute.json` gate by gate. Engine lease is `commander-308-e298`; pass `--session-id commander-308-e298` on every mutating call.
- **pid:** none — foreground
- **expected artifact:** `.agent-work/issue-308/execute.json` with every item `complete`, then spine `archive` complete and the lease released.

## What a fresh agent must know that the spine does not carry

- **`g6-land-consolidation` is BLOCKED on Tommy's two-bin routing ruling.** Do NOT
  self-rule. The question, with both bins argued, is
  `.agent-work/issue-308/ROUTING_QUESTION.md`. If the ruling has not arrived, leave g6 and
  g7 pending and hand the branch up **PENDING**, saying so.
- **`g4` deliberately leaves ONE lesson active** (`verify-launch-order-claims-against-code`)
  because disposing it *is* the routing decision. `checks/dispositions_done.py` pins that
  carve-out by id. Zero active entries is a FAILURE at g4, not a success.
- Interpreter is `python` (3.14, has pytest). `py` has **no pytest** and reads as a
  silently green suite. Full suite ≈ 415s, green at `4cec87a` (1620 passed, 2 skipped).
- Never touch the main checkout `C:/Programs/constellation-skills` — it holds the human's
  uncommitted work.

_Updated: 2026-08-02T20:55:00Z_
