import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_installer():
    return load("install_constellation")


FEEDBACK_ENTRY = """# Constellation Feedback Export

<!-- collected: never -->

## 2026-06-10 — {project} — issue-5

- **Candidate:** `engine-current-crash-cp1252`
- **Observed:** `engine current crashes on cp1252 consoles with non-ascii task text`
- **Cost:** `run stalled until PYTHONIOENCODING workaround found`
- **Proposal:** `set utf-8 io encoding inside checklist_engine.py instead of requiring env var`
- **Grounding:** `AGENT_FEEDBACK.md 2026-06-06 fleet entry`
- **Confidence:** `high`
"""


class CheckSkillFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.m = load("check_skill_freshness")
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.skills_root = self.project / ".claude" / "skills"
        installer = load_installer()
        self.project.mkdir(parents=True)
        installer.main(
            ["--agent", "claude", "--scope", "project", "--project", str(self.project),
             "--skills", "workbench"],
            env={}, cwd=self.project, out=lambda _line: None,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_fresh_install_is_up_to_date(self):
        rows = self.m.check(self.project, self.skills_root)
        self.assertTrue(rows)
        self.assertTrue(all(r["status"] == "up-to-date" for r in rows))

    def test_upstream_change_detected_and_baseline_promotion(self):
        upstream = (
            self.skills_root / "constellation-workbench" / "templates" / "LESSONS.template.md"
        )
        upstream.write_text(upstream.read_text(encoding="utf-8") + "\nupstream change\n", encoding="utf-8")

        statuses = {r["template"]: r["status"] for r in self.m.check(self.project, self.skills_root)}
        self.assertEqual(statuses["LESSONS.template.md"], "upstream-changed")

        self.m.update_baseline(self.project, self.skills_root)
        statuses = {r["template"]: r["status"] for r in self.m.check(self.project, self.skills_root)}
        self.assertEqual(statuses["LESSONS.template.md"], "up-to-date")
        manifest = json.loads(
            (self.project / ".agent-work" / "templates" / "TEMPLATES_MANIFEST.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["baseline_origin"], "baseline-promoted")

    def test_local_customization_and_both_changed(self):
        local = self.project / ".agent-work" / "templates" / "AGENT_FEEDBACK.template.md"
        baseline = (
            self.project / ".agent-work" / "templates" / ".baseline"
            / "constellation-workbench" / "AGENT_FEEDBACK.template.md"
        )
        local.write_text(baseline.read_text(encoding="utf-8") + "\nproject custom field\n", encoding="utf-8")
        statuses = {r["template"]: r["status"] for r in self.m.check(self.project, self.skills_root)}
        self.assertEqual(statuses["AGENT_FEEDBACK.template.md"], "project-customized")

        upstream = (
            self.skills_root / "constellation-workbench" / "templates" / "AGENT_FEEDBACK.template.md"
        )
        upstream.write_text(upstream.read_text(encoding="utf-8") + "\nupstream change\n", encoding="utf-8")
        statuses = {r["template"]: r["status"] for r in self.m.check(self.project, self.skills_root)}
        self.assertEqual(statuses["AGENT_FEEDBACK.template.md"], "both-changed")


class CollectFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.m = load("collect_feedback")
        self.tmp = tempfile.TemporaryDirectory()
        self.roots = []
        for name in ("alpha", "beta"):
            root = Path(self.tmp.name) / name
            (root / ".agent-work").mkdir(parents=True)
            (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
                FEEDBACK_ENTRY.format(project=name), encoding="utf-8"
            )
            self.roots.append(root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_recurring_candidate_grouped_across_projects(self):
        grouped = self.m.collect(self.roots)
        self.assertEqual(len(grouped), 1)
        hits = next(iter(grouped.values()))
        self.assertEqual(sorted(p for p, _ in hits), ["alpha", "beta"])
        report = self.m.render_report(grouped)
        self.assertIn("Recurring", report)
        self.assertIn("engine-current-crash-cp1252", report)

    def test_mark_advances_marker_and_entries_not_recollected(self):
        feedback = self.roots[0] / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
        self.m.mark_collected(feedback)
        grouped = self.m.collect([self.roots[0]])
        self.assertEqual(grouped, {})

    def test_template_placeholder_entries_skipped(self):
        root = Path(self.tmp.name) / "fresh"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback Export\n\n<!-- collected: never -->\n\n"
            "## `<date>` — `<project>` — `<work-id>`\n\n- **Candidate:** `<slug>`\n",
            encoding="utf-8",
        )
        self.assertEqual(self.m.collect([root]), {})


if __name__ == "__main__":
    unittest.main()
