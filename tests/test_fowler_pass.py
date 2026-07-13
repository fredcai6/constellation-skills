"""Tests for the constellation-reviewer sharpening rail
(scripts/verify_fowler_pass.py).

The reviewer drives a survey whose `r6-fowler` item runs a refactoring / code-smell
pass in the sense of Martin Fowler's *Refactoring*. This rail mechanically enforces
the two locked behaviors of DESIGN_SPEC Section D3 on the Fowler-pass RECORD:

  * VisitEverySmellTests -- the pass must render a verdict on every baseline Fowler
                            smell; a record that omits one is REFUSED (it can't be
                            silently narrowed so a present smell is never looked at).
  * PlantedSmellTests    -- a fixture carrying an obvious Fowler smell is SURFACED:
                            a record that flags it passes and the smell shows in the
                            flagged set; a record that drops that smell is refused.
  * OverrideLogTests     -- a smell judged subordinate to a DOCUMENTED repo standard
                            (verdict `overridden`, so not flagged) is honored ONLY
                            with a logged reason (standard + why); an override with
                            no logged reason is REFUSED (the bounded rail).
  * RailExceptionTests   -- skipping the WHOLE pass needs an independent reviewer's
                            co-sign + a log; self-assertion never passes, and the
                            exception never excuses a single unlogged override.
  * StructureTests       -- record-shape refusals + CLI exit codes.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The obvious planted smell used by PlantedSmellTests: a function with a
# 7-argument parameter list — Fowler's "long parameter list". The fixture is a
# real code string so the test reads as an end-to-end smell-test, not an abstract
# record check.
PLANTED_FIXTURE = '''\
def build_report(title, author, date, body, footer, theme, locale):
    return title + author + date + body + footer + theme + locale
'''
PLANTED_SMELL = "long-parameter-list"

REQUIRED_SMELLS = (
    "long-method", "large-class", "duplicated-code", "feature-envy", "data-clumps",
    "primitive-obsession", "long-parameter-list", "shotgun-surgery", "divergent-change",
    "message-chains", "speculative-generality", "comments-as-deodorant",
)


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _smell(name: str, verdict: str = "absent", **overrides) -> dict:
    s = {"smell": name, "verdict": verdict, "finding": "", "override": None}
    s.update(overrides)
    return s


def _all_absent() -> list:
    """A complete, valid pass where every baseline smell is absent."""
    return [_smell(name) for name in REQUIRED_SMELLS]


def _with(name: str, **overrides) -> list:
    """The full baseline with one smell's entry overridden by `overrides`."""
    return [_smell(n, **overrides) if n == name else _smell(n) for n in REQUIRED_SMELLS]


def _record(smells=None, **overrides) -> dict:
    rec = {
        "work_id": "issue-x",
        "diff_ref": "the change under review",
        "smells": smells if smells is not None else _all_absent(),
        "rail_exception": None,
    }
    rec.update(overrides)
    return rec


# --------------------------------------------------------------------------- #
class VisitEverySmellTests(unittest.TestCase):
    """Every baseline smell must carry a verdict — the pass can't be silently skipped."""

    def setUp(self):
        self.rail = load("verify_fowler_pass")

    def test_complete_pass_passes(self):
        self.rail.verify_fowler_pass(_record())

    def test_missing_smell_refused(self):
        # Drop one baseline smell: the pass narrowed itself so that smell is never
        # looked at — refused.
        smells = [s for s in _all_absent() if s["smell"] != "duplicated-code"]
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))

    def test_unknown_smell_refused(self):
        smells = _all_absent() + [_smell("vibes-off")]
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))

    def test_duplicate_smell_refused(self):
        smells = _all_absent() + [_smell("large-class")]
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))

    def test_bad_verdict_refused(self):
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=_with("long-method", verdict="meh")))


# --------------------------------------------------------------------------- #
class PlantedSmellTests(unittest.TestCase):
    """A fixture with an obvious Fowler smell is surfaced by the pass."""

    def setUp(self):
        self.rail = load("verify_fowler_pass")

    def test_planted_smell_flagged_passes_and_surfaces(self):
        # THE named case: the fixture plants a long-parameter-list smell; a pass
        # that flags it clears the rail AND the smell shows up flagged.
        self.assertGreaterEqual(PLANTED_FIXTURE.count(","), 5)  # the fixture really is smelly
        smells = _with(PLANTED_SMELL, verdict="flagged",
                       finding="build_report() takes 7 positional args — introduce a parameter object")
        rec = _record(smells=smells, diff_ref="fixture: build_report()")
        self.rail.verify_fowler_pass(rec)
        flagged = [s["smell"] for s in rec["smells"] if s["verdict"] == "flagged"]
        self.assertIn(PLANTED_SMELL, flagged)

    def test_flagged_smell_without_finding_refused(self):
        # Flagging a smell but recording nothing is not a surfaced smell.
        smells = _with(PLANTED_SMELL, verdict="flagged", finding="")
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))

    def test_dropping_the_planted_smell_is_refused(self):
        # The pass can't quietly omit the very smell the fixture plants.
        smells = [s for s in _all_absent() if s["smell"] != PLANTED_SMELL]
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))


# --------------------------------------------------------------------------- #
class OverrideLogTests(unittest.TestCase):
    """A smell subordinate to a documented repo standard is honored only when logged."""

    def setUp(self):
        self.rail = load("verify_fowler_pass")

    def test_override_with_logged_reason_honored(self):
        # THE named case (honored): the smell is present but a documented standard
        # wins; with the standard + reason logged, the override passes.
        smells = _with("speculative-generality", verdict="overridden",
                       override={"repo_standard": "GLOSSARY: the ports-and-adapters seam is a required extension point",
                                 "reason": "the seam is a stated requirement, not speculative generality"})
        self.rail.verify_fowler_pass(_record(smells=smells))

    def test_override_without_logged_reason_refused(self):
        # THE named case (refused): an override with no logged reason — a silent
        # "repo standard wins" — is refused by the bounded rail.
        smells = _with("speculative-generality", verdict="overridden", override=None)
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))

    def test_override_missing_standard_refused(self):
        smells = _with("primitive-obsession", verdict="overridden",
                       override={"repo_standard": "", "reason": "it's fine"})
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))

    def test_override_missing_reason_refused(self):
        smells = _with("primitive-obsession", verdict="overridden",
                       override={"repo_standard": "CREW_CONTEXT: raw ids are canonical", "reason": ""})
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=smells))


# --------------------------------------------------------------------------- #
class RailExceptionTests(unittest.TestCase):
    """Skipping the whole pass needs an independent reviewer's co-sign + log."""

    def setUp(self):
        self.rail = load("verify_fowler_pass")

    def test_reviewer_cosigned_whole_pass_skip_passes(self):
        # A docs-only diff: no code to smell-test. The whole pass is skipped, but
        # only because an independent reviewer co-signed it and it's logged.
        rec = _record(smells=[_smell("long-method")],  # incomplete on purpose
                      rail_exception={"reviewer_cosign": "reviewer-agent-7",
                                      "log": "docs-only diff; no code surface to smell-test"})
        self.rail.verify_fowler_pass(rec)

    def test_self_asserted_whole_pass_skip_refused(self):
        rec = _record(smells=[_smell("long-method")],
                      rail_exception={"reviewer_cosign": "", "log": "I judged there's nothing to check"})
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(rec)

    def test_exception_does_not_excuse_a_single_unlogged_override(self):
        # The exception covers a whole-pass skip only. Once the pass IS run, a
        # single unlogged override is still refused.
        smells = _with("feature-envy", verdict="overridden", override=None)
        rec = _record(smells=smells,
                      rail_exception={"reviewer_cosign": "reviewer-agent-7", "log": "ok"})
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(rec)


# --------------------------------------------------------------------------- #
class StructureTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_fowler_pass")

    def test_empty_diff_ref_refused(self):
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(diff_ref="  "))

    def test_no_smells_refused(self):
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(_record(smells=[]))

    def test_non_object_refused(self):
        with self.assertRaises(self.rail.FowlerPassError):
            self.rail.verify_fowler_pass(["not", "a", "record"])

    def test_absent_needs_no_finding_or_override(self):
        # The common case: every smell absent, nothing else required.
        self.rail.verify_fowler_pass(_record())

    def test_shipped_template_clears_the_rail(self):
        # The template the reviewer copies must itself be a valid, complete record.
        tmpl = json.loads((ROOT / "skills" / "reviewer" / "templates" / "FOWLER_PASS.template.json").read_text(encoding="utf-8"))
        self.rail.verify_fowler_pass(tmpl)

    def test_cli_refuses_unlogged_override_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "record.json"
            smells = _with("data-clumps", verdict="overridden", override=None)
            p.write_text(json.dumps(_record(smells=smells)), encoding="utf-8")
            self.assertNotEqual(0, self.rail.main([str(p)]))

    def test_cli_accepts_complete_pass_zero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "record.json"
            p.write_text(json.dumps(_record()), encoding="utf-8")
            self.assertEqual(0, self.rail.main([str(p)]))


if __name__ == "__main__":
    unittest.main()
