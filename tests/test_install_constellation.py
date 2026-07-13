import importlib.util
import contextlib
import re
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_constellation.py"
VERIFIER = ROOT / "scripts" / "verify_agent_feedback.py"
SKILL_NAMES = [
    "constellation-admiral",
    "constellation-charter",
    "constellation-commander",
    "constellation-commander-delegated",
    "constellation-workbench",
    "constellation-interrogator",
    "constellation-cartographer",
    "constellation-docent",
    "constellation-scout",
    "constellation-implementer",
    "constellation-lessons-auditor",
    "constellation-reviewer",
    "constellation-triage",
    "constellation-explorer",
    "constellation-prototyper",
    "constellation-curator",
    "constellation-to-issues",
    "constellation-diagnose",
    "constellation-write-a-skill",
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
                sorted(path.name for path in target_root.iterdir() if path.is_dir()),
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
                sorted(path.name for path in target_root.iterdir() if path.is_dir()),
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
                    "docent",
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
            self.assertTrue(
                (
                    target_root
                    / "constellation-docent"
                    / "scripts"
                    / "docent_freshness.py"
                ).exists()
            )

    def test_global_doctrine_buckets_bundled_per_audience(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"

            exit_code = installer.main(
                [
                    "--agent", "codex", "--scope", "user", "--dest", str(target_root),
                    "--skills", "commander", "implementer", "interrogator", "charter",
                ],
                env={},
                out=lambda _: None,
            )
            self.assertEqual(0, exit_code)

            def refs(skill_name):
                ref_dir = target_root / skill_name / "references"
                return {p.name for p in ref_dir.glob("global-*.md")}

            # everyone-global reaches every role; tier buckets reach only their tier
            self.assertEqual({"global-everyone.md", "global-orchestrator.md"}, refs("constellation-commander"))
            self.assertEqual({"global-everyone.md", "global-crew.md"}, refs("constellation-implementer"))
            self.assertEqual({"global-everyone.md"}, refs("constellation-interrogator"))
            # Charter carries all three: the baseline it elicits project deltas from
            self.assertEqual(
                {"global-everyone.md", "global-orchestrator.md", "global-crew.md"},
                refs("constellation-charter"),
            )

    def test_windows_md_bundled_alongside_global_everyone(self):
        # windows.md is the canonical Windows/harness hazard doctrine; it must ship
        # to every tier bucket (orchestrator, crew, all-tier) alongside global-everyone.md,
        # same mechanism, since the hazards apply to every role. It intentionally does
        # NOT match the `global-*.md` glob used by test_global_doctrine_buckets_bundled_per_audience
        # above, so it needs its own assertion.
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"

            exit_code = installer.main(
                [
                    "--agent", "codex", "--scope", "user", "--dest", str(target_root),
                    "--skills", "commander", "implementer", "charter",
                ],
                env={},
                out=lambda _: None,
            )
            self.assertEqual(0, exit_code)

            for skill_name in (
                "constellation-commander",   # orchestrator-tier
                "constellation-implementer",  # crew-tier
                "constellation-charter",      # all-tier
            ):
                with self.subTest(skill_name=skill_name):
                    windows_md = target_root / skill_name / "references" / "windows.md"
                    self.assertTrue(windows_md.is_file(), windows_md)
                    self.assertTrue(
                        (target_root / skill_name / "references" / "global-everyone.md").is_file()
                    )

    def test_shared_reference_dir_is_not_installed_as_a_skill(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root)],
                env={}, out=lambda _: None,
            )
            self.assertEqual(
                sorted(SKILL_NAMES),
                sorted(path.name for path in target_root.iterdir() if path.is_dir()),
            )
            self.assertFalse((target_root / "_shared").exists())

    def test_force_refreshes_global_doctrine_buckets(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            args = ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                    "--skills", "implementer"]
            installer.main(args, env={}, out=lambda _: None)

            bucket = target_root / "constellation-implementer" / "references" / "global-crew.md"
            bucket.write_text("STALE\n", encoding="utf-8")

            installer.main(args + ["--force"], env={}, out=lambda _: None)
            self.assertNotEqual("STALE\n", bucket.read_text(encoding="utf-8"))
            self.assertIn("Global doctrine", bucket.read_text(encoding="utf-8"))

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
            # the state-note precondition on execute is bundled and its token rewritten
            self.assertTrue((commander_root / "scripts" / "verify_state_note.py").exists())
            self.assertIn(
                (commander_root / "scripts" / "verify_state_note.py").as_posix(),
                spine["tasks"]["execute"]["preconditions"][1]["check"]["command"],
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

    def test_platform_interpreter_maps_os_name(self):
        # Narrow unit: os.name -> interpreter. (Mocking os.name only around this
        # pure helper is safe; mocking it around a full install would break pathlib
        # on a Windows host.)
        installer = load_installer()
        with mock.patch.object(installer.os, "name", "nt"):
            self.assertEqual("py", installer._platform_interpreter())
        with mock.patch.object(installer.os, "name", "posix"):
            self.assertEqual("python3", installer._platform_interpreter())

    def _install_commander_spine(self, installer, interpreter):
        # Drive the REAL rewrite path but pin the platform interpreter, so the test
        # runs identically on any host (os.name can't be safely faked around a full
        # install because pathlib refuses to build a foreign path flavor).
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            with mock.patch.object(installer, "_platform_interpreter", return_value=interpreter):
                exit_code = installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest",
                     str(target_root), "--skills", "commander"],
                    env={}, out=lambda _: None,
                )
            self.assertEqual(0, exit_code)
            commander_root = target_root / "constellation-commander"
            spine_path = commander_root / "templates" / "COMMANDER_SPINE.template.json"
            return spine_path.read_text(encoding="utf-8"), commander_root.as_posix()

    def test_installed_spine_rewrites_interpreter_prefix_on_windows(self):
        installer = load_installer()
        spine_text, commander_root = self._install_commander_spine(installer, "py")
        # the literal `python <` interpreter prefix is gone; the resolved command
        # now carries the `py` launcher (and the `<…-skill-dir>` token resolved).
        self.assertNotIn("python <", spine_text)
        self.assertNotIn("<commander-skill-dir>", spine_text)
        self.assertIn(f"py {commander_root}/scripts/init_work_area.py", spine_text)

    def test_installed_spine_rewrites_interpreter_prefix_on_posix(self):
        installer = load_installer()
        spine_text, commander_root = self._install_commander_spine(installer, "python3")
        self.assertNotIn("python <", spine_text)
        self.assertNotIn("<commander-skill-dir>", spine_text)
        self.assertIn(f"python3 {commander_root}/scripts/init_work_area.py", spine_text)

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

    def test_subset_force_does_not_wipe_unselected_skills(self):
        # --skills SUBSET with --force must replace only the selected skills;
        # it wiped the entire constellation-* set until issue-87's follow-up.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            base = ["--agent", "codex", "--scope", "user", "--dest", str(target_root)]
            self.assertEqual(0, installer.main(base, env={}, out=lambda _: None))
            installed_before = {p.name for p in target_root.iterdir()}
            self.assertIn("constellation-workbench", installed_before)
            self.assertEqual(
                0,
                installer.main(base + ["--skills", "commander", "--force"],
                               env={}, out=lambda _: None))
            self.assertEqual({p.name for p in target_root.iterdir()}, installed_before)

    def test_full_force_clears_orphaned_constellation_dirs(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            orphan = target_root / "constellation-retired-role"
            orphan.mkdir(parents=True)
            (orphan / "SKILL.md").write_text("old", encoding="utf-8")
            self.assertEqual(
                0,
                installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                     "--force"],
                    env={}, out=lambda _: None))
            self.assertFalse(orphan.exists())

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

    def test_lessons_gate_verifier_bundled_into_commander_and_admiral(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "commander", "admiral"], env={}, out=lambda _: None)
            for skill in ("constellation-commander", "constellation-admiral"):
                self.assertTrue(
                    (target_root / skill / "scripts" / "verify_lessons_applied.py").exists())

    def test_bundled_scripts_carry_their_sibling_imports(self):
        # Every bundled script that does `from X import ...` on a sibling
        # scripts/ module must have that module in the same bundle, or the
        # installed copy crashes with ModuleNotFoundError (agent_work_root
        # was missing from the commander/admiral bundles until issue-87).
        installer = load_installer()
        scripts_dir = Path(installer.__file__).resolve().parent
        siblings = {p.stem for p in scripts_dir.glob("*.py")}
        for skill, bundle in installer.SKILL_SCRIPT_BUNDLES.items():
            names = set(bundle)
            for script in bundle:
                text = (scripts_dir / script).read_text(encoding="utf-8")
                for mod in re.findall(r"^from (\w+) import", text, re.M):
                    if mod in siblings:
                        self.assertIn(
                            f"{mod}.py", names,
                            f"{skill}: {script} imports {mod} but {mod}.py is not bundled")

    def test_worktree_isolation_verifier_bundled_into_commander_and_admiral(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "commander", "admiral"], env={}, out=lambda _: None)
            for skill in ("constellation-commander", "constellation-admiral"):
                self.assertTrue(
                    (target_root / skill / "scripts" / "verify_worktree_isolation.py").exists())

    def test_explorer_script_bundle_lands_in_installed_skill(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "explorer"], env={}, out=lambda _: None)
            scripts_root = target_root / "constellation-explorer" / "scripts"
            for script in ("checklist_engine.py", "init_work_area.py", "run_crew.py",
                           "recover_crews.py", "verify_cycles.py", "verify_spec_confirmed.py"):
                with self.subTest(script=script):
                    self.assertTrue((scripts_root / script).is_file(), scripts_root / script)

    def test_deep_module_vocabulary_ships_into_installed_skill(self):
        # The vocabulary lands in the single-source global-everyone.md and rides the
        # existing reference-bundle mechanism into every installed skill (spec Testing
        # pathway 3) — assert it on the explorer's bundled copy.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "explorer"], env={}, out=lambda _: None)
            vocab = (target_root / "constellation-explorer" / "references"
                     / "global-everyone.md").read_text(encoding="utf-8")
            self.assertIn("Deep-module vocabulary", vocab)

    def test_relocated_doctrine_pins_ship_to_installed_destination(self):
        # issue-102 Move 11 content-pin: every doctrine relocated by moves
        # 1,2,4,5,6,7,8,9 + the move-10 canonical must ride the reference-bundle
        # mechanism into its CORRECT installed destination. Destinations differ
        # by bucket, so each signature is asserted on the file it actually lands
        # in (everyone -> ANY installed skill's global-everyone.md; orchestrator
        # -> an orchestrator-tier skill's global-orchestrator.md; move 9's home
        # is lessons-auditor's own SKILL.md).
        # Falsification: drop a bucket line in _shared -> the matching assert reds.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "explorer", "commander", "lessons-auditor"],
                           env={}, out=lambda _: None)

            # EVERYONE moves -> bundled references/global-everyone.md (rides to all
            # tiers; explorer stands in for "any installed skill").
            everyone = (target_root / "constellation-explorer" / "references"
                        / "global-everyone.md").read_text(encoding="utf-8")
            for sig in ("reporting misfit is compliance",              # move 1 boilerplate
                        "checklist-engine.md",                         # move 2 engine pointer
                        "never the idea class",                        # move 4 scoped-nulls
                        "Verify claimed side-effects against the world",  # move 5 world-verif
                        "A delegate is not a replacement"):            # move 8 delegate
                with self.subTest(bucket="global-everyone", sig=sig):
                    self.assertIn(sig, everyone)

            # ORCHESTRATOR moves + move-10 canonical -> bundled
            # references/global-orchestrator.md (commander is orchestrator-tier).
            orch = (target_root / "constellation-commander" / "references"
                    / "global-orchestrator.md").read_text(encoding="utf-8")
            for sig in ("Unchanged-tree shortcut",       # move 6 unchanged-tree
                        "Idle subagent adjudication",     # move 7 crew-idle
                        "Design-it-twice"):               # move 10 canonical (guard it still ships)
                with self.subTest(bucket="global-orchestrator", sig=sig):
                    self.assertIn(sig, orch)

            # SINGLE-HOME move 9 -> the home keeps the full rule in its own SKILL.md.
            auditor = (target_root / "constellation-lessons-auditor"
                       / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("forks its identity", auditor)  # move 9 sibling-ids

    def test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md(self):
        # issue-102 Move 11 no-residual: each retired inline signature must NOT
        # reappear in the SKILL.md body it was cut from. Scope is the SOURCE tree
        # skills/**/SKILL.md ONLY -- every references/ file is EXCLUDED, because
        # the bundled _shared copies and the deliberately-retained role references
        # (checklist-engine.md, prototyper measurement/ui.md, admiral
        # fleet-doctrine.md) legitimately carry these rules now.
        # Falsification: restore an inline copy into a carrier SKILL.md -> red.
        source_root = ROOT / "skills"
        skill_mds = sorted(source_root.glob("**/SKILL.md"))
        self.assertTrue(skill_mds, "no SKILL.md found under skills/")
        bodies = {p: p.read_text(encoding="utf-8") for p in skill_mds}

        # Most moves' home is a _shared bucket (a reference, excluded), so the
        # retired signature must be absent from ALL SKILL.md bodies.
        retired = (
            "reporting misfit is compliance",   # move 1 boilerplate
            "FOLLOW THIS SKILL STRICTLY",        # banner (count 0)
            "not on what the result claims",     # move 5 world-verif old phrasing
            "never on what the report asserted", # move 5 world-verif old phrasing
            "delegate is not a replacement",     # move 8 delegate-not-replacement
            "Unchanged-tree shortcut",           # move 6 unchanged-tree
            "idle_notification",                 # move 7 crew-idle
        )
        for sig in retired:
            for path, body in bodies.items():
                with self.subTest(sig=sig, skill=path.parent.name):
                    self.assertNotIn(sig, body)

        # EXCEPTION -- move 9's home IS lessons-auditor/SKILL.md (a SKILL.md, not
        # a bucket), which legitimately KEEPS the full rule. So the sibling-ids
        # residual is scoped to the admiral CARRIER only: the delegated rationale
        # must not be restored inline into admiral (present in lessons-auditor is
        # fine and is NOT asserted here).
        admiral = (source_root / "admiral" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("breaks recurrence counting", admiral)

    def test_commander_delegated_installs_with_orchestrator_bucket(self):
        # issue-107 g2: the delegated entry is a real installable skill (dir +
        # SKILL.md) and carries the orchestrator reference bucket (global-everyone,
        # global-orchestrator, design-it-twice-brief) plus windows.md — the same
        # _GLOBAL_ORCHESTRATOR audience as constellation-commander.
        # Falsification: drop the "commander-delegated" line from
        # SKILL_REFERENCE_BUNDLES -> the bucket asserts red; delete the source
        # SKILL.md -> the install/discover asserts red.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "commander-delegated"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            skill_root = target_root / "constellation-commander-delegated"
            self.assertTrue(skill_root.is_dir())
            self.assertTrue((skill_root / "SKILL.md").is_file())
            refs = skill_root / "references"
            for ref in ("global-everyone.md", "global-orchestrator.md",
                        "design-it-twice-brief.md", "windows.md"):
                with self.subTest(ref=ref):
                    self.assertTrue((refs / ref).is_file(), refs / ref)

    def test_commander_delegated_points_at_installed_commander_core(self):
        # issue-107 g2: the delegated skill borrows commander's core doctrine by a
        # PROSE POINTER (not a skill-dir token). Two-part contract, existence +
        # path-literal only (NOT behavioral resolution):
        #  (a) the delegated SKILL.md carries the literal relative path string
        #      "references/commander-core.md"; and
        #  (b) a full install of both skills yields an existing
        #      constellation-commander/references/commander-core.md file for it to
        #      point at.
        # Falsification: change the pointer string in the delegated SKILL.md ->
        # (a) reds; remove commander's commander-core.md -> (b) reds.
        delegated_src = (ROOT / "skills" / "commander-delegated"
                         / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/commander-core.md", delegated_src)

        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "commander-delegated", "commander"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            self.assertTrue(
                (target_root / "constellation-commander" / "references"
                 / "commander-core.md").is_file()
            )

    def test_curator_script_bundle_lands_in_installed_skill(self):
        # issue-104 G4: curate_corpus.py (G1) rides SKILL_SCRIPT_BUNDLES["curator"]
        # into the installed skill's scripts/, same mechanism as explorer above.
        # Falsification: delete the SKILL_SCRIPT_BUNDLES["curator"] line -> this
        # asserts red (the file never lands).
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "curator"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            self.assertTrue(
                (target_root / "constellation-curator" / "scripts"
                 / "curate_corpus.py").is_file()
            )

    def test_curator_carries_global_everyone_bucket(self):
        # issue-104 G4: curator is a solo, non-orchestrating, human-invoked role
        # (same audience as interrogator/lessons-auditor) so it carries
        # _GLOBAL_EVERYONE only: global-everyone.md + windows.md, no
        # global-orchestrator.md or global-crew.md.
        # Falsification: delete the SKILL_REFERENCE_BUNDLES["curator"] line ->
        # this reds (neither file lands, references/ has no global-*.md at all).
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "curator"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            refs = target_root / "constellation-curator" / "references"
            for ref in ("global-everyone.md", "windows.md"):
                with self.subTest(ref=ref):
                    self.assertTrue((refs / ref).is_file(), refs / ref)
            self.assertEqual({"global-everyone.md"}, {p.name for p in refs.glob("global-*.md")})

    def test_curator_installs_and_discovers_as_a_skill(self):
        # issue-104 G4: curator is a real installable/discoverable skill (dir +
        # SKILL.md), not just present in SKILL_NAMES for other tests.
        # Falsification: rename/remove skills/curator/SKILL.md (or drop curator
        # from discover_skills' source tree) -> install exit_code != 0 / the
        # SKILL.md assertion reds.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "curator"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)
            self.assertTrue(
                (target_root / "constellation-curator" / "SKILL.md").is_file()
            )


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
            # same skill set -> no new templates -> manifest byte-identical, untouched
            self.assertEqual(original, manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(any("left untouched" in m for m in messages))

    def test_reinstall_adds_new_upstream_template_to_existing_baseline(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            base = ["--agent", "claude", "--scope", "project", "--project", str(project),
                    "--baseline-only"]
            # initial baseline tracks only workbench templates
            installer.main(base + ["--skills", "workbench"], env={}, cwd=project, out=lambda _l: None)
            troot = project / ".agent-work" / "templates"
            mpath = troot / "TEMPLATES_MANIFEST.json"
            before = {(e["skill"], e["template"]): e["sha256"]
                      for e in json.loads(mpath.read_text(encoding="utf-8"))["templates"]}
            self.assertTrue(before)
            self.assertFalse(any(s == "constellation-commander" for s, _ in before))
            wb_baseline = (troot / ".baseline" / "constellation-workbench"
                           / "LESSONS.template.md").read_text(encoding="utf-8")

            # a later install brings a skill whose templates the project never tracked
            messages = []
            installer.main(base + ["--skills", "workbench", "commander"],
                           env={}, cwd=project, out=messages.append)
            after = {(e["skill"], e["template"]): e["sha256"]
                     for e in json.loads(mpath.read_text(encoding="utf-8"))["templates"]}

            # new skill's templates are now tracked, with baseline anchors present
            self.assertIn(("constellation-commander", "COMMANDER_SPINE.template.json"), after)
            self.assertTrue((troot / ".baseline" / "constellation-commander"
                             / "COMMANDER_SPINE.template.json").is_file())
            self.assertTrue(any("new template" in m for m in messages))
            # the genuinely-new template also gets an editable working copy
            self.assertTrue((troot / "COMMANDER_SPINE.template.json").is_file())
            # existing workbench anchors are untouched (same shas, same baseline bytes)
            for key, sha in before.items():
                self.assertEqual(after[key], sha)
            self.assertEqual(
                wb_baseline,
                (troot / ".baseline" / "constellation-workbench" / "LESSONS.template.md")
                .read_text(encoding="utf-8"),
            )

    def test_reinstall_does_not_backfill_removed_working_copies(self):
        # The over-seed guard: a project that drops a working copy (choosing to be
        # a lean consumer of the installed skill) must not have it silently
        # backfilled on reinstall — a frozen copy would read as false drift and
        # mask later upstream changes.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            args = ["--agent", "claude", "--scope", "project", "--project", str(project),
                    "--baseline-only", "--skills", "workbench"]
            installer.main(args, env={}, cwd=project, out=lambda _l: None)
            troot = project / ".agent-work" / "templates"
            lessons_wc = troot / "LESSONS.template.md"
            self.assertTrue(lessons_wc.is_file())  # fresh install seeded it
            lessons_wc.unlink()  # project opts out of tracking it locally

            installer.main(args, env={}, cwd=project, out=lambda _l: None)  # reinstall
            self.assertFalse(lessons_wc.exists())  # not backfilled (already tracked)

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

    def test_project_install_seeds_editable_working_copies(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "commander", "workbench"],
                env={}, cwd=project, out=lambda _line: None,
            )
            templates_root = project / ".agent-work" / "templates"
            manifest = json.loads(
                (templates_root / "TEMPLATES_MANIFEST.json").read_text(encoding="utf-8")
            )
            # every baselined template gets a flat, editable working copy (not under .baseline/)
            for entry in manifest["templates"]:
                local = templates_root / entry["template"]
                self.assertTrue(local.is_file(), local)
            spine = templates_root / "COMMANDER_SPINE.template.json"
            self.assertTrue(spine.is_file())
            # seeded in token form: identical content to its baseline anchor
            baseline = (templates_root / ".baseline" / "constellation-commander"
                        / "COMMANDER_SPINE.template.json")
            self.assertEqual(spine.read_text(encoding="utf-8"),
                             baseline.read_text(encoding="utf-8"))

    def test_install_never_clobbers_existing_working_copy(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            templates_root = project / ".agent-work" / "templates"
            templates_root.mkdir(parents=True)
            custom = templates_root / "COMMANDER_SPINE.template.json"
            custom.write_text("PROJECT-CUSTOMIZED\n", encoding="utf-8")
            installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "commander"],
                env={}, cwd=project, out=lambda _line: None,
            )
            # a project edit (or Charter seed) is never overwritten by reinstall
            self.assertEqual("PROJECT-CUSTOMIZED\n", custom.read_text(encoding="utf-8"))

    def test_seeded_working_copy_reads_up_to_date_against_baseline(self):
        installer = load_installer()
        freshness = load_module(
            "check_skill_freshness", ROOT / "scripts" / "check_skill_freshness.py"
        )

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "commander"],
                env={}, cwd=project, out=lambda _line: None,
            )
            skills_root = project / ".claude" / "skills"
            statuses = {r["template"]: r["status"]
                        for r in freshness.check(project, skills_root)}
            # a freshly seeded, unedited copy (token form) is neither customized nor drifted,
            # even for a spine template whose <skill-dir> tokens were rewritten at install
            self.assertEqual("up-to-date", statuses["COMMANDER_SPINE.template.json"])


class BaselineOnlyTests(unittest.TestCase):
    def test_baseline_only_seeds_manifest_without_installing_skills(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            exit_code = installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--baseline-only"],
                env={}, cwd=project, out=lambda _line: None,
            )
            self.assertEqual(0, exit_code)
            self.assertTrue(
                (project / ".agent-work" / "templates" / "TEMPLATES_MANIFEST.json").is_file()
            )
            self.assertFalse((project / ".claude" / "skills").exists())

    def test_baseline_only_also_seeds_working_copies(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "commander", "--baseline-only"],
                env={}, cwd=project, out=lambda _line: None,
            )
            self.assertTrue(
                (project / ".agent-work" / "templates"
                 / "COMMANDER_SPINE.template.json").is_file()
            )

    def test_baseline_only_requires_project_scope(self):
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                installer.main(
                    ["--agent", "claude", "--scope", "user", "--baseline-only"],
                    env={}, cwd=Path(tmp), out=lambda _line: None,
                )


class CorpusMarkerTests(unittest.TestCase):
    """Every real install stamps a CORPUS.json provenance marker (#122)."""

    def _read_marker(self, target_root: Path) -> dict:
        marker = target_root / "CORPUS.json"
        self.assertTrue(marker.is_file(), f"missing marker at {marker}")
        return json.loads(marker.read_text(encoding="utf-8"))

    def _assert_shape(self, marker: dict) -> None:
        self.assertEqual({"corpus_id", "source_commit", "date"}, set(marker))
        self.assertTrue(marker["corpus_id"].startswith("sha256:"))
        self.assertIsInstance(marker["source_commit"], str)
        self.assertTrue(marker["source_commit"])
        # date is an ISO calendar date the installer stamped.
        self.assertRegex(marker["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_user_scope_install_writes_marker(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root)],
                env={}, out=lambda _: None,
            )
            self._assert_shape(self._read_marker(target_root))

    def test_project_scope_install_writes_marker(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            project.mkdir()
            installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project)],
                env={}, cwd=project, out=lambda _: None,
            )
            self._assert_shape(self._read_marker(project / ".claude" / "skills"))

    def test_corpus_id_recomputes_to_the_recorded_value(self):
        # The stamped id must equal a re-hash of exactly the installed skills, so a
        # consumer (or the eval harness) can verify the copy it holds.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "charter", "implementer"],
                env={}, out=lambda _: None,
            )
            marker = self._read_marker(target_root)
            recomputed = installer.compute_corpus_id(
                target_root, names=["constellation-charter", "constellation-implementer"]
            )
            self.assertEqual(marker["corpus_id"], recomputed)

    def test_marker_excludes_foreign_sibling_skills(self):
        # A user's own skill sitting in a shared root must not perturb the corpus id.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            target_root.mkdir()
            foreign = target_root / "my-own-skill"
            foreign.mkdir()
            (foreign / "SKILL.md").write_text("mine\n", encoding="utf-8")
            installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", "charter"],
                env={}, out=lambda _: None,
            )
            marker = self._read_marker(target_root)
            scoped = installer.compute_corpus_id(
                target_root, names=["constellation-charter"]
            )
            self.assertEqual(marker["corpus_id"], scoped)
            # Mutating the foreign skill leaves the constellation corpus id unchanged.
            (foreign / "SKILL.md").write_text("mine CHANGED\n", encoding="utf-8")
            self.assertEqual(
                scoped,
                installer.compute_corpus_id(target_root, names=["constellation-charter"]),
            )

    def test_dry_run_writes_no_marker(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--dry-run"],
                env={}, out=lambda _: None,
            )
            self.assertFalse((target_root / "CORPUS.json").exists())
