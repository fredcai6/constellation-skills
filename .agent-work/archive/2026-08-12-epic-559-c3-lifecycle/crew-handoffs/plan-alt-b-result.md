# Plan alternative B — `best-seam-placement`

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `plan` · **Role:** `plan-alt-b`
**Constraint:** one deep lifecycle module owns open and close as its interface; the MCP door and a
shell CLI are two adapters over the same seam.

## 1. The candidate, one paragraph

A new module, `scripts/spine_lifecycle.py`, owns two pure-plus-impure operations —
`open_work(work_id, spec, root, parent=...)` and `close_work(spine_path, root)` — as the single place
every property the launch order demands (refuse-and-roll-back, self-verification, occupied-worktree
refusal, the fixed close ordering, spine-last archiving) is implemented and tested. Two thin adapters
sit over it: two new MCP tools (`spine_open`, `spine_close`) dispatched from a sibling of `call_tool` on
the already-registered `spine` server, and a CLI (`python scripts/spine_lifecycle.py open|close ...`)
that matches the shape every other provisioning-adjacent script in this corpus already has
(`generate_spine.py`, `init_work_area.py`, `verify_worktree_isolation.py` are all CLI + importable
library). Neither adapter contains logic the other lacks; each is a few lines that parses its own
calling convention and calls the module. The module, not either adapter, is where a reviewer reads the
close ordering once and trusts both callers obey it — that is the whole bet this candidate makes.

## 2. The gate plan

Every gate's evidence includes the standing baseline: `env -u SPINE_FILE -u SPINE_SESSION -u
SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` stays green (2824+N passed, 3 skipped,
growing subtests, N = this gate's own new tests) and `python scripts/validate_spine.py --sweep --root .`
stays at exactly 23 fault lines. I do not repeat that as a numbered postcondition on every gate; it is
the reason gates are ordered the way they are — nothing here opens a red window and leaves it for a
later gate to close.

### g0-lifecycle-contract — reasoning gate, no crew

**Imperative.** Freeze `LIFECYCLE_CONTRACT.md`: the module's function signatures and pure/impure split;
the `origin` block schema (below); the worktree/branch naming convention derived from `work_id`; the two
MCP tool schemas; the CLI subcommand shapes; the `[[gate.dispatch]]` spec-format extension and the
reserved postcondition id it injects.

**Close criteria.** `c1`: `LIFECYCLE_CONTRACT.md` exists and is internally consistent — arrival only,
same waiver class as C2's own `g0-design`.

**Evidence.** The document itself.

**Crew-waiver reason.** Naming-and-authority decision with nothing to run — identical justification to
`DESIGN_NOTE.md`'s own g0.

### g1-carried-findings — crew gate

**Imperative.** Fix `cond.get("not_yet_written")` bare truthiness in `generate_spine.py` (lines 424,
673, confirmed present on this base) with an `isinstance(..., bool)` guard that REFUSES a non-bool value
as a new spec-shape fault rather than silently coercing it — consistent with this generator's own
refuse-rather-than-guess ethos, and strictly stronger than the minimal fix (coercing a non-bool to
`False` would still let a TOML `"false"` string quietly become `True`'s opposite by accident; refusing
names the mistake instead). Reconcile `DESIGN_NOTE.md` §4, §7, §10 against the §6 `### CORRECTION` block
and against shipped `generate_spine.py`/`validate_spine.py` behavior; delete or correct any claim the
correction contradicts.

**Close criteria.**
- `c1` — kind `pytest`, selector `not_yet_written and (guard or Guard)`, targets
  `tests/test_generate_spine.py`, `min_collect = 5` (2 VIOLATING + 2 INNOCENT + 1 omitted-field case,
  fixtures below).
- `c2` — kind `qualitative`, because: "prose staleness has no oracle; DESIGN_NOTE.md is a frozen
  contract document, not code — a reviewer reads §4/§7/§10 against §6's own correction and against a
  fresh read of `generate_spine.py`/`validate_spine.py` and confirms no sentence there is now false."

**Evidence.** The fixture test file diff; the DESIGN_NOTE.md diff; baseline.

**Crew gate.** Implementer, Sonnet.

### g2-lifecycle-module — crew gate

**Imperative.** Write `scripts/spine_lifecycle.py`: pure helpers (`compute_worktree_path`,
`compute_branch_name`, `build_origin_block`, `_closeout_preconditions_met`) beside the impure
`open_work`, `close_work`, and a CLI `main(argv)` — the same function-granularity split
`generate_spine.py`/`validate_spine.py`/`checklist_engine.py` already use. `open_work` reuses
`generate_spine.main` (captured, not reimplemented) to compile the spec, then injects `origin` and
re-validates before writing; `close_work` reuses `run_crew.spine_terminal` (already exists, already
tested) rather than re-deriving terminality. No door wiring yet — this gate proves the module against
itself and against the CLI, the second adapter the constraint demands.

**Close criteria.**
- `c1` — kind `pytest`, selector `OpenWork and (Rollback or Occupied)`, targets
  `tests/test_spine_lifecycle.py`, `min_collect = 4`.
- `c2` — kind `pytest`, selector `CloseWork and (Ordering or Terminal or Released or SpineLast)`,
  targets `tests/test_spine_lifecycle.py`, `min_collect = 5`.
- `c3` — kind `pytest`, selector `CLI and (Open or Close)`, targets `tests/test_spine_lifecycle.py`,
  `min_collect = 2` — the CLI is exercised as a subprocess against a tmp git fixture, not merely
  imported; this is the proof the second adapter is real, not decorative.
- `c4` — kind `pytest`, selector `Origin and RoundTrip`, targets `tests/test_spine_lifecycle.py`,
  `min_collect = 1` — drives a generated spine through a real `claim → start → attest → advance` and
  asserts `origin` survives untouched (mission-frame measurement 5, now pinned as a regression rather
  than a one-off measurement).

**Evidence.** `scripts/spine_lifecycle.py`; `tests/test_spine_lifecycle.py`; baseline.

**Crew gate.** Implementer, Sonnet.

### g3-door-adapters — crew gate

**Imperative.** Add `spine_open`/`spine_close` to `mcp_spine_server.py`'s `TOOLS`/`TOOL_NAMES`, dispatched
from a NEW sibling function (`call_lifecycle_tool`, never touching `call_tool`'s body) so the existing
choke-point pin stays exactly as strict as it is today. `spine_open`'s tool schema takes `work_id`,
`spec`, optional `branch`/`base` — no `root`/`worktree` argument; the repo root is derived from the
BOUND spine's own worktree (`git -C SPINE.parent rev-parse --show-toplevel`), never caller-supplied,
matching the "ambient state is bound at server-launch time, not exposed as tool arguments" rule the rest
of this door already lives by. `spine_close` takes no path argument at all — it acts on `SPINE_FILE`,
full stop; there is no field to redirect because none exists.

**Close criteria.**
- `c1` — kind `pytest`, selector `test_call_tool_can_only_produce_content_two_ways`, targets
  `tests/test_mcp_identity.py`, `min_collect = 1` — the EXISTING pin, unmodified, still green: the
  pass-through door is still pass-through.
- `c2` — kind `pytest`, selector `LifecycleChokePoint`, targets `tests/test_mcp_lifecycle.py`
  (new file) — the analogous AST pin over `call_lifecycle_tool`: every `return` in it must be one of
  `as_result_lifecycle(open_work(...))`-shaped / `as_result_lifecycle(close_work(...))`-shaped /
  `_tool_error(...)`, its own containment guard rather than smuggling through the guard built for a
  different hazard. `min_collect = 1`.
- `c3` — kind `pytest`, selector `SpineOpen or SpineClose`, targets `tests/test_mcp_lifecycle.py`,
  `min_collect = 4` — VIOLATING/INNOCENT fixtures (below) plus a full stdio JSON-RPC round trip:
  `tools/call spine_open` then, after a fabricated advance-to-terminal, `tools/call spine_close`,
  against a tmp git repo.

**Evidence.** `mcp_spine_server.py` diff; `tests/test_mcp_lifecycle.py`; baseline.

**Crew gate.** Implementer, Sonnet.

### g4-declared-dispatch — crew gate

**Imperative.** Extend the spec format with `[[gate.dispatch]]` (`role`, `parent`, `model`, all
required); a declared dispatch missing `parent` or `model` is a new spec-shape fault, refused before any
probe, naming the gate and the missing field. On a spec that declares one, the compiler injects a
`command`-kind postcondition (not `artifact` — DESIGN_NOTE §6's own lesson: don't inject a check kind
`record`/`consolidate` never evaluate, and don't invent a checkable file with no producer) that shells
out to a small reader of `crew-runs.json` (reusing `run_crew.load_registry`/`find_entry`'s shape, not
duplicating the JSON parsing) and refuses unless an entry for that gate/role carries the declared
`parent` and `model`.

**Close criteria.**
- `c1` — kind `pytest`, selector `spec-dispatch and (missing_parent or missing_model)`, targets
  `tests/test_generate_spine.py`, `min_collect = 4`.
- `c2` — kind `pytest`, selector `dispatch and postcondition and compiled`, targets
  `tests/test_generate_spine.py`, `min_collect = 2` — the injected postcondition's shape (a `command`
  check, not an unenforceable `artifact` one).
- `c3` — kind `pytest`, selector `DeclaredDispatch and Registry`, targets
  `tests/test_declared_dispatch.py` (new file), `min_collect = 3` — end to end: a real
  `crew-runs.json` entry with the wrong `parent`/`model` fails the postcondition; the right one passes.

**Evidence.** `generate_spine.py` diff; new/updated test files; baseline.

**Crew gate.** Implementer, Sonnet.

### g5-integration-and-close — crew gate

**Imperative.** One real, unmocked round trip in a tmp git repo: `spine_open` a throwaway work id, do
minimal gate work to reach terminal, `spine_lease release`, `spine_close`, and assert the archive
landed, the commit exists, staged by name, and the printed verdict names branch/commit/"ready to PR".
Confirm the corpus sweep is still 23 and regenerate the code map (`python -m scripts.code_map build`)
since this candidate ships a new module. As the capstone, and because the launch order says "drive your
own work through the door": when this spine itself reaches its own closeout, close it with the
newly-built `spine_close` — the run that built the tool is archived by the tool it built.

**Close criteria.**
- `c1` — kind `pytest`, selector `EndToEnd and Lifecycle`, targets `tests/test_spine_lifecycle_e2e.py`
  (new file), `min_collect = 1`.
- `c2` — kind `pytest`, selector `sweep and fault_count`, targets `tests/test_spine_lifecycle_e2e.py`,
  `min_collect = 1` — runs `validate_spine.py --sweep` as a subprocess and asserts the line count is 23,
  never a paraphrase of the number.
- `c3` — kind `qualitative`, because: "`map/INDEX.md` is a derived artifact and hand-editing it is
  forbidden by its own header; regeneration is one command but whether the result is accurate is a
  qualitative read, not a checkable one."

**Evidence.** `tests/test_spine_lifecycle_e2e.py`; `map/INDEX.md` diff; sweep output; baseline.

**Crew gate.** Implementer, Sonnet.

## 3. The violating fixtures

House style: `tests/test_mcp_adoption.py::_cli_only_verb_violations` — VIOLATING / INNOCENT /
ACCEPTED_FALSE_ALARM.

| Guard | VIOLATING (must catch) | INNOCENT (must not catch) |
|---|---|---|
| Occupied-worktree refusal (`open_work`) | Target path already a registered `git worktree` (an earlier `open` crashed after `worktree add`, before scaffolding) | Target path free, no registration |
| | Target directory exists on disk but is not a registered worktree (orphaned leftover) | A different `work_id`'s worktree exists as a sibling directory; the target path itself is free |
| Rollback-on-failure (`open_work`) | Worktree created, but `verify_worktree_isolation.check_distinct_real` reports not-ok (registered-worktree list faked to omit the new path) — must remove worktree + delete the branch it created | Every step succeeds — worktree, branch, `.agent-work/<work_id>/spine.json` with `origin` all exist, no rollback fires |
| | `generate_spine` compilation fails on a bad spec after the worktree exists — must remove worktree + branch, no `.agent-work/<work_id>` left behind | A pre-existing, unrelated worktree/branch for a different `work_id` is untouched by a failed open of a new one (rollback scoped to only what this call created) |
| Close ordering (`close_work`) | Invoked while `engine_session.status == "active"` (lease not released) — refuse naming "lease not released" | `engine_session.status == "released"` AND every item terminal — proceeds |
| | Invoked while the spine is not terminal (an in-progress gate remains) — refuse naming which gate | A different `work_id`'s archive directory is untouched by closing this one |
| | Simulated interruption after moving `crew-handoffs/`/`evidence/`/`triage-candidates/`/`crew-runs.json` but before moving `spine.json` — `spine.json` and its `.journal` must still be at the ORIGINAL path (spine-last), so a retry can find them | — |
| `[[gate.dispatch]]` missing field | Entry with no `model` | Entry with both `parent` and `model` set — compiles clean, injects the postcondition |
| | Entry with no `parent` | A gate with no `[[gate.dispatch]]` at all (a reasoning gate) — no postcondition injected, no fault |
| `not_yet_written` type guard | `not_yet_written = "false"` (TOML string) — must be refused, not silently truthy | `not_yet_written = false` (real bool) — strict path, unchanged |
| | `not_yet_written = "true"` (TOML string) — must be refused, not silently truthy | `not_yet_written = true` (real bool) — Blocker-0 TDD-red path, unchanged; field omitted entirely — unchanged |
| Lifecycle choke-point (sibling of `call_tool`) | A hypothetical handler that builds a dict itself, or concatenates onto a result, instead of returning `as_result_lifecycle(...)`/`_tool_error(...)` — the AST walk must flag it, mirroring `test_call_tool_can_only_produce_content_two_ways` but scoped to `call_lifecycle_tool` | The real `spine_open`/`spine_close` handlers, which return exactly those two shapes |
| Path/id containment (`spine_open`) | `spec` argument resolving outside repo root (`../../etc/passwd`-shaped) | `work_id` containing `..` or a leading `/` (reject via reused `run_crew.validate_work_id`, not a second implementation) | `spec` a normal repo-relative `specs/<role>.spine.toml` path; `work_id` a normal nested id like `epic-559/c3-lifecycle` |

No `ACCEPTED_FALSE_ALARM` bucket is populated for these: every guard above is a boolean containment or
state check with an oracle behind it (a registered-worktree list, a lease status field, a spec-shape
fault), not a heuristic probe like `population`/`script`'s AST-based ones — there is nothing plausible
that trips the guard without being a real violation, so a false-alarm bucket would be empty by
construction and I am not inventing one to look thorough.

## 4. The four answers, argued

**(a) How `open` is reachable through a door that binds one spine at import and whose `call_tool` is
AST-pinned to two return shapes.** Measured directly, not assumed: `.mcp.json` binds `SPINE_FILE` with a
shell default, so a real dispatch's door process always starts bound to *some* spine — never unbound.
The choke-point pin is the actual obstacle, and it is narrower than it looks: I read `call_tool`'s AST
walk myself and it starts from the specific `ast.FunctionDef` node named `call_tool`
(`next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "call_tool")`), then
walks only that node's subtree. A function defined as a **sibling** at module level — not nested inside
`call_tool` — is entirely outside that subtree and the pin never sees it. So `spine_open` is dispatched
from `call_lifecycle_tool`, a new sibling of `call_tool`; it never calls `run_engine` (there is no engine
verb for "create a spine that does not exist yet") and never returns from inside `call_tool`, so the
existing pin is unchanged, unmodified, and still exactly as strict. Any door process — bound to ANY
spine, including one mid-run on a completely unrelated gate — can call `spine_open` to create a
different spine and worktree, because `open_work` never touches `SPINE_FILE` at all; it only reads
`SPINE.parent`'s own repo to find the toplevel to provision alongside. The chicken-and-egg dissolves
because opening was never an engine call in the first place.

**(b) Where the worktree record lives.** Inside the spine, top-level `origin`, written by `open_work`
after `generate_spine.main` compiles and writes the spine, then re-validated before the whole `open` is
declared successful:

```json
"origin": {
  "work_id": "epic-559/c3-lifecycle",
  "branch": "epic-559/c3-lifecycle",
  "worktree": "/abs/path/to/worktree",
  "base": "<sha the branch was cut from>",
  "opened_at": "2026-08-12T08:31:00+00:00",
  "opened_by": "spine_open",
  "parent": "admiral-epic-418-followon"
}
```

This rests on the measured round-trip property (unknown top-level keys survive `claim → start → attest
→ advance` untouched, and `validate_spine.py` has no unknown-key fault) — g2's `c4` pins that as a
regression test rather than a one-off measurement. The payoff is specific and load-bearing for THIS
candidate's own close design: `close_work` reads `origin.worktree` directly off the bound spine instead
of asking `agent_work_root.durable_root()` anything. That sidesteps `durable_root`'s two-answer behavior
entirely for every spine opened this way — the ambiguity it exists to resolve (main checkout vs.
worktree, gated on an active Admiral epic lease) never has to be asked, because the record already says
which. `durable_root()` is untouched by this candidate and stays exactly what it is today: a fallback
for spines that were NOT opened this way (hand-provisioned, pre-epic-559), which this epic does not
retrofit.

**(c) Whether the declared dispatch is data the engine consults or prose a crew retypes.** Data the
engine consults, by checking it: the compiler injects a `command`-kind postcondition that reads
`crew-runs.json` and refuses `advance` unless a registry entry for that gate/role carries the declared
`parent` and `model`. I chose `command` over `artifact` deliberately, on the same evidence DESIGN_NOTE
§6 already surfaced the hard way: `record`/`consolidate` never evaluate `artifact`-kind postconditions on
a survey item, and `gated` gates have no producer that would honestly attach a "dispatch matched"
artifact — inventing one just to get an `artifact` check would be exactly the "turns a gate that cannot
fail into one that cannot pass" trap §6 already named for a different field. A `command` check that
shells out and greps the registry has a real, already-existing oracle behind it (`crew-runs.json` itself,
which measurement 6 confirms already records both fields per entry) and works identically whether the
gate is `gated` or `survey`. The residual is honest and small: the rendered imperative is still prose a
crew reads before dispatching, so a forgotten `--parent` is still POSSIBLE at dispatch time — what
changes is that it is no longer possible to advance PAST it silently. The defect moves from "invisible
forever" to "caught at the next gate boundary," which is the same shape of improvement `not_yet_written`'s
own fix in g1 makes.

**(d) One lifecycle tool or two, and why.** Two tools, but this candidate's reasoning for it is different
from — and I'd argue stronger than — "their binding relationships are opposite": the module already
exposes two separate pure-ish functions, `open_work` and `close_work`, with disjoint preconditions and no
shared control flow (open never checks lease state; close never touches git branches). Mapping each
straight to its own MCP tool keeps every adapter body a boring one-liner —
`as_result_lifecycle(open_work(...))`, `as_result_lifecycle(close_work(...))` — literally the same shape
`call_tool` already enforces for the engine tools. Folding both behind one `spine_lifecycle` tool with an
`action: open|close` argument would force the adapter itself to branch, which is exactly the shape that
let a guard written for one case start covering the other by accident elsewhere in this file (`amend`'s
`--delta` reusing `--from-child`'s containment predicate is the deliberate, correct version of sharing;
an `action` switch inside one tool handler forcing TWO different identity postures apart is the
accidental, dangerous version). Two tools is the seam falling out of the module's own shape, not a
grouping preference layered on top of it.

## 5. Where this constraint hurts

Named, specific, honest — not softened:

- **Net-new surface for no currently-measured second caller.** `.mcp.json`'s own ruling is "the agents
  should not know about the cli, period" — so the CLI's audience is deliberately non-agent: a human
  driving by hand, the Admiral during epic closeout, or future `recover_crews.py`-style tooling. Nothing
  in this run's own measurements shows an EXISTING caller that needs the CLI today. I am shipping it
  because the constraint requires a second adapter to prove the seam is real, and because every sibling
  script in this corpus already has this shape — not because I measured a missing capability. That is
  the constraint's own tax, paid honestly rather than smuggled in as "obviously needed."
- **One more named hop than the caller strictly needs.** A crew calling `spine_open` goes: MCP tool →
  `call_lifecycle_tool` → `spine_lifecycle.open_work` → `generate_spine.main` → `init_work_area`. A
  `smallest-diff` candidate that calls `generate_spine`/`init_work_area` straight from the tool body
  removes one of those layers. That layer buys locality (§6) at the cost of one more file a reviewer has
  to open to trace a single call.
- **Doubled test surface per property.** Because the CLI must be exercised, not merely asserted to exist
  (g2's `c3`), every one of the four required properties gets at least one test through the module
  directly AND, for at least the CLI, a second test through a subprocess boundary — not double the
  underlying logic, but double the entry points a reviewer has to convince themselves both actually
  agree with each other.
- **A CLI is a second way an agent could, in principle, be told to do this** — and the standing ruling is
  that agents should not know about the CLI at all. I have not found a way to ship "a real second
  adapter" without also shipping a surface that, if a handoff carelessly told a crew to shell out to it
  instead of calling the door, would be exactly the defect class this epic exists to close. The mitigation
  is doctrine (a handoff never names the CLI to a dispatched crew), not mechanism — this candidate does
  not, and I don't think can, mechanically prevent that misuse the way `_identity_violation` mechanically
  prevents a redirect. Worth the Admiral's attention if this candidate is picked.

## 6. Scoring

| Axis | Score | Why |
|---|---|---|
| Depth | 4/5 | All four required properties live in one module; both adapters are thin. Loses a point to the extra named hop in §5. |
| Locality | 5/5 | A change to the close ordering touches exactly `close_work`'s body; both adapters inherit it unchanged. A `smallest-diff` candidate that puts the ordering logic inside the MCP tool body risks the CLI (if it wants the same ordering) either reimporting from an MCP transport file or duplicating the sequence — this candidate has no such risk by construction. |
| Seam placement | 5/5 | The boundary is exactly where the tests want it: `open_work`/`close_work` are plain functions a test calls with a tmp-path repo, no stdio JSON-RPC framing required for the property tests, only for the thin adapter round-trip tests (g3's `c3`). |
| Testability | 5/5 | Rollback, occupied-worktree refusal, and close ordering are each falsifiable with a violating fixture at the module level (§3), independent of either adapter. |

**What it would lose to `smallest-diff`.** Raw diff size, review time, and — concretely — exposure to
this epic's own named review failure mode: C2's branch was reviewed five times and each review missed
something different, with **more code** correlating with more places to miss something. A
`smallest-diff` candidate that reuses `init_work_area.py`/`generate_spine.py` as libraries directly from
the two MCP tool bodies, with no new module and no CLI, ships the identical four required properties in
less code, with less to review, and with nothing built for a caller nobody has asked for yet. If the
Admiral's priority this wave is "ship the four properties, fast, defer generality," `smallest-diff` is
the better bet. This candidate is the better bet only if a second caller of open/close is genuinely
expected soon — plausible, given this epic's own history of eight hand-provisioned worktrees, but a
forecast, not a measurement, and I am naming it as exactly that.

## 7. Measured, not contradicting the mission frame — one clarification worth recording

I re-ran or directly re-read every measurement in `MISSION_FRAME.md`'s table by reading the cited source
lines myself rather than trusting the note. None contradicted. One is worth sharpening rather than just
confirming, because it is load-bearing for answer (a) above and I did not want to assert it from the
note alone: I read `test_call_tool_can_only_produce_content_two_ways` directly
(`tests/test_mcp_identity.py:1460-1500`) and confirmed the AST walk is scoped to the specific
`FunctionDef` node named `call_tool`, found via `next(n for n in ast.walk(tree) if ...)`, and then
`ast.walk(fn)` only over that node's own subtree — not the whole module. That means a sibling function
is provably, structurally outside the pin's reach, not merely "probably fine because nobody tests it." I
also directly confirmed `run_crew.spine_terminal` (`scripts/run_crew.py:317`) already exists as an
importable, tested predicate for "is this spine done" — `close_work` reuses it rather than re-deriving
terminality from `checklist_engine.active_id` a second time, which both candidates should do regardless
of which wins.

## Workflow Feedback

**What helped.** Reading `mcp_spine_server.py`'s module docstring and `_identity_violation`'s own
docstring before writing anything — both are unusually explicit about WHY each guard is shaped the way
it is, which let me reason about where a new guard should sit (sibling function, same containment
helper) instead of guessing. The DESIGN_NOTE.md §6 CORRECTION block was the single most load-bearing
paragraph in the whole reading list: without it I would have designed the declared-dispatch postcondition
as an `artifact` check and repeated the exact trap it names.

**What got in the way.** The handoff's reading list is long (five docs plus six source files) and none
of it says which facts are already frozen decisions I should adopt versus open questions I should argue
independently — `PROBLEM_STATEMENT.md`'s "four questions the Admiral wants answered" reads, on a first
pass, as already-settled Commander conclusions, and I had to re-derive from `DESIGN_IT_TWICE_BRIEF.md`
that I was meant to argue them fresh under my own constraint rather than cite them. A one-line note in
the handoff ("PROBLEM_STATEMENT's four answers are the Commander's own reasoning, not a frozen verdict —
argue your own") would have saved a re-read. Separately: the handoff never states whether the gate ids I
invent need to avoid colliding with the real Commander spine's own gate ids (`g0`..whatever
`execute.json` already uses) — I picked prefixed names (`g0-lifecycle-contract`, etc.) defensively but
without a stated rule to check against.
