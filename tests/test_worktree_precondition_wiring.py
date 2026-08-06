"""Deliberate-breakage tests for the worktree-isolation precondition (#329/#422).

Two things are asserted, each with BOTH a broken-state and a fixed-state
assertion in the same test (a check that only ever demonstrates the pass
side is not proven to fail on a genuine omission -- the #392 shape this
issue exists to prevent):

  1. `scripts/verify_worktree_precondition_coverage.py` (the enumeration
     script) actually refuses when a worktree-entering template is missing
     the wired precondition, and actually passes when it is present.
  2. The precondition, once wired onto `COMMANDER_SPINE.template.json`'s
     `init` gate, actually blocks `checklist_engine.start()` when the
     `--here` argument does not match the real worktree, and actually lets
     `start()` proceed once it does.

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
COVERAGE_SCRIPT = ROOT / "scripts" / "verify_worktree_precondition_coverage.py"
ISOLATION_SCRIPT = ROOT / "scripts" / "verify_worktree_isolation.py"
ENGINE_SCRIPT = ROOT / "scripts" / "checklist_engine.py"
REAL_TEMPLATE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"
TEMPLATE_REL_PATH = "skills/commander/templates/COMMANDER_SPINE.template.json"


def _load_engine():
    spec = importlib.util.spec_from_file_location(
        "checklist_engine_worktree_precondition_test", ENGINE_SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_coverage_script(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(COVERAGE_SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


class EnumerationDeliberateBreakage(unittest.TestCase):
    """The coverage script must refuse a template missing the precondition,
    and must pass the real (fixed) tree -- in the same test."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_broken_copy(self) -> Path:
        """Copy the real COMMANDER_SPINE.template.json into the tmp fixture
        at the same relative path the coverage script expects, with the c0
        precondition stripped from the `init` gate -- reproducing the #329
        pre-fix state (an omitted precondition), not a hypothetical shape."""
        data = json.loads(REAL_TEMPLATE.read_text(encoding="utf-8"))
        init_gate = data["tasks"]["init"]
        # Sanity: the fixture starts from a template that DOES carry the
        # precondition, so stripping it is a genuine mutation, not a no-op.
        assert any(
            "verify_worktree_isolation.py" in (c.get("check") or {}).get("command", "")
            for c in init_gate.get("preconditions", [])
        ), "real template unexpectedly missing the precondition before stripping"
        init_gate["preconditions"] = []

        dest = self.tmp_root / TEMPLATE_REL_PATH
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        # Assert the mutation actually applied to the file we will point the
        # script at (never trust the in-memory dict alone).
        written = json.loads(dest.read_text(encoding="utf-8"))
        assert written["tasks"]["init"]["preconditions"] == []
        return dest

    def test_refuses_broken_copy_and_passes_real_fixed_tree(self):
        self._write_broken_copy()

        broken = _run_coverage_script(self.tmp_root)
        self.assertNotEqual(
            broken.returncode, 0,
            f"coverage script did not refuse the broken copy; stdout={broken.stdout!r}",
        )
        # Names the offending template path and gate id -- not a bare "FAIL".
        self.assertIn("init", broken.stderr)
        self.assertIn("COMMANDER_SPINE.template.json", broken.stderr)

        fixed = _run_coverage_script(ROOT)
        self.assertEqual(
            fixed.returncode, 0,
            f"coverage script failed against the real fixed tree; stderr={fixed.stderr!r}",
        )
        # States the count checked, not just "OK".
        self.assertIn("1 worktree-entering template", fixed.stdout)


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


if __name__ == "__main__":
    unittest.main()
