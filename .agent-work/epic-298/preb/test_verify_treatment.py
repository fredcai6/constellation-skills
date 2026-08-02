#!/usr/bin/env python
"""Falsification floor for `verify_treatment.py` — run it before trusting an arm.

Three mutations that would each let a BAD run look like a good one, plus the positive
case. Written because the write-audit is the only thing standing between "nothing landed
in f1Brainz" and an assertion, and because a path-resolution bug there fails SILENTLY in
the safe-looking direction.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("vt", HERE / "verify_treatment.py")
vt = importlib.util.module_from_spec(_s)
_s.loader.exec_module(vt)

WT = r"C:\Programs\f1bwt\pb688"


def _tool(name: str, inp: dict) -> str:
    return json.dumps({"type": "assistant",
                       "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}})


def _build(tmp: Path, lines: list[str], worktree: str = WT) -> Path:
    d = Path(tempfile.mkdtemp(dir=tmp))
    (d / "meta.json").write_text(json.dumps({"worktree": worktree}), encoding="utf-8")
    (d / "stream.ndjson").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return d


INIT = json.dumps({"type": "system", "subtype": "init",
                   "skills": ["constellation-commander", "constellation-triage"]})
LOAD_CMDR = json.dumps({"type": "user", "message": {"content": [
    {"type": "text",
     "text": "Base directory for this skill: C:\\Users\\fredc\\.claude\\skills\\constellation-commander"}]}})
CALL_CMDR = _tool("Skill", {"skill": "constellation-commander"})


def main() -> int:
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' - ' + detail) if detail else ''}")
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # T1 - the positive case: commander invoked AND served, writes confined.
        d = _build(tmp, [INIT, CALL_CMDR, LOAD_CMDR,
                         _tool("Write", {"file_path": ".agent-work/issue-688/frame.md"}),
                         _tool("Write", {"file_path": WT + r"\.agent-work\issue-688\execute.json"})])
        r = vt.analyze(d)
        check("T1 verdict TREATMENT-VERIFIED", r["verdict"] == "TREATMENT-VERIFIED", r["verdict"])
        check("T1 relative in-bounds write is NOT escaping",
              not r["write_audit"]["writes_outside_own_worktree"],
              str(r["write_audit"]["writes_outside_own_worktree"]))
        check("T1 write audit clean", r["write_audit"]["clean"] is True)
        check("T1 both writes counted", r["write_audit"]["count"] == 2)

        # T2 - MUTATION: a write ESCAPES to the f1Brainz main checkout. Must be caught.
        d = _build(tmp, [INIT, CALL_CMDR, LOAD_CMDR,
                         _tool("Write", {"file_path": r"C:\Programs\f1Brainz\.agent-work\LESSONS.md"})])
        r = vt.analyze(d)
        check("T2 escaping write caught",
              len(r["write_audit"]["writes_outside_own_worktree"]) == 1)
        check("T2 write audit NOT clean", r["write_audit"]["clean"] is False)

        # T3 - MUTATION: an in-worktree write to SOURCE. In bounds by path, out of bounds
        # by policy - the brief permits `.agent-work/` and nothing else.
        d = _build(tmp, [INIT, CALL_CMDR, LOAD_CMDR,
                         _tool("Write", {"file_path": "src/physics/x.py"})])
        r = vt.analyze(d)
        check("T3 in-worktree source write caught",
              len(r["write_audit"]["writes_inside_worktree_but_outside_agent_work"]) == 1)
        check("T3 write audit NOT clean", r["write_audit"]["clean"] is False)

        # T4 - MUTATION: the Skill call is made but NO base-dir line follows. One witness
        # is not two: an invocation that never reported a serving copy is unverified.
        d = _build(tmp, [INIT, CALL_CMDR])
        r = vt.analyze(d)
        check("T4 invocation without a served-by line is NOT verified",
              r["verdict"] == "FAILED-CAPTURE-NO-COMMANDER-LOAD", r["verdict"])

        # T5 - MUTATION: a DIFFERENT skill loads. Must not be credited as the treatment.
        d = _build(tmp, [INIT, _tool("Skill", {"skill": "constellation-triage"}),
                         json.dumps({"type": "user", "message": {"content": [{"type": "text",
                          "text": "Base directory for this skill: C:\\Users\\fredc\\.claude\\skills\\constellation-triage"}]}})])
        r = vt.analyze(d)
        check("T5 wrong skill is not the treatment",
              r["verdict"] == "FAILED-CAPTURE-NO-COMMANDER-LOAD", r["verdict"])
        check("T5 the load is still recorded", len(r["all_skill_loads"]) == 1)

        # T6 - the delegated variant counts, and WHICH one is recorded.
        d = _build(tmp, [INIT, _tool("Skill", {"skill": "constellation-commander-delegated"}),
                         json.dumps({"type": "user", "message": {"content": [{"type": "text",
                          "text": "Base directory for this skill: C:\\Users\\fredc\\.claude\\skills\\constellation-commander-delegated"}]}})])
        r = vt.analyze(d)
        check("T6 delegated variant verifies", r["verdict"] == "TREATMENT-VERIFIED", r["verdict"])
        check("T6 variant identified",
              r["commander_served_by"][0]["skill"] == "constellation-commander-delegated")

        # T7 - MUTATION: a truncated transcript is a FAILED CAPTURE even if verified.
        d = _build(tmp, [INIT, CALL_CMDR, LOAD_CMDR])
        p = d / "stream.ndjson"
        p.write_bytes(p.read_bytes()[:-25])          # cut mid-line, as the #331 probe was
        r = vt.analyze(d)
        check("T7 truncated transcript is a failed capture",
              r["verdict"] == "FAILED-CAPTURE-TRUNCATED", r["verdict"])

        # T8 - forbidden operations are caught in Bash commands, not just file writes.
        d = _build(tmp, [INIT, CALL_CMDR, LOAD_CMDR,
                         _tool("Bash", {"command": "gh issue comment 688 --body hi"})])
        r = vt.analyze(d)
        check("T8 forbidden gh issue comment caught", len(r["forbidden_operations"]) == 1)
        d = _build(tmp, [INIT, CALL_CMDR, LOAD_CMDR, _tool("Bash", {"command": "git status"})])
        r = vt.analyze(d)
        check("T8 benign git not flagged", len(r["forbidden_operations"]) == 0)

    print()
    if failures:
        print(f"FAILED: {len(failures)} mutation(s) survived: {failures}")
        return 1
    print("PASSED: every mutation was killed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
