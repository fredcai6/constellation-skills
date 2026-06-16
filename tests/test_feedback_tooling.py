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

    def test_same_slug_different_prose_is_one_recurring_candidate(self):
        # Same candidate slug, deliberately different observed/proposal prose
        # (prose drift across runs). They must share a fingerprint and count as
        # one recurring candidate with occurrence count 2.
        a = {
            "candidate": "run-crew-cli-launcher-misfit",
            "observed": "run_crew.py builds claude --session argv; no such binary here",
            "proposal": "add a registry-only dispatch mode for Agent-tool harnesses",
        }
        b = {
            "candidate": "run-crew-cli-launcher-misfit",
            "observed": "the installed claude CLI rejects --session/--role/--handoff entirely",
            "proposal": "document a non-CLI / --dispatch=external path that records but never spawns",
        }
        self.assertEqual(self.m.fingerprint(a), self.m.fingerprint(b))

        root = Path(self.tmp.name) / "drift"
        (root / ".agent-work").mkdir(parents=True)
        body = "# Constellation Feedback Export\n"
        for i, e in enumerate((a, b)):
            body += (
                f"\n## 2026-06-11 — drift — issue-{i}\n\n"
                f"- **Candidate:** `{e['candidate']}`\n"
                f"- **Observed:** `{e['observed']}`\n"
                f"- **Proposal:** `{e['proposal']}`\n"
            )
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(body, encoding="utf-8")

        new, open_unresolved = self.m.collect([root])
        self.assertEqual(len(new), 1)  # one recurring candidate, not two
        hits = next(iter(new.values()))
        self.assertEqual(len(hits), 2)  # occurrence count 2

    def test_single_project_recurrence_trips_validated_signal(self):
        # A finding that recurs twice within ONE project must trip the
        # recurring/validated signal even with no cross-project recurrence.
        root = Path(self.tmp.name) / "solo"
        (root / ".agent-work").mkdir(parents=True)
        body = "# Constellation Feedback Export\n"
        for i, prose in enumerate(("worded one way", "worded a different way")):
            body += (
                f"\n## 2026-06-11 — solo — issue-{i}\n\n"
                "- **Candidate:** `spine-lease-stale-on-long-crew`\n"
                f"- **Observed:** `lease lapses mid-gate, {prose}`\n"
                "- **Proposal:** `heartbeat the lease around long gates`\n"
            )
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(body, encoding="utf-8")

        new, open_unresolved = self.m.collect([root])
        hits = next(iter(new.values()))
        self.assertEqual(len(hits), 2)
        self.assertEqual(len({p for p, _ in hits}), 1)  # single project only
        report = self.m.render_report(new, open_unresolved)
        self.assertIn("recurring", report)
        self.assertIn("occurrences: 2", report)

    def test_legacy_resolved_fingerprint_still_resolves(self):
        # Backward-compat: an entry whose legacy content-hash is recorded in
        # `resolved` must still be treated as resolved after the fingerprint
        # change (which now keys on the candidate slug).
        entry = self.m.parse_entries(
            FEEDBACK_ENTRY.format(project="alpha")
        )[0]
        legacy_fp = self.m._content_fingerprint(entry)
        # slug-based fingerprint must differ from the legacy content hash
        self.assertNotEqual(self.m.fingerprint(entry), legacy_fp)

        sidecar = self.roots[0] / ".agent-work" / "CONSTELLATION_FEEDBACK.collected.json"
        sidecar.write_text(
            json.dumps(
                {
                    "collected": {legacy_fp: "2026-06-11"},
                    "resolved": {legacy_fp: {"date": "2026-06-11", "note": "fixed upstream"}},
                }
            ),
            encoding="utf-8",
        )
        new, open_unresolved = self.m.collect([self.roots[0]])
        self.assertEqual(new, {})
        self.assertEqual(open_unresolved, {})

    def test_contentless_section_blocks_are_not_findings(self):
        # Section-header blocks with no candidate/observed/proposal are export
        # noise; they must not collide into a bogus "recurring" candidate.
        root = Path(self.tmp.name) / "noisy"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback Export\n\n"
            "## 2026-06-15 | epic-453 follow-ups (#471/#472)\n\n"
            "some prose with no finding fields\n\n"
            "## 2026-06-15 | epic-453 — background-work failure modes\n\n"
            "more prose, still no fields\n",
            encoding="utf-8",
        )
        self.assertEqual(self.m.collect([root]), ({}, {}))

    def test_template_placeholder_entries_skipped(self):
        root = Path(self.tmp.name) / "fresh"
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "# Constellation Feedback Export\n\n"
            "## `<date>` — `<project>` — `<work-id>`\n\n- **Candidate:** `<slug>`\n",
            encoding="utf-8",
        )
        self.assertEqual(self.m.collect([root]), ({}, {}))


class InboxFilingTests(unittest.TestCase):
    """The human-gated issue-filing inbox: dry-run by default, --confirm to file,
    recurring-only by default, idempotent via a local ledger."""

    def setUp(self):
        self.m = load("collect_feedback")
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        # The ledger lives in the skills repo's (gitignored) .agent-work, not in
        # any consuming project — one issue per finding across all projects.
        self.inbox = self.base / "skills-repo" / ".agent-work" / "CONSTELLATION_INBOX.json"
        self.roots = []
        # alpha & beta share the recurring cp1252 candidate (2 occurrences)
        for name in ("alpha", "beta"):
            self._write_project(name, FEEDBACK_ENTRY.format(project=name))
        # gamma carries a distinct single-project candidate (1 occurrence)
        self._write_project(
            "gamma",
            "# Constellation Feedback Export\n\n"
            "## 2026-06-12 — gamma — issue-7\n\n"
            "- **Candidate:** `gamma-only-flaky-thing`\n"
            "- **Observed:** `only gamma ever hit this`\n"
            "- **Proposal:** `do the gamma fix`\n",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _write_project(self, name, body):
        root = self.base / name
        (root / ".agent-work").mkdir(parents=True)
        (root / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(body, encoding="utf-8")
        self.roots.append(root)

    def _merged(self):
        return self.m.merge_hits(*self.m.collect(self.roots))

    def _fake_filer(self):
        calls = []

        def filer(spec, *, repo=None):
            calls.append(spec)
            n = 40 + len(calls)
            return {"number": str(n), "url": f"https://github.com/x/y/issues/{n}"}

        filer.calls = calls
        return filer

    def test_dry_run_files_nothing(self):
        filer = self._fake_filer()
        result = self.m.file_issues(
            self._merged(), inbox_path=self.inbox, filer=filer, confirm=False
        )
        self.assertEqual(result["filed"], [])
        # only the recurring candidate is eligible; gamma single is excluded
        self.assertEqual(len(result["would_file"]), 1)
        self.assertEqual(filer.calls, [])  # nothing actually filed
        self.assertFalse(self.inbox.exists())  # ledger untouched

    def test_confirm_files_recurring_only(self):
        filer = self._fake_filer()
        result = self.m.file_issues(
            self._merged(), inbox_path=self.inbox, filer=filer, confirm=True
        )
        self.assertEqual(len(result["filed"]), 1)
        self.assertEqual(len(filer.calls), 1)
        self.assertIn("engine-current-crash-cp1252", filer.calls[0]["title"])
        ledger = json.loads(self.inbox.read_text(encoding="utf-8"))
        (_, rec), = ledger["filed"].items()
        self.assertEqual(rec["issue"], "41")
        self.assertEqual(rec["occurrences"], 2)
        self.assertEqual(rec["projects"], ["alpha", "beta"])

    def test_idempotent_no_double_file(self):
        filer = self._fake_filer()
        self.m.file_issues(self._merged(), inbox_path=self.inbox, filer=filer, confirm=True)
        again = self.m.file_issues(
            self._merged(), inbox_path=self.inbox, filer=filer, confirm=True
        )
        self.assertEqual(again["filed"], [])
        self.assertEqual(len(filer.calls), 1)  # only one create call, ever

    def test_include_singles_widens(self):
        filer = self._fake_filer()
        result = self.m.file_issues(
            self._merged(), inbox_path=self.inbox, filer=filer, confirm=True,
            include_singles=True,
        )
        self.assertEqual(
            sorted(s["candidate"] for s in result["filed"]),
            ["engine-current-crash-cp1252", "gamma-only-flaky-thing"],
        )

    def test_issue_spec_carries_substance(self):
        merged = self._merged()
        fp = next(f for f, hits in merged.items() if len(hits) >= self.m.RECURRENCE_THRESHOLD)
        spec = self.m.issue_spec(fp, merged[fp])
        self.assertIn("engine-current-crash-cp1252", spec["title"])
        self.assertIn("engine current crashes on cp1252", spec["body"])  # observed
        self.assertIn("set utf-8 io encoding", spec["body"])  # proposal
        self.assertIn("alpha", spec["body"])  # project list
        self.assertIn(fp, spec["body"])  # fingerprint

    def test_issue_spec_title_degrades_without_slug(self):
        # No candidate slug -> title falls back to a trimmed observed snippet, not
        # the bare fingerprint, so the backlog item stays scannable.
        hits = [("solo", {"observed": "engine deadlocks when two crews share a worktree lease"})]
        spec = self.m.issue_spec("deadbeef0000", hits)
        self.assertIn("engine deadlocks", spec["title"])
        self.assertNotIn("deadbeef0000", spec["title"])
        # but the ledger identity still falls back to the fingerprint
        self.assertEqual(spec["candidate"], "deadbeef0000")

    def test_partial_failure_keeps_earlier_filed(self):
        calls = []

        def flaky(spec, *, repo=None):
            calls.append(spec)
            if len(calls) == 2:
                raise RuntimeError("gh blew up")
            return {"number": "50", "url": "u"}

        with self.assertRaises(RuntimeError):
            self.m.file_issues(
                self._merged(), inbox_path=self.inbox, filer=flaky, confirm=True,
                include_singles=True,
            )
        ledger = json.loads(self.inbox.read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["filed"]), 1)  # first survived the crash

    def test_cli_dry_run_is_default_and_safe(self):
        def boom(spec, *, repo=None):
            raise AssertionError("dry run must never file")

        rc = self.m.main(
            ["--file-issues", "--inbox", str(self.inbox)] + [str(r) for r in self.roots],
            filer=boom,
        )
        self.assertEqual(rc, 0)
        self.assertFalse(self.inbox.exists())

    def test_cli_confirm_files_via_injected_filer(self):
        filer = self._fake_filer()
        rc = self.m.main(
            ["--file-issues", "--confirm", "--inbox", str(self.inbox)]
            + [str(r) for r in self.roots],
            filer=filer,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(len(filer.calls), 1)  # recurring only by default
        self.assertTrue(self.inbox.exists())


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
