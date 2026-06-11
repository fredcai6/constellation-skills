import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "apply_lessons_delta", ROOT / "scripts" / "apply_lessons_delta.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def add_op(lesson_id="handoff-diff-command", scope="handoff", **overrides):
    op = {
        "op": "add",
        "id": lesson_id,
        "scope": scope,
        "task_class": "general-workflow",
        "statement": "Reviewer handoffs must carry the exact diff command.",
        "grounding": "AGENT_FEEDBACK.md 2026-06-10 issue-1 — reviewer rediscovered diff range",
    }
    op.update(overrides)
    return op


class ApplyLessonsDeltaTests(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name) / "LESSONS.md"

    def tearDown(self):
        self.tmp.cleanup()

    def run_delta(self, delta, expect_rc=0):
        delta_path = Path(self.tmp.name) / "delta.json"
        delta_path.write_text(json.dumps(delta), encoding="utf-8")
        rc = self.m.main([str(delta_path), "--file", str(self.file)])
        self.assertEqual(rc, expect_rc)

    def test_creates_playbook_and_adds_lesson(self):
        self.run_delta({"work_id": "issue-1", "tick": True, "ops": [add_op()]})
        text = self.file.read_text(encoding="utf-8")
        self.assertIn("### lesson:handoff-diff-command", text)
        self.assertIn("run-tick=1", text)
        self.assertIn("- mentions: 1", text)

    def test_round_trip_preserves_lessons(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta({"work_id": "issue-2", "ops": [add_op("second-lesson", "commander")]})
        book = self.m.load_playbook(self.file)
        self.assertEqual([l.lesson_id for l in book.active], ["handoff-diff-command", "second-lesson"])

    def test_confirm_requires_grounding(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {"work_id": "issue-2", "ops": [{"op": "confirm", "id": "handoff-diff-command"}]},
            expect_rc=1,
        )

    def test_confirm_updates_counters(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {
                "work_id": "issue-2",
                "ops": [
                    {"op": "confirm", "id": "handoff-diff-command", "grounding": "g2 BLOCK verdict"}
                ],
            }
        )
        book = self.m.load_playbook(self.file)
        lesson = book.active[0]
        self.assertEqual(lesson.confirmed, 1)
        self.assertEqual(lesson.mentions, 2)
        self.assertEqual(lesson.runs_since_confirmed, 0)

    def test_disconfirm_flags_charter_review(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {
                "work_id": "issue-2",
                "ops": [
                    {"op": "disconfirm", "id": "handoff-diff-command", "grounding": "run evidence"}
                ],
            }
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active[0].status, "charter-review")

    def test_cap_enforced_and_retire_before_add(self):
        ops = [add_op(f"lesson-{i}") for i in range(20)]
        self.run_delta({"work_id": "seed", "ops": ops})
        self.run_delta({"work_id": "over", "ops": [add_op("lesson-21")]}, expect_rc=1)
        # retire-before-add in one delta succeeds
        self.run_delta(
            {
                "work_id": "swap",
                "ops": [
                    add_op("lesson-21"),
                    {"op": "retire", "id": "lesson-0", "reason": "superseded"},
                ],
            }
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(len(book.active), 20)
        self.assertIn("lesson-0", [l.lesson_id for l in book.dormant])

    def test_tick_auto_demotes_unconfirmed(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        for i in range(11):
            self.run_delta({"work_id": f"run-{i}", "tick": True})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])
        self.assertIn("auto-dormant", book.dormant[0].retired)

    def test_confirm_revives_dormant(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {"work_id": "issue-2", "ops": [{"op": "retire", "id": "handoff-diff-command", "reason": "test"}]}
        )
        self.run_delta(
            {
                "work_id": "issue-3",
                "ops": [
                    {"op": "confirm", "id": "handoff-diff-command", "grounding": "it recurred"}
                ],
            }
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active[0].lesson_id, "handoff-diff-command")
        self.assertEqual(book.dormant, [])

    def test_rejects_bad_scope_and_duplicate_id(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op(scope="vibes")]}, expect_rc=1)
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta({"work_id": "issue-2", "ops": [add_op()]}, expect_rc=1)

    def test_rejects_noop_delta(self):
        self.run_delta({"work_id": "issue-1", "ops": []}, expect_rc=1)

    def test_invalid_op_applies_nothing(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        before = self.file.read_text(encoding="utf-8")
        self.run_delta(
            {
                "work_id": "issue-2",
                "ops": [add_op("good-new-lesson"), {"op": "confirm", "id": "missing-lesson", "grounding": "x"}],
            },
            expect_rc=1,
        )
        self.assertEqual(self.file.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
