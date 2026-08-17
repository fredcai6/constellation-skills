"""C3 in detail: the `owned` door into the scan-bind.

Rework 2 gates the withhold on `not owned`. A session that OWNS an entry whose
spine is unreadable therefore keeps the scan. This asks what the scan then does
when the one spine it finds is one a SIBLING AGENT of the same session claimed --
and whether the answer depends on binding-file key ORDER, since
`session_view_provenance` is last-key-wins over `binding`'s own iteration order.
"""
import tempfile
import importlib.util, json, os, shutil, subprocess, tempfile
from pathlib import Path

REPO = "/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree"
OUT = Path(tempfile.mkdtemp(prefix="g3rev3-arms-"))  # self-contained: arms are re-extracted from git each run

def load(name, rev):
    src = subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    p = OUT / "arm_{}.py".format(name); p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("f_" + name, str(p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

ARMS = [("PREGATE", "999b7663"), ("REWORK1", "6bba3fd2"), ("HEAD", "c5ad8d61")]
MODS = {n: load(n, r) for n, r in ARMS}

SID, AGENT = "s-parent", "agentcrew"

def spine_doc(gate, marker, eng):
    return {"work_id": "w", "type": "gated", "items": [gate],
            "tasks": {gate: {"id": gate, "status": "in-progress",
                             "imperative": marker + " keep going"}},
            "engine_session": {"session_id": eng, "status": "active",
                               "claimed_by": "crew", "last_heartbeat": "x"}}

def build(proj, parent_key_first):
    d = proj / ".agent-work" / "run-crew"; d.mkdir(parents=True)
    crew = str(d / "spine.json")
    Path(crew).write_text(json.dumps(spine_doc("g3", "CREWMARK", "eng-crew")), encoding="utf-8")
    (d / "spine.json.journal").write_text("one\n", encoding="utf-8")
    own = str(proj / ".agent-work" / "run-own" / "spine.json")  # archived out from under it
    e = lambda p, eng: {"spine": p, "engine_session": eng, "worktree": str(proj),
                        "claimed_at": "2026-08-16T00:00:00+00:00"}
    store = {}
    if parent_key_first:
        store[SID] = {own: e(own, "eng-own")}
        store[SID + "#" + AGENT] = {crew: e(crew, "eng-crew")}
    else:
        store[SID + "#" + AGENT] = {crew: e(crew, "eng-crew")}
        store[SID] = {own: e(own, "eng-own")}
    return store, crew

def run(sr, parent_key_first, restart=True):
    tmp = Path(tempfile.mkdtemp(prefix="c3-"))
    try:
        proj = tmp / "proj"; (proj / ".agent-work").mkdir(parents=True)
        store, crew = build(proj, parent_key_first)
        sr.save_binding(proj, store)
        pay = {"session_id": SID, "cwd": str(proj)}
        start = sr.decide_session_start(dict(pay), proj) if restart else {}
        b = sr.load_binding(proj)
        bound_here = crew in (b.get(SID) or {})
        prov = sr.session_view_provenance(b, SID).get(crew)
        stop = sr.decide_stop(dict(pay), proj)
        crew_pay = {"session_id": SID, "agent_id": AGENT, "cwd": str(proj)}
        crew_stop = sr.decide_stop(dict(crew_pay), proj)
        return {
            "parent bound to crew spine": bound_here,
            "SessionStart ctx leaks CREWMARK": "CREWMARK" in json.dumps(start),
            "provenance of crew path": prov,
            "parent Stop": (stop.get("reason") or "")[:26],
            "parent Stop leaks CREWMARK": "CREWMARK" in json.dumps(stop),
            "CREW's own Stop leaks/keeps its gate": "CREWMARK" in json.dumps(crew_stop),
        }
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)

for order_label, pf in (("parent key FIRST (commander claimed before its crew)", True),
                        ("crew key FIRST (crew claimed before the parent)", False)):
    print("=" * 78)
    print("ORDER: " + order_label)
    for name, _ in ARMS:
        r = run(MODS[name], pf)
        print("  {:<8} {}".format(name, json.dumps(r)))
    r0 = run(MODS["HEAD"], pf, restart=False)
    print("  {:<8} {}".format("HEAD/no-restart(control)", json.dumps(r0)))
