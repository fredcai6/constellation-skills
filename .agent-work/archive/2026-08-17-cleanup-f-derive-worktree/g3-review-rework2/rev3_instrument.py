"""Reviewer-3's own instrument for #609 lane F g3 rework 2.

Independent of every prior harness. Three arms extracted BY ME and pinned by
revision, plus the WORKING TREE, with a guard that refuses to print unless the
arms genuinely differ -- by content hash AND by behaviour on the one cell this
rework exists to move.

Every cell is a SEQUENCE: SessionStart, then Stop, over ONE shared binding
store, with the spine genuinely inside <project>/.agent-work/*/spine.json where
the fallback scan can find it. Markers are pairwise NON-SUBSTRING of each other
(the review-1 harness could not read two of its own cases because CREW-MARKER
is a substring of OTHERCREW-MARKER).
"""
import hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = "/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree"
HOOK = "scripts/hooks/spine_rail.py"
OUT = Path(tempfile.mkdtemp(prefix="g3rev3-arms-"))  # self-contained: arms are re-extracted from git each run

ARMS = [("PREGATE", "999b7663"), ("REWORK1", "6bba3fd2"), ("HEAD", "c5ad8d61")]


def sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True, check=True).stdout


def load_arm(name, rev):
    if rev == "WORKTREE":
        src = Path(REPO, HOOK).read_text(encoding="utf-8")
    else:
        src = sh("git", "show", "{}:{}".format(rev, HOOK))
    p = OUT / "arm_{}.py".format(name)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("sr_" + name, str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, hashlib.sha256(src.encode()).hexdigest()[:12]


MODS, HASHES = {}, {}
for nm, rv in ARMS:
    MODS[nm], HASHES[nm] = load_arm(nm, rv)
WT_SRC = Path(REPO, HOOK).read_text(encoding="utf-8")
WT_HASH = hashlib.sha256(WT_SRC.encode()).hexdigest()[:12]

# ---- fixture builders --------------------------------------------------------

def spine_doc(gate, marker, eng, status="in-progress"):
    return {
        "work_id": "w", "type": "gated", "items": [gate],
        "tasks": {gate: {"id": gate, "status": status, "imperative": marker + " keep going"}},
        "engine_session": {"session_id": eng, "status": "active",
                           "claimed_by": "crew", "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    }


def write_spine(proj, work, gate, marker, eng):
    d = proj / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"
    p.write_text(json.dumps(spine_doc(gate, marker, eng)), encoding="utf-8")
    (d / "spine.json.journal").write_text("one\n", encoding="utf-8")
    return str(p)


def entry(proj, spath, eng):
    return {"spine": spath, "engine_session": eng, "worktree": str(proj),
            "claimed_at": "2026-08-16T00:00:00+00:00"}


def put_binding(sr, proj, mapping):
    sr.save_binding(proj, mapping)


# ---- the cells ---------------------------------------------------------------
# Each returns (proj, sid, payload_extra, note) with the store pre-seeded.

SID = "s-parent"
AGENT = "agentcrew"


def cell_b4(sr, proj):
    """B4: crew claimed the IN-TREE spine under sid#agent; parent owns nothing."""
    crew = write_spine(proj, "run-crew", "g3", "CREWMARK", "eng-crew")
    put_binding(sr, proj, {SID + "#" + AGENT: {crew: entry(proj, crew, "eng-crew")}})
    return {}


def cell_261(sr, proj):
    """#261: no binding at all, exactly one active in-tree spine."""
    write_spine(proj, "run-solo", "g1", "SOLOMARK", "eng-solo")
    put_binding(sr, proj, {})
    return {}


def cell_own_unreadable_plus_crew(sr, proj):
    """OWN entry whose spine was archived/deleted, AND a crew's in-tree spine
    claimed under sid#agent. `owned` is NON-empty, so rework 2's guard does not
    fire; the loop still leaves spine None; the scan finds exactly one spine --
    the CREW's."""
    own_path = str(proj / ".agent-work" / "run-own" / "spine.json")  # never created
    crew = write_spine(proj, "run-crew", "g3", "CREWMARK", "eng-crew")
    put_binding(sr, proj, {
        SID: {own_path: entry(proj, own_path, "eng-own")},
        SID + "#" + AGENT: {crew: entry(proj, crew, "eng-crew")},
    })
    return {}


def cell_own_unreadable_plus_unclaimed(sr, proj):
    """The shape the rewritten pre-existing test now builds: own entry deleted,
    and the scanned spine is claimed by NOBODY in the binding store (tc1)."""
    own_path = str(proj / ".agent-work" / "run-own" / "spine.json")
    write_spine(proj, "run-alone", "g1", "ALONEMARK", "eng-alone")
    put_binding(sr, proj, {SID: {own_path: entry(proj, own_path, "eng-own")}})
    return {}


def cell_b4_two_spines(sr, proj):
    """B4 topology but TWO in-tree spines: no bind (ambiguous), but pre-fix the
    advisory context still rendered the first match."""
    crew = write_spine(proj, "run-crew", "g3", "CREWMARK", "eng-crew")
    write_spine(proj, "run-other", "g9", "OTHRMARK", "eng-other")
    put_binding(sr, proj, {SID + "#" + AGENT: {crew: entry(proj, crew, "eng-crew")}})
    return {}


def cell_malformed_agent(sr, proj):
    """B4 topology, but the SessionStart payload names an unusable agent_id, so
    binding_key refuses to identify the actor."""
    crew = write_spine(proj, "run-crew", "g3", "CREWMARK", "eng-crew")
    put_binding(sr, proj, {SID + "#" + AGENT: {crew: entry(proj, crew, "eng-crew")}})
    return {"agent_id": "a/b"}


CELLS = [
    ("C1 B4: sees crew's entry, owns none, 1 in-tree spine", cell_b4),
    ("C2 #261: empty view, 1 in-tree spine", cell_261),
    ("C3 owns an UNREADABLE entry + crew's in-tree spine", cell_own_unreadable_plus_crew),
    ("C4 owns an UNREADABLE entry + unclaimed in-tree spine", cell_own_unreadable_plus_unclaimed),
    ("C5 B4 topology, 2 in-tree spines (ambiguous scan)", cell_b4_two_spines),
    ("C6 B4 topology, malformed agent_id in payload", cell_malformed_agent),
]

MARKERS = ["CREWMARK", "SOLOMARK", "ALONEMARK", "OTHRMARK"]


def markers_in(blob):
    return sorted(m for m in MARKERS if m in blob)


def run_cell(sr, builder, restart=True):
    tmp = Path(tempfile.mkdtemp(prefix="g3rev3-"))
    try:
        proj = tmp / "proj"
        (proj / ".agent-work").mkdir(parents=True)
        extra = builder(sr, proj)
        before = json.dumps(sr.load_binding(proj), sort_keys=True)
        payload = {"session_id": SID, "cwd": str(proj)}
        payload.update(extra)
        start = sr.decide_session_start(dict(payload), proj) if restart else {}
        after = sr.load_binding(proj)
        wrote = sorted(
            (k, os.path.basename(os.path.dirname(p)))
            for k, ents in after.items() for p in (ents or {})
            if (k, p) not in {(k2, p2) for k2, e2 in json.loads(before).items() for p2 in (e2 or {})}
        )
        stop = sr.decide_stop(dict(payload), proj)
        return {
            "start_wrote": wrote,
            "start_markers": markers_in(json.dumps(start)),
            "stop_decision": stop.get("decision") or "(allow)",
            "stop_markers": markers_in(json.dumps(stop)),
            "stop_foreign": "foreign-owned" in (stop.get("reason") or ""),
        }
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)


# ---- arm guard ---------------------------------------------------------------
# Refuse to print unless the arms are genuinely different code AND differ on the
# one cell the rework exists to move. This rework ADDS NO SYMBOL, so a symbol
# check would pass with two identical arms loaded.

def guard():
    problems = []
    if WT_HASH != HASHES["HEAD"]:
        problems.append("working tree is NOT byte-identical to HEAD's blob")
    if len({HASHES[n] for n, _ in ARMS}) != len(ARMS):
        problems.append("two arms hashed the same -- not distinct code")
    r1 = run_cell(MODS["REWORK1"], cell_b4)
    hd = run_cell(MODS["HEAD"], cell_b4)
    if not r1["start_wrote"]:
        problems.append("REWORK1 arm did not manufacture the B4 binding -- arm is not pre-fix")
    if hd["start_wrote"]:
        problems.append("HEAD arm still manufactures the B4 binding -- arm is not post-fix")
    if "CREWMARK" not in r1["stop_markers"]:
        problems.append("REWORK1 arm did not leak the crew imperative -- fixture does not reach B4")
    return problems


probs = guard()
print("=" * 78)
print("ARMS: " + ", ".join("{}={} ({})".format(n, r, HASHES[n]) for n, r in ARMS))
print("working tree sha {} == HEAD blob: {}".format(WT_HASH, WT_HASH == HASHES["HEAD"]))
if probs:
    print("GUARD REFUSED:")
    for p in probs:
        print("  - " + p)
    sys.exit(2)
print("GUARD OK: arms distinct by hash AND by behaviour on the B4 cell")
print("=" * 78)

hdr = "{:<52} {:<8} {:<34} {:<12} {:<10} {}".format(
    "cell", "arm", "SessionStart WROTE (key,workdir)", "start ctx", "Stop", "Stop markers")
print(hdr)
print("-" * len(hdr))
for label, builder in CELLS:
    for name, _rev in ARMS:
        r = run_cell(MODS[name], builder)
        print("{:<52} {:<8} {:<34} {:<12} {:<10} {}".format(
            label if name == "PREGATE" else "", name,
            str(r["start_wrote"])[:34] or "-",
            ",".join(r["start_markers"]) or "-",
            r["stop_decision"] + ("/foreign" if r["stop_foreign"] else ""),
            ",".join(r["stop_markers"]) or "-"))
    print("-" * len(hdr))

print()
print("CONTROL: same cells with NO SessionStart (Stop only), HEAD arm")
for label, builder in CELLS:
    r = run_cell(MODS["HEAD"], builder, restart=False)
    print("  {:<52} {:<18} {}".format(label, r["stop_decision"] + ("/foreign" if r["stop_foreign"] else ""),
                                      ",".join(r["stop_markers"]) or "-"))
