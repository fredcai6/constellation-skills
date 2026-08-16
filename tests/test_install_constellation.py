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
import tokenize
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_constellation.py"
# PRUNED (#447 g4): VERIFIER pointed at scripts/verify_agent_feedback.py, deleted by this
# retirement, as did load_verifier() and the two tests below that were its only callers.


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_installer():
    return load_module("install_constellation", INSTALLER)


# issue-116: derived from the installer's OWN enumeration (discover_skills()),
# never a second hand-maintained roster -- a skill added/renamed under skills/
# now shows up here automatically instead of silently drifting out of sync.
SKILL_NAMES = sorted(skill.install_name for skill in load_installer().discover_skills())


class InstallConstellationTests(unittest.TestCase):
    def test_replan_installs_its_pure_verifier_and_g1_contract_helper(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            self.assertEqual(
                0,
                installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                     "--skills", "replan"], env={}, out=lambda _: None,
                ),
            )
            installed = target_root / "constellation-replan" / "scripts"
            self.assertTrue((installed / "verify_replan.py").is_file())
            self.assertTrue((installed / "verify_issue_set.py").is_file())

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
                    / "verify_episode_captured.py"  # #447: replaced verify_agent_feedback.py
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
                (commander_root / "scripts" / "verify_episode_captured.py").as_posix(),
                spine["tasks"]["feedback"]["postconditions"][0]["check"]["command"],
            )
            self.assertIn(
                (commander_root / "scripts" / "verify_episode_captured.py").as_posix(),
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

    def test_there_is_no_os_name_interpreter_fallback_left(self):
        """Replaces test_platform_interpreter_maps_os_name (#539 owner ruling).

        `_platform_interpreter()` returned `py` on Windows and `python3`
        elsewhere and was reached ONLY after every candidate had been probed
        and rejected -- so its answer was always drawn from the set just
        disproved and could not be right on any platform. It is deleted rather
        than left unreferenced: dead code encoding a disproved guess is a trap
        for the next reader, who would reasonably assume it is a safety net.

        This test is the guard against it coming back, and it fails LOUDLY if
        someone reintroduces a name-shaped fallback."""
        installer = load_installer()
        self.assertFalse(
            hasattr(installer, "_platform_interpreter"),
            "_platform_interpreter is back. Its answer is always a member of "
            "INTERPRETER_CANDIDATES, and it can only run after every one of those "
            "was probed and failed -- so it is guaranteed wrong wherever it runs. "
            "resolve_interpreter must refuse instead.",
        )
        # And the module names no os.name-keyed interpreter default anywhere.
        source = INSTALLER.read_text(encoding="utf-8")
        self.assertNotIn(
            'if os.name == "nt" else', source,
            "an os.name-keyed interpreter default is back in install_constellation.py",
        )

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

    # PRUNED (#447 g4): test_agent_feedback_verifier_enforces_durable_log_location and
    # test_agent_feedback_verifier_enforces_archive_phase. Both loaded and exercised
    # scripts/verify_agent_feedback.py, which this retirement deleted; their subject is gone,
    # not merely renamed. Nothing about the INSTALLER, which this file is otherwise about,
    # was asserted by either.

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

    def test_initial_issues_is_the_only_discoverable_cut_skill(self):
        installer = load_installer()
        skills = installer.discover_skills()
        self.assertIn("to-initial-issues", {skill.source_name for skill in skills})
        self.assertIn("constellation-to-initial-issues", {skill.install_name for skill in skills})
        self.assertNotIn("to-issues", {skill.source_name for skill in skills})
        self.assertNotIn("constellation-to-issues", {skill.install_name for skill in skills})

    def test_legacy_initial_cut_destination_refuses_without_force_and_names_migration(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            legacy = target_root / "constellation-to-issues"
            legacy.mkdir(parents=True)
            marker = legacy / "legacy.txt"
            marker.write_text("keep until authorized", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
                installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                     "--skills", "to-initial-issues"], env={}, out=lambda _: None,
                )
            self.assertIn("--skills to-initial-issues --force", stderr.getvalue())
            self.assertEqual("keep until authorized", marker.read_text(encoding="utf-8"))
            self.assertFalse((target_root / "constellation-to-initial-issues").exists())

    def test_subset_force_removes_only_exact_legacy_destination_then_installs_canonical(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            legacy = target_root / "constellation-to-issues"
            unrelated = target_root / "constellation-to-issues-not-legacy"
            foreign = target_root / "foreign-skill"
            legacy.mkdir(parents=True)
            unrelated.mkdir()
            foreign.mkdir()
            self.assertEqual(
                0,
                installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                     "--skills", "to-initial-issues", "--force"],
                    env={}, out=lambda _: None,
                ),
            )
            self.assertFalse(legacy.exists())
            self.assertTrue(unrelated.exists())
            self.assertTrue(foreign.exists())
            self.assertTrue((target_root / "constellation-to-initial-issues" / "SKILL.md").is_file())

    def test_initial_cut_migration_dry_run_never_mutates_legacy_or_installs_canonical(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            legacy = target_root / "constellation-to-issues"
            legacy.mkdir(parents=True)
            marker = legacy / "legacy.txt"
            marker.write_text("unchanged", encoding="utf-8")
            output = []
            self.assertEqual(
                0,
                installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                     "--skills", "to-initial-issues", "--force", "--dry-run"],
                    env={}, out=output.append,
                ),
            )
            self.assertEqual("unchanged", marker.read_text(encoding="utf-8"))
            self.assertFalse((target_root / "constellation-to-initial-issues").exists())
            self.assertIn("constellation-to-issues", "\n".join(output))

    def test_full_force_leaves_exactly_canonical_initial_cut_destination(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            (target_root / "constellation-to-issues").mkdir(parents=True)
            self.assertEqual(
                0,
                installer.main(
                    ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                     "--force"], env={}, out=lambda _: None,
                ),
            )
            self.assertFalse((target_root / "constellation-to-issues").exists())
            self.assertTrue((target_root / "constellation-to-initial-issues").is_dir())

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

    def test_episode_write_path_bundled_into_commander_and_admiral(self):
        # #447: the playbook's apply/verify pair retired; what replaces it is the episode
        # store's WRITE side. The writer is named only in the spine IMPERATIVE (no check
        # runs it), so `test_every_spine_command_names_an_installed_script` below cannot
        # see it -- this per-name pin is what covers that half. The retired trio is
        # asserted ABSENT in the same breath, so a revert shows up here rather than as a
        # mid-run gate failure.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            installer.main(["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                            "--skills", "commander", "admiral"], env={}, out=lambda _: None)
            for skill in ("constellation-commander", "constellation-admiral"):
                scripts_root = target_root / skill / "scripts"
                for script in ("apply_episode_delta.py", "verify_episode_captured.py"):
                    with self.subTest(skill=skill, script=script):
                        self.assertTrue((scripts_root / script).is_file(), scripts_root / script)
                for retired in ("apply_lessons_delta.py", "verify_lessons_applied.py",
                                "verify_agent_feedback.py"):
                    with self.subTest(skill=skill, retired=retired):
                        self.assertFalse((scripts_root / retired).exists(),
                                         f"{skill} still ships the retired {retired}")

    #: Every spine template the installer ships, paired with the skill that serves it.
    #: Derived from the two roles that own a spine rather than globbed, because a spine
    #: only means anything alongside the skill whose scripts/ its commands resolve into.
    SPINE_TEMPLATES = {
        "commander": "COMMANDER_SPINE.template.json",
        "admiral": "ADMIRAL_SPINE.template.json",
    }

    def test_every_spine_command_names_an_installed_script(self):
        # GENERAL, deliberately not per-name. A test that asserts "commander installs
        # verify_episode_captured.py" protects the #447 rewiring and nothing after it; this
        # asserts that NO spine command names a script its own skill does not install, which
        # protects every future rewiring the same way. A spine that names an unshipped script
        # fails mid-run at the gate that needed it, with the run already half-done -- catching
        # it at install time is the whole point.
        #
        # Both condition lists are walked: a precondition command (execute.p2's state-note
        # check) can strand a run exactly as a postcondition command can.
        #
        # Not every command names a script -- archive.c2b shells out to `gh pr list`. A
        # command with no `.py` token is legitimately skipped; the assertion is about the
        # ones that DO name one.
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            exit_code = installer.main(
                ["--agent", "codex", "--scope", "user", "--dest", str(target_root),
                 "--skills", *self.SPINE_TEMPLATES],
                env={}, out=lambda _: None)
            self.assertEqual(0, exit_code)

            checked = 0
            for skill, template in self.SPINE_TEMPLATES.items():
                skill_root = target_root / f"constellation-{skill}"
                spine_path = skill_root / "templates" / template
                self.assertTrue(spine_path.is_file(), spine_path)
                spine = json.loads(spine_path.read_text(encoding="utf-8"))
                for task_id, task in spine["tasks"].items():
                    for which in ("preconditions", "postconditions"):
                        for cond in task.get(which) or ():
                            check = cond.get("check")
                            if not isinstance(check, dict) or check.get("kind") != "command":
                                continue
                            for named in re.findall(r"[\w.\-]+\.py",
                                                    check.get("command", "")):
                                script = Path(named).name
                                checked += 1
                                with self.subTest(skill=skill, task=task_id,
                                                  cond=cond["id"], script=script):
                                    self.assertTrue(
                                        (skill_root / "scripts" / script).is_file(),
                                        f"{skill} spine {task_id}.{cond['id']} runs "
                                        f"{script}, which SKILL_SCRIPT_BUNDLES does not "
                                        f"install into {skill_root / 'scripts'}",
                                    )
            # A loop that reported clean without examining anything is the failure this
            # guard is here to catch, so the count is asserted rather than trusted.
            self.assertGreater(checked, 0, "no spine command named a script -- the walk "
                                           "found nothing to check, which is not a pass")

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
                            "--skills", "explorer", "commander"],
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

            # PRUNED (#447 g4): the move-9 leg asserted "forks its identity" in
            # constellation-lessons-auditor/SKILL.md. That skill tree is deleted by this
            # retirement, so move 9's single home no longer exists and the leg has no
            # subject. Every other move's pin above is untouched and still asserted.

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

    def test_resolve_interpreter_refuses_when_no_candidate_answers(self):
        """#539 owner ruling, replacing the os.name-fallback test.

        Measured on the owner's Windows host: `py` is an extensionless
        `#!/bin/sh` wrapper PowerShell cannot execute, and neither `python3`
        nor `python` is on PATH. All three fail, and the old fallback stamped
        `py` -- the exact thing just proven unlaunchable -- into every
        installed skill body, so the failure surfaced later, elsewhere, with no
        trace back to the cause. It must hard-stop at the cause instead."""
        installer = load_installer()

        def always_fails(cmd, **kwargs):
            raise FileNotFoundError(f"no such candidate: {cmd[0]}")

        with mock.patch.object(installer.subprocess, "run", side_effect=always_fails):
            with self.assertRaises(installer.InstallError) as raised:
                installer.resolve_interpreter()

        message = str(raised.exception)
        # Actionable: names every candidate, says how each was tested, and says
        # what to do about it. A reader on a misconfigured box must not have to
        # read the source to understand this.
        for candidate in installer.INTERPRETER_CANDIDATES:
            self.assertIn(candidate, message)
        self.assertIn("--version", message)
        self.assertIn("PATH", message)

    def test_the_refusal_is_about_no_interpreter_and_not_about_probing_at_all(self):
        """Positive control for the refusal above: with a candidate that DOES
        answer, the same call returns a probed resolution. Without this, a
        `resolve_interpreter` that raised unconditionally would pass the test
        above and nobody would notice."""
        installer = load_installer()

        def only_python3_answers(cmd, **kwargs):
            if cmd[0] == "python3":
                return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")
            raise FileNotFoundError(f"no such candidate: {cmd[0]}")

        with mock.patch.object(installer.subprocess, "run", side_effect=only_python3_answers):
            resolution = installer.resolve_interpreter()
        self.assertEqual("python3", resolution.interpreter)
        self.assertEqual("probe", resolution.resolved_via)

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

    def test_sidecar_records_resolved_via_probe(self):
        # resolved_via sidecar-content correctness. Only "probe" is reachable
        # from an install now -- the os-default-fallback case this test used to
        # cover is gone with the fallback itself (#539 owner ruling). What a
        # sidecar written by an OLDER installer reads back as is covered
        # separately, below, since that is the one remaining producer.
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

    def test_install_refuses_rather_than_writing_a_sidecar_with_no_probe(self):
        """The install path's half of the ruling: no interpreter answering must
        stop the install, not produce a bundle stamped with a guess. Nothing is
        written -- not the skill tree, not a sidecar."""
        installer = load_installer()
        skill = installer.discover_skills()[0]

        def always_fails(cmd, **kwargs):
            raise FileNotFoundError("no such candidate")

        with tempfile.TemporaryDirectory() as tmp:
            target_root = Path(tmp) / "skills"
            with mock.patch.object(installer.subprocess, "run", side_effect=always_fails):
                with self.assertRaises(installer.InstallError):
                    installer.install_skills(
                        [skill], target_root, dry_run=False, force=False,
                        full_set=False, restart_message="", out=lambda _msg: None,
                    )
            self.assertFalse(
                (target_root / skill.install_name / "interpreter.json").exists(),
                "a sidecar was written from an interpreter that never answered",
            )

    def test_resolved_via_still_round_trips_a_historical_fallback_sidecar(self):
        """`resolved_via` keeps its non-probe value in the DATACLASS even though
        the installer can no longer produce one. scripts/verify_installed_bundles.py
        reconstructs an InterpreterResolution from an installed
        `interpreter.json`, and a bundle installed by an older version still
        carries "os-default-fallback" on disk -- reading it back is exactly how
        a consumer learns that bundle was built from the disproved guess and
        should be reinstalled. Dropping the value would blind that check."""
        installer = load_installer()
        resolution = installer.InterpreterResolution(
            "py", installer.INTERPRETER_CANDIDATES, "os-default-fallback")
        self.assertEqual("os-default-fallback", resolution.as_sidecar()["resolved_via"])


def _without_comments(src: str) -> str:
    """`src` with every `#` comment's text blanked out (line/column preserved).

    Mechanism 1 below (`_direct_runtime_siblings`) regex-scans raw text for a
    dynamic-load SHAPE; without this it cannot tell a line of code performing
    a load from a `#`-comment merely describing one elsewhere. `tokenize`
    (not a naive `line.split('#', 1)`) is what makes that distinction safe: a
    `#` inside a string literal is not a comment, and only `tokenize` knows
    the difference."""
    lines = src.splitlines(keepends=True)
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                row, col = tok.start
                line = lines[row - 1]
                trailing = line[len(line.rstrip("\r\n")):]
                lines[row - 1] = line[:col] + trailing
    except (tokenize.TokenizeError, SyntaxError, IndentationError):
        pass
    return "".join(lines)


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

    Mechanism 1's regex scans TEXT, so it has to be run against source with
    comments blanked out (#559 pass 3): `install_constellation.py` merely
    DESCRIBES the engine's and the hook's dynamic loads in a `#`-comment
    (`# checklist_engine._load_gauge_reader() -> Path(__file__).parent/
    "gauge_reader.py"`), and an unfiltered scan misread that prose as
    `install_constellation.py` itself performing the load -- a false sibling
    that then dragged `gauge_reader.py` into every script transitively
    reaching `install_constellation.py`, once this helper was generalized
    beyond the two modules whose own source happened to carry no such
    commentary about itself.
    """
    src = module_path.read_text(encoding="utf-8")
    names = set(re.findall(r'parent\s*/\s*"([A-Za-z0-9_]+\.py)"', _without_comments(src)))
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


class CompanionGuardCoversEveryScriptTests(unittest.TestCase):
    """#559 pass 3: the guard above (`test_engine_runtime_siblings_are_declared_
    as_companions`) reads `SCRIPT_RUNTIME_COMPANIONS.get('checklist_engine.py', ())`
    -- a LITERAL, so it watches exactly one script. `gauge_writer_hook.py` got its
    own, separately hand-written copy of the same check. Neither generalizes, so
    when `run_crew.py` grew a bare module-scope `import install_constellation`
    (#539's `assert_shell_safe_command`), the exact defect class this dict exists
    to catch (a bundled script's runtime sibling shipping nowhere) recurred one
    file over from where it is documented (`SCRIPT_RUNTIME_COMPANIONS` above), and
    the suite stayed green: no test ever looked at `run_crew.py`. Every installed
    Commander/Explorer bundle raised `ModuleNotFoundError` at import, before
    argparse ever ran.

    This test keys on every script actually bundled by any skill (derived from
    `SKILL_SCRIPT_BUNDLES`, not a hand-picked name), and requires that whatever a
    script reaches at runtime lands in the SAME skill's expanded bundle --
    whether that arrival is via a declared `SCRIPT_RUNTIME_COMPANIONS` entry (the
    mechanism the neighbour import needed) or an explicit hand-listed sibling
    already sharing the bundle (the mechanism `checklist_engine.py` already used,
    correctly, before this pass). Either is a real ship; only an absence is a bug."""

    SCRIPTS_ROOT = ROOT / "scripts"

    def test_every_bundled_script_ships_its_runtime_closure(self):
        installer = load_installer()
        bundled_scripts = sorted({
            script
            for scripts in installer.SKILL_SCRIPT_BUNDLES.values()
            for script in scripts
        })
        self.assertTrue(bundled_scripts, "no skill bundles any script?")
        checked = 0
        for name, scripts in installer.SKILL_SCRIPT_BUNDLES.items():
            expanded = set(installer.expand_script_bundle(scripts))
            for script in scripts:
                # `_direct_runtime_siblings`/`engine_runtime_closure` read
                # source and resolve sibling existence directly under
                # `scripts_root`, so they only see the FLAT layout most
                # scripts live in. A script whose source is a subdirectory
                # (`SCRIPT_SOURCE_SUBDIRS`, today just the hook pair) is
                # covered by its own dedicated, layout-aware check in
                # `HookScriptBundleTests` below instead of being silently
                # skipped as "no runtime siblings".
                if script in installer.SCRIPT_SOURCE_SUBDIRS:
                    continue
                reachable = engine_runtime_closure(script, self.SCRIPTS_ROOT)
                if not reachable:
                    continue
                checked += 1
                missing = reachable - expanded
                with self.subTest(skill=name, script=script):
                    self.assertEqual(
                        set(), missing,
                        f"{script!r} (bundled by skill {name!r}) reaches "
                        f"{sorted(missing)} at runtime, but that skill's expanded "
                        f"bundle does not ship {sorted(missing)} -- installed, "
                        f"{script!r}'s import of it fails",
                    )
        self.assertGreater(
            checked, 0,
            "no bundled script reached any local sibling at runtime -- this test "
            "would pass vacuously; the fixture premise (run_crew.py -> "
            "install_constellation.py, checklist_engine.py -> gauge_reader.py) "
            "changed",
        )


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
    # #600: the writer also loads the READER, for `owner_key` -- the one
    # definition of the name a gauge file carries. Its source sits in scripts/
    # rather than scripts/hooks/, but the install destination is FLAT, so in an
    # install it lands beside the writer like the rail does.
    READER = "gauge_reader.py"
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

    def test_installed_gauge_writer_hook_actually_loads_its_gauge_reader(self):
        """The #600 counterpart, and it is not ceremony: the writer's source
        lives in `scripts/hooks/` and the reader's in `scripts/`, so the loader
        has to find the reader ONE LEVEL UP in this checkout and BESIDE ITSELF in
        a flat install. A loader written for only the checkout layout passes
        every test that runs from a checkout and fails in every install --
        silently, into no owner, which would leave the writer producing
        `gauge.json` while a leased engine reads `gauge-<owner>.json`. That is a
        DARK governor, not merely an inert one, and only an installed-layout
        test can see it."""
        with tempfile.TemporaryDirectory() as tmp:
            scripts_dir = self._install_owner_skill(tmp)
            self.assertTrue((scripts_dir / self.READER).is_file())
            mod = load_module("installed_gauge_writer_hook_reader",
                              scripts_dir / self.WRITER)
            self.assertIsNotNone(
                mod._gauge_reader,
                "installed gauge writer hook could not load gauge_reader.py -- "
                "it would resolve no owner and write the unowned gauge.json "
                "where a leased engine reads an owner-keyed name, silently",
            )
            # and the loaded module is really the one that defines the key
            self.assertEqual(mod._owner_key("eng-1"), "eng-1-cf2640ffe69e")

    def test_gauge_writer_hook_dynamic_loads_are_declared_as_companions(self):
        """Parse the writer's source for `parent / "<name>.py"` sibling loads and
        require each to be declared. Mirrors the engine's companion test so a NEW
        dynamic load cannot be added without a matching bundle entry."""
        installer = load_installer()
        source = (self.HOOK_SOURCE_DIR / self.WRITER).read_text(encoding="utf-8")
        siblings = set(re.findall(r'parent\s*/\s*"([A-Za-z0-9_]+\.py)"', source))
        self.assertEqual(
            {self.RAIL, self.READER}, siblings,
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
            self.assertIn("WORKFLOW_CLOSEOUT.template.md", names)

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
                           / "WORKFLOW_CLOSEOUT.template.md").read_text(encoding="utf-8")

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
                (troot / ".baseline" / "constellation-workbench" / "WORKFLOW_CLOSEOUT.template.md")
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
            closeout_wc = troot / "WORKFLOW_CLOSEOUT.template.md"
            self.assertTrue(closeout_wc.is_file())  # fresh install seeded it
            closeout_wc.unlink()  # project opts out of tracking it locally

            installer.main(args, env={}, cwd=project, out=lambda _l: None)  # reinstall
            self.assertFalse(closeout_wc.exists())  # not backfilled (already tracked)

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


# --------------------------------------------------------------------------- #
# all four hooks, source-tree wiring, and loud refusal (#539)
# --------------------------------------------------------------------------- #
class _MultiHookFixture(_HookWiringFixture):
    """Adds helpers for the four-hook world on top of the governor fixture."""

    def _settings_json(self, tmp, name="settings.json") -> dict:
        return json.loads((Path(tmp) / name).read_text(encoding="utf-8"))

    def _all_commands(self, settings: dict) -> dict:
        """{(event, matcher, script): (command, timeout)} for every hook."""
        found = {}
        for event, entries in settings.get("hooks", {}).items():
            for entry in entries:
                for hook in entry["hooks"]:
                    command = hook["command"]
                    script = Path(command.split('"')[1]).name
                    found[(event, entry.get("matcher"), script)] = (command, hook.get("timeout"))
        return found


class AllFourHookWiringTests(_MultiHookFixture):
    """#539 gap 2: `--wire-hooks` could only ever write the PostToolUse gauge
    writer. The three spine_rail.py events -- Stop, SessionStart and a second
    PostToolUse -- had no representation in the installer at all, so neither
    wiring nor detection could see them.

    `--hooks governor` remains the default and remains byte-for-byte what the
    flag did before, because the rail can BLOCK a Stop and must not arrive in
    somebody's settings.json as a side effect of an install they already knew
    how to run."""

    def test_default_wire_hooks_still_writes_only_the_governor(self):
        """The unchanged contract, asserted rather than assumed."""
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks")
            settings = self._settings_json(tmp)
            self.assertEqual(["PostToolUse"], list(settings["hooks"]))
            self.assertEqual(1, len(settings["hooks"]["PostToolUse"]))

    def test_hooks_all_writes_every_spec_with_its_own_event_matcher_and_timeout(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all")
            written = self._all_commands(self._settings_json(tmp))
            self.assertEqual(
                len(installer.HOOK_SPECS), len(written),
                f"expected one entry per spec, got {sorted(written)}",
            )
            for spec in installer.HOOK_SPECS:
                key = (spec.event, spec.matcher, spec.script)
                self.assertIn(key, written, f"{spec.name} was not wired")
                command, timeout = written[key]
                self.assertEqual(spec.timeout, timeout, spec.name)
                # The event argument distinguishes the three rail entries from
                # each other; without it all three would invoke the same
                # handler and two of the three events would be dead.
                self.assertTrue(
                    command.endswith(" ".join(("", *spec.args)).rstrip()) if spec.args
                    else command.endswith('"'),
                    f"{spec.name}: args not appended: {command!r}",
                )

    def test_hooks_rail_writes_the_three_rail_events_and_no_governor(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "rail")
            written = self._all_commands(self._settings_json(tmp))
            self.assertEqual(
                {(s.event, s.matcher, s.script) for s in installer.SPINE_RAIL_SPECS},
                set(written),
            )

    def test_every_wired_command_actually_executes(self):
        """Run each generated command EXACTLY as Claude Code would -- same
        string, stdin JSON -- and require more than exit 0: exit 0 is also
        what an INERT hook produces. scripts/hooks/spine_rail.py fail-opens
        (prints nothing, returns 0) for any event it does not recognize, so a
        wrong event argument -- or a lost quote that shifts which positional
        argument lands where -- is invisible to a returncode-only assertion.
        The three spine_rail.py-backed entries (Stop, SessionStart,
        PostToolUse) are instead run against a REAL mid-flight project state
        and their actual stdout/side-effect is asserted. The governor
        (gauge_writer_hook.py) entry keeps the returncode-only check: it takes
        no positional event argument at all (HOOK_TIMEOUT/HOOK_MATCHER, no
        `args`), so a wrong event argument is not a failure mode it has."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all")
            written = self._all_commands(self._settings_json(tmp))
            self.assertEqual(
                len(installer.HOOK_SPECS), len(written), "nothing was wired, so nothing was run"
            )

            # A real project dir carrying a MID-FLIGHT spine (an in-progress
            # gate under an active lease) plus a binding for it under
            # session_id "resume-sid" -- the state Stop/SessionStart actually
            # act on.
            project_dir = Path(tmp) / "project"
            run_dir = project_dir / ".agent-work" / "run1"
            run_dir.mkdir(parents=True)
            spine_path = run_dir / "spine.json"
            spine_path.write_text(json.dumps({
                "items": ["m1"],
                "tasks": {"m1": {"id": "m1", "status": "in-progress", "imperative": "do m1"}},
                "engine_session": {
                    "session_id": "eng-1", "status": "active",
                    "claimed_by": "commander", "last_heartbeat": "2026-07-12T00:00:00+00:00",
                },
            }), encoding="utf-8", newline="\n")
            binding_path = project_dir / ".agent-work" / ".spine-rail-binding.json"
            binding_path.write_text(json.dumps({
                "resume-sid": {
                    str(spine_path): {
                        "spine": str(spine_path), "engine_session": "eng-1",
                        "worktree": str(project_dir), "claimed_at": "2026-07-27T00:00:00+00:00",
                    },
                },
            }), encoding="utf-8", newline="\n")

            env = {**os.environ, "PYTHONIOENCODING": "utf-8", "CLAUDE_PROJECT_DIR": str(project_dir)}

            def run(command, stdin_payload):
                return subprocess.run(
                    command, shell=True, input=json.dumps(stdin_payload),
                    capture_output=True, text=True, env=env,
                )

            for (event, matcher, script), (command, _timeout) in written.items():
                if script == installer.SPINE_RAIL_HOOK_SCRIPT and event == "Stop":
                    result = run(command, {"session_id": "resume-sid"})
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(
                        "SPINE MID-FLIGHT", result.stdout,
                        f"Stop against a genuinely mid-flight spine produced no block -- "
                        f"a wrong event argument would be invisible here: {command!r}\n"
                        f"stdout={result.stdout!r} stderr={result.stderr!r}",
                    )
                elif script == installer.SPINE_RAIL_HOOK_SCRIPT and event == "SessionStart":
                    result = run(command, {"session_id": "resume-sid"})
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(
                        "RESUMING", result.stdout,
                        f"SessionStart against an active spine produced no resume "
                        f"context -- a wrong event argument would be invisible here: "
                        f"{command!r}\nstdout={result.stdout!r} stderr={result.stderr!r}",
                    )
                elif script == installer.SPINE_RAIL_HOOK_SCRIPT and event == "PostToolUse":
                    claim_cmd = (
                        f'python checklist_engine.py --file "{spine_path}" '
                        f'claim --session-id eng-9'
                    )
                    result = run(command, {
                        "session_id": "claim-sid",
                        "tool_input": {"command": claim_cmd},
                    })
                    self.assertEqual(0, result.returncode, result.stderr)
                    written_binding = json.loads(binding_path.read_text(encoding="utf-8"))
                    self.assertIn(
                        "claim-sid", written_binding,
                        f"PostToolUse against a claim command wrote no binding -- a "
                        f"wrong event argument would be invisible here: {command!r}\n"
                        f"stdout={result.stdout!r} stderr={result.stderr!r}",
                    )
                    self.assertEqual(
                        str(spine_path),
                        written_binding["claim-sid"].get(str(spine_path), {}).get("spine"),
                        "PostToolUse recorded the wrong spine path for the claim",
                    )
                else:
                    result = run(command, {})
                    self.assertEqual(
                        0, result.returncode,
                        f"the wired command did not run: {command!r}\n"
                        f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
                    )

    def test_all_four_wired_then_detect_as_wired(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all")
            wiring = installer.detect_hook_wiring(
                self._settings(tmp), env={}, specs=installer.HOOK_SPECS)
            self.assertEqual(installer.WIRING_WIRED, wiring.state)
            self.assertEqual((), wiring.missing)

    def test_three_of_four_reads_as_partial_and_names_the_missing_hook(self):
        """THE new reassuring-failure shape, one level up from `stale`: before
        #539 a single resolvable entry made the whole verdict `wired`, so three
        missing hooks out of four would have read as fully wired."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all")
            settings = self._settings_json(tmp)
            del settings["hooks"]["Stop"]
            self._write_settings(tmp, settings)
            wiring = installer.detect_hook_wiring(
                self._settings(tmp), env={}, specs=installer.HOOK_SPECS)
            self.assertEqual(installer.WIRING_PARTIAL, wiring.state)
            self.assertEqual(("spine_rail_stop",), wiring.missing)
            line = installer.describe_hook_wiring(wiring)
            self.assertIn("PARTIALLY WIRED", line)
            self.assertIn("spine_rail_stop", line)

    def test_partial_is_unreachable_for_a_single_spec(self):
        """Anti-vacuity for the state above: with one spec there is nothing to
        be partial about, which is why the governor-only default keeps exactly
        its pre-#539 four-state behaviour."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry(f'py "{hook.as_posix()}"')]}})
            wiring = installer.detect_hook_wiring(path, env={})
            self.assertEqual(installer.WIRING_WIRED, wiring.state)

    def test_detection_of_an_exec_form_entry_is_not_a_false_unwired(self):
        """We never emit exec form, but a hand-written one is real. Reading it
        as "no hook here" would be a silent false negative in the one detector
        that exists to catch silence."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            path = self._write_settings(tmp, {"hooks": {"PostToolUse": [
                {"matcher": "*", "hooks": [{
                    "type": "command", "command": "python3",
                    "args": [hook.as_posix()], "timeout": 10}]}]}})
            self.assertEqual(
                installer.WIRING_WIRED, installer.detect_hook_wiring(path, env={}).state)


class SourceTreeHookWiringTests(_MultiHookFixture):
    """#539 gap 1: `hook_command()` pinned an absolute INSTALLED path by
    construction, so the one repo whose hooks it could not wire was the repo
    that owns them. `--hooks-from source` points at this checkout's own
    scripts/hooks/ instead.

    It writes settings.local.json, not settings.json, and that is not a
    preference: a source command carries this checkout's absolute path AND an
    interpreter probed on this host, so it is wrong for every other machine by
    construction."""

    def test_source_wiring_points_at_this_checkouts_own_hook_scripts(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all", "--hooks-from", "source")
            written = self._all_commands(self._settings_json(tmp, "settings.local.json"))
            self.assertEqual(len(installer.HOOK_SPECS), len(written))
            for (_event, _matcher, script), (command, _timeout) in written.items():
                expected = installer.source_hook_path(script)
                self.assertTrue(
                    expected.is_file(), f"wired a path with no file behind it: {expected}")
                self.assertIn(expected.as_posix(), command)
                self.assertNotIn("${CLAUDE_PROJECT_DIR}", command)

    def test_source_wiring_writes_the_local_file_and_never_the_shared_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all", "--hooks-from", "source")
            self.assertTrue((Path(tmp) / "settings.local.json").is_file())
            self.assertFalse(
                self._settings(tmp).exists(),
                "source wiring created the SHARED settings.json, which every "
                "contributor reads unmodified",
            )

    def test_source_wiring_leaves_an_existing_shared_settings_json_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared = self._write_settings(tmp, {"hooks": {"PostToolUse": [self._entry(
                '"${CLAUDE_PROJECT_DIR}/scripts/hooks/gauge_writer_hook.py"')]}})
            before = shared.read_bytes()
            self._run(tmp, "--wire-hooks", "--hooks", "all", "--hooks-from", "source")
            self.assertEqual(before, shared.read_bytes())

    def test_the_source_wired_commands_actually_execute(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp, "--wire-hooks", "--hooks", "all", "--hooks-from", "source")
            commands = [
                c for c, _ in
                self._all_commands(self._settings_json(tmp, "settings.local.json")).values()
            ]
            self.assertEqual(
                len(installer.HOOK_SPECS), len(commands), "nothing was wired, so nothing was run"
            )
            for command in commands:
                result = subprocess.run(
                    command, shell=True, input="{}", capture_output=True, text=True,
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
                self.assertEqual(
                    0, result.returncode,
                    f"the source-wired command did not run: {command!r}\n"
                    f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
                )

    def test_source_wiring_does_not_need_the_workbench_skill_installed(self):
        """The installed-copy precondition is about the install; source wiring
        points somewhere else entirely, so requiring it would be refusing on a
        ground that does not apply."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(self._dest(tmp)),
                 "--skills", "charter", "--wire-hooks", "--hooks-from", "source"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, code)
            self.assertTrue((Path(tmp) / "settings.local.json").is_file())

    def test_source_wiring_refuses_a_git_tracked_local_settings_file(self):
        """Committing it hands every teammate a path that does not exist on
        their machine, and an interpreter name that may not either."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=str(repo), capture_output=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"],
                           cwd=str(repo), capture_output=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=str(repo), capture_output=True)
            local = repo / "settings.local.json"
            local.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "add", "settings.local.json"], cwd=str(repo), capture_output=True)
            subprocess.run(["git", "commit", "-qm", "x"], cwd=str(repo), capture_output=True)
            before = local.read_bytes()

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "user", "--dest", str(self._dest(tmp)),
                         "--skills", self.OWNER_SKILL, "--wire-hooks", "--hooks-from", "source"],
                        env={}, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)
            self.assertIn("git-tracked", stderr.getvalue())
            self.assertEqual(before, local.read_bytes(), "the tracked file was written anyway")

    def test_the_same_run_succeeds_when_the_local_file_is_untracked(self):
        """Anti-vacuity for the refusal above: it must be about TRACKEDNESS,
        not about source mode refusing everything in a git repo."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=str(repo), capture_output=True)
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(self._dest(tmp)),
                 "--skills", self.OWNER_SKILL, "--wire-hooks", "--hooks-from", "source"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, code)
            self.assertTrue((repo / "settings.local.json").is_file())


class HookWiringLoudFailureTests(_MultiHookFixture):
    """#539's fourth requirement: whatever ships must fail LOUDLY on a platform
    it cannot serve. Silent success is the failure mode the whole issue exists
    to kill -- a hook that exits 0 without running is worse than one that
    errors, because nothing anywhere can report it."""

    def _fallback(self, installer):
        """A resolution that was never probed on this host. Since #539's owner
        ruling `resolve_interpreter()` refuses rather than returning one of
        these, so the remaining producer is verify_installed_bundles.py reading
        an `interpreter.json` written by an older installer -- which legitimately
        still carries "os-default-fallback"."""
        return installer.InterpreterResolution(
            "py", installer.INTERPRETER_CANDIDATES, "os-default-fallback")

    def _probed(self, installer):
        return installer.InterpreterResolution(
            sys.executable, installer.INTERPRETER_CANDIDATES, "probe")

    def test_wire_hooks_refuses_an_unprobed_interpreter_resolution(self):
        """Defense in depth on a public function. The CLI can no longer reach
        this (`resolve_interpreter` refuses one level up), but a resolution
        rebuilt from an old bundle's sidecar still can."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp)  # install the owner skill, wire nothing
            with self.assertRaises(installer.InstallError) as raised:
                installer.wire_hooks(
                    self._dest(tmp), interpreter=self._fallback(installer),
                    dry_run=False, scope="user", out=lambda _: None,
                )
            message = str(raised.exception)
            self.assertIn("not probed on this host", message)
            self.assertIn("os-default-fallback", message)
            self.assertFalse(
                self._settings(tmp).exists(),
                "refused loudly but wrote the unrunnable wiring anyway",
            )

    def test_the_same_call_succeeds_on_a_probed_interpreter(self):
        """Anti-vacuity: the refusal above must be about the FALLBACK, not
        about wire_hooks refusing every direct call."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp)
            installer.wire_hooks(
                self._dest(tmp), interpreter=self._probed(installer),
                dry_run=False, scope="user", out=lambda _: None,
            )
            self.assertTrue(self._settings(tmp).is_file())

    def test_the_fallback_refusal_also_fires_under_dry_run(self):
        """A dry run that printed a command the host cannot run would be
        telling the user the wiring is fine when it is not."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._run(tmp)
            with self.assertRaises(installer.InstallError):
                installer.wire_hooks(
                    self._dest(tmp), interpreter=self._fallback(installer),
                    dry_run=True, scope="user", out=lambda _: None,
                )

    def test_source_wiring_refuses_a_checkout_with_no_hook_scripts(self):
        """`--hooks-from source` only means something in a checkout that owns
        scripts/hooks/. Pointing it at a tree without them must refuse, not
        wire a path with nothing behind it."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            original = installer.source_hook_path
            installer.source_hook_path = lambda script, repo_root=None: (
                Path(tmp) / "no-such-checkout" / "scripts" / "hooks" / script)
            try:
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as raised:
                        installer.main(
                            ["--agent", "claude", "--scope", "user",
                             "--dest", str(self._dest(tmp)), "--skills", self.OWNER_SKILL,
                             "--wire-hooks", "--hooks-from", "source"],
                            env={}, out=lambda _: None,
                        )
                self.assertNotEqual(0, raised.exception.code)
                self.assertIn("no hook script", stderr.getvalue())
            finally:
                installer.source_hook_path = original
            self.assertFalse((Path(tmp) / "settings.local.json").exists())

    def test_build_hook_command_refuses_to_emit_a_leading_quote(self):
        """The trap this whole issue is named for, made unrepresentable at the
        emit site: a command starting with `"` parses under PowerShell as a
        string-literal expression, so the hook echoes its path and exits 0."""
        installer = load_installer()
        with self.assertRaises(installer.InstallError) as raised:
            installer.build_hook_command(Path("/repo/scripts/hooks/spine_rail.py"), "", ("Stop",))
        self.assertIn("does not start with a command word", str(raised.exception))


# --------------------------------------------------------------------------- #
# readiness check (#458) -- report-only, refuses when unready, never repairs
# --------------------------------------------------------------------------- #
class ReadinessEngineCheckTests(unittest.TestCase):
    """check_engine_runnable: readiness item 1, engine present and runnable.

    Must distinguish interpreter-missing from pytest-missing from
    both-present-and-working -- a bare launch success is NOT proof pytest
    actually runs. `py` on a real box exits nonzero with 'No module named
    pytest' and reads exactly like a red suite if only a launch is checked."""

    def test_check_engine_runnable_ready_when_pytest_runs_under_the_interpreter(self):
        installer = load_installer()
        result = installer.check_engine_runnable(python=sys.executable)
        self.assertTrue(result.ready)
        self.assertIn(sys.executable, result.reason)

    def test_check_engine_runnable_not_ready_when_interpreter_missing(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "no-such-interpreter")
            result = installer.check_engine_runnable(python=missing)
        self.assertFalse(result.ready)
        self.assertIn(missing, result.reason)
        self.assertNotIn("pytest", result.reason.lower())

    def test_check_engine_runnable_not_ready_when_pytest_missing(self):
        """The discriminating case named in the handoff: a launch that exits
        nonzero because pytest is not importable must read as pytest-missing,
        not interpreter-missing, and must never be reported as ready."""
        installer = load_installer()

        def fake_run(cmd, **kwargs):
            self.assertEqual([sys.executable, "-m", "pytest", "--version"], cmd)
            return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="No module named pytest")

        with mock.patch.object(installer.subprocess, "run", side_effect=fake_run):
            result = installer.check_engine_runnable(python=sys.executable)
        self.assertFalse(result.ready)
        self.assertIn("pytest", result.reason.lower())

    def test_check_engine_runnable_uses_the_given_interpreter_not_a_bare_launcher(self):
        """Regression guard: argv must be [<python>, '-m', 'pytest', ...], never
        a bare 'python'/'py' token standing in for the interpreter."""
        installer = load_installer()
        seen = {}

        def fake_run(cmd, **kwargs):
            seen["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, 0, stdout="pytest 8.0.0\n", stderr="")

        with mock.patch.object(installer.subprocess, "run", side_effect=fake_run):
            installer.check_engine_runnable(python=sys.executable)
        self.assertEqual(sys.executable, seen["cmd"][0])


class ReadinessWorkAreaCheckTests(unittest.TestCase):
    """check_work_area_present: readiness item 4, work area present
    (tree-scoped). README.md's own Baseline Assumptions: 'a Git repo, Markdown
    docs, and file-based workflow state'. Must NOT require .agent-work/ to
    already exist -- a project ready to START using Constellation has not
    necessarily run it yet."""

    def test_check_work_area_present_ready_with_a_git_directory(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".git").mkdir()
            result = installer.check_work_area_present(project)
        self.assertTrue(result.ready)

    def test_check_work_area_present_ready_with_a_git_worktree_file_pointer(self):
        """A git worktree's `.git` is a FILE, not a directory -- this very
        worktree is the proof case for that shape."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".git").write_text("gitdir: /elsewhere/.git/worktrees/x\n", encoding="utf-8")
            result = installer.check_work_area_present(project)
        self.assertTrue(result.ready)

    def test_check_work_area_present_not_ready_with_no_git_entry(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            result = installer.check_work_area_present(Path(tmp))
        self.assertFalse(result.ready)
        self.assertIn(str(Path(tmp)), result.reason)

    def test_check_work_area_present_does_not_require_agent_work_dir(self):
        """A project that has never run Constellation still has no .agent-work/
        -- that must not count against readiness."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".git").mkdir()
            self.assertFalse((project / ".agent-work").exists())
            result = installer.check_work_area_present(project)
        self.assertTrue(result.ready)


class ReadinessSkillsCheckTests(unittest.TestCase):
    """check_skills_installed: readiness item 2, skills installed and
    registered (tree/target-scoped). Decision point resolved here: the
    readiness mode reuses --agent/--scope (via the same target_root install
    itself computes) rather than standing scope-agnostic -- "installed" is
    inherently target-specific, so `expected_skills` matches what a real
    --agent/--scope/--skills combination would have installed."""

    def test_check_skills_installed_not_ready_when_target_root_missing(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"  # never created
            result = installer.check_skills_installed(target)
        self.assertFalse(result.ready)

    def test_check_skills_installed_not_ready_without_corpus_marker(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            target.mkdir()
            (target / "constellation-workbench").mkdir()  # skill dir with no CORPUS.json
            result = installer.check_skills_installed(target)
        self.assertFalse(result.ready)
        self.assertIn("CORPUS.json", result.reason)

    def test_check_skills_installed_not_ready_when_an_expected_skill_is_missing(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            target.mkdir()
            (target / "constellation-workbench").mkdir()
            (target / "CORPUS.json").write_text("{}", encoding="utf-8")
            result = installer.check_skills_installed(
                target, expected_skills=["constellation-workbench", "constellation-implementer"])
        self.assertFalse(result.ready)
        self.assertIn("constellation-implementer", result.reason)

    def test_check_skills_installed_ready_when_corpus_and_expected_skills_present(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            target.mkdir()
            (target / "constellation-workbench").mkdir()
            (target / "constellation-implementer").mkdir()
            (target / "CORPUS.json").write_text("{}", encoding="utf-8")
            result = installer.check_skills_installed(
                target, expected_skills=["constellation-workbench", "constellation-implementer"])
        self.assertTrue(result.ready)

    def test_check_skills_installed_ready_with_no_expected_skills_given(self):
        """expected_skills=None -- any installed corpus counts, matching a
        scope-agnostic caller that hasn't resolved a skill set yet."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            target.mkdir()
            (target / "constellation-workbench").mkdir()
            (target / "CORPUS.json").write_text("{}", encoding="utf-8")
            result = installer.check_skills_installed(target)
        self.assertTrue(result.ready)


class ReadinessHooksCheckTests(_HookWiringFixture):
    """is_git_tracked + check_hooks_shippable: readiness item 3, hooks wired in
    a file that ships. Reuses detect_hook_wiring/describe_hook_wiring rather
    than re-deriving wiring detection. Two DISTINCT ships-tests: project scope
    requires git-tracked membership (`git ls-files`) -- presence on disk alone
    is not enough, since a gitignored settings.local.json can be WIRED while
    the tracked settings.json is not; user scope has no tracked/untracked axis
    at all, so WIRED alone is sufficient there."""

    def _git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)

    def _init_repo(self, repo_root):
        self._git(repo_root, "init", "-q")
        self._git(repo_root, "config", "user.email", "test@example.com")
        self._git(repo_root, "config", "user.name", "Test")

    def _project_dest(self, repo_root) -> Path:
        return repo_root / ".claude" / "skills"

    # -- is_git_tracked -------------------------------------------------------

    def test_is_git_tracked_true_for_a_committed_file(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._init_repo(tmp)
            path = Path(tmp) / "settings.json"
            path.write_text("{}", encoding="utf-8")
            self._git(tmp, "add", "settings.json")
            self._git(tmp, "commit", "-q", "-m", "init")
            self.assertTrue(installer.is_git_tracked(path))

    def test_is_git_tracked_false_for_an_untracked_file(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._init_repo(tmp)
            path = Path(tmp) / "settings.local.json"
            path.write_text("{}", encoding="utf-8")  # never `git add`ed
            self.assertFalse(installer.is_git_tracked(path))

    def test_is_git_tracked_false_outside_any_repo(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text("{}", encoding="utf-8")
            self.assertFalse(installer.is_git_tracked(path))

    def test_is_git_tracked_true_for_a_relative_path_from_the_repo_root(self):
        """`--project .` hands `is_git_tracked` a RELATIVE path whose parent is a
        subdirectory (e.g. `.claude/settings.local.json`, parent `.claude`).
        `cwd=path.parent` for a RELATIVE path resolves that parent against the
        process's real cwd, and git then evaluates the RELATIVE pathspec against
        THAT cwd too -- doubling the parent segment (`.claude/.claude/...`), so a
        tracked file reads as untracked. The answer must not depend on whether
        the caller passed a relative or an absolute path."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            self._init_repo(repo_root)
            sub = repo_root / ".claude"
            sub.mkdir()
            path = sub / "settings.local.json"
            path.write_text("{}", encoding="utf-8")
            self._git(repo_root, "add", ".claude/settings.local.json")
            self._git(repo_root, "commit", "-q", "-m", "init")
            real_cwd = os.getcwd()
            os.chdir(repo_root)
            try:
                relative = Path(".claude") / "settings.local.json"
                self.assertTrue(installer.is_git_tracked(relative))
            finally:
                os.chdir(real_cwd)

    def test_is_git_tracked_true_for_a_tracked_symlink_pointing_outside_the_repo(self):
        """The absolutizing fix must NOT follow symlinks. A git-tracked symlink
        (mode 120000) whose target lives outside the repo resolves, under
        `Path.resolve()`, to a path git knows nothing about -- so a tracked file
        reads as untracked and the installer writes machine-specific wiring
        straight THROUGH the link into whatever repo owns the target, with no
        `git status` signal in this one. That is the same false negative the
        relative-path fix above exists to close, in a narrower shape."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "dotfiles"
            outside.mkdir()
            target = outside / "settings.local.json"
            target.write_text("{}", encoding="utf-8", newline="\n")

            repo_root = Path(tmp) / "project"
            repo_root.mkdir()
            self._init_repo(repo_root)
            sub = repo_root / ".claude"
            sub.mkdir()
            link = sub / "settings.local.json"
            link.symlink_to(target)
            self._git(repo_root, "add", ".claude/settings.local.json")
            self._git(repo_root, "commit", "-q", "-m", "init")

            mode = self._git(repo_root, "ls-files", "-s", ".claude/settings.local.json").stdout
            self.assertTrue(
                mode.startswith("120000"),
                f"fixture is not a tracked symlink, so this test proves nothing: {mode!r}",
            )
            self.assertTrue(installer.is_git_tracked(link))

    def test_is_git_tracked_never_raises_on_a_symlink_loop(self):
        """The docstring promises any git failure reads as untracked and never
        raises. `Path.resolve()` breaks that promise -- it walks the filesystem
        and raises RuntimeError on a symlink loop, which is outside the caught
        (OSError, TimeoutExpired) set and escapes as an unhandled traceback."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            a.symlink_to(b)
            b.symlink_to(a)
            self.assertFalse(installer.is_git_tracked(a / "settings.json"))

    # -- check_hooks_shippable --------------------------------------------------

    def test_check_hooks_shippable_not_ready_when_unwired(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._init_repo(tmp)
            result = installer.check_hooks_shippable(self._dest(tmp), scope="project", env={})
        self.assertFalse(result.ready)

    def test_check_hooks_shippable_project_scope_not_ready_when_wired_but_untracked(self):
        """The load-bearing case: settings.json is WIRED on disk but was never
        `git add`ed -- must read as NOT ready, not silently pass."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            self._init_repo(repo_root)
            hook = self._fake_hook_file(tmp)
            dest = self._project_dest(repo_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            (dest.parent / "settings.json").write_text(
                json.dumps({"hooks": {"PostToolUse": [
                    self._entry(f'py "{hook.as_posix()}"')]}}), encoding="utf-8")
            # deliberately never `git add`ed
            result = installer.check_hooks_shippable(dest, scope="project", env={})
        self.assertFalse(result.ready)
        self.assertIn("track", result.reason.lower())

    def test_check_hooks_shippable_project_scope_ready_when_wired_and_tracked(self):
        """Mirrors the real install layout: .git lives at the project root, but
        settings.json lives one level down under .claude/ -- git must still
        resolve tracked-ness from that nested cwd."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            self._init_repo(repo_root)
            hook = self._fake_hook_file(tmp)
            dest = self._project_dest(repo_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            (dest.parent / "settings.json").write_text(
                json.dumps({"hooks": {"PostToolUse": [
                    self._entry(f'py "{hook.as_posix()}"')]}}), encoding="utf-8")
            self._git(repo_root, "add", ".claude/settings.json")
            self._git(repo_root, "commit", "-q", "-m", "wire hooks")
            result = installer.check_hooks_shippable(dest, scope="project", env={})
        self.assertTrue(result.ready)

    def test_check_hooks_shippable_user_scope_ready_when_wired_with_no_git_repo_at_all(self):
        """User scope has no tracked/untracked axis -- WIRED alone is enough,
        even with no git repo present at all (~/.claude/settings.json is never
        part of a repo)."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            hook = self._fake_hook_file(tmp)
            self._write_settings(tmp, {"hooks": {"PostToolUse": [
                self._entry(f'py "{hook.as_posix()}"')]}})
            result = installer.check_hooks_shippable(self._dest(tmp), scope="user", env={})
        self.assertTrue(result.ready)


class ReadinessTriStateTests(_MultiHookFixture):
    """#539 requirement 3: `--check-readiness` must distinguish NOT WIRED YET
    from WIRED WRONG, and must not launder an honest "I cannot tell" into
    either a pass or a fail.

    The pre-existing CANNOT EVALUATE behaviour is RIGHT and is preserved: the
    detector refuses to expand `${CLAUDE_PROJECT_DIR}` because it would be
    expanded in the installer's process, not the future hook's. What was wrong
    was the ROLL-UP -- a two-state report had nowhere to put that answer, so a
    correctly wired repo read as defective."""

    def _wire_by_hand(self, tmp, command):
        return self._write_settings(tmp, {"hooks": {"PostToolUse": [self._entry(command)]}})

    @staticmethod
    def _report(installer, **overrides):
        """A ReadinessReport with every item READY except the named overrides.

        Built from `READINESS_ITEMS` rather than a hard-coded key list so a new
        readiness item cannot silently leave these roll-up tests exercising a
        report shape the production code no longer builds."""
        checks = {name: installer.ReadinessCheck(True, "ok") for name in installer.READINESS_ITEMS}
        for name, check in overrides.items():
            assert name in checks, f"{name} is not a readiness item"
            checks[name] = check
        return installer.ReadinessReport(checks)

    def test_a_correctly_wired_env_token_entry_is_undeterminable_not_not_ready(self):
        """The exact reported defect: this settings.json is healthy, and the
        installer cannot prove it from here. Neither confirmed nor condemned."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._wire_by_hand(tmp, 'py "${CLAUDE_PROJECT_DIR}/' + self.WRITER + '"')
            check = installer.check_hooks_shippable(self._dest(tmp), scope="user", env={})
            self.assertFalse(check.ready, "an unconfirmed hook must not read as confirmed")
            self.assertFalse(check.determinable)
            self.assertEqual(installer.READINESS_UNDETERMINABLE, check.verdict)
            self.assertIn("CANNOT EVALUATE", check.reason)
            self.assertIn("neither confirmed nor condemned", check.reason)

    def test_a_stale_entry_is_not_ready_and_determinable(self):
        """Anti-vacuity for the case above: WIRED WRONG is a real failure and
        must stay one. If everything unwirable became CANNOT DETERMINE, the
        distinction would be worthless."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            self._wire_by_hand(tmp, f'py "{Path(tmp).as_posix()}/gone/{self.WRITER}"')
            check = installer.check_hooks_shippable(self._dest(tmp), scope="user", env={})
            self.assertFalse(check.ready)
            self.assertTrue(check.determinable)
            self.assertEqual(installer.READINESS_NOT_READY, check.verdict)
            self.assertIn("STALE", check.reason)

    def test_an_unwired_project_says_not_wired_yet_rather_than_broken(self):
        """A fresh clone must read as UNINSTALLED, not DEFECTIVE."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            check = installer.check_hooks_shippable(self._dest(tmp), scope="user", env={})
            self.assertFalse(check.ready)
            self.assertIn("UNWIRED", check.reason)
            self.assertIn("NOT WIRED YET is not the same as WIRED WRONG", check.reason)
            self.assertNotIn("STALE", check.reason)

    def test_the_report_rolls_undeterminable_up_to_its_own_verdict(self):
        installer = load_installer()
        report = self._report(
            installer,
            hooks=installer.ReadinessCheck(False, "cannot tell", determinable=False),
        )
        self.assertEqual(installer.READINESS_UNDETERMINABLE, report.verdict)
        self.assertEqual(installer.READINESS_EXIT_UNDETERMINABLE, report.exit_code)
        self.assertFalse(report.ready, "CANNOT DETERMINE must never read as READY")

    def test_a_real_failure_outranks_an_undeterminable_one(self):
        """Anti-vacuity for the roll-up: an undeterminable item must not soften
        a genuine failure sitting beside it."""
        installer = load_installer()
        report = self._report(
            installer,
            skills=installer.ReadinessCheck(False, "not installed"),
            hooks=installer.ReadinessCheck(False, "cannot tell", determinable=False),
        )
        self.assertEqual(installer.READINESS_NOT_READY, report.verdict)
        self.assertEqual(1, report.exit_code)
        # ...and the undeterminable item still reads as itself, not as failed.
        block = installer.describe_readiness_report("Claude Code", report)
        self.assertIn("hooks: CANNOT DETERMINE", block)
        self.assertIn("skills: NOT READY", block)

    def test_a_fully_ready_report_is_still_ready(self):
        """Anti-vacuity: the tri-state must not have made READY unreachable."""
        installer = load_installer()
        report = installer.ReadinessReport({
            name: installer.ReadinessCheck(True, "ok") for name in installer.READINESS_ITEMS
        })
        self.assertEqual(installer.READINESS_READY, report.verdict)
        self.assertEqual(0, report.exit_code)

    def test_cli_exits_three_when_only_undeterminable_items_remain(self):
        """End to end through the real CLI, on a project whose hooks are wired
        exactly the way this repo's own tracked settings.json wires them."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / ".claude").mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=str(project), capture_output=True)
            (project / ".claude" / "settings.json").write_text(
                (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"),
                encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=str(project), capture_output=True)
            subprocess.run(
                ["git", "-c", "user.email=t@e.com", "-c", "user.name=T",
                 "commit", "-qm", "init"], cwd=str(project), capture_output=True)
            install = ["--agent", "claude", "--scope", "project",
                       "--project", str(project), "--skills", "workbench"]
            self.assertEqual(0, installer.main(install, env={}, cwd=project, out=lambda _: None))

            lines = []
            code = installer.main(
                [*install, "--check-readiness", "--hooks", "all"],
                env={}, cwd=project, out=lines.append,
            )
        output = "\n".join(lines)
        self.assertEqual(
            installer.READINESS_EXIT_UNDETERMINABLE, code,
            f"a correctly wired project did not read as CANNOT DETERMINE:\n{output}",
        )
        self.assertIn("hooks: CANNOT DETERMINE", output)
        self.assertIn("skills: READY", output)


class NoInterpreterOnHostTests(unittest.TestCase):
    """#539 owner ruling: when `probe_host_interpreter()` finds no working
    candidate, the install HARD-STOPS -- it does not fall back to a guess.

    The reason is stronger than "don't ship something we know fails".
    `_platform_interpreter()` was reached only after every candidate had been
    probed and rejected, and its answer was always a member of that same
    disproved set: `py` on Windows, `python3` on POSIX. It could not be right
    by construction on any platform. It was not a safety net; it was a
    guaranteed-wrong value that ran only in worlds where its own answer had
    been falsified, and it stamped that value into every installed skill body
    so the failure surfaced later, elsewhere, untraceable to its cause.

    This class audits every caller of the probe, one considered answer each --
    an install aborts, a dry run aborts identically, `--baseline-only` is
    untouched because it writes no interpreter at all, and `--check-readiness`
    REPORTS rather than aborting, because refusing to run the diagnostic when
    this condition IS the diagnosis would be its own defect."""

    NOTHING_ANSWERS = "no working Python interpreter found on this host"

    def _no_interpreter(self, installer):
        """Patch so every `<candidate> --version` probe fails, exactly as on the
        owner's Windows host where `py` is an unexecutable `#!/bin/sh` wrapper
        and neither `python3` nor `python` is on PATH."""
        real_run = installer.subprocess.run

        def only_probes_fail(cmd, **kwargs):
            if cmd and cmd[-1] == "--version" and cmd[0] in installer.INTERPRETER_CANDIDATES:
                raise FileNotFoundError(f"no such candidate: {cmd[0]}")
            return real_run(cmd, **kwargs)

        return mock.patch.object(installer.subprocess, "run", side_effect=only_probes_fail)

    def _git_project(self, tmp):
        project = Path(tmp) / "project"
        project.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=str(project), capture_output=True)
        return project

    # -- caller 1: a real install --------------------------------------------

    def test_a_real_install_refuses_and_writes_nothing(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            stderr = io.StringIO()
            with self._no_interpreter(installer):
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as raised:
                        installer.main(
                            ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                             "--skills", "workbench"],
                            env={}, out=lambda _: None,
                        )
            self.assertNotEqual(0, raised.exception.code)
            message = stderr.getvalue()
            self.assertIn(self.NOTHING_ANSWERS, message)
            for candidate in installer.INTERPRETER_CANDIDATES:
                self.assertIn(candidate, message)
            self.assertFalse(dest.exists(), "refused but installed anyway")

    def test_the_same_install_succeeds_when_an_interpreter_answers(self):
        """Positive control for every refusal in this class: the refusals are
        about NO INTERPRETER, not about some unrelated condition in these
        fixtures. Without this, a `main()` that refused unconditionally would
        pass every other test here."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", "workbench"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, code)
            self.assertTrue((dest / "constellation-workbench").is_dir())

    # -- caller 2: --dry-run --------------------------------------------------

    def test_a_dry_run_refuses_exactly_as_the_real_run_would(self):
        """A dry run used to skip the probe entirely, so on a host with no
        interpreter it printed a clean plan and exited 0 for an install that
        could not succeed. A dry run that says "fine" about a run that would
        refuse is worse than no dry run at all."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            stderr = io.StringIO()
            with self._no_interpreter(installer):
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as raised:
                        installer.main(
                            ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                             "--skills", "workbench", "--dry-run"],
                            env={}, out=lambda _: None,
                        )
            self.assertNotEqual(0, raised.exception.code)
            self.assertIn(self.NOTHING_ANSWERS, stderr.getvalue())

    def test_a_dry_run_still_succeeds_when_an_interpreter_answers(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            lines = []
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--skills", "workbench", "--dry-run"],
                env={}, out=lines.append,
            )
            self.assertEqual(0, code)
            self.assertIn("DRY RUN", "\n".join(lines))

    # -- caller 3: --baseline-only -------------------------------------------

    def test_baseline_only_is_unaffected_because_it_writes_no_interpreter(self):
        """A considered answer, not an inherited one. --baseline-only seeds
        template baselines and working copies, both `shutil.copy2` of a source
        template verbatim -- it never reaches `rewrite_installed_skill_paths`,
        so no `python <` token is rewritten and there is no interpreter name to
        write. Refusing here would block a legitimate operation on a ground
        that does not apply to it: the mirror of the defect this ruling fixes."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_project(tmp)
            with self._no_interpreter(installer):
                code = installer.main(
                    ["--agent", "claude", "--scope", "project", "--project", str(project),
                     "--skills", "workbench", "--baseline-only"],
                    env={}, cwd=project, out=lambda _: None,
                )
            self.assertEqual(0, code, "--baseline-only refused despite needing no interpreter")
            seeded = list(project.rglob("*.template.*"))
            self.assertTrue(seeded, "--baseline-only exited 0 without seeding anything")
            # ...and nothing it wrote names an interpreter that was never probed.
            for path in seeded:
                self.assertNotIn(
                    "py <", path.read_text(encoding="utf-8", errors="replace"),
                    f"{path} carries a rewritten interpreter prefix",
                )

    # -- caller 4: --check-readiness -----------------------------------------

    def test_check_readiness_reports_the_condition_instead_of_aborting(self):
        """Readiness exists to NAME what is wrong with a host. Aborting the
        diagnostic when this condition is the diagnosis would be its own
        defect, so this item reports a plain NOT READY -- determinable, not
        CANNOT DETERMINE: a probe that ran and found nothing is a measurement,
        not an unknown."""
        installer = load_installer()
        with self._no_interpreter(installer):
            check = installer.check_interpreter_resolvable()
        self.assertFalse(check.ready)
        self.assertTrue(check.determinable)
        self.assertEqual(installer.READINESS_NOT_READY, check.verdict)
        self.assertIn(self.NOTHING_ANSWERS, check.reason)

    def test_the_readiness_item_passes_when_an_interpreter_answers(self):
        installer = load_installer()
        check = installer.check_interpreter_resolvable()
        self.assertTrue(check.ready, check.reason)
        # A pass names what was actually verified, never just "ok".
        self.assertIn("--version", check.reason)

    def test_check_readiness_cli_names_the_failing_interpreter_item(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_project(tmp)
            lines = []
            with self._no_interpreter(installer):
                code = installer.main(
                    ["--agent", "claude", "--scope", "user",
                     "--dest", str(Path(tmp) / "skills"), "--check-readiness",
                     "--project", str(project)],
                    env={}, cwd=project, out=lines.append,
                )
            output = "\n".join(lines)
        self.assertEqual(1, code, f"readiness did not refuse:\n{output}")
        self.assertIn("interpreter: NOT READY", output)
        self.assertIn(self.NOTHING_ANSWERS, output)

    def test_the_interpreter_item_is_a_distinct_question_from_the_engine_item(self):
        """Not a duplicate of `engine`. `check_engine_runnable` asks whether
        pytest runs under `sys.executable` -- an interpreter that always exists,
        because it is the one running this process. This asks whether any
        candidate resolves as a NAME on PATH, which is what installed skill
        bodies and hook commands are written in terms of. A host passes the
        first and fails the second exactly when no candidate is on PATH."""
        installer = load_installer()
        with self._no_interpreter(installer):
            engine = installer.check_engine_runnable()
            interpreter = installer.check_interpreter_resolvable()
        self.assertTrue(
            engine.ready,
            "the engine item moved with the interpreter item, so this test proves nothing",
        )
        self.assertFalse(interpreter.ready)

    def test_readiness_reports_every_declared_item(self):
        """Anti-vacuity for the new item: a fifth check that build_readiness_report
        never populates would KeyError, and one that describe_ never printed
        would be invisible. Both are asserted against READINESS_ITEMS rather
        than a hard-coded list."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_project(tmp)
            report = installer.build_readiness_report(
                agent=installer.AGENT_TARGETS["claude"],
                target_root=Path(tmp) / "skills", scope="user",
                project_root=project, env={},
            )
        self.assertEqual(set(installer.READINESS_ITEMS), set(report.checks))
        block = installer.describe_readiness_report("Claude Code", report)
        for name in installer.READINESS_ITEMS:
            self.assertIn(f"- {name}: ", block)


class ReadinessCLITests(unittest.TestCase):
    """run_readiness_check / --check-readiness: the thin report layer over the
    four checks. Exits 0 only when every targeted agent is fully ready; exits
    nonzero with a named per-item reason otherwise. Never repairs, never
    writes settings.json at any scope, under any condition."""

    def _git_init(self, path):
        path.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=str(path), capture_output=True, text=True)
        return path

    def test_check_readiness_exits_zero_when_every_item_is_ready(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_init(Path(tmp) / "project")
            dest = Path(tmp) / "skills"
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", "workbench", "--wire-hooks"],
                env={}, out=lambda _: None,
            )
            self.assertEqual(0, code)

            lines = []
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", "workbench", "--check-readiness", "--project", str(project)],
                env={}, cwd=project, out=lines.append,
            )
        self.assertEqual(0, code)
        self.assertIn("READY", "\n".join(lines))

    def test_check_readiness_exits_nonzero_and_names_the_failing_item(self):
        """Refusing case: nothing installed at the target -- must exit nonzero
        and name the specific failing reason, not fail silently."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_init(Path(tmp) / "project")
            dest = Path(tmp) / "skills"  # never installed into
            lines = []
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--check-readiness", "--project", str(project)],
                env={}, cwd=project, out=lines.append,
            )
        self.assertNotEqual(0, code)
        output = "\n".join(lines)
        self.assertIn("NOT READY", output)
        self.assertIn(str(dest), output)

    def test_check_readiness_never_writes_settings_json(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_init(Path(tmp) / "project")
            dest = Path(tmp) / "skills"
            installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--check-readiness", "--project", str(project)],
                env={}, cwd=project, out=lambda _: None,
            )
            self.assertFalse((dest.parent / "settings.json").exists())

    def test_check_readiness_refuses_combination_with_wire_hooks(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "user",
                         "--dest", str(Path(tmp) / "skills"),
                         "--check-readiness", "--wire-hooks"],
                        env={}, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)

    def test_check_readiness_refuses_combination_with_hooks_from(self):
        """`--hooks-from` only affects what gets WRITTEN and this mode writes
        nothing, so accepting it would imply it changed what was checked.
        `--hooks` is a different matter and IS accepted -- it selects which
        hooks are reported on, which is the mode's whole job."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = self._git_init(Path(tmp) / "project")
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "user",
                         "--dest", str(Path(tmp) / "skills"), "--check-readiness",
                         "--project", str(project), "--hooks-from", "source"],
                        env={}, cwd=project, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)
            # ...and --hooks all is accepted on the same command line.
            code = installer.main(
                ["--agent", "claude", "--scope", "user",
                 "--dest", str(Path(tmp) / "skills"), "--check-readiness",
                 "--project", str(project), "--hooks", "all"],
                env={}, cwd=project, out=lambda _: None,
            )
            self.assertNotEqual(2, code, "--hooks all was rejected as a bad combination")

    def test_check_readiness_refuses_combination_with_baseline_only(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    installer.main(
                        ["--agent", "claude", "--scope", "project", "--project", tmp,
                         "--check-readiness", "--baseline-only"],
                        env={}, out=lambda _: None,
                    )
            self.assertNotEqual(0, raised.exception.code)


def _write_mcp_config(path: Path, command: str) -> None:
    path.write_text(json.dumps({
        "mcpServers": {
            "spine": {
                "command": command,
                "args": ["scripts/mcp_spine_server.py"],
                "env": {"SPINE_FILE": "${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"},
            }
        }
    }, indent=2) + "\n", encoding="utf-8")


class RepoMcpConfigWiringTests(unittest.TestCase):
    """M2 g3-rework: `install_constellation.py` must wire this checkout's own
    `.mcp.json` (M2 job 2's `MCP_INTERPRETER_PLACEHOLDER`) AS PART OF
    INSTALLING -- a fresh clone must never need a separate remembered step.

    `wire_repo_mcp_config` / `mcp_config_path` are keyword-only `main()`
    parameters, not CLI flags: they default to `False` / `None` so every
    existing direct call to `main()` throughout this file -- the bulk of this
    suite -- is completely unaffected and NEVER touches a real `.mcp.json`.
    Only the true CLI entry point (`if __name__ == "__main__":`) sets
    `wire_repo_mcp_config=True`, so a real install run wires automatically
    with nothing to remember, while `main()` itself stays exactly as pure as
    it always was. Every test here passes an explicit `mcp_config_path`
    pointing at a fixture -- never this repo's own tracked `.mcp.json`."""

    def test_a_plain_main_call_never_touches_an_mcp_config_even_when_one_is_given(self):
        """The default (`wire_repo_mcp_config=False`, what every other test in
        this file gets) must be a true no-op on the mcp config path -- this is
        what keeps the other ~50 real-install tests in this file safe."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "<python-interpreter>")
            before = mcp_config.read_text(encoding="utf-8")
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--skills", "workbench"],
                env={}, out=lambda _: None, mcp_config_path=mcp_config,
            )
            self.assertEqual(0, code)
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))

    def test_wire_repo_mcp_config_true_wires_the_placeholder_using_the_same_run_probe(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "<python-interpreter>")
            lines = []
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--skills", "workbench"],
                env={}, out=lines.append, wire_repo_mcp_config=True, mcp_config_path=mcp_config,
            )
            self.assertEqual(0, code)
            written = json.loads(mcp_config.read_text(encoding="utf-8"))
            resolved = installer.probe_host_interpreter()
            self.assertEqual(resolved, written["mcpServers"]["spine"]["command"])
            self.assertIn(str(mcp_config), "\n".join(lines))

    def test_wire_repo_mcp_config_is_a_noop_when_the_command_is_not_rewritable(self):
        """A path or another program's name is left alone regardless of what
        this run probes -- the genuine no-op case, unlike a bare name that
        merely happens to match the local probe (host-dependent, so not
        asserted here)."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "/usr/bin/python3.12")
            before = mcp_config.read_text(encoding="utf-8")
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--skills", "workbench"],
                env={}, out=lambda _: None, wire_repo_mcp_config=True, mcp_config_path=mcp_config,
            )
            self.assertEqual(0, code)
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))

    def test_wire_repo_mcp_config_rewrites_a_bare_name_that_differs_from_the_probe(self):
        """M2 g4-repair: the bug this gate fixes. A committed bare name
        (`python3`) that is not what this run's probe resolves to must be
        rewritten, not silently left as a no-op -- reproduced against a real
        `.mcp.json` copy in r1-control; this exercises the same path through
        the CLI entry point's own `main()`."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "python3")

            def only_py_answers(cmd, **kwargs):
                if cmd[0] == "py":
                    return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")
                raise FileNotFoundError(f"no such candidate: {cmd[0]}")

            with mock.patch.object(installer.subprocess, "run", side_effect=only_py_answers):
                code = installer.main(
                    ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                     "--skills", "workbench"],
                    env={}, out=lambda _: None, wire_repo_mcp_config=True, mcp_config_path=mcp_config,
                )
            self.assertEqual(0, code)
            written = json.loads(mcp_config.read_text(encoding="utf-8"))
            self.assertEqual("py", written["mcpServers"]["spine"]["command"])

    def test_no_mcp_config_present_is_a_safe_noop_not_a_refusal(self):
        """An installed copy of this script (write-a-skill bundles it) runs
        from inside some other skill's tree with no `.mcp.json` beside it --
        that is not a defect to refuse the whole install over."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / "nonexistent" / ".mcp.json"
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--skills", "workbench"],
                env={}, out=lambda _: None, wire_repo_mcp_config=True, mcp_config_path=mcp_config,
            )
            self.assertEqual(0, code)
            self.assertFalse(mcp_config.exists())

    def test_dry_run_reports_would_wire_and_writes_nothing(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "<python-interpreter>")
            before = mcp_config.read_text(encoding="utf-8")
            lines = []
            code = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--skills", "workbench", "--dry-run"],
                env={}, out=lines.append, wire_repo_mcp_config=True, mcp_config_path=mcp_config,
            )
            self.assertEqual(0, code)
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))
            self.assertIn("DRY RUN", "\n".join(lines))

    def test_check_readiness_never_wires_even_when_flagged(self):
        """Report-only mode never writes settings.json at any scope -- an
        mcp config is no exception, even if a caller passed the flag."""
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "<python-interpreter>")
            before = mcp_config.read_text(encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=str(Path(tmp)), capture_output=True)
            installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(Path(tmp) / "skills"),
                 "--check-readiness", "--project", tmp],
                env={}, cwd=Path(tmp), out=lambda _: None,
                wire_repo_mcp_config=True, mcp_config_path=mcp_config,
            )
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))

    def test_baseline_only_never_wires_even_when_flagged(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=str(project), capture_output=True)
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "<python-interpreter>")
            before = mcp_config.read_text(encoding="utf-8")
            code = installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "workbench", "--baseline-only"],
                env={}, cwd=project, out=lambda _: None,
                wire_repo_mcp_config=True, mcp_config_path=mcp_config,
            )
            self.assertEqual(0, code)
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))

    def test_hard_stop_when_nothing_probes_leaves_the_mcp_config_untouched(self):
        """The #539 hard-stop-when-nothing-probes property extends to this
        write path for free: `resolve_interpreter()` raises before any
        install work happens, so the mcp config is never reached at all."""
        installer = load_installer()

        def always_fails(cmd, **kwargs):
            raise FileNotFoundError(f"no such candidate: {cmd[0]}")

        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "<python-interpreter>")
            before = mcp_config.read_text(encoding="utf-8")
            stderr = io.StringIO()
            with mock.patch.object(installer.subprocess, "run", side_effect=always_fails):
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as raised:
                        installer.main(
                            ["--agent", "claude", "--scope", "user",
                             "--dest", str(Path(tmp) / "skills"), "--skills", "workbench"],
                            env={}, out=lambda _: None,
                            wire_repo_mcp_config=True, mcp_config_path=mcp_config,
                        )
            self.assertNotEqual(0, raised.exception.code)
            self.assertIn("no working Python interpreter found on this host", stderr.getvalue())
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))

    def test_default_mcp_config_path_points_at_this_checkouts_own_mcp_json(self):
        """No override at all resolves to REPO_ROOT/.mcp.json -- the same
        default `wire_mcp_interpreter.py` uses -- so a real CLI run (which
        never passes `mcp_config_path`) finds this checkout's own file."""
        installer = load_installer()
        self.assertEqual(installer.REPO_ROOT / ".mcp.json", installer.default_mcp_config_path())

    def test_the_cli_entry_point_passes_wire_repo_mcp_config_true(self):
        """The one place `wire_repo_mcp_config=True` may come from by default
        -- not a `main()` default, which would flip every other test in this
        file into a real-file write."""
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn('if __name__ == "__main__":', text)
        self.assertIn("wire_repo_mcp_config=True", text)


class WireMcpInterpreterReuseTests(unittest.TestCase):
    """`scripts/wire_mcp_interpreter.py` (M2 job 2) must reuse
    install_constellation.py's rewrite rather than carrying a second copy --
    the single-source-of-truth this rework's job 1 already established for
    `resolve_interpreter()` now also covers the pure rewrite function."""

    def test_wire_mcp_interpreter_reuses_the_installers_rewrite_function(self):
        wire_path = ROOT / "scripts" / "wire_mcp_interpreter.py"
        wire = load_module("wire_mcp_interpreter_reuse_check", wire_path)
        installer = wire._install
        self.assertIs(wire.rewrite_mcp_config_interpreter, installer.rewrite_mcp_config_interpreter)
        self.assertEqual(wire.MCP_INTERPRETER_PLACEHOLDER, installer.MCP_INTERPRETER_PLACEHOLDER)
        self.assertIs(wire.is_rewritable_mcp_command, installer.is_rewritable_mcp_command)


class IsRewritableMcpCommandTests(unittest.TestCase):
    """M2 g4-repair: the matcher must widen past placeholder-equality to any
    bare interpreter name, while leaving paths and other programs alone."""

    def test_accepts_the_placeholder(self):
        installer = load_installer()
        self.assertTrue(installer.is_rewritable_mcp_command(installer.MCP_INTERPRETER_PLACEHOLDER))

    def test_accepts_bare_python_names_and_their_exe_forms(self):
        installer = load_installer()
        for name in ("python", "python3", "py", "python.exe", "python3.exe", "py.exe"):
            with self.subTest(name=name):
                self.assertTrue(installer.is_rewritable_mcp_command(name))

    def test_rejects_a_path_even_when_its_final_component_is_a_bare_name(self):
        installer = load_installer()
        for command in ("/usr/bin/python3.12", "/usr/bin/python3", r"C:\Python312\python.exe"):
            with self.subTest(command=command):
                self.assertFalse(installer.is_rewritable_mcp_command(command))

    def test_rejects_a_different_program_name(self):
        installer = load_installer()
        for command in ("uv", "node", "run-server.sh"):
            with self.subTest(command=command):
                self.assertFalse(installer.is_rewritable_mcp_command(command))

    def test_rejects_non_string_commands(self):
        installer = load_installer()
        self.assertFalse(installer.is_rewritable_mcp_command(None))


class RewriteMcpConfigInterpreterBareNameTests(unittest.TestCase):
    """M2 g4-repair: `rewrite_mcp_config_interpreter` must rewrite a bare
    interpreter name, not just the placeholder -- the silent no-op reproduced
    against a real `.mcp.json` copy in the r1-control gate."""

    def test_rewrites_a_bare_name_that_differs_from_the_resolved_interpreter(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "python3")
            interpreter = installer.InterpreterResolution("py", ("py", "python3", "python"), "probe")

            changed = installer.rewrite_mcp_config_interpreter(mcp_config, interpreter)

            self.assertTrue(changed)
            written = json.loads(mcp_config.read_text(encoding="utf-8"))
            self.assertEqual("py", written["mcpServers"]["spine"]["command"])

    def test_leaves_an_absolute_path_alone(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            mcp_config = Path(tmp) / ".mcp.json"
            _write_mcp_config(mcp_config, "/usr/bin/python3.12")
            before = mcp_config.read_text(encoding="utf-8")
            interpreter = installer.InterpreterResolution("python3", ("py", "python3", "python"), "probe")

            changed = installer.rewrite_mcp_config_interpreter(mcp_config, interpreter)

            self.assertFalse(changed)
            self.assertEqual(before, mcp_config.read_text(encoding="utf-8"))
