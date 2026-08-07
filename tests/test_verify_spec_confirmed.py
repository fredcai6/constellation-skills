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

    def test_unconfirmed_marker_still_fails_review_when_table_is_incomplete(self):
        # #428: dropping the marker refusal from `review` must not soften
        # review's real job. A marked draft whose Disposition cells are not all
        # filled is still refused -- the marker is simply not the reason.
        text = "# UNCONFIRMED — DO NOT CUT\n\n" + spec(DRAFT_BLOCK, TABLE_EMPTY_DISPOSITION)
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "review")
        self.assertIn("Disposition", str(ctx.exception))

    def test_unconfirmed_marker_still_fails_review_when_table_is_absent(self):
        text = f"# UNCONFIRMED — DO NOT CUT\n\n# Design Spec\n\n{DRAFT_BLOCK}\n\nNo table here.\n"
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "review")
        self.assertIn("no findings table", str(ctx.exception))

    def test_live_design_spec_passes_default_phase(self):
        # .agent-work is untracked local state: the issue-58 spec may still be
        # live, already archived, or absent entirely (fresh clone) — skip then.
        candidates = (
            ROOT / ".agent-work" / "issue-58" / "DESIGN_SPEC.md",
            ROOT / ".agent-work" / "archive" / "2026-07-08-issue-58" / "DESIGN_SPEC.md",
        )
        live = next((p for p in candidates if p.exists()), None)
        if live is None:
            self.skipTest("issue-58 DESIGN_SPEC.md not present in this checkout (untracked artifact)")
        text = live.read_text(encoding="utf-8")
        self.m.verify_spec_confirmed(text, "confirm")  # no raise


class ReviewPhaseIsPassableByAConformantDraft(unittest.TestCase):
    """Issue #428: `--phase review` was unpassable BY CONSTRUCTION.

    The `UNCONFIRMED — DO NOT CUT` marker may only come off at confirm, so a
    conformant draft at review time still carries it. The marker refusal ran in
    EVERY phase, which meant review refused precisely the drafts it exists to
    check. A check that cannot succeed is the mirror of one that cannot fail,
    and just as useless: an agent whose review step can only ever refuse learns
    to route around the step, not to fix the draft.

    The marker refusal is therefore a CONFIRM-phase rule ("no work is cut from
    an unconfirmed design"). Review keeps the checks that are actually its job:
    a findings table exists, and every Disposition cell is filled.

    Pinned in both directions -- review must PASS the conformant marked draft
    and must still REFUSE a genuinely bad one (see the two
    `..._still_fails_review_...` tests above), and confirm must be untouched.
    """

    MARKER = "# UNCONFIRMED — DO NOT CUT"

    def setUp(self):
        self.m = load()

    def test_marked_draft_with_complete_table_passes_review(self):
        # The conformant-draft case: exactly what an explorer hands its review
        # step. This is the assertion that was impossible before the fix.
        text = f"{self.MARKER}\n\n" + spec(DRAFT_BLOCK, FULL_TABLE)
        self.m.verify_spec_confirmed(text, "review")  # no raise

    def test_marked_draft_hyphen_variant_passes_review(self):
        text = "# UNCONFIRMED - DO NOT CUT\n\n" + spec(DRAFT_BLOCK, FULL_TABLE)
        self.m.verify_spec_confirmed(text, "review")  # no raise

    def test_marker_refusal_survives_at_confirm(self):
        # The rule is relocated, not removed: cutting work from a marked spec
        # is still refused, by name.
        text = f"{self.MARKER}\n\n" + spec(CONFIRMED_BLOCK, FULL_TABLE)
        with self.assertRaises(self.m.SpecVerificationError) as ctx:
            self.m.verify_spec_confirmed(text, "confirm")
        self.assertIn("UNCONFIRMED", str(ctx.exception))


class ConfirmPhaseRegressionOnALiveSpec(unittest.TestCase):
    """The #428 fix must not move the confirm gate at all.

    The epic-418 `REVISED_SPEC.md` is a real spec confirmed through
    `--phase confirm` (exit 0) on 2026-08-07, used here as the regression fixture.

    It is located by glob, not by a hardcoded work-area path. The path was
    hardcoded to `.agent-work/epic-418/spec-revision/` until the epic-418 relaunch
    archived that run and moved the spec to `.agent-work/epic-418-redux/`; both
    tests then skipped, and the skip guard — correctly — refused the build. A
    work-area path is not a stable address: work areas get archived, and a fixture
    that skips when its file moves is a test that disarms itself exactly when
    someone reorganizes around it.
    """

    def setUp(self):
        self.m = load()

    def _fixture(self):
        matches = sorted((ROOT / ".agent-work").glob("*/spec-revision/REVISED_SPEC.md"))
        if not matches:
            self.skipTest("no epic REVISED_SPEC.md under .agent-work/*/spec-revision/")
        return matches[0].read_text(encoding="utf-8")

    def test_live_revised_spec_still_passes_confirm(self):
        self.m.verify_spec_confirmed(self._fixture(), "confirm")  # no raise

    def test_live_revised_spec_also_passes_review(self):
        # A spec good enough to confirm is good enough to review; before the fix
        # this held only because the marker had already been removed at confirm.
        self.m.verify_spec_confirmed(self._fixture(), "review")  # no raise


if __name__ == "__main__":
    unittest.main()
