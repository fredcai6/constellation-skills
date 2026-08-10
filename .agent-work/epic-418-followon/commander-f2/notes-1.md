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

---

# CORRECTION — the map is present. I reported a tool's guess as an observation.

I told the Admiral the map was absent epic-wide. It is not. `map/INDEX.md` is 23855 bytes
covering **132 modules and 4848 entities**, with a per-module `INDEX.md` under each, and
`tests/test_code_map.py::MapTreeFreshnessTests` asserts it is byte-identical to a fresh
build. It names every surface this run owns:

```
scripts.mcp_spine_server      8 entities,  5 holes
scripts.install_constellation 81 entities, 30 holes
scripts.apply_episode_delta   54 entities, 25 holes
scripts.episode_capture       15 entities
scripts.checklist_engine     106 entities, 25 holes
```

**What actually happens** is that `map_orient`'s `ANCHOR_RE` accepts only
`struct:` / `capability:` / `event:` / `constraint:` / `assumption:` / `claim:` /
`decision:` tokens — the vocabulary of a hand-written architecture packet. A generated
code map contains none of them by construction. #536 taught the probe where to look and
did not teach it what it would find, so it now reaches the right file and rejects it.

**How I got it wrong, stated plainly because the mechanism is the lesson.**
`map_orient.py:447` returns the literal string `"content but no citable anchor id
(unfilled template?)"`. That parenthetical is a *guess about the file's state*, printed
inside a verdict. I read it, believed it, and repeated it one tier up as an observation
without opening the file. A tool that reports a defective world and a healthy one alike,
plus a plausible explanation that makes checking feel unnecessary — which is the exact
failure class this epic exists to catch. The Admiral measured it and corrected me; filed
as **#548**.

Receipt re-issued with `map/INDEX.md` hash-pinned as a substitute I genuinely read. The
run stays DEGRADED, but for the true reason: **the orientation tool cannot parse a code
map**, not because a map is missing. `map_orient` is not repaired inside this wave.

# g1 reframed: identity when the harness shares the container

The Admiral found the same defect in a **second, independent seam** while I was working
(#549). `spine_rail.py`'s binding file *is* keyed per agent — #419's fix works — but
`session_view()` merges the bare `sid` key and every `sid#<agent_id>` key into one flat
map, and `decide_stop` takes the first non-foreign entry. The discriminator exists and a
merge two functions later discards it. The second guard cannot save it: `_foreign_worktree()`
compares against a recorded `worktree` that every child entry inherited from its parent,
because `CLAUDE_PROJECT_DIR` resolves once at session launch (#269).

Same shape as mine, twice, neither aware of the other: **the harness shares the container,
and we put identity in the container.**

So g1's deliverable is not "is the door's env-binding right." It is a **fleet-wide
position on identity under a shared container**, which must say whether it applies to the
hook seam or explicitly does not. The constraint that makes this sharp: **the hook seam has
no per-call argument to fall back to.** A Stop hook receives what the harness hands it. So
any answer of the form "move identity to the call" has to say what a seam *without calls*
does instead — and that is the argument that decides g1. `spine_rail.py` is #549's and
outside my fence; g1 cites it and repairs nothing.

# g2's landing site — settled at plan time, not left to a Sonnet implementer

The cold critic caught that I had left this open. It is settled now.

The Mechanical bin is hardcoded at `apply_episode_delta.py:166-178` as scalars and ints.
A **record per rejection is unrepresentable there**. And `apply_episode_delta.py`,
`episode_capture.py` and `docs/EPISODE_STORE.md` are all **outside this run's file
ownership** — extending the allowlist is neither in my latitude nor in my float list.

**Decision:** the door writes one record per rejection to a door-side JSONL beside the
spine, and the run's episode carries it as an **`artifact-ref`** line — already in the
Mechanical allowlist, already list-shaped (`MECHANICAL_ALL_FIELDS = MECHANICAL_SCALAR_FIELDS
+ ("artifact-ref",)`), already produced by `episode_capture._artifact_refs()`. Full
per-rejection granularity survives in the referenced artifact; the store contract is
untouched; no unowned file is edited.

Rejected, with reasons: overloading `refusals` (the engine's own counter — a second writer
makes one field disagree with its own source); overloading `failed-commands` (counts engine
`command` checks; wrong semantics); extending the allowlist (unowned files, store-contract
change).

**The CLI arm does not get the same instrumentation this run,** and the reason is
structural rather than budgetary: a CLI shape rejection exits inside `argparse` *before*
`load(path)` runs, so the engine does not know which spine was meant and there is no run to
attribute it to. The door always knows, because its spine is bound at import. The
comparability cost for future DC5-style work is recorded here rather than paid.

# Cold critic triage — 6 BLOCKING, 8 SHOULD-FIX, 3 NOTE

Every BLOCKING finding is taken. The critic was right on all six, and two of them
(#1 and #6) were the same disease the launch order warns about, in my own plan.

| # | Finding | Disposition |
|---|---|---|
| 1 | g4b never reads the CLI-invocation count its own reused scorer produces; `reached_done` is one-sided | **Taken.** g4b now closes on `assert_acceptance.py`, which refuses unless `reached_done` AND zero CLI engine invocations |
| 2 | No gate checks the chosen spine can be driven through the door at all | **Taken.** Spine decided at plan time (`IMPLEMENTER_PLAN.template.json`); verb-coverage check is an explicit g4b constraint |
| 3 | g1's only check is green before the gate starts, and its evidence anchor pre-decided the trade | **Taken.** The trade is now a six-item frozen list the reviewer verifies item by item; the pin is explicitly outcome-neutral |
| 4 | g2's store-contract decision left open for a Sonnet implementer, against unowned files | **Taken.** Settled above, and carried as a constraint that says do not reopen it |
| 5 | `.mcp.json` hardcodes `"command": "python3"`; the rewrite map never touches it | **Taken.** g3's first constraint; the install test now asserts interpreter as well as paths |
| 6 | All five integrate gates carried the same repo-wide suite, green before the run began | **Taken.** Each integrate now has its OWN test node first, then the suite, then the verdict |

SHOULD-FIX 7, 9, 10, 11, 12, 13, 14 taken. 8 taken — two decorative preconditions removed,
so a BLOCK at g3 no longer blocks the doc-only adoption gate. NOTE 15 taken (N≥2 induced
failures). NOTE 17's cut taken, and it is the one place the critic and the independent
minimality candidate converged: **g1's implement dispatch is collapsed**; I author the
decision and the pin, and an independent reviewer challenges both against a frozen list
and a mutation. What is lost — an independent cold read of the identity code before I
commit — is named in the gate itself rather than hidden. 9 crew dispatches, not 10.
