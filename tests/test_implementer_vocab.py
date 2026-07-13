"""Light vocabulary assertion for the constellation-implementer sharpening
(DESIGN_SPEC Section D2 — vertical-slice vocabulary).

D2 is a *vocabulary* delta with NO machinery behind it (SF3/TF8): the implementer
should frame its plan chunks as vertical slices — a bite-sized, end-to-end sliver
of observable behavior — rather than horizontal layers. There is nothing to
execute, so quality is the independent reviewer's judgment; this test only pins
the vocabulary into the skill doctrine so a future edit can't silently drop it.
It is deliberately light (a doc assertion), matching the design's "no machinery".
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "implementer" / "SKILL.md"


class VerticalSliceVocabTests(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")
        self.lower = self.text.lower()

    def test_skill_present(self):
        self.assertTrue(SKILL.is_file(), f"missing {SKILL}")

    def test_vertical_slice_vocabulary_present(self):
        # THE named case: the implementer's plan chunks read as vertical slices.
        self.assertIn(
            "vertical slice", self.lower,
            "implementer SKILL.md does not carry the vertical-slice vocabulary (D2)",
        )

    def test_slices_are_end_to_end_not_layers(self):
        # The vocabulary must actually frame a slice as end-to-end behavior, and
        # contrast it against a horizontal layer — that contrast is the point.
        self.assertIn("end to end", self.lower)
        self.assertRegex(self.lower, r"horizontal layer|not a horizontal|not a layer|layer")

    def test_chunks_are_bite_sized(self):
        # A slice is a bite-sized chunk (the launch-order phrasing for D2).
        self.assertRegex(self.lower, r"bite-?sized|thin(nest)? sliver|thin sliver")

    def test_no_new_machinery_claimed(self):
        # D2 adds no step/machinery; the doctrine says so explicitly so a reader
        # (and a future editor) knows this is vocabulary, not a new gate.
        self.assertRegex(
            self.lower,
            r"no new step|no new machinery|adds no new|no machinery",
            "the vertical-slice note should state it adds no new machinery (D2 is vocabulary-only)",
        )


if __name__ == "__main__":
    unittest.main()
