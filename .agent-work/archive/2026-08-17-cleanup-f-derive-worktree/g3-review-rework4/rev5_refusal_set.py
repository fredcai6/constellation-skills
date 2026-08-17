"""What the render now REFUSES -- enumerated mechanically, REWORK3 vs WORKTREE.

Criterion 4 asks for the refusal set and for a legitimate resume context that is
now withheld, or a statement that none was found. This enumerates
topology x match-count on the two arms either side of the fix and prints the rows
whose answer changed, so "who newly gets nothing" is counted, not asserted.

C9/C10 additionally probe the ONE input the fix's own choice turns on -- a
SessionStart payload carrying `agent_id`, which makes `own_key != sid`. The
pinned probe capture contains no SessionStart payload at all (six rows, all
PostToolUse), so this input is unmeasured upstream and must be constructed.
"""
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev5rs-"))


def load(name, rev):
    if rev is None:
        src = (REPO / "scripts/hooks/spine_rail.py").read_text(encoding="utf-8")
    else:
        src = subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                             cwd=str(REPO), capture_output=True, text=True, check=True).stdout
    p = OUT / ("arm_%s.py" % name)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("rs_" + name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, src


ARMS = ["REWORK3", "WORKTREE"]
REVS = {"REWORK3": "68d190f7", "WORKTREE": None}
MODS, SRCS = {}, {}
for _n in ARMS:
    MODS[_n], SRCS[_n] = load(_n, REVS[_n])
assert SRCS["REWORK3"] != SRCS["WORKTREE"]
assert "for _cand_spine, _cand_path in matches:" in SRCS["WORKTREE"]
assert "for _cand_spine, _cand_path in matches:" not in SRCS["REWORK3"]
print("arms: REWORK3=68d190f7 (%d bytes) vs WORKTREE (%d bytes); render loop only in WORKTREE\n"
      % (len(SRCS["REWORK3"]), len(SRCS["WORKTREE"])))

PAYLOADS = [json.loads(l)["payload"] for l in
            (REPO / "tests/fixtures/probe_payloads.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
SID = PARENT["session_id"]
AID = CREW["agent_id"]
CREW_KEY = SID + "#" + AID


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


MARKS = ("CAND0", "CAND1", "CAND2", "MINE")


def render_of(start):
    blob = json.dumps(start.get("hookSpecificOutput") or {})
    return sorted(m for m in MARKS if (m + "-MARKER") in blob) or ["<nothing>"]


# --- topologies -------------------------------------------------------------
# Each builds a project with n candidate spines and returns nothing; `who`
# decides who claims candidate i.
def topology(name, own_state, claimer):
    """own_state: 'none' (no binding at all) | 'archived' (owns an entry whose
    spine no longer loads) | 'foreign-only' (visible entries, owns none).
    claimer(i, n) -> None | 'crew' | 'self'."""
    return (name, own_state, claimer)


TOPOLOGIES = [
    topology("#261 no binding at all", "none", lambda i, n: None),
    topology("B4 owns nothing visible; crew claims all", "foreign-only", lambda i, n: "crew"),
    topology("B5/B6 archived; crew claims ALL", "archived", lambda i, n: "crew"),
    topology("archived; crew claims the FIRST only", "archived", lambda i, n: "crew" if i == 0 else None),
    topology("archived; crew claims the LAST only", "archived", lambda i, n: "crew" if i == n - 1 else None),
    topology("tc1 archived; claimed by NOBODY", "archived", lambda i, n: None),
    topology("archived; SELF claims all (bare sid)", "archived", lambda i, n: "self"),
    topology("archived; SELF first, crew rest", "archived", lambda i, n: "self" if i == 0 else "crew"),
]


def build(sr, proj, own_state, claimer, n):
    if own_state in ("archived", "foreign-only"):
        write_spine(proj, "run-own", "execute", "MINE-MARKER the archived one", "eng-own")
    paths = []
    for i in range(n):
        p = write_spine(proj, "run-c%d" % i, "g%d" % i, "CAND%d-MARKER candidate %d" % (i, i), "eng-c%d" % i)
        paths.append((i, "run-c%d" % i, "eng-c%d" % i, p))
    if own_state == "archived":
        post(sr, PARENT, "run-own", "eng-own", proj)
    for i, work, eng, _p in paths:
        who = claimer(i, n)
        if who == "crew":
            post(sr, CREW, work, eng, proj)
        elif who == "self":
            post(sr, PARENT, work, eng, proj)
    if own_state == "foreign-only":
        post(sr, CREW, "run-own", "eng-own", proj)
    if own_state in ("archived", "foreign-only"):
        shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    return paths


print("=" * 78)
rows, changed = 0, []
for name, own_state, claimer in TOPOLOGIES:
    for n in (1, 2, 3):
        answers = {}
        for arm in ARMS:
            sr = MODS[arm]
            proj = Path(tempfile.mkdtemp(prefix="rs-", dir=str(OUT)))
            (proj / ".agent-work").mkdir()
            build(sr, proj, own_state, claimer, n)
            before = sr.load_binding(proj)
            start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
            after = sr.load_binding(proj)
            answers[arm] = {"renders": render_of(start),
                            "wrote": bool(set(after.get(SID) or {}) - set(before.get(SID) or {}))}
            rows += 1
        same = answers["REWORK3"] == answers["WORKTREE"]
        if not same:
            changed.append((name, n, answers))
        print("  {:<6} n={}  {:<42} REWORK3={:<28} WORKTREE={}".format(
            "SAME" if same else "CHANGED", n, name,
            json.dumps(answers["REWORK3"]["renders"]) + ("+w" if answers["REWORK3"]["wrote"] else ""),
            json.dumps(answers["WORKTREE"]["renders"]) + ("+w" if answers["WORKTREE"]["wrote"] else "")))

print("\nrows measured: %d   topologies x counts: %d   rows whose answer rework 4 changed: %d"
      % (rows, len(TOPOLOGIES) * 3, len(changed)))
for name, n, a in changed:
    print("  CHANGED n=%d  %-42s %s -> %s" % (n, name, a["REWORK3"]["renders"], a["WORKTREE"]["renders"]))

# --- C9/C10: the input the fix's own choice turns on ------------------------
print("\n" + "=" * 78)
print("C9/C10  a SessionStart carrying `agent_id` (own_key != sid) -- CONSTRUCTED:")
print("        the pinned probe capture has %d rows and NO SessionStart payload at all,"
      % len(PAYLOADS))
print("        so this input is unmeasured upstream and cannot be reproduced from it.\n")

for label, claim_as in (("C9  candidate claimed by the SESSION's bare sid  ", "self"),
                        ("C10 candidate claimed by this agent's OWN key   ", "agent")):
    out = {}
    for arm in ARMS:
        sr = MODS[arm]
        proj = Path(tempfile.mkdtemp(prefix="c9-", dir=str(OUT)))
        (proj / ".agent-work").mkdir()
        write_spine(proj, "run-own", "execute", "MINE-MARKER archived", "eng-own")
        post(sr, CREW, "run-own", "eng-own", proj)        # archived entry under sid#agent
        write_spine(proj, "run-c0", "g0", "CAND0-MARKER candidate 0", "eng-c0")
        post(sr, PARENT if claim_as == "self" else CREW, "run-c0", "eng-c0", proj)
        shutil.rmtree(str(proj / ".agent-work" / "run-own"))
        before = sr.load_binding(proj)
        start = sr.decide_session_start({"session_id": SID, "agent_id": AID, "cwd": str(proj)}, proj)
        after = sr.load_binding(proj)
        out[arm] = {"renders": render_of(start),
                    "wrote": bool(set(after.get(SID) or {}) - set(before.get(SID) or {}))}
    print("  %s REWORK3=%-22s WORKTREE=%-22s %s" % (
        label, json.dumps(out["REWORK3"]), json.dumps(out["WORKTREE"]),
        "SAME" if out["REWORK3"] == out["WORKTREE"] else "CHANGED"))

print("\nscratch: %s" % OUT)
