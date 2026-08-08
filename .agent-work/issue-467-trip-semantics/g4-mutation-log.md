# g4 mutation log — issue #467, the engine-only append-only trip ledger

Every guard shipped at `g4-implement`, mutated one at a time. For each: the exact source
branch broken, the **named** test that went red, and the **TOTAL** failure count. A mutation
that breaks forty unrelated tests does not show the test defends the branch — it shows the
opposite — so the totals are reported whether they flatter the tests or not, and the three
with a wide blast radius (N1, N7, N17) say so plainly.

**Method — the route the g4 handoff mandated, so a reviewer can repeat it exactly.**

1. The implementation was **committed first**, at `20240f44` (parent `9997c32d`).
2. For each mutation the driver applied **one** textual replacement **directly to
   `scripts/checklist_engine.py`** (asserting the anchor matched exactly once, and asserting
   afterwards that the file had actually changed — a `sed` that matches nothing leaves a green
   suite that reads exactly like a passing guard), ran

   ```
   FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py
   ```

   then restored the file and **asserted `git diff --quiet -- scripts/checklist_engine.py`
   before the next mutation**. Every entry below is `reverted_clean=True`; the battery aborts
   on the first dirty revert. Final state after the battery: clean.
3. No `git archive` snapshot and no temp tree — the mutation is applied to the tracked file in
   place and reverted with `git checkout`-equivalent restore, so there is no git-oracle noise.

Named failures were collected from **both** `FAILED` and `SUBFAILED` lines. Several of these
tests are `subTest` sweeps whose failures appear only as `SUBFAILED`, so a `FAILED`-only grep
would have reported "no named test" for N10. The TOTAL is read from pytest's own summary line,
which is authoritative.

**Green baseline for this file: 409 passed, 120 subtests passed** (at `20240f44`; 384 passed /
107 subtests before this gate's tests were added).

Driver and raw results (kept outside the repo, reproducible):
`C:/Users/fredc/AppData/Local/Temp/g4_mutate.py`, `.../g4_mutation_results.json`.

---

## The writer — `_append_trip_entry` and its two call sites in `_trip_hard_gate`

## N1 — the `begin-refused` entry is never written

- **Branch broken:** the `_append_trip_entry(cl, iid, verb, "begin-refused", …)` call before
  `raise EngineError(` deleted.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_begin_refused_is_recorded_and_the_healthy_world_records_nothing`
- **TOTAL: 23 failed**, 386 passed. **Wide, declared rather than hidden.** This is the mutation
  that removes the mechanism's most common write, so it takes out nearly the whole ledger
  surface: 20 of the 23 are this gate's own ledger/compliance tests, and the other three are
  the pre-existing no-mutation guards this gate reconciled
  (`test_hard_refusal_leaves_state_unmutated`, `test_trip_begin_start_refused_at_and_above_hard_without_refresh`,
  `test_trip_begin_reopen_refused_at_hard_without_refresh`), which now assert the entry the
  refusal is supposed to leave. Nothing outside the ledger's own surface notices, which is the
  correct blast radius.

## N2 — the `begin-released` entry is never written

- **Branch broken:** the `_append_trip_entry(…, "begin-released", …)` call before the release
  `return` deleted.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line`
- **TOTAL: 5 failed**, 404 passed. Also red: the CLI twin, the append-only sequence test, and
  the two advisory tests that render a released begin. **This is the more important of the two
  outcomes** — it is the case where work actually proceeded over the line — and it has its own
  named test rather than sharing N1's.

## N3 — append-only broken: the ledger is REPLACED rather than extended

- **Branch broken:** `ledger = cl.setdefault("trip_ledger", [])` → `ledger = []` followed by
  `cl["trip_ledger"] = ledger`.
- **NAMED test red:** `TripLedgerFailSafeAndEngineOnly::test_ledger_an_existing_ledger_is_extended_never_replaced`
- **TOTAL: 3 failed**, 406 passed. Narrow, and the right three: the two append-only tests plus
  the advisory count test, which can only see three entries if all three survived.

## N4 — the entry id stops being positional

- **Branch broken:** `tid = f"tl-{len(ledger) + 1}"` → `tid = "tl-1"`.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_is_append_only_across_repeated_begins`
- **TOTAL: 2 failed**, 407 passed. Narrow.

## N5 — the recorded `verb` is hardcoded instead of the verb that ran

- **Branch broken:** `"verb": verb` → `"verb": "start"` in the entry.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_is_append_only_across_repeated_begins`
- **TOTAL: 2 failed**, 407 passed. The other is the reconciled
  `test_trip_begin_reopen_refused_at_hard_without_refresh`, which asserts a `reopen` entry says
  `reopen`. A ledger that recorded every begin as `start` would be plausible and wrong, which
  is the class of defect this pins.

## N6 — the recorded `hard` drops the gate's own headroom reserve

- **Branch broken:** `_gate_headroom_tokens(cl, iid)` → `0` in the `thresholds_for` call.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_records_the_per_gate_hard_line_not_a_global_constant`
- **TOTAL: 1 failed**, 408 passed. Exactly one test defends this, and it is the positive
  control written for it: a test asserting only `hard == the default hard` would have stayed
  green here, because the default is what a dropped reserve produces.

## N7 — the entry stops recording which understanding it was written under

- **Branch broken:** `"why_ref": why_ref` → `"why_ref": None`.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_entry_carries_every_field_including_the_live_why_ref`
- **TOTAL: 12 failed**, 397 passed. **Wide, and declared.** `why_ref` is the field the whole
  compliance keying runs on, so losing it takes out every selector and render test as well as
  the entry-shape test. That is the correct radius: the field is load-bearing for the signal,
  not decorative. It is also the evidence for the one field I added beyond the eight the
  handoff named — without it, nothing downstream can tell a live mark from a superseded one.

---

## The selector — `begin_over_line_records`

## N8 — the FAIL-SAFE broken from the claim side

- **Branch broken:** `_trip_advisory`'s no-reading early return changed from
  `return _no_reading_advisory(base_dir)` to the same **plus** a TRIP LEDGER line whenever the
  selector is non-empty — i.e. the engine now reports non-compliance it cannot currently
  observe.
- **NAMED test red:** `TripLedgerFailSafeAndEngineOnly::test_ledger_a_none_reading_writes_no_entry_and_makes_no_compliance_claim`
- **TOTAL: 1 failed**, 408 passed. Narrow, and worth the note: g2's log reported that the
  None-reading fail-safe had **no specific mutation** — deleting or inverting the `reading is
  None` check breaks 47–59 unrelated tests, because no-reading is the path the whole suite
  takes. Mutating the **claim** rather than the **check** is a targeted way at the same
  property, and it kills exactly one test. It closes g2's M11 gap for the ledger's half of the
  fail-safe; it does not retroactively close it for the guard's half.

## N9 — the selector stops keying on the live understanding

- **Branch broken:** the `if e.get("why_ref") != live: continue` filter deleted, so a mark left
  under a superseded understanding reads as current non-compliance.
- **NAMED test red:** `TripLedgerComplianceSignal::test_compliance_signal_reads_the_live_understanding_not_a_superseded_one`
- **TOTAL: 3 failed**, 406 passed. Also red: the reopen-freshens test and the advisory's
  superseded test. All three are the keying's own surface. **This is the mutation the
  two-world-on-an-identical-ledger test exists for** — the defective and healthy spines there
  hold byte-identical ledgers, so only the keying can distinguish them.

## N10 — the selector stops filtering on the begin outcomes

- **Branch broken:** the `if e.get("outcome") not in ("begin-refused", "begin-released")`
  filter deleted.
- **NAMED test red:** `TripLedgerComplianceSignal::test_compliance_signal_counts_both_begin_outcomes_and_nothing_else`
- **TOTAL: 3 failed**, 409 passed. All three are `SUBFAILED` cases of that one sweep — the
  three non-begin outcome values it feeds. A `FAILED`-only grep would have reported "no named
  test" here, which is why both line kinds are collected.

## N11 — the whole selector dead-coded

- **Branch broken:** `return []` inserted at the top of `begin_over_line_records`, i.e. the
  mechanism removed rather than misconfigured (the M5 shape from g3).
- **NAMED test red:** `TripLedgerComplianceSignal::test_compliance_signal_is_empty_in_the_healthy_world_and_names_the_begin_in_the_defective_one`
- **TOTAL: 11 failed**, 400 passed. Ten of this gate's selector and render tests plus the
  fail-safe test's positive control. **This is the mutation that decides whether the tests
  discriminate at all** — a suite of negative-only assertions would have stayed entirely green
  here, which is precisely what happened to g3's M5 before its positive control was added. It
  was also run as this gate's RED observation for the selector, before the tests were green.
- **Declared limit:** one test in `TripLedgerComplianceSignal` stays green under this mutation —
  `test_compliance_signal_is_empty_on_a_spine_that_never_carried_a_ledger`. It is a
  backward-compatibility guard whose expected value genuinely is the empty list, so it cannot
  discriminate here and is not claimed to. It is paired with the positive controls above.

## N12 — the selector stops being pure

- **Branch broken:** `out.append(e)` → `e["seen"] = True; out.append(e)`, so reading the ledger
  stamps the stored entries.
- **NAMED test red:** `TripLedgerComplianceSignal::test_compliance_selector_is_pure_and_reads_stored_state_only`
- **TOTAL: 2 failed**, 407 passed. Purity is load-bearing because the selector is called from
  the read-only `current` path, where a write is both a side effect and — since `main()` does
  not save on `current` — a write that silently evaporates.

---

## The render — the extended `_trip_advisory` HARD branch

## N13 — the note dropped from the ALREADY-REQUESTED sub-branch

- **Branch broken:** `+ ledger_note` removed from the sub-branch an agent with a pending
  refresh-request sees.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_also_rides_the_already_requested_hard_advisory`
- **TOTAL: 2 failed**, 407 passed. Narrow. This sub-branch is the **released** case — the one
  where work actually proceeded — so extending only the other branch would have left the worse
  world silent. That is why it has its own test rather than sharing N14's.

## N14 — the note dropped from the no-request sub-branch

- **Branch broken:** `+ ledger_note` removed from the other HARD return.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world`
- **TOTAL: 3 failed**, 406 passed. Also red: the CLI-boundary test and the fail-safe test's
  positive control.

## N15 — the rendered count hardcoded to 1

- **Branch broken:** `{len(records)}` → literal `1` in the rendered line.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_names_the_count_and_the_latest_begin`
- **TOTAL: 1 failed**, 408 passed. Narrow, and it is caught only because that test builds a
  three-entry spine and asserts `"1 begin(s)"` is **absent**. A single-entry fixture would have
  passed under this mutation.

## N16 — the rendered entry is the FIRST recorded begin, not the latest

- **Branch broken:** `last = records[-1]` → `records[0]`.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_names_the_count_and_the_latest_begin`
- **TOTAL: 1 failed**, 408 passed. Narrow. Caught only because that test's three entries are of
  two different kinds — a fixture whose entries were all identical could not tell first from
  last.

## N17 — the note leaks into the SOFT band

- **Branch broken:** `+ ledger_note` appended to the SOFT return as well, so a retained mark is
  re-litigated on every `current`.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_never_appears_below_the_hard_band`
- **TOTAL: 23 failed**, 405 passed. **Wide, and declared.** Most are `SUBFAILED` samples of the
  pre-existing SOFT-band sweeps; the named failures also include
  `GateHeadroomOverrideTripTests::test_headroom_override_changes_the_advisory_for_its_gate_only`,
  `..._neighbour_advisory_is_byte_identical_to_no_override`,
  `TripRealGaugeFileWiring::test_fresh_soft_gauge_advises_on_current_but_advance_passes` and
  `TripTwoBandGatePolicy::test_soft_fires_at_and_above_soft`. The radius is honest: those tests
  pin the SOFT string by equality, so any addition to it is a real regression, and they catch
  this one without having been written for it.
- **CORRECTION (#467 B1 rework, g4-review NB2/handoff instruction):** the branch as logged above —
  `+ ledger_note` appended to the SOFT return — is **not reachable as written**. `ledger_note`
  (now `live_note`/`historical_note` after the B1 rework's split, same scoping before and after)
  is a local computed **inside** the `if fill >= hard:` block; the SOFT return sits in a sibling
  `if fill >= soft:` block below it, where that name is undefined. Applying the logged mutation
  literally raises `NameError: name 'ledger_note' is not defined` on any SOFT-band call — a
  **crash**, not a behavioural change, so the recorded radius of 23 is crash noise (every test
  that ever calls `_trip_advisory` in the SOFT band errors, not just the ones that would catch a
  real leak). The **behavioural** form of this mutant — actually computing the note in the SOFT
  branch too, rather than referencing an out-of-scope name — still kills
  `test_compliance_line_never_appears_below_the_hard_band`, with a **TOTAL: 1 failed**, everything
  else green. Corrected in place, visibly, rather than rewritten as if it had always said this
  (g3 M15 precedent, `g3-mutation-log.md`).

---

## The wiring

## N18 — the write site made reachable from a CLI verb

- **Branch broken:** `_run_verb`'s `start` branch calls `_trip_hard_gate(cl, args.id, base_dir,
  verb="start")` itself, so the ledger becomes writable from inside verb dispatch.
- **NAMED test red:** `TripLedgerFailSafeAndEngineOnly::test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`
- **TOTAL: 6 failed**, 403 passed. The call-graph guard catches it directly; the other five are
  behavioural — a doubled guard writes two entries per begin. **This is the mutation that
  decides the "engine-written only" claim.** The guard is read off the engine's own call graph
  with `ast`, not off a hand-maintained list of verbs, so it cannot drift out of date as verbs
  are added.

## N19 — dispatch stops telling the guard which verb ran

- **Branch broken:** `_trip_hard_gate(cl, …, base_dir, verb=v)` → `…, base_dir)`, so every
  entry records `verb: null`.
- **NAMED test red:** `TripLedgerRecordsBeginsOverTheLine::test_ledger_is_append_only_across_repeated_begins`
- **TOTAL: 11 failed**, 398 passed. A guard that is implemented but never wired to its input is
  the shipped-inert failure mode; N5 proves the field is recorded, N19 proves it is **fed from
  the dispatch boundary**. Only N19 can catch the unwiring.

---

## The B1 rework (#467 g4-rework, attempt 2) — N20–N22

The reviewer's B1 finding (see `g4-reviewer-result.md`): the mandated HARD-band close is
guaranteed to supersede the live why-record, emptying `begin_over_line_records` — so the one
close an over-the-line agent is required to make is also the one thing that silences the only
rendered signal. The fix adds a second, unkeyed selector (`begin_over_line_records_historical`)
and a second rendered line (`TRIP HISTORY`), computed once and appended to both HARD sub-branches
alongside the existing live line. These three mutations target exactly that addition.

**Method — adapted from the g4 method above, declared rather than silent.** The g4 method commits
the implementation first, then reverts each mutant with `git checkout --` and asserts
`git diff --quiet` against the committed baseline. This rework's implementer does not commit (the
Commander does), so `scripts/checklist_engine.py` is genuinely, correctly dirty in git for the
whole run — `git checkout --` here would destroy the real fix along with the mutant. The driver
(`.agent-work/issue-467-trip-semantics/g4-rework/mutate_n20_22.py`) instead snapshots the real,
uncommitted implementation before mutating and reverts each mutant against that snapshot,
asserting byte-identity (not `git diff --quiet`) before the next mutation. Same discipline
otherwise: one textual replacement per mutation, anchor asserted to match exactly once, asserted
to actually change the file, tests run, reverted, revert asserted clean before the next.

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py
```

Baseline for this file at the point these mutations were run: 34 passed / 21 subtests passed on
the targeted `-k 'ledger or compliance'` slice; full-file baseline 409 passed prior to this
rework's new tests (see close criterion 9 for the full-suite counts). Raw driver output:
`.agent-work/issue-467-trip-semantics/g4-rework/mutate_n20_22.py`; console output pasted into the
implementer result.

## N20 — the new (historical) selector dead-coded to `return []`

- **Branch broken:** `begin_over_line_records_historical`'s final `return out` replaced with
  `return []`, so the historical read always reports nothing.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent`
- **TOTAL: 13 failed** (`FAILED` + `SUBFAILED`), 407 passed, 126 subtests passed. The radius
  includes every other new historical-selector test (they all assert a non-empty result somewhere)
  plus the render-site test — a dead-coded selector cannot render anything, so every consumer of
  it goes red together. Reverted clean.

## N21 — the historical line dropped from the ALREADY-REQUESTED HARD sub-branch

- **Branch broken:** the already-requested `return (...) + live_note + historical_note` had
  `+ historical_note` removed, leaving `+ live_note` only — mirrors g4's own N13 one level up, now
  against the historical line specifically.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_also_rides_the_already_requested_hard_advisory`
- **TOTAL: 2 failed**, 416 passed, 128 subtests passed. Narrow and precise: only the tests pinning
  the already-requested branch's exact string are affected. Reverted clean.

## N22 — the historical selector keyed to the live why-record (re-creates B1)

- **Branch broken:** `begin_over_line_records_historical` given the SAME keying as the live
  selector (`_latest_why_record` lookup + `why_ref != live: continue`), collapsing it to a copy of
  `begin_over_line_records`. This is the mirror-image defect this whole rework exists to prevent:
  a live-only signal that goes silent at exactly the seam a fresh reader arrives at.
- **NAMED test red:** `TripLedgerComplianceOnTheHardAdvisory::test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent`
  — **killed AT THE SEAM**, as the handoff required: this test builds the exact offender's-own-close
  scenario and asserts the historical line still names the retained begin; with this mutation the
  historical selector is ALSO emptied by the same supersede, so the assertion that `TRIP HISTORY`
  is present fails, reproducing B1 byte-for-byte at the render site.
- **TOTAL: 4 failed**, 414 passed, 128 subtests passed. Narrower than N20 because the mutated
  selector still returns *something* in scenarios where nothing has yet been superseded (the
  keying is a no-op until the understanding actually moves on) — only tests that specifically
  exercise a supersede catch it, which is exactly the point: **the seam is a specific state, not
  every state**, and this mutant is only distinguishable there. Reverted clean.

**3 mutations, all 3 killed by a named test, all reverted clean.** No equivalent mutants declared.
Combined with N18/N19 above (unchanged by this rework — the write site and its wiring were not
touched) and the original N1–N17, the engine-written-only guarantee and the render-site-once
guarantee both hold with the historical selector added.

---

## Summary

| # | branch broken | named test | total failed |
|---|---|---|---|
| N1 | `begin-refused` never written | `test_ledger_begin_refused_is_recorded_and_the_healthy_world_records_nothing` | 23 |
| N2 | `begin-released` never written | `test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line` | 5 |
| N3 | ledger replaced, not extended | `test_ledger_an_existing_ledger_is_extended_never_replaced` | 3 |
| N4 | entry id not positional | `test_ledger_is_append_only_across_repeated_begins` | 2 |
| N5 | `verb` hardcoded | `test_ledger_is_append_only_across_repeated_begins` | 2 |
| N6 | `hard` drops the gate reserve | `test_ledger_records_the_per_gate_hard_line_not_a_global_constant` | 1 |
| N7 | `why_ref` not recorded | `test_ledger_entry_carries_every_field_including_the_live_why_ref` | 12 |
| N8 | fail-safe: a claim made on silence | `test_ledger_a_none_reading_writes_no_entry_and_makes_no_compliance_claim` | 1 |
| N9 | selector stops keying on the live understanding | `test_compliance_signal_reads_the_live_understanding_not_a_superseded_one` | 3 |
| N10 | selector stops filtering outcomes | `test_compliance_signal_counts_both_begin_outcomes_and_nothing_else` | 3 |
| N11 | selector dead-coded | `test_compliance_signal_is_empty_in_the_healthy_world_and_names_the_begin_in_the_defective_one` | 11 |
| N12 | selector stops being pure | `test_compliance_selector_is_pure_and_reads_stored_state_only` | 2 |
| N13 | note dropped from the released sub-branch | `test_compliance_line_also_rides_the_already_requested_hard_advisory` | 2 |
| N14 | note dropped from the refused sub-branch | `test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world` | 3 |
| N15 | rendered count hardcoded | `test_compliance_line_names_the_count_and_the_latest_begin` | 1 |
| N16 | rendered entry is the first, not the latest | `test_compliance_line_names_the_count_and_the_latest_begin` | 1 |
| N17 | note leaks into the SOFT band | `test_compliance_line_never_appears_below_the_hard_band` | 23 |
| N18 | write site reachable from a CLI verb | `test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb` | 6 |
| N19 | dispatch stops passing the verb | `test_ledger_is_append_only_across_repeated_begins` | 11 |
| N20 | historical selector dead-coded to `[]` | `test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent` | 13 |
| N21 | historical line dropped from the already-requested sub-branch | `test_compliance_line_also_rides_the_already_requested_hard_advisory` | 2 |
| N22 | historical selector keyed to live (re-creates B1) | `test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent` | 4 |

**19 mutations at g4-implement, all 19 killed by a named test; 3 more (N20–N22) at the B1 rework,
all 3 killed by a named test — 22 total, 0 survivors.** No equivalent mutants were declared —
after g3's M15 was found to be a false `EQUIVALENT`, a declaration of equivalence is a claim
needing evidence, and none of these twenty-two needed one. Three (N1, N7, N17) have a wide blast
radius, attributable in each case to a field or string that other tests legitimately pin, and
declared above rather than dressed up.

The four that matter most:

- **N11** — the selector dead-coded. Negative-only tests survive this; only the positive
  controls kill it. This is g3's M5 in this gate's clothing.
- **N9** — the keying dropped. The test that catches it holds an **identical ledger** in both
  worlds, so nothing but the keying can be what it measures.
- **N18** — the write site reachable from a verb. Read off the call graph, so it cannot drift.
- **N8** — a compliance claim made on silence. The fail-safe's failure mode is to look
  *cleaner*, not louder, which is why it is mutated from the claim side.
