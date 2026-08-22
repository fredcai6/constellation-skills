# Review Result

## Assigned Gate
`g1-implement` (work-id: w2-ledger) — reviewing attempt 2's result

## Result
`APPROVE`

## Handoff compliance
Full compliance. `_append_override_entry(cl, kind, **fields)`, re-pointed `_append_trip_entry`, and
`_override_entries(cl, kind=None)` all exist exactly as specified — flat entry dicts (`id`, `kind`,
`ts`, then kind-specific fields), `ov-N` ids scoped across all kinds. Verified independently (not
trusting the implementer's pasted output):

- `grep -n '_append_trip_entry(' scripts/checklist_engine.py` → exactly the definition (line 2189)
  plus two call sites (2392, 2394), both read in context and confirmed inside `_trip_hard_gate`.
- `grep -nE 'trip_ledger"?\]\s*=|setdefault\("trip_ledger"' scripts/checklist_engine.py` → zero
  matches (exit code 1). `trip_ledger` is never written again.
- `pytest tests/test_checklist_engine.py -k trip -q` → 126 passed (independently re-run).
- `pytest tests/test_checklist_engine.py -q` → **497 passed, 0 failed** (independently re-run;
  matches claimed baseline 494 + 3 new tests, no regressions).
- `pytest tests/test_checklist_engine.py::OverrideLedgerMigration -v` → 3/3 passed (independently
  re-run).
- The previously-outside-the-selector `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`
  → independently re-run, passes.

Read all 3 new `OverrideLedgerMigration` tests in full (not trusted from the name): each exercises
exactly what its name claims —
(a) `test_override_ledger_only_fixture_feeds_the_trip_selectors_identically_to_a_legacy_one` builds a
legacy `trip_ledger`-only fixture and an `override_ledger`-only fixture with an equivalent `kind="trip"`
entry, and asserts both selectors return identical results (field-for-field except `id`);
(b) `test_override_entries_kind_filter_does_not_leak_non_trip_kinds_and_keeps_legacy_entries` builds a
fixture with both a legacy `trip_ledger` entry and an `override_ledger` carrying a `force-claim` entry
plus a `trip` entry, and confirms `_override_entries(cl, kind="trip")` returns only the two trip
entries (no leakage), while the unfiltered call returns all three (no dropped legacy entry);
(c) `test_live_transition_orders_legacy_entries_before_a_fresh_trip` seeds legacy `trip_ledger` entries
then drives a REAL trip through `E.dispatch` (not hand-constructed), and confirms `_override_entries(cl)`
returns `[tl-1, tl-2, ov-1]` — legacy-first, chronologically correct.

## Scope drift
None. `git status --porcelain` shows exactly the three allowed files modified
(`scripts/checklist_engine.py`, `tests/test_checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`).
Read the full diff of `scripts/checklist_engine.py` end to end: confined to
`_append_override_entry`, `_append_trip_entry`, `_override_entries`, `begin_over_line_records`,
`begin_over_line_records_historical`. No specific exclusion touched — `dispatch()`'s claim/
release/waive branches, `waive()`/`claim()`/`release()`'s own bodies, `generate_spine.py`, `specs/`,
and `skills/*/templates/*.json` all show zero diff.

## Evidence verdict
Test mode `test-after` is appropriate (well-specified storage/read-path refactor, existing suite is
the regression floor). All required evidence commands independently re-run with matching output —
see Handoff compliance above. The AST-based call-graph proof
(`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`) was read in full: it genuinely
traces `_append_override_entry <- _append_trip_entry <- _trip_hard_gate <- dispatch` via `ast.walk`
over the real call graph, and separately confirms `_run_verb` reaches none of the three writer-side
functions — this is the real proof named in the handoff, not a weaker string-grep proxy.

## Code/doc quality
Minimal, maintainable, matches surrounding idiom. Spot-checked 5+ of the ~35 rewritten tests against
`git diff` (across `TripTwoBandGatePolicy`, `TripLedgerRecordsBeginsOverTheLine`,
`TripInstructedBeginIsNotAnOffence`, `TripLedgerFailSafeAndEngineOnly`) — each is a mechanical
key-swap preserving the exact semantic fact it asserted before (`_without_trip_ledger` →
`_without_override_ledger`, confirmed the rename correctly pops `"override_ledger"`; raw-key
assertions → `E._override_entries(cl, kind="trip")` reads). `test_ledger_an_existing_ledger_is_extended_never_replaced`
read directly: still tests setdefault-extends-never-replaces and id-continues-the-sequence (`ov-2`),
just against the new key. The two `set(entry) == {...}` field-set assertions that gained `"kind"`
(`test_ledger_entry_carries_every_field_including_the_live_why_ref`,
`test_the_instructed_begin_is_still_recorded_never_hidden`) both drive the real production write path
(`E.dispatch`) and confirm `kind` is a necessary consequence of the new envelope, not scope creep.

`docs/CHECKLIST_SCHEMA.md`'s new section read against the code's actual emission: the example
`trip` entry's field order (`id`, `kind`, `ts`, `gate`, `verb`, `outcome`, `fill`, `hard`, `model`,
`why_ref`) matches `_append_override_entry`'s literal construction
(`{"id": oid, "kind": kind, "ts": _now(), **fields}` with `_append_trip_entry`'s kwarg order) exactly.
The waive-count caveat sentence is present and correctly paraphrases the existing "Override policy"
section (verified the quoted source text exists at line 268).

**Fowler pass (r6-fowler):** 11 of 12 baseline smells absent; `speculative-generality` overridden —
the generic `kind`+`**fields` writer signature and the three forward-documented (not-yet-written)
kinds are, on their face, generality ahead of a proven caller, but this is subordinate to the
handoff's own settled/human decision (`decision:ledger-schema-is-override-ledger-with-kind`) naming
this exact envelope shape as the target, not implementer-invented speculation. Logged reason recorded
in `.agent-work/w2-ledger/FOWLER_PASS.json`; `verify_fowler_pass.py` exits 0.

## Map impact verdict
- **Evidence supports claimed change:** yes — grep/AST/test evidence directly backs the claimed
  storage/read-path-only change.
- **Constraints not violated:** yes — `constraint:engine-written-only` re-confirmed via the AST
  call-graph test (read in full, traces the real chain); trip mechanism behavior confirmed
  byte-identical by direct diff read (zero lines changed in `_trip_hard_gate`'s decision logic:
  the `instructed=` computation, outcome assignment, and `EngineError` message are all untouched)
  plus the full regression pass.
- **Notes match the diff:** yes — Map Anchors (`_append_trip_entry` re-pointed not removed,
  `_trip_hard_gate` context/unmodified, `_override_entries` new) all match exactly.
- **Decision candidates surfaced:** n/a — both named decision anchors (`decision:ledger-schema-is-override-ledger-with-kind`,
  `decision:merge-order-is-legacy-first`) are already `@grade: settled`, matched by the code as
  implemented; no new authority-requiring decision arose.
- **Durable context routed:** n/a — no new out-of-scope finding this gate.

## Reconciliation check
No divergence from recorded architecture. Both decision anchors match the implementation exactly;
`_override_entries`'s merge order (legacy-`trip_ledger`-first, then `override_ledger`) confirmed
directly in the function body, not just the docstring/handoff claim.

## Blockers
- none

## Out-of-scope observations
- none beyond what the implementer already flagged (the `run_crew.py cli`-backend dispatch
  env-inheritance gap — already recorded in the implementer's own result, not re-litigated here).

## Workflow Feedback
- **Handoff gaps:** none in the review task itself. One friction in the tooling this review drove:
  the reviewer skill's own `REVIEW_SURVEY.template.json` ships `r6-fowler`'s `c1` postcondition
  command with a literal `<work-id>` placeholder (`.agent-work/<work-id>/FOWLER_PASS.json`) that is
  never substituted when a reviewer builds its own survey by copying the template and only replacing
  the top-level `work_id` field (the substitution the template's own comment implies is "already
  done everywhere else in this survey" — but this one postcondition-command string is inside a
  nested `check.command`, not a top-level field, so a naive top-level substitute misses it). This
  caused a `REFUSED: r6-fowler: command postconditions unmet ['c1']` on first `record`. Fixed via the
  item's own documented REPAIR PATH (`amend` with a `retext-check` op, authority = the dispatching
  Commander per `SPINE_PARENT`) — recorded as amendment `retext-check r6-fowler.c1` in the survey's
  own audit trail.
- **Context rediscovered:** none beyond the above — the handoff and Map Anchors were unusually
  complete for this gate.
- **Instructions improvised around:** per this skill's own crew-dispatch doctrine (confirmed via
  `crew-runs.json`: this crew's entry carries `spine: null`), the `SPINE_FILE`/`SPINE_SESSION` env
  inherited from the dispatching process points at the Commander's own spine, not mine. Per the
  skill's "when nothing is bound" branch, authored and drove my own `survey` checklist at
  `.agent-work/w2-ledger/g1-implement-review/review.json` via the CLI (`checklist_engine.py`
  claim/start/record/append/attach/amend/consolidate/release), rather than touching the Commander's
  bound spine through the MCP door.
- **What would have made this easier:** fix the `REVIEW_SURVEY.template.json` r6-fowler postcondition
  command to either use a placeholder token the reviewer's own survey-instantiation step is documented
  to sweep for everywhere (not just top-level fields), or ship it already resolved relative to
  `work_id` at template-render time.

## Return status
`complete`

## Addendum: Stop hook refused

After this result was written and the survey lease released, the harness's Stop hook fired the
Commander's `execute` gate imperative at this session (reload `constellation-commander`, write the
Commander's `STATE_NOTE.md`, drive `execute.json` gate by gate, dispatch further crews via
`run_crew.py`, etc.) — sourced from `constellation/w2-ledger/commander/commander`'s spine, which
this session's env resolves to (the same `run_crew.py` `cli`-backend env-inheritance gap noted in
Workflow Feedback above and in both g1-implement implementer attempts' own addenda) but does not
own: it is a different, live session (lease held by `commander`, heartbeat ~34m at the time of the
hook). This crew is `constellation/w2-ledger/g1-implement/reviewer/attempt-1`, dispatched to
independently verify exactly one gate's implementation per the handoff, not to drive the Commander's
own execute loop.

Refused, for the same reason and in the same shape as both implementer attempts' addenda: did not
reload the commander skill, did not touch `execute.json`, `REPLAN_INPUT.json`, or `STATE_NOTE.md`,
and did not dispatch any further crew. This crew's own work (the consolidated APPROVE verdict plus
this result) is already recorded above; acting on the hook's instruction would mean this reviewer
session driving a spine/lease it does not hold authority over. Recorded here so the refusal is part
of this crew's own audit trail, not just an unlogged stop.
