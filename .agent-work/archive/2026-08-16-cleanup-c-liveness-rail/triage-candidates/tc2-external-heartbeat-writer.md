# Triage Recommendation: external-backend crew entries never re-touch `last_heartbeat` after dispatch

## Classification
missing capability anchor

## Source checklist/artifact
- execute.json triage_candidates tc2 (flagged from g1-review, echoing g1-implement's own out-of-scope observation)
- `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement-result.md`

## Structural anchor
`scripts/run_crew.py` (external-backend entry construction, `ExternalBackend.dispatch`)

## Cartographer mismatch class
none

## Desired behavior
- **Desired:** an `external`-backend crew's registry entry periodically re-touches its own `last_heartbeat` field while genuinely still working, so #599's `entry_liveness()` heartbeat-age corroboration (issue #599, this lane) measures true "time since last observed sign of life" rather than "time since dispatch."
- **Today instead:** `last_heartbeat` is set once at `build_entry` (equal to `started_at`) and only touched again by `verify()` (on a fresh result landing) or `resume()`. There is no periodic heartbeat-touch anywhere for a still-`running` external entry between dispatch and completion.
- **Type:** `measured` — read every `last_heartbeat` write site in `scripts/run_crew.py` (grep + manual trace); confirmed no periodic writer exists.
- **Rev:** `a69bbac4` through this lane's head `590bf44d` (this lane did not add one — explicitly out of scope per its own handoff).

## Possible fix
Add a lightweight heartbeat-touch call inside whatever polling/wait loop drives a long-running external dispatch (if one exists) or inside `run_crew.py`'s own registry-read paths when a caller checks on a still-running external entry. Needs design: what counts as "still working" for a process this repo does not itself control the lifecycle of (the external backend spawns nothing).

## Open questions
- Does anything today poll an external entry while it's in flight in a way that could double as a heartbeat-touch, or would this require a genuinely new periodic mechanism?

## Recommended priority
low

**Reason:** #599's 8h window was deliberately chosen with wide margins on both sides (≈2.3× above the longest observed healthy completion, ≈2.8× below the shortest observed phantom) specifically because this gap exists; it is not an active correctness bug today, just a known weakening of the corroboration's precision for a hypothetical multi-hour healthy dispatch this repo has not yet observed.

## Related artifacts
- `scripts/run_crew.py:264` (`entry_liveness`, this lane's #599 fix)
- `.agent-work/cleanup-c-liveness-rail/PLAN_CONVERGENCE.md`

## Disposition
`recommend-and-defer`

**Detail:** filing authority is unclear this run — not named in Inherited Latitude, and building this mechanism was explicitly excluded from this lane's Specific Exclusions.

## Issue creation authority
`issue-ready only`
