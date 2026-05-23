import importlib.util
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_constellation.py"
SKILL_NAMES = [
    "constellation-charter",
    "constellation-workbench",
    "constellation-cartographer",
    "constellation-conductor",
    "constellation-crew",
    "constellation-triage",
]


def load_installer():
    spec = importlib.util.spec_from_file_location("install_constellation", INSTALLER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class InstallConstellationTests(unittest.TestCase):
    def test_project_scope_installs_all_skills_under_project_codex_skills(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target-project"
            project.mkdir()

            exit_code = installer.main(
                ["--scope", "project", "--project", str(project)],
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

    def test_user_scope_uses_codex_home_and_accepts_short_or_full_skill_names(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / "codex-home"

            exit_code = installer.main(
                [
                    "--scope",
                    "user",
                    "--skills",
                    "charter",
                    "constellation-crew",
                ],
                env={"CODEX_HOME": str(codex_home)},
                out=lambda _: None,
            )

            self.assertEqual(0, exit_code)
            target_root = codex_home / "skills"
            self.assertEqual(
                ["constellation-charter", "constellation-crew"],
                sorted(path.name for path in target_root.iterdir()),
            )

    def test_dry_run_prints_plan_without_creating_target(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            output = []

            exit_code = installer.main(
                [
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
                    ["--scope", "user", "--dest", str(target_root), "--skills", "charter"],
                    env={},
                    out=lambda _: None,
                ),
            )

            sentinel = target_root / "constellation-charter" / "STALE.txt"
            sentinel.write_text("old install", encoding="utf-8")

            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--scope", "user", "--dest", str(target_root), "--skills", "charter"],
                        env={},
                        out=lambda _: None,
                    )

            self.assertNotEqual(0, raised.exception.code)
            self.assertTrue(sentinel.exists())

            self.assertEqual(
                0,
                installer.main(
                    [
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


if __name__ == "__main__":
    unittest.main()
