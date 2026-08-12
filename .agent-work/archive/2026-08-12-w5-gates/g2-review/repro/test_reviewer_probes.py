"""g2-review independent probes.

Written by the reviewer, not the implementer. These reuse the doctrine suite's
installed-layout fixture but assert propositions the delivered tests do not,
so close criteria 2, 4 and 5 rest on measurement rather than code reading.
"""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "doctrine_under_review", ROOT / "tests" / "test_iterative_planning_doctrine.py"
)
doctrine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(doctrine)

load_json = doctrine.load_json


class ReviewerProbes(doctrine.InstalledIterativeRoleRuntimeTests):
    """Subclassed for the installed-skills fixture; only probe_* methods matter."""

    def seed_from_templates(self, decision, launch_id, boundary_id="wave-1"):
        """A boundary built from the replan templates with a chosen decision."""
        (self.work_area / "NEXT_WAVE.json").write_text(
            json.dumps(
                {"boundary_id": boundary_id, "launch_id": launch_id, "trigger": "wave_boundary"}
            ),
            encoding="utf-8",
            newline="\n",
        )
        transition = self.work_area / "transitions" / boundary_id
        transition.mkdir(parents=True)
        templates = self.skills_root / "constellation-replan" / "templates"
        shutil.copy2(templates / "REPLAN_INPUT.template.json", transition / "REPLAN_INPUT.json")
        result_path = transition / "REPLAN_RESULT.json"
        shutil.copy2(templates / "REPLAN_RESULT.template.json", result_path)
        result = load_json(result_path)
        result["decision"] = decision
        result_path.write_text(json.dumps(result), encoding="utf-8", newline="\n")
        (self.work_area / "ADMIRAL_LOG.md").write_text(
            f"- TRANSITION | boundary={boundary_id} | decision={decision} | verified\n",
            encoding="utf-8",
            newline="\n",
        )
        return transition, result_path

    # --- close criterion 2: the relaxation must be conditional, not blanket ---

    def test_probe_advance_with_null_launch_id_is_still_refused(self):
        self.seed_from_templates("advance", None)
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(1, refused.returncode, refused.stdout)
        self.assertIn("launch_id must be a nonempty string", refused.stderr)

    def test_probe_replan_with_null_launch_id_is_still_refused(self):
        self.seed_from_templates("replan", None)
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(1, refused.returncode, refused.stdout)
        self.assertIn("launch_id must be a nonempty string", refused.stderr)

    def test_probe_advance_with_unsafe_launch_id_is_still_refused(self):
        self.seed_from_templates("advance", "../escape")
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(1, refused.returncode, refused.stdout)
        self.assertIn("launch_id contains unsafe path characters", refused.stderr)

    def test_probe_advance_control_with_a_named_launch_still_passes(self):
        """The advance path is refused for the null, not broken outright."""
        self.seed_from_templates("advance", "wave-2")
        passed = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(0, passed.returncode, passed.stderr)

    # --- close criterion 4: repair stays refused, however it is dressed ---

    def test_probe_repair_with_a_valid_named_launch_is_still_refused(self):
        """The delivered mutation only covers repair with a null launch_id."""
        self.seed_from_templates("repair", "wave-2")
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(1, refused.returncode, refused.stdout)
        self.assertIn("only advance or replan may authorize NEXT_WAVE", refused.stderr)

    # --- close criterion 5: boundary_id validation is decision-independent ---

    def test_probe_unsafe_boundary_id_is_refused_under_every_decision(self):
        for decision in ("advance", "replan", "repair", "stop"):
            with self.subTest(decision=decision):
                (self.work_area / "NEXT_WAVE.json").write_text(
                    json.dumps(
                        {
                            "boundary_id": "../escape",
                            "launch_id": None if decision == "stop" else "wave-2",
                            "trigger": "wave_boundary",
                        }
                    ),
                    encoding="utf-8",
                    newline="\n",
                )
                refused = self.run_role("admiral", "admiral-prelaunch")
                self.assertEqual(1, refused.returncode, refused.stdout)
                self.assertIn("boundary_id contains unsafe path characters", refused.stderr)

    def test_probe_empty_boundary_id_is_refused_under_stop(self):
        (self.work_area / "NEXT_WAVE.json").write_text(
            json.dumps({"boundary_id": "", "launch_id": None, "trigger": "wave_boundary"}),
            encoding="utf-8",
            newline="\n",
        )
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(1, refused.returncode, refused.stdout)
        self.assertIn("boundary_id must be a nonempty string", refused.stderr)
