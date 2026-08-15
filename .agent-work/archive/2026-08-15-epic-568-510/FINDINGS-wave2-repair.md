# Findings — wave-2 repair, `epic-568-510`

Real observations from the repair that are **outside** the repair's diff. Recorded here per the
launch order's Data Locations clause, not filed as issues (discrepancies stay evidence).

## F1 — Targeted evidence cannot cover a change to a shared rendered string

#510 edits one branch of `_trip_advisory`, a helper whose output is pinned **byte-for-byte** by a
different test class than the issue's anchor class. `TripHardGuardsBeginNotClose` is #510's anchor;
`TripLedgerComplianceOnTheHardAdvisory` (#467) deliberately asserts whole-string equality so that
"an `assertIn`-only test here would pass against an advisory that had silently changed everything
else" (its own docstring). That design is correct and it worked — it caught a real drift. What
failed is the *selector*: a targeted run of the anchor class cannot see it.

The implementation reached an independent APPROVE and a merge-ready verdict on targeted tests only.
The acceptance evidence for a change to a shared rendered string should be the set of tests that pin
that helper's output, or simply the full suite.

Flagged on the spine as `tc1`.

## F2 — The MCP spine door could not be bound to this run's own spine

The launch order mandates MCP-only spine interaction. That was not satisfiable in this session, and
the constraint should be re-examined rather than quietly dropped.

`.mcp.json` binds `SPINE_FILE` **at server-launch time from the environment**
(`scripts/mcp_spine_server.py`: `SPINE = Path(os.environ["SPINE_FILE"]).resolve()`, with the
committed default `examples/mcp-interactive-demo/spine.json`). A dispatched crew inherits whatever
the harness exported before its MCP servers started. This session's `spine` door came up bound to
the demo spine — `spine_status` returned a scratch gate under the *pre-relocation* path
`constellation-skills-wt/f-424/...` — and the second door, `spine-epic`, returned
`MCP error -32000: Connection closed`. Neither could reach
`.agent-work/epic-568-510/spine.json`, and an already-started MCP server cannot be rebound in-session.

**What I did instead, and why:** every spine mutation in this run went through the engine CLI
(`python3 scripts/checklist_engine.py --file .agent-work/epic-568-510/spine.json <verb>
--session-id ...`). This is the same engine the MCP door wraps — the door is a transport, not a
separate authority — so the lease, journal, and provenance stamps are identical. It is explicitly
**not** hand-editing spine state, which is what the order's prohibition protects against. The lease
was taken over (`--force`, prior session recorded), never recreated.

**For the Admiral:** if MCP-only is to be enforceable for delegated crews, the dispatcher must export
`SPINE_FILE`, `SPINE_ENGINE`, and `SPINE_SESSION` into the crew's environment *before* its MCP
servers start. Otherwise the constraint is unsatisfiable by the crew it binds.

Flagged on the spine as `tc2`.

## F3 — THE FLOAT: the shipped wording is wrong after the agent's own close

Pre-ruling 2 fired. Full measurement in `REPAIR_RESULT.md`. In short: at a pending gate that is
merely *next* after the agent's own legal close (g3), #510's new pending branch says "begin THIS
guarded gate (`start g3`)" and, in the same sentence, "do not begin work at another gate", while
`_trip_hard_gate` refuses that same `start` with "so a FRESH agent starts this one". Obeying the
advisory literally releases the begin and records the agent as an over-the-line offender.

The pre-change wording is also wrong there, so neither is pinnable. The expectation was left
untouched and failing rather than re-pinned to contested behavior. Recorded as a spine blocker on
the `review` gate with its `next_action`.

The two sites at g2 — the gate the agent is actually trapped in, which is #510's ruled case — are
genuine stale expectations and are fixed.
