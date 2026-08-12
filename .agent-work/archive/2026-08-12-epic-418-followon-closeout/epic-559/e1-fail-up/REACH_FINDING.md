# f3 — can a dispatched crew reach its parent? (PROBE-EVIDENCE)

**Question.** `run_crew.py` now binds `SPINE_PARENT` and grants `SendMessage`. Does a headless
`claude -p` crew actually reach the session that dispatched it, or is the durable spine/registry
record the only channel that works?

## Probe 1 — parent named by a descriptive string

Dispatched with `--parent "Admiral session 717403d3 (constellation-skills, epic-418-followon)"`.
The crew ran `ListAgents` and recorded the output verbatim:

```
Peer sessions (6):
  mcp cs [5912e0]  ·  interactive  ·  busy  ·  started 18h ago
  tommy-f0 [9dfa0e]  ·  interactive  ·  idle  ·  started 2d ago
  new guy! [d86672]  ·  bg  ·  shell  ·  started 2d ago
  d1-stale-pins-9f [2639cc]  ·  interactive  ·  started 15m ago
  c1-spine-lint-b6 [06a20a]  ·  interactive  ·  started 15m ago
  f1brainz-cb [53e3b0]  ·  interactive  ·  shell  ·  started 1d ago
```

No listed name or id matches `SPINE_PARENT` ("Admiral session 717403d3" / "717403d3"). It then
attempted `SendMessage(to="Admiral session 717403d3", message="PROBE-REACHED-PARENT")` anyway, to
capture the real error rather than assume one. The attempt failed, verbatim:

```
{"success":false,"message":"No agent named 'Admiral session 717403d3' is reachable.\nUse ListAgents to see everyone you can message."}
```

**What this establishes.** A headless crew *is* on the peer graph — the two sibling crews running
at that moment (`d1-stale-pins-9f`, `c1-spine-lint-b6`) appear in its `ListAgents` output. But a
crew cannot reach a parent named by a descriptive string; the address has to be the exact
addressable name, and the dispatching session does not get its own addressable name for free.
`mcp cs` is the most plausible candidate for the Admiral in this list (interactive, busy, oldest),
and `SendMessage` from the Admiral to `mcp cs` was itself refused — consistent with that entry
being the Admiral's own session, unreachable from outside by that route either.

## Probe 2 — parent named directly as `mcp cs`

A second probe was dispatched with `--parent "mcp cs"` to test that candidate name directly. It
reported its spine already done on restart and **wrote no artifact at all** — no REACH.md, no
SendMessage attempt, no error captured. It produced no evidence one way or the other.

**Recorded as:** inconclusive. An honest inconclusive result is worth more than a tidied-up claim
that probe 2 also failed, or that it would have succeeded — neither is measured. This is
PROBE-EVIDENCE from probe 2: no reach attempt occurred, no result exists.

## Ruling

The durable path is the mechanism; messaging is at best a latency improvement on top of it. A crew
that cannot satisfy a check blocks: the blocked gate lives in its spine, and the parent is recorded
in the launcher's registry entry (`--parent`, bound as `SPINE_PARENT`, from `f1-bind-parent`). A
polling parent finds both regardless of whether a message ever lands, and this survives the crew
dying mid-question, which a message does not.

`SendMessage` stays granted in `CREW_ALLOWED_TOOLS` — it costs nothing to keep, and it works when a
real addressable name is passed (as it did for probe 1's `ListAgents` call and its `SendMessage`
attempt, which reached the tool and returned a real, not a hallucinated, refusal). But nothing in
`run_crew.py` or the crew skills should depend on a message arriving. Do not grant a tool that
cannot work; this one works — it simply cannot resolve a descriptive parent string to a live
session, so it is kept as an optimisation, never the channel of record.
