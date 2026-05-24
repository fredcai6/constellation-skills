import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


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
            "workbench": 1700,
            "cartographer": 1900,
            "conductor": 2900,
            "crew": 1250,
            "triage": 1300,
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
        self.assertRegex(combined, r"ask one question at a time|one question at a time")
        self.assertIn("continue drilling", combined)

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

    def test_conductor_uses_consistent_route_names_and_grillme_posture(self):
        conductor = read("skills/conductor/SKILL.md").lower()
        interrogation_result = read(
            "skills/conductor/templates/PROBLEM_INTERROGATION_RESULT.template.md"
        ).lower()

        self.assertNotIn("lightweight grillme", conductor)
        self.assertIn("relentless", conductor)
        self.assertIn("baseline-needed", interrogation_result)
        self.assertNotIn("custodian-needed", interrogation_result)

    def test_model_stratification_and_gate_chunking_are_explicit(self):
        context = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        conductor = read("skills/conductor/SKILL.md").lower()
        gated_plan = read("skills/conductor/templates/GATED_PLAN.template.md").lower()

        self.assertNotIn("model stratification", context)
        self.assertIn("larger mandate", conductor)
        self.assertIn("simpler model", conductor)
        self.assertIn("chunk gates", conductor)
        self.assertIn("simpler models", conductor)
        self.assertIn("suggested model tier", gated_plan)

    def test_bounded_crew_stops_instead_of_inferring_hidden_intent(self):
        crew = read("skills/crew/SKILL.md").lower()
        handoff = read("skills/conductor/templates/SUBAGENT_HANDOFF.template.md").lower()

        self.assertIn("do not infer hidden intent", crew)
        self.assertIn("mandate", handoff)
        self.assertIn("model tier", handoff)
        self.assertIn("specific exclusions", handoff)
        self.assertIn("success criteria", handoff)
        self.assertIn("required verification commands", handoff)
        self.assertIn("no-test-surface rationale", handoff)
        self.assertNotIn("forbidden scope", handoff)

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
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            frontmatter = re.match(r"---\n(.*?)\n---", text, re.DOTALL).group(1)
            description = next(
                line.split(":", 1)[1].strip()
                for line in frontmatter.splitlines()
                if line.startswith("description:")
            )
            self.assertIn("Use when", description, str(path))

    def test_decision_note_and_route_table_are_removed(self):
        self.assertFalse((ROOT / "skills/conductor/templates/DECISION_NOTE.template.md").exists())
        self.assertFalse((ROOT / "skills/conductor/references/route-table.md").exists())

        for rel_path in [
            "SKILL_INDEX.md",
            "skills/conductor/SKILL.md",
            "skills/conductor/templates/PROBLEM_INTERROGATION_RESULT.template.md",
            "skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md",
        ]:
            self.assertNotIn("decision note", read(rel_path).lower())

    def test_templates_omit_empty_sections_and_open_questions_do_not_accumulate(self):
        principles = read("docs/OPERATING_PRINCIPLES.md").lower()
        open_questions = read("skills/charter/templates/CHARTER_OPEN_QUESTIONS.template.md").lower()

        self.assertIn("omit optional sections when empty", principles)
        self.assertIn("delete this file", open_questions)
        self.assertIn("not a backlog", open_questions)
        self.assertIn(".agent-work/charter_open_questions.md", open_questions)

    def test_stop_using_constellation_is_operational_and_context_is_projection(self):
        conductor = read("skills/conductor/SKILL.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("no `.agent-work/`", conductor)
        self.assertIn("no gated plan", conductor)
        self.assertIn("project-specific overlay", orchestrator)
        self.assertNotIn("stop using constellation", orchestrator)

    def test_review_template_has_two_review_stages_without_new_role(self):
        review = read("skills/crew/templates/REVIEW_RESULT.template.md").lower()

        self.assertIn("handoff compliance", review)
        self.assertIn("code quality", review)

    def test_crew_tdd_mode_is_explicit_and_carried_by_handoffs(self):
        crew = read("skills/crew/SKILL.md").lower()
        gated_plan = read("skills/conductor/templates/GATED_PLAN.template.md").lower()
        handoff = read("skills/conductor/templates/SUBAGENT_HANDOFF.template.md").lower()
        implementer_result = read("skills/crew/templates/IMPLEMENTER_RESULT.template.md").lower()
        review_result = read("skills/crew/templates/REVIEW_RESULT.template.md").lower()

        self.assertIn("vertical tdd", crew)
        self.assertIn("red -> green -> refactor", crew)
        self.assertIn("test mode", gated_plan)
        self.assertIn("test mode", handoff)
        self.assertIn("tdd evidence", implementer_result)
        self.assertIn("failing test observed", implementer_result)
        self.assertIn("red-green-refactor", review_result)

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
        self.assertIn("purpose / constraint anchors", packet)
        self.assertIn("serves", combined)
        self.assertIn("constrained-by", combined)
        self.assertIn("depends-on", combined)
        self.assertIn("consumer -> provider", combined)
        self.assertIn("purpose usually stays", model)
        self.assertIn("constraints are sparse", model)
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

    def test_cartographer_map_build_replaces_explorer_build(self):
        cartographer = read("skills/cartographer/SKILL.md").lower()
        map_build = read("skills/cartographer/templates/MAP_BUILD.template.md").lower()

        self.assertTrue((ROOT / "skills/cartographer/templates/MAP_BUILD.template.md").exists())
        self.assertFalse((ROOT / "skills/cartographer/templates/EXPLORER_BUILD.template.md").exists())
        self.assertIn("map_build.md", cartographer)
        self.assertIn("docs/architecture/generated/map.json", map_build)
        self.assertIn("docs/architecture/overlays/", map_build)
        self.assertIn("repo source tree", map_build)
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

    def test_triage_remains_accessible_to_conductor_and_cartographer(self):
        conductor = read("skills/conductor/SKILL.md").lower()
        cartographer = read("skills/cartographer/SKILL.md").lower()
        triage = read("skills/triage/SKILL.md").lower()

        self.assertIn("triage", conductor)
        self.assertIn("triage", cartographer)
        self.assertIn("does not implement", triage)

    def test_curation_modes_and_escape_hatches_are_explicit(self):
        charter = read("skills/charter/SKILL.md").lower()
        cartographer = read("skills/cartographer/SKILL.md").lower()
        conductor = read("skills/conductor/SKILL.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("context compile", charter)
        self.assertIn("context curation", conductor)
        self.assertIn("architecture curation", cartographer)
        self.assertIn("stop using constellation", conductor)
        self.assertNotIn("stop using constellation", orchestrator)

    def test_gate_is_central_unit_and_closeout_compresses(self):
        conductor = read("skills/conductor/SKILL.md").lower()
        gated_plan = read("skills/conductor/templates/GATED_PLAN.template.md").lower()
        workbench = read("skills/workbench/SKILL.md").lower()

        self.assertIn("gate is the central unit", conductor)
        self.assertIn("smallest chunk", gated_plan)
        self.assertIn("closeout compression", workbench)

    def test_role_boundaries_survive_slimming(self):
        expectations = {
            "workbench": [".agent-work/", "not durable project truth"],
            "cartographer": ["current-only structural map", "does not change code"],
            "conductor": ["does not implement", "cartographer verifies architecture"],
            "crew": ["implementer owns scoped change", "reviewer owns independent verification"],
            "triage": ["does not implement", "issue-ready recommendations"],
        }

        for skill, phrases in expectations.items():
            with self.subTest(skill=skill):
                body = read(f"skills/{skill}/SKILL.md").lower()
                for phrase in phrases:
                    self.assertIn(phrase, body)

    def test_generated_context_is_role_overlay_not_role_manual(self):
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        crew = read("skills/charter/templates/CREW_CONTEXT.template.md").lower()
        old_low_level = ROOT / "skills/charter/templates/IMPLEMENTER_REVIEWER_CONTEXT.template.md"

        self.assertFalse(old_low_level.exists())
        self.assertIn("conductor and cartographer", orchestrator)
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
        self.assertNotIn("conductor", crew)
        self.assertNotIn("cartographer", crew)
        self.assertNotIn("triage", crew)
        self.assertNotIn("workbench", crew)
        self.assertNotIn("open_questions", crew)

    def test_charter_outputs_prioritize_context_density(self):
        charter = read("skills/charter/SKILL.md").lower()
        checklist = read("skills/charter/templates/CHARTER_CHECKLIST.template.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()
        crew = read("skills/charter/templates/CREW_CONTEXT.template.md").lower()
        handoff = read("skills/conductor/templates/SUBAGENT_HANDOFF.template.md").lower()

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

    def test_readme_documents_user_and_project_install(self):
        readme = read("README.md")

        self.assertIn("scripts/install_constellation.py", readme)
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
