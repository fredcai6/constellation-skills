"""Criterion 8 (a rebind under a held lease is refused) and criterion 6 (the
three telemetry env overrides still win).

One door process per part, driven over real JSON-RPC.

Part 1 also checks the refusal lands BEFORE anything is minted: no branch and no
worktree may exist afterwards. A refusal that arrived after `open_work` would
leave real git objects behind for work the door then declined to drive.

Part 2 sets SPINE_CALLLOG / SPINE_START_MARKER / SPINE_REJECTION_LOG away from
the spine and asserts all three landed at the override and NONE beside the spine
-- `tests/test_mcp_lifecycle.py:102-103` depends on exactly this.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORK_ID = "g3-rev-lease"


def drive(env, cwd, calls, timeout=180):
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "rev", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]
    for i, (n, a) in enumerate(calls):
        msgs.append({"jsonrpc": "2.0", "id": 30 + i, "method": "tools/call",
                     "params": {"name": n, "arguments": a}})
    r = subprocess.run(
        [sys.executable, "scripts/mcp_spine_server.py"],
        input="\n".join(json.dumps(m) for m in msgs) + "\n",
        capture_output=True, text=True, env=env, cwd=str(cwd), timeout=timeout,
    )
    out = {}
    for line in r.stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if isinstance(m.get("id"), int) and m["id"] >= 30:
            res = m.get("result", {})
            out[m["id"] - 30] = (res.get("isError"),
                                 "".join(c.get("text", "") for c in res.get("content", [])))
    return r, out


def seed_repo(tmp):
    repo = tmp / "repo"
    repo.mkdir()
    shutil.copytree(REPO / "scripts", repo / "scripts")
    for a in (["init", "-q"], ["config", "user.email", "r@e.com"],
              ["config", "user.name", "r"], ["add", "-A"], ["commit", "-q", "-m", "seed"]):
        subprocess.run(["git", *a], cwd=str(repo), capture_output=True, text=True)
    return repo


def write_spine(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "w", "type": "gated", "items": ["a1"],
        "tasks": {"a1": {"id": "a1", "title": "t", "imperative": "do",
                         "preconditions": [], "postconditions": [], "constraints": [],
                         "directives": None, "child_checklist": None, "status": "pending",
                         "status_detail": {}, "result": None, "finding": None,
                         "evidence": [], "rework_count": 0}},
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }), encoding="utf-8")


# ============ PART 1: rebind under a held lease ============
print("=" * 72)
print("PART 1 -- criterion 8: a rebind while a lease is held")
print("=" * 72)
tmp1 = Path(tempfile.mkdtemp(prefix="g3lease-"))
repo1 = seed_repo(tmp1)
spine1 = repo1 / "work" / "spine.json"
write_spine(spine1)

env1 = dict(os.environ)
env1["SPINE_FILE"] = str(spine1)
env1["SPINE_SESSION"] = "constellation/holder"
env1.pop("SPINE_ENGINE", None)
env1.pop("SPINE_PARENT", None)
for v in ("SPINE_CALLLOG", "SPINE_START_MARKER", "SPINE_REJECTION_LOG"):
    env1[v] = str(tmp1 / v.lower())

spec = {"work_id": WORK_ID, "type": "gated",
        "tasks": [{"id": "m1", "title": "t", "imperative": "do"}]}

r, out = drive(env1, repo1, [
    ("spine_lease", {"action": "claim", "claimed_by": "reviewer"}),
    ("spine_open", {"work_id": WORK_ID, "spec": spec}),
    ("spine_lease", {"action": "release"}),
    ("spine_open", {"work_id": WORK_ID, "spec": spec}),
])
labels = ["claim the lease", "spine_open WHILE HELD -- must REFUSE",
          "release the lease", "spine_open after release -- must SUCCEED"]
for i, lab in enumerate(labels):
    err, text = out.get(i, (None, "(no answer)"))
    print(f"\n--- {lab}\n    isError: {err}\n    {text.strip()[:330]}")

print(f"\nserver exit: {r.returncode}   stderr: {r.stderr.strip()[:200] or '(none)'}")
branches = subprocess.run(["git", "branch", "--list", WORK_ID], cwd=str(repo1),
                          capture_output=True, text=True).stdout.strip()
print(f"\nAFTER the refusal the open was later ALLOWED, so cleanup is expected to find it.")
print(f"branch {WORK_ID!r} now: {branches!r}")

# Prove the refusal itself mints nothing: fresh repo, lease held, open ONCE.
tmp2 = Path(tempfile.mkdtemp(prefix="g3lease2-"))
repo2 = seed_repo(tmp2)
spine2 = repo2 / "work" / "spine.json"
write_spine(spine2)
env2 = dict(env1)
env2["SPINE_FILE"] = str(spine2)
for v in ("SPINE_CALLLOG", "SPINE_START_MARKER", "SPINE_REJECTION_LOG"):
    env2[v] = str(tmp2 / v.lower())
r2, out2 = drive(env2, repo2, [
    ("spine_lease", {"action": "claim", "claimed_by": "reviewer"}),
    ("spine_open", {"work_id": WORK_ID, "spec": spec}),
])
err, text = out2.get(1, (None, "(no answer)"))
print(f"\n--- fresh repo, lease held, ONE spine_open\n    isError: {err}\n    {text.strip()[:200]}")
b2 = subprocess.run(["git", "branch", "--list", WORK_ID], cwd=str(repo2),
                    capture_output=True, text=True).stdout.strip()
wt2 = (repo2 / ".worktrees" / WORK_ID).exists()
print(f"    branch created?  {b2!r}   (must be '')")
print(f"    worktree exists? {wt2}    (must be False)")

for t in (tmp1, tmp2):
    for wt in (t / "repo" / ".worktrees").glob("*"):
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(t / "repo"), capture_output=True, text=True)
    shutil.rmtree(t, ignore_errors=True)

# ============ PART 2: the three env overrides ============
print()
print("=" * 72)
print("PART 2 -- criterion 6: SPINE_CALLLOG / SPINE_START_MARKER / SPINE_REJECTION_LOG")
print("=" * 72)
tmp3 = Path(tempfile.mkdtemp(prefix="g3ovr-"))
repo3 = seed_repo(tmp3)
spine3 = repo3 / "work" / "spine.json"
write_spine(spine3)
ovr = tmp3 / "elsewhere"
ovr.mkdir()

env3 = dict(os.environ)
env3["SPINE_FILE"] = str(spine3)
env3["SPINE_SESSION"] = ""
env3.pop("SPINE_ENGINE", None)
env3.pop("SPINE_PARENT", None)
env3["SPINE_CALLLOG"] = str(ovr / "my_calls.jsonl")
env3["SPINE_START_MARKER"] = str(ovr / "my_marker")
env3["SPINE_REJECTION_LOG"] = str(ovr / "my_rejections.jsonl")

r3, out3 = drive(env3, repo3, [
    ("spine_status", {}),
    ("definitely_not_a_tool", {}),
])
print(f"\nspine_status isError={out3.get(0, (None,''))[0]}")
print(f"rejection    isError={out3.get(1, (None,''))[0]}")
print(f"server exit: {r3.returncode}   stderr: {r3.stderr.strip()[:200] or '(none)'}")
print("\nAT THE OVERRIDE PATHS:")
for label, p in (("SPINE_CALLLOG", ovr / "my_calls.jsonl"),
                 ("SPINE_START_MARKER", ovr / "my_marker"),
                 ("SPINE_REJECTION_LOG", ovr / "my_rejections.jsonl")):
    print(f"  {label:22s} exists={p.exists()}   {p}")
beside = sorted(p.name for p in spine3.parent.iterdir() if p.name != "spine.json")
print(f"\nBESIDE THE SPINE (must contain NO telemetry): {beside or '(nothing but spine.json)'}")
shutil.rmtree(tmp3, ignore_errors=True)
