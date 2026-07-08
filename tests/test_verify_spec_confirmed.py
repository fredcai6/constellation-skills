import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "verify_spec_confirmed", ROOT / "scripts" / "verify_spec_confirmed.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FULL_TABLE = """
| ID | Lens(es) | Sev | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | BLOCKING | something | EDIT | fixed it |
| F2 | testability | MAJOR | something else | REJECT | not needed |
"""

TABLE_WITH_SEVERITY_HEADER = """
| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | BLOCKING | something | EDIT | fixed it |
"""

TABLE_EMPTY_DISPOSITION = """
| ID | Lens(es) | Sev | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | BLOCKING | something | EDIT | fixed it |
| F2 | testability | MAJOR | something else |  | not needed |
"""

CONFIRMED_BLOCK = """
## Confirmation

- **Status: CONFIRMED**
- Confirmed by: fredcai6 (human)
- Date: 2026-07-07
"""

DRAFT_BLOCK = """
## Confirmation

- **Status: DRAFT**
- Confirmed by:
- Date:
"""

# Regression fixtures for the newline-bleed defect: a blank field's `\s*`
# must not consume the line break and capture the *next* field's line as
# its own value (which would mask the blank field as non-empty).
CONFIRMED_BLANK_CONFIRMED_BY_BLOCK = """
## Confirmation

- **Status: CONFIRMED**
- Confirmed by:
- Date: 2026-07-08
"""

CONFIRMED_BLANK_DATE_BLOCK = """
## Confirmation

- **Status: CONFIRMED**
- Confirmed by: fredcai6 (human)
- Date:
"""


def spec(confirmation_block: str, table: str, extra: str = "") -> str:
    return f"# Design Spec\n\n{confirmation_block}\n\n## Findings\n{table}\n{extra}\n"


class VerifySpecConfirmedTests(unittest.TestCase):
    def setUp(self):
        self.m = load()

    def test_confirmed_full_table_passes_confirm_phase(self):
        self.m.verify_spec_confirmed(spec(CONFIRMED_BLOCK, FULL_TABLE), "confirm")  # no raise

    def test_confirmed_full_table_passes_review_phase(self):
        self.m.verify_spec_confirmed(spec(CONFIRMED_BLOCK, FULL_TABLE), "review")  # no raise

    def test_severity_header_variant_tolerated(self):
        self.m.verify_spec_confirmed(spec(CONFIRMED_BLOCK, TABLE_WITH_SEVERITY_HEADER), "confirm")

    def test_draft_fails_confirm_phase(self):
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(spec(DRAFT_BLOCK, FULL_TABLE), "confirm")
        self.assertIn("CONFIRMED", str(ctx.exception))

    def test_confirmed_blank_confirmed_by_fails_confirm_phase(self):
        # Regression: blank Confirmed-by followed by a filled Date must not
        # let the Date line bleed into the Confirmed-by capture and mask it
        # as non-empty.
        text = spec(CONFIRMED_BLANK_CONFIRMED_BY_BLOCK, FULL_TABLE)
        fields = self.m.parse_confirmation(text)
        self.assertEqual(fields["confirmed_by"], "")
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("Confirmed by", str(ctx.exception))

    def test_confirmed_blank_date_fails_confirm_phase(self):
        # Regression: same newline-bleed class, blank Date field this time.
        text = spec(CONFIRMED_BLANK_DATE_BLOCK, FULL_TABLE)
        fields = self.m.parse_confirmation(text)
        self.assertEqual(fields["date"], "")
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("Date", str(ctx.exception))

    def test_draft_passes_review_phase_when_table_complete(self):
        self.m.verify_spec_confirmed(spec(DRAFT_BLOCK, FULL_TABLE), "review")  # no raise

    def test_empty_disposition_fails_confirm_phase(self):
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(spec(CONFIRMED_BLOCK, TABLE_EMPTY_DISPOSITION), "confirm")
        self.assertIn("Disposition", str(ctx.exception))

    def test_empty_disposition_fails_review_phase(self):
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(spec(CONFIRMED_BLOCK, TABLE_EMPTY_DISPOSITION), "review")
        self.assertIn("Disposition", str(ctx.exception))

    def test_unconfirmed_marker_as_header_fails(self):
        text = "# UNCONFIRMED — DO NOT CUT\n\n" + spec(CONFIRMED_BLOCK, FULL_TABLE)
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("UNCONFIRMED", str(ctx.exception))

    def test_unconfirmed_marker_hyphen_variant_fails(self):
        text = "# UNCONFIRMED - DO NOT CUT\n\n" + spec(CONFIRMED_BLOCK, FULL_TABLE)
        with self.assertRaises(self.m.SpecVerificationError):
            self.m.verify_spec_confirmed(text, "confirm")

    def test_unconfirmed_marker_mentioned_in_prose_does_not_fail(self):
        # A doctrine sentence *mentioning* the marker inside prose must not
        # trip the refusal -- only a standalone status/header line does.
        prose = (
            "A shelved (unconfirmed) shaped-design issue carries a loud "
            "`UNCONFIRMED — DO NOT CUT` header."
        )
        text = spec(CONFIRMED_BLOCK, FULL_TABLE, extra=prose)
        self.m.verify_spec_confirmed(text, "confirm")  # no raise

    def test_no_findings_table_fails_confirm_phase(self):
        text = f"# Design Spec\n\n{CONFIRMED_BLOCK}\n\nNo table here.\n"
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("no findings table", str(ctx.exception))

    def test_no_findings_table_fails_review_phase(self):
        text = f"# Design Spec\n\n{DRAFT_BLOCK}\n\nNo table here.\n"
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "review")
        self.assertIn("no findings table", str(ctx.exception))

    def test_live_design_spec_passes_default_phase(self):
        live = ROOT / ".agent-work" / "issue-58" / "DESIGN_SPEC.md"
        text = live.read_text(encoding="utf-8")
        self.m.verify_spec_confirmed(text, "confirm")  # no raise


if __name__ == "__main__":
    unittest.main()
