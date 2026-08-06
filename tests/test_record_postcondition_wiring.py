"""Tests for #422 (epic-418 workstream D, gate g2): `record()`'s new command-kind
postcondition check (`scripts/checklist_engine.py`).

Before this change, `record()` (the survey verb) stored whatever result the agent
typed and never evaluated `postconditions` at all. This wires it to mirror
`advance()`'s existing pattern (reuse `_check_condition`, same `EngineError`
refusal shape) for `command`-kind postconditions ONLY, and ONLY when
`result == "pass"`:

  * RecordCommandPostconditionTests -- the generic mechanism: a passing command
    postcondition lets `record(pass)` through; a failing one refuses it;
    `record(fail)` is never blocked by the same failing check; an item with no
    command postcondition is unaffected (the regression floor).
  * InterrogationDeliberateBreakageTests / FowlerDeliberateBreakageTests -- the
    acceptance criteria: the REAL, unmodified `scripts/verify_interrogation.py`
    and `scripts/verify_fowler_pass.py` rails, invoked as a subprocess via a real
    command postcondition against a genuinely bad scratch record written to
    `tmp_path`, actually refuse `record(pass)`. Minimal invalid fixtures follow
    the shapes in `tests/test_interrogation.py` (`_decision(human_answer="")` --
    a resolved decision self-answered by the agent) and `tests/test_fowler_pass.py`
    (`_all_absent()` with one baseline smell dropped -- a skipped smell).

Loaded the same way as `tests/test_checklist_engine.py`: importlib from
ROOT/scripts, so these tests run against the real vendored engine module, not an
installed copy.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
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

PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
FAIL_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


def survey_item(iid, status="in-progress", postconditions=None):
    return {
        "id": iid, "title": iid, "imperative": f"check {iid}",
        "preconditions": [], "postconditions": postconditions or [],
        "constraints": [], "directives": None, "child_checklist": None,
        "status": status, "status_detail": {},
        "result": None, "finding": None, "evidence": [], "rework_count": 0,
    }


def survey(**tasks):
    items = list(tasks.keys())
    return {"work_id": "s", "type": "survey", "config": {},
            "items": items, "tasks": tasks, "consolidation": None,
            "triage_candidates": [], "blockers": []}


def command_post(command, cid="c1"):
    return [{"id": cid, "statement": "command check", "check": {"kind": "command", "command": command}, "satisfied": False}]


# --------------------------------------------------------------------------- #
class RecordCommandPostconditionTests(unittest.TestCase):
    """The generic mechanism, mirroring advance()'s own pattern."""

    def test_pass_with_passing_command_postcondition_succeeds(self):
        cl = survey(v1=survey_item("v1", postconditions=command_post(PASS_COMMAND)))
        msg = E.record(cl, "v1", "pass", None)
        self.assertEqual(msg, "v1 recorded pass")
        self.assertEqual(cl["tasks"]["v1"]["status"], "complete")
        self.assertEqual(cl["tasks"]["v1"]["result"], "pass")

    def test_pass_with_failing_command_postcondition_refused(self):
        cl = survey(v1=survey_item("v1", postconditions=command_post(FAIL_COMMAND)))
        with self.assertRaises(E.EngineError) as ctx:
            E.record(cl, "v1", "pass", None)
        self.assertIn("c1", str(ctx.exception))
        # A refusal must stop the caller, not quietly relabel the request as fail.
        self.assertIsNone(cl["tasks"]["v1"]["result"])
        self.assertEqual(cl["tasks"]["v1"]["status"], "in-progress")

    def test_fail_never_blocked_by_failing_command_postcondition(self):
        cl = survey(v1=survey_item("v1", postconditions=command_post(FAIL_COMMAND)))
        msg = E.record(cl, "v1", "fail", "the real reason it failed")
        self.assertEqual(msg, "v1 recorded fail: the real reason it failed")
        self.assertEqual(cl["tasks"]["v1"]["status"], "complete")
        self.assertEqual(cl["tasks"]["v1"]["result"], "fail")

    def test_item_with_no_command_postcondition_unaffected(self):
        # Regression floor: the vast majority of survey items carry no
        # postcondition at all (or a null-kind one) -- record() must behave
        # byte-for-byte as before for those.
        cl = survey(v1=survey_item("v1"))
        self.assertEqual(E.record(cl, "v1", "pass", None), "v1 recorded pass")
        self.assertEqual(cl["tasks"]["v1"]["status"], "complete")

    def test_null_kind_postcondition_stays_unevaluated(self):
        # #422 D-scope ruling: null-kind postconditions remain out of scope for
        # record() -- an unsatisfied null-kind postcondition never blocks pass.
        post = [{"id": "c1", "statement": "manually checked", "check": None, "satisfied": False}]
        cl = survey(v1=survey_item("v1", postconditions=post))
        self.assertEqual(E.record(cl, "v1", "pass", None), "v1 recorded pass")

    def test_record_refused_on_gated_unchanged(self):
        # Existing guard (unrelated to this change) must still hold.
        cl = {"work_id": "g", "type": "gated", "config": {}, "items": ["g1"],
              "tasks": {"g1": survey_item("g1")}, "consolidation": None,
              "triage_candidates": [], "blockers": []}
        with self.assertRaises(E.EngineError):
            E.record(cl, "g1", "pass", None)


# --------------------------------------------------------------------------- #
# Minimal fixtures mirroring tests/test_interrogation.py's _fact/_decision/_record.
def _fact(**overrides) -> dict:
    q = {
        "id": "q1", "kind": "fact",
        "question": "which module owns the retry policy?",
        "status": "resolved", "resolution": "retry policy lives in net/backoff.py",
        "code_evidence": "net/backoff.py:42 defines RetryPolicy",
    }
    q.update(overrides)
    return q


def _decision(**overrides) -> dict:
    q = {
        "id": "q2", "kind": "decision",
        "question": "should retries be capped at 3 or 5?",
        "status": "resolved", "resolution": "cap at 5",
        "human_answer": "the counterpart chose 5 to match the upstream SLA",
    }
    q.update(overrides)
    return q


def _interrogation_record(**overrides) -> dict:
    rec = {
        "goal": "resolve the retry-policy design ambiguity",
        "mode": "interactive",
        "questions": [_fact(), _decision()],
        "signoff": {"by": "fredc (counterpart)", "statement": "yes, questioning is complete"},
        "consolidated": True,
    }
    rec.update(overrides)
    return rec


class InterrogationDeliberateBreakageTests(unittest.TestCase):
    """Real, unmodified scripts/verify_interrogation.py run as a subprocess
    against real (good/bad) scratch records in a tmp dir -- never mocked."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _item_for(self, record_path: Path) -> dict:
        command = f'python scripts/verify_interrogation.py "{record_path.as_posix()}"'
        return survey_item("zc-consolidate", postconditions=command_post(command))

    def test_valid_record_lets_record_pass_through(self):
        record_path = Path(self.tmp.name) / "interrogation-record.json"
        record_path.write_text(json.dumps(_interrogation_record()), encoding="utf-8")
        cl = survey(**{"zc-consolidate": self._item_for(record_path)})
        msg = E.record(cl, "zc-consolidate", "pass", None)
        self.assertEqual(msg, "zc-consolidate recorded pass")
        self.assertEqual(cl["tasks"]["zc-consolidate"]["status"], "complete")

    def test_self_answered_decision_refuses_record_pass(self):
        # DELIBERATE BREAKAGE: a resolved decision with an empty human_answer is
        # the self-answered-decision shape verify_interrogation.py itself refuses
        # (tests/test_interrogation.py::DecisionBlockTests).
        bad_record = _interrogation_record(questions=[_fact(), _decision(human_answer="")])
        record_path = Path(self.tmp.name) / "bad-interrogation-record.json"
        record_path.write_text(json.dumps(bad_record), encoding="utf-8")
        cl = survey(**{"zc-consolidate": self._item_for(record_path)})
        with self.assertRaises(E.EngineError) as ctx:
            E.record(cl, "zc-consolidate", "pass", None)
        self.assertIn("c1", str(ctx.exception))
        self.assertIsNone(cl["tasks"]["zc-consolidate"]["result"])
        # Never blocked from recording the honest failure.
        cl2 = copy.deepcopy(cl)
        self.assertEqual(E.record(cl2, "zc-consolidate", "fail", "self-answered decision"),
                          "zc-consolidate recorded fail: self-answered decision")


# --------------------------------------------------------------------------- #
# Minimal fixtures mirroring tests/test_fowler_pass.py's _smell/_all_absent/_record.
REQUIRED_SMELLS = (
    "long-method", "large-class", "duplicated-code", "feature-envy", "data-clumps",
    "primitive-obsession", "long-parameter-list", "shotgun-surgery", "divergent-change",
    "message-chains", "speculative-generality", "comments-as-deodorant",
)


def _smell(name: str, verdict: str = "absent", **overrides) -> dict:
    s = {"smell": name, "verdict": verdict, "finding": "", "override": None}
    s.update(overrides)
    return s


def _all_absent() -> list:
    return [_smell(name) for name in REQUIRED_SMELLS]


def _fowler_record(smells=None, **overrides) -> dict:
    rec = {
        "work_id": "issue-x",
        "diff_ref": "the change under review",
        "smells": smells if smells is not None else _all_absent(),
        "rail_exception": None,
    }
    rec.update(overrides)
    return rec


class FowlerDeliberateBreakageTests(unittest.TestCase):
    """Real, unmodified scripts/verify_fowler_pass.py run as a subprocess against
    real (good/bad) scratch records in a tmp dir -- never mocked."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _item_for(self, record_path: Path) -> dict:
        command = f'python scripts/verify_fowler_pass.py "{record_path.as_posix()}"'
        return survey_item("r6-fowler", postconditions=command_post(command))

    def test_complete_pass_lets_record_pass_through(self):
        record_path = Path(self.tmp.name) / "fowler-pass-record.json"
        record_path.write_text(json.dumps(_fowler_record()), encoding="utf-8")
        cl = survey(**{"r6-fowler": self._item_for(record_path)})
        msg = E.record(cl, "r6-fowler", "pass", None)
        self.assertEqual(msg, "r6-fowler recorded pass")
        self.assertEqual(cl["tasks"]["r6-fowler"]["status"], "complete")

    def test_skipped_smell_refuses_record_pass(self):
        # DELIBERATE BREAKAGE: dropping one baseline smell is the skipped-smell
        # shape verify_fowler_pass.py itself refuses
        # (tests/test_fowler_pass.py::VisitEverySmellTests::test_missing_smell_refused).
        smells = [s for s in _all_absent() if s["smell"] != "duplicated-code"]
        bad_record = _fowler_record(smells=smells)
        record_path = Path(self.tmp.name) / "bad-fowler-pass-record.json"
        record_path.write_text(json.dumps(bad_record), encoding="utf-8")
        cl = survey(**{"r6-fowler": self._item_for(record_path)})
        with self.assertRaises(E.EngineError) as ctx:
            E.record(cl, "r6-fowler", "pass", None)
        self.assertIn("c1", str(ctx.exception))
        self.assertIsNone(cl["tasks"]["r6-fowler"]["result"])
        # Never blocked from recording the honest failure.
        cl2 = copy.deepcopy(cl)
        self.assertEqual(E.record(cl2, "r6-fowler", "fail", "skipped a baseline smell"),
                          "r6-fowler recorded fail: skipped a baseline smell")


if __name__ == "__main__":
    unittest.main()
