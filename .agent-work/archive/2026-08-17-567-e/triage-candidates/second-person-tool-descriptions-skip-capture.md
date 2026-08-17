# Triage candidate: second-person `TOOLS` descriptions silently skip episode capture

**Found by:** g1-review (fresh reviewer subagent), work-id 567-e, issue #541.

**What was found:** `_capture_refusal_episode()` quotes a tool's own registered `TOOLS`
`description` verbatim for the captured episode's `expected-behavior` field. Four `TOOLS`
descriptions besides `spine_bind` (already fixed this gate) still carry second-person
pronouns ("you"/"your"): `spine_status`, `spine_lease`, `spine_halt`, and possibly others not
yet audited. `apply_episode_delta.py`'s pre-existing `verify_episode_observations.py` guard
rejects any assertion statement containing a second-person pronoun, so the very first door-own
rejection captured for any of these tools will silently skip capture (a stderr `EPISODE
CAPTURE SKIPPED` diagnostic is written, but no episode is created, no crash, no error surfaced
to the caller).

**Why it matters:** This is a fail-safe gap, not a fail-unsafe one — nothing crashes and the
JSONL sidecar (`_log_rejection`'s own append) still captures the rejection. But it means
episode-store coverage for issue #541 is narrower than "every door-own rejection with a bound
spine": specifically, rejections raised by calling `spine_status`, `spine_lease`, or
`spine_halt` with the wrong arguments will not land in `episodes/`, silently, until their
`TOOLS` descriptions are reworded the same way `spine_bind`'s was this gate.

**Recommendation:** Audit all `TOOLS` entries in `scripts/mcp_spine_server.py` for
second-person pronouns and reword them to third-person/imperative, mirroring the `spine_bind`
fix in this gate (meaning-preserving, minimal). Small, mechanical, same-file change — a good
candidate for a follow-up issue or a fold-in to the next lane touching this file.

**Owner suggestion:** whichever lane next touches `scripts/mcp_spine_server.py`'s `TOOLS` list,
or a small standalone issue.
