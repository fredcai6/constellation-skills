import ast
import importlib.util
import contextlib
import os
import re
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_constellation.py"
VERIFIER = ROOT / "scripts" / "verify_agent_feedback.py"


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


# issue-116: derived from the installer's OWN enumeration (discover_skills()),
# never a second hand-maintained roster -- a skill added/renamed under skills/
# now shows up here automatically instead of silently drifting out of sync.
SKILL_NAMES = sorted(skill.install_name for skill in load_installer().discover_skills())


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
        # Drive the REAL rewrite path but pin the resolved interpreter, so the test
        # runs identically on any host (os.name can't be safely faked around a full
        # install because pathlib refuses to build a foreign path flavor, and the
        # real probe's outcome is host-dependent). `resolve_interpreter` -- not
        # `_platform_interpreter` -- is main()'s entry point since #228 added the
        # real host probe; `_platform_interpreter` is now only the total-failure
        # fallback, no longer the sole thing to patch to control the outcome.
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            resolution = installer.InterpreterResolution(
                interpreter, installer.INTERPRETER_CANDIDATES, "probe"
            )
            with mock.patch.object(installer, "resolve_interpreter", return_value=resolution):
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
        # A bundled script sourced from a scripts/ SUBDIRECTORY still installs flat,
        # so it is a sibling of the rest once installed -- count it as one here too,
        # or this guard would go blind exactly on the scripts it cannot see.
        siblings |= {Path(name).stem for name in installer.SCRIPT_SOURCE_SUBDIRS}
        for skill, bundle in installer.SKILL_SCRIPT_BUNDLES.items():
            names = set(bundle)
            for script in bundle:
                text = installer.script_source_path(
                    script, scripts_dir).read_text(encoding="utf-8")
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

    def test_every_discovered_skill_is_pinned_in_skill_index(self):
        # issue-116: SKILL_INDEX.md is a hand-maintained roster; this pins it
        # against the SAME enumeration install_constellation.py itself uses
        # (discover_skills()), never a second hardcoded list -- a silently
        # stale index (a skill added to skills/ but never documented) would
        # otherwise go unnoticed.
        # Falsification: add/rename a skill under skills/ without a matching
        # `skills/<source_name>/SKILL.md` path landing in SKILL_INDEX.md's text
        # -> this reds, naming exactly the missing skill(s).
        installer = load_installer()
        skills = installer.discover_skills()
        index_text = (ROOT / "SKILL_INDEX.md").read_text(encoding="utf-8")

        missing = sorted(
            skill.install_name
            for skill in skills
            if f"skills/{skill.source_name}/SKILL.md" not in index_text
        )
        self.assertEqual(
            [], missing,
            f"SKILL_INDEX.md is missing entries for: {missing}",
        )

    def test_shared_sync_integrity_installed_references_match_source_bytes(self):
        # issue-116: every skill that bundles skills/_shared/* files must receive
        # an installed copy that is byte-identical to the source -- a hand-edited
        # installed copy or a stale bundling step would otherwise drift silently.
        # Enumeration is the installer's own SKILL_REFERENCE_BUNDLES (via
        # discover_skills()'s required_references), never a second hardcoded list.
        # Falsification: change a bundled reference's bytes between source and
        # install (or corrupt the copy step) -> the byte comparison reds.
        installer = load_installer()
        skills = installer.discover_skills()
        consuming = [skill for skill in skills if skill.required_references]
        self.assertTrue(
            consuming, "expected at least one skill to consume skills/_shared/* files"
        )

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                [
                    "--agent", "codex", "--scope", "user", "--dest", str(target_root),
                    "--skills", *(skill.source_name for skill in consuming),
                ],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, exit_code)

            shared_root = ROOT / "skills" / "_shared"
            for skill in consuming:
                installed_refs = target_root / skill.install_name / "references"
                for ref in skill.required_references:
                    with self.subTest(skill=skill.install_name, reference=ref):
                        source_bytes = (shared_root / ref).read_bytes()
                        installed_bytes = (installed_refs / ref).read_bytes()
                        self.assertEqual(source_bytes, installed_bytes)


def _find_py_free_interpreter_dir(installer):
    """Find a real PATH entry that carries a genuine python3/python executable
    but NOT a `py` launcher -- used to genuinely shadow PATH so the real probe
    cannot resolve `py`, rather than asserting a hand-set fixture value (issue
    #228's active lesson `verify-harness-field-and-drive-real-writer`). Returns
    None if the current host has no such entry (test skips rather than fakes it).
    """
    exe_suffix = ".exe" if installer.os.name == "nt" else ""
    py_names = {"py" + exe_suffix}
    target_names = {"python3" + exe_suffix, "python" + exe_suffix}
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        directory = Path(entry)
        if not directory.is_dir():
            continue
        try:
            names = {p.name for p in directory.iterdir() if p.is_file()}
        except OSError:
            continue
        if names & py_names:
            continue
        if names & target_names:
            return directory
    return None


class InterpreterProbeTests(unittest.TestCase):
    """Issue #228: real host probe (py -> python3 -> python) + fallback chain +
    per-skill sidecar, threaded through install_skills() as an explicit
    parameter (never a module-level global/cache)."""

    def test_probe_resolves_a_real_invocable_interpreter_on_this_host(self):
        # Required evidence (1): drives the REAL probe end to end, no mocked
        # return value anywhere in this test.
        installer = load_installer()
        resolved = installer.probe_host_interpreter()
        self.assertIsNotNone(resolved)
        self.assertIn(resolved, installer.INTERPRETER_CANDIDATES)
        # Independently re-drive the same real subprocess call to prove the
        # returned name is genuinely invocable on this host right now, not
        # merely the first candidate returned by construction.
        result = subprocess.run(
            [resolved, "--version"], capture_output=True, text=True, timeout=5
        )
        self.assertEqual(0, result.returncode)

    def test_probe_falls_through_to_next_candidate_when_py_is_unresolvable(self):
        # Required evidence (2): genuinely induces "py is unresolvable" by
        # mutating the AMBIENT os.environ PATH (mock.patch.dict), not by passing
        # a restricted `env=` into subprocess.run and not by hand-setting a
        # "resolved interpreter" fixture value. On Windows, CreateProcess resolves
        # an unqualified executable name against the CALLING process's real
        # environment, not the `env=` dict handed to subprocess.run -- verified
        # empirically while building this test: a restricted `env=` argument left
        # `py` resolving via the untouched ambient PATH, while mutating
        # os.environ["PATH"] itself made `py` genuinely unresolvable. This is why
        # the shadow below patches os.environ directly.
        #
        # ...but "genuinely unresolvable" is a HOST-DEPENDENT claim, not a
        # universal one, and the empirical verification above was done on a
        # single box. Windows CreateProcess also searches the Windows and
        # System32 directories, which PATH cannot shadow -- and an all-users
        # Python launcher installs `py.exe` into C:\Windows. On such a host
        # (the GitHub Actions windows runner is one) `py` still resolves with
        # PATH restricted, and this test would assert the exact opposite of the
        # state it just set up. So VERIFY the premise inside the shadowed
        # environment before asserting on it, and skip when it does not hold --
        # the same "skip rather than fake it" rule the py_free_dir guard above
        # already follows.
        installer = load_installer()
        py_free_dir = _find_py_free_interpreter_dir(installer)
        if py_free_dir is None:
            self.skipTest(
                "no PATH entry on this host carries python3/python without also "
                "carrying a py launcher; cannot genuinely induce py-unresolvable"
            )
        with mock.patch.dict(os.environ, {"PATH": str(py_free_dir)}):
            # Probe `py` the same way probe_host_interpreter does, so the guard
            # measures the real resolution path rather than a PATH-only proxy
            # like shutil.which (which would report "not found" here even on a
            # host where CreateProcess still finds py.exe outside PATH).
            py_still_resolves = installer._probe_interpreter_candidate(
                "py", timeout=installer.DEFAULT_INTERPRETER_PROBE_TIMEOUT)
            if py_still_resolves:
                self.skipTest(
                    "py resolves outside PATH on this host, so py-unresolvable "
                    "cannot be genuinely induced"
                )
            resolved = installer.probe_host_interpreter()
        self.assertIn(resolved, ("python3", "python"))
        self.assertNotEqual("py", resolved)

    def test_probe_prefers_py_over_python3_when_both_succeed(self):
        # Required evidence (4): candidate order. Monkeypatches the exact
        # subprocess boundary the probe calls (installer.subprocess.run), per the
        # active lesson's sanctioned alternative to PATH-shadowing.
        installer = load_installer()
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd[0])
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")

        with mock.patch.object(installer.subprocess, "run", side_effect=fake_run):
            resolved = installer.probe_host_interpreter()
        self.assertEqual("py", resolved)
        self.assertEqual(["py"], calls)  # never even tries python3 -- py wins first

    def test_probe_timeout_candidate_falls_through_without_hanging(self):
        # Required evidence (7): a subprocess.TimeoutExpired candidate is treated
        # as failure and falls through, not left hanging.
        installer = load_installer()
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append((cmd[0], kwargs.get("timeout")))
            if cmd[0] == "py":
                raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")

        with mock.patch.object(installer.subprocess, "run", side_effect=fake_run):
            resolved = installer.probe_host_interpreter()
        self.assertEqual("python3", resolved)
        self.assertEqual(["py", "python3"], [c for c, _ in calls])
        # the explicit timeout really is threaded into the subprocess call, not
        # just documented in prose
        self.assertTrue(all(t == installer.DEFAULT_INTERPRETER_PROBE_TIMEOUT for _, t in calls))

    def test_resolve_interpreter_falls_back_to_os_default_on_total_failure(self):
        # Required evidence (5): a dedicated test for the NEW total-probe-failure
        # -> os.name-default fallback branch, distinct from
        # test_platform_interpreter_maps_os_name (which tests the OLD, still-intact
        # pure os.name helper directly, not this new fallback wiring).
        installer = load_installer()

        def always_fails(cmd, **kwargs):
            raise FileNotFoundError(f"no such candidate: {cmd[0]}")

        with mock.patch.object(installer.subprocess, "run", side_effect=always_fails):
            with mock.patch.object(installer.os, "name", "nt"):
                resolution = installer.resolve_interpreter()
        self.assertEqual("py", resolution.interpreter)
        self.assertEqual("os-default-fallback", resolution.resolved_via)

        with mock.patch.object(installer.subprocess, "run", side_effect=always_fails):
            with mock.patch.object(installer.os, "name", "posix"):
                resolution = installer.resolve_interpreter()
        self.assertEqual("python3", resolution.interpreter)
        self.assertEqual("os-default-fallback", resolution.resolved_via)

    def test_probe_invoked_exactly_once_total_across_multi_skill_install(self):
        # Required evidence (3): a call-count assertion (not prose) that the
        # once-per-run resolution is genuinely threaded/cached, not re-probed per
        # skill. Wraps (not replaces) resolve_interpreter -- the once-per-run probe
        # entry point install_skills() lazily calls -- so this still drives the
        # real probe underneath while positively counting invocations.
        installer = load_installer()
        skills = installer.discover_skills()[:3]
        self.assertGreaterEqual(len(skills), 2, "need N>1 skills for this test to be meaningful")

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            with mock.patch.object(
                installer, "resolve_interpreter", wraps=installer.resolve_interpreter
            ) as resolve_spy:
                installer.install_skills(
                    skills,
                    target_root,
                    dry_run=False,
                    force=False,
                    full_set=False,
                    restart_message="",
                    out=lambda _msg: None,
                )
            self.assertEqual(
                1,
                resolve_spy.call_count,
                "resolve_interpreter must be called exactly once for an N-skill "
                "install, not once per skill",
            )
            for skill in skills:
                self.assertTrue((target_root / skill.install_name / "interpreter.json").is_file())

    def test_sidecar_records_resolved_via_for_probe_success_and_fallback(self):
        # Required evidence (6): resolved_via sidecar-content correctness for
        # BOTH the probe-success and os-default-fallback cases.
        installer = load_installer()
        skill = installer.discover_skills()[0]

        def fake_run_success(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            with mock.patch.object(installer.subprocess, "run", side_effect=fake_run_success):
                installer.install_skills(
                    [skill], target_root, dry_run=False, force=False,
                    full_set=False, restart_message="", out=lambda _msg: None,
                )
            sidecar = json.loads(
                (target_root / skill.install_name / "interpreter.json").read_text(encoding="utf-8")
            )
            self.assertEqual("probe", sidecar["resolved_via"])
            self.assertEqual("py", sidecar["interpreter"])
            self.assertEqual(["py", "python3", "python"], sidecar["candidates"])

        def fake_run_failure(cmd, **kwargs):
            raise FileNotFoundError("no such candidate")

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            with mock.patch.object(installer.subprocess, "run", side_effect=fake_run_failure):
                with mock.patch.object(installer.os, "name", "nt"):
                    installer.install_skills(
                        [skill], target_root, dry_run=False, force=False,
                        full_set=False, restart_message="", out=lambda _msg: None,
                    )
            sidecar = json.loads(
                (target_root / skill.install_name / "interpreter.json").read_text(encoding="utf-8")
            )
            self.assertEqual("os-default-fallback", sidecar["resolved_via"])
            self.assertEqual("py", sidecar["interpreter"])


def _direct_runtime_siblings(module_path: Path, scripts_root: Path) -> set[str]:
    """Sibling modules under scripts/ that `module_path` can reach at runtime.

    Two reach mechanisms exist in this tree and BOTH have to be seen:

    1. dynamic path load -- `Path(__file__).parent / "x.py"` + importlib
       (`checklist_engine._load_gauge_reader()`).
    2. `sys.path.insert(0, <own parent>)` followed by a PLAIN
       `import x` / `from x import ...` (`checklist_engine` -> `episode_capture`,
       #305). Deferred imports written inside a function to break an import
       cycle (`episode_capture.emit_step_manifest` -> `context_manifest`) count
       too, which is why this walks the AST rather than matching top-of-file
       lines.

    Mechanism 2 is the one the original regex-only detector was blind to, so the
    #305 sidecar could be imported by the engine and shipped by nobody. A name
    counts only if `scripts/<name>.py` actually exists -- that single test is
    what separates a co-located sibling from stdlib/third-party without a
    hand-kept denylist that could rot.
    """
    src = module_path.read_text(encoding="utf-8")
    names = set(re.findall(r'parent\s*/\s*"([A-Za-z0-9_]+\.py)"', src))
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0] + ".py")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0] + ".py")
    return {name for name in names if (scripts_root / name).is_file()}


def engine_runtime_closure(entry: str, scripts_root: Path) -> set[str]:
    """Everything `entry` drags in at runtime, TRANSITIVELY, minus itself.

    Transitive because the shipping unit is the closure, not the first hop:
    `episode_capture.py` alone would still crash on an install missing
    `agent_work_root.py`. Cycles are normal here (`context_manifest` imports
    `checklist_engine` back) and are absorbed by the visited set."""
    seen = {entry}
    queue = [entry]
    reached: set[str] = set()
    while queue:
        for name in _direct_runtime_siblings(scripts_root / queue.pop(), scripts_root):
            reached.add(name)
            if name not in seen:
                seen.add(name)
                queue.append(name)
    reached.discard(entry)
    return reached


class RuntimeCompanionBundleTests(unittest.TestCase):
    """A bundled script that loads a sibling at runtime must ship that sibling.

    The Context Governor (epic-178) was inert in every install from the day it
    shipped: `checklist_engine.py` was bundled into ten skills, `gauge_reader.py`
    into none, and `_load_gauge_reader()` fails open to None -- so Trip silently
    never fired and nothing reported that it wasn't firing. These tests are
    derived from the engine's ACTUAL dynamic loads rather than a hand-kept list,
    so a newly-added companion cannot be forgotten the same way."""

    # Modules checklist_engine.py reaches at runtime, transitively. Kept here as
    # the expected set so the parse below has something to assert against; the
    # parse is what makes it honest.
    #   gauge_reader     -- dynamic `parent / "gauge_reader.py"` load (#256)
    #   episode_capture  -- sys.path.insert + plain import (#305)
    #   agent_work_root  -- episode_capture, module scope
    #   context_manifest -- episode_capture, deferred inside emit_step_manifest
    ENGINE_RUNTIME_SIBLINGS = {
        "gauge_reader.py", "episode_capture.py",
        "agent_work_root.py", "context_manifest.py",
    }
    SCRIPTS_ROOT = ROOT / "scripts"

    def test_engine_runtime_siblings_are_declared_as_companions(self):
        """Derive what checklist_engine.py reaches at runtime and require every
        reached sibling to be declared in SCRIPT_RUNTIME_COMPANIONS.

        This replaces a regex that only saw `parent / "<name>.py"` dynamic loads.
        That regex returned exactly {'gauge_reader.py'} against an engine source
        that ALREADY contained `from episode_capture import emit_step_manifest`,
        so #305's capture seam shipped to nobody and no test noticed: the engine
        wraps the import in `try/except ImportError` with a no-op fallback, so on
        every installed skill the gate completed and emitted nothing. The point
        of widening this is the NEXT sidecar attached the same way, not this one.
        """
        installer = load_installer()
        reachable = engine_runtime_closure("checklist_engine.py", self.SCRIPTS_ROOT)
        self.assertEqual(
            self.ENGINE_RUNTIME_SIBLINGS, reachable,
            "checklist_engine.py's runtime sibling closure changed; update "
            "SCRIPT_RUNTIME_COMPANIONS and this expectation together",
        )
        declared = set(installer.SCRIPT_RUNTIME_COMPANIONS.get("checklist_engine.py", ()))
        undeclared = reachable - declared
        self.assertEqual(
            set(), undeclared,
            f"checklist_engine.py imports {sorted(undeclared)} at runtime but "
            "SCRIPT_RUNTIME_COMPANIONS['checklist_engine.py'] does not declare "
            "them -- every skill bundling the engine installs a tree where that "
            "import fails, and the engine's ImportError fallback makes the "
            "feature no-op SILENTLY",
        )
        self.assertEqual(reachable, declared)

    def test_every_skill_bundling_the_engine_also_gets_its_runtime_companions(self):
        """Generalized from the gauge-reader-only form: assert the whole declared
        companion tuple lands in every engine-carrying bundle, so adding a
        companion to the dict automatically widens this test's coverage."""
        installer = load_installer()
        companions = installer.SCRIPT_RUNTIME_COMPANIONS["checklist_engine.py"]
        # the original #256 guarantee, still pinned by name so the generalization
        # cannot quietly drop it
        self.assertIn("gauge_reader.py", companions)
        engine_skills = [
            name for name, scripts in installer.SKILL_SCRIPT_BUNDLES.items()
            if "checklist_engine.py" in scripts
        ]
        self.assertTrue(engine_skills, "no skill bundles checklist_engine.py?")
        for name in engine_skills:
            expanded = installer.expand_script_bundle(
                installer.SKILL_SCRIPT_BUNDLES[name])
            for companion in companions:
                with self.subTest(skill=name, companion=companion):
                    self.assertIn(companion, expanded)

    def test_expansion_preserves_order_and_does_not_duplicate(self):
        installer = load_installer()
        # Derived from the dict, not a literal: this test is about the expansion
        # MECHANISM, and pinning a literal companion list here made adding the
        # #305 sidecars fail a test that has no opinion about them.
        companions = installer.SCRIPT_RUNTIME_COMPANIONS["checklist_engine.py"]
        # a companion also listed explicitly must not be added twice
        out = installer.expand_script_bundle(("checklist_engine.py", companions[0]))
        self.assertEqual(("checklist_engine.py", *companions), out)
        self.assertEqual(len(out), len(set(out)))
        # explicit entries keep their position; companions follow their owner
        self.assertEqual(
            (companions[0], "checklist_engine.py", *companions[1:]),
            installer.expand_script_bundle((companions[0], "checklist_engine.py")),
        )
        # a script with no companions passes through untouched
        self.assertEqual(("docent_freshness.py",),
                         installer.expand_script_bundle(("docent_freshness.py",)))

    def test_installed_engine_can_actually_load_its_gauge_reader(self):
        """End-to-end: install for real, then load the INSTALLED engine and assert
        it resolved its gauge reader. Asserting the file's presence would not
        prove the import path works -- this drives the real loader."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            rc = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", "admiral"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, rc)
            engine = dest / "constellation-admiral" / "scripts" / "checklist_engine.py"
            self.assertTrue(engine.is_file())
            mod = load_module("installed_checklist_engine", engine)
            self.assertIsNotNone(
                mod._gauge_reader,
                "installed engine could not load gauge_reader.py -- the Context "
                "Governor would be inert in this install",
            )
            self.assertTrue(hasattr(mod._gauge_reader, "thresholds_for"))

    def test_installed_engine_binds_the_real_capture_seam_not_the_fallback(self):
        """End-to-end for #305/#362: install a skill whose bundle is the engine
        ALONE, then load the installed engine and prove `emit_step_manifest` is
        the sidecar's, not the module-local `try/except ImportError` no-op.

        Asserting the dict, or even the files on disk, cannot prove this: the
        fallback is what makes the failure silent, so the only honest check is
        which function the installed engine actually bound. `implementer` is the
        deliberate choice of skill -- its bundle carries no companion by hand, so
        everything here arrives through expand_script_bundle()."""
        installer = load_installer()
        companions = installer.SCRIPT_RUNTIME_COMPANIONS["checklist_engine.py"]
        self.assertEqual(("checklist_engine.py",),
                         installer.SKILL_SCRIPT_BUNDLES["implementer"],
                         "test premise changed: implementer no longer bundles the "
                         "engine alone, so this no longer exercises expansion")
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            rc = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", "implementer"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, rc)
            scripts_dir = dest / "constellation-implementer" / "scripts"
            for companion in companions:
                with self.subTest(companion=companion):
                    self.assertTrue((scripts_dir / companion).is_file(),
                                    f"{companion} did not ship")
            # A stale sibling already in sys.modules would satisfy the engine's
            # import from the REPO and green this test on a broken install.
            sidecars = ("episode_capture", "agent_work_root", "context_manifest")
            saved = {n: sys.modules.pop(n, None) for n in sidecars}
            try:
                mod = load_module("installed_engine_305", scripts_dir / "checklist_engine.py")
                self.assertEqual(
                    "episode_capture", mod.emit_step_manifest.__module__,
                    "installed engine fell back to the no-op emit_step_manifest -- "
                    "the #305 capture seam would be inert in this install",
                )
                bound = Path(sys.modules["episode_capture"].__file__).resolve()
                self.assertEqual((scripts_dir / "episode_capture.py").resolve(), bound,
                                 "engine bound a sidecar from outside the install")
            finally:
                for name, prior in saved.items():
                    if prior is None:
                        sys.modules.pop(name, None)
                    else:
                        sys.modules[name] = prior


class HookScriptBundleTests(unittest.TestCase):
    """The Context Governor's gauge WRITER has to ship, and ship co-located.

    #256 bundled the gauge *reader* into every skill carrying the engine, so an
    installed tree could READ a gauge that nothing ever WROTE -- the installer
    had zero references to the hook pair. These tests ship the writer.

    The co-location half is the load-bearing half and it fails SILENTLY:
    `gauge_writer_hook._load_spine_rail()` resolves
    `Path(__file__).resolve().parent / "spine_rail.py"` inside a bare
    `try/except Exception: return None`. Land the two files in different
    directories and nothing raises, nothing logs -- the hook just stops
    resolving gauge paths. So the assertions below are made against the
    OUTCOME ON DISK from a real install, and against the real loader, never
    against the bundle dict alone (which cannot see a source-path mistake)."""

    HOOK_SOURCE_DIR = ROOT / "scripts" / "hooks"
    WRITER = "gauge_writer_hook.py"
    RAIL = "spine_rail.py"
    # Canonical owner: the hook exists solely to feed checklist_engine.py's
    # `current` advisory, so it installs into the checklist engine's home skill.
    # Deliberately NOT a companion of checklist_engine.py -- that would copy it
    # into ~10 skills and reintroduce a "which copy is canonical?" ambiguity.
    OWNER_SKILL = "workbench"
    INSTALLED_OWNER = "constellation-workbench"

    def _install_owner_skill(self, tmp: str) -> Path:
        """Really install the owner skill into a temp dest; return its scripts/ dir."""
        installer = load_installer()
        dest = Path(tmp) / "skills"
        exit_code = installer.main(
            ["--agent", "claude", "--scope", "user", "--dest", str(dest),
             "--skills", self.OWNER_SKILL],
            env={}, out=lambda _line: None,
        )
        self.assertEqual(0, exit_code)
        return dest / self.INSTALLED_OWNER / "scripts"

    def test_hook_pair_lands_co_located_in_a_real_install(self):
        """Install for real and assert both files sit in the SAME directory on
        disk. Inspecting the bundle dict would pass even if the copy loop wrote
        them to different places."""
        with tempfile.TemporaryDirectory() as tmp:
            scripts_dir = self._install_owner_skill(tmp)
            writer = scripts_dir / self.WRITER
            rail = scripts_dir / self.RAIL
            self.assertTrue(
                writer.is_file(),
                f"{self.WRITER} was not installed -- no install ships a gauge writer",
            )
            self.assertTrue(
                rail.is_file(),
                f"{self.RAIL} was not installed -- the writer's sibling load "
                f"would fail open to None and the hook would silently no-op",
            )
            self.assertEqual(
                writer.parent, rail.parent,
                "hook pair is not co-located; the sibling load resolves relative "
                "to __file__, so a split lands them where neither can find the other",
            )
            installed = sorted(p.name for p in scripts_dir.iterdir() if p.is_file())
            self.assertIn(self.WRITER, installed)
            self.assertIn(self.RAIL, installed)

    def test_installed_gauge_writer_hook_actually_loads_its_spine_rail(self):
        """End-to-end: install, then import the INSTALLED writer and assert it
        resolved its rail. Presence on disk does not prove the sibling load
        works; this drives the real loader (import-time `_load_spine_rail()`)."""
        with tempfile.TemporaryDirectory() as tmp:
            scripts_dir = self._install_owner_skill(tmp)
            mod = load_module("installed_gauge_writer_hook", scripts_dir / self.WRITER)
            self.assertIsNotNone(
                mod._spine_rail,
                "installed gauge writer hook could not load spine_rail.py -- it "
                "would resolve no gauge path and write nothing, silently",
            )
            self.assertTrue(hasattr(mod._spine_rail, "resolve_project_dir"))

    def test_gauge_writer_hook_dynamic_loads_are_declared_as_companions(self):
        """Parse the writer's source for `parent / "<name>.py"` sibling loads and
        require each to be declared. Mirrors the engine's companion test so a NEW
        dynamic load cannot be added without a matching bundle entry."""
        installer = load_installer()
        source = (self.HOOK_SOURCE_DIR / self.WRITER).read_text(encoding="utf-8")
        siblings = set(re.findall(r'parent\s*/\s*"([A-Za-z0-9_]+\.py)"', source))
        self.assertEqual(
            {self.RAIL}, siblings,
            f"{self.WRITER}'s dynamic sibling loads changed; update "
            "SCRIPT_RUNTIME_COMPANIONS and this expectation together",
        )
        declared = set(installer.SCRIPT_RUNTIME_COMPANIONS.get(self.WRITER, ()))
        self.assertEqual(siblings, declared)

    def test_owner_skill_bundle_expands_to_both_hook_scripts(self):
        installer = load_installer()
        expanded = installer.expand_script_bundle(
            installer.SKILL_SCRIPT_BUNDLES[self.OWNER_SKILL])
        self.assertIn(self.WRITER, expanded)
        self.assertIn(self.RAIL, expanded)

    def test_gauge_writer_hook_ships_to_exactly_one_canonical_owner(self):
        """One canonical copy, by design: whatever later wires this hook into a
        settings.json needs an unambiguous path to point at."""
        installer = load_installer()
        owners = sorted(
            name for name, scripts in installer.SKILL_SCRIPT_BUNDLES.items()
            if self.WRITER in installer.expand_script_bundle(scripts)
        )
        self.assertEqual([self.OWNER_SKILL], owners)

    def test_hook_sources_stay_under_scripts_hooks(self):
        """The SOURCE layout is frozen -- this repo's own settings file plus
        tests/test_gauge_writer.py and tests/test_spine_rail.py hardcode
        `scripts/hooks/...`. Bundling must reach into the subdirectory rather
        than relocate the sources up into scripts/."""
        installer = load_installer()
        for name in (self.WRITER, self.RAIL):
            with self.subTest(script=name):
                self.assertTrue((self.HOOK_SOURCE_DIR / name).is_file())
                self.assertFalse((ROOT / "scripts" / name).exists())
                self.assertEqual("hooks", installer.SCRIPT_SOURCE_SUBDIRS[name])

    def test_validation_accepts_hook_scripts_from_their_subdirectory(self):
        """`validate_required_scripts` runs before every install and resolves
        sources under scripts/. A subdir-blind check turns bundling the hooks
        into a hard install failure rather than a silent one."""
        installer = load_installer()
        owner = [s for s in installer.discover_skills()
                 if s.source_name == self.OWNER_SKILL]
        self.assertEqual(1, len(owner))
        self.assertIn(self.WRITER, owner[0].required_scripts)
        installer.validate_required_scripts(owner)  # must not raise


class ScriptsPackageBundlingTests(unittest.TestCase):
    """Issue #456 g0: scripts/ gained its first real Python package, and the
    install destination is flat. A package whose modules import each other
    relatively cannot survive that flattening, so every directory under scripts/
    has to be on the record as one thing or the other."""

    SCRIPTS = ROOT / "scripts"

    def _source_dirs(self):
        """Directories under scripts/ that hold Python modules."""
        return sorted(d for d in self.SCRIPTS.iterdir()
                      if d.is_dir() and d.name != "__pycache__"
                      and any(d.glob("*.py")))

    def test_every_scripts_subdirectory_is_declared_one_way_or_the_other(self):
        """The gate this test exists for: a new package under scripts/ fails here
        until somebody decides whether it bundles, instead of failing at install
        time in someone else's run."""
        installer = load_installer()
        self.assertTrue(self._source_dirs(), "input precondition: scripts/ must "
                        "have at least one module subdirectory, or this declares nothing")
        for d in self._source_dirs():
            with self.subTest(directory=d.name):
                non_installable = d.name in installer.NON_INSTALLABLE_PACKAGES
                flattened = [p.name for p in d.glob("*.py")
                             if installer.SCRIPT_SOURCE_SUBDIRS.get(p.name) == d.name]
                self.assertTrue(
                    non_installable or len(flattened) == len(list(d.glob("*.py"))),
                    f"scripts/{d.name}/ is neither in NON_INSTALLABLE_PACKAGES nor "
                    f"fully declared in SCRIPT_SOURCE_SUBDIRS")

    def test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not(self):
        """The declaration has to match reality: __init__.py is what makes the
        relative imports that flattening breaks."""
        installer = load_installer()
        for d in self._source_dirs():
            with self.subTest(directory=d.name):
                is_package = (d / "__init__.py").is_file()
                self.assertEqual(is_package,
                                 d.name in installer.NON_INSTALLABLE_PACKAGES)

    def test_no_skill_bundles_a_module_from_a_non_installable_package(self):
        """Bundling one of these copies it flat and every relative import in it
        raises on the installed side, where nothing here would catch it."""
        installer = load_installer()
        forbidden = set()
        for pkg in installer.NON_INSTALLABLE_PACKAGES:
            forbidden |= {p.name for p in (self.SCRIPTS / pkg).glob("*.py")}
        self.assertTrue(forbidden, "input precondition: the non-installable "
                        "packages must actually contain modules to forbid")
        for skill in installer.discover_skills():
            for script in skill.required_scripts:
                with self.subTest(skill=skill.install_name, script=script):
                    self.assertNotIn(script, forbidden)

    def test_the_declared_package_is_runnable_from_a_checkout(self):
        """The stated alternative to bundling has to actually work, or the
        declaration is just a refusal."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.code_map", "--help"],
            cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)


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


class RegisteredScriptSourceTests(unittest.TestCase):
    """Source resolution has exactly ONE owner: `script_source_path`.

    The installer half of the #262 regression. `scripts/verify_skill_registered.py`
    re-implemented the lookup as `REPO_ROOT/"scripts"/script`, blind to
    SCRIPT_SOURCE_SUBDIRS, and falsely refused `workbench` the moment a bundled
    script started shipping from `scripts/hooks/`. That was invisible to the whole
    suite, so pin it from both sides: the rail's side lives in
    tests/test_write_a_skill.py."""

    def test_every_registered_bundle_script_resolves_through_the_shared_resolver(self):
        installer = load_installer()
        scripts_root = Path(installer.REPO_ROOT) / "scripts"
        subdir_backed = 0
        for skill, bundle in installer.SKILL_SCRIPT_BUNDLES.items():
            for script in installer.expand_script_bundle(bundle):
                with self.subTest(skill=skill, script=script):
                    source = installer.script_source_path(script, scripts_root)
                    self.assertTrue(
                        source.is_file(),
                        f"{skill} registers {script}, which script_source_path resolves "
                        f"to {source} -- a path with no file behind it",
                    )
                if script in installer.SCRIPT_SOURCE_SUBDIRS:
                    subdir_backed += 1
        self.assertGreater(
            subdir_backed, 0,
            "no registered script is sourced from a subdirectory any more -- this "
            "test no longer exercises the case it was written for",
        )


class _HookWiringFixture(unittest.TestCase):
    """Shared fixture for the Context Governor settings.json detection + wiring
    tests. `--dest <tmp>/skills` is used everywhere so the settings file under
    test is `<tmp>/settings.json` -- a real install layout, and structurally
    incapable of touching the developer's own ~/.claude/settings.json."""

    OWNER_SKILL = "workbench"
    INSTALLED_OWNER = "constellation-workbench"
    WRITER = "gauge_writer_hook.py"

    def _dest(self, tmp) -> Path:
        return Path(tmp) / "skills"

    def _settings(self, tmp) -> Path:
        return Path(tmp) / "settings.json"

    def _write_settings(self, tmp, payload: dict) -> Path:
        path = self._settings(tmp)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def _run(self, tmp, *extra, expect=0):
        """A real install run against <tmp>/skills, capturing its output."""
        installer = load_installer()
        lines = []
        code = installer.main(
            ["--agent", "claude", "--scope", "user", "--dest", str(self._dest(tmp)),
             "--skills", self.OWNER_SKILL, *extra],
            env={}, out=lines.append,
        )
        self.assertEqual(expect, code)
        return "\n".join(lines)

    def _fake_hook_file(self, tmp) -> Path:
        """A resolvable gauge_writer_hook.py that no install created -- lets the
        detector be exercised without paying for a full install."""
        path = Path(tmp) / "elsewhere" / self.WRITER
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# stand-in\n", encoding="utf-8")
        return path

    @staticmethod
    def _entry(command: str, matcher: str = "*") -> dict:
        return {"matcher": matcher,
                "hooks": [{"type": "command", "command": command, "timeout": 10}]}


class HookWiringDetectionTests(_HookWiringFixture):
    """Always-on, no-flag detection (#262). Three states -- wired / stale /
    unwired -- classified by RESOLVING the referenced path against the
    filesystem, never by string-matching it.

    `stale` is the load-bearing state and is not polish: under binary detection
    a moved or renamed install reads as *wired*, which is the reassuring-failure
    shape. Per #265, "hook not wired at all" is the one silence cause the gauge
    writer can never self-report -- a hook that never runs cannot write a sidecar
    explaining that it never ran -- so this detector is the only thing in the
    system that can ever surface it.

    The other half is a human ruling (`decision:opt-in-wiring-only`): without
    `--wire-hooks` the installer reads and reports and writes NOTHING, and does
    not even create an absent settings.json."""

    def test_detects_unwired_when_settings_json_is_absent(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            wiring = installer.detect_hook_wiring(self._settings(tmp), env={})
            self.assertEqual(installer.WIRING_UNWIRED, wiring.state)
            self.assertFalse(wiring.settings_exists)

    def test_detects_unwired_when_settings_has_no_governor_entry(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry('py "/opt/other/unrelated_hook.py"', matcher="Bash")]}})
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_UNWIRED, wiring.state)
            self.assertTrue(wiring.settings_exists)

    def test_detects_wired_when_the_entry_resolves_on_disk(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry(f'py "{hook.as_posix()}"')]}})
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_WIRED, wiring.state)

    def test_detects_stale_when_the_entry_path_no_longer_exists(self):
        """The moved-install case. A string-matching detector reports this as
        `wired` -- syntactically present, silently dead."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry(f'py "{hook.as_posix()}"')]}})
            hook.unlink()  # the install moved / was uninstalled
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_STALE, wiring.state)
            self.assertEqual((), wiring.resolved)
            self.assertEqual(1, len(wiring.unresolved))

    def test_detection_classifies_by_resolution_not_by_string_match(self):
        """Two entries, textually indistinguishable in shape; only one has a file
        behind it. A string-matching detector cannot tell them apart at all."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            real = self._fake_hook_file(tmp)
            ghost = Path(tmp) / "moved-away" / self.WRITER  # never created
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry(f'py "{ghost.as_posix()}"'),
                self._entry(f'py "{real.as_posix()}"'),
            ]}})
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_WIRED, wiring.state)
            self.assertEqual(1, len(wiring.resolved))
            self.assertEqual(1, len(wiring.unresolved))

    def test_detection_expands_env_tokens_in_a_hand_wired_entry(self):
        """docs/GAUGE_WRITER_HOOK.md currently tells users to hand-wire a
        `${CLAUDE_PROJECT_DIR}` entry. The installer never GENERATES that form,
        but reporting a working hand-wired entry as `stale` would be a false
        alarm, so resolution expands env tokens from the run's own env."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry('py "${CLAUDE_PROJECT_DIR}/' + self.WRITER + '"')]}})
            env = {"CLAUDE_PROJECT_DIR": hook.parent.as_posix()}
            self.assertEqual(installer.WIRING_WIRED,
                             installer.detect_hook_wiring(path, env=env).state)
            # ...and with nothing to expand it with, we say we CANNOT TELL.
            # Not `stale`: CLAUDE_PROJECT_DIR is empirically unreadable outside a
            # hook subprocess (#269), so it is unset in the ordinary case and
            # reporting "definitely broken" would be the false alarm this
            # expansion was added to prevent -- just pointed the other way.
            self.assertEqual(installer.WIRING_UNDETERMINABLE,
                             installer.detect_hook_wiring(path, env={}).state)

    def test_detection_will_not_expand_an_arbitrary_env_var(self):
        """Regression, reproduced by the g2 reviewer: expansion happens in the
        INSTALLER's environment while the entry runs in a future HOOK's, so an
        unrelated variable that happens to be set right now could resolve a path
        and report WIRED -- manufacturing the exact reassuring failure this
        detector exists to prevent. Only CLAUDE_PROJECT_DIR is expandable."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry('py "%MYTOOLS%/' + self.WRITER + '"')]}})
            # The var IS set and WOULD resolve to a real file -- and we still
            # refuse to claim the hook is wired on that basis.
            wiring = installer.detect_hook_wiring(
                path, env={"MYTOOLS": hook.parent.as_posix()})
            self.assertEqual(installer.WIRING_UNDETERMINABLE, wiring.state)
            self.assertEqual((), wiring.resolved)
            self.assertEqual(1, len(wiring.undeterminable))

    def test_undeterminable_is_reported_as_neither_wired_nor_stale(self):
        """"I cannot tell" must not be laundered into either confident verdict."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry('py "${SOME_OTHER_VAR}/' + self.WRITER + '"')]}})
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_UNDETERMINABLE, wiring.state)
            line = installer.describe_hook_wiring(wiring)
            self.assertIn("CANNOT EVALUATE", line)
            self.assertNotIn("WIRED --", line)
            self.assertNotIn("STALE", line)

    def test_a_resolvable_entry_still_wins_over_an_undeterminable_one(self):
        """A real working entry alongside an unevaluatable one is WIRED: the
        governor demonstrably fires, whatever the other entry does."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry('py "%MYSTERY%/' + self.WRITER + '"'),
                self._entry(f'py "{hook.as_posix()}"')]}})
            self.assertEqual(installer.WIRING_WIRED,
                             installer.detect_hook_wiring(path, env={}).state)

    def test_detection_survives_an_unparseable_settings_json(self):
        """A broken settings.json must not take the install down with it, and
        must not be reported as one of the three real states -- we could not
        classify it at all."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._settings(tmp)
            path.write_text("{ not json", encoding="utf-8")
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_UNREADABLE, wiring.state)
            output = self._run(tmp)  # a real install run still succeeds
            self.assertIn("Context Governor hooks:", output)

    def test_no_flag_install_run_reports_the_wiring_state(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            output = self._run(tmp)
            self.assertIn(f"Context Governor hooks: {installer.WIRING_UNWIRED.upper()}",
                          output)

    def test_no_flag_install_run_does_not_create_an_absent_settings_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp)
            self.assertFalse(
                self._settings(tmp).exists(),
                "the no-flag path created a settings.json -- the human ruling is "
                "that the installer never writes one without --wire-hooks",
            )

    def test_no_flag_install_run_leaves_settings_json_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_settings(tmp, {
                "permissions": {"allow": ["Bash(ls:*)"]},
                "hooks": {"PostToolUse": [
                    self._entry('py "/opt/other/unrelated_hook.py"', matcher="Bash")]},
            })
            before = path.read_bytes()
            self._run(tmp)
            self.assertEqual(before, path.read_bytes())

    def test_no_flag_dry_run_detects_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--dry-run")
            self.assertFalse(self._settings(tmp).exists())

    def test_settings_path_is_the_sibling_of_the_installed_skills_dir(self):
        installer = load_installer()
        self.assertEqual(
            Path("/home/u/.claude/settings.json"),
            installer.settings_path_for_target_root(Path("/home/u/.claude/skills")),
        )

    def test_detection_is_skipped_for_agents_with_no_hook_mechanism(self):
        """Hooks are a Claude Code mechanism. Reporting on -- let alone writing --
        a `hooks.PostToolUse` array under ~/.codex/ would be talking about a file
        nothing ever reads."""
        installer = load_installer()
        lines = []
        with tempfile.TemporaryDirectory() as tmp:
            code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(self._dest(tmp)),
                 "--skills", self.OWNER_SKILL],
                env={}, out=lines.append,
            )
        self.assertEqual(0, code)
        self.assertNotIn("Context Governor hooks:", "\n".join(lines))


class HookWiringOptInTests(_HookWiringFixture):
    """`--wire-hooks` -- the ONLY path on which the installer writes a
    settings.json (`decision:opt-in-wiring-only`, a human ruling).

    The command string carries an ABSOLUTE installed path, never
    `${CLAUDE_PROJECT_DIR}`. That variable happens to deliver anti-tamper today
    only as an accident of undocumented harness behaviour (#269: it is fixed at
    session launch, so it happens to point at the main checkout for a worktree
    agent). An absolute installed path is pinned BY CONSTRUCTION and asks the
    harness to guarantee nothing -- which is what actually protects Fred's
    ruling that an agent's own branch cannot edit the code that judges it."""

    def _wire(self, tmp, *extra):
        return self._run(tmp, "--wire-hooks", *extra)

    def _settings_json(self, tmp) -> dict:
        return json.loads(self._settings(tmp).read_text(encoding="utf-8"))

    def _entries(self, tmp) -> list:
        return self._settings_json(tmp)["hooks"]["PostToolUse"]

    UNRELATED = {
        "matcher": "Bash",
        "hooks": [{"type": "command",
                   "command": 'py "${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" PostToolUse',
                   "timeout": 20}],
    }

    # -- the command string -------------------------------------------------

    def test_wire_hooks_writes_an_absolute_path_not_a_project_dir_token(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._wire(tmp)
            command = self._entries(tmp)[0]["hooks"][0]["command"]
            expected = installer.installed_gauge_writer_path(self._dest(tmp))
            self.assertIn(expected.as_posix(), command)
            self.assertNotIn("${CLAUDE_PROJECT_DIR}", command)
            self.assertNotIn("$HOME", command)
            self.assertNotIn("%USERPROFILE%", command)
            self.assertTrue(Path(expected).is_absolute())
            self.assertTrue(expected.is_file(), "wired a path with no file behind it")

    def test_wired_command_uses_the_probed_interpreter_and_documented_timeout(self):
        """The interpreter comes from the existing probe, not a hardcoded `py`;
        the timeout is carried verbatim from docs/GAUGE_WRITER_HOOK.md."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._wire(tmp)
            entry = self._entries(tmp)[0]
            self.assertEqual("*", entry["matcher"])
            hook = entry["hooks"][0]
            self.assertEqual("command", hook["type"])
            self.assertEqual(10, hook["timeout"])
            self.assertEqual(installer.HOOK_TIMEOUT, hook["timeout"])
            self.assertTrue(
                hook["command"].startswith(installer.resolve_interpreter().interpreter + " "),
                f"command did not start with the probed interpreter: {hook['command']!r}",
            )

    def test_the_wired_command_string_actually_executes(self):
        """Run the generated command EXACTLY as Claude Code would -- same string,
        stdin JSON -- and require it not to refuse.

        String-matching the rendered command is not evidence that it works, and
        this whole issue exists because a shipped-but-inert Context Governor is
        indistinguishable from a working one from the outside. A quoting slip,
        a bad interpreter, or a path that does not resolve would be invisible to
        every other assertion in this class."""
        with tempfile.TemporaryDirectory() as tmp:
            self._wire(tmp)
            command = self._entries(tmp)[0]["hooks"][0]["command"]
            result = subprocess.run(
                command, shell=True, input="{}", capture_output=True, text=True,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            self.assertEqual(
                0, result.returncode,
                f"the wired command did not run: {command!r}\n"
                f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
            )

    def test_a_wired_entry_then_detects_as_wired(self):
        """Round trip: what the wiring writes is what the detector recognises."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._wire(tmp)
            wiring = installer.detect_hook_wiring(self._settings(tmp), env={})
            self.assertEqual(installer.WIRING_WIRED, wiring.state)

    # -- negative 2: --wire-hooks --dry-run TOGETHER -------------------------

    def test_wire_hooks_with_dry_run_together_writes_nothing(self):
        """THE risky combination, and it gets its own test on purpose: `dry_run`
        is pre-existing plumbing that a brand-new write path can trivially fail
        to consult. A no-flag dry run is trivially safe and does NOT stand in
        for this."""
        with tempfile.TemporaryDirectory() as tmp:
            existing = self._write_settings(tmp, {
                "permissions": {"allow": ["Bash(ls:*)"]},
                "hooks": {"PostToolUse": [self.UNRELATED]},
            })
            before = existing.read_bytes()
            output = self._wire(tmp, "--dry-run")
            self.assertEqual(
                before, existing.read_bytes(),
                "--wire-hooks --dry-run modified settings.json",
            )
            self.assertIn("DRY RUN", output)

    def test_wire_hooks_with_dry_run_does_not_create_an_absent_settings_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._wire(tmp, "--dry-run")
            self.assertFalse(
                self._settings(tmp).exists(),
                "--wire-hooks --dry-run created a settings.json",
            )

    # -- negative 3: additive -----------------------------------------------

    def test_wire_hooks_is_additive_and_preserves_unrelated_settings(self):
        """An unrelated PostToolUse matcher must survive intact and unreordered,
        alongside unrelated top-level keys."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_settings(tmp, {
                "permissions": {"allow": ["Bash(ls:*)"], "deny": []},
                "env": {"FOO": "bar"},
                "hooks": {
                    "Stop": [{"hooks": [{"type": "command", "command": "py stop.py"}]}],
                    "PostToolUse": [self.UNRELATED],
                },
            })
            self._wire(tmp)
            settings = self._settings_json(tmp)
            self.assertEqual({"allow": ["Bash(ls:*)"], "deny": []}, settings["permissions"])
            self.assertEqual({"FOO": "bar"}, settings["env"])
            self.assertEqual(
                [{"hooks": [{"type": "command", "command": "py stop.py"}]}],
                settings["hooks"]["Stop"],
            )
            entries = settings["hooks"]["PostToolUse"]
            self.assertEqual(2, len(entries))
            # ...intact, and FIRST -- not reordered.
            self.assertEqual(self.UNRELATED, entries[0])

    def test_wire_hooks_appends_a_sibling_and_never_nests_in_an_existing_matcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_settings(tmp, {"hooks": {"PostToolUse": [self.UNRELATED]}})
            self._wire(tmp)
            entries = self._entries(tmp)
            self.assertEqual(1, len(entries[0]["hooks"]),
                             "the new hook was nested inside the existing matcher block")
            new = entries[1]
            self.assertEqual("*", new["matcher"])
            self.assertEqual(1, len(new["hooks"]))

    def test_wire_hooks_creates_settings_json_only_under_the_opt_in_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp)                       # no flag
            self.assertFalse(self._settings(tmp).exists())
            self._wire(tmp, "--force")           # opt-in
            self.assertTrue(self._settings(tmp).exists())
            self.assertEqual(1, len(self._entries(tmp)))

    def test_wire_hooks_twice_does_not_duplicate_the_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._wire(tmp)
            self._wire(tmp, "--force")
            self.assertEqual(1, len(self._entries(tmp)))

    def test_wire_hooks_leaves_a_stale_entry_in_place_and_adds_a_sibling(self):
        """No self-healing, by design (the design brief names this an accepted
        cost): the stale entry is REPORTED, never silently rewritten."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            stale = self._entry('py "/gone/away/gauge_writer_hook.py"')
            self._write_settings(tmp, {"hooks": {"PostToolUse": [stale]}})
            output = self._wire(tmp)
            entries = self._entries(tmp)
            self.assertEqual(2, len(entries))
            self.assertEqual(stale, entries[0])
            self.assertEqual(
                installer.WIRING_WIRED,
                installer.detect_hook_wiring(self._settings(tmp), env={}).state,
            )
            self.assertIn("Context Governor hooks:", output)

    # -- refusals -----------------------------------------------------------

    def test_wire_hooks_hard_errors_when_the_canonical_owner_is_not_installed(self):
        """Refusing to wire something it cannot locate is correct, and is NOT a
        fail-open violation: `decision:fail-open-is-inviolable` governs hook
        EXECUTION paths, not installer preconditions."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "user",
                         "--dest", str(self._dest(tmp)),
                         "--skills", "charter", "--wire-hooks"],
                        env={}, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)
            self.assertIn(self.OWNER_SKILL, stderr.getvalue())
            self.assertFalse(self._settings(tmp).exists())

    def test_wire_hooks_refuses_an_unparseable_settings_json_without_clobbering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._settings(tmp)
            path.write_text("{ not json", encoding="utf-8")
            before = path.read_bytes()
            installer = load_installer()
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "user",
                         "--dest", str(self._dest(tmp)),
                         "--skills", self.OWNER_SKILL, "--wire-hooks"],
                        env={}, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)
            self.assertEqual(before, path.read_bytes())

    def test_wire_hooks_is_rejected_for_an_agent_with_no_hook_mechanism(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "codex", "--scope", "user",
                         "--dest", str(self._dest(tmp)),
                         "--skills", self.OWNER_SKILL, "--wire-hooks"],
                        env={}, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)
            self.assertFalse(self._settings(tmp).exists())

    def test_wire_hooks_is_rejected_with_baseline_only(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            project.mkdir()
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "project",
                         "--project", str(project), "--baseline-only", "--wire-hooks"],
                        env={}, cwd=project, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)

    # -- the committability cost, surfaced ----------------------------------

    def test_wire_hooks_at_project_scope_warns_the_file_is_committable(self):
        """An absolute path embeds the user's home directory AND username, and a
        project-scope settings.json is committable. Wiring must not make
        committing it the path of least resistance."""
        installer = load_installer()
        lines = []
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            project.mkdir()
            code = installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", self.OWNER_SKILL, "--wire-hooks"],
                env={}, cwd=project, out=lines.append,
            )
            self.assertEqual(0, code)
            settings = project / ".claude" / "settings.json"
            self.assertTrue(settings.is_file())
            output = "\n".join(lines).lower()
            self.assertIn("commit", output)
            self.assertIn("absolute path", output)
            self.assertIn("user name", output)
