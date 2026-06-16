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
        # A project-local working copy is now seeded at install, so promoting the
        # baseline alone leaves that copy stale (it reads project-customized until
        # reconciled). The reconcile step brings the working copy up to the new
        # upstream too; then it reads up-to-date.
        local = self.project / ".agent-work" / "templates" / "LESSONS.template.md"
        local.write_text(upstream.read_text(encoding="utf-8"), encoding="utf-8")
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
        new, open_unresolved = self.m.collect(self.roots)
        self.assertEqual(len(new), 1)
        self.assertEqual(open_unresolved, {})
        hits = next(iter(new.values()))
        self.assertEqual(sorted(p for p, _ in hits), ["alpha", "beta"])
        report = self.m.render_report(new, open_unresolved)
        self.assertIn("recurring", report)
        self.assertIn("engine-current-crash-cp1252", report)

    def test_collected_entries_move_to_open_until_resolved(self):
        self.m.mark_collected(self.roots[0])
        new, open_unresolved = self.m.collect([self.roots[0]])
        self.assertEqual(new, {})
        self.assertEqual(len(open_unresolved), 1)
        report = self.m.render_report(new, open_unresolved)
        self.assertIn("not yet resolved", report)

    def test_resolved_entries_disappear(self):
        self.m.mark_collected(self.roots[0])
        (_, open_unresolved) = self.m.collect([self.roots[0]])
        fp = next(iter(open_unresolved))
        self.assertTrue(self.m.mark_resolved(self.roots[0], fp, "fixed in PR #19"))
        new, open_after = self.m.collect([self.roots[0]])
        self.assertEqual(new, {})
        self.assertEqual(open_after, {})
        # resolving twice is a no-op
        self.assertFalse(self.m.mark_resolved(self.roots[0], fp, "again"))

    def test_partial_collection_is_per_entry(self):
        # add a second, different entry to alpha AFTER marking the first collected
        self.m.mark_collected(self.roots[0])
        feedback = self.roots[0] / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
        feedback.write_text(
            feedback.read_text(encoding="utf-8")
            + "\n## 2026-06-11 — alpha — issue-9\n\n"
            + "- **Candidate:** `another-thing`\n"
            + "- **Observed:** `something else entirely`\n"
            + "- **Proposal:** `do a different thing`\n",
            encoding="utf-8",
        )
        new, open_unresolved = self.m.collect([self.roots[0]])
        self.assertEqual(len(new), 1)
        self.assertEqual(len(open_unresolved), 1)

    def test_template_placeholder_entries_skipped(self):
        root = Path(self.tmp.name) / "fresh"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback Export\n\n"
            "## `<date>` — `<project>` — `<work-id>`\n\n- **Candidate:** `<slug>`\n",
            encoding="utf-8",
        )
        self.assertEqual(self.m.collect([root]), ({}, {}))


class FreshnessPathTokenTests(unittest.TestCase):
    def test_installed_path_rewritten_template_is_up_to_date(self):
        m = load("check_skill_freshness")
        installer = load_installer()

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            skills_root = Path(tmp) / "user-skills"
            project.mkdir()
            # user-scope install (rewrites path tokens to absolute paths)
            installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(skills_root),
                 "--skills", "commander"],
                env={}, out=lambda _line: None,
            )
            # project baseline seeded from pristine repo source (token form)
            installer.main(
                ["--agent", "claude", "--scope", "project", "--project", str(project),
                 "--skills", "commander", "--baseline-only"],
                env={}, cwd=project, out=lambda _line: None,
            )
            statuses = {r["template"]: r["status"] for r in m.check(project, skills_root)}
            self.assertEqual(statuses["COMMANDER_SPINE.template.json"], "up-to-date")
