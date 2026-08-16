"""Drive the real MCP door over stdio as a SUBPROCESS and report what it answers.

Adapted from the 2026-08-15 probe named in LAUNCH_ORDER.md's Data Locations. Two
additions this lane needs:

  * it prints the server's PROCESS EXIT CODE, which is the whole evidence for #604
    (the door dying on its own call log presents to the client only as
    "Connection closed");
  * SPINE_FILE is only injected when a spine argument is given, so the unbound case
    (#603) can be probed at all -- `--unbound` actively REMOVES it from the
    environment rather than passing an empty string, which is a different case.

Never validate the door by reasoning about this session's own connection: that door
is bound to whatever .mcp.json said at launch. Always launch your own.

Usage:
    py .agent-work/cleanup-a-door/door_probe.py <spine-path> [tool] [json-args]
    py .agent-work/cleanup-a-door/door_probe.py --unbound [tool] [json-args]
"""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def probe(spine, tool="spine_status", args=None, session=""):
    env = dict(os.environ, SPINE_ENGINE="scripts/checklist_engine.py", SPINE_SESSION=session)
    if spine is None:
        env.pop("SPINE_FILE", None)          # genuinely unset, not empty
    else:
        env["SPINE_FILE"] = spine
    p = subprocess.Popen(
        [sys.executable, "scripts/mcp_spine_server.py"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env, cwd=REPO,
    )
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "probe", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": tool, "arguments": args or {}}},
    ]
    try:
        out, err = p.communicate("\n".join(json.dumps(m) for m in msgs) + "\n", timeout=60)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        print("TIMEOUT")
    print(f"SPINE_FILE={'(unset)' if spine is None else spine}")
    print(f"TOOL={tool}")
    answered = False
    for line in out.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("id") == 2:
            answered = True
            print("RESULT:", json.dumps(d.get("result", d))[:1500])
    if not answered:
        print("RESULT: (the server never answered the call)")
    print("STDERR:", err.strip()[:800] or "(none)")
    print(f"EXIT {p.returncode}")
    return p.returncode


if __name__ == "__main__":
    argv = sys.argv[1:]
    spine = None if (argv and argv[0] == "--unbound") else (argv[0] if argv else None)
    tool = argv[1] if len(argv) > 1 else "spine_status"
    args = json.loads(argv[2]) if len(argv) > 2 else None
    sys.exit(0 if probe(spine, tool, args) == 0 else 0)  # report, never propagate
