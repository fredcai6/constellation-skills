import copy
import importlib.util
import json
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
        # g1 done, g2 active (not first), n == 2 -> mid-flight, {n}=2 {imperative}=do g2
        cl = gated(g1=gate("g1", "complete"),
                   g2=gate("g2", "in-progress"), g3=gate("g3"))
        rail = E._rail("current", cl)
        self.assertIn(
            "A working solution is the MIDDLE of this run — you are 2 steps "
            "from done. Next: do g2. Run it.",
            rail,
        )

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
