"""Deliberate-breakage tests for a worktree-isolation precondition (#329/#422).

One thing is asserted, with BOTH a broken-state and a fixed-state assertion
in the same test (a check that only ever demonstrates the pass side is not
proven to fail on a genuine omission -- the #392 shape this issue exists to
prevent): a wired `verify_worktree_isolation.py --here` precondition actually
blocks `checklist_engine.start()` when its argument does not match the real
worktree, and actually lets `start()` proceed once it does. The gate is
exercised twice: called directly, and driven through `main()` with `--file`
the way production drives it.

The enumeration half of this file is gone (#315/#568). It asserted that
`COMMANDER_SPINE.template.json` wired that command check onto its `init`
gate, via `scripts/verify_worktree_precondition_coverage.py`. Enforcement is
now engine-native -- `checklist_engine.origin_worktree_refusal` compares the
spine's creation-time `origin.worktree` against the engine's own cwd on every
guarded verb -- so *per-template coverage of a command check* is the wrong
question, and both the precondition and the script asserting its wiring were
retired. The command check itself still works, which is what survives here.

These tests carry NO evidence about the engine-native guard: every fixture
below builds an `origin`-less spine by hand, so they exercise its fallback
branch only. `tests/test_spine_origin_isolation.py` is where the stamped path
is proven.

Both deliberate-breakage constructions run in temp fixtures only
(`tempfile.TemporaryDirectory`, cleaned up in `tearDown`) -- never against
this worktree's own `.git` or the shared checkout.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISOLATION_SCRIPT = ROOT / "scripts" / "verify_worktree_isolation.py"
ENGINE_SCRIPT = ROOT / "scripts" / "checklist_engine.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location(
        "checklist_engine_worktree_precondition_test", ENGINE_SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EngineDeliberateBreakage(unittest.TestCase):
    """The wired precondition must actually block `start()` -- not just the
    standalone coverage script -- when `--here` disagrees with the real
    worktree, and must let `start()` proceed once it agrees. Runs against a
    throwaway git repo built fresh in a temp dir, never this worktree's own
    `.git` or the shared checkout."""

    def setUp(self):
        self.E = _load_engine()
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self._cwd = os.getcwd()
        self._git("init", "-q")
        self._git(
            "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "--allow-empty", "-m", "init",
        )

    def tearDown(self):
        os.chdir(self._cwd)
        self.tmp.cleanup()

    def _git(self, *args):
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True, capture_output=True, text=True,
        )

    def _gated_checklist(self, here_expected: str) -> dict:
        command = f'"{sys.executable}" "{ISOLATION_SCRIPT.as_posix()}" --here "{here_expected}"'
        init_gate = {
            "id": "init", "title": "init", "imperative": "do init",
            "preconditions": [{
                "id": "c0",
                "statement": "this Commander is operating in the worktree it was "
                             "provisioned into, not the shared checkout or another "
                             "agent's worktree -- proven, not asserted",
                "check": {"kind": "command", "command": command},
                "satisfied": False,
            }],
            "postconditions": [{"id": "c1", "statement": "work area scaffolded", "check": None, "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None, "finding": None,
            "evidence": [], "rework_count": 0,
        }
        return {
            "work_id": "t", "type": "gated", "config": {},
            "items": ["init"], "tasks": {"init": init_gate},
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }

    def test_start_refused_on_mismatch_then_succeeds_once_fixed(self):
        os.chdir(self.repo)
        wrong = (Path(self.tmp.name) / "definitely-not-the-worktree").as_posix()
        cl = self._gated_checklist(wrong)

        with self.assertRaises(self.E.EngineError) as ctx:
            self.E.start(cl, "init")
        self.assertIn("c0", str(ctx.exception))
        self.assertEqual(cl["tasks"]["init"]["status"], "pending")

        # Fix: point --here at the real worktree root and retry the SAME gate.
        correct = self.repo.resolve().as_posix()
        cl["tasks"]["init"]["preconditions"][0]["check"]["command"] = (
            f'"{sys.executable}" "{ISOLATION_SCRIPT.as_posix()}" --here "{correct}"'
        )
        result = self.E.start(cl, "init")
        self.assertEqual(result, "init -> in-progress")
        self.assertEqual(cl["tasks"]["init"]["status"], "in-progress")


class IsolationGateSurvivesThroughTheCLI(unittest.TestCase):
    """The isolation gate must still REFUSE a wrong-worktree launcher when driven
    the way production drives it: through `main()` with `--file`, so the engine
    computes `base_dir = path.parent` (#315).

    Why this exists as a SEPARATE test from
    `test_start_refused_on_mismatch_then_succeeds_once_fixed` above: that test
    calls `E.start(cl, "init")` directly, with **no `base_dir`**. Any future
    change that resolves a command check's cwd from `base_dir` leaves that test
    green (it takes the `base_dir is None` path) while silently disarming the
    real gate.

    The disarming is not hypothetical. `verify_worktree_isolation.py --here`
    runs `git rev-parse --show-toplevel` **from the ambient cwd** and compares
    it to EXPECTED -- so cwd is the check's SUBJECT, not a path base. In a real
    spine, EXPECTED is `<repo-root>`, which is by construction the very root a
    `base_dir`-derived cwd would resolve to, making the comparison `X == X` and
    the gate unfailable.

    So: if you are here because this test went red while making command checks
    cwd-independent, do not just relax the assertion. A command check that
    observes the environment needs an explicit contract -- a schema flag, or the
    launcher's cwd passed into the check's environment -- before the engine may
    relocate it. If such a contract HAS landed, this fixture is what needs
    updating: it writes the bare `--here` form, so teach it the new form and keep
    both sides asserted. What must not change is that a launcher standing in the
    wrong worktree is still refused.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.main_checkout = base / "main"
        self.worktree = base / "wt"
        subprocess.run(["git", "init", "-q", str(self.main_checkout)],
                       check=True, capture_output=True, text=True)
        self._git("-c", "user.email=t@t", "-c", "user.name=t",
                  "commit", "-q", "--allow-empty", "-m", "init")
        subprocess.run(
            ["git", "-C", str(self.main_checkout), "worktree", "add", "-q",
             str(self.worktree), "-b", "wtbranch"],
            check=True, capture_output=True, text=True,
        )
        self.spine_path = self.worktree / ".agent-work" / "w1" / "spine.json"
        self.spine_path.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        subprocess.run(["git", "-C", str(self.main_checkout), *args],
                       check=True, capture_output=True, text=True)

    def _write_spine(self, here_expected: str) -> None:
        command = (
            f'"{sys.executable}" "{ISOLATION_SCRIPT.as_posix()}" '
            f'--here "{here_expected}"'
        )
        self.spine_path.write_text(json.dumps({
            "work_id": "w1", "type": "gated", "items": ["init"],
            "tasks": {"init": {
                "id": "init", "title": "init", "imperative": "isolation",
                "preconditions": [{
                    "id": "c0",
                    "statement": "operating in the provisioned worktree",
                    "check": {"kind": "command", "command": command},
                    "satisfied": False,
                }],
                "postconditions": [],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }},
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }, indent=1), encoding="utf-8")

    def _start_from(self, cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ENGINE_SCRIPT), "--file",
             str(self.spine_path), "start", "init"],
            cwd=str(cwd), capture_output=True, text=True,
        )

    def test_gate_refuses_launcher_standing_in_the_main_checkout(self):
        # The spine lives in the worktree and demands the agent be there.
        self._write_spine(self.worktree.resolve().as_posix())

        # Launch from the MAIN CHECKOUT -- the wrong place, which is exactly
        # what this gate exists to catch.
        proc = self._start_from(self.main_checkout)
        combined = proc.stdout + proc.stderr
        self.assertIn("c0", combined,
                      msg=f"gate did not refuse; engine said: {combined!r}")
        self.assertEqual(
            json.loads(self.spine_path.read_text(encoding="utf-8"))
            ["tasks"]["init"]["status"], "pending",
            msg="the isolation gate was disarmed: a launcher standing in the "
                "main checkout advanced a gate asserting it was in the worktree",
        )

    def test_gate_passes_launcher_standing_in_the_worktree(self):
        # The pass side, so the refusal above is proven to be a real signal
        # rather than a gate that never opens.
        self._write_spine(self.worktree.resolve().as_posix())
        proc = self._start_from(self.worktree)
        combined = proc.stdout + proc.stderr
        self.assertIn("init -> in-progress", combined,
                      msg=f"gate did not open; engine said: {combined!r}")


if __name__ == "__main__":
    unittest.main()
