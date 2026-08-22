# Implementer Handoff

## Gate
g1-implement (work-id: w2-ledger)

## Task
In `scripts/checklist_engine.py`, unify the trip-ledger write path into a
generic override ledger, without changing any observable trip behavior yet
(waive/claim/release wiring is a separate, later gate — g2).

1. Add a top-level function `_append_override_entry(cl: dict, kind: str, **fields) -> str`.
   Same idiom as today's `_append_trip_entry` (:2167-2187): `cl.setdefault("override_ledger", [])`,
   append-only (never mutate or remove an existing entry), ids scoped `ov-N` **across all kinds**
   (not per-kind — so ordering across kinds is recoverable from the id alone, mirroring
   `trip_ledger`'s `tl-N` idiom). Each entry is `{"id": ..., "kind": kind, "ts": ..., **fields}`.
2. Re-point `_append_trip_entry` to call `_append_override_entry(cl, "trip", gate=..., verb=...,
   outcome=..., fill=..., hard=..., model=..., why_ref=...)` instead of writing `trip_ledger`
   directly. `_trip_hard_gate` (:2263) remains the ONLY caller of `_append_trip_entry` — this must
   stay true; do not add any other caller. `_trip_hard_gate` is reached only from `dispatch()`
   (:3699) before `_run_verb` (:3703), for `start`/`reopen` only — this chokepoint property is
   NOT being changed in this gate, only the storage the write lands in.
3. Add `_override_entries(cl: dict, kind: str | None = None) -> list[dict]` as the ONE read path
   going forward:
   - Yields every entry of `cl.get("trip_ledger", [])` **first**, each retagged with `kind="trip"`
     in the RETURNED dict only (never write this retag back into `cl`) — this is a backward-compat
     read for spines that predate this migration; `trip_ledger` itself is NEVER rewritten in place
     and NEVER migrated — old archived JSON stays exactly as it is on disk.
   - Then yields every entry of `cl.get("override_ledger", [])`.
   - This "legacy first, then new" order is deliberately fixed (not sorted by timestamp): no
     `override_ledger` entry can chronologically precede the code deploy that introduces the key,
     so putting legacy entries first is always correct for any single spine's own continuous
     history, including one that straddles the deploy boundary mid-flight.
   - When `kind` is given, filter the merged sequence to entries whose `kind` matches.
4. Rewrite `begin_over_line_records` (:2192) and `begin_over_line_records_historical` (:2230) to
   source from `_override_entries(cl, kind="trip")` instead of reading `cl.get("trip_ledger")`
   directly. This is a read-path swap only — their existing outcome/why_ref filtering logic is
   unchanged; do not alter what they select for, only where they read from.
5. After this gate, `scripts/checklist_engine.py` must never write to the `"trip_ledger"` key again
   anywhere (no `cl["trip_ledger"] = ...`, no `cl.setdefault("trip_ledger", ...)`). It is fine, and
   required, for `_override_entries` to *read* `cl.get("trip_ledger", [])`.
6. Extend `docs/CHECKLIST_SCHEMA.md` in the same gate (not a follow-up commit) — two spots:
   - Near the top-of-file schema block (~line 77, where `"trip_ledger": []` is listed), add
     `"override_ledger": []` to the block with a one-line comment pointing at the new section.
   - Extend "### The trip ledger" (~line 459 onward): add a subsection describing `override_ledger`,
     its `kind` discriminant with the four values this ledger will eventually carry
     (`trip` / `force-claim` / `force-release` / `waive` — only `trip` is written as of this gate;
     the other three land in gate g2, name them here anyway since the schema documents the target
     shape), one example entry per kind (base the `trip` example on what `_append_trip_entry` today
     actually emits; you may show illustrative shapes for the other three, clearly marked
     "landed in a later gate"), and the migration-contract paragraph: legacy `trip_ledger` entries
     read through `_override_entries` retagged `kind="trip"`, ordered before `override_ledger`
     entries, never rewritten in place. Add one sentence noting that once `waive` entries land
     (g2), that kind's count is expected to be the loudest and least-exceptional of the four on
     ordinary runs — a plain policy-allowed waive is this schema's own documented routine path
     (see `docs/CHECKLIST_SCHEMA.md:267`, "A human who intends an artifact ... carries an
     `override_policy` on it and `waive`s it"), not a rare event — so a future reader of a closeout
     summary should not over-index on a nonzero `waive` count alone.

## Protected Intent
The trip ledger's proven "engine-written-only, reachable only from the dispatch chokepoint before
any verb runs" property must survive this refactor byte-for-byte in its OBSERVABLE behavior — every
existing trip-ledger test must pass unmodified. This gate only changes internal storage/read-path,
never trip semantics.

## Test Mode
TDD not required (this is a well-specified refactor with an existing test suite as the regression
floor), but test-after is mandatory: every new function/path needs its own test, and the full
existing trip-ledger test file must pass unmodified.

## REWORK NOTE (attempt 2 — reads this section first)

Attempt 1 correctly landed the production code (`_append_override_entry`, re-pointed
`_append_trip_entry`, `_override_entries`, the two selectors' read-path swap) and correctly
STOPPED rather than guess past a genuine conflict in this handoff: ~35 tests in
`tests/test_checklist_engine.py` assert directly on the raw `cl["trip_ledger"][0]`-style storage
key (including a shared helper `_without_trip_ledger` that pops only `"trip_ledger"` before an
immutability comparison), which now legitimately stays empty for anything written after this gate
lands. That is a real contradiction between "never write trip_ledger again" and "existing -k trip
tests pass UNMODIFIED" as originally written — attempt 1 was right to stop rather than dual-write
(explicitly forbidden) or silently reinterpret "unmodified."

**Resolution (Commander decision, in-latitude "implementation shape"):** "passes unmodified" meant
*the trip mechanism's observable behavior* (dispatch/refusal semantics, the three outcome shapes) is
unchanged — never that the test file's raw storage-key assertions are frozen text. Rewrite those
~35 tests (`-k trip` selection) PLUS `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`
(:3942, same root cause, outside the `-k trip` name filter — attempt 1 flagged this correctly) to
read through `_override_entries(cl, kind="trip")` / the `override_ledger` key instead of raw
`cl["trip_ledger"]` indexing. Update `_without_trip_ledger` to pop `"override_ledger"` (the key
entries now actually live under) — rename the helper to `_without_override_ledger` if that reads
better, updating its call sites. This is a mechanical key-swap in each assertion, not a weakening:
each rewritten test must still assert the exact same semantic fact (which entries exist, in what
order, with what fields) that it asserted before, just reading them through the new accessor. If a
test's assertion cannot be preserved this way without changing what it actually verifies, stop and
name that specific test rather than guessing.

Do NOT re-touch the already-landed production code from attempt 1 (verify it is intact via the
grep commands below) unless you find it does not actually support the rewritten tests correctly.

## Close Criteria
- `_append_override_entry`, `_append_trip_entry` (re-pointed), `_override_entries` all exist as
  specified above (attempt 1 landed this; verify intact).
- `_trip_hard_gate` is the only caller of `_append_trip_entry` (grep-verifiable).
- Every test in `tests/test_checklist_engine.py` selected by `-k trip`, PLUS
  `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`,
  passes — rewritten per the REWORK NOTE above to read through the new accessor where they
  previously indexed raw `trip_ledger`, asserting the identical semantic fact each did before.
- A new test: a fixture using ONLY the new `override_ledger` key (no `trip_ledger` key at all) with
  `kind="trip"` entries feeds `begin_over_line_records`/`_historical` identically to how a
  `trip_ledger`-only fixture does today.
- A new test: a fixture carrying BOTH a legacy `trip_ledger` (simulating an archived spine) and an
  `override_ledger` with unrelated kinds (e.g. `kind="force-claim"`, even though nothing writes that
  kind yet — hand-construct the fixture entry) reads correctly through `_override_entries(cl,
  kind="trip")`: no leakage of the non-trip kind into the trip view, no dropped legacy entries.
- A new test: a "live transition" fixture — a spine with legacy `trip_ledger` entries `tl-1`, `tl-2`,
  which THEN receives a fresh trip event (drive a `start`/`reopen` refusal through the real
  `_trip_hard_gate` path so `_append_trip_entry`/`_append_override_entry` actually run) — asserts
  `_override_entries(cl)` with no kind filter returns them in order `tl-1, tl-2, ov-1` (legacy first,
  chronologically correct).
- `grep -n 'trip_ledger' scripts/checklist_engine.py` shows exactly one match kind: reads inside
  `_override_entries` (and its own docstring/comments) — zero assignment/`setdefault` sites.
- `docs/CHECKLIST_SCHEMA.md` updated as specified; field names and shapes in the doc match what the
  code actually emits (self-consistency, not aspirational).

## Allowed Scope
- `scripts/checklist_engine.py`: `_append_trip_entry`, `_trip_hard_gate` (read-only, do not change
  its call site or the three existing outcomes' shapes), `_append_override_entry` (new),
  `_override_entries` (new), `begin_over_line_records`, `begin_over_line_records_historical`.
- `docs/CHECKLIST_SCHEMA.md`: the two spots named above.
- `tests/test_checklist_engine.py`: add new test cases; do not delete or weaken existing trip-ledger
  assertions. Pre-authorized to touch this file for new coverage.

## Specific Exclusions
- Do NOT wire `waive()`, `claim`, or `release` into `_append_override_entry` — that is gate g2, a
  separate implementer dispatch, deliberately sequenced after this one lands.
- Do NOT touch `generate_spine.py`, `specs/`, or the spec-to-template migration (epic standing rule).
- Do NOT touch the attest/condition surface of `checklist_engine.py` or any shipped spine template
  (fenced to a parallel `w2-basis` lane — outside this repo's worktree, but the surface itself is
  off-limits here too since it is the same file).
- Do NOT touch `dispatch()`'s claim/release/waive branches — those are g2's scope.

## Constraints
- `_append_override_entry(cl, kind, **fields)`: `kind` is a required positional/keyword string;
  `**fields` are stored verbatim in the entry dict alongside `id`/`kind`/`ts`. Do not invent an
  envelope+detail nesting — entries stay flat dicts (matches today's flat trip-ledger shape and
  keeps the two existing selectors' `e.get("outcome")`/`e.get("why_ref")` reads working unchanged
  on `kind="trip"` entries).
- `_override_entries`'s `kind` filter parameter is optional; omitting it returns the full merged,
  ordered sequence.
- Never write `trip_ledger` again — read-only henceforth.

## Map Anchors (inbound)
- **Map entry point:** `scripts/checklist_engine.py` (read `_append_trip_entry` :2167-2187,
  `_trip_hard_gate` :2263, `begin_over_line_records` :2192, `begin_over_line_records_historical`
  :2230, `dispatch` :3663 in that order — do not read `dispatch`'s claim/release/waive branches as
  in-scope, they are read-only context for understanding the chokepoint, not this gate's target),
  then `docs/CHECKLIST_SCHEMA.md` ("### The trip ledger" ~line 459, top schema block ~line 77).
- **Structural:** `struct:scripts/checklist_engine.py#_append_trip_entry, function`;
  `struct:scripts/checklist_engine.py#_trip_hard_gate, function`;
  `struct:scripts/checklist_engine.py#dispatch, function` (context only, not a target).
- **Capability:** `capability:engine-session-leasing-and-gate-advancement`;
  `capability:trip-ledger`.
- **Constraints/assumptions:** `constraint:engine-written-only` — the ledger must be reachable only
  from the dispatch chokepoint, provably, not asserted; `constraint:no-spec-migration` — do not
  touch generate_spine.py/specs/.
- **Decision anchors:**
  `decision:ledger-schema-is-override-ledger-with-kind` — override_ledger top-level key, kind
  discriminant, single merge-reading function, no archived-JSON migration.
  `@grade: settled/human · leans g1-implement,g1-review · settle: done at plan via design-it-twice
  convergence, see .agent-work/w2-ledger/PLAN_ALTERNATIVES.md`
  `decision:merge-order-is-legacy-first` — `_override_entries` yields retagged legacy trip_ledger
  entries before override_ledger entries.
  `@grade: settled/measured · leans g1-implement · settle: done, .agent-work/w2-ledger/PLAN_CRITIC.md
  Finding 5`
- **Evidence expectations:** `claim:trip-ledger-is-engine-written-only` — verified by grep + call-site
  trace at plan time; re-confirm the same grep here.
- **Map confidence flags:** none — this repo's architecture map is DEGRADED-UNPARSEABLE for this
  run (`.agent-work/w2-ledger/map-orientation.json`); work from the file/line anchors above, which
  are code-verified, not map-verified.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; `docs/CHECKLIST_SCHEMA.md`;
  `tests/test_checklist_engine.py`. Verify each with `git check-ignore <path>` exiting 1
  (not ignored) before you finish.

## Required Evidence
- `pytest tests/test_checklist_engine.py -k trip -q` output, full, showing all trip-related tests
  passing (load-bearing — this is the regression floor).
- The three new test cases' names and pass/fail, individually.
- `grep -n 'trip_ledger' scripts/checklist_engine.py` output pasted verbatim (load-bearing — this is
  how the chokepoint/no-more-writes claim is verified, not asserted).
- `grep -n '_append_trip_entry(' scripts/checklist_engine.py` output pasted verbatim, showing the
  definition plus exactly one call site (`_trip_hard_gate`).
- Full `pytest tests/test_checklist_engine.py -q` output (confirmatory — the whole file, not just
  `-k trip`, to catch any unrelated regression).

## Wiring Grep
```bash
grep -rn "_append_override_entry\|_override_entries" --include=*.py . | grep -v "def _append_override_entry\|def _override_entries"
```
State the count of call sites found for each symbol. `_append_override_entry` should show exactly
one caller after this gate (`_append_trip_entry`); `_override_entries` should show exactly two
callers (`begin_over_line_records`, `begin_over_line_records_historical`) plus your own new tests.

## Verification Commands
```bash
cd /home/tommy/projects/569-w2-ledger
python -m pytest tests/test_checklist_engine.py -k trip -q
python -m pytest tests/test_checklist_engine.py -q
grep -n 'trip_ledger' scripts/checklist_engine.py
grep -n '_append_trip_entry(' scripts/checklist_engine.py
```

## Suggested Model Tier
simple bounded — sonnet. This is a well-specified, mechanical refactor (widen a write path, add a
merge-reading function, swap two selectors' read source) with the design already decided at plan
time; no open architectural judgment is asked of you here.

## Authority
The ledger schema (override_ledger + kind discriminant, legacy-first merge order, flat entry shape)
was decided by the Commander at plan time via a design-it-twice convergence plus a cold critic pass
— do not re-litigate the schema shape. If you find the schema genuinely unworkable against the real
code (not just inconvenient), stop and report why rather than silently choosing a different shape.

## Stop Conditions
Stop and return if: the schema as specified conflicts with something concrete in the code you find
while implementing (name it); an existing trip-ledger test cannot be made to pass unmodified without
changing trip *behavior* (not just its storage); required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/w2-ledger/crew-handoffs/g1-implement-implementer-result.md` before ending your turn.
