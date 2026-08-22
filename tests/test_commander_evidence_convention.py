"""Pin the g1-implement evidence convention (epic-559/b-instructions-to-checks, rework).

`g1-implement.c1` in EXECUTE_PLAN.template.json matches implementer-result evidence
on an exact field/value (currently {"status": "complete"}); the engine's artifact
match is exact dict equality (checklist_engine.py:846-860), so a Commander that
never learns the field name from a document will find the gate permanently
unsatisfiable. These tests assert the shipped check and the three places a
Commander would look (the template's own imperative, commander-core.md,
IMPLEMENTER_HANDOFF.template.md) name the same field and value, and that the
value is a lowercase member of the Crew Return Status enum -- so either the check
drifting or a doc drifting turns a test red.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTE_PLAN = ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json"
COMMANDER_CORE = ROOT / "skills" / "commander" / "references" / "commander-core.md"
IMPLEMENTER_HANDOFF = ROOT / "skills" / "commander" / "templates" / "IMPLEMENTER_HANDOFF.template.md"
STATUS_MODEL = ROOT / "skills" / "_shared" / "status-model.md"


def _g1_implement_task():
    data = json.loads(EXECUTE_PLAN.read_text(encoding="utf-8"))
    return data["tasks"]["g1-implement"]


def _crew_return_status_values():
    text = STATUS_MODEL.read_text(encoding="utf-8")
    m = re.search(r"Crew Return Status.*?```text\s*\n(.+?)\n```", text, re.DOTALL)
    assert m, "status-model.md: could not locate the Crew Return Status enum block"
    return [v.strip() for v in m.group(1).split("|")]


class EvidenceConventionTests(unittest.TestCase):
    def setUp(self):
        self.task = _g1_implement_task()
        self.c1 = next(c for c in self.task["postconditions"] if c["id"] == "c1")
        self.match = self.c1["check"]["match"]
        self.field, self.value = next(iter(self.match.items()))
        self.commander_core = COMMANDER_CORE.read_text(encoding="utf-8")
        self.implementer_handoff = IMPLEMENTER_HANDOFF.read_text(encoding="utf-8")

    def test_c1_match_value_is_a_lowercase_crew_return_status(self):
        # The engine's artifact match is exact dict equality: any case other
        # than the enum's own lowercase form can never satisfy it.
        enum_values = _crew_return_status_values()
        self.assertIn(self.value, enum_values,
                       f"g1-implement.c1 match value {self.value!r} is not one of {enum_values}")
        self.assertEqual(self.value, self.value.lower(),
                          f"g1-implement.c1 match value {self.value!r} is not lowercase")

    def test_g1_implement_imperative_names_the_field_and_lowercase_rule(self):
        # The template that carries the check must carry the instruction that
        # satisfies it (the shipped defect this gate exists to close).
        imperative = self.task["imperative"]
        self.assertIn(self.field, imperative,
                       "g1-implement imperative never names its own postcondition field")
        self.assertIn("Return status", imperative,
                       "g1-implement imperative never points at the IMPLEMENTER_RESULT's own Return status field")
        self.assertIn("lowercase", imperative.lower(),
                       "g1-implement imperative never states the lowercase requirement")

    def test_commander_core_repeats_the_convention(self):
        self.assertIn(self.field, self.commander_core,
                       "commander-core.md never names the implementer-result evidence field")
        self.assertIn("Return status", self.commander_core,
                       "commander-core.md never points at the IMPLEMENTER_RESULT's own Return status field")
        self.assertIn("lowercase", self.commander_core.lower(),
                       "commander-core.md never states the lowercase requirement")

    def test_implementer_handoff_template_repeats_the_convention(self):
        self.assertIn(self.field, self.implementer_handoff,
                       "IMPLEMENTER_HANDOFF.template.md never names the implementer-result evidence field")
        self.assertIn("Return status", self.implementer_handoff,
                       "IMPLEMENTER_HANDOFF.template.md never points at the Return status field")
        self.assertIn("lowercase", self.implementer_handoff.lower(),
                       "IMPLEMENTER_HANDOFF.template.md never states the lowercase requirement")


if __name__ == "__main__":
    unittest.main()
