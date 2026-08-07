"""Tests for `scripts/verify_context_declaration.py` -- the mechanical lint
pinning every declared `context_refs` path against the step's own imperative
prose.

The load-bearing test here is `test_divergent_declaration_is_rejected`: a lint
that only passes over the clean shipped corpus proves the corpus is clean, not
that the lint works. `tests/fixtures/context_declaration_lint.json` therefore
carries a fixture whose declaration and prose genuinely diverge, and this
module asserts the lint fails *for that reason* (the offending path is named
in the diagnostic), not merely that some exit code happened to be non-zero --
asserting bare non-zero from a probe that fails for an unrelated reason is the
exact defect this suite is shaped to avoid reintroducing.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = json.loads(
    (ROOT / "tests" / "fixtures" / "context_declaration_lint.json").read_text(encoding="utf-8")
)


def load():
    spec = importlib.util.spec_from_file_location(
        "verify_context_declaration", ROOT / "scripts" / "verify_context_declaration.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_divergent_declaration_is_rejected():
    """The load-bearing negative test, named and shaped exactly as the gate's
    postcondition requires: a bare, module-level pytest function (not nested in
    a unittest.TestCase class) so that
    `pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected`
    resolves it directly -- pytest's `::` node-id selector is an exact match, not
    a substring search, so a same-named method nested inside a class does NOT
    satisfy that node id.

    A lint that only passes over the clean shipped corpus proves the corpus is
    clean, not that the lint works: this fixture's declaration and prose
    genuinely diverge (`references/narrowed-away.md` is declared but never
    named in the task's own imperative), and this asserts the lint's real CLI
    entry point, `main()`, rejects it -- and that the rejection is traceable to
    the actual offending path, not merely "some check somewhere returned
    non-zero" (the exact anti-pattern the gate's handoff calls out by name).
    """
    m = load()
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "divergent.json"
        path.write_text(json.dumps(FIXTURES["divergent"]), encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = m.main([str(path)])
        assert code != 0, "the lint must exit non-zero on a divergent fixture"
        assert "narrowed-away.md" in stderr.getvalue(), (
            f"failure must name the actual offending path, got stderr: {stderr.getvalue()!r}"
        )


class CheckChecklistTests(unittest.TestCase):
    """Direct tests against the pure `check_checklist` function -- no CLI, no
    subprocess, so a failure here can only mean the checking logic itself is
    wrong."""

    def setUp(self):
        self.m = load()

    def test_check_checklist_reports_the_narrowed_away_path(self):
        problems = self.m.check_checklist(FIXTURES["divergent"], source="fixture:divergent")
        self.assertTrue(problems, "expected at least one offender")
        self.assertTrue(
            any("narrowed-away.md" in p for p in problems),
            f"expected the specific offending path named in a problem string, got: {problems}",
        )
        # The two declared-and-present paths must NOT be flagged alongside it --
        # a lint that flags everything on any failure would trivially "catch"
        # the divergent case for the wrong reason.
        self.assertFalse(any("global-everyone.md" in p for p in problems))
        self.assertFalse(any("GLOSSARY.md" in p for p in problems))

    def test_check_checklist_accepts_the_valid_fixture(self):
        problems = self.m.check_checklist(FIXTURES["valid"], source="fixture:valid")
        self.assertEqual(problems, [])

    def test_prose_naming_more_than_declared_is_not_flagged(self):
        # The stated direction limit: the prose here names docs/agents/GLOSSARY.md,
        # which the declaration omits entirely. The lint cannot see that (the
        # imperative is prose, not a parseable list) and must not invent a
        # violation for it -- only a declared-but-unmentioned path is an offense.
        problems = self.m.check_checklist(
            FIXTURES["prose_names_more_than_declared"], source="fixture:prose-wider"
        )
        self.assertEqual(problems, [])

    def test_suffix_of_a_longer_path_is_rejected(self):
        # B2: bare substring containment let a declared 'agents/GLOSSARY.md'
        # pass against prose naming only the longer, DIFFERENT path
        # 'docs/agents/GLOSSARY.md'. The path-boundary rule must catch this --
        # the match is preceded by '/', a path character, so it is a suffix
        # of a longer path, not a standalone occurrence.
        problems = self.m.check_checklist(
            FIXTURES["boundary_suffix_rejected"], source="fixture:boundary-suffix"
        )
        self.assertTrue(problems, "a suffix-of-a-longer-path match must be rejected")
        self.assertTrue(any("agents/GLOSSARY.md" in p for p in problems), problems)

    def test_legitimate_boundary_occurrences_are_accepted(self):
        # B2 non-regression: start-of-string, whitespace, backtick, '(', and
        # quote are all legitimate boundaries. The real shipped
        # COMMANDER_SPINE.template.json relies on exactly these shapes
        # (parens and prose), so the boundary rule must not over-reject them.
        problems = self.m.check_checklist(
            FIXTURES["boundary_legitimate_occurrences_accepted"], source="fixture:boundary-legit"
        )
        self.assertEqual(problems, [])

    def test_trailing_extension_glued_to_a_shorter_path_is_rejected(self):
        # Symmetric half of B2 (commander-300 addendum): the same defect
        # class -- a declared path resolving to a DIFFERENT file than the
        # prose names -- also shows up as a trailing overrun. Declared
        # 'docs/agents/GLOSSARY.md' must not match inside the prose's only
        # occurrence, 'docs/agents/GLOSSARY.md.bak' (a realistic
        # backup-sibling drift shape).
        problems = self.m.check_checklist(
            FIXTURES["boundary_trailing_rejected"], source="fixture:boundary-trailing"
        )
        self.assertTrue(problems, "a path glued to a trailing extension must be rejected")
        self.assertTrue(any("docs/agents/GLOSSARY.md" in p for p in problems), problems)

    def test_legitimate_trailing_occurrences_are_accepted(self):
        # Trailing non-regression: a sentence-ending period, a comma, a
        # closing backtick, a closing paren, and end-of-string are all
        # legitimate trailing boundaries. The shipped
        # COMMANDER_SPINE.template.json ends several of its own declared
        # paths in a sentence period (e.g. '...engine-config.json. Where the
        # repo...'), so the trailing rule must not over-reject that shape.
        problems = self.m.check_checklist(
            FIXTURES["boundary_trailing_legitimate_accepted"], source="fixture:boundary-trailing-legit"
        )
        self.assertEqual(problems, [])


class CliTests(unittest.TestCase):
    """End-to-end through `main()` -- the real entry point CI would invoke."""

    def setUp(self):
        self.m = load()
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _write_fixture(self, key: str) -> str:
        path = Path(self.tmp.name) / f"{key}.json"
        path.write_text(json.dumps(FIXTURES[key]), encoding="utf-8")
        return str(path)

    def test_valid_declaration_is_accepted(self):
        path = self._write_fixture("valid")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.m.main([path])
        self.assertEqual(code, 0, "the lint must exit zero on a clean, matching declaration")

    def test_lint_passes_over_real_shipped_spine_templates(self):
        # Not a fixture: every real, committed template this repo ships. A
        # suite that only exercises authored fixtures would prove the fixtures
        # work, not that the lint is safe to run over the actual corpus.
        templates = sorted((ROOT / "skills").glob("*/templates/*.json"))
        self.assertGreaterEqual(len(templates), 10)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = self.m.main([str(p) for p in templates])
        self.assertEqual(code, 0, f"real corpus must pass cleanly: {stderr.getvalue()}")

    def test_nonexistent_path_fails_visibly_not_silently(self):
        missing = str(Path(self.tmp.name) / "does-not-exist.json")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = self.m.main([missing])
        self.assertNotEqual(code, 0)

    def test_narrowed_declaration_is_deliberately_not_caught(self):
        # Characterization test for the lint's real direction, pinned as an
        # exit code rather than restated only in prose that can drift again.
        # "narrowing" is: a path dropped from context_refs while the prose
        # still names it. The fixture here declares only
        # references/global-everyone.md while its own imperative also names
        # docs/agents/GLOSSARY.md -- that second path was silently dropped
        # from the declaration. The lint has no way to parse "the paths this
        # sentence claims to read" out of free-form prose, so this direction
        # is genuinely invisible to it and MUST pass clean (exit 0). This is
        # the lint's documented blind spot, not a bug -- see the module
        # docstring and docs/CHECKLIST_ENGINE_DESIGN.md.
        path = self._write_fixture("prose_names_more_than_declared")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.m.main([path])
        self.assertEqual(
            code, 0,
            "a narrowed declaration (path dropped while prose still names it) "
            "must NOT be caught -- this is the lint's known, documented blind spot",
        )


class DiscoveryTests(unittest.TestCase):
    """The default (no explicit paths) discovery path, since CI will invoke the
    lint with none."""

    def setUp(self):
        self.m = load()

    def test_default_discovery_finds_the_commander_spine_and_passes(self):
        code = self.m.main(["--root", str(ROOT)])
        self.assertEqual(code, 0)

    def test_default_discovery_skips_non_checklist_template_json(self):
        # skills/charter/templates/ENGINE_CONFIG.template.json and siblings are
        # not gated/survey checklists at all; discovery must not choke on them.
        targets = self.m.discover_templates(ROOT)
        self.assertIn(
            ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json",
            targets,
        )


if __name__ == "__main__":
    unittest.main()
