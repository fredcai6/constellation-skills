import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"
EXAMPLE = ROOT / "docs" / "examples" / "inner-loop-example.jsonc"


def load_engine():
    spec = importlib.util.spec_from_file_location("checklist_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load_engine()


def gate(iid, status="pending", command=None, preconds=None):
    post = []
    if command is not None:
        post = [{"id": "c1", "statement": "tests pass", "check": {"kind": "command", "command": command}, "satisfied": False}]
    return {
        "id": iid, "title": iid, "imperative": f"do {iid}",
        "preconditions": preconds or [], "postconditions": post,
        "constraints": [], "directives": None, "child_checklist": None,
        "status": status, "status_detail": {}, "result": None, "finding": None,
        "evidence": [], "rework_count": 0,
    }


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
        cl = gated(g1=gate("g1", "in-progress", command="true"), g2=gate("g2"))
        self.assertIn("ACTIVE g1", E.current(cl))

    def test_current_skips_terminal_items(self):
        cl = gated(g1=gate("g1", "complete"), g2=gate("g2", "pending", command="true"))
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


class AdvanceGated(unittest.TestCase):
    def test_command_postcondition_pass_completes(self):
        cl = gated(g1=gate("g1", "in-progress", command="true"))
        E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        self.assertTrue(any(e["type"] == "command-output" for e in cl["tasks"]["g1"]["evidence"]))

    def test_command_postcondition_fail_refuses_and_records(self):
        cl = gated(g1=gate("g1", "in-progress", command="false"))
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
        cl = gated(g1=gate("g1", "in-progress", command="true"))
        with self.assertRaises(E.EngineError):
            E.record(cl, "g1", "pass", None)


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
        gcl = gated(g1=gate("g1", "in-progress", command="true"))
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
        cl = gated(cap=1, g1=gate("g1", "complete", command="true"))
        msg = E.reopen(cl, "g1", "redo")
        self.assertIn("reopened", msg)
        self.assertEqual(cl["tasks"]["g1"]["rework_count"], 1)
        cl["tasks"]["g1"]["status"] = "complete"  # pretend it was re-advanced
        msg = E.reopen(cl, "g1", "still wrong")
        self.assertIn("ESCALATED", msg)
        self.assertEqual(cl["tasks"]["g1"]["status"], "blocked")
        self.assertTrue(cl["blockers"])

    def test_reopen_resets_postconditions(self):
        cl = gated(cap=3, g1=gate("g1", "complete", command="true"))
        cl["tasks"]["g1"]["postconditions"][0]["satisfied"] = True
        E.reopen(cl, "g1", "redo")
        self.assertFalse(cl["tasks"]["g1"]["postconditions"][0]["satisfied"])


class BubbleUp(unittest.TestCase):
    def test_block_appends_blocker(self):
        cl = gated(g1=gate("g1", "in-progress", command="true"))
        E.block(cl, "g1", "stuck", "user", "ask")
        self.assertEqual(cl["blockers"][0]["item"], "g1")

    def test_flag_candidate(self):
        cl = gated(g1=gate("g1", "in-progress", command="true"))
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
        cl = gated(g1=gate("g1", "in-progress", command="false"))
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
                  "items": ["g1"], "tasks": {"g1": gate("g1", "complete", command="true")},
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


if __name__ == "__main__":
    unittest.main()
