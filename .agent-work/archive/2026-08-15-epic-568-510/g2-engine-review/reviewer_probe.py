"""Independent reviewer reproduction for epic-568-510 g2-engine.

Written by the reviewer, not copied from the implementer's test class. Two jobs:

1. Reproduce the behavior change end to end (the claim), including through the CLI.
2. Falsify NARROWNESS by exhaustive sweep: over every combination of verb, target
   gate, gate status, request presence/keying, why_exempt, gauge band and checklist
   type this engine can reach, assert the implication

       outcome == "begin-instructed"  =>  the advisory the agent SAW (computed
       before the verb ran) literally instructed `start <that same gate>`

   A single counterexample refutes "the exemption is as narrow as the instruction
   that earns it".
"""
import contextlib
import io
import itertools
import json
import subprocess
import sys
import tempfile
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import checklist_engine as E  # noqa: E402

MODEL = "claude-opus-4-8"
SOFT, HARD = E._gauge_reader.thresholds_for(MODEL)
OVER = min(HARD + 0.05, 1.0)
UNDER = max(HARD - 0.10, 0.0)

failures = []
notes = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (f"   [{detail}]" if detail else ""))
    if not ok:
        failures.append((label, detail))


def reading(fill, observed_at=None):
    return E._gauge_reader.Reading(
        schema_version=1, fill_fraction=fill, model=MODEL,
        observed_at=observed_at or datetime.now(timezone.utc))


PASS_COMMAND = f'"{sys.executable}" -c "import sys; sys.exit(0)"'


def task(iid, status="pending", why_exempt=False):
    post = [{"id": "c1", "statement": "tests pass",
             "check": {"kind": "command", "command": PASS_COMMAND}, "satisfied": False}]
    t = {"id": iid, "title": iid, "imperative": f"do {iid}",
         "preconditions": [], "postconditions": post, "constraints": [],
         "directives": None, "child_checklist": None, "status": status,
         "status_detail": {}, "result": None, "finding": None,
         "evidence": [], "rework_count": 0}
    if why_exempt is not None:
        t["why_exempt"] = why_exempt
    return t


def spine(statuses, why_exempt=False, kind="gated"):
    """statuses: list of (id, status). g1 is closed via the real `advance` when
    asked for, so the why_trail is genuine rather than hand-built."""
    tasks = {i: task(i, s, why_exempt) for i, s in statuses}
    return {"work_id": "probe", "type": kind, "config": {"rework_cap": 3},
            "items": [i for i, _ in statuses], "tasks": tasks,
            "consolidation": None, "triage_candidates": [], "blockers": []}


def ns(verb, iid):
    if verb == "start":
        return types.SimpleNamespace(verb="start", id=iid, session_id=None)
    return types.SimpleNamespace(verb="reopen", id=iid, reason="rework", session_id=None)


def live_wid(cl):
    rec = E._latest_why_record(cl)
    return rec["id"] if rec else None


def advisory(cl, fill):
    with mock.patch.object(E, "_read_gauge", return_value=reading(fill)):
        return E._trip_advisory(cl, Path("."))


def run_verb(cl, verb, iid, fill):
    """Returns (raised_exception_or_None, message_or_None)."""
    patch = mock.patch.object(E, "_read_gauge",
                              return_value=None if fill is None else reading(fill))
    with patch:
        try:
            return None, E.dispatch(cl, ns(verb, iid), base_dir=Path("."))
        except E.EngineError as exc:
            return exc, None


def outcomes(cl):
    return [e["outcome"] for e in cl.get("trip_ledger", [])]


# --------------------------------------------------------------------------- #
print(f"\nthresholds for {MODEL}: soft={SOFT:.4f} hard={HARD:.4f}  "
      f"(over={OVER:.4f} under={UNDER:.4f})")

print("\n=== 1. reproduce the claim: obey the pending-HARD advisory ===")
cl = spine([("g1", "in-progress"), ("g2", "pending"), ("g3", "pending")])
E.advance(cl, "g1", why="u1 — my own legal close")            # real close, real why_trail
assert E.active_id(cl) == "g2" and cl["tasks"]["g2"]["status"] == "pending"

seen = advisory(cl, OVER)
check("the advisory the agent sees really instructs `start g2`",
      "begin THIS guarded gate (`start g2`)" in seen)

E.attach(cl, "g2", "refresh-request", {"seam": "g2", "why_ref": live_wid(cl)})
exc, msg = run_verb(cl, "start", "g2", OVER)
check("obeying it is permitted", exc is None and msg.endswith("g2 -> in-progress"),
      str(exc or msg))
check("the gate really opened", cl["tasks"]["g2"]["status"] == "in-progress")
check("recorded as begin-instructed", outcomes(cl) == ["begin-instructed"], str(outcomes(cl)))
check("the event is NOT hidden from the ledger", len(cl["trip_ledger"]) == 1)
check("live compliance selector is empty", E.begin_over_line_records(cl) == [])
check("historical compliance selector is empty", E.begin_over_line_records_historical(cl) == [])
after = advisory(cl, OVER)
check("neither compliance line renders after obeying",
      "TRIP LEDGER:" not in after and "TRIP HISTORY" not in after, after)
check("the entry keeps every #467 field",
      set(cl["trip_ledger"][0]) == {"id", "gate", "verb", "outcome", "fill",
                                    "hard", "model", "why_ref", "ts"},
      str(sorted(cl["trip_ledger"][0])))

print("\n=== 2. the same thing through the real CLI (no in-process mocking) ===")
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    f = d / "spine.json"
    cl2 = spine([("g1", "in-progress"), ("g2", "pending"), ("g3", "pending")])
    E.advance(cl2, "g1", why="u1 — my own legal close")
    f.write_text(json.dumps(cl2), encoding="utf-8")
    (d / ".agent-work").mkdir(parents=True, exist_ok=True)
    gauge = {"schema_version": 1, "fill_fraction": OVER, "model": MODEL,
             "observed_at": datetime.now(timezone.utc).isoformat()}
    E._gauge_path(d).parent.mkdir(parents=True, exist_ok=True)
    E._gauge_path(d).write_text(json.dumps(gauge), encoding="utf-8")

    def cli(*argv):
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = E.main(["--file", str(f), *argv])
        return code, buf.getvalue() + err.getvalue()

    code, out = cli("current")
    check("CLI `current` instructs `start g2`",
          "begin THIS guarded gate (`start g2`)" in out, out[-200:])
    code, _ = cli("attach", "g2", "--type", "refresh-request",
                  "--field", "seam=g2", "--field", "why_ref=w-1")
    check("CLI attach of the requested refresh succeeds", code == 0)
    code, out = cli("start", "g2")
    check("CLI `start g2` succeeds", code == 0, out[-200:])
    disk = json.loads(f.read_text(encoding="utf-8"))
    check("CLI persisted outcome is begin-instructed",
          [e["outcome"] for e in disk["trip_ledger"]] == ["begin-instructed"],
          str([e["outcome"] for e in disk.get("trip_ledger", [])]))
    code, out = cli("current")
    check("CLI `current` does not brand the obedient agent",
          "TRIP LEDGER:" not in out and "TRIP HISTORY" not in out, out[-300:])

print("\n=== 3. begin-released is still reachable and still branded ===")
cl3 = spine([("g1", "in-progress"), ("g2", "pending"), ("g3", "pending")])
E.advance(cl3, "g1", why="u1")
E.attach(cl3, "g1", "refresh-request", {"seam": "g1", "why_ref": live_wid(cl3)})
exc, _ = run_verb(cl3, "reopen", "g1", OVER)
check("reopen over the line is released", outcomes(cl3) == ["begin-released"], str(outcomes(cl3)))
check("and it IS branded (historical selector)",
      len(E.begin_over_line_records_historical(cl3)) == 1)
check("the TRIP HISTORY line renders for it",
      "TRIP HISTORY" in advisory(cl3, OVER))

print("\n=== 4. EXHAUSTIVE NARROWNESS SWEEP ===")
print("    implication under test: outcome == begin-instructed  =>  the advisory")
print("    the agent saw literally said: begin THIS guarded gate (`start <target>`)")

VERBS = ["start", "reopen"]
TARGETS = ["g1", "g2", "g3"]          # closed / active / later
ACTIVE_STATUS = ["pending", "in-progress", "blocked"]
REQUEST = ["none", "keyed-at-target", "stale-key-at-target", "keyed-elsewhere"]
WHY_EXEMPT = [False, True]
GAUGE = ["over", "under", "absent", "predates-claim"]
KIND = ["gated", "survey"]

rows = 0
instructed_rows = 0
violations = []
matrix = {}

for verb, target, astatus, req, wx, band, kind in itertools.product(
        VERBS, TARGETS, ACTIVE_STATUS, REQUEST, WHY_EXEMPT, GAUGE, KIND):
    cl = spine([("g1", "complete"), ("g2", astatus), ("g3", "pending")],
               why_exempt=wx, kind=kind)
    if not wx:
        # a genuine why_trail, as a real run would have
        E._append_why(cl, "g1", "u1 — the understanding in force", False)
    wid = live_wid(cl)
    if req == "keyed-at-target":
        E.attach(cl, target, "refresh-request", {"seam": target, "why_ref": wid})
    elif req == "stale-key-at-target":
        E.attach(cl, target, "refresh-request", {"seam": target, "why_ref": "w-stale-999"})
    elif req == "keyed-elsewhere":
        other = "g3" if target != "g3" else "g1"
        E.attach(cl, other, "refresh-request", {"seam": other, "why_ref": wid})

    if band == "predates-claim":
        # a well-formed reading sampled BEFORE this session claimed the checklist
        E.claim(cl, "s-probe", "reviewer", ".", {})
        r = reading(OVER, observed_at=datetime.now(timezone.utc) - timedelta(hours=2))
    elif band == "over":
        r = reading(OVER)
    elif band == "under":
        r = reading(UNDER)
    else:
        r = None

    with mock.patch.object(E, "_read_gauge", return_value=r):
        seen = E._trip_advisory(cl, Path("."))
        try:
            E.dispatch(cl, ns(verb, target), base_dir=Path("."))
        except E.EngineError:
            pass
        except Exception as exc:                      # pragma: no cover - probe safety
            notes.append(f"unexpected {type(exc).__name__} at {(verb, target, astatus, req, wx, band, kind)}: {exc}")

    rows += 1
    got = outcomes(cl)
    key = (verb, target, astatus, req, wx, band, kind)
    matrix[key] = got
    for o in got:
        if o == "begin-instructed":
            instructed_rows += 1
            wanted = f"begin THIS guarded gate (`start {target}`)"
            if wanted not in seen:
                violations.append((key, seen))

check(f"sweep covered {rows} reachable states (non-empty, so the loop looped)", rows > 0)
check(f"{instructed_rows} of them produced a begin-instructed entry (the exemption is reachable)",
      instructed_rows > 0)
check("NO state produced begin-instructed without the advisory instructing that exact start",
      not violations, f"{len(violations)} counterexample(s): {violations[:2]}")

# the converse direction: every state that DID get the exemption must satisfy all
# four keying conditions simultaneously.
bad_shape = [k for k, v in matrix.items() if "begin-instructed" in v
             and not (k[0] == "start" and k[1] == "g2" and k[2] == "pending"
                      and k[6] == "gated" and k[5] == "over")]
check("every exempted state is exactly (start, active gate, pending, gated, over-hard)",
      not bad_shape, str(bad_shape[:3]))

print("\n=== 5. named narrowness probes from the handoff ===")
probe_names = {
    "reopen": [k for k, v in matrix.items() if k[0] == "reopen" and "begin-instructed" in v],
    "start with no keyed request": [k for k, v in matrix.items()
                                    if k[0] == "start" and k[3] in ("none", "stale-key-at-target",
                                                                    "keyed-elsewhere")
                                    and "begin-instructed" in v],
    "start at a non-active gate": [k for k, v in matrix.items()
                                   if k[0] == "start" and k[1] != "g2" and "begin-instructed" in v],
    "start at an in-progress or blocked gate": [k for k, v in matrix.items()
                                                if k[2] in ("in-progress", "blocked")
                                                and "begin-instructed" in v],
    "survey checklist": [k for k, v in matrix.items() if k[6] == "survey" and v],
    "why_exempt gate (live why id None)": [k for k, v in matrix.items()
                                           if k[4] and "begin-instructed" in v
                                           and f"begin THIS guarded gate (`start {k[1]}`)" not in ""],
    "absent gauge reading": [k for k, v in matrix.items() if k[5] == "absent" and v],
    "reading that predates the claim": [k for k, v in matrix.items() if k[5] == "predates-claim" and v],
}
for label in ("reopen", "start with no keyed request", "start at a non-active gate",
              "start at an in-progress or blocked gate", "survey checklist",
              "absent gauge reading", "reading that predates the claim"):
    check(f"{label}: never exempted / never ledgered", not probe_names[label],
          str(probe_names[label][:2]))

# why_exempt is allowed to be exempted -- but only where the advisory also instructs it.
wx_instructed = [k for k, v in matrix.items() if k[4] and "begin-instructed" in v]
check(f"why_exempt gates: {len(wx_instructed)} exempted, and all were advisory-instructed "
      f"(covered by the sweep implication above)", True)

print("\n=== 6. the AST call-graph pin, verified independently ===")
import ast
tree = ast.parse((ROOT / "scripts" / "checklist_engine.py").read_text(encoding="utf-8"))
callers, namers = set(), set()
for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                and sub.func.id == "_append_trip_entry":
            callers.add(fn.name)
        if isinstance(sub, ast.Constant) and sub.value == "trip_ledger":
            namers.add(fn.name)
check("_append_trip_entry has exactly one caller", callers == {"_trip_hard_gate"}, str(sorted(callers)))
check("exactly three functions name 'trip_ledger'", len(namers) == 3, str(sorted(namers)))

print("\n" + "=" * 72)
for n in notes:
    print("NOTE:", n)
print(f"RESULT: {len(failures)} failed check(s) out of the probe")
for f_, d in failures:
    print("  FAILED:", f_, d)
sys.exit(1 if failures else 0)
