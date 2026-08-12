# Plan alternatives (design-it-twice) — issue #688

Contract: `references/design-it-twice-brief.md`. Three candidates, each under **one named distinct
constraint**, compared on **depth / locality / seam placement / testability**, converging to one
opinionated recommendation (not a menu).

**Mechanism deviation, stated up front:** the contract asks for candidates generated **in parallel
by separate authors**. This session operates under a standing instruction not to dispatch subagents
unless the user asks for them, so the three candidates were authored **serially, in-context**, under
the same distinct-constraint discipline. The substance of design-it-twice is preserved; the
independence of the authors is not. Recorded as an untaken road, below.

---

## Candidate A — constraint: *minimum diff*

Grade the multiplier inline in `grip_baseline.py`. No new module, no new record fields,
`damage_batch` untouched.

| axis | reading |
|---|---|
| depth | Shallow — the R-only gap, the proxy and the `None`-vs-`0.0` discipline stay spread across callers. |
| locality | Best of the three: one file, one test file. |
| seam | None created. A **third** in-repo implementation of "how wet was this session" (after `weather_features` and `damage_batch.is_wet_race`). |
| testability | Adequate — reachable through `fit_grip_baseline_from_laps`. |

**Killed by two things.** (1) The graded severity is computed and then thrown away: with nothing
persisted, #712's consumer cannot distinguish a *measured* dry from a *proxied* dry, which is the
one thing the terminal consumer decision will need. (2) `grip_baseline.py` is already 705 of 999
lines at main; +120 lines of read logic pushes a file the project's own limits check is watching.

## Candidate B — constraint: *one home, two adapters* — **RECOMMENDED**

Extract `src/physics/layer2/session_wetness.py`: one resolver returning
`(severity: Optional[float], source: str)`. `grip_baseline` reads it; `damage_batch.is_wet_race`
**delegates** to it, keeping its bool + `threshold=0.1` semantics byte-identical. The record gains
`wetness_severity` + `wetness_source`.

| axis | reading |
|---|---|
| depth | Good — one call hides the R-only gap, the compound fallback, and the missingness discipline. Deep-module test: much behind little. |
| locality | Change and verification concentrate in the new module + its test; the two adapters are thin. |
| seam | **Real, not hypothetical** — two implementers exist *today* (`is_wet_race` is the second), which is exactly the "one adapter = a guess, two = a real seam" bar. |
| testability | Best — the resolver becomes directly unit-testable at the fraction grain; today the same logic is only reachable through a bool. |

**Costs, named:** it touches `damage_batch.py`, a consumed module — so its pre-existing guard tests
become a *mandatory* re-run (lesson `consumed-frozen-module-run-guard-tests`), not an optional one.
And it adds two store columns (free at the mechanism level: `GripStore._migrate_missing_columns` is
additive and dataclass-driven, but the round-trip still needs an assertion).

## Candidate C — constraint: *fix it at the source*

Extend `weather_features.populate_wet_features_for_db` past its `session_type='R'` filter so
`wet_lap_fraction` is populated for every session type. Physics then needs no proxy at all.

| axis | reading |
|---|---|
| depth | Best long-run — deletes the R-only gap at its origin and pays `damage_batch`, `burn_rate_calibration` and `fuel_features` at the same time. |
| locality | One data-region function. |
| seam | Correct placement: the data region already owns this column. |
| testability | Good, but acceptance now depends on a **repopulation of every season DB**. |

**Killed for this run, not on merit.** It collides head-on with **#728**, which is already cut and
sequenced as W6 stage 2's funded precondition; it makes #688's acceptance depend on a backfill
outside its own scope; and it is a **data-region change made to serve a physics consumer**, which
needs the owner, not a step-6 commander. Note also that populating `wet_lap_fraction` for Q *from
lap compounds* is **precisely the compound proxy** — C is B's fallback relocated upstream at far
higher blast radius.

---

## Convergence — B, with C's shape grafted in

Take **B**. Graft the one genuinely better idea from **C**: write the resolver so that the proxy
branch is a *fallback that stops firing on its own*. When #728 lands and `wet_lap_fraction` becomes
populated for all session types, the primary branch simply starts winning and `wetness_source` flips
from `compound_proxy` to `surface_features` — **no code change in physics, and the store records
that the substrate improved.** That makes B forward-compatible with C rather than a competitor to
it, and it turns `wetness_source` from a nicety into the thing that makes the transition auditable.

Reject **A** outright: it is cheaper today and strictly worse at the one thing the stream's terminal
decision (#712) needs.

## Untaken roads (surfaced at plan approval, per bias-to-yes)

1. **Parallel independent authoring of the candidates** — not run; standing session instruction bars
   dispatching subagents unqualified. Serial in-context authoring was substituted. *Risk:* the
   candidates share one author's blind spots.
2. **The cold plan critic** — **NOT RUN, and this is a genuine gap, not a formality.** The
   mechanism's whole value is a reader with **no authoring context**, which the plan's author cannot
   supply, and dispatching one is barred by the same instruction. *Mitigation, and it is weaker than
   the thing it replaces:* the critic's three standard lenses are written into `execute.json` as
   explicit close criteria the implementer/reviewer crews must answer — **intent-fit** (does the gate
   serve step 6's stated point), **testability** (can each pathway be exercised and falsified), and
   **simplicity/YAGNI** (what can be deleted). A crew reviewer reading only its handoff is the
   nearest available cold read; it is not a critic of the *plan*.
3. **Panel-vs-single** — a 3-lens panel would be the default for an architecture-touching plan. This
   plan adds one small module inside an existing component and touches no boundary, so a single
   critic would have been the right call even if one were available. Surfaced as a choice, not
   assumed.
