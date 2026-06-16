import copy
import importlib.util
import json
import sys
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
PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'
FAIL_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(1)"'


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

    def test_stale_lease_blocks_mutation_until_reclaimed(self):
        cl = gated(g1=gate("g1", command=PASS_COMMAND))
        E.claim(cl, "s1", "commander", ".", {})
        cl["engine_session"]["last_heartbeat"] = _old_ts(10_000)
        cfg = {"lease_stale_seconds": 1800}
        self.assertTrue(E._is_stale(cl["engine_session"], cfg))
        # a mutating verb against a stale-only lease refuses with a claim instruction
        with self.assertRaises(E.EngineError):
            E.require_session(cl, "start", "s1", cfg)
        # but it can be reclaimed (same session) — does not permanently lock
        msg = E.claim(cl, "s1", "commander", ".", cfg)
        self.assertEqual(cl["engine_session"]["status"], "active")
        self.assertFalse(E._is_stale(cl["engine_session"], cfg))

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
