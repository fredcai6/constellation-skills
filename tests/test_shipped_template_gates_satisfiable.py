"""Prove the shipped EXECUTE_PLAN.template.json's g1-implement gate is actually
satisfiable by a real drive of the real engine (epic-559/b-instructions-to-checks,
rework r2).

Before this test, nothing in this repo asserted that a shipped template's gates
could be closed by evidence attached exactly as its own imperative instructs --
that gap is why g1-implement.c1 shipped requiring a payload shape
(`status=complete`) no document told a Commander to produce. This drives the CLI
the same way `references/checklist-engine.md` and the g1-implement imperative
themselves document it: `attach g1-implement --type implementer-result --field
status=<value>`, then `advance`. Both directions: a `complete` value must
advance the gate, and a `blocked` value must refuse it -- a check that cannot
fail is as broken as one that cannot pass.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"
TEMPLATE = ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json"


def run(plan_path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--file", str(plan_path), *args],
        cwd=ROOT, capture_output=True, text=True,
    )


def instantiate(tmp_path, work_id):
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    data["work_id"] = work_id
    plan_path = tmp_path / "EXECUTE_PLAN.json"
    plan_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return plan_path


def status_of(plan_path, task_id):
    return json.loads(plan_path.read_text(encoding="utf-8"))["tasks"][task_id]["status"]


def drive_to_g1_implement_in_progress(plan_path):
    """Ordered ritual any Commander must run before g1-implement's own
    postcondition matters: clear e0-context, attest g1-implement's
    precondition, then start it."""
    r = run(plan_path, "start", "e0-context")
    assert r.returncode == 0, r.stderr
    r = run(plan_path, "attest", "e0-context", "--cond", "c1", "--which", "postconditions",
            "--note", "context loaded (scratch drive)")
    assert r.returncode == 0, r.stderr
    r = run(plan_path, "advance", "e0-context", "--why", "scratch drive: context step is a no-op here")
    assert r.returncode == 0, r.stderr
    r = run(plan_path, "attest", "g1-implement", "--cond", "p1", "--which", "preconditions",
            "--note", "no prior gate in this scratch plan")
    assert r.returncode == 0, r.stderr
    r = run(plan_path, "start", "g1-implement")
    assert r.returncode == 0, r.stderr


class ShippedImplementGateSatisfiableTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)
        self.addCleanup(self._tmpdir.cleanup)

    def test_complete_evidence_advances_the_gate(self):
        plan_path = instantiate(self.tmp_path, "scratch-satisfiable-pass")
        drive_to_g1_implement_in_progress(plan_path)

        r = run(plan_path, "attach", "g1-implement", "--type", "implementer-result",
                "--field", "status=complete")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(plan_path, "advance", "g1-implement", "--why",
                "scratch drive: implementer-result attached with status=complete per the shipped imperative")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("g1-implement -> complete", r.stdout)
        self.assertEqual(status_of(plan_path, "g1-implement"), "complete")

    def test_blocked_evidence_refuses_the_gate(self):
        plan_path = instantiate(self.tmp_path, "scratch-satisfiable-fail")
        drive_to_g1_implement_in_progress(plan_path)

        r = run(plan_path, "attach", "g1-implement", "--type", "implementer-result",
                "--field", "status=blocked")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(plan_path, "advance", "g1-implement", "--why",
                "scratch drive: implementer-result attached with status=blocked -- must refuse")
        self.assertNotEqual(r.returncode, 0,
                             "advance must refuse a blocked implementer-result, not silently close the gate")
        self.assertIn("REFUSED", r.stderr)
        self.assertIn("postconditions unmet", r.stderr)
        # The refusal must not have silently closed the gate anyway.
        self.assertEqual(status_of(plan_path, "g1-implement"), "in-progress")


if __name__ == "__main__":
    unittest.main()
