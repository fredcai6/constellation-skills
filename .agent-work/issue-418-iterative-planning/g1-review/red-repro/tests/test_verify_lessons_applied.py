import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerifyLessonsAppliedTests(unittest.TestCase):
    def setUp(self):
        self.apply = _load("apply_lessons_delta")
        self.verify = _load("verify_lessons_applied")
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name) / "LESSONS.md"

    def tearDown(self):
        self.tmp.cleanup()

    def _apply(self, delta):
        p = Path(self.tmp.name) / "d.json"
        p.write_text(json.dumps(delta), encoding="utf-8")
        self.assertEqual(0, self.apply.main([str(p), "--file", str(self.file)]))

    def _add(self, **ov):
        op = {"op": "add", "id": "handoff-diff-command", "scope": "handoff",
              "task_class": "general-workflow", "statement": "s",
              "grounding": "AGENT_FEEDBACK.md i1",
              "bank_reason": "re-observe before fixing"}
        op.update(ov)
        return op

    def test_clear_when_no_playbook(self):
        self.assertEqual(0, self.verify.main(["--file", str(self.file)]))

    def test_clear_when_no_ripe_lessons(self):
        self._apply({"work_id": "i1", "ops": [self._add()]})
        self.assertEqual(0, self.verify.main(["--file", str(self.file)]))

    def test_blocks_on_unpaid_ripe_lesson(self):
        self._apply({"work_id": "i1", "ops": [self._add(target="docs/agents/CREW_CONTEXT.md")]})
        for _ in range(3):
            self._apply({"work_id": "x", "ops": [
                {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"}]})
        self.assertEqual(1, self.verify.main(["--file", str(self.file)]))

    def test_clear_after_apply(self):
        self._apply({"work_id": "i1", "ops": [self._add(target="docs/agents/CREW_CONTEXT.md")]})
        for _ in range(3):
            self._apply({"work_id": "x", "ops": [
                {"op": "confirm", "id": "handoff-diff-command", "grounding": "g"}]})
        self._apply({"work_id": "x2", "ops": [
            {"op": "apply", "id": "handoff-diff-command", "applied_evidence": "edited CREW_CONTEXT",
             "authority": "human",
             "drill": "docs/superpowers/drills/handoff-diff-command.md"}]})
        self.assertEqual(0, self.verify.main(["--file", str(self.file)]))
