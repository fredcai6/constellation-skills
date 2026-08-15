# Review Result

## Assigned Gate
`g2`

## Result
`APPROVE`

## Handoff compliance
Both required close-criteria pieces are present and correct. `build_entry` (`scripts/run_crew.py:946`) sets
`entry["door_bound"] = (backend == BACKEND_CLI)` — equality against the literal `"cli"` constant (confirmed
`BACKEND_CLI = "cli"`, `BACKEND_EXTERNAL = "external"` at lines 64-65), the correct direction so a
hypothetical future third backend defaults to `False` (safe), not `True`. `ExternalBackend.dispatch`
(`scripts/run_crew.py:1318-1362`) prints an unconditional stderr banner immediately before its single
`return None, entry` statement — no `if`/flag guards it — naming the door as unbound, `.mcp.json`'s demo
default, and instructing `spine_status` verification before any mutating verb; all four required phrases
(unbound / `.mcp.json` / demo default / `spine_status`) confirmed present. `CliBackend` is unaffected and
gets `door_bound=True` through the same shared `build_entry` constructor call (`CliBackend.dispatch` passes
`backend=self.name` where `self.name = BACKEND_CLI`) — grep for `"backend":` in `run_crew.py` shows exactly
one dict-literal site, confirming no duplicated entry-construction path exists.

## Scope drift
None. `git status --porcelain` shows only `scripts/run_crew.py` and `tests/test_crew_launcher.py` modified.
All four specific-exclusion files (`scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`.mcp.json`, `scripts/mcp_spine_server.py`) show zero diff. `finalize_from_exit_code` (g1's already-committed
change) is untouched — confirmed via `grep -c` on the diff. Test-file diff is purely additive (3 new methods,
no existing test line changed).

## Evidence verdict
All claimed evidence independently reproduced, not just re-read:
- Full `tests/test_crew_launcher.py`: 172 passed (matches).
- Targeted `-k` filter on the 3 new tests: 3 passed, 3012 deselected (matches).
- Red-before-green reproduced from scratch via `git stash push -- scripts/run_crew.py` (new tests left in
  place against the unfixed code): 3 failed with identical failure modes (`KeyError: 'door_bound'` x2,
  `AssertionError: 'unbound' not found in ''`) — matches the implementer's pasted RED output. `git stash pop`
  restored the fix; re-ran both the targeted 3 and the full 172-test suite, both green again.
- `git check-ignore scripts/run_crew.py tests/test_crew_launcher.py`: exit 1 (both tracked), matches.
- Wiring grep for `door_bound`: identical 6-line output to the implementer's paste.

TDD evidence shows genuine red (KeyError / empty-string assertion, not a trivially-always-passing check) then
green — satisfies "a check that cannot fail is indistinguishable from one that passed."

## Code/doc quality
Minimal, additive change: one new dict key + docstring paragraph in `build_entry`, one unconditional `print`
call in `ExternalBackend.dispatch`; no new helper functions, no signature changes, no speculative
abstraction. Naming (`door_bound`, snake_case) matches surrounding dict-literal conventions. Assertions
target actual runtime behavior (the dict key's value, the real captured stderr bytes), not docstrings or
description fields. No hidden fallback — the banner is genuinely unconditional.

## Map impact verdict
- **Evidence supports claimed change:** yes — independently reproduced (see Evidence verdict).
- **Constraints not violated:** yes — the pinned prohibition against binding the door out-of-band
  (`scripts/mcp_spine_server.py`, `tests/test_mcp_identity.py:914`) was read, respected, and the file left
  untouched; confirmed via `git diff --stat -- scripts/mcp_spine_server.py` (zero diff).
- **Notes match the diff:** yes — implementer's Map Impact notes (structural anchors, capability = new
  observability field + new stderr warning, no event impact, no new decision candidates, `door_bound` as an
  unconsumed claim surface) match the diff with no overstatement or omission.
- **Decision candidates surfaced:** n/a — none new; the two-piece scope was pinned by the corrected handoff.
- **Durable context routed:** yes — one non-blocking triage candidate flagged (below), matching the
  implementer's own out-of-scope observation.

## Reconciliation check
Map is DEGRADED-UNPARSEABLE repo-wide per handoff — no map citation expected. Grepped for exact-key-set
schema validators over registry entries (none found), so the new always-present `door_bound` key cannot
silently break an existing consumer.

## Blockers
- none

## Out-of-scope observations
- Surface `door_bound: false` in `recover_crews.py`'s human-facing report so a human debugging a
  stuck/abandoned crew sees the unbound-door hazard without already knowing which backends bind a door.
  Confirmed by implementer, independently re-verified: neither `verify_external_result` nor
  `recover_crews.py`'s classifier reads `door_bound` today. Non-blocking, outside this gate's Allowed Scope.
- Fowler pass flagged one non-blocking `duplicated-code` observation: the new stderr banner in
  `ExternalBackend.dispatch` repeats the clause "spawns no process and builds no environment, so nothing
  binds" verbatim from the pre-existing `--spine` refusal message a few lines above it in the same class.
  Deliberate (implementer's own Assumptions note: reused phrasing for hazard-message consistency) — string
  phrasing, not duplicated logic. Worth a future constant-hoist so the two messages cannot drift apart if one
  is edited later without the other; not a defect today.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff's Close Criteria section was precise enough to check each
  clause mechanically (the equality-direction warning in particular was exactly the kind of thing worth
  double-checking, and it checked out).
- **Context rediscovered:** none beyond what the handoff and implementer result already anchored — reading
  `CliBackend.dispatch`'s call site to `build_entry` (already flagged by the implementer as worth confirming)
  was a one-read check, not a rediscovery.
- **Instructions improvised around:** the dispatch's explicit "no MCP spine door bound... drive your own
  survey checklist through the CLI checklist engine" instruction matched the environment (`SPINE_FILE`/
  `SPINE_SESSION` were bound to the parent Commander's own spine, not mine) — followed the dispatch's
  explicit override of the skill's default MCP-door guidance, as g1's reviewer did before me. One mechanical
  note: the skill's `r6-fowler` template item hard-codes the Fowler record path as
  `.agent-work/<work-id>/FOWLER_PASS.json` (work-id-scoped, not gate-scoped), so this gate's Fowler record
  overwrote g1's prior `FOWLER_PASS.json` on disk at that path. Harmless here since g1's review already
  consolidated and its own `review.json` evidence embeds the command output verbatim (not a live reference to
  the file), but a gate-scoped path (e.g. under each gate's own `g<N>-review/` directory) would avoid the
  collision entirely for any future multi-gate work where the file's on-disk survival mattered.
- **What would have made this easier:** nothing concrete for this review; the corrected handoff and the
  implementer's thorough Map Impact / Wiring Grep sections made independent verification fast.

## Return status
`complete`
