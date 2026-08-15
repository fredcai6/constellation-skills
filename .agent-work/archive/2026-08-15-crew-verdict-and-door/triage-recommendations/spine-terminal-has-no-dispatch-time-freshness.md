# Triage Recommendation: `spine_terminal has no dispatch-time freshness parameter`

## Classification
`missing test` / `bug` (latent, not yet triggered)

## Source checklist/artifact
- g1 IMPLEMENTER_RESULT out-of-scope observation, independently confirmed by the g1 reviewer (`.agent-work/crew-verdict-and-door/crew-handoffs/g1-implementer-result.md`, `g1-reviewer-result.md`).

## Structural anchor
`scripts/run_crew.py:317-361` (`spine_terminal`)

## Cartographer mismatch class
None.

## Observations
### Observation 1
- **What's wrong:** `spine_terminal(spine, root)` takes no `since`/dispatch-time parameter, unlike `result_fresh(result, root, since)`. A terminal spine left over from an EARLIER attempt at the same path can rescue a LATER attempt's missing/stale result into `completed`, as long as that later attempt's `exit_code` is `0` — even if the later attempt did nothing new.
- **Expected:** A spine consulted for a verdict should be fresh relative to the dispatch being judged, mirroring `result_fresh`'s existing freshness contract.
- **Conditions:** Both `--spine` and `--result` given; the spine path is reused across attempts (e.g. `--resume`, or two attempts at the same gate); the earlier attempt's spine reached terminal state and was never cleaned up; the later attempt exits `0` without itself completing new work.
- **Type:** `inferred` — read off `spine_terminal`'s signature and this run's own g1 fix (which added a new consumer of `spine_terminal` that leans on this exact property slightly more than before, since the rescue path is a NEW way for `spine_terminal`'s answer to flip a verdict from `failed` to `completed`).
- **Rev:** `35f6c663` (this run's HEAD after both g1 and g2).

## Desired behavior
- **Desired:** `spine_terminal` (or a caller-side staleness guard mirroring `result_fresh`) only counts a terminal spine as dispositive if it reached terminal state at/after the dispatch's own `since` timestamp.
- **Today instead:** `spine_terminal` reads the spine file's current state with no time comparison at all.
- **Type:** `measured` — read the full function body at `scripts/run_crew.py:317-361`; confirmed no `since` parameter and no mtime comparison anywhere in it.
- **Rev:** `453f8492` (unchanged by this run; `spine_terminal` itself was explicitly out of scope for `crew-verdict-and-door`).

## Possible fix
Add an optional `since` parameter to `spine_terminal`, compared against the spine file's own mtime (mirroring `result_fresh`'s floor-to-whole-seconds comparison) — or have `finalize_from_exit_code`'s new rescue branch check the spine file's mtime itself before trusting `spine_terminal`'s answer. Either requires deciding what "the spine became terminal" means when the engine journal doesn't currently timestamp individual `advance` calls at the item level — that may be a bigger design question than the fix suggests.

## Open questions
- Does `checklist_engine.py`'s journal already carry a per-item completion timestamp that a caller-side check could read instead of the spine file's whole-file mtime? Not investigated this run (checklist_engine.py is outside file ownership for `crew-verdict-and-door`).

## Recommended priority
`low`

**Reason:** Latent, not yet observed in production — requires a specific reuse-of-spine-path-across-attempts pattern this run did not itself trigger. Worth fixing before it does, not urgent.

## Related artifacts
- `.agent-work/crew-verdict-and-door/crew-handoffs/g1-implementer-result.md`
- `.agent-work/crew-verdict-and-door/crew-handoffs/g1-reviewer-result.md`
- `.agent-work/crew-verdict-and-door/REPLAN_INPUT.json` (`parked_possibilities`)

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: this run's launch order (LAUNCH_ORDER.md) grants no tracker-filing authority -- Task 1/Task 2 are the only scoped deliverables, and this candidate is explicitly out of scope for both (it requires touching spine_terminal itself, which g1's handoff fenced off).`

## Issue creation authority
`issue-ready only`
