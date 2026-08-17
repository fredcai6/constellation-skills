"""C2b -- the ambiguous-scan render leak, with glob order removed as a variable.

C2 left one hole: with two active spines, one crew-claimed and one unclaimed,
WHICH one gets rendered depends on `base.glob("*/spine.json")` order, which is
filesystem order and not guaranteed. So here BOTH remaining active spines are
claimed by the CREW (#202: one binding key legitimately holds N spines). Then
whichever one the glob returns first, the spine the parent is handed is one the
store visibly attributes to another binding key -- the exact contradiction
`_attributed_to_another_key` refuses to WRITE, still RENDERED.

Also prints the parent's nudge counter, to explain the round-2 difference in P3.
"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev4c2b-"))


def load(name, rev):
    if rev is None:
        src = (REPO / "scripts/hooks/spine_rail.py").read_text(encoding="utf-8")
    else:
        src = subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                             cwd=str(REPO), capture_output=True, text=True, check=True).stdout
    p = OUT / ("arm_%s.py" % name); p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("arm_" + name, str(p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ARMS = [("PREGATE", "999b7663"), ("REWORK2", "7d12c29d"), ("WORKTREE", None)]
MODS = {n: load(n, r) for n, r in ARMS}
assert "_attributed_to_another_key" in (OUT / "arm_WORKTREE.py").read_text()
assert "_attributed_to_another_key" not in (OUT / "arm_REWORK2.py").read_text()

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


for arm, _rev in ARMS:
    sr = MODS[arm]
    proj = Path(tempfile.mkdtemp(prefix=arm + "-", dir=str(OUT)))
    (proj / ".agent-work").mkdir()
    a = write_spine(proj, "run-crew-a", "g3", "CREWA-MARKER the crew's first gate", "eng-a")
    b = write_spine(proj, "run-crew-b", "g4", "CREWB-MARKER the crew's second gate", "eng-b")
    write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
    post(sr, CREW, "run-crew-a", "eng-a", proj)
    post(sr, CREW, "run-crew-b", "eng-b", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))          # archived at closeout

    binding = sr.load_binding(proj)
    owners = sr.session_view_provenance(binding, SID)
    matches = sr._scan_active_spine(proj)
    # every remaining active spine is attributed to the CREW's composite key
    assert len(matches) == 2, len(matches)
    assert all(owners.get(p) == CREW_KEY for _s, p in matches), owners
    assert owners.get(a) == CREW_KEY and owners.get(b) == CREW_KEY

    start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    rendered = json.dumps(start.get("hookSpecificOutput") or {})
    after = sr.load_binding(proj)
    print("{:<9} {}".format(arm, json.dumps({
        "scan_matches": len(matches),
        "every_match_owned_by_crew": True,
        "wrote_a_binding": bool(set(after.get(SID) or {}) - set(binding.get(SID) or {})),
        "renders_a_crew_gate": ("CREWA-MARKER" in rendered) or ("CREWB-MARKER" in rendered),
        "renders_pick_it_up": "Pick the run back up" in rendered,
    }, sort_keys=True)))
    if arm == "WORKTREE":
        print("         rendered additionalContext ->")
        print("         " + (json.loads(rendered).get("additionalContext", "")[:220] if rendered != "{}" else "(empty)"))

# --- P3's round-2 explanation: the 3-strike nudge counter, keyed by sid alone --
print()
sr = MODS["WORKTREE"]
proj = Path(tempfile.mkdtemp(prefix="nudge-", dir=str(OUT)))
(proj / ".agent-work").mkdir()
write_spine(proj, "run-crew", "g3", "CREW-MARKER implement the crew gate", "eng-crew")
write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
post(sr, CREW, "run-crew", "eng-crew", proj)
post(sr, PARENT, "run-own", "eng-own", proj)
shutil.rmtree(str(proj / ".agent-work" / "run-own"))
for i, who in enumerate(["parent", "crew", "parent", "crew"]):
    payload = {"session_id": SID, "cwd": str(proj)}
    if who == "crew":
        payload["agent_id"] = CREW["agent_id"]
    out = sr.decide_stop(payload, proj)
    n = sr.load_nudges(proj).get(SID, {})
    print("  stop #{} ({:<6}) decision={:<9} nudge_count={}".format(
        i + 1, who, out.get("decision") or ("continue" if out.get("continue") else "-"), n.get("count")))
print("scratch:", OUT)
