"""What the bind-on-resume writer now REFUSES, enumerated by measurement.

The question this answers is the risk the fix carries: is any LEGITIMATE bind
now refused? So the grid is not "cases I can think of" -- it is every reachable
combination of the two facts the guard reads (which of the three states the read
is in, and what the store already attributes the scanned path to), each run on
the committed hook and on the working tree, with the two answers printed side by
side. A cell that changes is a refusal; a cell that does not is a bind that
survived.

Claims are written by the real claim writer (`handle_post_tool_use` on the
repo's pinned probe capture) wherever the case involves a real claim. The
`bind()`-equivalent hand-written entry is used only for the one shape a real
claim cannot produce on demand -- a session's own claim on a spine that is then
archived -- and even there the claim itself is real; only the archiving is
simulated, by deleting the file, which is what closeout does.
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rw3-ref-"))
HOOK = REPO / "scripts/hooks/spine_rail.py"

PAYLOADS = [json.loads(l)["payload"]
            for l in (REPO / "tests/fixtures/probe_payloads.jsonl").read_text(
                encoding="utf-8").splitlines() if l.strip()]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
SID = PARENT["session_id"]


def _import(name, src):
    p = OUT / "arm_{}.py".format(name)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("ref_" + name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BEFORE = _import("before", subprocess.run(
    ["git", "show", "HEAD:scripts/hooks/spine_rail.py"], cwd=str(REPO),
    capture_output=True, text=True, check=True).stdout)
AFTER = _import("after", HOOK.read_text(encoding="utf-8"))


def put(proj, work, gate, marker, eng):
    d = proj / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"
    p.write_text(json.dumps({
        "work_id": "w", "type": "gated", "items": [gate],
        "tasks": {gate: {"id": gate, "status": "in-progress", "imperative": marker}},
        "engine_session": {"session_id": eng, "status": "active", "claimed_by": "commander",
                           "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    }), encoding="utf-8")
    (d / "spine.json.journal").write_text('{"seq": 0}\n', encoding="utf-8")
    return p


def claim(sr, payload, work, eng, proj):
    d = dict(payload)
    d["tool_input"] = {"command": (
        "py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
        "claim --session-id %s --claimed-by commander" % (work, eng))}
    d["cwd"] = str(proj)
    sr.handle_post_tool_use(d, proj)


def run(sr, case):
    """Returns (did it write a binding under the bare sid for the scanned path,
    what the store attributes that path to afterwards)."""
    tmp = Path(tempfile.mkdtemp(prefix="ref-"))
    try:
        proj = tmp / "proj"
        (proj / ".agent-work").mkdir(parents=True)
        target = put(proj, "run-target", "g3", "TARGETMARK", "eng-target")
        target_abs = str(target.resolve())
        sid = SID

        if case == "261-empty-view":
            sid = "s-resumed"
        elif case == "B4-owns-nothing":
            claim(sr, CREW, "run-target", "eng-target", proj)
        elif case == "B5-owns-an-archived-spine":
            claim(sr, CREW, "run-target", "eng-target", proj)
            own = put(proj, "run-own", "g1", "OWNMARK", "eng-own")
            claim(sr, PARENT, "run-own", "eng-own", proj)
            own.unlink()
            shutil.rmtree(str(proj / ".agent-work" / "run-own"))
        elif case == "202-owns-an-archived-spine-target-unclaimed":
            own = put(proj, "run-own", "g1", "OWNMARK", "eng-own")
            claim(sr, PARENT, "run-own", "eng-own", proj)
            own.unlink()
            shutil.rmtree(str(proj / ".agent-work" / "run-own"))
        elif case == "own-archived-spine-target-already-its-own":
            claim(sr, PARENT, "run-target", "eng-target", proj)
            own = put(proj, "run-own", "g1", "OWNMARK", "eng-own")
            claim(sr, PARENT, "run-own", "eng-own", proj)
            own.unlink()
            shutil.rmtree(str(proj / ".agent-work" / "run-own"))
        elif case == "ambiguous-two-spines":
            claim(sr, CREW, "run-target", "eng-target", proj)
            put(proj, "run-second", "g2", "SECONDMARK", "eng-second")
        else:
            raise AssertionError(case)

        sr.decide_session_start({"session_id": sid, "cwd": str(proj)}, proj)
        binding = sr.load_binding(proj)
        return (target_abs in (binding.get(sid) or {}),
                sr.session_view_provenance(binding, sid).get(target_abs))
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)


CASES = [
    ("261-empty-view", "no binding at all, one in-tree spine (#261)"),
    ("B4-owns-nothing", "non-empty view, owns none of it (B4)"),
    ("B5-owns-an-archived-spine", "owns an unloadable entry, target claimed by a sibling (B5)"),
    ("202-owns-an-archived-spine-target-unclaimed",
     "owns an unloadable entry, target claimed by NOBODY (#202's shape)"),
    ("own-archived-spine-target-already-its-own",
     "owns an unloadable entry, target already its OWN claim"),
    ("ambiguous-two-spines", "two in-tree spines -- writer never reached"),
]

print("HEAD (committed) vs the WORKING TREE, at the bind-on-resume writer")
print("=" * 92)
print("{:<62} {:>12} {:>12}".format("case", "HEAD binds", "AFTER binds"))
print("-" * 92)
changed = []
for case, label in CASES:
    b_bound, b_prov = run(BEFORE, case)
    a_bound, a_prov = run(AFTER, case)
    print("{:<62} {:>12} {:>12}".format(label, str(b_bound), str(a_bound)))
    if b_bound != a_bound:
        changed.append((label, b_prov, a_prov))
print("-" * 92)
print("cells that changed: {}".format(len(changed)))
for label, b_prov, a_prov in changed:
    print("  {}".format(label))
    print("      provenance of the scanned path, HEAD  : {}".format(b_prov))
    print("      provenance of the scanned path, AFTER : {}".format(a_prov))
