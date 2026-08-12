# g2 mutation log — issue #467, Trip HARD guards BEGIN not CLOSE

Every guard shipped at `g2-implement`, mutated one at a time. For each: the exact source
branch broken, the **named** test that went red, and the **TOTAL** failure count for that
mutation. A mutation that breaks forty unrelated tests does not show the test defends the
branch — it shows the opposite, so the totals are reported whether they flatter the tests or
not.

**Method.** `scripts/checklist_engine.py` was copied to a pristine reference before the first
mutation. Each run applied exactly one textual replacement (asserted unique), ran
`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py`,
then restored from the pristine copy. Restoration was verified at the end with `diff`
(identical) and a clean 416-passed run. Failure names were derived with
`grep -E '^FAILED' | sed 's/^FAILED tests\/test_checklist_engine.py:://' | sort`; the TOTAL is
read from pytest's own summary line, which is authoritative where the two disagree (long
`FAILED` lines can wrap and undercount the grep — this happened only on M11b/M11c).

Green baseline for this file pair: **416 passed, 30 subtests passed**.

---

## M1 — `start` dropped from the guarded verb set

- **Branch broken:** `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` → `{"reopen"}`
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_start_refused_at_and_above_hard_without_refresh`
- **TOTAL: 7 failed**, 409 passed. Also red: `test_trip_begin_stale_why_ref_does_not_release_begin_work`,
  `test_trip_begin_refusal_names_the_concrete_why_id`,
  `TripTwoBandGatePolicy::test_hard_refuses_begin_work_at_and_above_hard_without_refresh`,
  `TripTwoBandGatePolicy::test_hard_refusal_leaves_state_unmutated`,
  `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`,
  `TripRealGaugeFileWiring::test_fresh_hard_gauge_sibling_of_spine_refuses_begin_work_then_passes_with_refresh`.
  All seven are `start`-guard tests (four of them the re-aimed ones) — the blast radius is the
  guard's own surface, not collateral.

## M2 — `reopen` dropped from the guarded verb set

- **Branch broken:** `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` → `{"start"}`
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_reopen_refused_at_hard_without_refresh`
- **TOTAL: 1 failed**, 415 passed. Exactly one test defends `reopen`, and it is the one named.

## M3 — `advance` put back into the guarded set (the #431 deadlock, restored)

- **Branch broken:** `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` → `{"start", "reopen", "advance"}`
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest`
  — **the permanent DC2 guard**
- **TOTAL: 6 failed**, 410 passed. Also red:
  `test_handoff_digest_names_the_understanding_written_at_the_tripping_gate`,
  `test_handoff_mechanical_close_refused_at_hard`,
  `test_handoff_why_exempt_is_suspended_at_hard`,
  `test_handoff_unmet_postconditions_still_refuse_before_the_why_demand`,
  `TripRealGaugeFileWiring::test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance`.
  All six exercise a close at/over hard, which this mutation refuses outright. This is the
  mutation that matters most: it restores the deadlock, and the permanent guard catches it.

## M4 — `advance`'s no-silent-close branch disabled

- **Branch broken:** `if require_why:` → `if False:` (in `advance`, :1975)
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_handoff_mechanical_close_refused_at_hard`
- **TOTAL: 3 failed**, 413 passed. Also red: `test_handoff_why_exempt_is_suspended_at_hard`,
  `TripTwoBandGatePolicy::test_hard_handoff_close_needs_a_why_even_with_a_refresh_request_pending`.

## M5 — the same rule unwired at the dispatch seam

- **Branch broken:** `require_why=_trip_hard_band_reading(cl, base_dir) is not None)` →
  `require_why=False)` (in `_run_verb`, :2806)
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_handoff_why_exempt_is_suspended_at_hard`
- **TOTAL: 3 failed**, 413 passed — the same three as M4.
- **Why both M4 and M5:** M4 proves the rule exists; M5 proves it is *wired to the gauge*. A
  guard that is implemented but never reached is the shipped-inert failure this gate exists to
  fix, and only M5 can catch it.

## M6 — the refresh hint reverted to the literal `<why-id>`

- **Branch broken:** `--field why_ref={why_id or '<why-id>'}` → `--field why_ref=<why-id>`
  (in `_refresh_attach_hint`, :1289)
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_handoff_refresh_hint_carries_the_concrete_why_id`
- **TOTAL: 3 failed**, 413 passed. Also red: `test_trip_begin_refusal_names_the_concrete_why_id`,
  `test_handoff_hard_advisory_reads_as_a_changed_instruction` — the two places the hint is
  rendered to an agent, which is the right blast radius.

## M7 — the HARD advisory reverted to the alarm wording

- **Branch broken:** the no-pending-request return of `_trip_advisory`'s HARD branch (:1469)
  replaced with the pre-#467 text `` `advance` is BLOCKED until you request a refresh ``
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_handoff_hard_advisory_reads_as_a_changed_instruction`
- **TOTAL: 2 failed**, 414 passed. Also red: `TripTwoBandGatePolicy::test_hard_advisory_on_current_points_at_attach`
  (re-aimed), which pins the same wording at the `dispatch` boundary.

## M8 — the below-hard early return removed from the band predicate

- **Branch broken:** `if reading.fill_fraction < hard: return None` deleted from
  `_trip_hard_band_reading` (:1495), so every reading reads as HARD
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_start_allowed_just_below_hard`
- **TOTAL: 5 failed**, 411 passed. Also red: `test_handoff_mechanical_close_still_allowed_below_hard`,
  `TripTwoBandGatePolicy::test_hard_never_refuses_below_hard`,
  `TripTwoBandGatePolicy::test_soft_never_forces_advance`,
  `TripRealGaugeFileWiring::test_fresh_soft_gauge_advises_on_current_but_advance_passes`.
  The last three are pre-existing SOFT-band tests and are red for the correct reason — with the
  threshold gone, the SOFT band is swallowed by HARD.

## M9 — #190's identity filter dropped at the guard

- **Branch broken:** `has_pending_refresh_request(cl, iid, why_ref=wid)` →
  `has_pending_refresh_request(cl, iid)` (in `_trip_hard_gate`, :1524)
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_stale_why_ref_does_not_release_begin_work`
- **TOTAL: 2 failed**, 414 passed. Also red: `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`
  (re-aimed). This is the evidence that #190's check survived the move verbatim.

## M10 — the gated-only fail-safe removed

- **Branch broken:** `if cl.get("type") != GATED: return None` deleted from `_trip_hard_band_reading` (:1489)
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_survey_never_refuses_begin_work`
- **TOTAL: 1 failed**, 415 passed.

## M11 — the None-reading fail-safe: **no specific mutation exists** (reported, not hidden)

Three attempts, reported in full because the result is a limitation of the tests, not a pass:

- **M11a (discarded — null mutation).** `if reading is None: return None` → `return reading`.
  **0 failures**, 416 passed. Correctly so: the two are the same value. Discarded as a
  non-mutation; it proves nothing either way and is logged only so the count is honest.
- **M11b.** The `if reading is None` check deleted outright (:1493).
  **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_none_reading_never_refuses_begin_work`.
  **TOTAL: 59 failed**, 360 passed.
- **M11c.** The check inverted to fail UNSAFE — a missing reading returns a synthetic
  `fill_fraction=1.0` Reading instead of None.
  **NAMED test red:** `TripHardGuardsBeginNotClose::test_handoff_no_silent_close_never_fires_on_a_none_reading`.
  **TOTAL: 47 failed**, 372 passed.

**Verdict, stated plainly:** by this gate's own standard, M11b and M11c do **not** demonstrate
that the three fail-safe tests defend that branch — 47–59 failures is exactly the "breaks forty
unrelated tests" pattern the standard rejects. The cause is structural rather than a test
weakness: nearly every fixture in the suite runs with no gauge file, so `reading is None` is the
path the whole suite takes, and any mutation to it changes the behaviour of everything. The
honest claim is therefore the weaker one: `constraint:fail-safe-on-no-reading` is **massively
over-determined** by the suite and cannot be regressed silently, but no single named test owns
it. Named coverage exists and is listed above; specificity is not claimed.

## M12 — `resume` guarded (the specific exclusion, violated on purpose)

- **Branch broken:** `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` → `{"start", "reopen", "resume"}`
- **NAMED test red:** `TripHardGuardsBeginNotClose::test_trip_begin_resume_is_not_guarded_at_hard`
- **TOTAL: 1 failed**, 415 passed. The exclusion ruling is pinned by exactly one test, and
  breaking the ruling is the only thing that trips it.

---

## Summary

| # | branch broken | named test | total failed |
|---|---|---|---|
| M1 | `start` out of the guarded set | `test_trip_begin_start_refused_at_and_above_hard_without_refresh` | 7 |
| M2 | `reopen` out of the guarded set | `test_trip_begin_reopen_refused_at_hard_without_refresh` | 1 |
| M3 | `advance` back in the guarded set | `test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest` | 6 |
| M4 | `advance`'s `require_why` branch disabled | `test_handoff_mechanical_close_refused_at_hard` | 3 |
| M5 | `require_why` unwired at dispatch | `test_handoff_why_exempt_is_suspended_at_hard` | 3 |
| M6 | hint reverted to literal `<why-id>` | `test_handoff_refresh_hint_carries_the_concrete_why_id` | 3 |
| M7 | HARD advisory reverted to alarm wording | `test_handoff_hard_advisory_reads_as_a_changed_instruction` | 2 |
| M8 | below-hard early return removed | `test_trip_begin_start_allowed_just_below_hard` | 5 |
| M9 | #190 identity filter dropped | `test_trip_begin_stale_why_ref_does_not_release_begin_work` | 2 |
| M10 | gated-only fail-safe removed | `test_trip_begin_survey_never_refuses_begin_work` | 1 |
| M11 | None-reading fail-safe | **no specific mutation available — see above** | 0 / 59 / 47 |
| M12 | `resume` guarded (exclusion violated) | `test_trip_begin_resume_is_not_guarded_at_hard` | 1 |

Eleven of twelve mutations turn their named test red with a blast radius confined to the
guard's own surface. M11 is reported as a limitation rather than dressed up as a pass.
