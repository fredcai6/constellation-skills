"""Independent (reviewer-authored) two-world seam test for the g4 B1 rework.

World H: a COMPLIANT agent. It never begins work over the hard line; it closes
the gate it is in with `advance --why` (the HARD band's mandated close) and
stops.

World D: a RUNAWAY. It is refused a BEGIN over the hard line at least once
(recorded to trip_ledger), then closes the SAME way -- `advance --why` -- and
stops.

The deciding question from the handoff: at the seam (immediately after each
world's close), is `current`'s output different, and does World D's output
name the TRUE TOTAL of over-the-line begins on disk?

Nothing is mocked. Real spine file, real gauge sidecar stamped from the clock,
real CLI subprocess.
"""
import json, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = ROOT / "scripts" / "checklist_engine.py"
spec = importlib.util.spec_from_file_location("eng", ENGINE)
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

MODEL = "claude-opus-4-8"
SOFT, HARD = E._gauge_reader.thresholds_for(MODEL)
OVER = min(HARD + 0.05, 1.0)
PASS_CMD = f'"{sys.executable}" -c "import sys; sys.exit(0)"'


def gate(i, status):
    return {"id": i, "title": i, "imperative": f"do {i}", "preconditions": [],
            "postconditions": [{"id": "c1", "statement": "ok",
                                "check": {"kind": "command", "command": PASS_CMD},
                                "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": status, "status_detail": {}, "result": None, "finding": None,
            "evidence": [], "rework_count": 0, "why_exempt": False}


def cli(f, *a):
    p = subprocess.run([sys.executable, str(ENGINE), "--file", str(f), *a],
                       capture_output=True, text=True, cwd=str(ROOT))
    return p.returncode, p.stdout, p.stderr


def new_spine(work_id):
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    ts = {f"g{i}": gate(f"g{i}", "in-progress" if i == 1 else "pending") for i in range(1, 4)}
    E.save(f, {"work_id": work_id, "type": "gated", "config": {"rework_cap": 3},
               "items": list(ts), "tasks": ts, "consolidation": None,
               "triage_candidates": [], "blockers": []})
    (Path(d) / "gauge.json").write_text(json.dumps(
        {"schema_version": 1, "fill_fraction": OVER, "model": MODEL,
         "observed_at": datetime.now(timezone.utc).isoformat()}), encoding="utf-8")
    return f


def seam_lines(out):
    live = next((l for l in out.splitlines() if l.startswith("TRIP LEDGER")), None)
    hist = next((l for l in out.splitlines() if l.startswith("TRIP HISTORY")), None)
    return live, hist


# ---------------------------------------------------------------- World H --
fH = new_spine("world-H-compliant")
cli(fH, "advance", "g1", "--why", "world H: closing g1, never began over the line")
rc, out, _ = cli(fH, "current")
assert rc == 0, out
liveH, histH = seam_lines(out)
clH = json.loads(fH.read_text(encoding="utf-8"))

# ---------------------------------------------------------------- World D --
fD = new_spine("world-D-runaway")
cli(fD, "start", "g2")  # not reached yet -- g1 is active; keep g1 in-progress
# Runaway: refused BEGIN at g1's own... use g2 after leaving g1 in-progress won't
# trigger BEGIN guard on g1 itself, so drive a refused/released BEGIN at g2 the
# same way the shipped scenario does: advance g1 first, then get refused at g2,
# attach a refresh, get released, THEN advance/close the SAME gate (g2) with --why.
fD = new_spine("world-D-runaway")
cli(fD, "advance", "g1", "--why", "world D: closing g1 (compliant so far)")
cli(fD, "start", "g2")  # REFUSED over the line -> tl-1 begin-refused
cli(fD, "attach", "g2", "--type", "refresh-request", "--field", "seam=g2", "--field", "why_ref=w-1")
cli(fD, "start", "g2")  # RELEASED (refresh already requested) -> tl-2 begin-released
rc, out, _ = cli(fD, "advance", "g2", "--why", "world D: closing g2, the gate the runaway happened in")
assert rc == 0, out
rc, out, _ = cli(fD, "current")
assert rc == 0, out
liveD, histD = seam_lines(out)
clD = json.loads(fD.read_text(encoding="utf-8"))
true_total_D = len([e for e in clD.get("trip_ledger") or []])

print("=== WORLD H (compliant close, never over the line) ===")
print(f"  trip_ledger on disk : {clH.get('trip_ledger')}")
print(f"  seam LIVE line      : {liveH!r}")
print(f"  seam HISTORY line   : {histH!r}")

print("\n=== WORLD D (runaway: refused+released BEGIN, then closes the SAME way) ===")
print(f"  trip_ledger on disk : {[(e['id'], e['outcome']) for e in clD.get('trip_ledger') or []]}")
print(f"  true total on disk  : {true_total_D}")
print(f"  seam LIVE line      : {liveD!r}")
print(f"  seam HISTORY line   : {histD!r}")

print("\n=== VERDICT ===")
identical = (liveH, histH) == (liveD, histD)
print(f"  seam output identical between H and D? {identical}")
names_true_total = histD is not None and f"{true_total_D} begin(s)" in histD
print(f"  World D's seam output names the true total ({true_total_D})? {names_true_total}")
print(f"  World H seam is silent on both lines (expected)? {liveH is None and histH is None}")
