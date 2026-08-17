"""Reviewer 5's own instrument for g3 rework 4 (B6 render selection).

Design decisions, stated so a later reader can attack them:

* Three arms, each printing the sha256 + byte length of the source it ACTUALLY
  loaded, with a guard asserting the arms differ and that the render loop is
  present only in WORKTREE. Every harness on this gate has had a shelf-life
  defect; the guard is how this one declares its own.
* The differential arm is REWORK3 (`68d190f7`), the commit immediately before
  the fix, not REWORK2 -- so a changed row is attributable to rework 4 alone.
  PREGATE (`999b7663`) is kept to test the "pre-existing" claim.
* Bindings are written by the PRODUCTION writer (`handle_post_tool_use`) from
  the repo's pinned probe capture. Nothing hand-writes the store, except one
  explicitly-labelled constructed case-variant in C7.
* GLOB ORDER IS REMOVED AS A VARIABLE BY MEASURING IT, not by assuming it: the
  scan runs first, and attributions are then applied relative to the order the
  filesystem actually returned.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev5-"))
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
    return m, src


ARMS = [("PREGATE", "999b7663"), ("REWORK3", "68d190f7"), ("WORKTREE", None)]
MODS, SRCS = {}, {}
for _n, _r in ARMS:
    MODS[_n], SRCS[_n] = load(_n, _r)

print("== arms ==")
for n, r in ARMS:
    print("  {:<9} {:<10} sha256={} bytes={}".format(
        n, r or "worktree", hashlib.sha256(SRCS[n].encode()).hexdigest()[:12], len(SRCS[n])))
assert len({hashlib.sha256(s.encode()).hexdigest() for s in SRCS.values()}) == 3, "arms not distinct"
assert RENDER_LOOP in SRCS["WORKTREE"], "worktree arm lacks the render loop"
assert RENDER_LOOP not in SRCS["REWORK3"], "rework3 arm already has the render loop"
assert RENDER_LOOP not in SRCS["PREGATE"]
assert "_attributed_to_another_key" in SRCS["REWORK3"], "rework3 should have the write guard"
assert "_attributed_to_another_key" not in SRCS["PREGATE"]
print("  guard ok: 3 distinct arms; render loop only in WORKTREE; write guard in "
      "REWORK3+WORKTREE only\n")

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
    """Production writer: the PostToolUse hook observing an engine claim."""
    data = dict(payload)
    data["tool_input"] = {"command": ("py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
                                      "claim --session-id %s --claimed-by commander" % (work, eng))}
    data["cwd"] = str(proj)
    return sr.handle_post_tool_use(data, proj)


def newproj(arm, tag):
    proj = Path(tempfile.mkdtemp(prefix="%s-%s-" % (arm, tag), dir=str(OUT)))
    (proj / ".agent-work").mkdir()
    return proj


def markers(rendered):
    return sorted(m for m in ("CREWA", "CREWB", "CREWC", "FREE1", "FREE2", "MINE")
                  if (m + "-MARKER") in rendered)


def observe(sr, proj, binding_before, start):
    after = sr.load_binding(proj)
    rendered = json.dumps(start.get("hookSpecificOutput") or {})
    return {
        "renders": markers(rendered),
        "pick_it_up": "Pick the run back up" in rendered,
        "wrote_binding": bool(set(after.get(SID) or {}) - set(binding_before.get(SID) or {})),
    }


def run(tag, build, arms=("PREGATE", "REWORK3", "WORKTREE")):
    """build(sr, proj) -> dict of facts asserted BEFORE the measurement."""
    print("== %s ==" % tag)
    rows = {}
    for arm in arms:
        sr = MODS[arm]
        proj = newproj(arm, tag.split()[0])
        pre = build(sr, proj)
        binding_before = sr.load_binding(proj)
        start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
        row = observe(sr, proj, binding_before, start)
        rows[arm] = row
        print("  {:<9} {}".format(arm, json.dumps(row, sort_keys=True)))
    print("  setup asserted: %s" % json.dumps(pre, sort_keys=True))
    return rows


# ---------------------------------------------------------------------------
# C1 -- rev4_c2b's topology, on my own arms: 2 matches, BOTH attributed to the
# crew. Whichever the glob returns first is one the view attributes elsewhere.
# ---------------------------------------------------------------------------
def build_c1(sr, proj):
    write_spine(proj, "run-crew-a", "g3", "CREWA-MARKER crew gate one", "eng-a")
    write_spine(proj, "run-crew-b", "g4", "CREWB-MARKER crew gate two", "eng-b")
    write_spine(proj, "run-own", "execute", "MINE-MARKER my own gate", "eng-own")
    post(sr, CREW, "run-crew-a", "eng-a", proj)
    post(sr, CREW, "run-crew-b", "eng-b", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))  # archived at closeout
    owners = sr.session_view_provenance(sr.load_binding(proj), SID)
    matches = sr._scan_active_spine(proj)
    assert len(matches) == 2 and all(owners.get(p) == CREW_KEY for _s, p in matches)
    return {"matches": 2, "all_attributed_to": "crew composite key"}


C1 = run("C1 two matches, both the crew's", build_c1)

# ---------------------------------------------------------------------------
# C2 -- THREE matches: two the crew's, one nobody's. Past the prior instrument.
# ---------------------------------------------------------------------------
def build_c2(sr, proj):
    write_spine(proj, "run-crew-a", "g3", "CREWA-MARKER crew gate one", "eng-a")
    write_spine(proj, "run-crew-b", "g4", "CREWB-MARKER crew gate two", "eng-b")
    write_spine(proj, "run-free", "gX", "FREE1-MARKER claimed by nobody", "eng-free")
    write_spine(proj, "run-own", "execute", "MINE-MARKER my own gate", "eng-own")
    post(sr, CREW, "run-crew-a", "eng-a", proj)
    post(sr, CREW, "run-crew-b", "eng-b", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    owners = sr.session_view_provenance(sr.load_binding(proj), SID)
    matches = sr._scan_active_spine(proj)
    assert len(matches) == 3
    attributed = [p for _s, p in matches if owners.get(p) == CREW_KEY]
    free = [p for _s, p in matches if p not in owners]
    assert len(attributed) == 2 and len(free) == 1
    return {"matches": 3, "crew": 2, "unattributed": 1,
            "glob_leads_with": "crew" if matches[0][1] in attributed else "free"}


C2 = run("C2 three matches, two the crew's + one unclaimed", build_c2)

# ---------------------------------------------------------------------------
# C3 -- THREE matches, ALL the crew's. Nothing left to render.
# ---------------------------------------------------------------------------
def build_c3(sr, proj):
    for w, g, m, e in (("run-crew-a", "g3", "CREWA-MARKER one", "eng-a"),
                       ("run-crew-b", "g4", "CREWB-MARKER two", "eng-b"),
                       ("run-crew-c", "g5", "CREWC-MARKER three", "eng-c")):
        write_spine(proj, w, g, m, e)
        post(sr, CREW, w, e, proj)
    write_spine(proj, "run-own", "execute", "MINE-MARKER my own gate", "eng-own")
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    owners = sr.session_view_provenance(sr.load_binding(proj), SID)
    matches = sr._scan_active_spine(proj)
    assert len(matches) == 3 and all(owners.get(p) == CREW_KEY for _s, p in matches)
    return {"matches": 3, "all_attributed_to": "crew composite key"}


C3 = run("C3 three matches, ALL the crew's", build_c3)

# ---------------------------------------------------------------------------
# C4 -- THE tc1 BOUNDARY. Matches attributed to NOBODY, at n = 1, 2, 3.
# ADMIRAL_RULING-1 R2: an unowned spine path yields today's behaviour, never a
# refusal. Every arm must agree, row for row.
# ---------------------------------------------------------------------------
def make_tc1(n):
    def build(sr, proj):
        for i in range(n):
            write_spine(proj, "run-free-%d" % i, "g%d" % i,
                        ("FREE1-MARKER" if i == 0 else "FREE2-MARKER") + " nobody claimed this",
                        "eng-free-%d" % i)
        write_spine(proj, "run-own", "execute", "MINE-MARKER my own gate", "eng-own")
        post(sr, PARENT, "run-own", "eng-own", proj)
        shutil.rmtree(str(proj / ".agent-work" / "run-own"))
        owners = sr.session_view_provenance(sr.load_binding(proj), SID)
        matches = sr._scan_active_spine(proj)
        assert len(matches) == n
        assert all(p not in owners for _s, p in matches), "tc1 row must be unattributed"
        return {"matches": n, "attributed_to": "NOBODY"}
    return build


C4 = {n: run("C4 tc1 boundary, %d match(es) attributed to NOBODY" % n, make_tc1(n))
      for n in (1, 2, 3)}

# ---------------------------------------------------------------------------
# C5 -- the ACTING session owns one of the matches (its own bare-sid claim),
# reached through an archived own entry so `spine` is still None at the scan.
# ---------------------------------------------------------------------------
def build_c5(sr, proj):
    write_spine(proj, "run-own", "execute", "MINE-MARKER archived", "eng-own")
    post(sr, PARENT, "run-own", "eng-own", proj)          # posted FIRST -> leads sid_bindings
    write_spine(proj, "run-crew-a", "g3", "CREWA-MARKER crew gate one", "eng-a")
    post(sr, CREW, "run-crew-a", "eng-a", proj)
    write_spine(proj, "run-mine", "g9", "MINE-MARKER my own live gate", "eng-mine")
    post(sr, PARENT, "run-mine", "eng-mine", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))  # own entry whose spine no longer loads
    owners = sr.session_view_provenance(sr.load_binding(proj), SID)
    matches = sr._scan_active_spine(proj)
    mine = [p for _s, p in matches if owners.get(p) == SID]
    crew = [p for _s, p in matches if owners.get(p) == CREW_KEY]
    assert len(matches) == 2 and len(mine) == 1 and len(crew) == 1
    return {"matches": 2, "one_is_mine_bare_sid": True,
            "glob_leads_with": "mine" if matches[0][1] in mine else "crew"}


C5 = run("C5 acting session owns one of the matches", build_c5)

# ---------------------------------------------------------------------------
# C6 -- ORDER INDEPENDENCE, measured both ways. The scan runs first; whichever
# candidate the filesystem actually leads with is the one attributed away.
# ---------------------------------------------------------------------------
def make_c6(attribute_leader):
    def build(sr, proj):
        write_spine(proj, "run-x", "g3", "CREWA-MARKER spine x", "eng-x")
        write_spine(proj, "run-y", "g4", "FREE1-MARKER spine y", "eng-y")
        write_spine(proj, "run-own", "execute", "MINE-MARKER my own gate", "eng-own")
        post(sr, PARENT, "run-own", "eng-own", proj)
        order = [p for _s, p in sr._scan_active_spine(proj)]
        assert len(order) == 3
        order = [p for p in order if "run-own" not in p]
        target = order[0] if attribute_leader else order[1]
        work = "run-x" if "run-x" in target else "run-y"
        post(sr, CREW, work, "eng-x" if work == "run-x" else "eng-y", proj)
        shutil.rmtree(str(proj / ".agent-work" / "run-own"))
        owners = sr.session_view_provenance(sr.load_binding(proj), SID)
        matches = sr._scan_active_spine(proj)
        assert len(matches) == 2
        assert owners.get(target) == CREW_KEY
        assert sum(1 for _s, p in matches if p in owners) == 1
        return {"matches": 2, "attributed": "the glob LEADER" if attribute_leader else "the glob TRAILER",
                "attributed_marker": "CREWA" if work == "run-x" else "FREE1",
                "free_marker": "FREE1" if work == "run-x" else "CREWA"}
    return build


C6_LEAD = run("C6a attribute the glob LEADER, expect the trailer rendered", make_c6(True))
C6_TRAIL = run("C6b attribute the glob TRAILER, expect the leader rendered", make_c6(False))

# ---------------------------------------------------------------------------
# C7 -- WINDOWS. `_attributed_to_another_key` routes through `_same_path`, which
# folds case; rework 4 adds a SECOND call site for it. `normcase` is the identity
# on this host, so the case expectation is CONSTRUCTED, both as a direct probe of
# the predicate and end-to-end through the new call site.
# ---------------------------------------------------------------------------
print("== C7 case folding at the new call site ==")
sr = MODS["WORKTREE"]
probe_owners = {"/tmp/P/.agent-work/RUN/spine.json": CREW_KEY}
lower = "/tmp/p/.agent-work/run/spine.json"
real_normcase = os.path.normcase
print("  predicate, linux (measured)     _attributed_to_another_key(UPPER-owned, lower) = %s"
      % sr._attributed_to_another_key(probe_owners, lower, SID))
try:
    os.path.normcase = str.lower
    print("  predicate, win32 (simulated)    _attributed_to_another_key(UPPER-owned, lower) = %s"
          % sr._attributed_to_another_key(probe_owners, lower, SID))
finally:
    os.path.normcase = real_normcase
assert os.path.normcase is real_normcase, "normcase not restored"
print("  normcase restored: %s" % (os.path.normcase is real_normcase))


def build_c7(sr, proj):
    """End-to-end: ONE match, the crew's claim recorded under a case-variant
    spelling of the SAME path. The variant key is CONSTRUCTED -- stated plainly,
    because no production writer can emit it on a case-sensitive host."""
    p = write_spine(proj, "run-crew-a", "g3", "CREWA-MARKER crew gate one", "eng-a")
    post(sr, CREW, "run-crew-a", "eng-a", proj)
    write_spine(proj, "run-own", "execute", "MINE-MARKER my own gate", "eng-own")
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    b = sr.load_binding(proj)
    entries = b[CREW_KEY]
    entry = entries.pop(p)
    variant = p.replace("/run-crew-a/", "/RUN-CREW-A/")
    entries[variant] = entry
    (proj / ".agent-work" / ".spine-rail-binding.json").write_text(json.dumps(b), encoding="utf-8")
    owners = sr.session_view_provenance(sr.load_binding(proj), SID)
    matches = sr._scan_active_spine(proj)
    assert len(matches) == 1 and matches[0][1] == p and p not in owners and variant in owners
    return {"matches": 1, "owned_key_spelling": "UPPER (constructed)", "scan_spelling": "lower"}


print()
C7_LINUX = run("C7a case variant, linux normcase (identity)", build_c7, arms=("WORKTREE",))
try:
    os.path.normcase = str.lower
    C7_WIN = run("C7b case variant, win32 normcase SIMULATED (str.lower)", build_c7, arms=("WORKTREE",))
finally:
    os.path.normcase = real_normcase
assert os.path.normcase is real_normcase, "normcase not restored after C7b"
print("  normcase restored: %s\n" % (os.path.normcase is real_normcase))

# ---------------------------------------------------------------------------
# C8 -- #261. Empty binding store, one active-leased spine: must still bind and
# must render its OWN marker, on every arm.
# ---------------------------------------------------------------------------
def build_c8(sr, proj):
    write_spine(proj, "run-mine", "g9", "MINE-MARKER my own live gate", "eng-mine")
    assert not sr.load_binding(proj), "binding store must start empty for #261"
    assert len(sr._scan_active_spine(proj)) == 1
    return {"matches": 1, "binding_store": "empty"}


C8 = run("C8 #261 empty store, one match", build_c8)

# ---------------------------------------------------------------------------
# verdicts
# ---------------------------------------------------------------------------
print("== verdicts ==")


def same(rows):
    return len({json.dumps(r, sort_keys=True) for r in rows.values()}) == 1


print("  C1 leak on PREGATE/REWORK3, withheld on WORKTREE : %s" % (
    C1["PREGATE"]["renders"] and C1["REWORK3"]["renders"] and not C1["WORKTREE"]["renders"]))
print("  C2 WORKTREE renders the UNCLAIMED spine only      : %s (%s)" % (
    C2["WORKTREE"]["renders"] == ["FREE1"], C2["WORKTREE"]["renders"]))
print("  C3 WORKTREE renders nothing when all are claimed  : %s" % (not C3["WORKTREE"]["renders"]))
for n in (1, 2, 3):
    print("  C4 tc1 n=%d ALL ARMS IDENTICAL (no new refusal)    : %s %s" % (
        n, same(C4[n]), C4[n]["WORKTREE"]["renders"]))
print("  C5 WORKTREE renders the session's OWN spine       : %s (%s)" % (
    C5["WORKTREE"]["renders"] == ["MINE"], C5["WORKTREE"]["renders"]))
print("  C6a leader attributed -> trailer rendered         : %s" % (C6_LEAD["WORKTREE"]["renders"],))
print("  C6b trailer attributed -> leader rendered         : %s" % (C6_TRAIL["WORKTREE"]["renders"],))
print("  C7a linux: renders (different files)              : %s" % (C7_LINUX["WORKTREE"]["renders"],))
print("  C7b win32: withheld (same file)                   : %s" % (C7_WIN["WORKTREE"]["renders"],))
print("  C8 #261 binds and renders own on ALL arms         : %s %s" % (
    same(C8), json.dumps(C8["WORKTREE"], sort_keys=True)))
print("\nscratch: %s" % OUT)
