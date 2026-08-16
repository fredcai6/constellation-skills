"""Second route to the same leak, with the NATURAL key order (parent claimed
before its crew). `_reap_binding_entries` drops an outer key whose every entry
was reaped (`if kept:`), and `_resume_mutate` then re-inserts `new_map[sid]` --
at the END of the dict. Provenance is last-key-wins, so the reap+rebind flips
ownership of the crew's path to the parent's bare key by itself.
"""
import tempfile
import importlib.util, json, shutil, subprocess, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = "/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree"
OUT = Path(tempfile.mkdtemp(prefix="g3rev3-arms-"))  # self-contained: arms are re-extracted from git each run

def load(name, rev):
    src = subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    p = OUT / "arm_{}.py".format(name); p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("r_" + name, str(p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

ARMS = [("PREGATE", "999b7663"), ("REWORK1", "6bba3fd2"), ("HEAD", "c5ad8d61")]
MODS = {n: load(n, r) for n, r in ARMS}
SID, AGENT = "s-parent", "agentcrew"
OLD = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
FRESH = datetime.now(timezone.utc).isoformat()

def run(sr, own_claimed_at, label):
    tmp = Path(tempfile.mkdtemp(prefix="reap-"))
    try:
        proj = tmp / "proj"; (proj / ".agent-work").mkdir(parents=True)
        d = proj / ".agent-work" / "run-crew"; d.mkdir(parents=True)
        crew = str(d / "spine.json")
        Path(crew).write_text(json.dumps({
            "work_id": "w", "type": "gated", "items": ["g3"],
            "tasks": {"g3": {"id": "g3", "status": "in-progress",
                             "imperative": "CREWMARK implement the crew gate"}},
            "engine_session": {"session_id": "eng-crew", "status": "active",
                               "claimed_by": "crew", "last_heartbeat": "x"}}), encoding="utf-8")
        (d / "spine.json.journal").write_text("one\n", encoding="utf-8")
        own = str(proj / ".agent-work" / "run-own" / "spine.json")  # archived away
        # NATURAL order: the parent (commander) claimed FIRST, its crew second.
        sr.save_binding(proj, {
            SID: {own: {"spine": own, "engine_session": "eng-own",
                        "worktree": str(proj), "claimed_at": own_claimed_at}},
            SID + "#" + AGENT: {crew: {"spine": crew, "engine_session": "eng-crew",
                                       "worktree": str(proj), "claimed_at": FRESH}},
        })
        pay = {"session_id": SID, "cwd": str(proj)}
        start = sr.decide_session_start(dict(pay), proj)
        b = sr.load_binding(proj)
        stop = sr.decide_stop(dict(pay), proj)
        return {
            "arm/label": label,
            "binding key order after": list(b),
            "parent bound to CREW spine": crew in (b.get(SID) or {}),
            "provenance(crew path)": sr.session_view_provenance(b, SID).get(crew),
            "SessionStart leaked CREWMARK": "CREWMARK" in json.dumps(start),
            "parent Stop reason": (stop.get("reason") or "")[:34],
            "parent Stop LEAKED CREWMARK": "CREWMARK" in json.dumps(stop),
        }
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)

for age_label, ts in (("own entry 48h stale (reaped)", OLD), ("own entry fresh (retained)", FRESH)):
    print("=" * 78)
    print("ROUTE: parent key FIRST (natural), " + age_label)
    for name, _ in ARMS:
        print("  " + json.dumps(run(MODS[name], ts, name)))
