"""Differential evidence for #609 lane F g3: the SAME constructed payloads and
binding store run through three hooks side by side -- BEFORE the gate (its base,
999b7663), the BLOCKED intermediate an independent reviewer refused (e3e50a69),
and AFTER the rework (working tree).

Constructed payloads and a constructed binding store, per the handoff: the hook
cannot be validated from inside a session whose CLAUDE_PROJECT_DIR resolved at
launch to the main checkout (#269).

Every arm is PINNED, and every pin is guarded. This harness read `git rev-parse
HEAD` for its BEFORE arm until the g3 reviewer caught it: that was honest only
while HEAD happened to be the base, and the moment the change was committed both
arms loaded the same post-change hook and printed 26 identical rows -- including
the three rows a reviewer is told to spot-check, which came back BEFORE BLOCK /
AFTER BLOCK and read as confirmation. A check that cannot fail is
indistinguishable from one that passed. `_assert_arms_are_what_they_claim` is
what makes this one able to fail: it identifies each arm by symbols the changes
moved rather than by a commit id, so an arm pinned at the wrong revision kills
the run instead of printing agreeable rows.

Run: py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HOOK = "scripts/hooks/spine_rail.py"
# The gate's base: the commit this lane's g3 branched from, PINNED. Never
# `rev-parse HEAD` -- see the module docstring.
BASE_REV = "999b7663"
# The commit an independent reviewer BLOCKED, carried as a third arm so the
# regression it found (SessionStart selecting by claim order) and the repair
# are visible in one table instead of in two runs a reader has to reconcile.
BLOCKED_REV = "e3e50a69"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _assert_arms_are_what_they_claim(sources, mods):
    """Refuse to report a differential whose arms cannot disagree.

    Each arm is identified by symbols the changes moved, not by a commit id a
    reader has to trust: BEFORE still has the tree-as-ownership test that g3
    deleted; BLOCKED has `_is_own_entry` (g3's comparison) but not
    `_own_entries` (the rework's shared selection); AFTER has both. Any arm
    pinned at the wrong revision trips one of these and the harness dies
    instead of printing agreeable rows.
    """
    expected = {
        "BEFORE": {"_foreign_worktree": True, "_is_own_entry": False, "_own_entries": False},
        "BLOCKED": {"_foreign_worktree": False, "_is_own_entry": True, "_own_entries": False},
        "AFTER": {"_foreign_worktree": False, "_is_own_entry": True, "_own_entries": True},
    }
    problems = []
    for arm, wanted in expected.items():
        for symbol, want in wanted.items():
            if hasattr(mods[arm], symbol) is not want:
                problems.append("%s %s %s" % (arm, "lacks" if want else "already has", symbol))
    for a, b in (("BEFORE", "BLOCKED"), ("BLOCKED", "AFTER"), ("BEFORE", "AFTER")):
        if sources[a] == sources[b]:
            problems.append("%s and %s are byte-identical" % (a, b))
    if problems:
        raise SystemExit("REFUSING to print a differential that cannot fail:\n  - "
                         + "\n  - ".join(problems))
    print("  arm pins GUARDED by symbol, not by trust: BEFORE(%s) has _foreign_worktree only,"
          % BASE_REV)
    print("  BLOCKED(%s) has _is_own_entry but no _own_entries, AFTER has both, all three differ."
          % BLOCKED_REV)


def _at(rev):
    src = subprocess.run(["git", "-C", str(REPO), "show", "%s:%s" % (rev, HOOK)],
                         capture_output=True, text=True).stdout
    if not src:
        raise SystemExit("could not read %s:%s -- is %s in this repo?" % (rev, HOOK, rev))
    path = os.path.join(_tmp, "spine_rail_%s.py" % rev)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(src)
    return src, path


_tmp = tempfile.mkdtemp(prefix="g3-differential-")
_before_src, _before_path = _at(BASE_REV)
_blocked_src, _blocked_path = _at(BLOCKED_REV)
_after_src = (REPO / HOOK).read_text(encoding="utf-8")

BEFORE = _load("spine_rail_before", _before_path)
BLOCKED = _load("spine_rail_blocked", _blocked_path)
AFTER = _load("spine_rail_after", str(REPO / HOOK))


# --- fixture builders (same shapes tests/test_spine_rail.py uses) -------------

def make_spine(items_status, lease_status="active", session_id="eng-1", imperatives=None):
    imperatives = imperatives or {}
    return {
        "items": [i for i, _ in items_status],
        "tasks": {i: {"id": i, "status": s, "imperative": imperatives.get(i, "do %s" % i)}
                  for i, s in items_status},
        "engine_session": {"session_id": session_id, "status": lease_status,
                           "claimed_by": "commander",
                           "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    }


def write_spine(root, spine, work="run1", journal_lines=1):
    d = Path(root) / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"
    p.write_text(json.dumps(spine), encoding="utf-8", newline="\n")
    if journal_lines:
        (d / "spine.json.journal").write_text(
            "".join('{"seq": %d}\n' % i for i in range(journal_lines)),
            encoding="utf-8", newline="\n")
    return str(p)


def entry(spine_path, worktree, engine_session="eng-1"):
    return {"spine": spine_path, "engine_session": engine_session,
            "worktree": worktree, "claimed_at": "2026-08-16T12:00:00+00:00"}


def render(out, markers):
    """A one-line verdict plus which marker imperative leaked into either
    rendered field -- reason and additionalContext both, since #549's leak was
    through the second one."""
    if not out:
        return "EMPTY -- Stop allowed / no SessionStart context injected"
    if out.get("continue"):
        return "ALLOW (3-strike hatch)"
    if "hookSpecificOutput" in out and out.get("decision") != "block":
        ctx = out["hookSpecificOutput"].get("additionalContext", "")
        got = [m for m in markers if m in ctx]
        return "INJECT %s" % (got or "no marker")
    text = out.get("reason", "") + " || " + out["hookSpecificOutput"]["additionalContext"]
    got = [m for m in markers if m in text]
    kind = "foreign-owner" if "foreign-owned" in out.get("reason", "") else "own-gate"
    named = [w for w in ("run-crew", "run-parent", "run1") if w in text]
    return "BLOCK (%s) about %s, rendering %s" % (kind, named or "?", got or "NOTHING")


def scenario(label, build, call, markers):
    rows = []
    for name, mod in (("BEFORE", BEFORE), ("BLOCKED", BLOCKED), ("AFTER", AFTER)):
        proj = Path(tempfile.mkdtemp(prefix="g3-%s-" % name.lower())).resolve()
        os.environ["CLAUDE_PROJECT_DIR"] = str(proj)
        try:
            payload = build(mod, proj)
            rows.append((name, render(call(mod, proj, payload), markers)))
        finally:
            shutil.rmtree(str(proj), ignore_errors=True)
    print("\n%s" % label)
    for name, verdict in rows:
        print("  %-7s %s" % (name, verdict))
    return rows


STOP = lambda mod, proj, payload: mod.decide_stop(payload, proj)
START = lambda mod, proj, payload: mod.decide_session_start(payload, proj)

SID = "harness-session"
CREW_AGENT = "a8f0a946eaaa2fe6c"
CREW_KEY = SID + "#" + CREW_AGENT


def one_tree(mod, proj):
    """A Commander and an IN-TREE crew: one worktree, two spines, two binding
    keys. The crew's key is written first, so its entry leads the merged view."""
    crew = write_spine(proj, make_spine([("g3", "in-progress")],
                                        imperatives={"g3": "CREW-MARKER"}), work="run-crew")
    parent = write_spine(proj, make_spine([("execute", "in-progress")],
                                          imperatives={"execute": "PARENT-MARKER"}), work="run-parent")
    mod.save_binding(proj, {CREW_KEY: {crew: entry(crew, str(proj))},
                            SID: {parent: entry(parent, str(proj))}})


MARKERS = ("PARENT-MARKER", "CREW-MARKER", "OWN-MARKER", "RESUME-MARKER",
           "FAILSAFE-MARKER", "PLATFORM-MARKER")

print("=" * 78)
print("#609 lane F g3 -- BEFORE (%s) vs BLOCKED (%s) vs AFTER (working tree)"
      % (BASE_REV, BLOCKED_REV))
print("=" * 78)
_assert_arms_are_what_they_claim(
    {"BEFORE": _before_src, "BLOCKED": _blocked_src, "AFTER": _after_src},
    {"BEFORE": BEFORE, "BLOCKED": BLOCKED, "AFTER": AFTER})

print("\n--- (1) the #549 shape, and (2) call site 1: mid-flight Stop blocking ---")

scenario(
    "S1  parent + IN-TREE crew, ONE worktree, the PARENT stops",
    lambda mod, proj: (one_tree(mod, proj), {"session_id": SID, "cwd": str(proj)})[1],
    STOP, MARKERS)

scenario(
    "S2  same, the CREW stops (payload carries its agent_id)",
    lambda mod, proj: (one_tree(mod, proj),
                       {"session_id": SID, "agent_id": CREW_AGENT, "cwd": str(proj)})[1],
    STOP, MARKERS)


def own_elsewhere(mod, proj):
    other = proj / "otherwt"
    sp = write_spine(other, make_spine([("g1", "in-progress")],
                                       imperatives={"g1": "OWN-MARKER"}))
    mod.save_binding(proj, {"s1": {sp: entry(sp, str(other))}})


scenario(
    "S3  this agent's OWN claim, recorded in another worktree, it stops",
    lambda mod, proj: (own_elsewhere(mod, proj), {"session_id": "s1", "cwd": str(proj)})[1],
    STOP, MARKERS)


def crew_elsewhere(mod, proj):
    crew_tree = proj / "crewwt"
    sp = write_spine(crew_tree, make_spine([("g3", "in-progress")],
                                           imperatives={"g3": "CREW-MARKER"}), work="run-crew")
    mod.save_binding(proj, {CREW_KEY: {sp: entry(sp, str(crew_tree))}})


scenario(
    "S4  crew in ITS OWN tree, parent stops with no gate of its own",
    lambda mod, proj: (crew_elsewhere(mod, proj), {"session_id": SID, "cwd": str(proj)})[1],
    STOP, MARKERS)

print("\n--- (2) call site 2: which binding entry a resumed session picks up ---")


def bound_elsewhere(mod, proj):
    alt = proj / "altwt"
    sp = write_spine(alt, make_spine([("g2", "in-progress")],
                                     imperatives={"g2": "RESUME-MARKER"}), journal_lines=0)
    mod.save_binding(proj, {"s1": {sp: entry(sp, str(alt))}})


scenario(
    "S5  SessionStart: own binding recorded in another worktree, nothing to scan",
    lambda mod, proj: (bound_elsewhere(mod, proj), {"session_id": "s1", "cwd": str(proj),
                                                    "source": "resume"})[1],
    START, MARKERS)

print("\n--- (4) the fail-safe direction: errored / garbage input ---")


def garbage(worktree):
    def build(mod, proj):
        sp = write_spine(proj, make_spine([("g1", "in-progress")],
                                          imperatives={"g1": "FAILSAFE-MARKER"}))
        mod.save_binding(proj, {"s1": {sp: entry(sp, worktree)}})
    return build


for label, worktree, cwd in (
    ("null worktree", None, "$PROJ"),
    ("int worktree", 12345, "$PROJ"),
    ("empty worktree", "", "$PROJ"),
    ("int cwd", "$PROJ", 12345),
    ("dict cwd", "$PROJ", {"not": "a path"}),
    ("no cwd at all", "$PROJ", None),
):
    def build(mod, proj, _wt=worktree, _cwd=cwd):
        wt = str(proj) if _wt == "$PROJ" else _wt
        garbage(wt)(mod, proj)
        payload = {"session_id": "s1"}
        if _cwd is not None:
            payload["cwd"] = str(proj) if _cwd == "$PROJ" else _cwd
        return payload
    scenario("S6  %-16s -- uncertainty must BLOCK, never relax" % label, build, STOP, MARKERS)


def unidentifiable(mod, proj):
    sp = write_spine(proj, make_spine([("g1", "in-progress")],
                                      imperatives={"g1": "FAILSAFE-MARKER"}))
    mod.save_binding(proj, {"s1": {sp: entry(sp, str(proj))}})


scenario(
    "S7  malformed agent_id ('a/b'): the hook cannot say who is stopping",
    lambda mod, proj: (unidentifiable(mod, proj),
                       {"session_id": "s1", "agent_id": "a/b", "cwd": str(proj)})[1],
    STOP, MARKERS)

print("\n--- Windows: separators and case folding, constructed not inherited ---")
print("  os.path.normcase folds case+separators only on win32; this host is %s,"
      % sys.platform)
print("  where normcase is the identity function -- so the expectation below is")
print("  CONSTRUCTED: recorded worktree 'C:\\\\Foo\\\\wt' vs cwd 'c:/foo/wt' are the")
print("  same path on Windows and two different paths here. Ownership is now an")
print("  exact binding-key comparison, so the verdict must not depend on that.")
print("  normcase folds these two equal here: %s (expected only on win32)"
      % (os.path.normcase("C:\\Foo\\wt") == os.path.normcase("c:/foo/wt")))


def windows_shape(mod, proj):
    sp = write_spine(proj, make_spine([("g1", "in-progress")],
                                      imperatives={"g1": "PLATFORM-MARKER"}))
    mod.save_binding(proj, {"s1": {sp: entry(sp, "C:\\Foo\\wt")}})


scenario(
    "S8  recorded 'C:\\Foo\\wt', stopping from 'c:/foo/wt'",
    lambda mod, proj: (windows_shape(mod, proj),
                       {"session_id": "s1", "cwd": "c:/foo/wt"})[1],
    STOP, MARKERS)

print("\n--- (5) call site 2 again: SELECTION, the g3 rework (B2) ---")
print("  Every row below places its spines OUTSIDE `<proj>/.agent-work/*/spine.json`,")
print("  so the blind fallback scan finds nothing and only the BINDING can answer.")
print("  These four are the reviewer's cases 2, 6, 3 and 5.")

SELECT_MARKERS = MARKERS + ("AGENT-A-MARKER", "AGENT-B-MARKER")


def parent_and_crew(mod, proj, parent_first=False):
    """Two spines in two trees, one harness session, two binding keys."""
    parent = write_spine(proj / "parentwt", make_spine([("execute", "in-progress")],
                         imperatives={"execute": "PARENT-MARKER"}), work="run-parent")
    crew = write_spine(proj / "crewwt", make_spine([("g3", "in-progress")],
                       imperatives={"g3": "CREW-MARKER"}), work="run-crew")
    keys = [(CREW_KEY, {crew: entry(crew, str(proj / "crewwt"))}),
            (SID, {parent: entry(parent, str(proj / "parentwt"))})]
    if parent_first:
        keys.reverse()
    mod.save_binding(proj, dict(keys))
    assert mod._scan_active_spine(proj) == [], "the scan must find nothing here"


scenario(
    "S9   SessionStart: crew's key written FIRST, the PARENT's session starts",
    lambda mod, proj: (parent_and_crew(mod, proj), {"session_id": SID, "cwd": str(proj),
                                                    "source": "resume"})[1],
    START, SELECT_MARKERS)

scenario(
    "S10  the SAME binding, the PARENT's key written first -- the answer must not move",
    lambda mod, proj: (parent_and_crew(mod, proj, parent_first=True),
                       {"session_id": SID, "cwd": str(proj), "source": "resume"})[1],
    START, SELECT_MARKERS)


def only_a_crews_key(mod, proj):
    crew = write_spine(proj / "crewwt", make_spine([("g3", "in-progress")],
                       imperatives={"g3": "CREW-MARKER"}), work="run-crew")
    mod.save_binding(proj, {CREW_KEY: {crew: entry(crew, str(proj / "crewwt"))}})
    assert mod._scan_active_spine(proj) == [], "the scan must find nothing here"


scenario(
    "S11  only a CREW's per-agent key exists; the parent never claimed anything",
    lambda mod, proj: (only_a_crews_key(mod, proj), {"session_id": SID, "cwd": str(proj),
                                                     "source": "resume"})[1],
    START, SELECT_MARKERS)


def two_crew_agents(mod, proj):
    a = write_spine(proj / "wt-a", make_spine([("g1", "in-progress")],
                    imperatives={"g1": "AGENT-A-MARKER"}), work="run-a")
    b = write_spine(proj / "wt-b", make_spine([("g1", "in-progress")],
                    imperatives={"g1": "AGENT-B-MARKER"}), work="run-b")
    mod.save_binding(proj, {SID + "#agentA": {a: entry(a, str(proj / "wt-a"))},
                            SID + "#agentB": {b: entry(b, str(proj / "wt-b"))}})
    assert mod._scan_active_spine(proj) == [], "the scan must find nothing here"


scenario(
    "S12  two crew agents; the payload NAMES agentB -- whose gate comes back?",
    lambda mod, proj: (two_crew_agents(mod, proj),
                       {"session_id": SID, "agent_id": "agentB", "cwd": str(proj),
                        "source": "resume"})[1],
    START, SELECT_MARKERS)

print("\n--- the import block: stdlib only, and unchanged ---")
before_imports = [l for l in _before_src.splitlines() if l.startswith(("import ", "from "))]
after_imports = [l for l in _after_src.splitlines() if l.startswith(("import ", "from "))]
print("  BEFORE: %s" % before_imports)
print("  AFTER : %s" % after_imports)
print("  identical: %s" % (before_imports == after_imports))

shutil.rmtree(_tmp, ignore_errors=True)
