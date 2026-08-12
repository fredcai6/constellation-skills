# Working notes — issue #303 (implementer)

Worktree: `C:/Programs/constellation-skills-wt/298-303`
Branch: `epic-298/303`

## m1 — verify launch-order claims against code

Read `scripts/verify_spec_confirmed.py` in full. Confirmed the three refusal
mechanisms named in the launch order actually exist:

- `_UNCONFIRMED_MARKER_RE` — loud `UNCONFIRMED — DO NOT CUT` marker line, checked first, any phase.
- `find_findings_table` + empty-Disposition-cell scan — any phase.
- `parse_confirmation` (Status/Confirmed-by/Date) — confirm phase only.

Read `tests/test_verify_spec_confirmed.py`. All three named cases already have
**direct-function-call** unit-test coverage:

- Case 1 (partial Confirmation block): `test_confirmed_blank_confirmed_by_fails_confirm_phase`,
  `test_confirmed_blank_date_fails_confirm_phase`.
- Case 2 (empty Disposition cell): `test_empty_disposition_fails_confirm_phase`.
- Case 3 (deleted marker, DRAFT status): `test_draft_fails_confirm_phase` (DRAFT_BLOCK has no
  marker line and Status DRAFT — refuses via the Status check, which is the correct outcome:
  the marker-deletion scenario is caught regardless of which named reason fires).

**Gap identified:** none of the existing tests invoke the actual CLI (`verify_spec_confirmed.py`
as a subprocess) and observe a real process exit code / stderr message — they call
`verify_spec_confirmed()` directly as a Python function. The mission text ("Present
`verify_spec_confirmed.py` with...") reads as the CLI tool, not just its internal function, so
this is not a full honest-null — the CLI-level exercise is the genuinely new value this issue
adds. m2 closes that gap with real fixture files and real subprocess invocations.

## m2 — three fixtures, three observed CLI refusals

Fixtures under `.agent-work/issue-303/fixtures/` (throwaway, worktree-local, never a real
confirmed spec):

### Case 1 — partially-filled Confirmation block

File: `.agent-work/issue-303/fixtures/case1-partial-confirmation.md`
(Status: CONFIRMED, "Confirmed by" left blank, Date filled.)

Command:
```
py scripts/verify_spec_confirmed.py .agent-work/issue-303/fixtures/case1-partial-confirmation.md --phase confirm
```
Exit code: `1`
Stderr:
```
Confirmed by is missing or empty
```

### Case 2 — empty Disposition cell

File: `.agent-work/issue-303/fixtures/case2-empty-disposition.md`
(Confirmation block fully filled; findings table row F2 has an empty Disposition cell.)

Command:
```
py scripts/verify_spec_confirmed.py .agent-work/issue-303/fixtures/case2-empty-disposition.md --phase confirm
```
Exit code: `1`
Stderr:
```
findings table has empty Disposition cell(s) at data row(s) [2]
```

### Case 3 — deleted marker, Status still DRAFT

File: `.agent-work/issue-303/fixtures/case3-deleted-marker-draft.md`
(No `UNCONFIRMED — DO NOT CUT` marker line anywhere; Status still reads DRAFT — simulates the
marker having been deleted without the status actually being promoted.)

Command:
```
py scripts/verify_spec_confirmed.py .agent-work/issue-303/fixtures/case3-deleted-marker-draft.md --phase confirm
```
Exit code: `1`
Stderr:
```
Status is not CONFIRMED (found 'DRAFT'); Confirmed by is missing or empty; Date is missing or empty
```

**All three refuse.** No case needed the verifier changed (out of scope, not touched). No case
looked like it needed a design change — the gate genuinely fires as claimed. This is the
positive counterpart to the honest-null clause: the backstop was watched fire, three times, and
it fired correctly all three times.

Each case is additionally wired as an engine `command` postcondition using the
`! <command>` bash-negation-wrapper technique (decision:refusal-is-mechanically-checked /
`lesson:prove-command-fails-postcondition`), so "the gate refuses" is a mechanically
re-verified engine check, not a self-reported attest. See `execute.json` gate `m2-fixtures`.

## Workflow feedback (preliminary — finalized in verdict-303.md)

- The `! <command>` negation-wrapper technique for a command postcondition worked exactly as
  described: authored `! py scripts/verify_spec_confirmed.py <fixture> --phase confirm` as the
  `check.command` text, and the engine's re-run at `advance` correctly reports the postcondition
  met when the underlying command exits non-zero (negated to 0) and would refuse if the
  underlying command ever started exiting 0 (negated to non-zero). Second data point for
  `lesson:prove-command-fails-postcondition` — recommend promoting it from "one Commander
  improvised it once" to a documented pattern in the template/reference docs, since it is not
  obvious from `templates/IMPLEMENTER_PLAN.template.json` alone that this is the sanctioned shape
  for a must-fail check.
