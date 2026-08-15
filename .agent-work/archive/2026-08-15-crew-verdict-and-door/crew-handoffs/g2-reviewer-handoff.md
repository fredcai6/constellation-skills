# Reviewer Handoff

## Gate
`g2`

## Survey State Location
Create your review survey checklist at `.agent-work/crew-verdict-and-door/g2-review/review.json`.

## What Was Implemented
Two additive pieces in `scripts/run_crew.py`, hardening the already-known unbound-MCP-door hazard on the
`external` crew-dispatch backend (binding the door out-of-band is impossible by construction, out of scope):
(1) `build_entry` sets `entry["door_bound"] = (backend == BACKEND_CLI)` on every registry entry; (2)
`ExternalBackend.dispatch` prints an unconditional stderr banner naming the unbound door and instructing the
caller to verify `spine_status` before any mutating verb.

## How to Inspect the Diff
UNCOMMITTED working tree in
`/home/tommy/projects/constellation-skills/.worktrees/crew-verdict-and-door` (branch
`fix/crew-verdict-and-door`). g1's fix is already committed at `f06d314e` — that commit is expected history,
not part of this gate's diff. Inspect only the uncommitted delta:
```bash
git status --porcelain
git diff scripts/run_crew.py
git diff tests/test_crew_launcher.py
```

## Task Statement
Make the external backend's unbound-door hazard impossible to miss, without attempting to bind it (a prior
cold-critic pass caught that the original ask — "state it in the crew prompt" — targets code that doesn't
exist in this file; the corrected ask is the registry field + stderr banner, both confirmed buildable inside
`scripts/run_crew.py`).

## Close Criteria
- `build_entry` sets `door_bound` on every entry: `True` iff `backend == "cli"` (equality, not `!=
  "external"` — check this precisely, since the wrong direction silently defaults a future third backend to
  `True`).
- `ExternalBackend.dispatch` unconditionally prints a stderr line (every external dispatch, not just some)
  naming: the door is unbound, it resolves to `.mcp.json`'s demo default, and the caller must verify
  `spine_status` before any mutating verb.
- `CliBackend` is unaffected — confirm it still gets `door_bound=True` via the same shared `build_entry`
  path, not a separate/duplicated code path.
- No existing test broke; full `tests/test_crew_launcher.py` green.
- Nothing outside `scripts/run_crew.py` and `tests/` was touched; `scripts/mcp_spine_server.py` untouched
  (binding was correctly not attempted).

## Allowed Scope
`scripts/run_crew.py` (`build_entry`, `ExternalBackend.dispatch`) and `tests/test_crew_launcher.py`.

## Specific Exclusions
- `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`, `.mcp.json`, `scripts/mcp_spine_server.py` —
  must show zero diff.
- g1's already-committed change (`finalize_from_exit_code`, commit `f06d314e`) — not this gate's concern,
  don't re-review it.

## Constraints the Implementation Must Respect
- `door_bound` field name and equality-against-"cli" semantics are pinned by the handoff — verify the exact
  condition used, not just that some boolean exists.
- The stderr banner must be unconditional and must fire on every `ExternalBackend.dispatch` call, not
  behind a flag or conditional.

## Map Anchors (inbound)
- **Structural:** `scripts/run_crew.py:868-` (`build_entry`, changed); `scripts/run_crew.py:1278-1310`
  (`ExternalBackend.dispatch`, changed).
- **Map confidence flags:** repo's derived code map is DEGRADED-UNPARSEABLE repo-wide — do not expect map
  citations.

## Evidence Produced
From `IMPLEMENTER_RESULT` at `.agent-work/crew-verdict-and-door/crew-handoffs/g2-implementer-result.md`
(read it in full): TDD red-then-green for the 3 new tests, full `test_crew_launcher.py` run (172 passed),
`git check-ignore` exit 1, wiring grep for `door_bound`. Re-run the pytest commands yourself.

## Suggested Model Tier
simple bounded.

## Stop Conditions
BLOCK if: either of the two required pieces is missing or conditional; the equality direction on
`door_bound` is backwards; anything outside allowed scope was touched; a claimed test result doesn't
reproduce.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK) to
`.agent-work/crew-verdict-and-door/crew-handoffs/g2-reviewer-result.md` before ending your turn.
