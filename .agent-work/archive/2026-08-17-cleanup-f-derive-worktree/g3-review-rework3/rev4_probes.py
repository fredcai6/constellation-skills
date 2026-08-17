"""Review 4's follow-on probes, all against the WORKTREE arm.

P1  case folding      -- explicit case expectation, and a SIMULATED Windows
                         normcase, since normcase is the identity on this host
P2  make it raise     -- adversarial inputs to `_attributed_to_another_key`
P3  three calls       -- scoped null 1: SessionStart, Stop, SessionStart, Stop
P4  gauge writer      -- scoped null 3: what the gauge writer resolves in the
                         B5 topology, refused-bind vs the rework-2 bind
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev4p-"))
sys.path.insert(0, str(REPO / "scripts" / "hooks"))

spec = importlib.util.spec_from_file_location("sr_wt", str(REPO / "scripts/hooks/spine_rail.py"))
sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
spec2 = importlib.util.spec_from_file_location("gw", str(REPO / "scripts/hooks/gauge_writer_hook.py"))
gw = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(gw)

PROBE = REPO / "tests/fixtures/probe_payloads.jsonl"
PAYLOADS = [json.loads(l)["payload"] for l in PROBE.read_text(encoding="utf-8").splitlines() if l.strip()]
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


def post(payload, work, eng, proj):
    data = dict(payload)
    data["tool_input"] = {"command": ("py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
                                      "claim --session-id %s --claimed-by commander" % (work, eng))}
    data["cwd"] = str(proj)
    return sr.handle_post_tool_use(data, proj)


def b5_fixture(proj):
    crew_spine = write_spine(proj, "run-crew", "g3", "CREW-MARKER implement the crew gate", "eng-crew")
    write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
    post(CREW, "run-crew", "eng-crew", proj)
    post(PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    return crew_spine


def fresh(tag):
    p = Path(tempfile.mkdtemp(prefix=tag + "-", dir=str(OUT)))
    (p / ".agent-work").mkdir()
    return p


print("=" * 78)
print("P1  case folding")
print("  os.path.normcase is identity on this host:",
      os.path.normcase("/P/A/Spine.json") == "/P/A/Spine.json")
lower = "/p/.agent-work/run-crew/spine.json"
upper = "/p/.agent-work/RUN-CREW/spine.json"
owners = {upper: "sid#agent"}
print("  linux  _same_path(lower, upper)                :", sr._same_path(lower, upper),
      "(expect False -- they are two different files here)")
print("  linux  _attributed_to_another_key -> refuse?   :",
      sr._attributed_to_another_key(owners, lower, "sid"), "(expect False)")
_real = os.path.normcase
try:
    os.path.normcase = str.lower              # simulate a Windows host
    print("  win32  _same_path(lower, upper)                :", sr._same_path(lower, upper),
          "(expect True -- one file under a case-insensitive fs)")
    print("  win32  _attributed_to_another_key -> refuse?   :",
          sr._attributed_to_another_key(owners, lower, "sid"), "(expect True)")
finally:
    os.path.normcase = _real
print("  restored:", os.path.normcase is _real)

print("=" * 78)
print("P2  try to make _attributed_to_another_key raise")


class Boom(dict):
    def items(self):
        raise RuntimeError("boom")


class BoomKey(str):
    def __eq__(self, other):
        raise RuntimeError("boom-eq")

    def __hash__(self):
        return 0


adversarial = [
    ("owners.items() raises", Boom(), "/p/s.json", "sid"),
    ("owner_key.__eq__ raises", {"/p/s.json": BoomKey("x")}, "/p/s.json", "sid"),
    ("owners is None", None, "/p/s.json", "sid"),
    ("owners is a list", ["/p/s.json"], "/p/s.json", "sid"),
    ("spine_path is None", {"/p/s.json": "other"}, None, "sid"),
    ("bind_key is None", {"/p/s.json": "other"}, "/p/s.json", None),
    ("non-str owners key", {42: "other"}, "/p/s.json", "sid"),
    ("owner_key is None", {"/p/s.json": None}, "/p/s.json", "sid"),
]
for label, o, p, k in adversarial:
    try:
        r = sr._attributed_to_another_key(o, p, k)
        print("  {:<26} -> {}".format(label, r))
    except Exception as e:  # pragma: no cover -- the whole point
        print("  {:<26} -> RAISED {!r}".format(label, e))

print("=" * 78)
print("P3  three-plus call sequence on B5's topology (WORKTREE arm)")
proj = fresh("p3")
crew_spine = b5_fixture(proj)
seq = []
for i in range(2):
    st = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    b = sr.load_binding(proj)
    stop = sr.decide_stop({"session_id": SID, "cwd": str(proj)}, proj)
    crew_stop = sr.decide_stop({"session_id": SID, "agent_id": CREW["agent_id"], "cwd": str(proj)}, proj)
    seq.append({
        "round": i + 1,
        "start_render": json.dumps(st.get("hookSpecificOutput") or {})[:40],
        "bound_crew_spine": crew_spine in (b.get(SID) or {}),
        "attribution": sr.session_view_provenance(b, SID).get(crew_spine),
        "parent_stop": (stop.get("reason") or "")[:34],
        "parent_stop_leaks": "CREW-MARKER" in json.dumps(stop),
        "crew_sees_own_gate": "CREW-MARKER" in json.dumps(crew_stop.get("reason") or ""),
    })
for row in seq:
    print("  " + json.dumps(row, sort_keys=True))
print("  rounds identical (idempotent):", seq[0]["bound_crew_spine"] == seq[1]["bound_crew_spine"]
      and seq[0]["attribution"] == seq[1]["attribution"]
      and seq[0]["crew_sees_own_gate"] == seq[1]["crew_sees_own_gate"])

print("=" * 78)
print("P4  gauge writer in the B5 topology (scoped null 3)")
proj = fresh("p4")
crew_spine = b5_fixture(proj)
sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
parent_paths = gw.resolve_gauge_path(proj, SID)
crew_paths = gw.resolve_gauge_path(proj, CREW_KEY)
print("  after the REFUSED bind:")
print("    parent key ->", [str(p) for p in parent_paths])
print("    crew key   ->", [str(p) for p in crew_paths])
# and the counterfactual: what rework 2 would have left behind (bind present)
proj2 = fresh("p4b")
crew_spine2 = b5_fixture(proj2)
b = sr.load_binding(proj2)
b.setdefault(SID, {})[crew_spine2] = {"spine": crew_spine2, "engine_session": "eng-crew",
                                      "worktree": str(proj2), "claimed_at": "2026-08-16T00:00:00+00:00"}
sr.save_binding(proj2, b)
print("  counterfactual, bind PRESENT (what rework 2 wrote):")
print("    parent key ->", [str(p) for p in gw.resolve_gauge_path(proj2, SID)])
print("    crew key   ->", [str(p) for p in gw.resolve_gauge_path(proj2, CREW_KEY)])
print("=" * 78)
print("scratch:", OUT)
