# Implementation Result

## Assigned gate
`g2-implement` (work-id: w2-ledger)

## Completed slice
PART A: `waive()` now echoes the passed `authority` into `produced_by` (never the literal `"human"`), and compares `override_policy.authority` against the passed `authority` (case/whitespace-normalized), report-only — setting `authority_mismatch`/`expected_authority` on both the waiver evidence payload and the `waived` marker on a mismatch, adding nothing on a match or when no policy authority is declared. `waive()` never refuses or blocks on a mismatch.

PART B: `dispatch()`'s claim, release, and generic/waive branches now each call `_append_override_entry` directly — after `claim()` returns, for a genuine forced takeover (`force-claim`); before the early `return release(...)`, for a forced non-owner release (`force-release`); after a successful `waive` via `_run_verb`, for every successful waive (`waive`, forced/mismatched or not). All three append call sites live in `dispatch()` only — never inside `waive()`/`claim()`/`release()`'s own bodies.

Also updated the g1-landed AST call-graph chokepoint proof (`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`) to reflect the new direct `dispatch -> _append_override_entry` edge, and added the named promotion trigger (verbatim) as a code comment near the mismatch-detection code and to `docs/CHECKLIST_SCHEMA.md`.

## Scope
**Files changed:**
- `scripts/checklist_engine.py` — `waive()`, `dispatch()` (claim/release/generic-verb branches only)
- `tests/test_checklist_engine.py` — new coverage (pre-authorized)
- `docs/CHECKLIST_SCHEMA.md` — `produced_by`/`authority_mismatch` doc + promotion-trigger text, added right after the existing `override_policy`/`waived`-marker paragraph

**Specific exclusions touched:** no — `_append_override_entry`/`_append_trip_entry`/`_override_entries`/the two trip selectors, `dispatch()`'s `current`/`start`/`advance`/`attest`/`attach` branches, `generate_spine.py`, `specs/`, and enforcement of the promotion trigger were all left untouched, as required.

## Behavior changed
Yes. `waive()`'s evidence `produced_by` now reflects the real authority (previously always `"human"`, a #503 defect). A brand-new, report-only `authority_mismatch`/`expected_authority` pair can now appear on waiver evidence/markers. `override_ledger` now gains `force-claim`, `force-release`, and `waive` entries (previously only `trip`), written exclusively from `dispatch()`.

## Map Impact
- **Structural anchors touched:** `struct:scripts/checklist_engine.py#waive, function` (produced_by + mismatch logic added); `struct:scripts/checklist_engine.py#dispatch, function` (three new `_append_override_entry` call sites in the claim/release/generic-verb branches).
- **Capabilities added/changed/affected:** `capability:override-authority-handling` — waive's authority is now recorded truthfully and compared (report-only) against a declared policy; claim/release/waive are now provably engine-written into `override_ledger` from the CLI chokepoint alone.
- **Constraints/assumptions touched:** `constraint:override-policy-authority-is-currently-advisory` (docs/CHECKLIST_SCHEMA.md, now documented alongside the new report-only mismatch field and its promotion trigger, still advisory/unenforced) — honored, not stressed. `constraint:widening-live-refusal-report-only` — honored: no new refusal path was added.
- **Decision candidates / resolved decisions:** `decision:waive-fix-shape` — implemented exactly as specified (one-token produced_by fix + chokepoint-side report-only mismatch read, not a refusal inside `waive()`). `decision:record-every-waive` — implemented: every successful waive is recorded, not only forced/mismatched ones.
- **Claims/evidence produced:** `claim:save-happens-once-after-dispatch-returns` re-confirmed by reading `main()` — appends inside `dispatch()` before its single `return` are safe; the release-branch append runs before `release(...)`'s own early `return`, which itself returns out of `dispatch()` before `main()`'s one `save()` call, so no double-write risk.
- **Trust limitations / drift found:** `docs/CHECKLIST_SCHEMA.md`'s override-ledger example table (lines ~638-668) still says `force-claim`/`force-release`/`waive` are "landed in a later gate" — that gate is this one, so the table is now stale. Left untouched per Allowed Scope ("the promotion-trigger addition only"); flagged below as a triage candidate rather than fixed unilaterally.
- **Triage candidates:** update `docs/CHECKLIST_SCHEMA.md`'s override-ledger kind table (~line 641-668) to move `force-claim`/`force-release`/`waive` out of "nothing writes them yet" and pin their now-real field shapes (the actual fields are `verb`, `session_id`, `previous_session_id`, `takeover_reason` for the two force-* kinds, and `task`, `cond`, `evidence`, `authority`, `reason`, `forced`, optionally `authority_mismatch`/`expected_authority` for `waive` — narrower than the illustrative `actor`/`prior_actor`/`check_id` shapes shown there today).

## Test mode
**Required:** test-after
**Satisfied:** yes — existing suite is the regression floor; new tests added per Close Criteria alongside the implementation.

## Evidence

```bash
$ python -m pytest tests/test_checklist_engine.py -k waive -q
..................................                                       [100%]
34 passed, 477 deselected in 0.54s
```
**Result:** pass

```bash
$ python -m pytest tests/test_checklist_engine.py -q
........................................................................ [ 14%]
.................................................... [ 24%]
........................................................................ [ 38%]
.................................................................. [ 51%]
................................................................................................................................................................................................... [ 89%]
................................................. [ 99%]
.....                                                               [100%]
511 passed, 147 subtests passed in 4.82s
```
**Result:** pass (whole file, confirmatory)

```bash
$ grep -n '_append_override_entry(' scripts/checklist_engine.py
2167:def _append_override_entry(cl: dict, kind: str, **fields) -> str:
2201:    return _append_override_entry(
3766:            _append_override_entry(
3792:                _append_override_entry(
3837:                _append_override_entry(cl, "waive", **fields)
```
**Result:** 4 call sites total in `scripts/checklist_engine.py` itself (the `def` line is not a call site) — 1 inside `_append_trip_entry` (g1), 3 inside `dispatch()`'s release/claim/generic-verb branches (this gate). Matches the Wiring Grep's expected count exactly; zero call sites inside `waive()`, `claim()`, or `release()`'s own bodies (proven mechanically by the updated AST test below, not by this grep alone).

```bash
$ python -m pytest tests/test_checklist_engine.py -k test_dispatch_call_records_waive_claim_release_direct_call_does_not -v
... PASSED
```
**Result:** pass — direct-call-vs-dispatch-call chokepoint test: driving `waive`/`claim --force`/`release --force` through `dispatch()` via `main()` appends 3 entries (`force-claim`, `force-release`, `waive`); calling `waive()`/`claim()`/`release()` directly leaves `override_ledger` entirely absent.

```bash
$ python -m pytest tests/test_checklist_engine.py -k test_force_release_against_archived_path_gets_zero_banner_decoration -v
... PASSED
```
**Result:** pass — a force-release against an archived-path spine gets zero `_ARCHIVED_BANNER`/"ARCHIVED" text in its output, and still appends its `force-release` entry.

```bash
$ python -m pytest tests/test_checklist_engine.py -k test_dispatch_waive_lookup_matches_waive_own_which_only_lookup -v
... PASSED
```
**Result:** pass — duplicate-lookup-parity test: a cond id `"c1"` present in both `preconditions` and `postconditions` with different `override_policy.authority` proves `dispatch`'s re-lookup and `waive()`'s own lookup both honor `--which` (no cross-list fallback), so the ledger entry reflects the actually-waived condition.

```bash
$ python -m pytest tests/test_checklist_engine.py -k test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb -v
... PASSED
```
**Result:** pass — updated AST/call-graph proof: `_append_override_entry`'s only callers are `_append_trip_entry` and `dispatch`; `_run_verb` and `waive`/`claim`/`release`'s own bodies reach none of the writer-side functions.

## Docs/contracts touched
- `docs/CHECKLIST_SCHEMA.md` — added a paragraph documenting `produced_by`/`authority_mismatch`/`expected_authority` right after the existing `override_policy`/waived-marker text, plus the named promotion trigger verbatim.

## Assumptions
- Current file line numbers for `waive()` (3527) and `dispatch()` (3745, at gate start) differ from the handoff's stale estimates (3475/3663) — re-located both by function name per the handoff's own caveat that estimates may drift.
- `main()` saves once after `dispatch()` returns (re-confirmed by reading `main()` directly, per the handoff's evidence-expectations anchor) — safe to append inside `dispatch()` before any return, including the release branch's early one.

## Stop conditions hit
None. The release-branch restructuring stayed a clean early return (capture-before-call, append-before-return) with no fall-through needed. No waive test required a new refusal. All required evidence was producible.

## Out-of-scope observations
- `docs/CHECKLIST_SCHEMA.md`'s override-ledger kind table (~line 641-668) is now stale ("landed in a later gate" for kinds this gate just landed) — filed as a triage candidate above rather than fixed, since Allowed Scope named only the promotion-trigger addition for this doc.

## Workflow Feedback

- **Handoff gaps:** none beyond the acknowledged line-number drift (handoff explicitly flagged this as likely stale, and it was).
- **Context rediscovered:** the dispatch()/`_run_verb` structure had shifted slightly since the handoff was authored (heartbeat/release are early returns before the current/claim/else chain, not literally "the elif v == 'claim': arm, ~line 3680-3684" etc.) — re-derived from the live source rather than the handoff's line citations, per its own caveat.
- **Instructions improvised around:** the implementer skill's spine-binding check found `SPINE_SESSION` bound to the Commander's own session/file (a dispatch that gave this crew no door of its own, per `references/checklist-engine.md`'s documented case) — authored and drove my own `IMPLEMENTER_PLAN.json` via the CLI directly (`scripts/checklist_engine.py --file <own plan>`) rather than the MCP door, per the skill's explicit fallback instruction for exactly this case. Also: my own plan's `m2` postcondition initially required a whole-suite-green check, but the AST chokepoint-proof test was explicitly assigned to a later plan item (`m4`) and necessarily fails until then — used `amend`'s `retext-check` op (an in-progress gate's sanctioned self-correction path) to narrow `m2`/`m3`'s check to exclude that one known/expected/in-scope-for-m4 test, rather than mis-sequencing the work to avoid a legitimate, temporary red.
- **What would have made this easier:** none — the handoff's Task/Constraints/Close Criteria were unusually precise and left little room for ambiguity; the dispatch-binding gap is a dispatcher-side defect (worth surfacing to whoever launches implementer crews going forward), not a handoff-content gap.

## Return status
`complete`
