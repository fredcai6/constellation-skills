"""Criterion 3: THE exit criterion, end to end, in ONE process, no CLI.

unbound refuses -> spine_open binds -> `claim` SUCCEEDS -> a second mutating
verb -> status shows the new spine.

`claim` is the load-bearing call: `run_engine` omits `--session-id` when
`SESSION` is empty and `checklist_engine.py` raises "claim requires a non-empty
--session-id", so a transcript that stops at `spine_status` proves nothing.

Staged in a THROWAWAY git repo carrying a copy of `scripts/`, because an unbound
door derives its primary checkout from the server script's own location -- so
running the repo's own script here would mint work in the developer's real tree.
Cleans up after itself.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORK_ID = "g3-reviewer-exit"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


tmp = Path(tempfile.mkdtemp(prefix="g3exit-"))
repo = tmp / "repo"
repo.mkdir()
shutil.copytree(REPO / "scripts", repo / "scripts")
git("init", "-q", cwd=repo)
git("config", "user.email", "rev@example.com", cwd=repo)
git("config", "user.name", "rev", cwd=repo)
git("add", "-A", cwd=repo)
git("commit", "-q", "-m", "seed", cwd=repo)

env = dict(os.environ)
for v in ("SPINE_FILE", "SPINE_SESSION", "SPINE_ENGINE", "SPINE_PARENT",
          "SPINE_CALLLOG", "SPINE_START_MARKER", "SPINE_REJECTION_LOG"):
    env.pop(v, None)
print("ENVIRONMENT: SPINE_FILE, SPINE_SESSION, SPINE_ENGINE all ABSENT\n")

spec = {"work_id": WORK_ID, "type": "gated",
        "tasks": [{"id": "m1", "title": "prove it", "imperative": "do the thing"}]}

calls = [
    ("spine_status", {}, "UNBOUND -- must refuse"),
    ("spine_open", {"work_id": WORK_ID, "spec": spec}, "mints AND binds"),
    ("spine_lease", {"action": "claim", "claimed_by": "reviewer"},
     "claim -- THE proof SESSION was rebound"),
    ("spine_start", {"task_id": "m1"}, "a second mutating verb on the new spine"),
    ("spine_status", {}, "the door is really driving the new spine"),
]

msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "g3-reviewer", "version": "0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
]
for i, (name, args, _) in enumerate(calls):
    msgs.append({"jsonrpc": "2.0", "id": 10 + i, "method": "tools/call",
                 "params": {"name": name, "arguments": args}})

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
    if isinstance(m.get("id"), int) and m["id"] >= 10:
        answers[m["id"] - 10] = m.get("result", m)

for i, (name, args, why) in enumerate(calls):
    res = answers.get(i)
    print(f"--- call {i + 1}: {name} -- {why}")
    if res is None:
        print("    (NO ANSWER -- the server died)\n")
        continue
    text = "".join(c.get("text", "") for c in res.get("content", []))
    print(f"    isError: {res.get('isError')}")
    for ln in text.strip().splitlines():
        print(f"    {ln}")
    print()

print(f"server exit code: {r.returncode}  (0 = alive through all {len(calls)} calls)")
print(f"server stderr: {r.stderr.strip()[:500] or '(none)'}")

# --- cleanup, and PROVE it
wt = repo / ".worktrees" / WORK_ID
print(f"\nCLEANUP: worktree existed before removal: {wt.exists()}")
git("worktree", "remove", "--force", str(wt), cwd=repo)
git("branch", "-D", WORK_ID, cwd=repo)
print("worktree list after removal:")
print(git("worktree", "list", cwd=repo).stdout.strip())
shutil.rmtree(tmp, ignore_errors=True)
print(f"throwaway tree removed: {not tmp.exists()}")

# --- and prove the REAL repo was never touched
real = subprocess.run(["git", "worktree", "list"], cwd=str(REPO),
                      capture_output=True, text=True).stdout
print(f"\nreal checkout still has NO {WORK_ID} worktree: {WORK_ID not in real}")
real_b = subprocess.run(["git", "branch", "--list", WORK_ID], cwd=str(REPO),
                        capture_output=True, text=True).stdout.strip()
print(f"real checkout has no {WORK_ID} branch: {real_b == ''!r} ({real_b!r})")
