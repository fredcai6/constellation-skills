"""What the RENDER now refuses -- six topologies x two scan-match counts, on
two arms, with the rows that changed answer counted mechanically.

The question this answers is the handoff's risk question: the B6 repair makes
`decide_session_start`'s scan skip a candidate this session's view attributes to
another binding key, so WHO newly gets nothing, and is any of it legitimate?

Arms are REWORK3 (the committed HEAD this rework amends) and WORKTREE (the tree
as it stands). Each arm prints the sha256 and byte length of the source it
actually loaded, and a guard asserts the two differ and that the render loop is
present in one and absent from the other -- every scratch harness on this gate
has been pinned to a revision the tree moved past, so the arms are checked
before any row is believed.

Every binding entry is written by the production writer, `handle_post_tool_use`,
from the repo's pinned probe capture. The one exception is named where it
happens: the cross-session row needs a second harness session_id, which the
capture does not contain, so its payload is constructed while the WRITER stays
production's.
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rw4-refuses-"))
RENDER_LOOP = "for _cand_spine, _cand_path in matches:"


def load(name, rev):
    if rev is None:
        src = (REPO / "scripts/hooks/spine_rail.py").read_text(encoding="utf-8")
    else:
        src = subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                             cwd=str(REPO), capture_output=True, text=True, check=True).stdout
    p = OUT / ("arm_%s.py" % name)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("arm_" + name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("arm {:<9} sha256={} bytes={} render_loop={}".format(
        name, hashlib.sha256(src.encode()).hexdigest()[:12], len(src), RENDER_LOOP in src))
    return m, src


HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                      capture_output=True, text=True, check=True).stdout.strip()
ARMS = [("REWORK3", HEAD), ("WORKTREE", None)]
MODS, SRCS = {}, {}
for _n, _r in ARMS:
    MODS[_n], SRCS[_n] = load(_n, _r)
assert SRCS["REWORK3"] != SRCS["WORKTREE"], "arms are the same source"
assert RENDER_LOOP not in SRCS["REWORK3"] and RENDER_LOOP in SRCS["WORKTREE"]
assert "_attributed_to_another_key" in SRCS["REWORK3"]  # rework 3's write guard is in BOTH
print("guard ok: 2 distinct arms, HEAD={}, render loop only in WORKTREE\n".format(HEAD[:8]))

PAYLOADS = [json.loads(l)["payload"] for l in
            (REPO / "tests/fixtures/probe_payloads.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
SID = PARENT["session_id"]
CREW_KEY = SID + "#" + CREW["agent_id"]
OTHER_SID = "another-harness-session"


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


def claim(sr, payload, work, eng, proj):
    data = dict(payload)
    data["tool_input"] = {"command": (
        "py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
        "claim --session-id %s --claimed-by commander" % (work, eng))}
    data["cwd"] = str(proj)
    return sr.handle_post_tool_use(data, proj)


# Each topology says who claims the SCANNED spines and whether the acting
# session owns an entry of its own that no longer loads.
TOPOLOGIES = [
    ("#261 no binding at all", "nobody", False, False),
    ("B4 owns nothing visible; crew claims the scan", "crew", False, False),
    ("B5/B6 owns an ARCHIVED entry; crew claims the scan", "crew", True, False),
    ("tc1 owns an ARCHIVED entry; scan claimed by NOBODY", "nobody", True, False),
    ("owns an ARCHIVED entry; the scan is its OWN bare claim", "self", True, False),
    ("B7 owns an ARCHIVED entry; ANOTHER SESSION claims the scan", "other", True, True),
    # Only distinguishable at n=2, and the row where the repair CHOOSES rather
    # than withholds: the crew claims whichever spine the glob returns FIRST, so
    # glob order is removed as a variable in the other direction.
    ("owns an ARCHIVED entry; crew claims the LEADING match only", "crew-leading", True, True),
]


def build(sr, proj, claimant, archived_own):
    """Returns the list of scanned spine paths, after all claims are written."""
    scanned = []
    for work, gate, marker, eng in WORKS:
        scanned.append(write_spine(proj, work, gate, marker, eng))
    if archived_own:
        write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
        claim(sr, PARENT, "run-own", "eng-own", proj)
    if claimant == "crew-leading":
        leading = Path(sr._scan_active_spine(proj)[0][1]).parent.name
        eng = dict((w, e) for w, _g, _m, e in WORKS)[leading]
        claim(sr, CREW, leading, eng, proj)
    for (work, _gate, _marker, eng) in WORKS:
        if claimant == "crew":
            claim(sr, CREW, work, eng, proj)
        elif claimant == "self":
            claim(sr, PARENT, work, eng, proj)
        elif claimant == "other":
            # constructed payload, production writer: the pinned capture holds
            # exactly one harness session_id and this row needs a second one.
            claim(sr, {"session_id": OTHER_SID}, work, eng, proj)
    if archived_own:
        shutil.rmtree(str(proj / ".agent-work" / "run-own"))  # archived at closeout
    return scanned


rows = {}
for n_matches in (1, 2):
    WORKS = [("run-a", "g3", "MARKER-A first gate", "eng-a")]
    if n_matches == 2:
        WORKS.append(("run-b", "g4", "MARKER-B second gate", "eng-b"))
    for label, claimant, archived_own, _note in TOPOLOGIES:
        for arm, _rev in ARMS:
            sr = MODS[arm]
            proj = Path(tempfile.mkdtemp(prefix="t-", dir=str(OUT)))
            (proj / ".agent-work").mkdir()
            scanned = build(sr, proj, claimant, archived_own)
            before = sr.load_binding(proj)
            assert len(sr._scan_active_spine(proj)) == n_matches, (label, n_matches)

            start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)

            rendered = json.dumps(start.get("hookSpecificOutput") or {})
            after = sr.load_binding(proj)
            filed = set(after.get(SID) or {}) - set(before.get(SID) or {})
            rows[(n_matches, label, arm)] = {
                "renders": "RESUMING" in rendered,
                "marker": ("A" if "MARKER-A" in rendered else
                           "B" if "MARKER-B" in rendered else
                           "own" if "OWN-MARKER" in rendered else "-"),
                "binds_a_scanned_path": bool(filed & set(scanned)),
            }

changed = []
for n_matches in (1, 2):
    for label, _c, _a, _n in TOPOLOGIES:
        a = rows[(n_matches, label, "REWORK3")]
        b = rows[(n_matches, label, "WORKTREE")]
        same = a == b
        if not same:
            changed.append((n_matches, label))
        print("n={}  {}{}".format(n_matches, label, "" if same else "   <-- CHANGED"))
        print("      REWORK3   {}".format(json.dumps(a, sort_keys=True)))
        print("      WORKTREE  {}".format(json.dumps(b, sort_keys=True)))

print("\nrows measured: {}   topologies x match-counts: {}   rows whose answer this rework changed: {}"
      .format(len(rows), len(TOPOLOGIES) * 2, len(changed)))
for n_matches, label in changed:
    print("  CHANGED  n={}  {}".format(n_matches, label))
print("scratch:", OUT)
