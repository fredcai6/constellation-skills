"""Pin the issue-#304 prose deletions in BOTH directions.

Two 86-word blocks of dead-path prose were deleted from the shipped Commander
templates: the `config_ref`-is-absent-by-design block in
`COMMANDER_SPINE.template.json` `tasks.context.imperative`, and its
byte-parallel twin in `EXECUTE_PLAN.template.json` `tasks.e0-context.imperative`.
They went because they are falsified in both directions at once: `docs/agents/`
**exists** in this repo (it holds `ORCHESTRATOR_CONTEXT.md`), so *"a skill-source
repo has no docs/agents/ overlay at all"* is false on its face; and Charter ships
a task that **writes** `docs/agents/engine-config.json`, so *"do NOT create the
overlay file"* contradicts a sibling role's shipped deliverable (#336).

**Absence alone is not the test.** The phrase `no docs/agents/ overlay at all`
occurred **twice** in `tasks.context.imperative`. The first occurrence is the
substitute-and-record rule -- the degraded-mode intake this whole issue exists to
*strengthen* -- and the second was inside the dead-path block. A naive
string-level delete removes both and silently strips degraded-mode intake while
appearing to remove only dead prose. That failure mode is pre-registered as
tripwire **T4** (`TRIPWIRES.md`, committed at `0119fa4` before any deletion
existed), and it is a tripwire aimed at the deleting edit itself.

So the deletion is pinned from both sides: the dead prose must be ABSENT, the
substitute-and-record rule must be PRESENT, and the phrase must occur EXACTLY
ONCE. An absence-only suite would pass just as happily on a template that had
deleted everything.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"
EXECUTE = ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json"

# The dead-path block's opening and closing phrases, and the two claims inside it
# that are individually falsified. Pinned as phrases rather than as one 86-word
# blob so a partial reintroduction cannot slip back in under a reflowed sentence.
SPINE_DEAD_OPENING = (
    "The checklist config_ref (docs/agents/engine-config.json) is absent-by-design"
)
EXECUTE_DEAD_OPENING = (
    "This checklist's config_ref (docs/agents/engine-config.json) is absent-by-design"
)
DEAD_CLAIMS = (
    "a skill-source repo has no docs/agents/ overlay at all",
    "do NOT create the overlay file",
    "rather than chasing the dead path",
)

# The load-bearing survivor: the substitute-and-record rule, quoted from the
# imperative as it must still read.
SUBSTITUTE_AND_RECORD = (
    "Where the repo carries no docs/agents/ overlay at all (e.g. a skill-source "
    "repo), substitute the closest repo doctrine you can find (README, "
    "CONTRIBUTING, top-level docs) and record the substitution"
)

OVERLAY_PHRASE = "no docs/agents/ overlay at all"


def imperative(path: Path, step: str) -> str:
    return json.loads(path.read_text(encoding="utf-8"))["tasks"][step]["imperative"]


class SpineDeadPathProseAbsent(unittest.TestCase):
    """(a) The dead-path block is gone from the Commander spine's context step."""

    def setUp(self) -> None:
        self.imp = imperative(SPINE, "context")

    def test_opening_phrase_absent(self) -> None:
        self.assertNotIn(SPINE_DEAD_OPENING, self.imp)

    def test_each_falsified_claim_absent(self) -> None:
        for claim in DEAD_CLAIMS:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.imp)


class ExecutePlanDeadPathProseAbsent(unittest.TestCase):
    """(b) The byte-parallel block is gone from the execute plan's context step."""

    def setUp(self) -> None:
        self.imp = imperative(EXECUTE, "e0-context")

    def test_opening_phrase_absent(self) -> None:
        self.assertNotIn(EXECUTE_DEAD_OPENING, self.imp)

    def test_each_falsified_claim_absent(self) -> None:
        for claim in DEAD_CLAIMS:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.imp)


class SubstituteAndRecordRuleSurvives(unittest.TestCase):
    """T4, as a test: the load-bearing FIRST occurrence must survive.

    This is the half that makes the deletion a real edit rather than a blunt
    one. Absence assertions alone would pass on an emptied imperative.
    """

    def setUp(self) -> None:
        self.imp = imperative(SPINE, "context")

    def test_substitute_and_record_rule_present(self) -> None:
        self.assertIn(SUBSTITUTE_AND_RECORD, self.imp)

    def test_overlay_phrase_occurs_exactly_once(self) -> None:
        # Twice meant one live rule plus one dead-path claim. Once means the
        # dead claim went and the rule stayed. Zero means T4 fired.
        self.assertEqual(self.imp.count(OVERLAY_PHRASE), 1)

    def test_surviving_occurrence_is_the_rule_not_the_dead_claim(self) -> None:
        # Belt and braces: the single surviving occurrence must sit inside the
        # substitute-and-record sentence, not somewhere else that merely
        # happens to spell the phrase.
        self.assertIn(OVERLAY_PHRASE, SUBSTITUTE_AND_RECORD)
        self.assertEqual(
            self.imp.index(OVERLAY_PHRASE),
            self.imp.index(SUBSTITUTE_AND_RECORD) + SUBSTITUTE_AND_RECORD.index(OVERLAY_PHRASE),
        )


class DeclaredConfigRefPathStillNamed(unittest.TestCase):
    """The deleted block mentioned a declared `context_refs` path.

    `test_context_declaration_lint.py` requires every declared `context_refs`
    path to appear verbatim in its task's imperative. `docs/agents/engine-config.json`
    is declared, and the deleted block named it -- so this asserts directly what
    that lint would otherwise catch only indirectly: the path survives the
    deletion because the intake sentence at the top of the imperative still
    names it.
    """

    def test_engine_config_path_still_named_in_context_imperative(self) -> None:
        self.assertIn("docs/agents/engine-config.json", imperative(SPINE, "context"))


if __name__ == "__main__":
    unittest.main()
