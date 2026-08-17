## Wave review — boundary w1 (pre-launch)

No wave has run yet. This is the launch-authorizing transition for wave 1, and it exists to record two things measured before dispatch rather than discovered inside it.

**The epic's repro holds, with one correction and one extension.** At `600de02`: 15 CLI-fallback clauses across 11 files, as recorded. Eleven live `<engine>` tokens across 7 files, not the 9 the epic body states. Zero door vocabulary in `specs/*.spine.toml` — only `implementer` and `reviewer` specs exist. The verb gap is closed at 11 tools.

**The extension is the one that matters.** #559 frames the unreachable-own-spine collision as a dispatched-subagent problem. It is not. It stopped this Admiral in its own process at step one: `spine_status` returned `REFUSED: no spine is bound to this door`, and `spine_open` only mints a new worktree, branch and compiled spine — no verb binds the door to an existing spine file. Init was consequently driven on the CLI fallback and logged as an `ADMIRAL ERROR`. Lane A's scope is therefore the general case, and the doctrine sweep is genuinely blocked behind it: you cannot delete a fallback that is currently the only path.

**Decision: advance.** Wave 1 launches four lanes concurrently — A (Opus), B, C and G (Sonnet). Every discrepancy is dispositioned; no issue was created, per the standing ruling that filing is held to closeout.
