"""CLI-level regression coverage for verify_spec_confirmed.py's confirm-gate refusal.

tests/test_verify_spec_confirmed.py already exercises verify_spec_confirmed() as a direct
function call for these same three cases. This module is the adversarial-fixture half named
by issue #303 (epic-298 element E): it invokes the script as an actual subprocess and asserts
on the real process exit code and stderr, so the refusal is proven at the interface a human or
another tool would actually observe -- "the gate refuses" stays proven at the CLI boundary, not
just at the internal function boundary.

Fixture text is embedded inline (not a fixture file on disk) so this test has no dependency on
any file under the gitignored .agent-work/ tree.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_spec_confirmed.py"

FULL_TABLE = """
| ID | Lens(es) | Sev | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | MINOR | placeholder finding | ACCEPT | placeholder reason |
"""

CASE1_PARTIAL_CONFIRMATION = f"""# Throwaway CLI fixture -- case 1: partially-filled Confirmation block

## Confirmation

- **Status: CONFIRMED**
- Confirmed by:
- Date: 2026-07-31

## Findings
{FULL_TABLE}
"""

CASE2_EMPTY_DISPOSITION = """# Throwaway CLI fixture -- case 2: empty Disposition cell

## Confirmation

- **Status: CONFIRMED**
- Confirmed by: fredcai6 (human)
- Date: 2026-07-31

## Findings

| ID | Lens(es) | Sev | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | MINOR | placeholder finding | ACCEPT | placeholder reason |
| F2 | testability | MAJOR | another placeholder finding |  | left undecided |
"""

CASE3_DELETED_MARKER_DRAFT = f"""# Throwaway CLI fixture -- case 3: deleted marker, Status still DRAFT

## Confirmation

- **Status: DRAFT**
- Confirmed by:
- Date:

## Findings
{FULL_TABLE}
"""


def _run_cli(tmp_path: Path, text: str) -> subprocess.CompletedProcess:
    fixture = tmp_path / "fixture.md"
    fixture.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(fixture), "--phase", "confirm"],
        capture_output=True,
        text=True,
    )


class VerifySpecConfirmedCliRefusalTests(unittest.TestCase):
    """Each case: the real subprocess must exit non-zero and name the reason."""

    def setUp(self):
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_case1_partial_confirmation_block_refuses(self):
        result = _run_cli(self.tmp_path, CASE1_PARTIAL_CONFIRMATION)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Confirmed by", result.stderr)

    def test_case2_empty_disposition_cell_refuses(self):
        result = _run_cli(self.tmp_path, CASE2_EMPTY_DISPOSITION)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Disposition", result.stderr)

    def test_case3_deleted_marker_draft_status_refuses(self):
        result = _run_cli(self.tmp_path, CASE3_DELETED_MARKER_DRAFT)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Status is not CONFIRMED", result.stderr)


if __name__ == "__main__":
    unittest.main()
