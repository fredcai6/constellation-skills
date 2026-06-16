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


    def test_amend_updates_fields_preserving_counters(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {"work_id": "issue-2",
             "ops": [{"op": "confirm", "id": "handoff-diff-command", "grounding": "recurred"}]}
        )
        self.run_delta(
            {"work_id": "issue-3",
             "ops": [{"op": "amend", "id": "handoff-diff-command",
                      "statement": "Reviewer handoffs carry the exact diff command AND base commit.",
                      "grounding": "issue-3 reviewer rediscovered the base commit"}]}
        )
        book = self.m.load_playbook(self.file)
        lesson = book.active[0]
        self.assertIn("base commit", lesson.statement)
        self.assertEqual(lesson.confirmed, 1)
        self.assertEqual(lesson.mentions, 2)
        self.assertTrue(any("amended" in h and "was:" in h for h in lesson.history))

    def test_amend_requires_grounding_and_a_field(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {"work_id": "issue-2",
             "ops": [{"op": "amend", "id": "handoff-diff-command", "statement": "x"}]},
            expect_rc=1,
        )
        self.run_delta(
            {"work_id": "issue-2",
             "ops": [{"op": "amend", "id": "handoff-diff-command", "grounding": "g"}]},
            expect_rc=1,
        )

    def test_rejects_bad_scope_and_duplicate_id(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op(scope="vibes")]}, expect_rc=1)
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta({"work_id": "issue-2", "ops": [add_op()]}, expect_rc=1)

    def _confirm(self, lesson_id, work_id, grounding="it recurred again"):
        self.run_delta(
            {"work_id": work_id, "ops": [{"op": "confirm", "id": lesson_id, "grounding": grounding}]}
        )

    def test_constellation_confirm_is_debt_not_trust(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("run-crew-cli-misfit", scope="constellation")]}
        )
        self._confirm("run-crew-cli-misfit", "issue-2")
        lesson = self.m.load_playbook(self.file).active[0]
        # trust counter stays 0; debt counter accrues; status flags debt
        self.assertEqual(lesson.confirmed, 0)
        self.assertEqual(lesson.recurrences, 1)
        self.assertEqual(lesson.status, "recurrence-debt")
        # still counts as a mention and resets dormancy (debt stays visible)
        self.assertEqual(lesson.mentions, 2)
        self.assertEqual(lesson.runs_since_confirmed, 0)
        self.assertTrue(any("constellation debt" in h for h in lesson.history))

    def test_constellation_recurrence_accrues_more_debt(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("spine-lease-stale", scope="constellation")]}
        )
        self._confirm("spine-lease-stale", "issue-2")
        self._confirm("spine-lease-stale", "issue-3")
        lesson = self.m.load_playbook(self.file).active[0]
        self.assertEqual(lesson.recurrences, 2)
        self.assertEqual(lesson.confirmed, 0)

    def test_non_constellation_confirm_unchanged(self):
        # the split must not leak: a project-scoped lesson confirms as trust
        self.run_delta({"work_id": "issue-1", "ops": [add_op("project-thing", scope="project")]})
        self._confirm("project-thing", "issue-2")
        lesson = self.m.load_playbook(self.file).active[0]
        self.assertEqual(lesson.confirmed, 1)
        self.assertEqual(lesson.recurrences, 0)
        self.assertEqual(lesson.status, "active")

    def test_recurrence_debt_renders_and_round_trips(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("engine-quirk", scope="constellation")]}
        )
        self._confirm("engine-quirk", "issue-2")
        text = self.file.read_text(encoding="utf-8")
        self.assertIn("- recurrences: 1", text)
        self.assertIn("- status: recurrence-debt", text)
        # round-trips: reload then rerender preserves the debt counter and status
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active[0].recurrences, 1)
        self.assertIn("- recurrences: 1", self.m.render_playbook(book))

    def test_constellation_confirm_revives_dormant_as_debt(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("crew-survey-state", scope="constellation")]}
        )
        self.run_delta(
            {"work_id": "issue-2", "ops": [{"op": "retire", "id": "crew-survey-state", "reason": "test"}]}
        )
        self._confirm("crew-survey-state", "issue-3")
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.dormant, [])
        lesson = book.active[0]
        self.assertEqual(lesson.recurrences, 1)
        self.assertEqual(lesson.status, "recurrence-debt")

    def test_constellation_debt_paid_by_retire(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("fixed-upstream", scope="constellation")]}
        )
        self._confirm("fixed-upstream", "issue-2")
        self.run_delta(
            {"work_id": "issue-3",
             "ops": [{"op": "retire", "id": "fixed-upstream", "reason": "fixed upstream in PR #99"}]}
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])
        self.assertIn("fixed-upstream", [l.lesson_id for l in book.dormant])

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
