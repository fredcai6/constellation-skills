#!/usr/bin/env python3
"""m3-config-gen postcondition c1: prove gen_mcp_config.py for real against a
live headless `claude -p` dispatch -- not a hand-inspected file.

Generates a per-dispatch config keyed session_id#agentId, then runs:

    claude -p "<task>" --mcp-config <generated>.json --strict-mcp-config \
        --allowedTools "mcp__spine__spine_status"

against a throwaway scratch spine whose g1 imperative carries an unguessable
per-run NONCE. If the dispatch's own final answer contains that nonce, the
model could only have gotten it by genuinely calling the tool through the
generated config and getting real engine output back -- a model cannot guess
a random nonce it was never shown any other way. --strict-mcp-config means
this dispatch has NO other MCP server available, so the tool call (if any)
can only have gone through this one generated, per-dispatch server instance.
"""
from __future__ import annotations

import json
import secrets
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from mcp_client import REPO_ROOT  # noqa: E402

ARM = HERE / "arm-headless"
CONFIG_OUT = HERE / "generated-mcp-config.json"
TRANSCRIPT = HERE / "prove_headless_dispatch.transcript"


def main() -> int:
    nonce = "N" + secrets.token_hex(8)
    subprocess.run(
        [sys.executable, str(HERE / "make_scratch_spine.py"), str(ARM), nonce],
        check=True, cwd=str(REPO_ROOT),
    )
    spine_file = ARM / "spine.json"

    session_id = "epic418-424-headless-probe"
    agent_id = "probe1"
    gen = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "gen_mcp_config.py"),
         "--spine-file", str(spine_file),
         "--session-id", session_id,
         "--agent-id", agent_id,
         "--out", str(CONFIG_OUT)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    print("gen_mcp_config.py stdout:", gen.stdout.strip())
    print("gen_mcp_config.py stderr:", gen.stderr.strip())
    assert gen.returncode == 0, f"gen_mcp_config.py failed: {gen.stderr}"

    config = json.loads(CONFIG_OUT.read_text(encoding="utf-8"))
    print("GENERATED CONFIG:", json.dumps(config, indent=2))
    server_entry = config["mcpServers"]["spine"]
    expected_session = f"{session_id}#{agent_id}"
    assert server_entry["env"]["SPINE_SESSION"] == expected_session, (
        f"expected SPINE_SESSION={expected_session!r}, got {server_entry['env']['SPINE_SESSION']!r}"
    )
    assert server_entry["env"]["SPINE_FILE"] == str(spine_file.resolve())
    print(f"ASSERT OK: generated config keyed SPINE_SESSION={expected_session!r}")

    prompt = (
        "Call the spine_status tool exactly once (no other tools, no other actions). "
        "Then reply with ONLY the raw text content of that tool's result, verbatim, "
        "with no commentary, no markdown fences, nothing added or removed."
    )
    dispatch = subprocess.run(
        ["claude", "-p", prompt,
         "--mcp-config", str(CONFIG_OUT),
         "--strict-mcp-config",
         "--allowedTools", "mcp__spine__spine_status",
         "--permission-mode", "acceptEdits",
         "--output-format", "json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180,
    )
    print("DISPATCH EXIT:", dispatch.returncode)
    print("DISPATCH STDOUT:", dispatch.stdout)
    print("DISPATCH STDERR:", dispatch.stderr[-4000:])

    TRANSCRIPT.write_text(
        "GENERATED CONFIG:\n" + json.dumps(config, indent=2) +
        "\n\nDISPATCH EXIT: " + str(dispatch.returncode) +
        "\n\nDISPATCH STDOUT:\n" + dispatch.stdout +
        "\n\nDISPATCH STDERR:\n" + dispatch.stderr,
        encoding="utf-8",
    )

    assert dispatch.returncode == 0, f"headless dispatch failed, exit {dispatch.returncode}"
    result = json.loads(dispatch.stdout)
    final_text = result.get("result", "")
    print("FINAL ANSWER TEXT:", final_text)

    assert nonce in final_text, (
        f"nonce {nonce!r} not found in the dispatch's final answer -- the tool call "
        f"either did not happen or did not round-trip real engine output back to the "
        f"model. Final answer was:\n{final_text}"
    )
    print(f"ASSERT OK: unguessable nonce {nonce!r} appears in the headless dispatch's "
          f"final answer -- proves a REAL tool call went through the generated "
          f"per-dispatch config and returned genuine engine output")

    # Corroborate with the server's own call log for this arm, if present.
    call_log = ARM / "mcp_calls.jsonl"
    if call_log.exists():
        lines = call_log.read_text(encoding="utf-8").strip().splitlines()
        print(f"SERVER CALL LOG ({len(lines)} lines):")
        for line in lines:
            print(" ", line)
        assert lines, "call log exists but is empty"
        assert any(json.loads(ln)["verb"] == "current" for ln in lines), \
            "call log has no 'current' verb entry -- spine_status never reached the engine"
        print("ASSERT OK: server's own call log corroborates a real 'current' engine call")

    print("\nHEADLESS DISPATCH PROOF: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
