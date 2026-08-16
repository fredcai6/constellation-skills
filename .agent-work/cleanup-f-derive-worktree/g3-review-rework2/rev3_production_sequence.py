"""The decisive sequence, driven ONLY through production writers.

No hand-built binding store. Every binding entry is written by
`handle_post_tool_use` from a REAL captured harness payload (the repo's pinned
probe capture), so nothing here depends on a store shape I invented.

  1. a crew claims the IN-TREE spine A            -> binding[sid#agent]
  2. the parent claims its own IN-TREE spine B    -> binding[sid]      (appended 2nd)
  3. B is archived away (its file removed)        -- routine at closeout
  4. the parent restarts (SessionStart), then stops (Stop)

Step 1+2 is the B4 fixture the last review accepted as this lane's own topology,
continued by one ordinary event: the parent claiming a spine of its own.
"""
import tempfile
import importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev3-arms-"))  # self-contained: arms are re-extracted from git each run
sys.path.insert(0, str(REPO / "tests"))

PROBE = REPO / "tests/fixtures/probe_payloads.jsonl"
WRAPPERS = [json.loads(l) for l in PROBE.read_text(encoding="utf-8").splitlines() if l.strip()]
PAYLOADS = [w["payload"] for w in WRAPPERS]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
assert PARENT["session_id"] == CREW["session_id"], "one harness session"
SID = PARENT["session_id"]
CREW_KEY = SID + "#" + CREW["agent_id"]


def load(name, rev):
    src = subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                         cwd=str(REPO), capture_output=True, text=True, check=True).stdout
    p = OUT / "arm_{}.py".format(name); p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("p_" + name, str(p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ARMS = [("PREGATE", "999b7663"), ("REWORK1", "6bba3fd2"), ("HEAD", "c5ad8d61")]
MODS = {n: load(n, r) for n, r in ARMS}


def spine_json(gate, marker, eng):
    return json.dumps({
        "work_id": "w", "type": "gated", "items": [gate],
        "tasks": {gate: {"id": gate, "status": "in-progress", "imperative": marker}},
        "engine_session": {"session_id": eng, "status": "active",
                           "claimed_by": "commander", "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    })


def put(proj, work, gate, marker, eng):
    d = proj / ".agent-work" / work; d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"; p.write_text(spine_json(gate, marker, eng), encoding="utf-8")
    (d / "spine.json.journal").write_text('{"seq": 0}\n', encoding="utf-8")
    return p


def claim_cmd(work, eng):
    return ("py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
            "claim --session-id %s --claimed-by commander" % (work, eng))


def post(payload, command, cwd):
    d = dict(payload); d["tool_input"] = {"command": command}; d["cwd"] = str(cwd); return d


def sequence(sr, restart=True):
    tmp = Path(tempfile.mkdtemp(prefix="seq-"))
    try:
        proj = tmp / "proj"; (proj / ".agent-work").mkdir(parents=True)
        put(proj, "run-crew", "g3", "CREWMARK implement the crew gate", "eng-crew")
        b_path = put(proj, "run-own", "g1", "OWNMARK drive your own gate", "eng-own")

        # 1. the crew claims first (the accepted B4 fixture)
        sr.handle_post_tool_use(post(CREW, claim_cmd("run-crew", "eng-crew"), proj), proj)
        # 2. then the parent claims a spine of its own
        sr.handle_post_tool_use(post(PARENT, claim_cmd("run-own", "eng-own"), proj), proj)
        keys_after_claims = list(sr.load_binding(proj))
        # 3. the parent's spine is archived away
        b_path.unlink()
        shutil.rmtree(str(proj / ".agent-work" / "run-own"))

        pay = {"session_id": SID, "cwd": str(proj)}
        start = sr.decide_session_start(dict(pay), proj) if restart else {}
        binding = sr.load_binding(proj)
        crew_spine = str((proj / ".agent-work" / "run-crew" / "spine.json").resolve())
        stop = sr.decide_stop(dict(pay), proj)
        crew_stop = sr.decide_stop({"session_id": SID, "agent_id": CREW["agent_id"],
                                    "cwd": str(proj)}, proj)
        return {
            "keys after the two real claims": keys_after_claims,
            "keys after the restart": list(binding),
            "parent now bound to the CREW's spine": crew_spine in (binding.get(SID) or {}),
            "provenance(crew spine)": sr.session_view_provenance(binding, SID).get(crew_spine),
            "SessionStart handed the parent CREWMARK": "CREWMARK" in json.dumps(start),
            "parent Stop reason": (stop.get("reason") or "(allow)")[:38],
            "parent Stop handed it CREWMARK": "CREWMARK" in json.dumps(stop),
            "the CREW still sees its own gate": "CREWMARK" in json.dumps(crew_stop),
        }
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)


print("probe capture:", PROBE.name, "| sid:", SID, "| crew key:", CREW_KEY)
print("=" * 78)
for name, rev in ARMS:
    print("{:<8} {}".format(name, rev))
    for k, v in sequence(MODS[name]).items():
        print("    {:<44} {}".format(k, v))
print("-" * 78)
print("CONTROL (HEAD, no SessionStart between the claims and the Stop):")
for k, v in sequence(MODS["HEAD"], restart=False).items():
    print("    {:<44} {}".format(k, v))
