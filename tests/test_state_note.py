import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


FILLED = """# Crash-resume state note — issue-42

- **step:** execute · gate g2-integrate
- **slug:** issue-42 / feat-branch / ../wt-issue-42
- **next command:** py -m pytest -q && gh pr merge 42
- **pid:** 48121
- **expected artifact:** .agent-work/issue-42/g2-result.json

_Updated: 2026-06-16T13:40:00Z_
"""

# A note for a purely foreground run: pid is an explicit value, not a placeholder.
FOREGROUND = FILLED.replace("- **pid:** 48121", '- **pid:** none — foreground')

# Straight from the template — every value still a <placeholder>.
UNFILLED = """# Crash-resume state note — <work-id>

- **step:** <which spine/gate step you are on>
- **slug:** <work-id, branch, and worktree path>
- **next command:** <the exact command a fresh agent runs to resume>
- **pid:** <PID of the detached process, or "none — foreground">
- **expected artifact:** <the output file whose existence signals completion>
"""


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_state_note")

    def test_filled_note_has_no_problems(self):
        self.assertEqual(self.m.validate(FILLED), [])

    def test_foreground_pid_is_a_valid_value(self):
        self.assertEqual(self.m.validate(FOREGROUND), [])

    def test_unfilled_template_flags_every_field(self):
        problems = self.m.validate(UNFILLED)
        for field in self.m.REQUIRED_FIELDS:
            self.assertTrue(
                any(field in p for p in problems), f"{field} should be flagged unfilled"
            )

    def test_missing_field_is_flagged(self):
        text = FILLED.replace("- **pid:** 48121\n", "")
        problems = self.m.validate(text)
        self.assertEqual(problems, ["missing field: pid"])

    def test_empty_value_is_flagged(self):
        text = FILLED.replace("- **next command:** py -m pytest -q && gh pr merge 42", "- **next command:**")
        problems = self.m.validate(text)
        self.assertTrue(any("next command" in p for p in problems))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_state_note")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".agent-work" / "issue-42").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, text):
        (self.root / ".agent-work" / "issue-42" / "STATE_NOTE.md").write_text(text, encoding="utf-8")

    def test_missing_file_returns_1(self):
        self.assertEqual(self.m.main(["issue-42", "--root", str(self.root)]), 1)

    def test_filled_note_returns_0(self):
        self._write(FILLED)
        self.assertEqual(self.m.main(["issue-42", "--root", str(self.root)]), 0)

    def test_unfilled_note_returns_1(self):
        self._write(UNFILLED)
        self.assertEqual(self.m.main(["issue-42", "--root", str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
