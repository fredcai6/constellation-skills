"""Tests for the constellation-interrogator sharpening rail
(scripts/verify_interrogation.py).

The interrogator drives a survey to a joint understanding. This rail mechanically
enforces the two locked behaviors of DESIGN_SPEC Section D1 on the interrogation
RECORD (the survey's consolidated output):

  * FinishGateTests   -- no-quit-early: a record marked `consolidated` is REFUSED
                         unless it carries a joint-understanding sign-off (a real
                         `by` + `statement`) AND no question is still open. Loop
                         termination is not enough; the human sign-off is the gate.
  * DecisionBlockTests -- a `decision`-typed question marked resolved is REFUSED
                         without a non-empty `human_answer`: a decision is never
                         self-answered by the agent.
  * FactAllowedTests  -- a `fact`-typed question the agent resolved by exploring
                         code (non-empty `code_evidence`) is ALLOWED without a
                         human answer; a resolved fact with no evidence is refused.
  * RailExceptionTests -- a defended finish-gate exception passes ONLY with an
                         independent reviewer's co-sign + a log entry; self-
                         assertion never passes.
  * StructureTests    -- the record shape refusals + CLI exit codes.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fact(**overrides) -> dict:
    q = {
        "id": "q1",
        "kind": "fact",
        "question": "which module owns the retry policy?",
        "status": "resolved",
        "resolution": "retry policy lives in net/backoff.py",
        "code_evidence": "net/backoff.py:42 defines RetryPolicy",
    }
    q.update(overrides)
    return q


def _decision(**overrides) -> dict:
    q = {
        "id": "q2",
        "kind": "decision",
        "question": "should retries be capped at 3 or 5?",
        "status": "resolved",
        "resolution": "cap at 5",
        "human_answer": "the counterpart chose 5 to match the upstream SLA",
    }
    q.update(overrides)
    return q


def _signoff(**overrides) -> dict:
    s = {
        "by": "fredc (counterpart)",
        "statement": "yes, questioning is complete; we share the understanding",
    }
    s.update(overrides)
    return s


def _record(**overrides) -> dict:
    rec = {
        "goal": "resolve the retry-policy design ambiguity",
        "mode": "interactive",
        "questions": [_fact(), _decision()],
        "signoff": _signoff(),
        "consolidated": True,
    }
    rec.update(overrides)
    return rec


# --------------------------------------------------------------------------- #
class FinishGateTests(unittest.TestCase):
    """No-quit-early: consolidation refused without the joint-understanding sign-off."""

    def setUp(self):
        self.rail = load("verify_interrogation")

    def test_consolidated_with_signoff_and_no_open_passes(self):
        self.rail.verify_interrogation(_record())

    def test_consolidated_without_signoff_refused(self):
        # THE named case: the finish gate refuses consolidation absent the
        # joint-understanding sign-off evidence.
        rec = _record()
        del rec["signoff"]
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_consolidated_with_empty_signoff_statement_refused(self):
        rec = _record(signoff=_signoff(statement="   "))
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_consolidated_with_empty_signoff_by_refused(self):
        rec = _record(signoff=_signoff(by=""))
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_consolidated_with_open_question_refused(self):
        # Loop-terminated but an open question remains: not a joint understanding.
        rec = _record(questions=[_fact(), _decision(status="open")])
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_not_consolidated_needs_no_signoff(self):
        # Mid-interrogation: no sign-off demanded yet.
        rec = _record(consolidated=False, questions=[_fact(status="open")])
        del rec["signoff"]
        self.rail.verify_interrogation(rec)


# --------------------------------------------------------------------------- #
class DecisionBlockTests(unittest.TestCase):
    """A decision is never self-answered: resolved decision needs a human answer."""

    def setUp(self):
        self.rail = load("verify_interrogation")

    def test_decision_with_human_answer_passes(self):
        self.rail.verify_interrogation(_record(questions=[_decision()]))

    def test_decision_resolved_without_human_answer_refused(self):
        # THE named case: a decision-question marked resolved with no human answer
        # (the agent raced ahead and self-answered it) is refused.
        rec = _record(questions=[_decision(human_answer="")])
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_decision_resolved_missing_human_answer_key_refused(self):
        q = _decision()
        del q["human_answer"]
        rec = _record(questions=[q])
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_open_decision_needs_no_human_answer(self):
        # An unresolved decision is a legitimate mid-loop state (not consolidated).
        rec = _record(consolidated=False, questions=[_decision(status="open", human_answer="")])
        del rec["signoff"]
        self.rail.verify_interrogation(rec)


# --------------------------------------------------------------------------- #
class FactAllowedTests(unittest.TestCase):
    """A fact resolved by exploring code is allowed without a human answer."""

    def setUp(self):
        self.rail = load("verify_interrogation")

    def test_fact_resolved_by_code_evidence_passes(self):
        # THE named case: a fact-question the agent resolved by exploring the code
        # (code_evidence present, no human answer) is allowed.
        rec = _record(questions=[_fact()])
        self.rail.verify_interrogation(rec)

    def test_fact_resolved_without_evidence_refused(self):
        # The split's other edge: a resolved fact must be grounded in code/docs
        # evidence, not asserted.
        rec = _record(questions=[_fact(code_evidence="")])
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_fact_needs_no_human_answer(self):
        q = _fact()  # no human_answer key at all
        self.assertNotIn("human_answer", q)
        self.rail.verify_interrogation(_record(questions=[q]))


# --------------------------------------------------------------------------- #
class RailExceptionTests(unittest.TestCase):
    """A defended finish-gate exception needs an independent reviewer co-sign."""

    def setUp(self):
        self.rail = load("verify_interrogation")

    def test_reviewer_cosigned_exception_passes(self):
        rec = _record()
        del rec["signoff"]
        rec["rail_exception"] = {
            "reviewer_cosign": "reviewer-agent-7",
            "log": "async counterpart; reviewer co-signed the recorded understanding",
        }
        self.rail.verify_interrogation(rec)

    def test_self_asserted_exception_refused(self):
        rec = _record()
        del rec["signoff"]
        rec["rail_exception"] = {"reviewer_cosign": "", "log": "I judged it complete"}
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)

    def test_exception_does_not_excuse_self_answered_decision(self):
        # The exception covers the finish gate only, never the decision-block.
        rec = _record(questions=[_decision(human_answer="")])
        del rec["signoff"]
        rec["rail_exception"] = {"reviewer_cosign": "reviewer-agent-7", "log": "ok"}
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(rec)


# --------------------------------------------------------------------------- #
class StructureTests(unittest.TestCase):
    def setUp(self):
        self.rail = load("verify_interrogation")

    def test_empty_goal_refused(self):
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(_record(goal="  "))

    def test_bad_mode_refused(self):
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(_record(mode="telepathic"))

    def test_no_questions_refused(self):
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(_record(questions=[]))

    def test_bad_question_kind_refused(self):
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(_record(questions=[_fact(kind="vibe")]))

    def test_bad_question_status_refused(self):
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(_record(questions=[_fact(status="maybe")]))

    def test_duplicate_question_id_refused(self):
        with self.assertRaises(self.rail.InterrogationError):
            self.rail.verify_interrogation(_record(questions=[_fact(), _fact()]))

    def test_skipped_question_needs_neither_answer_nor_evidence(self):
        # A question an earlier answer overcame (survey `skip`) is inert here.
        rec = _record(questions=[_fact(status="skipped", code_evidence=""),
                                 _decision(status="skipped", human_answer="")])
        self.rail.verify_interrogation(rec)

    def test_cli_refuses_unsigned_consolidation_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "record.json"
            rec = _record()
            del rec["signoff"]
            p.write_text(json.dumps(rec), encoding="utf-8")
            self.assertNotEqual(0, self.rail.main([str(p)]))

    def test_cli_accepts_signed_consolidation_zero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "record.json"
            p.write_text(json.dumps(_record()), encoding="utf-8")
            self.assertEqual(0, self.rail.main([str(p)]))


if __name__ == "__main__":
    unittest.main()
