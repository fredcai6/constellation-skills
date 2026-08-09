"""Parsed role-doctrine invariants for the G1 -> G2 iterative planning chain."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
EXPLORER_SPINE = ROOT / "skills" / "explorer" / "templates" / "EXPLORER_SPINE.template.json"
COMMANDER_SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"
ADMIRAL_SPINE = ROOT / "skills" / "admiral" / "templates" / "ADMIRAL_SPINE.template.json"
EXPLORER_SKILL = ROOT / "skills" / "explorer" / "SKILL.md"
COMMANDER_CORE = ROOT / "skills" / "commander" / "references" / "commander-core.md"
ADMIRAL_SKILL = ROOT / "skills" / "admiral" / "SKILL.md"
SHAPED_BRIEF = ROOT / "skills" / "to-initial-issues" / "templates" / "SHAPED_BRIEF.template.json"
REPLAN_INPUT = ROOT / "skills" / "replan" / "templates" / "REPLAN_INPUT.template.json"
REPLAN_RESULT = ROOT / "skills" / "replan" / "templates" / "REPLAN_RESULT.template.json"
ROLE_VERIFIER = ROOT / "scripts" / "verify_iterative_role_artifacts.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def markdown_section(path: Path, heading: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    heading_index = next(
        index for index, line in enumerate(lines)
        if line.startswith("#") and line.lstrip("# ") == heading
    )
    level = len(lines[heading_index]) - len(lines[heading_index].lstrip("#"))
    start = heading_index + 1
    end = next(
        (
            index for index in range(start, len(lines))
            if lines[index].startswith("#")
            and len(lines[index]) - len(lines[index].lstrip("#")) <= level
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


def issue(issue_id: str = "A"):
    return {
        "id": issue_id,
        "title": f"Issue {issue_id}",
        "desired_outcome": "The initial public seam is demonstrated.",
        "useful_now": "It closes one coherent learning loop.",
        "appetite": "One bounded gate",
        "acceptance_or_falsification_evidence": "The public verifier passes or refuses.",
        "implementation_latitude": "Choose internals while preserving confirmed intent.",
        "hard_constraints_no_gos": [],
        "local_unknowns": [],
        "anchors": ["skills/to-initial-issues"],
        "type": "AFK",
        "blocks": [],
    }


class ParsedRoleContractTests(unittest.TestCase):
    def setUp(self):
        self.explorer = load_json(EXPLORER_SPINE)
        self.commander = load_json(COMMANDER_SPINE)
        self.admiral = load_json(ADMIRAL_SPINE)

    def test_explorer_confirm_has_one_canonical_executable_output(self):
        directives = self.explorer["tasks"]["confirm"].get("directives")
        self.assertIsInstance(directives, dict, "Explorer confirm lacks a parsed iterative-planning contract")
        shaped = directives["shaped_brief"]
        self.assertEqual(
            shaped,
            {
                "template": "../constellation-to-initial-issues/templates/SHAPED_BRIEF.template.json",
                "output": ".agent-work/<work-id>/SHAPED_BRIEF.json",
                "retains": ["ideas", "evidence"],
                "weight": "irreversible-or-load-bearing-initial-commitments",
                "separate_prose_handoff": False,
                "check": "verify_iterative_role_artifacts.py explorer",
            },
        )

    def test_commander_execute_returns_exact_replan_evidence_without_filing(self):
        directives = self.commander["tasks"]["execute"].get("directives")
        self.assertIsInstance(directives, dict, "Commander execute lacks a parsed replan-input contract")
        returned = directives["replan_input"]
        self.assertEqual(returned["template"], "../constellation-replan/templates/REPLAN_INPUT.template.json")
        self.assertEqual(returned["output"], ".agent-work/<work-id>/REPLAN_INPUT.json")
        self.assertEqual(returned["check"], "verify_iterative_role_artifacts.py commander")
        self.assertEqual(
            returned["evidence_fields"],
            ["completed_outcomes", "wave_evidence", "discrepancies"],
        )
        self.assertEqual(
            returned["classifications"],
            [
                "blocks_current_wave_exit",
                "invalidates_forecast_or_decomposition",
                "later_only",
                "evidence_only",
                "drop",
            ],
        )
        self.assertIs(returned["auto_file_discrepancies"], False)

    def test_admiral_execute_requires_one_verified_exit_before_next_launch(self):
        directives = self.admiral["tasks"]["execute"].get("directives")
        self.assertIsInstance(directives, dict, "Admiral execute lacks a parsed wave-transition contract")
        transition = directives["wave_transition"]
        self.assertEqual(transition["input_template"], "../constellation-replan/templates/REPLAN_INPUT.template.json")
        self.assertEqual(transition["result_template"], "../constellation-replan/templates/REPLAN_RESULT.template.json")
        self.assertEqual(transition["triggers"], ["wave_boundary", "material_exception"])
        self.assertEqual(transition["decisions"], ["advance", "repair", "replan", "stop"])
        self.assertIs(transition["one_exit_before_next_launch"], True)
        self.assertIs(transition["forecast_is_provisional"], True)
        self.assertIs(transition["repair_holds_forecast"], True)
        self.assertEqual(transition["render"], ["revised_epic_body", "wave_review_comment"])
        self.assertEqual(transition["posting"], "authorized-tracker-port-after-gates")
        self.assertIs(transition["direct_gh_or_network_mutation"], False)
        self.assertEqual(transition["next_wave"], ".agent-work/<work-id>/NEXT_WAVE.json")
        self.assertEqual(transition["transition_root"], ".agent-work/<work-id>/transitions/<boundary-id>")
        self.assertEqual(transition["audit"], ".agent-work/<work-id>/ADMIRAL_LOG.md")
        self.assertEqual(transition["check"], "verify_iterative_role_artifacts.py admiral-prelaunch")

        explorer_c3 = next(item for item in self.explorer["tasks"]["confirm"]["postconditions"] if item["id"] == "c3")
        commander_c2 = next(item for item in self.commander["tasks"]["execute"]["postconditions"] if item["id"] == "c2")
        admiral_c3 = next(item for item in self.admiral["tasks"]["execute"]["postconditions"] if item["id"] == "c3")
        for postcondition, mode in (
            (explorer_c3, " explorer "),
            (commander_c2, " commander "),
            (admiral_c3, " admiral-prelaunch "),
        ):
            self.assertEqual((postcondition["check"] or {}).get("kind"), "command")
            self.assertIn("verify_iterative_role_artifacts.py", postcondition["check"]["command"])
            self.assertIn(mode, postcondition["check"]["command"])

    def test_live_markdown_sections_match_the_structured_chain(self):
        explorer = markdown_section(EXPLORER_SKILL, "Confirmed shaped brief")
        shaped = self.explorer["tasks"]["confirm"]["directives"]["shaped_brief"]
        self.assertIn(Path(shaped["template"]).name, explorer)
        self.assertIn(Path(shaped["output"]).name, explorer)
        self.assertIn("single executable", explorer)

        commander = markdown_section(COMMANDER_CORE, "Return execution evidence for replanning")
        returned = self.commander["tasks"]["execute"]["directives"]["replan_input"]
        self.assertIn(Path(returned["template"]).name, commander)
        for classification in returned["classifications"]:
            self.assertIn(classification, commander)
        self.assertIn("do not file", commander)

        admiral = markdown_section(ADMIRAL_SKILL, "Replan before the next wave")
        transition = self.admiral["tasks"]["execute"]["directives"]["wave_transition"]
        self.assertIn(Path(transition["input_template"]).name, admiral)
        self.assertIn(Path(transition["result_template"]).name, admiral)
        for decision in transition["decisions"]:
            self.assertIn(f"`{decision}`", admiral)
        self.assertIn("authorized tracker port", admiral)

    def test_existing_engine_recovery_review_and_human_gates_survive(self):
        explorer_checks = [item["check"] for item in self.explorer["tasks"]["confirm"]["postconditions"]]
        self.assertTrue(any(check and check.get("evidence_type") == "user-decision" for check in explorer_checks))
        self.assertTrue(any(check and "verify_spec_confirmed.py" in check.get("command", "") for check in explorer_checks))

        commander_execute = self.commander["tasks"]["execute"]
        commander_prechecks = [item["check"] for item in commander_execute["preconditions"]]
        self.assertTrue(any(check and "verify_state_note.py" in check.get("command", "") for check in commander_prechecks))
        self.assertIn("run_crew.py", commander_execute["imperative"])
        self.assertIn("recover_crews.py", commander_execute["imperative"])
        for task_id in ("understand", "plan", "triage", "review"):
            checks = [item["check"] for item in self.commander["tasks"][task_id]["postconditions"]]
            self.assertTrue(
                any(check and check.get("evidence_type") == "user-decision" for check in checks),
                task_id,
            )

        latitude_checks = [item["check"] for item in self.admiral["tasks"]["latitude"]["postconditions"]]
        self.assertTrue(any(check and check.get("evidence_type") == "user-decision" for check in latitude_checks))
        admiral_prechecks = [item["check"] for item in self.admiral["tasks"]["execute"]["preconditions"]]
        self.assertTrue(any(check and "verify_state_note.py" in check.get("command", "") for check in admiral_prechecks))
        closeout_checks = [item["check"] for item in self.admiral["tasks"]["closeout"]["postconditions"]]
        self.assertTrue(any(check and check.get("evidence_type") == "user-decision" for check in closeout_checks))


class PublicIterativePlanningSeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.initial = load_module("g3_verify_issue_set", ROOT / "scripts" / "verify_issue_set.py")
        cls.replan = load_module("g3_verify_replan", ROOT / "skills" / "replan" / "scripts" / "verify_replan.py")

    def test_explorer_template_flows_directly_to_initial_cut_and_renderer(self):
        brief = load_json(SHAPED_BRIEF)
        self.initial.verify_shaped_brief(brief)
        manifest = self.initial.build_initial_manifest(brief, [issue()])
        self.initial.verify_issue_set(manifest, brief)
        self.assertEqual(manifest["epic"]["title"], brief["title"])
        self.assertEqual(manifest["epic"]["spec_path"], brief["source_path"])
        for field in (
            "definition_of_done", "good_enough", "hard_constraints", "fixed_decisions",
            "wave_forecast", "uncertainty_register", "parked_possibilities",
        ):
            self.assertEqual(manifest[field], brief[field], field)
        rendered = self.initial.render_epic_body(manifest)
        self.assertIn(brief["intent_and_why"], rendered)
        self.assertIn("## Wave forecast (nonbinding)", rendered)

    def test_commander_packet_and_admiral_transition_share_exact_g2_seam(self):
        packet = load_json(REPLAN_INPUT)
        result = load_json(REPLAN_RESULT)
        self.replan.verify_replan_input(packet)
        self.replan.verify_replan_result(packet, result)
        self.assertEqual(
            {entry["classification"] for entry in packet["discrepancies"]},
            set(self.replan.CLASSIFICATION_ACTIONS),
        )
        self.assertTrue(all("issue_created" not in entry for entry in packet["discrepancies"]))
        self.assertEqual(result["decision"], "repair")
        self.assertEqual(result["revised_forecast"], packet["current_plan"]["wave_forecast"])
        rendered = self.replan.render_replan_markdown(packet, result)
        self.assertIn(result["wave_review_comment"], rendered)
        self.assertIn(result["revised_epic_body"], rendered)


class MissingExecutableRoleBehaviorTest(unittest.TestCase):
    def test_install_bundled_role_artifact_verifier_exists(self):
        self.assertTrue(
            ROLE_VERIFIER.is_file(),
            "missing executable installed-layout/run-artifact/pre-launch verifier",
        )


@unittest.skipUnless(ROLE_VERIFIER.is_file(), "awaiting executable G3 role verifier")
class InstalledIterativeRoleRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.skills_root = cls.root / "skills"
        cls.project = cls.root / "project"
        cls.project.mkdir()
        cls.installer = load_module("g3_install_constellation", ROOT / "scripts" / "install_constellation.py")
        selected = cls.installer.select_skills(
            ["explorer", "commander", "admiral", "to-initial-issues", "replan"],
            cls.installer.discover_skills(),
        )
        cls.installer.install_skills(
            selected,
            cls.skills_root,
            dry_run=False,
            force=False,
            full_set=False,
            restart_message="",
            out=lambda _: None,
            interpreter=cls.installer.InterpreterResolution(sys.executable, (sys.executable,), "probe"),
        )
        cls.roles = {
            "explorer": cls.skills_root / "constellation-explorer",
            "commander": cls.skills_root / "constellation-commander",
            "admiral": cls.skills_root / "constellation-admiral",
        }

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work_id = self._testMethodName.replace("test_", "run-")
        self.work_area = self.project / ".agent-work" / self.work_id
        self.work_area.mkdir(parents=True)

    def run_role(self, role: str, mode: str):
        helper = self.roles[role] / "scripts" / ROLE_VERIFIER.name
        self.assertTrue(helper.is_file(), f"{role} install omitted {ROLE_VERIFIER.name}")
        return subprocess.run(
            [sys.executable, str(helper), mode, "--work-id", self.work_id],
            cwd=self.project,
            capture_output=True,
            text=True,
        )

    def test_all_cross_skill_paths_resolve_in_real_installed_layout(self):
        explorer = load_json(self.roles["explorer"] / "templates" / "EXPLORER_SPINE.template.json")
        commander = load_json(self.roles["commander"] / "templates" / "COMMANDER_SPINE.template.json")
        admiral = load_json(self.roles["admiral"] / "templates" / "ADMIRAL_SPINE.template.json")
        checks = [
            (self.roles["explorer"], explorer["tasks"]["confirm"]["directives"]["shaped_brief"]["template"]),
            (self.roles["commander"], commander["tasks"]["execute"]["directives"]["replan_input"]["template"]),
            (self.roles["admiral"], admiral["tasks"]["execute"]["directives"]["wave_transition"]["input_template"]),
            (self.roles["admiral"], admiral["tasks"]["execute"]["directives"]["wave_transition"]["result_template"]),
        ]
        self.assertEqual(4, len(checks))
        for root, relative in checks:
            with self.subTest(relative=relative):
                self.assertTrue((root / relative).resolve().is_file())

    def test_explorer_confirm_refuses_missing_or_malformed_real_artifact(self):
        self.assertNotEqual(0, self.run_role("explorer", "explorer").returncode)
        output = self.work_area / "SHAPED_BRIEF.json"
        output.write_text('{"schema_version": 1}', encoding="utf-8", newline="\n")
        self.assertNotEqual(0, self.run_role("explorer", "explorer").returncode)
        shutil.copy2(
            self.skills_root / "constellation-to-initial-issues" / "templates" / "SHAPED_BRIEF.template.json",
            output,
        )
        self.assertEqual(0, self.run_role("explorer", "explorer").returncode)

    def test_commander_execute_refuses_missing_or_malformed_real_packet(self):
        self.assertNotEqual(0, self.run_role("commander", "commander").returncode)
        output = self.work_area / "REPLAN_INPUT.json"
        output.write_text('{"schema_version": 1}', encoding="utf-8", newline="\n")
        self.assertNotEqual(0, self.run_role("commander", "commander").returncode)
        shutil.copy2(
            self.skills_root / "constellation-replan" / "templates" / "REPLAN_INPUT.template.json",
            output,
        )
        self.assertEqual(0, self.run_role("commander", "commander").returncode)

    def test_admiral_prelaunch_refuses_until_transition_is_unique_verified_and_rendered(self):
        next_wave = {
            "boundary_id": "wave-1",
            "launch_id": "wave-2",
            "trigger": "wave_boundary",
        }
        (self.work_area / "NEXT_WAVE.json").write_text(
            json.dumps(next_wave), encoding="utf-8", newline="\n"
        )
        self.assertNotEqual(0, self.run_role("admiral", "admiral-prelaunch").returncode)

        transition = self.work_area / "transitions" / "wave-1"
        transition.mkdir(parents=True)
        shutil.copy2(
            self.skills_root / "constellation-replan" / "templates" / "REPLAN_INPUT.template.json",
            transition / "REPLAN_INPUT.json",
        )
        result_path = transition / "REPLAN_RESULT.json"
        shutil.copy2(
            self.skills_root / "constellation-replan" / "templates" / "REPLAN_RESULT.template.json",
            result_path,
        )
        audit_line = "- TRANSITION | boundary=wave-1 | decision=repair | verified"
        log_path = self.work_area / "ADMIRAL_LOG.md"
        log_path.write_text(audit_line + "\n", encoding="utf-8", newline="\n")

        broken = load_json(result_path)
        broken["revised_forecast"] = []
        result_path.write_text(json.dumps(broken), encoding="utf-8", newline="\n")
        self.assertNotEqual(0, self.run_role("admiral", "admiral-prelaunch").returncode)

        shutil.copy2(
            self.skills_root / "constellation-replan" / "templates" / "REPLAN_RESULT.template.json",
            result_path,
        )
        authorized = load_json(result_path)
        authorized["decision"] = "advance"
        result_path.write_text(json.dumps(authorized), encoding="utf-8", newline="\n")
        audit_line = "- TRANSITION | boundary=wave-1 | decision=advance | verified"
        log_path.write_text("", encoding="utf-8", newline="\n")
        with self.subTest(audit_cardinality="zero"):
            self.assertNotEqual(0, self.run_role("admiral", "admiral-prelaunch").returncode)
        log_path.write_text(audit_line + "\n" + audit_line + "\n", encoding="utf-8", newline="\n")
        with self.subTest(audit_cardinality="multiple"):
            self.assertNotEqual(0, self.run_role("admiral", "admiral-prelaunch").returncode)

        shutil.copy2(
            self.skills_root / "constellation-replan" / "templates" / "REPLAN_RESULT.template.json",
            result_path,
        )
        result = load_json(result_path)
        installed_replan = load_module(
            "g3_installed_verify_replan",
            self.skills_root / "constellation-replan" / "scripts" / "verify_replan.py",
        )
        source = load_json(transition / "REPLAN_INPUT.json")
        installed_replan.verify_replan_result(source, result)
        self.assertTrue(installed_replan.render_replan_markdown(source, result).strip())
        log_path.write_text(audit_line + "\n", encoding="utf-8", newline="\n")
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertNotEqual(0, refused.returncode, "repair cannot authorize NEXT_WAVE")

        advanced = copy.deepcopy(result)
        advanced["decision"] = "advance"
        result_path.write_text(json.dumps(advanced), encoding="utf-8", newline="\n")
        log_path.write_text(
            "- TRANSITION | boundary=wave-1 | decision=advance | verified\n",
            encoding="utf-8",
            newline="\n",
        )
        passed = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(0, passed.returncode, passed.stderr)

        replanned = copy.deepcopy(result)
        replanned["decision"] = "replan"
        result_path.write_text(json.dumps(replanned), encoding="utf-8", newline="\n")
        log_path.write_text(
            "- TRANSITION | boundary=wave-1 | decision=replan | verified\n",
            encoding="utf-8",
            newline="\n",
        )
        passed = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertEqual(
            replanned["revised_epic_body"].strip() + "\n",
            (transition / "CURRENT_TRUTH.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            replanned["wave_review_comment"].strip() + "\n",
            (transition / "WAVE_REVIEW.md").read_text(encoding="utf-8"),
        )

        inapplicable = copy.deepcopy(replanned)
        inapplicable["applicable"] = False
        inapplicable["material_changes"] = [
            {
                "surface": "intent_and_why",
                "before": "old",
                "after": "new",
                "reason": "evidence",
            }
        ]
        inapplicable["escalation"] = {
            "boundary": "intent_and_why",
            "proposed_value": "new intent",
            "reason": "human decision required",
            "authority_required": "human",
        }
        result_path.write_text(json.dumps(inapplicable), encoding="utf-8", newline="\n")
        log_path.write_text(
            "- TRANSITION | boundary=wave-1 | decision=replan | verified\n",
            encoding="utf-8",
            newline="\n",
        )
        refused = self.run_role("admiral", "admiral-prelaunch")
        with self.subTest(launch_authority="applicable:false"):
            self.assertNotEqual(0, refused.returncode, "applicable:false cannot authorize NEXT_WAVE")

        stopped = copy.deepcopy(replanned)
        stopped["decision"] = "stop"
        stopped["current_wave"] = None
        result_path.write_text(json.dumps(stopped), encoding="utf-8", newline="\n")
        log_path.write_text(
            "- TRANSITION | boundary=wave-1 | decision=stop | verified\n",
            encoding="utf-8",
            newline="\n",
        )
        refused = self.run_role("admiral", "admiral-prelaunch")
        with self.subTest(launch_authority="stop"):
            self.assertNotEqual(0, refused.returncode, "stop cannot authorize NEXT_WAVE")


def make_source_checkout(path: Path) -> Path:
    """A source-checkout shape: `scripts/` plus `skills/<name>/SKILL.md`, and --
    the point of the fixture -- no `SKILL.md` of its own at the top level."""
    (path / "scripts").mkdir(parents=True)
    shutil.copy2(ROLE_VERIFIER, path / "scripts" / ROLE_VERIFIER.name)
    (path / "skills" / "commander").mkdir(parents=True)
    (path / "skills" / "commander" / "SKILL.md").write_text(
        "# commander\n", encoding="utf-8", newline="\n"
    )
    return path


def install_bundles(dest: Path, names: list[str], module_name: str):
    installer = load_module(module_name, ROOT / "scripts" / "install_constellation.py")
    installer.install_skills(
        installer.select_skills(names, installer.discover_skills()),
        dest,
        dry_run=False,
        force=False,
        full_set=False,
        restart_message="",
        out=lambda _: None,
        interpreter=installer.InterpreterResolution(sys.executable, (sys.executable,), "probe"),
    )
    return installer


@unittest.skipUnless(ROLE_VERIFIER.is_file(), "awaiting executable G3 role verifier")
class GuardLocationStructureTests(unittest.TestCase):
    """The location guard decides "where am I running from" by structure, not by name.

    The old `startswith("constellation-")` test had two polarities. It wrongly
    ACCEPTED the source repo, which is itself named `constellation-skills`
    (#501, #468), and it wrongly REFUSED a Commander worktree, whose directory is
    not named `constellation-*` at all. Both are measured here on real trees.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.verifier = load_module("g1_guard_role_verifier", ROLE_VERIFIER)
        cls.skills_root = cls.root / "installed"
        install_bundles(
            cls.skills_root,
            ["commander", "to-initial-issues", "replan"],
            "g1_guard_install_constellation",
        )
        cls.installed_bundle = cls.skills_root / "constellation-commander"
        # Name-only decoy: named like a bundle and sitting in a real skills root,
        # but carrying no SKILL.md of its own.
        cls.decoy = cls.skills_root / "constellation-decoy"
        (cls.decoy / "scripts").mkdir(parents=True)
        cls.checkout = make_source_checkout(cls.root / "programs" / "constellation-skills")
        cls.worktree = make_source_checkout(
            cls.root / "constellation-skills-wt" / "epic418-w5-gates"
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def columns(self, path: Path) -> dict:
        """The three structural columns the predicate reads, measured on disk."""
        parent = path.parent
        return {
            "own_skill_md": (path / "SKILL.md").is_file(),
            "parent_corpus_json": (parent / self.verifier.CORPUS_MARKER).is_file(),
            "parent_bundle_siblings": sum(
                1 for child in parent.glob("constellation-*") if (child / "SKILL.md").is_file()
            ),
        }

    def test_guard_location_predicate_separates_the_three_real_locations(self):
        cases = [
            ("installed-bundle", self.installed_bundle, True),
            ("main-checkout", self.checkout, False),
            ("commander-worktree", self.worktree, False),
        ]
        self.assertEqual(3, len(cases))
        for label, path, expected in cases:
            with self.subTest(location=label, columns=self.columns(path)):
                self.assertTrue(path.is_dir(), f"{label} fixture was never built")
                self.assertEqual(expected, self.verifier._is_installed_bundle(path))
        installed = self.columns(self.installed_bundle)
        self.assertTrue(installed["own_skill_md"])
        # Assert what the sibling scan looped over: an empty scan would report
        # "not a skills root" without ever examining a bundle.
        self.assertGreaterEqual(installed["parent_bundle_siblings"], 3)
        self.assertTrue(self.verifier._is_skills_root(self.skills_root))
        for label, path in (("main-checkout", self.checkout), ("commander-worktree", self.worktree)):
            with self.subTest(not_a_skills_root=label):
                self.assertFalse(self.verifier._is_skills_root(path.parent))
        # The old name test is the thing being replaced: it disagrees on BOTH
        # of the two non-installed locations, in opposite directions.
        self.assertTrue(self.checkout.name.startswith("constellation-"))
        self.assertFalse(self.worktree.name.startswith("constellation-"))

    def test_guard_location_predicate_rejects_name_only_decoy(self):
        self.assertTrue(self.decoy.is_dir())
        # The decoy would pass the old guard on its name alone.
        self.assertTrue(self.decoy.name.startswith("constellation-"))
        # Clause 2 holds for it -- its parent IS a real skills root -- so clause 1
        # is the only thing rejecting it.
        self.assertTrue(self.verifier._is_skills_root(self.decoy.parent))
        self.assertFalse((self.decoy / "SKILL.md").is_file())
        self.assertFalse(self.verifier._is_installed_bundle(self.decoy))

    def test_guard_location_predicate_refuses_to_let_a_candidate_certify_itself(self):
        """A lone `constellation-*` bundle cannot vouch for its own parent.

        Regression guard for the self-match #501 would have returned through: the
        sibling scan runs on the PARENT, so unless the candidate is excluded, the
        second clause is satisfied by the candidate itself and the structural test
        decays into `startswith("constellation-")` plus a `SKILL.md` -- exactly the
        set the old name test wrongly accepted.
        """
        lonely = self.root / "self-certify" / "constellation-alone"
        lonely.mkdir(parents=True)
        (lonely / "SKILL.md").write_text("# alone\n", encoding="utf-8", newline="\n")

        # Nothing else marks the parent: no CORPUS.json, no other bundle.
        self.assertFalse((lonely.parent / self.verifier.CORPUS_MARKER).is_file())
        self.assertEqual([lonely], list(lonely.parent.glob("constellation-*")))
        # Unexcluded, the parent looks like a root -- solely because of the candidate.
        self.assertTrue(self.verifier._is_skills_root(lonely.parent))
        # Excluded, it does not, so the candidate is not an installed bundle.
        self.assertFalse(self.verifier._is_skills_root(lonely.parent, exclude=lonely))
        self.assertFalse(self.verifier._is_installed_bundle(lonely))

        # A genuine sibling is what makes the parent a real root, and then the
        # candidate IS accepted -- the exclusion narrows nothing it should not.
        sibling = lonely.parent / "constellation-sibling"
        sibling.mkdir()
        (sibling / "SKILL.md").write_text("# sibling\n", encoding="utf-8", newline="\n")
        self.assertTrue(self.verifier._is_installed_bundle(lonely))

    def test_guard_location_predicate_accepts_by_marker_not_by_name(self):
        """A bundle is accepted on structure even when nothing is named `constellation-*`."""
        marked = self.root / "marker-only"
        bundle = marked / "oddly-named-bundle"
        bundle.mkdir(parents=True)
        (bundle / "SKILL.md").write_text("# bundle\n", encoding="utf-8", newline="\n")
        self.assertFalse(self.verifier._is_skills_root(marked))
        (marked / self.verifier.CORPUS_MARKER).write_text(
            '{"corpus_id": "test"}\n', encoding="utf-8", newline="\n"
        )
        self.assertTrue(self.verifier._is_skills_root(marked))
        self.assertTrue(self.verifier._is_installed_bundle(bundle))
        self.assertEqual(0, sum(1 for _ in marked.glob("constellation-*")))


@unittest.skipUnless(ROLE_VERIFIER.is_file(), "awaiting executable G3 role verifier")
class GuardRuntimeTests(unittest.TestCase):
    """Resolution order, the `--skills-root` flag, the refusal, and the wrong-root mutation.

    The class name deliberately carries neither gate token, so `-k guard_location`
    and `-k guard_mutation` select on method names alone.

    Every run here shells out with HOME/USERPROFILE pointed at a temp home, so the
    developer's real `~/.claude/skills` can never leak in and make a probe pass.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.home = cls.root / "h"
        cls.user_skills = cls.home / ".claude" / "skills"
        install_bundles(
            cls.user_skills,
            ["commander", "to-initial-issues", "replan"],
            "g1_resolution_install_constellation",
        )
        cls.bundle_script = (
            cls.user_skills / "constellation-commander" / "scripts" / ROLE_VERIFIER.name
        )
        assert cls.bundle_script.is_file()
        # A detached copy of the same script in a Commander-worktree shape: not a
        # bundle, and not named `constellation-*` either.
        cls.detached = make_source_checkout(cls.root / "wt" / "epic418-w5-gates")
        cls.detached_script = cls.detached / "scripts" / ROLE_VERIFIER.name
        cls.bare_home = cls.root / "bare"
        cls.bare_home.mkdir()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work_id = self._testMethodName.replace("test_", "run-")

    def make_project(self, label: str) -> Path:
        project = self.root / "projects" / f"{label}-{self.work_id}"
        (project / ".agent-work" / self.work_id).mkdir(parents=True)
        return project

    def work_area(self, project: Path) -> Path:
        return project / ".agent-work" / self.work_id

    def seed(self, project: Path, mode: str) -> None:
        """Write the artifacts `mode` needs so the run reaches the skills root."""
        area = self.work_area(project)
        if mode == "explorer":
            shutil.copy2(
                self.user_skills
                / "constellation-to-initial-issues"
                / "templates"
                / "SHAPED_BRIEF.template.json",
                area / "SHAPED_BRIEF.json",
            )
            return
        replan_templates = self.user_skills / "constellation-replan" / "templates"
        if mode == "commander":
            shutil.copy2(replan_templates / "REPLAN_INPUT.template.json", area / "REPLAN_INPUT.json")
            return
        (area / "NEXT_WAVE.json").write_text(
            json.dumps({"boundary_id": "wave-1", "launch_id": "wave-2", "trigger": "wave_boundary"}),
            encoding="utf-8",
            newline="\n",
        )
        transition = area / "transitions" / "wave-1"
        transition.mkdir(parents=True)
        shutil.copy2(replan_templates / "REPLAN_INPUT.template.json", transition / "REPLAN_INPUT.json")
        result = load_json(replan_templates / "REPLAN_RESULT.template.json")
        result["decision"] = "advance"
        (transition / "REPLAN_RESULT.json").write_text(
            json.dumps(result), encoding="utf-8", newline="\n"
        )
        (area / "ADMIRAL_LOG.md").write_text(
            "- TRANSITION | boundary=wave-1 | decision=advance | verified\n",
            encoding="utf-8",
            newline="\n",
        )

    def run_verifier(self, script: Path, mode: str, project: Path, home: Path, skills_root=None):
        env = dict(os.environ)
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
        argv = [sys.executable, str(script), mode, "--work-id", self.work_id]
        if skills_root is not None:
            argv += ["--skills-root", str(skills_root)]
        return subprocess.run(argv, cwd=project, env=env, capture_output=True, text=True)

    def test_guard_location_resolution_uses_own_bundle_without_a_fallback_note(self):
        project = self.make_project("own-bundle")
        self.seed(project, "commander")
        run = self.run_verifier(self.bundle_script, "commander", project, self.bare_home)
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertNotIn("note:", run.stderr)

    def test_guard_location_resolution_probes_project_scope_before_user_scope(self):
        """Project scope wins over user scope -- proved by behaviour, not by the note.

        The project-scope root is a marker-only decoy holding no bundles, so if the
        project scope really wins the run fails naming a verifier UNDER THAT ROOT.
        The user-scope root is the real install, which would have succeeded.
        """
        project = self.make_project("project-scope")
        self.seed(project, "commander")
        project_root = project / ".claude" / "skills"
        project_root.mkdir(parents=True)
        (project_root / "CORPUS.json").write_text(
            '{"corpus_id": "decoy"}\n', encoding="utf-8", newline="\n"
        )
        run = self.run_verifier(self.detached_script, "commander", project, self.home)
        self.assertNotEqual(0, run.returncode, run.stdout)
        self.assertIn(str(project_root), run.stderr)
        self.assertNotIn(str(self.user_skills / "constellation-replan"), run.stderr)
        self.assertIn("note:", run.stderr)

    def test_guard_location_resolution_falls_back_to_user_scope_with_a_visible_note(self):
        project = self.make_project("user-scope")
        self.seed(project, "commander")
        self.assertFalse((project / ".claude" / "skills").exists())
        run = self.run_verifier(self.detached_script, "commander", project, self.home)
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertIn("note:", run.stderr)
        self.assertIn(str(self.user_skills), run.stderr)

    def test_guard_location_resolution_refusal_names_the_problem_and_every_root_tried(self):
        project = self.make_project("no-root")
        self.seed(project, "commander")
        run = self.run_verifier(self.detached_script, "commander", project, self.bare_home)
        self.assertEqual(1, run.returncode, run.stdout)
        self.assertIn("REFUSED:", run.stderr)
        # It names the REAL problem, not the old wrong one.
        self.assertIn("cannot locate an installed constellation skills root", run.stderr)
        self.assertNotIn("must run from an installed constellation-* skill", run.stderr)
        self.assertNotIn("installed public verifier is missing", run.stderr)
        stated, listing = run.stderr.split("Roots tried (", 1)[1].split("): ", 1)
        roots = [entry.strip() for entry in listing.strip().splitlines()[0].split(";")]
        self.assertEqual(int(stated), len(roots))
        self.assertEqual(3, len(roots))
        expected = [
            # the root the script's own location would have implied, then the two
            # install scopes, project before user
            self.detached.parent,
            project / ".claude" / "skills",
            self.bare_home / ".claude" / "skills",
        ]
        self.assertEqual([str(path) for path in expected], roots)

    def test_guard_location_flag_wins_and_is_reachable_from_all_three_modes(self):
        modes = ["explorer", "commander", "admiral-prelaunch"]
        self.assertEqual(3, len(modes))
        for mode in modes:
            project = self.make_project(mode)
            self.seed(project, mode)
            with self.subTest(mode=mode, flag="absent"):
                without = self.run_verifier(self.detached_script, mode, project, self.bare_home)
                self.assertNotEqual(0, without.returncode)
                self.assertIn("cannot locate an installed constellation skills root", without.stderr)
            with self.subTest(mode=mode, flag="present"):
                with_flag = self.run_verifier(
                    self.detached_script, mode, project, self.bare_home, skills_root=self.user_skills
                )
                self.assertEqual(0, with_flag.returncode, with_flag.stderr)

    def test_guard_location_flag_beats_an_otherwise_resolvable_root(self):
        """`--skills-root` wins even when autodetection would have found something."""
        project = self.make_project("flag-wins")
        self.seed(project, "commander")
        wrong = self.root / "flag-wins-root"
        (wrong / "constellation-explorer").mkdir(parents=True)
        (wrong / "constellation-explorer" / "SKILL.md").write_text(
            "# explorer\n", encoding="utf-8", newline="\n"
        )
        # The bundle copy would resolve its own parent; the flag overrides that.
        run = self.run_verifier(
            self.bundle_script, "commander", project, self.home, skills_root=wrong
        )
        self.assertNotEqual(0, run.returncode, run.stdout)
        self.assertIn(str(wrong / "constellation-replan"), run.stderr)

    def test_guard_mutation_wrong_skills_root_drives_the_acceptance_check_red(self):
        """Point the resolver at a plausible-but-wrong root; acceptance must go RED.

        The wrong root is not obviously broken: it satisfies the skills-root test,
        so nothing upstream of the load rejects it. It simply is not the root that
        holds the verifiers this run needs -- which is exactly the shape of #501's
        original wrong-accept, where `C:/Programs` was resolved as a skills root.
        """
        wrong = self.root / "mutation-wrong-root"
        (wrong / "constellation-explorer").mkdir(parents=True)
        (wrong / "constellation-explorer" / "SKILL.md").write_text(
            "# explorer\n", encoding="utf-8", newline="\n"
        )
        # Assert the mutation applied: the wrong root IS plausible, and IS missing
        # the verifiers. A mutation that never took would leave a green run that
        # reads exactly like a working guard.
        verifier = load_module("g1_mutation_role_verifier", ROLE_VERIFIER)
        self.assertTrue(verifier._is_skills_root(wrong))
        missing = {
            "explorer": wrong / "constellation-to-initial-issues" / "scripts" / "verify_issue_set.py",
            "commander": wrong / "constellation-replan" / "scripts" / "verify_replan.py",
            "admiral-prelaunch": wrong / "constellation-replan" / "scripts" / "verify_replan.py",
        }
        for mode, absent in missing.items():
            self.assertFalse(absent.exists(), f"{mode} target must be absent from the wrong root")
            self.assertTrue(
                (self.user_skills / absent.relative_to(wrong)).is_file(),
                f"{mode} target must be present in the correct root",
            )

        self.assertEqual(3, len(missing))
        for mode, absent in missing.items():
            project = self.make_project(f"mutation-{mode}")
            self.seed(project, mode)
            with self.subTest(mode=mode, root="correct"):
                green = self.run_verifier(
                    self.detached_script, mode, project, self.bare_home, skills_root=self.user_skills
                )
                self.assertEqual(0, green.returncode, green.stderr)
            with self.subTest(mode=mode, root="wrong"):
                red = self.run_verifier(
                    self.detached_script, mode, project, self.bare_home, skills_root=wrong
                )
                self.assertEqual(1, red.returncode, "acceptance must not survive a wrong root")
                self.assertIn("installed public verifier is missing", red.stderr)
                self.assertIn(str(absent), red.stderr)

    def test_guard_location_flag_refuses_a_path_that_is_not_a_directory(self):
        project = self.make_project("bad-flag")
        self.seed(project, "commander")
        missing = self.root / "nope"
        run = self.run_verifier(
            self.detached_script, "commander", project, self.bare_home, skills_root=missing
        )
        self.assertEqual(1, run.returncode, run.stdout)
        self.assertIn("--skills-root is not a directory", run.stderr)
        self.assertIn(str(missing), run.stderr)


if __name__ == "__main__":
    unittest.main()
