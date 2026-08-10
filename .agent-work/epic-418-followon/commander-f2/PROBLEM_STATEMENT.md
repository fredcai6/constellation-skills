# Problem statement — commander-f2 (#542 adoption, #541 friction capture)

Delegated run. No reachable human; the Admiral is the reachable tier. The frozen
`LAUNCH_ORDER-F2-mcp-adoption.md` is the source of truth, reconciled below against the
code as it actually stands on `abad896d`.

## The ask, in one line

The MCP front door from F (#424) is built, merged and unused. Make agents drive through
it, and make the door confess its own friction while they do.

## Reconciliation against the order's assumed baseline

Three of the order's premises were re-derived rather than taken on trust. Two hold
exactly; one needs a correction that narrows the defect.

**Holds — the three adoption counts are all zero.** Re-derived here, and they will be
re-measured at g4 as proof they moved:

| Count | Order says | Measured on `abad896d` |
|---|---|---|
| Files under `skills/` referencing the door's tools | 0 | **0** (`grep -rlE 'spine_status\|spine_lease\|spine_start\|spine_advance\|spine_evidence\|spine_halt\|spine_survey_result\|mcp__spine__' skills/` → exit 1, no output; 101 files under `skills/`) |
| MCP references in `scripts/install_constellation.py` | 0 | **0** (`grep -ciE 'mcp'` → `0`) |
| Agents actually driving through it | 0 | **0** — no role template, SKILL body or reference names the door |

The corpus has no knowledge of the door at all. Not a stale mention, not a "coming
soon": zero.

**Holds — `gen_mcp_config.py` is gone and its removal is settled.** The tombstone at
`docs/CHECKLIST_ENGINE_DESIGN.md:303-312` scopes itself precisely: *"Do not reintroduce
per-dispatch config generation on identity grounds without new evidence."* g3 must
therefore be careful to be a different thing, and to say so: installing one
project-scope `.mcp.json` into a target project at install time is neither per-dispatch
nor on identity grounds. `${VAR}` expansion stays exactly as it is, and is what keys
identity. If g3's design ever drifts toward minting a config per dispatch, it has
crossed the tombstone and must stop.

**Needs correction — #541's mechanism.** The order says the door "absorbs the fumbles
that used to land in a transcript where someone could read them" and asks that the
server's rejections be captured. Read against the code, that is half true, and the
half that is false is the half that would have been built for nothing.

- **Engine refusals through the door are already captured.**
  `mcp_spine_server.run_engine()` calls `checklist_engine.main(argv)` in-process, and
  `main()` increments `refusals` at `checklist_engine.py:3319-3321` inside its
  `EngineError` handler and inside the persistence guard. `episode_capture.py:430-432`
  reads that counter into the `## Mechanical` block, which
  `apply_episode_delta.py` requires on every `create`. That chain is intact and needs
  no work.
- **The door's own rejections are captured nowhere.** Every `_tool_error(...)` return
  in `call_tool()` short-circuits before `run_engine()`, so it reaches neither the
  engine's counter nor the server's own `mcp_calls.jsonl` (`_log()` is called only from
  `run_engine()`). Four classes take this path: unknown tool name; unknown `action` on
  the four multiplexed tools; missing required argument (`_require`, 8 sites); and — the
  sharpest — a **client-side schema rejection**, which never reaches the server process
  at all.

So the honest statement of the defect is narrower than the order's framing and, being
narrower, is actually measurable: *the door answers some calls itself without consulting
the engine, and exactly those answers leave no trace in any store, while the engine's
refusals through the same door already do.* One door, two rejection classes, one mute.

This correction matters against F's own DC5 result, which measured **zero** malformed
calls in both arms. Instrumenting "the door absorbing fumbles" would be instrumenting a
phenomenon already measured at zero. Instrumenting the door's own silent answers is a
real gap regardless of what the fumble rate turns out to be.

## What "done" means (the order's four criteria, plus g1's)

1. Role spine instructions name the door's tools as the default path, CLI documented as
   the remaining fallback. **The CLI stays** (`decision:the-cli-door-stays`) — an edit
   that removes it fails the gate.
2. A real dispatched agent drove a real role spine to done through the door alone,
   measured **from its own call record**, never the server log
   (`decision:count-from-the-call-record`).
3. `install_constellation.py` ships and wires `.mcp.json`, so a fresh install gets the
   door.
4. The server's own rejections land in the run's episode through
   `apply_episode_delta.py`, and say so **loudly, every turn**, when they cannot
   (`decision:fail-loud-every-turn`).
5. The identity trade is decided and the property given up is written down
   (`decision:identity-trade-is-recorded`).

## Constraints that bind every gate

- **Never duplicate engine logic.** The server wraps the engine's own dispatch;
  `git diff` against `checklist_engine.py` was empty for all of F. It stays empty.
- **Episodes are records, not rules.** Nothing written under `episodes/` may be phrased
  as guidance for a future agent (`ORCHESTRATOR_CONTEXT.md` "The Retired Learning
  Playbook"; `decision:episodes-are-records-not-rules`).
- **Write `episodes/` only through `apply_episode_delta.py`**, with `--store-root
  episodes` on every invocation.
- **Never write `settings.json` at user scope.**
- **Zero is a result.** If the acceptance run produces zero rejections, report zero; do
  not manufacture friction, and do not read zero as proof the capture works — that needs
  a seeded-rejection control (`decision:zero-is-a-result`).
- **An UNMEASURED condition is not a measured negative** and will not be reported as one.

## The risky unknown, settled first

The identity **composition**: the Task-tool harness shares the process, and the door
puts identity in the process (`mcp_spine_server.py:113-115`, module-level constants at
import, no tool taking a spine path). Two agents on one lease is the exact failure
engine session leases exist to prevent. If a subagent-dispatching role cannot safely use
the door, then editing role spine instructions to default to it is the wrong edit — so
this is settled at g1, before anything is written against it.

## Open questions this run must settle and record

- g1: which of the three identity options, and the property given up.
- g2: per-call granularity vs a summary at lease release; whether the CLI arm gets the
  same instrumentation (without it, future DC5-style measurements compare an
  instrumented door against an uninstrumented one); whether an immediately-corrected
  rejection weighs the same as an unresolved one.
- g3: how an installed `.mcp.json` names the installed door and engine, given the
  installer today writes no project-root dotfile of any kind and its `.mcp.json` source
  uses paths relative to this repo.
- g4: which role spines change and in what order; how the acceptance run is staged.

## Known map gap

`map_orient.py` returns DEGRADED-UNPARSEABLE on this base — `map/ids.jsonl` is empty and
`map/INDEX.md` is an unfilled template, so there are no structural anchors for any
surface this run owns. Discharged on the record with hash-pinned substitutes and
escalated to the Admiral as a standing epic-wide condition. Blast radius for this run was
derived from source reads and F's archived evidence instead, and that substitution is
declared rather than hidden.
