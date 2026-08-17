# Mission Frame

Shrunk per template allowance: this repo has no `docs/architecture` packet map (context step returned
DEGRADED-UNPARSEABLE, discharged with file-path substitutes) and this is a bounded, small,
mostly-mechanical text/doctrine change once the fence is applied. No `struct:`/`capability:`/`decision:`
node ids exist to cite; anchors below are the substitute file paths the context step hash-pinned.

## Intent
Make the Stop hook's mid-flight refusal (`scripts/hooks/spine_rail.py`) state explicitly that it
outranks the context-trip advisory, and point an agent who must honestly exit mid-gate at
`spine_halt block` rather than at a turn-end handoff the Stop hook will refuse. State the same
precedence in shipped skill doctrine (`skills/commander/references/crew-dispatch.md`) so a Commander
reads it before hitting the fork live.

## Scope reduction (load-bearing finding, not a map fact)
`#442`'s two problem instances (the `RAIL:` banner text and the HARD refusal's `attach ... refresh-request`
remedy string) and `#595`'s context-trip SOFT advisory text ("hand off here… advisory — decline with a
reason if you're nearly done") are ALL authored in `scripts/checklist_engine.py`
(`_RAIL_STRINGS`, `_trip_advisory`), which the launch order fences to Lane A this wave and which the
file itself marks FROZEN/verbatim ("do not paraphrase" — a measurement precondition for #145).
`scripts/hooks/spine_rail.py`, my sole-owned file, contains only the Stop hook's own `SPINE MID-FLIGHT`
refusal text (`_mid_flight_reason`) — that is the only piece of either issue's target text I can
legally edit this wave. This is floated to the Admiral (see `notes-c.md` and `RETURN.md`); the plan
below is scoped to what remains in latitude.

## Affected Capabilities (file-path substitutes, no map ids)
- `scripts/hooks/spine_rail.py` — the Stop hook (`decide_stop` / `_mid_flight_reason`): refuses a
  mid-spine turn-end. In scope: add the precedence statement + `spine_halt block` pointer.
- `skills/commander/references/crew-dispatch.md` — shipped doctrine a Commander reads before crew
  dispatch. In scope: state Stop-hook-outranks-advisory explicitly (pre-ruling names this file).
- `scripts/checklist_engine.py` — `_RAIL_STRINGS` (RAIL banner + HARD refusal remedy) and
  `_trip_advisory` (SOFT advisory wording). OUT OF SCOPE this wave: fenced to Lane A.

## Structural Anchors
- `scripts/hooks/spine_rail.py:1479-1520` (`_mid_flight_reason`, `_owning_session_reason`)
- `skills/commander/references/crew-dispatch.md` (crew dispatch doctrine, shipped skill source —
  canonical per `skills/_shared/global-*.md`, never `skills/<role>/references/global-*.md`)

## Governing Constraints / Assumptions
- Fence: sole writer this wave of `scripts/hooks/spine_rail.py` and rail/refusal/advisory strings
  wherever authored, EXCEPT `scripts/checklist_engine.py` / `scripts/mcp_spine_server.py` (Lane A).
- `decision:trip-mechanic-untouched` — change what the hook *says*, never *when* it fires.
- `decision:in-session-observation-is-not-evidence` — hook code runs from the MAIN checkout; validate
  the edit in a fresh subprocess with `CLAUDE_PROJECT_DIR` pointed at this worktree, not in-session.

## Decision Anchors & Decision Pressure
- `decision:stop-hook-is-authoritative` — the Stop hook outranks the context-trip advisory; already
  ruled by the launch order.
  `@grade: settled/human · leans g1-implement`
- `decision:no-third-mechanism` — do not invent a new advisory surface; subordinate one of the two
  existing mechanisms in shipped text instead.
  `@grade: settled/human · leans g1-implement`
- decision pressure: whether stating precedence in `spine_rail.py` + `crew-dispatch.md` alone (without
  touching the SOFT advisory's own wording in the fenced `checklist_engine.py`) is a sufficient
  "settled in shipped text" deliverable for #595, or whether the Admiral wants the advisory's own
  wording changed too once Lane A's fence lifts — surfaced to the Admiral, not decided here.

## Claims / Evidence Surfaces
- The two 2026-08-15 episodes (`launcher-hygiene-002`, `stop-hook-door-binding-002`) are the evidence
  that the fork is real and costly; read, not re-derived.
- Fresh-process validation of the `spine_rail.py` edit (subprocess with `CLAUDE_PROJECT_DIR` set to
  this worktree) is the re-confirmation this run owes per the fence.

## Map Confidence / Staleness / Disputes
- No packet map exists for this repo; N/A beyond the DEGRADED discharge already recorded at context.

## Out of Scope
- Any edit to `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py` (Lane A's files this wave).
- Redesigning the trip mechanic (when it fires).
- Filing issues (write triage candidates only, per pre-ruling `decision:no-issue-filing`).
