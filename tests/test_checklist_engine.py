import copy
import importlib.util
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

    def _write_child(self, d, verdict):
        cons = {"verdict": verdict, "findings": []} if verdict else None
        child = survey(v1=survey_item("v1", "complete"))
        child["consolidation"] = cons
        p = Path(d) / "child.json"
        E.save(p, child)
        return p

    def test_advance_from_child_approve_completes(self):
        with tempfile.TemporaryDirectory() as d:
            child = self._write_child(d, "APPROVE")
            cl = self._review_gate()
            msg = E.advance(cl, "g1", from_child=str(child), base_dir=Path(d))
            self.assertEqual(msg, "g1 -> complete")
            self.assertEqual(cl["tasks"]["g1"]["status"], "complete")

    def test_advance_from_child_block_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            child = self._write_child(d, "BLOCK")
            cl = self._review_gate()
            with self.assertRaises(E.EngineError):
                E.advance(cl, "g1", from_child=str(child), base_dir=Path(d))
            self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
            # the child's verdict was still attached as evidence
            self.assertTrue(any(e["type"] == "review-result" for e in cl["tasks"]["g1"]["evidence"]))

    def test_advance_from_child_without_consolidation_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            child = self._write_child(d, None)
            cl = self._review_gate()
            with self.assertRaises(E.EngineError):
                E.advance(cl, "g1", from_child=str(child), base_dir=Path(d))

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
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        out = E.current(cl)  # read-only, no session needed
        self.assertIn("LEASE active: s1", out)
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
                self.assertTrue(E.current(data).startswith("ACTIVE"))


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


class DoctrineRail(unittest.TestCase):
    """#138 channel A: the engine appends position-derived doctrine to railed verbs'
    success output and the check-failure rail to the REFUSED path. The five strings
    are frozen/verbatim; these tests pin the exact asserted substrings."""

    def test_rail_verbs_set_is_exact(self):
        # Only these six verbs are railed; heartbeat/release/record/skip are not.
        self.assertEqual(
            E.RAIL_VERBS,
            {"claim", "current", "start", "advance", "attest", "attach"},
        )
        for unrailed in ("heartbeat", "release", "record", "skip", "consolidate"):
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
    the FRONT for every railed verb (including `current`), and to the front
    of the REFUSED path in main() -- the operative result/refusal line lands
    LAST on its stream, so `tail -1` reads the result, not the banner. This
    is the exact field defect: the Admiral piped engine output through
    `tail -1` and saw only the banner, silently hiding a real REFUSED line."""

    def test_success_output_rail_banner_is_first_operative_line_is_last(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND), g2=gate("g2"))
        code, out, err = _run_main(cl, ["advance", "g1", "--mechanical"])
        self.assertEqual(code, 0)
        lines = [ln for ln in out.splitlines() if ln.strip()]
        self.assertTrue(lines[0].startswith("RAIL: "), lines)
        self.assertEqual(lines[-1], "g1 -> complete")

    def test_current_rail_banner_is_first_suffix_ordering_after_body_unchanged(self):
        cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND),
                   g2=gate("g2"), g3=gate("g3"))
        code, out, err = _run_main(cl, ["current"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("RAIL: "))
        self.assertLess(out.index("RAIL: "), out.index("ACTIVE g1"))

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
        self.assertTrue(E.has_pending_refresh_request(cl, "g2"))
        out = E.current(cl)
        self.assertIn("REFRESH REQUESTED:", out)
        self.assertIn(why_ref, out)  # the why_ref pointer surfaces on the line

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


class FromChildAttachIdempotent(unittest.TestCase):
    """#191 — the `advance --from-child` seam is dedup-idempotent: a refused advance
    (which `main()` persists) followed by a retry must NOT double-attach the child
    consolidation. The attach stays BEFORE the postcondition/why guards; the fix is
    a dedup, not a reorder."""

    def _review_gate(self):
        # non-exempt gate whose artifact postcondition is satisfied by the from-child
        # review-result — so the refusal that fires is the why-capture one, AFTER the
        # attach (the double-attach window this fix closes).
        t = gate("g1", "in-progress", why_exempt=False)
        t["postconditions"] = [{
            "id": "c2", "statement": "approved",
            "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}},
            "satisfied": False,
        }]
        t["child_checklist"] = "child"
        return gated(g1=t)

    def _write_child(self, d):
        cons = {"verdict": "APPROVE", "findings": []}
        child = survey(v1=survey_item("v1", "complete"))
        child["consolidation"] = cons
        p = Path(d) / "child.json"
        E.save(p, child)
        return p

    def _review_results(self, cl):
        return [e for e in cl["tasks"]["g1"]["evidence"] if e["type"] == "review-result"]

    def test_refuse_then_retry_attaches_exactly_one(self):
        with tempfile.TemporaryDirectory() as d:
            child = self._write_child(d)
            cl = self._review_gate()
            # first attempt: no --why -> refuses AFTER the from-child attach
            with self.assertRaises(E.EngineError):
                E.advance(cl, "g1", from_child=str(child), base_dir=Path(d))
            self.assertEqual(len(self._review_results(cl)), 1)
            # retry, still no --why -> dedup, STILL exactly one
            with self.assertRaises(E.EngineError):
                E.advance(cl, "g1", from_child=str(child), base_dir=Path(d))
            self.assertEqual(len(self._review_results(cl)), 1)
            # finally with --why -> completes, STILL exactly one
            msg = E.advance(cl, "g1", from_child=str(child), base_dir=Path(d), why="ok")
            self.assertEqual(msg, "g1 -> complete")
            self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
            self.assertEqual(len(self._review_results(cl)), 1)

    def test_cli_refuse_then_retry_persists_exactly_one(self):
        # CLI round-trip: main() actually SAVES on the refused advance, so this
        # exercises the real double-attach path the dedup closes.
        with tempfile.TemporaryDirectory() as d:
            child = self._write_child(d)
            cl = self._review_gate()
            spine = Path(d) / "spine.json"
            E.save(spine, cl)
            self.assertEqual(
                E.main(["--file", str(spine), "advance", "g1", "--from-child", str(child)]), 1)
            self.assertEqual(len(self._review_results(E.load(spine))), 1)
            self.assertEqual(
                E.main(["--file", str(spine), "advance", "g1", "--from-child", str(child)]), 1)
            self.assertEqual(len(self._review_results(E.load(spine))), 1)
            self.assertEqual(
                E.main(["--file", str(spine), "advance", "g1", "--from-child", str(child),
                        "--why", "ok"]), 0)
            reloaded = E.load(spine)
            self.assertEqual(reloaded["tasks"]["g1"]["status"], "complete")
            self.assertEqual(len(self._review_results(reloaded)), 1)


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


def _advance_ns(iid="g1"):
    return types.SimpleNamespace(
        verb="advance", id=iid, from_child=None, why=None,
        mechanical=False, session_id=None,
    )


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
    def test_hard_refuses_at_and_above_hard_without_refresh(self):
        # Acceptance 2/4 (falsifiable: does HARD ever let you pass without a
        # refresh-request? -> NO): at/above hard with no refresh-request, advance
        # REFUSES and the gate stays in-progress.
        for fill in (self.hard, min(self.hard + 0.05, 1.0)):
            cl = copy.deepcopy(self.cl)
            with mock.patch.object(E, "_read_gauge", return_value=_reading(fill)):
                with self.assertRaises(E.EngineError) as ctx:
                    E.dispatch(cl, _advance_ns("g1"), base_dir=Path("."))
            self.assertEqual(cl["tasks"]["g1"]["status"], "in-progress")
            self.assertIn("refresh", str(ctx.exception).lower())
            self.assertIn("attach g1 --type refresh-request", str(ctx.exception))

    def test_hard_never_refuses_below_hard(self):
        # Acceptance 2: just below hard, HARD does not fire — advance passes.
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard - 0.001)):
            msg = E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertIn("g1 -> complete", msg)

    def test_hard_passes_once_refresh_request_exists(self):
        # HARD forces UNTIL a refresh-request exists for the gate; with one present,
        # advance is allowed through (the agent has already requested the refresh).
        E.attach(self.cl, "g1", "refresh-request", {"seam": "g1", "why_ref": "w-1"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            msg = E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertIn("g1 -> complete", msg)
        self.assertEqual(self.cl["tasks"]["g1"]["status"], "complete")

    def test_hard_refusal_leaves_state_unmutated(self):
        # A HARD refusal is raised BEFORE the verb runs: no why_trail, no status flip.
        before = copy.deepcopy(self.cl)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(self.cl, _advance_ns("g1"), base_dir=Path("."))
        self.assertEqual(self.cl, before)

    def test_hard_advisory_on_current_points_at_attach(self):
        # On the read-only `current`, the HARD band escalates the advisory to the
        # exact remedy (the attach command) and flags that advance is blocked.
        with mock.patch.object(E, "_read_gauge", return_value=_reading(self.hard)):
            out = E.dispatch(self.cl, types.SimpleNamespace(verb="current"),
                             base_dir=Path("."))
        self.assertIn(">= hard", out)
        self.assertIn("BLOCKED", out)
        self.assertIn("attach g1 --type refresh-request", out)

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
        self.assertIsNone(E._gauge_path(None))
        self.assertIsNone(E._read_gauge(None))
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
        # distinct new trip through HARD on the same still-open gate; a FRESH request
        # keyed to the current digest releases it.
        _, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        cl = gated(
            g1=gate("g1", "in-progress", command=PASS_COMMAND, why_exempt=False),
            g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=False),
            g3=gate("g3", "pending", command=PASS_COMMAND, why_exempt=False),
        )
        E.advance(cl, "g1", why="u1")                 # -> w-1
        E.start(cl, "g2"); E.advance(cl, "g2", why="u2")  # -> w-2; g3 active, latest why w-2
        E.start(cl, "g3")
        # stale request keyed to w-1 (an earlier trip's understanding)
        E.attach(cl, "g3", "refresh-request", {"seam": "g3", "why_ref": "w-1"})
        adv = types.SimpleNamespace(verb="advance", id="g3", from_child=None,
                                    why="u3", mechanical=False, session_id=None)
        before = copy.deepcopy(cl)
        with mock.patch.object(E, "_read_gauge", return_value=_reading(hard)):
            with self.assertRaises(E.EngineError):
                E.dispatch(cl, adv, base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g3"]["status"], "in-progress")  # unmutated
        self.assertEqual(cl, before)
        # a FRESH request keyed to the current digest (w-2) releases HARD
        E.attach(cl, "g3", "refresh-request", {"seam": "g3", "why_ref": "w-2"})
        with mock.patch.object(E, "_read_gauge", return_value=_reading(hard)):
            msg = E.dispatch(cl, adv, base_dir=Path("."))
        self.assertIn("g3 -> complete", msg)
        self.assertEqual(cl["tasks"]["g3"]["status"], "complete")


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
    the FIRST non-empty result -- the three sub-advisories are mocked
    directly (band-structure style) since this is testing DISPATCH ORDER,
    not any one advisory's own text."""

    def test_uncalibrated_wins_over_skip_and_stale(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value="\nCONTEXT GAUGE OFF: x"), \
             mock.patch.object(E, "_skip_reason_advisory", return_value="\nCONTEXT GAUGE SILENT: skip"), \
             mock.patch.object(E, "_stale_record_advisory", return_value="\nCONTEXT GAUGE SILENT: stale"):
            self.assertEqual(E._no_reading_advisory(Path(".")), "\nCONTEXT GAUGE OFF: x")

    def test_skip_reason_wins_over_stale_when_uncalibrated_empty(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value=""), \
             mock.patch.object(E, "_skip_reason_advisory", return_value="\nCONTEXT GAUGE SILENT: skip"), \
             mock.patch.object(E, "_stale_record_advisory", return_value="\nCONTEXT GAUGE SILENT: stale"):
            self.assertEqual(E._no_reading_advisory(Path(".")), "\nCONTEXT GAUGE SILENT: skip")

    def test_stale_record_is_the_last_resort(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value=""), \
             mock.patch.object(E, "_skip_reason_advisory", return_value=""), \
             mock.patch.object(E, "_stale_record_advisory", return_value="\nCONTEXT GAUGE SILENT: stale"):
            self.assertEqual(E._no_reading_advisory(Path(".")), "\nCONTEXT GAUGE SILENT: stale")

    def test_all_empty_yields_empty(self):
        with mock.patch.object(E, "_uncalibrated_advisory", return_value=""), \
             mock.patch.object(E, "_skip_reason_advisory", return_value=""), \
             mock.patch.object(E, "_stale_record_advisory", return_value=""):
            self.assertEqual(E._no_reading_advisory(Path(".")), "")


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

    def test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh(self):
        soft, hard = E._gauge_reader.thresholds_for("claude-opus-4-8")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spine.json"
            E.save(f, self._spine())
            # gauge sibling of the spine, fresh (observed_at == now), fill >= hard
            self._write_gauge(d, min(hard + 0.05, 1.0),
                              datetime.now(timezone.utc).isoformat())
            import contextlib, io
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = E.main(["--file", str(f), "advance", "g1"])
            self.assertEqual(rc, 1)  # HARD refuses
            self.assertIn("REFUSED:", err.getvalue())
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "in-progress")
            # request a refresh, then the same advance is allowed through
            self.assertEqual(
                E.main(["--file", str(f), "attach", "g1", "--type", "refresh-request",
                        "--field", "seam=g1", "--field", "why_ref=w-1"]), 0)
            self.assertEqual(E.main(["--file", str(f), "advance", "g1"]), 0)
            self.assertEqual(E.load(f)["tasks"]["g1"]["status"], "complete")

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


class TaskFieldCompleteness(unittest.TestCase):
    """Issue #420, defect 3: a real enumeration of the fields a Task may
    carry (docs/CHECKLIST_SCHEMA.md's Task table, plus `anchors` -- documented
    only in commander-core.md prose, not the schema table) asserting every
    POPULATED field's content appears somewhere in current()'s rendered
    output for a fixture that carries every field. Built as a loop over the
    fixture's own keys minus a documented, justified exclusion set -- NOT a
    hardcoded check of only anchors/constraints by name -- so a genuinely new
    field added to Task later and forgotten in render_human() fails this test
    by default, exactly the way anchors/constraints failed before this fix."""

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
    #   directives         -- KNOWN GAP, same unrendered-defect class as
    #                          anchors/constraints (never read by state()
    #                          either), but issue #420 caps this fix's
    #                          authorized scope to "the two new fields":
    #                          anchors + constraints (IMPLEMENTER_HANDOFF
    #                          Allowed Scope). Excluded here rather than
    #                          silently expanded into; flagged as an
    #                          out-of-scope triage candidate in the
    #                          IMPLEMENTER_RESULT instead.
    _EXCLUDED_FIELDS = {
        "id", "status", "preconditions", "postconditions", "status_detail",
        "rework_count", "result", "finding", "evidence", "why_exempt",
        "child_checklist", "context_refs", "title", "directives",
    }

    @staticmethod
    def _flatten(value):
        """Best-effort text extraction for str / [str] / {category: [str]}
        shapes -- the shapes anchors/constraints actually carry in the live
        corpus. Anything else (list-of-dict, bool, int, None) yields []."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and value and all(isinstance(v, str) for v in value):
            return list(value)
        if isinstance(value, dict):
            out = []
            for v in value.values():
                if isinstance(v, list):
                    out.extend(x for x in v if isinstance(x, str))
                elif isinstance(v, str):
                    out.append(v)
            return out
        return []

    def test_every_populated_field_renders_for_a_fully_populated_gate(self):
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
        t["directives"] = ["DIRECTIVE_UNIQUE_TEXT"]  # populated but excluded -- see class docstring
        t["context_refs"] = [{"root": "repo", "path": "x", "required": True}]
        t["child_checklist"] = "some-other-work-id"
        t["evidence"] = [{"id": "e1", "type": "note", "payload": {}, "produced_by": "test", "ts": ""}]
        t["status_detail"] = {"note": "STATUS_DETAIL_UNIQUE_TEXT"}
        cl = gated(g1=t)
        out = E.current(cl)

        # Dedicated checks for the two structured, list-of-dict fields.
        self.assertIn("PRECOND_UNIQUE_TEXT", out)
        self.assertIn("POSTCOND_UNIQUE_TEXT", out)

        # Generic enumeration over everything else -- fails loud for any
        # populated, non-excluded field whose content doesn't surface. A
        # future field added to Task and left unhandled by render_human()
        # lands here by default (it is not in _EXCLUDED_FIELDS) and fails.
        checked_any = False
        for field, value in t.items():
            if field in self._EXCLUDED_FIELDS or not value:
                continue
            for text in self._flatten(value):
                checked_any = True
                self.assertIn(
                    text, out,
                    f"populated field {field!r} (value {value!r}) has content "
                    f"{text!r} missing from current()'s output",
                )
        self.assertTrue(checked_any, "the generic loop asserted nothing -- "
                         "the fixture or exclusion set is miscalibrated")
        # Sanity: name the two fields this loop is specifically proving,
        # so a change to the fixture that accidentally drops them is loud.
        self.assertIn("CONSTRAINT_UNIQUE_TEXT", out)
        self.assertIn("ANCHOR_UNIQUE_TEXT", out)


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
