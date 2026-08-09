"""Parsed role-doctrine invariants for the G1 -> G2 iterative planning chain."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
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
# The epic's own terminal transition, tracked in git. Copied -- never mutated --
# so the stop golden path is measured against a packet a real Admiral wrote
# rather than a template with one field edited.
LIVE_STOP_TRANSITION = ROOT / ".agent-work" / "epic-418-redux" / "transitions" / "w4-to-close"


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
        verified_stop = self.run_role("admiral", "admiral-prelaunch")
        with self.subTest(launch_authority="stop"):
            # Inverted by #506, and the inversion IS the fix rather than a check
            # bent to fit it. The old expectation encoded the conflation this
            # issue removes: that a decision authorizing no launch could not be
            # verified either. What is asserted now is the corrected contract --
            # a stop transition passes pre-launch, having authorized nothing.
            self.assertEqual(0, verified_stop.returncode, verified_stop.stderr)

    def seed_stop_boundary(self, launch_id):
        """Seed a boundary whose transition is a real, verified `stop`.

        The packet pair is copied from the live epic's own terminal transition,
        so the golden path below is measured against output a real Admiral
        produced. `launch_id` is the caller's variable because whether a stop may
        leave it unset is precisely what is under test.
        """
        (self.work_area / "NEXT_WAVE.json").write_text(
            json.dumps({"boundary_id": "wave-1", "launch_id": launch_id, "trigger": "wave_boundary"}),
            encoding="utf-8",
            newline="\n",
        )
        transition = self.work_area / "transitions" / "wave-1"
        transition.mkdir(parents=True)
        for name in ("REPLAN_INPUT.json", "REPLAN_RESULT.json"):
            shutil.copy2(LIVE_STOP_TRANSITION / name, transition / name)
        result = load_json(transition / "REPLAN_RESULT.json")
        self.assertEqual("stop", result["decision"], "live fixture must really be a stop")
        self.assertIs(True, result["applicable"], "live fixture must be an applicable stop")
        log_path = self.work_area / "ADMIRAL_LOG.md"
        log_path.write_text(
            "- TRANSITION | boundary=wave-1 | decision=stop | verified\n",
            encoding="utf-8",
            newline="\n",
        )
        return transition, result, log_path

    def test_admiral_prelaunch_stop_boundary_verifies_a_transition_that_authorizes_no_launch(self):
        """A stop is verified, not merely refused, and may say no launch follows.

        Verification and authorization are different jobs; the old verifier did
        both in one clause and so could not express "this transition is sound and
        it ends the epic" (#506). Under stop the authorization clause is skipped,
        which is what lets `NEXT_WAVE.launch_id` be null. Everything else still
        has to run -- G2, the unique audit match, the render, and both Markdown
        writes -- and the writes are asserted here because they are the only
        observable proof that the run reached the end rather than short-circuiting.
        """
        transition, result, _ = self.seed_stop_boundary(None)
        passed = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertEqual(
            result["revised_epic_body"].strip() + "\n",
            (transition / "CURRENT_TRUTH.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            result["wave_review_comment"].strip() + "\n",
            (transition / "WAVE_REVIEW.md").read_text(encoding="utf-8"),
        )

    def test_admiral_prelaunch_stop_boundary_permits_but_does_not_require_a_null_launch_id(self):
        """"May express no launch authorized" is permission, not obligation.

        Every boundary already on disk carries a populated `launch_id`, so a stop
        that leaves one there must still verify -- the verifier never reads it for
        anything but path safety. Path safety is not part of the relaxation,
        though: an unsafe `launch_id` must still be refused under stop, which is
        the second half of this test.
        """
        transition, _, _ = self.seed_stop_boundary("wave-2")
        passed = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertTrue((transition / "WAVE_REVIEW.md").is_file())

        (self.work_area / "NEXT_WAVE.json").write_text(
            json.dumps({"boundary_id": "wave-1", "launch_id": "../escape", "trigger": "wave_boundary"}),
            encoding="utf-8",
            newline="\n",
        )
        refused = self.run_role("admiral", "admiral-prelaunch")
        self.assertNotEqual(0, refused.returncode, "stop must not smuggle an unsafe launch_id past the guard")
        self.assertIn("launch_id contains unsafe path characters", refused.stderr)

    def test_admiral_prelaunch_stop_mutation_every_surviving_requirement_still_goes_red(self):
        """The stop relaxation is narrow: only the authorization clause is skipped.

        A relaxation is worth only what it declined to relax, so every
        requirement that must survive a stop is broken here in turn and the run
        has to refuse for that exact reason. Each mutation asserts it really
        applied before asserting the refusal, because a mutation that never took
        would leave a red that proves nothing -- and each asserts the two
        Markdown files were not written, which is where a refusal that arrived
        too late would show up.

        The last case is the one that guards this change specifically: a `repair`
        with no launch named must still be refused. A stop skipping the
        authorization clause must not become "anything with a null launch_id
        skips it."
        """
        transition, _, log_path = self.seed_stop_boundary(None)
        next_wave_path = self.work_area / "NEXT_WAVE.json"
        source_path = transition / "REPLAN_INPUT.json"
        result_path = transition / "REPLAN_RESULT.json"
        replan_bundle = self.skills_root / "constellation-replan"
        # In `pristine` so the per-subtest restore loop resets it like any other
        # mutated input -- the render mutation degrades code, not packet data.
        renderer_path = replan_bundle / "scripts" / "verify_replan.py"
        pristine = {
            path: path.read_text(encoding="utf-8")
            for path in (next_wave_path, source_path, result_path, log_path, renderer_path)
        }
        written = (transition / "CURRENT_TRUTH.md", transition / "WAVE_REVIEW.md")
        replan_templates = replan_bundle / "templates"

        control = self.run_role("admiral", "admiral-prelaunch")
        self.assertEqual(0, control.returncode, control.stderr)
        for path in written:
            self.assertTrue(path.is_file(), "the control run must reach the writes")

        stop_audit = "- TRANSITION | boundary=wave-1 | decision=stop | verified\n"

        def write(path: Path, text: str) -> None:
            path.write_text(text, encoding="utf-8", newline="\n")

        def audit_decision_mismatch():
            write(log_path, "- TRANSITION | boundary=wave-1 | decision=advance | verified\n")
            self.assertNotIn("decision=stop", log_path.read_text(encoding="utf-8"))

        def audit_entry_absent():
            write(log_path, "")
            self.assertEqual("", log_path.read_text(encoding="utf-8"))

        def audit_entry_duplicated():
            write(log_path, stop_audit * 2)
            self.assertEqual(2, log_path.read_text(encoding="utf-8").count("TRANSITION"))

        def packet_fails_g2():
            # Blanking `revised_epic_body` rather than emptying `revised_forecast`:
            # an empty forecast is legitimate for a stop -- the epic ends, so
            # nothing is forecast -- and the packet stays G2-valid, which would
            # have made this mutation a no-op. This field is the one CURRENT_TRUTH.md
            # is written from, so breaking it is both a real G2 break and the one
            # a stop cannot shrug off.
            broken = json.loads(pristine[result_path])
            broken["revised_epic_body"] = "   "
            write(result_path, json.dumps(broken))
            self.assertFalse(load_json(result_path)["revised_epic_body"].strip())

        def packet_is_inapplicable():
            inapplicable = json.loads(pristine[result_path])
            inapplicable["applicable"] = False
            write(result_path, json.dumps(inapplicable))
            self.assertIs(False, load_json(result_path)["applicable"])

        def boundary_id_is_unsafe():
            write(
                next_wave_path,
                json.dumps({"boundary_id": "../escape", "launch_id": None, "trigger": "wave_boundary"}),
            )
            self.assertEqual("../escape", load_json(next_wave_path)["boundary_id"])

        def repair_names_no_launch():
            shutil.copy2(replan_templates / "REPLAN_INPUT.template.json", source_path)
            shutil.copy2(replan_templates / "REPLAN_RESULT.template.json", result_path)
            write(log_path, "- TRANSITION | boundary=wave-1 | decision=repair | verified\n")
            self.assertEqual("repair", load_json(result_path)["decision"])
            self.assertIsNone(load_json(next_wave_path)["launch_id"])

        def renderer_returns_empty():
            # The render leg. Without this case a stop-shortcut that skipped the
            # render entirely left this test GREEN -- found by the g2 reviewer,
            # which is the one thing the docstring above promised could not happen.
            # Degrading the INSTALLED renderer is the discriminating probe: the
            # packet cannot express "the renderer failed", so no data mutation
            # reaches this clause.
            source = renderer_path.read_text(encoding="utf-8")
            marker = "def render_replan_markdown("
            self.assertIn(marker, source)
            head, _, tail = source.partition(marker)
            signature, _, body = tail.partition("\n")
            write(renderer_path, f'{head}{marker}{signature}\n    return ""\n{body}')
            self.assertIn('return ""', renderer_path.read_text(encoding="utf-8"))

        mutations = {
            "audit_decision_mismatch": (audit_decision_mismatch, "verified TRANSITION audit decision must match"),
            "audit_entry_absent": (audit_entry_absent, "must have exactly one verified TRANSITION audit entry"),
            "audit_entry_duplicated": (audit_entry_duplicated, "must have exactly one verified TRANSITION audit entry"),
            "packet_fails_g2": (packet_fails_g2, "Admiral transition violates G2"),
            "packet_is_inapplicable": (packet_is_inapplicable, "inapplicable transition cannot authorize NEXT_WAVE"),
            "boundary_id_is_unsafe": (boundary_id_is_unsafe, "boundary_id contains unsafe path characters"),
            "repair_names_no_launch": (repair_names_no_launch, "only advance or replan may authorize NEXT_WAVE"),
            "renderer_returns_empty": (renderer_returns_empty, "Admiral transition renderer returned empty Markdown"),
        }
        self.assertEqual(8, len(mutations))

        # `finally`, not just the head of the next iteration: the last mutation
        # would otherwise still be in force when this test returns. That is inert
        # for the mutations that touch packet data (the per-test work area goes
        # away), but `renderer_returns_empty` degrades the shared per-class
        # installed bundle, and a later test in this class asserting a REFUSAL
        # would then pass for the wrong reason.
        try:
            for label, (mutate, expected) in mutations.items():
                with self.subTest(mutation=label):
                    for path, text in pristine.items():
                        write(path, text)
                    for path in written:
                        path.unlink(missing_ok=True)
                    mutate()
                    red = self.run_role("admiral", "admiral-prelaunch")
                    self.assertEqual(1, red.returncode, red.stdout)
                    self.assertIn(expected, red.stderr)
                    for path in written:
                        self.assertFalse(path.is_file(), f"{label} must refuse before the transition is written")
        finally:
            for path, text in pristine.items():
                write(path, text)
            self.assertNotIn('return ""', renderer_path.read_text(encoding="utf-8"))


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


# --- archive.c2b reachability (#439, #484) -----------------------------------
#
# The Commander spine's `archive` step asserts the run is REACHABLE. Its check is
# a `command` condition, so per docs/CHECKLIST_SCHEMA.md the ENGINE'S VERDICT IS
# THE EXIT CODE and stdout is discarded. Three properties therefore have to hold
# at once, and the tests below exercise all three against the SHIPPED text:
#
#   1. the branch is derived at check time (no unsubstituted placeholder can ship;
#      `<branch>` is not a resolver-owned token, so instantiation cannot catch it),
#   2. a MERGED pull request counts as reachable, a CLOSED-unmerged one does not,
#   3. the count comparison happens IN THE SHELL, because `gh --jq 'length > 0'`
#      prints `true`/`false` while `gh` exits 0 either way.
#
# No test in this repo may reach the network, so `gh` is stubbed. The stub models
# gh's observable contract for this one call and REFUSES (nonzero, loudly) any
# flag, field or `--jq` expression it does not model — so a future edit to the
# check text cannot silently drift into a shape the stub waves through. Note in
# particular that the stub derives its filtering FROM the `--jq` text it is
# handed, rather than hardcoding the expected answer: that is what keeps the jq
# expression itself load-bearing here.
#
# NOT proven by these tests, stated plainly: the `--jq` expression's behaviour
# under gh's real embedded gojq. There is no `jq` on PATH to delegate to and
# `gh` cannot evaluate a filter offline, so the expression is exercised against
# the stub's modelled subset (`.field == "literal"` atoms joined by ` or `/` and `,
# wrapped in `[.[] | select(...)] | length`, plus the bare `length` and
# `length > N` forms). Anything outside that subset refuses rather than passes.

GH_STUB_SOURCE = r'''"""Offline stand-in for `gh pr list` (archive.c2b reachability tests).

Models only what the shipped check calls and refuses everything else, so the
check text cannot drift into a shape this stub silently accepts.
"""
import json
import os
import re
import sys

ATOM = re.compile(r'^\.([A-Za-z_][A-Za-z0-9_]*)\s*==\s*"([^"]*)"$')
SELECT_LENGTH = re.compile(r'^\[\s*\.\[\]\s*\|\s*select\((.*)\)\s*\]\s*\|\s*length$', re.S)
LENGTH_GT = re.compile(r'^length\s*>\s*(\d+)$')


def refuse(message):
    sys.stderr.write("gh-stub refuses: " + message + "\n")
    raise SystemExit(3)


def compile_condition(text):
    """Compile a jq select() body into a predicate over one PR dict."""
    def atom(part):
        match = ATOM.match(part.strip())
        if not match:
            refuse("unmodelled jq select atom: " + part.strip())
        field, value = match.group(1), match.group(2)
        return lambda pr: pr.get(field) == value

    clauses = [
        [atom(piece) for piece in or_part.split(" and ")]
        for or_part in text.split(" or ")
    ]
    return lambda pr: any(all(f(pr) for f in clause) for clause in clauses)


def apply_jq(expr, rows):
    expr = expr.strip()
    match = SELECT_LENGTH.match(expr)
    if match:
        keep = compile_condition(match.group(1))
        return str(sum(1 for pr in rows if keep(pr)))
    if expr == "length":
        return str(len(rows))
    match = LENGTH_GT.match(expr)
    if match:
        return "true" if len(rows) > int(match.group(1)) else "false"
    refuse("unmodelled --jq expression: " + expr)


def main(argv):
    if argv[:2] != ["pr", "list"]:
        refuse("only `gh pr list` is modelled, got: " + " ".join(argv))
    opts = {}
    index = 2
    while index < len(argv):
        flag = argv[index]
        if not flag.startswith("--"):
            refuse("unexpected positional argument: " + flag)
        if index + 1 >= len(argv):
            refuse("flag with no value: " + flag)
        opts[flag] = argv[index + 1]
        index += 2
    for required in ("--head", "--state", "--json"):
        if required not in opts:
            refuse("missing required flag " + required)

    fixture = json.loads(os.environ["GH_STUB_PRS"])
    rows = [{"state": state} for state in fixture.get(opts["--head"], [])]

    wanted = opts["--state"]
    if wanted == "all":
        pass
    elif wanted == "open":
        rows = [row for row in rows if row["state"] == "OPEN"]
    elif wanted == "closed":
        rows = [row for row in rows if row["state"] in ("CLOSED", "MERGED")]
    elif wanted == "merged":
        rows = [row for row in rows if row["state"] == "MERGED"]
    else:
        refuse("unmodelled --state: " + wanted)

    if opts["--json"].split(",") != ["state"]:
        refuse("only `--json state` is modelled, got: " + opts["--json"])

    if "--jq" in opts:
        sys.stdout.write(apply_jq(opts["--jq"], rows) + "\n")
    else:
        sys.stdout.write(json.dumps(rows) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

GIT_STUB_SOURCE = r'''"""Offline stand-in for the one `git` call the archive.c2b check makes."""
import os
import sys

argv = sys.argv[1:]
if not (argv[:1] == ["-C"] and argv[2:] == ["rev-parse", "--abbrev-ref", "HEAD"]):
    sys.stderr.write("git-stub refuses: unmodelled invocation: " + " ".join(argv) + "\n")
    raise SystemExit(3)
if not os.path.isdir(argv[1]):
    sys.stderr.write("git-stub refuses: -C path is not a directory: " + argv[1] + "\n")
    raise SystemExit(3)
sys.stdout.write(os.environ["GIT_STUB_BRANCH"] + "\n")
'''


class ArchiveReachabilityRuntimeTests(unittest.TestCase):
    """Exit-code behaviour of the shipped `archive.c2b` check text.

    The class name deliberately carries neither gate token, so `-k archive_c2b`
    and `-k archive_mutation` select on method names alone.

    The check text is never retyped here: every run resolves the real template
    through the real resolver and reads the command out of the resolved JSON, so
    a byte-identical template cannot close these tests green.
    """

    STUB_BRANCH = "epic-418/reachability-probe"

    @classmethod
    def setUpClass(cls):
        cls.engine = load_module("checklist_engine_for_archive_c2b", ROOT / "scripts" / "checklist_engine.py")
        cls.resolver = load_module("init_work_area_for_archive_c2b", ROOT / "scripts" / "init_work_area.py")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.stub_dir = Path(cls.tmp.name) / "bin"
        cls.stub_dir.mkdir(parents=True)
        gh_stub = Path(cls.tmp.name) / "gh_stub.py"
        git_stub = Path(cls.tmp.name) / "git_stub.py"
        gh_stub.write_text(GH_STUB_SOURCE, encoding="utf-8", newline="\n")
        git_stub.write_text(GIT_STUB_SOURCE, encoding="utf-8", newline="\n")
        interpreter = Path(sys.executable).as_posix()
        for name, script in (("gh", gh_stub), ("git", git_stub)):
            shim = cls.stub_dir / name
            shim.write_text(
                f'#!/bin/sh\nexec "{interpreter}" "{script.as_posix()}" "$@"\n',
                encoding="utf-8",
                newline="\n",
            )
            os.chmod(shim, 0o755)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def resolved_c2b(cls) -> str:
        """The archive.c2b check command, read out of the real resolved template."""
        resolved = cls.resolver.resolve_spine(
            COMMANDER_SPINE.read_text(encoding="utf-8"),
            "archive-c2b-probe",
            None,
            ROOT,
        )
        archive = json.loads(resolved)["tasks"]["archive"]
        for cond in archive["postconditions"]:
            if cond["id"] == "c2b":
                return cond["check"]["command"]
        raise AssertionError("archive has no c2b postcondition")

    def run_command(self, command: str, prs: dict, branch: str | None = None):
        """Run `command` through the ENGINE'S OWN POSIX-shell runner, with the
        stubs early on PATH. Using the engine's runner rather than a private
        subprocess call is the point: the verdict measured here is the verdict
        the engine would record."""
        saved = dict(os.environ)
        try:
            os.environ["PATH"] = str(self.stub_dir) + os.pathsep + os.environ.get("PATH", "")
            os.environ["GH_STUB_PRS"] = json.dumps(prs)
            os.environ["GIT_STUB_BRANCH"] = branch or self.STUB_BRANCH
            proc, marker = self.engine._run_check_command(command)
        finally:
            os.environ.clear()
            os.environ.update(saved)
        # A missing POSIX shell would make every check "fail" for a reason that
        # has nothing to do with reachability; refuse to read that as evidence.
        self.assertEqual("posix", marker, "these tests require the engine's POSIX shell")
        return proc

    def test_archive_c2b_ships_no_unresolved_placeholder(self):
        """Defect 1: `<branch>` is not resolver-owned, so nothing else catches it.

        `_assert_no_resolver_placeholders` only guards the token families the
        resolver owns, so a `<branch>` left in a check command instantiates
        cleanly and fails at run time. This is the regression floor for that.
        """
        command = self.resolved_c2b()
        leftovers = re.findall(r"<[a-zA-Z][a-zA-Z0-9_-]*>", command)
        self.assertEqual([], leftovers, f"archive.c2b ships an unsubstituted token: {command}")

    def test_archive_c2b_derives_the_branch_from_the_real_repository(self):
        """The derivation is real: run it here, against this checkout, no stub.

        Proves the `git -C <repo-root> rev-parse` fragment inside the shipped
        command actually yields this worktree's branch — the thing the literal
        `<branch>` never did.
        """
        command = self.resolved_c2b()
        match = re.search(r'\$\((git -C [^)]+ rev-parse --abbrev-ref HEAD)\)', command)
        self.assertIsNotNone(match, f"archive.c2b derives no branch: {command}")
        derived = subprocess.run(
            [self.engine._find_posix_shell(), "-c", match.group(1)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, derived.returncode, derived.stderr)
        expected = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, expected.returncode, expected.stderr)
        self.assertEqual(expected.stdout.strip(), derived.stdout.strip())
        self.assertTrue(derived.stdout.strip(), "the derivation returned an empty branch")

    def test_archive_c2b_four_pr_states_decide_reachability_by_exit_code(self):
        """no-PR and CLOSED-unmerged must FAIL; OPEN and MERGED must PASS.

        Defect 2 is the MERGED leg: a merged pull request is reachable work, and
        the shipped `--state open` check called it unreachable. The no-PR leg is
        the one the old `--jq 'length > 0'` form could never fail, because `gh`
        exits 0 whether it printed `true` or `false`.
        """
        command = self.resolved_c2b()
        branch = self.STUB_BRANCH
        cases = (
            ("no-PR", {}, False),
            ("OPEN", {branch: ["OPEN"]}, True),
            ("MERGED", {branch: ["MERGED"]}, True),
            ("CLOSED-unmerged", {branch: ["CLOSED"]}, False),
        )
        for label, prs, reachable in cases:
            with self.subTest(state=label):
                proc = self.run_command(command, prs)
                if reachable:
                    self.assertEqual(
                        0, proc.returncode, f"{label} is reachable: {proc.stdout}{proc.stderr}"
                    )
                else:
                    self.assertNotEqual(
                        0, proc.returncode, f"{label} is NOT reachable: {proc.stdout}{proc.stderr}"
                    )

    def test_archive_c2b_a_merged_pr_alone_satisfies_the_check(self):
        """The narrow statement of defect 2, isolated from the rest of the matrix.

        A branch whose ONLY pull request is merged is reachable. Kept separate
        because it is the single behaviour change #439 asks for, and a matrix
        subtest that silently stopped running would not be noticed here.
        """
        proc = self.run_command(self.resolved_c2b(), {self.STUB_BRANCH: ["MERGED"]})
        self.assertEqual(0, proc.returncode, f"{proc.stdout}{proc.stderr}")

    def test_archive_mutation_reintroduced_defects_all_drive_the_check_red(self):
        """Each reintroduced defect must break the check, and each leg is paired.

        Every leg asserts three things: the mutation really applied to the text,
        the mutated command gives the wrong verdict, and THE UNMUTATED COMMAND
        GIVES THE RIGHT ONE ON THE IDENTICAL FIXTURE. The third assertion is what
        stops a leg being a no-op — a mutation that "fails" on a fixture where
        the real command also fails proves nothing. Each leg's own no-op
        condition is named in its comment.
        """
        command = self.resolved_c2b()
        branch = self.STUB_BRANCH
        merged = {branch: ["MERGED"]}
        opened = {branch: ["OPEN"]}
        closed = {branch: ["CLOSED"]}
        no_pr: dict = {}

        derivation = re.search(r'"\$\(git -C [^)]+ rev-parse --abbrev-ref HEAD\)"', command)
        self.assertIsNotNone(derivation, f"archive.c2b derives no branch: {command}")
        derivation_text = derivation.group(0)

        # The pre-#439 shape, DERIVED from the shipped text rather than retyped:
        # unwrap the shell comparison and put the boolean filter back. Retyping it
        # would test a string this repo does not ship.
        unwrapped = re.match(r'^test "\$\((?P<inner>.+)\)" -gt 0$', command)
        self.assertIsNotNone(unwrapped, f"archive.c2b does not compare in the shell: {command}")
        boolean_form, swaps = re.subn(
            r"--jq '.*'$", "--jq 'length > 0'", unwrapped.group("inner")
        )
        self.assertEqual(1, swaps, "could not derive the stdout-verdict form")

        # (label, mutated text, fixture, control exits 0?, mutant exits 0?)
        legs = (
            # No-op if: the unmutated command also failed on an OPEN pull request
            # -- i.e. if the check were broken for every state. The control leg
            # rules that out. `<branch>` unquoted is ALSO a shell redirection, so
            # this leg fails before `gh` is ever reached; the quoted leg below is
            # the one that proves the branch VALUE is load-bearing.
            ("literal <branch> token, exactly as shipped",
             command.replace(derivation_text, "<branch>"), opened, True, False),
            # No-op if: the stub ignored `--head`, or the fixture answered for
            # every branch. The stub keys strictly on `--head`, and the control
            # leg passes on the same fixture, so neither holds.
            ("quoted literal branch that matches nothing",
             command.replace(derivation_text, '"<branch>"'), opened, True, False),
            # No-op if: run on a fixture holding an OPEN pull request, where
            # `--state open` and `--state all` agree. MERGED is the fixture that
            # separates them.
            ("--state narrowed back to open",
             command.replace("--state all", "--state open"), merged, True, False),
            # No-op if: the stub ignored the `--jq` text. It does not -- it
            # compiles the select() body into its predicate, so dropping the
            # MERGED arm really changes the count.
            ("MERGED dropped from the selector",
             command.replace(' or .state == "MERGED"', ""), merged, True, False),
            # The inverse: widening the selector must not make a closed-unmerged
            # branch look reachable. No-op if: run on any fixture without a
            # CLOSED pull request.
            ("CLOSED widened into the selector",
             command.replace('.state == "MERGED"', '.state == "MERGED" or .state == "CLOSED"'),
             closed, False, True),
            # The exit-code property, and the reason the whole shape is a shell
            # comparison. No-op if: run on a fixture WITH a reachable pull request
            # -- there the real command exits 0 too and the leg shows nothing. It
            # must run on a fixture with nothing reachable.
            ("verdict carried by stdout instead of the exit code",
             boolean_form, no_pr, False, True),
        )

        for label, mutated, prs, control_passes, mutant_passes in legs:
            with self.subTest(mutation=label):
                self.assertNotEqual(command, mutated, "the mutation did not apply")
                control = self.run_command(command, prs)
                mutant = self.run_command(mutated, prs)
                # The control leg is what stops this being a no-op: without it a
                # mutation could "fail" for a reason the real command shares.
                if control_passes:
                    self.assertEqual(
                        0, control.returncode,
                        f"control must pass on {prs}: {control.stdout}{control.stderr}",
                    )
                else:
                    self.assertNotEqual(
                        0, control.returncode,
                        f"control must fail on {prs}: {control.stdout}{control.stderr}",
                    )
                if mutant_passes:
                    self.assertEqual(
                        0, mutant.returncode,
                        f"{label} must WRONGLY pass: {mutant.stdout}{mutant.stderr}",
                    )
                else:
                    self.assertNotEqual(
                        0, mutant.returncode,
                        f"{label} must drive the check RED: {mutant.stdout}{mutant.stderr}",
                    )
                # Belt and braces: control and mutant must DISAGREE, or the leg
                # measured nothing at all.
                self.assertNotEqual(
                    control.returncode == 0, mutant.returncode == 0,
                    f"{label} is a no-op: it agrees with the real check",
                )

    def test_archive_mutation_the_stub_refuses_an_unmodelled_check_shape(self):
        """The stub cannot silently wave through a check text it does not model.

        Without this, every test above would be worth only as much as the stub's
        coverage, and a future edit to the check could drift into an unmodelled
        shape that the stub answered for anyway. Refusal is nonzero, which reads
        as an unreachable verdict -- fail visibly, never a quiet pass.
        """
        command = self.resolved_c2b()
        unmodelled = (
            command.replace("--json state", "--json number,state"),
            command.replace('select(.state == "OPEN"', "select(.state | test(\"OPEN\")"),
            command.replace("--state all", "--state draft"),
        )
        for mutated in unmodelled:
            with self.subTest(text=mutated[:60]):
                self.assertNotEqual(command, mutated, "the mutation did not apply")
                proc = self.run_command(mutated, {self.STUB_BRANCH: ["OPEN"]})
                self.assertNotEqual(0, proc.returncode, proc.stdout)


if __name__ == "__main__":
    unittest.main()
