"""The `plan` step's ordering and coverage rules, as SERVED to a Commander run.

Both rules were doctrine in `references/commander-core.md` and reached the
running agent nowhere: the served imperative is what an agent acts on, and
neither rule was in it.

1. **Ordering.** `design-it-twice-brief.md` runs its plan-phase form by
   "comparing gate *plans* for a confirmed issue", and `plan`'s `c5` gates the
   critic on "the converged candidate plan" -- both mean the candidates come
   BEFORE `execute.json` exists. The served imperative said "Then author the
   gate plan into execute.json" and only afterwards "Before the plan-approved
   checkpoint run plan-alternatives", which reads as author-then-justify. `c4`'s
   own wording ("before the plan freezes") does not catch that, because a plan
   authored but not yet approved has not frozen. Candidates generated against an
   incumbent argue for it; that is the bias the mechanism exists to defeat.

2. **Coverage.** "Confirm `execute.json` contains one gate for every file and
   decision-class in the issue's stated file-ownership scope" carries a named
   cost in doctrine -- the missing gate surfaces only at review, where it forces
   a reopen -- and neither the imperative nor any postcondition said it.

3. **Named artifacts.** Neither the candidates nor the critic's findings had a
   canonical path: doctrine only asked a dispatch to name "the equivalent
   stable artifact path", so every run invented one. That is two defects at
   once. A relaunched Commander cannot recover an artifact whose path it never
   fixed -- the same fragility `crew-handoffs/<gate>-<role>-result.md` exists to
   avoid -- and an artifact with no path can never be ordered against
   `execute.json` by any check. Naming them does not build the check; it
   removes the reason the check was impossible.

These are PROSE invariants. `c4` and `c5` have `check: null`, so nothing at
runtime distinguishes a run that ordered the work correctly from one that
attested it did. That limit is real, it is NOT fixed here, and `c4`/`c5` now
say so in their own statements rather than leaving a reader to infer it -- the
same honesty `context.c2` and `plan.c6` already practise about what they prove.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"


def plan() -> dict:
    return json.loads(SPINE.read_text(encoding="utf-8"))["tasks"]["plan"]


def imperative() -> str:
    return plan()["imperative"]


def condition(cond_id: str) -> dict:
    for cond in plan()["postconditions"]:
        if cond["id"] == cond_id:
            return cond
    raise AssertionError(f"plan has no postcondition {cond_id}")


class Ordering(unittest.TestCase):
    def test_the_imperative_names_the_order_explicitly(self):
        prose = imperative().lower()
        self.assertIn("do not reorder it", prose)
        self.assertIn("candidates, convergence, critic, execute.json", prose)

    def test_execute_json_is_authored_at_step_four_and_nowhere_earlier(self):
        """The ordering rule collapses if a candidate IS `execute.json`: the
        first candidate becomes the incumbent the others argue with.

        This used to be a standalone prohibition ("candidates are authored as
        candidate plans, never into execute.json"). A cold read counted the rule
        stated four separate times and called it anxiety rather than emphasis.
        It is now stated once, welded to the act it governs at step (4), which
        is where an agent is standing when it could get this wrong."""
        prose = imperative()
        self.assertIn("(4) Only then author the winner into execute.json", prose)
        # (1)-(3) hand candidates a destination of their own, so "not here"
        # never has to be said: the only execute.json write is at (4).
        self.assertEqual(prose.count("author the winner into execute.json"), 1)

    def test_the_imperative_names_the_author_then_justify_anti_pattern(self):
        """Stating the order is not enough on its own -- the failure it
        prevents is the one a reader will otherwise rationalise into."""
        prose = imperative().lower()
        self.assertIn("justification, not a comparison", prose)

    def test_c4_and_c5_deadline_on_authoring_not_on_freezing(self):
        """"Before the plan freezes" is satisfiable by authoring first and
        approving later, which is exactly the sequence being ruled out."""
        for cond_id in ("c4", "c5"):
            with self.subTest(cond=cond_id):
                statement = condition(cond_id)["statement"].lower()
                self.assertIn("execute.json is authored", statement)
                self.assertNotIn("before the plan freezes", statement)


class OwnershipScopeCoverage(unittest.TestCase):
    def test_the_imperative_requires_a_gate_per_ownership_scope_entry(self):
        prose = imperative().lower()
        self.assertIn("file-ownership scope", prose)
        self.assertIn("its own gate", prose)

    def test_the_imperative_defines_what_does_not_count_as_a_gate(self):
        """The consequence clause ("the miss surfaces at review, where it forces
        a reopen") was cut as motivation an agent cannot act on. This clause
        stays, because it is the operational definition c2's enumeration runs
        on: without it an agent satisfies the letter of c2 using deferral stubs
        that name a decision as handled somewhere else."""
        self.assertIn(
            'defers a decision as "handled elsewhere" is not that gate',
            imperative(),
        )

    def test_c2_states_the_coverage_requirement(self):
        """The condition an agent reads on refusal has to carry it too."""
        statement = condition("c2")["statement"].lower()
        self.assertIn("file-ownership scope", statement)
        self.assertIn("converged candidate plan", statement)


class VisualStructure(unittest.TestCase):
    """The four ordered steps and the freeze conditions are the parts an agent
    executes in sequence, and they had no visual handle: the whole instruction
    was one unbroken paragraph. Nothing in the engine forbids newlines --
    `render_human` interpolates the imperative and appends the conditions block
    after it -- the corpus had simply never used them. These pins keep the
    structure from being flattened back by a well-meaning reformat."""

    def test_each_numbered_step_starts_its_own_line(self):
        lines = [ln.strip() for ln in imperative().splitlines()]
        for marker in ("(1)", "(2)", "(3)", "(4)"):
            with self.subTest(step=marker):
                self.assertTrue(
                    any(ln.startswith(marker) for ln in lines),
                    f"{marker} must begin a line, not sit mid-paragraph",
                )

    def test_the_freeze_conditions_are_a_bulleted_list(self):
        lines = [ln.strip() for ln in imperative().splitlines()]
        bullets = [ln for ln in lines if ln.startswith("- ")]
        self.assertEqual(len(bullets), 3, f"expected 3 freeze bullets, got {bullets}")
        self.assertIn("Before the plan freezes:", imperative())

    def test_the_count_is_not_restated_now_that_the_list_is_visible(self):
        """"Three things must hold" was a reader's crutch for an unbroken
        paragraph and a maintenance liability once bulleted: add a fourth
        condition and the prose silently lies. The bullets carry the count."""
        self.assertNotIn("Three things", imperative())


class NamedArtifacts(unittest.TestCase):
    CANDIDATE = ".agent-work/<work-id>/plan-candidate-<constraint>.md"
    BRIEF = ".agent-work/<work-id>/PLAN_ALTERNATIVES.md"
    CRITIC = ".agent-work/<work-id>/PLAN_CRITIC.md"

    def test_the_imperative_names_all_three_paths(self):
        """An artifact the step does not name cannot be found after a relaunch
        and cannot be ordered against `execute.json` by any later check."""
        prose = imperative()
        for path in (self.CANDIDATE, self.BRIEF, self.CRITIC):
            with self.subTest(path=path):
                self.assertIn(path, prose)

    def test_c4_and_c5_name_the_artifacts_they_are_about(self):
        """The condition an agent reads on refusal has to say where the thing
        it is asserting about lives."""
        self.assertIn(self.CANDIDATE, condition("c4")["statement"])
        self.assertIn(self.BRIEF, condition("c4")["statement"])
        self.assertIn(self.CRITIC, condition("c5")["statement"])

    def test_each_path_is_given_at_the_step_that_produces_it(self):
        """The prose insisting the paths are "fixed, not per-run inventions"
        was cut: an agent handed three exact paths does not also need telling
        they are not inventions. What replaces it is placement -- each path
        appears inside the numbered step that writes it, so the agent reads it
        while doing that step rather than in a footnote after step (4)."""
        prose = imperative()
        step1 = prose.index("(1) Run plan-alternatives")
        step2 = prose.index("(2) Converge")
        step3 = prose.index("(3) Run a cold plan critic")
        step4 = prose.index("(4) Only then author")
        self.assertTrue(step1 < prose.index(self.CANDIDATE) < step2)
        self.assertTrue(step2 < prose.index(self.BRIEF) < step3)
        self.assertTrue(step3 < prose.index(self.CRITIC) < step4)


class HonestAboutNotBeingChecked(unittest.TestCase):
    """`context.c2` and `plan.c6` both state plainly what they do and do not
    prove. `c4` and `c5` asserted an ordering with `check: null` and said
    nothing -- the one place the corpus overclaimed by silence."""

    def test_c4_and_c5_declare_they_are_not_machine_verified(self):
        for cond_id in ("c4", "c5"):
            with self.subTest(cond=cond_id):
                self.assertIn("NOT machine-verified", condition(cond_id)["statement"])

    def test_c4_names_the_sequence_it_cannot_distinguish(self):
        """A bare 'not verified' is weaker than naming the exact run that would
        slip through, which is the one #1's ordering rule rules out."""
        statement = condition("c4")["statement"].lower()
        self.assertIn("authored first and attested afterwards", statement)

    def test_c4_and_c5_still_carry_no_check(self):
        """If a check ever lands, these tests must be revisited rather than
        left asserting a limit that no longer holds."""
        for cond_id in ("c4", "c5"):
            with self.subTest(cond=cond_id):
                self.assertIsNone(condition(cond_id)["check"])


class GreenAtEveryGateBoundary(unittest.TestCase):
    def test_the_imperative_requires_verification_green_at_each_boundary(self):
        prose = imperative().lower()
        self.assertIn("green at every gate boundary", prose)
        self.assertIn("known-red window", prose)


class MapEntryPointRelay(unittest.TestCase):
    def test_the_imperative_requires_handing_the_map_entry_point_down(self):
        """You did the map work at frame time; a crew re-deriving it pays for
        the same reading twice."""
        prose = imperative().lower()
        self.assertIn("map entry point", prose)
        self.assertIn("crew handoff", prose)


class TrivialChangeEscape(unittest.TestCase):
    def test_the_escape_is_one_act_recorded_on_both_c1_and_c6(self):
        """`c1` is attestable and `c6` is a waivable command check, so a
        trivial change that discharges only one of them is refused at advance
        with no instruction saying why."""
        prose = imperative().lower()
        self.assertIn("waive c6", prose)
        self.assertIn("attest c1", prose)


if __name__ == "__main__":
    unittest.main()
