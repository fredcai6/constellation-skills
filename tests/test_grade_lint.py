"""Tests for scripts/grade_lint.py — the @grade: inline-tag linter (issue #230,
epic-226).

Covers the 13 required tests from the g1-implement handoff: the 4 named by the
issue (ungraded FAIL, guess-missing-settle FAIL, dangling-leans FAIL, clean PASS)
plus 9 added by a cold-critic review (prose-is-not-a-decision, the preflight/
execute mode fork, positive leans resolution, the fence regression, multi-path
GL012 file-scoping, the JSON structural walk, --strict-warnings, exit code 2,
and the template round-trip against the real shipped files).

Fixtures are built as REAL Markdown/JSON decision blocks in the exact shape the
shipped templates emit (a real '## Pre-Rulings' heading with real list-item
bullets, a real EXECUTE_PLAN-shaped JSON) rather than hand-simplified stand-ins,
per the fixture-design rule in the handoff.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run(module, argv):
    """Call main(argv) capturing stdout; return (exit_code, stdout_text)."""
    buf = StringIO()
    with redirect_stdout(buf):
        rc = module.main(argv)
    return rc, buf.getvalue()


def _write(tmpdir: str, name: str, text: str) -> str:
    path = Path(tmpdir) / name
    path.write_text(text, encoding="utf-8")
    return str(path)


class GradeLintCoreTests(unittest.TestCase):
    """Tests 1-8: the four issue-named cases plus the cold-critic additions that
    prove a naive implementation (regex-any-line, ignore fences) would falsely
    pass or falsely fail."""

    def setUp(self):
        self.gl = _load("grade_lint")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    # 1. ungraded load-bearing decision -> FAIL (GL001, exit 1)
    def test_ungraded_decision_fails_preflight(self):
        text = (
            "# Launch Order\n\n"
            "## Pre-Rulings\n"
            "Ruled in advance, each overridable if evidence contradicts it.\n"
            "- decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(1, rc)
        data = json.loads(out)
        codes = [v["code"] for v in data["violations"]]
        self.assertIn("GL001", codes)

    # 2. guess without settle: -> FAIL (GL004, exit 1)
    def test_guess_without_settle_fails(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "- decision:foo — some choice with no cheap experiment named.\n"
            "  @grade: guess\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(1, rc)
        data = json.loads(out)
        codes = [v["code"] for v in data["violations"]]
        self.assertIn("GL004", codes)

    # 3. dangling leans -> FAIL (GL005, exit 1)
    def test_dangling_lean_fails(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "- decision:foo — some choice.\n"
            "  @grade: guess · leans nonexistent-gate · settle: a quick spike\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--format", "json", "--known-id", "g1-implement"])
        self.assertEqual(1, rc)
        data = json.loads(out)
        codes = [v["code"] for v in data["violations"]]
        self.assertIn("GL005", codes)

    # 4. clean plan -> PASS (exit 0)
    def test_clean_plan_passes(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "- decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.\n"
            "  @grade: guess · leans g1-implement · settle: 20-line spike appends 2 records, "
            "assert ordering survives a crash\n"
            "- decision:foo-settled — some settled fact, confirmed by a human.\n"
            "  @grade: settled/human\n"
            "- decision:bar-deferred — a choice deferred until later evidence arrives.\n"
            "  @grade: placeholder\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--known-id", "g1-implement"])
        self.assertEqual(0, rc, out)

    # 5. prose is not a decision -> NO violation
    def test_prose_is_not_a_decision(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance, each overridable if evidence contradicts it "
            "— say so when overriding.\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(0, rc, out)
        data = json.loads(out)
        self.assertEqual([], data["violations"])

    # 6. --mode execute suppresses GL001 -- THE FORK's behavioral promise
    def test_execute_mode_suppresses_gl001(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "- decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc_preflight, _ = _run(self.gl, [path])
        rc_execute, out_execute = _run(self.gl, [path, "--mode", "execute", "--format", "json"])
        self.assertEqual(1, rc_preflight)
        self.assertEqual(0, rc_execute, out_execute)
        data = json.loads(out_execute)
        codes = [v["code"] for v in data["violations"]]
        self.assertNotIn("GL001", codes)

    # 7. positive leans resolution -> does NOT fail
    def test_positive_leans_resolution(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "- decision:dedup-wal — reuse WAL not new journal.\n"
            "  @grade: guess · leans g1-implement · settle: 20-line spike, assert ordering\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--known-id", "g1-implement"])
        self.assertEqual(0, rc, out)

    # 8. fence regression -> decision-shaped line + @grade inside a fence -> NO violation
    def test_fence_regression(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "```\n"
            "- decision:fenced — should be invisible to every rule.\n"
            "  @grade: guess\n"
            "```\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(0, rc, out)
        data = json.loads(out)
        self.assertEqual([], data["violations"])


class GradeLintMultiFileAndJsonTests(unittest.TestCase):
    def setUp(self):
        self.gl = _load("grade_lint")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    # 9. multi-path invocation: GL012 does NOT fire across files (ruling 2)
    def test_gl012_scoped_per_file_not_across_files(self):
        file_a = _write(
            self.tmp.name,
            "a.md",
            "## Pre-Rulings\nRuled in advance.\n"
            "- decision:shared-id — first framing of the choice.\n"
            "  @grade: settled/human\n",
        )
        file_b = _write(
            self.tmp.name,
            "b.md",
            "## Pre-Rulings\nRuled in advance.\n"
            "- decision:shared-id — a different, unrelated plan's framing.\n"
            "  @grade: guess · settle: a quick check\n",
        )
        rc, out = _run(self.gl, [file_a, file_b, "--format", "json"])
        self.assertEqual(0, rc, out)
        data = json.loads(out)
        codes = [v["code"] for v in data["violations"]]
        self.assertNotIn("GL012", codes)

    # 10. JSON path coverage: GL001 + GL005 via a real EXECUTE_PLAN-shaped
    # tasks[*].anchors.decision[] structure; anchors:{"inherits": ...} skipped.
    def test_json_structural_walk(self):
        plan = {
            "work_id": "test-json",
            "type": "gated",
            "items": ["g1-implement", "g1-review"],
            "tasks": {
                "g1-implement": {
                    "id": "g1-implement",
                    "anchors": {
                        "decision": [
                            "decision:foo — a real decision with no grade at all"
                        ]
                    },
                },
                "g1-review": {
                    "id": "g1-review",
                    "anchors": {"inherits": "g1-implement anchors"},
                },
            },
            "anchors": {
                "decision": [
                    "decision:bar — another real decision @grade: guess "
                    "· leans nonexistent-item · settle: a quick check"
                ]
            },
        }
        path = _write(self.tmp.name, "plan.json", json.dumps(plan))
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(1, rc, out)
        data = json.loads(out)
        codes = [v["code"] for v in data["violations"]]
        self.assertIn("GL001", codes)
        self.assertIn("GL005", codes)


class GradeLintCliFlagsTests(unittest.TestCase):
    def setUp(self):
        self.gl = _load("grade_lint")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    # 11. --strict-warnings flips a WARN-only run from exit 0 to exit 1
    def test_strict_warnings_flips_exit_code(self):
        text = (
            "## Pre-Rulings\n"
            "Ruled in advance.\n"
            "- decision:x — some settled fact with no recorded provenance.\n"
            "  @grade: settled\n"
        )
        path = _write(self.tmp.name, "order.md", text)
        rc_default, out_default = _run(self.gl, [path])
        rc_strict, _ = _run(self.gl, [path, "--strict-warnings"])
        self.assertEqual(0, rc_default, out_default)
        self.assertEqual(1, rc_strict)

    # 12. exit code 2 on a missing file and on invalid JSON
    def test_exit_code_2_missing_file(self):
        missing = str(Path(self.tmp.name) / "does-not-exist.md")
        rc, _ = _run(self.gl, [missing])
        self.assertEqual(2, rc)

    def test_exit_code_2_invalid_json(self):
        path = _write(self.tmp.name, "broken.json", "{ not valid json")
        rc, _ = _run(self.gl, [path])
        self.assertEqual(2, rc)


class GradeLintTemplateRoundTripTests(unittest.TestCase):
    """13. Lint the REAL shipped files and assert exit 0. These files are edited
    in a later gate to add worked examples, so this reads them from the repo as
    they exist rather than hardcoding their content — it must keep passing after
    that edit."""

    def setUp(self):
        self.gl = _load("grade_lint")

    def test_shipped_templates_lint_clean(self):
        paths = [
            ROOT / "skills" / "admiral" / "templates" / "LATITUDE_CONTRACT.template.md",
            ROOT / "skills" / "admiral" / "templates" / "LAUNCH_ORDER.template.md",
            ROOT / "skills" / "commander" / "templates" / "MISSION_FRAME.template.md",
            ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json",
        ]
        for p in paths:
            self.assertTrue(p.is_file(), f"missing shipped template: {p}")
            rc, out = _run(self.gl, [str(p), "--format", "json"])
            self.assertEqual(0, rc, f"{p} did not lint clean:\n{out}")

    def test_shipped_templates_lint_clean_combined(self):
        paths = [
            ROOT / "skills" / "admiral" / "templates" / "LATITUDE_CONTRACT.template.md",
            ROOT / "skills" / "admiral" / "templates" / "LAUNCH_ORDER.template.md",
            ROOT / "skills" / "commander" / "templates" / "MISSION_FRAME.template.md",
            ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json",
        ]
        rc, out = _run(self.gl, [str(p) for p in paths])
        self.assertEqual(0, rc, out)

    def test_shipped_templates_clean_under_strict_warnings(self):
        """The templates carry a grade slot on their own placeholder bullets, so
        they must be clean at WARN level too — not merely FAIL-free. This is what
        caught the placeholder-child-grade orphan below."""
        paths = [
            ROOT / "skills" / "admiral" / "templates" / "LATITUDE_CONTRACT.template.md",
            ROOT / "skills" / "admiral" / "templates" / "LAUNCH_ORDER.template.md",
            ROOT / "skills" / "commander" / "templates" / "MISSION_FRAME.template.md",
            ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json",
        ]
        rc, out = _run(self.gl, [str(p) for p in paths] + ["--strict-warnings"])
        self.assertEqual(0, rc, out)


class GradeLintPlaceholderChildGradeTests(unittest.TestCase):
    """Regression: a grade welded to a decision that was skipped as template
    scaffolding is itself scaffolding, and must NOT report as an orphan grade.
    Before the fix, every template that showed a grade slot under its own
    `- <placeholder>` bullet emitted a spurious GL010."""

    def setUp(self):
        self.gl = _load("grade_lint")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_grade_under_placeholder_bullet_is_not_an_orphan(self):
        path = _write(self.tmp.name, "tpl.md", "\n".join([
            "## Pre-Rulings",
            "Ruled in advance; each overridable.",
            "- `<ruling>`",
            "  `@grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]`",
            "",
        ]))
        rc, out = _run(self.gl, [path, "--strict-warnings", "--format", "json"])
        self.assertEqual(0, rc, out)
        self.assertNotIn("GL010", out)

    def test_real_orphan_grade_still_reported(self):
        """The fix must not blunt GL010 generally: a grade under a PROSE line
        (no decision bullet at all) is still an orphan."""
        path = _write(self.tmp.name, "orphan.md", "\n".join([
            "## Pre-Rulings",
            "Some narrative prose that is not a decision.",
            "  @grade: settled/human",
            "",
        ]))
        rc, out = _run(self.gl, [path, "--strict-warnings", "--format", "json"])
        self.assertEqual(1, rc, out)
        self.assertIn("GL010", out)


class GradeLintReviewerRegressionTests(unittest.TestCase):
    """Two correctness bugs found by adversarial probing at review, fixed in
    lane. Both are in the Markdown decision-detection heuristic, and neither is
    reachable from the shipped templates — which is exactly why they needed
    their own tests."""

    def setUp(self):
        self.gl = _load("grade_lint")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_bracket_spans_are_not_scaffolding(self):
        """A line starting with one angle-bracket span and ending with another
        is REAL ungraded decision text, not a template placeholder. The greedy
        `^<.*>$` read silently PASSED it — a false clean on an invalid plan."""
        path = _write(self.tmp.name, "greedy.md", "\n".join([
            "## Pre-Rulings",
            "- <decision:dedup-wal> dedup writes reuse the WAL not a new journal <needs review>",
            "",
        ]))
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(1, rc, out)
        self.assertIn("GL001", out)

    def test_true_placeholder_still_skipped(self):
        """The narrower rule must not break the placeholder skip the template
        round-trip depends on."""
        path = _write(self.tmp.name, "ph.md", "\n".join([
            "## Pre-Rulings",
            "- `<ruling>`",
            "",
        ]))
        rc, out = _run(self.gl, [path, "--strict-warnings", "--format", "json"])
        self.assertEqual(0, rc, out)

    def test_nested_sub_bullet_is_elaboration_not_a_decision(self):
        """A bullet indented under a graded decision elaborates it. Treating it
        as its own decision was a false FAIL on a valid plan."""
        path = _write(self.tmp.name, "nested.md", "\n".join([
            "## Pre-Rulings",
            "- decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.",
            "  @grade: settled/human",
            "    - clarifying note: applies to the primary shard, not replicas.",
            "",
        ]))
        rc, out = _run(self.gl, [path, "--strict-warnings", "--format", "json"])
        self.assertEqual(0, rc, out)

    def test_sibling_bullet_at_same_indent_is_still_its_own_decision(self):
        """The nesting rule keys on indentation, so a SIBLING bullet must still
        be graded on its own — otherwise the fix would swallow real decisions."""
        path = _write(self.tmp.name, "sibling.md", "\n".join([
            "## Pre-Rulings",
            "- decision:dedup-wal — reuse the existing WAL.",
            "  @grade: settled/human",
            "- decision:cache-ttl — entries expire on a fixed 300s TTL.",
            "",
        ]))
        rc, out = _run(self.gl, [path, "--format", "json"])
        self.assertEqual(1, rc, out)
        self.assertIn("GL001", out)


if __name__ == "__main__":
    unittest.main()
