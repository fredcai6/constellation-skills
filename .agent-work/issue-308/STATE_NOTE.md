# Crash-resume state note — issue-308

- **step:** execute · `g1` and `g2` COMPLETE; next active item is `g3-drop-cap-implement` (a crew gate)
- **slug:** work-id `issue-308`, branch `epic-298/308`, worktree `C:/Programs/constellation-skills-wt/e298-308`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-308/execute.json current --session-id commander-308-e298`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/issue-308/execute.json` with every item `complete`, then the spine driven through reconcile → triage → review → feedback → archive, and the lease released last.

Everything through `1dd83a1` is committed and pushed. Nothing of value is worktree-local.

## Engine state

Spine: init, context, understand, plan complete; execute in-progress.
Execute plan: `e0-context`, `g1-build-destination`, `g2-doc-coherence` complete.
Two leases, same session id `commander-308-e298` — one on `spine.json`, one on
`execute.json`. Pass `--session-id commander-308-e298` on every mutating call.

## What a fresh agent must know that the spine does not carry

1. **`g6-land-consolidation` is BLOCKED on Tommy's two-bin routing ruling.** Do NOT
   self-rule. Both bins are argued in `.agent-work/issue-308/ROUTING_QUESTION.md`. If the
   ruling has not arrived, leave g6 and g7 pending and hand the branch up **PENDING**.
2. **`g4` deliberately leaves ONE lesson active** —
   `verify-launch-order-claims-against-code` — because disposing it *is* the routing
   decision (graduating it to `docs/agents/` is bin 2). `checks/dispositions_done.py` pins
   that carve-out **by id**. **Zero active entries is a FAILURE at g4, not a success.**
   This was the cold critic's BLOCKING 1.
3. **g5's intake set is 6 sites across 5 files**, re-enumerated by command after the
   critic found the original hand-written list named 5 and the original guard phrase
   matched only 2. The site in `ADMIRAL_SPINE.template.json` is in the **`latitude`** task,
   not `context`. `checks/lesson_intake_is_cut.py` is the guard; it enumerates the corpus
   rather than trusting a list.
4. **g5 must also update `tests/test_context_manifest.py`** (~line 550), which pins the
   spine declaration list including `(".agent-work/LESSONS.md", False)` as an exact
   literal. Dropping the manifest entry without that edit reds the suite. The gate
   imperative authorizes it.
5. Interpreter is `python` (3.14, has pytest). **`py` has no pytest** and reads as a
   silently green suite. Full suite ≈ 415s; green at `4cec87a` and at `1dd83a1`.
6. Never touch the main checkout `C:/Programs/constellation-skills` — the human's
   uncommitted work is there.
7. Shell traps hit this run, both real: **backticks inside double-quoted strings are
   executed** (broke a postcondition, now single-quoted), and **`git checkout <file>` to
   undo a test mutation reverts the real edit too** — snapshot to a scratch copy instead.

_Updated: 2026-08-02T21:20:00Z_
