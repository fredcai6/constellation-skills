# Mission frame — C3: the work lifecycle is one thing

**Work id:** `epic-559/c3-lifecycle` · **Base:** `293b7721` · **Mode:** delegated, Admiral not reachable

## Map confidence, stated first because it governs everything below

This run oriented **DEGRADED-UNPARSEABLE** and discharged the verdict at the context step. There is no
Cartographer packet map in this repo: `docs/architecture/` does not exist in any of its three probed
forms, and `map/ids.jsonl` is an empty file, so the derived code map carries no citable anchor id
either. The receipt at `.agent-work/epic-559/c3-lifecycle/map-orientation.json` hash-pins the five
documents read in a map's place:

- `map/INDEX.md` — the derived code map: package/module inventory with per-module hole counts. It gives
  the shape of the tree and nothing about intent.
- `README.md` — the corpus thesis: independent reviewer every time, mechanically-enforced rails, an
  architecture network keeping *why* hooked to *what*.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — the project deltas that bind this plan.
- `docs/agents/GLOSSARY.md` — one name for one thing.
- `docs/agents/CREW_CONTEXT.md` — the crew-tier posture every handoff inherits.

**How the degradation alters this plan, concretely.** Every structural claim below was read from source
rather than confirmed against a frame, which inverts the intended order and is worth saying plainly
rather than dressing up. The mitigation is that each such claim is written here as a *measurement with
its command*, so a reviewer can re-run it instead of trusting it — and the plan gates each carry the
re-run as a close criterion. No gate is authored on an unverified structural belief.

`docs/agents/ORCHESTRATOR_CONTEXT.md` also names a second, smaller gap: this spine's `config_ref` points
at `docs/agents/engine-config.json`, which does not exist. The engine tolerates the absence today.

## Intent

An agent creates work the same way it drives work — through the door, in one call — and the closing
advance puts the work away and says it is ready to PR.

Three pieces, one lifecycle: **open** (branch + worktree + work area + spine, in one verified
operation), **close** (archive + stage-by-name + commit + readiness verdict, in the fixed order), and a
**declared dispatch** the generator emits with parent and model already in it.

## Affected capabilities

| Capability | Where it lives now | What changes |
|---|---|---|
| Drive a spine through a door | `scripts/mcp_spine_server.py` — 9 tools, 18 of 18 engine verbs | Two tools added that are **not** engine verbs; the existing pass-through surface is untouched |
| Compile a spine from a spec | `scripts/generate_spine.py` — shell-only `argparse` entry | Becomes reachable through the door; gains a declared-dispatch section |
| Provision a worktree | **nowhere** — two after-the-fact verifiers and three paragraphs of prose | Becomes an operation with a rollback and a self-verification |
| Archive a finished work area | **nowhere** — hand-typed shell each run | Becomes the terminal operation, ordered so it cannot eat the spine driving it |
| Dispatch a crew | `scripts/run_crew.py` — durable registry recording `parent` and `model` | Becomes the oracle a gate postcondition reads |

## Structural measurements this plan rests on

Each is a command a reviewer re-runs, not a belief.

1. **Nothing provisions a worktree.** `grep -rl "worktree add" scripts/ skills/` → 5 files: two
   verifiers (`scripts/verify_worktree_isolation.py`, `scripts/verify_worktree_precondition_coverage.py`)
   and three prose files. No provisioner.
2. **The door always starts.** `.mcp.json` binds `SPINE_FILE` with a shell default, so the import-time
   read at `scripts/mcp_spine_server.py:106` never raises on a real dispatch. The launch order's stated
   chicken-and-egg is therefore not the obstacle it names.
3. **The real obstacle is the pass-through pin.**
   `tests/test_mcp_identity.py::IdentityBindingPinTests::test_call_tool_can_only_produce_content_two_ways`
   AST-walks `call_tool` and refuses any `return` that is not literally `as_result(run_engine(...))` or
   `_tool_error(...)`. A tool that provisions a worktree cannot be written inside that function.
4. **`_identity_violation` refuses argv that leaves the binding.** `scripts/mcp_spine_server.py:174` asks
   the engine's own parser what `--file` resolves to and refuses anything but the bound spine. An open
   cannot be an engine call against a spine that does not exist yet.
5. **The engine round-trips unknown top-level spine keys.** Driven live through
   `claim → start → attest → advance`: a top-level `origin` block came back intact, beside the engine's
   own `refusals`, `engine_session` and `why_trail`. `scripts/validate_spine.py` has no unknown-key fault.
6. **The crew registry records what a dispatch is accused of forgetting.** This run's own entry in
   `.agent-work/epic-559/c3-lifecycle/crew-runs.json` carries `"parent": "admiral-epic-418-followon"` and
   `"model": "opus"`.
7. **`durable_root` answers twice.** `scripts/agent_work_root.py:110` returns the main checkout for a
   linked worktree *except* under an active Admiral epic lease, when it returns the worktree.
8. **Both carried findings reproduce.** `cond.get("not_yet_written")` at `scripts/generate_spine.py:424`
   and `:673`; the DESIGN_NOTE at `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` carries a
   `### CORRECTION` block inside §6 that §4, §7 and §10 were never reconciled against.

## Governing constraints and assumptions

Binding, from the frozen launch order: the engine's on-disk format is not changed · the close ordering
(postconditions → advance → release → move, spine last → commit → report) is fixed and is not latitude ·
close never opens a PR and never removes a worktree · stage by name, never `git add -A` ·
`settings.json`, `.mcp.json` and `docs/agents/*` untouched · `skills/**` untouched and floated if it must
change · never run `scripts/install_constellation.py` · no merge or push to `main` · never two crews in
one worktree.

Two assumptions, both stated because they are falsifiable and load-bearing:

- **A tool added to the already-registered `spine` server needs no `.mcp.json` edit.** Follows from the
  server being launched by `.mcp.json` as `scripts/mcp_spine_server.py` with no per-tool declaration.
- **The gate plan cannot be named `execute.json`.** The commander template names it that, but this
  Commander's own spine is `.agent-work/epic-559/c3-lifecycle/execute.json`. Writing the gate plan there
  would overwrite the spine mid-run. The gate plan is authored as `GATE_PLAN.json` and the collision is
  reported as workflow feedback, not silently absorbed.

## Decision pressure — durable choices this run forces

Four, each answered in `PROBLEM_STATEMENT.md` and frozen in `LIFECYCLE_CONTRACT.md` at gate `g0`:

1. **Where a non-pass-through tool lives on a pass-through door.** Answer — a sibling dispatcher beside
   `call_tool`, so the existing pin stays exactly as strict, with its own containment guard and its own
   violating fixtures. Fixedness — a guess, settled by `g2` shipping it against the real pin.
2. **Where the worktree record lives.** Answer — inside the spine, top-level `origin`, on measurement 5.
   Fixedness — measured; the residual is that nothing defends it, so a regression test pins the
   round-trip.
3. **Whether a declared dispatch is data or prose.** Answer — data the engine consults by *checking* it
   against the crew registry, on measurement 6. Fixedness — a guess, settled by `g3`.
4. **One lifecycle tool or two.** Answer — two, because their binding relationships are opposite.
   Fixedness — a guess, settled by `g2`.

## Claims and evidence surfaces

| Claim the run will make | How it is proven |
|---|---|
| Open refuses rather than half-succeeds | A test that forces failure after the worktree exists and asserts the worktree is gone |
| Open never reuses an occupied worktree | A violating fixture: a second open against a worktree with a live crew registry entry must refuse by name |
| The record survives the engine | A test driving a generated spine through the engine and asserting `origin` is intact |
| Close cannot eat its own spine | A test that runs the real close after a real terminal advance and asserts the spine landed in the archive |
| A declared dispatch missing parent or model is refused | Violating fixtures at generation time, in the `_cli_only_verb_violations` house style |
| The pass-through door is still pass-through | The existing pin runs unchanged and green |
| Nothing shipped moved | `python scripts/validate_spine.py --sweep --root .` still reports exactly 23 fault lines |

## Out of scope

Opening a PR · removing a worktree · any change to `scripts/checklist_engine.py`'s on-disk format · any
change to `scripts/validate_spine.py` · the CLI-residue cleanup in `skills/**` (R1 owns it) · filing any
GitHub issue · the survey-item artifact-postcondition gap the C2 note floated (an engine change, above a
Commander's latitude) · evidence provenance binding (same reason).

## Baselines, pinned to `293b7721`

- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  → **2824 passed, 3 skipped, 1121 subtests**, re-measured this run, matching the order.
- `python scripts/validate_spine.py --sweep --root .` → **23 fault lines**, re-measured this run,
  matching the order.
