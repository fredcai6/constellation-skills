# notes-1 — commander-f2 (#542 adoption + #541 friction capture)

Work-id `epic-418-followon/commander-f2`. Worktree
`/home/tommy/projects/constellation-skills-wt/f2-mcp-adoption`, branch
`epic-418/f2-mcp-adoption`, base `abad896d`.

## Bootstrap floor (done, in order)

1. `cd` into the worktree.
2. `init_work_area.py epic-418-followon/commander-f2 --spine
   skills/commander/templates/COMMANDER_SPINE.template.json`, then
   `checklist_engine.py --file <spine> claim --session epic-418-followon/commander-f2`
   → `claimed lease epic-418-followon/commander-f2 -> active`, exit 0.
3. Proof-of-life reported.

Isolation, verified by me, not taken on trust:

```
$ python scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
worktree OK: in /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
EXIT=0
```

Suite baseline re-derived on this branch with `python -m pytest` (NOT `python3`):
**2267 passed, 1 skipped, 1079 subtests passed, 0 failed**, 101s. Matches the launch
order exactly. Every command in this run is redirected to a file and its own `$?`
captured — never piped into `head`/`tail`.

## Reconciling the order's assumed baseline against the code

The order is right about the shape and slightly off about the mechanism on #541. The
correction narrows the defect, and narrowing it is what makes it measurable.

**What already works.** `mcp_spine_server.run_engine()` calls
`checklist_engine.main(argv)` in-process. `main()` counts a refusal at
`checklist_engine.py:3319-3321`, inside its `EngineError` handler and inside the
persistence guard. So an **engine** refusal arriving through the door already
increments the spine's `refusals`, already gets persisted, and already reaches the
episode: `episode_capture.mechanical_fields()` reads `checklist["refusals"]`
(`episode_capture.py:430-432`) into the `## Mechanical` block that
`apply_episode_delta.py` requires on every `create`.

That path is not broken and does not need building. Saying so is the difference
between a repair and a rewrite.

**What is genuinely silent.** Every `_tool_error(...)` return in
`mcp_spine_server.call_tool()` short-circuits **before** `run_engine()`. It therefore
touches:

- not the engine's `refusals` counter (never entered `main()`),
- not `mcp_calls.jsonl` (`_log()` is only ever called from `run_engine()`),
- not the journal, not the spine file, not the episode.

The rejection classes that take this path today:

| Rejection | Site | Reaches engine? | Recorded anywhere? |
|---|---|---|---|
| unknown tool name | `main()` `tools/call` branch | no | **no** |
| `spine_lease` / `spine_evidence` / `spine_halt` / `spine_survey_result` unknown `action` | `call_tool` | no | **no** |
| missing required argument (`_require`) | `call_tool`, 8 sites | no | **no** |
| client-side schema rejection (`additionalProperties: false`, missing `required`) | the *client*, before the server is spoken to | no | **no** |

That last row is the sharpest one and is the reason
`decision:count-from-the-call-record` exists: a schema rejection never arrives at the
server at all, so no server-side instrument can ever see it. Any capture that lives
only in the server is structurally blind to it.

**So the honest statement of #541's defect** is narrower than "the door absorbs
fumbles": *the door's own rejections — the ones it answers itself, without consulting
the engine — leave no trace in any store, while the engine's rejections through the
same door already do.* One door, two rejection classes, one of them mute.

This matters against F's DC5 result, which measured **zero** malformed calls in both
arms. A capture built on the assumption that the door is busy absorbing fumbles would
be instrumenting a phenomenon already measured at zero.

## The store constrains where a rejection can land

`docs/EPISODE_STORE.md` §4 and `apply_episode_delta.py:162-178`: the `## Mechanical`
bin is a **closed allowlist** — `run`, `project`, `role`, `spine-step`,
`context-manifest-ref`, `refusals`, `reopens`, `rework-count`, `failed-commands`,
`artifact-ref`. `_validate_create` rejects any key outside it as misfiled. So "which
field does a door rejection land in" is a real design question with three candidates
(fold into `refusals` / add a mechanical field / carry it as an agent-supplied
observation), not a free choice. Settled at g2, recorded there.

Binding doctrine, from `ORCHESTRATOR_CONTEXT.md` "The Retired Learning Playbook" and
matching `decision:episodes-are-records-not-rules`: an episode is a record of what
happened and is **never read back as a rule**. Nothing this run writes into
`episodes/` may be phrased as guidance for a future agent.

## g1 — the identity composition, as the code actually has it

`mcp_spine_server.py:113-115` reads `SPINE_ENGINE`, `SPINE_FILE`, `SPINE_SESSION` as
module-level constants at import. No tool takes a spine path. One process = one server
= one spine = one identity, for the life of the process.

`tests/test_mcp_identity.py:533-627` (`DC3InheritanceMechanismTests`) proves the
**environment** seam fails closed: a sibling process launched with no configuration
gets no identity and crashes naming `SPINE_FILE`, never the parent's reading, with the
parent's door asserted up throughout and a leak counterfactual proving the assertion
is not vacuous. Its docstring is explicit that the **harness** seam — whether the
Task tool reuses an already-connected client object inside one process — is "a
product-internal mechanism with no observation point reachable from a subprocess-level
test."

The order records that the harness seam measured **YES**. So the composition is:
harness shares the process, we put identity in the process, and the result is two
agents on one lease — the exact failure engine session leases exist to prevent.

The option set and what each costs is argued at g1 and recorded there. One
observation that shapes it and belongs here: **the CLI already is the per-call
identity door.** It takes `--file` and `--session-id` on every invocation. Moving the
spine path to a per-call argument on the MCP door would not add a capability the repo
lacks; it would delete the one property that distinguishes the two doors, and leave us
with two copies of the same door.
