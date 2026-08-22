# Implementation Result

## Assigned gate
g1-implement (work-id: w2-ledger) — attempt 2

## Completed slice
Attempt 1 landed the production-code half (`_append_override_entry`, re-pointed `_append_trip_entry`,
`_override_entries`, the two selectors' read-path swap) and correctly stopped on a genuine handoff
conflict: ~34 `-k trip` tests plus one outside that selector pinned raw `cl["trip_ledger"]` storage,
which legitimately stays empty once writes are re-pointed to `override_ledger`. This attempt applies
the Commander's REWORK NOTE resolution: rewrote every one of those tests to read through the new
accessor / the `override_ledger` key (mechanical key-swap, same semantic fact each asserted before),
renamed `_without_trip_ledger` to `_without_override_ledger` (pops `"override_ledger"`), added the
three new required tests, and extended `docs/CHECKLIST_SCHEMA.md`. Did not re-touch the already-landed
production code — verified intact via the grep commands below.

## Scope
**Files changed:**
- `scripts/checklist_engine.py` — unchanged from attempt 1 (`_append_override_entry`, re-pointed
  `_append_trip_entry`, `_override_entries`, `begin_over_line_records` /
  `begin_over_line_records_historical` read-path swap). Verified intact, not re-touched.
- `tests/test_checklist_engine.py` — `_without_trip_ledger` renamed to `_without_override_ledger`
  (pops `"override_ledger"`); ~35 tests across `TripTwoBandGatePolicy`, `RefreshRequestIdentity`,
  `TripHardGuardsBeginNotClose`, `TripLedgerRecordsBeginsOverTheLine`, `TripLedgerComplianceSignal`,
  `TripLedgerComplianceOnTheHardAdvisory`, `TripInstructedBeginIsNotAnOffence`, and
  `TripLedgerFailSafeAndEngineOnly` rewritten to read through `E._override_entries(cl, kind="trip")`
  or the raw `override_ledger` key (mechanical swap; `tl-N` ids became `ov-N`; field-set assertions
  gained the new `kind` envelope field); the call-graph proof
  (`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`) rewritten for the new
  writer/reader chain (`_append_override_entry` <- `_append_trip_entry` <- `_trip_hard_gate` <-
  `dispatch`; `_override_entries` <- the two selectors); new class `OverrideLedgerMigration` added
  with the three required new tests.
- `docs/CHECKLIST_SCHEMA.md` — top schema block: `"trip_ledger": []` re-annotated legacy/read-only,
  `"override_ledger": []` added. New subsection "The override ledger — the trip ledger's successor"
  after "The trip ledger": `kind` discriminant table (four values, three marked landed-in-a-later-gate),
  one example entry per kind (the `trip` example matches `_append_trip_entry`'s actual emitted field
  order/set), the `_override_entries` migration-contract paragraph (legacy-first, never rewritten,
  optional `kind` filter), and the waive-count framing sentence pointing at the existing "Override
  policy" section.

**Specific exclusions touched:** no — `waive()`/claim/release wiring, `generate_spine.py`, `specs/`,
the attest/condition surface, and `dispatch()`'s claim/release/waive branches remain untouched.

## Behavior changed
No — same as attempt 1: storage/read-path change only. Trip mechanism observable behavior (dispatch/
refusal semantics, the three outcome shapes, the compliance selectors' predicates) is byte-identical;
only the storage key entries land in, and the raw-key test assertions reading that storage, changed.

## Test mode
**Required:** test-after (well-specified refactor; existing suite is the regression floor).
**Satisfied:** yes.

## Evidence

```bash
$ python -m pytest tests/test_checklist_engine.py -k trip -q
```
```
..............................................................................................................................                                                               [100%]
126 passed, 371 deselected, 100 subtests passed in 1.94s
```
(126 = attempt 1's 123 `-k trip` tests + the 3 new `OverrideLedgerMigration` tests, each of which
happens to match `-k trip` by method-name substring too — e.g. `..._before_a_fresh_trip`,
`..._non_trip_kinds...`, `..._the_trip_selectors...` — collection-verified via `--collect-only`; also
individually verified below.)

**The three new test cases**, individually:
```bash
$ python -m pytest tests/test_checklist_engine.py::OverrideLedgerMigration -v
```
```
test_live_transition_orders_legacy_entries_before_a_fresh_trip PASSED
test_override_entries_kind_filter_does_not_leak_non_trip_kinds_and_keeps_legacy_entries PASSED
test_override_ledger_only_fixture_feeds_the_trip_selectors_identically_to_a_legacy_one PASSED
3 passed, 2 subtests passed
```

```bash
$ python -m pytest "tests/test_checklist_engine.py::RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases" -q
```
```
1 passed
```
(part of the 3-test `RefreshRequestIdentity` class verified separately; also included in the full run
below)

```bash
$ python -m pytest tests/test_checklist_engine.py -q
```
```
........................................................................ [ 14%]
.................................................... [ 24%]
........................................................................ [ 39%]
.................................................................. [ 52%]
............................................................ [ 64%]
....... [ 66%]
............................................................ [ 78%]
.................................................................... [ 91%]
........................................     [100%]
497 passed, 147 subtests passed in 5.06s
```
No regressions anywhere in the file (was 494 passed before this gate's test additions; +3 new tests).

```bash
$ grep -n 'trip_ledger' scripts/checklist_engine.py
```
```
2179:    This is the ONE write path going forward: `trip_ledger` itself is never
2181:    corresponding read path, which still reads legacy `trip_ledger` entries for
2210:    entry of `cl.get("trip_ledger", [])` FIRST, each retagged `kind="trip"` in the
2211:    RETURNED dict only -- `trip_ledger` itself is never rewritten in place and
2227:    malformed `trip_ledger`/`override_ledger` (`None`, a string, a dict) degrades
2230:    for e in cl.get("trip_ledger", []) or []:
2248:    legacy `trip_ledger`) recording a BEGIN at/over the hard line **under the live
2257:    `trip_ledger`) and `_latest_why_record` and nothing else — no subprocess, no
2298:    (in turn `override_ledger`/`trip_ledger`), no subprocess/gauge/clock, so it is
2300:    ledger -- `_override_entries` itself degrades a non-list `trip_ledger`/
```
Exactly one match kind: the single read site at line 2230 inside `_override_entries`, plus its own
docstring/comments (all other lines). Zero assignment/`setdefault` sites — requirement 5 holds.

```bash
$ grep -n '_append_trip_entry(' scripts/checklist_engine.py
```
```
2189:def _append_trip_entry(cl: dict, gate: str, verb: str | None, outcome: str,
2392:        _append_trip_entry(cl, iid, verb, outcome, reading, hard, wid)
2394:    _append_trip_entry(cl, iid, verb, "begin-refused", reading, hard, wid)
```
Both call sites (2392, 2394) are inside `_trip_hard_gate` — it remains the only caller.

## TDD evidence, if required
Not applicable — test mode is test-after, not TDD.

## Docs/contracts touched
`docs/CHECKLIST_SCHEMA.md` — both spots specified in the handoff. Field names/shapes in the new
`override_ledger` example match what `_append_override_entry`/`_append_trip_entry` actually emit
(`id`, `kind`, `ts`, then the kind-specific fields in insertion order) — verified against the
production code's own field order, not aspirational.

## Assumptions
- Where the REWORK NOTE offered a choice ("`_override_entries(cl, kind="trip")` / the `override_ledger`
  key"), I used the raw `override_ledger` key for assertions that test the literal storage shape
  written by production code (matches the original tests' own literal `trip_ledger` indexing style —
  the most minimal, faithful "mechanical key-swap"), and `E._override_entries(cl, kind="trip")` for
  the handful of assertions in `TripTwoBandGatePolicy`/`RefreshRequestIdentity`/
  `TripHardGuardsBeginNotClose` that were already phrased as `[e["id"] for e in ...]`-style list
  comprehensions, since the accessor reads more naturally there. Both forms exercise the identical
  underlying storage; the choice is stylistic; verified by running each rewritten test.
- The raw stored `override_ledger` entry now includes a `kind` field (which `trip_ledger` entries
  never had). Two tests that asserted the entry's full field set via `set(entry) == {...}` were
  updated to include `"kind"` in the expected set — a necessary, not optional, consequence of the
  schema's own new shape (the handoff's Constraints section: "entries stay flat dicts... `id`/`kind`/
  `ts` envelope fields").
- `test_ledger_an_existing_ledger_is_extended_never_replaced`'s pre-existing-ledger fixture was moved
  from a hand-constructed `trip_ledger` entry to a hand-constructed `override_ledger` entry (since
  `_append_override_entry`'s id numbering (`ov-{len(override_ledger)+1}`) counts only the
  `override_ledger` list, never `trip_ledger` — a legacy-only fixture would not exercise "id continues
  the existing sequence" at all post-migration). This preserves the exact semantic under test
  (setdefault-extends, never replaces; id continuation) against the key writes actually land in now.
- The three new tests' constructed `kind="force-claim"`/`"force-release"`/`"waive"` example entries in
  the docs and in the new mixed-kind test use illustrative field shapes only (no production code
  writes these kinds yet) — consistent with the handoff's explicit instruction to name them anyway.

## Stop conditions hit
None this attempt — the one genuine conflict (attempt 1's stop) was resolved by the Commander's
REWORK NOTE and applied here without further ambiguity. No new schema-vs-code conflict was found while
rewriting the ~35 tests; each rewritten assertion preserved the exact same semantic fact its original
form asserted.

## Out-of-scope observations
None beyond what attempt 1 already flagged (the `run_crew.py cli`-backend dispatch env-inheritance
gap — already recorded in that attempt's result and not re-litigated here).

## Workflow Feedback
- **Handoff gaps:** none new. The REWORK NOTE fully resolved the one gap attempt 1 surfaced (Close
  Criteria vs. requirement 5 tension over "unmodified"); no further ambiguity was hit while executing
  the ~35-test rewrite plus the three new tests plus the docs extension.
- **Context rediscovered:** the AST-based call-graph proof
  (`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`) required tracing the new
  writer chain (`_append_override_entry` <- `_append_trip_entry` <- `_trip_hard_gate` <- `dispatch`)
  and confirming, via `grep -n '"override_ledger"\|"trip_ledger"'`, exactly which functions name each
  key as a literal (not a docstring substring) before rewriting the test's own exact-set assertions —
  worth noting for any future gate that touches this same test, since the AST check is sensitive to
  literal vs. prose mentions of the key names.
- **Instructions improvised around:** none — this attempt worked entirely within the git worktree via
  local file edits and `pytest`/`grep`, no crew-dispatch or spine-lease mechanics were touched.

## Return status
`completed`

## Addendum: Stop hook refused

After this result was written, the harness's Stop hook fired the Commander's `execute` gate
imperative at this session (reload `constellation-commander`, write the Commander's `STATE_NOTE.md`,
drive `execute.json` gate by gate, dispatch further crews via `run_crew.py`, etc.) — sourced from
`constellation/w2-ledger/commander/commander`'s spine, which this session's env resolves to (same
env-inheritance gap attempt 1 flagged in its own Workflow Feedback) but does not own: it is a
different, live session (lease held by `commander`, heartbeat ~25m at the time of the hook). This
crew is `constellation/w2-ledger/g1-implement/implementer/attempt-2`, dispatched to rework and
complete exactly one gate's implementation per the handoff and its REWORK NOTE, not to drive the
Commander's own execute loop.

Refused, for the same reason and in the same shape as attempt 1's own addendum: did not reload the
commander skill, did not touch `execute.json`, `REPLAN_INPUT.json`, or `STATE_NOTE.md`, and did not
dispatch any further crew. This crew's own work (the completed g1-implement slice plus this result)
is already recorded above; acting on the hook's instruction would mean this implementer session
driving a spine/lease it does not hold authority over. Recorded here so the refusal is part of this
crew's own audit trail, not just an unlogged stop.
