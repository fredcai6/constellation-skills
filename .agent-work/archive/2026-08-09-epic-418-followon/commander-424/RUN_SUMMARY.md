# Run summary — issue #424, workstream F of epic #418 (continuation)

Run under `LAUNCH_ORDER-424-continuation.md`, repair `w1-f424-repair`. Delegated: no reachable human;
the Admiral ratifies at the epic return boundary.

**Branch** `epic-418/f-424-mcp-door` · **PR #533** · **worktree** `/home/tommy/projects/constellation-skills-wt/f-424`

---

## The six done-conditions

| # | Condition | Verdict | Evidence |
|---|---|---|---|
| **DC1** | Cold agent reaches done on a real role spine through the door, zero malformed calls | **PASS** | Machine assertion: `assert_dc1.py` over two cold agents' own call records — both reached `DONE`, both zero malformed calls |
| **DC2** | Separation: parent and subagent drive two different spines at once, own instances, leases never collide | **PASS** | `tests/test_mcp_identity.py`; genuine concurrency via barrier-released threads with intersecting wall-clock windows; a collision control that reproduces a real leak when two processes share one spine file |
| **DC3** | Inheritance fails closed: an unconfigured subagent gets a refusal or no identity, never the parent's lease | **PASS**, behind a positive control | Control **in the assertion path**, demonstrated red for three distinct manipulations with proof each applied, green when correct. The g3 reviewer mutated the real door: a hardcoded identity turned exactly the 2 tests whose premise is "no `SPINE_FILE`" red, leaving 10 green |
| **DC4** | Same-gate equivalence as a **property** over every gate carrying an imperative | **PASS** | `tests/test_mcp_imperative_equivalence.py`: 61 gates across 12 shipped templates, discovered by **walking** the template tree. The g2 reviewer truncated the production door's `as_result()` and watched 4 of 5 tests go red, and added a scratch template to watch the population move 61→62 |
| **DC5** | Spine-management cost falls, attributably to the door | **PASS on the pre-registered metric**, *not by the expected mechanism* | 4 arms, both orders: CLI 22.0 vs MCP 18.0 invocation attempts, non-overlapping spreads. But **malformed calls were zero in both arms** — the saving is the schema arriving with the tools, not the door absorbing fumbles. Per-order gap 2 and 6, so 18% is a midpoint, not an effect-size estimate |
| **DC6** | The governor's threshold instruction arrives through a tool result and is acted on | **PASS**, with a named non-compliance | 2 of 33 tool results carried the HARD instruction verbatim; the agent's next calls attached a `refresh-request` and advanced with a `--why` handoff. It then **ignored the "and stop" half** and drove four more gates |

**No condition is UNMEASURED.** One arm of DC6 *was* unmeasured (a gauge seeded before the lease
claim, correctly declined by the engine) and is reported as UNMEASURED, not as a negative; the re-run
is what carries the verdict.

## What shipped

- `scripts/mcp_spine_server.py` — the door. Wraps `checklist_engine.main(argv)`; `git diff` against
  the engine is **empty** for the whole workstream.
- `.mcp.json` — project-scope config using `${VAR:-default}` expansion, so identity comes from each
  caller's environment at server launch.
- `tests/test_mcp_spine_server.py` (21), `tests/test_mcp_identity.py` (12),
  `tests/test_mcp_imperative_equivalence.py` (5).
- **`scripts/gen_mcp_config.py` — REMOVED.** See below.
- `docs/CHECKLIST_ENGINE_DESIGN.md` — new section "A second front door: the MCP server", carrying the
  tombstone and a do-not-reintroduce-on-identity-grounds warning.

**Closing regression:** all 38 tests F shipped, run together, green. **Full suite: 2177 passed,
1 skipped, 1061 subtests, 0 failed.** The old six-failure pin is retired and re-derived as empty on
this tree.

## The two findings that changed the shipped surface

**1. `gen_mcp_config.py` was removed, and the measurement everyone expected to save it is what
killed it.** The gate was blocked by its own reviewer on the *justification*, not the code. Two
measurements resolved it: a committed project-scope `.mcp.json` already keys identity per dispatch
through `${VAR}` expansion (two dispatches, one directory, one config, each returning its own
unguessable nonce, corroborated server-side); and DC3's open question — does an in-session Task-tool
subagent share its parent's already-launched server? — measured **YES**. That YES was the last
argument for keeping generation, and it does not survive: a generated config binds at server launch
**per process** exactly as `${VAR}` does, so it names a case *neither* mechanism reaches. Removal
went through the gate's own rework path, and the same reviewer that blocked returned APPROVE after
re-reproducing the measurement itself.

**2. DC5 passed, but not for the reason the workstream assumed.** The premise was that a typed door
absorbs malformed calls. There were none to absorb — zero in both arms, on an instrument whose
controls prove it can score them. What the door actually bought was that nobody had to read a manual.
Against that, a typed tool call carries one verb and cannot batch, so the door costs roughly **1.8×**
as many composed tool calls as a shell chaining several invocations per command.

## No gate left blocked by its own reviewer

Four reviewer BLOCKs across the run. **All four resolved on evidence; none overridden, none waived.**

| Gate | Block | Resolution |
|---|---|---|
| `g1-integrate` | Justification for `gen_mcp_config.py` does not hold | File removed; re-reviewed; APPROVE |
| `g4-review` #1 | A shell `for` loop scored six engine invocations as one — `rep2-cli` was 23/7, not 18/2 | Scorer fixed; this **flipped DC5 from negative to pass** |
| `g4-review` #2 | The verdict was kept anyway, on a decomposition reached for only after the pre-registered metric flipped | Verdict changed to PASS; the decomposition demoted to a labelled secondary observation |
| `g4-review` #3 | A leftover duplicate paragraph and an order-control claim its own arithmetic did not support | Both fixed; APPROVE |

The second one is the one worth carrying up: **I had written a conclusion and was finding routes back
to it after the evidence moved.** Neither correction came from me. `MEASUREMENT.md` records the whole
sequence — negative, blocked, still negative, blocked again, now pass — rather than presenting the
final verdict as if it had been the first.

## Deviations from the order, each stated

- **Gate order.** Ran `g3 → g1-integrate → g2 → g4` as instructed. The engine cannot express
  "resolve a blocked gate on a later gate's evidence" (a blocked gate holds the active slot and
  `amend` cannot move it), so g3's implementer ran as the named blocker-clearing evidence, then the
  pending tail was reordered by `amend` under the launch order's authority.
- **`execute.c2`'s command was retexted** (not waived) because
  `verify_iterative_role_artifacts.py --work-id epic-418-followon/commander-424` refuses any
  multi-segment work-id before verifying anything. The replacement runs the **same** G2 verification
  on an explicit path. That guard was masking a real defect: the inherited packet had
  `completed_outcomes` as strings where objects are required. Repaired and verified.
- **Two stale handoff baselines corrected** before dispatch: the g2 and g3 handoffs still named the
  retired six-failure pin. Both now state the measured green baseline and a `0 failed` bar.

## Triage: 9 candidates, all recommend-and-defer

Nothing filed — the launch order grants no issue-filing authority. Nothing fixed — the same order
routes cheap fixes rather than implementing them inside a wave under measurement, and T7/T8 are
deferred on that basis despite clearing all four fix-now rungs. Full recommendations in
`triage-candidates/TRIAGE.md`.

The pattern worth the Admiral's attention: **T1 and T2 are the same defect in two different tools** —
`run_crew.py` and `verify_iterative_role_artifacts.py` both assume a work-id contains no `/`, and the
epic/commander convention always gives it one. T1 silently converts completed crews into
apparently-running ones; T2 refuses a check before it can run.

## Replan packet

`REPLAN_INPUT.json` verifies against the G2 schema, carrying 1 completed outcome, 8 wave-evidence
entries and 10 classified discrepancies. No discrepancy was auto-filed.
