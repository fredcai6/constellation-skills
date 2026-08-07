# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g1 — Enforcement scripts + spine resolution (issue-58)

## Rework note
This is **attempt-3**, reworking attempt-2 (commit `1f7c460`) per a reviewer BLOCK. Reviewer finding: `.agent-work/issue-58/crew-handoffs/g1-review/REVIEW_RESULT.md`. Defect: in `scripts/verify_spec_confirmed.py`, the field regexes for `Confirmed by:` and `Date:` used `\s*` between the colon and the capture group; on a blank field, `\s*` consumed the line break and captured the *next* field's line as this field's value, so a CONFIRMED spec with a blank `Confirmed by:` (or blank `Date:`) silently PASSED confirm phase instead of failing — the one forbidden failure mode on this hard-gate path. Fixed in commit `802ab07` (below); everything else from attempt-2 is unchanged and still holds.

## Completed slice
Built the mechanical enforcement layer for constellation-explorer: `verify_cycles.py` (explore-step hard gate — refuses close on zero or unconsolidated cycles), `verify_spec_confirmed.py` (review/confirm hard gate — refuses on incomplete Confirmation block, empty Disposition cells, missing findings table, or a loud `UNCONFIRMED — DO NOT CUT` status/header line), and a generic `<skill-dir>` token on `resolve_spine()` alongside the untouched `<commander-skill-dir>` token. All four required test files exist with green and red cases, including the two new regression cases added in this rework. Commits `1f7c460` (initial) + `802ab07` (rework fix).

## Scope
**Files changed (across both commits):**
- `scripts/verify_cycles.py` (new, commit `1f7c460`)
- `scripts/verify_spec_confirmed.py` (new in `1f7c460`; field-regex fix in `802ab07`)
- `tests/test_verify_cycles.py` (new, commit `1f7c460`)
- `tests/test_verify_spec_confirmed.py` (new in `1f7c460`; 2 regression tests added in `802ab07`)
- `scripts/init_work_area.py` (edit — `resolve_spine` + its docstring/help only, commit `1f7c460`)
- `tests/test_init_work_area.py` (edit — additive only, commit `1f7c460`)

**Specific exclusions touched:** no — `checklist_engine.py`, `install_constellation.py`, `test_install_constellation.py`, `skills/`, and `DESIGN_SPEC.md` were not touched in either commit.

## Behavior changed
Yes. Two new CLI verifiers exist and are runnable standalone (not yet wired into any spine template — that's a later gate's job per Map Anchors). `resolve_spine()` gained a new token it resolves in addition to the unchanged `<commander-skill-dir>` handling; the public function signature is unchanged. Rework: `verify_spec_confirmed.py`'s Confirmed-by/Date/Status field parsing now correctly fails on a blank field regardless of which field comes last in the Confirmation section, instead of silently passing when a blank field is followed by another field line.

## Map Impact

- **Structural anchors touched:** `scripts/verify_cycles.py` (NEW, top-level `verify_cycles`/`CyclesVerificationError`), `scripts/verify_spec_confirmed.py` (NEW, top-level `verify_spec_confirmed`/`parse_confirmation`/`find_findings_table`/`SpecVerificationError`; rework touched only the three module-level regex constants `_STATUS_RE`/`_CONFIRMED_BY_RE`/`_DATE_RE`), `scripts/init_work_area.py::resolve_spine` (extended via new private helper `_resolve_skill_dir_token`, called twice — once per token — from `resolve_spine`).
- **Capabilities added/changed/affected:** work-area/spine instantiation now resolves a generic `<skill-dir>` token identically to `<commander-skill-dir>`; hard-gate mechanical enforcement for explore-cycle consolidation and design-spec confirmation now exists as two standalone, unit-tested CLI scripts, with the confirm-phase field checks now closing the newline-bleed gap the reviewer found.
- **Constraints/assumptions touched:** explore-cannot-close-without-consolidated-cycle (spec F3) is now mechanically checkable via `verify_cycles.py`; confirm-refuses-on-empty-Disposition-or-DRAFT-or-blank-Confirmed-by/Date (spec F1/F4) is now genuinely mechanically checkable via `verify_spec_confirmed.py` — the rework closes the gap where the "fail visibly, no silent fallback" constraint was violated for the blank-Confirmed-by/Date paths specifically; `<commander-skill-dir>` back-compat preserved (unchanged in the rework, still covered by the original + coexistence tests).
- **Decision candidates / resolved decisions:** the two scripts intentionally share **no** parsing module (handoff constraint: "one canonical path: two single-purpose scripts, no shared parsing framework"); each is fully self-contained — unchanged by the rework, which touched only regex literals inside `verify_spec_confirmed.py`.
- **Claims/evidence produced:** `verify_spec_confirmed.py .agent-work/issue-58/DESIGN_SPEC.md` PASSES (default/confirm phase) against the live CONFIRMED spec both before and after the rework — see Evidence below. New evidence this rework: a hand-built fixture reproducing the reviewer's exact repro (CONFIRMED + blank Confirmed-by + filled Date) now correctly FAILs, and the symmetric blank-Date case also correctly FAILs.
- **Trust limitations / drift found:** none newly found in this rework beyond the one the reviewer already surfaced and this fix closes.
- **Triage candidates:** neither verifier is yet referenced by any spine template's `command` postcondition — wiring `verify_cycles.py`/`verify_spec_confirmed.py` into `EXPLORER_SPINE.template.json`'s `explore`/`review`/`confirm` steps, and adding them to `SKILL_SCRIPT_BUNDLES["explorer"]` in `install_constellation.py`, is explicitly out of this gate's scope (owned by later g2–g5 gates per the handoff). Unchanged from attempt-2.

## Test mode
**Required:** test-after allowed (behavioral unit tests are a gate deliverable either way; red cases mandatory)
**Satisfied:** yes — every deliverable has green (pass) and red (fail-visibly) test cases; the rework adds two more red cases targeting the exact defect class the reviewer found. See Evidence.

## Evidence (post-rework, re-run in full)

```bash
$ python -m pytest tests/test_verify_cycles.py tests/test_verify_spec_confirmed.py tests/test_init_work_area.py -q
...............................                                          [100%]
31 passed in 0.29s
```
(31, up from 29 pre-rework — the 2 new regression tests.)

```bash
$ python -m pytest tests/ -q
........................................................................ [ 18%]
.................................................................................................................................... [ 51%]
........................................................................ [ 69%]
.................................................................. [ 85%]
.........................................s...............                [100%]
398 passed, 1 skipped, 18 subtests passed in 6.34s
```
(398, up from 396 pre-rework.)

```bash
$ python scripts/verify_spec_confirmed.py .agent-work/issue-58/DESIGN_SPEC.md
spec confirmation ok (confirm): .agent-work/issue-58/DESIGN_SPEC.md
```
(exit 0 — still PASSES after the fix)

```bash
$ git check-ignore scripts/init_work_area.py tests/test_init_work_area.py
```
(exit 1 — neither path is gitignored, as required; unchanged from attempt-2)

**Result:** pass — all required and targeted evidence commands succeeded post-rework.

## TDD evidence, if required
Test mode was test-after (permitted by the handoff). Both green and red cases were written and verified for each script; the rework specifically red-then-green'd the defect:

- Failing test observed (pre-fix, reproducing the reviewer's exact repro):
  ```
  parse_confirmation() on a CONFIRMED spec with blank "Confirmed by:" followed
  by a filled "Date:" line returned confirmed_by='- Date: 2026-07-08'
  (should be ''); verify_spec_confirmed(text, "confirm") did not raise.
  ```
- Passing test observed (post-fix): same fixture now yields `confirmed_by=''`
  and `verify_spec_confirmed` raises `"Confirmed by is missing or empty"`.
  Symmetric case (blank Date, filled Confirmed-by) also verified fixed.
  Both are now permanent tests: `test_confirmed_blank_confirmed_by_fails_confirm_phase`,
  `test_confirmed_blank_date_fails_confirm_phase` in `tests/test_verify_spec_confirmed.py`.
- Full targeted (31) and full-suite (398) runs above, all green.
- Refactor while green: yes — the fix is a minimal regex-literal change ([ \t]* in place of \s* immediately before each of the three field capture groups, plus the same tightening on the leading bullet whitespace for Confirmed-by/Date for defense in depth), verified against both the regression fixtures and the full suite before being taken as final evidence.

Prior (attempt-2) red-case examples, still valid and unaffected by this rework:
```bash
$ python scripts/verify_cycles.py explore-empty --root /tmp/redcase
no cycle-*.json files found in ...: explore cannot close having run zero cycles
```
(exit 1)

## Docs/contracts touched
- none — no docs files were in allowed scope for this gate.

## Assumptions
- `verify_spec_confirmed.py`'s work-id fallback form resolves to `<root>/.agent-work/<work-id>/DESIGN_SPEC.md` (unchanged from attempt-2; the handoff said "accept a work-id form if convenient" without specifying the resolution rule, so I matched every other `verify_*.py` script's `.agent-work/<work-id>/` convention).
- The findings-table detector accepts *any* Markdown pipe table whose header row contains `ID`, `Disposition`, and `Reason` (exact names), tolerating any wording for the Lens/Sev columns — unchanged from attempt-2, matches the handoff's explicit tolerance instruction.
- Rework-specific: I tightened the leading `-\s*` to `-[ \t]*` on the Confirmed-by/Date regexes too (not just the post-colon whitespace the reviewer's root-cause analysis named), on the reasoning that any `\s*` immediately preceding a bullet-line literal is the same latent newline-bleed risk class even though it didn't manifest in the reviewer's specific repro; verified this doesn't change behavior on any existing passing fixture (full suite stayed green).

## Stop conditions hit
- none — no exclusion needed touching, scope was not exceeded, the live DESIGN_SPEC.md passed without weakening any fail path (if anything, the fail path is now stricter and more correct), and no out-of-authority decision arose.

## Out-of-scope observations
- Neither verifier is yet wired into any spine template `command` postcondition or into `install_constellation.py`'s `SKILL_SCRIPT_BUNDLES` — expected, since the handoff scoped this gate to the scripts + tests only (wiring belongs to later gates per the Map Anchors' evidence expectations). Unchanged from attempt-2.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** The original implementer handoff's test-case list for `verify_spec_confirmed.py` named "DRAFT fail on confirm phase" and "empty-Disposition fail both phases" as required red cases, but did not separately name "CONFIRMED status with only one of Confirmed-by/Date blank" as a distinct required case — my attempt-2 `DRAFT_BLOCK` fixture happened to leave both fields blank *together*, which masked this exact class of bug because the earlier `Status != CONFIRMED` check fired first and short-circuited before the field regexes were ever exercised on a genuinely-CONFIRMED-but-partially-blank input. A handoff line explicitly calling out "test each Confirmation field's blank case independently, with the other fields filled" would have caught this in attempt-2 rather than requiring a review round-trip.
- **Context rediscovered:** none — confirmed after review: the reviewer's REVIEW_RESULT.md gave the exact regex, the exact root cause, and a working repro, so no independent debugging or archaeology was needed to locate or understand the defect — only to fix and generalize the fix across the sibling field regexes and add the regression tests.
- **Instructions improvised around:** the rework order asked to "audit EVERY field regex in both verifier scripts for the same \s*-before-capture newline-bleed pattern" — `verify_cycles.py` has no regex-based field parsing (it parses cycle files as JSON), so that audit found nothing to fix there; I read this as confirming absence rather than a gap, and note it here rather than silently skipping the instruction.
- **What would have made this easier:** Per-field blank-case test coverage as a named requirement in the original handoff (see Handoff gaps above) would have surfaced this in attempt-2's own review-independent testing, avoiding the extra round-trip.

## Return status
complete
