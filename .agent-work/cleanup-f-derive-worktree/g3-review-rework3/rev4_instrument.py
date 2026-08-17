"""Review 4's OWN instrument. Production writers only, two calls, spine in-tree.

Every binding entry is written by `handle_post_tool_use` from the repo's pinned
REAL probe capture. No hand-built store.

Arms are loaded from git by revision, plus a WORKTREE arm read from the working
tree. A guard asserts the WORKTREE arm is not byte-identical to the newest
pinned arm -- both scratch harnesses on this gate had shelf-life defects in
opposite directions, so every arm prints the sha it actually loaded.

Cases:
  C1  B5's topology, single active spine   -- the case rework 3 claims to fix
  C2  B5's topology, TWO active spines     -- ambiguous scan: no bind by
                                              construction, but what is RENDERED?
  C3  B4's topology (owns nothing visible) -- must stay fixed
  C4  #261 empty view                      -- must still bind
  C5  cross-SESSION claim                  -- a different harness session_id
                                              holds the attribution
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree")
OUT = Path(tempfile.mkdtemp(prefix="g3rev4-"))

PROBE = REPO / "tests/fixtures/probe_payloads.jsonl"
WRAPPERS = [json.loads(l) for l in PROBE.read_text(encoding="utf-8").splitlines() if l.strip()]
PAYLOADS = [w["payload"] for w in WRAPPERS]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
assert PARENT["session_id"] == CREW["session_id"], "one harness session"
SID = PARENT["session_id"]
CREW_KEY = SID + "#" + CREW["agent_id"]

WT_SRC = (REPO / "scripts/hooks/spine_rail.py").read_text(encoding="utf-8")


def _git_show(rev):
    return subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                          cwd=str(REPO), capture_output=True, text=True, check=True).stdout


def _load_src(name, src):
    p = OUT / "arm_{}.py".format(name)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("arm_" + name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ARM_REVS = [("PREGATE", "999b7663"), ("REWORK2", "7d12c29d"), ("WORKTREE", None)]
MODS, SRCS = {}, {}
for name, rev in ARM_REVS:
    src = WT_SRC if rev is None else _git_show(rev)
    SRCS[name] = src
    MODS[name] = _load_src(name, src)
    print("arm {:<9} {:<10} sha256={} bytes={}".format(
        name, rev or "worktree", hashlib.sha256(src.encode()).hexdigest()[:12], len(src)))

# Shelf-life guard: the WORKTREE arm must genuinely differ from every pinned arm,
# and must carry the symbol under test.
for name, rev in ARM_REVS:
    if rev is not None:
        assert SRCS[name] != WT_SRC, "REFUSING: {} is byte-identical to the worktree".format(name)
assert "_attributed_to_another_key" in SRCS["WORKTREE"], "WORKTREE arm lacks the symbol under test"
assert "_attributed_to_another_key" not in SRCS["REWORK2"], "REWORK2 arm already has the fix?!"
print("guard ok: 3 distinct arms, symbol present only in WORKTREE\n")


def spine_dict(gate, marker, eng):
    return {
        "work_id": "w", "type": "gated", "items": [gate],
        "tasks": {gate: {"id": gate, "status": "in-progress", "imperative": marker}},
        "engine_session": {"session_id": eng, "status": "active",
                           "claimed_by": "commander",
                           "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    }


def write_spine(proj, work, gate, marker, eng):
    d = proj / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    (d / "spine.json").write_text(json.dumps(spine_dict(gate, marker, eng)), encoding="utf-8")
    (d / "spine.json.journal").write_text(json.dumps({"seq": 0}) + "\n", encoding="utf-8")
    return str((d / "spine.json").resolve())


def claim_cmd(work, eng, sess=None):
    return ("py scripts/checklist_engine.py --file .agent-work/{}/spine.json "
            "claim --session-id {} --claimed-by commander".format(work, eng))


def post(sr, payload, work, eng, proj):
    data = dict(payload)
    data["tool_input"] = {"command": claim_cmd(work, eng)}
    data["cwd"] = str(proj)
    return sr.handle_post_tool_use(data, proj)


def fresh(tag):
    p = Path(tempfile.mkdtemp(prefix="proj-{}-".format(tag), dir=str(OUT)))
    (p / ".agent-work").mkdir()
    return p


def render(out):
    return json.dumps(out.get("hookSpecificOutput") or {})


# ---------------------------------------------------------------- cases -----

def c1_single(sr, proj):
    """B5: crew claims in-tree spine A; parent claims its own spine B; B is
    archived at closeout; parent restarts. ONE active spine remains (A)."""
    crew_spine = write_spine(proj, "run-crew", "g3", "CREW-MARKER implement the crew gate", "eng-crew")
    write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
    post(sr, CREW, "run-crew", "eng-crew", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    assert list(sr.load_binding(proj)) == [CREW_KEY, SID], sr.load_binding(proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    assert len(sr._scan_active_spine(proj)) == 1
    # the parent DOES own a visible entry (B5's door, not B4's)
    b = sr.load_binding(proj)
    if hasattr(sr, "_own_entries"):  # PREGATE predates the helper; topology is identical
        assert sr._own_entries(list(sr.session_view(b, SID).items()),
                               sr.session_view_provenance(b, SID), SID), "not B5's door"

    start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    b2 = sr.load_binding(proj)
    bound = crew_spine in (b2.get(SID) or {})
    owner_after = sr.session_view_provenance(b2, SID).get(crew_spine)
    leaked = "CREW-MARKER" in render(start)
    parent_stop = sr.decide_stop({"session_id": SID, "cwd": str(proj)}, proj)
    crew_stop = sr.decide_stop({"session_id": SID, "agent_id": CREW["agent_id"],
                                "cwd": str(proj)}, proj)
    return {
        "bound": bound,
        "attribution_after": owner_after,
        "render_leaks_CREW-MARKER": leaked,
        "parent_stop_leaks": "CREW-MARKER" in json.dumps(parent_stop),
        "crew_keeps_own_gate": "CREW-MARKER" in json.dumps(crew_stop.get("reason") or ""),
    }


def c2_two_active(sr, proj):
    """Identical to C1 except the tree holds a SECOND active-leased spine, so
    the scan is ambiguous (len(matches)==2). No bind is possible by
    construction -- the question is what SessionStart RENDERS."""
    write_spine(proj, "run-crew", "g3", "CREW-MARKER implement the crew gate", "eng-crew")
    write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
    write_spine(proj, "run-third", "gX", "THIRD-MARKER unrelated active run", "eng-third")
    post(sr, CREW, "run-crew", "eng-crew", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    matches = sr._scan_active_spine(proj)
    assert len(matches) == 2, len(matches)
    first_marker = json.dumps(matches[0][0])

    start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    b2 = sr.load_binding(proj)
    rendered = render(start)
    return {
        "scan_matches": len(matches),
        "glob_first_is_crew": "CREW-MARKER" in first_marker,
        "bound_anything": bool(set(b2.get(SID) or {}) - set()) and
                          any("run-crew" in p or "run-third" in p for p in (b2.get(SID) or {})),
        "render_nonempty": bool(rendered != "{}"),
        "render_leaks_CREW-MARKER": "CREW-MARKER" in rendered,
        "render_leaks_THIRD-MARKER": "THIRD-MARKER" in rendered,
        "render_says_pick_it_up": "Pick the run back up" in rendered,
    }


def c3_b4(sr, proj):
    """B4: the parent owns NOTHING visible; only the crew's in-tree spine."""
    crew_spine = write_spine(proj, "run-crew", "g3", "CREW-MARKER implement the crew gate", "eng-crew")
    post(sr, CREW, "run-crew", "eng-crew", proj)
    assert list(sr.load_binding(proj)) == [CREW_KEY]
    start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    b2 = sr.load_binding(proj)
    stop = sr.decide_stop({"session_id": SID, "cwd": str(proj)}, proj)
    return {
        "bound": crew_spine in (b2.get(SID) or {}),
        "render_leaks_CREW-MARKER": "CREW-MARKER" in render(start),
        "parent_stop_leaks": "CREW-MARKER" in json.dumps(stop),
    }


def c4_261(sr, proj):
    """#261: nothing claimed under this session at all; one active spine."""
    own = write_spine(proj, "run-solo", "g1", "SOLO-MARKER my own run", "eng-solo")
    assert sr.load_binding(proj) == {}
    start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    b2 = sr.load_binding(proj)
    return {
        "bound": own in (b2.get(SID) or {}),
        "render_has_own_marker": "SOLO-MARKER" in render(start),
    }


def c5_cross_session(sr, proj):
    """The attribution is held by a DIFFERENT harness session_id.

    `owners` at the call site is session_view_provenance(binding, sid) -- the
    ACTING session's view. A claim filed under another session_id is not in it.
    Same damage shape as B5, one door over: does the writer guard see it?
    """
    other_sid = "OTHER-SESSION-0000"
    crew_spine = write_spine(proj, "run-crew", "g3", "CREW-MARKER implement the crew gate", "eng-crew")
    write_spine(proj, "run-own", "execute", "OWN-MARKER drive your own gate", "eng-own")
    other = dict(CREW)
    other["session_id"] = other_sid          # a real captured payload, other session
    post(sr, other, "run-crew", "eng-crew", proj)
    post(sr, PARENT, "run-own", "eng-own", proj)
    keys = list(sr.load_binding(proj))
    shutil.rmtree(str(proj / ".agent-work" / "run-own"))
    assert len(sr._scan_active_spine(proj)) == 1

    start = sr.decide_session_start({"session_id": SID, "cwd": str(proj)}, proj)
    b2 = sr.load_binding(proj)
    stop = sr.decide_stop({"session_id": SID, "cwd": str(proj)}, proj)
    return {
        "binding_keys_before": keys,
        "bound": crew_spine in (b2.get(SID) or {}),
        "render_leaks_CREW-MARKER": "CREW-MARKER" in render(start),
        "parent_stop_claims_it_as_own": "CREW-MARKER" in json.dumps(stop.get("reason") or ""),
    }


CASES = [("C1 B5 single-active", c1_single),
         ("C2 B5 two-active (ambiguous scan)", c2_two_active),
         ("C3 B4 owns-nothing", c3_b4),
         ("C4 #261 empty view", c4_261),
         ("C5 cross-SESSION attribution", c5_cross_session)]

results = {}
for label, fn in CASES:
    print("=" * 78)
    print(label)
    for arm, _rev in ARM_REVS:
        sr = MODS[arm]
        proj = fresh(arm)
        try:
            row = fn(sr, proj)
        except AssertionError as e:
            row = {"FIXTURE-ASSERT": str(e) or repr(e)}
        results[(label, arm)] = row
        print("  {:<9} {}".format(arm, json.dumps(row, sort_keys=True)))
print("=" * 78)
print("scratch:", OUT)
