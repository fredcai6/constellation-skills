# Launch Order: `epic-568-510 — engine — permit the start the advisory instructs`

**Issued:** 2026-08-14 by `admiral-epic-568` · **Boundary:** `wave-2-510-engine-ruling` · **Launch:** `epic-568-wave-2-510-engine`
**Frozen.** Read it as written. Where it is wrong, say so and float rather than quietly working around it.

## Mission

Your predecessor in this lane refused to pin a contradiction, floated it, and the human ruled. The
ruling: **make the engine permit the `start` the advisory instructs**, rather than narrowing the
advisory's wording. Close the contradiction in behavior, prove it with a red/green over engine
behavior, and take the lane to the point where publication is all that remains.

This is an engine-core change. You hold the serialized `scripts/checklist_engine.py` lane. No other
Commander may implement in it while you do.

## Prior-Wave Verdicts (pasted)

From `constellation/epic-568-510/g2-repair/commander/attempt-1`, verbatim on the load-bearing points:

> At a pending gate that is merely *next* after the agent's own legal close (g3, not the gate it is
> trapped in), the new branch says *"begin THIS guarded gate (`start g3`)"* and in the same sentence
> *"do not begin work at another gate"* — while `_trip_hard_gate` refuses that identical `start` with
> *"so a FRESH agent starts this one."* I simulated obeying it: the begin is **released** and the
> ledger ends `[('g2','begin-refused'), ('g3','begin-refused'), ('g3','begin-released')]` — the
> engine's own compliance signal brands the agent an offender for doing what the engine told it.

> The pre-change wording is *also* wrong at g3, so **neither wording is pinnable**.

Also established by that run, and not to be re-litigated:

- `E.advance(cl,"g2")` → `EngineError: g2 is 'pending', must be in-progress to advance`. The
  pre-change wording, shown at a pending gate, named a command the engine rejects. That was #510's
  original defect and its fix at the **trapped** gate (g2) is correct and already landed in this lane.
- Two of the three `TripLedgerComplianceOnTheHardAdvisory` expectations were genuinely stale and are
  fixed. The third is the marker for this contradiction and is **deliberately still failing**.
- An independent falsifier confirmed no test was weakened and that reverting only the test file
  reproduces the three original engine failures.

## Pre-Rulings

1. **`decision:fix-the-engine-not-the-prose` — settled by the human.** The advisory's instruction
   stands; the engine changes so that instruction becomes true. Do not resolve this by editing
   advisory wording.
2. **`decision:scope-is-the-contradiction` — settled.** Change the smallest engine behavior that
   makes the advised `start` legal at a gate reached by the agent's own legal close, and stops the
   compliance ledger from recording an offense for obeying. This is not licence to redesign gate
   lifecycle.
3. **`decision:enumerate-before-you-change` — settled, and do this first.** Before changing behavior,
   enumerate every test that asserts on `_trip_hard_gate` refusal or on trip-ledger contents. The
   ledger is a shared rendered surface — the last repair in this lane was defeated by a whole-string
   pin living in a *different* test class (`#467`'s), invisible to a targeted run. Report the
   enumeration in your result.
4. **`decision:repro-before-and-after` — settled.** Close on a repro that fails before and passes
   after, over **engine behavior** — the ledger sequence above is the natural candidate. Not a text
   assertion. Do not delete or weaken a test to reach green.
5. **`decision:clear-caches-before-measuring` — settled.** `find . -name __pycache__ -type d -not
   -path './.git/*' -prune -exec rm -rf {} +` before **every** suite run. Stale `.pyc` files from the
   wave-1 worktree relocation fabricated a phantom failure earlier in this wave.
6. **`decision:map-refresh-is-mechanical` — settled.** Regenerate with
   `python -m scripts.code_map build --root .` and commit. No judgement required.

## Honest-Null Clause

A measured negative is a complete, successful deliverable. If the enumeration in pre-ruling 3 shows
that permitting this `start` breaks compliance semantics other work depends on — that the refusal is
load-bearing rather than incidental — **that is a real and valuable result. Report it and stop.** Do
not force the ruled fix through a surface that turns out to be structural. The human ruled on the
information available at the time; new measurement is exactly what would revise it.

## Inherited Latitude

Bounded internals of the engine change are yours. Direction is settled: the engine yields, not the
prose. You may **not** redesign gate lifecycle, change what `advance` requires, or alter
production defaults beyond the contradiction. Anything that reaches those floats.

## File Ownership

Yours: `scripts/checklist_engine.py` (the `_trip_hard_gate` / `_trip_advisory` region),
`tests/test_checklist_engine.py`, `map/INDEX.md`, your own episode records.
Not yours: `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py`, `scripts/run_crew.py`.

## Workspace

Worktree `.worktrees/epic-568-510`, branch `epic-568/510-hard-advisory`, **already rebased by the
Admiral onto `main` at `c23c3d0f`; your base commit is `23ed6b70`.** The two `map/INDEX.md` conflicts
raised by that rebase were resolved by regenerating the map, never by hand-editing it. The worktree
is yours alone.

## The MCP door — read this before you fight it

Your spine is `.agent-work/epic-568-510/spine.json`, at `review` **blocked** on the float, with a
live lease your predecessor took over with `--force`.

**Do not treat "MCP-only" as satisfiable.** I asserted that constraint in the previous orders without
checking, and it was false: `scripts/mcp_spine_server.py:145-146` binds the door at module import
from `SPINE_FILE`, `.mcp.json` defaults that to the interactive demo, a running server cannot be
rebound, and `tests/test_mcp_identity.py:914` pins that no argument may redirect it. Both previous
Commanders hit this; `mcp__spine-epic__` returns `Connection closed`.

**Ruling for this dispatch:** if your door does not resolve to your own spine, use the
`scripts/checklist_engine.py` CLI — the same engine the door wraps, with identical lease and journal
provenance — and **say so plainly in your result**. That is a disclosed, authorized fallback, not a
deviation. What remains forbidden is hand-editing spine state or bypassing the engine entirely.

## Inherited Context

`main` carries wave 1 plus two wave-2 lanes: `0448275e` (origin/worktree isolation), `e0c998b6`
(Codex tier metadata), `c23c3d0f` (spine-rail binding). #441 is fenced by external quota until
2026-08-20 and is not competing with you.

## Pre-empted Steps

Do not re-run `understand` or `plan`. Do not redo the two stale-expectation fixes; they are correct
and committed. Start from the contradiction.

## Data Locations

Findings file: `.agent-work/epic-568-510/FINDINGS-wave2-engine.md`. Your predecessor's
`FINDINGS-wave2-repair.md` holds the measurement behind the float — read it first.

## Budget

One bounded engine change. If it grows past the contradiction, stop and float.

## Stop Conditions

Stop and report if any of these fire:
- The enumeration shows the refusal is load-bearing (honest-null clause).
- The fix requires changing `advance` semantics, gate lifecycle, or production defaults.
- Green requires deleting or weakening a test rather than correcting behavior.
- Any file outside your ownership must change.

## Return Shape

Report: the enumeration from pre-ruling 3; what engine behavior you changed and the red/green proof
over it; the cache-clean full Linux suite counts before and after; whether the map is fresh; whether
you used the MCP door or the disclosed CLI fallback; and anything floated. **You are fenced from
push, PR, and merge** — that is the Admiral's delegated class. Park where publication is all that
remains and say so.
