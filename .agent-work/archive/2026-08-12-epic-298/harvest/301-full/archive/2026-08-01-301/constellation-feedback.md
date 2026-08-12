### commander-core.md instructs delegated Commanders to use a channel their tier cannot open

- **Where:** `skills/commander/references/commander-core.md`, Mission frame section — "Any background subagent you dispatch ... must be told **in its spawn prompt** to deliver its result via `SendMessage`".
- **Defect:** a delegated Commander runs as a *teammate*, and the harness refuses a teammate spawning a *named* subagent ("Teammates cannot spawn other teammates — the team roster is flat"). Unnamed subagents have no `SendMessage` address, so the instruction is unfollowable at exactly the tier the doctrine targets. All four design-panel dispatches from commander-301 failed on first attempt.
- **Also misleading, not just impossible:** the stated rationale (teammates "end on a bare idle notification with the report undelivered") does not apply to an unnamed subagent, whose final message the parent reads directly.
- **Suggested:** split the guidance by tier — keep the SendMessage line for agents that can spawn named teammates; for a delegated Commander, specify "dispatch without `name`; deliverable to a path, summary as the final message." Check whether `skills/admiral/` carries the same instruction downward.
- **Filed:** fredcai6/constellation-skills#314
