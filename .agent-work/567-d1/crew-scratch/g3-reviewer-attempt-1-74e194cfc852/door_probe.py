"""g3-review probe: measure the second-checklist refusal the specs' new prose asserts.

Run as a FRESH process with explicit paths (CREW_CONTEXT "Two Engines Are Alive In
Your Session"; ORCHESTRATOR_CONTEXT s.Dogfooding). Never imported by the survey run.

argv[1] is the case name. Each case is one fresh process:
  bound-then-rebind : SPINE_FILE=A, claim A's lease, then spine_bind B  -> expect REFUSED
  released-then-rebind : same, but release A's lease first              -> expect SUCCESS (control)
  unbound-then-bind : no SPINE_FILE at all, spine_status then spine_bind -> expect REFUSED, then SUCCESS
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard")
PROBE = HERE / "door-probe"


def make_spine(work_id: str) -> Path:
    """A minimal real survey spine, instantiated from the project template so the
    door and engine see the shape they actually ship against."""
    PROBE.mkdir(parents=True, exist_ok=True)
    src = REPO / ".agent-work" / "templates" / "REVIEW_SURVEY.template.json"
    payload = json.loads(src.read_text(encoding="utf-8").replace("<work-id>", work_id))
    dest = PROBE / f"{work_id}.json"
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    return dest


def load_door():
    sys.path.insert(0, str(REPO / "scripts"))
    import mcp_spine_server as door
    return door


def call(door, name, args):
    fn = door.call_lifecycle_tool if name in door.LIFECYCLE_TOOL_NAMES else door.call_tool
    res = fn(name, args)
    text = "".join(c.get("text", "") for c in res.get("content", []))
    return res.get("isError", False), text


def show(label, is_error, text):
    print(f"--- {label}")
    print(f"    isError={is_error}")
    for line in text.splitlines() or [""]:
        print(f"    {line}")


def main():
    case = sys.argv[1]
    a = make_spine("567-d1-g3r-probe-a")
    b = make_spine("567-d1-g3r-probe-b")

    if case == "unbound-then-bind":
        for var in ("SPINE_FILE", "SPINE_SESSION"):
            os.environ.pop(var, None)
        door = load_door()
        print(f"env SPINE_FILE={os.environ.get('SPINE_FILE')!r} SPINE_SESSION={os.environ.get('SPINE_SESSION')!r}")
        show("spine_status (nothing bound)", *call(door, "spine_status", {}))
        show("spine_bind B", *call(door, "spine_bind", {"spine_file": str(b)}))
        show("spine_lease claim on B", *call(door, "spine_lease", {"action": "claim", "claimed_by": "probe"}))
        show("spine_status on B", *call(door, "spine_status", {}))
        show("spine_lease release on B", *call(door, "spine_lease", {"action": "release"}))
        return

    # Both remaining cases start BOUND to A, exactly as a crew dispatched with a
    # spine of its own does: SPINE_FILE/SPINE_SESSION in the environment at start.
    import importlib
    sys.path.insert(0, str(REPO / "scripts"))
    import spine_lifecycle
    session_a = spine_lifecycle.session_id_for("567-d1-g3r-probe-a")
    os.environ["SPINE_FILE"] = str(a)
    os.environ["SPINE_SESSION"] = session_a
    door = importlib.import_module("mcp_spine_server")
    print(f"env SPINE_FILE={os.environ['SPINE_FILE']!r} SPINE_SESSION={os.environ['SPINE_SESSION']!r}")
    print(f"door SPINE={str(door.SPINE)!r} SESSION={door.SESSION!r}")

    show("spine_lease claim on A", *call(door, "spine_lease", {"action": "claim", "claimed_by": "probe"}))

    if case == "bound-then-rebind":
        show("spine_bind B  <-- the second checklist, lease HELD", *call(door, "spine_bind", {"spine_file": str(b)}))
        show("spine_status (still A?)", *call(door, "spine_status", {}))
        show("spine_lease release on A (cleanup)", *call(door, "spine_lease", {"action": "release"}))
        return

    if case == "released-then-rebind":
        show("spine_lease release on A", *call(door, "spine_lease", {"action": "release"}))
        show("spine_bind B  <-- same call, lease RELEASED", *call(door, "spine_bind", {"spine_file": str(b)}))
        show("spine_status (now B?)", *call(door, "spine_status", {}))
        return

    raise SystemExit(f"unknown case {case!r}")


main()
