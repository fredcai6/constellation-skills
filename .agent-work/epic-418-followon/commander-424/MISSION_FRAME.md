# Mission frame — #424, workstream F, MCP front door

## Intent

Put a second, typed front door on the checklist engine so that *operating the engine* stops costing
the agent doing the real work its attention. An MCP stdio server wraps the engine's own
`main(argv)`; the CLI door stays. The token delta is a constraint that must not go the wrong way, not
the thing being bought.

## Map confidence, staleness, disputes

> **CORRECTION, added at g1-integrate — the statement below is wrong, and the tool that produced it
> is wrong too.** This repo **does** carry a machine-generated code map, at `map/INDEX.md`
> (55 modules, 1047 entities), with a freshness test (`tests/test_code_map.py`) that fails if it is
> not rebuilt after source changes. `map_orient.py` never found it: it probes only
> `docs/architecture/generated/map.json`, `docs/architecture/index.md` and `docs/architecture/`, then
> falls back to `README.md`/`AGENTS.md`/`CLAUDE.md`/a `docs/` index. `map/` is in neither list, so the
> tool reported `DEGRADED-NO-MAP` on a repo with a real, enforced, current code map. I found this
> only because adding two scripts turned the freshness test red. Filed as a triage candidate. The
> practical cost: this run planned as if map-blind when a map was available, and the substitutes I
> hash-pinned were doctrine files rather than the structural map I should have read.

**There is no *Cartographer packet* architecture map.** `map_orient orient` returned `DEGRADED-NO-MAP` — no
`docs/architecture/generated/map.json`, no `docs/architecture/index.md`, no packets directory,
`anchor_count: 0`. This is a skill-source repo. The verdict was discharged, not skipped, with five
hash-pinned substitutes, two unmapped statements and an escalation to the Admiral.

Anchors below are therefore cut from the **substitutes the context-step receipt pinned** plus the
engine's own verb table, which I read directly and treat as the authority for the surface F wraps.
Per `commander-core.md`'s architecture bookend, a run with no packet map reconciles the structural
record directly rather than blocking on an absent map.

**Disputed / stale, and it bites:** `docs/agents/CREW_CONTEXT.md` is Windows-framed and says `py`
has no pytest. On this Linux host both shims resolve to one venv (3.12.3, pytest 9.1.1). The launch
order's measured fact governs. Named, not fixed — it is fenced corpus text and out of scope.

## Structural anchors (hash-pinned substitutes from the context receipt)

- `docs/agents/ORCHESTRATOR_CONTEXT.md` — record stores are written only through their writers;
  episodes are records, never rules; no successor playbook.
- `docs/agents/GLOSSARY.md` — one name per thing. Already carries A2's outcome: HARD refuses the
  verbs that BEGIN work at a gate, `start` and `reopen`, never `advance`. This is the line F types.
- `docs/agents/CREW_CONTEXT.md` — verification discipline: a check that cannot fail is
  indistinguishable from one that passed; assert against behaviour, never against text describing it;
  any guard that loops must assert what it looped over.
- `docs/CHECKLIST_SCHEMA.md` — the gate/condition schema the tools' arguments must be typed against.
- `README.md` — corpus layout.

## Affected capabilities

- **The engine's dispatch surface** (`scripts/checklist_engine.py`, `main(argv)`): 18 verbs —
  `current, claim, heartbeat, release, start, advance, record, consolidate, skip, block, resume,
  reopen, append, amend, attest, waive, attach, flag-candidate`. F wraps this and duplicates none of
  it.
- **Per-dispatch agent launch** — the delivery mechanism the probe selected.
- **Spine templates** — the source of imperative text that must ride tool results verbatim.

## Governing constraints and assumptions

Fixed by spec F, not up for re-litigation:

1. No engine logic duplicated — wrap `main()`, so refusals, rails, recovery hints, journal and lease
   enforcement ride through unchanged.
2. Gate imperative rides tool results **verbatim**; no second rendering path.
3. CLI door stays; every uncovered verb keeps a documented CLI fallback.
4. `settings.json` never written, at any scope. Project-scope `.mcp.json` only.
5. Each agent gets its own server instance, keyed `session_id#agentId`.
6. Rich tool descriptions accepted without a control arm (recorded as an unmeasured preference
   promoted to a constraint).

## Decision anchors and decision pressure

**No map decision anchors exist to cite.** This run oriented `DEGRADED-NO-MAP`, so there is no map
for an anchor to be a member of, and the only citations that can resolve are the hash-pinned
substitutes listed under "Structural anchors" above. The governing decisions below are **launch-order
pre-rulings and one measured finding of my own** — they bind this plan, but they are not, and are not
claimed to be, map anchors. They are named here without map-anchor grammar so the frame does not
assert a map membership that does not exist. Their `decision:` ids and `@grade:` tags are carried on
the gates they actually govern, in `execute.json`'s per-gate `anchors.decision` blocks.

- **The `.mcp.json` delivery branch point — my first answer was WRONG and was caught at g1-review.**
  **What survives:** a live interactive session does **not** hot-reload a fresh `.mcp.json`, and
  `claude mcp list` does show a new project-scope server as `⏸ Pending approval`. Both reproduce.
  **What was false:** the consequence I drew from it — that project-scope `.mcp.json` therefore
  "cannot serve a cold agent at all". It can. A headless `claude -p` with `--allowedTools` and **no**
  `--mcp-config` reaches the server through the plain committed project-scope file; the server
  launched (its start-marker was written) and returned its output. The reviewer reproduced this
  twice against server-side artifacts, and I then reproduced it myself in a fresh project directory
  with no prior approval state. My probe conflated two different gates: MCP server *approval* in the
  interactive TUI, and the ordinary per-tool *permission* gate that every headless tool call passes
  through and that `--allowedTools` opens. Missing `--allowedTools` is what made my original
  no-`--mcp-config` attempt look like non-delivery.
  **Regrade: `settled/measured` → falsified; replaced by the finding above.**
  **`gen_mcp_config.py` still earns its place, for a different and real reason:** a single shared
  project-scope `.mcp.json` binds one `SPINE_FILE` and one `SPINE_SESSION` for every consumer, so it
  cannot give a parent and a subagent *different* spines (DC2) and cannot key identity per agent
  (DC3, protected-intent item 5). Per-dispatch generation is justified by **identity and
  separation**, not by delivery necessity. Grade: settled/measured, on the corrected basis.
- **MCP is the vehicle, not the destination** — do not gold-plate the grouping; seven-over-eighteen
  is a placeholder. Grade: settled/human.
- **Count from the call record** — DC5's count never comes from the engine's refusals counter, and
  never from the server's own log as numerator (see the evidence table). Grade: settled/spec.
- **Hold the bug fixes constant** — two of the four named bugs (#439, #446) are *already* fixed in
  the template this run drives, i.e. constant before both arms. Nothing to hold. Grade: settled/spec.
- **Decision pressure, new:** the uncovered-verb list is where the grouping choice actually bites.
  `waive` and `attach` are load-bearing on real role spines (this very run needed both), while
  `skip`/`amend`/`append` are rarer. Covering the wrong eleven makes the door useless on a real
  spine and would only surface at DC1.

## Claims and evidence surfaces

| Claim | Where its evidence comes from |
|---|---|
| Door is up and serving (DC3's **positive control**) | A live tool call returning engine output through the server, before any no-identity result is allowed to count |
| Imperatives are identical CLI vs MCP (DC4) | A **property** check over every gate carrying an imperative, not a sample |
| Spine-management cost falls (DC5) | One counting unit identical across arms: an **invocation attempt** read from the driving agent's own record, including attempts the client rejected pre-flight. The server's JSONL is corroborating detail, never the numerator — a malformed call rejected by client-side schema validation never reaches the server, so a server-log numerator structurally suppresses exactly the fumbles the MCP arm is credited with avoiding. Plus far-side recovery events, and an order control across arms. |
| Inheritance fails closed (DC3) | A subagent dispatched with no special configuration |
| Governor instruction rides a tool result (DC6) | The trip advisory text appearing in a tool result and being acted on |

## Relevant events already in the tree

- **DC3 has a live positive control.** Two spines in this session both carry session
  `86708414-f5d3-40d3-8c9a-2f96d1ccdc14`, differing only in free-text `claimed_by`. Inheritance does
  not fail closed today; the control detects a real defect, not a planted one.
- **A fumble of exactly the class F absorbs, from this run:** `attest` is refused on an
  engine-checked condition, but the projection renders engine-checked and attestable conditions in
  the same shape. Cost: one wasted round-trip, paid by the agent doing the real work.

## Out of scope

Gold-plating the tool grouping. Fixing the six pinned red tests (a concurrent agent owns them).
Touching `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
`tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py`
(fenced). Any `settings.json` write. Closing any issue. Promoting anything into `docs/agents/*`.
