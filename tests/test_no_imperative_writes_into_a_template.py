"""No shipped instruction may direct an agent to WRITE into `templates/`.

A template is the blank, not the destination. An agent that follows such an
instruction literally mutates the shared skill install for every future run in
every repo on that machine.

Filed as #363, found by the g2 reviewer on #304 which refused the instruction and
improvised around it, and by a second reviewer that improvised the same way. Two
independent runs both worked around it and neither fix reached the source.

Still live when this test was written -- `skills/reviewer/SKILL.md` said "Record
the pass to `templates/FOWLER_PASS.template.json`" while its own survey template
had already been corrected to instantiate into the run directory, and
`skills/interrogator/SKILL.md` carried the identical shape for
INTERROGATION_RECORD. The convention already existed in practice; only the
instructions were wrong.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

# "record/write/save ... to `templates/...`" -- a directive whose destination is
# a path under templates/. `from templates/...` is the correct direction and must
# not match.
WRITE_INTO_TEMPLATE = re.compile(
    r"(?:record|write|save|output|emit)[^.\n]{0,80}?\bto\s+`?templates/",
    re.IGNORECASE,
)


def _shipped_prose():
    for p in sorted(SKILLS.rglob("*.md")):
        yield p, p.read_text(encoding="utf-8")
    for p in sorted(SKILLS.rglob("*.json")):
        yield p, p.read_text(encoding="utf-8")


class NoShippedImperativeWritesIntoATemplate(unittest.TestCase):
    def test_no_instruction_names_a_templates_path_as_a_write_destination(self):
        offenders = []
        for path, text in _shipped_prose():
            for m in WRITE_INTO_TEMPLATE.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                offenders.append(f"{path.relative_to(ROOT)}:{line}: {m.group(0)[:70]}")
        self.assertEqual(
            offenders, [],
            "these shipped instructions direct a write INTO the installed "
            "template rather than an instantiation FROM it:\n  "
            + "\n  ".join(offenders),
        )

    def test_the_guard_can_fail(self):
        """Red-proof against the exact string that shipped (#363)."""
        shipped = "Record the pass to `templates/FOWLER_PASS.template.json`, then run"
        self.assertTrue(WRITE_INTO_TEMPLATE.search(shipped))

    def test_the_guard_does_not_fire_on_the_correct_direction(self):
        """The mirror: instantiating FROM a template must stay legal, or the
        rule is unsatisfiable and every skill has to stop naming its template."""
        correct = (
            "Instantiate the pass record FROM `templates/FOWLER_PASS.template.json` "
            "INTO your survey directory"
        )
        self.assertIsNone(WRITE_INTO_TEMPLATE.search(correct))


if __name__ == "__main__":
    unittest.main()
