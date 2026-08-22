# Review Result

## Assigned Gate
`g2-implement` (work-id: w2-ledger)

## Result
`APPROVE`

## Handoff compliance
Both #503 defects fixed exactly as specified: `waive()`'s evidence `produced_by` now echoes the
passed `authority` (verified: `E.waive(cl, ..., "commander", ...)` → `ev["produced_by"] ==
"commander"`, not the old hardcoded `"human"`). `authority_mismatch`/`expected_authority` are added
report-only, case/whitespace-normalized, on both the evidence payload and the `waived` marker, and
are genuinely absent (not `False`) when nothing to compare — confirmed by reading the code (fields
only added inside the `if mismatch:` block) and by tests using `assertNotIn`, never `assertFalse`.
`dispatch()`'s claim/release/generic-verb branches each call `_append_override_entry` directly for
`force-claim`/`force-release`/`waive`; grep and the updated AST chokepoint test both confirm zero
call sites inside `waive()`/`claim()`/`release()`'s own bodies. All required evidence commands were
re-run by me, not just trusted from the implementer's report.

## Scope drift
None. Only 3 files touched (`scripts/checklist_engine.py`, `tests/test_checklist_engine.py`,
`docs/CHECKLIST_SCHEMA.md`) — exactly the allowed scope. Diff hunks in the engine file are confined
to `waive()` (one contiguous block) and `dispatch()`'s release/claim/generic-waive branches;
`current`/`start`/`advance`/`attest`/`attach` are untouched. `_append_trip_entry`,
`_append_override_entry`'s own definition, `_override_entries`, and the two trip selectors show zero
diff — the diff only adds new *call sites* to `_append_override_entry`, never edits to it or the
other three excluded functions. `generate_spine.py`, `specs/`, the attest/condition surface, and
shipped spine templates are untouched (confirmed via `git status --porcelain`).

## Evidence verdict
Required evidence present and reproduced independently:
- Full suite: `python3 -m pytest tests/test_checklist_engine.py -q` → **511 passed, 147 subtests
  passed** (baseline 497 + 14 new tests — the delta is exactly new tests, not a mix with weakened
  old ones; I ran the full file myself rather than trusting the implementer's paste).
- `-k waive`: **34 passed**.
- `grep -n '_append_override_entry' scripts/checklist_engine.py` → 5 matches: 1 `def`, 1 call inside
  `_append_trip_entry` (g1), 3 calls inside `dispatch()` (this gate). Zero inside
  `waive()`/`claim()`/`release()`.
- Read `test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb` in full: it walks the
  AST and asserts the *exact* caller sets of `_append_override_entry`, `_append_trip_entry`,
  `_trip_hard_gate`, and `_override_entries` — not a grep count, a structural proof. It also asserts
  `waive`/`claim`/`release`'s own bodies contain zero calls to `_append_override_entry`. This
  genuinely proves what it claims.
- `test_dispatch_call_records_waive_claim_release_direct_call_does_not`: drives `waive`/`claim
  --force`/`release --force` through `E.main()` (the CLI path) and gets exactly `["force-claim",
  "force-release", "waive"]` in `override_ledger`; a second block calls `E.claim`/`E.waive`/
  `E.release` directly (not through `E.main`) and asserts `override_ledger` is entirely absent from
  the resulting dict. Confirmed this genuinely bypasses `dispatch()` — it calls the bare functions.
- `test_force_claim_noop_with_nothing_to_take_over_appends_nothing`: constructs a fixture with no
  prior `claim` at all (first-ever claim), so `previous_session_id` is `None` — not a force-claim on
  an already-empty ledger. Confirmed.
- `test_force_release_against_archived_path_gets_zero_banner_decoration`: captures real stdout via
  `contextlib.redirect_stdout` and asserts `E._ARCHIVED_BANNER` and the literal string `"ARCHIVED"`
  are both absent — checks the actual output text, not just a non-crash. Also confirms the entry
  still landed. Traced why release gets no banner: the `_append_override_entry` call sits inside
  `if v == "release":` *before* `return release(...)`, so `dispatch()` returns immediately and never
  reaches the archived-banner code further down — an early return, deliberately not converted to a
  fall-through.
- `test_dispatch_waive_lookup_matches_waive_own_which_only_lookup`: constructs `cond id "c1"` present
  in both `preconditions` (authority `"alpha"`) and `postconditions` (authority `"beta"`), waives the
  precondition, and asserts the ledger entry's `authority` is `"alpha"` (the precondition's), proving
  `dispatch`'s re-lookup honors `--which` with no cross-list fallback — the same lookup `waive()`
  itself used.
- No new `raise EngineError` anywhere in the diff: `git diff | grep '^+.*raise EngineError'` returns
  nothing. The mismatch path never refuses, confirmed by both the grep and by reading `waive()`'s
  full body (the only two `raise` lines present are pre-existing, unchanged context).
- `main()`'s single `save()` call site on the success path (line 4242, after `dispatch()` returns) is
  unchanged — re-confirmed by reading it directly, independent of the implementer's own claim.

## Code/doc quality
Minimal, matches surrounding conventions, well-commented where genuinely non-obvious (the
report-only/promotion-trigger rationale). `docs/CHECKLIST_SCHEMA.md`'s promotion-trigger paragraph is
semantically identical to the handoff's named trigger (conditions (a) and (b) match in substance; the
doc drops the fragile "line 284" citation and self-references "the authority field above" instead of
the full path — a reasonable adaptation for a self-referential doc, not a substance deviation). The
kind table's `force-claim`/`force-release`/`waive` rows now show field shapes that match the actual
`_append_override_entry` call sites and the example JSON — spot-checked directly against the code, not
just read as prose.

Fowler code-smell pass (`.agent-work/w2-ledger/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0):
12/12 smells rendered a verdict, 0 flagged, 2 overridden (`duplicated-code`, `feature-envy` — both in
dispatch()'s generic-waive branch, which re-implements the condition lookup and reaches into
`cond["waived"]`). Both overrides are logged against the handoff's own Protected Intent ("override
ledger reachable only from dispatch(), never from a verb's own body") and `decision:record-every-waive`
— the duplication/envy is the direct, tested cost of that chokepoint boundary, not an accidental
shortcut.

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Impact claim is backed by a reproduced test
  or direct code read (see Evidence verdict above).
- **Constraints not violated:** yes — `constraint:override-policy-authority-is-currently-advisory`
  still holds (doc still says "advisory"); `constraint:widening-live-refusal-report-only` honored (no
  new `raise`).
- **Notes match the diff:** yes, with one reconciled discrepancy — the implementer's result claims
  the doc kind-table was left stale and filed only as a triage candidate, but the actual working-tree
  diff (and the reviewer handoff) shows it was subsequently fixed (by the Commander, per the handoff).
  No outstanding drift in the current tree.
- **Decision candidates surfaced:** `decision:waive-fix-shape` and `decision:record-every-waive`
  (both `@grade: settled/human`) implemented exactly as graded — no silent narrowing (e.g. recording
  only forced waives) or widening (e.g. adding a refusal).
- **Durable context routed:** the implementer's out-of-scope doc-staleness observation was already
  resolved in this tree; no further routing needed.

## Reconciliation check
None outstanding. The one discrepancy between the implementer's result narrative and the actual diff
(doc table claimed stale vs. actually fixed) is explained by a subsequent Commander edit and does not
represent unreconciled drift in the current working tree.

## Blockers
- none

## Out-of-scope observations
- none new — the implementer's one out-of-scope observation (stale doc kind-table) is already
  resolved in the current diff.

## Workflow Feedback

- **Handoff gaps:** none — Task/Constraints/Close Criteria were precise enough to verify directly
  against the diff and tests with no ambiguity.
- **Context rediscovered:** `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` in this dispatched crew's
  environment pointed at the Commander's own `execute` spine (`spine_status` returned the
  Commander's gate content directly, and `crew-runs.json`'s entry for this reviewer crew shows
  `"spine": null"`) — not a spine bound for this reviewer. Per this session's own prior-run memory
  and the third/fourth observed shape of this exact pattern (same work-id, same day), I built and
  drove my own survey via the CLI (`.agent-work/w2-ledger/g2-implement-review/review.json`) rather
  than treating the Commander's spine as mine to advance. This confirms the reviewer skill's opening
  instructions ("a spine is bound for you; `spine_status` is your first call") do not yet branch on
  whether `SPINE_FILE` actually belongs to this session — a `run_crew.py` `cli`-backend dispatch with
  `spine: null` needs its own carve-out in the skill text, not just tribal knowledge from a prior run.
- **Instructions improvised around:** same as above — used the CLI-driven own-survey fallback path
  instead of the MCP door, since the door was bound to the parent, not to me.
- **What would have made this easier:** have the reviewer skill (and implementer skill) explicitly
  check `crew-runs.json`'s own `spine` field for the dispatched crew before trusting
  `SPINE_FILE`/`SPINE_SESSION`, rather than relying on `spine_status`'s refusal (which does not always
  fire) or `spine_bind`'s refusal as the confirming signal.

## Return status
`complete`
