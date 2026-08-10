#!/usr/bin/env python3
"""m1-server-core postcondition c1: prove the door is genuinely up and serving
BEFORE anything else -- DC3's positive control (MISSION_FRAME claim table).

Builds a fresh throwaway scratch spine, launches the real server as a
subprocess, and asserts:
  1. initialize replies with serverInfo naming this server.
  2. tools/list returns exactly the 7 tools this gate committed to.
  3. a real spine_status (-> engine `current`) call returns genuine engine
     output naming the scratch spine's actual first gate -- not a stub, not a
     hand-written string this script invented.

Writes the full transcript to smoke_test.transcript for the evidence record.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from mcp_client import McpSession, REPO_ROOT  # noqa: E402

ARM = HERE / "arm-smoke"
TRANSCRIPT = HERE / "smoke_test.transcript"

EXPECTED_TOOLS = {
    "spine_status", "spine_lease", "spine_start", "spine_advance",
    "spine_evidence", "spine_halt", "spine_survey_result",
}


def main() -> int:
    subprocess.run([sys.executable, str(HERE / "make_scratch_spine.py"), str(ARM)],
                    check=True, cwd=str(REPO_ROOT))
    spine_file = ARM / "spine.json"
    lines = []

    sess = McpSession(spine_file, session_id="smoke-test")
    try:
        init = sess.initialize()
        lines.append("INITIALIZE: " + json.dumps(init))
        assert "result" in init, f"initialize returned no result: {init}"
        server_info = init["result"]["serverInfo"]
        assert server_info["name"] == "spine", f"unexpected serverInfo: {server_info}"

        tools = sess.tools_list()
        names = {t["name"] for t in tools}
        lines.append("TOOLS: " + json.dumps(sorted(names)))
        assert names == EXPECTED_TOOLS, f"tool surface mismatch: {names} != {EXPECTED_TOOLS}"
        assert len(tools) == 7, f"expected exactly 7 tools, got {len(tools)}"

        status = sess.call("spine_status")
        text = status["content"][0]["text"]
        lines.append("SPINE_STATUS: " + text)
        assert status.get("isError") is not True, f"spine_status errored: {status}"
        # This text must be genuine engine `current` output for THIS scratch
        # spine's real first gate -- not a fixed string this test made up.
        assert "ACTIVE g1" in text, f"expected the real first gate in output, got: {text!r}"
        assert "notes.txt" in text, f"expected the real gate's imperative content, got: {text!r}"
        assert "next: start g1" in text, f"expected a real next-verb hint, got: {text!r}"
    finally:
        sess.close()

    TRANSCRIPT.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print("SMOKE TEST: PASS")
    print(f"transcript: {TRANSCRIPT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
