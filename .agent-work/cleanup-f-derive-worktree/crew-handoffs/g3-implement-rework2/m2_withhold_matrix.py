"""What newly withholds at `decide_session_start`, derived by command rather
than by memory (#609 lane F g3, rework 2 / B4).

The blocker this answers is a property of TWO calls and of the ONE mutable
store the two hook sites share, so a single-call differential cannot see it.
Every cell below is therefore a SEQUENCE -- a SessionStart, then a Stop -- and
every cell reports both halves: what the first call WROTE to the binding store,
and what the second call RENDERED. It also places its spines INSIDE
`<project>/.agent-work/*/spine.json`, where the fallback scan can actually
reach them; every earlier instrument on this gate placed them outside it, which
is why every earlier instrument was blind to this.

Three arms, all pinned, none trusted:

  BEFORE   999b7663  the gate's base -- selection by claim order
  REWORK1  6bba3fd2  ownership-based selection, the pass that was BLOCKED on B4
  AFTER              the working tree

Constructed payloads and a constructed binding store, per the handoff: the hook
cannot be validated from inside a session whose CLAUDE_PROJECT_DIR resolved at
launch to the main checkout (#269).

Run: py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement-rework2/m2_withhold_matrix.py
"""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HOOK = "scripts/hooks/spine_rail.py"
BASE_REV = "999b7663"    # before the gate
REWORK1_REV = "6bba3fd2"  # the BLOCKED pass this rework amends

SID = "parent-sid"
CREW_AID = "crewagent1234"
CREW_KEY = SID + "#" + CREW_AID

_tmp = tempfile.mkdtemp(prefix="g3-withhold-matrix-")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _at(rev):
    src = subprocess.run(["git", "-C", str(REPO), "show", "%s:%s" % (rev, HOOK)],
                         capture_output=True, text=True).stdout
    if not src:
        raise SystemExit("could not read %s:%s" % (rev, HOOK))
    path = os.path.join(_tmp, "spine_rail_%s.py" % rev)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(src)
    return src, path


_before_src, _before_path = _at(BASE_REV)
_rework1_src, _rework1_path = _at(REWORK1_REV)
_after_src = (REPO / HOOK).read_text(encoding="utf-8")

ARMS = [
    ("BEFORE", _load("sr_before", _before_path)),
    ("REWORK1", _load("sr_rework1", _rework1_path)),
    ("AFTER", _load("sr_after", str(REPO / HOOK))),
]
MODS = dict(ARMS)


# --- fixtures ----------------------------------------------------------------

def make_spine(gate, imperative, engine="eng-x"):
    return {
        "items": [gate],
        "tasks": {gate: {"id": gate, "status": "in-progress", "imperative": imperative}},
        "engine_session": {"session_id": engine, "status": "active", "claimed_by": "crew",
                           "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    }


def write_spine(root, spine, work):
    d = Path(root) / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"
    p.write_text(json.dumps(spine), encoding="utf-8")
    (d / "spine.json.journal").write_text('{"seq": 0}\n', encoding="utf-8")
    return str(p)


def entry(sr, path, worktree, engine="eng-x"):
    return {"spine": path, "engine_session": engine, "worktree": worktree,
            "claimed_at": sr._now_iso()}


# --- the cells ---------------------------------------------------------------
#
# Each builds a fresh project dir and returns (binding, payload). `scan` names
# how many active-leased spines sit inside the glob.

def cell_261_empty_view_one_spine(sr, proj):
    """#261: a resumed/compacted session that never itself ran `claim`."""
    write_spine(proj, make_spine("g1", "SCAN-MARKER keep going"), "run-solo")
    return {}, {"session_id": SID, "cwd": str(proj)}


def cell_empty_view_no_spine(sr, proj):
    return {}, {"session_id": SID, "cwd": str(proj)}


def cell_empty_view_two_spines(sr, proj):
    """Ambiguous scan: context, never a binding (decision:no-bind-on-ambiguous-scan)."""
    write_spine(proj, make_spine("g1", "SCAN-MARKER a"), "run-a")
    write_spine(proj, make_spine("g2", "SCAN-MARKER b"), "run-b")
    return {}, {"session_id": SID, "cwd": str(proj)}


def cell_b4_crew_only_in_tree(sr, proj):
    """B4. The parent sees its in-tree crew's entry and owns nothing."""
    sp = write_spine(proj, make_spine("g3", "CREW-MARKER implement the crew gate"), "run-crew")
    return {CREW_KEY: {sp: entry(sr, sp, str(proj))}}, {"session_id": SID, "cwd": str(proj)}


def cell_crew_only_out_of_tree(sr, proj):
    """The same ownership shape with nothing for the scan to find."""
    sp = write_spine(proj / "crewwt", make_spine("g3", "CREW-MARKER the crew gate"), "run-crew")
    return {CREW_KEY: {sp: entry(sr, sp, str(proj / "crewwt"))}}, {"session_id": SID,
                                                                   "cwd": str(proj)}


def cell_owns_a_readable_entry(sr, proj):
    """Owns one, sees the crew's too. Answered from its own binding, no rebind."""
    crew = write_spine(proj, make_spine("g3", "CREW-MARKER the crew gate"), "run-crew")
    own = write_spine(proj / "ownwt", make_spine("execute", "PARENT-MARKER drive execute"),
                      "run-parent")
    return ({CREW_KEY: {crew: entry(sr, crew, str(proj))},
             SID: {own: entry(sr, own, str(proj / "ownwt"))}},
            {"session_id": SID, "cwd": str(proj)})


def cell_owns_an_unreadable_entry(sr, proj):
    """Owns one whose spine was deleted or archived out from under it (#202)."""
    write_spine(proj, make_spine("g1", "SCAN-MARKER keep going"), "run-solo")
    gone = str(proj / "ownwt" / ".agent-work" / "run-gone" / "spine.json")
    return {SID: {gone: entry(sr, gone, str(proj / "ownwt"))}}, {"session_id": SID,
                                                                 "cwd": str(proj)}


def cell_unidentifiable_agent(sr, proj):
    """`binding_key` refuses a malformed agent_id (#441), so nothing is OWN."""
    sp = write_spine(proj, make_spine("g3", "CREW-MARKER the crew gate"), "run-crew")
    return ({CREW_KEY: {sp: entry(sr, sp, str(proj))}},
            {"session_id": SID, "agent_id": "a/b", "cwd": str(proj)})


def cell_tc5_path_collision(sr, proj):
    """tc5: the parent and its subagent both bind the SAME path, and provenance
    is last-key-wins, so the parent stops owning an entry it did claim."""
    sp = write_spine(proj, make_spine("g3", "CREW-MARKER the crew gate"), "run-crew")
    return ({SID: {sp: entry(sr, sp, str(proj))},
             CREW_KEY: {sp: entry(sr, sp, str(proj))}},  # written last -> wins
            {"session_id": SID, "cwd": str(proj)})


def cell_crew_only_two_spines(sr, proj):
    """Owns nothing AND the scan is ambiguous -- no bind on any arm."""
    sp = write_spine(proj, make_spine("g3", "CREW-MARKER the crew gate"), "run-crew")
    write_spine(proj, make_spine("g4", "SCAN-MARKER other"), "run-other")
    return {CREW_KEY: {sp: entry(sr, sp, str(proj))}}, {"session_id": SID, "cwd": str(proj)}


CELLS = [
    ("empty view, 1 in-tree spine (#261)", cell_261_empty_view_one_spine),
    ("empty view, no spine", cell_empty_view_no_spine),
    ("empty view, 2 in-tree spines", cell_empty_view_two_spines),
    ("sees crew only, 1 in-tree spine (B4)", cell_b4_crew_only_in_tree),
    ("sees crew only, nothing to scan", cell_crew_only_out_of_tree),
    ("sees crew only, 2 in-tree spines", cell_crew_only_two_spines),
    ("owns a readable entry", cell_owns_a_readable_entry),
    ("owns an UNREADABLE entry, 1 spine", cell_owns_an_unreadable_entry),
    ("unidentifiable agent (#441)", cell_unidentifiable_agent),
    ("tc5 path collision", cell_tc5_path_collision),
]


def _pairs(binding):
    """Every (binding key, abs spine path) the store holds."""
    return {(k, p) for k, entries in (binding or {}).items()
            for p in (entries or {}) if isinstance(entries, dict)}


def run(sr, build):
    """One SessionStart then one Stop, reporting both halves."""
    proj = Path(tempfile.mkdtemp(prefix="cell-")).resolve()
    prior = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = str(proj)
    try:
        binding, payload = build(sr, proj)
        sr.save_binding(proj, binding)
        # (key, path) PAIRS, not keys: the bind-on-resume write merges onto an
        # existing `sid` key, so counting keys alone reports "-" for a session
        # that already holds one -- which is precisely the tc5 and
        # unreadable-entry rows, i.e. the ones worth seeing.
        before = _pairs(sr.load_binding(proj))
        start = sr.decide_session_start(payload, proj) or {}
        wrote = sorted(_pairs(sr.load_binding(proj)) - before)
        stop = sr.decide_stop(payload, proj) or {}
        blob = json.dumps(start)
        return {
            "bound": ("+" + ",".join(k for k, _p in wrote)) if wrote else "-",
            "start": ("CREW" if "CREW-MARKER" in blob else
                      "SCAN" if "SCAN-MARKER" in blob else
                      "PARENT" if "PARENT-MARKER" in blob else "-"),
            "stop": ("own-gate:CREW" if "CREW-MARKER" in json.dumps(stop) else
                     "own-gate:SCAN" if "SCAN-MARKER" in json.dumps(stop) else
                     "own-gate:PARENT" if "PARENT-MARKER" in json.dumps(stop) else
                     "foreign-owner" if stop.get("decision") == "block" else "-"),
        }
    finally:
        if prior is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prior
        shutil.rmtree(str(proj), True)


def guard(results):
    """Refuse to print a differential whose arms cannot disagree.

    Two independent identifications, because neither alone is enough here.
    By SYMBOL: BEFORE still has the tree-as-ownership test g3 deleted, and
    REWORK1 has `_own_entries` (the rework's shared selection) which BEFORE
    does not. That separates BEFORE from the other two but NOT REWORK1 from
    AFTER -- this rework adds no symbol, so a symbol check alone would pass
    with both arms loaded from the same file.

    So REWORK1 and AFTER are separated by BEHAVIOUR, on the one cell whose
    answer this change exists to move: REWORK1 MUST manufacture a bare-`sid`
    binding on the B4 cell and AFTER must not. An arm pinned at the wrong
    revision fails that and kills the run instead of printing agreeable rows.
    """
    problems = []
    for arm, want in (("BEFORE", {"_foreign_worktree": True, "_own_entries": False}),
                      ("REWORK1", {"_foreign_worktree": False, "_own_entries": True}),
                      ("AFTER", {"_foreign_worktree": False, "_own_entries": True})):
        for symbol, present in want.items():
            if hasattr(MODS[arm], symbol) is not present:
                problems.append("%s %s %s" % (arm, "lacks" if present else "already has", symbol))
    for a, b, src_a, src_b in (("BEFORE", "REWORK1", _before_src, _rework1_src),
                               ("REWORK1", "AFTER", _rework1_src, _after_src),
                               ("BEFORE", "AFTER", _before_src, _after_src)):
        if src_a == src_b:
            problems.append("%s and %s are byte-identical" % (a, b))
    b4 = "sees crew only, 1 in-tree spine (B4)"
    if results["REWORK1"][b4]["bound"] != "+" + SID:
        problems.append("REWORK1 does not manufacture the B4 binding -- wrong revision pinned")
    if results["AFTER"][b4]["bound"] != "-":
        problems.append("AFTER still manufactures the B4 binding -- the fix is not in this tree")
    if problems:
        raise SystemExit("REFUSING to print a differential that cannot fail:\n  - "
                         + "\n  - ".join(problems))
    print("  arms GUARDED: BEFORE(%s) has _foreign_worktree and no _own_entries; REWORK1(%s)"
          % (BASE_REV, REWORK1_REV))
    print("  and AFTER both have _own_entries and differ byte-wise, and are separated by")
    print("  BEHAVIOUR on the B4 cell -- REWORK1 binds there, AFTER does not.")


def main():
    results = {arm: {label: run(sr, build) for label, build in CELLS} for arm, sr in ARMS}
    guard(results)
    print()
    print("Each cell is a SessionStart followed by a Stop, sharing one binding store.")
    print("bound = binding keys the SessionStart WROTE; start/stop = whose marker rendered.")
    print()
    head = "%-38s | %-28s | %-28s | %-28s" % ("cell", "BEFORE " + BASE_REV,
                                              "REWORK1 " + REWORK1_REV, "AFTER (working tree)")
    print(head)
    print("-" * len(head))
    moved = 0
    for label, _ in CELLS:
        cols = []
        for arm, _sr in ARMS:
            r = results[arm][label]
            cols.append("%-8s %-6s %s" % (r["bound"], r["start"], r["stop"]))
        if results["REWORK1"][label] != results["AFTER"][label]:
            moved += 1
            label = "* " + label
        print("%-38s | %-28s | %-28s | %-28s" % (label, cols[0], cols[1], cols[2]))
    print()
    print("%d cells, %d moved by this rework (marked *)." % (len(CELLS), moved))
    print("A cell that did NOT move is evidence too: rework 1's approved answers are unchanged.")


if __name__ == "__main__":
    main()
