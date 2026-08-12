# Implementation Result

## Assigned gate
`g3-implement` — issue #467, epic #418. Per-gate, tighten-only context-headroom override.

## Completed slice

All four parts, plus the mutation battery.

- **(a)** `gauge_reader.thresholds_for(model, headroom_tokens=0)` subtracts an absolute-token
  reserve from **both** caps before dividing by the window, with two non-negative clamps.
- **(b)** `checklist_engine._gate_headroom_tokens(cl, gate)` — the single resolver, reading
  `tasks.<gate>.context_headroom_tokens` and nothing else. Missing, malformed, negative, or
  parked in `config` all resolve to 0. No checklist-config tier was shipped.
- **(c)** That one resolver feeds **both** threshold call sites: `_trip_advisory` (the number
  the agent is SHOWN) and `_trip_hard_band_reading` (the number it is JUDGED against, which
  backs both the begin-work guard and g2's no-silent-close rule). `_trip_hard_band_reading`
  now takes the gate it is being asked about, defaulting fail-tight to the active gate.
- **(d)** The commander spine template's `execute` gate — and only that gate — carries
  `context_headroom_tokens: 30000`, with the reasoning in an adjacent `context_headroom_note`.

## Scope

**Files changed:**
- `scripts/gauge_reader.py` — `thresholds_for` signature, clamps, docstring. `_PROFILES` untouched.
- `scripts/checklist_engine.py` — new `_gate_headroom_tokens`; both threshold call sites;
  `_trip_hard_band_reading` gained a `gate` parameter; `_trip_hard_gate` and `dispatch`'s
  `advance` now name the gate they are asking about.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — `execute` gate only.
- `tests/test_gauge_reader.py` — new `ThresholdsHeadroomOverrideTests` (5 tests).
- `tests/test_checklist_engine.py` — new `GateHeadroomOverrideResolverTests` (3) and
  `GateHeadroomOverrideTripTests` (9).
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — new.
- `.agent-work/issue-467-trip-semantics/crew-plans/g3-implementer-plan.json` (+ journal) — my
  engine-driven plan.

**Not touched, though pre-authorized:** `tests/test_init_work_area.py`,
`tests/test_install_constellation.py`. The template edit needed no reconciliation — both
suites were green unchanged (138 passed, 380 subtests).

**Specific exclusions touched:** no. `_PROFILES` and `_DEFAULT_PROFILE` are byte-identical to
HEAD (the only diff lines mentioning them are new docstring prose); no config tier exists;
exactly one gate carries an override; the engine computes no threshold — it passes a token
count to `gauge_reader` and reads back fractions; nothing g2 shipped was re-opened.

## Behavior changed

Yes. A gate may now declare an absolute-token context reserve; the governor subtracts it from
that gate's soft and hard thresholds. Every gate without the key behaves exactly as before —
proven by a byte-identical-advisory assertion, not by inspection.

## Map Impact

- **Structural anchors touched:** `scripts/gauge_reader.py` — `thresholds_for` gains a second
  parameter and two clamps (:124, now :124-165). `scripts/checklist_engine.py` — new
  `_gate_headroom_tokens` (:1277) in the Trip section; `_trip_advisory` (:1485) and
  `_trip_hard_band_reading` (:1520-1543) are the only two threshold call sites and both now
  pass a resolved reserve; `_trip_hard_gate` (:1565) and `dispatch`'s advance (:2857) pass the
  gate under question. `skills/commander/templates/COMMANDER_SPINE.template.json` — `execute`.
- **Capabilities changed:** Trip thresholds — were global-per-model, now global-per-model
  tightened by an optional per-gate absolute-token reserve. Tighten-only.
- **Constraints honored:** `constraint:no-threshold-values` — the engine reads a token count
  and a fraction, computes neither. `constraint:tighten-only` — enforced by two clamps in
  `thresholds_for` plus a validating resolver, i.e. two independent layers. 
  `constraint:global-default-untouched` — `_PROFILES` unchanged.
- **Decisions:** `decision:gate-headroom-absolute-tokens`, `decision:headroom-not-cap`,
  `decision:no-config-tier` — all three implemented as given, none contradicted.
  `decision:execute-gate-reserve-value` — authored as **30000**; see below. Still `@grade: guess`.
- **Claims/evidence produced:** `claim:dc4-neighbour-isolation` — asserted on both sides by
  name, at one fill on one model, three different ways (unit guard, CLI boundary, advisory
  text) and killed by mutation M9/M13.
- **Triage candidates:** the schema doc gap and the settle-experiment gap, below.

## Test mode

**Required:** TDD (test-first) with mutation testing on every guard shipped.
**Satisfied:** yes. Each of the three code slices was RED before it was GREEN, and every guard
was mutated. Counts below are real, pasted from the runs.

## Evidence

### 1. The neighbour-isolation test (load-bearing) — DC4, both sides by name

```python
    GATE = "execute"          # the overridden gate: the run's longest
    NEIGHBOUR = "reconcile"   # the named neighbour: declares nothing, reserves nothing
    MODEL = "claude-opus-5"
    RESERVE = 50_000
    DEFAULT_SOFT, DEFAULT_HARD = 0.08, 0.15        # 80_000/1M, 150_000/1M
    OVERRIDDEN_SOFT, OVERRIDDEN_HARD = 0.03, 0.10  # (80_000-50_000)/1M, (150_000-50_000)/1M
    FILL = 0.12  # ONE fill, strictly between OVERRIDDEN_HARD and DEFAULT_HARD

    def test_headroom_override_trips_its_own_gate_and_not_its_neighbour(self):
        cl = self._cl()
        with self._gauge():
            with self.assertRaises(E.EngineError) as ctx:
                E._trip_hard_gate(cl, self.GATE, Path("."))
            # ... and the neighbour, at that same 12%, is not refused at all.
            self.assertIsNone(E._trip_hard_gate(cl, self.NEIGHBOUR, Path(".")))
            # The band decision itself, read straight from the single place that makes it:
            self.assertIsNotNone(E._trip_hard_band_reading(cl, Path("."), self.GATE))
            self.assertIsNone(E._trip_hard_band_reading(cl, Path("."), self.NEIGHBOUR))
        self.assertIn("12% is at/over the hard limit", str(ctx.exception))
```

Same checklist object, same `_read_gauge` patch, same fill, same model. Three further tests
carry the same both-sides discrimination at other surfaces: through the CLI boundary
(`start execute` refuses and leaves it pending; `start reconcile` returns
`reconcile -> in-progress`), on the advisory text, and on the no-silent-close rule. The
strongest form is `test_headroom_override_neighbour_advisory_is_byte_identical_to_no_override`
— the neighbour's advisory *with* an override on `execute` equals its advisory when no
override exists anywhere, while the overridden gate's advisory is asserted **not** equal.

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -v tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'
tests/test_checklist_engine.py::GateHeadroomOverrideResolverTests::test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideResolverTests::test_no_checklist_config_tier_supplies_a_headroom_override PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideResolverTests::test_wellformed_headroom_override_is_read_from_its_own_gate_only PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_also_governs_the_no_silent_close_rule PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_changes_the_advisory_for_its_gate_only PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_defaults_to_the_active_gates_reserve PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_moves_the_advisory_and_the_guard_together PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_neighbour_advisory_is_byte_identical_to_no_override PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_neighbour_is_unaffected_through_the_cli_boundary PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_never_trips_without_a_reading PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_headroom_override_trips_its_own_gate_and_not_its_neighbour PASSED
tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_shipped_spine_template_carries_exactly_one_headroom_override PASSED
tests/test_gauge_reader.py::ThresholdsHeadroomOverrideTests::test_headroom_override_can_only_tighten_never_loosen PASSED
tests/test_gauge_reader.py::ThresholdsHeadroomOverrideTests::test_headroom_override_never_judges_an_uncalibrated_model PASSED
tests/test_gauge_reader.py::ThresholdsHeadroomOverrideTests::test_headroom_override_of_zero_is_exactly_the_shipped_default PASSED
tests/test_gauge_reader.py::ThresholdsHeadroomOverrideTests::test_headroom_reserve_larger_than_a_cap_clamps_at_zero PASSED
tests/test_gauge_reader.py::ThresholdsHeadroomOverrideTests::test_headroom_reserve_tightens_both_caps PASSED
=========== 20 passed, 413 deselected, 125 subtests passed in 0.88s ===========
```

(20, not 17: three pre-existing tests match the frozen selector — two `Waiver` override-policy
tests and one `Hardening` config-override test.)

### 2. Tighten-only is unreachable to violate (load-bearing)

Structural, not just tested: **two independent layers**. The resolver refuses to emit anything
but a non-negative plain `int`, and `thresholds_for` clamps the reserve non-negative *and*
each reduced cap non-negative. Loosening would require both to fail.

I tried to loosen it directly, bypassing the resolver and calling `thresholds_for` with the
most hostile values I could construct:

```
shipped claude-opus-5 pair: (0.08, 0.15)
ATTEMPTS TO LOOSEN IT THROUGH THE RESERVE:
  reserve=-1           -> (0.08, 0.15)   no-op or tighter
  reserve=-80000       -> (0.08, 0.15)   no-op or tighter
  reserve=-1000000000000 -> (0.08, 0.15)   no-op or tighter
  reserve=-1e+308      -> (0.08, 0.15)   no-op or tighter
  reserve=-inf         -> (0.08, 0.15)   no-op or tighter
  reserve=True         -> (0.079999, 0.149999)   no-op or tighter
  reserve=False        -> (0.08, 0.15)   no-op or tighter
  reserve=-0.0         -> (0.08, 0.15)   no-op or tighter
  reserve=0            -> (0.08, 0.15)   no-op or tighter
  reserve=nan          -> (0.08, 0.15)   no-op or tighter

AND WHAT THE ENGINE RESOLVER LETS THROUGH AT ALL:
  authored nan        -> resolver returns 0
  authored -1000000000 -> resolver returns 0
  authored '30000'    -> resolver returns 0
  authored True       -> resolver returns 0
  authored 30000      -> resolver returns 30000
```

`nan` is the one value that defeats an ordinary comparison, and it is worth naming: `max(0,
nan)` returns 0 because `nan > 0` is false, so it lands on the safe side by luck of argument
order — but it never reaches there anyway, because the resolver rejects it as not-an-`int`.
The regression test for this is the hostile sweep
`test_headroom_override_can_only_tighten_never_loosen`: 6 models × 8 reserves = 48 subtests
asserting the returned pair is never above the shipped pair and never below 0.0, and that a
non-positive reserve reproduces the shipped pair **exactly**. Mutation M1 (drop the reserve
clamp) turns 18 of those subtests red and nothing else in the suite notices.

### 3. The malformed/negative test carries its positive control in the same test (load-bearing)

```python
    def test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not(self):
        malformed = ("30000", None, True, False, 1.5, float("nan"), [], {}, object())
        for value in malformed:
            with self.subTest(value=repr(value)):
                self.assertEqual(E._gate_headroom_tokens(self._cl(g1=value), "g1"), 0)
        for value in (-1, -30_000, -10 ** 12):
            with self.subTest(value=value):
                self.assertEqual(E._gate_headroom_tokens(self._cl(g1=value), "g1"), 0)
        # POSITIVE CONTROL, same resolver, same fixture shape:
        cl = self._cl(g1=30_000)
        self.assertEqual(E._gate_headroom_tokens(cl, "g1"), 30_000)
        self.assertNotEqual(E._gate_headroom_tokens(cl, "g1"), 0)
```

Proof that the control is load-bearing, not decoration: **mutation M5 dead-codes the entire
resolver (`return raw` → `return 0`) and the twelve negative assertions above still pass.**
Only the last two lines catch it. TOTAL for M5: 9 failed, 424 passed.

### 4. The advisory and the guard read the same resolved number (load-bearing) — demonstrated

Not asserted by inspection. `test_headroom_override_moves_the_advisory_and_the_guard_together`
sweeps 5 reserves × 13 fills = 65 samples and requires, at every sample, that
"the advisory says `>= hard`" and "the begin-work guard refuses" are the **same boolean** —
plus an anti-vacuity assertion that both outcomes actually occurred in the sweep.

The demonstration is the mutation pair: breaking **either** side alone makes them disagree.

- M11 (advisory stops reading the reserve): **20 failed** — including that sweep.
- M12 (band decision stops reading the reserve): **22 failed** — including that sweep.

The wiring grep shows the same thing structurally: one resolver, exactly two production call
sites, and they are the advisory and the guard.

```
$ grep -rn "_gate_headroom_tokens" --include=*.py scripts | grep -v "def _gate_headroom_tokens" | grep -v self_test
scripts/checklist_engine.py:1486:                                              _gate_headroom_tokens(cl, gate))      <- _trip_advisory   (SHOWN)
scripts/checklist_engine.py:1531:    `_gate_headroom_tokens` and applied by `gauge_reader.thresholds_for`. It     <- docstring
scripts/checklist_engine.py:1543:        reading.model, _gate_headroom_tokens(cl, gate or active_id(cl)))          <- _trip_hard_band_reading (JUDGED)
```

**Count: 2 external production call sites** (plus one docstring mention), and 11 test call
sites. Both required sides are present. `thresholds_for` likewise has exactly 2 production
call sites, and both pass a resolved reserve:

```
$ grep -rn "thresholds_for(" --include=*.py scripts | grep -v "def thresholds_for"
scripts/checklist_engine.py:1485:    soft, hard = _gauge_reader.thresholds_for(reading.model,
scripts/checklist_engine.py:1542:    _, hard = _gauge_reader.thresholds_for(
scripts/gauge_reader.py:44:# ... comment
scripts/gauge_reader.py:49:# ... comment
```

The authored key appears exactly once in the shipped templates:

```
$ grep -rn "context_headroom_tokens" --include=*.json skills
skills/commander/templates/COMMANDER_SPINE.template.json:80:      "context_headroom_tokens": 30000,
```

### 5. The mutation log

`.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — **16 mutations, 15 killed by a
named test, 1 declared equivalent with reasoning.** Every entry states the branch broken, the
NAMED failing test, and the TOTAL failure count. Summary:

| # | Branch broken | Named test red | TOTAL |
|---|---|---|---|
| M1 | tighten-only clamp on the reserve | `test_headroom_override_can_only_tighten_never_loosen` | 18 failed |
| M2 | non-negative clamp on both reduced caps | `test_headroom_reserve_larger_than_a_cap_clamps_at_zero` | 13 failed |
| M3 | reserve off the SOFT cap | `test_headroom_reserve_tightens_both_caps` | 12 failed |
| M4 | reserve off the HARD cap | `test_headroom_reserve_tightens_both_caps` | 12 failed |
| M5 | resolver return (mechanism dead-coded) | `test_malformed_or_negative_headroom_override_...` | 9 failed |
| M6 | resolver negative check | same | 3 failed |
| M7 | resolver bool exclusion | same | 1 failed |
| M8 | resolver int type check | same | 9 failed |
| M9 | per-gate scoping (reserve leaks to all gates) | `test_headroom_override_trips_its_own_gate_and_not_its_neighbour` | 7 failed |
| M10 | gate-level-only (config tier added) | `test_no_checklist_config_tier_supplies_a_headroom_override` | 1 failed |
| M11 | advisory reads the reserve | `test_headroom_override_moves_the_advisory_and_the_guard_together` | 20 failed |
| M12 | band decision reads the reserve | `test_headroom_override_trips_its_own_gate_and_not_its_neighbour` | 22 failed |
| M13 | guard judges the gate being BEGUN | `test_headroom_override_trips_its_own_gate_and_not_its_neighbour` | 1 failed |
| M14 | band decision's fail-tight active-gate default | `test_headroom_override_defaults_to_the_active_gates_reserve` | 1 failed |
| M15 | advance names the gate being closed | **none — declared equivalent** | 0 failed |
| M16 | spine template's execute reserve | `test_shipped_spine_template_carries_exactly_one_headroom_override` | 1 failed |

Two honest declarations, made rather than dressed up:

- **M15 has no narrow mutation and I am not claiming one.** `advance` refuses any gate that is
  not `in-progress`, and `start` refuses to open a gate that is not the active one, so in
  every reachable state the gate being advanced *is* the active gate and the two expressions
  are behaviourally identical. I judged it an equivalent mutant rather than manufacture an
  unreachable fixture to kill it. The explicit argument stays because it states intent and
  stops being equivalent the moment either refusal changes.
- **M3 and M4 have a wide blast radius (12 each), and the reason is declared:** nine of the
  twelve are the whole `GateHeadroomOverrideTripTests` class, killed by its own `setUp`, which
  asserts the fixture's band arithmetic before any test runs so a profile change breaks loudly
  instead of making every assertion in the class vacuous.

### 6. Confirmatory — uncalibrated-model fallback

`test_headroom_override_never_judges_an_uncalibrated_model` pins both halves: `thresholds_for`
stays TOTAL under an override (an unlisted model yields `(0.25, 0.50)` off `_DEFAULT_PROFILE`'s
own 200K window), **and** `read()` still returns `None` for that model, so no override can ever
be judged against a guessed window. #252's path is not reintroduced.

### 7. Confirmatory — `_PROFILES` untouched

```
$ git diff -U0 scripts/gauge_reader.py | grep -E "^@@"
@@ -124,2 +124,3 @@ class Reading:
@@ -131,0 +133,28 @@ def thresholds_for(model: str) -> tuple[float, float]:
@@ -134 +163,2 @@ def thresholds_for(model: str) -> tuple[float, float]:
```

Every hunk is inside `thresholds_for` (:124-165). No line of `_PROFILES` (:76) or
`_DEFAULT_PROFILE` (:98) changed; the only diff lines naming them are new docstring prose.

### 8. Confirmatory — no checklist-config tier

```
$ grep -rn "context_headroom" --include=*.py scripts | grep -i "config"
(no matches)
```

Plus `test_no_checklist_config_tier_supplies_a_headroom_override`, which parks the key at both
the checklist root and in `config` and asserts the resolver ignores both. Mutation M10 (add
the tier) turns exactly that one test red.

### 9. Verification commands

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py tests/test_init_work_area.py tests/test_install_constellation.py
571 passed, 535 subtests passed

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'
20 passed, 413 deselected, 125 subtests passed        # frozen closeout selector: collects, exit 0, not 5

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1832 passed, 2 skipped, 806 subtests passed
```

**Delta from the stated baseline (1815 passed, 2 skipped, 683 subtests):** +17 passed, +123
subtests, 0 skipped-count change.

The **+17 passed is exact and fully attributed**: 17 new tests, 5 in `test_gauge_reader.py` and
12 in `test_checklist_engine.py`. I measured the pre-change numbers rather than inferring them —
with my diff stashed, the two files ran **416 passed, 30 subtests** and the full suite ran
**1815 passed, 2 skipped, 682 subtests**, matching the handoff's passed-count exactly.

The **subtest delta is off by one and I am reporting it rather than rounding it away.** My two
files add 125 subtests (48 tighten-only sweep + 12 malformed/negative sweep + 65
advisory/guard sweep), measured directly: 30 before, 155 after. The full suite moved 682 → 806,
i.e. +124. And the handoff's stated baseline (683) is itself one above the 682 I measured on
this tree today. Both post-change full-suite runs agreed at 806, so this is not my diff being
nondeterministic: one subtest somewhere else in the tree enumerates something that varies with
run state. I did not chase it down — flagged below as a triage candidate.

## TDD evidence

Three red→green cycles, each observed before the code existed:

- **(a)** RED `52 failed, 1 passed` on `tests/test_gauge_reader.py -k 'headroom or override'`
  (the new signature did not exist) → GREEN `50 passed, 48 subtests`.
- **(b)** RED `15 failed, 3 passed` on `tests/test_checklist_engine.py -k 'headroom or override'`
  (no resolver) → GREEN `6 passed, 12 subtests`.
- **(c)** RED `6 failed, 7 passed` on the same selector (resolver existed, call sites unwired)
  → GREEN `18 passed, 125 subtests`.
- Refactor while green: yes — the fixture gained `PASS_COMMAND` postconditions so `advance`
  was legal, and one test was added after the fact (`..._defaults_to_the_active_gates_reserve`)
  specifically so mutation M14 had a killer.

## The reserve value in (d) — 30000, and why

**`decision:execute-gate-reserve-value` = 30000 tokens.** Still `@grade: guess`. Authored in
one obvious place — `skills/commander/templates/COMMANDER_SPINE.template.json`, the `execute`
gate — with the reasoning in the adjacent `context_headroom_note` so a later run can revise it
in place without re-deriving anything.

**Reasoning, presented as a guess and not as a measurement:**

1. `execute` is the gate that cannot be abandoned halfway. It drives every crew gate, and each
   crew dispatch costs tens of thousands of tokens. Beginning it with a few thousand tokens of
   room means tripping *inside* it and handing off mid-gate — the exact failure the reserve
   exists to prevent.
2. The only observation I was given is the commander at **~127K fill after a cold resume plus
   one full three-task gate**. That bounds one gate's marginal cost in the tens of thousands
   but cannot separate it from the resume baseline, so it supports a range, not a number.
3. 30K is a round number at the low end of that range. Against `claude-opus-5` (1M window, 80K
   soft / 150K hard) it moves `execute`'s begin-work line from 15% to **12%** and its advisory
   from 8% to **5%**, while every other gate keeps the shipped default untouched.
4. The earlier advisory is intended, not a side effect: the cheapest handoff seam in the whole
   run is *before* entering `execute`, and that is the seam the advisory names.
5. It also behaves sanely on the 200K model (90K/140K caps → 60K/110K, i.e. 30%/55%), which is
   the property an absolute-token reserve is chosen for.

**I did not attempt the named settle experiment, and I confirmed the handoff's reason
independently:** `gauge.json` holds only the latest reading (one record, overwritten), and the
per-gate context manifests under `.agent-work/*/context/` carry no fill value, so
"`fill_fraction` at the moment `execute` was started" is not recoverable from existing
artifacts. Nothing in this run makes it recoverable either. **A cheaper experiment does exist
and is worth one line in a future gate:** have the writer hook (or `_trip_advisory`) append the
`(gate, fill_fraction)` pair to a per-run log at each gate boundary. After a handful of
commander runs, the reserve becomes measurable rather than argued. Routing that is the
Admiral's call, not mine.

**I did not use the retracted role-blindness reading for anything** — not to justify this
number, not as supporting evidence.

## Docs/contracts touched
- None. `docs/CHECKLIST_SCHEMA.md` documents the Task object's optional keys (`why_exempt` is
  there) and now under-describes the schema by one key. It is outside my allowed scope, so I
  did not edit it — flagged below.

## Assumptions
- `context_headroom_tokens` as the key name, and `context_headroom_note` as the adjacent
  reasoning field. The handoff fixed the former (`tasks.<gate>.context_headroom_tokens`); the
  note key is mine, and it is inert — nothing reads it but the test that asserts the number is
  documented.
- The gate a reserve is judged against is the gate being **begun** (for `start`/`reopen`) and
  the gate being **closed** (for `advance`), defaulting to the active gate. An expensive gate's
  "I need this much room" is a statement about entering *it*.
- A reserve tightens **both** bands, so an overridden gate's SOFT advisory also fires earlier.
  The handoff specifies both caps, so I take this as intended rather than a side effect.

## Stop conditions hit
- None. No scope had to be exceeded, no exclusion touched, all required evidence was
  producible, and no decision outside my authority was needed. The neighbour-isolation test
  asserts both sides.

## Out-of-scope observations
- **`docs/CHECKLIST_SCHEMA.md` now under-documents the Task object** by one optional key
  (`context_headroom_tokens`). One table row plus a sentence in the Trip section. Outside my
  allowed scope; the natural home is the `reconcile` gate of this run.
- **The settle experiment for the reserve value needs a cheap fill-at-gate-boundary log**
  (above). Today no artifact records fill per gate, so the value stays a guess indefinitely
  unless something starts recording it.
- **One full-suite subtest is unaccounted for** (683 stated in the handoff / 682 measured here
  with my diff stashed / 806 after, against +125 measured directly on my two files). The test
  count is exactly stable and both post-change runs agreed, so nothing is flaky in the
  pass/fail sense — some suite's subtest enumeration depends on run state. Worth a cheap look
  by whoever owns suite hygiene, since it makes "explain any delta" harder than it needs to be
  for every future gate.
- **`_trip_advisory` and `_trip_hard_band_reading` each read the gauge file separately** on the
  same `current` call. Harmless today (the read is cheap and fail-safe), but it means the shown
  and judged numbers come from two reads of one file rather than one. Not a defect I could
  produce a failure for; recorded so it is not rediscovered.

## Workflow Feedback

- **Handoff gaps:** two, both minor. (1) The handoff fixes the *key* but not the *scope* the
  reserve is judged at — "the gate being begun" versus "the active gate" is a real choice, and
  I had to derive it from intent. It matters: mutation M13 is exactly that choice, and it is
  killable. Worth one sentence in a future handoff. (2) The **Verification Commands** baseline
  ("1815 passed, 2 skipped, 683 subtests") is stated without a revision, and its subtest half
  does not reproduce (682 here, measured at HEAD with my diff stashed). Per the pin-a-claim
  rule this baseline should carry the commit it was measured at — the passed-count matched
  exactly, so the pin would have turned a 20-minute reconciliation into a lookup.
- **Context rediscovered:** almost none — the Map Anchors carried line numbers, decisions with
  grades, and the retraction, which is the most useful handoff I have worked from. The one
  thing I had to dig up myself was how the *test fixtures* build a gated checklist (`gated`,
  `gate`, `_reading`, `_start_ns`, `PASS_COMMAND`) and that a gated gate needs at least one
  postcondition before `advance` is legal — I found that by getting refused.
- **Instructions improvised around:** my plan's `m4` postcondition asserted
  `grep -c context_headroom_tokens == 1` on the template, which my first draft broke by naming
  the adjacent note field `context_headroom_tokens_note` (same substring, count 2). The engine
  owns the plan file and I must not hand-edit it, and `amend` only rescopes *pending* gates
  while `m4` was in-progress — so I renamed the note field to `context_headroom_note` to
  satisfy the check as written. The rename is an improvement, but the general shape (a
  substring-counting check I can no longer edit once the gate opens) is a trap worth knowing
  about: **write `grep -c` postconditions against an anchor that cannot be accidentally
  extended.**
- **What would have made this easier:** the two frozen anti-patterns in this handoff ("the
  negative-only test cannot fail", "DC4 is met only by the and-not-its-neighbours half") were
  the single most valuable thing in it — they named the two vacuous tests I would otherwise
  have written and made both mutation-checkable. Keep that section in future handoffs verbatim,
  and consider adding the third of its kind: **an equivalence sweep is the only honest way to
  show two call sites cannot diverge**, since asserting it in prose is what (c) was at risk of
  becoming.

## Return status
`complete`
