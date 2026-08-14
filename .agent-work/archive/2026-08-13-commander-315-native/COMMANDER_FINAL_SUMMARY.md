# Commander final summary — `commander-315-native`

## Outcome

The engine-native worktree isolation change and its MCP/crew compatibility follow-up are complete
locally. The original floated collision was resolved by the human ruling to implement both honest
cwd repairs. Fresh independent re-review returned **APPROVE**, the engine-owned integration suite
passed, `execute.json` reached terminal DONE, and `REPLAN_INPUT.json` passes the iterative-role
artifact verifier.

No merge was performed. At review-summary time the branch was one local commit ahead of
`origin/epic-568/c2-native-isolation`. During the later archive gate, the Admiral confirmed the
launch order's exact-branch push authority to update existing PR #577; merge remained forbidden.

## Closed gates and implemented behavior

- **Plan/execute:** The original engine-native origin stamp and refusal remain unchanged. The
  human-ruled follow-up makes crew dispatch/resume establish the crew's own absolute worktree cwd
  and makes the MCP door enter the bound spine's worktree only around one synchronous in-process
  engine call, restoring its previous cwd in `finally`.
- **Independent review:** First follow-up review correctly BLOCKED because default `.` still
  resolved relatively. Bounded g1c rework fixed the resolver and added parser-default dispatch and
  resume coverage. A fresh reviewer then returned APPROVE.
- **Integration:** The MCP-owned full-suite check initially inherited the door's `SPINE_FILE`,
  `SPINE_ENGINE`, and `SPINE_SESSION`, producing one deterministic false red in
  `DC3InheritanceMechanismTests`. Under the Admiral's explicit ruling, only g1-integrate.c1 was
  amended through MCP to clear those three bindings for pytest. No waiver was used.
- **Reconciliation:** No packet architecture map existed (degraded orientation, zero anchors).
  Reconciliation was direct: production docstrings describe both cwd boundaries, `map/INDEX.md`
  was regenerated, and map-tree freshness passed.
- **Triage:** Every candidate is routed in `TRIAGE_RECOMMENDATIONS.md`: tc6-tc7 are fixed-now at
  `48f07123`; tc8-tc16 are issue-ready recommend-and-defer records because explicit tracker-write
  approval was absent. No issue was filed and none remains unrouted.

## Durable revisions

- `a04d7828` — stamp spine origin and enforce native worktree isolation in the engine.
- `ed25bf8f`, `890ff76f` — original review/block/float records.
- `48f07123` — absolute crew worktree cwd plus scoped MCP bound-worktree engine cwd, tests, and map.

## Verification

- Engine-owned full suite through the amended MCP check: **2,981 passed, 6 skipped**.
- Fresh g1c reviewer full suite: **2,981 passed, 6 skipped, 1,130 subtests passed**.
- Focused crew placement suite: **171 passed**.
- Map-tree freshness: **1 passed**.
- Native origin repro: **GATE ARMED: True**.
- `python scripts/verify_iterative_role_artifacts.py commander --work-id commander-315-native`:
  **iterative role artifact ok**.
- `git diff --check`: clean before the follow-up commit and during reconciliation.

## Harness observations

- The native MCP door was successfully used for every engine interaction by driving
  `scripts/mcp_spine_server.py` over stdio. Neither this Commander nor its replacement crews used
  the checklist engine CLI.
- The installed MCP tool set was not hot-loaded into the already-running host, so manual JSON-RPC
  stdio was necessary. That path worked but is mechanically noisy.
- Claude dispatch hit its weekly quota before review work began. The documented external backend
  plus Codex crew fallback produced durable, independently verified implementer/reviewer results.
- MCP-bound engine checks inherit `SPINE_*` unless their command deliberately clears those names;
  this matters for tests whose contract is a clean caller environment.

## Remaining authority boundary

Local work is complete. The archive gate received exact-branch authority to update PR #577.
Merging remains a separate human decision.
