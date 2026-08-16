# Why this export is staged rather than written to the durable root

The Admiral launch order at
`.agent-work/cleanup-b-context-identity/LAUNCH_ORDER.md` fences this lane to
`scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`,
`scripts/checklist_engine.py` (gauge/trip/refresh regions) and their tests, and
parks the run at `archive` with publication reserved to the Admiral ("Park at
`archive`. **Do not merge** — publication is the Admiral's class").

`.agent-work/CONSTELLATION_FEEDBACK.md` is the durable root ledger and sits
outside that scope, so this run does not write it. The export beside this file is
staged for the Admiral to harvest before sweeping the worktree.

This citation is **not** a substitute for the export — a `FENCE.md` without the
staged content fails the gate, and it should, because learning cannot be silently
dropped. `CONSTELLATION_FEEDBACK.export.md` is beside this file.

Run: `cleanup-b-context-identity` · commander session
`commander-cleanup-b-context-identity` · branch `cleanup/b-context-identity` ·
base `a69bbac4` · 2026-08-16.
