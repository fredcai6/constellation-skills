"""Both doors into the bind-on-resume writer, measured through production
writers only, on three arms.

Copied in construction from the reviewer's `g3-review-rework2/
rev3_production_sequence.py` (committed evidence -- copied, not edited) and
changed in two ways that matter:

  * the AFTER arm is the WORKING TREE, not a pinned sha. Three pins have now
    rotted on this lane -- one to a moving HEAD, one to a superseded commit,
    one to a commit that was amended out from under the handoff citing it. The
    two BEFORE arms are still pinned, because they name states that must not
    move; each is asserted to still hash to what it was extracted as, and the
    BEFORE-2 arm is asserted byte-identical to `git show HEAD:` so "the arm I
    am comparing against" cannot silently drift from "the committed code".
  * it measures BOTH doors in one run: B4 (the parent owns nothing visible)
    and B5 (the parent owns an entry whose spine no longer loads).

Guard, behavioural rather than symbolic: this rework DOES add a symbol, but a
symbol check would still pass on a tree where the symbol exists and is never
called. So the harness refuses to print unless the arms differ by hash AND
BEFORE-2 actually leaks the B5 cell while AFTER does not.

Every binding entry below is written by `handle_post_tool_use` from the repo's
own pinned probe capture. Nothing here builds a binding store by hand.
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
OUT = Path(tempfile.mkdtemp(prefix="g3rw3-arms-"))
HOOK = REPO / "scripts/hooks/spine_rail.py"

PROBE = REPO / "tests/fixtures/probe_payloads.jsonl"
PAYLOADS = [json.loads(l)["payload"] for l in PROBE.read_text(encoding="utf-8").splitlines() if l.strip()]
PARENT = [p for p in PAYLOADS if "agent_id" not in p][0]
CREW = [p for p in PAYLOADS if "agent_id" in p][0]
assert PARENT["session_id"] == CREW["session_id"], "one harness session"
SID = PARENT["session_id"]
CREW_KEY = SID + "#" + CREW["agent_id"]


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _import(name, src):
    p = OUT / "arm_{}.py".format(name)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("arm_" + name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, _sha(src)


def _at_rev(rev):
    return subprocess.run(["git", "show", "{}:scripts/hooks/spine_rail.py".format(rev)],
                          cwd=str(REPO), capture_output=True, text=True, check=True).stdout


PINNED = [("PREGATE", "999b7663"), ("BEFORE-2", "HEAD")]
ARMS, SHAS = {}, {}
for name, rev in PINNED:
    ARMS[name], SHAS[name] = _import(name, _at_rev(rev))
ARMS["AFTER"], SHAS["AFTER"] = _import("AFTER", HOOK.read_text(encoding="utf-8"))

# The properties that make each pin the right one, asserted rather than trusted.
assert SHAS["PREGATE"] == _sha(_at_rev("999b7663")), "PREGATE arm is not what 999b7663 holds"
assert SHAS["BEFORE-2"] == _sha(_at_rev("HEAD")), "BEFORE-2 arm is not the committed hook"
assert len({SHAS["PREGATE"], SHAS["BEFORE-2"], SHAS["AFTER"]}) == 3, \
    "arms do not differ: this harness would be comparing a tree with itself"


def spine_json(gate, marker, eng):
    return json.dumps({
        "work_id": "w", "type": "gated", "items": [gate],
        "tasks": {gate: {"id": gate, "status": "in-progress", "imperative": marker}},
        "engine_session": {"session_id": eng, "status": "active",
                           "claimed_by": "commander",
                           "last_heartbeat": "2026-08-16T00:00:00+00:00"},
    })


def put(proj, work, gate, marker, eng):
    d = proj / ".agent-work" / work
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spine.json"
    p.write_text(spine_json(gate, marker, eng), encoding="utf-8")
    (d / "spine.json.journal").write_text('{"seq": 0}\n', encoding="utf-8")
    return p


def claim_cmd(work, eng):
    return ("py scripts/checklist_engine.py --file .agent-work/%s/spine.json "
            "claim --session-id %s --claimed-by commander" % (work, eng))


def post(payload, command, cwd):
    d = dict(payload)
    d["tool_input"] = {"command": command}
    d["cwd"] = str(cwd)
    return d


def cell(sr, door, restart=True):
    """door 'B4': the parent owns nothing visible.
       door 'B5': the parent owns its own spine, which is then archived away.
       door '261': nothing is claimed at all -- the path that must NOT break."""
    tmp = Path(tempfile.mkdtemp(prefix="cell-"))
    try:
        proj = tmp / "proj"
        (proj / ".agent-work").mkdir(parents=True)
        crew_spine = str(put(proj, "run-crew", "g3", "CREWMARK implement the crew gate",
                             "eng-crew").resolve())
        if door == "261":
            solo = str(put(proj, "run-solo", "g1", "SOLOMARK keep going", "eng-solo").resolve())
            shutil.rmtree(str(proj / ".agent-work" / "run-crew"))
            sid = "s-resumed"
        else:
            sid = SID
            sr.handle_post_tool_use(post(CREW, claim_cmd("run-crew", "eng-crew"), proj), proj)
            if door == "B5":
                b = put(proj, "run-own", "g1", "OWNMARK drive your own gate", "eng-own")
                sr.handle_post_tool_use(post(PARENT, claim_cmd("run-own", "eng-own"), proj), proj)
                b.unlink()
                shutil.rmtree(str(proj / ".agent-work" / "run-own"))

        pay = {"session_id": sid, "cwd": str(proj)}
        start = sr.decide_session_start(dict(pay), proj) if restart else {}
        binding = sr.load_binding(proj)
        own = binding.get(sid) or {}
        stop = sr.decide_stop(dict(pay), proj)
        row = {
            "bound to another agent's spine": crew_spine in own,
            "provenance(crew spine)": sr.session_view_provenance(binding, sid).get(crew_spine),
            "SessionStart handed it CREWMARK": "CREWMARK" in json.dumps(start),
            "its Stop": (stop.get("reason") or "(allow)")[:40],
            "its Stop handed it CREWMARK": "CREWMARK" in json.dumps(stop),
        }
        if door == "261":
            row = {
                "bound to the one unclaimed spine": solo in own,
                "SessionStart handed it SOLOMARK": "SOLOMARK" in json.dumps(start),
                "the next Stop reads that write as OWN": "SOLOMARK" in json.dumps(stop),
            }
        else:
            crew_stop = sr.decide_stop({"session_id": sid, "agent_id": CREW["agent_id"],
                                        "cwd": str(proj)}, proj)
            row["the CREW still sees its own gate"] = "CREWMARK" in json.dumps(crew_stop)
        return row
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)


# Behavioural guard: BEFORE-2 must really leak B5 and AFTER must really not,
# or these rows are being read off two trees that do the same thing.
assert cell(ARMS["BEFORE-2"], "B5")["bound to another agent's spine"] is True, \
    "BEFORE-2 does not leak B5: the arm is not the committed pre-fix code"
assert cell(ARMS["AFTER"], "B5")["bound to another agent's spine"] is False, \
    "AFTER still leaks B5: the working tree does not carry the fix"

print("probe capture:", PROBE.name, "| sid:", SID, "| crew key:", CREW_KEY)
print("arm hashes:", {k: SHAS[k] for k in ("PREGATE", "BEFORE-2", "AFTER")})
print("=" * 78)
for door in ("B4", "B5", "261"):
    print("\n### door {} ###".format(door))
    for name in ("PREGATE", "BEFORE-2", "AFTER"):
        print("  {:<9}".format(name))
        for k, v in cell(ARMS[name], door).items():
            print("      {:<40} {}".format(k, v))
    print("  {:<9} (no SessionStart)".format("AFTER"))
    for k, v in cell(ARMS["AFTER"], door, restart=False).items():
        print("      {:<40} {}".format(k, v))
