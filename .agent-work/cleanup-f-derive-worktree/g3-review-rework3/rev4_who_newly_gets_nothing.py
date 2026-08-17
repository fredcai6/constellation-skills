"""Criterion 4, measured rather than reasoned: enumerate WHO newly gets nothing.

Every state that can reach decide_session_start's fallback, crossed with the
scan's match count, run on REWORK2 (the tree before rework 3) and on WORKTREE.
A row where the two arms differ is a session whose answer rework 3 changed.

Store shapes are written by the production claim writer wherever the topology
allows it; the two "unloadable entry" shapes are produced by ARCHIVING a really
claimed spine (rmtree) or by a real claim whose entry is then emptied of its
`spine` field, never by inventing a store.
"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev4enum-"))


def load(name, rev):
    src = ((REPO / "scripts/hooks/spine_rail.py").read_text(encoding="utf-8") if rev is None
           else subprocess.run(["git", "show", "%s:scripts/hooks/spine_rail.py" % rev], cwd=str(REPO),
                               capture_output=True, text=True, check=True).stdout)
    p = OUT / ("arm_%s.py" % name); p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("arm_" + name, str(p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ARMS = [("REWORK2", "7d12c29d"), ("WORKTREE", None)]
MODS = {n: load(n, r) for n, r in ARMS}

PAYLOADS = [json.loads(l)["payload"] for l in
            (REPO / "tests/fixtures/probe_payloads.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
SID = PARENT["session_id"]
CREW_KEY = SID + "#" + CREW["agent_id"]


def spine_dict(gate, marker, eng):
    return {"work_id": "w", "type": "gated", "items": [gate],
            "tasks": {gate: {"id": gate, "status": "in-progress", "imperative": marker}},
            "engine_session": {"session_id": eng, "status": "active", "claimed_by": "commander",
                               "last_heartbeat": "2026-08-16T00:00:00+00:00"}}


def write_spine(proj, work, gate, marker, eng):
    d = proj / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    (d / "spine.json").write_text(json.dumps(spine_dict(gate, marker, eng)), encoding="utf-8")
    (d / "spine.json.journal").write_text(json.dumps({"seq": 0}) + "\n", encoding="utf-8")
    return str((d / "spine.json").resolve())


def post(sr, payload, work, eng, proj):
    data = dict(payload)
    data["tool_input"] = {"command": ("py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
                                      "claim --session-id %s --claimed-by commander" % (work, eng))}
    data["cwd"] = str(proj)
    return sr.handle_post_tool_use(data, proj)


# --- topologies: each builds a project and returns the scanned spine path ----

def t_no_binding(sr, proj, extra):
    write_spine(proj, "run-x", "gX", "X-MARKER", "eng-x")
    for i in range(extra):
        write_spine(proj, "run-e%d" % i, "gE", "E-MARKER", "eng-e%d" % i)


def t_owns_nothing_crew_claims(sr, proj, extra):
    write_spine(proj, "run-x", "gX", "X-MARKER", "eng-x")
    post(sr, CREW, "run-x", "eng-x", proj)
    for i in range(extra):
        write_spine(proj, "run-e%d" % i, "gE", "E-MARKER", "eng-e%d" % i)


def t_own_archived_crew_claims_scanned(sr, proj, extra):
    write_spine(proj, "run-x", "gX", "X-MARKER", "eng-x")
    write_spine(proj, "run-own", "gO", "O-MARKER", "eng-own")
    post(sr, CREW, "run-x", "eng-x", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    for i in range(extra):
        write_spine(proj, "run-e%d" % i, "gE", "E-MARKER", "eng-e%d" % i)


def t_own_archived_scanned_unclaimed(sr, proj, extra):
    write_spine(proj, "run-x", "gX", "X-MARKER", "eng-x")       # claimed by NOBODY
    write_spine(proj, "run-own", "gO", "O-MARKER", "eng-own")
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    for i in range(extra):
        write_spine(proj, "run-e%d" % i, "gE", "E-MARKER", "eng-e%d" % i)


def t_own_archived_scanned_is_own_bare(sr, proj, extra):
    """The parent claimed the scanned spine itself (bare key), plus a second of
    its own that is later archived. The scanned path is attributed to the very
    key the bind would file it under."""
    write_spine(proj, "run-x", "gX", "X-MARKER", "eng-x")
    write_spine(proj, "run-own", "gO", "O-MARKER", "eng-own")
    post(sr, PARENT, "run-x", "eng-x", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    # blind the loadable one so the fallback is still reached
    b = sr.load_binding(proj)
    for path in list(b.get(SID) or {}):
        if "run-x" in path:
            b[SID][path] = dict(b[SID][path], spine="")     # entry with no usable spine field
    sr.save_binding(proj, b)
    for i in range(extra):
        write_spine(proj, "run-e%d" % i, "gE", "E-MARKER", "eng-e%d" % i)


TOPOLOGIES = [
    ("no binding at all (#261)", t_no_binding),
    ("owns nothing visible; crew claims the scanned spine (B4)", t_owns_nothing_crew_claims),
    ("owns an ARCHIVED entry; crew claims the scanned spine (B5)", t_own_archived_crew_claims_scanned),
    ("owns an ARCHIVED entry; scanned spine claimed by NOBODY (tc1)", t_own_archived_scanned_unclaimed),
    ("owns an ARCHIVED entry; scanned spine is its OWN bare claim", t_own_archived_scanned_is_own_bare),
]

print("{:<62} {:<6} {:<10} {:<10} {}".format("topology", "extra", "arm", "bound?", "renders a gate?"))
diffs = 0
rows = 0
for label, fn in TOPOLOGIES:
    for extra in (0, 1):          # extra unclaimed active spines -> scan match count 1 or 2
        answers = {}
        for arm, _rev in ARMS:
            sr = MODS[arm]
            proj = Path(tempfile.mkdtemp(prefix="e-", dir=str(OUT)))
            (proj / ".agent-work").mkdir()
            fn(sr, proj, extra)
            before = json.dumps(sr.load_binding(proj), sort_keys=True)
            start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
            after = json.dumps(sr.load_binding(proj), sort_keys=True)
            rendered = json.dumps(start.get("hookSpecificOutput") or {})
            answers[arm] = (before != after, rendered != "{}")
            rows += 1
            print("{:<62} {:<6} {:<10} {:<10} {}".format(
                label if arm == ARMS[0][0] else "", extra, arm,
                str(answers[arm][0]), str(answers[arm][1])))
        if answers["REWORK2"] != answers["WORKTREE"]:
            diffs += 1
            print("  ^^ CHANGED BY REWORK 3: {} (extra={})".format(label, extra))
        print()
print("rows measured:", rows, " topologies x match-counts:", len(TOPOLOGIES) * 2,
      " rows whose answer rework 3 changed:", diffs)
print("scratch:", OUT)
