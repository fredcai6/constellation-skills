"""Tests for scripts/verify_installed_bundles.py -- the copy-vs-source check.

The point of this verifier is that it must be able to FAIL. Epic #418's whole
subject was checks that could not: `archive.c2b` never invoked `gh` in any PR
state, and the fix first proposed for it exited 0 in all four. So the tests below
install a real bundle into a temp root, then assert BOTH directions -- clean
install passes, and each way a bundle can rot is caught. A test that only asserted
the green case would reproduce the defect it is here to prevent.

The other thing under test is that the verifier is substitution-AWARE. A naive
byte comparison reports every placeholder-bearing bundle as stale; that false
positive is what a substitution-blind check produced during #418's closeout, so
`test_placeholder_bundle_is_not_reported_as_drift` pins the distinction.
"""

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts" / "verify_installed_bundles.py"
INSTALLER = ROOT / "scripts" / "install_constellation.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class InstalledBundleVerifierTests(unittest.TestCase):
    """Every test installs into its own temp root, so nothing here reads or writes
    the developer's real ~/.claude/skills."""

    @classmethod
    def setUpClass(cls):
        cls.verifier = load_module("verify_installed_bundles_under_test", VERIFIER)
        cls.installer = load_module("install_constellation_under_test", INSTALLER)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="verify-bundles-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / "skills"
        self.root.mkdir(parents=True)

        # One real skill, installed the real way -- not a hand-built fixture, so the
        # test cannot pass against a bundle layout the installer never produces.
        # ADMIRAL specifically, because its templates carry `<admiral-skill-dir>`
        # and `python <` tokens: a skill with no placeholders (triage, for one) is
        # byte-identical to its source once installed, so every substitution-aware
        # assertion below would pass without exercising the substitution at all.
        self.skill = self.installer.select_skills(
            ["admiral"], self.installer.discover_skills()
        )[0]
        self.installer.install_skills(
            [self.skill],
            self.root,
            dry_run=False,
            force=True,
            full_set=False,
            restart_message="",
            out=lambda _msg: None,
        )
        self.target = self.root / self.skill.install_name

    def verify(self):
        return self.verifier.verify_bundle(self.skill, self.root)

    # --- it can pass -------------------------------------------------------

    def test_freshly_installed_bundle_is_in_sync(self):
        report = self.verify()
        self.assertEqual(report.status, "in-sync", msg=f"{report.differing} {report.missing_files}")
        self.assertEqual(report.problem_count, 0)

    def test_placeholder_bundle_is_not_reported_as_drift(self):
        """The false positive this verifier exists to avoid.

        The triage bundle's text is rewritten at install time. A byte comparison of
        source against installed therefore differs on every rewritten file, while
        the substitution-aware comparison must report in-sync.
        """
        rewritten = [
            p
            for p in self.target.rglob("*")
            if p.is_file()
            and p.suffix.lower() in self.installer.REWRITABLE_TEXT_SUFFIXES
            and (self.skill.source_path / p.relative_to(self.target)).is_file()
            and p.read_bytes()
            != (self.skill.source_path / p.relative_to(self.target)).read_bytes()
        ]
        self.assertTrue(
            rewritten,
            "no file differed byte-wise from source, so this test would pass vacuously",
        )
        self.assertEqual(self.verify().status, "in-sync")

    # --- it can fail -------------------------------------------------------

    def test_mutated_installed_file_is_caught(self):
        skill_md = self.target / "SKILL.md"
        skill_md.write_text(skill_md.read_text(encoding="utf-8") + "\ndrifted\n", encoding="utf-8")
        report = self.verify()
        self.assertEqual(report.status, "differs")
        self.assertIn("SKILL.md", report.differing)

    def test_stale_installed_copy_of_a_changed_source_is_caught(self):
        """The real failure mode: source moves on, the bundle does not."""
        skill_md = self.target / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace("Constellation Admiral", "OLD HEADING", 1),
            encoding="utf-8",
        )
        self.assertIn("SKILL.md", self.verify().differing)

    def test_deleted_installed_file_is_caught(self):
        victim = next(p for p in self.target.rglob("*.md") if p.name != "SKILL.md")
        rel = victim.relative_to(self.target).as_posix()
        victim.unlink()
        report = self.verify()
        self.assertEqual(report.status, "differs")
        self.assertIn(rel, report.missing_files)

    def test_file_from_no_source_is_caught(self):
        (self.target / "smuggled.md").write_text("not from any source\n", encoding="utf-8")
        report = self.verify()
        self.assertEqual(report.status, "differs")
        self.assertIn("smuggled.md", report.extra_files)

    def test_missing_bundle_is_caught(self):
        shutil.rmtree(self.target)
        self.assertEqual(self.verify().status, "missing")

    def test_missing_sidecar_is_reported_not_guessed(self):
        """With no interpreter.json there is no way to know what the bundle was
        built with, so the verifier says so rather than re-probing this host and
        comparing against an interpreter the bundle may never have seen."""
        (self.target / self.verifier.SIDECAR).unlink()
        self.assertEqual(self.verify().status, "no-sidecar")

    # --- line endings ------------------------------------------------------

    def test_line_ending_difference_alone_is_not_drift(self):
        """A bare ` M`/`diff` on CRLF cost epic #418 a retracted scope accusation
        and nearly a second one; the verifier must not repeat it."""
        skill_md = self.target / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        skill_md.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        self.assertEqual(self.verify().status, "in-sync")


class SubstitutionMapIsSharedTests(unittest.TestCase):
    """The verifier must import the installer's map, never re-derive it: a private
    copy would drift from the installer and report its own drift as the corpus's."""

    @classmethod
    def setUpClass(cls):
        # Load the verifier and then reach for the installer module IT imported.
        # Hand-loading a second copy would compare two distinct module objects and
        # the identity assertion below could never hold -- the test would be
        # unfailable in the other direction, asserting nothing.
        cls.verifier = load_module("verify_installed_bundles_shared", VERIFIER)
        cls.installer = sys.modules["install_constellation"]

    def test_verifier_uses_the_installers_replacement_builder(self):
        self.assertIs(
            self.verifier.installed_path_replacements,
            self.installer.installed_path_replacements,
        )
        self.assertIs(
            self.verifier.apply_installed_path_replacements,
            self.installer.apply_installed_path_replacements,
        )

    def test_replacement_map_resolves_the_shell_metacharacter_tokens(self):
        """`<skill-dir>` left unsubstituted is shell input redirection under
        `sh -c` -- the `archive.c2b` defect (#439/#484). The map must consume it."""
        skill = self.installer.select_skills(["admiral"], self.installer.discover_skills())[0]
        target = Path("/tmp/constellation-admiral")
        interp = self.installer.InterpreterResolution("py", ("py",), "probe")
        replacements = self.installer.installed_path_replacements(target, skill, interp)
        rendered = self.installer.apply_installed_path_replacements(
            "python <admiral-skill-dir>/scripts/x.py and python <skill-dir>/y.py",
            replacements,
        )
        self.assertNotIn("<admiral-skill-dir>", rendered)
        self.assertNotIn("<skill-dir>", rendered)
        self.assertNotIn("python <", rendered)


if __name__ == "__main__":
    unittest.main()
