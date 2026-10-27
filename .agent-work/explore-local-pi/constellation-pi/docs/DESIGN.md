# First version decisions

Confirmed in the implementation request on 2026-10-22:

- This is a foundation expected to evolve quickly, not a disposable prototype.
- Pi owns Commander and lower-level sessions. Claude is the first model provider.
- Start with the Commander workflow; defer other role workflows and remote access.
- Preserve the engine's current Claude Code/Codex use.
- Role and engine state supply nominal actions. Explicit direction from the human
  or a higher-level agent can override the nominal path with recorded authority.
- Keep mechanisms light; prevent specific known errors and catch remaining failures.
- Exercise mechanics with deterministic tests and use lightweight models sparingly.

Implementation choices within that scope:

- Separate local `constellation-pi` repo; pinned Pi SDK 1.4.0.
- SDK host rather than a terminal extension: Commander and crew sessions share a
  small controller while each retains a separate persisted Pi session. A later TUI
  or Telegram client can use the same controller.
- JSON subprocess bridge imports the unmodified Python engine and returns its state
  projection. No new engine CLI format or duplicated state machine is needed.
- Narrow plan/implement/review/accept Commander path proves session dispatch and
  evidence integration before porting all existing Commander gates.
- Default Haiku, off thinking, bounded calls/turns/output, no automatic retries,
  compaction requests, or cache warming. The local GPU is unused.

Known scope limits:

- Local source checkout dependency is configured by path, not yet versioned as an
  independently distributed engine package.
- Tool exposure is chosen at the beginning of a Commander prompt. After a dispatch
  changes the gate, the next chat refreshes tools; repeating the old dispatch in
  that prompt is refused by a fresh state check.
- Pi abort cannot preempt an arbitrary custom callback; nested work has its own
  limits and cleanup waits for it to settle.
- Usage is known Pi usage. A hard process crash can lose final provider accounting;
  calls are counted before requests, and session paths are saved before prompting.
- An allocated session path can precede its first persisted user message. If a crash
  happens in that narrow window, a missing transcript causes a visible resume error.
  No provider call has started before that first user message is persisted. Inspect
  the run binding and clear only that missing session pointer to restart it.
- Crew claims still require review. A structured result is evidence to inspect,
  not proof of correctness.
