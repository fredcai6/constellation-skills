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
        context = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("relentless", context)
        self.assertNotIn("without being antagonistic", context)
        self.assertNotIn("lightweight", context)

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

        self.assertIn("model stratification", context)
        self.assertIn("larger mandate", context)
        self.assertIn("simpler model", context)
        self.assertIn("chunk gates", conductor)
        self.assertIn("simpler models", conductor)
        self.assertIn("suggested model tier", gated_plan)

    def test_bounded_crew_stops_instead_of_inferring_hidden_intent(self):
        crew = read("skills/crew/SKILL.md").lower()
        handoff = read("skills/conductor/templates/SUBAGENT_HANDOFF.template.md").lower()

        self.assertIn("do not infer hidden intent", crew)
        self.assertIn("mandate", handoff)
        self.assertIn("model tier", handoff)

    def test_ground_rule_decision_audit_doc_is_not_part_of_runtime_context(self):
        for rel_path in [
            "README.md",
            "skills/charter/SKILL.md",
            "skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md",
        ]:
            self.assertNotIn("ground_rule_decisions", read(rel_path).lower())

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
        open_questions = read("skills/charter/templates/OPEN_QUESTIONS.template.md").lower()

        self.assertIn("omit optional sections when empty", principles)
        self.assertIn("delete resolved questions", open_questions)
        self.assertIn("future work goes to triage", open_questions)

    def test_stop_using_constellation_is_operational_and_context_is_projection(self):
        conductor = read("skills/conductor/SKILL.md").lower()
        orchestrator = read("skills/charter/templates/ORCHESTRATOR_CONTEXT.template.md").lower()

        self.assertIn("no `.agent-work/`", conductor)
        self.assertIn("no gated plan", conductor)
        self.assertIn("role context is a projection", orchestrator)

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
        packet = read("skills/cartographer/templates/ARCHITECTURE_PACKET.template.md").lower()
        index = read("skills/cartographer/templates/ARCHITECTURE_INDEX.template.md").lower()

        self.assertIn("hierarchy", cartographer)
        self.assertIn("level", packet)
        self.assertIn("parent", packet)
        self.assertIn("system-context | container | component | code-path", packet)
        self.assertIn("architecture hierarchy", index)
        self.assertIn("do not require all levels", cartographer)

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

        self.assertIn("context curation", charter)
        self.assertIn("context curation", conductor)
        self.assertIn("architecture curation", cartographer)
        self.assertIn("stop using constellation", conductor)
        self.assertIn("stop using constellation", orchestrator)

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
            "cartographer": ["current architecture truth", "does not change code"],
            "conductor": ["does not implement", "cartographer verifies architecture"],
            "crew": ["implementer owns scoped change", "reviewer owns independent verification"],
            "triage": ["does not implement", "issue-ready recommendations"],
        }

        for skill, phrases in expectations.items():
            with self.subTest(skill=skill):
                body = read(f"skills/{skill}/SKILL.md").lower()
                for phrase in phrases:
                    self.assertIn(phrase, body)

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
        self.assertIn("--scope user", readme)
        self.assertIn("--scope project", readme)
        self.assertIn("--dry-run", readme)
        self.assertIn("--force", readme)


if __name__ == "__main__":
    unittest.main()
