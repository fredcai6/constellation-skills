import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SAMPLE_BODY = (
    "**Run shape:** `commander (delegated)` · spine init->archive\n\n"
    "**Instruction adherence:** `fully followed`\n"
    "- Drove the whole spine through the engine.\n\n"
    "**Friction / unclear:**\n"
    "- The resolver did not know the admiral role's own skill-dir/session-id tokens.\n\n"
    "**Crew-reported friction:**\n"
    "- none -- confirmed after review: no crew dispatched this gate.\n\n"
    "**What worked:**\n"
    "- The generalized token discovery caught the admiral case without a new hardcode.\n\n"
    "**Improvement signals:**\n"
    "- none -- confirmed after review: no further gaps found in the resolver.\n"
)


def _load(module_name, rel_path):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_stage_feedback():
    return _load("stage_feedback", "scripts/stage_feedback.py")


# PRUNED (#447 g4): load_verify_agent_feedback() loaded scripts/verify_agent_feedback.py,
# which this retirement deleted. Its only callers were the four tests of
# VerifyAgentFeedbackAcceptsStagedOutputTests, pruned with it at the foot of this file.


class StageFeedbackTests(unittest.TestCase):
    def test_writes_all_four_files(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            staged = m.stage_feedback(
                root,
                "issue-154",
                feedback_body=SAMPLE_BODY,
                launch_order="launch-orders/W2-154.md",
                ownership="scripts/init_work_area.py, scripts/stage_feedback.py",
                return_shape="stage the fenced trio",
                entry_date="2026-07-19",
            )
            self.assertEqual(staged, root / ".agent-work" / "staged-feedback" / "issue-154")
            for name in ("AGENT_FEEDBACK.md", "lessons-delta.json", "CONSTELLATION_FEEDBACK.md", "FENCE.md"):
                self.assertTrue((staged / name).is_file(), name)

    def test_agent_feedback_heading_carries_work_id(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            staged = m.stage_feedback(
                root,
                "issue-154",
                feedback_body=SAMPLE_BODY,
                launch_order="lo.md",
                ownership="x",
                return_shape="y",
                entry_date="2026-07-19",
            )
            text = (staged / "AGENT_FEEDBACK.md").read_text(encoding="utf-8")
            self.assertIn("## `2026-07-19` -- `issue-154`", text)
            self.assertIn("Drove the whole spine", text)

    def test_default_lessons_delta_is_tick_only_valid_json(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            staged = m.stage_feedback(
                root, "issue-154", feedback_body=SAMPLE_BODY, launch_order="lo.md", ownership="x", return_shape="y"
            )
            data = json.loads((staged / "lessons-delta.json").read_text(encoding="utf-8"))
            self.assertIs(data["tick"], True)
            self.assertEqual(data["work_id"], "issue-154")
            self.assertEqual(data["ops"], [])

    def test_invalid_lessons_delta_json_rejected(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError):
                m.stage_feedback(
                    root,
                    "issue-154",
                    feedback_body=SAMPLE_BODY,
                    launch_order="lo.md",
                    ownership="x",
                    return_shape="y",
                    lessons_delta="{not valid json",
                )

    def test_default_constellation_feedback_confirms_empty(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            staged = m.stage_feedback(
                root, "issue-154", feedback_body=SAMPLE_BODY, launch_order="lo.md", ownership="x", return_shape="y"
            )
            text = (staged / "CONSTELLATION_FEEDBACK.md").read_text(encoding="utf-8")
            self.assertIn("no constellation-wide exports", text)
            self.assertIn("issue-154", text)

    def test_fence_cites_launch_order_ownership_and_return_shape(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            staged = m.stage_feedback(
                root,
                "issue-154",
                feedback_body=SAMPLE_BODY,
                launch_order="launch-orders/W2-154.md",
                ownership="scripts/init_work_area.py only",
                return_shape="stage the fenced trio, name its path",
            )
            text = (staged / "FENCE.md").read_text(encoding="utf-8")
            self.assertIn("launch-orders/W2-154.md", text)
            self.assertIn("scripts/init_work_area.py only", text)
            self.assertIn("stage the fenced trio, name its path", text)

    def test_no_clobber_without_force(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m.stage_feedback(
                root, "issue-154", feedback_body=SAMPLE_BODY, launch_order="lo.md", ownership="x", return_shape="y"
            )
            with self.assertRaises(SystemExit):
                m.stage_feedback(
                    root,
                    "issue-154",
                    feedback_body="different body",
                    launch_order="lo.md",
                    ownership="x",
                    return_shape="y",
                )

    def test_force_overwrites(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m.stage_feedback(
                root, "issue-154", feedback_body=SAMPLE_BODY, launch_order="lo.md", ownership="x", return_shape="y"
            )
            staged = m.stage_feedback(
                root,
                "issue-154",
                feedback_body="replacement body -- **Friction / unclear:**\n- replaced.\n",
                launch_order="lo.md",
                ownership="x",
                return_shape="y",
                force=True,
            )
            text = (staged / "AGENT_FEEDBACK.md").read_text(encoding="utf-8")
            self.assertIn("replaced.", text)

    def test_empty_fence_text_rejected(self):
        m = load_stage_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(SystemExit):
                m.stage_feedback(
                    root,
                    "issue-154",
                    feedback_body=SAMPLE_BODY,
                    launch_order="lo.md",
                    ownership="x",
                    return_shape="y",
                    fence_text="   ",
                )


# CLASS PRUNED (#447 g4): VerifyAgentFeedbackAcceptsStagedOutputTests and all four of its
# tests -- test_phase_feedback_passes_against_staged_output,
# test_phase_archive_passes_when_work_area_already_swept,
# test_missing_member_of_trio_still_fails, test_boilerplate_only_feedback_body_still_fails.
# Every one asserted that scripts/verify_agent_feedback.py accepts stage_feedback.py's
# staged trio; this retirement deleted that verifier, so the whole class lost its subject
# and became empty. stage_feedback.py itself is UNTOUCHED and still fully covered by the
# classes above -- nothing in it broke, only the gate it used to be graded against is gone.

if __name__ == "__main__":
    unittest.main()
