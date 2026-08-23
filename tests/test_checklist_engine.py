import copy
import importlib.util
import inspect
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"
EXAMPLE = ROOT / "docs" / "examples" / "inner-loop-example.jsonc"


def load_engine():
    spec = importlib.util.spec_from_file_location("checklist_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load_engine()
PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
FAIL_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


def gate(iid, status="pending", command=None, preconds=None, why_exempt=True):
    # why_exempt defaults to True here so the legacy fixtures below (written before
    # #179 why-capture, and orthogonal to it) keep advancing silently. The ENGINE's
    # real default is NOT exempt (a missing key => not exempt); pass why_exempt=False
    # to build an explicitly non-exempt gate, or why_exempt=None to omit the key
    # entirely (an existing-shape/legacy gate). See WhyCapture / RefreshPrimitives.
    post = []
    if command is not None:
        post = [{"id": "c1", "statement": "tests pass", "check": {"kind": "command", "command": command}, "satisfied": False}]
    t = {
        "id": iid, "title": iid, "imperative": f"do {iid}",
        "preconditions": preconds or [], "postconditions": post,
        "constraints": [], "directives": None, "child_checklist": None,
        "status": status, "status_detail": {}, "result": None, "finding": None,
        "evidence": [], "rework_count": 0,
    }
    if why_exempt is not None:
        t["why_exempt"] = why_exempt
    return t


def gated(cap=3, **tasks):
    items = list(tasks.keys())
    return {"work_id": "t", "type": "gated", "config": {"rework_cap": cap},
            "items": items, "tasks": tasks, "consolidation": None,
            "triage_candidates": [], "blockers": []}


def survey_item(iid, status="pending"):
    return {"id": iid, "title": iid, "imperative": f"check {iid}",
            "preconditions": [], "postconditions": [], "constraints": [], "directives": None,
            "child_checklist": None, "status": status, "status_detail": {},
            "result": None, "finding": None, "evidence": [], "rework_count": 0}


def survey(**tasks):
    items = list(tasks.keys())
    return {"work_id": "s", "type": "survey", "config": {},
            "items": items, "tasks": tasks, "consolidation": None,
            "triage_candidates": [], "blockers": []}


def _make_non_active(cl, active_status="pending", active_status_detail=None):
    """Given a single-item GATED checklist built via `gated(g1=...)`, return
    an equivalent checklist with the SAME target task ('g1'), preceded by a
    dummy guard gate ('g0', status `active_status`) so g1 is guaranteed
    NON-active. This is the shape `recovery_for`'s active-gate-position
    branch needs and which no single-task fixture (used by every
    recovery-family test before rework 2) can ever express (Reviewer BLOCK,
    g3-review rework 2).

    `active_status` defaults to `"pending"`, matching every caller before
    rework 3->4 -- but a hardcoded `"pending"` guard could only ever express
    the ONE case where `start()`'s own bare "not the active gate; start
    {active} first" message happens to be self-recovering (Finding 1,
    g3-review rework 3->4): it could never express `in-progress` or
    `blocked`, exactly the two states where that unconditional advice
    itself refuses. Pass `active_status="in-progress"` / `"blocked"` to
    express those. `active_status_detail` optionally sets the guard gate's
    own `status_detail` (e.g. a `blocked` guard's restorability)."""
    new_cl = copy.deepcopy(cl)
    g0 = gate("g0", active_status)
    if active_status_detail is not None:
        g0["status_detail"] = active_status_detail
    new_cl["tasks"]["g0"] = g0
    new_cl["items"] = ["g0"] + new_cl["items"]
    return new_cl


def _run_main(cl, argv):
    """Run E.main() against `cl` (written to a tmp file) and capture
    (exit_code, stdout, stderr) -- the real CLI boundary, not a direct verb
    call, so this exercises dispatch()/main()'s COMPOSITION (rail position,
    recovery text) rather than the pure verb functions alone."""
    import contextlib
    import io
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "c.json"
        E.save(f, cl)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = E.main(["--file", str(f)] + argv)
        return code, out.getvalue(), err.getvalue()


def _run_at(path, argv):
    """Like `_run_main`, but against an EXISTING file path -- lets a sequence
    of CLI calls share persisted state across steps, so a two-step recovery
    (e.g. resume, THEN retry the original op) can be run end to end and the
    retry's own success asserted, not just that the first step didn't raise."""
    import contextlib
    import io
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = E.main(["--file", str(path)] + argv)
    return code, out.getvalue(), err.getvalue()


class CurrentAndOrdering(unittest.TestCase):
    def test_current_is_first_open_gate(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND), g2=gate("g2"))
        self.assertIn("ACTIVE g1", E.current(cl))

    def test_current_skips_terminal_items(self):
        cl = gated(g1=gate("g1", "complete"), g2=gate("g2", "pending", command=PASS_COMMAND))
        self.assertIn("ACTIVE g2", E.current(cl))

    def test_cannot_start_out_of_order(self):
        cl = gated(g1=gate("g1"), g2=gate("g2"))
        with self.assertRaises(E.EngineError):
            E.start(cl, "g2")

    def test_survey_all_visited_prompts_consolidate(self):
        cl = survey(v1=survey_item("v1", "complete"))
        self.assertIn("consolidate", E.current(cl))


class Preconditions(unittest.TestCase):
    def test_qualitative_precondition_blocks_until_attested(self):
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        with self.assertRaises(E.EngineError):
            E.start(cl, "g1")
        E.attest(cl, "g1", "p1", "preconditions", "checked it")
        self.assertEqual(E.start(cl, "g1"), "g1 -> in-progress")

    def test_command_precondition_refuses_start_until_it_passes(self):
        # The state-note precondition on `execute` relies on this seam: `start`
        # runs a command precondition and refuses the gate on non-zero exit.
        failing = [{"id": "p1", "statement": "state note present",
                    "check": {"kind": "command", "command": FAIL_COMMAND}, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=failing))
        with self.assertRaises(E.EngineError):
            E.start(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "pending")

        passing = [{"id": "p1", "statement": "state note present",
                    "check": {"kind": "command", "command": PASS_COMMAND}, "satisfied": False}]
        cl2 = gated(g1=gate("g1", "pending", preconds=passing))
        self.assertEqual(E.start(cl2, "g1"), "g1 -> in-progress")


class AdvanceGated(unittest.TestCase):
    def test_command_postcondition_pass_completes(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        self.assertTrue(any(e["type"] == "command-output" for e in cl["tasks"]["g1"]["evidence"]))

    def test_command_postcondition_fail_refuses_and_records(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["payload"]["exit"], 1)

    def test_artifact_postcondition_needs_matching_evidence(self):
        post = [{"id": "c2", "statement": "approved", "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}, "satisfied": False}]
        t = gate("g1", "in-progress")
        t["postconditions"] = post
        cl = gated(g1=t)
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")

    def test_record_refused_on_gated(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.record(cl, "g1", "pass", None)


def _artifact_gate(iid, status="in-progress"):
    """A gate whose single postcondition is an `artifact`/`review-result`
    check matching `verdict: APPROVE` (the gN-review / gN-integrate shape)."""
    t = gate(iid, status)
    t["postconditions"] = [{
        "id": "c1", "statement": "approved",
        "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
        "satisfied": False,
    }]
    return t


class AttestArtifactByReference(unittest.TestCase):
    def test_attest_artifact_by_reference_cross_task(self):
        # Attach the APPROVE review-result ONCE to g1 (gN-review); satisfy g2's
        # (gN-integrate) identical artifact postcondition by reference — no re-attach.
        cl = gated(g1=_artifact_gate("g1"), g2=_artifact_gate("g2"))
        self.assertEqual(E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"}),
                         "attached e-g1-1 (review-result) to g1")
        res = E.attest(cl, "g2", "c1", "postconditions", None, evidence_id="e-g1-1")
        self.assertEqual(res, "attested g2.c1 via e-g1-1")
        c = cl["tasks"]["g2"]["postconditions"][0]
        self.assertTrue(c["satisfied"])
        self.assertEqual(c["satisfied_by"], "e-g1-1")
        self.assertEqual(c["attested"], {"evidence": "e-g1-1", "note": None})

    def test_attest_artifact_survives_advance(self):
        # The `attested` short-circuit must hold through re-evaluation at advance:
        # g2's own evidence is empty, so without it the artifact branch would reset.
        cl = gated(g1=_artifact_gate("g1"), g2=_artifact_gate("g2"))
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        E.attest(cl, "g2", "c1", "postconditions", None, evidence_id="e-g1-1")
        self.assertEqual(E.advance(cl, "g2"), "g2 -> complete")
        self.assertEqual(cl["tasks"]["g2"]["status"], "complete")

    def test_attest_artifact_requires_evidence(self):
        cl = gated(g1=_artifact_gate("g1"))
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g1", "c1", "postconditions", None)

    def test_attest_artifact_evidence_not_found(self):
        cl = gated(g1=_artifact_gate("g1"))
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g1", "c1", "postconditions", None, evidence_id="e-nope-1")

    def test_attest_artifact_type_mismatch(self):
        cl = gated(g1=_artifact_gate("g1"), g2=_artifact_gate("g2"))
        E.attach(cl, "g1", "command-output", {"verdict": "APPROVE"})
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g2", "c1", "postconditions", None, evidence_id="e-g1-1")

    def test_attest_artifact_match_fails(self):
        cl = gated(g1=_artifact_gate("g1"), g2=_artifact_gate("g2"))
        E.attach(cl, "g1", "review-result", {"verdict": "BLOCK"})
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g2", "c1", "postconditions", None, evidence_id="e-g1-1")

    def test_attest_still_refuses_command_check(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g1", "c1", "postconditions", None, evidence_id="e-x-1")

    def test_reopen_clears_attested_marker(self):
        cl = gated(g1=_artifact_gate("g1"), g2=_artifact_gate("g2"))
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        E.attest(cl, "g2", "c1", "postconditions", None, evidence_id="e-g1-1")
        E.advance(cl, "g2")
        E.reopen(cl, "g2", "rework")
        c = cl["tasks"]["g2"]["postconditions"][0]
        self.assertNotIn("attested", c)
        self.assertFalse(c["satisfied"])

    def test_null_check_attest_unchanged(self):
        # backward compat: a check:null condition is still attested with just a note.
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        self.assertEqual(E.attest(cl, "g1", "p1", "preconditions", "checked it"),
                         "attested g1.p1")
        self.assertTrue(cl["tasks"]["g1"]["preconditions"][0]["satisfied"])

    def test_bare_postcondition_attest_falls_back_to_other_list(self):
        # A bare `attest <id> --cond c1` uses the default which=preconditions, but the
        # null postcondition lives in the postconditions list. The fallback finds it.
        post = [{"id": "c1", "statement": "docs updated", "check": None, "satisfied": False}]
        g = gate("g1", "in-progress")
        g["postconditions"] = post
        cl = gated(g1=g)
        self.assertEqual(E.attest(cl, "g1", "c1", "preconditions", "verified"),
                         "attested g1.c1")
        self.assertTrue(cl["tasks"]["g1"]["postconditions"][0]["satisfied"])

    def test_attest_not_found_names_both_lists(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError) as ctx:
            E.attest(cl, "g1", "nope", "preconditions", "note")
        msg = str(ctx.exception)
        self.assertIn("preconditions", msg)
        self.assertIn("postconditions", msg)


def _basis_gate(basis=None, cond_id="c1", statement="frame written"):
    post = [{"id": cond_id, "statement": statement, "check": None, "satisfied": False}]
    if basis is not None:
        post[0]["basis"] = basis
    t = gate("g1", "in-progress")
    t["postconditions"] = post
    return t


class BasisAttestGuard(unittest.TestCase):
    """569-w2-basis g1: attest()'s `check: null` branch grows a report-only
    guard for a basis-bearing condition. It NEVER raises and NEVER changes
    whether the attest succeeds -- see BasisRendering's docstring for the
    render half. A basis-bearing attest always attaches a `basis-check`
    evidence item recording {locator_kind, locator, resolved, problem},
    pass or fail, so a future promotion-to-blocking decision has a durable
    record to measure against (PLAN_CRITIC.md finding 5)."""

    def test_no_basis_attest_is_byte_identical_to_legacy(self):
        # Protected Intent: a check:null condition with no basis attests
        # EXACTLY as it did before this gate -- same return value, same
        # satisfied_by shape, and no basis-check evidence appears.
        cl = gated(g1=_basis_gate(basis=None))
        res = E.attest(cl, "g1", "c1", "postconditions", "checked it")
        self.assertEqual(res, "attested g1.c1")
        c = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(c["satisfied"])
        self.assertEqual(c["satisfied_by"], "checked it")
        self.assertEqual(cl["tasks"]["g1"]["evidence"], [])

    def test_no_note_attest_falls_back_to_attested_literal_unchanged(self):
        cl = gated(g1=_basis_gate(basis=None))
        E.attest(cl, "g1", "c1", "postconditions", None)
        c = cl["tasks"]["g1"]["postconditions"][0]
        self.assertEqual(c["satisfied_by"], "attested")
        self.assertEqual(cl["tasks"]["g1"]["evidence"], [])

    def test_abstain_basis_behaves_like_no_basis(self):
        basis = {"locator_kind": "abstain", "locator": {}}
        cl = gated(g1=_basis_gate(basis=basis))
        res = E.attest(cl, "g1", "c1", "postconditions", "checked it")
        self.assertEqual(res, "attested g1.c1")
        c = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(c["satisfied"])
        self.assertEqual(c["satisfied_by"], "checked it")
        # No basis-check evidence for abstain -- the explicit opt-out.
        self.assertEqual(cl["tasks"]["g1"]["evidence"], [])

    def test_file_basis_missing_target_is_report_only_and_records_unresolved(self):
        basis = {"locator_kind": "file", "locator": {"path": "does-not-exist.md"}}
        cl = gated(g1=_basis_gate(basis=basis))
        with tempfile.TemporaryDirectory() as d:
            # Report-only: the attest SUCCEEDS even though the locator target
            # is missing -- never raises.
            res = E.attest(cl, "g1", "c1", "postconditions", "checked it", base_dir=Path(d))
        self.assertEqual(res, "attested g1.c1")
        c = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(c["satisfied"])
        self.assertEqual(c["satisfied_by"], "checked it")
        evidence = cl["tasks"]["g1"]["evidence"]
        self.assertEqual(len(evidence), 1)
        ev = evidence[0]
        self.assertEqual(ev["type"], "basis-check")
        self.assertEqual(ev["payload"]["locator_kind"], "file")
        self.assertEqual(ev["payload"]["locator"], {"path": "does-not-exist.md"})
        self.assertFalse(ev["payload"]["resolved"])
        self.assertIsNotNone(ev["payload"]["problem"])

    def test_file_basis_present_target_is_report_only_and_records_resolved(self):
        basis = {"locator_kind": "file", "locator": {"path": "MISSION_FRAME.md"}}
        cl = gated(g1=_basis_gate(basis=basis))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "MISSION_FRAME.md").write_text("hello", encoding="utf-8")
            res = E.attest(cl, "g1", "c1", "postconditions", "checked it", base_dir=Path(d))
        self.assertEqual(res, "attested g1.c1")
        c = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(c["satisfied"])
        ev = cl["tasks"]["g1"]["evidence"][0]
        self.assertEqual(ev["type"], "basis-check")
        self.assertTrue(ev["payload"]["resolved"])
        self.assertIsNone(ev["payload"]["problem"])

    def test_file_basis_glob_below_min_matches_report_only_unresolved(self):
        basis = {"locator_kind": "file",
                 "locator": {"path": "*.absent", "glob": True, "min_matches": 1}}
        cl = gated(g1=_basis_gate(basis=basis))
        with tempfile.TemporaryDirectory() as d:
            E.attest(cl, "g1", "c1", "postconditions", "checked it", base_dir=Path(d))
        ev = cl["tasks"]["g1"]["evidence"][0]
        self.assertFalse(ev["payload"]["resolved"])

    def test_file_basis_glob_meeting_min_matches_resolved(self):
        basis = {"locator_kind": "file",
                 "locator": {"path": "*.md", "glob": True, "min_matches": 2}}
        cl = gated(g1=_basis_gate(basis=basis))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.md").write_text("x", encoding="utf-8")
            (Path(d) / "b.md").write_text("x", encoding="utf-8")
            E.attest(cl, "g1", "c1", "postconditions", "checked it", base_dir=Path(d))
        ev = cl["tasks"]["g1"]["evidence"][0]
        self.assertTrue(ev["payload"]["resolved"])

    def test_evidence_ref_basis_resolves_against_a_satisfied_sibling_condition(self):
        basis = {"locator_kind": "evidence_ref", "locator": {"task_id": "g0", "cond_id": "p1"}}
        g0 = gate("g0", "complete")
        g0["preconditions"] = [{"id": "p1", "statement": "upstream", "check": None,
                                 "satisfied": True, "satisfied_by": "e-g0-1"}]
        cl = gated(g0=g0, g1=_basis_gate(basis=basis))
        E.attest(cl, "g1", "c1", "postconditions", "checked it")
        ev = cl["tasks"]["g1"]["evidence"][0]
        self.assertTrue(ev["payload"]["resolved"])
        self.assertIsNone(ev["payload"]["problem"])

    def test_evidence_ref_basis_unresolved_when_sibling_condition_unsatisfied(self):
        basis = {"locator_kind": "evidence_ref", "locator": {"task_id": "g0", "cond_id": "p1"}}
        g0 = gate("g0", "in-progress")
        g0["preconditions"] = [{"id": "p1", "statement": "upstream", "check": None,
                                 "satisfied": False}]
        cl = gated(g0=g0, g1=_basis_gate(basis=basis))
        res = E.attest(cl, "g1", "c1", "postconditions", "checked it")
        # Report-only: still succeeds despite the unresolved locator.
        self.assertEqual(res, "attested g1.c1")
        ev = cl["tasks"]["g1"]["evidence"][0]
        self.assertFalse(ev["payload"]["resolved"])
        self.assertIsNotNone(ev["payload"]["problem"])

    def test_resolve_basis_locator_is_pure_for_evidence_ref(self):
        # Constraint: no filesystem/subprocess touch for evidence_ref.
        basis = {"locator_kind": "evidence_ref", "locator": {"task_id": "g0", "cond_id": "p1"}}
        g0 = gate("g0", "complete")
        g0["preconditions"] = [{"id": "p1", "statement": "upstream", "check": None,
                                 "satisfied": True, "satisfied_by": "e-g0-1"}]
        cl = gated(g0=g0)
        with mock.patch.object(E.subprocess, "run",
                                side_effect=AssertionError("touched subprocess")):
            problem = E._resolve_basis_locator(cl, None, basis)
        self.assertIsNone(problem)

    def test_attest_wires_base_dir_from_cli_dispatch_to_checklist_directory(self):
        # Fresh-process CLI boundary: dispatch() computes base_dir from the
        # checklist FILE's own directory (path.parent) -- prove attest's new
        # base_dir param actually receives that value end to end, not just
        # when called directly in-process.
        basis = {"locator_kind": "file", "locator": {"path": "sibling.md"}}
        cl = gated(g1=_basis_gate(basis=basis))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            (Path(d) / "sibling.md").write_text("x", encoding="utf-8")
            E.save(f, cl)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "c1",
                                          "--which", "postconditions", "--note", "checked"])
            self.assertEqual(code, 0, err)
            reloaded = E.load(f)
        ev = reloaded["tasks"]["g1"]["evidence"][0]
        self.assertEqual(ev["type"], "basis-check")
        self.assertTrue(ev["payload"]["resolved"], ev["payload"])


def _artifact_gate_matching(iid, match, status="in-progress"):
    t = gate(iid, status)
    t["postconditions"] = [{
        "id": "c1", "statement": "approved",
        "check": {"kind": "artifact", "evidence_type": "review-result", "match": match},
        "satisfied": False,
    }]
    return t


class ArtifactMatchListMembership(unittest.TestCase):
    """decision:match-shape-bare-list -- a list-valued match[k] means
    membership (`have in want`); scalar match[k] keeps `==` unchanged;
    a present-but-non-dict `match` is a clean refusal, never an
    AttributeError (decision:match-not-dict-is-shape-fault)."""

    def test_check_condition_list_match_membership_hit(self):
        t = _artifact_gate_matching("g1", {"verdict": ["APPROVE", "BLOCK"]})
        t["evidence"] = [{"id": "e1", "type": "review-result", "payload": {"verdict": "APPROVE"}, "produced_by": "reviewer", "ts": ""}]
        cond = t["postconditions"][0]
        self.assertTrue(E._check_condition(cond, t))
        self.assertTrue(cond["satisfied"])

    def test_check_condition_list_match_membership_miss(self):
        t = _artifact_gate_matching("g1", {"verdict": ["APPROVE", "BLOCK"]})
        t["evidence"] = [{"id": "e1", "type": "review-result", "payload": {"verdict": "PENDING"}, "produced_by": "reviewer", "ts": ""}]
        cond = t["postconditions"][0]
        self.assertFalse(E._check_condition(cond, t))
        self.assertFalse(cond["satisfied"])

    def test_check_condition_scalar_match_unchanged(self):
        cl = gated(g1=_artifact_gate("g1"))
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        E.attach(cl, "g1", "review-result", {"verdict": "BLOCK"})
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")

    def test_check_condition_non_dict_match_is_clean_refusal_not_crash(self):
        t = _artifact_gate_matching("g1", ["APPROVE", "BLOCK"])
        t["evidence"] = [{"id": "e1", "type": "review-result", "payload": {"verdict": "APPROVE"}, "produced_by": "reviewer", "ts": ""}]
        cond = t["postconditions"][0]
        self.assertFalse(E._check_condition(cond, t))
        self.assertFalse(cond["satisfied"])

    def test_attest_list_match_membership_hit(self):
        cl = gated(g1=_artifact_gate_matching("g1", {"verdict": ["APPROVE", "BLOCK"]}))
        E.attach(cl, "g1", "review-result", {"verdict": "BLOCK"})
        res = E.attest(cl, "g1", "c1", "postconditions", None, evidence_id="e-g1-1")
        self.assertEqual(res, "attested g1.c1 via e-g1-1")

    def test_attest_list_match_membership_miss(self):
        cl = gated(g1=_artifact_gate_matching("g1", {"verdict": ["APPROVE", "BLOCK"]}))
        E.attach(cl, "g1", "review-result", {"verdict": "PENDING"})
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g1", "c1", "postconditions", None, evidence_id="e-g1-1")

    def test_attest_non_dict_match_is_clean_engine_error_not_crash(self):
        cl = gated(g1=_artifact_gate_matching("g1", ["APPROVE", "BLOCK"]))
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        with self.assertRaises(E.EngineError):
            E.attest(cl, "g1", "c1", "postconditions", None, evidence_id="e-g1-1")


class SurveyAndConsolidation(unittest.TestCase):
    def test_record_fail_does_not_block(self):
        cl = survey(v1=survey_item("v1", "in-progress"), v2=survey_item("v2"))
        E.record(cl, "v1", "fail", "bad")
        self.assertEqual(cl["tasks"]["v1"]["status"], "complete")
        self.assertIn("ACTIVE v2", E.current(cl))

    def test_append_only_on_survey(self):
        cl = survey(v1=survey_item("v1", "complete"))
        E.append(cl, "v2", "extra", "check extra")
        self.assertEqual(cl["items"], ["v1", "v2"])
        gcl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.append(gcl, "g2", "x", "y")

    def test_consolidate_refuses_unvisited(self):
        cl = survey(v1=survey_item("v1", "complete"), v2=survey_item("v2"))
        with self.assertRaises(E.EngineError):
            E.consolidate(cl, "APPROVE", None, None)

    def test_consolidate_guard_blocks_approve_over_fail(self):
        cl = survey(v1=survey_item("v1", "complete"))
        cl["tasks"]["v1"]["result"] = "fail"
        cl["tasks"]["v1"]["finding"] = "nope"
        with self.assertRaises(E.EngineError):
            E.consolidate(cl, "APPROVE", None, None)
        # override allowed
        E.consolidate(cl, "APPROVE", None, "accepted risk")
        self.assertEqual(cl["consolidation"]["verdict"], "APPROVE")

    def test_consolidate_block_over_fail_ok(self):
        cl = survey(v1=survey_item("v1", "complete"))
        cl["tasks"]["v1"]["result"] = "fail"
        cl["tasks"]["v1"]["finding"] = "nope"
        msg = E.consolidate(cl, "BLOCK", None, None)
        self.assertIn("BLOCK", msg)
        self.assertEqual(cl["consolidation"]["findings"], ["v1: nope"])


class ReworkCap(unittest.TestCase):
    def test_reopen_increments_then_escalates(self):
        cl = gated(cap=1, g1=gate("g1", "complete", command=PASS_COMMAND))
        msg = E.reopen(cl, "g1", "redo")
        self.assertIn("reopened", msg)
        self.assertEqual(cl["tasks"]["g1"]["rework_count"], 1)
        cl["tasks"]["g1"]["status"] = "complete"  # pretend it was re-advanced
        msg = E.reopen(cl, "g1", "still wrong")
        self.assertIn("ESCALATED", msg)
        self.assertEqual(cl["tasks"]["g1"]["status"], "blocked")
        self.assertTrue(cl["blockers"])

    def test_reopen_resets_postconditions(self):
        cl = gated(cap=3, g1=gate("g1", "complete", command=PASS_COMMAND))
        cl["tasks"]["g1"]["postconditions"][0]["satisfied"] = True
        E.reopen(cl, "g1", "redo")
        self.assertFalse(cl["tasks"]["g1"]["postconditions"][0]["satisfied"])


class BubbleUp(unittest.TestCase):
    def test_block_appends_blocker(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "stuck", "user", "ask")
        self.assertEqual(cl["blockers"][0]["item"], "g1")

    def test_flag_candidate(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.flag_candidate(cl, "g1", "found unrelated thing")
        self.assertEqual(cl["triage_candidates"][0]["from"], "g1")


class CliAndExample(unittest.TestCase):
    def _strip_jsonc(self, text):
        out, i, n, instr, esc = [], 0, len(text), False, False
        while i < n:
            c = text[i]
            if instr:
                out.append(c)
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    instr = False
                i += 1
                continue
            if c == '"':
                instr = True
                out.append(c)
                i += 1
                continue
            if c == "/" and i + 1 < n and text[i + 1] == "/":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            out.append(c)
            i += 1
        return "".join(out)

    def test_example_artifacts_load_and_walk(self):
        clean = self._strip_jsonc(EXAMPLE.read_text(encoding="utf-8")).strip()
        dec = json.JSONDecoder()
        objs, idx = [], 0
        while idx < len(clean):
            while idx < len(clean) and clean[idx] in " \t\r\n":
                idx += 1
            if idx >= len(clean):
                break
            obj, idx = dec.raw_decode(clean, idx)
            objs.append(obj)
        self.assertEqual(len(objs), 2)
        execute = next(o for o in objs if o["type"] == "gated")
        review = next(o for o in objs if o["type"] == "survey")
        self.assertIn("ACTIVE g1", E.current(execute))  # g1 reopened
        self.assertEqual(review["consolidation"]["verdict"], "BLOCK")

    def test_cli_current_and_refusal(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(E.main(["--file", str(f), "current"]), 0)
            # advancing a failing gate refuses (exit 1) but persists the command evidence
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 1)
            reloaded = E.load(f)
            self.assertTrue(reloaded["tasks"]["g1"]["evidence"])


class Hardening(unittest.TestCase):
    def _review_gate(self, status="in-progress"):
        t = gate("g1", status)
        t["postconditions"] = [{
            "id": "c2", "statement": "approved",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        }]
        t["child_checklist"] = "child"
        return gated(g1=t)

    def test_advance_takes_no_from_child(self):
        """#634 regrowth guard: `advance` closes a gate on the evidence ON it,
        never on a path named in the call.

        `--from-child` read a child checklist's `consolidation` and attached it
        as the gate's `review-result` before advancing. It was cut as dead
        weight -- measured over the whole corpus, every gate declaring a
        `child_checklist` carried NO review-result and all 253 review-results on
        disk sat on gates declaring NO child. It also let any JSON file with a
        `consolidation` key close a gate, measured live on a fabricated APPROVE.

        Pinned as an ABSENCE rather than deleted quietly, because this repo's
        record is that a retired path grows back (see
        `tests/test_cli_retirement_guard.py`, written for the same reason). The
        signature and the CLI are checked separately: a re-added parameter with
        no flag, or a flag with no parameter, each fail alone.
        """
        self.assertNotIn("from_child", inspect.signature(E.advance).parameters)

        ns = E.parse_args(["--file", "x.json", "advance", "g1"])
        self.assertFalse(
            hasattr(ns, "from_child"),
            "the advance subparser declares --from-child again; it was cut at #634",
        )

    def test_the_from_child_guard_can_fail(self):
        """Positive control for the guard above -- a check that cannot fail is
        not evidence. A stand-in carrying the retired shape is caught by the
        same two predicates."""
        def advance(cl, iid, from_child=None):  # the retired signature
            return None
        self.assertIn("from_child", inspect.signature(advance).parameters)

    def test_config_ref_resolves_rework_cap(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "charter.json"
            E.save(cfg, {"config": {"rework_cap": 1}})
            cl = {"work_id": "t", "type": "gated", "config_ref": "charter.json",
                  "items": ["g1"], "tasks": {"g1": gate("g1", "complete", command=PASS_COMMAND)},
                  "consolidation": None, "triage_candidates": [], "blockers": []}
            resolved = E.load_config(cl, Path(d))
            self.assertEqual(E.rework_cap(resolved), 1)
            # reopen via dispatch should escalate on the 2nd attempt using the resolved cap
            import types
            ns = types.SimpleNamespace(verb="reopen", id="g1", reason="redo")
            E.dispatch(cl, ns, base_dir=Path(d))           # 1 -> in-progress
            cl["tasks"]["g1"]["status"] = "complete"
            msg = E.dispatch(cl, ns, base_dir=Path(d))     # 2 -> escalate (cap 1)
            self.assertIn("ESCALATED", msg)

    def test_inline_config_overrides_ref(self):
        cl = {"work_id": "t", "type": "gated", "config": {"rework_cap": 9},
              "config_ref": "nonexistent.json", "items": [], "tasks": {}}
        self.assertEqual(E.rework_cap(E.load_config(cl, Path("."))), 9)

    def test_attach_via_field_pairs_avoids_shell_json(self):
        import types
        ns = types.SimpleNamespace(payload_file=None, payload=None, field=["verdict=APPROVE"])
        cl = self._review_gate()
        E.attach(cl, "g1", "review-result", E.build_payload(ns))
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")


def _waivable_gate(iid, command, status="in-progress"):
    """A gate whose command postcondition carries an override policy."""
    t = gate(iid, status, command=command)
    t["postconditions"][0]["override_policy"] = {
        "allowed": True, "authority": "human", "reason_required": True,
    }
    return t


class Waiver(unittest.TestCase):
    def test_failed_command_check_refuses_advance(self):
        # mirrors AdvanceGated; kept here as the baseline the waiver path relaxes
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")

    def test_command_output_records_exit_status_on_failure(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["type"], "command-output")
        self.assertEqual(ev["payload"]["exit"], 1)

    def test_allowed_waiver_marks_condition_satisfied(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        msg = E.waive(cl, "g1", "c1", "postconditions", "human", "non-blocking for docs")
        self.assertIn("waived g1.c1", msg)
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(cond["satisfied"])
        self.assertTrue(cond["waived"])
        self.assertEqual(cond["satisfied_by"], cond["waived"]["evidence"])

    def test_waived_failing_command_lets_advance_succeed(self):
        # hazard #3: a waived FAILING command must NOT be re-run and un-waived at advance
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        E.waive(cl, "g1", "c1", "postconditions", "human", "accepted risk")
        msg = E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        self.assertIn("WAIVED", msg)
        # the waiver survived re-evaluation
        self.assertTrue(cl["tasks"]["g1"]["postconditions"][0]["waived"])

    def test_waiver_refused_when_no_override_policy(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.waive(cl, "g1", "c1", "postconditions", "human", "please")
        self.assertFalse(cl["tasks"]["g1"]["postconditions"][0].get("waived"))

    def test_waiver_refused_when_override_not_allowed(self):
        t = gate("g1", "in-progress", command=FAIL_COMMAND)
        t["postconditions"][0]["override_policy"] = {"allowed": False}
        cl = gated(g1=t)
        with self.assertRaises(E.EngineError):
            E.waive(cl, "g1", "c1", "postconditions", "human", "please")

    def test_force_waiver_succeeds_without_policy_and_records_forced(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        msg = E.waive(cl, "g1", "c1", "postconditions", "human", "emergency", forced=True)
        self.assertIn("FORCED", msg)
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(cond["waived"]["forced"])
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["type"], "waiver")
        self.assertTrue(ev["payload"]["forced"])
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete (WAIVED postconditions ['c1'])")

    def test_waiver_requires_authority(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.waive(cl, "g1", "c1", "postconditions", "", "reason")

    def test_waiver_requires_reason_when_required(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.waive(cl, "g1", "c1", "postconditions", "human", "   ")

    def test_force_waiver_requires_reason(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with self.assertRaises(E.EngineError):
            E.waive(cl, "g1", "c1", "postconditions", "human", None, forced=True)

    def test_waiver_evidence_records_cond_authority_reason(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        E.waive(cl, "g1", "c1", "postconditions", "human", "pyright non-blocking")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["type"], "waiver")
        self.assertEqual(ev["payload"]["cond"], "c1")
        self.assertEqual(ev["payload"]["authority"], "human")
        self.assertEqual(ev["payload"]["reason"], "pyright non-blocking")

    def test_waiver_evidence_produced_by_echoes_authority(self):
        # #503: produced_by must echo the actual authority passed, never the
        # hardcoded literal "human".
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        E.waive(cl, "g1", "c1", "postconditions", "commander", "accepted risk")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["produced_by"], "commander")

    def test_waiver_authority_mismatch_is_report_only(self):
        t = _waivable_gate("g1", FAIL_COMMAND)
        t["postconditions"][0]["override_policy"]["authority"] = "commander"
        cl = gated(g1=t)
        msg = E.waive(cl, "g1", "c1", "postconditions", "implementer", "accepted risk")
        # never refuses or blocks on the mismatch -- same success shape as before
        self.assertIn("waived g1.c1", msg)
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertTrue(ev["payload"]["authority_mismatch"])
        self.assertEqual(ev["payload"]["expected_authority"], "commander")
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertTrue(cond["waived"]["authority_mismatch"])
        self.assertEqual(cond["waived"]["expected_authority"], "commander")
        self.assertTrue(cond["satisfied"])

    def test_waiver_authority_mismatch_is_case_and_whitespace_normalized(self):
        t = _waivable_gate("g1", FAIL_COMMAND)
        t["postconditions"][0]["override_policy"]["authority"] = "  Commander  "
        cl = gated(g1=t)
        E.waive(cl, "g1", "c1", "postconditions", "commander", "accepted risk")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertNotIn("authority_mismatch", ev["payload"])
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertNotIn("authority_mismatch", cond["waived"])

    def test_waiver_no_mismatch_fields_when_authority_matches(self):
        t = _waivable_gate("g1", FAIL_COMMAND)
        t["postconditions"][0]["override_policy"]["authority"] = "human"
        cl = gated(g1=t)
        E.waive(cl, "g1", "c1", "postconditions", "human", "accepted risk")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertNotIn("authority_mismatch", ev["payload"])
        self.assertNotIn("expected_authority", ev["payload"])
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertNotIn("authority_mismatch", cond["waived"])
        self.assertNotIn("expected_authority", cond["waived"])

    def test_waiver_no_mismatch_fields_when_policy_authority_absent(self):
        # policy.get("authority") absent entirely -- nothing to compare against,
        # today's silent pass stays unchanged.
        t = gate("g1", "in-progress", command=FAIL_COMMAND)
        t["postconditions"][0]["override_policy"] = {"allowed": True, "reason_required": True}
        cl = gated(g1=t)
        self.assertNotIn("authority", cl["tasks"]["g1"]["postconditions"][0]["override_policy"])
        E.waive(cl, "g1", "c1", "postconditions", "human", "accepted risk")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertNotIn("authority_mismatch", ev["payload"])
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertNotIn("authority_mismatch", cond["waived"])

    def test_reopen_clears_waiver(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        E.waive(cl, "g1", "c1", "postconditions", "human", "accepted")
        E.advance(cl, "g1")
        E.reopen(cl, "g1", "redo it properly")
        self.assertFalse(cl["tasks"]["g1"]["postconditions"][0].get("waived"))

    def test_cli_waive_then_advance(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            # advancing a failing gate refuses
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 1)
            # waive it through the CLI
            self.assertEqual(
                E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                        "--authority", "human", "--reason", "accepted risk"]), 0)
            # now advance succeeds and the waiver persisted
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            reloaded = E.load(f)
            self.assertEqual(reloaded["tasks"]["g1"]["status"], "complete")
            self.assertTrue(reloaded["tasks"]["g1"]["postconditions"][0]["waived"])
            self.assertTrue(any(e["type"] == "waiver" for e in reloaded["tasks"]["g1"]["evidence"]))

    def test_cli_waive_refused_without_policy(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                        "--authority", "human", "--reason", "x"]), 1)


class WaiveExemptFromSessionGate(unittest.TestCase):
    """B1 (deficiency cleanup batch A+B): `waive` is exempt from the SESSION
    gate specifically -- not removed from `MUTATING_VERBS`, so the audit
    trail (journaling) still fires. This is what used to force the five-step
    handshake (release -> claim -> waive -> release -> reclaim) for the
    sanctioned case: a parent waiving a child's condition while the child
    holds a fresh lease of its own."""

    def test_cross_session_waive_succeeds_while_a_different_session_holds_the_lease(self):
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, cl)
            # the CHILD claims its own fresh (non-stale) lease
            self.assertEqual(
                E.main(["--file", str(f), "claim", "--session-id", "child-1",
                        "--claimed-by", "implementer"]), 0)
            # the PARENT -- a DIFFERENT session, no takeover, no --force --
            # waives the child's condition. Before B1 this was refused by
            # the session gate exactly as a `start`/`advance` would be.
            code = E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                            "--authority", "human", "--reason", "accepted risk",
                            "--session-id", "parent-1"])
            self.assertEqual(code, 0)
            reloaded = E.load(f)
            self.assertTrue(reloaded["tasks"]["g1"]["postconditions"][0]["waived"])
            # the CHILD's lease itself is untouched -- waive is not a takeover
            self.assertEqual(reloaded["engine_session"]["session_id"], "child-1")

    def test_cross_session_waive_is_journaled(self):
        # waive stays in MUTATING_VERBS (B1's explicit constraint), so
        # main()'s journaling branch -- which reads that same set -- still
        # appends a line for it. This is the audit trail B1 must not delete.
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, cl)
            E.main(["--file", str(f), "claim", "--session-id", "child-1",
                    "--claimed-by", "implementer"])
            code = E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                            "--authority", "human", "--reason", "accepted risk",
                            "--session-id", "parent-1"])
            self.assertEqual(code, 0)
            jp = Path(str(f) + ".journal")
            self.assertTrue(jp.is_file(), "waive must still append a journal line")
            lines = [json.loads(ln) for ln in jp.read_text(encoding="utf-8").splitlines() if ln.strip()]
            waive_entries = [ln for ln in lines if ln.get("verb") == "waive"]
            self.assertEqual(len(waive_entries), 1)
            self.assertEqual(waive_entries[0]["session_id"], "parent-1")
            self.assertEqual(waive_entries[0]["task"], "g1")

    def test_waive_still_in_mutating_verbs(self):
        self.assertIn("waive", E.MUTATING_VERBS)

    def test_other_mutating_verbs_still_session_gated(self):
        # the exemption is narrow: waive alone, not the whole gate.
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        E.claim(cl, "child-1", "implementer", ".", {})
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "start", "parent-1", {})
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "advance", "parent-1", {})
        E.require_session(cl, "waive", "parent-1", {})  # does not raise


def _old_ts(seconds_ago):
    """An ISO-8601 timestamp `seconds_ago` in the past (for stale-lease tests)."""
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat()


class Leasing(unittest.TestCase):
    def test_first_claim_creates_active_lease(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        msg = E.claim(cl, "s1", "commander", ".", {})
        self.assertIn("claimed lease s1", msg)
        sess = cl["engine_session"]
        self.assertEqual(sess["status"], "active")
        self.assertEqual(sess["session_id"], "s1")
        self.assertEqual(sess["claimed_by"], "commander")
        self.assertIsNone(sess["previous_session_id"])
        self.assertIsNone(sess["takeover_reason"])

    def test_same_session_reclaim_is_idempotent_and_refreshes(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10)
        before = cl["engine_session"]["last_heartbeat"]
        msg = E.claim(cl, "s1", "commander", ".", {})  # no refusal
        self.assertIn("resumed lease s1", msg)
        self.assertNotEqual(cl["engine_session"]["last_heartbeat"], before)
        self.assertEqual(cl["engine_session"]["status"], "active")

    def test_different_active_session_claim_refused(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        with self.assertRaises(E.EngineError):
            E.claim(cl, "s2", "commander", ".", {})
        # original lease untouched
        self.assertEqual(cl["engine_session"]["session_id"], "s1")

    def test_mutating_verb_refused_with_missing_or_wrong_session(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        # missing session
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "start", None, {})
        # wrong session
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "start", "s2", {})

    def test_active_non_stale_refusal_teaches_the_qualified_remedy(self):
        # A6 (deficiency cleanup batch A+B): the refusal for a DIFFERENT,
        # still-active (non-stale) session must not hand out either filed
        # defect's remedy as a bare, unconditional command -- #632 (passing
        # the holder's --session-id with no qualifier) or #369 (reaching
        # straight for claim --force --reason). Both remedies still appear,
        # each now WITH the condition that makes it correct, plus the
        # honest third option: leave it alone.
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        with self.assertRaises(E.EngineError) as ctx:
            E.require_session(cl, "start", "s2", {})
        msg = str(ctx.exception)
        self.assertIn("if that is YOU resuming", msg)
        self.assertIn("never a name you have not actually run under", msg)
        self.assertIn("if it is still working, leave this plan alone", msg)
        self.assertIn("if you know it is gone", msg)
        self.assertIn("--session-id 's1'", msg)

    def test_mutating_verb_allowed_with_matching_session(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        E.require_session(cl, "start", "s1", {})  # does not raise
        self.assertEqual(E.start(cl, "g1"), "g1 -> in-progress")

    def test_backward_compat_no_lease_allows_mutation_without_session(self):
        # no engine_session -> legacy flow works with no --session-id
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        self.assertNotIn("engine_session", cl)
        E.require_session(cl, "start", None, {})  # no-op
        self.assertEqual(E.start(cl, "g1"), "g1 -> in-progress")
        E.require_session(cl, "advance", None, {})
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")

    def test_stale_lease_self_heals_for_owner(self):
        # The owner is never blocked by its own staleness: the gate passes, and
        # the liveness stamp clears the staleness without a re-claim — and writes
        # no takeover record (resuming your own work is not a takeover).
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10_000)
        cfg = {"lease_stale_seconds": 1800}
        self.assertTrue(E._is_stale(cl["engine_session"], cfg))
        E.require_session(cl, "start", "s1", cfg)   # owner: does not raise
        E._refresh_owner_heartbeat(cl, "s1")        # liveness stamp clears it
        self.assertFalse(E._is_stale(cl["engine_session"], cfg))
        self.assertIsNone(cl["engine_session"]["previous_session_id"])
        self.assertIsNone(cl["engine_session"]["takeover_reason"])

    def test_nonowner_against_stale_lease_still_refused(self):
        # The unchanged half: a DIFFERENT session must still claim a stale lease.
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10_000)
        cfg = {"lease_stale_seconds": 1800}
        self.assertTrue(E._is_stale(cl["engine_session"], cfg))
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "start", "s2", cfg)

    def test_mutating_verb_stamps_owner_heartbeat(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(60)  # old but not stale
        before = cl["engine_session"]["last_heartbeat"]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "start", "g1", "--session-id", "s1"]), 0)
            reloaded = E.load(f)
        self.assertEqual(reloaded["tasks"]["g1"]["status"], "in-progress")
        self.assertNotEqual(reloaded["engine_session"]["last_heartbeat"], before)

    def test_read_only_current_does_not_refresh_owner_heartbeat(self):
        # A read-only `current` must never advance the owner's liveness stamp.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(60)  # old but not stale
        before = cl["engine_session"]["last_heartbeat"]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "current"]), 0)
            reloaded = E.load(f)
        self.assertEqual(reloaded["engine_session"]["last_heartbeat"], before)

    def test_no_refresh_on_refused_mutating_call_by_owner(self):
        # The crux: a mutating verb by the OWNER that passes require_session but is
        # then REFUSED by the verb itself (here `start g2` out of order) must NOT
        # refresh the lease — even though main() persists the checklist on the
        # EngineError path. Otherwise a session that only issues failing verbs
        # would keep its lease alive forever and never go stale.
        cl = gated(g1=gate("g1"), g2=gate("g2"))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(60)  # old but not stale
        before = cl["engine_session"]["last_heartbeat"]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            # start g2 refuses (g1 not complete): require_session passes (owner s1),
            # the verb raises -> REFUSED (exit 1), main still saves on error path.
            self.assertEqual(
                E.main(["--file", str(f), "start", "g2", "--session-id", "s1"]), 1)
            reloaded = E.load(f)
        self.assertEqual(reloaded["tasks"]["g2"]["status"], "pending")
        self.assertEqual(reloaded["engine_session"]["last_heartbeat"], before)

    def test_refresh_owner_heartbeat_noop_for_nonowner_and_no_lease(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E._refresh_owner_heartbeat(cl, "s1")            # no lease: no-op, no crash
        self.assertNotIn("engine_session", cl)
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10)
        before = cl["engine_session"]["last_heartbeat"]
        E._refresh_owner_heartbeat(cl, "s2")            # non-owner: untouched
        self.assertEqual(cl["engine_session"]["last_heartbeat"], before)

    def test_stale_lease_reclaimed_by_force(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10_000)
        cfg = {"lease_stale_seconds": 1800}
        msg = E.claim(cl, "s2", "commander", ".", cfg, force=True, reason="resumed crashed parent")
        self.assertEqual(cl["engine_session"]["session_id"], "s2")
        self.assertEqual(cl["engine_session"]["previous_session_id"], "s1")

    def test_force_takeover_records_audit_trail(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        with self.assertRaises(E.EngineError):
            E.claim(cl, "s2", "commander", ".", {})  # active, must force
        msg = E.claim(cl, "s2", "commander", ".", {}, force=True, reason="lost parent resurrected")
        self.assertIn("FORCED", msg)
        sess = cl["engine_session"]
        self.assertEqual(sess["session_id"], "s2")
        self.assertEqual(sess["previous_session_id"], "s1")
        self.assertEqual(sess["takeover_reason"], "lost parent resurrected")

    def test_force_takeover_requires_reason(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        with self.assertRaises(E.EngineError):
            E.claim(cl, "s2", "commander", ".", {}, force=True, reason="  ")

    def test_heartbeat_only_by_owner(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10)
        before = cl["engine_session"]["last_heartbeat"]
        E.heartbeat(cl, "s1")
        self.assertNotEqual(cl["engine_session"]["last_heartbeat"], before)
        with self.assertRaises(E.EngineError):
            E.heartbeat(cl, "s2")

    def test_release_closes_lease_and_allows_new_claim(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        E.release(cl, "s1")
        self.assertEqual(cl["engine_session"]["status"], "released")
        # released lease no longer gates mutation
        E.require_session(cl, "start", None, {})  # no raise
        # and a fresh claim succeeds
        msg = E.claim(cl, "s2", "commander", ".", {})
        self.assertIn("claimed lease s2", msg)
        self.assertEqual(cl["engine_session"]["status"], "active")

    def test_release_only_by_owner_unless_forced(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        with self.assertRaises(E.EngineError):
            E.release(cl, "s2")
        # non-owner force needs a reason
        with self.assertRaises(E.EngineError):
            E.release(cl, "s2", force=True, reason="")
        E.release(cl, "s2", force=True, reason="cleanup after crash")
        self.assertEqual(cl["engine_session"]["status"], "released")

    def test_current_reports_active_lease_without_session(self):
        # A3 (deficiency cleanup batch A+B): `active` is rendered as `HELD`
        # plus an age, never a raw verdict word.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        out = E.current(cl)  # read-only, no session needed
        self.assertIn("LEASE HELD: s1", out)
        self.assertIn("last heartbeat", out)
        self.assertNotIn("LEASE active", out)
        self.assertIn("ACTIVE g1", out)

    def test_cli_claim_then_advance_with_session(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "claim", "--session-id", "s1",
                        "--claimed-by", "commander", "--worktree", "."]), 0)
            # mutating without --session-id is refused once a lease exists
            self.assertEqual(E.main(["--file", str(f), "start", "g1"]), 1)
            # with the matching session it succeeds
            self.assertEqual(
                E.main(["--file", str(f), "start", "g1", "--session-id", "s1"]), 0)
            self.assertEqual(
                E.main(["--file", str(f), "advance", "g1", "--session-id", "s1"]), 0)
            reloaded = E.load(f)
            self.assertEqual(reloaded["tasks"]["g1"]["status"], "complete")
            # heartbeat + release through the CLI
            self.assertEqual(E.main(["--file", str(f), "heartbeat", "--session-id", "s1"]), 0)
            self.assertEqual(E.main(["--file", str(f), "release", "--session-id", "s1"]), 0)
            self.assertEqual(E.load(f)["engine_session"]["status"], "released")

    def test_refusal_before_the_first_ever_claim_is_counted(self):
        # #427: claim()'s own `cl.setdefault("refusals", 0)` (~1030) only arms
        # the counter on a SUCCESSFUL claim. A checklist that has never once
        # been successfully claimed (no `engine_session`, ever) has no armed
        # counter, so main()'s persistence-path increment (only bumps an
        # already-int value, deliberately, to avoid backdating a pre-counter
        # checklist with a guessed number) silently drops a refusal that
        # happens BEFORE that first claim -- e.g. this malformed claim call
        # itself. 0 would be a TRUE reading here (never claimed, ever), not a
        # guess, so it should be armed and counted.
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        self.assertIsNone(cl.get("engine_session"))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(
                f, ["claim", "--session-id", "", "--claimed-by", "implementer"])
            self.assertEqual(code, 1)
            after = E.load(f)
        self.assertEqual(after.get("refusals"), 1)

    def test_refusal_on_a_never_claimed_child_gate_plan_does_not_arm_the_counter(self):
        # #357 g1 review carry-over: a child gate plan is legitimately driven
        # WITHOUT ever calling `claim` at all -- `engine_session` stays None
        # for its whole life by design (production shape, not a checklist
        # mid-way to its first claim). #427's own fix must not conflate the
        # two: arming on ANY refusal while unclaimed would give this shape a
        # `refusals` key it is supposed to never carry (episode_capture's
        # negative control asserts the key's ABSENCE is structural, not "zero
        # refusals happened"). A refused `start` on an unknown gate id needs
        # no lease and no `claim` call to reach -- exactly the #357 shape.
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        self.assertIsNone(cl.get("engine_session"))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "does-not-exist"])
            self.assertEqual(code, 1)
            after = E.load(f)
        self.assertNotIn("refusals", after,
                          "a never-claimed child gate plan must not have its "
                          "refusals key armed by a non-claim refusal")


class ShippedTemplates(unittest.TestCase):
    def test_every_template_is_valid_json_and_checklists_walk(self):
        roots = sorted((ROOT / "skills").glob("*/templates/*.json"))
        self.assertTrue(roots, "no shipped templates found")
        for t in roots:
            with self.subTest(template=str(t.relative_to(ROOT))):
                data = json.loads(t.read_text(encoding="utf-8"))  # also catches stray tags
                if "items" not in data:
                    continue  # config file (e.g. ENGINE_CONFIG), not a checklist
                self.assertTrue(data["items"])
                # Not a literal startswith: the role spines (Admiral,
                # Commander, Explorer) declare `bookend` gates (#634), and
                # since the #634-follow-up fix to state()/render_human() a
                # populated `bookend_gates` list renders its own line ahead
                # of the ACTIVE line -- same PREFIX slot `lease_line`
                # already occupies. The walk claim this test makes ("the
                # checklist actually has an active gate") survives; only the
                # exact string position moved.
                self.assertTrue(
                    any(line.startswith("ACTIVE") for line in E.current(data).splitlines())
                )


def _policy(**overrides):
    """A representative artifact policy (the spine's shape) for evaluator tests."""
    p = {
        "mode": "staged",
        "max_file_bytes": 1_000_000,
        "deny_globs": ["*.parquet", "*.pkl", "*.pickle", "data/generated/**", "records/**"],
        "allow_globs": ["docs/**", "src/**", "tests/**", "skills/**", "scripts/**", ".agent-work/**"],
        "require_human_waiver_for_binary": True,
    }
    p.update(overrides)
    return p


class GitChangePolicyEvaluator(unittest.TestCase):
    """PURE evaluator tests — no git, no working tree."""

    def test_clean_diff_no_violations(self):
        files = [{"path": "docs/a.md", "size": 10, "binary": False},
                 {"path": "src/x.py", "size": 500, "binary": False},
                 {"path": "tests/test_x.py", "size": 80, "binary": False}]
        self.assertEqual(E.evaluate_git_change_policy(files, _policy()), [])

    def test_empty_diff_satisfied(self):
        self.assertEqual(E.evaluate_git_change_policy([], _policy()), [])

    def test_empty_policy_no_constraints(self):
        files = [{"path": "anything", "size": 9_999_999, "binary": True}]
        self.assertEqual(E.evaluate_git_change_policy(files, {}), [])

    def test_oversized_file_violates(self):
        files = [{"path": "blob.txt", "size": 2_000_000, "binary": False}]
        v = E.evaluate_git_change_policy(files, _policy())
        self.assertEqual(len(v), 1)
        self.assertIn("exceeds max_file_bytes", v[0])

    def test_oversized_file_in_allow_glob_exempt(self):
        files = [{"path": "src/big.py", "size": 2_000_000, "binary": False}]
        self.assertEqual(E.evaluate_git_change_policy(files, _policy()), [])

    def test_denied_records_dir_violates(self):
        files = [{"path": "records/foo.json", "size": 1, "binary": False}]
        v = E.evaluate_git_change_policy(files, _policy())
        self.assertIn("matches deny glob", v[0])

    def test_denied_nested_records_dir_violates(self):
        # recursive ** — the nested record-dump case
        files = [{"path": "records/a/b/foo.json", "size": 1, "binary": False}]
        self.assertTrue(E.evaluate_git_change_policy(files, _policy()))

    def test_denied_parquet_anywhere_violates(self):
        files = [{"path": "sub/dir/model.parquet", "size": 1, "binary": False}]
        v = E.evaluate_git_change_policy(files, _policy())
        self.assertIn("*.parquet", v[0])

    def test_binary_addition_requires_waiver(self):
        files = [{"path": "blob.dat", "size": 1, "binary": True}]
        v = E.evaluate_git_change_policy(files, _policy())
        self.assertIn("binary/blob addition", v[0])

    def test_binary_in_allow_glob_exempt(self):
        files = [{"path": "skills/img.png", "size": 1, "binary": True}]
        self.assertEqual(E.evaluate_git_change_policy(files, _policy()), [])

    def test_binary_allowed_when_policy_off(self):
        files = [{"path": "blob.dat", "size": 1, "binary": True}]
        self.assertEqual(
            E.evaluate_git_change_policy(files, _policy(require_human_waiver_for_binary=False)), [])

    def test_deny_beats_allow(self):
        # an explicit deny always denies, even inside an allow_glob dir
        files = [{"path": "src/model.parquet", "size": 1, "binary": False}]
        v = E.evaluate_git_change_policy(files, _policy())
        self.assertEqual(len(v), 1)
        self.assertIn("matches deny glob", v[0])

    def test_canonical_shared_file_denied_despite_agent_work_allow(self):
        # lesson:shared-files-not-on-mission-branch — committing canonical
        # shared state (LESSONS.md / AGENT_FEEDBACK.md / CONSTELLATION_FEEDBACK*)
        # on a mission branch clobbers sibling runs. `.agent-work/**` is an
        # allow_glob, so only an explicit deny on the exact file catches it.
        policy = _policy(
            deny_globs=[".agent-work/LESSONS.md"],
            allow_globs=[".agent-work/**"],
        )
        files = [{"path": ".agent-work/LESSONS.md", "size": 10, "binary": False}]
        v = E.evaluate_git_change_policy(files, policy)
        self.assertEqual(len(v), 1)
        self.assertIn("matches deny glob", v[0])
        self.assertIn(".agent-work/LESSONS.md", v[0])
        # an ordinary scratch path under the same allow_glob still passes
        scratch = [{"path": ".agent-work/issue-472/notes.md", "size": 10, "binary": False}]
        self.assertEqual(E.evaluate_git_change_policy(scratch, policy), [])


class GitChangePolicyCheck(unittest.TestCase):
    """The git-change-policy CHECK kind wired through advance/waive, with the
    collector stubbed so tests need no git."""

    def setUp(self):
        self._orig = E._collect_changed_files
        E._collect_changed_files = lambda policy, base_dir, _self=self: self._files
        self._files = []

    def tearDown(self):
        E._collect_changed_files = self._orig

    def _gate(self, status="in-progress", waivable=True):
        t = gate("g1", status)
        cond = {"id": "c4", "statement": "no suspicious artifacts",
                "check": dict(_policy(), kind="git-change-policy"), "satisfied": False}
        if waivable:
            cond["override_policy"] = {"allowed": True, "authority": "human", "reason_required": True}
        t["postconditions"] = [cond]
        return gated(g1=t)

    def test_clean_diff_advance_succeeds(self):
        self._files = [{"path": "docs/a.md", "size": 10, "binary": False}]
        cl = self._gate()
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["type"], "artifact-policy")
        self.assertEqual(ev["payload"]["violations"], [])

    def test_violation_blocks_advance_and_records_evidence(self):
        self._files = [{"path": "records/dump.json", "size": 1, "binary": False}]
        cl = self._gate(waivable=False)
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["type"], "artifact-policy")
        self.assertTrue(ev["payload"]["violations"])
        self.assertIn("records/dump.json", ev["payload"]["violations"][0])

    def test_oversized_blocks_advance(self):
        self._files = [{"path": "big.txt", "size": 5_000_000, "binary": False}]
        cl = self._gate(waivable=False)
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")

    def test_binary_blocks_advance(self):
        self._files = [{"path": "blob.dat", "size": 1, "binary": True}]
        cl = self._gate(waivable=False)
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")

    def test_human_waiver_satisfies_and_records_violation(self):
        self._files = [{"path": "data/generated/x.parquet", "size": 1, "binary": False}]
        cl = self._gate(waivable=True)
        # default: blocked
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        # the violation is on the record before the human waives it
        viol_ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(viol_ev["type"], "artifact-policy")
        self.assertTrue(viol_ev["payload"]["violations"])
        # human waives via the #7 override path
        E.waive(cl, "g1", "c4", "postconditions", "human", "intentional sample fixture")
        msg = E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        self.assertIn("WAIVED", msg)
        # waiver evidence records authority + reason; violation evidence still present
        types = [e["type"] for e in cl["tasks"]["g1"]["evidence"]]
        self.assertIn("waiver", types)
        self.assertIn("artifact-policy", types)
        waiver = next(e for e in cl["tasks"]["g1"]["evidence"] if e["type"] == "waiver")
        self.assertEqual(waiver["payload"]["authority"], "human")
        self.assertEqual(waiver["payload"]["reason"], "intentional sample fixture")

    def test_waived_policy_not_reevaluated_at_advance(self):
        # a waived policy condition must NOT be re-collected/re-checked at advance
        self._files = [{"path": "records/dump.json", "size": 1, "binary": False}]
        cl = self._gate(waivable=True)
        E.waive(cl, "g1", "c4", "postconditions", "human", "accepted")
        # if the check re-ran, it would un-waive and refuse; it must not
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete (WAIVED postconditions ['c4'])")


class RepoRevision(unittest.TestCase):
    """`repo_revision()` -- Tommy's doctrine-version stamp (#300 g5): HEAD commit
    plus a dirty marker, both via the existing `_git()` subprocess helper.
    Oracle-compared against real `git` output, the same pattern the manifest's
    `rev()` blob-OID tests use against `git hash-object`."""

    def _git(self, *args, cwd=None):
        import subprocess
        return subprocess.run(
            ["git", *args], cwd=str(cwd) if cwd else str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )

    def test_repo_revision_commit_matches_git_rev_parse_head_oracle(self):
        oracle = self._git("rev-parse", "HEAD")
        self.assertEqual(oracle.returncode, 0, oracle.stderr)
        result = E.repo_revision(ROOT)
        self.assertEqual(result["commit"], oracle.stdout.strip())

    def test_repo_revision_dirty_matches_git_status_porcelain_non_emptiness_oracle(self):
        oracle = self._git("status", "--porcelain")
        self.assertEqual(oracle.returncode, 0, oracle.stderr)
        result = E.repo_revision(ROOT)
        self.assertEqual(result["dirty"], bool(oracle.stdout.strip()))

    def test_repo_revision_shape_is_exactly_commit_and_dirty(self):
        result = E.repo_revision(ROOT)
        self.assertEqual(sorted(result), ["commit", "dirty"])

    def test_repo_revision_a_non_git_directory_yields_none_none_without_raising(self):
        with tempfile.TemporaryDirectory() as d:
            result = E.repo_revision(Path(d))
        self.assertEqual(result, {"commit": None, "dirty": None})

    def test_repo_revision_base_dir_none_falls_back_to_process_cwd(self):
        # `_git(args, None)` runs with no `cwd=` override, i.e. the caller's own
        # cwd -- this test's cwd is inside the repo (pytest's invocation root),
        # so it must resolve exactly like passing ROOT explicitly does.
        self.assertEqual(E.repo_revision(None), E.repo_revision(ROOT))

    def test_repo_revision_a_real_dirty_working_tree_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self._git("init", "-q", cwd=d)
            self._git("config", "user.email", "t@t", cwd=d)
            self._git("config", "user.name", "t", cwd=d)
            (d / "a.txt").write_text("one\n", encoding="utf-8")
            self._git("add", "a.txt", cwd=d)
            self._git("commit", "-q", "-m", "init", cwd=d)
            clean = E.repo_revision(d)
            self.assertEqual(clean, {"commit": clean["commit"], "dirty": False})
            (d / "a.txt").write_text("two\n", encoding="utf-8")
            dirty = E.repo_revision(d)
            self.assertEqual(dirty["commit"], clean["commit"])
            self.assertTrue(dirty["dirty"])


class GitChangePolicyCollectorIntegration(unittest.TestCase):
    """Optional end-to-end: a real temp git repo exercising _collect_changed_files.
    Skipped if git is unavailable."""

    def setUp(self):
        import shutil
        if shutil.which("git") is None:
            self.skipTest("git not available")

    def _git(self, d, *args):
        import subprocess
        return subprocess.run(["git", *args], cwd=str(d), capture_output=True, text=True)

    def test_staged_collector_reports_path_size_binary(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self._git(d, "init", "-q")
            self._git(d, "config", "user.email", "t@t")
            self._git(d, "config", "user.name", "t")
            (d / "small.txt").write_text("hi", encoding="utf-8")
            (d / "blob.bin").write_bytes(b"\x00\x01\x02\x00binary\x00data")
            self._git(d, "add", "small.txt", "blob.bin")
            files = E._collect_changed_files({"mode": "staged"}, d)
            by_path = {f["path"]: f for f in files}
            self.assertIn("small.txt", by_path)
            self.assertIn("blob.bin", by_path)
            self.assertEqual(by_path["small.txt"]["size"], 2)
            self.assertFalse(by_path["small.txt"]["binary"])
            self.assertTrue(by_path["blob.bin"]["binary"])

    def test_evaluator_over_collected_files_flags_deny_glob(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self._git(d, "init", "-q")
            self._git(d, "config", "user.email", "t@t")
            self._git(d, "config", "user.name", "t")
            (d / "records").mkdir()
            (d / "records" / "dump.json").write_text("{}", encoding="utf-8")
            self._git(d, "add", "records/dump.json")
            files = E._collect_changed_files({"mode": "staged"}, d)
            violations = E.evaluate_git_change_policy(files, _policy())
            self.assertTrue(any("records/dump.json" in v for v in violations))


if __name__ == "__main__":
    unittest.main()


class Cp1252StdioTests(unittest.TestCase):
    def test_current_survives_cp1252_stdio_with_unicode_task_text(self):
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as d:
            cl = gated(g1=gate("g1"))
            cl["tasks"]["g1"]["imperative"] = "calibrate → ≈ 0.5 per §7.6 — unicode imperative"
            path = Path(d) / "plan.json"
            path.write_text(json.dumps(cl), encoding="utf-8")

            env = dict(os.environ)
            env.pop("PYTHONUTF8", None)
            env["PYTHONIOENCODING"] = "cp1252"  # reproduce the captured-console regime
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--file", str(path), "current"],
                capture_output=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))
            decoded = proc.stdout.decode("utf-8")
            self.assertIn("unicode imperative", decoded)
            self.assertIn("→ ≈ 0.5 per §7.6", decoded)


class PosixShellRoutingTests(unittest.TestCase):
    def test_bash_candidates_from_mingw64_git(self):
        # which("git") on a stock box resolves to the mingw64 copy; Git root is the
        # great-grandparent, so a parent/grandparent-only walk would miss bash.
        cands = E._bash_candidates_from_git(r"C:\Program Files\Git\mingw64\bin\git.exe")
        self.assertIn(r"C:\Program Files\Git\bin\bash.exe", cands)
        self.assertIn(r"C:\Program Files\Git\usr\bin\bash.exe", cands)

    def test_bash_candidates_from_cmd_git(self):
        cands = E._bash_candidates_from_git(r"C:\Program Files\Git\cmd\git.exe")
        self.assertIn(r"C:\Program Files\Git\bin\bash.exe", cands)
        self.assertIn(r"C:\Program Files\Git\usr\bin\bash.exe", cands)

    def test_find_posix_shell_prefers_which_bash(self):
        with mock.patch.object(E.os, "name", "nt"), \
             mock.patch.object(E.shutil, "which",
                               side_effect=lambda n: r"X:\bash.exe" if n == "bash" else None):
            self.assertEqual(E._find_posix_shell(), r"X:\bash.exe")

    def test_find_posix_shell_guards_none_git(self):
        # which() returns None for everything: git is None, so the if-guard must
        # prevent _bash_candidates_from_git(None) from ever being called.
        with mock.patch.object(E.os, "name", "nt"), \
             mock.patch.object(E.shutil, "which", return_value=None), \
             mock.patch.object(E, "_bash_candidates_from_git",
                               side_effect=AssertionError("called with None git")):
            self.assertIsNone(E._find_posix_shell())

    def test_find_posix_shell_falls_back_to_sh_on_windows(self):
        # bash and git both missing, but a POSIX sh is on PATH: the final
        # `return shutil.which("sh")` branch is taken even on Windows.
        with mock.patch.object(E.os, "name", "nt"), \
             mock.patch.object(E.shutil, "which",
                               side_effect=lambda n: r"X:\sh.exe" if n == "sh" else None):
            self.assertEqual(E._find_posix_shell(), r"X:\sh.exe")

    def test_run_check_command_no_posix_shell_fails_visibly(self):
        # With no POSIX shell, the engine refuses to route POSIX-form text through
        # cmd.exe: it returns a synthetic FAILED result (returncode 127) with the
        # marker "no-posix-shell" and a stderr naming the missing shell.
        with mock.patch.object(E, "_find_posix_shell", return_value=None):
            proc, marker = E._run_check_command(PASS_COMMAND)
        self.assertEqual(marker, "no-posix-shell")
        self.assertEqual(proc.returncode, 127)
        self.assertIn("POSIX shell", proc.stderr)

    def test_command_evidence_stamps_no_posix_shell_marker(self):
        with mock.patch.object(E, "_find_posix_shell", return_value=None):
            cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
            # the check now FAILS visibly, so advance is refused (postcondition unmet)
            with self.assertRaises(E.EngineError):
                E.advance(cl, "g1")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["payload"]["shell"], "no-posix-shell")
        self.assertEqual(ev["payload"]["exit"], 127)

    def test_no_posix_shell_never_invokes_subprocess_run(self):
        # Anti-regression: the no-shell branch must NOT run POSIX text through
        # cmd.exe. Patch subprocess.run to explode if called, and confirm the
        # failed no-posix-shell result still comes back without invoking it.
        with mock.patch.object(E, "_find_posix_shell", return_value=None), \
             mock.patch.object(E.subprocess, "run",
                               side_effect=AssertionError("subprocess.run must not run in the no-shell branch")):
            proc, marker = E._run_check_command(PASS_COMMAND)
        self.assertEqual(marker, "no-posix-shell")
        self.assertEqual(proc.returncode, 127)

    @unittest.skipUnless(E._find_posix_shell(), "no POSIX shell found")
    def test_posix_routing_runs_pipe_and_marks_evidence(self):
        # The shell:"posix" assertion is the real guard — it proves the command was
        # routed through bash. (The command's pass/fail alone does not discriminate:
        # where Git's usr\bin is on PATH, grep/pipes also pass under cmd.exe.)
        cl = gated(g1=gate("g1", "in-progress", command="echo isolated | grep -q isolated"))
        E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["payload"]["shell"], "posix")


class ResumeVerb(unittest.TestCase):
    def test_block_records_prior_status(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "waiting on human", "human", "resolve it")
        self.assertEqual(cl["tasks"]["g1"]["status_detail"]["prior_status"], "in-progress")
        # the bubbled blockers entry stays byte-identical to today: no prior_status leak
        self.assertNotIn("prior_status", cl["blockers"][0])
        self.assertEqual(
            set(cl["blockers"][0].keys()),
            {"item", "blocker", "authority_needed", "next_action"},
        )

    def test_resume_after_resolved_block_restores_and_advances(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "b", "human", "n")
        msg = E.resume(cl, "g1", "blocker resolved")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        self.assertIn("resumed", msg)
        self.assertEqual(cl["tasks"]["g1"]["status_detail"]["resume_reason"], "blocker resolved")
        self.assertNotIn("prior_status", cl["tasks"]["g1"]["status_detail"])
        # a resumed in-progress gate advances normally (why_exempt fixture)
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")

    def test_resume_restores_pending_prior(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        E.block(cl, "g1", "b", "human", "n")
        E.resume(cl, "g1", "fixed")
        self.assertEqual(cl["tasks"]["g1"]["status"], "pending")

    def test_resume_refuses_non_blocked(self):
        for st in ("pending", "in-progress", "complete"):
            cl = gated(g1=gate("g1", st, command=PASS_COMMAND))
            with self.assertRaises(E.EngineError):
                E.resume(cl, "g1", "r")

    def test_resume_requires_reason(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "b", "human", "n")
        with self.assertRaises(E.EngineError):
            E.resume(cl, "g1", "   ")

    def test_resume_refuses_cap_escalated_block(self):
        # Drive a reopen past the rework cap so the gate ends up blocked WITHOUT a
        # recorded prior_status (cap escalation). resume must refuse it (cap integrity).
        cl = gated(cap=1, g1=gate("g1", "complete", command=PASS_COMMAND))
        E.reopen(cl, "g1", "first")                 # rework 1/1 -> in-progress
        cl["tasks"]["g1"]["status"] = "complete"    # simulate re-completion
        msg = E.reopen(cl, "g1", "second")          # 2 > 1 -> ESCALATED (blocked, no prior)
        self.assertIn("ESCALATED", msg)
        self.assertEqual(cl["tasks"]["g1"]["status"], "blocked")
        self.assertNotIn("prior_status", cl["tasks"]["g1"]["status_detail"])
        with self.assertRaises(E.EngineError):
            E.resume(cl, "g1", "resolved")

    def test_resume_clears_blocker_from_bubble_list(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "b", "human", "n")
        self.assertTrue(any(b["item"] == "g1" for b in cl["blockers"]))
        E.resume(cl, "g1", "fixed")
        self.assertFalse(any(b.get("item") == "g1" for b in cl["blockers"]))

    def test_resume_in_mutating_verbs(self):
        self.assertIn("resume", E.MUTATING_VERBS)

    def test_resume_cli_round_trip(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "block", "g1", "--blocker", "b", "--next", "n"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "blocked")
            self.assertEqual(
                E.main(["--file", str(f), "resume", "g1", "--reason", "resolved"]), 0)
            reloaded = E.load(f)
        self.assertEqual(reloaded["tasks"]["g1"]["status"], "in-progress")

    def test_resume_refreshes_owner_heartbeat(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        E.block(cl, "g1", "b", "human", "n")            # in-progress -> blocked
        cl["engine_session"]["last_heartbeat"] = _old_ts(60)  # old but not stale
        before = cl["engine_session"]["last_heartbeat"]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "resume", "g1", "--reason", "r",
                        "--session-id", "s1"]), 0)
            reloaded = E.load(f)
        self.assertEqual(reloaded["tasks"]["g1"]["status"], "in-progress")
        self.assertNotEqual(reloaded["engine_session"]["last_heartbeat"], before)


def _add_op(nid, after=None, posts=None, **extra):
    """An `amend` add op with the required minimum fields, plus overrides."""
    op = {
        "op": "add", "id": nid,
        "title": f"title {nid}", "imperative": f"do {nid}",
        "postconditions": posts if posts is not None else [
            {"id": "c1", "statement": "done", "check": None, "satisfied": False}
        ],
    }
    if after is not None:
        op["after"] = after
    op.update(extra)
    return op


class AmendVerb(unittest.TestCase):
    def test_amend_refused_on_survey(self):
        cl = survey(v1=survey_item("v1"))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g9")]}, "r", "human")

    def test_amend_refuses_empty_authority(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g9")]}, "r", "")

    def test_amend_refuses_empty_reason(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g9")]}, "  ", "human")

    def test_amend_refuses_empty_or_missing_ops(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": []}, "r", "human")
        with self.assertRaises(E.EngineError):
            E.amend(cl, {}, "r", "human")

    def test_amend_adds_pending_gate_at_position_and_logs(self):
        # g1 complete (frozen), g2 pending. Insert g1a after g1 must land AFTER g1
        # (index 1) which is >= floor (1). New gate is pending with full shape.
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "pending", command=PASS_COMMAND))
        msg = E.amend(cl, {"ops": [_add_op("g1a", after="g1")]}, "insert step", "human")
        self.assertIn("g1a", msg)
        self.assertEqual(cl["items"], ["g1", "g1a", "g2"])
        t = cl["tasks"]["g1a"]
        self.assertEqual(t["status"], "pending")
        self.assertEqual(t["rework_count"], 0)
        self.assertEqual(t["evidence"], [])
        self.assertIn("preconditions", t)
        self.assertIn("postconditions", t)
        # audit trail
        self.assertEqual(len(cl["amendments"]), 1)
        rec = cl["amendments"][0]
        self.assertEqual(rec["reason"], "insert step")
        self.assertEqual(rec["authority"], "human")
        self.assertTrue(rec["ops"])

    def test_amend_add_appends_at_end_when_no_after(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        E.amend(cl, {"ops": [_add_op("g2")]}, "add tail", "human")
        self.assertEqual(cl["items"], ["g1", "g2"])

    def test_amend_add_later_op_can_reference_earlier_added_id(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        E.amend(cl, {"ops": [_add_op("g2"), _add_op("g3", after="g2")]}, "chain", "human")
        self.assertEqual(cl["items"], ["g1", "g2", "g3"])

    def test_amend_add_refuses_before_frozen_gate(self):
        # g1 complete (frozen at index 0, floor=1), g2 pending. Adding with after
        # omitted appends at end (fine); but inserting before the frozen gate is
        # impossible via `after` — simulate by requiring after references a later
        # frozen boundary. Here we make g2 complete too and try to insert after g1
        # (index 1) which is < floor (2) -> refuse.
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "complete", command=PASS_COMMAND),
                   g3=gate("g3", "pending", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, {"ops": [_add_op("g1a", after="g1")]}, "bad insert", "human")
        self.assertIn("frozen", str(ctx.exception))

    def test_amend_add_refuses_duplicate_id(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g1")]}, "dup", "human")

    def test_amend_add_refuses_bad_id_and_missing_postconditions(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("Bad_ID")]}, "r", "human")
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g2", posts=[])]}, "r", "human")

    def test_amend_drops_pending_gate(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "pending", command=PASS_COMMAND))
        E.amend(cl, {"ops": [{"op": "drop", "id": "g2"}]}, "cut it", "human")
        self.assertEqual(cl["items"], ["g1"])
        self.assertNotIn("g2", cl["tasks"])

    def test_amend_drop_refuses_non_pending(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, {"ops": [{"op": "drop", "id": "g1"}]}, "r", "human")
        self.assertIn("pending", str(ctx.exception))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [{"op": "drop", "id": "g2"}]}, "r", "human")

    def test_amend_rescopes_pending_gate(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        newposts = [{"id": "c1", "statement": "new", "check": None, "satisfied": False}]
        E.amend(cl, {"ops": [{"op": "rescope", "id": "g1",
                              "title": "retitled", "imperative": "new imp",
                              "postconditions": newposts}]}, "reshape", "human")
        t = cl["tasks"]["g1"]
        self.assertEqual(t["title"], "retitled")
        self.assertEqual(t["imperative"], "new imp")
        self.assertEqual(t["postconditions"], newposts)
        self.assertEqual(t["status"], "pending")

    def test_amend_rescope_refuses_non_pending(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [{"op": "rescope", "id": "g1", "title": "x"}]}, "r", "human")

    def test_amend_rescope_refuses_no_fields_and_empty_postconditions(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [{"op": "rescope", "id": "g1"}]}, "r", "human")
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [{"op": "rescope", "id": "g1", "postconditions": []}]}, "r", "human")

    def test_amend_all_or_nothing_leaves_checklist_identical(self):
        # 1st op valid (add g2), 2nd op invalid (drop a complete gate). The whole
        # delta must abort: items/tasks byte-identical, no amendments recorded.
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "pending", command=PASS_COMMAND))
        before = copy.deepcopy(cl)
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g3"),
                                 {"op": "drop", "id": "g1"}]}, "r", "human")
        self.assertEqual(cl["items"], before["items"])
        self.assertEqual(cl["tasks"], before["tasks"])
        self.assertNotIn("amendments", cl)

    def test_amend_in_mutating_verbs(self):
        self.assertIn("amend", E.MUTATING_VERBS)

    def test_amend_cli_round_trip(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "delta.json"
            delta.write_text(json.dumps({"ops": [_add_op("g2", after="g1")]}), encoding="utf-8")
            rc = E.main(["--file", str(f), "amend", "--delta", str(delta),
                         "--reason", "cli add", "--authority", "human"])
            self.assertEqual(rc, 0)
            reloaded = E.load(f)
            self.assertEqual(reloaded["items"], ["g1", "g2"])
            self.assertEqual(reloaded["amendments"][0]["authority"], "human")

    def test_amend_cli_bad_delta_file_refuses(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            rc = E.main(["--file", str(f), "amend", "--delta", str(Path(d) / "nope.json"),
                         "--reason", "r", "--authority", "human"])
            self.assertEqual(rc, 1)


class AmendRetextCheck(unittest.TestCase):
    def _retext(self, tid="g1", cond="c1", **extra):
        op = {"op": "retext-check", "id": tid, "cond": cond}
        op.update(extra)
        return {"ops": [op]}

    def test_amend_retext_check_on_in_progress_fixes_command_without_satisfying(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        cond = cl["tasks"]["g1"]["postconditions"][0]
        cond["satisfied"] = True            # a stale (wrong-check) pass
        cond["satisfied_by"] = "old-run"
        E.amend(cl, self._retext(command=PASS_COMMAND), "path relocated", "human")
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertEqual(cond["check"]["command"], PASS_COMMAND)
        self.assertFalse(cond["satisfied"])
        self.assertNotIn("satisfied_by", cond)
        # correcting text never satisfies — gate stays in-progress
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        self.assertEqual(len(cl["amendments"]), 1)

    def test_amend_retext_check_corrected_command_lets_advance(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        E.amend(cl, self._retext(command=PASS_COMMAND), "fix check", "human")
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")

    def test_amend_retext_check_drops_waived_and_attested(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        cond = cl["tasks"]["g1"]["postconditions"][0]
        cond["satisfied"] = True
        cond["satisfied_by"] = "y"
        cond["waived"] = {"authority": "human", "reason": "x"}
        cond["attested"] = {"note": "z"}
        E.amend(cl, self._retext(command=PASS_COMMAND), "fix", "human")
        cond = cl["tasks"]["g1"]["postconditions"][0]
        self.assertFalse(cond["satisfied"])
        self.assertNotIn("waived", cond)
        self.assertNotIn("attested", cond)
        self.assertNotIn("satisfied_by", cond)

    def test_amend_retext_check_refuses_complete_gate(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, self._retext(command=PASS_COMMAND), "r", "human")
        self.assertIn("reopen", str(ctx.exception))

    def test_amend_retext_check_refuses_null_check(self):
        cl = gated(g1=gate("g1", "in-progress"))
        cl["tasks"]["g1"]["postconditions"] = [
            {"id": "c1", "statement": "s", "check": None, "satisfied": False}]
        with self.assertRaises(E.EngineError):
            E.amend(cl, self._retext(command=PASS_COMMAND), "r", "human")

    def test_amend_retext_check_refuses_command_on_non_command(self):
        cl = gated(g1=_artifact_gate("g1", "in-progress"))
        with self.assertRaises(E.EngineError):
            E.amend(cl, self._retext(command=PASS_COMMAND), "r", "human")

    def test_amend_retext_check_refuses_kind_change(self):
        # check-object replacement with a different kind -> refused
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, self._retext(
                check={"kind": "artifact", "evidence_type": "review-result"}), "r", "human")
        # a check:null swap is not a check-text correction -> refused
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, self._retext(check=None), "r", "human")
        # an object with a null kind -> refused
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, self._retext(check={"kind": None}), "r", "human")

    def test_amend_retext_check_requires_command_or_check(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with self.assertRaises(E.EngineError):
            E.amend(cl, self._retext(), "r", "human")

    def test_amend_retext_check_all_or_nothing(self):
        # 1st op valid (retext g1), 2nd op invalid (unknown cond on g2). The whole
        # delta aborts: g1's check text is left UNCHANGED and no amendment recorded.
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND),
                   g2=gate("g2", "pending", command=PASS_COMMAND))
        before = copy.deepcopy(cl)
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [
                {"op": "retext-check", "id": "g1", "cond": "c1", "command": PASS_COMMAND},
                {"op": "retext-check", "id": "g2", "cond": "nope", "command": PASS_COMMAND},
            ]}, "r", "human")
        self.assertEqual(cl["tasks"]["g1"]["postconditions"][0]["check"]["command"], FAIL_COMMAND)
        self.assertEqual(cl["tasks"], before["tasks"])
        self.assertNotIn("amendments", cl)

    def test_amend_retext_check_cli_round_trip(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "delta.json"
            delta.write_text(json.dumps({"ops": [
                {"op": "retext-check", "id": "g1", "cond": "c1", "command": PASS_COMMAND}]}),
                encoding="utf-8")
            rc = E.main(["--file", str(f), "amend", "--delta", str(delta),
                         "--reason", "fix path", "--authority", "human"])
            self.assertEqual(rc, 0)
            reloaded = E.load(f)
        cond = reloaded["tasks"]["g1"]["postconditions"][0]
        self.assertEqual(cond["check"]["command"], PASS_COMMAND)
        self.assertFalse(cond["satisfied"])


class AmendBookendGuard(unittest.TestCase):
    """#634: a declared-bookend gate (task.get('bookend')) is frozen against
    every amend op that would drop it, rescope it, retext its check, or land a
    new gate after it — while an undeclared plan (no 'bookend' key anywhere)
    behaves exactly as at 9b38b9d9. See probe-closing-bookend.md for the
    measured gap this closes."""

    def test_amend_add_refuses_after_last_bookend(self):
        # g3 is the declared closing bookend. Appending past it (no 'after',
        # or 'after' the bookend itself) must be refused either way.
        g3 = gate("g3", "pending")
        g3["bookend"] = True
        cl = gated(g1=gate("g1", "pending"), g2=gate("g2", "pending"), g3=g3)
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, {"ops": [_add_op("g4")]}, "r", "human")
        self.assertIn("bookend", str(ctx.exception))
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g4", after="g3")]}, "r", "human")

    def test_amend_add_into_middle_still_succeeds(self):
        g3 = gate("g3", "pending")
        g3["bookend"] = True
        cl = gated(g1=gate("g1", "pending"), g2=gate("g2", "pending"), g3=g3)
        E.amend(cl, {"ops": [_add_op("g1a", after="g1")]}, "r", "human")
        self.assertEqual(cl["items"], ["g1", "g1a", "g2", "g3"])

    def test_amend_drop_refuses_bookend_gate_pending(self):
        # the exact hole probe-closing-bookend.md measured: a PENDING closing
        # gate is otherwise perfectly droppable.
        archive = gate("archive", "pending")
        archive["bookend"] = True
        cl = gated(g1=gate("g1", "pending"), archive=archive)
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, {"ops": [{"op": "drop", "id": "archive"}]}, "r", "human")
        self.assertIn("bookend", str(ctx.exception))
        self.assertIn("archive", cl["tasks"])

    def test_amend_drop_pending_gate_no_bookend_key_still_succeeds(self):
        # backward compatibility: no 'bookend' key anywhere -> 9b38b9d9 behavior.
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   archive=gate("archive", "pending"))
        E.amend(cl, {"ops": [{"op": "drop", "id": "archive"}]}, "cut it", "human")
        self.assertEqual(cl["items"], ["g1"])
        self.assertNotIn("archive", cl["tasks"])

    def test_amend_reproduces_measured_gap_refused_when_declared(self):
        # probe-closing-bookend.md's fixture: init/context/understand/plan
        # complete, execute in-progress, reconcile/triage/review/feedback/archive
        # pending. The probe's delta dropped archive, feedback, review with
        # exit 0. Declared, it must now be refused (and unmutated).
        tasks = {
            "init": gate("init", "complete", command=PASS_COMMAND),
            "context": gate("context", "complete", command=PASS_COMMAND),
            "understand": gate("understand", "complete", command=PASS_COMMAND),
            "plan": gate("plan", "complete", command=PASS_COMMAND),
            "execute": gate("execute", "in-progress", command=PASS_COMMAND),
            "reconcile": gate("reconcile", "pending"),
            "triage": gate("triage", "pending"),
            "review": gate("review", "pending"),
            "feedback": gate("feedback", "pending"),
            "archive": gate("archive", "pending"),
        }
        tasks["archive"]["bookend"] = True
        cl = gated(**tasks)
        before = copy.deepcopy(cl)
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [{"op": "drop", "id": "archive"},
                                  {"op": "drop", "id": "feedback"},
                                  {"op": "drop", "id": "review"}]},
                    "probe: is the CLOSING bookend frozen?", "probe")
        self.assertEqual(cl["items"], before["items"])
        self.assertEqual(cl["tasks"], before["tasks"])

    def test_amend_rescope_refuses_bookend_gate(self):
        g1 = gate("g1", "pending")
        g1["bookend"] = True
        cl = gated(g1=g1)
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, {"ops": [{"op": "rescope", "id": "g1", "title": "x"}]}, "r", "human")
        self.assertIn("bookend", str(ctx.exception))
        self.assertEqual(cl["tasks"]["g1"]["title"], "g1")

    def test_amend_rescope_sets_bookend_flag_via_overwritable(self):
        # retrofit path: a live spine can be frozen through the engine.
        cl = gated(g1=gate("g1", "pending"))
        self.assertNotIn("bookend", cl["tasks"]["g1"])
        E.amend(cl, {"ops": [{"op": "rescope", "id": "g1", "bookend": True}]},
                "retrofit", "human")
        self.assertTrue(cl["tasks"]["g1"]["bookend"])

    def test_amend_rescope_bookend_flag_is_one_way_latch(self):
        cl = gated(g1=gate("g1", "pending"))
        E.amend(cl, {"ops": [{"op": "rescope", "id": "g1", "bookend": True}]},
                "retrofit", "human")
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [{"op": "rescope", "id": "g1", "bookend": False}]},
                    "try to unset", "human")
        self.assertTrue(cl["tasks"]["g1"]["bookend"])

    def test_amend_retext_check_refuses_bookend_gate(self):
        # a freeze that only stops deletion is not a freeze: retext-check could
        # otherwise rewrite a frozen gate's command to something trivially true.
        g1 = gate("g1", "in-progress", command=FAIL_COMMAND)
        g1["bookend"] = True
        cl = gated(g1=g1)
        with self.assertRaises(E.EngineError) as ctx:
            E.amend(cl, {"ops": [{"op": "retext-check", "id": "g1", "cond": "c1",
                                  "command": PASS_COMMAND}]}, "r", "human")
        self.assertIn("bookend", str(ctx.exception))
        self.assertEqual(cl["tasks"]["g1"]["postconditions"][0]["check"]["command"], FAIL_COMMAND)

    def test_amend_all_or_nothing_leaves_checklist_unmutated_with_bookend_violation(self):
        # 1st op legal (add g3), 2nd op refused (drop the bookend g2). The
        # whole delta must abort: items/tasks byte-identical, legal op absent.
        g2 = gate("g2", "pending")
        g2["bookend"] = True
        cl = gated(g1=gate("g1", "pending"), g2=g2)
        before = copy.deepcopy(cl)
        with self.assertRaises(E.EngineError):
            E.amend(cl, {"ops": [_add_op("g3", after="g1"),
                                 {"op": "drop", "id": "g2"}]}, "r", "human")
        self.assertEqual(cl["items"], before["items"])
        self.assertEqual(cl["tasks"], before["tasks"])
        self.assertNotIn("amendments", cl)


class ReopenCascade(unittest.TestCase):
    def test_reopen_cascades_downstream_complete_and_supersedes_evidence(self):
        cl = gated(g1=_artifact_gate("g1", "complete"),
                   g2=_artifact_gate("g2", "complete"),
                   g3=gate("g3", "pending", command=PASS_COMMAND))
        # give both g1 and g2 their own review-result evidence
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        E.attach(cl, "g2", "review-result", {"verdict": "APPROVE"})
        cl["tasks"]["g1"]["postconditions"][0]["satisfied"] = True
        cl["tasks"]["g2"]["postconditions"][0]["satisfied"] = True
        msg = E.reopen(cl, "g1", "rework g1")
        # target back in-progress
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        # downstream g2 reset to pending
        self.assertEqual(cl["tasks"]["g2"]["status"], "pending")
        self.assertFalse(cl["tasks"]["g2"]["postconditions"][0]["satisfied"])
        self.assertEqual(cl["tasks"]["g2"]["status_detail"]["superseded_by_reopen"], "g1")
        # g2's evidence retained but marked superseded
        ev = cl["tasks"]["g2"]["evidence"][0]
        self.assertIn("superseded", ev)
        self.assertEqual(ev["superseded"]["by"], "reopen:g1")
        self.assertEqual(ev["superseded"]["reason"], "rework g1")
        # target's own evidence superseded too
        self.assertIn("superseded", cl["tasks"]["g1"]["evidence"][0])
        self.assertIn("cascade-reset downstream", msg)
        self.assertIn("g2", msg)

    def test_reopen_cascade_leaves_downstream_skipped_untouched(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "skipped", command=PASS_COMMAND),
                   g3=gate("g3", "complete", command=PASS_COMMAND))
        cl["tasks"]["g2"]["status_detail"] = {"reason": "OBE"}
        msg = E.reopen(cl, "g1", "redo")
        # skipped downstream untouched
        self.assertEqual(cl["tasks"]["g2"]["status"], "skipped")
        self.assertNotIn("superseded_by_reopen", cl["tasks"]["g2"]["status_detail"])
        # complete downstream g3 was reset
        self.assertEqual(cl["tasks"]["g3"]["status"], "pending")
        self.assertIn("g3", msg)

    def test_reopen_no_cascade_when_no_downstream_touchable(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND),
                   g2=gate("g2", "pending", command=PASS_COMMAND))
        msg = E.reopen(cl, "g1", "redo")
        # g2 already pending -> not cascaded, message has no cascade clause
        self.assertNotIn("cascade-reset", msg)
        self.assertEqual(cl["tasks"]["g2"]["status"], "pending")

    def test_superseded_evidence_does_not_satisfy_artifact_recheck(self):
        # g1 passes on its own review-result; reopen supersedes it; advance must
        # refuse until FRESH evidence is attached.
        cl = gated(g1=_artifact_gate("g1", "in-progress"))
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")
        E.reopen(cl, "g1", "stale approval")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")  # only evidence is superseded -> inert
        # fresh evidence rescues it
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")

    def test_superseded_evidence_refused_by_attest_reference(self):
        cl = gated(g1=_artifact_gate("g1", "complete"),
                   g2=_artifact_gate("g2", "pending"))
        E.attach(cl, "g1", "review-result", {"verdict": "APPROVE"})
        E.reopen(cl, "g1", "supersede it")  # supersedes g1's evidence
        with self.assertRaises(E.EngineError) as ctx:
            E.attest(cl, "g2", "c1", "postconditions", None, evidence_id="e-g1-1")
        self.assertIn("superseded", str(ctx.exception))


class JournalEmission(unittest.TestCase):
    """The append-only journal sidecar (#131): one hash-chained line per SUCCESSFUL
    mutating verb, written only by main(), never read back by the engine (backward
    compatible)."""

    def _save(self, d, cl):
        f = Path(d) / "spine.json"
        E.save(f, cl)
        return f

    def _journal_lines(self, f):
        jp = Path(str(f) + ".journal")
        if not jp.is_file():
            return []
        return [json.loads(ln) for ln in jp.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def test_mutating_verb_appends_one_journal_line(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            self.assertEqual(E.main(["--file", str(f), "start", "g1"]), 0)
            lines = self._journal_lines(f)
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0]["verb"], "start")
            self.assertEqual(lines[0]["task"], "g1")
            self.assertEqual(lines[0]["seq"], 1)
            self.assertEqual(lines[0]["prev_hash"], "")
            self.assertTrue(lines[0]["hash"])

    def test_non_mutating_verb_does_not_journal(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            self.assertEqual(E.main(["--file", str(f), "current"]), 0)
            self.assertEqual(self._journal_lines(f), [])

    def test_dry_run_does_not_journal(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            self.assertEqual(E.main(["--file", str(f), "--dry-run", "start", "g1"]), 0)
            self.assertEqual(self._journal_lines(f), [])

    def test_refused_verb_does_not_journal(self):
        # advancing a failing gate refuses (exit 1) -> no journal line for it.
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 1)
            self.assertEqual(self._journal_lines(f), [])

    def test_hash_chain_links_successive_verbs(self):
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            E.main(["--file", str(f), "start", "g1"])
            E.main(["--file", str(f), "advance", "g1"])
            lines = self._journal_lines(f)
            self.assertEqual([l["seq"] for l in lines], [1, 2])
            self.assertEqual(lines[1]["prev_hash"], lines[0]["hash"])

    def test_journal_captures_new_evidence_ids(self):
        # advancing a command gate produces e-g1-1; the journal records it.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            E.main(["--file", str(f), "advance", "g1"])
            lines = self._journal_lines(f)
            self.assertIn("e-g1-1", lines[-1]["evidence_ids"])

    def test_engine_never_reads_journal_backward_compatible(self):
        # A pre-existing junk journal must not perturb engine operation: verbs still
        # succeed and the engine appends, proving it never reads the sidecar back.
        cl = gated(g1=gate("g1", "pending", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = self._save(d, cl)
            Path(str(f) + ".journal").write_text("not json at all\n", encoding="utf-8")
            self.assertEqual(E.main(["--file", str(f), "start", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "in-progress")


class AppendJournalEntryLineEndings(unittest.TestCase):
    """Issue #493: `append_journal_entry` wrote in text mode
    (`jp.open('a', encoding='utf-8')`), the same defect class #465 fixed in
    `save()` -- a platform-default newline translation on write churns an
    existing journal's endings on every append and ignores the file's own
    convention. Mirrors tests/test_engine_survey_retext_and_newlines.py's
    save() pattern: fixtures built with `write_bytes`, assertions on
    `read_bytes` -- a `write_text` fixture is born CRLF on Windows and a
    `read_text` assertion is vacuously true forever under universal-newline
    translation, so neither can prove anything here."""

    def _line_ending_counts(self, raw: bytes) -> tuple[int, int]:
        crlf = raw.count(b"\r\n")
        return crlf, raw.count(b"\n") - crlf

    def _append(self, jp: Path) -> None:
        spine_path = Path(str(jp)[:-len(".journal")])
        E.append_journal_entry(spine_path, "start", "g1", "s1", [])

    def test_append_preserves_lf_journal_endings(self):
        # On WINDOWS this is the discriminating case: the old text-mode open
        # translates every written '\n' to the platform ending ('\r\n'), so
        # the new line lands CRLF while the rest of the journal stays LF --
        # a churned, mixed-ending file.
        with tempfile.TemporaryDirectory() as d:
            jp = Path(d) / "spine.json.journal"
            jp.write_bytes(b'{"seq": 1, "hash": "x"}\n')
            crlf, lf = self._line_ending_counts(jp.read_bytes())
            self.assertEqual(crlf, 0, "fixture was not born LF")

            self._append(jp)

            crlf, lf = self._line_ending_counts(jp.read_bytes())
            self.assertEqual(
                crlf, 0,
                f"append_journal_entry churned an LF journal to CRLF "
                f"({crlf} CRLF endings written)")
            self.assertGreater(lf, 1, "append wrote no new line")

    def test_append_preserves_crlf_journal_endings(self):
        # Guard against the obvious over-correction of "always write LF" --
        # on POSIX this is the discriminating case, on Windows it is the one
        # that must not regress.
        with tempfile.TemporaryDirectory() as d:
            jp = Path(d) / "spine.json.journal"
            jp.write_bytes(b'{"seq": 1, "hash": "x"}\r\n')
            crlf, lf = self._line_ending_counts(jp.read_bytes())
            self.assertGreater(crlf, 0, "fixture was not born CRLF")
            self.assertEqual(lf, 0, "fixture was not born CRLF")

            self._append(jp)

            crlf, lf = self._line_ending_counts(jp.read_bytes())
            self.assertGreater(crlf, 1, "append wrote no CRLF endings at all")
            self.assertEqual(
                lf, 0,
                f"append_journal_entry churned a CRLF journal to LF "
                f"({lf} bare LF endings written)")

    def test_append_defaults_new_journal_to_lf(self):
        with tempfile.TemporaryDirectory() as d:
            jp = Path(d) / "spine.json.journal"
            self.assertFalse(jp.exists())

            self._append(jp)

            crlf, lf = self._line_ending_counts(jp.read_bytes())
            self.assertEqual(crlf, 0, "a brand-new journal must default to LF")
            self.assertGreater(lf, 0, "append wrote no line endings at all")


class DoctrineRail(unittest.TestCase):
    """#138 channel A: the engine appends position-derived doctrine to railed verbs'
    success output and the check-failure rail to the REFUSED path. The five strings
    are frozen/verbatim; these tests pin the exact asserted substrings."""

    def test_rail_verbs_set_is_exact(self):
        # Only these five verbs are railed. `current` was removed (A1, deficiency
        # cleanup batch A+B): it is the only railed verb a NON-OWNER routinely
        # calls, so railing it told a reader who had not yet decided a dead plan
        # was its own to "Run it." heartbeat/release/record/skip are still not
        # railed either.
        self.assertEqual(
            E.RAIL_VERBS,
            {"claim", "start", "advance", "attest", "attach"},
        )
        for unrailed in ("heartbeat", "release", "record", "skip", "consolidate", "current"):
            self.assertNotIn(unrailed, E.RAIL_VERBS)

    def test_rail_marker_and_leading_newlines(self):
        cl = gated(g1=gate("g1", "in-progress"), g2=gate("g2"), g3=gate("g3"))
        rail = E._rail("current", cl)
        self.assertTrue(rail.startswith("\n\nRAIL: "))

    def test_rail_early(self):
        # active gate is the first item (n == 3) -> early, {id} = g1
        cl = gated(g1=gate("g1", "in-progress"), g2=gate("g2"), g3=gate("g3"))
        rail = E._rail("current", cl)
        self.assertIn(
            "Work the engine never saw did not happen. Run the step's checks, "
            "then `attest` and `advance g1`.",
            rail,
        )

    def test_rail_mid_flight(self):
        # g1 done, g2 active (not first), n == 2 -> mid-flight, {n}=2.
        # ON THE `current` VERB SPECIFICALLY (issue #420): render_human()'s own
        # ACTIVE line already prints g2's full imperative, so the RAIL must NOT
        # repeat it -- it substitutes a short pointer instead. The frozen
        # `_RAIL_STRINGS["mid-flight"]` TEMPLATE text itself is unchanged
        # ("...Next: {imperative}. Run it."); only what fills {imperative}
        # changes, and only for point=='current'.
        cl = gated(g1=gate("g1", "complete"),
                   g2=gate("g2", "in-progress"), g3=gate("g3"))
        rail = E._rail("current", cl)
        self.assertIn(
            "A working solution is the MIDDLE of this run — you are 2 steps "
            "from done. Next:",
            rail,
        )
        self.assertNotIn("do g2", rail, "current's RAIL must not repeat the "
                          "imperative already shown on the ACTIVE line")
        # The imperative appears exactly once in current()'s full combined
        # output (ACTIVE line) -- not a second time inside the RAIL.
        full = E.current(cl) + rail
        self.assertEqual(full.count("do g2"), 1)

    def test_rail_mid_flight_non_current_verb_keeps_full_imperative(self):
        # Sibling to the dedup test above: every OTHER railed verb
        # (claim/start/advance/attest/attach) has no ACTIVE line of its own in
        # its output, so the RAIL's imperative mention is the ONLY place the
        # caller sees "what's next" -- it must stay the full, unabridged text,
        # unchanged from before this fix. Same fixture as test_rail_mid_flight.
        cl = gated(g1=gate("g1", "complete"),
                   g2=gate("g2", "in-progress"), g3=gate("g3"))
        for verb in ("start", "advance", "attest", "claim", "attach"):
            rail = E._rail(verb, cl)
            self.assertIn(
                "A working solution is the MIDDLE of this run — you are 2 "
                "steps from done. Next: do g2. Run it.",
                rail,
                f"non-current verb {verb!r} must keep the full imperative",
            )

    def test_dispatch_current_shows_imperative_exactly_once_mid_flight(self):
        # CLI-boundary regression guard (issue #420 close criterion): drive
        # through dispatch()/main(), not the bare current() function, since
        # the duplication only existed at the RAIL layer appended in
        # dispatch(). g1 complete, g2 active (not first/last), g3 pending --
        # a genuine mid-flight spine, 3+ gates.
        cl = gated(g1=gate("g1", "complete"),
                   g2=gate("g2", "in-progress"), g3=gate("g3"))
        code, out, err = _run_main(cl, ["current"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("do g2"), 1, out)

    def test_rail_near_terminal(self):
        # one non-terminal item remains (n == 1) -> near-terminal
        cl = gated(g1=gate("g1", "complete"), g2=gate("g2", "in-progress"))
        rail = E._rail("current", cl)
        self.assertIn(
            "The finish is a sequence, not an announcement. Final `advance` "
            "first, then `release` — the journal, not your prose, is the proof.",
            rail,
        )

    def test_rail_terminal(self):
        # no non-terminal items (n == 0) -> terminal
        cl = gated(g1=gate("g1", "complete"), g2=gate("g2", "complete"))
        rail = E._rail("current", cl)
        self.assertIn(
            "Release is your last journaled action. Run `release`; do not claim it.",
            rail,
        )

    def test_rail_only_on_gated(self):
        # survey checklists get NO rail, ever.
        s = survey(v1=survey_item("v1", "in-progress"))
        self.assertEqual(E._rail("current", s), "")
        self.assertEqual(E._rail("check-failure", s), "")

    def test_dispatch_appends_rail_to_success_output(self):
        # A successful advance moves g1 -> complete; active becomes g2 (n == 1),
        # so the appended rail is the near-terminal string. Proves dispatch wiring.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND),
                   g2=gate("g2"))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            import contextlib, io
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            printed = out.getvalue()
            self.assertIn("RAIL: ", printed)
            self.assertIn(
                "The finish is a sequence, not an announcement. Final `advance` "
                "first, then `release` — the journal, not your prose, is the proof.",
                printed,
            )

    def test_main_refused_path_appends_check_failure_rail(self):
        # A failing command gate refuses advance (exit 1); the REFUSED stderr line
        # carries the check-failure rail verbatim.
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 1)
            printed = err.getvalue()
            self.assertIn("REFUSED:", printed)
            self.assertIn(
                "This check failed; that verdict is scoped to this check, not the "
                "approach. Do the missing work and `attest`/`attach` the evidence, "
                "or escalate with `block`/`waive` and a reason. Report 'this check "
                "failed', never 'this step is impossible'. Quiet abandonment and "
                "fabricated evidence are the two forbidden exits.",
                printed,
            )

    def test_refused_rail_suppressed_on_survey(self):
        # A survey refusal must NOT carry a rail.
        s = survey(v1=survey_item("v1", "pending"))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "s.json"
            E.save(f, s)
            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                # advance is invalid for a survey -> REFUSED, but no rail.
                self.assertEqual(E.main(["--file", str(f), "advance", "v1"]), 1)
            printed = err.getvalue()
            self.assertIn("REFUSED:", printed)
            self.assertNotIn("RAIL:", printed)


class RailPositionOrdering(unittest.TestCase):
    """Item 4 / constraint 4 (issue #227 gate g3): the RAIL banner moves to
    the FRONT for every railed verb, and to the front of the REFUSED path in
    main() -- the operative result/refusal line lands LAST on its stream, so
    `tail -1` reads the result, not the banner. This is the exact field
    defect: the Admiral piped engine output through `tail -1` and saw only
    the banner, silently hiding a real REFUSED line.

    `current` was removed from `RAIL_VERBS` (A1, deficiency cleanup batch
    A+B) and no longer carries any RAIL banner at all -- see
    `test_current_carries_no_rail_banner` below."""

    def test_success_output_rail_banner_is_first_operative_line_is_last(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND), g2=gate("g2"))
        code, out, err = _run_main(cl, ["advance", "g1", "--mechanical"])
        self.assertEqual(code, 0)
        lines = [ln for ln in out.splitlines() if ln.strip()]
        self.assertTrue(lines[0].startswith("RAIL: "), lines)
        self.assertEqual(lines[-1], "g1 -> complete")

    def test_current_carries_no_rail_banner(self):
        # A1: `current` is unrailed. A plan whose owner is long gone must not
        # tell a mere reader "you are N steps from done... Run it." -- the
        # body starts directly with the ACTIVE line, no RAIL: banner at all.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND),
                   g2=gate("g2"), g3=gate("g3"))
        code, out, err = _run_main(cl, ["current"])
        self.assertEqual(code, 0)
        self.assertNotIn("RAIL: ", out)
        self.assertTrue(out.startswith("ACTIVE g1"), out)

    def test_refused_output_rail_banner_is_first_operative_refused_line_is_last(self):
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND))
        code, out, err = _run_main(cl, ["advance", "g1", "--mechanical"])
        self.assertEqual(code, 1)
        lines = [ln for ln in err.splitlines() if ln.strip()]
        self.assertTrue(lines[0].startswith("RAIL: "), lines)
        self.assertTrue(lines[-1].startswith("REFUSED:"), lines)

    def test_tail_minus_1_yields_refusal_not_banner_state_caused(self):
        # The exact field defect, reproduced: a state-caused refusal (blocked
        # task) piped through `tail -1` must show the REFUSED line, not RAIL.
        g = gate("g1", "blocked")
        g["status_detail"] = {"prior_status": "pending"}
        cl = gated(g1=g)
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        tail_1 = [ln for ln in err.splitlines() if ln.strip()][-1]
        self.assertIn("REFUSED:", tail_1)

    def test_tail_minus_1_yields_success_result_not_banner(self):
        cl = gated(g1=gate("g1", "pending"))
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 0)
        tail_1 = [ln for ln in out.splitlines() if ln.strip()][-1]
        self.assertEqual(tail_1, "g1 -> in-progress")

    def test_survey_refusal_still_no_rail_operative_line_still_last(self):
        s = survey(v1=survey_item("v1", "pending"))
        code, out, err = _run_main(s, ["advance", "v1"])
        self.assertEqual(code, 1)
        self.assertNotIn("RAIL:", err)
        tail_1 = [ln for ln in err.splitlines() if ln.strip()][-1]
        self.assertIn("REFUSED:", tail_1)


def _run_at_archived(cl, argv, work="run1"):
    """Like `_run_main`, but the checklist file's own directory sits under a
    literal `.agent-work/archive/<work>/` path -- so `_is_archived_path`'s
    predicate (a lexical fact about `--file`, not the tempdir's parent) reads
    True, exactly as it would for a real archived plan."""
    import contextlib
    import io
    with tempfile.TemporaryDirectory() as d:
        archive_dir = Path(d) / ".agent-work" / "archive" / work
        archive_dir.mkdir(parents=True)
        f = archive_dir / "c.json"
        E.save(f, cl)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = E.main(["--file", str(f)] + argv)
        return code, out.getvalue(), err.getvalue()


class ArchivedPathBannerAndRailSuppression(unittest.TestCase):
    """A2 (deficiency cleanup batch A+B): a plan filed under `.agent-work/
    archive/` is finished by definition. It gets the ARCHIVED banner and the
    rail is suppressed -- a path fact, no liveness claim, refuses nothing."""

    def test_current_on_archived_plan_shows_banner_and_no_rail(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND), g2=gate("g2"))
        code, out, err = _run_at_archived(cl, ["current"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith(E._ARCHIVED_BANNER), out)
        self.assertNotIn("RAIL:", out)
        self.assertIn("ACTIVE g1", out)

    def test_current_on_non_archived_plan_shows_no_banner(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        code, out, err = _run_main(cl, ["current"])
        self.assertEqual(code, 0)
        self.assertNotIn("ARCHIVED", out)

    def test_railed_mutating_verb_on_archived_plan_still_works_no_rail_banner_shown(self):
        # The banner and suppression apply to EVERY railed verb dispatched
        # against an archived-path plan, not only the read-only `current` --
        # the verb itself still runs; only the advice around it changes.
        cl = gated(g1=gate("g1", "pending"))
        code, out, err = _run_at_archived(cl, ["start", "g1"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith(E._ARCHIVED_BANNER), out)
        self.assertNotIn("RAIL:", out)
        self.assertIn("g1 -> in-progress", out)

    def test_non_railed_verb_on_archived_plan_still_gets_the_banner(self):
        # `block` is a MUTATING verb but not in RAIL_VERBS, so the banner here
        # is proof it is applied independently of the rail-suppression branch,
        # not by riding along inside it.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        code, out, err = _run_at_archived(
            cl, ["block", "g1", "--blocker", "x1 result", "--authority", "parent agent"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith(E._ARCHIVED_BANNER), out)

    def test_is_archived_path_is_a_lexical_fact_not_a_resolve(self):
        self.assertTrue(E._is_archived_path(Path("/anything/.agent-work/archive/x")))
        self.assertTrue(E._is_archived_path(Path("/anything/.agent-work/archive")))
        self.assertFalse(E._is_archived_path(Path("/anything/.agent-work/run1")))
        self.assertFalse(E._is_archived_path(Path("/agent-work/archive/x")))
        self.assertFalse(E._is_archived_path(None))


class NextForTheHolder(unittest.TestCase):
    """A4 (deficiency cleanup batch A+B): the `next:` hint is addressed to
    whoever holds the plan's lease -- relabeled to `next (for the holder):`
    whenever a lease is held, true for the owner and a stranger alike, and
    left exactly as `next:` when no lease exists (the common, majority
    shape -- see A2/A3's own tests)."""

    def test_next_relabeled_when_a_lease_is_held(self):
        cl = gated(g1=gate("g1", "pending"))
        E.claim(cl, "s1", "commander", ".", {})
        out = E.current(cl)
        self.assertIn("next (for the holder): start g1", out)
        self.assertNotIn("\nnext: start g1", out)

    def test_next_unrelabeled_with_no_lease(self):
        cl = gated(g1=gate("g1", "pending"))
        out = E.current(cl)
        self.assertIn("next: start g1", out)
        self.assertNotIn("for the holder", out)

    def test_next_unrelabeled_after_release(self):
        cl = gated(g1=gate("g1", "pending"))
        E.claim(cl, "s1", "commander", ".", {})
        E.release(cl, "s1")
        out = E.current(cl)
        self.assertIn("next: start g1", out)
        self.assertNotIn("for the holder", out)


class RecoveryGoldenOutput(unittest.TestCase):
    """Item 2 (issue #227 gate g3): every state-caused REFUSED names its
    exact exit verb. One golden test per refusal family named in the
    handoff's table, plus the runnable-as-written proof (constraint 6)."""

    def test_blocked_task_recovery_names_resume_and_notes_no_unblock_verb(self):
        g = gate("g1", "blocked")
        g["status_detail"] = {"prior_status": "pending"}
        cl = gated(g1=g)
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        self.assertIn("REFUSED:", err)
        self.assertIn("resume g1 --reason", err)
        self.assertIn("no separate", err.lower())
        self.assertIn("Do not edit the JSON — use the engine.", err)

    def test_blocked_task_with_no_restorable_prior_does_not_suggest_resume_or_reopen(self):
        # No status_detail.prior_status at all: resume would ALSO refuse, and
        # so would reopen (it requires status=="complete", never "blocked") --
        # recovery must not loop back to a command that just fails again
        # (Reviewer BLOCK, g3-review rework 1: the previous fix here still
        # named `reopen` as a runnable alternative; it refuses every time).
        # Only `skip` genuinely works from this state -- prove it runs.
        g = gate("g1", "blocked")
        cl = gated(g1=g)
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        self.assertNotIn("resume g1 --reason", err)
        self.assertNotIn("reopen g1 --reason", err)
        self.assertIn("skip g1 --reason", err)
        self.assertIn("Do not edit the JSON — use the engine.", err)
        self.assertEqual(E.skip(cl, "g1", "why"), "g1 -> skipped because why")

    def test_complete_task_recovery_names_reopen(self):
        cl = gated(g1=gate("g1", "complete"))
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        self.assertIn("reopen g1 --reason", err)
        self.assertIn("Do not edit the JSON — use the engine.", err)

    def test_unmet_precondition_recovery_names_exact_attest_with_real_id(self):
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        self.assertIn("attest g1 --cond p1 --which preconditions", err)
        self.assertIn("Do not edit the JSON — use the engine.", err)

    def test_unmet_postcondition_recovery_names_exact_attest_with_real_id(self):
        post_null = [{"id": "c1", "statement": "docs updated", "check": None, "satisfied": False}]
        g = gate("g1", "in-progress")
        g["postconditions"] = post_null
        cl = gated(g1=g)
        code, out, err = _run_main(cl, ["advance", "g1", "--mechanical"])
        self.assertEqual(code, 1)
        self.assertIn("attest g1 --cond c1 --which postconditions", err)
        self.assertIn("Do not edit the JSON — use the engine.", err)

    def test_recovery_commands_actually_run(self):
        # Constraint 6: recovery must be runnable AS WRITTEN (positional id,
        # not --id) -- prove it by actually running the printed command.
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        self.assertIn("attest g1 --cond p1 --which preconditions", err)
        E.attest(cl, "g1", "p1", "preconditions", "checked it")
        self.assertEqual(E.start(cl, "g1"), "g1 -> in-progress")


class UnknownCondIdRecovery(unittest.TestCase):
    """Constraint 3 (issue #227 gate g3): unknown-cond-id is a 4th axis
    OUTSIDE the (status, verb) grid -- a malformed-argument refusal, not a
    status one. Its own standalone test: the refusal must literally contain
    EVERY real p*/c* id on the task, not just the words
    'preconditions'/'postconditions' (test_attest_not_found_names_both_lists
    at :236 only asserts the latter and must not be mistaken for coverage of
    this)."""

    def test_unknown_cond_id_enumerates_every_real_id_on_the_task(self):
        pre = [{"id": "p1", "statement": "a", "check": None, "satisfied": False},
               {"id": "p2", "statement": "b", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, preconds=pre))
        code, out, err = _run_main(cl, ["attest", "g1", "--cond", "nope", "--which", "preconditions"])
        self.assertEqual(code, 1)
        self.assertIn("REFUSED:", err)
        for real_id in ("p1", "p2", "c1"):
            self.assertIn(real_id, err)


class Inv3RecoveryEnumeration(unittest.TestCase):
    """Constraint 2 (issue #227 gate g3, THE TRAP): the enumeration grid must
    be GENERATED from MUTATING_VERBS + the engine's own status vocabulary,
    not a hand-typed list of the three named refusal families -- a
    hand-typed list would pass green while OTHER status-guarded refusals
    (e.g. `advance` on a `pending` task, `reopen` on a `blocked` task) fall
    through to the old bare message."""

    # WHICH verbs carry a status guard is unavoidably identified by hand (the
    # guard lives inside each verb's own body, not in a lookup table); what
    # must NOT be hand-typed is the grid itself, the coverage count, or
    # "non-generic" -- all three are derived/checked below. The EXCLUSION of
    # every other MUTATING_VERBS member is independently PROVEN (not just
    # asserted) by Inv3ExclusionCheck below, which actually runs them.
    STATUS_GUARDED_VERBS = {"start": "pending", "advance": "in-progress",
                             "resume": "blocked", "reopen": "complete"}

    def _argv(self, verb, tid):
        return {
            "start": ["start", tid],
            "advance": ["advance", tid, "--mechanical"],
            "resume": ["resume", tid, "--reason", "cleared"],
            "reopen": ["reopen", tid, "--reason", "why"],
        }[verb]

    def _fixture(self, status):
        g = gate("g1", status, command=PASS_COMMAND)
        if status == "blocked":
            g["status_detail"] = {"prior_status": "pending"}
        return gated(g1=g)

    def _is_non_generic(self, message, task_id):
        runnable_tokens = ("start ", "advance ", "resume ", "reopen ", "attest ")
        return task_id in message and any(tok in message for tok in runnable_tokens)

    def test_generated_grid_every_state_caused_refusal_is_non_generic(self):
        self.assertTrue(set(self.STATUS_GUARDED_VERBS) <= E.MUTATING_VERBS)
        grid = [(status, verb) for verb in self.STATUS_GUARDED_VERBS for status in E.STATUS_VALUES]
        self.assertEqual(len(grid), len(self.STATUS_GUARDED_VERBS) * len(E.STATUS_VALUES))
        refused = 0
        honest_terminal = 0
        for status, verb in grid:
            cl = self._fixture(status)
            code, out, err = _run_main(cl, self._argv(verb, "g1"))
            if code == 0:
                self.assertEqual(status, self.STATUS_GUARDED_VERBS[verb],
                                  f"{verb} unexpectedly succeeded from status={status!r}")
                continue
            self.assertIn("REFUSED:", err)
            refused += 1
            if status == "skipped":
                # Genuinely terminal: no verb reverses a skip. An honest
                # "no recovery verb exists" statement is correct here, not a
                # fabricated runnable command (global doctrine: fail visibly,
                # no hidden fallback).
                self.assertIn("g1", err)
                self.assertIn("skip", err.lower())
                honest_terminal += 1
            else:
                self.assertTrue(self._is_non_generic(err, "g1"),
                                 f"generic refusal for (status={status!r}, verb={verb!r}): {err!r}")
        expected_refusals = len(grid) - len(self.STATUS_GUARDED_VERBS)
        self.assertEqual(refused, expected_refusals)
        self.assertEqual(honest_terminal, len(self.STATUS_GUARDED_VERBS))


class Inv3ExclusionCheck(unittest.TestCase):
    """The trap's own named examples (issue #227 gate g3 handoff): `waive` on
    a complete gate, `block` on an already-blocked gate, `attest` on a
    pending task, `skip` on a complete gate -- plus `attach`, the fifth
    verb with no status guard. None of these five guards on task status in
    its own body -- proven here by actually RUNNING each across every
    status, rather than asserted in prose.

    Reviewer BLOCK (g3-review rework 1): the previous version of this class
    hand-picked 4 of the 10 excluded `MUTATING_VERBS` members and claimed
    totality it never checked -- `amend`'s `drop`/`rescope`/`retext-check`
    sub-ops turned out to guard on status too (now covered by
    `Inv3AmendSubOpEnumeration` below, with recovery wired). The exclusion
    set here is now DERIVED from `E.MUTATING_VERBS` itself (an engine-native
    constant) minus the buckets covered elsewhere, so a FUTURE verb that
    starts guarding on status and isn't sorted into one of those buckets
    fails the set-equality assertion below instead of silently vanishing
    from coverage the way `amend` did."""

    STATUS_GUARDED_TOP_LEVEL = {"start", "advance", "resume", "reopen"}
    STRUCTURALLY_EXCLUDED = {"record", "consolidate", "append", "flag-candidate"}
    PARTIALLY_GUARDED = {"amend"}

    def test_exclusion_set_is_derived_and_exhaustive(self):
        remaining = (E.MUTATING_VERBS - self.STATUS_GUARDED_TOP_LEVEL
                     - self.STRUCTURALLY_EXCLUDED - self.PARTIALLY_GUARDED)
        self.assertEqual(remaining, {"skip", "block", "attest", "waive", "attach"})

    def test_waive_block_attest_skip_attach_never_produce_a_status_caused_refusal(self):
        for status in E.STATUS_VALUES:
            post = [{"id": "c1", "statement": "x", "check": None, "satisfied": False,
                     "override_policy": {"allowed": True}}]
            g = gate("g1", status)
            g["postconditions"] = post
            if status == "blocked":
                g["status_detail"] = {"prior_status": "pending"}
            base_cl = gated(g1=g)
            for verb, args in (
                ("waive", ["waive", "g1", "--cond", "c1", "--which", "postconditions",
                           "--authority", "human", "--reason", "why"]),
                ("block", ["block", "g1", "--blocker", "x", "--authority", "human"]),
                ("attest", ["attest", "g1", "--cond", "c1", "--which", "postconditions",
                            "--note", "n"]),
                ("skip", ["skip", "g1", "--reason", "why"]),
                ("attach", ["attach", "g1", "--type", "note", "--field", "k=v"]),
            ):
                cl = copy.deepcopy(base_cl)
                code, out, err = _run_main(cl, args)
                self.assertEqual(code, 0,
                                  f"{verb} on status={status!r} unexpectedly refused: {err!r}")


class Inv3StructuralExclusion(unittest.TestCase):
    """The remaining `MUTATING_VERBS` members (`record`, `consolidate`,
    `append`, `flag-candidate`) are excluded from the (status, verb) grid for
    a STRUCTURAL reason, not because nobody checked: `record`/`append`
    refuse on a checklist-TYPE mismatch before ever inspecting a task's
    status; `consolidate`/`flag-candidate` take no task `id` argument at
    all. Verified by running them against a gated, single-task fixture
    across every status (record/append) or with no id supplied at all
    (consolidate/flag-candidate)."""

    def test_record_and_append_refuse_on_type_before_touching_task_status(self):
        for status in E.STATUS_VALUES:
            cl = gated(g1=gate("g1", status, command=PASS_COMMAND))
            code, out, err = _run_main(cl, ["record", "g1", "--result", "pass"])
            self.assertEqual(code, 1)
            self.assertIn("record is for survey checklists", err)
            cl2 = gated(g1=gate("g1", status, command=PASS_COMMAND))
            code, out, err = _run_main(cl2, ["append", "g9", "--title", "t", "--imperative", "i"])
            self.assertEqual(code, 1)
            self.assertIn("append only on survey checklists", err)

    def test_consolidate_and_flag_candidate_never_touch_a_task_id(self):
        for status in E.STATUS_VALUES:
            s = survey(v1=survey_item("v1", "complete"))
            code, out, err = _run_main(s, ["consolidate", "--verdict", "APPROVE"])
            self.assertEqual(code, 0)
            cl = gated(g1=gate("g1", status, command=PASS_COMMAND))
            code, out, err = _run_main(cl, ["flag-candidate", "--from", "g1", "--statement", "s"])
            self.assertEqual(code, 0)


class Inv3AmendSubOpEnumeration(unittest.TestCase):
    """Same GENERATED-grid rigor as `Inv3RecoveryEnumeration`, applied to
    `amend`'s status-guarded sub-ops (Reviewer BLOCK, g3-review rework 1:
    these were the actual hole in the original exclusion claim). The grid is
    amend's own op-kind -> required-status(es) mapping (read directly off
    `amend()`'s own guards, the same way `STATUS_GUARDED_VERBS` records
    start/advance/resume/reopen's) crossed with `E.STATUS_VALUES`."""

    AMEND_OP_REQUIRED_STATUSES = {
        "drop": ("pending",),
        "rescope": ("pending",),
        "retext-check": ("pending", "in-progress"),
    }

    def _delta_for(self, op):
        if op == "drop":
            return {"ops": [{"op": "drop", "id": "g1"}]}
        if op == "rescope":
            return {"ops": [{"op": "rescope", "id": "g1", "title": "new title"}]}
        return {"ops": [{"op": "retext-check", "id": "g1", "which": "postconditions",
                         "cond": "c1", "command": PASS_COMMAND}]}

    def _fixture(self, status):
        g = gate("g1", status)
        g["postconditions"] = [{"id": "c1", "statement": "x",
                                 "check": {"kind": "command", "command": PASS_COMMAND},
                                 "satisfied": status == "complete"}]
        if status == "complete":
            g["evidence"] = [{"id": "e-g1-1", "type": "command-output",
                               "payload": {"cmd": PASS_COMMAND, "exit": 0, "shell": "posix"},
                               "produced_by": "engine", "ts": ""}]
            g["postconditions"][0]["satisfied_by"] = "e-g1-1"
        if status == "blocked":
            g["status_detail"] = {"prior_status": "pending"}
        return gated(g1=g)

    def test_generated_amend_grid_every_refusal_is_non_generic_or_honest(self):
        grid = [(status, op) for op in self.AMEND_OP_REQUIRED_STATUSES for status in E.STATUS_VALUES]
        expected_successes = sum(len(v) for v in self.AMEND_OP_REQUIRED_STATUSES.values())
        refused = 0
        for status, op in grid:
            cl = self._fixture(status)
            with tempfile.TemporaryDirectory() as d:
                f = Path(d) / "c.json"
                E.save(f, cl)
                delta = Path(d) / "delta.json"
                delta.write_text(json.dumps(self._delta_for(op)), encoding="utf-8")
                code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                             "--reason", "r", "--authority", "human"])
            if code == 0:
                self.assertIn(status, self.AMEND_OP_REQUIRED_STATUSES[op])
                continue
            self.assertIn("REFUSED:", err)
            refused += 1
            runnable = any(f"{tok} g1" in err for tok in
                           ("start", "advance", "resume", "reopen", "skip", "attest"))
            honest = "no verb reaches" in err
            self.assertTrue(runnable or honest,
                             f"generic amend refusal for (status={status!r}, op={op!r}): {err!r}")
        self.assertEqual(refused, len(grid) - expected_successes)


class RecoveryRunnabilityAudit(unittest.TestCase):
    """Reviewer ask #3 (g3-review rework 1): a general regression test that
    would have caught BOTH original defects -- for every branch
    `recovery_for()` can emit, actually invoke the command(s) it names
    against a tmp fixture in the originating state, and assert none of them
    raise `EngineError`. Where a branch is a genuine two-step recovery
    (resume/reopen, THEN retry the original op), both steps run in sequence
    against the SAME persisted file and the retry is asserted to SUCCEED,
    not just that the first step didn't raise. A branch that prints no
    command at all (the honest "no verb" statements) is asserted to name
    none of the runnable verbs, so a future edit can't quietly reintroduce a
    fabricated command there either."""

    def test_blocked_restorable_prior_resume_runs(self):
        g = gate("g1", "blocked", command=PASS_COMMAND)
        g["status_detail"] = {"prior_status": "pending"}
        cl = gated(g1=g)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("resume g1 --reason", err)
            code, out, err = _run_at(f, ["resume", "g1", "--reason", "cleared"])
            self.assertEqual(code, 0)

    def test_blocked_no_restorable_prior_only_skip_is_named_and_it_runs(self):
        cl = gated(g1=gate("g1", "blocked", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("skip g1 --reason", err)
            self.assertNotIn("reopen g1 --reason", err)
            self.assertNotIn("resume g1 --reason", err)
            code, out, err = _run_at(f, ["skip", "g1", "--reason", "why"])
            self.assertEqual(code, 0)

    def test_complete_reopen_runs(self):
        cl = gated(g1=gate("g1", "complete", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("reopen g1 --reason", err)
            code, out, err = _run_at(f, ["reopen", "g1", "--reason", "why"])
            self.assertEqual(code, 0)

    def test_skipped_status_names_no_runnable_command(self):
        cl = gated(g1=gate("g1", "skipped", command=PASS_COMMAND))
        code, out, err = _run_main(cl, ["start", "g1"])
        self.assertEqual(code, 1)
        for tok in ("start ", "advance ", "resume ", "reopen ", "attest "):
            self.assertNotIn(tok + "g1", err)

    def test_unmet_null_precondition_attest_then_start_runs(self):
        pre = [{"id": "p1", "statement": "x", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("attest g1 --cond p1 --which preconditions", err)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "p1",
                                         "--which", "preconditions", "--note", "n"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 0)

    def test_unmet_artifact_postcondition_attest_evidence_then_advance_runs(self):
        post = [{"id": "c1", "statement": "reviewed",
                 "check": {"kind": "artifact", "evidence_type": "review-result",
                           "match": {"verdict": "APPROVE"}}, "satisfied": False}]
        g = gate("g1", "in-progress")
        g["postconditions"] = post
        cl = gated(g1=g)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["advance", "g1", "--mechanical"])
            self.assertEqual(code, 1)
            self.assertIn("attest g1 --cond c1 --which postconditions", err)
            self.assertIn("--evidence", err)
            code, out, err = _run_at(f, ["attach", "g1", "--type", "review-result",
                                         "--field", "verdict=APPROVE"])
            self.assertEqual(code, 0)
            self.assertIn("attached e-g1-1", out)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "c1",
                                         "--which", "postconditions", "--evidence", "e-g1-1"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["advance", "g1", "--mechanical"])
            self.assertEqual(code, 0)

    def test_unmet_command_precondition_fix_and_retry_runs(self):
        pre = [{"id": "p1", "statement": "x",
                "check": {"kind": "command", "command": FAIL_COMMAND}, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn(
                "fix the underlying issue so precondition p1 passes, then retry start g1", err)
            # "Fix the underlying issue": the equivalent of a human fixing whatever
            # made the command fail -- rewrite the fixture's command to one that
            # now passes, then retry exactly the verb the recovery text names.
            data = E.load(f)
            data["tasks"]["g1"]["preconditions"][0]["check"]["command"] = PASS_COMMAND
            E.save(f, data)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 0)

    def test_unknown_cond_id_attest_with_a_real_id_runs(self):
        pre = [{"id": "p1", "statement": "a", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, preconds=pre))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "nope", "--which", "preconditions"])
            self.assertEqual(code, 1)
            self.assertIn("p1", err)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "p1",
                                         "--which", "preconditions", "--note", "n"])
            self.assertEqual(code, 0)

    def test_amend_drop_blocked_pending_prior_resume_then_retry_runs(self):
        g = gate("g1", "blocked", command=PASS_COMMAND)
        g["status_detail"] = {"prior_status": "pending"}
        cl = gated(g1=g)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "drop.json"
            delta.write_text(json.dumps({"ops": [{"op": "drop", "id": "g1"}]}), encoding="utf-8")
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 1)
            self.assertIn("resume g1 --reason", err)
            code, out, err = _run_at(f, ["resume", "g1", "--reason", "cleared"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 0)

    def test_amend_drop_in_progress_names_no_runnable_command(self):
        # in-progress has no verb that resets a gate back to 'pending' -- an
        # honest "no verb reaches" statement is correct, not a fabricated one.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "drop.json"
            delta.write_text(json.dumps({"ops": [{"op": "drop", "id": "g1"}]}), encoding="utf-8")
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 1)
            for tok in ("start ", "advance ", "resume ", "reopen ", "skip ", "attest "):
                self.assertNotIn(tok + "g1", err)

    def test_amend_retext_check_complete_reopen_then_retry_runs(self):
        post = [{"id": "c1", "statement": "tests pass",
                 "check": {"kind": "command", "command": PASS_COMMAND}, "satisfied": True,
                 "satisfied_by": "e-g1-1"}]
        g = gate("g1", "complete")
        g["postconditions"] = post
        g["evidence"] = [{"id": "e-g1-1", "type": "command-output",
                           "payload": {"cmd": PASS_COMMAND, "exit": 0, "shell": "posix"},
                           "produced_by": "engine", "ts": ""}]
        cl = gated(g1=g)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "retext.json"
            delta.write_text(json.dumps({"ops": [{"op": "retext-check", "id": "g1",
                                                   "which": "postconditions", "cond": "c1",
                                                   "command": PASS_COMMAND}]}), encoding="utf-8")
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 1)
            self.assertIn("reopen g1 --reason", err)
            code, out, err = _run_at(f, ["reopen", "g1", "--reason", "why"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 0)

    def test_amend_retext_check_blocked_in_progress_prior_resume_then_retry_runs(self):
        g = gate("g1", "blocked")
        g["postconditions"] = [{"id": "c1", "statement": "x",
                                 "check": {"kind": "command", "command": PASS_COMMAND},
                                 "satisfied": False}]
        g["status_detail"] = {"prior_status": "in-progress"}
        cl = gated(g1=g)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "retext.json"
            delta.write_text(json.dumps({"ops": [{"op": "retext-check", "id": "g1",
                                                   "which": "postconditions", "cond": "c1",
                                                   "command": PASS_COMMAND}]}), encoding="utf-8")
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 1)
            self.assertIn("resume g1 --reason", err)
            code, out, err = _run_at(f, ["resume", "g1", "--reason", "cleared"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 0)

    def test_amend_retext_check_skipped_names_no_runnable_command(self):
        g = gate("g1", "skipped")
        g["postconditions"] = [{"id": "c1", "statement": "x",
                                 "check": {"kind": "command", "command": PASS_COMMAND},
                                 "satisfied": False}]
        cl = gated(g1=g)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "retext.json"
            delta.write_text(json.dumps({"ops": [{"op": "retext-check", "id": "g1",
                                                   "which": "postconditions", "cond": "c1",
                                                   "command": PASS_COMMAND}]}), encoding="utf-8")
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 1)
            for tok in ("start ", "advance ", "resume ", "reopen ", "skip "):
                self.assertNotIn(tok + "g1", err)


class RecoveryActiveGatePosition(unittest.TestCase):
    """Reviewer BLOCK (g3-review rework 2): before this gate, `_next_verbs()`
    had exactly ONE caller (`state()`), always invoked on the checklist's own
    active gate. `recovery_for()` is the first caller to invoke it on an
    ARBITRARY refusing task -- which need not be active. `start()`, and only
    `start()`, additionally refuses a non-active gate on a GATED checklist, so
    the `pending` sub-case's bare "start {tid}" suggestion could itself
    refuse. Scope is precise: only `pending` (not `in-progress` --
    `advance`/`resume`/`reopen` carry no active-gate check), only `GATED`
    (`SURVEY` has no active-gate ordering at all)."""

    def _two_gate(self):
        g1 = gate("g1", "pending")  # stays active/incomplete throughout
        g2 = gate("g2", "pending")  # the refusing, non-active task
        return gated(g1=g1, g2=g2)

    def test_non_active_pending_recovery_does_not_suggest_start_and_names_active_gate(self):
        cl = self._two_gate()
        code, out, err = _run_main(cl, ["advance", "g2", "--mechanical"])
        self.assertEqual(code, 1)
        self.assertIn("REFUSED:", err)
        self.assertIn("not the active gate", err)
        self.assertIn("'g1'", err)
        self.assertIn("current", err)
        # The exact failure mode: must NOT hand back a `start g2` command,
        # since g2 is not the active gate and `start g2` would itself refuse.
        self.assertNotIn("start g2", err)
        self.assertIn("Do not edit the JSON — use the engine.", err)

    def test_non_active_pending_recovery_full_sequence_resolves_the_original_problem(self):
        # Full end-to-end proof, not just "the advice doesn't crash": follow
        # the recovery's own advice (run `current`, work the active gate)
        # and confirm the ORIGINAL attempted op eventually succeeds too --
        # not just that some other command happened not to raise.
        g1 = gate("g1", "pending", command=PASS_COMMAND)
        g2 = gate("g2", "pending")
        cl = gated(g1=g1, g2=g2)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["advance", "g2", "--mechanical"])
            self.assertEqual(code, 1)
            self.assertIn("not the active gate", err)
            self.assertIn("'g1'", err)
            # Run exactly what the recovery says: `current`.
            code, out, err = _run_at(f, ["current"])
            self.assertEqual(code, 0)
            self.assertIn("ACTIVE g1", out)
            self.assertIn("next: start g1", out)
            # Follow current's own (separately-proven-safe) hint through to
            # g1's completion.
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["advance", "g1", "--mechanical"])
            self.assertEqual(code, 0)
            # g2 is active now -- the ORIGINAL problem (advance g2) still
            # refuses (g2 itself hasn't been started), but for the RIGHT
            # reason, and start g2 -- refused a moment ago -- now succeeds.
            code, out, err = _run_at(f, ["start", "g2"])
            self.assertEqual(code, 0)

    def test_in_progress_non_active_task_has_no_equivalent_hole(self):
        # advance()/resume()/reopen() carry no active-gate check at all, so
        # an in-progress, non-active task's "advance {tid}" recovery
        # genuinely runs -- confirmed live, not just asserted from the
        # rework request's own claim.
        g1 = gate("g1", "in-progress", command=PASS_COMMAND)
        g2 = gate("g2", "in-progress", command=PASS_COMMAND)  # also in-progress; active_id(cl) is still g1
        cl = gated(g1=g1, g2=g2)
        self.assertEqual(E.active_id(cl), "g1")
        code, out, err = _run_main(cl, ["resume", "g2", "--reason", "x"])
        self.assertEqual(code, 1)  # resume refuses (g2 isn't blocked) -- unrelated to position
        self.assertIn("advance g2", err)
        code, out, err = _run_main(cl, ["advance", "g2", "--mechanical"])
        self.assertEqual(code, 0)


class RecoveryPositionAudit(unittest.TestCase):
    """Reviewer ask (g3-review rework 2), the load-bearing half: parameterize
    the recovery-family tests over ACTIVE vs NON-active position, not just
    status -- a single-task fixture makes the refusing task trivially always
    active by construction, so it structurally cannot exercise this axis
    (which is exactly how the position hole shipped unnoticed). Re-runs every
    OTHER refusal family against a NON-active version of its fixture and
    proves the named recovery command still runs clean -- confirming, by
    actually running them, that `resume`/`reopen`/`attest`/`skip`/`amend`
    genuinely have no active-gate dependency, rather than taking that on
    faith from source inspection alone."""

    def test_blocked_restorable_prior_resume_runs_when_non_active(self):
        g = gate("g1", "blocked", command=PASS_COMMAND)
        g["status_detail"] = {"prior_status": "pending"}
        cl = _make_non_active(gated(g1=g))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("resume g1 --reason", err)
            code, out, err = _run_at(f, ["resume", "g1", "--reason", "cleared"])
            self.assertEqual(code, 0)

    def test_blocked_no_restorable_prior_skip_runs_when_non_active(self):
        cl = _make_non_active(gated(g1=gate("g1", "blocked", command=PASS_COMMAND)))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("skip g1 --reason", err)
            code, out, err = _run_at(f, ["skip", "g1", "--reason", "why"])
            self.assertEqual(code, 0)

    def test_complete_reopen_runs_when_non_active(self):
        cl = _make_non_active(gated(g1=gate("g1", "complete", command=PASS_COMMAND)))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("reopen g1 --reason", err)
            code, out, err = _run_at(f, ["reopen", "g1", "--reason", "why"])
            self.assertEqual(code, 0)

    def test_unmet_precondition_recovery_is_unreachable_while_non_active(self):
        # start()'s active-gate check runs BEFORE its precondition-unmet
        # check, so a non-active task's unmet-precondition recovery can
        # never actually surface via `start` -- the position refusal fires
        # first and wins. This is itself the self-audit answer for this
        # branch: it needs no position-awareness of its own, because it is
        # structurally unreachable until position is already correct.
        # Confirmed by actually driving the sequence, not just asserted.
        pre = [{"id": "p1", "statement": "x", "check": None, "satisfied": False}]
        cl = _make_non_active(gated(g1=gate("g1", "pending", preconds=pre)))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("not the active gate", err)
            self.assertIn("'g0'", err)
            self.assertNotIn("attest g1", err)
            # Clear g0 out of the way; g1 becomes active, and ONLY THEN does
            # the precondition-unmet recovery appear and run clean.
            code, out, err = _run_at(f, ["skip", "g0", "--reason", "clear the way"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 1)
            self.assertIn("attest g1 --cond p1 --which preconditions", err)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "p1",
                                         "--which", "preconditions", "--note", "n"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["start", "g1"])
            self.assertEqual(code, 0)

    def test_unmet_postcondition_attest_runs_when_non_active(self):
        post = [{"id": "c1", "statement": "x", "check": None, "satisfied": False}]
        g = gate("g1", "in-progress")
        g["postconditions"] = post
        cl = _make_non_active(gated(g1=g))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["advance", "g1", "--mechanical"])
            self.assertEqual(code, 1)
            self.assertIn("attest g1 --cond c1 --which postconditions", err)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "c1",
                                         "--which", "postconditions", "--note", "n"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["advance", "g1", "--mechanical"])
            self.assertEqual(code, 0)

    def test_unknown_cond_id_attest_runs_when_non_active(self):
        pre = [{"id": "p1", "statement": "a", "check": None, "satisfied": False}]
        cl = _make_non_active(gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, preconds=pre)))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "nope", "--which", "preconditions"])
            self.assertEqual(code, 1)
            self.assertIn("p1", err)
            code, out, err = _run_at(f, ["attest", "g1", "--cond", "p1",
                                         "--which", "preconditions", "--note", "n"])
            self.assertEqual(code, 0)

    def test_amend_drop_blocked_pending_prior_resume_runs_when_non_active(self):
        g = gate("g1", "blocked", command=PASS_COMMAND)
        g["status_detail"] = {"prior_status": "pending"}
        cl = _make_non_active(gated(g1=g))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            delta = Path(d) / "drop.json"
            delta.write_text(json.dumps({"ops": [{"op": "drop", "id": "g1"}]}), encoding="utf-8")
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 1)
            self.assertIn("resume g1 --reason", err)
            code, out, err = _run_at(f, ["resume", "g1", "--reason", "cleared"])
            self.assertEqual(code, 0)
            code, out, err = _run_at(f, ["amend", "--delta", str(delta),
                                         "--reason", "r", "--authority", "human"])
            self.assertEqual(code, 0)


class Inv3StartNonActiveEnumeration(unittest.TestCase):
    """Finding 1 (g3-review rework 3 -> 4, the FOURTH instance of the same
    anti-pattern). `start()`'s own "not the active gate" guard
    (`checklist_engine.py` ~:1420) named an UNCONDITIONAL `start {active}`
    exit -- self-recovering only in the one case every prior fixture could
    express (`_make_non_active`'s guard hardcoded `status="pending"`), and
    silently wrong whenever the active gate was actually `in-progress` or
    `blocked` (both ordinary, reopen-cascade-reachable states). Fixed by
    wiring `task_id`/`verb`/`status="pending"` onto that raise (the refusing
    task IS always pending here -- the status!="pending" branch above it
    already returns otherwise), routing it into the SAME
    pending/GATED/non-active branch rework 3 already proved safe (never
    guesses a command for the active gate; points at `current`) -- no new
    branch, per the rework request's explicit instruction to reuse rather
    than parallel-write.

    Generated over `E.STATUS_VALUES` restricted to the statuses `active_id`
    can actually return (non-terminal: `pending`/`in-progress`/`blocked`),
    not hand-picked, so a future new status is not silently skipped."""

    ACTIVE_GATE_STATUSES = tuple(s for s in E.STATUS_VALUES if s not in E.TERMINAL)

    def test_active_statuses_are_exactly_the_non_terminal_ones(self):
        self.assertEqual(self.ACTIVE_GATE_STATUSES, ("pending", "in-progress", "blocked"))

    def test_generated_grid_never_names_a_refusing_command_for_the_active_gate(self):
        for active_status in self.ACTIVE_GATE_STATUSES:
            with self.subTest(active_status=active_status):
                cl = _make_non_active(gated(g1=gate("g1", "pending")), active_status=active_status)
                code, out, err = _run_main(cl, ["start", "g1"])
                self.assertEqual(code, 1)
                self.assertIn("REFUSED:", err)
                self.assertIn("not the active gate", err)
                self.assertIn("'g0'", err)
                self.assertIn("Recovery:", err)
                self.assertIn("current", err)
                # The exact failure mode this closes: must NOT hand back
                # "start g0" as if it always worked -- it only does when
                # active_status=='pending', and this message must not claim
                # otherwise for the other two.
                self.assertNotIn("start g0", err)
                self.assertIn("Do not edit the JSON — use the engine.", err)

    def test_generated_grid_the_named_advice_current_never_refuses(self):
        # Prove the recovery's own advice is unconditionally safe by
        # actually running it, for every active-gate status -- not assumed
        # from "current is read-only" alone.
        for active_status in self.ACTIVE_GATE_STATUSES:
            with self.subTest(active_status=active_status):
                cl = _make_non_active(gated(g1=gate("g1", "pending")), active_status=active_status)
                code, out, err = _run_main(cl, ["current"])
                self.assertEqual(code, 0)
                self.assertIn(f"ACTIVE g0 [{active_status}]", out)

    def test_reopen_cascade_reproduces_the_ordinary_reachability_path(self):
        # Reviewer's own reachability note: a reopen cascade leaves an
        # upstream gate active (in-progress) while resetting a downstream
        # gate to pending -- no synthetic fixture hacking required.
        g1 = gate("g1", "complete", command=PASS_COMMAND)
        g2 = gate("g2", "complete", command=PASS_COMMAND)
        cl = gated(g1=g1, g2=g2)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            code, out, err = _run_at(f, ["reopen", "g1", "--reason", "rework"])
            self.assertEqual(code, 0)
            reloaded = E.load(f)
            self.assertEqual(reloaded["tasks"]["g1"]["status"], "in-progress")
            self.assertEqual(reloaded["tasks"]["g2"]["status"], "pending")
            self.assertEqual(E.active_id(reloaded), "g1")
            code, out, err = _run_at(f, ["start", "g2"])
            self.assertEqual(code, 1)
            self.assertIn("not the active gate", err)
            self.assertIn("'g1'", err)
            self.assertIn("current", err)
            self.assertNotIn("start g1", err)


class WhyCapture(unittest.TestCase):
    """#179 Module 1 — the why-capture invariant: a non-exempt advance solicits a
    single running `why`, silence fails closed, the digest is the latest
    non-mechanical `why`, and a reopen freshens it."""

    def _two_open(self):
        # g1 in-progress (non-exempt), g2 pending (non-exempt): advancing g1 leaves
        # g2 as the active gate so `current` still has an ACTIVE line to carry DIGEST.
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def test_non_exempt_advance_without_why_is_refused(self):
        # Acceptance 1 (load-bearing): no why, no --mechanical -> REFUSED, fails closed.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        self.assertNotIn("why_trail", cl)  # nothing recorded on the refused path

    def test_exempt_gate_advances_with_no_why_prompt(self):
        # Acceptance 2: an explicitly exempt gate advances silently, records no why.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=True))
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")
        self.assertNotIn("why_trail", cl)

    def test_mechanical_discharges_and_is_not_the_digest(self):
        # Acceptance 3: --mechanical advances a non-exempt gate; the trail records a
        # mechanical marker but that entry never becomes the digest.
        cl = self._two_open()
        E.advance(cl, "g1", why="the real understanding")
        E.start(cl, "g2")
        self.assertEqual(E.advance(cl, "g2", mechanical=True), "g2 -> complete")
        trail = cl["why_trail"]
        mech = [e for e in trail if e.get("mechanical")]
        self.assertEqual(len(mech), 1)
        self.assertEqual(mech[0]["gate"], "g2")
        self.assertIsNone(mech[0]["why"])
        # digest is still the last *non-mechanical* why, not the mechanical marker
        self.assertEqual(E._digest(cl), "the real understanding")
        self.assertIn("DIGEST: the real understanding", E.current(cl))

    def test_latest_non_mechanical_why_is_the_digest_line(self):
        # Acceptance 4: the latest non-mechanical why is retrievable as DIGEST: via current.
        cl = self._two_open()
        E.advance(cl, "g1", why="first understanding")
        # g2 is now active; DIGEST rides the ACTIVE line
        out = E.current(cl)
        self.assertIn("ACTIVE g2", out)
        self.assertIn("DIGEST: first understanding", out)
        # a second non-mechanical why supersedes it as the latest
        E.start(cl, "g2")
        E.advance(cl, "g2", why="second understanding")
        self.assertEqual(E._digest(cl), "second understanding")
        self.assertIn("DIGEST: second understanding", E.current(cl))

    def test_reopen_freshens_digest(self):
        # Acceptance 5: after a reopen, the reopened gate's understanding stops being
        # the digest (the superseded understanding is no longer "latest").
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        E.advance(cl, "g1", why="stale understanding")
        self.assertEqual(E._digest(cl), "stale understanding")
        E.reopen(cl, "g1", "needs rework")
        # the reopen appended a marker (append-only); the prior why-record is intact
        self.assertTrue(any(e.get("reopen") for e in cl["why_trail"]))
        self.assertEqual(cl["why_trail"][0]["why"], "stale understanding")
        # but it is no longer the live digest
        self.assertIsNone(E._digest(cl))
        self.assertNotIn("DIGEST:", E.current(cl))
        # re-advancing with a fresh why restores a live digest
        E.advance(cl, "g1", why="fresh understanding")
        self.assertEqual(E._digest(cl), "fresh understanding")

    def test_reopen_cascade_freshens_downstream_why(self):
        # A cascade reopen resets downstream gates; their why must be freshened too.
        cl = gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
        )
        E.advance(cl, "g1", why="g1 understanding")
        E.start(cl, "g2")
        E.advance(cl, "g2", why="g2 understanding")
        self.assertEqual(E._digest(cl), "g2 understanding")
        # reopen g1 cascades to g2; both understandings are now stale
        E.reopen(cl, "g1", "upstream rework")
        self.assertEqual(cl["tasks"]["g2"]["status"], "pending")
        self.assertIsNone(E._digest(cl))

    def test_mechanical_takes_precedence_when_both_given(self):
        # --mechanical is a distinct discharge flag: passing it records a mechanical
        # marker even if a --why string is also present (crisp, predictable).
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        E.advance(cl, "g1", why="ignored", mechanical=True)
        self.assertTrue(cl["why_trail"][-1]["mechanical"])
        self.assertIsNone(cl["why_trail"][-1]["why"])

    def test_blank_why_still_fails_closed(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1", why="   ")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")

    def test_postconditions_checked_before_why(self):
        # A failing postcondition yields the postcondition refusal, not the why prompt
        # (no buying past unfinished work).
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND, why_exempt=False))
        with self.assertRaises(E.EngineError) as ctx:
            E.advance(cl, "g1")  # no why supplied, but postcondition fails first
        self.assertIn("postconditions unmet", str(ctx.exception))
        self.assertNotIn("why_trail", cl)

    def test_why_trail_is_append_only_across_advances(self):
        cl = self._two_open()
        E.advance(cl, "g1", why="one")
        first = copy.deepcopy(cl["why_trail"][0])
        E.start(cl, "g2")
        E.advance(cl, "g2", why="two")
        # the earlier record is byte-identical (never mutated); a new one was appended
        self.assertEqual(cl["why_trail"][0], first)
        self.assertEqual([e["id"] for e in cl["why_trail"]], ["w-1", "w-2"])

    def test_cli_non_exempt_refused_then_advances_with_why(self):
        # Through main(): a why-less advance REFUSES cleanly (exit 1, no crash) and
        # persists no completion; with --why it succeeds and creates the why_trail.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 1)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "in-progress")
            self.assertEqual(
                E.main(["--file", str(f), "advance", "g1", "--why", "understood the seam"]), 0)
            reloaded = E.load(f)
            self.assertEqual(reloaded["tasks"]["g1"]["status"], "complete")
            self.assertEqual(reloaded["why_trail"][-1]["why"], "understood the seam")

    def test_cli_mechanical_flag_advances(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "advance", "g1", "--mechanical"]), 0)
            self.assertTrue(E.load(f)["why_trail"][-1]["mechanical"])


class WhyCaptureBackwardCompat(unittest.TestCase):
    """Pre-ruling: the new engine must drive existing-shape spines (NO `why_trail`
    key, NO `why_exempt` on tasks) — missing why_exempt => not exempt; a why-less
    advance REFUSES cleanly (never throws); why_trail is created on first write."""

    def test_existing_shape_non_exempt_refused_then_passes_with_why(self):
        raw = gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=None)
        self.assertNotIn("why_exempt", raw)  # genuinely legacy-shaped task
        cl = gated(g1=raw)
        self.assertNotIn("why_trail", cl)    # genuinely legacy-shaped spine
        # missing why_exempt is treated as NOT exempt -> refused, fails closed
        with self.assertRaises(E.EngineError):
            E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        # ... then passes with a why, and why_trail is created on first write
        self.assertEqual(E.advance(cl, "g1", why="post-hoc understanding"), "g1 -> complete")
        self.assertIn("why_trail", cl)
        self.assertEqual(cl["why_trail"][-1]["why"], "post-hoc understanding")

    def test_existing_shape_exempt_task_advances_silently(self):
        # An existing-shape spine that opts a task OUT (why_exempt: true) advances with
        # no why prompt and records nothing.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=True))
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete")
        self.assertNotIn("why_trail", cl)

    def test_cli_legacy_spine_refuses_cleanly_never_crashes(self):
        # The clean-refusal guarantee through the CLI boundary: exit 1 (REFUSED),
        # not an uncaught exception, and the spine is left drivable.
        raw = gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=None)
        cl = gated(g1=raw)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = E.main(["--file", str(f), "advance", "g1"])
            self.assertEqual(rc, 1)
            self.assertIn("REFUSED:", err.getvalue())
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "in-progress")


class RefreshPrimitives(unittest.TestCase):
    """#179 Module 4 — the refresh PRIMITIVES only (flow wiring is #183): a
    `refresh-request` evidence type carried by the ordinary `attach` verb, the pure
    `has_pending_refresh_request` predicate, and a `REFRESH REQUESTED:` line on
    `current`."""

    def _one_active_after_advance(self):
        cl = gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
        )
        E.advance(cl, "g1", why="upstream understanding")  # g2 becomes active
        return cl

    def test_refresh_request_round_trip(self):
        # Acceptance 6: attach a refresh-request; predicate true + current shows the
        # line. Absent one: false + no line.
        cl = self._one_active_after_advance()
        # absent: predicate false, no line
        self.assertFalse(E.has_pending_refresh_request(cl, "g2"))
        self.assertNotIn("REFRESH REQUESTED", E.current(cl))
        # attach a refresh-request (pointers only) against the active gate g2
        why_ref = cl["why_trail"][-1]["id"]
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": why_ref})
        payload = cl["tasks"]["g2"]["evidence"][-1]["payload"]
        self.assertNotIn("lease_claimed_at", payload)  # unleased legacy attach
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))
        out = E.current(cl)
        self.assertIn("REFRESH REQUESTED:", out)
        self.assertIn(why_ref, out)  # the why_ref pointer surfaces on the line

    def test_claimed_refresh_request_records_and_matches_the_active_claim(self):
        cl = self._one_active_after_advance()
        with mock.patch.object(E, "_now", return_value="2026-08-20T10:00:00+00:00"):
            E.claim(cl, "agent-1", "implementer", ".", {})
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        payload = cl["tasks"]["g2"]["evidence"][-1]["payload"]
        self.assertEqual(payload["lease_claimed_at"], "2026-08-20T10:00:00+00:00")
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))

    def test_same_session_reclaim_consumes_the_earlier_refresh_request(self):
        cl = self._one_active_after_advance()
        with mock.patch.object(E, "_now", return_value="2026-08-20T10:00:00+00:00"):
            E.claim(cl, "agent-1", "implementer", ".", {})
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))
        self.assertIn("REFRESH REQUESTED:", E.current(cl))

        with mock.patch.object(E, "_now", return_value="2026-08-20T10:01:00+00:00"):
            E.claim(cl, "agent-1", "implementer", ".", {})

        self.assertFalse(E.has_pending_refresh_request(cl, "g2"))
        self.assertNotIn("REFRESH REQUESTED:", E.current(cl))

    def test_legacy_unstamped_refresh_request_keeps_pending_behavior(self):
        cl = self._one_active_after_advance()
        E.claim(cl, "agent-1", "implementer", ".", {})
        cl["tasks"]["g2"]["evidence"].append({
            "id": "legacy-refresh",
            "type": "refresh-request",
            "payload": {"seam": "g2", "why_ref": "w-1"},
            "produced_by": "engine",
            "ts": "",
        })
        E.claim(cl, "agent-1", "implementer", ".", {})
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))

    def test_cli_successor_claim_consumes_request_before_first_current(self):
        cl = self._one_active_after_advance()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            claim = ["--file", str(f), "claim", "--session-id", "agent-1",
                     "--claimed-by", "implementer", "--worktree", "."]
            self.assertEqual(E.main(claim), 0)
            self.assertEqual(
                E.main(["--file", str(f), "attach", "g2", "--type", "refresh-request",
                        "--field", "seam=g2", "--field", "why_ref=w-1",
                        "--session-id", "agent-1"]), 0)
            attached = E.load(f)["tasks"]["g2"]["evidence"][-1]
            self.assertEqual(
                attached["payload"]["lease_claimed_at"],
                E.load(f)["engine_session"]["claimed_at"],
            )

            import contextlib, io
            before = io.StringIO()
            with contextlib.redirect_stdout(before):
                self.assertEqual(E.main(["--file", str(f), "current"]), 0)
            self.assertIn("REFRESH REQUESTED:", before.getvalue())

            self.assertEqual(E.main(claim), 0)
            successor = io.StringIO()
            with contextlib.redirect_stdout(successor):
                self.assertEqual(E.main(["--file", str(f), "current"]), 0)
            self.assertNotIn("REFRESH REQUESTED:", successor.getvalue())

    def test_refresh_request_is_seam_specific(self):
        cl = self._one_active_after_advance()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))
        self.assertFalse(E.has_pending_refresh_request(cl, "g1"))  # different seam

    def test_superseded_refresh_request_is_not_pending(self):
        # The reopen cascade supersedes evidence; a superseded refresh-request must
        # stop counting as pending (the predicate honors the supersession marker).
        cl = self._one_active_after_advance()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        ev = cl["tasks"]["g2"]["evidence"][-1]
        ev["superseded"] = {"by": "reopen:g1", "reason": "x", "ts": "t"}
        self.assertFalse(E.has_pending_refresh_request(cl, "g2"))

    def test_predicate_is_pure_no_mutation(self):
        cl = self._one_active_after_advance()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        before = copy.deepcopy(cl)
        E.has_pending_refresh_request(cl, "g2")
        E.has_pending_refresh_request(cl, "g1")
        self.assertEqual(cl, before)  # no side effects

    def test_predicate_on_legacy_spine_no_refresh_type(self):
        # A spine that never attached a refresh-request: predicate false, no crash.
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        self.assertFalse(E.has_pending_refresh_request(cl, "g1"))

    def test_cli_attach_refresh_request_then_current_shows_line(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            self.assertEqual(
                E.main(["--file", str(f), "attach", "g1", "--type", "refresh-request",
                        "--field", "seam=g1", "--field", "why_ref=w-1"]), 0)
            import contextlib, io
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(E.main(["--file", str(f), "current"]), 0)
            self.assertIn("REFRESH REQUESTED:", out.getvalue())


class SurveyWhySuffixReachUp(unittest.TestCase):
    """#189 — `_why_suffix` is extended to surveys so a survey role (reviewer) can
    cold-start from `current` alone. A survey never accumulates a `why_trail`, so no
    `DIGEST:` line appears — only the `REFRESH REQUESTED:` line, the reach-up target."""

    def test_survey_shows_no_refresh_line_before_attach(self):
        sv = survey(v1=survey_item("v1", "in-progress"))
        out = E.current(sv)
        self.assertNotIn("REFRESH REQUESTED", out)
        self.assertNotIn("DIGEST:", out)

    def test_survey_refresh_request_renders_on_current(self):
        sv = survey(v1=survey_item("v1", "in-progress"))
        self.assertNotIn("REFRESH REQUESTED", E.current(sv))
        # predicate already worked on surveys; only the display was gated-only.
        E.attach(sv, "v1", "refresh-request", {"seam": "v1", "why_ref": "w-1"})
        self.assertTrue(E.has_pending_refresh_request(sv, "v1"))
        out = E.current(sv)
        self.assertIn("REFRESH REQUESTED:", out)
        self.assertIn("v1", out)  # the active item/seam names the line
        # a survey has no why_trail -> no live digest -> no DIGEST line
        self.assertNotIn("DIGEST:", out)

    def test_survey_all_visited_renders_no_suffix(self):
        # aid is None (all items visited) -> no refresh line, no crash.
        sv = survey(v1=survey_item("v1", "complete"))
        out = E.current(sv)
        self.assertNotIn("REFRESH REQUESTED", out)
        self.assertNotIn("DIGEST:", out)


import types
from datetime import datetime, timedelta, timezone


def _reading(fill, model="claude-opus-4-8"):
    """A fresh, well-formed gauge Reading with the given fill — constructed
    directly so band-structure tests are decoupled from the reader's file I/O
    and clock. `observed_at` is aware `now` (the field is unused by the policy)."""
    return E._gauge_reader.Reading(
        schema_version=1, fill_fraction=fill, model=model,
        observed_at=datetime.now(timezone.utc),
    )


def _advance_ns(iid="g1", why=None, mechanical=False):
    return types.SimpleNamespace(
        verb="advance", id=iid, why=why,
        mechanical=mechanical, session_id=None,
    )


def _start_ns(iid="g1"):
    return types.SimpleNamespace(verb="start", id=iid, session_id=None)


def _reopen_ns(iid="g1", reason="rework"):
    return types.SimpleNamespace(verb="reopen", id=iid, reason=reason, session_id=None)


def _resume_ns(iid="g1", reason="blocker resolved", note=None):
    return types.SimpleNamespace(verb="resume", id=iid, reason=reason, note=note,
                                 session_id=None)


def _refresh_requests_anywhere(cl):
    """Every `refresh-request` evidence item in the WHOLE checklist, superseded or
    not — the load-bearing precondition of the permanent DC2 guard below. With one
    of these present the HARD guard lifts, so the guarded advance succeeds on BOTH
    sides of #467 and the test would prove nothing."""
    return [ev for t in cl.get("tasks", {}).values()
            for ev in (t.get("evidence") or [])
            if isinstance(ev, dict) and ev.get("type") == "refresh-request"]


def _without_override_ledger(cl):
    """#467: a refused BEGIN now makes exactly ONE state change — `_trip_hard_gate`
    appends an `override_ledger` entry recording the attempt before it raises. Every
    other no-mutation property the guards below assert (no status flip, no manifest,
    no liveness stamp, no evidence) still holds exactly as it did, so those guards
    compare with the ledger lifted out — and each one asserts the ledger's OWN
    expected growth separately, so lifting it out cannot hide a regression."""
    out = copy.deepcopy(cl)
    out.pop("override_ledger", None)
    return out


class TripTwoBandGatePolicy(unittest.TestCase):
    """#182 Module 3 — the Trip two-band gate policy. Thresholds are model-keyed
    via #181's `thresholds_for`; NUMBERS are deferred to first-run calibration, so
    every assertion is structural — pinned to the ACTUAL (soft, hard) the table
    returns, never to a hardcoded 0.75/0.90. Both bands are exercised through the
    `dispatch` CLI boundary (where the policy actually rides), with the gauge read
    patched to a controlled Reading. Real-file wiring is covered separately below."""

    def setUp(self):
        # The table ships empty (every model -> DEFAULT_THRESHOLDS); read the pair
        # the policy will actually see rather than assuming the numbers.
        self.soft, self.hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        # gates are why_exempt so a clean advance needs no --why: this isolates the
        # Trip bands from #179's why-capture. HARD is checked BEFORE the verb, so
        # exemption never lets a HARD-tripped advance through.
        self.cl = gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=True),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=True),
        )

    # --- SOFT band (advisory, on `current`) --------------------------------- #
    def test_soft_fires_at_and_above_soft(self):
        # Acceptance 1: SOFT fires at/above soft. At exactly soft, and above it.
        for fill in (self.soft, (self.soft + self.hard) / 2):
            with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
                out = E.dispatch(self.cl, types.SimpleNamespace(verb="current"),
                                 base_dir=Path("."))
            self.assertIn("CONTEXT", out)
            self.assertIn(">= soft", out)

    def test_soft_never_below_soft(self):
        # Acceptance 1 (falsifiable half): below soft -> no advisory at all.
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.soft - 0.01)):
            out = E.dispatch(self.cl, types.SimpleNamespace(verb="current"),
                             base_dir=Path("."))
        self.assertNotIn("CONTEXT", out)

    def test_soft_never_forces_advance(self):
        # Acceptance 3/4 (falsifiable: does SOFT ever force? -> NO): in the SOFT
        # band `advance` still succeeds; SOFT is advisory only.
        fill = (self.soft + self.hard) / 2  # strictly between soft and hard
        with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
            msg = E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertIn("g1 -> complete", msg)
        self.assertEqual(self.cl["tasks"]["g1"]["status"], "complete")

    # --- HARD band (refusal, on `advance`) ---------------------------------- #
    def test_hard_refuses_begin_work_at_and_above_hard_without_refresh(self):
        # Acceptance 2/4 (falsifiable: does HARD ever let you pass without a
        # refresh-request? -> NO). RE-AIMED by #467: the verb HARD refuses is the one
        # that BEGINS work at a gate (`start`), never the one that closes the gate the
        # agent is already inside. At/above hard with no refresh-request, `start`
        # REFUSES and the gate stays pending.
        for fill in (self.hard, min(self.hard + 0.05, 1.0)):
            cl = copy.deepcopy(self.cl)
            E.advance(cl, "g1")  # close g1 normally; g2 is now the next PENDING gate
            with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
                with self.assertRaises(E.EngineError) as ctx:
                    E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
            self.assertEqual(cl["tasks"]["g2"]["status"], "pending")
            self.assertIn("refresh", str(ctx.exception).lower())
            self.assertIn("attach g2 --type refresh-request", str(ctx.exception))

    def test_hard_never_refuses_below_hard(self):
        # Acceptance 2: just below hard, HARD does not fire — advance passes.
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard - 0.001)):
            msg = E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertIn("g1 -> complete", msg)

    def test_hard_handoff_close_needs_a_why_even_with_a_refresh_request_pending(self):
        # RE-AIMED by #467. Before: "HARD forces UNTIL a refresh-request exists, then
        # advance passes" — which no longer says anything, since HARD never refuses an
        # advance at all now. The live question in its place is whether a pending
        # refresh-request buys SILENCE at the close. It must not: the request is a
        # pointer for the next agent, not a substitute for the understanding this one
        # owes. The gate is why_exempt, so this also pins that the exemption stays
        # suspended at hard even on the already-requested path.
        E.attach(self.cl, "g1", "refresh-request", {"seam": "g1", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
            self.assertEqual(self.cl["tasks"]["g1"]["status"], "in-progress")
            msg = E.dispatch(self.cl, _advance_ns("g1", why="handing off at g1"),
                             base_dir=Path("."))
        self.assertIn("g1 -> complete", msg)
        self.assertEqual(self.cl["tasks"]["g1"]["status"], "complete")
        self.assertEqual(E._digest(self.cl), "handing off at g1")

    def test_hard_refusal_leaves_state_unmutated(self):
        # A HARD refusal is raised BEFORE the verb runs: no status flip, no manifest,
        # no liveness stamp. RE-AIMED by #467 from `advance` to `start` — same
        # ordering property, asserted on the verb HARD now guards.
        E.advance(self.cl, "g1")
        before = copy.deepcopy(self.cl)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(self.cl, _start_ns("g2"), base_dir=Path("."))
        self.assertEqual(_without_override_ledger(self.cl), _without_override_ledger(before))
        # ...and the one mutation a refusal DOES make (#467): the recorded begin.
        self.assertEqual([e["id"] for e in E._override_entries(self.cl, kind="trip")], ["ov-1"])
        self.assertEqual(E._override_entries(self.cl, kind="trip")[0]["outcome"], "begin-refused")

    def test_hard_advisory_on_current_points_at_attach(self):
        # On the read-only `current`, the HARD band still escalates to the exact
        # remedy (the attach command). RE-AIMED by #467: the "BLOCKED" assertion had
        # to go, because the advisory no longer claims `advance` is blocked — it is
        # not, and saying so was the instruction defect behind #431. In its place the
        # advisory states a changed instruction. This fixture's gates are why_exempt
        # and carry no why_trail, so it also pins the `<why-id>` fallback for a
        # checklist with no live understanding to name.
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            out = E.dispatch(self.cl, types.SimpleNamespace(verb="current"),
                             base_dir=Path("."))
        self.assertIn(">= hard", out)
        self.assertIn("your instruction has changed", out)
        self.assertIn("attach g1 --type refresh-request --field seam=g1 "
                      "--field why_ref=<why-id>", out)
        self.assertNotIn("BLOCKED", out)

    # --- missing/stale reading (None) --------------------------------------- #
    def test_none_reading_never_forces_and_gives_no_advice(self):
        # Acceptance 3: a missing/stale reading (None) -> no advice on current, and
        # never forces a handoff (advance passes).
        with mock.patch.object(E, "_read_gauge", return_value=None):
            out = E.dispatch(self.cl, types.SimpleNamespace(verb="current"),
                             base_dir=Path("."))
            self.assertNotIn("CONTEXT", out)
            msg = E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertIn("g1 -> complete", msg)

    def test_survey_checklist_gets_no_trip_policy(self):
        # Trip is gated-only; a survey never sees an advisory (and has no advance).
        sv = survey(v1=survey_item("v1", "in-progress"))
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            out = E.dispatch(sv, types.SimpleNamespace(verb="current"), base_dir=Path("."))
        self.assertNotIn("CONTEXT", out)

    def test_unresolvable_work_id_no_base_dir_no_reading(self):
        # No base_dir -> the gauge location is unresolvable -> no reading, no advice,
        # never forces (the real _read_gauge/_gauge_path returns None on base_dir None).
        self.assertIsNone(E._gauge_path(self.cl, None))
        self.assertIsNone(E._read_gauge(self.cl, None))
        self.assertEqual(E._trip_advisory(self.cl, None), "")
        E._trip_hard_gate(self.cl, "g1", None)  # no raise


class RefreshRequestIdentity(unittest.TestCase):
    """#190 — `has_pending_refresh_request` gains an optional `why_ref` identity
    filter (default = existing gate-only), and the HARD-band callers key on the
    current-digest why-record so a distinct new trip cannot ride a stale request's
    coattails through HARD."""

    def _g2_active(self):
        # g1 advanced (why -> w-1); g2 is now the active gate, latest why = w-1.
        cl = gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
        )
        E.advance(cl, "g1", why="u1")
        return cl

    def test_predicate_identity_filter(self):
        cl = self._g2_active()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        # default (gate-only) form: any pending request for the gate
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))
        # identity form: matches only the request keyed to the given why-record
        self.assertTrue(E.has_pending_refresh_request(cl, "g2", why_ref="w-1"))
        self.assertFalse(E.has_pending_refresh_request(cl, "g2", why_ref="w-2"))

    def test_identity_filter_stays_pure(self):
        cl = self._g2_active()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        before = copy.deepcopy(cl)
        E.has_pending_refresh_request(cl, "g2", why_ref="w-2")
        self.assertEqual(cl, before)  # no side effects with the new param

    def test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases(self):
        # A STALE refresh-request (keyed to an earlier understanding) must NOT wave a
        # distinct new trip through HARD; a FRESH request keyed to the current digest
        # releases it. RE-AIMED by #467 from `advance` to `start`: #190's identity
        # check is unchanged, it just now defends the BEGIN-work boundary.
        _, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        cl = gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )
        E.advance(cl, "g1", why="u1")                 # -> w-1
        E.start(cl, "g2"); E.advance(cl, "g2", why="u2")  # -> w-2; g3 pending, latest why w-2
        # stale request keyed to w-1 (an earlier trip's understanding)
        E.attach(cl, "g3", "refresh-request", {"seam": "g3", "why_ref": "w-1"})
        ns = _start_ns("g3")
        before = copy.deepcopy(cl)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, ns, base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g3"]["status"], "pending")  # unmutated
        self.assertEqual(_without_override_ledger(cl), _without_override_ledger(before))
        self.assertEqual([e["id"] for e in E._override_entries(cl, kind="trip")], ["ov-1"])  # #467
        self.assertEqual(E._override_entries(cl, kind="trip")[0]["outcome"], "begin-refused")
        # a FRESH request keyed to the current digest (w-2) releases HARD
        E.attach(cl, "g3", "refresh-request", {"seam": "g3", "why_ref": "w-2"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(hard)):
            msg = E.dispatch(cl, ns, base_dir=Path("."))
        self.assertIn("g3 -> in-progress", msg)
        self.assertEqual(cl["tasks"]["g3"]["status"], "in-progress")


class TripHardGuardsBeginNotClose(unittest.TestCase):
    """#467 — the HARD band moves off the verb that CLOSES a gate and onto the two
    verbs that BEGIN work at one (`start`, `reopen`).

    Closing the gate you are already inside IS the handoff, so it is never refused
    for being over the line. What IS refused is beginning new work you cannot
    finish, and closing a gate SILENTLY — a mechanical or why-less close records no
    understanding, so `_latest_why_record` skips it and the next agent cold-starts
    from a pre-trip digest, which is #431 reproduced after the fix.

    `resume` is deliberately NOT guarded: it restores a BLOCKED gate to the status
    it held before, which for an `in-progress` prior returns the agent to the gate
    it is already mid-way through — the "closing your own gate" case this design
    promises never to refuse.

    Every test name here matches the frozen `g2-integrate` closeout selector
    (`trip_begin`, `begin_work`, `handoff`). pytest exits 5 on an empty collection,
    so these names are load-bearing, not cosmetic."""

    # The exact refusal raised when a gate would be closed with NOTHING recorded
    # while the gauge is at/over hard. Asserted by equality, never by substring.
    NO_SILENT_CLOSE = (
        "g1: context is at/over the hard limit, so this gate cannot be closed "
        "silently — a mechanical or why-less close records no understanding, and "
        "the next agent would cold-start from a digest written before your work. "
        "Closing the gate is NOT refused; only the silence is. Run: "
        "advance g1 --why \"<understanding>\""
    )

    def setUp(self):
        self.soft, self.hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        self.over_hard = min(self.hard + 0.05, 1.0)

    def _three_gates(self, why_exempt=False):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=why_exempt),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=why_exempt),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=why_exempt),
        )

    def _g2_pending_after_g1(self):
        """g1 advanced with a real understanding (-> w-1); g2 is the next PENDING
        gate, so `start g2` is a genuine BEGIN-work move and the live why-record
        the identity check keys on is w-1."""
        cl = self._three_gates()
        E.advance(cl, "g1", why="u1")
        return cl

    # --- THE PERMANENT DC2 GUARD -------------------------------------------- #
    def test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest(self):
        """The permanent regression guard against the #431 deadlock returning.

        Pinned at `fill >= hard` with NO refresh-request anywhere in the spine —
        exactly the condition under which the pre-#467 engine REFUSED. It asserts
        BOTH halves: the advance completes, AND the digest becomes the
        understanding written AT this gate. If this fixture ever acquires a pending
        refresh-request, the guard lifts, the advance passes on both sides of the
        change, and this test silently stops guarding anything."""
        cl = self._three_gates()
        self.assertEqual(_refresh_requests_anywhere(cl), [])
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            # the two properties this test's value depends on, asserted in place
            self.assertGreaterEqual(E._read_gauge(Path(".")).fill_fraction, self.hard)
            msg = E.dispatch(
                cl, _advance_ns("g1", why="handed off at g1: HARD now guards the begin verbs"),
                base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 -> complete"), msg)
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        self.assertEqual(E._digest(cl), "handed off at g1: HARD now guards the begin verbs")
        self.assertEqual(_refresh_requests_anywhere(cl), [])

    def test_handoff_digest_names_the_understanding_written_at_the_tripping_gate(self):
        """#431's actual observable (DC3): after the handoff-carrying close, the
        digest names the understanding written AT the tripping gate, not the one
        from the gate before it."""
        cl = self._three_gates()
        E.advance(cl, "g1", why="pre-trip understanding")
        E.start(cl, "g2")
        self.assertEqual(E._digest(cl), "pre-trip understanding")
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            msg = E.dispatch(cl, _advance_ns("g2", why="at-g2 handoff understanding"),
                             base_dir=Path("."))
        self.assertTrue(msg.endswith("g2 -> complete"), msg)
        self.assertEqual(E._digest(cl), "at-g2 handoff understanding")

    # --- BEGIN-work verbs ARE guarded --------------------------------------- #
    def test_trip_begin_start_refused_at_and_above_hard_without_refresh(self):
        for fill in (self.hard, self.over_hard):
            cl = self._g2_pending_after_g1()
            before = copy.deepcopy(cl)
            with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
                with self.assertRaises(E.EngineError) as ctx:
                    E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
            self.assertEqual(cl["tasks"]["g2"]["status"], "pending")
            # refused BEFORE any gate mutation or liveness stamp; the ONE state change
            # a refusal now makes is the #467 ledger entry, asserted on its own.
            self.assertEqual(_without_override_ledger(cl), _without_override_ledger(before))
            self.assertEqual([e["id"] for e in E._override_entries(cl, kind="trip")], ["ov-1"])
            self.assertEqual(E._override_entries(cl, kind="trip")[0]["outcome"], "begin-refused")
            self.assertEqual(E._override_entries(cl, kind="trip")[0]["verb"], "start")
            self.assertIn("attach g2 --type refresh-request", str(ctx.exception))

    def test_trip_begin_reopen_refused_at_hard_without_refresh(self):
        cl = self._g2_pending_after_g1()  # g1 is complete
        before = copy.deepcopy(cl)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError) as ctx:
                E.dispatch(cl, _reopen_ns("g1", reason="rework"), base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        self.assertEqual(_without_override_ledger(cl), _without_override_ledger(before))
        self.assertEqual([e["id"] for e in E._override_entries(cl, kind="trip")], ["ov-1"])  # #467
        self.assertEqual(E._override_entries(cl, kind="trip")[0]["verb"], "reopen")
        self.assertIn("attach g1 --type refresh-request", str(ctx.exception))

    def test_trip_begin_start_released_by_a_matching_refresh_request(self):
        cl = self._g2_pending_after_g1()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            msg = E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertTrue(msg.endswith("g2 -> in-progress"), msg)
        self.assertEqual(cl["tasks"]["g2"]["status"], "in-progress")

    def test_claimed_refresh_releases_hard_until_a_later_claim_consumes_it(self):
        cl = self._g2_pending_after_g1()
        with mock.patch.object(E, "_now", return_value="2026-08-20T10:00:00+00:00"):
            E.claim(cl, "agent-1", "implementer", ".", {})
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})

        released = copy.deepcopy(cl)
        released_start = _start_ns("g2")
        released_start.session_id = "agent-1"
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            msg = E.dispatch(released, released_start, base_dir=Path("."))
        self.assertTrue(msg.endswith("g2 -> in-progress"), msg)

        with mock.patch.object(E, "_now", return_value="2026-08-20T10:01:00+00:00"):
            E.claim(cl, "agent-1", "implementer", ".", {})
        consumed_start = _start_ns("g2")
        consumed_start.session_id = "agent-1"
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, consumed_start, base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g2"]["status"], "pending")

    def test_trip_begin_stale_why_ref_does_not_release_begin_work(self):
        """#190's identity check, preserved verbatim at the new guard sites: a
        request keyed to an EARLIER understanding does not wave a new trip through."""
        cl = self._g2_pending_after_g1()  # live why-record is w-1
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-99"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g2"]["status"], "pending")
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            msg = E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertTrue(msg.endswith("g2 -> in-progress"), msg)

    def test_trip_begin_start_allowed_just_below_hard(self):
        cl = self._g2_pending_after_g1()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard - 0.001)):
            msg = E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertTrue(msg.endswith("g2 -> in-progress"), msg)

    # --- `resume` is NOT guarded (specific exclusion) ----------------------- #
    def test_trip_begin_resume_is_not_guarded_at_hard(self):
        """`resume` returns a BLOCKED gate to its pre-block status. For an
        `in-progress` prior that hands the agent back the gate it is already inside
        — the case this design promises never to refuse."""
        cl = self._three_gates()
        E.block(cl, "g1", "needs a ruling", "human", "ask")
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            msg = E.dispatch(cl, _resume_ns("g1", reason="ruling arrived"), base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 resumed -> in-progress (blocker resolved: ruling arrived)"), msg)
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")

    # --- closing SILENTLY is refused (the other half of #431) --------------- #
    def test_handoff_mechanical_close_refused_at_hard(self):
        """`--mechanical` records no understanding, so `_latest_why_record` skips it
        and the next agent cold-starts from a pre-trip digest — #431 reproduced after
        the fix. At/over hard the mechanical close is refused by name."""
        cl = self._three_gates()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError) as ctx:
                E.dispatch(cl, _advance_ns("g1", mechanical=True), base_dir=Path("."))
        self.assertEqual(str(ctx.exception), self.NO_SILENT_CLOSE)
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
        self.assertEqual(cl.get("why_trail", []), [])  # nothing recorded, nothing skipped

    def test_handoff_why_exempt_is_suspended_at_hard(self):
        """A `why_exempt` gate normally closes silently. At/over hard the exemption is
        SUSPENDED — and suspended means the understanding is actually RECORDED, not
        merely demanded: a --why that the engine accepted but never wrote to the
        why_trail would leave the digest just as stale."""
        cl = self._three_gates(why_exempt=True)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError) as ctx:
                E.dispatch(cl, _advance_ns("g1"), base_dir=Path("."))
            self.assertEqual(str(ctx.exception), self.NO_SILENT_CLOSE)
            self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
            msg = E.dispatch(cl, _advance_ns("g1", why="exempt gate, closed with an understanding"),
                             base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 -> complete"), msg)
        self.assertEqual(E._digest(cl), "exempt gate, closed with an understanding")

    def test_handoff_mechanical_close_still_allowed_below_hard(self):
        """The falsifiable half: below hard nothing changes — a mechanical close is
        still a legitimate marker for a step that carries no new understanding."""
        cl = self._three_gates()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard - 0.001)):
            msg = E.dispatch(cl, _advance_ns("g1", mechanical=True), base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 -> complete"), msg)
        self.assertTrue(cl["why_trail"][-1]["mechanical"])

    def test_handoff_no_silent_close_never_fires_on_a_none_reading(self):
        """Fail-safe: a missing/stale reading must not conjure a why requirement out
        of a gate that is exempt, any more than it conjures a refusal."""
        cl = self._three_gates(why_exempt=True)
        with mock.patch.object(E, "_read_gauge", return_value=None):
            msg = E.dispatch(cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 -> complete"), msg)

    def test_handoff_unmet_postconditions_still_refuse_before_the_why_demand(self):
        """Ordering preserved: you cannot be asked for a handoff understanding as a
        way of buying past unfinished work — a failing postcondition still yields the
        postcondition refusal, even at/over hard."""
        cl = gated(g1=gate("g1", "in-progress", command=FAIL_COMMAND, why_exempt=False))
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError) as ctx:
                E.dispatch(cl, _advance_ns("g1", mechanical=True), base_dir=Path("."))
        self.assertEqual(str(ctx.exception), "g1: postconditions unmet ['c1']")

    # --- fail-safe: the guard no-ops where it always has -------------------- #
    def test_trip_begin_none_reading_never_refuses_begin_work(self):
        cl = self._g2_pending_after_g1()
        with mock.patch.object(E, "_read_gauge", return_value=None):
            self.assertTrue(E.dispatch(cl, _start_ns("g2"), base_dir=Path(".")).endswith("g2 -> in-progress"))
            msg = E.dispatch(cl, _reopen_ns("g1", reason="r"), base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 reopened (rework 1/3); cascade-reset downstream "
                                     "['g2'] (evidence superseded, retained)"), msg)
        self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")

    def test_trip_begin_survey_never_refuses_begin_work(self):
        sv = survey(v1=survey_item("v1", "pending"))
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            msg = E.dispatch(sv, _start_ns("v1"), base_dir=Path("."))
        self.assertTrue(msg.endswith("v1 -> in-progress"), msg)

    # --- what the agent is TOLD (the #431 observable) ----------------------- #
    def _hard_advisory(self, cl, fill):
        with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
            return E._trip_advisory(cl, Path("."))

    def test_handoff_hard_advisory_reads_as_a_changed_instruction(self):
        """#431 is an instruction-conformance defect, so the fix is verified on what
        the agent is TOLD. At HARD on a pending gate the advisory must state the
        legal sequence — request refresh, begin the guarded gate, then advance with
        a handoff — and never read as an alarm about being unsafe or blocked."""
        cl = self._g2_pending_after_g1()  # g2 active/pending, live why-record w-1
        out = self._hard_advisory(cl, self.over_hard)
        self.assertEqual(out, (
            f"\nCONTEXT {self.over_hard:.0%} (>= hard): your instruction has changed. "
            f"First request a refresh with: attach g2 --type refresh-request --field "
            f"seam=g2 --field why_ref=w-1; then begin THIS guarded gate (`start g2`); "
            f"then close it carrying your handoff (`advance g2 --why \"<understanding>\"`) "
            f"and stop. A fresh agent picks up from your DIGEST; do not begin work at "
            f"another gate."
        ))
        for alarm in ("BLOCKED", "unsafe", "runaway", "lost"):
            self.assertNotIn(alarm, out)

    def test_handoff_pending_hard_refresh_start_advance_preserves_digest_on_successor_current(self):
        """The pending-HARD remedy is executable in the stated order, and its
        handoff remains visible to the successor through `current`."""
        cl = self._g2_pending_after_g1()
        handoff = "g2: completed under the fresh refresh request"
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            self.assertTrue(E.dispatch(cl, _start_ns("g2"), base_dir=Path(".")).endswith(
                "g2 -> in-progress"))
            self.assertTrue(E.dispatch(cl, _advance_ns("g2", why=handoff), base_dir=Path(".")).endswith(
                "g2 -> complete"))
        self.assertEqual(cl["tasks"]["g3"]["status"], "pending")
        self.assertEqual(E._digest(cl), handoff)
        self.assertIn(f"DIGEST: {handoff}", E.current(cl))

    def test_handoff_hard_advisory_with_refresh_already_requested_reads_as_an_instruction(self):
        cl = self._g2_pending_after_g1()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        out = self._hard_advisory(cl, self.over_hard)
        self.assertEqual(out, (
            f"\nCONTEXT {self.over_hard:.0%} (>= hard): your instruction has changed, "
            f"and the refresh for g2 is already requested. Now begin THIS guarded gate "
            f"(`start g2`), then close it carrying your handoff (`advance g2 --why "
            f"\"<understanding>\"`) and stop. A fresh agent picks up from your DIGEST; "
            f"do not begin work at another gate."
        ))
        for alarm in ("BLOCKED", "unsafe", "runaway", "lost"):
            self.assertNotIn(alarm, out)

    def test_handoff_hard_advisory_rides_current_at_the_cli_boundary(self):
        """The advisory reaches the agent through the read-only `current`, unchanged
        by the rail prefix — `current` itself stays pure."""
        cl = self._g2_pending_after_g1()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            out = E.dispatch(cl, types.SimpleNamespace(verb="current"), base_dir=Path("."))
        self.assertTrue(out.endswith(self._hard_advisory(cl, self.over_hard)), out)

    def test_handoff_refresh_hint_carries_the_concrete_why_id(self):
        """The literal `<why-id>` placeholder cost four separate agents a silent
        no-op: `attach ... --field why_ref=<why-id>` exits 0 and records a request
        that matches no understanding, so the identity check never releases. The hint
        must emit the real id, and fall back to the placeholder only when there is no
        live why-record to name."""
        self.assertEqual(
            E._refresh_attach_hint("g2", "w-7"),
            "attach g2 --type refresh-request --field seam=g2 --field why_ref=w-7")
        self.assertNotIn("<why-id>", E._refresh_attach_hint("g2", "w-7"))
        self.assertEqual(
            E._refresh_attach_hint("g2", None),
            "attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>")

    def test_trip_begin_refusal_names_the_concrete_why_id(self):
        cl = self._g2_pending_after_g1()  # live why-record is w-1
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError) as ctx:
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertIn("--field why_ref=w-1", str(ctx.exception))
        self.assertNotIn("<why-id>", str(ctx.exception))

    def test_trip_begin_no_base_dir_never_refuses_begin_work(self):
        cl = self._g2_pending_after_g1()
        E._trip_hard_gate(cl, "g2", None)  # no raise: unresolvable gauge location
        self.assertTrue(E.dispatch(cl, _start_ns("g2"), base_dir=None).endswith("g2 -> in-progress"))


class GateHeadroomOverrideResolverTests(unittest.TestCase):
    """#467 (b): ONE resolver for the per-gate context-headroom reserve, read from
    `tasks.<gate>.context_headroom_tokens` and NOWHERE else. There is deliberately
    no checklist-config tier: it would have zero users, and one adapter is a
    hypothetical seam, not a real one. A missing, malformed, or negative value
    resolves to 0 -- the shipped default, which no gate may lower."""

    def _cl(self, **overrides):
        cl = gated(g1=gate("g1", "in-progress"), g2=gate("g2", "pending"))
        for iid, value in overrides.items():
            cl["tasks"][iid]["context_headroom_tokens"] = value
        return cl

    def test_wellformed_headroom_override_is_read_from_its_own_gate_only(self):
        cl = self._cl(g1=30_000)
        self.assertEqual(E._gate_headroom_tokens(cl, "g1"), 30_000)
        # The neighbour declares nothing, so it reserves nothing. A per-gate knob
        # that leaked onto its siblings would not be per-gate.
        self.assertEqual(E._gate_headroom_tokens(cl, "g2"), 0)
        # No gate named / no such gate -> 0, so the resolver is total.
        self.assertEqual(E._gate_headroom_tokens(cl, None), 0)
        self.assertEqual(E._gate_headroom_tokens(cl, "no-such-gate"), 0)

    def test_no_checklist_config_tier_supplies_a_headroom_override(self):
        # decision:no-config-tier -- gate-level ONLY. A value parked at the
        # checklist root or in `config` must be invisible to the resolver, so a
        # run-wide reserve cannot be smuggled in behind the per-gate one.
        cl = self._cl()
        cl["context_headroom_tokens"] = 30_000
        cl["config"]["context_headroom_tokens"] = 30_000
        self.assertEqual(E._gate_headroom_tokens(cl, "g1"), 0)
        self.assertEqual(E._gate_headroom_tokens(cl, "g2"), 0)

    def test_malformed_or_negative_headroom_override_resolves_to_the_default_but_a_wellformed_one_does_not(self):
        """BOTH halves, in ONE test, through the SAME resolver -- deliberately.

        A test asserting only that a malformed value resolves to the default
        CANNOT FAIL: resolving to the default is exactly what a missing feature
        does, so it passes with the whole mechanism dead-coded. The positive
        control below is what makes the negative half mean anything."""
        malformed = ("30000", None, True, False, 1.5, float("nan"), [], {}, object())
        for value in malformed:
            with self.subTest(value=repr(value)):
                cl = self._cl(g1=value)
                self.assertEqual(E._gate_headroom_tokens(cl, "g1"), 0)
        for value in (-1, -30_000, -10 ** 12):
            with self.subTest(value=value):
                cl = self._cl(g1=value)
                self.assertEqual(E._gate_headroom_tokens(cl, "g1"), 0)
        # POSITIVE CONTROL, same resolver, same fixture shape: a well-formed
        # override resolves to a DIFFERENT number than the default it falls back
        # to above. Without this assertion every line above would still pass
        # against a resolver that always returned 0.
        cl = self._cl(g1=30_000)
        self.assertEqual(E._gate_headroom_tokens(cl, "g1"), 30_000)
        self.assertNotEqual(E._gate_headroom_tokens(cl, "g1"), 0)


class GateHeadroomOverrideTripTests(unittest.TestCase):
    """#467 (c)+(d): the resolved reserve reaches BOTH the number the agent is SHOWN
    (`_trip_advisory`) and the number it is JUDGED against (`_trip_hard_band_reading`,
    which backs the begin-work guard and the no-silent-close rule), so the two can
    never diverge.

    Every assertion below runs at ONE fill on ONE model, and names BOTH sides: the
    overridden gate's behaviour changes AND the neighbour's does not. Proving only
    that the overridden gate trips earlier would be satisfied by giving every gate
    an override, which is precisely the failure this pins against.

    Numbers are INDEPENDENT literals for claude-opus-5 (1M window, 80K soft, 150K
    hard), never read back off the profile table -- that would be circular."""

    GATE = "execute"          # the overridden gate: the run's longest
    NEIGHBOUR = "reconcile"   # the named neighbour: declares nothing, reserves nothing
    MODEL = "claude-opus-5"
    RESERVE = 50_000
    DEFAULT_SOFT, DEFAULT_HARD = 0.08, 0.15        # 80_000/1M, 150_000/1M
    OVERRIDDEN_SOFT, OVERRIDDEN_HARD = 0.03, 0.10  # (80_000-50_000)/1M, (150_000-50_000)/1M
    FILL = 0.12  # ONE fill, strictly between OVERRIDDEN_HARD and DEFAULT_HARD

    def setUp(self):
        # Pin the band arithmetic this fixture depends on, so a later profile edit
        # breaks HERE with a clear reason rather than quietly making every
        # assertion below vacuous.
        self.assertEqual(E._gauge_reader.thresholds_for(self.MODEL),
                         (self.DEFAULT_SOFT, self.DEFAULT_HARD))
        self.assertEqual(E._gauge_reader.thresholds_for(self.MODEL, self.RESERVE),
                         (self.OVERRIDDEN_SOFT, self.OVERRIDDEN_HARD))
        self.assertLess(self.OVERRIDDEN_HARD, self.FILL)
        self.assertLess(self.FILL, self.DEFAULT_HARD)

    def _cl(self, reserve=RESERVE, execute_status="in-progress"):
        # PASS_COMMAND postconditions so `advance` is legal (a gated gate needs at
        # least one); why_exempt (gate()'s default) so a clean close needs no --why,
        # which is what makes the no-silent-close assertion below discriminating.
        cl = gated(execute=gate(self.GATE, execute_status, command=PASS_COMMAND),
                   reconcile=gate(self.NEIGHBOUR, "pending", command=PASS_COMMAND))
        if reserve is not None:
            cl["tasks"][self.GATE]["context_headroom_tokens"] = reserve
        return cl

    def _gauge(self, fill=FILL):
        return mock.patch.object(E, "_read_gauge",
                                 return_value=_reading(fill, self.MODEL))

    # --- DC4: the overridden gate changes AND the neighbour does not -------- #
    def test_headroom_override_trips_its_own_gate_and_not_its_neighbour(self):
        """The binding condition. SAME checklist, SAME fill, SAME model, both sides
        named: `execute` (reserve 50K) is at/over hard and refuses to be begun,
        while `reconcile` (no reserve) is nowhere near hard and begins freely."""
        cl = self._cl()
        with self._gauge():
            with self.assertRaises(E.EngineError) as ctx:
                E._trip_hard_gate(cl, self.GATE, Path("."))
            # ... and the neighbour, at that same 12%, is not refused at all.
            self.assertIsNone(E._trip_hard_gate(cl, self.NEIGHBOUR, Path(".")))
            # The band decision itself, read straight from the single place that
            # makes it: a Reading for the overridden gate, None for the neighbour.
            self.assertIsNotNone(E._trip_hard_band_reading(cl, Path("."), self.GATE))
            self.assertIsNone(E._trip_hard_band_reading(cl, Path("."), self.NEIGHBOUR))
        self.assertIn("12% is at/over the hard limit", str(ctx.exception))

    def test_headroom_override_neighbour_is_unaffected_through_the_cli_boundary(self):
        """The same both-sides discrimination end to end through `dispatch`, where
        the guard actually rides: `start execute` REFUSES and leaves the gate
        pending, `start reconcile` succeeds -- one fill, one model."""
        cl = self._cl(execute_status="pending")
        with self._gauge():
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns(self.GATE), base_dir=Path("."))
            self.assertEqual(cl["tasks"][self.GATE]["status"], "pending")
            # Advance past the overridden gate so the neighbour is the active one,
            # then begin it at the SAME 12% fill: it opens normally.
            neighbour_cl = copy.deepcopy(cl)
            neighbour_cl["tasks"][self.GATE]["status"] = "complete"
            msg = E.dispatch(neighbour_cl, _start_ns(self.NEIGHBOUR), base_dir=Path("."))
        self.assertTrue(msg.endswith(f"{self.NEIGHBOUR} -> in-progress"), msg)

    def test_headroom_override_changes_the_advisory_for_its_gate_only(self):
        """What the agent is SHOWN, both sides named at one fill: active `execute`
        reads the HARD instruction; active `reconcile` reads the ordinary SOFT
        advisory and never the hard one."""
        cl = self._cl()
        with self._gauge():
            overridden = E._trip_advisory(cl, Path("."))
            neighbour_cl = copy.deepcopy(cl)
            neighbour_cl["tasks"][self.GATE]["status"] = "complete"
            neighbour = E._trip_advisory(neighbour_cl, Path("."))
        self.assertIn(">= hard", overridden)
        self.assertIn("your instruction has changed", overridden)
        self.assertIn(f"advance {self.GATE}", overridden)
        # The neighbour at the SAME 12%: above its own soft (8%), nowhere near its
        # own hard (15%) -- i.e. exactly what it says with no override in play.
        self.assertIn(">= soft", neighbour)
        self.assertNotIn(">= hard", neighbour)

    def test_headroom_override_neighbour_advisory_is_byte_identical_to_no_override(self):
        """Stronger form of the not-its-neighbours half: the neighbour's advisory
        with an override on `execute` is EXACTLY the text it has when no override
        exists anywhere. Not merely 'still soft' -- unchanged."""
        with_override = self._cl()
        with_override["tasks"][self.GATE]["status"] = "complete"
        without_override = self._cl(reserve=None)
        without_override["tasks"][self.GATE]["status"] = "complete"
        with self._gauge():
            self.assertEqual(E._trip_advisory(with_override, Path(".")),
                             E._trip_advisory(without_override, Path(".")))
            # And the overridden gate's own advisory is NOT what it would be
            # without the override -- so the equality above is discrimination,
            # not a mechanism that does nothing.
            self.assertNotEqual(E._trip_advisory(self._cl(), Path(".")),
                                E._trip_advisory(self._cl(reserve=None), Path(".")))

    # --- (c): shown number and judged number cannot diverge ----------------- #
    def test_headroom_override_moves_the_advisory_and_the_guard_together(self):
        """DEMONSTRATED, not asserted: sweep the whole fill range against several
        reserves and require the advisory's HARD branch and the begin-work guard's
        refusal to agree on EVERY sample. If the two ever read different resolved
        numbers, some sample in the sweep separates them."""
        seen = set()
        for reserve in (0, 20_000, 50_000, 79_999, 140_000):
            for fill in (0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.0999, 0.10,
                         0.12, 0.1499, 0.15, 0.30, 1.0):
                cl = self._cl(reserve=reserve)
                with self.subTest(reserve=reserve, fill=fill):
                    with self._gauge(fill):
                        advisory_says_hard = ">= hard" in E._trip_advisory(cl, Path("."))
                        try:
                            E._trip_hard_gate(cl, self.GATE, Path("."))
                            guard_refuses = False
                        except E.EngineError:
                            guard_refuses = True
                    self.assertEqual(advisory_says_hard, guard_refuses)
                    seen.add(advisory_says_hard)
        # The sweep must actually cross the line in both directions, or the
        # equality above would hold vacuously.
        self.assertEqual(seen, {True, False})

    def test_headroom_override_also_governs_the_no_silent_close_rule(self):
        """The third consumer of the same resolved number (g2's no-silent-close
        rule, which rides `_trip_hard_band_reading` through `advance`'s
        `require_why`): at 12% the overridden gate may not close in silence, while
        the neighbour -- why_exempt, same fill, same model -- still may."""
        cl = self._cl()
        with self._gauge():
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _advance_ns(self.GATE), base_dir=Path("."))
            self.assertEqual(cl["tasks"][self.GATE]["status"], "in-progress")
            msg = E.dispatch(cl, _advance_ns(self.GATE, why="handing off at execute"),
                             base_dir=Path("."))
            self.assertIn(f"{self.GATE} -> complete", msg)
            # The named neighbour at the same fill closes silently, as it always has.
            E.dispatch(cl, _start_ns(self.NEIGHBOUR), base_dir=Path("."))
            msg = E.dispatch(cl, _advance_ns(self.NEIGHBOUR), base_dir=Path("."))
        self.assertIn(f"{self.NEIGHBOUR} -> complete", msg)

    def test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate(self):
        """B-1 (g3 rework 2, mutation M15). The no-silent-close rule's band decision
        must be read for the gate NAMED in the `advance`, never for whatever
        `active_id()` reports -- M15's declared-EQUIVALENT reasoning claimed those
        two are always the same gate. They are not: `block()` carries no status
        guard and `blocked` is not in `TERMINAL`, so `active_id()` can sit BEHIND a
        later in-progress gate. Reached through public verbs only -- start/advance/
        start/block/advance -- the same sequence the reviewer reproduced at the
        CLI: g1 (no override) is advanced to complete, then BLOCKED (legal --
        block() has no status guard); g2 (carrying the override) is started while
        g1 is still open and is left in-progress. `active_id(cl)` then reports g1,
        even though the gate being CLOSED is g2."""
        cl = gated(
            g1=gate("g1", "pending", command=PASS_COMMAND, why_exempt=True),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=True),
        )
        cl["tasks"]["g2"]["context_headroom_tokens"] = self.RESERVE
        # Low fill while g1 is opened/closed and g2 is opened, so neither begin-work
        # guard (start is TRIP_HARD_GUARDED) refuses -- the fill rises to FILL (12%)
        # only AFTER g2 is already under way, exactly as the CLI reproduction did.
        with self._gauge(fill=0.0):
            E.dispatch(cl, _start_ns("g1"), base_dir=Path("."))
            E.dispatch(cl, _advance_ns("g1"), base_dir=Path("."))
            E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        with self._gauge():  # FILL=0.12: over g2's overridden hard, under g1's default hard
            E.dispatch(cl, types.SimpleNamespace(
                verb="block", id="g1", blocker="upstream authority", authority="human",
                next_action="wait", session_id=None,
            ), base_dir=Path("."))
            self.assertEqual(cl["tasks"]["g1"]["status"], "blocked")
            # The divergence M15 declared unreachable: the ACTIVE gate is g1, but
            # the gate being CLOSED below is g2.
            self.assertEqual(E.active_id(cl), "g1")
            with self.assertRaises(E.EngineError) as ctx:
                E.dispatch(cl, _advance_ns("g2", mechanical=True), base_dir=Path("."))
            self.assertEqual(cl["tasks"]["g2"]["status"], "in-progress")
        self.assertIn("cannot be closed silently", str(ctx.exception))

    def test_headroom_override_defaults_to_the_active_gates_reserve(self):
        """Asked without a gate, the band decision falls back to the ACTIVE gate --
        the same gate `_trip_advisory` reports on, which is what keeps the shown
        number and the judged number identical. Failing OPEN here (resolving to no
        reserve when the caller names no gate) would silently drop an expensive
        gate's protection, so the default is fail-tight, not fail-open."""
        cl = self._cl()  # `execute` is active AND carries the reserve
        with self._gauge():
            self.assertIsNotNone(E._trip_hard_band_reading(cl, Path(".")))
            # ... and with no override anywhere, the same call at the same fill is
            # below hard -- so the line above is the reserve talking, not the fill.
            self.assertIsNone(E._trip_hard_band_reading(self._cl(reserve=None), Path(".")))

    def test_shipped_spine_template_carries_exactly_one_headroom_override(self):
        """(d) exercised for real, against the SHIPPED template rather than a
        fixture: the commander spine's `execute` gate -- the run's longest, and the
        one whose imperative already tells the agent in prose to ensure context
        headroom before entering -- carries a reserve, and NO other gate does.

        The "no other gate" half is the load-bearing one: handing every gate an
        override would invent a table of ungraded placeholders and destroy the
        per-gate meaning of the knob. The reserve is read here through the REAL
        resolver, so the authored number and the number the governor uses cannot
        drift apart."""
        spine = json.loads((ROOT / "skills" / "commander" / "templates"
                            / "COMMANDER_SPINE.template.json").read_text(encoding="utf-8"))
        carriers = [iid for iid, t in spine["tasks"].items()
                    if "context_headroom_tokens" in t]
        self.assertEqual(carriers, ["execute"])
        reserve = E._gate_headroom_tokens(spine, "execute")
        self.assertGreater(reserve, 0)
        self.assertEqual(reserve, spine["tasks"]["execute"]["context_headroom_tokens"])
        # Every other gate keeps the shipped default, named explicitly.
        for iid in ("plan", "reconcile", "review", "archive"):
            self.assertEqual(E._gate_headroom_tokens(spine, iid), 0)
        # The value is a documented guess, not a bare magic number: the reasoning
        # lives next to it so a later run can revise it in one obvious place.
        self.assertIn("GUESS", spine["tasks"]["execute"]["context_headroom_note"])

    # --- fail-safe: an override never manufactures a trip ------------------- #
    def test_headroom_override_never_trips_without_a_reading(self):
        """A reserve is a tightening of a reading, never a substitute for one: with
        no gauge reading, an overridden gate is as ungoverned as any other."""
        cl = self._cl()
        with mock.patch.object(E, "_read_gauge", return_value=None):
            self.assertEqual(E._trip_advisory(cl, Path(".")), "")
            self.assertIsNone(E._trip_hard_gate(cl, self.GATE, Path(".")))
            self.assertIsNone(E._trip_hard_band_reading(cl, Path("."), self.GATE))


class FormatAgeTests(unittest.TestCase):
    """_format_age: whole seconds/minutes/hours, pure arithmetic + string
    formatting -- the unit boundaries (60s, 3600s) are unit conversion, never
    a threshold judgment this function makes (constraint:no-threshold-values)."""

    def test_seconds(self):
        self.assertEqual(E._format_age(timedelta(seconds=45)), "45s")

    def test_zero(self):
        self.assertEqual(E._format_age(timedelta(seconds=0)), "0s")

    def test_minutes(self):
        self.assertEqual(E._format_age(timedelta(minutes=26, seconds=3)), "26m03s")

    def test_just_under_an_hour(self):
        self.assertEqual(E._format_age(timedelta(minutes=59, seconds=59)), "59m59s")

    def test_hours(self):
        self.assertEqual(E._format_age(timedelta(hours=2, minutes=5)), "2h05m")

    def test_exactly_one_hour(self):
        self.assertEqual(E._format_age(timedelta(hours=1)), "1h00m")

    def test_negative_delta_clamps_to_zero(self):
        # A future observed_at (clock skew) must never render a negative age.
        self.assertEqual(E._format_age(timedelta(seconds=-30)), "0s")

    def test_fractional_seconds_truncate_to_whole_seconds(self):
        self.assertEqual(E._format_age(timedelta(seconds=1.9)), "1s")


class SkipReasonAdvisoryTests(unittest.TestCase):
    """_skip_reason_advisory reads a REAL gauge-skip.json sidecar (same real-
    file convention as TripRealGaugeFileWiring below) and renders it."""

    def _write_skip(self, d, reason, observed_at, candidate_count=None):
        record = {"schema_version": 1, "reason": reason, "observed_at": observed_at}
        if candidate_count is not None:
            record["candidate_count"] = candidate_count
        (Path(d) / E._gauge_reader.SKIP_FILENAME).write_text(json.dumps(record), encoding="utf-8")

    def test_no_sidecar_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(E._skip_reason_advisory(Path(d) / "gauge.json"), "")

    def test_none_gauge_path_returns_empty(self):
        self.assertEqual(E._skip_reason_advisory(None), "")

    def test_ambiguous_binding_message(self):
        with tempfile.TemporaryDirectory() as d:
            self._write_skip(d, "ambiguous-binding", datetime.now(timezone.utc).isoformat(), candidate_count=2)
            out = E._skip_reason_advisory(Path(d) / "gauge.json")
        self.assertIn("CONTEXT", out)
        self.assertIn("2 candidate spines", out)

    def test_no_usable_record_message(self):
        with tempfile.TemporaryDirectory() as d:
            self._write_skip(d, "no-usable-record", datetime.now(timezone.utc).isoformat())
            out = E._skip_reason_advisory(Path(d) / "gauge.json")
        self.assertIn("CONTEXT", out)
        self.assertIn("no usable usage record", out)

    def test_unknown_reason_gets_a_generic_fallback_not_silence(self):
        with tempfile.TemporaryDirectory() as d:
            self._write_skip(d, "some-future-reason", datetime.now(timezone.utc).isoformat())
            out = E._skip_reason_advisory(Path(d) / "gauge.json")
        self.assertIn("CONTEXT", out)
        self.assertIn("some-future-reason", out)

    def test_corrupt_sidecar_never_raises_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / E._gauge_reader.SKIP_FILENAME).write_text("{not json", encoding="utf-8")
            self.assertEqual(E._skip_reason_advisory(Path(d) / "gauge.json"), "")

    def test_skip_reason_raising_is_swallowed(self):
        with tempfile.TemporaryDirectory() as d:
            gauge_path = Path(d) / "gauge.json"
            with mock.patch.object(E._gauge_reader, "skip_reason", side_effect=RuntimeError("boom")):
                self.assertEqual(E._skip_reason_advisory(gauge_path), "")


class StaleRecordAdvisoryTests(unittest.TestCase):
    """_stale_record_advisory reports a REAL gauge.json's own raw facts, with
    no staleness/skew/calibration gate of its own (raw_record's contract)."""

    def _write_gauge(self, d, record):
        (Path(d) / "gauge.json").write_text(json.dumps(record), encoding="utf-8")

    def test_no_gauge_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(E._stale_record_advisory(Path(d) / "gauge.json"), "")

    def test_none_gauge_path_returns_empty(self):
        self.assertEqual(E._stale_record_advisory(None), "")

    def test_stale_record_reports_raw_facts_no_threshold_language(self):
        with tempfile.TemporaryDirectory() as d:
            stale = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
            self._write_gauge(d, {"schema_version": 1, "fill_fraction": 0.33,
                                   "model": "claude-opus-4-8", "observed_at": stale})
            out = E._stale_record_advisory(Path(d) / "gauge.json")
        self.assertIn("CONTEXT", out)
        self.assertIn("33%", out)
        self.assertIn("claude-opus-4-8", out)
        self.assertNotIn(">= soft", out)
        self.assertNotIn(">= hard", out)

    def test_uncalibrated_model_record_also_reported_raw(self):
        # raw_record has no calibration gate -- an uncalibrated model's own
        # gauge.json (which read() also rejects) is still reported raw here.
        with tempfile.TemporaryDirectory() as d:
            self._write_gauge(d, {"schema_version": 1, "fill_fraction": 0.5,
                                   "model": "claude-future-9",
                                   "observed_at": datetime.now(timezone.utc).isoformat()})
            out = E._stale_record_advisory(Path(d) / "gauge.json")
        self.assertIn("claude-future-9", out)

    def test_corrupt_file_never_raises(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "gauge.json").write_text("{not json", encoding="utf-8")
            self.assertEqual(E._stale_record_advisory(Path(d) / "gauge.json"), "")

    def test_raw_record_raising_is_swallowed(self):
        with tempfile.TemporaryDirectory() as d:
            gauge_path = Path(d) / "gauge.json"
            with mock.patch.object(E._gauge_reader, "raw_record", side_effect=RuntimeError("boom")):
                self.assertEqual(E._stale_record_advisory(gauge_path), "")


class NoReadingAdvisoryDispatchTests(unittest.TestCase):
    """_no_reading_advisory tries each localizable cause in order and returns
    the FIRST non-empty result -- the sub-advisories are mocked directly
    (band-structure style) since this is testing DISPATCH ORDER, not any one
    advisory's own text.

    The checklist passed in is leaseless, so it names no owner and the #600
    owner-mismatch branch ahead of these three cannot fire -- these cases keep
    testing exactly the order they always tested. The mismatch branch's own
    priority is pinned by test_owner_mismatch_advisory_outranks_the_others."""

    def test_uncalibrated_wins_over_skip_and_stale(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value="\nCONTEXT GAUGE OFF: x"), \
             mock.patch.object(E, "_skip_reason_advisory", return_value="\nCONTEXT GAUGE SILENT: skip"), \
             mock.patch.object(E, "_stale_record_advisory", return_value="\nCONTEXT GAUGE SILENT: stale"):
            self.assertEqual(E._no_reading_advisory({}, Path(".")), "\nCONTEXT GAUGE OFF: x")

    def test_skip_reason_wins_over_stale_when_uncalibrated_empty(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value=""), \
             mock.patch.object(E, "_skip_reason_advisory", return_value="\nCONTEXT GAUGE SILENT: skip"), \
             mock.patch.object(E, "_stale_record_advisory", return_value="\nCONTEXT GAUGE SILENT: stale"):
            self.assertEqual(E._no_reading_advisory({}, Path(".")), "\nCONTEXT GAUGE SILENT: skip")

    def test_stale_record_is_the_last_resort(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value=""), \
             mock.patch.object(E, "_skip_reason_advisory", return_value=""), \
             mock.patch.object(E, "_stale_record_advisory", return_value="\nCONTEXT GAUGE SILENT: stale"):
            self.assertEqual(E._no_reading_advisory({}, Path(".")), "\nCONTEXT GAUGE SILENT: stale")

    def test_all_empty_yields_empty(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value=""), \
             mock.patch.object(E, "_skip_reason_advisory", return_value=""), \
             mock.patch.object(E, "_stale_record_advisory", return_value=""):
            self.assertEqual(E._no_reading_advisory({}, Path(".")), "")


class TripRealGaugeFileWiring(unittest.TestCase):
    """#182 — end-to-end through `main()` with a REAL gauge.json written where
    #180's writer drops it (a SIBLING of the spine: `base_dir/gauge.json`), read by
    #181's real `read()`. Proves the path pairing and the reader wiring, not just
    the band logic. Fresh fill >= hard refuses; a stale/absent gauge never forces."""

    def _write_gauge(self, d, fill, observed_at):
        (Path(d) / "gauge.json").write_text(json.dumps({
            "schema_version": 1, "fill_fraction": fill,
            "model": "claude-opus-4-8", "observed_at": observed_at,
        }), encoding="utf-8")

    def _spine(self):
        # why_exempt so advance needs no --why; HARD is orthogonal to why-capture.
        return gated(g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=True))

    def test_fresh_hard_gauge_sibling_of_spine_refuses_begin_work_then_passes_with_refresh(self):
        # RE-AIMED by #467 from `advance` to `start`: same real-file wiring proof,
        # asserted on the verb HARD now guards. Beginning work at a pending gate over
        # the line is refused end-to-end through main(), and a refresh-request releases it.
        soft, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, gated(
                g1=gate("g1", "complete", command=PASS_COMMAND, why_exempt=True),
                g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=True),
            ))
            # gauge sibling of the spine, fresh (observed_at == now), fill >= hard
            self._write_gauge(d, min(hard + 0.05, 1.0),
                              datetime.now(timezone.utc).isoformat())
            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = E.main(["--file", str(f), "start", "g2"])
            self.assertEqual(rc, 1)  # HARD refuses BEGIN-work
            self.assertIn("REFUSED:", err.getvalue())
            self.assertEqual(E.load(f)["tasks"]["g2"]["status"], "pending")
            # request a refresh, then the same start is allowed through
            self.assertEqual(
                E.main(["--file", str(f), "attach", "g2", "--type", "refresh-request",
                        "--field", "seam=g2", "--field", "why_ref=w-1"]), 0)
            self.assertEqual(E.main(["--file", str(f), "start", "g2"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g2"]["status"], "in-progress")

    def test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance(self):
        """#467, the real-file twin of the permanent DC2 guard: with a REAL gauge
        over hard and NO refresh-request anywhere, the gate the agent is already
        inside closes through main() and the digest carries the understanding
        written at it. The pre-#467 engine returned rc 1 here."""
        _, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, gated(g1=gate("g1", "in-progress", command=PASS_COMMAND,
                                    why_exempt=False)))
            self._write_gauge(d, min(hard + 0.05, 1.0),
                              datetime.now(timezone.utc).isoformat())
            self.assertEqual(E.main(["--file", str(f), "advance", "g1",
                                     "--why", "closing g1 carrying my handoff"]), 0)
            cl = E.load(f)
            self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
            self.assertEqual(E._digest(cl), "closing g1 carrying my handoff")
            self.assertEqual(_refresh_requests_anywhere(cl), [])

    def test_stale_gauge_reads_none_and_never_forces(self):
        _, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            # fill >= hard but observed_at is well beyond max_age -> reader -> None
            stale = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            self._write_gauge(d, min(hard + 0.05, 1.0), stale)
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")

    def test_absent_gauge_file_never_forces(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())  # no gauge.json written
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")

    def _write_uncalibrated_flag(self, d, model):
        (Path(d) / E._gauge_reader.UNCALIBRATED_FILENAME).write_text(json.dumps({
            "schema_version": 1, "model": model,
            "observed_at": datetime.now(timezone.utc).isoformat(),
        }), encoding="utf-8")

    def test_uncalibrated_model_is_announced_on_current(self):
        """#252 — a blind governor must SAY it is blind. Silence is how an
        uncalibrated claude-opus-5 went unnoticed for a whole epic."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_uncalibrated_flag(d, "claude-future-9")
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("CONTEXT GAUGE OFF", out)
            self.assertIn("claude-future-9", out)
            # names both tables so the fix is actionable without hunting
            self.assertIn("MODEL_WINDOWS", out)
            self.assertIn("_PROFILES", out)

    def test_uncalibrated_model_never_forces_or_refuses(self):
        """It is a missing instrument, not a full context — with no window we
        cannot claim the context is either full or empty, so advance passes."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_uncalibrated_flag(d, "claude-future-9")
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")

    def test_a_real_reading_wins_over_a_stale_flag(self):
        """A leftover flag must not shout over a live gauge — the reading is
        the better signal whenever one exists."""
        soft, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_uncalibrated_flag(d, "claude-future-9")
            self._write_gauge(d, max(soft - 0.02, 0.0),
                              datetime.now(timezone.utc).isoformat())
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                E.main(["--file", str(f), "current"])
            self.assertNotIn("CONTEXT GAUGE OFF", buf.getvalue())

    def test_fresh_soft_gauge_advises_on_current_but_advance_passes(self):
        soft, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_gauge(d, (soft + hard) / 2,
                              datetime.now(timezone.utc).isoformat())
            import contextlib, io
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(E.main(["--file", str(f), "current"]), 0)
            self.assertIn("CONTEXT", out.getvalue())
            self.assertIn(">= soft", out.getvalue())
            # SOFT never forces: advance still succeeds
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)

    # -- #271: gauge-skip.json real-file wiring through main() --------------- #

    def _write_skip_flag_sidecar(self, d, reason, candidate_count=None):
        record = {"schema_version": 1, "reason": reason,
                   "observed_at": datetime.now(timezone.utc).isoformat()}
        if candidate_count is not None:
            record["candidate_count"] = candidate_count
        (Path(d) / E._gauge_reader.SKIP_FILENAME).write_text(json.dumps(record), encoding="utf-8")

    def test_ambiguous_binding_skip_is_announced_on_current(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_skip_flag_sidecar(d, "ambiguous-binding", candidate_count=2)
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("CONTEXT", out)
            self.assertIn("2 candidate spines", out)

    def test_no_usable_record_skip_is_announced_on_current(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_skip_flag_sidecar(d, "no-usable-record")
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = E.main(["--file", str(f), "current"])
            self.assertEqual(rc, 0)
            self.assertIn("CONTEXT", buf.getvalue())

    def test_skip_flag_never_forces_or_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_skip_flag_sidecar(d, "ambiguous-binding", candidate_count=2)
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")

    def test_uncalibrated_flag_wins_over_a_skip_flag_at_the_same_path(self):
        """Priority order proven with REAL coexisting sidecars, not just
        mocks: the uncalibrated flag (a standing defect) always wins."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_skip_flag_sidecar(d, "no-usable-record")
            self._write_uncalibrated_flag(d, "claude-future-9")
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertIn("CONTEXT GAUGE OFF", out)
            self.assertNotIn("GAUGE SILENT", out)

    def test_stale_rejected_gauge_reports_raw_facts_on_current(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            stale = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
            self._write_gauge(d, 0.22, stale)
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("CONTEXT", out)
            self.assertIn("22%", out)
            self.assertNotIn(">= soft", out)
            self.assertNotIn(">= hard", out)

    def test_stale_gauge_report_never_forces_advance(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            stale = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
            self._write_gauge(d, 0.99, stale)
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")


# --------------------------------------------------------------------------- #
# #477 — a reading has an OWNER, and the engine can name it.
#
# The gauge is written per checklist DIRECTORY by a PostToolUse hook, so the
# number a fresh agent finds on its first `current` was sampled by whoever drove
# that directory before it — its predecessor after a relaunch, or the Commander
# whose work area its own plan sits in. Measured live on 2026-08-08 during epic
# 418: `.agent-work/issue-458-readiness/gauge.json` read `fill_fraction 0.190464,
# observed_at 23:18:53Z` — NINE MINUTES before the agent reading it existed. That
# agent was over the hard line on turn one, having done nothing.
#
# There is NO predicate over the bare number `0.190464` that separates a reading
# I took from one you took. The only fact on this side of the seam that carries
# WHO and WHEN is the engine's own lease: `engine_session.claimed_at` is the
# moment the acting session took this checklist. A sample taken strictly BEFORE
# that moment cannot be this session's, whatever it says.
#
# The failure this closes is a LOOP, which is why it is worth a guard: relaunch ->
# inherit the number -> trip HARD -> file a refresh-request -> stand down ->
# relaunch, indefinitely, with every cycle looking like correct doctrine being
# followed. It cost epic 418 four crew relaunches in one wave.
# --------------------------------------------------------------------------- #
class TripGaugeReadingOwnership(unittest.TestCase):
    """#477 — the engine DECLINES a gauge reading sampled before the acting
    session claimed this checklist, and says so instead of going quiet.

    Every test here drives the REAL reader over a REAL gauge.json sibling of a
    REAL spine through `main()`, because the defect is entirely in the pairing of
    a real file with a real lease; a patched `_read_gauge` would prove nothing.

    Timestamps are derived from the lease's own recorded `claimed_at` rather than
    from a second wall-clock read, so `before` and `after` are exact rather than
    racing the test's own runtime."""

    #: distinguishes "caller said nothing" from "caller said None (unowned)"
    _ACTING = object()

    def _write_gauge(self, d, fill, observed_at, session_id=_ACTING,
                     owner_field=_ACTING):
        """Write the gauge file the ACTING SESSION owns (#600).

        The gauge is no longer one file per work DIRECTORY -- it is named for
        the session that produced it. A test that kept writing the bare
        `gauge.json` here would be planting a file the leased engine no longer
        reads, and every #477/#601 assertion below would start passing
        vacuously against silence rather than against a declined reading.
        Passing `session_id=None` writes the UNOWNED `gauge.json`, which is
        what a LEASELESS checklist still reads, exactly as today (R3)."""
        sid = self.SESSION if session_id is self._ACTING else session_id
        owner = E._gauge_reader.owner_key(sid)
        record = {
            "schema_version": 1, "fill_fraction": fill,
            "model": "claude-opus-4-8", "observed_at": observed_at,
        }
        # The filename removes the collision; the `owner` field makes a
        # mismatch detectable if one ever reappears (R1: both, not either).
        stamped = owner if owner_field is self._ACTING else owner_field
        if stamped is not None:
            record["owner"] = stamped
        path = Path(d) / E._gauge_reader.gauge_filename(owner)
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def _over_hard(self):
        _, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        return min(hard + 0.05, 1.0)

    def _spine(self):
        # g1 complete / g2 pending: `start g2` is the BEGIN-work verb HARD guards,
        # so a trip is directly observable as a refusal.
        return gated(
            g1=gate("g1", "complete", command=PASS_COMMAND, why_exempt=True),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=True),
        )

    SESSION = "successor-session"

    def _claim(self, f, cl=None, session_id=None):
        """Save `cl` under a real active lease and return its `claimed_at`."""
        cl = self._spine() if cl is None else cl
        E.claim(cl, session_id or self.SESSION, "agent", ".", {})
        E.save(f, cl)
        return E._parse_ts(cl["engine_session"]["claimed_at"])

    # --- the defect: an inherited reading must not be obeyed ---------------- #
    def test_reading_sampled_before_the_claim_does_not_refuse_begin_work(self):
        """THE #477 CASE. Fill over the hard line, sampled nine minutes before
        this session claimed the checklist — the live epic-418 scenario, to the
        minute. It is the predecessor's exhaustion, so it must not stop this
        session beginning its first gate."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at - timedelta(minutes=9)).isoformat())
            rc = E.main(["--file", str(f), "start", "g2",
                         "--session-id", self.SESSION])
            self.assertEqual(rc, 0)
            self.assertEqual(E.load(f)["tasks"]["g2"]["status"], "in-progress")

    def test_reading_sampled_before_the_claim_is_not_rendered_as_a_band(self):
        """`current` must not present an inherited number as this session's
        soft/hard verdict. The band words are the whole payload an agent acts
        on — an inherited `>= hard` is what starts the relaunch loop."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at - timedelta(minutes=9)).isoformat())
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertNotIn(">= hard", out)
            self.assertNotIn(">= soft", out)

    def test_declined_reading_is_announced_not_silent(self):
        """Declining silently would reproduce the silent-governor failure this
        subsystem has already been burned by twice (#252, #271): the agent sees
        no number and cannot tell whether the gauge is broken, absent, or
        withheld. Say which one, name the session, and name the remedy."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at - timedelta(minutes=9)).isoformat())
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertIn("CONTEXT GAUGE", out)
            # the age, so an agent can see how far back the sample is
            self.assertIn("9m00s", out)
            # the session it is being measured against
            self.assertIn(self.SESSION, out)
            # the remedy: land your own tool call, don't file against this
            self.assertIn("refresh-request", out)

    def test_an_inherited_reading_never_suspends_the_mechanical_close(self):
        """At/over hard the engine bans a SILENT close (#431): `advance
        --mechanical` is refused and `why_exempt` is suspended. Riding that off
        an inherited number would force a fresh agent to write a handoff for
        work it has not done."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND,
                               why_exempt=True))
            claimed_at = self._claim(f, cl)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at - timedelta(minutes=9)).isoformat())
            rc = E.main(["--file", str(f), "advance", "g1", "--mechanical",
                         "--session-id", self.SESSION])
            self.assertEqual(rc, 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")

    # --- the other half: the governor must still work --------------------- #
    # Without these, "decline every reading" would pass the four tests above,
    # and the fix would be a way to switch the governor off.
    def test_a_self_measured_reading_over_hard_still_refuses(self):
        """Same file, same lease, one second the OTHER side of `claimed_at`."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at + timedelta(seconds=1)).isoformat())
            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = E.main(["--file", str(f), "start", "g2",
                             "--session-id", self.SESSION])
            self.assertEqual(rc, 1)
            self.assertIn("REFUSED:", err.getvalue())
            self.assertEqual(E.load(f)["tasks"]["g2"]["status"], "pending")

    def test_a_reading_sampled_exactly_at_the_claim_is_owned(self):
        """The boundary is STRICTLY before. An equal timestamp is kept, so
        second-resolution coincidence never silences a real reading."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(), claimed_at.isoformat())
            rc = E.main(["--file", str(f), "start", "g2",
                         "--session-id", self.SESSION])
            self.assertEqual(rc, 1)

    # --- #601: the relaunch the guard exists for must actually reach it ---- #
    # The guard above is correct and was, in production, unreachable: a
    # relaunched agent reuses its session name, lands on claim()'s idempotent
    # same-session branch, and that branch refreshed only `last_heartbeat`. With
    # `claimed_at` pinned at leg 1's claim, leg 1's reading is `observed_at >
    # claimed_at` -- owned -- and every test above passes while the live loop
    # they describe keeps running. These two drive the relaunch itself.
    def test_a_relaunch_reclaim_restamps_claimed_at(self):
        """The mechanism, at the unit: re-claiming a lease you already hold moves
        `claimed_at`, not just the heartbeat."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            self._claim(f)
            cl = E.load(f)
            # Backdate the claim so the assertion is about the re-stamp and not
            # about two wall-clock reads landing in the same second.
            stale = _old_ts(30)
            cl["engine_session"]["claimed_at"] = stale
            cl["engine_session"]["last_heartbeat"] = stale
            msg = E.claim(cl, self.SESSION, "agent", ".", {})
            self.assertIn("resumed lease", msg)
            self.assertGreater(
                E._parse_ts(cl["engine_session"]["claimed_at"]),
                E._parse_ts(stale))

    def test_leg_ones_reading_stops_refusing_leg_two_after_its_own_reclaim(self):
        """THE #601 CASE, end to end through `main()`. Leg 1 claims and its
        gauge sample lands AFTER that claim -- an honest self-measured reading
        over the hard line, which correctly refuses leg 1. Leg 2 relaunches into
        the same spine under the same session name and re-claims. That sample is
        now pre-claim, so it is declined and leg 2 may begin its gate.

        Without the re-stamp this is the observed production failure: leg 2 is
        refused on turn one by a number it did not produce, files a
        refresh-request, stands down, and the next leg inherits the same state.
        """
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            self._claim(f)
            # Leg 1 ran half an hour ago. Backdating its lease is what makes the
            # relaunch real: leg 2's re-claim happens NOW, so leg 1's sample --
            # honestly self-measured one second after leg 1 claimed -- is on the
            # far side of it. Sampling relative to a fresh claim instead would
            # put the reading in the future and prove nothing.
            cl = E.load(f)
            leg1_claim = E._parse_ts(_old_ts(30))
            cl["engine_session"]["claimed_at"] = leg1_claim.isoformat()
            cl["engine_session"]["last_heartbeat"] = leg1_claim.isoformat()
            E.save(f, cl)
            self._write_gauge(d, self._over_hard(),
                              (leg1_claim + timedelta(seconds=1)).isoformat())

            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = E.main(["--file", str(f), "start", "g2",
                             "--session-id", self.SESSION])
            self.assertEqual(rc, 1, "leg 1's own reading must still refuse leg 1")

            # Leg 2: same session name, so this is the idempotent branch.
            rc = E.main(["--file", str(f), "claim",
                         "--session-id", self.SESSION, "--claimed-by", "agent"])
            self.assertEqual(rc, 0)

            rc = E.main(["--file", str(f), "start", "g2",
                         "--session-id", self.SESSION])
            self.assertEqual(rc, 0)
            self.assertEqual(E.load(f)["tasks"]["g2"]["status"], "in-progress")

    # --- fail OPEN: no provenance means today's behaviour, exactly --------- #
    def test_leaseless_checklist_reads_the_unowned_gauge(self):
        """#600 R3, stated as its own pin because it is the one place
        owner-keying could silently REMOVE coverage rather than add it.

        Owner-keying applies only where a lease exists. With no lease there is
        no owner, so the engine reads the UNOWNED `gauge.json` and trips on it
        exactly as it does today. Going quiet here is the permit direction and
        therefore inside this lane's latitude — but it is a real loss of
        coverage on checklists that are governed today, and taking it as a side
        effect of a rename is how coverage disappears without anyone deciding
        it should. The fail-safe is "no ATTRIBUTABLE reading yields None"; it
        must not become "no lease yields nothing".

        Drives the real reader over a real file on disk through `main()`, and
        pins the negative direction too: an OWNER-KEYED file must NOT be picked
        up by a leaseless checklist, or this would pass for the wrong reason.
        """
        observed_at = (datetime.now(timezone.utc)
                       - timedelta(minutes=9)).isoformat()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            path = self._write_gauge(d, self._over_hard(), observed_at,
                                     session_id=None)
            self.assertEqual(path.name, "gauge.json")
            self.assertEqual(
                E.main(["--file", str(f), "start", "g2"]), 1,
                "a leaseless checklist must still trip on the unowned gauge")

        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            # the same over-hard reading, but named for an owner. A leaseless
            # checklist has no owner to match it against, so it must not be
            # read -- no reading, no trip, and NO fallback to somebody's file.
            path = self._write_gauge(d, self._over_hard(), observed_at,
                                     session_id="somebody-else")
            self.assertNotEqual(path.name, "gauge.json")
            self.assertEqual(
                E.main(["--file", str(f), "start", "g2"]), 0,
                "a leaseless checklist must not trip on an owned reading")

    def test_a_record_stamped_for_another_owner_is_declined_and_announced(self):
        """#600 R1: the filename removes the collision, the `owner` FIELD makes
        a mismatch detectable if one ever reappears. Both, not either.

        A record sitting in this session's own filename but stamped for someone
        else can only be a bug -- the two sides compute the owner from the same
        string through the same function. Declining is the quiet direction and
        never a refusal, but declining SILENTLY would look exactly like "no
        gauge yet", which is how #252 and #271 both survived unnoticed."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            # this session's own filename, a fresh self-measured over-hard
            # reading, but stamped for somebody else
            path = self._write_gauge(d, self._over_hard(),
                                     (claimed_at + timedelta(seconds=1)).isoformat(),
                                     owner_field="somebody-else-000000000000")
            self.assertEqual(path.name,
                             E._gauge_reader.gauge_filename(
                                 E._gauge_reader.owner_key(self.SESSION)))

            # not obeyed: the same reading with an honest stamp refuses `start`
            # (test_a_self_measured_reading_over_hard_still_refuses), so a rc of
            # 0 here is the decline and nothing else.
            rc = E.main(["--file", str(f), "start", "g2",
                         "--session-id", self.SESSION])
            self.assertEqual(rc, 0)

            # and not silent
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                E.main(["--file", str(f), "current"])
            out = buf.getvalue()
            self.assertIn("CONTEXT GAUGE DECLINED", out)
            self.assertIn("somebody-else-000000000000", out)  # what it claims
            self.assertIn(self.SESSION, out)                  # who is driving
            self.assertNotIn(">= hard", out)

    def test_a_record_with_no_owner_field_is_not_treated_as_a_mismatch(self):
        """Every gauge file written before #600 carries no owner, and they must
        keep working -- absence is not disagreement."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at + timedelta(seconds=1)).isoformat(),
                              owner_field=None)
            self.assertEqual(E.main(["--file", str(f), "start", "g2",
                                     "--session-id", self.SESSION]), 1)

    def test_owner_mismatch_advisory_outranks_the_others(self):
        """It is the only cause on that dispatcher that can only be a DEFECT
        rather than a condition, so it must not be buried under a description of
        a gauge that is working correctly and has nothing to say."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            claimed_at = self._claim(f)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at + timedelta(seconds=1)).isoformat(),
                              owner_field="somebody-else-000000000000")
            cl = E.load(f)
            with mock.patch.object(E, "_uncalibrated_advisory",
                                   return_value="\nCONTEXT GAUGE OFF: x"), \
                 mock.patch.object(E, "_skip_reason_advisory",
                                   return_value="\nCONTEXT GAUGE SILENT: skip"), \
                 mock.patch.object(E, "_stale_record_advisory",
                                   return_value="\nCONTEXT GAUGE SILENT: stale"):
                out = E._no_reading_advisory(cl, Path(d))
            self.assertIn("CONTEXT GAUGE DECLINED", out)

    def test_no_lease_at_all_behaves_exactly_as_today(self):
        """Every gauge.json in the wild predates this guard and most checklists
        are driven with no lease at all. With nothing to measure ownership
        against, the reading is used — a gauge that starts refusing readings
        would stop every run in the fleet."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            self._write_gauge(d, self._over_hard(),
                              (datetime.now(timezone.utc)
                               - timedelta(minutes=9)).isoformat(),
                              session_id=None)
            self.assertEqual(E.main(["--file", str(f), "start", "g2"]), 1)

    def test_a_released_lease_behaves_exactly_as_today(self):
        """A released lease names nobody currently driving, so it cannot be the
        anchor for whose reading this is — and, since #600, cannot name the
        file either, so this reads the unowned gauge."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            cl = self._spine()
            E.claim(cl, self.SESSION, "agent", ".", {})
            claimed_at = E._parse_ts(cl["engine_session"]["claimed_at"])
            cl["engine_session"]["status"] = "released"
            E.save(f, cl)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at - timedelta(minutes=9)).isoformat(),
                              session_id=None)
            self.assertEqual(E.main(["--file", str(f), "start", "g2"]), 1)

    def test_an_unparseable_claimed_at_behaves_exactly_as_today(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            cl = self._spine()
            E.claim(cl, self.SESSION, "agent", ".", {})
            claimed_at = E._parse_ts(cl["engine_session"]["claimed_at"])
            cl["engine_session"]["claimed_at"] = "not-a-timestamp"
            E.save(f, cl)
            self._write_gauge(d, self._over_hard(),
                              (claimed_at - timedelta(minutes=9)).isoformat())
            self.assertEqual(E.main(["--file", str(f), "start", "g2",
                                     "--session-id", self.SESSION]), 1)

    # --- the predicate itself, unit-level --------------------------------- #
    def _r(self, observed_at):
        return E._gauge_reader.Reading(
            schema_version=1, fill_fraction=0.5, model="claude-opus-4-8",
            observed_at=observed_at)

    def _leased(self, **overrides):
        cl = {"engine_session": {
            "session_id": self.SESSION, "status": "active",
            "claimed_at": "2026-08-08T23:28:00+00:00"}}
        cl["engine_session"].update(overrides)
        return cl

    def test_lease_claimed_at_reads_the_active_lease(self):
        self.assertEqual(
            E._lease_claimed_at(self._leased()),
            datetime(2026, 8, 8, 23, 28, tzinfo=timezone.utc))

    def test_lease_claimed_at_is_none_for_every_absent_or_unusable_shape(self):
        for label, cl in (
            ("no key", {}),
            ("not a dict", {"engine_session": "nope"}),
            ("released", self._leased(status="released")),
            ("no status", self._leased(status=None)),
            ("missing claimed_at", self._leased(claimed_at=None)),
            ("empty claimed_at", self._leased(claimed_at="")),
            ("unparseable claimed_at", self._leased(claimed_at="whenever")),
            ("non-string claimed_at", self._leased(claimed_at=17)),
        ):
            with self.subTest(label):
                self.assertIsNone(E._lease_claimed_at(cl))

    def test_predicate_is_true_only_strictly_before_the_claim(self):
        claimed = datetime(2026, 8, 8, 23, 28, tzinfo=timezone.utc)
        cl = self._leased()
        for label, observed, expected in (
            ("nine minutes before", claimed - timedelta(minutes=9), True),
            ("one microsecond before", claimed - timedelta(microseconds=1), True),
            ("exactly at", claimed, False),
            ("one second after", claimed + timedelta(seconds=1), False),
        ):
            with self.subTest(label):
                self.assertIs(E._reading_predates_claim(cl, self._r(observed)),
                              expected)

    def test_predicate_fails_open_on_a_missing_reading_or_lease(self):
        claimed = datetime(2026, 8, 8, 23, 28, tzinfo=timezone.utc)
        self.assertIs(E._reading_predates_claim(self._leased(), None), False)
        self.assertIs(
            E._reading_predates_claim({}, self._r(claimed - timedelta(days=1))),
            False)


# --------------------------------------------------------------------------- #
# #227 gate g2 — state()/render_human() port-and-adapter, current() as a
# complete gate briefing. See dit-I1-ports-RESULT.md (constellation-skills,
# archive/2026-07-24-explore-design-thrust) for the ratified StateView shape;
# the g2 handoff deliberately kills the panel's --json flag / render_json
# adapter / explain-show verb, so state() below is internal structure only.
# --------------------------------------------------------------------------- #
class GoldenOutputBriefing(unittest.TestCase):
    """Golden-output tests for render_human()/current(): one per active-task
    state (pending/in-progress/blocked) plus the three no-active-task branches
    (DONE with no waived, DONE with WAIVED, survey ALL ITEMS VISITED). None of
    these six had a golden (exact-output) test before this change, and they
    are exactly the branches most likely to be silently reshaped by a
    render_human() rewrite."""

    def test_pending_active_task_shows_open_preconditions_and_next_start(self):
        # p1 is a NULL-kind precondition and it is still [unmet]: `start` MUST
        # NOT appear in next: (rework 1, g2 review BLOCK) -- it would refuse
        # immediately ("preconditions unmet ['p1']"). Only attest is legal here.
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "preconditions:\n"
            "  p1 [unmet] null — iface exists\n"
            "0/1 met\n"
            "next: attest g1 --cond p1 --which preconditions"
        ))

    def test_pending_active_task_with_satisfied_preconditions_shows_next_start(self):
        # Once the (only) precondition is satisfied, `start` becomes legal and
        # reappears in next: -- the positive-space complement of the test above.
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": True, "satisfied_by": "attested"}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "1/1 met\n"
            "next: start g1"
        ))

    def test_in_progress_active_task_shows_open_postconditions_and_next_advance(self):
        # A non-exempt gate with one open ARTIFACT-kind postcondition: `advance`
        # MUST NOT appear in next: (rework 1, g2 review BLOCK) -- it would
        # refuse immediately ("postconditions unmet ['c1']"). Only the
        # attest --evidence hint (the INV-1 trap) is legal here.
        t = gate("g1", "in-progress", why_exempt=False)
        t["postconditions"] = [{
            "id": "c1", "statement": "approved",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        }]
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [in-progress] — do g1\n"
            "postconditions:\n"
            "  c1 [unmet] artifact — approved\n"
            "0/1 met\n"
            "next: attest g1 --cond c1 --which postconditions --evidence <evidence-id>"
        ))

    def test_in_progress_non_exempt_with_open_command_postcondition_shows_advance_with_why(self):
        # A COMMAND-kind postcondition is live-checked inside advance() itself,
        # so an open one here does NOT suppress the hint (unlike the artifact
        # case above) -- and being non-exempt, --why is required.
        t = gate("g1", "in-progress", why_exempt=False, command=PASS_COMMAND)
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [in-progress] — do g1\n"
            "postconditions:\n"
            "  c1 [unmet] command — tests pass\n"
            "0/1 met\n"
            "next: advance g1 --why \"<understanding>\" (or --mechanical)"
        ))

    def test_blocked_active_task_shows_resume_hint(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "waiting on x1 result", "parent agent", "escalate; do not re-dispatch")
        out = E.current(cl)
        self.assertIn("ACTIVE g1 [blocked] — do g1", out)
        self.assertIn("next: resume g1 --reason \"<why the blocker cleared>\"", out)

    def test_done_no_open_items_no_waived(self):
        cl = gated(g1=gate("g1", "complete"))
        self.assertEqual(E.current(cl), "DONE: no open items.")

    def test_done_no_open_items_with_waived(self):
        t = gate("g1", "in-progress", why_exempt=True)
        t["postconditions"] = [{
            "id": "c1", "statement": "x",
            "check": {"kind": "command", "command": FAIL_COMMAND},
            "satisfied": False, "override_policy": {"allowed": True},
        }]
        cl = gated(g1=t)
        E.waive(cl, "g1", "c1", "postconditions", "human", "flaky check, closeout-only")
        self.assertEqual(E.advance(cl, "g1"), "g1 -> complete (WAIVED postconditions ['c1'])")
        self.assertEqual(E.current(cl), "DONE: no open items. WAIVED: ['g1.c1']")

    def test_all_items_visited_prompts_consolidate(self):
        cl = survey(v1=survey_item("v1", "complete"))
        self.assertEqual(E.current(cl), "ALL ITEMS VISITED. Next: consolidate")


class RenderBookendFreeze(unittest.TestCase):
    """#634 follow-up: `bookend: true` changes what `amend` will accept, but
    until this change `current()` never mentioned it -- the freeze was
    discoverable only by attempting the refused amend, or by reading
    spine.json directly (itself a doctrine violation; see global-everyone.md's
    "current is the complete gate briefing"). Golden (exact-output) tests for
    the new `bookend:` prefix line, on the model of GoldenOutputBriefing
    above: one per branch that must carry it (active gate, DONE), plus the
    unchanged-output regression for a plan that declares no bookend at all."""

    def test_active_gate_briefing_carries_bookend_line_for_other_gate(self):
        # g1 is the active (pending) gate; g2 is a declared bookend further
        # down the plan. The freeze line names g2 even though g1, not g2, is
        # what the agent is about to act on -- exactly the case the defect
        # describes: an agent planning an amend on g1 needs to see that g2
        # is off-limits WITHOUT touching amend or spine.json.
        g2 = gate("g2", "pending")
        g2["bookend"] = True
        cl = gated(g1=gate("g1", "pending"), g2=g2)
        self.assertEqual(E.current(cl), (
            "bookend (frozen -- amend refuses drop/rescope/retext-check, and "
            "add past the last one): g2\n"
            "ACTIVE g1 [pending] — do g1\n"
            "next: start g1"
        ))

    def test_multiple_bookends_render_in_item_order(self):
        init = gate("init", "pending")
        init["bookend"] = True
        archive = gate("archive", "pending")
        archive["bookend"] = True
        cl = gated(init=init, mid=gate("mid", "pending"), archive=archive)
        out = E.current(cl)
        self.assertTrue(out.startswith("bookend (frozen"), out)
        self.assertIn("init, archive", out)

    def test_done_state_still_shows_bookend_line(self):
        # The freeze is a whole-plan property, not scoped to the active gate:
        # it must render on the DONE branch too, not just while a gate is
        # active.
        g1 = gate("g1", "complete")
        g1["bookend"] = True
        cl = gated(g1=g1)
        self.assertEqual(E.current(cl), (
            "bookend (frozen -- amend refuses drop/rescope/retext-check, and "
            "add past the last one): g1\n"
            "DONE: no open items."
        ))

    def test_no_bookend_declared_adds_no_line(self):
        # Regression: an undeclared plan's current() output is byte-identical
        # to before this change (matches GoldenOutputBriefing's un-prefixed
        # goldens above).
        cl = gated(g1=gate("g1", "pending"))
        self.assertEqual(E.current(cl), "ACTIVE g1 [pending] — do g1\nnext: start g1")


class RenderAnchorsAndConstraints(unittest.TestCase):
    """Issue #420, defect 2: `anchors` and `constraints` are real, populated
    corpus content on execute.json gates (Commander mission-frame anchors,
    per-gate constraints) -- confirmed live against 20+ archived execute.json
    gates -- but `state()` never read them, so `current()` silently dropped
    them even when populated. `current` is documented as a COMPLETE briefing
    (INV-1, docs/CHECKLIST_ENGINE_DESIGN.md); this closes that gap."""

    def test_constraints_render_when_present(self):
        t = gate("g1", "pending")
        t["constraints"] = ["stay pinned to X", "no touching Y"]
        cl = gated(g1=t)
        out = E.current(cl)
        self.assertIn("stay pinned to X", out)
        self.assertIn("no touching Y", out)

    def test_anchors_render_when_present_dict_shape(self):
        # Real corpus shape: category -> [str] (Commander mission-frame
        # anchors, e.g. this very issue's own execute.json g1-implement gate).
        t = gate("g1", "pending")
        t["anchors"] = {"structural": ["scripts/foo.py: bar()"],
                         "constraint": ["INV-2 purity"]}
        cl = gated(g1=t)
        out = E.current(cl)
        self.assertIn("scripts/foo.py: bar()", out)
        self.assertIn("INV-2 purity", out)

    def test_anchors_render_when_present_list_shape(self):
        # Some archived gates carry a flat list instead of the category dict
        # -- both shapes appear in the live corpus (verified this run).
        t = gate("g1", "pending")
        t["anchors"] = ["a flat anchor note"]
        cl = gated(g1=t)
        out = E.current(cl)
        self.assertIn("a flat anchor note", out)

    def test_anchors_render_when_dict_value_is_a_plain_string(self):
        # A THIRD real corpus shape (Commander's own g1-implement-integrate
        # rework, found during independent verification of this fix):
        # {category: "<plain string>"} -- a dict whose VALUE is a bare
        # string, not a list. Ground truth: skills/commander/templates/
        # EXECUTE_PLAN.template.json's g1-review gate carries exactly this
        # shape. A naive `for item in (items or [])` treats the string as an
        # iterable and emits one line PER CHARACTER -- worse than the
        # pre-#420 silent drop, because it actively renders garbage.
        t = gate("g1-review", "pending")
        t["anchors"] = {
            "inherits": "g1-implement anchors — review verifies the change "
                        "against the same structural/capability/constraint/"
                        "decision/evidence anchors",
        }
        cl = gated(**{"g1-review": t})
        out = E.current(cl)
        self.assertIn(
            "inherits: g1-implement anchors — review verifies the change "
            "against the same structural/capability/constraint/decision/"
            "evidence anchors",
            out,
        )
        # The character-by-character explosion this guards against: if the
        # bug regresses, the string is iterated and single letters appear as
        # their own "inherits: X" lines instead of the whole sentence once.
        self.assertEqual(out.count("inherits:"), 1, out)

    def test_absent_constraints_and_anchors_render_unchanged(self):
        # No anchors key at all, constraints defaulted to [] by gate() --
        # output stays byte-identical to the pre-#420 shape: this fix must
        # add nothing when the fields are empty/absent.
        pre = [{"id": "p1", "statement": "iface exists", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "preconditions:\n"
            "  p1 [unmet] null — iface exists\n"
            "0/1 met\n"
            "next: attest g1 --cond p1 --which preconditions"
        ))

    def test_empty_constraints_list_and_no_postconditions_renders_unchanged(self):
        t = gate("g1", "pending")  # constraints defaults to [], no anchors key
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), "ACTIVE g1 [pending] — do g1\nnext: start g1")


class RenderDirectives(unittest.TestCase):
    """Issue #433: `directives` is the third populated Task field `state()`
    never read, so `current()` dropped it exactly the way it dropped
    `anchors`/`constraints` before #420. A tree-wide inventory of this
    worktree (2955 gates) found 8 populated `directives` blocks, every one a
    dict of name -> contract dict; `docs/CHECKLIST_SCHEMA.md` separately
    declares the field as `[string] | null` and the `add` amend op accepts
    that flat shape unvalidated, so BOTH shapes must render. `current` is
    documented as a COMPLETE briefing (INV-1,
    docs/CHECKLIST_ENGINE_DESIGN.md); a directive the agent never sees is a
    silently unenforced instruction."""

    SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

    # The golden below is written over the ACTUAL SHIPPED spine, not a
    # fixture shaped like it: the claim under test is
    # `claim:a-populated-directives-block-appears-in-current` for a gate that
    # really ships, so a hand-built fixture could not prove it.
    def _shipped_spine_with_execute_active(self):
        cl = json.loads(self.SPINE.read_text(encoding="utf-8"))
        for iid in cl["items"]:
            if iid == "execute":
                break
            cl["tasks"][iid]["status"] = "complete"
        self.assertEqual(E.active_id(cl), "execute")
        return cl

    def test_shipped_commander_spine_execute_gate_renders_its_directives(self):
        cl = self._shipped_spine_with_execute_active()
        t = cl["tasks"]["execute"]
        self.assertTrue(
            t.get("directives"),
            "fixture drift: the shipped COMMANDER_SPINE `execute` gate no "
            "longer carries a populated `directives` block, so this golden "
            "is no longer proving anything -- re-run the corpus inventory",
        )
        out = E.current(cl)

        # The ACTIVE line stays byte-identical to `ACTIVE {id} [{status}] —
        # {imperative}`, unchanged by this issue (GoldenOutputBriefing pins
        # the same format across every shipped template) -- but it is no
        # longer necessarily splitlines()[0]. COMMANDER_SPINE declares
        # init/archive as bookends (#634), so since the #634-follow-up fix
        # a `bookend:` line now occupies the same PREFIX slot `lease_line`
        # already used, ahead of it.
        active_line = next(line for line in out.splitlines() if line.startswith("ACTIVE"))
        self.assertEqual(active_line, f"ACTIVE execute [pending] — {t['imperative']}")

        self.assertIn(
            "\ndirectives:\n"
            "  replan_input:\n"
            "    template: ../constellation-replan/templates/REPLAN_INPUT.template.json\n"
            "    single_issue_template: ../constellation-replan/templates/RUN_EVIDENCE.template.json\n"
            "    output: .agent-work/<work-id>/REPLAN_INPUT.json\n"
            "    evidence_fields: completed_outcomes, wave_evidence, discrepancies\n"
            "    classifications: blocks_current_wave_exit, invalidates_forecast_or_decomposition, later_only, evidence_only, drop\n"
            "    auto_file_discrepancies: false\n"
            "    check: verify_iterative_role_artifacts.py commander\n",
            out,
        )
        # Placement: after the conditions body, before the `next:` hint --
        # the same slot `anchors:` occupies.
        self.assertEqual(out.count("directives:"), 1, out)
        self.assertLess(out.index("directives:"), out.index("\nnext: "), out)

    def test_nested_contract_dict_shape_renders_indented_leaves(self):
        # Shape (a), the one all 8 populated corpus gates carry, isolated
        # from the shipped template so the format itself is pinned: a list
        # leaf joins with ", " and a non-string scalar takes JSON spelling
        # (Python False -> `false`), so what prints reads back as the JSON
        # the gate actually carries.
        t = gate("g1", "pending")
        t["directives"] = {"replan_input": {
            "template": "../constellation-replan/templates/REPLAN_INPUT.template.json",
            "evidence_fields": ["completed_outcomes", "wave_evidence"],
            "auto_file_discrepancies": False,
        }}
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "directives:\n"
            "  replan_input:\n"
            "    template: ../constellation-replan/templates/REPLAN_INPUT.template.json\n"
            "    evidence_fields: completed_outcomes, wave_evidence\n"
            "    auto_file_discrepancies: false\n"
            "next: start g1"
        ))

    def test_dict_value_that_is_not_a_dict_renders_as_one_leaf_line(self):
        # #479/#433 g1 review carry-over: shape (a)'s `else` branch -- a dict
        # value that is not itself a dict -- was flagged dead by mutation and
        # is kept deliberately (mirrors _render_anchor_lines' own
        # unrecognized-shape posture), not deleted. This characterization
        # test is the checkable form of that "kept deliberately" reason
        # (pre-ruling #3): the corpus carries no such shape today (none found
        # across skills/*/templates/*.template.json), so nothing else in the
        # suite exercises it.
        t = gate("g1", "pending")
        t["directives"] = {"replan_input": "a bare string"}
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "directives:\n"
            "  replan_input: a bare string\n"
            "next: start g1"
        ))

    def test_flat_list_of_strings_shape_renders_one_line_each(self):
        # Shape (b), the one docs/CHECKLIST_SCHEMA.md declares and the `add`
        # amend op accepts unvalidated. Narrowing the renderer to dicts would
        # silently reinstate the #433 defect for this shape.
        t = gate("g1", "pending")
        t["directives"] = ["file REPLAN_INPUT.json before advancing",
                            "discrepancies are evidence, never auto-filed issues"]
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "directives:\n"
            "  file REPLAN_INPUT.json before advancing\n"
            "  discrepancies are evidence, never auto-filed issues\n"
            "next: start g1"
        ))

    def test_flat_list_with_a_non_string_item_renders_every_item(self):
        # g1 review carry-over: the list branch must be TOTAL, the way
        # _render_anchor_lines' list branch is. Filtering it to
        # `isinstance(item, str)` silently DROPPED a non-string item -- a
        # populated value the briefing never shows, which is the #433 defect
        # class reproduced inside the #433 fix, and it contradicted the
        # helper's own stated rule. Non-string items take the JSON spelling
        # _directive_leaf documents, so `False` prints as `false`.
        t = gate("g1", "pending")
        t["directives"] = ["file REPLAN_INPUT.json before advancing", 17, False]
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "directives:\n"
            "  file REPLAN_INPUT.json before advancing\n"
            "  17\n"
            "  false\n"
            "next: start g1"
        ))

    def test_absent_or_empty_directives_add_no_output(self):
        # The #420 rule, held: an absent or empty field adds NOTHING -- no
        # bare `directives:` header, no blank line. gate() already sets
        # `directives: None`, the corpus default on 2947 of the 2955 gates
        # inventoried.
        baseline = "ACTIVE g1 [pending] — do g1\nnext: start g1"
        self.assertEqual(E.current(gated(g1=gate("g1", "pending"))), baseline)
        for empty in (None, {}, [], ""):
            with self.subTest(directives=empty):
                t = gate("g1", "pending")
                t["directives"] = empty
                self.assertEqual(E.current(gated(g1=t)), baseline)
        t = gate("g1", "pending")
        del t["directives"]  # key absent entirely, not merely null
        self.assertEqual(E.current(gated(g1=t)), baseline)

    def test_unrecognized_directives_shape_renders_nothing(self):
        # Same discipline _render_anchor_lines states: a shape the corpus
        # does not actually use renders nothing rather than guessing.
        t = gate("g1", "pending")
        t["directives"] = 17
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), "ACTIVE g1 [pending] — do g1\nnext: start g1")

    def test_directives_render_after_anchors_and_before_next(self):
        t = gate("g1", "pending")
        t["constraints"] = ["CONSTRAINT_TEXT"]
        t["anchors"] = {"structural": ["ANCHOR_TEXT"]}
        t["directives"] = ["DIRECTIVE_TEXT"]
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [pending] — do g1\n"
            "constraints:\n"
            "  CONSTRAINT_TEXT\n"
            "anchors:\n"
            "  structural: ANCHOR_TEXT\n"
            "directives:\n"
            "  DIRECTIVE_TEXT\n"
            "next: start g1"
        ))

    def test_state_passes_directives_through_without_re_running_checks(self):
        # INV-2: state() is a pure projection. The passthrough must not
        # touch a `command` check -- if it did, this gate's deliberately
        # process-spawning postcondition would run on a read-only `current`.
        t = gate("g1", "in-progress", command=FAIL_COMMAND, why_exempt=False)
        t["directives"] = {"replan_input": {"output": "x.json"}}
        cl = gated(g1=t)
        with mock.patch.object(E.subprocess, "run",
                                side_effect=AssertionError("state() ran a command check")):
            view = E.state(cl)
        self.assertEqual(view["active"]["directives"],
                          {"replan_input": {"output": "x.json"}})


class BasisRendering(unittest.TestCase):
    """569-w2-basis g1: a `basis` sibling field on a `check: null` Condition
    lets plan authoring declare a resolvable locator (`file`/`evidence_ref`)
    for a qualitative postcondition. `current()` must render it -- one
    indented line immediately under the open condition's own line -- only
    when populated and not `abstain`, the same populated-only convention
    `constraints`/`anchors`/`directives` already use. This class covers the
    render half only; the attest-time report-only guard is BasisAttestGuard."""

    def test_populated_file_basis_renders_basis_line(self):
        post = [{"id": "c1", "statement": "frame written", "check": None,
                 "satisfied": False,
                 "basis": {"locator_kind": "file",
                           "locator": {"path": ".agent-work/w2-basis/MISSION_FRAME.md"}}}]
        t = gate("g1", "in-progress")
        t["postconditions"] = post
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [in-progress] — do g1\n"
            "postconditions:\n"
            "  c1 [unmet] null — frame written\n"
            "    basis: file .agent-work/w2-basis/MISSION_FRAME.md\n"
            "0/1 met\n"
            "next: attest g1 --cond c1 --which postconditions"
        ))

    def test_populated_evidence_ref_basis_renders_basis_line(self):
        post = [{"id": "c1", "statement": "upstream reviewed", "check": None,
                 "satisfied": False,
                 "basis": {"locator_kind": "evidence_ref",
                           "locator": {"task_id": "g0", "cond_id": "c1"}}}]
        t = gate("g1", "in-progress")
        t["postconditions"] = post
        cl = gated(g1=t)
        out = E.current(cl)
        self.assertIn("    basis: evidence_ref g0.c1\n", out)

    def test_abstain_basis_renders_nothing(self):
        post = [{"id": "c1", "statement": "frame written", "check": None,
                 "satisfied": False,
                 "basis": {"locator_kind": "abstain", "locator": {}}}]
        t = gate("g1", "in-progress")
        t["postconditions"] = post
        cl = gated(g1=t)
        out = E.current(cl)
        self.assertNotIn("basis:", out)
        self.assertEqual(out, (
            "ACTIVE g1 [in-progress] — do g1\n"
            "postconditions:\n"
            "  c1 [unmet] null — frame written\n"
            "0/1 met\n"
            "next: attest g1 --cond c1 --which postconditions"
        ))

    def test_absent_basis_renders_nothing_and_baseline_is_unchanged(self):
        # No basis key at all -- must render byte-identical to the pre-#569
        # baseline (Protected Intent: no observable change for a condition
        # that carries no basis).
        post = [{"id": "c1", "statement": "frame written", "check": None,
                 "satisfied": False}]
        t = gate("g1", "in-progress")
        t["postconditions"] = post
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [in-progress] — do g1\n"
            "postconditions:\n"
            "  c1 [unmet] null — frame written\n"
            "0/1 met\n"
            "next: attest g1 --cond c1 --which postconditions"
        ))

    def test_basis_line_sits_under_its_own_condition_not_after_all(self):
        post = [
            {"id": "c1", "statement": "first", "check": None, "satisfied": False,
             "basis": {"locator_kind": "file", "locator": {"path": "a.md"}}},
            {"id": "c2", "statement": "second", "check": None, "satisfied": False},
        ]
        t = gate("g1", "in-progress")
        t["postconditions"] = post
        cl = gated(g1=t)
        self.assertEqual(E.current(cl), (
            "ACTIVE g1 [in-progress] — do g1\n"
            "postconditions:\n"
            "  c1 [unmet] null — first\n"
            "    basis: file a.md\n"
            "  c2 [unmet] null — second\n"
            "0/2 met\n"
            "next: attest g1 --cond c1 --which postconditions | attest g1 --cond c2 --which postconditions"
        ))

    def test_state_passes_basis_through_without_re_running_checks(self):
        # INV-2: state() is a pure projection reading the stored `basis`
        # dict only -- it must never probe anything, and a `basis` field
        # sits beside a `command` check elsewhere on the same gate here to
        # prove the passthrough doesn't trip that check either.
        t = gate("g1", "in-progress", command=FAIL_COMMAND, why_exempt=False)
        t["postconditions"].append(
            {"id": "c2", "statement": "frame written", "check": None,
             "satisfied": False,
             "basis": {"locator_kind": "file", "locator": {"path": "a.md"}}}
        )
        cl = gated(g1=t)
        with mock.patch.object(E.subprocess, "run",
                                side_effect=AssertionError("state() ran a command check")):
            view = E.state(cl)
        basis_conds = [c for c in view["active"]["postconditions"] if c["id"] == "c2"]
        self.assertEqual(basis_conds[0]["basis"],
                          {"locator_kind": "file", "locator": {"path": "a.md"}})


class TaskFieldCompleteness(unittest.TestCase):
    """Issue #420 defect 3, made falsifiable by #433: a real enumeration of the
    fields a Task may carry (docs/CHECKLIST_SCHEMA.md's Task table, plus
    `anchors` -- documented only in commander-core.md prose, not the schema
    table) asserting every POPULATED field's content appears somewhere in
    current()'s rendered output for a fixture that carries every field. Built as
    a loop over the fixture's own keys minus a documented, justified exclusion
    set -- NOT a hardcoded check of only anchors/constraints by name -- so a
    genuinely new field added to Task later and forgotten in render_human()
    fails this test by default, exactly the way anchors/constraints failed
    before #420's fix.

    Three properties are what make this loop CAPABLE OF FAILING. #420's version
    had none of them and so reported green in the defective world:

      - `_leaf_texts` is TOTAL. The old `_flatten` returned [] for the nested
        contract-dict shape every populated corpus `directives` block carries,
        so the inner loop body never ran and the property asserted nothing
        about the field while reporting green.
      - the loop keeps a PER-FIELD ledger and asserts it EQUALS the set of
        populated non-excluded fields. A single `checked_any` flag for the whole
        loop let any field cover for any other, so a field the extractor read no
        text out of still passed.
      - the fixture's key set is asserted to be a SUPERSET of the engine's own
        canonical Task builder `_build_amend_task`. The loop runs over the
        FIXTURE's keys, so a field added to the engine's Task shape and
        forgotten here would be absent from the loop, absent from the ledger's
        expected set, and green -- the identical forgetting failure this class
        exists to catch.

    RESIDUAL LIMIT, stated rather than implied: the superset assertion closes
    the hole for fields the ENGINE introduces. A field introduced only by a
    template -- carried in a shipped checklist JSON but built by neither
    `_build_amend_task` nor `append()` -- is still invisible to this property
    and needs a human to add it to the fixture.

    `test_the_property_fails_when_a_populated_field_is_unrendered` below is the
    in-suite proof that the assertion path can actually go red: a property only
    ever observed passing is indistinguishable from one that cannot fail."""

    # Fields intentionally excluded from the generic content-presence loop,
    # each for a stated reason -- not because checking them is inconvenient:
    #   id, status         -- identity/control-flow, already pinned by the
    #                          ACTIVE line's own exact format (other goldens).
    #   preconditions,
    #   postconditions     -- structured list-of-dict; content checked below
    #                          by dedicated statement-text assertions, not
    #                          this generic string-flattening loop.
    #   status_detail      -- per-status bookkeeping (leases, blockers), not
    #                          narrative content the briefing prints as-is.
    #   rework_count       -- a bookkeeping counter, not caller-facing prose.
    #   result, finding    -- survey-only fields (docs/CHECKLIST_SCHEMA.md);
    #                          not applicable to a `gated` active-gate briefing.
    #   evidence           -- attached artifact records, not re-echoed
    #                          verbatim into `current`'s text.
    #   why_exempt         -- a boolean opt-out flag, not content.
    #   child_checklist    -- a work-id pointer to a different plan, not prose
    #                          content this checklist's `current` narrates.
    #   context_refs       -- a separate declared-file-manifest mechanism
    #                          (scripts/context_manifest.py), not `current`
    #                          prose.
    #   title              -- a short label, historically never part of the
    #                          briefing (redundant with `imperative`).
    # `directives` is deliberately NOT in the set below: as of #433 state()
    # reads it and render_human() prints it, so it is ordinary rendered content
    # and the generic loop carries it like anchors/constraints. It was excluded
    # under #420 only because that issue capped its authorized scope to the two
    # fields it introduced.
    _EXCLUDED_FIELDS = {
        "id", "status", "preconditions", "postconditions", "status_detail",
        "rework_count", "result", "finding", "evidence", "why_exempt",
        "child_checklist", "context_refs", "title",
    }

    @staticmethod
    def _leaf_texts(value):
        """TOTAL leaf extraction: recurse dicts and lists to any depth and
        stringify every scalar, so EVERY populated shape yields something to
        assert on. Returns [] only for None and for empty containers.

        This replaces #420's `_flatten`, which handled str / [str] /
        {category: [str]} and returned [] for everything else -- including the
        nested contract-dict shape all 8 populated corpus `directives` blocks
        carry. A field the extractor reads nothing out of is a field the
        property never checks, which is how the loop reported green while
        asserting nothing.

        Deliberately INDEPENDENT of the renderer's `_directive_leaf` /
        `_render_directive_lines`: sharing them would let one bug render nothing
        and assert nothing, in agreement, with both sides green. The one known
        divergence is a bool leaf (Python `True` here vs the renderer's JSON
        `true`); no field currently reachable by the loop carries one, and it
        would surface as a loud red rather than a silent green."""
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value else []
        if isinstance(value, dict):
            return [leaf for v in value.values()
                    for leaf in TaskFieldCompleteness._leaf_texts(v)]
        if isinstance(value, (list, tuple)):
            return [leaf for v in value
                    for leaf in TaskFieldCompleteness._leaf_texts(v)]
        return [str(value)]

    def _fully_populated_gate(self):
        """One gate carrying every field the Task shape allows, each with
        content unique enough to find in the rendered briefing."""
        t = gate("g1", "in-progress", why_exempt=False)
        # Both left OPEN (satisfied=False): render_human() only prints a
        # condition's statement while it is open (the satisfied-hiding
        # behavior is pre-existing and out of this issue's scope), so the
        # completeness check needs an open condition to see the content.
        t["preconditions"] = [{"id": "p1", "statement": "PRECOND_UNIQUE_TEXT",
                                "check": None, "satisfied": False}]
        t["postconditions"] = [{"id": "c1", "statement": "POSTCOND_UNIQUE_TEXT",
                                 "check": None, "satisfied": False}]
        t["constraints"] = ["CONSTRAINT_UNIQUE_TEXT"]
        t["anchors"] = {"structural": ["ANCHOR_UNIQUE_TEXT"]}
        # The nested contract-dict shape -- the one all 8 populated corpus
        # `directives` blocks carry, and the one the old `_flatten` returned []
        # for. A flat [str] here would pass under a non-recursive extractor and
        # so would prove nothing.
        t["directives"] = {"replan_input": {
            "template": "DIRECTIVE_TEMPLATE_UNIQUE_TEXT",
            "evidence_fields": ["DIRECTIVE_FIELD_UNIQUE_TEXT"],
        }}
        t["context_refs"] = [{"root": "repo", "path": "x", "required": True}]
        t["child_checklist"] = "some-other-work-id"
        t["evidence"] = [{"id": "e1", "type": "note", "payload": {}, "produced_by": "test", "ts": ""}]
        t["status_detail"] = {"note": "STATUS_DETAIL_UNIQUE_TEXT"}
        return t

    def _assert_every_populated_field_renders(self, t, out):
        """The property itself, factored out so the negative self-test below
        drives the REAL assertion path rather than a copy of it."""
        # Dedicated checks for the two structured, list-of-dict fields.
        self.assertIn("PRECOND_UNIQUE_TEXT", out)
        self.assertIn("POSTCOND_UNIQUE_TEXT", out)

        # Generic enumeration over everything else -- fails loud for any
        # populated, non-excluded field whose content doesn't surface. A
        # future field added to Task and left unhandled by render_human()
        # lands here by default (it is not in _EXCLUDED_FIELDS) and fails.
        expected = set()
        asserted = set()
        for field, value in t.items():
            if field in self._EXCLUDED_FIELDS or not value:
                continue
            expected.add(field)
            for text in self._leaf_texts(value):
                asserted.add(field)
                self.assertIn(
                    text, out,
                    f"populated field {field!r} (value {value!r}) has content "
                    f"{text!r} missing from current()'s output",
                )
        # The per-field ledger, NOT one flag for the whole loop: with a single
        # `checked_any`, any field could cover for any other and a field the
        # extractor read no text out of passed green.
        self.assertEqual(
            asserted, expected,
            f"populated field(s) {sorted(expected - asserted)} were carried by "
            f"the loop but asserted NOTHING -- _leaf_texts read no text out of "
            f"them, so current()'s output was never checked against their "
            f"content",
        )

    def test_every_populated_field_renders_for_a_fully_populated_gate(self):
        t = self._fully_populated_gate()
        out = E.current(gated(g1=t))
        self._assert_every_populated_field_renders(t, out)
        # Sanity: name the three fields this loop is specifically proving,
        # so a change to the fixture that accidentally drops them is loud.
        self.assertIn("CONSTRAINT_UNIQUE_TEXT", out)
        self.assertIn("ANCHOR_UNIQUE_TEXT", out)
        self.assertIn("DIRECTIVE_TEMPLATE_UNIQUE_TEXT", out)

    def test_fixture_carries_every_field_the_engines_task_builder_builds(self):
        # The hole the loop above cannot see on its own: it runs over the
        # FIXTURE's keys, so a Task field added to the engine later and
        # forgotten here is absent from the loop, absent from the ledger's
        # expected set, and passes green. Checked against the engine's OWN
        # canonical Task builder rather than docs/CHECKLIST_SCHEMA.md's Task
        # table: the table is hand-authored prose, and nothing checks it
        # against what runs (it is currently stale on the `directives` row).
        # _build_amend_task is asked for its keys rather than having them
        # re-listed here, so the enumeration cannot drift from the builder.
        built = E._build_amend_task({
            "id": "x", "title": "t", "imperative": "i",
            "postconditions": [{"id": "c1", "statement": "s",
                                 "check": None, "satisfied": False}],
        })
        missing = set(built) - set(self._fully_populated_gate())
        self.assertEqual(
            missing, set(),
            f"the engine's Task builder _build_amend_task now emits "
            f"{sorted(missing)}, which this class's fixture does not carry, so "
            f"the completeness loop would never see the field -- add it to "
            f"_fully_populated_gate() with content the briefing should show, or "
            f"to _EXCLUDED_FIELDS with a stated reason. append() mirrors the "
            f"same shape (scripts/checklist_engine.py)",
        )

    def test_the_property_fails_when_a_populated_field_is_unrendered(self):
        # The NEGATIVE self-test, and the durable machine proof that the
        # assertion path above can reach a failing state. It drives
        # _assert_every_populated_field_renders -- the same helper the positive
        # test drives, not a copy -- against a briefing rendered WITHOUT the
        # `directives` block, which is exactly what current() emitted before
        # #433 while this class reported green.
        t = self._fully_populated_gate()
        unrendered = copy.deepcopy(t)
        unrendered["directives"] = None
        out = E.current(gated(g1=unrendered))
        self.assertNotIn("DIRECTIVE_TEMPLATE_UNIQUE_TEXT", out)

        # `t` still carries the populated block, so the property is being asked
        # about a field the output does not show -- it must RAISE, and name it.
        with self.assertRaises(AssertionError) as caught:
            self._assert_every_populated_field_renders(t, out)
        self.assertIn("directives", str(caught.exception))


def _builder_task_keys():
    """The engine's own canonical Task-shape key set, asked for rather than
    re-listed here so the enumeration cannot drift from the builder (same
    approach as TaskFieldCompleteness.test_fixture_carries_every_field_the_
    engines_task_builder_builds above). `_build_amend_task` and `append()`
    both delegate to `_new_task` as of #474, so either call site's output has
    the identical key set."""
    built = E._build_amend_task({
        "id": "x", "title": "t", "imperative": "i",
        "postconditions": [{"id": "c1", "statement": "s",
                             "check": None, "satisfied": False}],
    })
    return set(built)


def _collect_shipped_task_fields():
    """Walk every shipped gated/survey checklist template
    (skills/*/templates/*.template.json) and union every key any `tasks`
    dict entry carries. This is the real corpus TaskFieldCompleteness's own
    RESIDUAL LIMIT says nothing checks: a field a template carries but
    neither `_build_amend_task` nor `append()` builds."""
    fields = set()
    for path in sorted(ROOT.glob("skills/*/templates/*.template.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("type") not in ("gated", "survey"):
            continue
        tasks = data.get("tasks", {})
        if not isinstance(tasks, dict):
            continue
        for task in tasks.values():
            if isinstance(task, dict):
                fields |= set(task.keys())
    return fields


def _assert_task_fields_allowed(fields, allowlist, label):
    """The shared assertion both the negative self-test and the positive
    corpus test drive -- not a copy of it -- so a bug in one is a bug in
    both. Anything in `fields` that is neither engine-built nor on the
    stated `allowlist` is unaccounted for and fails loudly, naming it."""
    unaccounted = fields - (_builder_task_keys() | allowlist)
    assert not unaccounted, (
        f"{label}: field(s) {sorted(unaccounted)} are neither built by the "
        f"engine's Task constructor (_new_task) nor on the stated "
        f"template-only allowlist -- add them to the allowlist with a "
        f"stated reason, or fix the producer"
    )


class TemplateOnlyFieldAllowlist(unittest.TestCase):
    """#475: TaskFieldCompleteness's own stated RESIDUAL LIMIT (above) says a
    field introduced only by a shipped template -- carried in a checklist JSON
    but built by neither `_build_amend_task` nor `append()` -- is invisible to
    that property and needs a human to add it. This class closes that hole: a
    walker over the real shipped templates plus a superset assertion against
    (the engine's own Task builder keys) union (a small, stated allowlist of
    template-only fields), so a genuinely new template-only field fails
    loudly instead of silently passing.

    RED-BEFORE-GREEN (NOT OVERRIDABLE per the issue): the negative self-test
    below was written and run FIRST, before `_assert_task_fields_allowed` or
    `_collect_shipped_task_fields` existed, and observed failing with
    `NameError: name '_assert_task_fields_allowed' is not defined` -- proof
    the check can fail on a planted field before it ships, not just pass by
    construction. Only after that red was the helper implemented."""

    ALLOWLIST = {
        "anchors", "context_refs", "why_exempt",
        "context_headroom_tokens", "context_headroom_note", "kind",
        # #634/g2: template-only declaration read by checklist_engine.py's
        # _is_bookend -- never built by _new_task/_build_amend_task, only
        # ever landed by a template author or the rescope-overwritable path.
        "bookend",
        # Template-only prose parked beside the imperative it qualifies, for
        # whoever EDITS the step's check -- same role as
        # `context_headroom_note`, and read by no code at all. `render_human`
        # emits a fixed field set, so it never reaches a run;
        # tests/test_map_contract_wiring.py pins both that invisibility and
        # the reasoning the note has to keep carrying.
        "map_check_note",
    }

    def test_negative_self_test_catches_a_synthetic_planted_field(self):
        planted = _builder_task_keys() | {"totally_synthetic_field_zzqx"}
        with self.assertRaises(AssertionError) as caught:
            _assert_task_fields_allowed(
                planted, self.ALLOWLIST, "synthetic plant")
        self.assertIn("totally_synthetic_field_zzqx", str(caught.exception))

    def test_shipped_templates_carry_no_unaccounted_task_fields(self):
        # The real corpus walk: every `tasks` dict key across every shipped
        # gated/survey template must be builder-emitted or on the allowlist.
        shipped_fields = _collect_shipped_task_fields()
        _assert_task_fields_allowed(
            shipped_fields, self.ALLOWLIST, "shipped templates")


def _doc_task_field_table():
    """Parse docs/CHECKLIST_SCHEMA.md's `## Task` section field table (the
    `| field | type | notes |` rows between the `## Task` header and the
    next `## ` header) into a set of field names. Reads the `` `field` ``
    column of every row shaped like a table data row -- the header and
    separator rows don't backtick-quote a field name, so they never match."""
    path = ROOT / "docs" / "CHECKLIST_SCHEMA.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "## Task")
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    fields = set()
    for line in lines[start:end]:
        m = re.match(r"\|\s*`([A-Za-z_]+)`\s*\|", line)
        if m:
            fields.add(m.group(1))
    return fields


def _assert_doc_reconciles_with_builder(doc_fields, builder_keys, allowlist, label):
    """The shared reconciliation assertion both the negative self-test and
    the positive doc-vs-builder test drive -- not a copy of it. Two
    directions, matching the issue's own stated check: every builder field
    must be documented, and every documented field must be either
    builder-emitted or on the stated template-only allowlist. This makes the
    doc VERIFIABLE against what the engine builds, not authoritative over
    it (#433 g3) -- a field the allowlist carries but the doc omits is not
    itself a failure here."""
    undocumented_builder = builder_keys - doc_fields
    unaccounted_doc = doc_fields - (builder_keys | allowlist)
    assert not undocumented_builder and not unaccounted_doc, (
        f"{label}: builder field(s) {sorted(undocumented_builder)} are not "
        f"documented in CHECKLIST_SCHEMA.md's Task table; documented "
        f"field(s) {sorted(unaccounted_doc)} are neither builder-emitted "
        f"nor on the stated template-only allowlist"
    )


class SchemaDocFieldReconciliation(unittest.TestCase):
    """#476: docs/CHECKLIST_SCHEMA.md's `## Task` field table is hand-authored
    prose that nothing checks against what the engine actually builds
    (#433's g3 finding, quoted in the issue). This test makes the table
    VERIFIABLE, not authoritative: a drift check between the doc and
    `_new_task`'s real key set (plus m2-475's `TemplateOnlyFieldAllowlist.
    ALLOWLIST`), never a new source of truth the engine is bound by.

    RED-BEFORE-GREEN: the negative self-test drives the SAME
    `_assert_doc_reconciles_with_builder` helper the positive test drives,
    against a synthetic field set missing one real builder field
    (`status`), and confirms it raises naming that field -- proof the
    reconciliation can actually fail, not just pass by construction."""

    def test_negative_self_test_catches_an_undocumented_builder_field(self):
        doc_fields = _doc_task_field_table() - {"status"}
        with self.assertRaises(AssertionError) as caught:
            _assert_doc_reconciles_with_builder(
                doc_fields, _builder_task_keys(),
                TemplateOnlyFieldAllowlist.ALLOWLIST, "synthetic plant")
        self.assertIn("status", str(caught.exception))

    def test_schema_doc_task_table_reconciles_with_the_builder(self):
        _assert_doc_reconciles_with_builder(
            _doc_task_field_table(), _builder_task_keys(),
            TemplateOnlyFieldAllowlist.ALLOWLIST,
            "CHECKLIST_SCHEMA.md Task table")


class Inv1CompletenessOracle(unittest.TestCase):
    """#227 g2 constraint 3 (INV-1, completeness): current()'s output must be a
    superset of every argument the caller's ACTUAL next legal verb needs. The
    map below is HAND-AUTHORED against the verbs' RUNTIME bodies:

      - advance --why: optional at parse_args() (~line 1668) but REQUIRED at
        runtime unless --mechanical or the gate is why_exempt — see advance()
        ~1077-1087 (`raise EngineError(...)` on a why-less non-exempt advance).
      - attest --evidence: optional at parse_args() (~line 1715) but REQUIRED
        at runtime whenever the condition's check.kind == "artifact" — see
        attest() ~1539-1544 (`raise EngineError(...)` with no --evidence).

    A map built by walking `parser._actions` for `required=True` would omit
    BOTH of these — exactly the two args agents most often re-open source to
    discover. This test does not call any engine map or read state()'s
    next_verbs list; it inspects the rendered current() STRING directly, so it
    cannot be a self-confirming fixture.

    Rework 1 (g2 review BLOCK) split this into TWO scenarios instead of one:
    while an open artifact-kind postcondition is unresolved, `advance` is not
    yet the caller's legal next verb at all (only `attest --evidence` is), so
    a single gate can't exercise both `--evidence` and `--why` truthfully at
    once — the original combined test's premise ("advance is always next") was
    exactly the bug this rework fixes."""

    VERB_REQUIRED_ARGS = {
        "start": [("id", "always")],
        "advance": [
            ("id", "always"),
            ("why", lambda t, c=None: not bool(t.get("why_exempt"))),
        ],
        "attest": [
            ("id", "always"), ("cond", "always"), ("which", "always"),
            ("evidence", lambda t, c: (c or {}).get("check", {}).get("kind") == "artifact"),
        ],
        "waive": [("id", "always"), ("cond", "always"), ("which", "always"), ("authority", "always")],
    }

    def test_current_output_covers_attest_evidence_when_that_is_the_legal_move(self):
        # An in-progress gate with ONE open artifact-kind postcondition (not
        # just a null-check gate, per the handoff's instruction): `attest
        # --evidence` is the legal next move; `advance` is NOT (it would
        # refuse), so current() must not need to carry --why here at all.
        t = gate("g1", "in-progress", why_exempt=False)
        cond = {
            "id": "c1", "statement": "approved",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        }
        t["postconditions"] = [cond]
        cl = gated(g1=t)
        out = E.current(cl)

        self.assertIn("g1", out)  # `id` is required by every verb in the map
        for argname, rule in self.VERB_REQUIRED_ARGS["attest"]:
            if not (rule == "always" or rule(t, cond)):
                continue
            if argname == "cond":
                self.assertIn(cond["id"], out, "attest --cond value missing from current()")
            elif argname == "which":
                self.assertIn("postconditions", out, "attest --which value ('postconditions') missing")
            elif argname == "evidence":
                self.assertIn("--evidence", out, "attest --evidence flag missing though c1 is artifact-kind")
        # advance is not yet legal from here -> must not be suggested at all.
        self.assertNotIn("advance g1", out)

    def test_current_output_covers_advance_why_once_it_is_the_legal_move(self):
        # A non-exempt in-progress gate with NO open null/artifact condition
        # left (a live command postcondition is present but never blocks, per
        # _blocking_conditions): `advance --why` IS the legal next move now.
        t = gate("g1", "in-progress", why_exempt=False, command=PASS_COMMAND)
        cl = gated(g1=t)
        out = E.current(cl)

        self.assertIn("g1", out)
        for argname, rule in self.VERB_REQUIRED_ARGS["advance"]:
            if argname == "why" and (rule == "always" or rule(t)):
                self.assertIn("--why", out, "advance --why flag missing though g1 is not why_exempt")


class Inv2PurityNoSubprocess(unittest.TestCase):
    """#227 g2 constraint 2 (INV-2, purity): state()/current() must NEVER
    invoke subprocess for a command/git-change-policy check — reading state is
    not a probe. Patches subprocess.run to explode if called, drives current()
    over a spine full of command- and git-change-policy-kind conditions
    recorded as unsatisfied, and asserts it renders (without raising from
    current() itself) while subprocess.run is never reached."""

    def test_current_never_invokes_subprocess(self):
        pre = [{"id": "p1", "statement": "iface exists",
                "check": {"kind": "command", "command": FAIL_COMMAND}, "satisfied": False}]
        t = gate("g1", "in-progress", preconds=pre)
        t["postconditions"] = [
            {"id": "c1", "statement": "tests pass",
             "check": {"kind": "command", "command": FAIL_COMMAND}, "satisfied": False},
            {"id": "c2", "statement": "no suspicious artifacts",
             "check": {"kind": "git-change-policy", "mode": "staged"}, "satisfied": False},
        ]
        cl = gated(g1=t)

        with mock.patch.object(
            E.subprocess, "run",
            side_effect=AssertionError("current()/state() must never invoke subprocess.run (INV-2)"),
        ):
            out = E.current(cl)  # would raise AssertionError if subprocess.run were called

        self.assertIn("p1 [unmet] command", out)
        self.assertIn("c1 [unmet] command", out)
        self.assertIn("c2 [unmet] git-change-policy", out)


class LegacySpineBackwardCompat(unittest.TestCase):
    """#227 g2 constraint 5: a REAL captured, organically-evolved spine (no
    why_trail key at all, no why_exempt on any task) must render through
    current()/state() WITHOUT EVER RAISING. This engine drives live runs right
    now, including the one that dispatched this change; a KeyError on real
    data would break work in flight. The fixture is a read-only COPY of a real
    explorer spine.json (constellation-skills .agent-work archive) — never
    mutated with a live/mutating engine verb; any status flip below is a
    plain in-memory dict edit on the copy, not an engine call."""

    FIXTURE = ROOT / "tests" / "fixtures" / "legacy_spine_organic.json"

    def test_fixture_is_genuinely_legacy_shaped(self):
        cl = E.load(self.FIXTURE)
        self.assertNotIn("why_trail", cl)
        self.assertTrue(all("why_exempt" not in t for t in cl["tasks"].values()))

    def test_all_terminal_shape_renders_done_without_raising(self):
        cl = E.load(self.FIXTURE)
        out = E.current(cl)  # must not raise
        self.assertIn("DONE: no open items.", out)
        self.assertIn("LEASE released:", out)

    def test_state_projection_renders_on_all_terminal_shape(self):
        cl = E.load(self.FIXTURE)
        view = E.state(cl)  # must not raise
        self.assertIsNone(view["active"])
        self.assertEqual(view["kind"], "gated")

    def test_status_flip_renders_active_branch_on_real_condition_data(self):
        # In-memory-only status flip (not a `reopen` engine call) so the ACTIVE
        # branch renders against a real historic task missing why_exempt.
        cl = E.load(self.FIXTURE)
        cl["tasks"]["route"]["status"] = "in-progress"
        out = E.current(cl)  # must not raise despite the missing why_exempt key
        # a released-lease line still precedes the ACTIVE line (see LEASE tests
        # elsewhere), so check containment, not startswith, here.
        self.assertIn("ACTIVE route", out)
        self.assertIn("met", out)

    def test_reopened_gate_with_unmet_condition_renders_kind_and_real_statement(self):
        cl = E.load(self.FIXTURE)
        t = cl["tasks"]["init"]
        t["status"] = "in-progress"
        t["postconditions"][0]["satisfied"] = False  # c1: check.kind == "command"
        out = E.current(cl)  # must not raise
        self.assertIn("ACTIVE init", out)
        self.assertIn(
            "c1 [unmet] command — work area scaffolded and spine.json materialized", out)


class NextVerbsAreLegalFromHere(unittest.TestCase):
    """Rework 1 (#227 g2 review BLOCK): `next:` must only suggest a verb that
    will NOT refuse from the state it renders — the ratified panel's invariant
    4 ("next_verbs is exhaustive and legal-from-here… derived from (status,
    position, condition state)"), which the pre-fix `_next_verbs()` violated.
    The reviewer reproduced two concrete refusals: a pending gate with an open
    null precondition suggested `start` (refused: preconditions unmet), and a
    non-exempt in-progress gate with an open artifact postcondition suggested
    `advance` (refused: postconditions unmet) — against the implementer's own
    two canonical golden fixtures.

    This closes the loop the golden (string-only) tests didn't: for a matrix
    of task states and condition mixes, it ACTUALLY RUNS the verb `next:`
    suggests against a tmp in-memory fixture (never a real spine file) and
    asserts it does not raise `EngineError` — plus proves the terminal verb is
    SUPPRESSED while a blocking null/artifact condition is open, and NOT
    suppressed by an open command/git-change-policy condition (those are
    live-checked inside start()/advance() itself, never probed by state())."""

    def _next(self, cl, aid):
        return E.state(cl)["active"]["next_verbs"]

    # --- start() is gated on PREconditions ---------------------------------- #
    def test_pending_with_open_null_precondition_suppresses_start(self):
        pre = [{"id": "p1", "statement": "upstream done", "check": None, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        verbs = self._next(cl, "g1")
        self.assertFalse(any(v.startswith("start ") for v in verbs),
                          f"start suggested despite an open null precondition: {verbs}")
        self.assertTrue(any(v.startswith("attest g1 --cond p1") for v in verbs))
        # The ONE verb actually suggested must not raise.
        E.attest(copy.deepcopy(cl), "g1", "p1", "preconditions", "checked it")

    def test_pending_with_open_artifact_precondition_suppresses_start_until_attested(self):
        pre = [{
            "id": "p1", "statement": "reviewed",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        }]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        self.assertFalse(any(v.startswith("start ") for v in self._next(cl, "g1")))
        # Run the suggested attest --evidence for real, then confirm the
        # previously-suppressed `start` reappears AND actually succeeds.
        work = copy.deepcopy(cl)
        E.attach(work, "g1", "review-result", {"verdict": "APPROVE"})
        eid = work["tasks"]["g1"]["evidence"][-1]["id"]
        E.attest(work, "g1", "p1", "preconditions", None, evidence_id=eid)  # must not raise
        self.assertTrue(any(v.startswith("start ") for v in self._next(work, "g1")))
        self.assertEqual(E.start(work, "g1"), "g1 -> in-progress")  # must not raise

    def test_pending_with_only_open_command_precondition_still_suggests_start(self):
        # command-kind preconditions are engine-checked LIVE at start(); state()
        # never probes them (INV-2), so an open one must NOT suppress the hint.
        pre = [{"id": "p1", "statement": "tests pass", "check": {"kind": "command", "command": PASS_COMMAND}, "satisfied": False}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        verbs = self._next(cl, "g1")
        self.assertTrue(any(v.startswith("start ") for v in verbs), f"start missing: {verbs}")
        self.assertEqual(E.start(copy.deepcopy(cl), "g1"), "g1 -> in-progress")  # no raise: command passes live

    def test_pending_with_satisfied_preconditions_suggests_start_and_it_runs(self):
        pre = [{"id": "p1", "statement": "upstream done", "check": None, "satisfied": True, "satisfied_by": "attested"}]
        cl = gated(g1=gate("g1", "pending", preconds=pre))
        self.assertIn("start g1", self._next(cl, "g1"))
        self.assertEqual(E.start(copy.deepcopy(cl), "g1"), "g1 -> in-progress")  # no raise

    # --- advance() is gated on POSTconditions -------------------------------- #
    def test_in_progress_with_open_null_postcondition_suppresses_advance(self):
        t = gate("g1", "in-progress", why_exempt=True)
        t["postconditions"] = [{"id": "c1", "statement": "reviewed", "check": None, "satisfied": False}]
        cl = gated(g1=t)
        verbs = self._next(cl, "g1")
        self.assertFalse(any(v.startswith("advance ") for v in verbs),
                          f"advance suggested despite an open null postcondition: {verbs}")
        self.assertTrue(any(v.startswith("attest g1 --cond c1") for v in verbs))
        E.attest(copy.deepcopy(cl), "g1", "c1", "postconditions", "verified")  # must not raise

    def test_in_progress_with_open_artifact_postcondition_suppresses_advance_until_attested(self):
        t = gate("g1", "in-progress", why_exempt=False)
        t["postconditions"] = [{
            "id": "c1", "statement": "approved",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        }]
        cl = gated(g1=t)
        self.assertFalse(any(v.startswith("advance ") for v in self._next(cl, "g1")),
                          "advance suggested despite an open artifact postcondition")
        # Run the suggested attest --evidence for real, then confirm the
        # previously-suppressed `advance` reappears AND actually succeeds.
        work = copy.deepcopy(cl)
        E.attach(work, "g1", "review-result", {"verdict": "APPROVE"})
        eid = work["tasks"]["g1"]["evidence"][-1]["id"]
        E.attest(work, "g1", "c1", "postconditions", None, evidence_id=eid)  # must not raise
        self.assertTrue(any(v.startswith("advance ") for v in self._next(work, "g1")))
        self.assertEqual(E.advance(work, "g1", why="cleared the blocker"), "g1 -> complete")  # no raise

    def test_in_progress_with_only_open_command_postcondition_still_suggests_advance(self):
        t = gate("g1", "in-progress", why_exempt=True, command=PASS_COMMAND)
        cl = gated(g1=t)
        verbs = self._next(cl, "g1")
        self.assertTrue(any(v.startswith("advance ") for v in verbs), f"advance missing: {verbs}")
        self.assertEqual(E.advance(copy.deepcopy(cl), "g1"), "g1 -> complete")  # no raise: command passes live

    def test_in_progress_non_exempt_advance_hint_carries_why_and_runs(self):
        t = gate("g1", "in-progress", why_exempt=False, command=PASS_COMMAND)
        cl = gated(g1=t)
        verbs = self._next(cl, "g1")
        advance_hint = next(v for v in verbs if v.startswith("advance "))
        self.assertIn("--why", advance_hint)
        self.assertEqual(
            E.advance(copy.deepcopy(cl), "g1", why="test understanding"), "g1 -> complete")  # no raise

    # --- resume()/record() hints are never suppressed by open conditions ----- #
    # resume() genuinely carries no condition gate. record() DOES carry one
    # since #422/#328 (`--result pass` vs `command`-kind postconditions), but it
    # is command-kind only -- the class _blocking_conditions() excludes under
    # INV-2 -- and `--result fail` is ungated, so the hint stands either way.
    # See tests/test_next_verbs_record_gate_comment.py (#437).
    def test_blocked_resume_hint_runs(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.block(cl, "g1", "waiting on x1 result", "parent agent", "escalate; do not re-dispatch")
        verbs = self._next(cl, "g1")
        self.assertTrue(any(v.startswith("resume ") for v in verbs))
        self.assertEqual(
            E.resume(copy.deepcopy(cl), "g1", reason="blocker cleared"),
            "g1 resumed -> in-progress (blocker resolved: blocker cleared)")  # no raise

    def test_survey_in_progress_record_hint_runs_even_with_open_null_postcondition(self):
        # A `null`-kind postcondition is one record() does not evaluate at all
        # (#422/#328 scoped its check to `command`-kind), so unlike advance()
        # the hint is present AND runnable despite this condition being open.
        cl = survey(v1=survey_item("v1", "in-progress"))
        cl["tasks"]["v1"]["postconditions"] = [{"id": "c1", "statement": "checked", "check": None, "satisfied": False}]
        verbs = self._next(cl, "v1")
        self.assertTrue(any(v.startswith("record ") for v in verbs), f"record missing: {verbs}")
        self.assertEqual(E.record(copy.deepcopy(cl), "v1", "pass", None), "v1 recorded pass")  # no raise


class TestGlobToRegex(unittest.TestCase):
    """Direct tests of `_glob_to_regex` (scripts/checklist_engine.py:449), which
    had zero direct coverage before this class (only reached indirectly through
    `_glob_match`, which layers a different concern -- basename fallback -- on
    top). `_glob_to_regex` itself is frozen this run; every assertion here
    exercises the returned regex string's *matching behavior* via `re.match`
    against representative subjects, not a string-diff against a hand-derived
    regex literal (which would be brittle to harmless reformatting of the
    implementation's regex-building)."""

    # Dimension: literal chars -- non-special characters pass through
    # `re.escape`'d, so regex-meta characters in the pattern (`.`, `+`) match
    # only themselves, not their regex meta-meaning.
    def test_glob_to_regex_literal_chars_are_escaped(self):
        regex = E._glob_to_regex("a.b")
        self.assertIsNotNone(re.match(regex, "a.b"))
        # Unescaped, "." would also match any single char -- confirm it doesn't.
        self.assertIsNone(re.match(regex, "axb"))

        regex = E._glob_to_regex("a+b")
        self.assertIsNotNone(re.match(regex, "a+b"))
        # Unescaped, "+" would mean one-or-more of the preceding char.
        self.assertIsNone(re.match(regex, "aaab"))

    # Dimension: single `*` -- matches within one path segment only
    # ([^/]*); must NOT cross a `/`.
    def test_glob_to_regex_single_star_matches_within_segment_only(self):
        regex = E._glob_to_regex("a*b")
        self.assertIsNotNone(re.match(regex, "ab"))     # zero chars
        self.assertIsNotNone(re.match(regex, "axxb"))   # several chars
        self.assertIsNone(re.match(regex, "a/xb"))      # does not cross '/'
        self.assertIsNone(re.match(regex, "ax/b"))

    # Dimension: `**` -- crosses segments (`.*`) when not immediately
    # followed by `/`.
    def test_glob_to_regex_double_star_crosses_segments(self):
        regex = E._glob_to_regex("x**y")
        self.assertIsNotNone(re.match(regex, "xy"))       # zero chars
        self.assertIsNotNone(re.match(regex, "xay"))      # one char
        self.assertIsNotNone(re.match(regex, "xa/by"))    # crosses a separator

    # Dimension: `**` -- leading `**/` form: zero-or-more leading segments
    # ((?:.*/)?).
    def test_glob_to_regex_leading_double_star_slash_matches_zero_or_more_leading_segments(self):
        regex = E._glob_to_regex("**/b")
        self.assertIsNotNone(re.match(regex, "b"))        # zero leading segments
        self.assertIsNotNone(re.match(regex, "a/b"))      # one leading segment
        self.assertIsNotNone(re.match(regex, "a/c/b"))    # two leading segments
        self.assertIsNone(re.match(regex, "ab"))          # not a segment boundary

    # Dimension: `**` -- trailing `/**` form also matches the directory
    # itself ((?:/.*)?): `records/**` must cover `records/x` AND
    # `records/a/b`, per the function's own docstring.
    def test_glob_to_regex_trailing_slash_double_star_also_matches_directory_itself(self):
        regex = E._glob_to_regex("records/**")
        self.assertIsNotNone(re.match(regex, "records"))       # the dir itself
        self.assertIsNotNone(re.match(regex, "records/x"))     # one level deep
        self.assertIsNotNone(re.match(regex, "records/a/b"))   # nested
        self.assertIsNone(re.match(regex, "recordsX"))         # not a sibling

    # Dimension: `?` -- matches exactly one non-separator char ([^/]); must
    # NOT match `/` and must NOT match zero or two chars.
    def test_glob_to_regex_question_mark_matches_exactly_one_non_separator_char(self):
        regex = E._glob_to_regex("a?b")
        self.assertIsNotNone(re.match(regex, "axb"))   # exactly one char
        self.assertIsNone(re.match(regex, "ab"))       # zero chars
        self.assertIsNone(re.match(regex, "axyb"))     # two chars
        self.assertIsNone(re.match(regex, "a/b"))      # separator doesn't count

    # Dimension: empty pattern -- `""` produces `"^$"`, matching only the
    # empty string.
    def test_glob_to_regex_empty_pattern_matches_only_empty_string(self):
        regex = E._glob_to_regex("")
        self.assertEqual(regex, "^$")
        self.assertIsNotNone(re.match(regex, ""))
        self.assertIsNone(re.match(regex, "a"))

    # Dimension: anchoring -- the returned regex is always `^...$` (full
    # string match); it must not match as a substring of a longer string it
    # is not equal to.
    def test_glob_to_regex_anchoring_requires_full_string_match(self):
        regex = E._glob_to_regex("abc")
        self.assertIsNotNone(re.match(regex, "abc"))
        self.assertIsNone(re.match(regex, "abcx"))   # trailing extra chars
        self.assertIsNone(re.match(regex, "xabc"))   # leading extra chars
        self.assertIsNone(re.match(regex, "xabcx"))  # substring in the middle

    # Dimension: path-separator handling -- `/` in the pattern is a literal
    # `/` in the output (outside the `/**` trailing-suffix special case
    # covered separately above).
    def test_glob_to_regex_path_separator_is_literal(self):
        regex = E._glob_to_regex("a/b")
        self.assertIsNotNone(re.match(regex, "a/b"))
        self.assertIsNone(re.match(regex, "ab"))    # separator is required
        self.assertIsNone(re.match(regex, "aXb"))   # not interchangeable with any char


class TripLedgerRecordsBeginsOverTheLine(unittest.TestCase):
    """#467 (a) — the engine-only, append-only trip ledger.

    The discriminating question this epic is about is NOT "did a handoff artifact
    appear before the next advance" (`advance` already refuses a non-exempt gate
    with no `--why`, so that is true in BOTH worlds and discriminates nothing). It
    is: **did anyone BEGIN work while over the line?** Every test below is a
    two-world pair — the defective spine AND its healthy counterpart — and names
    the field that differs. A test that only asserted the defective side could not
    fail.

    Names match the frozen `g4-integrate` closeout selector (`ledger`).
    """

    MODEL = "claude-opus-4-8"

    def setUp(self):
        self.soft, self.hard = E._gauge_reader.thresholds_for(self.MODEL)
        self.over_hard = min(self.hard + 0.05, 1.0)
        self.under_hard = max(self.hard - 0.001, 0.0)

    def _three_gates(self):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def _g2_pending_after_g1(self):
        """g1 closed with a real understanding (-> w-1); g2 pending, so `start g2`
        is a genuine BEGIN-work move and the live why-record is w-1."""
        cl = self._three_gates()
        E.advance(cl, "g1", why="u1")
        return cl

    def _ledger(self, cl):
        return cl.get("override_ledger")

    # --- shape 1: an over-the-line BEGIN that was REFUSED -------------------- #
    def test_ledger_begin_refused_is_recorded_and_the_healthy_world_records_nothing(self):
        """DEFECTIVE: the agent is told to wrap up, closes g1 — and then begins g2
        anyway. HEALTHY: same spine, same gauge, the agent closes g1 and STOPS.
        Differing field: `override_ledger` (absent vs one `begin-refused` entry)."""
        # healthy world — told to wrap up, wrapped up, stopped.
        healthy = self._three_gates()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            msg = E.dispatch(healthy, _advance_ns("g1", why="wrapping up at g1"),
                             base_dir=Path("."))
        self.assertTrue(msg.endswith("g1 -> complete"), msg)
        self.assertIsNone(self._ledger(healthy))          # <-- the differing field

        # defective world — same close, then a BEGIN over the line.
        defective = self._three_gates()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            E.dispatch(defective, _advance_ns("g1", why="wrapping up at g1"), base_dir=Path("."))
            with self.assertRaises(E.EngineError):
                E.dispatch(defective, _start_ns("g2"), base_dir=Path("."))
        led = self._ledger(defective)                     # <-- the differing field
        self.assertIsInstance(led, list)
        self.assertEqual(len(led), 1)
        self.assertEqual(led[0]["outcome"], "begin-refused")
        self.assertEqual(led[0]["gate"], "g2")
        self.assertEqual(led[0]["verb"], "start")
        # the refusal still stands: the ledger records the attempt, it does not permit it
        self.assertEqual(defective["tasks"]["g2"]["status"], "pending")

    # --- shape 2: an over-the-line BEGIN that was RELEASED ------------------- #
    def test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line(self):
        """Both worlds run the IDENTICAL command on the IDENTICAL spine and both
        succeed — g1 goes back to `in-progress` either way. The ONLY difference is
        which side of the hard line the gauge reads. Differing field: `override_ledger`
        (absent below the line vs one `begin-released` entry over it).

        #510: the begin exercised here is a `reopen`, which the HARD advisory never
        instructs — it drives a COMPLETE gate back to in-progress and cascades
        downstream, so it is a genuine begin-work-you-cannot-finish move. This test
        used to run `start g2`, which is now the ONE begin the advisory itself
        mandates at a pending gate and is therefore recorded as `begin-instructed`
        (see `TripInstructedBeginIsNotAnOffence`). The released-begin guarantee this
        test exists for is unchanged; only the verb that still earns it is."""
        def _run(fill):
            cl = self._g2_pending_after_g1()
            E.attach(cl, "g1", "refresh-request", {"seam": "g1", "why_ref": "w-1"})
            with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
                E.dispatch(cl, _reopen_ns("g1", reason="rework"), base_dir=Path("."))
            self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
            return cl

        healthy = _run(self.under_hard)
        self.assertIsNone(self._ledger(healthy))          # <-- the differing field

        defective = _run(self.over_hard)
        led = self._ledger(defective)                     # <-- the differing field
        self.assertIsInstance(led, list)
        self.assertEqual(len(led), 1)
        self.assertEqual(led[0]["outcome"], "begin-released")
        self.assertEqual(led[0]["gate"], "g1")
        self.assertEqual(led[0]["verb"], "reopen")

    # --- the entry's own shape ---------------------------------------------- #
    def test_ledger_entry_carries_every_field_including_the_live_why_ref(self):
        cl = self._g2_pending_after_g1()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        entry = cl["override_ledger"][0]
        self.assertEqual(
            set(entry),
            {"id", "kind", "gate", "verb", "outcome", "fill", "hard", "model", "why_ref", "ts"})
        self.assertEqual(entry["id"], "ov-1")
        self.assertEqual(entry["kind"], "trip")
        self.assertEqual(entry["model"], self.MODEL)
        self.assertEqual(entry["why_ref"], "w-1")
        self.assertAlmostEqual(entry["fill"], self.over_hard, places=4)
        self.assertAlmostEqual(entry["hard"], self.hard, places=4)
        # `ts` is a real engine timestamp, not a placeholder string
        self.assertTrue(datetime.fromisoformat(entry["ts"]))

    def test_ledger_records_the_per_gate_hard_line_not_a_global_constant(self):
        """POSITIVE CONTROL for the `hard` field. Asserting `hard == self.hard`
        above would still pass against a writer that stored one frozen number, so
        this asserts the recorded `hard` MOVES with the begun gate's own headroom
        reserve — the per-gate line the agent was actually judged against."""
        cl = self._g2_pending_after_g1()
        cl["tasks"]["g2"]["context_headroom_tokens"] = 30_000
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        entry = cl["override_ledger"][0]
        _, tightened = E._gauge_reader.thresholds_for(self.MODEL, 30_000)
        self.assertAlmostEqual(entry["hard"], tightened, places=4)
        self.assertNotAlmostEqual(entry["hard"], self.hard, places=4)

    # --- append-only --------------------------------------------------------- #
    def test_ledger_is_append_only_across_repeated_begins(self):
        cl = self._g2_pending_after_g1()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
            first = copy.deepcopy(cl["override_ledger"][0])
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _reopen_ns("g1", reason="rework"), base_dir=Path("."))
            E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
            E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        led = cl["override_ledger"]
        self.assertEqual(len(led), 3)  # the count this guard looped over
        self.assertEqual([e["id"] for e in led], ["ov-1", "ov-2", "ov-3"])
        self.assertEqual([e["verb"] for e in led], ["start", "reopen", "start"])
        # #510: the third begin is the `start` of the pending ACTIVE gate with a
        # matching request on file — the one the HARD advisory itself instructs — so
        # it is recorded under its own outcome rather than as an over-the-line
        # begin. Append-only is the property under test and it holds across all
        # three kinds; the released case is pinned by the two tests above.
        self.assertEqual([e["outcome"] for e in led],
                         ["begin-refused", "begin-refused", "begin-instructed"])
        self.assertEqual(led[0], first)  # the earliest entry was never mutated

    # --- end to end through the CLI ------------------------------------------ #
    def _write_gauge(self, d, fill, observed_at):
        (Path(d) / "gauge.json").write_text(json.dumps({
            "schema_version": 1, "fill_fraction": fill,
            "model": self.MODEL, "observed_at": observed_at,
        }), encoding="utf-8")

    def _cli_spine(self, d):
        f = Path(d) / "spine.json"
        E.save(f, self._three_gates())
        # close g1 with a real understanding BEFORE any gauge exists -> w-1
        self.assertEqual(E.main(["--file", str(f), "advance", "g1", "--why", "u1"]), 0)
        return f

    def test_ledger_begin_refused_survives_the_raise_through_the_cli(self):
        """`main()` persists on the EngineError path for any verb that is not
        `current` and not `--dry-run`, which is what makes a `begin-refused` entry
        durable even though the verb raised. Proved end to end, from the file on
        disk — not by calling the function directly.

        Two worlds, same command: a FRESH over-hard gauge vs a STALE one (which the
        reader discards, so the band is inactive). Differing field: `override_ledger`
        on the reloaded file."""
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            f = self._cli_spine(d)
            stale = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            self._write_gauge(d, min(self.hard + 0.05, 1.0), stale)
            self.assertEqual(E.main(["--file", str(f), "start", "g2"]), 0)  # healthy
            healthy = E.load(f)
            self.assertIsNone(healthy.get("override_ledger"))   # <-- the differing field

        with tempfile.TemporaryDirectory() as d:
            f = self._cli_spine(d)
            self._write_gauge(d, min(self.hard + 0.05, 1.0),
                              datetime.now(timezone.utc).isoformat())
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = E.main(["--file", str(f), "start", "g2"])
            self.assertEqual(rc, 1)
            self.assertIn("REFUSED:", err.getvalue())
            defective = E.load(f)
            led = defective.get("override_ledger")             # <-- the differing field
            self.assertIsInstance(led, list)
            self.assertEqual(len(led), 1)
            self.assertEqual(led[0]["outcome"], "begin-refused")
            self.assertEqual(led[0]["gate"], "g2")
            self.assertEqual(led[0]["verb"], "start")
            self.assertEqual(led[0]["why_ref"], "w-1")
            self.assertEqual(defective["tasks"]["g2"]["status"], "pending")

    def test_ledger_begin_released_is_recorded_through_the_cli(self):
        """#510: `reopen`, not `start` — same reason as the in-process released-begin
        test above. A `start` of the pending active gate with a request on file is
        the begin the advisory itself instructs and is recorded as
        `begin-instructed`; every other released begin still lands here."""
        with tempfile.TemporaryDirectory() as d:
            f = self._cli_spine(d)
            self._write_gauge(d, min(self.hard + 0.05, 1.0),
                              datetime.now(timezone.utc).isoformat())
            self.assertEqual(
                E.main(["--file", str(f), "attach", "g1", "--type", "refresh-request",
                        "--field", "seam=g1", "--field", "why_ref=w-1"]), 0)
            self.assertEqual(
                E.main(["--file", str(f), "reopen", "g1", "--reason", "rework"]), 0)
            cl = E.load(f)
            self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
            led = cl.get("override_ledger")
            self.assertIsInstance(led, list)
            self.assertEqual(len(led), 1)
            self.assertEqual(led[0]["outcome"], "begin-released")
            self.assertEqual(led[0]["gate"], "g1")


class TripLedgerComplianceSignal(unittest.TestCase):
    """#467 (b) — the compliance signal: a PURE selector over the stored ledger,
    keyed to the LIVE understanding. Its emptiness is the predicate.

    Every test is a two-world pair. The sharpest of them holds the ledger BYTE
    IDENTICAL across both worlds and moves only which understanding is live, so the
    thing under test is the keying and nothing else.

    Names match the frozen `g4-integrate` closeout selector (`compliance`)."""

    MODEL = "claude-opus-4-8"

    def setUp(self):
        _, self.hard = E._gauge_reader.thresholds_for(self.MODEL)
        self.over_hard = min(self.hard + 0.05, 1.0)

    def _three_gates(self):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def _tripped_at_g2(self):
        """A spine carrying exactly one `begin-refused` entry written under w-1."""
        cl = self._three_gates()
        E.advance(cl, "g1", why="u1")
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertEqual(len(cl["override_ledger"]), 1)
        self.assertEqual(cl["override_ledger"][0]["why_ref"], "w-1")
        return cl

    def test_compliance_signal_is_empty_in_the_healthy_world_and_names_the_begin_in_the_defective_one(self):
        healthy = self._three_gates()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            E.dispatch(healthy, _advance_ns("g1", why="wrapping up and stopping"),
                       base_dir=Path("."))
        self.assertEqual(E.begin_over_line_records(healthy), [])   # <-- differing value

        defective = self._tripped_at_g2()
        records = E.begin_over_line_records(defective)             # <-- differing value
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["outcome"], "begin-refused")
        self.assertEqual(records[0]["gate"], "g2")

    def test_compliance_signal_reads_the_live_understanding_not_a_superseded_one(self):
        """The two worlds here hold an IDENTICAL ledger — same single entry, same
        `why_ref`. The ONLY difference is whether that entry's understanding is
        still the live one. Differing value: the selector's length (1 vs 0)."""
        defective = self._tripped_at_g2()
        ledger_snapshot = copy.deepcopy(defective["override_ledger"])
        self.assertEqual(len(E.begin_over_line_records(defective)), 1)

        # the understanding moves on: a fresh agent closes g2 with its OWN why (w-2)
        superseded = copy.deepcopy(defective)
        E.attach(superseded, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.start(superseded, "g2")
        E.advance(superseded, "g2", why="u2 — a fresh agent's understanding")
        self.assertEqual(E._latest_why_record(superseded)["id"], "w-2")

        # the ledger is untouched: the mark is retained, it just stops being current
        self.assertEqual(superseded["override_ledger"], ledger_snapshot)
        self.assertEqual(E.begin_over_line_records(superseded), [])  # <-- differing value

    def test_compliance_signal_goes_quiet_when_a_reopen_freshens_the_digest(self):
        """The other supersede path: `reopen` appends a reopen-marker, so
        `_latest_why_record` skips past the understanding the entry was written
        under. Positive control first, so the quiet half means something."""
        cl = self._tripped_at_g2()
        self.assertEqual(len(E.begin_over_line_records(cl)), 1)     # positive control
        before = copy.deepcopy(cl["override_ledger"])
        with mock.patch.object(E, "_read_gauge", return_value=None):
            E.dispatch(cl, _reopen_ns("g1", reason="rework"), base_dir=Path("."))
        self.assertIsNone(E._latest_why_record(cl))
        self.assertEqual(cl["override_ledger"], before)  # entry retained, never edited
        self.assertEqual(E.begin_over_line_records(cl), [])         # <-- differing value

    def test_compliance_signal_counts_both_begin_outcomes_and_nothing_else(self):
        """The outcome filter, two-world on the SAME entry: `begin-refused` and
        `begin-released` are the non-compliance record; any other outcome value a
        future writer might add is not silently counted as one."""
        cl = self._tripped_at_g2()
        entry = cl["override_ledger"][0]
        for outcome in ("begin-refused", "begin-released"):
            with self.subTest(outcome=outcome):
                entry["outcome"] = outcome
                self.assertEqual(len(E.begin_over_line_records(cl)), 1)
        for outcome in ("advance-noted", "", None):
            with self.subTest(outcome=outcome):
                entry["outcome"] = outcome
                self.assertEqual(E.begin_over_line_records(cl), [])

    def test_compliance_selector_is_pure_and_reads_stored_state_only(self):
        """Purity is load-bearing: the selector is called from the read-only
        `current` path, where a probe would be a side effect. Asserted three ways —
        no state change, no gauge read, no subprocess."""
        cl = self._tripped_at_g2()
        before = copy.deepcopy(cl)
        with mock.patch.object(E, "_read_gauge",
                               side_effect=AssertionError("the selector must not read the gauge")), \
             mock.patch.object(E.subprocess, "run",
                               side_effect=AssertionError("the selector must not run a subprocess")):
            records = E.begin_over_line_records(cl)
        self.assertEqual(len(records), 1)
        self.assertEqual(cl, before)  # no side effects

    def test_compliance_signal_is_empty_on_a_spine_that_never_carried_a_ledger(self):
        """Backward compatibility at the read side: a legacy spine with no
        `override_ledger` key is not a crash and not a claim — it is an empty record."""
        cl = self._three_gates()
        self.assertNotIn("override_ledger", cl)
        self.assertEqual(E.begin_over_line_records(cl), [])

    # --- #467 B1 rework: the HISTORICAL selector, additive and UNKEYED -------- #
    #
    # The live selector above is keyed to the live understanding by design (close
    # criterion (b)); that keying is what the mandated HARD-band close (`advance
    # --why`) is guaranteed to supersede, emptying the live selector even in the
    # exact runaway the ledger exists to catch (B1). The historical selector below
    # answers a different question -- not "under the understanding now in force"
    # but "ever" -- and is exactly what survives that supersede.

    def test_historical_signal_is_empty_in_the_healthy_world_and_names_the_begin_in_the_defective_one(self):
        healthy = self._three_gates()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            E.dispatch(healthy, _advance_ns("g1", why="wrapping up and stopping"),
                       base_dir=Path("."))
        self.assertEqual(E.begin_over_line_records_historical(healthy), [])   # <-- differing value

        defective = self._tripped_at_g2()
        records = E.begin_over_line_records_historical(defective)            # <-- differing value
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["outcome"], "begin-refused")
        self.assertEqual(records[0]["gate"], "g2")

    def test_historical_signal_survives_the_supersede_that_empties_the_live_one(self):
        """THE B1 regression, at the selector level. Byte-identical ledger to
        `test_compliance_signal_reads_the_live_understanding_not_a_superseded_one`
        — only the understanding moves on — but here it is the HISTORICAL
        selector under test, and it must NOT go quiet: going quiet on exactly this
        transition is the defect. Differing value: the LIVE selector's length
        (1 -> 0, positive control) vs the HISTORICAL selector's length (1 -> 1,
        unchanged — the field this test actually measures)."""
        defective = self._tripped_at_g2()
        ledger_snapshot = copy.deepcopy(defective["override_ledger"])
        self.assertEqual(len(E.begin_over_line_records(defective)), 1)              # positive control (live, before)
        self.assertEqual(len(E.begin_over_line_records_historical(defective)), 1)   # positive control (historical, before)

        # the offender's own close: a fresh why-record supersedes the live one
        superseded = copy.deepcopy(defective)
        E.attach(superseded, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.start(superseded, "g2")
        E.advance(superseded, "g2", why="u2 — the offender's own close")
        self.assertEqual(E._latest_why_record(superseded)["id"], "w-2")

        self.assertEqual(superseded["override_ledger"], ledger_snapshot)  # entry retained, never edited
        self.assertEqual(E.begin_over_line_records(superseded), [])                 # live goes quiet (positive control)
        self.assertEqual(len(E.begin_over_line_records_historical(superseded)), 1)  # <-- differing value: historical does not
        self.assertEqual(E.begin_over_line_records_historical(superseded)[0]["id"],
                         ledger_snapshot[0]["id"])

    def test_historical_signal_goes_quiet_only_when_the_ledger_itself_is_empty(self):
        """The other supersede path (`reopen`) quiets the LIVE selector the same
        way (already proven elsewhere); the historical one has no why_ref keying
        for a reopen-marker to bypass, so it is unaffected. Positive control
        first, so the differing value means something."""
        cl = self._tripped_at_g2()
        self.assertEqual(len(E.begin_over_line_records(cl)), 1)             # positive control
        self.assertEqual(len(E.begin_over_line_records_historical(cl)), 1)  # positive control
        with mock.patch.object(E, "_read_gauge", return_value=None):
            E.dispatch(cl, _reopen_ns("g1", reason="rework"), base_dir=Path("."))
        self.assertEqual(E.begin_over_line_records(cl), [])                 # live goes quiet (existing behaviour)
        self.assertEqual(len(E.begin_over_line_records_historical(cl)), 1)  # <-- differing value: historical does not

    def test_historical_signal_counts_both_begin_outcomes_and_nothing_else(self):
        cl = self._tripped_at_g2()
        entry = cl["override_ledger"][0]
        for outcome in ("begin-refused", "begin-released"):
            with self.subTest(outcome=outcome):
                entry["outcome"] = outcome
                self.assertEqual(len(E.begin_over_line_records_historical(cl)), 1)
        for outcome in ("advance-noted", "", None):
            with self.subTest(outcome=outcome):
                entry["outcome"] = outcome
                self.assertEqual(E.begin_over_line_records_historical(cl), [])

    def test_historical_selector_is_pure_and_reads_stored_state_only(self):
        cl = self._tripped_at_g2()
        before = copy.deepcopy(cl)
        with mock.patch.object(E, "_read_gauge",
                               side_effect=AssertionError("the selector must not read the gauge")), \
             mock.patch.object(E.subprocess, "run",
                               side_effect=AssertionError("the selector must not run a subprocess")):
            records = E.begin_over_line_records_historical(cl)
        self.assertEqual(len(records), 1)
        self.assertEqual(cl, before)  # no side effects

    def test_historical_signal_is_empty_on_a_spine_that_never_carried_a_ledger(self):
        cl = self._three_gates()
        self.assertNotIn("override_ledger", cl)
        self.assertEqual(E.begin_over_line_records_historical(cl), [])

    def test_historical_selector_never_raises_on_a_malformed_ledger(self):
        """Fail-safe parity with the live selector (criterion 8): a corrupted
        `override_ledger` value is read as empty, never a crash."""
        for malformed in (None, "not-a-list", {"also": "not-a-list"}):
            with self.subTest(malformed=repr(malformed)):
                cl = self._three_gates()
                cl["override_ledger"] = malformed
                self.assertEqual(E.begin_over_line_records_historical(cl), [])

    def test_historical_selector_skips_non_dict_entries_in_an_otherwise_valid_ledger(self):
        cl = self._three_gates()
        cl["override_ledger"] = [1, "x", None, {"id": "ov-1", "kind": "trip",
                                                 "outcome": "begin-refused",
                                                 "gate": "g2", "verb": "start"}]
        records = E.begin_over_line_records_historical(cl)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], "ov-1")


class TripLedgerComplianceOnTheHardAdvisory(unittest.TestCase):
    """#467 (c) — the signal is surfaced by EXTENDING the existing `_trip_advisory`
    HARD branch, not by a second render computing the same fact.

    Every assertion is an EQUALITY against the whole advisory string, so the healthy
    world is pinned byte-for-byte to what shipped and the defective world differs by
    exactly the added line. A `assertIn`-only test here would pass against an
    advisory that had silently changed everything else.

    Names match the frozen `g4-integrate` closeout selector (`compliance`)."""

    MODEL = "claude-opus-4-8"

    def setUp(self):
        _, self.hard = E._gauge_reader.thresholds_for(self.MODEL)
        self.over_hard = min(self.hard + 0.05, 1.0)

    def _three_gates(self):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def _g2_pending_after_g1(self):
        cl = self._three_gates()
        E.advance(cl, "g1", why="u1")
        return cl

    def _refuse_start(self, cl, iid="g2"):
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns(iid), base_dir=Path("."))

    def _advisory(self, cl):
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            return E._trip_advisory(cl, Path("."))

    # --- the exact strings, so both worlds are pinned ----------------------- #
    # #510: the HARD band states a different instruction for a PENDING guarded gate
    # than for an in-progress one, because `advance` on a pending gate is refused
    # ("must be in-progress to advance") — so the in-progress wording, shown at a
    # pending gate, named a command the engine would reject. These tests are #467
    # tests: their differing field is the TRIP LEDGER / TRIP HISTORY line, and the
    # base advisory is only a pinned prefix keeping each assertion a whole-string
    # equality. Each helper below is that same prefix for the status its scenario
    # actually leaves the active gate in.
    def _expected_hard_pending(self, gate, wid):
        return (f"\nCONTEXT {self.over_hard:.0%} (>= hard): your instruction has changed. "
                f"First request a refresh with: attach {gate} --type refresh-request "
                f"--field seam={gate} --field why_ref={wid}; then "
                f"begin THIS guarded gate (`start {gate}`); then close it carrying your "
                f"handoff (`advance {gate} --why \"<understanding>\"`) and stop. A fresh "
                f"agent picks up from your DIGEST; do not begin work at another gate.")

    def _expected_hard_already_requested_pending(self, gate):
        return (f"\nCONTEXT {self.over_hard:.0%} (>= hard): your instruction has changed, and "
                f"the refresh for {gate} is already requested. Now begin THIS guarded "
                f"gate (`start {gate}`), then close it carrying your handoff "
                f"(`advance {gate} --why \"<understanding>\"`) and stop. A fresh agent "
                f"picks up from your DIGEST; do not begin work at another gate.")

    def _expected_hard(self, gate, wid):
        return (f"\nCONTEXT {self.over_hard:.0%} (>= hard): your instruction has changed. "
                f"You have taken this as far as this context can carry it — now close THIS "
                f"gate carrying your handoff (`advance {gate} --why \"<understanding>\"`), "
                f"request a refresh, and stop. A fresh agent picks up from your DIGEST; do "
                f"not begin work at another gate. Request the refresh with: attach {gate} "
                f"--type refresh-request --field seam={gate} --field why_ref={wid}")

    def _expected_hard_already_requested(self, gate):
        return (f"\nCONTEXT {self.over_hard:.0%} (>= hard): your instruction has changed, "
                f"and the refresh for {gate} is already requested. Close THIS gate carrying "
                f"your handoff (`advance {gate} --why \"<understanding>\"`) and stop. A fresh "
                f"agent picks up from your DIGEST; do not begin work at another gate.")

    def _expected_live_note(self, n, verb, gate, outcome):
        return (f"\nTRIP LEDGER: {n} begin(s) at/over the hard line are on the record "
                f"under this understanding (latest: {verb} {gate} -> {outcome}). "
                f"Closing THIS gate clears this line; the line below, if present, "
                f"is not.")

    def _expected_historical_note(self, n, verb, gate, outcome):
        return (f"\nTRIP HISTORY: {n} begin(s) at/over the hard line are on the "
                f"record across this checklist's full history (latest: {verb} {gate} "
                f"-> {outcome}). No close clears this line.")

    def _expected_note(self, n, verb, gate, outcome):
        """The live line and the historical line together, for the common case
        (used by every existing shape-4 test below) where nothing has yet been
        superseded — the two selectors hold the SAME count and the SAME latest
        entry, so both lines carry identical (n, verb, gate, outcome)."""
        return (self._expected_live_note(n, verb, gate, outcome)
                + self._expected_historical_note(n, verb, gate, outcome))

    # --- shape 4: the rendered signal ---------------------------------------- #
    def test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world(self):
        # g2 is PENDING in both worlds: the refused begin does not start it.
        healthy = self._g2_pending_after_g1()
        self.assertEqual(self._advisory(healthy), self._expected_hard_pending("g2", "w-1"))

        defective = self._g2_pending_after_g1()
        self._refuse_start(defective)
        self.assertEqual(
            self._advisory(defective),
            self._expected_hard_pending("g2", "w-1")
            + self._expected_note(1, "start", "g2", "begin-refused"))

    def test_compliance_line_also_rides_the_already_requested_hard_advisory(self):
        """The HARD branch has TWO sub-branches. Extending only the one an agent
        without a pending request sees would leave the released case — the worse
        one, where work actually proceeded over the line — silent."""
        healthy = self._g2_pending_after_g1()
        E.attach(healthy, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        self.assertEqual(self._advisory(healthy),  # g2 still PENDING: nothing began it
                         self._expected_hard_already_requested_pending("g2"))

        # In the defective world the agent files a request at g3 as well and aims a
        # begin THERE — at a gate its advisory never named. That begin is released
        # by its own request and is a genuine over-the-line begin. It then takes the
        # instructed `start g2`, so g2 is in-progress and the advisory is the
        # in-progress instruction. (#510: `start g2` alone no longer serves here —
        # it is the begin the advisory itself mandates, recorded as
        # `begin-instructed`, which is exactly what must NOT ride this line.)
        defective = self._g2_pending_after_g1()
        E.attach(defective, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.attach(defective, "g3", "refresh-request", {"seam": "g3", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):  # `start` rejects a non-active gate
                E.dispatch(defective, _start_ns("g3"), base_dir=Path("."))
            E.dispatch(defective, _start_ns("g2"), base_dir=Path("."))  # instructed
        self.assertEqual([e["outcome"] for e in defective["override_ledger"]],
                         ["begin-released", "begin-instructed"])
        self.assertEqual(
            self._advisory(defective),
            self._expected_hard_already_requested("g2")
            + self._expected_note(1, "start", "g3", "begin-released"))

    def test_compliance_line_names_the_count_and_the_latest_begin(self):
        """The count is real, not a hardcoded 1, and the named begin is the LATEST
        one — asserted against a spine carrying three entries of two kinds."""
        cl = self._g2_pending_after_g1()
        self._refuse_start(cl, "g2")
        self._refuse_start(cl, "g2")
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertEqual(len(cl["override_ledger"]), 3)  # the count this guard looped over
        # #510: three entries are on the ledger but only TWO are over-the-line
        # begins — the third is the advisory's own instructed `start`. So the
        # rendered count is the count of COUNTED entries, and the named begin is the
        # latest COUNTED one, not simply the last row of the ledger. That is a
        # sharper version of what this test has always asserted.
        out = self._advisory(cl)
        self.assertEqual(
            out,
            self._expected_hard_already_requested("g2")
            + self._expected_note(2, "start", "g2", "begin-refused"))
        self.assertNotIn("1 begin(s)", out)
        self.assertNotIn("3 begin(s)", out)

    # --- #467 B1 rework: the HISTORICAL line, additive and rendered separately - #

    def test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent(self):
        """THE B1 regression, at the render site. World H: nothing was ever
        tripped — no begin verb ever ran over the line, so there is neither a
        live line nor a historical one. World D: the offender's own close — a
        refused begin at g2, then that SAME agent closes g2 with `advance --why`
        (the only legal close at/over hard) — which supersedes the live
        selector (the existing, correct keying) but must NOT silence the
        historical one. Positive control: World H proves the historical line
        does not render spuriously. Differing field: whether `TRIP HISTORY`
        appears at all, and the count it names."""
        healthy = self._g2_pending_after_g1()
        healthy_out = self._advisory(healthy)
        self.assertNotIn("TRIP HISTORY", healthy_out)  # positive control

        defective = self._g2_pending_after_g1()
        self._refuse_start(defective, "g2")
        self.assertEqual(len(defective["override_ledger"]), 1)
        E.attach(defective, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.start(defective, "g2")
        E.advance(defective, "g2", why="u2 — the offender's own close")
        out = self._advisory(defective)
        self.assertNotIn("TRIP LEDGER:", out)   # the live line is absent (B1's own reproduction)
        self.assertIn("TRIP HISTORY", out)      # <-- differing field: the historical line survives
        self.assertIn("1 begin(s)", out)        # names the true count, not zero

    def test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it(self):
        """B1, corrected: this IS the offender's own close, not a fresh agent's —
        the only legal close at/over hard is `advance --why`, and that is what an
        agent that just ran an over-the-line begin has to run to leave the gate it
        is trapped in. The keying reaches the RENDER, not just the selector: the
        same retained entry stops being reported on the LIVE line once THAT close
        writes the new why-record and supersedes the old one — that keying is
        correct and untouched (close criterion (b)). What changed is that the
        HISTORICAL line does not stop: unkeyed, it still names the retained begin.
        Differing field: which line is present after the SAME close (live absent,
        historical present) — this is the exact seam B1 measured as byte-identical
        to a compliant agent; it no longer is."""
        cl = self._g2_pending_after_g1()
        self._refuse_start(cl, "g2")
        self.assertEqual(len(cl["override_ledger"]), 1)  # positive control: it is there
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        E.start(cl, "g2")
        E.advance(cl, "g2", why="u2 — the offender's own close, the gate its own HARD advisory told it to close")
        self.assertEqual(len(cl["override_ledger"]), 1)  # retained, not deleted
        # ADJUDICATED (#510, wave 2). The active gate here is g3 — not the gate this
        # agent is trapped in, but the next one, reached by the agent's OWN close — and
        # g3 is PENDING, so the pending wording is the correct one: `advance` on a
        # pending gate is refused, so `start g3` then `advance g3 --why` really is the
        # only way this agent can leave its handoff at g3. The human ruled that the
        # ENGINE yields, not the prose: obeying that instruction is now recorded as
        # `begin-instructed` and is not counted as an over-the-line begin, so the
        # advisory no longer tells the agent to do something its own compliance signal
        # then punishes. The historical line below still names the g2 begin, which WAS
        # a real offence (a start with no refresh requested). See
        # TripInstructedBeginIsNotAnOffence for the engine-behaviour regression.
        self.assertEqual(
            self._advisory(cl),
            self._expected_hard_pending("g3", "w-2")
            + self._expected_historical_note(1, "start", "g2", "begin-refused"))

    def test_compliance_line_reaches_the_agent_through_current_at_the_cli_boundary(self):
        healthy = self._g2_pending_after_g1()
        defective = self._g2_pending_after_g1()
        self._refuse_start(defective)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            healthy_out = E.dispatch(healthy, types.SimpleNamespace(verb="current"),
                                     base_dir=Path("."))
            defective_out = E.dispatch(defective, types.SimpleNamespace(verb="current"),
                                       base_dir=Path("."))
        self.assertNotIn("TRIP LEDGER", healthy_out)     # <-- the differing field
        self.assertIn("TRIP LEDGER", defective_out)
        self.assertTrue(defective_out.endswith(
            self._expected_note(1, "start", "g2", "begin-refused")), defective_out)

    def test_compliance_line_never_appears_below_the_hard_band(self):
        """The signal is a HARD-band escalation. Below the line the advisory is the
        SOFT text (or nothing) and says nothing about the ledger — a spine can carry
        a stale mark without every `current` re-litigating it."""
        soft, _ = E._gauge_reader.thresholds_for(self.MODEL)
        cl = self._g2_pending_after_g1()
        self._refuse_start(cl)
        self.assertEqual(len(cl["override_ledger"]), 1)  # the mark is present either way
        for fill in (max(soft - 0.01, 0.0), (soft + self.hard) / 2):
            with self.subTest(fill=fill):
                with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
                    self.assertNotIn("TRIP LEDGER", E._trip_advisory(cl, Path(".")))


class TripInstructedBeginIsNotAnOffence(unittest.TestCase):
    """#510 (the engine half) — the HARD advisory at a PENDING gate INSTRUCTS a
    `start`, and the engine must not brand the agent that obeys it.

    `advance` is refused on a pending gate ("must be in-progress to advance"), so
    the ONLY way an over-the-line agent can leave its handoff AT a pending gate is
    the sequence the advisory names: request the refresh, `start` the gate, then
    `advance --why`. That start does not begin work the agent cannot finish — it is
    the handoff mechanism itself. #467 predates that instruction and recorded it as
    `begin-released`, so the compliance signal reported an offence for obedience.

    The engine now records that ONE configuration as `begin-instructed`: still an
    append-only ledger entry (nothing is hidden), but not one of the two outcomes
    the compliance selectors count. Everything else #467 guards is untouched, which
    the positive controls below pin.

    Differing field throughout: what `begin_over_line_records` /
    `begin_over_line_records_historical` hold after the agent obeys."""

    MODEL = "claude-opus-4-8"

    def setUp(self):
        _, self.hard = E._gauge_reader.thresholds_for(self.MODEL)
        self.over_hard = min(self.hard + 0.05, 1.0)

    def _three_gates(self):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def _pending_gate_reached_by_my_own_close(self):
        """g2 is pending and active because THIS agent legally closed g1 with a
        handoff — the exact seam the floated contradiction was measured at."""
        cl = self._three_gates()
        E.advance(cl, "g1", why="u1")
        return cl

    def _obey_the_advisory(self, cl, gate_id):
        """Do literally what the HARD pending advisory says, in its stated order."""
        rec = E._latest_why_record(cl)
        wid = rec["id"] if rec else None
        E.attach(cl, gate_id, "refresh-request", {"seam": gate_id, "why_ref": wid})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            return E.dispatch(cl, _start_ns(gate_id), base_dir=Path("."))

    def _advisory(self, cl):
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            return E._trip_advisory(cl, Path("."))

    def test_the_advisory_really_does_instruct_this_start(self):
        """Positive control on the premise: if the advisory ever stops naming
        `start <gate>` here, the exemption below is exempting something the engine
        no longer asks for, and this test says so before the others mislead."""
        cl = self._pending_gate_reached_by_my_own_close()
        self.assertEqual(cl["tasks"]["g2"]["status"], "pending")
        self.assertEqual(E.active_id(cl), "g2")
        self.assertIn("begin THIS guarded gate (`start g2`)", self._advisory(cl))

    def test_obeying_the_instructed_start_records_no_over_the_line_begin(self):
        """THE REGRESSION. The agent does exactly what the engine told it to do;
        neither compliance selector may hold anything afterwards."""
        cl = self._pending_gate_reached_by_my_own_close()
        msg = self._obey_the_advisory(cl, "g2")

        # the start is permitted and really opened the gate
        self.assertTrue(msg.endswith("g2 -> in-progress"), msg)
        self.assertEqual(cl["tasks"]["g2"]["status"], "in-progress")

        # <-- the differing field: obedience carries no over-the-line begin
        self.assertEqual(E.begin_over_line_records(cl), [])
        self.assertEqual(E.begin_over_line_records_historical(cl), [])

    def test_the_instructed_begin_is_still_recorded_never_hidden(self):
        """De-branding is not deletion: the event stays on the append-only ledger
        with its own outcome, so an auditor still sees that a begin happened over
        the line and why it was allowed."""
        cl = self._pending_gate_reached_by_my_own_close()
        self._obey_the_advisory(cl, "g2")
        led = cl["override_ledger"]
        self.assertEqual(len(led), 1)
        self.assertEqual(led[0]["outcome"], "begin-instructed")
        self.assertEqual(led[0]["gate"], "g2")
        self.assertEqual(led[0]["verb"], "start")
        self.assertEqual(led[0]["why_ref"], "w-1")
        self.assertEqual(set(led[0]), {"id", "kind", "gate", "verb", "outcome", "fill",
                                       "hard", "model", "why_ref", "ts"})

    def test_the_obedient_agent_is_not_named_on_its_next_current(self):
        """The symptom the float measured, at the render: after obeying, neither
        compliance line appears. Reported through the same read-only surface the
        agent actually sees."""
        cl = self._pending_gate_reached_by_my_own_close()
        self._obey_the_advisory(cl, "g2")
        out = self._advisory(cl)
        self.assertNotIn("TRIP LEDGER:", out)
        self.assertNotIn("TRIP HISTORY", out)

    # --- the exemption is NARROW: everything else is still an offence -------- #

    def test_a_start_without_the_instructed_refresh_is_still_refused_and_branded(self):
        """The advisory says request the refresh FIRST. A start that skips it is
        not the instructed one and is refused exactly as before."""
        cl = self._pending_gate_reached_by_my_own_close()
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertEqual(cl["override_ledger"][0]["outcome"], "begin-refused")
        self.assertEqual(len(E.begin_over_line_records(cl)), 1)  # still branded

    def test_a_reopen_over_the_line_is_still_released_and_branded(self):
        """`reopen` drives a COMPLETE gate back to in-progress and cascades
        downstream — work the agent cannot finish, and never something the advisory
        instructs. A pending request still releases it, and it stays an offence."""
        cl = self._pending_gate_reached_by_my_own_close()
        E.attach(cl, "g1", "refresh-request", {"seam": "g1", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            E.dispatch(cl, _reopen_ns("g1", reason="rework"), base_dir=Path("."))
        self.assertEqual(cl["override_ledger"][0]["outcome"], "begin-released")
        # the LIVE selector is silent here for a reason that predates this change:
        # `reopen` appends a reopen-marker why-record, which supersedes w-1 (its
        # documented keying). The unkeyed historical line is the one that must
        # still name this begin.
        self.assertEqual(len(E.begin_over_line_records_historical(cl)), 1)  # still branded

    def test_a_start_aimed_at_a_gate_the_advisory_did_not_name_is_still_branded(self):
        """The exemption is keyed to the ACTIVE gate the advisory names. A start
        aimed elsewhere is the agent's own choice, so it is recorded as a released
        begin even though a matching request is on file."""
        cl = self._pending_gate_reached_by_my_own_close()
        E.attach(cl, "g3", "refresh-request", {"seam": "g3", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):   # `start` itself rejects a non-active gate
                E.dispatch(cl, _start_ns("g3"), base_dir=Path("."))
        self.assertEqual(cl["override_ledger"][0]["outcome"], "begin-released")
        self.assertEqual(cl["override_ledger"][0]["gate"], "g3")
        self.assertEqual(len(E.begin_over_line_records(cl)), 1)  # still branded

    def test_below_the_line_nothing_is_recorded_at_all(self):
        """Fail-safe control: the new branch is inside the HARD band and cannot
        create a ledger on a healthy run."""
        cl = self._pending_gate_reached_by_my_own_close()
        E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge",
                               return_value=_reading(max(self.hard - 0.05, 0.0))):
            E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertNotIn("override_ledger", cl)


class TripLedgerFailSafeAndEngineOnly(unittest.TestCase):
    """#467 — the four properties that decide whether the signal is trustworthy
    rather than merely present: the fail-safe on a missing reading, engine-written-
    only, backward compatibility, and surveys.

    The fail-safe is the one most easily got wrong. A signal that reads SILENCE as
    "clean" is the same defect class as a check that cannot fail: it produces the
    compliant-looking answer in a world where nothing was observed at all. So the
    rule asserted here is stronger than "no entry" — it is **no entry AND no
    claim**.

    Names match the frozen `g4-integrate` closeout selector."""

    MODEL = "claude-opus-4-8"

    def setUp(self):
        _, self.hard = E._gauge_reader.thresholds_for(self.MODEL)
        self.over_hard = min(self.hard + 0.05, 1.0)

    def _three_gates(self):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def _g2_pending_after_g1(self):
        cl = self._three_gates()
        E.advance(cl, "g1", why="u1")
        return cl

    # --- fail-safe ----------------------------------------------------------- #
    def test_ledger_a_none_reading_writes_no_entry_and_makes_no_compliance_claim(self):
        """Silence must read as NEITHER compliant NOR non-compliant. Both halves are
        asserted, and the positive control at the end is what stops the whole test
        from being satisfied by a dead mechanism."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)  # empty: no gauge, no sidecars, so the advisory is silent
            cl = self._g2_pending_after_g1()
            with mock.patch.object(E, "_read_gauge", return_value=None):
                msg = E.dispatch(cl, _start_ns("g2"), base_dir=base)
                advisory = E._trip_advisory(cl, base)
            self.assertTrue(msg.endswith("g2 -> in-progress"), msg)
            self.assertNotIn("override_ledger", cl)     # half 1: no entry
            self.assertEqual(advisory, "")              # half 2: no claim either way
            self.assertEqual(E.begin_over_line_records(cl), [])

            # A spine that ALREADY carries a live mark, now read with NO gauge: the
            # engine must not report non-compliance it cannot currently observe...
            marked = self._g2_pending_after_g1()
            with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
                with self.assertRaises(E.EngineError):
                    E.dispatch(marked, _start_ns("g2"), base_dir=base)
            self.assertEqual(len(marked["override_ledger"]), 1)
            with mock.patch.object(E, "_read_gauge", return_value=None):
                self.assertEqual(E._trip_advisory(marked, base), "")   # no claim
            # POSITIVE CONTROL: the SAME spine, read WITH a gauge over the line, does
            # report it. Without this line every assertion above would still pass
            # against an advisory that had been dead-coded to "".
            with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
                self.assertIn("TRIP LEDGER", E._trip_advisory(marked, base))

    # --- engine-written only -------------------------------------------------- #
    def test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb(self):
        """The exhaustive proof, read off the engine's own call graph rather than a
        hand-maintained list of verbs.

        Post-migration (g1), the write path is `_append_override_entry` (the sole
        function naming the `override_ledger` key alongside its own reader
        `_override_entries`), and the read path over BOTH the new key and the
        legacy `trip_ledger` key is centralized in `_override_entries` — the only
        function naming `trip_ledger` at all, and the only caller of both
        selectors below. Facts asserted mechanically: (1) exactly which functions
        name each key; (2) `_append_override_entry`'s only callers are
        `_append_trip_entry` (trip kind, via `_trip_hard_gate` <- `dispatch`) and
        `dispatch` itself (g2: the claim/release/generic-verb branches call it
        directly for `force-claim`/`force-release`/`waive` kinds); (3) `_run_verb`
        — the function every CLI verb (`waive`/`claim`/`release` included) is
        dispatched through — reaches none of the four writer-side functions
        (`_append_override_entry`, `_append_trip_entry`, `_trip_hard_gate`, and
        `waive`/`claim`/`release` themselves never call it either). So no verb's
        own body can create, edit, or delete an entry — only `dispatch`, the CLI
        chokepoint, can — and the new reader is exactly that: a reader, called
        from the same two selector sites as before."""
        import ast
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        funcs = {n.name: n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertGreater(len(funcs), 50, "the call-graph scan looked at nothing")

        def names_the_key(node, key):
            return any(isinstance(c, ast.Constant) and c.value == key
                       for c in ast.walk(node))

        def calls_within(node):
            return {c.func.id for c in ast.walk(node)
                    if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}

        def callers_of(name):
            return sorted(f for f, node in funcs.items() if name in calls_within(node))

        self.assertEqual(
            sorted(f for f, n in funcs.items() if names_the_key(n, "override_ledger")),
            ["_append_override_entry", "_override_entries"])
        self.assertEqual(
            sorted(f for f, n in funcs.items() if names_the_key(n, "trip_ledger")),
            ["_override_entries"])
        self.assertEqual(callers_of("_append_override_entry"), ["_append_trip_entry", "dispatch"])
        self.assertEqual(callers_of("_append_trip_entry"), ["_trip_hard_gate"])
        self.assertEqual(callers_of("_trip_hard_gate"), ["dispatch"])
        self.assertEqual(callers_of("_override_entries"),
                         ["begin_over_line_records", "begin_over_line_records_historical",
                          "override_summary"])
        self.assertEqual(callers_of("begin_over_line_records"), ["_trip_advisory"])
        self.assertEqual(callers_of("begin_over_line_records_historical"), ["_trip_advisory"])
        # the append call sites live in `dispatch` around `_run_verb`, never
        # inside it -- and never inside `waive`/`claim`/`release`'s own bodies.
        run_verb_calls = calls_within(funcs["_run_verb"])
        for unreachable in ("_append_override_entry", "_append_trip_entry", "_trip_hard_gate"):
            self.assertNotIn(unreachable, run_verb_calls)
        for verb_fn in ("waive", "claim", "release"):
            self.assertNotIn("_append_override_entry", calls_within(funcs[verb_fn]))

    def _write_gauge(self, d, fill, observed_at):
        (Path(d) / "gauge.json").write_text(json.dumps({
            "schema_version": 1, "fill_fraction": fill,
            "model": self.MODEL, "observed_at": observed_at,
        }), encoding="utf-8")

    def test_ledger_only_the_begin_verbs_write_an_entry_over_the_line(self):
        """The behavioural twin of the call-graph proof: with a REAL gauge parked
        over the hard line, six non-begin verbs are driven through `main()` and none
        of them leaves a mark. The seventh — a begin verb — does. Without that last
        step the whole test would pass against a ledger that never wrote anything."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._three_gates())
            self._write_gauge(d, self.over_hard, datetime.now(timezone.utc).isoformat())
            non_begin = [
                ["current"],
                ["attach", "g1", "--type", "command-output", "--field", "cmd=x"],
                ["flag-candidate", "--from", "g1", "--statement", "a candidate"],
                ["advance", "g1", "--why", "u1"],
                ["block", "g2", "--blocker", "b", "--next", "n"],
                ["resume", "g2", "--reason", "unblocked"],
            ]
            for argv in non_begin:
                with self.subTest(verb=argv[0]):
                    self.assertEqual(E.main(["--file", str(f)] + argv), 0, argv)
                    self.assertNotIn("override_ledger", E.load(f))
            self.assertEqual(len(non_begin), 6)  # the count this guard looped over

            import contextlib, io
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(E.main(["--file", str(f), "start", "g2"]), 1)
            led = E.load(f)["override_ledger"]
            self.assertEqual(len(led), 1)
            self.assertEqual(led[0]["verb"], "start")

    # --- backward compatibility ---------------------------------------------- #
    def test_ledger_a_spine_with_no_ledger_key_drives_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._three_gates())
            self.assertNotIn("override_ledger", E.load(f))
            self.assertEqual(E.main(["--file", str(f), "advance", "g1", "--why", "u1"]), 0)
            self.assertEqual(E.main(["--file", str(f), "start", "g2"]), 0)
            self.assertEqual(E.main(["--file", str(f), "advance", "g2", "--why", "u2"]), 0)
            cl = E.load(f)
            self.assertNotIn("override_ledger", cl)  # the key is never created for nothing
            self.assertEqual(cl["tasks"]["g2"]["status"], "complete")

    def test_ledger_an_existing_ledger_is_extended_never_replaced(self):
        """`setdefault`, not assignment: entries already on the spine survive a new
        trip, and the new entry's id continues the existing sequence."""
        cl = self._g2_pending_after_g1()
        cl["override_ledger"] = [{"id": "ov-1", "kind": "trip", "gate": "g0", "verb": "start",
                                  "outcome": "begin-refused", "fill": 0.99, "hard": 0.9,
                                  "model": self.MODEL, "why_ref": "w-1", "ts": "2026-01-01T00:00:00Z"}]
        prior = copy.deepcopy(cl["override_ledger"][0])
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
        self.assertEqual(len(cl["override_ledger"]), 2)
        self.assertEqual(cl["override_ledger"][0], prior)   # untouched
        self.assertEqual(cl["override_ledger"][1]["id"], "ov-2")

    # --- surveys -------------------------------------------------------------- #
    def test_ledger_a_survey_never_writes_an_entry(self):
        """`_trip_hard_band_reading` returns None for a survey, so the band is
        inactive there and there is nothing to record. Paired with a gated positive
        control on the same reading, so the silence means something."""
        sv = survey(v1=survey_item("v1", "pending"))
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            msg = E.dispatch(sv, _start_ns("v1"), base_dir=Path("."))
            self.assertTrue(msg.endswith("v1 -> in-progress"), msg)
            self.assertNotIn("override_ledger", sv)
            # positive control: the same reading DOES record on a gated checklist
            cl = self._g2_pending_after_g1()
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
            self.assertEqual(len(cl["override_ledger"]), 1)


class OverrideLedgerMigration(unittest.TestCase):
    """g1 (override-ledger migration) — the new `override_ledger` key and the
    `_override_entries` merge-reading function, exercised directly rather than
    only through the two `trip`-kind selectors the classes above already cover
    end to end. Pins the migration contract itself: an override_ledger-only
    spine behaves like a trip_ledger-only one did before; a spine carrying both
    keys reads without leaking a non-trip kind or dropping a legacy entry; and a
    spine that straddles the deploy boundary orders legacy entries before a
    freshly written one."""

    MODEL = "claude-opus-4-8"

    def setUp(self):
        _, self.hard = E._gauge_reader.thresholds_for(self.MODEL)
        self.over_hard = min(self.hard + 0.05, 1.0)

    def _two_gates(self):
        return gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
        )

    def test_override_ledger_only_fixture_feeds_the_trip_selectors_identically_to_a_legacy_one(self):
        """A checklist carrying ONLY the new key (no `trip_ledger` at all) drives
        `begin_over_line_records`/`_historical` exactly as a `trip_ledger`-only
        fixture with the equivalent entry did before this migration."""
        common = dict(gate="g2", verb="start", outcome="begin-refused",
                      fill=0.95, hard=self.hard, model=self.MODEL, why_ref="w-1",
                      ts="2026-01-01T00:00:00Z")

        legacy = self._two_gates()
        E.advance(legacy, "g1", why="u1")
        legacy["trip_ledger"] = [{"id": "tl-1", **common}]

        migrated = self._two_gates()
        E.advance(migrated, "g1", why="u1")
        migrated["override_ledger"] = [{"id": "ov-1", "kind": "trip", **common}]

        for cl in (legacy, migrated):
            with self.subTest(cl="legacy" if cl is legacy else "migrated"):
                live = E.begin_over_line_records(cl)
                historical = E.begin_over_line_records_historical(cl)
                self.assertEqual(len(live), 1)
                self.assertEqual(len(historical), 1)

        # identical in every field but `id` -- the retag `_override_entries`
        # applies to a legacy entry reproduces exactly what the new key already
        # carries natively.
        self.assertEqual(
            {k: v for k, v in E.begin_over_line_records(legacy)[0].items() if k != "id"},
            {k: v for k, v in E.begin_over_line_records(migrated)[0].items() if k != "id"})

    def test_override_entries_kind_filter_does_not_leak_non_trip_kinds_and_keeps_legacy_entries(self):
        """A spine carrying BOTH a legacy `trip_ledger` (simulating an archived
        spine) and an `override_ledger` holding an unrelated kind (`force-claim`
        -- nothing writes that kind yet, g2 scope; hand-constructed here) reads
        correctly through the kind filter: no leakage of the non-trip kind into
        the trip view, no dropped legacy entries."""
        cl = self._two_gates()
        E.advance(cl, "g1", why="u1")
        cl["trip_ledger"] = [{"id": "tl-1", "gate": "g2", "verb": "start",
                              "outcome": "begin-refused", "fill": 0.95, "hard": self.hard,
                              "model": self.MODEL, "why_ref": "w-1",
                              "ts": "2026-01-01T00:00:00Z"}]
        cl["override_ledger"] = [
            {"id": "ov-1", "kind": "force-claim", "gate": "g5", "actor": "someone",
             "ts": "2026-01-02T00:00:00Z"},
            {"id": "ov-2", "kind": "trip", "gate": "g3", "verb": "start",
             "outcome": "begin-released", "fill": 0.96, "hard": self.hard,
             "model": self.MODEL, "why_ref": "w-1", "ts": "2026-01-03T00:00:00Z"},
        ]

        trip_only = E._override_entries(cl, kind="trip")
        self.assertEqual([e["id"] for e in trip_only], ["tl-1", "ov-2"])
        self.assertTrue(all(e["kind"] == "trip" for e in trip_only))

        everything = E._override_entries(cl)
        self.assertEqual([e["id"] for e in everything], ["tl-1", "ov-1", "ov-2"])

    def test_live_transition_orders_legacy_entries_before_a_fresh_trip(self):
        """A spine straddling the migration boundary: legacy `trip_ledger` entries
        `tl-1`, `tl-2` from before the deploy, THEN a fresh trip driven through the
        real `_trip_hard_gate` path (not hand-constructed). `_override_entries(cl)`
        with no kind filter returns all three in order `tl-1, tl-2, ov-1` -- legacy
        first, chronologically correct."""
        cl = self._two_gates()
        E.advance(cl, "g1", why="u1")
        cl["trip_ledger"] = [
            {"id": "tl-1", "gate": "g0", "verb": "start", "outcome": "begin-refused",
             "fill": 0.9, "hard": self.hard, "model": self.MODEL, "why_ref": "w-0",
             "ts": "2025-01-01T00:00:00Z"},
            {"id": "tl-2", "gate": "g0", "verb": "reopen", "outcome": "begin-released",
             "fill": 0.92, "hard": self.hard, "model": self.MODEL, "why_ref": "w-0",
             "ts": "2025-01-02T00:00:00Z"},
        ]
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))

        merged = E._override_entries(cl)
        self.assertEqual([e["id"] for e in merged], ["tl-1", "tl-2", "ov-1"])
        self.assertEqual(merged[-1]["kind"], "trip")
        self.assertEqual(merged[-1]["outcome"], "begin-refused")


class OverrideSummaryTests(unittest.TestCase):
    """#504 PART A: `override_summary` -- the closeout-facing summary over the
    override ledger. Reads only `_override_entries(cl)` (asserted directly by
    the call-graph proof above), so these tests exercise it purely on
    hand-built `cl` dicts, the same fixture idiom `OverrideLedgerMigration`
    already uses for `_override_entries` itself."""

    def test_no_ledger_at_all_summarizes_to_all_zero_and_no_ids(self):
        self.assertEqual(E.override_summary({}), {
            "trip": 0, "force-claim": 0, "force-release": 0,
            "waive": 0, "waive_authority_mismatch": 0, "ids": [],
        })

    def test_malformed_ledger_degrades_to_the_same_empty_summary(self):
        # Same fail-safe posture `_override_entries` documents for a malformed
        # `override_ledger`/`trip_ledger` (None, a string, a dict): degrade to
        # nothing rather than raising.
        cl = {"trip_ledger": "not-a-list", "override_ledger": None}
        self.assertEqual(E.override_summary(cl), {
            "trip": 0, "force-claim": 0, "force-release": 0,
            "waive": 0, "waive_authority_mismatch": 0, "ids": [],
        })

    def test_mixed_kinds_counted_and_ids_ordered_legacy_first(self):
        cl = {
            "trip_ledger": [
                {"id": "tl-1", "gate": "g1", "verb": "start", "outcome": "begin-refused"},
            ],
            "override_ledger": [
                {"id": "ov-1", "kind": "force-claim", "verb": "claim"},
                {"id": "ov-2", "kind": "force-release", "verb": "release"},
                {"id": "ov-3", "kind": "waive", "task": "m1", "cond": "c1"},
                {"id": "ov-4", "kind": "waive", "task": "m1", "cond": "c2",
                 "authority_mismatch": True, "expected_authority": "human"},
                {"id": "ov-5", "kind": "trip", "gate": "g2", "verb": "reopen",
                 "outcome": "begin-released"},
            ],
        }
        self.assertEqual(E.override_summary(cl), {
            "trip": 2, "force-claim": 1, "force-release": 1,
            "waive": 2, "waive_authority_mismatch": 1,
            "ids": ["tl-1", "ov-1", "ov-2", "ov-3", "ov-4", "ov-5"],
        })

    def test_waive_authority_mismatch_is_a_sub_count_not_a_sixth_kind(self):
        # A waive entry that carries no `authority_mismatch` key at all (the
        # ordinary, matched-authority case) must not be miscounted as a
        # mismatch -- only an explicit truthy flag counts.
        cl = {"override_ledger": [
            {"id": "ov-1", "kind": "waive", "task": "m1", "cond": "c1"},
            {"id": "ov-2", "kind": "waive", "task": "m1", "cond": "c2",
             "authority_mismatch": False},
        ]}
        summary = E.override_summary(cl)
        self.assertEqual(summary["waive"], 2)
        self.assertEqual(summary["waive_authority_mismatch"], 0)

    def test_does_not_read_the_ledger_keys_directly(self):
        """Purity proof, mirroring the call-graph test's own coverage: patch
        `_override_entries` itself and confirm `override_summary`'s output is
        driven entirely by its return value, never by a direct `cl.get(...)`
        read of `override_ledger`/`trip_ledger`."""
        cl = {"trip_ledger": "poisoned", "override_ledger": "poisoned"}
        canned = [{"id": "ov-1", "kind": "waive", "authority_mismatch": True}]
        with mock.patch.object(E, "_override_entries", return_value=canned) as patched:
            summary = E.override_summary(cl)
        patched.assert_called_once_with(cl)
        self.assertEqual(summary["waive"], 1)
        self.assertEqual(summary["waive_authority_mismatch"], 1)
        self.assertEqual(summary["ids"], ["ov-1"])


class OverrideLedgerG2ClaimReleaseWiring(unittest.TestCase):
    """g2 PART B (claim/release branches): force-claim/force-release append to
    override_ledger from dispatch()'s claim/release arms ONLY, never from
    claim()/release()'s own bodies -- exercised through the real CLI (`main`)
    so the whole chokepoint is proven, not just the pure verb functions."""

    def _one_gate(self):
        return gated(g1=gate("g1", "pending"))

    def test_force_claim_over_genuine_takeover_appends_entry(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, self._one_gate())
            self.assertEqual(
                E.main(["--file", str(f), "claim", "--session-id", "session-1",
                        "--claimed-by", "implementer"]), 0)
            self.assertEqual(
                E.main(["--file", str(f), "claim", "--session-id", "session-2",
                        "--claimed-by", "implementer", "--force",
                        "--reason", "predecessor abandoned"]), 0)
            cl = E.load(f)
            entries = [e for e in cl.get("override_ledger", []) if e["kind"] == "force-claim"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["session_id"], "session-2")
            self.assertEqual(entries[0]["previous_session_id"], "session-1")
            self.assertEqual(entries[0]["takeover_reason"], "predecessor abandoned")
            self.assertEqual(entries[0]["verb"], "claim")

    def test_force_claim_noop_with_nothing_to_take_over_appends_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, self._one_gate())
            # first-ever claim, no existing lease -- --force has nothing to take over
            self.assertEqual(
                E.main(["--file", str(f), "claim", "--session-id", "session-1",
                        "--claimed-by", "implementer", "--force",
                        "--reason", "belt and suspenders"]), 0)
            cl = E.load(f)
            self.assertNotIn("override_ledger", cl)

    def test_force_release_by_non_owner_appends_entry_before_return(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, self._one_gate())
            E.main(["--file", str(f), "claim", "--session-id", "session-1",
                    "--claimed-by", "implementer"])
            self.assertEqual(
                E.main(["--file", str(f), "release", "--session-id", "session-2",
                        "--force", "--reason", "orphaned lease"]), 0)
            cl = E.load(f)
            entries = [e for e in cl.get("override_ledger", []) if e["kind"] == "force-release"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["session_id"], "session-2")
            self.assertEqual(entries[0]["previous_session_id"], "session-1")
            self.assertEqual(entries[0]["takeover_reason"], "orphaned lease")
            self.assertEqual(entries[0]["verb"], "release")
            self.assertEqual(cl["engine_session"]["status"], "released")

    def test_owner_release_appends_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, self._one_gate())
            E.main(["--file", str(f), "claim", "--session-id", "session-1",
                    "--claimed-by", "implementer"])
            self.assertEqual(
                E.main(["--file", str(f), "release", "--session-id", "session-1"]), 0)
            cl = E.load(f)
            self.assertNotIn("override_ledger", cl)

    def test_force_release_against_archived_path_gets_zero_banner_decoration(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            archive_dir = Path(d) / ".agent-work" / "archive" / "run1"
            archive_dir.mkdir(parents=True)
            f = archive_dir / "c.json"
            E.save(f, self._one_gate())
            E.main(["--file", str(f), "claim", "--session-id", "session-1",
                    "--claimed-by", "implementer"])
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = E.main(["--file", str(f), "release", "--session-id", "session-2",
                                "--force", "--reason", "orphaned lease"])
            self.assertEqual(code, 0)
            self.assertNotIn(E._ARCHIVED_BANNER, out.getvalue())
            self.assertNotIn("ARCHIVED", out.getvalue())
            cl = E.load(f)
            entries = [e for e in cl.get("override_ledger", []) if e["kind"] == "force-release"]
            self.assertEqual(len(entries), 1)


class OverrideLedgerG2WaiveWiring(unittest.TestCase):
    """g2 PART B (generic/waive branch): every successful waive is recorded
    from dispatch(), not from waive()'s own body -- and the condition dispatch
    re-reads for the ledger entry uses the SAME which-only lookup waive()
    itself exercises (no preconditions/postconditions fallback)."""

    def _one_gate(self):
        return gated(g1=gate("g1", "in-progress"))

    def test_every_successful_waive_is_recorded_including_plain_matched_authority(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, gated(g1=_waivable_gate("g1", FAIL_COMMAND)))
            self.assertEqual(
                E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                        "--authority", "human", "--reason", "accepted risk"]), 0)
            cl = E.load(f)
            entries = [e for e in cl.get("override_ledger", []) if e["kind"] == "waive"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["task"], "g1")
            self.assertEqual(entries[0]["cond"], "c1")
            self.assertEqual(entries[0]["authority"], "human")
            self.assertEqual(entries[0]["reason"], "accepted risk")
            self.assertFalse(entries[0]["forced"])
            self.assertNotIn("authority_mismatch", entries[0])

    def test_forced_and_mismatched_waive_carries_those_fields_on_the_ledger_entry(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            t = _waivable_gate("g1", FAIL_COMMAND)
            t["postconditions"][0]["override_policy"]["authority"] = "commander"
            E.save(f, gated(g1=t))
            self.assertEqual(
                E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                        "--authority", "implementer", "--reason", "accepted", "--force"]), 0)
            cl = E.load(f)
            entries = [e for e in cl.get("override_ledger", []) if e["kind"] == "waive"]
            self.assertEqual(len(entries), 1)
            self.assertTrue(entries[0]["forced"])
            self.assertTrue(entries[0]["authority_mismatch"])
            self.assertEqual(entries[0]["expected_authority"], "commander")

    def test_dispatch_waive_lookup_matches_waive_own_which_only_lookup(self):
        """Divergence trap: cond id "c1" exists in BOTH preconditions and
        postconditions with DIFFERENT override_policy.authority. waive() itself
        only ever searches the requested `which` list (no fallback) -- so
        waiving preconditions.c1 with authority "alpha" (which matches the
        PRECONDITION's policy, not the postcondition's "beta") must record a
        ledger entry carrying the precondition's own waived marker. If
        dispatch's re-lookup defaulted to postconditions (or otherwise ignored
        `which`), it would read the untouched postcondition's absent `waived`
        marker instead and the entry would come out empty."""
        t = gate("g1", "in-progress")
        t["preconditions"] = [{
            "id": "c1", "statement": "precond", "check": None, "satisfied": False,
            "override_policy": {"allowed": True, "authority": "alpha"},
        }]
        t["postconditions"] = [{
            "id": "c1", "statement": "postcond", "check": {"kind": "command", "command": FAIL_COMMAND},
            "satisfied": False, "override_policy": {"allowed": True, "authority": "beta"},
        }]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, gated(g1=t))
            self.assertEqual(
                E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                        "--which", "preconditions",
                        "--authority", "alpha", "--reason", "accepted"]), 0)
            cl = E.load(f)
            # the precondition was waived, the postcondition untouched
            self.assertTrue(cl["tasks"]["g1"]["preconditions"][0].get("waived"))
            self.assertFalse(cl["tasks"]["g1"]["postconditions"][0].get("waived"))
            entries = [e for e in cl.get("override_ledger", []) if e["kind"] == "waive"]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["authority"], "alpha")
            self.assertEqual(entries[0]["reason"], "accepted")
            self.assertNotIn("authority_mismatch", entries[0])

    def test_dispatch_call_records_waive_claim_release_direct_call_does_not(self):
        """The chokepoint proof, behavioral half: driving waive/claim --force/
        release --force through checklist_engine.dispatch() (the CLI path)
        appends entries; calling waive()/claim()/release() directly, as
        library functions -- simulating anything that is NOT the CLI
        chokepoint -- leaves override_ledger untouched."""
        # -- via dispatch() (CLI path) --
        cl = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            E.save(f, cl)
            E.main(["--file", str(f), "claim", "--session-id", "s1", "--claimed-by", "x"])
            E.main(["--file", str(f), "claim", "--session-id", "s2", "--claimed-by", "x",
                    "--force", "--reason", "takeover"])
            E.main(["--file", str(f), "waive", "g1", "--cond", "c1",
                    "--authority", "human", "--reason", "accepted",
                    "--session-id", "s2"])
            E.main(["--file", str(f), "release", "--session-id", "s3",
                    "--force", "--reason", "orphaned"])
            reloaded = E.load(f)
            kinds = sorted(e["kind"] for e in reloaded.get("override_ledger", []))
            self.assertEqual(kinds, ["force-claim", "force-release", "waive"])

        # -- direct library calls (NOT the CLI chokepoint) --
        direct = gated(g1=_waivable_gate("g1", FAIL_COMMAND))
        E.claim(direct, "s1", "x", ".", {})
        E.claim(direct, "s2", "x", ".", {}, force=True, reason="takeover")
        E.waive(direct, "g1", "c1", "postconditions", "human", "accepted")
        E.release(direct, "s2", force=True, reason="orphaned")
        self.assertNotIn("override_ledger", direct)


class ShippedTemplateBookendDeclarations(unittest.TestCase):
    """#634 declared the `bookend` freeze mechanism in the engine; issue g2
    puts the declaration on the templates that actually ship it. Pins the
    EXACT set of bookend-flagged gate ids per role spine template -- a test
    that only checked 'at least one gate is flagged' would still pass in a
    world where the flag landed on the wrong gate, so this asserts both the
    intended two carry it AND every other gate in that template does not."""

    EXPECTED = {
        ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json": {"init", "archive"},
        ROOT / "skills" / "admiral" / "templates" / "ADMIRAL_SPINE.template.json": {"init", "closeout"},
        ROOT / "skills" / "explorer" / "templates" / "EXPLORER_SPINE.template.json": {"init", "route"},
    }

    def test_exact_bookend_set_per_template(self):
        for path, expected_bookends in self.EXPECTED.items():
            with self.subTest(template=path.name):
                cl = json.loads(path.read_text(encoding="utf-8"))
                actual_bookends = {tid for tid, task in cl["tasks"].items()
                                    if task.get("bookend")}
                self.assertEqual(
                    actual_bookends, expected_bookends,
                    f"{path.name}: expected bookend gates {sorted(expected_bookends)}, "
                    f"got {sorted(actual_bookends)}",
                )


class ShippedBookendHumanAcceptance(unittest.TestCase):
    """#634 froze `archive` (Commander) and `route` (Explorer) against `amend`
    -- but it froze COMPLETION, not ACCEPTANCE. Neither bookend carried a
    human-acceptance postcondition of its own: Commander's five `archive`
    postconditions were all mechanical (episode captured, branch pushed, PR
    reachable, `spine_close` authorized, diff clean), and Explorer's one
    `route` postcondition was an attested outcome, `check: null`. The run's
    only `user-decision` evidence sat in the MUTABLE middle instead --
    `review` for Commander, `confirm` for Explorer -- where `amend` can drop
    or rescope the gate that carries it. Admiral's `closeout` already got this
    right (`c5`: "epic summary accepted by the human", `{"kind": "artifact",
    "evidence_type": "user-decision"}`); this pins that Commander's `archive`
    and Explorer's `route` now carry an equivalent postcondition of their own.

    Pins the exact check SHAPE, not just postcondition count: a test that only
    counted postconditions would still pass in a world where the new one
    checked the wrong `evidence_type` or wasn't a `kind: artifact` check at
    all -- neither actually closes the gap this issue names."""

    EXPECTED_BOOKEND_TASK = {
        ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json": "archive",
        ROOT / "skills" / "explorer" / "templates" / "EXPLORER_SPINE.template.json": "route",
    }

    def test_frozen_bookend_carries_its_own_user_decision_postcondition(self):
        for path, task_id in self.EXPECTED_BOOKEND_TASK.items():
            with self.subTest(template=path.name):
                cl = json.loads(path.read_text(encoding="utf-8"))
                task = cl["tasks"][task_id]
                self.assertTrue(task.get("bookend"), f"{task_id} must still be a bookend")
                matches = [
                    c for c in task["postconditions"]
                    if isinstance(c.get("check"), dict)
                    and c["check"].get("kind") == "artifact"
                    and c["check"].get("evidence_type") == "user-decision"
                ]
                self.assertTrue(
                    matches,
                    f"{path.name}'s frozen bookend gate {task_id!r} carries no "
                    "{'kind': 'artifact', 'evidence_type': 'user-decision'} "
                    "postcondition -- the run's human-acceptance evidence still "
                    "lives only in the mutable middle, exactly the #634 residue "
                    "this pins against.",
                )


class CommanderSpineBasisFields(unittest.TestCase):
    """569-w2-basis g2: hand-authored `basis` (the report-only locator
    mechanism g1 shipped -- see docs/CHECKLIST_SCHEMA.md's "Basis" subsection
    and `_resolve_basis_locator`) on exactly `plan.c2`/`plan.c4`/`plan.c5` in
    the shipped COMMANDER_SPINE.template.json -- this repo's first live
    application of the field to real shipped content. Every other condition
    in the file, across every gate, must stay byte-identical (no `basis` key
    at all) per the epic's `ruling-engine-first-backfill-where-it-earns-it`
    (exactly these 3, not a rollout) and the g2 handoff's Protected Intent.

    Pinned to this gate's shipped git HEAD per
    `ruling-red-proof-pinned-to-shipped-revision`: written and run BEFORE the
    template carried any `basis` key and observed to fail (RED -- see the g2
    IMPLEMENTER_RESULT for the transcript), then made to pass by the surgical
    text edit (GREEN). If HEAD has moved past the pinned commit, skip rather
    than assert against a template shape this test was never written against."""

    SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

    # Captured via `git rev-parse HEAD` at implementation time (g2 dispatch).
    PINNED_HEAD = "9d5aac6daa58a72fc6a665cb39879ee5705f7f71"

    EXPECTED_BASIS = {
        "c2": {
            "locator_kind": "file",
            "locator": {"path": ".agent-work/<work-id>/execute.json"},
        },
        "c4": {
            "locator_kind": "file",
            "locator": {
                "path": ".agent-work/<work-id>/plan-candidate-*.md",
                "glob": True,
                "min_matches": 2,
            },
        },
        "c5": {
            "locator_kind": "file",
            "locator": {"path": ".agent-work/<work-id>/PLAN_CRITIC.md"},
        },
    }

    def _skip_if_head_moved(self):
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        head = out.stdout.strip()
        if head != self.PINNED_HEAD:
            self.skipTest(
                f"pinned to shipped revision {self.PINNED_HEAD}, HEAD is now "
                f"{head} -- this test's assumptions about the template's "
                "shape need re-verifying against the current HEAD before "
                "they can be trusted, not silently re-run against drift"
            )

    def _load_spine(self):
        return json.loads(self.SPINE.read_text(encoding="utf-8"))

    def test_plan_c2_c4_c5_each_carry_the_ratified_basis_shape(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        by_id = {c["id"]: c for c in cl["tasks"]["plan"]["postconditions"]}
        for cond_id, expected in self.EXPECTED_BASIS.items():
            with self.subTest(cond=cond_id):
                basis = by_id[cond_id].get("basis")
                self.assertIsInstance(
                    basis, dict, f"plan.{cond_id} carries no basis object")
                self.assertEqual(basis["locator_kind"], expected["locator_kind"])
                self.assertEqual(basis["locator"], expected["locator"])
                self.assertIsInstance(
                    basis.get("because"), str,
                    f"plan.{cond_id}'s basis carries no 'because' rationale")
                self.assertTrue(basis["because"].strip())

    def test_no_condition_outside_plan_c2_c4_c5_carries_a_basis_key(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        carrying = []
        for task_id, t in cl["tasks"].items():
            for which in ("preconditions", "postconditions"):
                for c in t.get(which, []) or []:
                    if "basis" in c:
                        carrying.append(f"{task_id}.{c['id']}")
        self.assertEqual(
            sorted(carrying),
            sorted(f"plan.{cond_id}" for cond_id in self.EXPECTED_BASIS),
            "exactly plan.c2/c4/c5 -- and no other condition in the whole "
            "template -- may carry a basis key; a mismatch here means either "
            "a missed target or drift onto a protected condition",
        )

    def test_live_checklist_from_the_template_renders_basis_lines_at_plan(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        for iid in cl["items"]:
            if iid == "plan":
                break
            cl["tasks"][iid]["status"] = "complete"
        self.assertEqual(E.active_id(cl), "plan")
        out = E.current(cl)
        self.assertIn(
            "    basis: file .agent-work/<work-id>/execute.json", out)
        self.assertIn(
            "    basis: file .agent-work/<work-id>/plan-candidate-*.md", out)
        self.assertIn(
            "    basis: file .agent-work/<work-id>/PLAN_CRITIC.md", out)


def _gate_with_check(iid, check, status="in-progress"):
    """A gate whose single postcondition IS `check` -- the shipped shape
    copied verbatim from the template, never re-typed by hand."""
    t = gate(iid, status)
    t["postconditions"] = [
        {"id": "c1", "statement": "s", "check": check, "satisfied": False}
    ]
    return t


class CommanderSpineW3PromotePromotions(unittest.TestCase):
    """569-w3-promote g1: 8 named `check: null` conditions in the shipped
    COMMANDER_SPINE.template.json promoted to real, mechanically-checked
    conditions using only the engine's existing check kinds (`command`,
    `artifact`) per `decision:no-new-check-kinds` -- init.c1, plan.c1/c2/c4/
    c5, reconcile.c1, archive.c2/c3. Every other condition in the file, and
    every `basis` object already present on plan.c2/c4/c5 (CommanderSpine
    BasisFields above), is untouched.

    Modeled directly on CommanderSpineBasisFields above: pin PINNED_HEAD via
    `git rev-parse HEAD` captured at implementation time, `skipTest` (never
    fail) if HEAD has since moved past it -- this repo's edits are still
    uncommitted at authoring time, so HEAD is the base commit this gate's
    edit sits on top of, not a future commit; see that class's own docstring
    for why a moved HEAD skips rather than asserts against drift.

    Each promoted condition is attacked with an ADVERSARY-CHOSEN mutation --
    never a restatement of the check's own match text -- to prove the check
    can genuinely discriminate the healthy world from the defective one, per
    this epic's own thesis: a check with zero discriminating power is worse
    than the honest `check: null` it replaces."""

    SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

    # Captured via `git rev-parse HEAD` at implementation time (g1 dispatch).
    PINNED_HEAD = "135c34eb0b0a10bc5cebb0e6e3869b124e63735e"

    EXPECTED_CHECKS = {
        ("init", "c1"): {
            "kind": "command",
            "command": (
                "python3 -c \"import json,sys; "
                "d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', "
                "encoding='utf-8')); "
                "sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""
            ),
        },
        ("plan", "c1"): {
            "kind": "artifact", "evidence_type": "mission-frame",
            "match": {"status": ["produced", "skipped-as-trivial"]},
        },
        ("plan", "c2"): {
            "kind": "artifact", "evidence_type": "execute-plan",
            "match": {"exists": True},
        },
        ("plan", "c4"): {
            "kind": "artifact", "evidence_type": "plan-alternatives",
            "match": {"converged": True},
        },
        ("plan", "c5"): {
            "kind": "artifact", "evidence_type": "plan-critic",
            "match": {"triaged": True},
        },
        ("reconcile", "c1"): {
            "kind": "artifact", "evidence_type": "file-diff",
            "match": {"nonempty": True},
        },
        ("archive", "c2"): {
            "kind": "command",
            "command": (
                'test "$(git -C <repo-root> rev-parse @)" '
                '= "$(git -C <repo-root> rev-parse @{u})"'
            ),
        },
        ("archive", "c3"): {"kind": "artifact", "evidence_type": "user-decision"},
    }

    # Every condition (across pre- and post-conditions) that already carried a
    # non-null check BEFORE this gate's promotion, measured directly against
    # `git show HEAD:...` rather than trusted from the handoff's own prose --
    # the handoff's "pre-existing 5" undercounts these 13; see this class's
    # entry in the g1 IMPLEMENTER_RESULT's Workflow Feedback.
    PRE_EXISTING_NONNULL = {
        ("context", "c2"), ("understand", "c1"), ("plan", "c3"), ("plan", "c6"),
        ("execute", "p2"), ("execute", "c2"), ("triage", "c2"), ("review", "c1"),
        ("feedback", "c1"), ("archive", "c1"), ("archive", "c2b"), ("archive", "c4"),
        ("archive", "c5"),
    }

    def _skip_if_head_moved(self):
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        head = out.stdout.strip()
        if head != self.PINNED_HEAD:
            self.skipTest(
                f"pinned to shipped revision {self.PINNED_HEAD}, HEAD is now "
                f"{head} -- this test's assumptions about the template's "
                "shape need re-verifying against the current HEAD before "
                "they can be trusted, not silently re-run against drift"
            )

    def _load_spine(self):
        return json.loads(self.SPINE.read_text(encoding="utf-8"))

    def test_promoted_checks_match_shipped_shape(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        for (tid, cid), expected in self.EXPECTED_CHECKS.items():
            with self.subTest(cond=f"{tid}.{cid}"):
                by_id = {c["id"]: c for c in cl["tasks"][tid]["postconditions"]}
                self.assertEqual(by_id[cid]["check"], expected)

    def test_no_condition_outside_pre_existing_and_promoted_carries_a_check(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        nonnull = set()
        for tid, t in cl["tasks"].items():
            for which in ("preconditions", "postconditions"):
                for c in t.get(which) or []:
                    if c.get("check") is not None:
                        nonnull.add((tid, c["id"]))
        expected = self.PRE_EXISTING_NONNULL | set(self.EXPECTED_CHECKS)
        self.assertEqual(
            nonnull, expected,
            "exactly the 13 pre-existing non-null checks plus these 8 "
            "promotions -- and no other condition anywhere in the template "
            "-- may carry a check; a mismatch means either a missed target "
            "or drift onto a condition this gate must not touch",
        )

    # ---- artifact-kind promotions: attest() cross-task reference, exactly ----
    # the mechanism `docs/CHECKLIST_SCHEMA.md`'s "attest" row documents (verify
    # exists + evidence_type + match; never asserts an artifact from thin air).

    def _assert_artifact_discriminates(
        self, cid, wrong_type_evidence, adversary_payload, matching_payload,
    ):
        """Shared drive for every artifact-kind promotion below: (1) evidence
        of the WRONG `type` is refused on the `evidence_type` boundary; (2)
        evidence of the RIGHT type but an adversary-chosen non-matching
        payload is refused on the `match` boundary; (3) a genuinely matching
        payload satisfies it -- proving the check can pass as well as fail."""
        tid, real_cid = cid.split(".")
        check = self.EXPECTED_CHECKS[(tid, real_cid)]
        src = gate("src", "in-progress")
        target = _gate_with_check("target", check)
        cl = gated(src=src, target=target)

        # (1) wrong evidence_type -- attacks the TYPE boundary, not the match.
        E.attach(cl, "src", wrong_type_evidence, {})
        with self.assertRaisesRegex(
            E.EngineError,
            re.escape(f"is type {wrong_type_evidence!r}, not the required {check['evidence_type']!r}"),
        ):
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-1")

        # (2) right type, adversary-chosen non-matching payload -- attacks the
        # boundary the match does NOT restate; see each caller's own rationale.
        E.attach(cl, "src", check["evidence_type"], adversary_payload)
        with self.assertRaisesRegex(E.EngineError, "does not match required"):
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-2")

        # (3) positive control: a genuinely matching artifact DOES satisfy it.
        E.attach(cl, "src", check["evidence_type"], matching_payload)
        self.assertEqual(
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-3"),
            "attested target.c1 via e-src-3",
        )

    def test_plan_c1_mission_frame_status_membership_discriminates(self):
        self._skip_if_head_moved()
        # adversary: a differently-CASED status string -- attacks the
        # case-sensitivity boundary the match list does not spell out, not a
        # restatement of "produced" / "skipped-as-trivial" themselves.
        self._assert_artifact_discriminates(
            "plan.c1",
            wrong_type_evidence="user-decision",
            adversary_payload={"status": "Produced"},
            matching_payload={"status": "skipped-as-trivial"},
        )

    def test_plan_c2_execute_plan_existence_only_discriminates(self):
        self._skip_if_head_moved()
        # adversary: an EXPLICIT `exists: false` -- a real "checked for it and
        # it is NOT there" claim, distinct from simply attaching no evidence
        # at all (which a different assertion already covers via wrong-type).
        self._assert_artifact_discriminates(
            "plan.c2",
            wrong_type_evidence="mission-frame",
            adversary_payload={"exists": False},
            matching_payload={"exists": True},
        )

    def test_plan_c4_plan_alternatives_converged_discriminates(self):
        self._skip_if_head_moved()
        # adversary: the STRING "true" rather than the boolean True -- attacks
        # exact-type equality (`_artifact_match_satisfied` uses `==`, so a
        # truthy-looking string is not a truthy-looking bool), never a
        # restatement of "converged".
        self._assert_artifact_discriminates(
            "plan.c4",
            wrong_type_evidence="plan-critic",
            adversary_payload={"converged": "true"},
            matching_payload={"converged": True},
        )

    def test_plan_c5_plan_critic_triaged_discriminates(self):
        self._skip_if_head_moved()
        # adversary: an explicit `triaged: false` -- the actual defect this
        # check exists to catch (critic ran, findings never triaged), not a
        # restatement of the match's own "triaged" key.
        self._assert_artifact_discriminates(
            "plan.c5",
            wrong_type_evidence="plan-alternatives",
            adversary_payload={"triaged": False},
            matching_payload={"triaged": True},
        )

    def test_reconcile_c1_file_diff_nonempty_discriminates(self):
        self._skip_if_head_moved()
        # adversary: an explicit `nonempty: false` -- "the diff came back
        # empty", the actual defect (map never touched), not a restatement of
        # "nonempty" itself.
        self._assert_artifact_discriminates(
            "reconcile.c1",
            wrong_type_evidence="command-output",
            adversary_payload={"nonempty": False},
            matching_payload={"nonempty": True},
        )

    def test_archive_c3_user_decision_type_only_discriminates(self):
        self._skip_if_head_moved()
        # This check carries NO `match` at all (reuses the archive.c5 /
        # review.c1 / triage.c2 shape exactly), so `match={}` is vacuously
        # true for ANY payload of the right type -- the ONLY boundary this
        # check has is `evidence_type` itself. The adversary payload below is
        # therefore an arbitrary dict; what discriminates is exclusively (1).
        check = self.EXPECTED_CHECKS[("archive", "c3")]
        self.assertNotIn("match", check)
        src = gate("src", "in-progress")
        target = _gate_with_check("target", check)
        cl = gated(src=src, target=target)
        E.attach(cl, "src", "review-result", {"verdict": "APPROVE"})
        with self.assertRaisesRegex(
            E.EngineError,
            re.escape("is type 'review-result', not the required 'user-decision'"),
        ):
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-1")
        E.attach(cl, "src", "user-decision", {"cite": "spine_close"})
        self.assertEqual(
            E.attest(cl, "target", "c1", "postconditions", None, evidence_id="e-src-2"),
            "attested target.c1 via e-src-2",
        )

    # ---- command-kind promotions: `advance` runs them; `attest` refuses ----

    def test_init_c1_command_check_discriminates_lease_status(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("init", "c1")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            (root / ".agent-work" / work_id).mkdir(parents=True)
            spine_path = root / ".agent-work" / work_id / "spine.json"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real claim() write -- status == "active".
            spine_path.write_text(json.dumps({"engine_session": {"status": "active"}}), encoding="utf-8")
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): a status value the lease machinery
            # itself never legitimately writes -- claim() only ever writes
            # "active", release() only ever writes "released" -- this is
            # neither, so it attacks "the check ran and saw a BAD value", not
            # merely "the key/file was absent" (a different, easier defect).
            spine_path.write_text(
                json.dumps({"engine_session": {"status": "quantum-entangled-lease"}}),
                encoding="utf-8",
            )
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            # command checks are satisfied by `advance`, never `attest`.
            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)

    def test_archive_c2_command_check_discriminates_unpushed_commits(self):
        self._skip_if_head_moved()
        import shutil
        import subprocess
        if shutil.which("git") is None:
            self.skipTest("git not available")

        check = self.EXPECTED_CHECKS[("archive", "c2")]

        def run(args, cwd):
            r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            remote = Path(tmp) / "remote.git"
            repo.mkdir()
            remote.mkdir()
            run(["git", "init", "-q", "-b", "main"], repo)
            run(["git", "config", "user.email", "t@t.example"], repo)
            run(["git", "config", "user.name", "t"], repo)
            run(["git", "commit", "-q", "--allow-empty", "-m", "init"], repo)
            run(["git", "init", "-q", "--bare"], remote)
            run(["git", "remote", "add", "origin", str(remote)], repo)
            run(["git", "push", "-q", "-u", "origin", "main"], repo)

            cmd = check["command"].replace("<repo-root>", repo.as_posix())
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: pushed, local HEAD == upstream.
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): a LOCAL commit made AFTER the last
            # push -- attacks branch-ahead-of-upstream specifically, not "no
            # upstream configured at all" (a different, less targeted defect
            # this check would also refuse but which never probes the
            # boundary the check text actually names -- @ vs @{u}).
            run(["git", "commit", "-q", "--allow-empty", "-m", "unpushed"], repo)
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)


class AdmiralSpineW3PromotePromotions(unittest.TestCase):
    """569-w3-promote g3: 3 named `check: null` conditions in the shipped
    ADMIRAL_SPINE.template.json promoted to real, mechanically-checked
    conditions using only the engine's existing check kinds (`command`) per
    `decision:no-new-check-kinds` -- init.c2, latitude.c1, execute.c2. Every
    other condition in the file is untouched, including closeout.c4
    ("...ADMIRAL_LOG archived"), left `check: null` on purpose: its archive
    destination (`scripts/spine_lifecycle.py::archive_name_for`) is
    `f"{today}-{work_id.replace('/', '-')}"`, keyed on the wall-clock date at
    CLOSE time (unknown at spine-authoring time, so no fixed path exists to
    write into a check) AND on a `/` -> `-` transform of `work_id` that the
    resolver's own `<work-id>` substitution (`resolve_spine`, a blind
    `str.replace`) never performs -- so even a glob-based check baked in at
    authoring time would silently mismatch for any work_id containing `/`, a
    shape the resolver's own docstring treats as legal. Neither half is a
    "real, stable path convention" a hand-authored check text can pin; per
    the handoff's own stated fallback this condition stays `check: null`.

    init.c2's promotion mirrors g1's already-landed COMMANDER_SPINE.template.json
    init.c1 EXACTLY (same seam: both roles' own spine.json lives at the same
    `.agent-work/<work-id>/spine.json` path) -- `command` is independently
    justified against THIS template's own pre-existing checks too: init.c1
    (same gate), execute.p2, execute.c3, and closeout.c2 are all already
    `command`-kind here, so this is not this template's first use of the
    kind. latitude.c1 and execute.c2 are new `command` text (not copied from
    a sibling template) but the same reasoning applies: `command` is this
    template's dominant pre-existing kind (4 uses spanning lease status,
    state-note verification, wave-transition verification, and episode
    capture) versus `artifact`, used here only twice and only ever for
    `user-decision` (a human-confirmation event genuinely populated by a real
    interaction) -- introducing a NEW `artifact` evidence_type for a raw file-
    existence claim would rely on trusting a hand-typed attest payload
    (`attest()`'s artifact path never touches the filesystem; only `basis`,
    which is report-only and inert once `check` is non-null, does that), so
    `command` is the more genuinely mechanical, less decorative choice here.

    Modeled directly on CommanderSpineW3PromotePromotions above: pin
    PINNED_HEAD via `git rev-parse HEAD` captured at implementation time,
    `skipTest` (never fail) if HEAD has since moved past it -- this repo's
    edits are still uncommitted at authoring time, so HEAD is the base
    commit (g1's own merged promotion) this gate's edit sits on top of, not
    a future commit.

    Each promoted condition is attacked with an ADVERSARY-CHOSEN mutation --
    never a restatement of the check's own match text -- to prove the check
    can genuinely discriminate the healthy world from the defective one, per
    this epic's own thesis: a check with zero discriminating power is worse
    than the honest `check: null` it replaces."""

    SPINE = ROOT / "skills" / "admiral" / "templates" / "ADMIRAL_SPINE.template.json"

    # Captured via `git rev-parse HEAD` at implementation time (g3 dispatch,
    # sitting on top of g1's already-merged COMMANDER_SPINE promotion).
    PINNED_HEAD = "ff8e96402a6a76cc6e7f5c1bd92e91b36c830156"

    EXPECTED_CHECKS = {
        ("init", "c2"): {
            "kind": "command",
            "command": (
                "python3 -c \"import json,sys; "
                "d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', "
                "encoding='utf-8')); "
                "sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""
            ),
        },
        ("latitude", "c1"): {
            "kind": "command",
            "command": 'test -s "<repo-root>/.agent-work/<work-id>/LATITUDE_CONTRACT.md"',
        },
        ("execute", "c2"): {
            "kind": "command",
            "command": (
                'test -s "<repo-root>/.agent-work/<work-id>/ADMIRAL_LOG.md" '
                '&& grep -qE "^- TRANSITION" "<repo-root>/.agent-work/<work-id>/ADMIRAL_LOG.md"'
            ),
        },
    }

    # Every condition (across pre- and post-conditions) that already carried a
    # non-null check BEFORE this gate's promotion, measured directly against
    # `git show HEAD:...` rather than trusted from the handoff's own prose.
    PRE_EXISTING_NONNULL = {
        ("init", "c1"), ("latitude", "c2"), ("execute", "p2"), ("execute", "c3"),
        ("closeout", "c2"), ("closeout", "c5"),
    }

    def _skip_if_head_moved(self):
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        head = out.stdout.strip()
        if head != self.PINNED_HEAD:
            self.skipTest(
                f"pinned to shipped revision {self.PINNED_HEAD}, HEAD is now "
                f"{head} -- this test's assumptions about the template's "
                "shape need re-verifying against the current HEAD before "
                "they can be trusted, not silently re-run against drift"
            )

    def _load_spine(self):
        return json.loads(self.SPINE.read_text(encoding="utf-8"))

    def test_promoted_checks_match_shipped_shape(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        for (tid, cid), expected in self.EXPECTED_CHECKS.items():
            with self.subTest(cond=f"{tid}.{cid}"):
                by_id = {c["id"]: c for c in cl["tasks"][tid]["postconditions"]}
                self.assertEqual(by_id[cid]["check"], expected)

    def test_closeout_c4_stays_null(self):
        """closeout.c4 ('branches dispositioned, worktrees swept, ADMIRAL_LOG
        archived') is the one condition this gate's own handoff named as a
        candidate and then explicitly declined -- pin that it stays `check:
        null` rather than silently drifting either way."""
        self._skip_if_head_moved()
        cl = self._load_spine()
        by_id = {c["id"]: c for c in cl["tasks"]["closeout"]["postconditions"]}
        self.assertIsNone(by_id["c4"]["check"])

    def test_no_condition_outside_pre_existing_and_promoted_carries_a_check(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        nonnull = set()
        for tid, t in cl["tasks"].items():
            for which in ("preconditions", "postconditions"):
                for c in t.get(which) or []:
                    if c.get("check") is not None:
                        nonnull.add((tid, c["id"]))
        expected = self.PRE_EXISTING_NONNULL | set(self.EXPECTED_CHECKS)
        self.assertEqual(
            nonnull, expected,
            "exactly the 6 pre-existing non-null checks plus these 3 "
            "promotions -- and no other condition anywhere in the template, "
            "including closeout.c4 -- may carry a check; a mismatch means "
            "either a missed target or drift onto a condition this gate "
            "must not touch",
        )

    # ---- command-kind promotions: `advance` runs them; `attest` refuses ----

    def test_init_c2_command_check_discriminates_lease_status(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("init", "c2")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            (root / ".agent-work" / work_id).mkdir(parents=True)
            spine_path = root / ".agent-work" / work_id / "spine.json"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real claim() write -- status == "active".
            spine_path.write_text(json.dumps({"engine_session": {"status": "active"}}), encoding="utf-8")
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): a status value the lease machinery
            # itself never legitimately writes -- claim() only ever writes
            # "active", release() only ever writes "released" -- this is
            # neither, so it attacks "the check ran and saw a BAD value", not
            # merely "the key/file was absent" (a different, easier defect).
            spine_path.write_text(
                json.dumps({"engine_session": {"status": "half-claimed"}}),
                encoding="utf-8",
            )
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            # command checks are satisfied by `advance`, never `attest`.
            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)

    def test_latitude_c1_command_check_discriminates_empty_file(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("latitude", "c1")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            work_dir = root / ".agent-work" / work_id
            work_dir.mkdir(parents=True)
            contract_path = work_dir / "LATITUDE_CONTRACT.md"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real, filled-in contract.
            contract_path.write_text("# Latitude Contract\n\ndecision classes: ...\n", encoding="utf-8")
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): the file EXISTS (a bare `test -f`
            # or `.exists()` claim would pass) but is EMPTY -- attacks the
            # nonempty boundary `-s` adds over plain existence, not the
            # easier "file missing entirely" defect.
            contract_path.write_text("", encoding="utf-8")
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)

    def test_execute_c2_command_check_discriminates_case_sensitive_grammar(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("execute", "c2")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            work_dir = root / ".agent-work" / work_id
            work_dir.mkdir(parents=True)
            log_path = work_dir / "ADMIRAL_LOG.md"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real TRANSITION line in the documented grammar.
            log_path.write_text(
                "# ADMIRAL_LOG\n\n- TRANSITION | boundary=b1 | decision=advance | verified\n",
                encoding="utf-8",
            )
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): the file is genuinely nonempty and
            # even mentions a transition, but NOT in the documented `^- TRANSITION`
            # grammar (lower-cased) -- attacks the pattern-match boundary
            # specifically, not the easier "file empty/missing" defect a
            # different assertion already covers.
            log_path.write_text(
                "# ADMIRAL_LOG\n\n- transition | boundary=b1 | decision=advance | verified\n",
                encoding="utf-8",
            )
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)


class ExplorerSpineW3PromotePromotions(unittest.TestCase):
    """569-w3-promote g4: 3 named `check: null` conditions in the shipped
    EXPLORER_SPINE.template.json promoted to real, mechanically-checked
    conditions using only the engine's existing check kinds (`command`) per
    `decision:no-new-check-kinds` -- init.c2, context.c1, spec.c1. Every
    other condition in the file is untouched, including route.c1
    ("confirmed spec routed (handed off / shaped-design issue filed /
    shelved with UNCONFIRMED header); work area archived; engine lease
    released"), left `check: null` on purpose: the handoff asked for a FULL
    promotion via an artifact enum-match on the 3 named routing outcomes
    ONLY IF each outcome has its own real, independently-checkable artifact.
    No routing tooling exists for any of the three (no `verify_*.py --phase
    route` script the way `verify_spec_confirmed.py` has a `review` phase,
    no persisted per-outcome record distinguishing "handed off" from "issue
    filed" from "shelved" -- SHAPED_BRIEF.json exists identically across all
    three outcomes, created upstream at `confirm`, so its presence cannot
    discriminate which routing path was taken). Per the handoff's own stated
    fallback ("leave the whole condition check: null and say so"), route.c1
    stays null.

    init.c2's promotion mirrors g1's already-landed COMMANDER_SPINE.template.json
    init.c1 and g3's already-landed ADMIRAL_SPINE.template.json init.c2
    EXACTLY (same seam: every role's own spine.json lives at the same
    `.agent-work/<work-id>/spine.json` path) -- `command` is independently
    justified against THIS template's own pre-existing checks too: init.c1
    (same gate), explore.c2, review.c1, and confirm.c2/c3 are all already
    `command`-kind here, so this is not this template's first use of the
    kind.

    context.c1 and spec.c1 are SPLIT promotions (mirroring COMMANDER_SPINE's
    own plan.c2): each condition's prose names two things -- a judgment
    half (whether doctrine/deltas/map were genuinely read; whether
    per-section approval and designed-it-twice fidelity were genuinely
    obtained) and a locatable-artifact half (IDEAS_BOARD.md / DESIGN_SPEC.md
    existing and nonempty, both real fixed paths named in each task's own
    imperative text). Only the artifact half is promoted; the `statement`
    text is left untouched (it still names both halves), and NO `basis`
    field is added -- `decision:no-basis-backfill` reserves that mechanism
    for w3-basis's own population; this gate's job is promotion only, and
    the check's honest existence-only scope is documented here, in this
    test class, rather than in a new `basis` object on the shipped
    condition. `command` (`test -s`) is the kind chosen for both, not
    `artifact`: `artifact` appears in this template
    only three times (explore.c1, confirm.c1, route.c2) and only ever for
    `evidence_type: user-decision`, a human-confirmation event genuinely
    populated by a real interaction -- introducing a NEW `artifact`
    evidence_type for a raw file-existence claim would rely on trusting a
    hand-typed attest payload (`attest()`'s artifact path never touches the
    filesystem; only `basis`, which is report-only, does that), so `command`
    is the more genuinely mechanical, less decorative choice here -- the
    same reasoning ADMIRAL_SPINE's own docstring gives for latitude.c1 and
    execute.c2, and the same check text shape (`test -s "<path>"`) as that
    template's own latitude.c1.

    Both context and spec each carry exactly ONE postcondition, so promoting
    either clears an all-null gate per `scripts/validate_spine.py`'s
    `falsifiable-all-null` fault (postcondition-only, ignores preconditions):
    the corpus-wide count drops from 17 (measured after g1+g3) to 15;
    `tests/test_validate_spine.py`'s floor is updated in the same edit as g1's
    own discipline (message text only -- the `>= 15` threshold itself still
    holds at exactly 15, so it is left as a live floor rather than lowered
    with slack, per the same "never move it silently" doctrine that pin
    already states).

    Modeled directly on CommanderSpineW3PromotePromotions /
    AdmiralSpineW3PromotePromotions above: pin PINNED_HEAD via `git rev-parse
    HEAD` captured at implementation time, `skipTest` (never fail) if HEAD
    has since moved past it -- this repo's edits are still uncommitted at
    authoring time, so HEAD is the base commit (g3's own merged promotion)
    this gate's edit sits on top of, not a future commit.

    Each promoted condition is attacked with an ADVERSARY-CHOSEN mutation --
    never a restatement of the check's own match text -- to prove the check
    can genuinely discriminate the healthy world from the defective one, per
    this epic's own thesis: a check with zero discriminating power is worse
    than the honest `check: null` it replaces."""

    SPINE = ROOT / "skills" / "explorer" / "templates" / "EXPLORER_SPINE.template.json"

    # Captured via `git rev-parse HEAD` at implementation time (g4 dispatch,
    # sitting on top of g3's already-merged ADMIRAL_SPINE promotion).
    PINNED_HEAD = "44180fe09c0357a7c2ffcefcaeea378b6e9ccecd"

    EXPECTED_CHECKS = {
        ("init", "c2"): {
            "kind": "command",
            "command": (
                "python3 -c \"import json,sys; "
                "d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', "
                "encoding='utf-8')); "
                "sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""
            ),
        },
        ("context", "c1"): {
            "kind": "command",
            "command": 'test -s "<repo-root>/.agent-work/<work-id>/IDEAS_BOARD.md"',
        },
        ("spec", "c1"): {
            "kind": "command",
            "command": 'test -s "<repo-root>/.agent-work/<work-id>/DESIGN_SPEC.md"',
        },
    }

    # Every condition (across pre- and post-conditions) that already carried a
    # non-null check BEFORE this gate's promotion, measured directly against
    # `git show HEAD:...` rather than trusted from the handoff's own prose.
    PRE_EXISTING_NONNULL = {
        ("init", "c1"), ("explore", "c1"), ("explore", "c2"), ("review", "c1"),
        ("confirm", "c1"), ("confirm", "c2"), ("confirm", "c3"), ("route", "c2"),
    }

    def _skip_if_head_moved(self):
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        head = out.stdout.strip()
        if head != self.PINNED_HEAD:
            self.skipTest(
                f"pinned to shipped revision {self.PINNED_HEAD}, HEAD is now "
                f"{head} -- this test's assumptions about the template's "
                "shape need re-verifying against the current HEAD before "
                "they can be trusted, not silently re-run against drift"
            )

    def _load_spine(self):
        return json.loads(self.SPINE.read_text(encoding="utf-8"))

    def test_promoted_checks_match_shipped_shape(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        for (tid, cid), expected in self.EXPECTED_CHECKS.items():
            with self.subTest(cond=f"{tid}.{cid}"):
                by_id = {c["id"]: c for c in cl["tasks"][tid]["postconditions"]}
                self.assertEqual(by_id[cid]["check"], expected)

    def test_route_c1_stays_null(self):
        """route.c1 ('confirmed spec routed ...; work area archived; engine
        lease released') is the one condition this gate's own handoff named
        as a candidate FULL promotion and then explicitly declined for lack
        of a real per-outcome artifact -- pin that it stays `check: null`
        rather than silently drifting either way."""
        self._skip_if_head_moved()
        cl = self._load_spine()
        by_id = {c["id"]: c for c in cl["tasks"]["route"]["postconditions"]}
        self.assertIsNone(by_id["c1"]["check"])

    def test_context_c1_and_spec_c1_keep_their_unsplit_statement_and_no_basis(self):
        """The SPLIT promotions must not let the `statement` text imply the
        check covers more than the file-existence half it actually checks,
        and must NOT gain a `basis` field either --
        `decision:no-basis-backfill` reserves that mechanism for w3-basis's
        own population, not this gate's promotions. Pin both: statement
        stays byte-identical, and no `basis` key was introduced."""
        self._skip_if_head_moved()
        cl = self._load_spine()
        context_c1 = cl["tasks"]["context"]["postconditions"][0]
        spec_c1 = cl["tasks"]["spec"]["postconditions"][0]
        self.assertEqual(
            context_c1["statement"],
            "doctrine + project deltas + map read where they exist; "
            "IDEAS_BOARD.md seeded from template",
        )
        self.assertNotIn("basis", context_c1)
        self.assertEqual(
            spec_c1["statement"],
            "DESIGN_SPEC.md crystallized from the board with per-section "
            "approval; load-bearing interfaces designed-it-twice or skipped "
            "with a stated reason",
        )
        self.assertNotIn("basis", spec_c1)

    def test_no_condition_outside_pre_existing_and_promoted_carries_a_check(self):
        self._skip_if_head_moved()
        cl = self._load_spine()
        nonnull = set()
        for tid, t in cl["tasks"].items():
            for which in ("preconditions", "postconditions"):
                for c in t.get(which) or []:
                    if c.get("check") is not None:
                        nonnull.add((tid, c["id"]))
        expected = self.PRE_EXISTING_NONNULL | set(self.EXPECTED_CHECKS)
        self.assertEqual(
            nonnull, expected,
            "exactly the 8 pre-existing non-null checks plus these 3 "
            "promotions -- and no other condition anywhere in the template, "
            "including route.c1 -- may carry a check; a mismatch means "
            "either a missed target or drift onto a condition this gate "
            "must not touch",
        )

    # ---- command-kind promotions: `advance` runs them; `attest` refuses ----

    def test_init_c2_command_check_discriminates_lease_status(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("init", "c2")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            (root / ".agent-work" / work_id).mkdir(parents=True)
            spine_path = root / ".agent-work" / work_id / "spine.json"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real claim() write -- status == "active".
            spine_path.write_text(json.dumps({"engine_session": {"status": "active"}}), encoding="utf-8")
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): a status value the lease machinery
            # itself never legitimately writes -- claim() only ever writes
            # "active", release() only ever writes "released" -- this is
            # neither, so it attacks "the check ran and saw a BAD value", not
            # merely "the key/file was absent" (a different, easier defect).
            spine_path.write_text(
                json.dumps({"engine_session": {"status": "stale-explorer-lease"}}),
                encoding="utf-8",
            )
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            # command checks are satisfied by `advance`, never `attest`.
            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)

    def test_context_c1_command_check_discriminates_empty_board(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("context", "c1")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            work_dir = root / ".agent-work" / work_id
            work_dir.mkdir(parents=True)
            board_path = work_dir / "IDEAS_BOARD.md"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real board seeded from the template.
            board_path.write_text("# Ideas Board\n\nthe point: ...\n", encoding="utf-8")
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): the file EXISTS (a bare `test -f`
            # or `.exists()` claim would pass) but is EMPTY -- attacks the
            # nonempty boundary `-s` adds over plain existence, not the
            # easier "file missing entirely" defect.
            board_path.write_text("", encoding="utf-8")
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)

    def test_spec_c1_command_check_discriminates_empty_spec(self):
        self._skip_if_head_moved()
        check = self.EXPECTED_CHECKS[("spec", "c1")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id = "w1"
            work_dir = root / ".agent-work" / work_id
            work_dir.mkdir(parents=True)
            spec_path = work_dir / "DESIGN_SPEC.md"
            cmd = check["command"].replace("<repo-root>", root.as_posix()).replace("<work-id>", work_id)
            resolved = {"kind": "command", "command": cmd}

            # HEALTHY: a real spec crystallized from the board.
            spec_path.write_text(
                "# Design Spec\n\nUNCONFIRMED -- DO NOT CUT\n", encoding="utf-8",
            )
            cl_ok = gated(g1=_gate_with_check("g1", resolved))
            self.assertEqual(E.advance(cl_ok, "g1"), "g1 -> complete")

            # DEFECTIVE (adversary-chosen): the file EXISTS but is EMPTY --
            # same nonempty boundary as context.c1 above, not the easier
            # "file missing entirely" defect.
            spec_path.write_text("", encoding="utf-8")
            cl_bad = gated(g1=_gate_with_check("g1", resolved))
            with self.assertRaises(E.EngineError):
                E.advance(cl_bad, "g1")

            with self.assertRaisesRegex(E.EngineError, "engine-checked; cannot attest"):
                E.attest(cl_bad, "g1", "c1", "postconditions", None)
