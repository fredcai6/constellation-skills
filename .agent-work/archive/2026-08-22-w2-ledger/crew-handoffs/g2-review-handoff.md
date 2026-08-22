# Reviewer Handoff

## Gate
g2-implement (work-id: w2-ledger)

## Survey State Location
`.agent-work/w2-ledger/g2-implement-review/review.json`

## What Was Implemented
PART A: `waive()`'s evidence `produced_by` now echoes the passed `authority` (never hardcoded
`"human"` — issue #503 defect 1). `waive()` now reads `override_policy.authority` and compares it,
case/whitespace-normalized, against the passed `authority`; on a mismatch it sets
`authority_mismatch: true` + `expected_authority` on both the evidence payload and the `waived`
marker, report-only — `waive()` never refuses/blocks on a mismatch (issue #503 defect 2).
PART B: `dispatch()`'s claim/release/generic-verb branches now each call `_append_override_entry`
directly (never inside `waive()`/`claim()`/`release()`'s own bodies): `force-claim` on a genuine
takeover, `force-release` on a genuine forced non-owner release (release's early `return` preserved,
not converted to a fall-through), `waive` on every successful waive (not only forced/mismatched
ones). The Commander also fixed a stale doc table (docs/CHECKLIST_SCHEMA.md's override-ledger kind
table previously said "landed in a later gate" for these three kinds; now shows their real field
shapes read from the actual code).

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/569-w2-ledger` (branch `epic-569/w2-ledger`), on
top of g1's already-committed change (commit `2895dc8b`). Use `git status --porcelain` then
`git diff -- scripts/checklist_engine.py tests/test_checklist_engine.py docs/CHECKLIST_SCHEMA.md`.

## Task Statement
Fix waive()'s two #503 defects; wire waive/force-claim/force-release into `override_ledger`
exclusively from `dispatch()`, provably.

## Close Criteria
- `produced_by` echoes the passed authority for a non-`"human"` value (e.g. `"commander"`).
- `authority_mismatch`/`expected_authority` appear ONLY when `override_policy.authority` disagrees
  with the passed `authority` (case/whitespace-normalized) — ABSENT (not `false`) otherwise,
  including when there is no declared `override_policy.authority` at all.
- `waive()` still succeeds and returns identically (same return string shape) on a mismatch — it
  NEVER blocks. Confirm by reading `waive()`'s body directly: no new `raise EngineError` was added
  for the mismatch case.
- `grep -n '_append_override_entry' scripts/checklist_engine.py` shows call sites ONLY inside
  `dispatch()` (the release branch, the claim branch, the generic/waive branch) plus g1's own call
  inside `_append_trip_entry` — ZERO inside `waive()`, `claim()`, or `release()`'s own function
  bodies. Verify this by reading the updated AST-based chokepoint test
  (`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`) in full and confirming it
  actually asserts this, not just by trusting the grep count.
- A test drives `waive`/`claim --force`/`release --force` through `checklist_engine.dispatch()`
  (the CLI path via `main()`) and asserts the resulting `override_ledger` entries land; a companion
  test calls `waive()`/`claim()`/`release()` directly (library functions, bypassing dispatch) and
  asserts `override_ledger` is UNCHANGED. Read both tests, confirm the direct-call test genuinely
  bypasses dispatch (doesn't accidentally route through it).
- `claim --force` with no actual prior owner (nothing to take over) produces NO `force-claim` entry
  — read the test, confirm it constructs a fixture with no pre-existing `engine_session` (or one
  with no `previous_session_id`), not just a force-claim on an already-empty ledger.
- A force-release against an archived-path spine gets ZERO archived-banner decoration in its output
  message, unchanged from before this gate — read the test and confirm it actually checks the
  output text (e.g. absence of `_ARCHIVED_BANNER`'s content), not just that the function didn't
  crash.
- The duplicate-lookup-parity test: read it and confirm it constructs a condition id that exists in
  BOTH `preconditions` and `postconditions` with DIFFERENT `override_policy.authority` values, and
  asserts dispatch's re-lookup used the same `--which`-scoped lookup `waive()` itself used (not a
  lookup that could fall back to the wrong list).
- Every existing test selected by `-k waive` passes; full file passes with no regressions (baseline
  was 497 after g1; expect 511 after g2's additions — confirm the actual delta is all new tests, not
  a mix of new tests and silently-weakened old ones).
- `docs/CHECKLIST_SCHEMA.md`'s promotion-trigger text matches the handoff's named trigger verbatim
  (both conditions (a) and (b)); the kind table's `force-claim`/`force-release`/`waive` rows show
  field shapes that match what the code actually emits (spot-check against the `dispatch()` call
  sites directly).

## Allowed Scope
`scripts/checklist_engine.py` (`waive()`, `dispatch()`'s claim/release/generic-verb branches only);
`tests/test_checklist_engine.py`; `docs/CHECKLIST_SCHEMA.md` (the promotion-trigger paragraph and
the kind-table fix).

## Specific Exclusions
Flag as a BLOCK if touched: `_append_override_entry`/`_append_trip_entry`/`_override_entries`/the
two trip selectors (landed in g1, should show zero diff this gate); `dispatch()`'s
`current`/`start`/`advance`/`attest`/`attach` branches; any enforcement of the promotion trigger
(it must stay report-only, no new `raise` anywhere in the mismatch path); `generate_spine.py`,
`specs/`, the attest/condition surface, shipped spine templates.

## Constraints the Implementation Must Respect
- The release-branch append runs before the existing `return release(...)` — confirm the early
  return itself is textually still present and unconverted to a fall-through (read the diff line by
  line around that branch, don't just trust the passing test).
- `authority_mismatch`/`expected_authority` absence-is-meaningful (not `false`/`None` when nothing
  to compare).

## Map Anchors (inbound)
- **Structural:** `struct:scripts/checklist_engine.py#waive, function`;
  `struct:scripts/checklist_engine.py#dispatch, function`.
- **Capability:** `capability:override-authority-handling`.
- **Constraints/assumptions:** `constraint:override-policy-authority-is-currently-advisory`;
  `constraint:widening-live-refusal-report-only` — re-confirm no new refusal was actually added
  anywhere in the diff (grep for new `raise EngineError` calls in the touched functions and account
  for each one).
- **Decision anchors:** `decision:waive-fix-shape` (`@grade: settled/human`);
  `decision:record-every-waive` (`@grade: settled/human`) — confirm the implementation matches both
  exactly, no silent narrowing (e.g. only recording forced waives) or widening (e.g. adding a
  refusal).
- **Evidence expectations:** `claim:save-happens-once-after-dispatch-returns` — re-confirm by
  reading `main()`'s single `save()` call site, independent of the implementer's own claim.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/w2-ledger/crew-handoffs/g2-implement-implementer-result.md`.
Target postcondition: `g2-integrate.c1` (tests-pass command) and `g2-integrate.c2` (this review's
verdict), plus `g2-integrate.c3` (AST-based no-direct-call-in-verb-bodies check).

## Suggested Model Tier
stronger — sonnet, reasoning-effort medium. The chokepoint proof and the release-branch
control-flow preservation both reward careful independent verification.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed; the full suite does not show all-green when
you run it yourself; the AST chokepoint test does not actually prove what it claims when read in
full; any new `raise` was added anywhere in the authority-mismatch path (a refusal, forbidden by
the report-only requirement).

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

Write the full `REVIEW_RESULT` to
`.agent-work/w2-ledger/crew-handoffs/g2-implement-reviewer-result.md` before ending your turn.
