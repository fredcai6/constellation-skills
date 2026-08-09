import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "verify_agent_feedback", ROOT / "scripts" / "verify_agent_feedback.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REAL_ENTRY = """# Agent Feedback Log

## 2026-06-10 — issue-9

**Run shape:** commander · 2 gates · sonnet

**Instruction adherence:** fully followed
- spine followed exactly

**Friction / unclear:**
- Map Anchors field lacked a staleness shorthand; improvised one

**Crew-reported friction:**
- implementer rediscovered the diff command the handoff should have carried

**What worked:**
- gate postconditions

**Improvement signals:**
- add staleness shorthand to MISSION_FRAME → route to Charter refresh
"""

BOILERPLATE_ENTRY = """# Agent Feedback Log

## 2026-06-10 — issue-9

**Instruction adherence:** fully followed
- everything fine

**Friction / unclear:**
- none

**Crew-reported friction:**
- None

**What worked:**
- all of it

**Improvement signals:**
- `none`
"""

REASONED_NONE_ENTRY = BOILERPLATE_ENTRY.replace(
    "- none",
    "- none — confirmed after review: reread each handoff field against the run, no gaps",
    1,
)


class VerifyAgentFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".agent-work").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_log(self, text):
        (self.root / ".agent-work" / "AGENT_FEEDBACK.md").write_text(text, encoding="utf-8")

    def verify(self, phase="feedback", work_id="issue-9"):
        self.m.verify_agent_feedback(self.root, work_id, phase)

    def test_real_entry_passes(self):
        self.write_log(REAL_ENTRY)
        self.verify()

    def test_missing_log_fails(self):
        with self.assertRaises(self.m.FeedbackVerificationError):
            self.verify()

    def test_boilerplate_all_none_fails(self):
        self.write_log(BOILERPLATE_ENTRY)
        with self.assertRaises(self.m.FeedbackVerificationError) as ctx:
            self.verify()
        self.assertIn("content-free", str(ctx.exception))

    def test_reasoned_none_passes(self):
        self.write_log(REASONED_NONE_ENTRY)
        self.verify()

    def test_lessons_in_work_area_fails(self):
        self.write_log(REAL_ENTRY)
        work = self.root / ".agent-work" / "issue-9"
        work.mkdir()
        (work / "LESSONS.md").write_text("x", encoding="utf-8")
        with self.assertRaises(self.m.FeedbackVerificationError) as ctx:
            self.verify()
        self.assertIn("lessons playbook", str(ctx.exception))

    def test_archived_lessons_fails(self):
        self.write_log(REAL_ENTRY)
        archive = self.root / ".agent-work" / "archive" / "2026-06-10-issue-9"
        archive.mkdir(parents=True)
        (archive / "LESSONS.md").write_text("x", encoding="utf-8")
        with self.assertRaises(self.m.FeedbackVerificationError):
            self.verify(phase="archive")

    def test_archive_phase_passes_when_clean(self):
        self.write_log(REAL_ENTRY)
        archive = self.root / ".agent-work" / "archive" / "2026-06-10-issue-9"
        archive.mkdir(parents=True)
        self.verify(phase="archive")

    def stage_trio(
        self,
        fence=True,
        feedback=REAL_ENTRY,
        lessons='{"tick": true}',
        constellation="# Constellation Feedback\n",
        fence_text="LAUNCH_ORDER commander-143: File Ownership / harvest-at-closeout",
        work_id="issue-9",
    ):
        staged = self.root / ".agent-work" / "staged-feedback" / work_id
        staged.mkdir(parents=True, exist_ok=True)
        if feedback is not None:
            (staged / "AGENT_FEEDBACK.md").write_text(feedback, encoding="utf-8")
        if lessons is not None:
            (staged / "lessons-delta.json").write_text(lessons, encoding="utf-8")
        if constellation is not None:
            (staged / "CONSTELLATION_FEEDBACK.md").write_text(constellation, encoding="utf-8")
        if fence and fence_text is not None:
            (staged / "FENCE.md").write_text(fence_text, encoding="utf-8")

    def test_fenced_staged_trio_passes(self):
        self.stage_trio()
        self.verify(phase="feedback")

        archive = self.root / ".agent-work" / "archive" / "2026-06-10-issue-9"
        archive.mkdir(parents=True)
        self.verify(phase="archive")

    def test_fence_citation_without_trio_fails(self):
        self.stage_trio(lessons=None, constellation=None)
        with self.assertRaises(self.m.FeedbackVerificationError) as ctx:
            self.verify()
        self.assertIn("learning cannot be silently dropped", str(ctx.exception))

    def test_unfenced_missing_log_unchanged(self):
        with self.assertRaises(self.m.FeedbackVerificationError) as ctx:
            self.verify()
        self.assertIn("missing durable feedback log", str(ctx.exception))
        self.assertIn("AGENT_FEEDBACK.md", str(ctx.exception))

    def test_unfenced_durable_still_passes_ignores_staged(self):
        self.write_log(REAL_ENTRY)
        self.stage_trio(fence=False, lessons=None, constellation=None)
        self.verify()


if __name__ == "__main__":
    unittest.main()
