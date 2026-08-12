# Problem statement — C3: the work lifecycle is one thing, and it is currently three

**Work id:** `epic-559/c3-lifecycle` · **Mode:** delegated, no reachable human
**Principal:** the frozen `LAUNCH_ORDER.md` in this work area; ratifying tier is the Admiral,
`admiral-epic-418-followon`.
**Reachability, measured:** `ListAgents` at 2026-08-12T08:3x lists four peer sessions and the Admiral
is not among them. There is no live channel up. Every float below lands in `COMMANDER_RETURN.md`, and
a gate I genuinely cannot satisfy gets `spine_halt block` naming the Admiral.

## The ask, in one sentence

An agent creates work the same way it drives work — through the door, in one call — and the closing
advance puts the work away and says it is ready to PR.

## Reconciling the order's assumed baseline against the code

The delegated doctrine requires this before planning: a headline mechanism the order treats as
unimplemented may already be shipped, and the real gap may be one the pre-rulings name only in
passing. Six claims checked, on base `293b7721`:

| # | The order's claim | Measured | Verdict |
|---|---|---|---|
| 1 | Nothing in this corpus provisions a worktree | `grep -rl "worktree add" scripts/ skills/` → 5 files: `verify_worktree_isolation.py`, `verify_worktree_precondition_coverage.py`, `LAUNCH_ORDER.template.md`, `fleet-doctrine.md`, `_shared/windows.md` | **Confirmed.** Two verifiers and three paragraphs of prose. No provisioner. |
| 2 | `durable_root()` returns two different roots depending on run state | `scripts/agent_work_root.py:110-141`: linked worktree → main checkout, **except** when `_active_epic_lease(main)` is true, then the worktree | **Confirmed**, and it is deliberate and documented. |
| 3 | `generate_spine.py` is reachable only from a shell | `scripts/generate_spine.py:848` is an `argparse` `main()`; no MCP tool names it; `TOOLS` in `mcp_spine_server.py:414` lists 9 tools, all engine verbs | **Confirmed.** By the standing ruling it is a defect today. |
| 4 | The door reads `SPINE_FILE` at import time and raises `KeyError` without it | `mcp_spine_server.py:106` — true of the module. **But** `.mcp.json` binds `SPINE_FILE` with a shell default (`${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}`), so a real dispatch always starts | **Refined, and this changes the design.** See "the chicken-and-egg" below. |
| 5 | `parent` reaches the registry only from `args.parent`, no environment fallback | `_crew_door_env` (`run_crew.py:722-752`) binds `SPINE_PARENT` unconditionally to `parent` or `UNKNOWN_PARENT`, never the dispatcher's ambient value; its docstring states the rule | **Confirmed.** The guard works; the instruction is what was dropped. |
| 6 | `not_yet_written` is read with bare truthiness | `generate_spine.py:424` `cond.get("not_yet_written")` and `:673` the same | **Confirmed.** A TOML `"false"` string is truthy. |

Two further measurements the order did not make, both load-bearing:

7. **The engine round-trips unknown top-level spine keys.** Driven live: a spine carrying a top-level
   `origin` block through `claim → start → attest → advance` came back with `origin` intact and the
   engine's own `refusals` / `engine_session` / `why_trail` added beside it. `validate_spine._shape_faults`
   has no unknown-top-level-key fault. So a worktree record **can** live inside the spine with **zero**
   change to what `checklist_engine.py` reads or writes.
8. **`call_tool` is pinned to two return shapes.**
   `tests/test_mcp_identity.py::IdentityBindingPinTests::test_call_tool_can_only_produce_content_two_ways`
   AST-walks `call_tool` and refuses any `return` that is not literally `as_result(run_engine(...))` or
   `_tool_error(...)`. This, not the import-time `KeyError`, is the real structural obstacle to putting a
   non-pass-through tool on this server.

## What is actually being asked for

### 1. Open — one call creates the spine and its worktree

One operation takes a work id and a spec and produces the branch, the worktree, the scaffolded work
area, the spine compiled into it, and the crew-binding environment. It verifies its own result with
`scripts/verify_worktree_isolation.py`. It refuses rather than half-succeeds and rolls back. It records
where it opened. It never silently reuses a worktree another crew is in. It is reachable through the
door.

### 2. Close — the terminal advance archives, and says it is ready

Moves `.agent-work/<work-id>/` to `.agent-work/archive/<work-id>/`, stages **by name**, commits the
move, prints a readiness verdict naming branch, commit, and what remains: "ready to PR."

The ordering is fixed and is not my latitude: postconditions → final `advance` → `release` → move
(spine file last) → commit → report.

It does not open the PR, does not remove the worktree, does not judge the work good.

### 3. The dispatch is emitted, not remembered

A spec declares the crews a gate dispatches; the generator emits the dispatch with `parent` and `model`
already in it, and refuses a declared dispatch missing either.

### Carried findings

- `not_yet_written` bare-truthiness → `isinstance` guard plus a VIOLATING fixture.
- `DESIGN_NOTE.md` §4, §7, §10 reconciled to shipped behaviour or the stale claims deleted.

## The four questions the Admiral wants answered in the plan

Answered here in outline; argued in `MISSION_FRAME.md` and frozen in the gate plan.

**Q1 — the chicken-and-egg.** The order names the import-time `KeyError` as the obstacle. Measured, it
is not: `.mcp.json` supplies a default, so the server always starts, bound to *some* spine. The real
obstacle is two properties of the bound-spine contract: `_identity_violation` refuses any argv whose
`--file` is not the bound spine, and the `call_tool` choke-point pin allows exactly two return shapes.
The resolution is to stop pretending an open is an engine verb. **`spine_open` never calls
`run_engine`.** It creates a spine at a path it computes from the work id; it never addresses the bound
one. So it is dispatched from a **sibling** of `call_tool`, leaving that function's pass-through pin
exactly as strict as it is today — and the new non-pass-through surface gets its own containment guard
with its own VIOLATING fixtures, rather than being smuggled through a guard written for a different
hazard. `.mcp.json` is untouched: the tool joins the server that is already registered.

**Q2 — where the worktree record lives.** *Inside the spine*, top-level `origin`, on measurement 7
above: it survives a full engine drive untouched, it archives with the spine because it **is** the
spine, and a sidecar would reintroduce exactly the two-files-that-can-disagree shape this epic exists
to remove. The honest residual: the engine defends nothing about it, so a regression test pins the
round-trip.

**Q3 — the dispatch: data, or an imperative to retype?** **Data the engine consults** — not by
executing it (the engine dispatches nothing and will not start) but by **checking it**. The generator
emits the declared dispatch into the gate, *and* a postcondition that reads the durable crew registry
(`crew-runs.json`, which records `parent` and `model` per entry as of `2a22c00a` — verified against
this run's own entry) and refuses to close the gate unless a crew for that gate and role is recorded
with the declared parent and the declared model. A forgotten `--parent` then fails a gate instead of
being noticed a wave later. The rendered imperative is still prose a crew reads, but it is no longer
the *only* thing standing between the instruction and the outcome.

**Q4 — one tool or two?** **Two.** Their binding relationships are opposite: `spine_open` acts on a
spine that does not exist yet and is not the bound one; `spine_close` acts on the bound spine and on
nothing else. Folding opposite identity semantics behind one `action` argument is how a guard written
for one of them ends up covering the other by accident.

## Governing constraints (from the order; all binding)

`checklist_engine.py`'s on-disk format unchanged · the close ordering fixed · close never opens a PR
and never removes a worktree · stage by name, never `git add -A` · `settings.json`, `.mcp.json`,
`docs/agents/*` untouched · `skills/**` untouched (R1 owns it; float, do not take) · never run
`scripts/install_constellation.py` · no merge or push to `main` · never two crews in one worktree.

## Baselines

- Tests: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  → order states 2824 passed, 3 skipped, 1121 subtests on `293b7721`. Re-measured this run; result
  recorded in `MISSION_FRAME.md`.
- Sweep: `python scripts/validate_spine.py --sweep --root .` → **23 fault lines measured on `293b7721`**,
  matching the order exactly. Any change to that number is a no-go.

## Floats to the Admiral (recorded, not blocking yet)

1. **`archive.c2b` demands a PR that is OPEN or MERGED**, and `archive.c2` demands the branch be
   pushed. The launch order forbids merge/push to `main` and makes `COMMANDER_RETURN.md` the delivery;
   `ORCHESTRATOR_CONTEXT.md` puts pushes and PRs behind explicit human approval. Pushing this *branch*
   is not pushing to `main`, but opening a PR is an outward-facing act the order does not authorize.
   I will drive every other archive postcondition and take this one to the Admiral at the archive gate.
2. **This repo has no Cartographer packet map at all** (`docs/architecture/` absent; `map/ids.jsonl`
   empty), so every Commander run here orients DEGRADED. Recorded with hash-pinned substitutes in
   `map-orientation.json`. Not fixable inside this order — `skills/**` and `docs/agents/*` are no-go.
3. **`docs/agents/engine-config.json` does not exist**, yet this spine's own `config_ref` names it.
   `checklist_engine.load_config` tolerates the absence; the DESIGN_NOTE's spec template hands the same
   path to every generated spine. Cosmetic today, load-bearing the moment a config is added.
