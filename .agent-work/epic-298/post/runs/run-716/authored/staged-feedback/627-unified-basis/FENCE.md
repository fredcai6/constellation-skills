# FENCE — 627-unified-basis

This run is dispatched under a frozen Admiral LAUNCH_ORDER (`ShipF-627 — issue #627+#506 Phase 3`). The launch
order's **File Ownership** fences my durable writes: "Sole writer this wave: verdict
`C:/Programs/f1Brainz/.agent-work/epic-601/wave5-627-verdict.md`; workbench under your worktree `.agent-work/`."
The shared durable feedback root (main checkout `.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` /
`CONSTELLATION_FEEDBACK.md`) is the Admiral's to own — writing it directly is outside my sole-writer fence, and my
worktree `.agent-work/` is gitignored.

Per the constellation-commander-delegated fenced-closeout rule, the durable feedback log write is therefore staged
as this worktree-local trio for the Admiral to harvest into the shared root before sweeping the worktree:
- `AGENT_FEEDBACK.md` — the run retrospective (mentions work id 627-unified-basis).
- `lessons-delta.json` — the full delta (5 confirms + tick applied locally; 1 `add`,
  `delegated-commander-foreground-poll-over-watcher-yield`, blocked locally by the Active cap 20 → the Admiral
  applies it to the shared root with a retire-to-make-room decision it owns).
- `CONSTELLATION_FEEDBACK.md` — 3 upstream doctrine/template improvements.

Precedent: the Admiral already harvests this pattern (`.agent-work/staged-feedback/{624-phase0,625-segmentation-substrate,638-f12-stability-rework,wave4-626}/`).
