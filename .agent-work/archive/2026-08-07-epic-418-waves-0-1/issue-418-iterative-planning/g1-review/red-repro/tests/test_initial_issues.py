"""Contract tests for the canonical constellation-to-initial-issues seam."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shaped_brief() -> dict:
    return {
        "schema_version": 1,
        "title": "Iterative planning",
        "source_path": "designs/ITERATIVE_PLAN.md",
        "confirmation": {
            "status": "CONFIRMED",
            "confirmed_by": "Fred",
            "date": "2026-08-06",
        },
        "intent_and_why": "Launch only what evidence supports now.",
        "definition_of_done": ["One coherent wave can be executed and checked."],
        "good_enough": {
            "mandatory_quality": "Strict inputs and recoverable filing",
            "sufficient_evidence": "Focused contract and crash tests",
            "appetite": "One bounded wave",
        },
        "hard_constraints": ["No live network writes"],
        "fixed_decisions": ["Only current-wave issues are actionable"],
        "initial_wave": {
            "objective": "Ship the initial-cut seam",
            "exit_criteria": ["Strict verification is green"],
        },
        "wave_forecast": [
            {
                "outcome": "Add replanning",
                "why_likely": "Wave evidence will change the next cut",
                "entry_conditions": ["Initial-cut seam is accepted"],
            }
        ],
        "uncertainty_register": [
            {
                "unknown": "How much doctrine must change",
                "affects": "Next-wave scope",
                "settle_by": "Role-contract gate",
                "current_evidence": "Current route is prose-heavy",
                "next_probe": "Run doctrine invariant tests",
            }
        ],
        "parked_possibilities": ["Autonomous portfolio optimization"],
        "evidence_digest": [
            {"claim": "Receipts recover crashes", "source": "tests", "conclusion": "Preserve seam"}
        ],
    }


def issue_drafts() -> list[dict]:
    return [
        {
            "id": "A",
            "title": "Build the strict seam",
            "desired_outcome": "A confirmed brief becomes one verified manifest.",
            "useful_now": "It unlocks the first runnable wave.",
            "appetite": "One implementation gate",
            "acceptance_or_falsification_evidence": "Focused contract tests pass.",
            "implementation_latitude": "Choose internal helpers; preserve public fields.",
            "hard_constraints_no_gos": ["No compatibility alias"],
            "local_unknowns": [],
            "anchors": ["scripts/verify_issue_set.py"],
            "type": "AFK",
            "blocks": ["B"],
        },
        {
            "id": "B",
            "title": "Accept the cut",
            "desired_outcome": "A human accepts the public contract.",
            "useful_now": "It closes the irreversible naming choice.",
            "appetite": "One review",
            "acceptance_or_falsification_evidence": "Human records approval.",
            "implementation_latitude": "Do not change fixed decisions.",
            "hard_constraints_no_gos": [],
            "local_unknowns": ["Final wording"],
            "anchors": ["skills/to-initial-issues/SKILL.md"],
            "type": "HITL",
            "hitl_reason": "A human owns acceptance.",
            "blocks": [],
        },
    ]


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_issue_set")

    def manifest(self, issues=None):
        return self.rail.build_initial_manifest(shaped_brief(), issues or issue_drafts())

    def test_checked_in_shaped_brief_template_feeds_cutter_directly(self):
        path = ROOT / "skills" / "to-initial-issues" / "templates" / "SHAPED_BRIEF.template.json"
        brief = json.loads(path.read_text(encoding="utf-8"))
        manifest = self.rail.build_initial_manifest(brief, issue_drafts())
        self.rail.verify_issue_set(manifest, brief)
        self.assertEqual(brief["title"], manifest["epic"]["title"])
        self.assertEqual(brief["source_path"], manifest["epic"]["spec_path"])
        for field in (
            "intent_and_why", "definition_of_done", "good_enough", "hard_constraints",
            "fixed_decisions", "wave_forecast", "uncertainty_register", "parked_possibilities",
        ):
            self.assertEqual(brief[field], manifest["epic"].get(field, manifest.get(field)))

    def test_mapping_puts_only_drafts_in_current_wave(self):
        brief = shaped_brief()
        manifest = self.rail.build_initial_manifest(brief, issue_drafts())
        self.assertEqual(brief["initial_wave"]["objective"], manifest["current_wave"]["objective"])
        self.assertEqual(issue_drafts(), manifest["current_wave"]["issues"])
        self.assertNotIn("issues", manifest)
        for forecast in manifest["wave_forecast"]:
            self.assertTrue({"id", "type", "body", "blocks"}.isdisjoint(forecast))

    def test_zero_edges_are_valid(self):
        drafts = issue_drafts()
        for issue in drafts:
            issue["blocks"] = []
        manifest = self.rail.build_initial_manifest(shaped_brief(), drafts)
        self.rail.verify_issue_set(manifest, shaped_brief())

    def test_dangling_and_cyclic_edges_fail(self):
        dangling = issue_drafts()
        dangling[0]["blocks"] = ["missing"]
        with self.assertRaisesRegex(self.rail.IssueSetError, "known issue"):
            self.rail.verify_issue_set(
                self.rail.build_initial_manifest(shaped_brief(), dangling), shaped_brief()
            )
        cyclic = issue_drafts()
        cyclic[1]["blocks"] = ["A"]
        with self.assertRaisesRegex(self.rail.IssueSetError, "cycle"):
            self.rail.verify_issue_set(
                self.rail.build_initial_manifest(shaped_brief(), cyclic), shaped_brief()
            )

    def test_exactly_eight_required_headings_render(self):
        manifest = self.manifest()
        body = self.rail.render_epic_body(manifest)
        headings = [line[3:] for line in body.splitlines() if line.startswith("## ")]
        self.assertEqual(
            [
                "Intent and why", "Definition of done", "Good-enough boundary and appetite",
                "Hard constraints and fixed decisions", "Current wave",
                "Wave forecast (nonbinding)", "Active uncertainty register", "Parked possibilities",
            ],
            headings,
        )

    def test_verifier_cli_uses_the_shaped_brief_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_path = root / "brief.json"
            manifest_path = root / "manifest.json"
            brief_path.write_text(json.dumps(shaped_brief()), encoding="utf-8")
            manifest_path.write_text(json.dumps(self.manifest()), encoding="utf-8")
            self.assertEqual(
                0,
                self.rail.main([str(manifest_path), "--brief", str(brief_path)]),
            )

    def test_strict_brief_rejects_missing_empty_wrong_type_enum_bad_date_and_unknown(self):
        mutations = [
            lambda x: x.pop("title"),
            lambda x: x.__setitem__("intent_and_why", "  "),
            lambda x: x.__setitem__("definition_of_done", "wrong"),
            lambda x: x["confirmation"].__setitem__("status", "DRAFT"),
            lambda x: x["confirmation"].__setitem__("date", "06/08/2026"),
            lambda x: x.__setitem__("surprise", True),
            lambda x: x.__setitem__("parked_possibilities", [""]),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                value = shaped_brief()
                mutate(value)
                with self.assertRaises(self.rail.IssueSetError):
                    self.rail.verify_shaped_brief(value)

    def test_strict_manifest_and_issue_contract_reject_unknown_or_bad_values(self):
        mutations = [
            lambda x: x.__setitem__("schema_version", True),
            lambda x: x.__setitem__("surprise", True),
            lambda x: x["current_wave"]["issues"][0].__setitem__("type", "MAYBE"),
            lambda x: x["current_wave"]["issues"][0].__setitem__("anchors", []),
            lambda x: x["current_wave"]["issues"][0].__setitem__("hitl_reason", "not allowed"),
            lambda x: x["wave_forecast"][0].__setitem__("id", "future"),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                manifest = self.manifest()
                mutate(manifest)
                with self.assertRaises(self.rail.IssueSetError):
                    self.rail.verify_issue_set(manifest, shaped_brief())


class SpyAdapter:
    def __init__(self):
        self.epics = {}
        self.issues = {}
        self.calls = []

    def find_epic(self, key):
        self.calls.append(("find_epic", key))
        return self.epics.get(key)

    def create_epic(self, epic, body, key):
        self.calls.append(("create_epic", epic["title"]))
        self.epics[key] = f"epic:{len(self.epics) + 1}"
        return self.epics[key]

    def find_issue(self, key):
        self.calls.append(("find_issue", key))
        return self.issues.get(key)

    def create_issue(self, issue, body, key):
        self.calls.append(("create_issue", issue["id"]))
        self.issues[key] = f"issue:{len(self.issues) + 1}"
        return self.issues[key]


class FilingTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_issue_set")
        self.filer = load("file_issue_set")
        self.brief = shaped_brief()
        self.manifest = self.rail.build_initial_manifest(self.brief, issue_drafts())

    def test_forecast_never_reaches_find_or_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter = SpyAdapter()
            self.filer.file_issue_set(self.manifest, self.brief, adapter, Path(tmp) / "receipt.json")
            rendered_calls = json.dumps(adapter.calls)
            self.assertNotIn("Add replanning", rendered_calls)
            self.assertEqual(["A", "B"], [arg for call, arg in adapter.calls if call == "create_issue"])

    def test_filer_cli_dry_run_uses_the_shaped_brief_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_path = root / "brief.json"
            manifest_path = root / "manifest.json"
            brief_path.write_text(json.dumps(self.brief), encoding="utf-8")
            manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
            self.assertEqual(
                0,
                self.filer.main(
                    [str(manifest_path), "--brief", str(brief_path), "--dry-run"]
                ),
            )

    def test_markdown_adapter_remains_offline_and_current_wave_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adapter = self.filer.MarkdownAdapter(root / "TRACKER.md")
            receipt = self.filer.file_issue_set(
                self.manifest, self.brief, adapter, root / "receipt.json"
            )
            self.assertEqual(1, adapter.count_epics())
            self.assertEqual(2, adapter.count_issues())
            self.assertEqual({"A", "B"}, set(receipt["issues"]))
            self.assertNotIn(
                "## ISSUE: Add replanning",
                (root / "TRACKER.md").read_text(encoding="utf-8"),
            )

    def test_epic_and_every_child_recover_each_crash_window_without_duplicates(self):
        points = ["before-file", "after-file-before-receipt", "after-receipt"]
        entities = ["epic", "issue:A", "issue:B"]
        for entity in entities:
            for point in points:
                with self.subTest(entity=entity, point=point), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    adapter = self.filer.MarkdownAdapter(root / "TRACKER.md")
                    receipt_path = root / "receipt.json"
                    with self.assertRaises(self.filer.CrashInjected):
                        self.filer.file_issue_set(
                            self.manifest, self.brief, adapter, receipt_path,
                            crash_at=f"{entity}:{point}",
                        )
                    receipt = self.filer.file_issue_set(
                        self.manifest, self.brief, adapter, receipt_path
                    )
                    self.assertEqual(1, adapter.count_epics())
                    self.assertEqual(2, adapter.count_issues())
                    self.assertEqual({"A", "B"}, set(receipt["issues"]))

    def test_receipt_manifest_and_entry_key_mismatches_fail_before_adapter_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt_path = root / "receipt.json"
            for bad_receipt in (
                {"manifest_key": "wrong", "issues": {}},
                {
                    "manifest_key": self.filer.manifest_key(self.manifest),
                    "epic": {"key": "wrong", "ref": "epic:1"},
                    "issues": {},
                },
                {
                    "manifest_key": self.filer.manifest_key(self.manifest),
                    "epic": {"key": self.filer.epic_key(self.manifest), "ref": "epic:1"},
                    "issues": {"A": {"key": "wrong", "ref": "issue:1"}},
                },
            ):
                with self.subTest(receipt=bad_receipt):
                    receipt_path.write_text(json.dumps(bad_receipt), encoding="utf-8")
                    adapter = SpyAdapter()
                    with self.assertRaises(self.filer.IssueSetError):
                        self.filer.file_issue_set(
                            self.manifest, self.brief, adapter, receipt_path
                        )
                    self.assertEqual([], adapter.calls)


if __name__ == "__main__":
    unittest.main()
