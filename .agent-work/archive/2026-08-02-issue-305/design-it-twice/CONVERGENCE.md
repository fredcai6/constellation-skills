# Design-it-twice convergence — issue #305 assembly seam

Two candidates, two named constraints, one recommendation (not a menu). Panel, not single:
the seam is a load-bearing interface on shared machinery three concurrent commanders depend
on — "when in doubt, panel" resolves to panel here without needing the doubt.

**Status: RECOMMENDATION ONLY. Floated to the Admiral, not adopted.** The launch order puts
"design-it-twice convergence on any load-bearing interface shape" on the must-float list,
human-only, always. Nothing below is decided by me.

## The comparison

| Axis | A — minimum engine surface | B — maximum unskippability |
|---|---|---|
| Seam | `dispatch()`'s `current` branch (`:2387`) | top of `dispatch()` (`:2375`), all verbs |
| Engine diff | ~3 lines (+1 if refusals lands) | larger, on the shared verb chokepoint |
| Coverage | only when an agent asks `current` | every engine call |
| Blast radius | low — read-only branch | higher — path every verb crosses |
| Refusals | optional gate, deferred to the float | central; new `cl["refusals"]` counter |

## What decided it

**Candidate A's premise is false, and B is what caught it.** A argues the `current` branch
is *"reached by every read of the plan, by construction — `current` is the only way an agent
learns what to do next."*

Verified at source, that is wrong. `checklist_engine.py:206`:

```python
RAIL_VERBS = {"claim", "current", "start", "advance", "attest", "attach"}
```

Six verbs carry the doctrine rail with the next imperative in it. An agent can drive an
entire spine through `start` → `attest` → `advance` and **never call `current` once** — it
gets its instruction from the rail on the verb it was already running. So a manifest emitted
only on the `current` branch is skippable by an agent that simply never asks. That is exactly
the failure `decision:manifest-is-a-byproduct` exists to prevent: *if producing it is
something the capture path calls, it will be skipped somewhere.*

Under the settled pre-ruling, coverage beats diff size. A hands the skip back to the agent;
B does not.

## Recommendation — B's seam, A's discipline

Not a menu and not a coin-flip: **take B's seam placement with A's containment rules.**

1. **Seam: the `dispatch()` chokepoint, emitting after the verb resolves**, so the manifest
   always describes the step the agent is about to act on (post-`advance`, that is the *new*
   active step — the one whose imperative the rail just handed them). Covers `current` as one
   case rather than treating it as the only case.
2. **A's fail-soft rule is adopted verbatim and is not optional.** The emit must never change
   any verb's exit code or output. It catches broadly, by documented exception to
   narrow-except style, because `build_manifest()` legitimately raises `ValueError` on a fully
   terminal checklist and a crash here would break every verb for every concurrent commander.
   This is the single most important constraint on the whole change: **the byproduct must
   never be able to break its host.**
3. **A's separate-module discipline is adopted.** All roots-resolution and field logic lives
   in a new `scripts/episode_capture.py`; the engine gains an import and one call. B's larger
   diff is accepted for *coverage*, not for logic-in-the-engine.
4. **A's exit-code vocabulary is adopted for every authored check:** 0 pass, 3 genuine red,
   4 fixture/setup failure — never 1 or 2, which collide with argparse and tracebacks. Forced
   by the engine facts that a `command` postcondition passes no `cwd=` and discards stdout, so
   the exit code is the only signal that reaches the spine.
5. **A's oracle choice is adopted and is the strongest idea in either candidate:** the
   negative control validates through `apply_episode_delta.validate_delta()` — *the real
   writer's own validator* — rather than a reimplemented field check. A reimplementation would
   drift from the contract silently; the real validator cannot.

## The untaken road, named

**A's seam, standalone.** Rejected on coverage, not on cost — its diff really is smaller and
its blast radius really is lower, and if the Admiral rules the wider seam too risky to land
while three commanders are live on this engine, A is the fallback that still delivers
manifest-on-`current` plus every other gate. It would ship a byproduct that a determined
agent can still skip, and that limitation would have to be stated in the record rather than
papered over.

## Honest weaknesses both candidates share, carried into the plan

- `artifact-ref` is list-shaped and optional, so its absence is definitionally valid and the
  negative control has **no red case for that one field**. Disclosed in the record, not
  engineered around.
- `write_manifest()` is a plain `open(..., "w")`, not an atomic rename; parallel agents on a
  shared spine can interleave. Out of scope here, filed rather than fixed.
- `role` is unresolvable on a lease-less run. The assembler **refuses rather than guessing** —
  a scoped null, per doctrine, not a fabricated value.
- `reopens` vs `rework-count` scoping (whole-run vs active-step) is **inferred** from the two
  distinct field names, not confirmed against `EPISODE_STORE.md`. Must be confirmed against
  the doc before the field is filled, not after.

## The dependency on the open float

Whether `refusals` gets an engine counter is **not** settled here — it is the separate float
already with the Admiral. The plan is authored so that answer changes **one gate**, not the
shape. If refusals stays out of scope, the assembler **refuses** rather than emitting a silent
`0`: a `0` on a run that was actually refused is a fabricated mechanical fact, which is worse
than an absent one and is precisely what `decision:zero-agent-effort-is-literal` forbids.
