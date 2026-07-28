"""Tests for constellation-write-a-skill's mint RAIL (scripts/verify_skill_registered.py)
and the shared skill-goodness criteria seam.

The rail is the single mechanically-enforced check the minted skill must clear
(DESIGN_SPEC Section C): it composes the existing curate_corpus.py mechanical
checks + install --dry-run installability, and adds the one property neither can
see on its own — install-BUNDLE REGISTRATION. An unregistered skill installs as
a dead seam (no doctrine, no rail script) while looking fine on disk; that is the
named failure mode this rail guards.

  * RailPassTests    -- a well-formed, REGISTERED toy skill clears curate +
                        installability + registration, and installs via dry-run.
  * RailRefuseTests  -- a toy skill MISSING bundle registration -> rail REFUSES.
  * SharedSeamTests  -- the prose criteria reference EXISTS and BOTH write-a-skill
                        and curator reference it.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOY_SKILL_MD = """---
name: constellation-toy-widget
description: Turn a toy capability into a repeatable widget procedure. Use when a human wants a demo widget scaffolded. Not curator (which maintains existing skills).
invoker: agent
---

# Constellation Toy Widget

Do the widget thing the same way every run.

## Steps

1. Take the intake.
2. Do the widget work.
3. Hand to an independent reviewer.
"""


def _write_toy(root: Path, name: str = "toy-widget", body: str = TOY_SKILL_MD) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    return skill_dir


class RailPassTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_skill_registered")

    def test_registered_wellformed_toy_passes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skills"
            _write_toy(root)
            # Registered in the reference bundle -> not a dead seam.
            self.rail.verify_skill_registered(
                "toy-widget", root,
                reference_bundles={"toy-widget": ("global-everyone.md",)},
                script_bundles={},
            )  # no raise == accepted

    def test_registered_toy_installs_via_dry_run(self):
        # The installability half of the rail: the toy passes install --dry-run.
        import tempfile
        installer = load("install_constellation")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skills"
            _write_toy(root)
            target = Path(d) / "target"
            skills = installer.discover_skills(root)
            selected = installer.select_skills(["toy-widget"], skills)
            installer.install_skills(
                selected, target, dry_run=True, force=False, full_set=False,
                restart_message="", out=lambda _: None,
            )  # no raise == would install


class RailRefuseTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_skill_registered")

    def test_missing_bundle_registration_refused(self):
        # THE named failure mode: a well-formed skill on disk that is NOT wired
        # into install_constellation's bundles -> dead seam -> rail refuses.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skills"
            _write_toy(root)
            with self.assertRaises(self.rail.SkillRegistrationError):
                self.rail.verify_skill_registered(
                    "toy-widget", root,
                    reference_bundles={},   # <- unregistered
                    script_bundles={},
                )

    def test_mechanically_broken_skill_refused(self):
        # A skill missing its when-to-use marker is mechanically broken -> refused
        # even when registered (curate's gating subset bites at mint time).
        import tempfile
        broken = TOY_SKILL_MD.replace("Use when a human wants a demo widget scaffolded. ", "")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skills"
            _write_toy(root, body=broken)
            with self.assertRaises(self.rail.SkillRegistrationError):
                self.rail.verify_skill_registered(
                    "toy-widget", root,
                    reference_bundles={"toy-widget": ("global-everyone.md",)},
                    script_bundles={},
                )


class RealSkillRegistrationTests(unittest.TestCase):
    """write-a-skill must itself satisfy its own rail — registered in the bundles
    and mechanically clean against the live corpus."""

    def setUp(self):
        self.rail = load("verify_skill_registered")
        self.installer = load("install_constellation")

    def test_write_a_skill_is_registered_in_bundles(self):
        self.assertIn("write-a-skill", self.installer.SKILL_REFERENCE_BUNDLES)
        self.assertIn("write-a-skill", self.installer.SKILL_SCRIPT_BUNDLES)

    def test_write_a_skill_clears_its_own_rail(self):
        # Uses the live registration maps + the real skills/ corpus.
        self.rail.verify_skill_registered("write-a-skill", ROOT / "skills")  # no raise

    def test_rail_resolves_a_subdir_sourced_script_instead_of_falsely_refusing(self):
        """Regression (#262): the rail checked bundle members with a hand-rolled
        `REPO_ROOT/"scripts"/script`, blind to SCRIPT_SOURCE_SUBDIRS. The moment
        the Context Governor hook pair was bundled -- its source lives in
        `scripts/hooks/`, not flat in `scripts/` -- the rail emitted a FALSE
        refusal for the skill that carries it:

            REFUSED: skill 'workbench' registers script 'gauge_writer_hook.py'
                     that does not exist under scripts/

        The script was right there. Source resolution has exactly ONE owner,
        `install_constellation.script_source_path`, and every consumer must go
        through it or they drift apart again.

        Driven against a TOY skill so the assertion isolates the resolver: the
        live corpus carries unrelated pre-existing curate gating flags (missing
        `invoker:` tags on ~12 skills, workbench included) that would mask what
        this test is measuring. `subdir_scripts` is derived from the live
        SCRIPT_SOURCE_SUBDIRS map, so the NEXT subdirectory-sourced script is
        covered automatically."""
        import tempfile
        subdir_scripts = sorted(self.installer.SCRIPT_SOURCE_SUBDIRS)
        self.assertTrue(subdir_scripts, "no script is sourced from a subdirectory any more")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skills"
            _write_toy(root)
            self.rail.verify_skill_registered(
                "toy-widget", root,
                reference_bundles={"toy-widget": ("global-everyone.md",)},
                script_bundles={"toy-widget": tuple(subdir_scripts)},
            )  # no raise == the subdir-sourced sources were found

    def test_rail_still_refuses_a_script_that_really_is_missing(self):
        """The resolver fix must not soften the check it was guarding: a bundle
        entry naming a script that exists nowhere is still a broken
        registration."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skills"
            _write_toy(root)
            with self.assertRaises(self.rail.SkillRegistrationError):
                self.rail.verify_skill_registered(
                    "toy-widget", root,
                    reference_bundles={"toy-widget": ("global-everyone.md",)},
                    script_bundles={"toy-widget": ("no_such_script_anywhere.py",)},
                )


class SharedSeamTests(unittest.TestCase):
    def test_criteria_reference_exists_and_both_consumers_reference_it(self):
        criteria = ROOT / "skills" / "_shared" / "skill-goodness.md"
        self.assertTrue(criteria.is_file(), "shared skill-goodness criteria reference must exist")
        author = (ROOT / "skills" / "write-a-skill" / "SKILL.md").read_text(encoding="utf-8")
        curator = (ROOT / "skills" / "curator" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("skill-goodness", author, "write-a-skill must reference the shared criteria")
        self.assertIn("skill-goodness", curator, "curator must reference the shared criteria")

    def test_installed_curator_carries_the_criteria_reference(self):
        # Both consumers must be able to CONSUME the reference once installed, not
        # just point at it: curator's pointer dangles unless skill-goodness.md is
        # bundled into its installed references/. Assert the reference bundle carries it.
        installer = load("install_constellation")
        self.assertIn(
            "skill-goodness.md", installer.SKILL_REFERENCE_BUNDLES.get("curator", ()),
            "installed curator must bundle skill-goodness.md or its pointer dangles",
        )


if __name__ == "__main__":
    unittest.main()
