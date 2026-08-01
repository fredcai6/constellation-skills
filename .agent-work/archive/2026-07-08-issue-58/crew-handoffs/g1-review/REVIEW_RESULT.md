# Review Result

Status values follow `skills/workbench/references/status-model.md`.

**This is a re-review (attempt-2) of the rework commit `802ab07`, which fixes the BLOCK from attempt-1 (original review of `1f7c460`).** The attempt-1 findings below are preserved for the record; the verdict and evidence sections reflect the re-review.

## Assigned Gate
g1 — Enforcement scripts + spine resolution (issue-58)

## Result
`APPROVE`

## Handoff compliance
The change delivers the two verifier scripts, the generic `<skill-dir>` token, and all four test files exactly as scoped. `resolve_spine`'s duplicated commander-token logic was correctly factored into a shared private helper (`_resolve_skill_dir_token`) reused for both tokens, and `<commander-skill-dir>` behavior is byte-identical (confirmed via the pre-existing test still passing plus a new coexistence test). The rework commit `802ab07` closes the one previously-unmet close criterion ("missing Confirmed-by/Date" fail path) — see Evidence verdict.

## Scope drift
None. `git show 1f7c460 --stat` (original) shows exactly the 6 allowed files: `scripts/verify_cycles.py` (new), `scripts/verify_spec_confirmed.py` (new), `tests/test_verify_cycles.py` (new), `tests/test_verify_spec_confirmed.py` (new), `scripts/init_work_area.py` (edit, confined to `resolve_spine`/`_resolve_skill_dir_token`/docstring/help), `tests/test_init_work_area.py` (additive edit). The rework `git show 802ab07 --stat` touches only `scripts/verify_spec_confirmed.py` (11 lines) and `tests/test_verify_spec_confirmed.py` (39 lines, additive tests) — squarely within the same allowed scope, no exclusion touched. `git status --porcelain` is clean; both commits are on `constellation/issue-58`.

## Evidence verdict
**Re-review, re-reproduced independently against `802ab07`:**
- `python -m pytest tests/test_verify_cycles.py tests/test_verify_spec_confirmed.py tests/test_init_work_area.py -q` → **31 passed** (was 29 at attempt-1; +2 regression tests for the fixed defect).
- `python -m pytest tests/ -q` → **398 passed, 1 skipped, 18 subtests passed** (was 396; +2).
- `python scripts/verify_spec_confirmed.py .agent-work/issue-58/DESIGN_SPEC.md` → PASS, exit 0.
- **Re-ran my original attempt-1 scratch repro** (CONFIRMED status + blank `Confirmed by:` + filled `Date:`, built independently, not the shipped test fixture) against the fixed script: now correctly **FAILS** with `Confirmed by is missing or empty`, exit 1.
- **Built and ran the symmetric case** (CONFIRMED status + filled `Confirmed by:` + blank `Date:`): correctly **FAILS** with `Date is missing or empty`, exit 1.
- Verified at the `parse_confirmation()` level directly: blank-Confirmed-by now yields `confirmed_by=''` (was `'- Date: 2026-07-08'` pre-fix); blank-Date yields `date=''`; both-blank yields both `''`.
- **Swept both verifier scripts** for any remaining `\s*`-immediately-before-a-capture-group `MULTILINE` pattern (the exact defect class): none remain. The one residual `\s*` in `_STATUS_RE` is leading bullet indentation before `**Status:`, not adjacent to a capture group; the trailing `\s*$` after Status's already-closed capture doesn't affect the captured value. Neither risks the newline-bleed class.
- Fix rationale matches root cause exactly: `\s*` → `[ \t]*` (horizontal-only) between each field's colon and its capture group in all three field regexes (`_STATUS_RE`, `_CONFIRMED_BY_RE`, `_DATE_RE`), so a blank field's whitespace can no longer consume the line break and bleed into the next field's line.

All required evidence now genuinely covers every fail path named in the implementer handoff's close criteria, independently reproduced.

## Code/doc quality
- CLI/exit-code/print style matches `scripts/verify_agent_feedback.py` (argparse, a raised `*VerificationError` caught in `main()`, `print(..., file=sys.stderr)` + `return 1` on fail, `print(...)` + `return 0` on pass, `SystemExit(main())` guard). Unaffected by the rework.
- Both new scripts import only `argparse`, `json`/`re`, `sys`, `pathlib`, `__future__` — stdlib only. Unaffected by the rework.
- No shared parsing module/framework between the two scripts — each is fully self-contained, per the constraint. Unaffected by the rework.
- The rework adds a clear inline comment at the regex definitions explaining *why* `[ \t]*` and not `\s*` is required — good defensive documentation against regression.
- The two new regression tests (`test_confirmed_blank_confirmed_by_fails_confirm_phase`, `test_confirmed_blank_date_fails_confirm_phase`) assert both the intermediate `parse_confirmation()` value and the final raised exception/message, which is stronger than asserting the exception alone — they pin the specific defect, not just a symptom.

## Map impact verdict
- **Evidence supports claimed change:** Yes, now fully — `verify_spec_confirmed.py`'s "confirm-refuses-on-empty-Confirmed-by/Date" sub-claim (spec F1) is now actually true and independently re-verified.
- **Constraints not violated:** Yes — "Fail visibly, no silent fallback" is now honored for the Confirmed-by/Date paths; the fix targets the constraint violation directly.
- **Notes match the diff:** Yes.
- **Decision candidates surfaced:** N/A for this rework (no new decisions required).
- **Durable context routed:** Yes — the rework's commit message correctly cites the reviewer finding it addresses.

## Reconciliation check
No architecture-baseline concerns. The rework is a minimal, targeted fix confined to the exact regexes implicated, with regression coverage for both the reported case and its symmetric counterpart.

## Blockers
None.

### Attempt-1 finding (resolved by 802ab07, preserved for record)
`verify_spec_confirmed.py` silently passed a CONFIRMED spec with a blank `Confirmed by:` field when `Date:` was filled, instead of failing the "missing Confirmed-by/Date" fail path. Root cause: `_CONFIRMED_BY_RE = re.compile(r"^-\s*Confirmed by:\s*(.*)$", re.MULTILINE)` — the `\s*` between `:` and the capture group matched the newline when the field was left blank, bleeding across the line boundary and capturing the *next* line's text as the "Confirmed by" value. Fixed in `802ab07` by constraining that whitespace to `[ \t]*` in all three field regexes (Status, Confirmed-by, Date); regression tests added for both the reported case and the symmetric blank-Date case. Independently re-verified above — resolved.

## Out-of-scope observations
- Neither verifier is yet wired into any spine template or `install_constellation.py`'s `SKILL_SCRIPT_BUNDLES` — correctly flagged by the implementer as belonging to later gates (g2–g5). No action needed from this gate.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** none — confirmed after review: the re-review order was precise (named commit, named the exact repro to re-run, named the symmetric case, named the sweep, named the two commands to re-run). No ambiguity this pass. (Attempt-1's note about the Survey State Location path inconsistency in REVIEWER_HANDOFF.md still stands and wasn't re-litigated here since it's a template issue, not this rework's.)
- **Context rediscovered:** none — confirmed after review: the rework commit message itself cited the exact finding and root cause, and the diff was small enough to verify by direct inspection plus the same scratch harness from attempt-1.
- **Instructions improvised around:** The checklist engine's `reopen` subcommand refused with "REFUSED: reopen applies to gated checklists" when I tried to reopen the two previously-failed `survey`-type items (`r3-evidence`, `r4a-fail-visible`) for the re-review. Survey-type checklists apparently allow re-recording a `done` item directly (the `record` subcommand accepted a new pass/finding on both without needing a reopen), so I used that instead. Worth confirming in the engine reference whether `record`-over-`done` is the intended re-review pattern for surveys, since `reopen` visibly doesn't apply there.
- **What would have made this easier:** A one-line note in the checklist-engine reference on how a survey (as opposed to a gated checklist) is meant to be re-recorded after a rework, so the `reopen`-refusal isn't a surprise mid-task.

## Return status
complete
