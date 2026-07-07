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
        # retire-before-add in one delta succeeds; the retired lesson is GONE (deleted)
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
        ids = [l.lesson_id for l in book.active]
        self.assertEqual(len(book.active), 20)
        self.assertNotIn("lesson-0", ids)        # deleted, not parked
        self.assertIn("lesson-21", ids)
        self.assertFalse(hasattr(book, "dormant"))

    def test_tick_auto_deletes_unconfirmed(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        for i in range(11):
            self.run_delta({"work_id": f"run-{i}", "tick": True})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])        # deleted after dormancy window
        self.assertNotIn("## Dormant", self.file.read_text(encoding="utf-8"))

    def test_retire_deletes_and_id_is_reusable(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        self.run_delta(
            {"work_id": "issue-2",
             "ops": [{"op": "retire", "id": "handoff-diff-command", "reason": "internalized"}]}
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active, [])
        # the id is free again — re-adding (relearning) just works, no collision
        self.run_delta({"work_id": "issue-3", "ops": [add_op()]})
        book = self.m.load_playbook(self.file)
        self.assertEqual([l.lesson_id for l in book.active], ["handoff-diff-command"])

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

    def _confirm(self, n_or_lesson_id, work_id_or_lid="handoff-diff-command", grounding="it recurred again"):
        """Support both old signature (lesson_id, work_id) and new signature (n, lid)."""
        if isinstance(n_or_lesson_id, int):
            # New signature: _confirm(n, lid="handoff-diff-command")
            for _ in range(n_or_lesson_id):
                self.run_delta({"work_id": "x", "ops": [{"op": "confirm", "id": work_id_or_lid, "grounding": "g"}]})
        else:
            # Old signature: _confirm(lesson_id, work_id, grounding="...")
            self.run_delta(
                {"work_id": work_id_or_lid, "ops": [{"op": "confirm", "id": n_or_lesson_id, "grounding": grounding}]}
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

    def test_constellation_pinned_from_auto_delete(self):
        self.run_delta(
            {"work_id": "issue-1", "ops": [add_op("worktree-isolation", scope="constellation")]}
        )
        for i in range(12):
            self.run_delta({"work_id": f"run-{i}", "tick": True})
        book = self.m.load_playbook(self.file)
        # constellation debt is pinned: unpaid upstream defect is never auto-deleted
        self.assertEqual([l.lesson_id for l in book.active], ["worktree-isolation"])

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
        self.assertEqual(book.active, [])        # deleted once paid
        self.assertNotIn("fixed-upstream", self.file.read_text(encoding="utf-8"))

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

    def test_legacy_dormant_section_discarded_on_load(self):
        # An existing playbook with a populated ## Dormant section must load (active
        # preserved) and render WITHOUT the graveyard — GC'd on first write.
        self.file.write_text(
            "# Lessons Playbook\n\n"
            "<!-- playbook-state: run-tick=3 cap=20 dormancy-runs=10 -->\n\n"
            "## Active\n\n"
            "### lesson:live-one\n"
            "- scope: project\n- task-class: general-workflow\n"
            "- statement: still active\n- grounding: g\n"
            "- mentions: 1\n- confirmed: 0\n- disconfirmed: 0\n"
            "- status: active\n- added: 2026-06-01 (x)\n"
            "- last-confirmed: none\n- runs-since-confirmed: 0\n\n"
            "## Dormant\n\n"
            "### lesson:old-ghost\n"
            "- scope: project\n- task-class: general-workflow\n"
            "- statement: parked long ago\n- grounding: g\n"
            "- mentions: 1\n- confirmed: 0\n- disconfirmed: 0\n"
            "- status: active\n- added: 2026-05-01 (y)\n"
            "- last-confirmed: none\n- runs-since-confirmed: 99\n"
            "- retired: 2026-05-02 (y) — auto-dormant\n",
            encoding="utf-8",
        )
        book = self.m.load_playbook(self.file)
        self.assertEqual([l.lesson_id for l in book.active], ["live-one"])
        rendered = self.m.render_playbook(book)
        self.assertNotIn("## Dormant", rendered)
        self.assertNotIn("old-ghost", rendered)

    def test_add_accepts_target_and_round_trips(self):
        self.run_delta({"work_id": "issue-1", "ops": [
            add_op(target="docs/agents/CREW_CONTEXT.md")]})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.active[0].target, "docs/agents/CREW_CONTEXT.md")
        self.assertIn("- target: docs/agents/CREW_CONTEXT.md", self.file.read_text(encoding="utf-8"))

    def test_thresholds_default_when_absent_and_render_explicit(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        book = self.m.load_playbook(self.file)
        self.assertEqual(book.apply_recurrences, 1)
        self.assertEqual(book.apply_confirmed, 3)
        self.assertIn("apply-recurrences=1 apply-confirmed=3", self.file.read_text(encoding="utf-8"))

    def test_thresholds_round_trip_custom_values(self):
        self.run_delta({"work_id": "issue-1", "ops": [add_op()]})
        text = self.file.read_text(encoding="utf-8").replace(
            "apply-recurrences=1 apply-confirmed=3", "apply-recurrences=2 apply-confirmed=5")
        self.file.write_text(text, encoding="utf-8")
        book = self.m.load_playbook(self.file)
        self.assertEqual((book.apply_recurrences, book.apply_confirmed), (2, 5))

    def test_defer_requires_reason(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "defer", "id": "handoff-diff-command"}]},
                       expect_rc=1)

    def test_defer_sets_status_and_records_count(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})
        self.run_delta({"work_id": "i2", "ops": [
            {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"},
            {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"}]})
        self.run_delta({"work_id": "i3", "ops": [
            {"op": "defer", "id": "handoff-diff-command", "reason": "needs human"}]})
        lesson = self.m.load_playbook(self.file).active[0]
        self.assertEqual(lesson.status, "deferred")
        self.assertEqual(lesson.deferred_at, 2)

    def test_apply_requires_applied_evidence(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "handoff-diff-command"}]},
                       expect_rc=1)

    def test_apply_deletes_non_constellation_lesson(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "handoff-diff-command",
            "applied_evidence": "docs/agents/CREW_CONTEXT.md §Implementation Rules"}]})
        self.assertEqual(self.m.load_playbook(self.file).active, [])

    def test_apply_requires_a_target(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})  # no target
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "handoff-diff-command",
            "applied_evidence": "e"}]}, expect_rc=1)

    def test_apply_refuses_constellation(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation",
            target="skills/_shared/global-everyone.md")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "apply", "id": "engine-attest",
            "applied_evidence": "e"}]}, expect_rc=1)

    def test_export_requires_grounding(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "export", "id": "engine-attest"}]},
                       expect_rc=1)

    def test_export_sets_exported_and_pins(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "export", "id": "engine-attest",
            "grounding": "CONSTELLATION_FEEDBACK.md 2026-06-27 engine-attest"}]})
        lesson = self.m.load_playbook(self.file).active[0]
        self.assertEqual(lesson.status, "exported")

    def test_export_refuses_non_constellation(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})  # handoff scope
        self.run_delta({"work_id": "i2", "ops": [{"op": "export", "id": "handoff-diff-command",
            "grounding": "g"}]}, expect_rc=1)

    def test_ripe_selects_confirmed_threshold_with_target(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self._confirm(3)
        ripe = self.m.ripe_lessons(self.m.load_playbook(self.file))
        self.assertEqual([l.lesson_id for l in ripe], ["handoff-diff-command"])

    def test_ripe_excludes_targetless_non_constellation(self):
        self.run_delta({"work_id": "i1", "ops": [add_op()]})  # no target
        self._confirm(3)
        self.assertEqual(self.m.ripe_lessons(self.m.load_playbook(self.file)), [])

    def test_ripe_selects_constellation_recurrence(self):
        self.run_delta({"work_id": "i1", "ops": [add_op("engine-attest", "constellation")]})
        self.run_delta({"work_id": "i2", "ops": [{"op": "confirm", "id": "engine-attest", "grounding": "g"}]})
        ripe = self.m.ripe_lessons(self.m.load_playbook(self.file))
        self.assertEqual([l.lesson_id for l in ripe], ["engine-attest"])

    def test_ripe_suppresses_exported_and_fresh_defer(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self._confirm(3)
        self.run_delta({"work_id": "i2", "ops": [
            {"op": "defer", "id": "handoff-diff-command", "reason": "later"}]})
        self.assertEqual(self.m.ripe_lessons(self.m.load_playbook(self.file)), [])

    def test_ripe_refires_when_count_climbs_past_defer(self):
        self.run_delta({"work_id": "i1", "ops": [add_op(target="docs/agents/CREW_CONTEXT.md")]})
        self._confirm(3)
        self.run_delta({"work_id": "i2", "ops": [
            {"op": "defer", "id": "handoff-diff-command", "reason": "later"}]})
        self._confirm(1)  # confirmed now 4 > deferred_at 3
        self.assertEqual([l.lesson_id for l in self.m.ripe_lessons(self.m.load_playbook(self.file))],
                         ["handoff-diff-command"])


if __name__ == "__main__":
    unittest.main()
