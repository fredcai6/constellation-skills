# Mission Frame — `cmdr-567-a`

Authored at `plan`, before `execute.json`. Base `600de020`.

**Read this caveat first, because it governs every anchor below.** This repo has
no packet map. `map_orient.py orient` returned `DEGRADED-UNPARSEABLE`: `map/ids.jsonl`
is tracked and **0 bytes**, and `map/INDEX.md` carries 29KB of generated structure
with no citable anchor id. So there is **no anchor inventory to cite ids from**. Per
the `context` step's contract, a DEGRADED verdict is discharged with hash-pinned
substitutes, and the anchors in this frame are drawn from those substitutes rather
than from map node ids that do not exist. The five substitutes pinned in
`.agent-work/epic-567-door/cmdr-a/map-orientation.json` are:
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `map/INDEX.md`,
`docs/CHECKLIST_ENGINE_DESIGN.md`, `notes-a.md`.

I am not shrinking this frame — the change is neither trivial nor local. It edits
the security boundary of the fleet's engine access.

## Intent

Give a role agent a door path to a spine that **already exists**, without raising
the number of spines one process may drive above one, and without widening what an
agent can reach beyond what is stated out loud. Second, make
`checklist_engine.save()` atomic so a concurrent reader or a crash cannot observe
or leave a torn spine. Net effect the epic needs: the CLI stops being the only
path, which is what unblocks deleting it in wave 2.

## Affected Capabilities

- **door-binding** — how the MCP door decides which spine it drives. Today: decided
  at process launch from `SPINE_FILE`, or at `spine_open` for a spine being minted.
  This run adds the case the door cannot currently express at all: a spine that
  exists and was not minted by this process.
- **door-identity-guard** — `_identity_violation`, which refuses any call resolving
  `--file`/`--session-id` away from the binding, and confines the path-bearing
  arguments `--from-child`/`--delta`. This run must leave its semantics intact; it
  compares against `SPINE` at call time, so it follows a rebinding automatically.
- **spine-state-persistence** — `checklist_engine.load`/`save`, the only read and
  write path for spine state. This run changes `save`'s durability, not its format.

## Examples / Events

- **The Admiral's own `spine_status` refusal**, quoted in the launch order, and
  **my own reproduction of it at step one of this run** with my spine on disk and
  its lease held by me. This is the concrete event the whole lane exists for, and
  it is measured twice at two tiers.
- **Lane G's incident this wave** — its implementer crew plus its own
  context-inheriting fork drove one `spine.json` under one lease id, and the lane
  could not tell its own writes from an attacker's. Consumed here as evidence for
  what `save()` atomicity does **not** fix.

## Structural Anchors

Cited as path/symbol, since no `struct:` ids exist. All in
`docs/CHECKLIST_ENGINE_DESIGN.md`'s subject area (pinned substitute).

- `scripts/mcp_spine_server.py` — the door. Level: module. The change lands here.
  - `SPINE` / `SESSION` (`:201`, `:202`) — module scope, the two identity globals.
  - `_bind_process_to` (`:878`) — the one sanctioned mutator of those two names.
  - `_unbound_refusal` (`:393`) — per-call binding check, deliberately uncached.
  - `_rebind_refusal` (`:920`) — refuses a rebind while a lease is held.
  - `_identity_violation` (`:443`) — the guard. Not to be re-specified this run.
  - `_resolve_confined` (`:322`) — the containment predicate, already
    parameterized on `bound_dir`.
  - `_spine_open` (`:968`) — mint-and-bind, today the only caller of the binder.
- `scripts/checklist_engine.py` — the engine. Level: module.
  - `save` (`:237`) and `load` (`:220`) — **line numbers pinned to base `600de020`,
    not to HEAD.** The atomicity change adds `import tempfile`, which shifts both by
    one (`load` → `:221`, `save` → `:238`). Pinned rather than updated because a
    number that drifts as the branch moves is the defect
    `global-everyone.md` §"Pin a claim to the revision you read it at" names. My own
    anchor-verification script caught this drift, which is the check working.
  - `save` is where the atomicity change lands. **`load` is OUT OF SCOPE** — it stays
    `json.loads(read_text())` and still surfaces a missing or malformed document as an
    unhandled traceback. The frame originally said the change "lands here" for both,
    which was wrong; a cold critic caught it (M12). Adding a refusal to `load` is a
    triage candidate, not this lane's work.
  - `_RAIL_STRINGS` and `_refresh_attach_hint` — **fenced to this lane but NOT my
    mission.** Lane C needs their text intact for a follow-up. Named here so the
    plan does not churn them.
- `tests/test_mcp_lifecycle.py` — the pins. Level: test module. Constrains the
  design more than any doc does.

## Governing Constraints / Assumptions

- **`constraint:one-spine-per-process`** — one process drives exactly one spine at
  a time. A candidate may move *when* the binding is decided; raising the count
  breaks a `settled` decision. Ignoring it reintroduces the composition failure
  `IDENTITY_TRADE.md` recorded.
- **`constraint:ast-pin-on-identity-assignment`** — a module-wide AST pin asserts
  assignments to `SPINE`/`SESSION` are exactly {module scope, `_bind_process_to`}.
  Ignoring it fails CI by construction. This is the strongest constraint in the
  frame and also a free correctness check on the winner.
- **`constraint:lifecycle-return-pin`** — `tests/test_mcp_lifecycle.py:137` pins
  every `return` in `call_lifecycle_tool` to literally `_spine_open(args)` /
  `_spine_close(args)`; `:194` bans `SPINE`, `SESSION`, `run_engine` from
  `_spine_open`'s own source. Both were left byte-identical by the previous lane
  and I will not weaken either — the previous lane's own record documents a
  superseded attempt to "extend" a pin and why that was the dangerous direction.
- **`constraint:fail-closed-binding`** — an unnamed spine must refuse, never
  resolve to something ambient. `_spine_from_env` (`:156`) records that an empty
  `SPINE_FILE` once resolved to `Path("").resolve()`, the process cwd, "silently
  binding the door to whatever directory it was standing in." Any candidate that
  infers a binding from ambient state has to prove it is not that defect again.
- **`assumption:in-session-observation-is-not-evidence`** — hooks and the engine
  execute from the main checkout regardless of worktree; `CLAUDE_PROJECT_DIR`
  resolves once at session launch (#269). Validation must be a fresh process with
  explicit paths. Source: `docs/agents/ORCHESTRATOR_CONTEXT.md` §Dogfooding
  (pinned substitute), which states this independently of my launch order.
- **`assumption:engine-under-edit-is-not-engine-in-play`** — my session drives the
  installed engine at `/home/tommy/.claude/skills/constellation-*/scripts/`; my
  worktree holds the source copy. Same source. The whole self-hosting proof rests
  on keeping these straight.

## Decision Anchors & Decision Pressure

Existing anchors this run inherits:

- `decision:one-spine-per-process-stands` — one process, one spine, regardless of when the binding is decided.
  `@grade: settled/inherited · leans g1-design,g2-implement`
- `decision:bind-on-open-over-new-verb` — a successful `spine_open` binds this process to what it minted, rather than making the caller relaunch the door.
  `@grade: settled/measured · leans g1-design · settle: already settled by lane cleanup/a-door; re-measurable by reading _bind_process_to's single call site`
- `decision:solve-the-general-case` — the mission is any role reaching its own spine, not the Task-tool crew case alone.
  `@grade: settled/admiral · leans g1-design,g2-implement`
- `decision:isolation-not-fencing` — whatever replaces "one file per process" is stated explicitly, including the reach delta.
  `@grade: guess/admiral · leans g1-design,g4-review · settle: name the property in the design doc and have the reviewer attack it`
- `decision:net-deletion` — the lane ends with something deleted.
  `@grade: settled/human · leans g1-design,g5-reconcile`
- `decision:convergence-is-human-only` — I generate and compare; the human picks. My recommendation is not ratified by my having made it.
  `@grade: settled/human · leans g1-design`
- `decision:atomicity-is-not-mutual-exclusion` — `save()` atomic replace fixes torn reads and crash corruption; it does NOT fix lost updates, and the run says so rather than letting the fix be read as concurrency safety.
  `@grade: settled/measured · leans g3-implement,g4-review · settle: two writers each load-mutate-save a copy; observe a well-formed file with one update missing`

Decision **pressure** — choices this run forces, surfaced as candidates, not settled by me:

- Which candidate wins the design-it-twice panel. `decision:convergence-is-human-only` makes this the human's, not mine. I return a comparison and one recommendation.
- Whether write-provenance (recording *which agent* wrote each journal entry) becomes a real requirement. Lane G's incident is the grounding and it is the actual fix for what bit them. Beyond my lane: triage candidate.
- Whether `#613`'s lost-update half gets its own lane once atomicity lands, since atomicity makes the remaining race quieter and therefore easier to mistake for solved.

## Claims / Evidence Surfaces

- **claim: an agent that did not launch its own door can drive its own spine through the door.** Checked by a fresh-process test that binds to a spine file it did not mint and then runs a read-only verb through the door successfully. This is the lane's exit criterion and the thing that must not be faked by an in-session observation.
- **claim: reach did not silently widen.** Checked by a negative test: a path outside the stated containment boundary is refused, with the refusal naming the boundary. `decision:isolation-not-fencing` makes this a first-class deliverable, not a side effect.
- **claim: the identity guard still refuses a foreign spine after a binding change.** Checked by the existing `tests/test_mcp_identity.py::IdentityBindingPinTests` plus the module-wide AST pin, both of which must pass unmodified.
- **claim: `save()` cannot leave or expose a torn spine.** Checked by a test that a reader concurrent with a writer sees either the old or the new complete document and never a partial one, and that no temp file is left behind on the success path.
- **claim: the engine under edit still drives a live spine.** Checked per the launch order's `decision:self-hosting-engine-edit`: read-only `current` against the live spine exits 0 under the new engine, and a mutating `advance` runs against a **copy**, never a live spine file.

## Map Confidence / Staleness / Disputes

- **`map/ids.jsonl` — empty, 0 bytes, tracked. Confidence: none.** No anchor id exists for any area of this repo. How it alters the plan: every anchor above is a path/symbol against a hash-pinned substitute rather than a map id, and the `plan` step's `c6` verify-frame gate cannot be satisfied by any frame, so it will be taken as a **recorded waiver**, not a silent skip. Escalated to the Admiral in the map receipt. Not fixed here: `map/` is not mine this wave.
- **The previous lane A reported this identically at `a69bbac4`** and it is unfixed at `600de020`, so it has survived a full epic as a known, filed, unactioned defect. Re-raised as a triage candidate rather than a second unfiled issue, per `decision:no-issue-filing`.
- **The launch order's own line reference is stale** — it cites `_identity_violation` at `mcp_spine_server.py:164`; it is at `:443` at `600de020`. The order's substantive claim about the function is correct. Recorded so no gate inherits the wrong line.

## Out of Scope

- `scripts/hooks/*` — untouched. Stated for the Admiral's merge sequencing, since concurrent lanes editing hook code can break every live session.
- `_RAIL_STRINGS` and `_refresh_attach_hint` in `checklist_engine.py` — fenced to me, needed intact by lane C. No gratuitous churn.
- `#613`'s lost-update / read-modify-write half, including the parent-heartbeat second writer. Only the atomicity half is in scope.
- Write-provenance (who wrote which journal entry) — the real fix for lane G's incident. Triage candidate.
- The wave-2 doctrine sweep: 15 `CLI fallback` clauses and 11 `<engine>` tokens, both re-measured and confirmed at `600de020`. Deleting them is blocked behind this lane, not part of it.
- `map/ids.jsonl`. Filing any issue (`decision:no-issue-filing`).
