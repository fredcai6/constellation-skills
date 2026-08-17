"""g3-implement rework probe: re-measure the refusal the specs' prose quotes.

Run as FRESH processes with explicit paths (CREW_CONTEXT "Two Engines Are Alive In
Your Session"): the door resolves SPINE_FILE at import, so each case must be its own
process. Called with no argv this file is the ORCHESTRATOR: it runs each case as a
subprocess of itself and asserts the expected outcome, exiting non-zero on any miss.

Cases, and the prose sentence each one measures:

  bound-then-rebind     "with your own lease held, binding a second checklist is
                        REFUSED -- 'one door drives one spine at a time ... release
                        it first'" -> expect REFUSED, fragment verbatim.
  released-then-rebind  positive control: the SAME bind after releasing the lease
                        -> expect SUCCESS, so the refusal is conditioned on holding
                        your own lease and nothing else.
  unbound-then-bind     "Dispatched without a spine of your own you arrive holding no
                        lease" and "an unbound door binds one spine and then drives
                        it identically -- the identity comes from that spine's own
                        work id" -> expect status REFUSED, bind SUCCESS, and the
                        returned SPINE_SESSION equal to session_id_for(work_id).
"""
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard")
PROBE = HERE / "door-probe"
CASES = ("bound-then-rebind", "released-then-rebind", "unbound-then-bind")
SPECS = ("specs/implementer.spine.toml", "specs/reviewer.spine.toml")


def quoted_halves(spec_path: str) -> tuple[str, list[str]]:
    """The fragment THAT SPEC quotes, read out of the spec itself rather than
    restated here -- so this check measures the shipped text, and drifts with it,
    instead of measuring a copy the probe author typed. The spec elides the middle
    of the refusal with '...', so each half is checked against the live refusal on
    its own."""
    spec = tomllib.loads((REPO / spec_path).read_text(encoding="utf-8"))
    imperative = spec["gate"][0]["imperative"]
    quotes = [q for q in re.findall(r'"([^"]+)"', imperative)
              if "one door drives one spine" in q]
    if len(quotes) != 1:
        raise SystemExit(f"{spec_path}: expected exactly one quoted refusal fragment, got {quotes!r}")
    return quotes[0], [half.strip() for half in quotes[0].split("...")]


def make_spine(work_id: str) -> Path:
    PROBE.mkdir(parents=True, exist_ok=True)
    src = REPO / ".agent-work" / "templates" / "IMPLEMENTER_PLAN.template.json"
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
    return bool(res.get("isError", False)), text


def emit(label, is_error, text):
    """One machine-readable line per call, so the orchestrator asserts on outcomes
    rather than on prose it wrote itself."""
    print("RESULT " + json.dumps({"label": label, "isError": is_error, "text": text}))


def run_case(case: str) -> None:
    a = make_spine("567-d1-g3i2-probe-a")
    b = make_spine("567-d1-g3i2-probe-b")

    if case == "unbound-then-bind":
        for var in ("SPINE_FILE", "SPINE_SESSION"):
            os.environ.pop(var, None)
        door = load_door()
        emit("status-unbound", *call(door, "spine_status", {}))
        emit("bind-b", *call(door, "spine_bind", {"spine_file": str(b)}))
        emit("claim-b", *call(door, "spine_lease", {"action": "claim", "claimed_by": "probe"}))
        emit("release-b", *call(door, "spine_lease", {"action": "release"}))
        return

    # Both remaining cases start BOUND to A with A's lease held -- exactly the state
    # of a crew dispatched WITH a spine of its own.
    sys.path.insert(0, str(REPO / "scripts"))
    import spine_lifecycle
    os.environ["SPINE_FILE"] = str(a)
    os.environ["SPINE_SESSION"] = spine_lifecycle.session_id_for("567-d1-g3i2-probe-a")
    door = load_door()
    emit("claim-a", *call(door, "spine_lease", {"action": "claim", "claimed_by": "probe"}))
    if case == "released-then-rebind":
        emit("release-a", *call(door, "spine_lease", {"action": "release"}))
    emit("bind-b", *call(door, "spine_bind", {"spine_file": str(b)}))
    emit("status-after", *call(door, "spine_status", {}))


def collect(case: str) -> dict[str, dict]:
    proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), case],
                          capture_output=True, text=True, cwd=str(REPO))
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"probe case {case} crashed (rc={proc.returncode})")
    out = {}
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            rec = json.loads(line[len("RESULT "):])
            out[rec["label"]] = rec
    return out


def main() -> int:
    if len(sys.argv) > 1:
        run_case(sys.argv[1])
        return 0

    # Each case is a genuinely separate process.
    got = {case: collect(case) for case in CASES}
    failures: list[str] = []
    checked = 0

    def check(cond: bool, label: str) -> None:
        nonlocal checked
        checked += 1
        print(f"{'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            failures.append(label)

    bound = got["bound-then-rebind"]
    check(bound["claim-a"]["isError"] is False, "bound: lease on A claims")
    check(bound["bind-b"]["isError"] is True,
          "bound+lease held: binding a second checklist is REFUSED")
    refusal = bound["bind-b"]["text"]
    for spec_path in SPECS:
        whole, halves = quoted_halves(spec_path)
        check(len(halves) == 2, f"{spec_path}: its quoted fragment elides one middle")
        for half in halves:
            check(half in refusal,
                  f"{spec_path} quotes {half!r} -- present VERBATIM in the live refusal")
    impl_quote, _ = quoted_halves(SPECS[0])
    rev_quote, _ = quoted_halves(SPECS[1])
    check(impl_quote == rev_quote, "both specs quote the refusal identically")
    check("567-d1-g3i2-probe-a" in bound["status-after"]["text"],
          "the refusal is total: spine_status still shows the FIRST spine")

    control = got["released-then-rebind"]
    check(control["release-a"]["isError"] is False, "control: A's lease releases")
    check(control["bind-b"]["isError"] is False,
          "control: the IDENTICAL bind SUCCEEDS once the lease is released "
          "-- so the refusal is conditioned on holding your own lease, nothing else")

    unbound = got["unbound-then-bind"]
    check(unbound["status-unbound"]["isError"] is True,
          "unbound: a crew dispatched without a spine holds no lease and no binding")
    check(unbound["bind-b"]["isError"] is False,
          "unbound: the door binds one spine and then drives it")
    check(unbound["claim-b"]["isError"] is False, "unbound: and claims its lease")
    sys.path.insert(0, str(REPO / "scripts"))
    import spine_lifecycle
    expected = spine_lifecycle.session_id_for("567-d1-g3i2-probe-b")
    payload = json.loads(unbound["bind-b"]["text"])
    check(payload.get("SPINE_SESSION") == expected,
          f"unbound: the identity comes from the spine's own work id ({expected})")

    print(f"\n{checked - len(failures)}/{checked} door-probe checks passed")
    for label in failures:
        print(f"  FAILED: {label}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
