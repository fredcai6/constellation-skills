"""Issue #437: `_next_verbs()`'s comments must not restate a premise #422/#328 killed.

`_next_verbs()` explains WHY the `record` hint is never suppressed. Its stated
reason was *"record() carries no precondition/postcondition gate at all"*. That
was true when it was written and is now false: since #422/#328, `record(pass)`
REFUSES on an unmet `command`-kind postcondition (`scripts/checklist_engine.py`,
`record()`), exactly mirroring `advance()`'s check.

The comment's CONCLUSION survives -- the hint really is never suppressed -- but
for a different reason than the one written down. The live reason is INV-2:
`record()`'s only gate is `command`-kind, which is precisely the class
`_blocking_conditions()` excludes because `state()` must not probe a command;
and `--result fail` is never gated at all, so the `<pass|fail>` hint is always a
legal move.

A comment that reaches a right answer from a dead premise is worse than no
comment: the next reader who trusts the premise will extend it to a case where
it no longer holds. So this pins the false claim ABSENT and the live reason
PRESENT -- absence alone would pass on a comment deleted wholesale, which would
lose the INV-2 reasoning the code actually depends on.

Style follows `tests/test_prose_deletions.py`: claims pinned as phrases, in both
directions.
"""

from __future__ import annotations

import copy
import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("checklist_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load_engine()

FAIL_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


def normalized_source(fn) -> str:
    """`inspect.getsource` with runs of whitespace collapsed, so a phrase that
    the real source wraps across lines still matches as one phrase and a
    harmless reflow of the comment cannot break the pin."""
    return " ".join(inspect.getsource(fn).split())


# The dead premise, in both the wordings `_next_verbs` used for it (docstring
# summary and inline comment at the `record` hint).
DEAD_PREMISE = (
    "`resume`/`record` carry no precondition/postcondition gate at all",
    "record() carries no precondition/postcondition gate at all",
)

# Bare-phrase backstop: any sentence still asserting record is ungated, however
# it is reflowed, has to spell one of these.
DEAD_PHRASE = "record"
# Verb-agnostic on purpose, so it matches "carry no ..." and "carries no ..."
# alike -- a reflow that changes only the verb must not slip the claim past.
UNGATED_PHRASE = "no precondition/postcondition gate at all"


class RecordIsGatedInFact(unittest.TestCase):
    """The premise is dead as a matter of runtime behaviour, not opinion.

    This is the ground truth the comment has to agree with. It passes both
    before and after the comment fix -- it is here to prove the comment's
    premise is false, not to detect the comment change.
    """

    def _survey_with_failing_command_post(self) -> dict:
        return {
            "work_id": "t",
            "type": "survey",
            "items": ["v1"],
            "tasks": {
                "v1": {
                    "id": "v1", "title": "v1", "imperative": "check v1",
                    "preconditions": [],
                    "postconditions": [{
                        "id": "c1", "statement": "rail passes",
                        "check": {"kind": "command", "command": FAIL_COMMAND},
                        "satisfied": False,
                    }],
                    "constraints": [], "directives": None, "child_checklist": None,
                    "status": "in-progress", "status_detail": {},
                }
            },
        }

    def test_record_pass_refuses_on_unmet_command_postcondition(self):
        # #422/#328: this is the gate the stale comment says does not exist.
        cl = self._survey_with_failing_command_post()
        with self.assertRaises(E.EngineError) as ctx:
            E.record(copy.deepcopy(cl), "v1", "pass", None)
        self.assertIn("command postconditions unmet", str(ctx.exception))

    def test_record_fail_is_never_gated_by_it(self):
        # Half the live reason the hint survives: an honest failure is always
        # recordable, so the `<pass|fail>` hint is always a legal move.
        cl = self._survey_with_failing_command_post()
        self.assertEqual(E.record(copy.deepcopy(cl), "v1", "fail", None), "v1 recorded fail")

    def test_hint_is_still_offered_despite_the_failing_command_postcondition(self):
        # The other half: INV-2 forbids `state()` probing the command, so
        # `_blocking_conditions()` excludes command-kind and the hint stands.
        cl = self._survey_with_failing_command_post()
        verbs = E._next_verbs("v1", cl["tasks"]["v1"], "survey")
        self.assertTrue(any(v.startswith("record ") for v in verbs), f"record hint missing: {verbs}")


class NextVerbsCommentDoesNotRestateTheDeadPremise(unittest.TestCase):
    """(a) The falsified claim is gone from `_next_verbs`."""

    def setUp(self) -> None:
        self.src = normalized_source(E._next_verbs)

    def test_each_dead_premise_wording_absent(self) -> None:
        for claim in DEAD_PREMISE:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.src)

    def test_no_sentence_claims_record_is_ungated(self) -> None:
        # Reflow-proof backstop: if the "no gate at all" phrase survives at all,
        # it must not be the clause that governs `record`.
        for idx in range(len(self.src)):
            idx = self.src.find(UNGATED_PHRASE, idx)
            if idx == -1:
                break
            clause = self.src[max(0, idx - 80):idx]
            self.assertNotIn(
                DEAD_PHRASE, clause,
                f"`record` still governed by an ungated claim: ...{clause}{UNGATED_PHRASE}",
            )
            idx += 1


class NextVerbsCommentStatesTheLiveReason(unittest.TestCase):
    """(b) The load-bearing survivor: the INV-2 reason the hint is kept.

    Absence-only assertions would pass on a comment that simply deleted the
    explanation. The code's correctness rests on this reasoning, so it must be
    written down.
    """

    def setUp(self) -> None:
        self.src = normalized_source(E._next_verbs)

    def test_names_the_command_kind_gate_and_its_issue(self) -> None:
        self.assertIn("#422/#328", self.src)

    def test_names_command_kind_as_the_gate_record_does_carry(self) -> None:
        self.assertIn("`command`-kind postcondition", self.src)

    def test_names_result_fail_as_never_gated(self) -> None:
        self.assertIn("--result fail", self.src)


if __name__ == "__main__":
    unittest.main()
