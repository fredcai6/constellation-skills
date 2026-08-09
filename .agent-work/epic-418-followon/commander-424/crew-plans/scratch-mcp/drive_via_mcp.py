#!/usr/bin/env python3
"""m2-drive-to-done postcondition c1: drive a throwaway scratch spine to DONE
through the MCP tools ONLY (no hand-edited JSON, no direct engine calls except
the one read-only CLI comparison for byte-identity), exercising all 7 tools,
proving refusal->isError, and proving byte-identical imperative text against
the CLI projection.

No model in the loop -- this is the server's own correctness harness, same
shape as the prototype's drive_via_mcp.py (git object de6a0844).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from mcp_client import McpSession, REPO_ROOT, ENGINE  # noqa: E402

ARM = HERE / "arm-drive"
TRANSCRIPT = HERE / "drive_via_mcp.transcript"

ASSERT_OK = 0
ASSERT_FAIL = 0


def check(cond: bool, msg: str) -> None:
    global ASSERT_OK, ASSERT_FAIL
    if cond:
        ASSERT_OK += 1
        print(f"ASSERT OK: {msg}")
    else:
        ASSERT_FAIL += 1
        print(f"ASSERT FAIL: {msg}")


def call(sess: McpSession, name: str, log: list, **args) -> dict:
    res = sess.call(name, **args)
    text = res["content"][0]["text"]
    log.append(f"--- {name}({args}) isError={res.get('isError')}\n{text}\n")
    print(f"--- {name}({args}) isError={res.get('isError')}")
    print(text)
    return res


def main() -> int:
    subprocess.run([sys.executable, str(HERE / "make_scratch_spine.py"), str(ARM)],
                    check=True, cwd=str(REPO_ROOT))
    spine_file = ARM / "spine.json"
    survey_file = ARM / "survey.json"
    ws = ARM / "workspace"
    log: list[str] = []

    sess = McpSession(spine_file, session_id="scratch-drive")
    try:
        # --- lease --------------------------------------------------------
        call(sess, "spine_lease", log, action="claim", claimed_by="scratch-driver")

        # --- refusal -> isError, carrying the engine's own text -----------
        refusal = call(sess, "spine_start", log, task_id="g1")
        check(refusal.get("isError") is not True, "spine_start g1 succeeds (pending, in order)")

        premature = call(sess, "spine_advance", log, task_id="g1", mechanical=True)
        premature_text = premature["content"][0]["text"]
        check(premature.get("isError") is True, "premature spine_advance g1 -> isError True")
        check("REFUSED" in premature_text, "refusal text carries the engine's literal REFUSED marker")
        check("postconditions unmet" in premature_text, "refusal names the unmet postconditions, verbatim from the engine")
        check("Recovery:" in premature_text, "refusal carries the engine's own recovery hint")

        # --- byte-identity: capture BEFORE any further mutation -----------
        cli = subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(spine_file), "current"],
            capture_output=True, text=True, check=True,
        )
        cli_text = cli.stdout.rstrip("\n")
        status = call(sess, "spine_status", log)
        mcp_text = status["content"][0]["text"]
        check(cli_text == mcp_text, "spine_status text is BYTE-IDENTICAL to the CLI `current` projection")
        # Demonstrate the check is not vacuous: a deliberately mutated copy of
        # the CLI text must NOT compare equal -- proves this assertion is
        # capable of failing, not just capable of passing.
        mutated = " " + cli_text
        check(mutated != mcp_text, "a deliberately mutated copy of the CLI text is correctly detected as UNEQUAL (the check can fail)")

        # --- g1: command-checked + attested postcondition ------------------
        (ws / "notes.txt").write_text("driving the scratch spine via MCP tools\n", encoding="utf-8")
        call(sess, "spine_evidence", log, action="attest", task_id="g1", condition_id="c2",
             which="postconditions", note="four gates understood: setup, decision, waivable check, closeout")
        adv = call(sess, "spine_advance", log, task_id="g1", why="workspace set up, notes.txt written, gates understood")
        check(adv.get("isError") is not True, "g1 advances cleanly once postconditions are genuinely met")

        # --- g2: artifact/user-decision postcondition via attach -----------
        call(sess, "spine_start", log, task_id="g2")
        call(sess, "spine_evidence", log, action="attach", task_id="g2", evidence_type="user-decision",
             fields={"decision": "proceed", "by": "human"})
        adv = call(sess, "spine_advance", log, task_id="g2", why="principal decision attached: proceed")
        check(adv.get("isError") is not True, "g2 advances once the user-decision artifact is attached")

        # --- g3: waivable check, satisfied by waiver, never made true ------
        call(sess, "spine_start", log, task_id="g3")
        check(not (ws / "optional_report.txt").exists(), "optional_report.txt genuinely does not exist before the waiver")
        call(sess, "spine_evidence", log, action="waive", task_id="g3", condition_id="c1",
             which="postconditions", authority="human",
             reason="principal accepts this check as non-blocking for this scratch run")
        adv = call(sess, "spine_advance", log, task_id="g3", why="check waived by the principal; optional_report.txt intentionally absent")
        adv_text = adv["content"][0]["text"]
        check(adv.get("isError") is not True, "g3 advances via the waiver alone")
        check("WAIVED" in adv_text and "c1" in adv_text, "advance message names the waived condition")

        # --- g4: block/resume cycle, then genuine close-out -----------------
        call(sess, "spine_start", log, task_id="g4")
        blocked = call(sess, "spine_halt", log, action="block", task_id="g4",
                       blocker="waiting on a fabricated dependency to prove spine_halt", authority="human")
        check(blocked.get("isError") is not True, "spine_halt block succeeds")
        resumed = call(sess, "spine_halt", log, action="resume", task_id="g4",
                       reason="fabricated dependency resolved")
        check(resumed.get("isError") is not True, "spine_halt resume succeeds")
        (ws / "SUMMARY.md").write_text(
            "# Summary\nDrove the scratch spine end to end through the 7 MCP tools: "
            "status, lease, start, advance, evidence (attest/attach/waive), halt, and "
            "(separately) survey_result.\n", encoding="utf-8")
        call(sess, "spine_evidence", log, action="attest", task_id="g4", condition_id="c2",
             which="postconditions", note="summary read back, honestly describes the run")
        final_adv = call(sess, "spine_advance", log, task_id="g4", why="closeout summary written and verified")
        check(final_adv.get("isError") is not True, "g4 (final gate) advances cleanly")

        final = call(sess, "spine_status", log)
        final_text = final["content"][0]["text"]
        check("DONE: no open items." in final_text, "spine reaches DONE through the tools alone")

        call(sess, "spine_lease", log, action="release")
    finally:
        sess.close()

    # --- survey_result: record + consolidate, on a separate survey fixture --
    survey_sess = McpSession(survey_file, session_id="scratch-drive-survey")
    try:
        call(survey_sess, "spine_lease", log, action="claim", claimed_by="scratch-driver")
        call(survey_sess, "spine_survey_result", log, action="record", task_id="r1", result="pass")
        call(survey_sess, "spine_survey_result", log, action="record", task_id="r2", result="fail",
             finding="deliberately recorded fail to exercise the override path")
        cons = call(survey_sess, "spine_survey_result", log, action="consolidate", verdict="APPROVE",
                    summary="scratch survey exercised for the MCP door proof",
                    override_reason="r2's fail is a planted fixture datum, not a real defect")
        cons_text = cons["content"][0]["text"]
        check(cons.get("isError") is not True, "consolidate APPROVE-with-override succeeds")
        check("verdict=APPROVE" in cons_text, "consolidation records the APPROVE verdict")
        call(survey_sess, "spine_lease", log, action="release")
    finally:
        survey_sess.close()

    TRANSCRIPT.write_text("\n".join(log), encoding="utf-8")
    print(f"\nASSERT OK: {ASSERT_OK}  ASSERT FAIL: {ASSERT_FAIL}")
    print(f"transcript: {TRANSCRIPT}")
    return 0 if ASSERT_FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
