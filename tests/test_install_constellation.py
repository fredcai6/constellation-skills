import importlib.util
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_constellation.py"
VERIFIER = ROOT / "scripts" / "verify_agent_feedback.py"
SKILL_NAMES = [
    "constellation-admiral",
    "constellation-charter",
    "constellation-commander",
    "constellation-workbench",
    "constellation-interrogator",
    "constellation-cartographer",
    "constellation-scout",
    "constellation-implementer",
    "constellation-lessons-auditor",
    "constellation-reviewer",
    "constellation-triage",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_installer():
    return load_module("install_constellation", INSTALLER)


def load_verifier():
    return load_module("verify_agent_feedback", VERIFIER)


class InstallConstellationTests(unittest.TestCase):
    def test_codex_project_scope_installs_all_skills_under_project_codex_skills(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target-project"
            project.mkdir()

            exit_code = installer.main(
                ["--agent", "codex", "--scope", "project", "--project", str(project)],
                env={},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            target_root = project / ".codex" / "skills"
            self.assertEqual(
                sorted(SKILL_NAMES),
                sorted(path.name for path in target_root.iterdir()),
            )
            self.assertTrue((target_root / "constellation-charter" / "SKILL.md").exists())
            self.assertTrue(
                (target_root / "constellation-charter" / "scripts" / "checklist_engine.py").exists()
            )
            self.assertTrue(
                (target_root / "constellation-commander" / "scripts" / "init_work_area.py").exists()
            )
            self.assertTrue(
                (
                    target_root
                    / "constellation-commander"
                    / "scripts"
                    / "verify_agent_feedback.py"
                ).exists()
            )
            self.assertTrue(
                (target_root / "constellation-commander" / "scripts" / "run_crew.py").exists()
            )
            self.assertTrue(
                (target_root / "constellation-commander" / "scripts" / "recover_crews.py").exists()
            )
            self.assertTrue(
                (target_root / "constellation-cartographer" / "scripts" / "build_architecture_map.py").exists()
            )

    def test_codex_user_scope_uses_codex_home_and_accepts_short_or_full_skill_names(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / "codex-home"

            exit_code = installer.main(
                [
                    "--agent",
                    "codex",
                    "--scope",
                    "user",
                    "--skills",
                    "charter",
                    "constellation-implementer",
                ],
                env={"CODEX_HOME": str(codex_home)},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            target_root = codex_home / "skills"
            self.assertEqual(
                ["constellation-charter", "constellation-implementer"],
                sorted(path.name for path in target_root.iterdir()),
            )
            self.assertTrue(
                (target_root / "constellation-charter" / "scripts" / "checklist_engine.py").exists()
            )
            self.assertTrue(
                (target_root / "constellation-implementer" / "scripts" / "checklist_engine.py").exists()
            )

    def test_shared_scripts_are_bundled_with_each_skill_that_requires_them(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"

            exit_code = installer.main(
                [
                    "--agent",
                    "codex",
                    "--scope",
                    "user",
                    "--dest",
                    str(target_root),
                    "--skills",
                    "charter",
                    "interrogator",
                    "cartographer",
                ],
                env={},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            for skill_name in (
                "constellation-charter",
                "constellation-interrogator",
                "constellation-cartographer",
            ):
                with self.subTest(skill_name=skill_name):
                    self.assertTrue(
                        (target_root / skill_name / "scripts" / "checklist_engine.py").exists()
                    )

            self.assertTrue(
                (
                    target_root
                    / "constellation-cartographer"
                    / "scripts"
                    / "build_architecture_map.py"
                ).exists()
            )

    def test_installed_templates_use_absolute_bundled_script_paths(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"

            exit_code = installer.main(
                [
                    "--agent",
                    "codex",
                    "--scope",
                    "user",
                    "--dest",
                    str(target_root),
                    "--skills",
                    "commander",
                    "cartographer",
                    "workbench",
                ],
                env={},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            commander_root = target_root / "constellation-commander"
            spine_path = commander_root / "templates" / "COMMANDER_SPINE.template.json"
            spine_text = spine_path.read_text(encoding="utf-8")
            spine = json.loads(spine_text)

            self.assertNotIn("<commander-skill-dir>", spine_text)
            self.assertIn(
                (commander_root / "scripts" / "init_work_area.py").as_posix(),
                spine["tasks"]["init"]["postconditions"][0]["check"]["command"],
            )
            self.assertIn(
                (commander_root / "scripts" / "verify_agent_feedback.py").as_posix(),
                spine["tasks"]["feedback"]["postconditions"][0]["check"]["command"],
            )
            self.assertIn(
                (commander_root / "scripts" / "verify_agent_feedback.py").as_posix(),
                spine["tasks"]["archive"]["postconditions"][0]["check"]["command"],
            )

            cartographer_root = target_root / "constellation-cartographer"
            map_build_text = (
                cartographer_root / "templates" / "MAP_BUILD.template.md"
            ).read_text(encoding="utf-8")
            self.assertNotIn("<cartographer-skill-dir>", map_build_text)
            self.assertIn(
                (cartographer_root / "scripts" / "build_architecture_map.py").as_posix(),
                map_build_text,
            )

            workbench_root = target_root / "constellation-workbench"
            reference_text = (
                workbench_root / "references" / "checklist-engine.md"
            ).read_text(encoding="utf-8")
            self.assertNotIn("<skill-dir>", reference_text)
            self.assertIn(
                (workbench_root / "scripts" / "checklist_engine.py").as_posix(),
                reference_text,
            )

    def test_agent_feedback_verifier_enforces_durable_log_location(self):
        verifier = load_verifier()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent_work = root / ".agent-work"
            work_id = "issue-123"
            (agent_work / work_id).mkdir(parents=True)
            feedback = agent_work / "AGENT_FEEDBACK.md"
            feedback.write_text(
                f"## 2026-06-08 — {work_id}\n\n"
                "**Friction / unclear:**\n- spine step ambiguous about lease release\n",
                encoding="utf-8",
            )

            verifier.verify_agent_feedback(root, work_id, "feedback")

            bad_feedback = agent_work / work_id / "AGENT_FEEDBACK.md"
            bad_feedback.write_text("archived by mistake", encoding="utf-8")
            with self.assertRaises(verifier.FeedbackVerificationError):
                verifier.verify_agent_feedback(root, work_id, "feedback")

    def test_agent_feedback_verifier_enforces_archive_phase(self):
        verifier = load_verifier()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent_work = root / ".agent-work"
            work_id = "issue-123"
            (agent_work / work_id).mkdir(parents=True)
            (agent_work / "AGENT_FEEDBACK.md").write_text(
                f"## 2026-06-08 — {work_id}\n\n"
                "**Friction / unclear:**\n- spine step ambiguous about lease release\n",
                encoding="utf-8",
            )

            with self.assertRaises(verifier.FeedbackVerificationError):
                verifier.verify_agent_feedback(root, work_id, "archive")

            archive_dir = agent_work / "archive" / f"2026-06-08-{work_id}"
            archive_dir.mkdir(parents=True)
            (agent_work / work_id).rmdir()
            verifier.verify_agent_feedback(root, work_id, "archive")

    def test_dry_run_prints_plan_without_creating_target(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            output = []

            exit_code = installer.main(
                [
                    "--agent",
                    "codex",
                    "--scope",
                    "user",
                    "--dest",
                    str(target_root),
                    "--skills",
                    "triage",
                    "--dry-run",
                ],
                env={},
                out=output.append,
            )

            self.assertEqual(0, exit_code)
            self.assertFalse(target_root.exists())
            self.assertIn("DRY RUN", "\n".join(output))
            self.assertIn("constellation-triage", "\n".join(output))

    def test_existing_install_requires_force(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"

            self.assertEqual(
                0,
                installer.main(
                    [
                        "--agent",
                        "codex",
                        "--scope",
                        "user",
                        "--dest",
                        str(target_root),
                        "--skills",
                        "charter",
                    ],
                    env={},
                    out=lambda _: None,
                ),
            )

            sentinel = target_root / "constellation-charter" / "STALE.txt"
            sentinel.write_text("old install", encoding="utf-8")

            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        [
                            "--agent",
                            "codex",
                            "--scope",
                            "user",
                            "--dest",
                            str(target_root),
                            "--skills",
                            "charter",
                        ],
                        env={},
                        out=lambda _: None,
                    )

            self.assertNotEqual(0, raised.exception.code)
            self.assertTrue(sentinel.exists())

            self.assertEqual(
                0,
                installer.main(
                    [
                        "--agent",
                        "codex",
                        "--scope",
                        "user",
                        "--dest",
                        str(target_root),
                        "--skills",
                        "charter",
                        "--force",
                    ],
                    env={},
                    out=lambda _: None,
                ),
            )
            self.assertFalse(sentinel.exists())

    def test_unknown_skill_fails_fast(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        [
                            "--agent",
                            "codex",
                            "--scope",
                            "user",
                            "--dest",
                            str(Path(tmp) / "skills"),
                            "--skills",
                            "unknown",
                        ],
                        env={},
                        out=lambda _: None,
                    )

            self.assertNotEqual(0, raised.exception.code)

    def test_claude_project_scope_installs_under_project_claude_skills(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target-project"
            project.mkdir()

            exit_code = installer.main(
                [
                    "--agent",
                    "claude",
                    "--scope",
                    "project",
                    "--project",
                    str(project),
                    "--skills",
                    "interrogator",
                ],
                env={},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(
                (project / ".claude" / "skills" / "constellation-interrogator" / "SKILL.md").exists()
            )
            self.assertFalse((project / ".codex").exists())

    def test_claude_user_scope_uses_home_claude_skills(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"

            exit_code = installer.main(
                [
                    "--agent",
                    "claude",
                    "--scope",
                    "user",
                    "--skills",
                    "triage",
                ],
                env={"HOME": str(home)},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            self.assertTrue((home / ".claude" / "skills" / "constellation-triage" / "SKILL.md").exists())


class TemplateBaselineTests(unittest.TestCase):
    def test_project_install_seeds_baseline_and_manifest(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            exit_code = installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "commander", "workbench"],
                env={}, cwd=project, out=lambda _line: None,
            )
            self.assertEqual(0, exit_code)

            manifest_path = project / ".agent-work" / "templates" / "TEMPLATES_MANIFEST.json"
            baseline_root = project / ".agent-work" / "templates" / ".baseline"
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["baseline_origin"], "baseline-from-install")
            self.assertTrue(manifest["templates"])
            for entry in manifest["templates"]:
                copy = baseline_root / entry["skill"] / entry["template"]
                self.assertTrue(copy.is_file(), copy)
                self.assertEqual(len(entry["sha256"]), 64)
            names = {e["template"] for e in manifest["templates"]}
            self.assertIn("COMMANDER_SPINE.template.json", names)
            self.assertIn("LESSONS.template.md", names)

    def test_reinstall_leaves_existing_baseline_untouched(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            args = ["--agent", "claude", "--scope", "project", "--project", str(project),
                    "--skills", "workbench"]
            installer.main(args, env={}, cwd=project, out=lambda _line: None)
            manifest_path = project / ".agent-work" / "templates" / "TEMPLATES_MANIFEST.json"
            original = manifest_path.read_text(encoding="utf-8")

            messages = []
            installer.main(args + ["--force"], env={}, cwd=project, out=messages.append)
            self.assertEqual(original, manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(any("leaving it untouched" in m for m in messages))

    def test_user_scope_install_writes_no_baseline(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", "workbench"],
                env={}, out=lambda _line: None,
            )
            self.assertFalse((Path(tmp) / ".agent-work").exists())
