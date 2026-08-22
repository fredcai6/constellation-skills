# Reviewer Handoff

## Gate
g1-implement (work-id: w2-ledger) — reviewing attempt 2's result (attempt 1 stopped BLOCK on a
genuine handoff conflict, resolved by the Commander's REWORK NOTE; attempt 2 completed).

## Survey State Location
`.agent-work/w2-ledger/g1-implement-review/review.json`

## What Was Implemented
Unified the trip-ledger write path into a new top-level `override_ledger` key with a `kind`
discriminant, while preserving the trip mechanism's own dispatch-chokepoint-only write property.
`_append_override_entry(cl, kind, **fields)` added; `_append_trip_entry` re-pointed to call it with
`kind="trip"`; `_override_entries(cl, kind=None)` added as the one read path (merges legacy
`trip_ledger` entries, retagged `kind="trip"`, ordered BEFORE `override_ledger` entries, for
backward-compatible reads only — `trip_ledger` itself is never rewritten in place); the two trip
selectors (`begin_over_line_records`, `begin_over_line_records_historical`) re-pointed to read
through `_override_entries`. `scripts/checklist_engine.py` never writes to `trip_ledger` again.
Attempt 2 additionally rewrote ~35 tests in `tests/test_checklist_engine.py` that pinned raw
`trip_ledger` storage (renamed `_without_trip_ledger` to `_without_override_ledger`), added a new
`OverrideLedgerMigration` test class (3 required tests), and extended `docs/CHECKLIST_SCHEMA.md`.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/569-w2-ledger` (branch `epic-569/w2-ledger`).
Use `git status --porcelain` then `git diff -- scripts/checklist_engine.py tests/test_checklist_engine.py docs/CHECKLIST_SCHEMA.md`
(untracked-safe; do not use `git diff --name-only`). Do not diff against `main` — this worktree is
ahead of main by unrelated prior-wave commits; the relevant change is the uncommitted working tree
only.

## Task Statement
Land `override_ledger` + `_append_override_entry` + `_override_entries`, re-point the trip writer,
without changing waive/claim/release wiring (that is gate g2, not yet dispatched) and without
changing trip mechanism *behavior* — only its storage.

## Close Criteria
- `_append_override_entry`, `_append_trip_entry` (re-pointed), `_override_entries` all exist as
  specified; flat entry dicts (`id`, `kind`, `ts`, then kind-specific fields), `ov-N` ids scoped
  across all kinds.
- `_trip_hard_gate` is the ONLY caller of `_append_trip_entry` — verify by grep, not by reading the
  implementer's claim: `grep -n '_append_trip_entry(' scripts/checklist_engine.py` should show
  exactly the definition plus two call sites, both inside `_trip_hard_gate`.
- `scripts/checklist_engine.py` never writes to `"trip_ledger"` again anywhere:
  `grep -nE 'trip_ledger"?\]\s*=|setdefault\("trip_ledger"' scripts/checklist_engine.py` must find
  ZERO matches (exit code 1).
- Every test selected by `pytest tests/test_checklist_engine.py -k trip -q` passes, INCLUDING the
  3 new `OverrideLedgerMigration` tests and the previously-outside-the-selector
  `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`.
  Full file: `pytest tests/test_checklist_engine.py -q` must show 497 passed, 0 failed (baseline
  before this gate was 494 passed; +3 new tests, no regressions, no deletions of assertions that
  changed what they verify).
- Specifically verify the 3 new `OverrideLedgerMigration` tests actually exercise what their names
  claim (read them, don't just trust green): (a) a fixture using ONLY `override_ledger` (no
  `trip_ledger` key) with `kind="trip"` entries feeds the two selectors identically to a
  `trip_ledger`-only fixture; (b) a fixture with BOTH a legacy `trip_ledger` and an
  `override_ledger` carrying an unrelated kind (e.g. `force-claim`) reads correctly through
  `_override_entries(cl, kind="trip")` — no leakage of the non-trip kind into the trip view, no
  dropped legacy entries; (c) a "live transition" fixture — legacy `trip_ledger` entries, THEN a
  fresh trip event driven through the REAL `_trip_hard_gate` path (not hand-constructed) — reads
  back via `_override_entries(cl)` (no kind filter) in order `<legacy entries>, <new entry>` —
  legacy-first, chronologically correct.
- `docs/CHECKLIST_SCHEMA.md`'s new section matches what the code actually emits, field-for-field —
  read the code's actual field order/shape and compare against the doc's example entries yourself,
  do not just check the doc reads plausibly. Confirm the doc includes the waive-count caveat
  sentence (that a nonzero `waive` count on ordinary runs is expected, not exceptional) even though
  no code writes a `waive` kind yet (that lands in gate g2) — the doc names it as a forward-looking
  contract, which is intentional per the handoff, not a doc/code mismatch.
- The rewritten ~35 tests must each still assert the SAME semantic fact they asserted before the
  rework (which entries exist, in what order, with what fields) — spot-check at least 5 of them
  against `git diff` to confirm the rewrite is a mechanical key-swap (`trip_ledger`→`override_ledger`
  or → `_override_entries(...)`), not a weakened or dropped assertion. Pay particular attention to
  `test_ledger_an_existing_ledger_is_extended_never_replaced` (IMPLEMENTER_RESULT reports its fixture
  was moved from a `trip_ledger` entry to an `override_ledger` entry — confirm this still tests
  "setdefault-extends, never replaces; id continues the sequence," just against the new key) and
  the two tests that gained `"kind"` in a `set(entry) == {...}` comparison (confirm this is a
  necessary consequence of the new envelope field, not scope creep).

## Allowed Scope
`scripts/checklist_engine.py` (the four/five named functions only — verify no other function in
this file changed by diffing the whole file, not just the named ones); `tests/test_checklist_engine.py`;
`docs/CHECKLIST_SCHEMA.md` (the two named spots).

## Specific Exclusions
Flag as a BLOCK if touched: `dispatch()`'s claim/release/waive branches (g2's scope, not this
gate's); `waive()`/`claim()`/`release()`'s own function bodies; `generate_spine.py`; `specs/`; any
file under the attest/condition surface or a shipped spine template (`skills/*/templates/*.json`).

## Constraints the Implementation Must Respect
- Trip mechanism observable behavior (dispatch/refusal semantics, the three trip outcome shapes:
  begin-refused/begin-released/begin-instructed) is byte-identical to before this gate — this is a
  storage/read-path change only. If you find ANY behavioral difference (not just a storage
  relocation), that is a BLOCK.
- `_override_entries`'s merge order is legacy-`trip_ledger`-first, then `override_ledger` — verify
  this ordering is actually what the code does (read `_override_entries`'s body), not just what the
  docstring/handoff claims.

## Map Anchors (inbound)
- **Structural:** `struct:scripts/checklist_engine.py#_append_trip_entry, function`;
  `struct:scripts/checklist_engine.py#_trip_hard_gate, function` (context/unmodified);
  `struct:scripts/checklist_engine.py#_override_entries, function` (new).
- **Capability:** `capability:engine-session-leasing-and-gate-advancement`; `capability:trip-ledger`.
- **Constraints/assumptions:** `constraint:engine-written-only` — the ledger must be reachable only
  from the dispatch chokepoint, provably (verify via the AST-based call-graph test the implementer
  reports rewriting: `test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb` — read it,
  confirm it actually traces `_append_override_entry <- _append_trip_entry <- _trip_hard_gate <-
  dispatch`, not a weaker string-grep proxy).
- **Decision anchors:**
  `decision:ledger-schema-is-override-ledger-with-kind` — override_ledger top-level key, kind
  discriminant, single merge-reading function, no archived-JSON migration.
  `@grade: settled/human · leans g1-implement,g1-review`
  `decision:merge-order-is-legacy-first` — chronologically correct for any spine straddling the
  migration.
  `@grade: settled/measured · leans g1-implement`
- **Evidence expectations:** `claim:trip-ledger-is-engine-written-only` — re-confirm via the grep
  commands in Close Criteria, do not accept the implementer's pasted grep output as sufficient on
  its own; re-run it yourself.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/w2-ledger/crew-handoffs/g1-implement-implementer-result.md`
(attempt 2; attempt 1's result is also in that directory for context on the resolved conflict).
Target postcondition: `g1-integrate.c1` (tests-pass command) and `g1-integrate.c2` (this review's
verdict).

## Suggested Model Tier
stronger — sonnet, reasoning-effort medium. The chokepoint call-graph proof and the "same semantic
fact, different storage key" claim across 35 rewritten tests both reward careful independent
verification over a quick skim; this is a regression-proof review, not a novel-design review.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed; the full suite does not show 497 passed, 0
failed when you run it yourself; any of the 3 new tests, when read, does not actually exercise what
its name claims; `trip_ledger` shows any write site; `_append_trip_entry` shows any caller besides
`_trip_hard_gate`.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

Write the full `REVIEW_RESULT` to
`.agent-work/w2-ledger/crew-handoffs/g1-implement-reviewer-result.md` before ending your turn.
