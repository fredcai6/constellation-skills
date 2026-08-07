"""Parsed role-doctrine invariants for the G1 -> G2 iterative planning chain."""

from __future__ import annotations

import copy
import importlib.util
import json
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


if __name__ == "__main__":
    unittest.main()
