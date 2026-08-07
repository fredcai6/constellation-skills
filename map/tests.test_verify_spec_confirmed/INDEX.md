# tests.test_verify_spec_confirmed
tests/test_verify_spec_confirmed.py, 176 lines, 19 holes

HOLE: no docstring

imports stdlib: importlib.util, pathlib.Path, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
FULL_TABLE = '\n| ID | Lens(es) | Sev | Finding | Disposition | Reason |\n|---|---|---|---|---|---|\...
TABLE_WITH_SEVERITY_HEADER = '\n| ID | Lens | Severity | Finding | Disposition | Reason |\n|---|---|---|---|---|---|...
TABLE_EMPTY_DISPOSITION = '\n| ID | Lens(es) | Sev | Finding | Disposition | Reason |\n|---|---|---|---|---|---|\...
CONFIRMED_BLOCK = '\n## Confirmation\n\n- **Status: CONFIRMED**\n- Confirmed by: fredcai6 (human)\n- Date...
DRAFT_BLOCK = '\n## Confirmation\n\n- **Status: DRAFT**\n- Confirmed by:\n- Date:\n'
CONFIRMED_BLANK_CONFIRMED_BY_BLOCK = '\n## Confirmation\n\n- **Status: CONFIRMED**\n- Confirmed by:\n- Date: 2026-07-08\n'
CONFIRMED_BLANK_DATE_BLOCK = '\n## Confirmation\n\n- **Status: CONFIRMED**\n- Confirmed by: fredcai6 (human)\n- Date...
```

- [load](load.md) function: HOLE: no docstring
- [spec](spec.md) function: HOLE: no docstring
- [VerifySpecConfirmedTests](VerifySpecConfirmedTests.md) class: HOLE: no docstring
  - [VerifySpecConfirmedTests.setUp](VerifySpecConfirmedTests.setUp.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_confirmed_full_table_passes_confirm_phase](VerifySpecConfirmedTests.test_confirmed_full_table_passes_confirm_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_confirmed_full_table_passes_review_phase](VerifySpecConfirmedTests.test_confirmed_full_table_passes_review_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_severity_header_variant_tolerated](VerifySpecConfirmedTests.test_severity_header_variant_tolerated.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_draft_fails_confirm_phase](VerifySpecConfirmedTests.test_draft_fails_confirm_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_confirmed_blank_confirmed_by_fails_confirm_phase](VerifySpecConfirmedTests.test_confirmed_blank_confirmed_by_fails_confirm_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_confirmed_blank_date_fails_confirm_phase](VerifySpecConfirmedTests.test_confirmed_blank_date_fails_confirm_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_draft_passes_review_phase_when_table_complete](VerifySpecConfirmedTests.test_draft_passes_review_phase_when_table_complete.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_empty_disposition_fails_confirm_phase](VerifySpecConfirmedTests.test_empty_disposition_fails_confirm_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_empty_disposition_fails_review_phase](VerifySpecConfirmedTests.test_empty_disposition_fails_review_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_unconfirmed_marker_as_header_fails](VerifySpecConfirmedTests.test_unconfirmed_marker_as_header_fails.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_unconfirmed_marker_hyphen_variant_fails](VerifySpecConfirmedTests.test_unconfirmed_marker_hyphen_variant_fails.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_unconfirmed_marker_mentioned_in_prose_does_not_fail](VerifySpecConfirmedTests.test_unconfirmed_marker_mentioned_in_prose_does_not_fail.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_no_findings_table_fails_confirm_phase](VerifySpecConfirmedTests.test_no_findings_table_fails_confirm_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_no_findings_table_fails_review_phase](VerifySpecConfirmedTests.test_no_findings_table_fails_review_phase.md) method: HOLE: no docstring
  - [VerifySpecConfirmedTests.test_live_design_spec_passes_default_phase](VerifySpecConfirmedTests.test_live_design_spec_passes_default_phase.md) method: HOLE: no docstring
