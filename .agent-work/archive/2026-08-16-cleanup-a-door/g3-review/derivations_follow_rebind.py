"""Criterion 5 + 4, empirically: do the four import-time SPINE derivations
actually FOLLOW a real rebind, and does the fenced guard still refuse afterwards?

Black-box where possible: one door process, unbound, driven over real JSON-RPC.
It is rebound by a REAL `spine_open` (not by poking `_bind_process_to`), then we
look at where its telemetry actually landed and what its containment check now
confines to.

The four named derivations:
  1. CALLLOG        (was :162)  -> mcp_calls.jsonl beside the spine
  2. START_MARKER   (was :167)  -> mcp_server_started beside the spine
  3. REJECTIONLOG   (was :177)  -> mcp_rejections.jsonl beside the spine
  4. _resolve_confined's `bound_dir` DEFAULT ARGUMENT (was :188)

A stale derivation writes one spine's telemetry into another's directory, so the
test is: nothing beside the OLD spine, everything beside the NEW one.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORK_ID = "g3-rev-rebind"

tmp = Path(tempfile.mkdtemp(prefix="g3reb-"))
repo = tmp / "repo"
repo.mkdir()
shutil.copytree(REPO / "scripts", repo / "scripts")
for a in (["init", "-q"], ["config", "user.email", "r@e.com"], ["config", "user.name", "r"],
          ["add", "-A"], ["commit", "-q", "-m", "seed"]):
    subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)

# --- the ORIGINAL binding: a real spine in its own directory, INSIDE the repo
# (it must be inside a checkout, or `_primary_checkout_for_lifecycle` -- which
# reads the BOUND spine first -- cannot resolve a root and `spine_open` refuses
# before it ever rebinds. Measured: it does exactly that.)
old_dir = repo / "old-spine-dir"
old_dir.mkdir()
old_spine = old_dir / "spine.json"
old_spine.write_text(json.dumps({
    "work_id": "old", "type": "gated", "items": ["a1"],
    "tasks": {"a1": {"id": "a1", "title": "old", "imperative": "old work",
                     "preconditions": [], "postconditions": [], "constraints": [],
                     "directives": None, "child_checklist": None, "status": "pending",
                     "status_detail": {}, "result": None, "finding": None,
                     "evidence": [], "rework_count": 0}},
    "consolidation": None, "triage_candidates": [], "blockers": [],
}), encoding="utf-8")

env = dict(os.environ)
env["SPINE_FILE"] = str(old_spine)
env["SPINE_SESSION"] = ""            # no lease held -> rebind is allowed
env.pop("SPINE_ENGINE", None)
env.pop("SPINE_PARENT", None)
for v in ("SPINE_CALLLOG", "SPINE_START_MARKER", "SPINE_REJECTION_LOG"):
    env.pop(v, None)                 # NO overrides: force the beside-the-spine derivation

spec = {"work_id": WORK_ID, "type": "gated",
        "tasks": [{"id": "m1", "title": "t", "imperative": "do"}]}

calls = [
    ("spine_status", {}, "bound to the OLD spine -- telemetry must land beside OLD"),
    ("spine_open", {"work_id": WORK_ID, "spec": spec}, "REBIND to a new spine"),
    ("spine_status", {}, "after rebind -- telemetry must now land beside NEW"),
    ("nope_not_a_tool", {}, "a DOOR-level rejection -> rejection log placement"),
    ("spine_advance", {"task_id": "m1", "from_child": "/etc/passwd", "mechanical": True},
     "containment: bound_dir must be the NEW spine's dir, not the OLD one"),
]

msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "rev", "version": "0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
]
for i, (n, a, _) in enumerate(calls):
    msgs.append({"jsonrpc": "2.0", "id": 20 + i, "method": "tools/call",
                 "params": {"name": n, "arguments": a}})

r = subprocess.run(
    [sys.executable, "scripts/mcp_spine_server.py"],
    input="\n".join(json.dumps(m) for m in msgs) + "\n",
    capture_output=True, text=True, env=env, cwd=str(repo), timeout=180,
)

answers = {}
for line in r.stdout.splitlines():
    try:
        m = json.loads(line)
    except ValueError:
        continue
    if isinstance(m.get("id"), int) and m["id"] >= 20:
        answers[m["id"] - 20] = m.get("result", m)

new_spine = None
for i, (n, a, why) in enumerate(calls):
    res = answers.get(i)
    print(f"--- call {i + 1}: {n} -- {why}")
    if res is None:
        print("    (NO ANSWER)\n")
        continue
    text = "".join(c.get("text", "") for c in res.get("content", []))
    print(f"    isError: {res.get('isError')}")
    print(f"    {text.strip()[:400]}")
    if n == "spine_open" and not res.get("isError"):
        new_spine = Path(json.loads(text)["SPINE_FILE"])
    print()

print(f"server exit: {r.returncode}   stderr: {r.stderr.strip()[:300] or '(none)'}")
print()
print("=== WHERE THE TELEMETRY ACTUALLY LANDED ===")
new_dir = new_spine.parent if new_spine else None
for label, d in (("OLD spine dir", old_dir), ("NEW spine dir", new_dir)):
    if d is None:
        continue
    found = sorted(p.name for p in d.iterdir()
                   if p.name in {"mcp_calls.jsonl", "mcp_server_started", "mcp_rejections.jsonl"})
    print(f"  {label}: {d}")
    print(f"    telemetry files: {found or '(none)'}")

if new_dir is not None:
    cl = new_dir / "mcp_calls.jsonl"
    if cl.exists():
        verbs = [json.loads(x)["verb"] for x in cl.read_text(encoding="utf-8").splitlines() if x.strip()]
        print(f"  NEW mcp_calls.jsonl verbs: {verbs}")
    old_cl = old_dir / "mcp_calls.jsonl"
    if old_cl.exists():
        verbs = [json.loads(x)["verb"] for x in old_cl.read_text(encoding="utf-8").splitlines() if x.strip()]
        print(f"  OLD mcp_calls.jsonl verbs: {verbs}   <-- must contain ONLY pre-rebind calls")

# cleanup
subprocess.run(["git", "worktree", "remove", "--force", str(repo / ".worktrees" / WORK_ID)],
               cwd=str(repo), capture_output=True, text=True)
subprocess.run(["git", "branch", "-D", WORK_ID], cwd=str(repo), capture_output=True, text=True)
shutil.rmtree(tmp, ignore_errors=True)
print(f"\nthrowaway tree removed: {not tmp.exists()}")
