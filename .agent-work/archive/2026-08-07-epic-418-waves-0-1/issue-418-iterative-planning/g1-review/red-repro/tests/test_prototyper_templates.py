"""Verifier<->template cross-check for the PROTOTYPE_RESULT.template.md gate.

g1-vocab (verdict enum, 4th disposition value) and g2-seam (workbench close via
the engine's generic artifact/match postcondition mechanism) shipped in
different gates. This suite proves them against each other with a REAL
fixture and the REAL vendored engine — never a hand-typed duplicate of the
enum strings, never a mocked engine — the exact failure mode
`lesson:verify-harness-field-and-drive-real-writer` names: a decision that
depends on a harness-supplied payload field must be verified against the
harness contract by driving the real writer path.

`prototype-result` is used here as a plain string tag to the engine's
existing generic `artifact`/`match` mechanism (like `user-decision` or
`review-result` elsewhere in this repo) — no new first-class `evidence_type`
is added to checklist_engine.py, and this suite never edits that file.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills" / "prototyper" / "templates" / "PROTOTYPE_RESULT.template.md"
ENGINE = ROOT / "scripts" / "checklist_engine.py"


def _extract_enum(text: str, heading: str) -> list[str]:
    """Pull the backtick-quoted, pipe-separated enum on the line directly
    under a `## <heading>` heading in the real template file. This is the
    ONLY source of enum values this suite uses — never a hand-typed literal
    standing in for the template."""
    pattern = re.compile(rf"^## {re.escape(heading)}\s*\n`([^`]+)`", re.MULTILINE)
    m = pattern.search(text)
    assert m, f"template no longer has a backtick-quoted enum under '## {heading}'"
    return [v.strip() for v in m.group(1).split("|")]


TEMPLATE_TEXT = TEMPLATE.read_text(encoding="utf-8")
VERDICT_VALUES = _extract_enum(TEMPLATE_TEXT, "Verdict")
DISPOSITION_VALUES = _extract_enum(TEMPLATE_TEXT, "Disposition")


# --------------------------------------------------------------------------- #
# PROTOTYPE_RESULT.template.md -> the extraction itself
# --------------------------------------------------------------------------- #
class PrototypeResultEnumExtraction(unittest.TestCase):
    """Proves the extraction actually reads the shipped template's current
    contract, so a drift in the template (renamed heading, reordered values,
    a dropped value) surfaces here rather than silently rotting the fixture
    below."""

    def test_verdict_enum_extracted_from_real_template(self):
        self.assertEqual(
            VERDICT_VALUES,
            ["answered-yes", "answered-no", "not-immediately-right"],
        )

    def test_disposition_enum_extracted_from_real_template(self):
        self.assertEqual(
            DISPOSITION_VALUES,
            ["deleted", "absorbed", "parked-with-owner", "captured-to-worktree"],
        )

    def test_disposition_enum_carries_the_new_4th_value(self):
        # The specific new value this gate exists to prove: captured-to-worktree.
        self.assertIn("captured-to-worktree", DISPOSITION_VALUES)


# --------------------------------------------------------------------------- #
# extracted enum values -> checklist_engine.py, driven as a subprocess
#
# A small fixture 'gated' checklist with one gate whose SOLE postcondition is
# the engine's generic `artifact`/`match` check, `evidence_type:
# "prototype-result"`, matched against the REAL verdict/disposition values
# extracted above. claim -> start -> attach -> advance, exactly the sequence
# a prototyper close would run.
# --------------------------------------------------------------------------- #
def _fixture_checklist(verdict: str, disposition: str) -> dict:
    return {
        "work_id": "proto-fixture",
        "type": "gated",
        "items": ["g1"],
        "tasks": {
            "g1": {
                "id": "g1", "title": "g1", "imperative": "close prototype result",
                "preconditions": [], "postconditions": [
                    {
                        "id": "c1",
                        "statement": "prototype-result verdict+disposition accepted",
                        "check": {
                            "kind": "artifact",
                            "evidence_type": "prototype-result",
                            "match": {"verdict": verdict, "disposition": disposition},
                        },
                        "satisfied": False,
                    }
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None, "finding": None,
                "evidence": [], "rework_count": 0,
                # Isolates the round-trip proof from the separate why-capture
                # mechanism (#179), which this suite does not exercise.
                "why_exempt": True,
            }
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


class PrototypeResultEngineRoundTrip(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.verdict = VERDICT_VALUES[0]  # "answered-yes"
        self.disposition = DISPOSITION_VALUES[-1]  # "captured-to-worktree"

    def tearDown(self):
        self.tmp.cleanup()

    def _write_checklist(self, verdict, disposition):
        path = self.root / "checklist.json"
        path.write_text(json.dumps(_fixture_checklist(verdict, disposition)), encoding="utf-8")
        return path

    def _run(self, path, *verb):
        return subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(path), *verb],
            capture_output=True, text=True, cwd=str(self.root),
        )

    def test_real_verdict_and_disposition_values_accepted_by_advance(self):
        # POSITIVE direction: the postcondition's match uses the real extracted
        # values, and attach supplies those SAME real values -> advance succeeds.
        path = self._write_checklist(self.verdict, self.disposition)
        claim = self._run(path, "claim", "--session-id", "proto-fixture",
                           "--claimed-by", "tester", "--worktree", ".")
        self.assertEqual(claim.returncode, 0, claim.stderr)
        start = self._run(path, "start", "g1", "--session-id", "proto-fixture")
        self.assertEqual(start.returncode, 0, start.stderr)
        attach = self._run(
            path, "attach", "g1", "--type", "prototype-result",
            "--field", f"verdict={self.verdict}",
            "--field", f"disposition={self.disposition}",
            "--session-id", "proto-fixture",
        )
        self.assertEqual(attach.returncode, 0, attach.stderr)
        advance = self._run(path, "advance", "g1", "--mechanical", "--session-id", "proto-fixture")
        self.assertEqual(advance.returncode, 0, advance.stderr)
        self.assertIn("g1 -> complete", advance.stdout)

    def test_off_vocabulary_verdict_is_refused_by_advance(self):
        # NEGATIVE direction: the postcondition still wants the REAL values, but
        # the attach supplies an off-vocabulary verdict ("maybe" is not in
        # VERDICT_VALUES) -> the artifact/match check must fail -> advance fails.
        # This proves the match check is actually exercised, not a no-op that
        # would pass any string.
        self.assertNotIn("maybe", VERDICT_VALUES)
        path = self._write_checklist(self.verdict, self.disposition)
        claim = self._run(path, "claim", "--session-id", "proto-fixture",
                           "--claimed-by", "tester", "--worktree", ".")
        self.assertEqual(claim.returncode, 0, claim.stderr)
        start = self._run(path, "start", "g1", "--session-id", "proto-fixture")
        self.assertEqual(start.returncode, 0, start.stderr)
        attach = self._run(
            path, "attach", "g1", "--type", "prototype-result",
            "--field", "verdict=maybe",
            "--field", f"disposition={self.disposition}",
            "--session-id", "proto-fixture",
        )
        self.assertEqual(attach.returncode, 0, attach.stderr)
        advance = self._run(path, "advance", "g1", "--mechanical", "--session-id", "proto-fixture")
        self.assertNotEqual(advance.returncode, 0)
        self.assertIn("postconditions unmet", advance.stderr)


if __name__ == "__main__":
    unittest.main()
