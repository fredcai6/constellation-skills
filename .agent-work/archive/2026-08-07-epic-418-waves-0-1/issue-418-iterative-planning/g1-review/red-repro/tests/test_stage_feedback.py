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


def load_verify_agent_feedback():
    return _load("verify_agent_feedback", "scripts/verify_agent_feedback.py")


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


class VerifyAgentFeedbackAcceptsStagedOutputTests(unittest.TestCase):
    """The whole point of the script: what it writes must pass
    `verify_agent_feedback.py --phase feedback` and `--phase archive`, exactly
    as a fenced Commander will invoke it, without any hand-patching."""

    def _stage(self, root: Path, work_id: str = "issue-154"):
        sf = load_stage_feedback()
        return sf.stage_feedback(
            root,
            work_id,
            feedback_body=SAMPLE_BODY,
            launch_order="launch-orders/W2-154-init-placeholder.md",
            ownership="scripts/init_work_area.py, scripts/stage_feedback.py, tests/",
            return_shape="stage the fenced trio; dogfood stage_feedback.py",
            entry_date="2026-07-19",
        )

    def test_phase_feedback_passes_against_staged_output(self):
        va = load_verify_agent_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage(root, "issue-154")
            # No durable AGENT_FEEDBACK.md exists at all in this bare tempdir; the
            # FENCE.md marker must route verification onto the staged-trio branch
            # rather than failing for a missing durable log.
            va.verify_agent_feedback(root, "issue-154", "feedback", durable=root)

    def test_phase_archive_passes_when_work_area_already_swept(self):
        va = load_verify_agent_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._stage(root, "issue-154")
            # Archive-phase negative checks additionally require the work area to be
            # gone and an archived run package to exist -- unrelated to the staged
            # trio itself, but part of the same gate.
            archived = root / ".agent-work" / "archive" / "2026-07-19-issue-154"
            archived.mkdir(parents=True)
            (archived / "spine.json").write_text("{}", encoding="utf-8")
            va.verify_agent_feedback(root, "issue-154", "archive", durable=root)

    def test_missing_member_of_trio_still_fails(self):
        # A FENCE.md citation without the complete trio must still fail the gate --
        # learning cannot be silently dropped by staging only the fence.
        va = load_verify_agent_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            staged = self._stage(root, "issue-154")
            (staged / "lessons-delta.json").unlink()
            with self.assertRaises(va.FeedbackVerificationError) as ctx:
                va.verify_agent_feedback(root, "issue-154", "feedback", durable=root)
            self.assertIn("lessons-delta.json", str(ctx.exception))

    def test_boilerplate_only_feedback_body_still_fails(self):
        # A feedback body whose signal sections are all bare "none" must still
        # trip the content-free rejection -- stage_feedback.py does not launder
        # boilerplate past the gate.
        sf = load_stage_feedback()
        va = load_verify_agent_feedback()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            boilerplate_body = (
                "**Friction / unclear:**\n- none\n\n**Improvement signals:**\n- none\n"
            )
            sf.stage_feedback(
                root,
                "issue-154",
                feedback_body=boilerplate_body,
                launch_order="lo.md",
                ownership="x",
                return_shape="y",
                entry_date="2026-07-19",
            )
            with self.assertRaises(va.FeedbackVerificationError) as ctx:
                va.verify_agent_feedback(root, "issue-154", "feedback", durable=root)
            self.assertIn("content-free", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
