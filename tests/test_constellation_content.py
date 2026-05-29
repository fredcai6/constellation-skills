import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def skill_markdown_paths():
    return sorted(path for path in (ROOT / "skills").rglob("*.md") if path.is_file())


class ConstellationContentTests(unittest.TestCase):
    def test_charter_skill_stays_lean(self):
        body = read("skills/charter/SKILL.md")
        self.assertLessEqual(
            len(body),
            6500,
            "Move detail into references when charter SKILL.md grows past the lean target.",
        )

    def test_role_skill_bodies_stay_lean(self):
        limits = {
            "workbench": 2300,
            "interrogator": 3300,
            "cartographer": 1900,
            "scout": 1400,
            "pilot": 2900,
            "crew": 1400,
            "triage": 1500,
        }

        for skill, limit in limits.items():
            with self.subTest(skill=skill):
                body = read(f"skills/{skill}/SKILL.md")
                self.assertLessEqual(
                    len(body),
                    limit,
                    f"Keep {skill} SKILL.md lean; move detail to templates/references.",
                )

    def test_charter_requires_relentless_single_question_interrogation(self):
        charter = read("skills/charter/SKILL.md").lower()
        protocol = read("skills/charter/references/interrogation-protocol.md").lower()
        combined = f"{charter}\n{protocol}"

        self.assertIn("relentless", combined)
        self.assertIn("invoke the `constellation-interrogator` skill", combined)
        self.assertRegex(combined, r"ask one question at a time|one question at a time")
        self.assertIn("continue drilling", combined)

    def test_interrogator_keeps_question_queue_in_agent_work(self):
        interrogator = read("skills/interrogator/SKILL.md").lower()

        self.assertIn("name: constellation-interrogator", interrogator)
        self.assertIn("relentlessly", interrogator)
        self.assertIn("question list", interrogator)
        self.assertIn(".agent-work/<work-id>/interrogator_questions.md", interrogator)
        self.assertIn("review topic and relevant code/docs", interrogator)
        self.assertIn("possible answers", interrogator)
        self.assertIn("recommendation", interrogator)

    def test_interrogator_has_mutable_starting_questions_for_charter_and_pilot(self):
        charter_template_path = ROOT / "skills/interrogator/templates/CHARTER_STARTING_QUESTIONS.template.md"
        pilot_template_path = ROOT / "skills/interrogator/templates/PILOT_STARTING_QUESTIONS.template.md"
        shared_template_path = ROOT / "skills/interrogator/templates/STARTING_QUESTIONS.template.md"

        self.assertTrue(charter_template_path.exists())
        self.assertTrue(pilot_template_path.exists())
        self.assertFalse(shared_template_path.exists())

        charter_template = charter_template_path.read_text(encoding="utf-8").lower()
        pilot_template = pilot_template_path.read_text(encoding="utf-8").lower()
        charter = read("skills/charter/SKILL.md").lower()
        pilot = read("skills/pilot/SKILL.md").lower()
        interrogator = read("skills/interrogator/SKILL.md").lower()

        self.assertIn("charter starting questions", charter_template)
        self.assertIn("aggressively update", charter_template)
        self.assertIn("pilot starting questions", pilot_template)
        self.assertIn("aggressively update", pilot_template)
        self.assertIn("templates/charter_starting_questions.template.md", charter)
        self.assertIn("templates/pilot_starting_questions.template.md", pilot)
        self.assertNotIn("templates/starting_questions.template.md", charter)
        self.assertNotIn("templates/starting_questions.template.md", pilot)
        self.assertNotIn("templates/starting_questions.template.md", interrogator)
        self.assertNotIn("templates/charter_starting_questions.template.md", interrogator)
        self.assertNotIn("templates/pilot_starting_questions.template.md", interrogator)
        self.assertIn("aggressively update", charter)
        self.assertIn("aggressively update", pilot)

    def test_generated_context_keeps_grilling_posture_sharp(self):
        charter = read("skills/charter/SKILL.md").lower()
        protocol = read("skills/charter/references/interrogation-protocol.md").lower()
        context = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("relentless", f"{charter}\n{protocol}")
        self.assertIn("project-specific overlay", context)
        self.assertNotIn("planning routes", context)
        self.assertNotIn("model stratification", context)
        self.assertNotIn("artifact triggers", context)
        self.assertNotIn("without being antagonistic", context)
        self.assertNotIn("lightweight", context)

    def test_charter_has_required_workflow_and_reference_artifacts(self):
        expected = [
            "skills/charter/references/rigorous-default.md",
            "skills/charter/references/engineering-rubric.md",
            "skills/charter/templates/CHARTER_CHECKLIST.template.md",
            "skills/charter/templates/CHARTER_OPEN_QUESTIONS.template.md",
            "skills/charter/templates/CREW_CONTEXT.template.md",
        ]

        for rel_path in expected:
            with self.subTest(path=rel_path):
                self.assertTrue((ROOT / rel_path).exists())

        removed = [
            "skills/charter/templates/OPEN_QUESTIONS.template.md",
            "skills/charter/templates/IMPLEMENTER_REVIEWER_CONTEXT.template.md",
        ]

        for rel_path in removed:
            with self.subTest(path=rel_path):
                self.assertFalse((ROOT / rel_path).exists())

        charter = read("skills/charter/SKILL.md")
        self.assertIn("ORCHESTRATOR_CONTEXT.md", charter)
        self.assertIn("CREW_CONTEXT.md", charter)
        self.assertIn("GLOSSARY.md", charter)
        self.assertIn("CHARTER_CHECKLIST.md", charter)
        self.assertIn(".agent-work/CHARTER_OPEN_QUESTIONS.md", charter)

    def test_charter_uses_single_checklist_instead_of_decision_audit(self):
        charter_files = [
            path
            for path in (ROOT / "skills" / "charter").rglob("*.md")
            if path.is_file()
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in charter_files).lower()

        self.assertIn("charter_checklist", combined)
        self.assertNotIn("charter_decisions", combined)
        self.assertNotIn("ground_rule_decisions", combined)

        checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        self.assertIn("allowed writes", checklist)
        self.assertIn("all other writes are out of charter scope", checklist)
        self.assertIn("current next question", checklist)
        self.assertIn("contradiction register", checklist)
        self.assertIn("strong | usable | weak | unresolved | not-material", checklist)
        self.assertIn("user decision | accepted default | unconfirmed default | repo artifact | assumption", checklist)
        self.assertNotIn("output target", checklist)

    def test_charter_forces_role_use_projection(self):
        charter = read("skills/charter/SKILL.md").lower()
        checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        protocol = read("skills/charter/references/interrogation-protocol.md").lower()
        combined = f"{charter}\n{checklist}\n{protocol}"

        self.assertIn("projection: orchestrator | crew | both | glossary | checklist-only", combined)
        self.assertIn("projection reason", combined)
        self.assertIn("planning/framing", combined)
        self.assertIn("gating/evidence", combined)
        self.assertIn("authority/scope", combined)
        self.assertIn("implementation", combined)
        self.assertIn("verification", combined)
        self.assertIn("review/blocking", combined)
        self.assertIn("stop/report", combined)
        self.assertIn("terminology", combined)
        self.assertIn("local traceability", combined)
        self.assertIn("orchestrator form", combined)
        self.assertIn("crew form", combined)
        self.assertIn("shared project invariants default to `both`", combined)
        self.assertIn("role-specific wording", combined)

    def test_charter_rubric_is_engineering_operational_not_truth_topology(self):
        rubric = read("skills/charter/references/engineering-rubric.md").lower()
        default = read("skills/charter/references/rigorous-default.md").lower()

        self.assertIn("correctness posture", rubric)
        self.assertIn("canonical inputs and data sources", rubric)
        self.assertIn("evidence and verification", rubric)
        self.assertIn("simplicity, abstraction, and unit shape", rubric)
        self.assertIn("interface and contract strictness", rubric)
        self.assertIn("architecture boundaries", rubric)
        self.assertIn("failure behavior", rubric)
        self.assertIn("state and side effects", rubric)
        self.assertIn("performance and resource posture", rubric)
        self.assertIn("documentation posture", rubric)
        self.assertIn("dependency and tooling posture", rubric)
        self.assertIn("security, privacy, and publicness", rubric)
        self.assertIn("generated artifacts and derived outputs", rubric)
        self.assertIn("compromise and debt policy", rubric)
        self.assertNotIn("truth hierarchy", rubric)

        self.assertIn("fail visibly", default)
        self.assertIn("one canonical path", default)
        self.assertIn("test-led", default)

    def test_pilot_is_checklist_driven_and_exits_without_crew(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        self.assertIn("checklist-driven workflow controller", pilot)
        self.assertIn("if no crew handoff is needed", pilot)
        self.assertIn("pilot is not needed", pilot)
        self.assertNotIn("constellation is not needed", pilot)
        self.assertIn("no fake lightweight constellation path", pilot)
        self.assertIn("invoke the `constellation-interrogator` skill", pilot)
        self.assertIn("0. load project context", checklist)
        self.assertIn("9. semantic closeout", checklist)
        self.assertIn("decide constellation value", checklist)
        self.assertIn("relentless", pilot)

    def test_pilot_plan_consistency_criteria_block_implementation_gate_definition(self):
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        self.assertIn("plan consistency criteria", checklist)
        self.assertIn("recorded override reason", checklist)
        self.assertLess(checklist.index("define implementation gates"), checklist.index("execute implementation gates"))
        self.assertIn("each implementation gate independently stoppable", checklist)
        self.assertIn("required verification commands exact", checklist)
        self.assertIn("reviewer approval not treated as sufficient alone", checklist)

    def test_pilot_removes_route_first_doctrine(self):
        pilot_files = [
            path
            for path in (ROOT / "skills" / "pilot").rglob("*.md")
            if path.is_file()
        ]
        combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in pilot_files)

        for phrase in [
            "research/prototype",
            "patch | quick",
            "cautious/framing",
            "baseline-needed",
            "recommended route",
            "**route:**",
            "route-first",
            "mode-first",
        ]:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

        self.assertIn("request cartographer baseline", combined)
        self.assertIn("collect triage candidate", combined)
        self.assertIn("define implementation gates", combined)

    def test_model_stratification_and_gate_chunking_are_explicit(self):
        context = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        self.assertNotIn("model stratification", context)
        self.assertIn("agent strength", pilot)
        self.assertIn("gate complexity", pilot)
        self.assertIn("scope size", pilot)
        self.assertIn("suggested model tier", checklist)

    def test_bounded_crew_stops_instead_of_inferring_hidden_intent(self):
        crew = read("skills/crew/SKILL.md").lower()
        handoff = read("skills/pilot/templates/CREW_HANDOFF.template.md").lower()

        self.assertIn("do not infer hidden intent", crew)
        self.assertIn("assigned gate", handoff)
        self.assertIn("model tier", handoff)
        self.assertIn("specific exclusions", handoff)
        self.assertIn("intent protected", handoff)
        self.assertIn("required verification commands", handoff)
        self.assertIn("no-test-surface rationale", handoff)
        self.assertNotIn("forbidden scope", handoff)
        self.assertNotIn("cartographer | triage", handoff)

    def test_ground_rule_decision_audit_doc_is_not_part_of_runtime_context(self):
        for rel_path in [
            "README.md",
            "skills/charter/SKILL.md",
            "skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md",
        ]:
            self.assertNotIn("ground_rule_decisions", read(rel_path).lower())
            self.assertNotIn("charter_decisions", read(rel_path).lower())

        self.assertFalse(
            (ROOT / "skills/charter/templates/GROUND_RULE_DECISIONS.template.md").exists()
        )

    def test_skill_descriptions_include_trigger_language(self):
        trigger_terms = ("Use when", "use when")
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            frontmatter = re.match(r"---\n(.*?)\n---", text, re.DOTALL).group(1)
            description = next(
                line.split(":", 1)[1].strip()
                for line in frontmatter.splitlines()
                if line.startswith("description:")
            )
            self.assertTrue(
                any(term in description for term in trigger_terms),
                f"{path}: description missing trigger language",
            )

    def test_decision_note_and_route_table_are_removed(self):
        self.assertFalse((ROOT / "skills/pilot/templates/DECISION_NOTE.template.md").exists())
        self.assertFalse((ROOT / "skills/pilot/references/route-table.md").exists())
        self.assertFalse((ROOT / "skills/pilot/templates/FRAMING_NOTE.template.md").exists())
        self.assertFalse((ROOT / "skills/pilot/templates/SUBAGENT_HANDOFF.template.md").exists())
        self.assertTrue((ROOT / "skills/pilot/templates/PILOT_CHECKLIST.template.md").exists())
        self.assertTrue((ROOT / "skills/pilot/templates/CREW_HANDOFF.template.md").exists())

        for rel_path in [
            "SKILL_INDEX.md",
            "skills/pilot/SKILL.md",
            "skills/pilot/templates/PILOT_CHECKLIST.template.md",
            "skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md",
        ]:
            self.assertNotIn("decision note", read(rel_path).lower())

    def test_templates_omit_empty_sections_and_open_questions_do_not_accumulate(self):
        packet_template = read("skills/cartographer/templates/ARCHITECTURE_PACKET.template.md").lower()
        open_questions = read("skills/charter/templates/CHARTER_OPEN_QUESTIONS.template.md").lower()

        self.assertIn("omit optional sections when empty", packet_template)
        self.assertIn("delete this file", open_questions)
        self.assertIn("not a backlog", open_questions)
        self.assertIn(".agent-work/charter_open_questions.md", open_questions)

    def test_agents_prefer_project_template_catalog(self):
        readme = read("README.md").lower()
        charter = read("skills/charter/SKILL.md").lower()
        checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        workbench = read("skills/workbench/SKILL.md").lower()

        combined = f"{readme}\n{charter}\n{checklist}\n{workbench}"
        self.assertIn(".agent-work/templates", combined)
        self.assertIn("prefer `.agent-work/templates/<template-name>`", combined)
        self.assertIn("fall back to bundled `templates/<template-name>`", combined)
        self.assertIn("charter seeds and updates project templates", combined)

    def test_source_repo_does_not_store_project_template_catalog(self):
        self.assertFalse((ROOT / (".agent" + "_work")).exists())

    def test_no_stale_agent_work_typo_in_tracked_text(self):
        for path in ROOT.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                self.assertNotIn(".agent" + "_work", text, str(path))

    def test_stop_using_constellation_is_operational_and_context_is_projection(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("no `.agent-work/`", pilot)
        self.assertIn("no implementation gates", pilot)
        self.assertIn("project-specific overlay", orchestrator)
        self.assertNotIn("stop using constellation", orchestrator)

    def test_review_template_has_two_review_stages_without_new_role(self):
        review = read("skills/crew/templates/REVIEW_RESULT.template.md").lower()

        self.assertIn("handoff compliance", review)
        self.assertIn("code quality", review)

    def test_crew_tdd_mode_is_explicit_and_carried_by_handoffs(self):
        crew = read("skills/crew/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        handoff = read("skills/pilot/templates/CREW_HANDOFF.template.md").lower()
        implementer_result = read("skills/crew/templates/IMPLEMENTER_RESULT.template.md").lower()
        review_result = read("skills/crew/templates/REVIEW_RESULT.template.md").lower()

        self.assertIn("vertical tdd", crew)
        self.assertIn("red -> green -> refactor", crew)
        self.assertIn("test mode", checklist)
        self.assertIn("test mode", handoff)
        self.assertIn("tdd evidence", implementer_result)
        self.assertIn("failing test observed", implementer_result)
        self.assertIn("red-green-refactor", review_result)

    def test_crew_contract_matches_pilot_handoff_interface(self):
        crew = read("skills/crew/SKILL.md").lower()
        implementer_result = read("skills/crew/templates/IMPLEMENTER_RESULT.template.md").lower()
        review_result = read("skills/crew/templates/REVIEW_RESULT.template.md").lower()
        combined = f"{crew}\n{implementer_result}\n{review_result}"

        for phrase in [
            "handoff completeness",
            "task, intent, allowed scope, specific exclusions, required evidence, test mode, stop conditions, and return format",
            "do not infer",
            "does not route",
            "does not create issues",
            "does not close gates",
            "does not expand scope",
            "structural baseline",
            "out-of-scope observations",
        ]:
            self.assertIn(phrase, combined)

        self.assertIn("specific exclusions touched", implementer_result)
        self.assertIn("scope drift", review_result)
        self.assertIn("evidence verdict", review_result)
        self.assertIn("tdd evidence, if required", implementer_result)
        self.assertNotIn("architecture packet", combined)
        self.assertNotIn("follow-up recommendations", combined)
        self.assertNotIn("non-blocking follow-ups", combined)

    def test_architecture_hierarchy_breadcrumbs_are_explicit(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        model = read("skills/cartographer/references/map-model.md").lower()
        packet = read("skills/cartographer/templates/ARCHITECTURE_PACKET.template.md").lower()
        index = read("skills/cartographer/templates/ARCHITECTURE_INDEX.template.md").lower()

        self.assertIn("structural map", cartographer)
        self.assertIn("architecture and code are one hierarchy", model)
        self.assertIn("module/file", model)
        self.assertIn("function-or-method", model)
        self.assertIn("structural node", packet)
        self.assertIn("level", packet)
        self.assertIn("parent", packet)
        self.assertIn("system-context | container | component | code-path | module", packet)
        self.assertIn("structural hierarchy", index)
        self.assertNotIn("do not require all levels", cartographer)

    def test_cartographer_model_is_current_structural_map_with_sparse_overlay(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        model = read("skills/cartographer/references/map-model.md").lower()
        packet = read("skills/cartographer/templates/ARCHITECTURE_PACKET.template.md").lower()
        index = read("skills/cartographer/templates/ARCHITECTURE_INDEX.template.md").lower()
        combined = f"{cartographer}\n{model}\n{packet}\n{index}"

        self.assertIn("current-only structural map", combined)
        self.assertIn("purpose / constraint / rationale anchors", packet)
        self.assertIn("serves", combined)
        self.assertIn("constrained-by", combined)
        self.assertIn("depends-on", combined)
        self.assertIn("consumer -> provider", combined)
        self.assertIn("purpose usually stays", model)
        self.assertIn("constraints are sparse", model)
        self.assertIn("rationale", model)
        self.assertIn("status is metadata only", model)

    def test_cartographer_uses_checkpoint_checklist_not_result_artifact(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        checklist = read("skills/cartographer/templates/CARTOGRAPHER_CHECKLIST.template.md").lower()

        self.assertTrue((ROOT / "skills/cartographer/templates/CARTOGRAPHER_CHECKLIST.template.md").exists())
        self.assertFalse((ROOT / "skills/cartographer/templates/CARTOGRAPHER_RESULT.template.md").exists())
        self.assertIn(".agent-work/cartographer_checklist.md", cartographer)
        self.assertIn("scope gate", checklist)
        self.assertIn("evidence gate", checklist)
        self.assertIn("model gate", checklist)
        self.assertIn("relationship gate", checklist)
        self.assertIn("packet gate", checklist)
        self.assertIn("map contract gate", checklist)
        self.assertIn("triage gate", checklist)
        self.assertIn("closeout gate", checklist)
        self.assertIn("triage candidate", checklist)

    def test_cartographer_is_packet_first_and_handles_ambiguity_explicitly(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        model = read("skills/cartographer/references/map-model.md").lower()
        checklist = read("skills/cartographer/templates/CARTOGRAPHER_CHECKLIST.template.md").lower()
        combined = f"{cartographer}\n{model}\n{checklist}"

        self.assertIn("packet-first", combined)
        self.assertIn("packets are the primary durable agent pages", model)
        self.assertIn("index and overlays support navigation", model)
        self.assertIn("user intent ambiguity", checklist)
        self.assertIn("decision rationale", checklist)
        self.assertIn("decide and record rationale", cartographer)
        self.assertIn("ask only when", cartographer)

    def test_cartographer_manual_traceability_and_spec_replacement_are_explicit(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        model = read("skills/cartographer/references/map-model.md").lower()
        checklist = read("skills/cartographer/templates/CARTOGRAPHER_CHECKLIST.template.md").lower()
        combined = f"{cartographer}\n{model}\n{checklist}"

        self.assertIn("manual packets are authoritative agent context", combined)
        self.assertIn("not mechanically trusted unless validation/generation is configured and passing", combined)
        self.assertIn("spec replacement is conditional", combined)
        self.assertIn("retired or explicitly demoted", combined)
        self.assertIn("parallel canonical docs", combined)
        self.assertIn("traceability mode: manual | validated | generated", checklist)
        self.assertIn("drift risk: low | medium | high", checklist)
        self.assertIn("parallel canonical docs: <paths or none>", checklist)

    def test_cartographer_supports_sparse_decision_anchors_without_history_log(self):
        model = read("skills/cartographer/references/map-model.md").lower()
        packet = read("skills/cartographer/templates/ARCHITECTURE_PACKET.template.md").lower()
        checklist = read("skills/cartographer/templates/CARTOGRAPHER_CHECKLIST.template.md").lower()
        decision = read("skills/cartographer/templates/ARCHITECTURE_DECISION.template.md").lower()
        readme = read("README.md").lower()
        combined = f"{model}\n{packet}\n{checklist}\n{decision}"

        self.assertTrue((ROOT / "skills/cartographer/templates/ARCHITECTURE_DECISION.template.md").exists())
        self.assertIn("decision anchors", combined)
        self.assertIn("docs/architecture/decisions/", readme)
        self.assertIn("not a history log", model)
        self.assertIn("current structural consequence", decision)
        self.assertIn("structural anchors", decision)
        self.assertIn("decision anchors", packet)
        self.assertIn("key decisions/rationale", checklist)
        self.assertIn("rationale anchors", packet)
        self.assertIn("rationale:<id>", packet)
        self.assertIn("captured as rationale overlays", model)
        self.assertIn("advance current or future work", model)
        self.assertNotIn("migration diary", decision)

    def test_cartographer_map_build_replaces_explorer_build(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        map_build = read("skills/cartographer/templates/MAP_BUILD.template.md").lower()

        self.assertTrue((ROOT / "skills/cartographer/templates/MAP_BUILD.template.md").exists())
        self.assertFalse((ROOT / "skills/cartographer/templates/EXPLORER_BUILD.template.md").exists())
        self.assertIn("map_build.md", cartographer)
        self.assertIn("docs/architecture/generated/map.json", map_build)
        self.assertIn("docs/architecture/overlays/", map_build)
        self.assertIn("repo source tree", map_build)
        self.assertIn("scripts/build_architecture_map.py", map_build)
        self.assertIn("--check", map_build)
        self.assertNotIn("human-explorable architecture artifact", map_build)

    def test_cartographer_rejects_out_of_scope_graph_concepts(self):
        cartographer_files = [
            path
            for path in (ROOT / "skills" / "cartographer").rglob("*.md")
            if path.is_file()
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in cartographer_files).lower()

        forbidden = [
            "test/evidence graph",
            "requirements matrix",
            "operational behavior map",
            "event/status graph",
            "intent without test",
            "test not linked to intent",
            "runtime failure map gap",
            "contains",
            "owned-by",
            "called-by",
            "implemented-by",
            "missing check",
            "curated diagrams",
            "explorer",
        ]

        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

        self.assertIn("tests/checks are evidence inputs and packet context only", combined)

    def test_triage_remains_accessible_to_pilot_and_cartographer(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        cartographer = read("skills/cartographer/SKILL.md").lower()
        scout = read("skills/scout/SKILL.md").lower()
        triage = read("skills/triage/SKILL.md").lower()

        self.assertIn("triage", pilot)
        self.assertIn("triage", cartographer)
        self.assertIn("triage", scout)
        self.assertIn("does not implement", triage)

    def test_scout_is_map_first_architecture_audit_not_cartographer(self):
        scout = read("skills/scout/SKILL.md").lower()
        heuristics = read("skills/scout/references/scout-heuristics.md").lower()
        report = read("skills/scout/templates/SCOUT_REPORT.template.md").lower()
        combined = f"{scout}\n{heuristics}\n{report}"

        self.assertIn("map-first architecture audit", combined)
        self.assertIn("read cartographer artifacts first", combined)
        self.assertIn("sample code to challenge the map", combined)
        self.assertIn("shallow structural node", combined)
        self.assertIn("deletion test", combined)
        self.assertIn("locality", combined)
        self.assertIn("leverage", combined)
        self.assertIn("structural anchor", report)
        self.assertIn("triage handoff", report)
        self.assertIn("does not update architecture truth", scout)
        self.assertIn("does not implement", scout)
        self.assertIn("does not redesign", scout)
        self.assertNotIn("own future work", scout)

    def test_triage_consumes_cartographer_structural_handoffs(self):
        triage = read("skills/triage/SKILL.md").lower()
        recommendation = read("skills/triage/templates/TRIAGE_RECOMMENDATION.template.md").lower()
        combined = f"{triage}\n{recommendation}"

        self.assertIn(".agent-work/cartographer_checklist.md", combined)
        self.assertIn("structural anchor", recommendation)
        self.assertIn("cartographer mismatch class", recommendation)
        self.assertIn("current truth", recommendation)
        self.assertIn("desired/future concern", recommendation)
        self.assertIn("source checklist/artifact", recommendation)
        self.assertIn("future-work packaging", triage)
        self.assertIn("missing structural node", triage)
        self.assertIn("stale generated map", triage)
        self.assertIn("structure/constraint mismatch", triage)

    def test_curation_modes_and_escape_hatches_are_explicit(self):
        charter = read("skills/charter/SKILL.md").lower()
        cartographer = read("skills/cartographer/SKILL.md").lower()
        pilot = read("skills/pilot/SKILL.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("context compile", charter)
        self.assertIn("context curation", pilot)
        self.assertIn("architecture curation", cartographer)
        self.assertIn("stop using constellation", pilot)
        self.assertNotIn("stop using constellation", orchestrator)

    def test_gate_is_central_unit_and_workbench_archives_without_compression(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        workbench = read("skills/workbench/SKILL.md").lower()
        closeout = read("skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md").lower()

        self.assertIn("gate is the central unit", pilot)
        self.assertIn("smallest chunk", pilot)
        self.assertIn("implementation gates", checklist)
        self.assertNotIn("closeout compression", workbench)
        self.assertNotIn("delete/condense", workbench)
        self.assertNotIn("repository history captured", closeout)

    def test_pilot_and_charter_archive_complete_work_packages(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        charter = read("skills/charter/SKILL.md").lower()
        charter_checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        workbench = read("skills/workbench/SKILL.md").lower()
        closeout = read("skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md").lower()

        combined = f"{pilot}\n{checklist}\n{charter}\n{charter_checklist}\n{workbench}\n{closeout}"
        self.assertIn("move the entire `.agent-work/<work-id>/` package", combined)
        self.assertIn("including `interrogator_questions.md`", combined)
        self.assertIn(".agent-work/archive/<date>-<work-id>/", combined)
        self.assertIn("no loose work-id artifacts remain", combined)
        self.assertIn("archived package commit decision", charter_checklist)

    def test_closeout_tracks_template_update_candidates(self):
        closeout = read("skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        charter_checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()

        self.assertIn("template update candidates", closeout)
        self.assertIn("do not mutate durable doctrine silently", closeout)
        self.assertIn("defer to charter", closeout)
        self.assertIn("route/apply/drop template update candidates", checklist)
        self.assertIn("consume template update candidates", charter_checklist)

    def test_charter_captures_repo_action_authority_for_pilot(self):
        charter_questions = read(
            "skills/interrogator/templates/CHARTER_STARTING_QUESTIONS.template.md"
        ).lower()
        charter_checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        pilot_checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        combined = f"{charter_questions}\n{charter_checklist}\n{orchestrator}\n{pilot_checklist}"
        self.assertIn("commit archived work packages", combined)
        self.assertIn("commit sensitivity", combined)
        self.assertIn("pilot may open prs directly", combined)
        self.assertIn("pilot may merge to main", combined)
        self.assertIn("repo action authority", combined)

    def test_pilot_uses_workbench_artifact_hygiene(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        workbench = read("skills/workbench/SKILL.md").lower()
        readme = read("README.md").lower()

        self.assertIn("workbench owns artifact hygiene", pilot)
        self.assertIn("single execution controller", checklist)
        self.assertIn("current state", checklist)
        self.assertNotIn("local_todo", checklist)
        self.assertIn("subagent kickoff", checklist)
        self.assertIn("crew-handoffs/", workbench)
        self.assertIn("triage-candidates/", workbench)
        self.assertNotIn("framing_note.md", workbench)
        self.assertNotIn("    handoffs/", workbench)
        self.assertNotIn("issue-recommendations/", workbench)
        self.assertIn("crew-handoffs/", readme)
        self.assertIn("triage-candidates/", readme)

    def test_workbench_uses_pilot_checklist_for_pilot_recovery_hooks(self):
        workbench = read("skills/workbench/SKILL.md").lower()
        pilot_checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        crew_role = read("skills/crew/references/role-scope.md").lower()
        default_checklist = read("skills/workbench/templates/DEFAULT_CHECKLIST.template.md").lower()
        combined = f"{workbench}\n{pilot_checklist}\n{crew_role}\n{default_checklist}"

        self.assertIn("pilot checklist", combined)
        self.assertIn("execution controller", combined)
        self.assertIn("task", pilot_checklist)
        self.assertIn("source", pilot_checklist)
        self.assertIn("definition of done", pilot_checklist)
        self.assertIn("execution notes", pilot_checklist)
        self.assertIn("status transitions", pilot_checklist)
        self.assertIn("current state", pilot_checklist)
        self.assertIn("one controller per work package", workbench)
        self.assertIn("default checklist", default_checklist)
        self.assertIn("never both", workbench)

    def test_role_checklists_are_direct_role_interfaces_not_workbench_owned(self):
        charter = read("skills/charter/SKILL.md").lower()
        pilot = read("skills/pilot/SKILL.md").lower()
        cartographer = read("skills/cartographer/SKILL.md").lower()
        crew_role = read("skills/crew/references/role-scope.md").lower()

        self.assertIn(".agent-work/<work-id>/charter_checklist.md", charter)
        self.assertIn("templates/charter_checklist.template.md", charter)
        self.assertIn("pilot_checklist", pilot)
        self.assertIn("templates/pilot_checklist.template.md", pilot)
        self.assertIn(".agent-work/cartographer_checklist.md", cartographer)
        self.assertIn("templates/cartographer_checklist.template.md", cartographer)
        self.assertIn("role-specific checklist", crew_role)
        self.assertIn("workbench | `.agent-work/<work-id>/default_checklist.md`", crew_role)
        self.assertNotIn("workbench | role-specific checklist templates", crew_role)

    def test_evidence_integration_requires_original_intent_not_approval_alone(self):
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        self.assertIn("original intent check", checklist)
        self.assertIn("reviewer approval alone insufficient", checklist)
        self.assertIn("implementation evidence", checklist)
        self.assertIn("review evidence", checklist)
        self.assertIn("assumption check", checklist)
        self.assertIn("scope drift check", checklist)
        self.assertIn("request cartographer", checklist)

    def test_status_model_is_shared_by_major_templates(self):
        status_model = read("skills/workbench/references/status-model.md").lower()
        self.assertIn("pending | in-progress | blocked | complete | skipped", status_model)
        self.assertIn("complete | partial | blocked | out-of-scope | failed", status_model)
        self.assertIn("approve | block | comment", status_model)
        self.assertIn("reviewer approval alone does not close a gate", status_model)

        for rel_path in [
            "skills/pilot/templates/PILOT_CHECKLIST.template.md",
            "skills/crew/templates/IMPLEMENTER_RESULT.template.md",
            "skills/crew/templates/REVIEW_RESULT.template.md",
            "skills/workbench/templates/DEFAULT_CHECKLIST.template.md",
        ]:
            with self.subTest(path=rel_path):
                self.assertIn(
                    "status values follow `skills/workbench/references/status-model.md`",
                    read(rel_path).lower(),
                )

    def test_implementation_gates_require_per_gate_review_cycle(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        combined = f"{pilot}\n{checklist}"
        self.assertIn("implementer crew -> integrate evidence -> reviewer crew -> integrate evidence -> gate close", combined)
        self.assertIn("do not batch review at final closeout", combined)
        self.assertIn("implementer dispatch", checklist)
        self.assertIn("reviewer dispatch", checklist)
        self.assertIn("implementation evidence", checklist)
        self.assertIn("review evidence", checklist)

    def test_pilot_collects_triage_candidates_instead_of_eager_issues(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()

        self.assertIn("triage candidate", checklist)
        self.assertIn("dropped because", checklist)
        self.assertIn("current work anchor", checklist)
        self.assertIn("structural anchor", checklist)
        self.assertIn("do not eagerly create issues", pilot)
        self.assertIn("current gate cannot proceed", pilot)

    def test_repo_mechanics_follow_project_orchestrator_context(self):
        pilot = read("skills/pilot/SKILL.md").lower()
        checklist = read("skills/pilot/templates/PILOT_CHECKLIST.template.md").lower()
        handoff = read("skills/pilot/templates/CREW_HANDOFF.template.md").lower()

        combined = f"{pilot}\n{checklist}\n{handoff}"
        self.assertIn("project orchestrator context", combined)
        self.assertIn("ask if silent", combined)
        self.assertIn("project mechanics", checklist)
        self.assertIn("project mechanics for this gate", handoff)
        self.assertIn("commit sha", checklist)
        self.assertNotIn("codex/", combined)

    def test_role_boundaries_survive_slimming(self):
        expectations = {
            "workbench": [".agent-work/", "not durable project truth"],
            "cartographer": ["current-only structural map", "does not change code"],
            "scout": ["map-first architecture audit", "does not implement"],
            "pilot": ["does not implement", "cartographer verifies architecture"],
            "crew": ["implementer owns scoped change", "reviewer owns independent verification"],
            "triage": ["does not implement", "issue-ready recommendations"],
        }

        for skill, phrases in expectations.items():
            with self.subTest(skill=skill):
                body = read(f"skills/{skill}/SKILL.md").lower()
                for phrase in phrases:
                    self.assertIn(phrase, body)

    def test_overview_defines_relationship_contracts(self):
        overview = read("docs/CONSTELLATION_OVERVIEW.md").lower()

        self.assertIn("relationship contract", overview)
        self.assertIn("producer | artifact/interface | consumer | contract", overview)

        expected_edges = [
            "charter | `docs/agents/orchestrator_context.md` | pilot, cartographer, scout",
            "charter | `docs/agents/crew_context.md` | crew",
            "pilot | `.agent-work/<work-id>/pilot_checklist.md` | pilot, crew, workbench",
            "workbench | `.agent-work/<work-id>/default_checklist.md` | crew",
            "cartographer | `docs/architecture/packets/` + `index.md` | scout, pilot, crew",
            "scout | `scout_report` | user, pilot, triage",
            "pilot | `crew_handoff` | crew",
            "crew | `implementer_result` / `review_result` | pilot",
            "pilot, cartographer, scout, crew | triage candidate | triage",
        ]

        for edge in expected_edges:
            with self.subTest(edge=edge):
                self.assertIn(edge, overview)

        self.assertIn("templates are the interface", overview)
        self.assertIn("skill.md is trigger, boundary, and resource pointer", overview)

    def test_installed_skill_markdown_does_not_depend_on_source_docs(self):
        banned = [
            "docs/constellation_overview.md",
        ]

        for path in skill_markdown_paths():
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=str(path.relative_to(ROOT))):
                for phrase in banned:
                    self.assertNotIn(phrase, text)

    def test_installed_skill_markdown_does_not_use_source_tree_peer_skill_paths(self):
        banned = [
            "skills/pilot/skill.md",
            "skills/cartographer/skill.md",
            "skills/crew/skill.md",
        ]

        for path in skill_markdown_paths():
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=str(path.relative_to(ROOT))):
                for phrase in banned:
                    self.assertNotIn(phrase, text)

    def test_public_workflow_layout_matches_role_artifact_paths(self):
        readme = read("README.md")

        self.assertIn("  CARTOGRAPHER_CHECKLIST.md", readme)
        self.assertIn("  SCOUT_REPORT.md", readme)
        self.assertIn("  <work-id>/", readme)
        self.assertLess(readme.index("CARTOGRAPHER_CHECKLIST.md"), readme.index("  <work-id>/"))
        self.assertLess(readme.index("SCOUT_REPORT.md"), readme.index("  <work-id>/"))

    def test_role_specific_relationship_references_exist(self):
        expectations = {
            "charter": [
                "pilot owns gated workflow control",
                "cartographer owns current-only structural truth",
                "crew executes bounded implementation and review",
                "give pilot and cartographer orchestrator context",
                "give crew crew context",
            ],
            "pilot": [
                "cartographer verifies structural truth",
                "crew executes assigned gates",
                "crew cannot close gates",
            ],
            "cartographer": [
                "pilot requests cartographer when structural truth may have changed",
                "crew may consume packets",
                "crew does not curate architecture",
            ],
            "crew": [
                "workbench | `.agent-work/<work-id>/default_checklist.md`",
                "default checklist is the controller when no role-specific checklist exists",
                "do not route, create issues, close gates, or expand scope",
            ],
        }

        for skill, phrases in expectations.items():
            role_doc = read(f"skills/{skill}/references/role-scope.md").lower()
            skill_body = read(f"skills/{skill}/SKILL.md").lower()
            with self.subTest(skill=skill):
                self.assertIn("references/role-scope.md", skill_body)
                for phrase in phrases:
                    self.assertIn(phrase, role_doc)

    def test_skill_bodies_point_to_templates_not_inline_manuals(self):
        expectations = {
            "charter": ["templates/charter_checklist.template.md", "references/engineering-rubric.md"],
            "workbench": ["templates/default_checklist.template.md", "templates/workflow_closeout.template.md"],
            "cartographer": ["templates/cartographer_checklist.template.md", "templates/architecture_packet.template.md"],
            "scout": ["templates/scout_report.template.md", "references/scout-heuristics.md"],
            "pilot": ["templates/pilot_checklist.template.md", "templates/crew_handoff.template.md"],
            "crew": ["templates/implementer_result.template.md", "templates/review_result.template.md"],
            "triage": ["templates/triage_recommendation.template.md"],
        }

        for skill, phrases in expectations.items():
            body = read(f"skills/{skill}/SKILL.md").lower()
            with self.subTest(skill=skill):
                self.assertIn("templates", body)
                for phrase in phrases:
                    self.assertIn(phrase, body)

    def test_template_conformance_scripts_exist(self):
        for rel_path in [
            "scripts/check_constellation_templates.py",
            "scripts/check_agent_work_package.py",
        ]:
            with self.subTest(path=rel_path):
                text = read(rel_path)
                self.assertIn("argparse", text)
                self.assertIn("sys.exit", text)

    def test_generated_context_is_role_overlay_not_role_manual(self):
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        crew = read("skills/charter/templates/CREW_CONTEXT.template.md").lower()
        old_low_level = ROOT / "skills/charter/templates/IMPLEMENTER_REVIEWER_CONTEXT.template.md"

        self.assertFalse(old_low_level.exists())
        self.assertIn("pilot and cartographer", orchestrator)
        self.assertIn("project-specific overlay", orchestrator)
        self.assertIn("handoff requirements", orchestrator)
        self.assertIn("evidence and verification map", orchestrator)
        self.assertIn("architecture and scope constraints", orchestrator)
        self.assertNotIn("triage", orchestrator)
        self.assertNotIn("workbench", orchestrator)
        self.assertNotIn("open_questions", orchestrator)
        self.assertNotIn("charter status", orchestrator)

        self.assertIn("crew context", crew)
        self.assertIn("handoff discipline", crew)
        self.assertIn("required handoff fields", crew)
        self.assertIn("specific exclusions, if any", crew)
        self.assertIn("handoff-required", crew)
        self.assertIn("stop and report", crew)
        self.assertIn("review block criteria", crew)
        self.assertNotIn("forbidden scope", crew)
        self.assertNotIn("route selection", crew)
        self.assertNotIn("workflow track", crew)
        self.assertNotIn("worktree setup", crew)
        self.assertNotIn("gate sequencing", crew)
        self.assertNotIn("architecture boundary", crew)
        self.assertNotIn("pilot", crew)
        self.assertNotIn("cartographer", crew)
        self.assertNotIn("triage", crew)
        self.assertNotIn("workbench", crew)
        self.assertNotIn("open_questions", crew)

    def test_charter_outputs_prioritize_context_density(self):
        charter = read("skills/charter/SKILL.md").lower()
        checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        crew = read("skills/charter/templates/CREW_CONTEXT.template.md").lower()
        handoff = read("skills/pilot/templates/CREW_HANDOFF.template.md").lower()

        combined = f"{charter}\n{checklist}"
        self.assertIn("context density", combined)
        self.assertIn("sacrifice grammar", combined)
        self.assertIn("minimize tokens", combined)
        self.assertIn("information per token", combined)

        for context in [orchestrator, crew]:
            self.assertIn("agent-facing", context)
            self.assertIn("bullets, tables, and fragments", context)
            self.assertIn("omit prose that does not change agent action", context)

        self.assertIn("agent-to-agent context", handoff)
        self.assertIn("concise fragments", handoff)

    def test_charter_compile_checks_projection_correctness(self):
        checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()

        self.assertIn("crew context contains every project invariant", checklist)
        self.assertIn("orchestrator context contains every project invariant", checklist)
        self.assertIn("shared decisions use role-specific wording", checklist)
        self.assertIn("crew context contains only universal verification rules", checklist)
        self.assertIn("area-specific commands are represented as handoff requirements", checklist)
        self.assertIn("workflow selection and coordination consequences reach crew through the handoff", checklist)

    def test_skill_frontmatter_has_only_name_and_description(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            match = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
            self.assertIsNotNone(match, f"{path} is missing YAML frontmatter")
            keys = [
                line.split(":", 1)[0]
                for line in match.group(1).splitlines()
                if line.strip()
            ]
            self.assertEqual(["name", "description"], keys, str(path))

    def test_pilot_uses_codex_accessible_skill_id(self):
        pilot = read("skills/pilot/SKILL.md")

        self.assertIn("name: constellation-pilot", pilot)
        self.assertNotIn("name: constellation-conductor", pilot)
        self.assertNotIn("name: constellation-coordinator", pilot)
        self.assertNotIn("name: constellation-coordination-flow", pilot)

    def test_readme_documents_user_and_project_install(self):
        readme = read("README.md")

        self.assertIn("scripts/install_constellation.py", readme)
        self.assertIn("scripts/build_architecture_map.py", readme)
        self.assertIn("--agent codex", readme)
        self.assertIn("--agent claude", readme)
        self.assertIn("--agent cursor", readme)
        self.assertIn("--agent gemini", readme)
        self.assertIn("--agent all", readme)
        self.assertIn("--scope user", readme)
        self.assertIn("--scope project", readme)
        self.assertIn("--dry-run", readme)
        self.assertIn("--force", readme)

    def test_public_docs_do_not_keep_old_cartographer_artifact_names(self):
        for rel_path in ["README.md", "SKILL_INDEX.md"]:
            text = read(rel_path).lower()
            self.assertIn("structural map", text)
            self.assertNotIn("explorer_build", text)
            self.assertNotIn("cartographer_result", text)
            self.assertNotIn("diagrams/", text)


if __name__ == "__main__":
    unittest.main()
