# #525 — Problem Statement (consolidated, understand step)

**Issue:** Audit + unify physics model parameter unit conventions (producer/consumer
alignment). Parent: #509 physics C-phase. Spawned from #522 (lateral units fix).

## North star (user-clarified 2026-06-27)

**De-overload / disambiguate — NOT unitless-as-dogma.** The goal is to remove terms
that silently mean different things in different places (the two lateral conventions;
`ρ`-in-aero present in one form, absent in the other; a duplicated `G_MS2`). "Prefer
specific/unitless" is a *tool* toward unambiguous parameters, not a mandate to convert
everything. Labelling the variables (unit-suffixed field names + clean co-located
headers) is the primary fix; mechanical unit-philosophy is secondary.

## Why now — recurrence

Third units-collision incident in a month, each silently corrupting downstream physics
until caught by hand: #518 G5 (`p_max` total-watts injected into a W/kg `theta_P` slot →
745 km/h ideal lap) and #522 (`lateral_view` g-unit A0/A2 read as m/s² by the shared
consumer → corner caps ~10× under-called). Both were the same failure mode: the unit
convention lived only in a docstring (or nowhere), producer and consumer authored months
apart, nothing enforcing alignment, the test suite blind because fixtures re-baseline to
whatever convention is in front of the author.

## Locked scope (settled — not re-litigated)

1. **Map** the unit convention of every physics model parameter across all channels
   (lateral A0/A2/ceiling/g_track/k_tire; longitudinal/power theta_P/theta_D/theta_R/
   p_max/CdA; braking a_b/b_b; traction; coast; terrain theta/z/banking) at each producer
   and each consumer. Identify overloaded/ambiguous terms.
2. **Label the variables:** unit-suffixed field names + one co-located unit header per
   param struct, so the convention sits at the assignment seam where a reviewer flinches.
3. **Unit-convention map** checked into the architecture docs as a short reference table,
   **directly referenced once from the top-level `docs/AGENT_GUIDE.md`** (read before any
   non-trivial work), with a standing instruction to review/update the map in the same gate
   whenever a physics model parameter is touched. (User ruling 2026-06-27: one top-level
   reference in the guide, not scattered references across the role-context docs.)
4. **Unify the two lateral producers** onto one convention; retire/generalize the #522
   `car_prior` Option-A patch. (Which convention = a post-audit decision; see below.)
5. **One output-level guard** — extend `tests/known_answer/test_published_f1_data.py` so a
   known car/track's ideal-lap top speed AND a representative corner cap must land in a
   physical band (fails on a #518/#522-class mismatch). Optionally one 3-line plausibility
   assert at the single conversion boundary. **NOT** a per-param band-test matrix; **NOT**
   a units library (`pint`) / per-param typed-unit wrappers.

**Out of scope:** changing the physics fits themselves (representation/alignment only);
evo/prediction composition (#509 P-phase); a units library; a per-param band-test matrix.

## Process — AUDIT FIRST, decide-fix checkpoint (user-ratified)

- **Gate 1 = evidence-only audit** (no code fixes): produce the full producer→consumer
  unit-convention map + an inventory of overloaded/ambiguous terms, each with a proposed
  disposition (fix-locally-in-this-run vs route-to-separate-issue).
- **Decide-fix checkpoint (user-decision):** ratify the canonical-convention call(s) and
  which fixes are in-scope-now vs routed out. The frozen fix gates are (re)planned here
  from the audit evidence (the `diagnose-first-decide-fix` pattern, as in #522).
- **No pre-decision** on the two governing forks — both deferred to the checkpoint:
  - **Lateral canonical convention (A vs B):** A = unitless/g-coefficient canonical
    everywhere (consumer moves to g-units, both producers feed g-units, bigger blast
    radius incl. the live `sim_evaluator`/`fit_batch`); B = m/s² canonical at the consumer,
    producers normalize up to it (smaller blast radius, consumer untouched). User is **not
    hard on unitless** — pick whichever best de-overloads with acceptable blast radius.
  - **ρ-in-aero:** an overloaded term to remove if we can. If unifying ρ turns out to need
    a **refit** (out of scope), **STOP and evaluate** — fix locally or route to a separate
    issue, decided at the checkpoint, not pre-committed.

## Latitude

Nominal cleanup (variable renames, comments) along the way is **in scope** and welcome —
it serves the de-overloading goal.

## Done-done bar (per #509)

Tests · honest behavior preserved · single canonical path · the unit-map doc + agent-context
wiring + the one output-level guard. No behavior regression: `sim_evaluator`, the C1
utilization path, and the published-F1 known-answer tests all stay physical.
