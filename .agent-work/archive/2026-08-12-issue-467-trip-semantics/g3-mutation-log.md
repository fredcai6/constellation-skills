# g3 mutation log — issue #467, per-gate tighten-only context-headroom override

Every guard shipped at `g3-implement`, mutated one at a time. For each: the exact source
branch broken, the **named** test that went red, and the **TOTAL** failure count for that
mutation. A mutation that breaks forty unrelated tests does not show the test defends the
branch — it shows the opposite, so the totals are reported whether they flatter the tests
or not, and the two mutations with a wide blast radius (M3, M4) say so plainly.

**Method.** Same as g2's. A driver copied the target file to a pristine sibling, applied
exactly ONE textual replacement (asserted unique before applying), ran

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py
```

restored from the copy, and asserted the restored bytes equalled the pristine bytes. After
the battery, `git diff --stat` showed only the three intended files and the pair ran clean
(433 passed, 155 subtests). Named failures were collected from **both** `FAILED` and
`SUBFAILED` lines — several of these tests are `subTest` sweeps, whose failures appear only
as `SUBFAILED`, so a `FAILED`-only grep would have reported "no named test" for M1, M6, M7
and M8. The TOTAL is read from pytest's own summary line, which is authoritative.

Green baseline for this file pair: **433 passed, 155 subtests passed** (pre-change, measured
at HEAD with the diff stashed: 416 passed, 30 subtests).

---

## `gauge_reader.thresholds_for` — the tighten-only clamps

## M1 — the tighten-only clamp on the RESERVE itself

- **Branch broken:** `reserve = max(0, headroom_tokens)` → `reserve = headroom_tokens`
- **NAMED test red:** `ThresholdsHeadroomOverrideTests::test_headroom_override_can_only_tighten_never_loosen`
- **TOTAL: 18 failed**, 433 passed. All 18 are `SUBFAILED` cases of that one sweep — the 18
  negative-reserve combinations (3 negative values × 6 models) it sweeps. This is THE safety
  mutation: without the clamp, a negative override RAISES both thresholds, i.e. a gate opts
  itself out of the governor. Nothing else in the suite notices, which is exactly why the
  sweep exists.

## M2 — the non-negative clamp on both reduced caps

- **Branch broken:** `(max(0, soft_cap - reserve) / window, max(0, hard_cap - reserve) / window)`
  → `((soft_cap - reserve) / window, (hard_cap - reserve) / window)`
- **NAMED test red:** `ThresholdsHeadroomOverrideTests::test_headroom_reserve_larger_than_a_cap_clamps_at_zero`
- **TOTAL: 13 failed**, 432 passed. One named test plus 12 `SUBFAILED` cases of
  `test_headroom_override_can_only_tighten_never_loosen` (the `>= 0.0` half of the sweep):
  an oversized reserve produces a NEGATIVE fraction, which no fill can ever be below, so the
  gate would silently stop tripping instead of tripping immediately.

## M3 — the reserve coming off the SOFT cap

- **Branch broken:** `max(0, soft_cap - reserve) / window` → `max(0, soft_cap) / window`
- **NAMED test red:** `ThresholdsHeadroomOverrideTests::test_headroom_reserve_tightens_both_caps`
- **TOTAL: 12 failed**, 421 passed. **Wide, and deliberately so — declared, not hidden.**
  Nine of the twelve are the whole `GateHeadroomOverrideTripTests` class, killed by its own
  `setUp`, which asserts the fixture's band arithmetic (`thresholds_for(MODEL, RESERVE) ==
  (0.03, 0.10)`) before any test runs. That guard exists so a profile or arithmetic change
  breaks loudly with a stated reason instead of quietly making every assertion in the class
  vacuous. The narrowly-attributable kill is the named test above.

## M4 — the reserve coming off the HARD cap

- **Branch broken:** `max(0, hard_cap - reserve) / window` → `max(0, hard_cap) / window`
- **NAMED test red:** `ThresholdsHeadroomOverrideTests::test_headroom_reserve_tightens_both_caps`
- **TOTAL: 12 failed**, 421 passed. Same shape and same declared reason as M3 (the fixture
  `setUp` assertion). M3 and M4 are indistinguishable by total, which is honest: both break
  the same "BOTH caps" requirement, and one test names it.

---

## `checklist_engine._gate_headroom_tokens` — the single resolver

## M5 — the resolver's return, i.e. the WHOLE MECHANISM dead-coded

- **Branch broken:** `    return raw` → `    return 0` (every override resolves to nothing)
- **NAMED test red:** `GateHeadroomOverrideResolverTests::test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not`
- **TOTAL: 9 failed**, 424 passed. **This is the mutation the frozen "one test, both
  assertions" requirement exists for.** The negative half of that test still PASSES under
  this mutation — resolve-to-default is what a missing feature does — and only the positive
  control in the same test catches it. Also red: the other resolver test and all six
  neighbour/advisory/guard tests, plus the shipped-template test.

## M6 — the resolver's NEGATIVE check

- **Branch broken:** `if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:`
  → `if not isinstance(raw, int) or isinstance(raw, bool):`
- **NAMED test red:** `GateHeadroomOverrideResolverTests::test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not`
- **TOTAL: 3 failed**, 433 passed — exactly the three negative values that test sweeps
  (`-1`, `-30_000`, `-10**12`), all `SUBFAILED`. Narrow. Note this is defence in depth: with
  the resolver's negative check gone, `thresholds_for`'s own clamp (M1) still refuses to
  loosen, so the safety property survives ONE of the two failing.

## M7 — the resolver's BOOL exclusion

- **Branch broken:** `... or isinstance(raw, bool) or raw < 0:` → `... or raw < 0:`
- **NAMED test red:** `GateHeadroomOverrideResolverTests::test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not`
- **TOTAL: 1 failed**, 433 passed. Exactly one `SUBFAILED` case (`True`), which would
  otherwise become a 1-token reserve because `bool` is an `int` subclass in Python.

## M8 — the resolver's INT type check

- **Branch broken:** `if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:`
  → `if raw is None or isinstance(raw, bool):`
- **NAMED test red:** `GateHeadroomOverrideResolverTests::test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not`
- **TOTAL: 9 failed**, 433 passed — the nine malformed values that test sweeps (a string, a
  float, NaN, a list, a dict, a bare object, …), all `SUBFAILED`. Narrow.

## M9 — per-gate scoping: one gate's reserve leaks onto EVERY gate

- **Branch broken:** `task = (cl.get("tasks") or {}).get(gate)` → take the first task that
  carries a `context_headroom_tokens` at all, ignoring which gate was asked about.
- **NAMED test red:** `GateHeadroomOverrideTripTests::test_headroom_override_trips_its_own_gate_and_not_its_neighbour`
- **TOTAL: 7 failed**, 426 passed. **This is the DC4 mutation.** It is the "68 hand-authored
  placeholders" failure in miniature — an override that applies everywhere — and every test
  it kills is a *neighbour* test: the resolver's own per-gate test, the four
  advisory/guard/close neighbour tests, and the shipped-template test. A suite that only
  proved the overridden gate trips earlier would have stayed green under this mutation.

## M10 — gate-level ONLY: a checklist-config tier smuggled in underneath

- **Branch broken:** `raw = task.get("context_headroom_tokens")` → same, defaulting to
  `cl["config"]["context_headroom_tokens"]`.
- **NAMED test red:** `GateHeadroomOverrideResolverTests::test_no_checklist_config_tier_supplies_a_headroom_override`
- **TOTAL: 1 failed**, 432 passed. Exactly one test defends `decision:no-config-tier`, and it
  is the one named.

---

## The two call sites — the shown number and the judged number

## M11 — the ADVISORY stops reading the reserve (the number the agent is SHOWN diverges)

- **Branch broken:** `_gauge_reader.thresholds_for(reading.model, _gate_headroom_tokens(cl, gate))`
  → `_gauge_reader.thresholds_for(reading.model)` inside `_trip_advisory`.
- **NAMED test red:** `GateHeadroomOverrideTripTests::test_headroom_override_moves_the_advisory_and_the_guard_together`
- **TOTAL: 20 failed**, 431 passed. Also red: `..._changes_the_advisory_for_its_gate_only`
  and `..._neighbour_advisory_is_byte_identical_to_no_override`. The 17 remaining are
  `SUBFAILED` samples of the together-sweep — the fills at which the advisory now says one
  thing and the guard does another. This is the divergence (c) exists to prevent, caught
  from the *shown* side.

## M12 — the BAND DECISION stops reading the reserve (the number the agent is JUDGED against diverges)

- **Branch broken:** `_gauge_reader.thresholds_for(reading.model, _gate_headroom_tokens(cl, gate or active_id(cl)))`
  → `_gauge_reader.thresholds_for(reading.model)` inside `_trip_hard_band_reading`.
- **NAMED test red:** `GateHeadroomOverrideTripTests::test_headroom_override_trips_its_own_gate_and_not_its_neighbour`
- **TOTAL: 22 failed**, 429 passed. Also red: the CLI-boundary neighbour test, the
  no-silent-close test, the active-gate-default test, and the together-sweep. Same
  divergence caught from the *judged* side — M11 and M12 both kill the together-sweep, which
  is precisely what makes that test evidence for (c) rather than an assertion about it.

## M13 — the begin-work guard judging the gate being BEGUN

- **Branch broken:** `_trip_hard_band_reading(cl, base_dir, iid)` → `(cl, base_dir)` in
  `_trip_hard_gate`, so the guard judges the ACTIVE gate's reserve instead of the reserve of
  the gate you are trying to open.
- **NAMED test red:** `GateHeadroomOverrideTripTests::test_headroom_override_trips_its_own_gate_and_not_its_neighbour`
- **TOTAL: 1 failed**, 432 passed. Narrow, and the failing half is the neighbour half: under
  the mutation, `reconcile` inherits `execute`'s reserve and is refused too.

## M14 — the band decision's fail-tight default to the ACTIVE gate

- **Branch broken:** `_gate_headroom_tokens(cl, gate or active_id(cl))` → `(cl, gate)`, so a
  caller that names no gate silently drops the reserve (fails OPEN).
- **NAMED test red:** `GateHeadroomOverrideTripTests::test_headroom_override_defaults_to_the_active_gates_reserve`
- **TOTAL: 1 failed**, 432 passed. Narrow.

## M15 — advance's `require_why` naming the gate being closed — **KILLED**

- **Branch broken:** `require_why=_trip_hard_band_reading(cl, base_dir, getattr(args, "id", None))`
  → `require_why=_trip_hard_band_reading(cl, base_dir)`.
- **NAMED test red:**
  `GateHeadroomOverrideTripTests::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate`
- **TOTAL: 1 failed**, 433 passed, 155 subtests — measured under this log's own Method above (the
  file pair, no `-k`), the same way every other entry here is measured. Narrow. *(Corrected by the
  Commander after the rework re-review's NB-1. The first draft of this line read "383 deselected
  (frozen `headroom or override` selector)", which mislabelled its provenance twice: this log's
  Method applies no `-k` at all, and that selector deselects 413, not 383 — 383 was the deselect
  count of a single-test run. I re-measured under the Method before rewriting it. The pair's green
  baseline is 434 passed with this rework's new test, 433 without.)*
- **CORRECTION (g3 rework 2, reviewer finding B-1):** this entry originally declared M15 an
  **equivalent mutant** on the reasoning that `advance` refuses any gate that is not
  `in-progress` and `start` refuses to open a gate that is not the active one, so in every
  reachable state the gate being advanced IS the active gate and `args.id == active_id(cl)`.
  **That reasoning is false and the fixture is reachable, not manufactured.** It enumerated
  `start` and `advance` but never `block()` (`checklist_engine.py:2116`), which carries **no
  status guard** — it will block an already-`complete` gate — and `blocked` is **not** in
  `TERMINAL` (`{"complete", "skipped"}`, `:63`). So `active_id()` can move **backwards**,
  behind a later gate that is already `in-progress`: advance `g1` to `complete`, start `g2`
  (which carries the override), then `block g1` — `active_id(cl)` now reports `g1` again even
  though `g2` is the gate being closed. Under the mutation, `advance g2 --mechanical` reads
  `_trip_hard_band_reading(cl, base_dir)` with no gate argument, which defaults to
  `active_id(cl)` (i.e. `g1`, which carries no reserve and is well under its default hard
  line at the fixture's 12% fill) instead of `g2` (whose overridden hard line the 12% fill is
  over), so the no-silent-close refusal never fires and `g2` closes silently. The reviewer
  reproduced this independently at the CLI against the shipped engine before this correction
  was made; the named test above reaches the same state through public verbs
  (`start`/`advance`/`start`/`block`/`advance`) and is RED under this mutation (1 failed) and
  GREEN on shipped code (1 passed). The prior EQUIVALENT declaration, and the commit message
  of `f9925be6` asserting it ("1 declared EQUIVALENT rather than faked"), were both wrong.
  This entry is corrected in place, visibly, rather than rewritten as if it had always said
  this. The explicit `args.id` argument this mutation removes is exactly what makes the
  no-silent-close rule judge the gate actually being closed rather than whatever gate
  `active_id()` happens to report.

---

## The shipped datum

## M16 — the spine template's execute-gate reserve

- **Branch broken:** `"context_headroom_tokens": 30000,` deleted from the `execute` gate of
  `skills/commander/templates/COMMANDER_SPINE.template.json`.
- **NAMED test red:** `GateHeadroomOverrideTripTests::test_shipped_spine_template_carries_exactly_one_headroom_override`
- **TOTAL: 1 failed**, 432 passed. Narrow. That test reads the reserve back through the REAL
  resolver and pins the "and no other gate" half, so both deleting the value and spraying it
  across every gate (M9's shape, at the data layer) are caught.

---

## Summary

16 mutations, all 16 killed by a named test. M15 was originally logged as a declared
equivalent mutant; g3 rework 2 (reviewer finding B-1) found that declaration false and
corrected it in place above — the reasoning missed `block()`, and the fixture it called
unreachable is reachable through public verbs. Two (M3, M4) have a wide blast radius that
is attributable to a deliberate fixture `setUp` assertion, declared above rather than
dressed up. The four mutations that matter most — M1 (loosening becomes possible), M5 (the
mechanism dead-coded), M9 (the reserve leaks onto every gate), M15 (the no-silent-close rule
judges the wrong gate) — are each killed by a test written specifically because that failure
mode would otherwise pass unnoticed.
