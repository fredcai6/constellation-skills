# Problem statement — #424, workstream F, MCP front door

Reconciled against the frozen `LAUNCH_ORDER-424.md` and the governing spec
`.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md` section F (lines 408–546, CONFIRMED
2026-08-07). No human was interrogated; delegated mode.

## The ask

Put a second front door on the checklist engine: an MCP stdio server exposing the drive loop as
roughly seven typed tools that wrap the engine's own `main(argv)` dispatch. The CLI door stays; F is
additive.

## What it is for

Cleave problem-solving from spine-management. The cost being removed is *attention*: an agent
fumbling a flag, reading usage, or working around a gate that refuses wrongly pays that cost out of
the budget it needed for the real work. The door moves the fumble to the far side of an interface.
**The token delta is a constraint that must not go the wrong way — it is not the thing being
bought.** Measuring token savings as the acceptance test measures the wrong thing (spec F, lines
429–443).

## Protected intent — what must survive

1. **No engine logic is duplicated.** The server wraps `checklist_engine.main()`. Refusals, rails,
   recovery hints, the journal and lease enforcement ride through unchanged.
2. **The gate imperative rides tool results verbatim.** Spine templates stay the single source of
   instruction text. No second rendering path.
3. **The CLI door stays**, and every uncovered verb keeps a documented CLI fallback.
4. **`settings.json` is never written at any scope.** Project-scope `.mcp.json` only.
5. **Each agent gets its own server instance**, keyed by `session_id#agentId`.

## Baseline reconciled against the actual code (not the order's framing)

- **The two-flavoured `advance` does not exist.** A2 (#467) shipped the line *between verbs*:
  `TRIP_HARD_GUARDED_VERBS = {start, reopen}`. `docs/agents/GLOSSARY.md` already states this
  ("HARD refuses the verbs that BEGIN work at a gate — `start` and `reopen`"). I type what the
  engine has. #424's body predicted otherwise and is superseded.
- **The engine exposes 18 verbs**: `current, claim, heartbeat, release, start, advance, record,
  consolidate, skip, block, resume, reopen, append, amend, attest, waive, attach, flag-candidate`.
  The prototype's 7 tools cover 11 of them. `heartbeat, skip, reopen, append, amend, waive, attach,
  flag-candidate` are uncovered and need either coverage or a documented CLI fallback.
- **`archive.c2b`'s `<branch>` placeholder (#439) is already fixed** in the spine template I am
  running: the check resolves the branch via `git rev-parse --abbrev-ref HEAD` and accepts OPEN or
  MERGED. This is one of the four "ordinary engine bugs" F was told to hold constant — it is
  already constant, fixed before both arms.
- **`docs/agents/engine-config.json` does not exist** in this repo. Recorded as a substitution at
  the context step, not treated as a missing prerequisite.
- **No architecture map exists** (`docs/architecture/` absent). `map_orient` returned
  DEGRADED-NO-MAP; discharged with five hash-pinned substitutes, two unmapped statements and an
  escalation. F introduces the first MCP surface in this repo, so there is no prior anchor to hang
  it on.

## The six done-conditions I owe a verdict on

| # | Condition | How it is decided |
|---|---|---|
| DC1 | Cold agent reaches done on a real role spine through the door, zero malformed calls | Smoke test only; close to true by construction once typed. Kept, not leaned on. |
| DC2 | Separation: parent and subagent drive two different spines at once, own server instances, leases never collide | Two concurrent instances, two spines, distinct readings. |
| DC3 | Inheritance fails closed: an unconfigured subagent gets a refusal or no identity, never the parent's lease | **Requires a positive control** — prove the door is up and serving first, else non-installation passes the test most loudly. |
| DC4 | Same-gate equivalence as a **property over every gate carrying an imperative**, checked mechanically | Not one sampled gate. Drift happens at the gate nobody sampled. |
| DC5 | Spine-management cost falls, attributably to the door | Counted **from the call record**, never the engine's refusals counter (#427 undercounts in the direction that flatters F). CLI baseline **re-measured**, not reused from exc-9. Far-side recovery events counted too. Only fumble classes a typed interface can absorb; engine-bug fixes held constant across arms. |
| DC6 | The governor's threshold instruction arrives through a tool result and is acted on | From A2. |

## Live positive control already in the tree (inherited fact)

DC3's failure is currently observable without manufacturing it: two spines in this run's session both
carry session `86708414-f5d3-40d3-8c9a-2f96d1ccdc14`, differing only in the free-text `claimed_by`
field. Inheritance does not fail closed today. The control detects a real defect, not a planted one.

## Pre-build branch point I own

`decision:mcp-probe-is-the-commanders` — does an interactive session pick up a fresh `.mcp.json`
without a restart? Picked up → project-scope `.mcp.json` suffices. Not picked up → per-dispatch
config generation is the delivery path and gets designed first. I run this probe and report the
branch.

## Out of scope

Gold-plating the tool grouping (MCP is the vehicle, not the destination — the seven-over-eighteen
split is an explicit placeholder). Fixing the six pinned red tests (not mine; a concurrent agent owns
them). Editing `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
`tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py`
(fenced to the posix-green agent).

## Honest-null clause

A measured negative on DC5 is a complete, successful deliverable and gets reported with the same
rigor as a win. The spec already fixes the mitigation: the CLI door stays, so a failed F costs the
build and not the fleet.
