"""#467 B1 rework -- close criterion 5: the two-worlds seam measurement.

Builds World H (compliant: the agent wraps up, closes its gate with
`advance --why`, stops -- no begin verb ever runs over the line) and World D
(runaway: a refused begin, a released begin, then the SAME agent closes with
`advance --why` -- the reviewer's own reproduction shape), then runs `current`
at the seam in each -- through the real CLI in a subprocess, on a real
gauge.json stamped from the clock. No mock anywhere in the advisory path.

Own fixture spine/gauge in a temp dir -- never execute.json/spine.json/gauge.json
(the Commander holds that lease).
"""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = ROOT / "scripts" / "checklist_engine.py"
spec = importlib.util.spec_from_file_location("eng", ENGINE)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

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


def new_world():
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    ts = {f"g{i}": gate(f"g{i}", "in-progress" if i == 1 else "pending") for i in range(1, 4)}
    E.save(f, {"work_id": "seam-probe", "type": "gated", "config": {"rework_cap": 3},
               "items": list(ts), "tasks": ts, "consolidation": None,
               "triage_candidates": [], "blockers": []})
    (Path(d) / "gauge.json").write_text(json.dumps(
        {"schema_version": 1, "fill_fraction": OVER, "model": MODEL,
         "observed_at": datetime.now(timezone.utc).isoformat()}), encoding="utf-8")
    return f


def seam_current(f):
    """A fresh reader's `current` at the seam -- the exact call B1 is about."""
    rc, out, err = cli(f, "current")
    assert rc == 0, (rc, out, err)
    return out


print(f"hard={HARD}, gauge parked at {OVER} for the whole run (fresh, from the clock)\n")

# --- World H: compliant. Wraps up, closes g1, stops. No begin ever runs over --
h = new_world()
rc, out, err = cli(h, "advance", "g1", "--why", "wrapping up as instructed, stopping here")
assert rc == 0, (rc, out, err)
H_OUT = seam_current(h)

# --- World D: runaway (reviewer's own shape) -----------------------------------
d = new_world()
rc, out, err = cli(d, "advance", "g1", "--why", "closing g1 as instructed")
assert rc == 0, (rc, out, err)
rc, out, err = cli(d, "start", "g2")                                   # REFUSED -> tl-1
assert rc != 0, "expected the refused begin to raise"
cli(d, "attach", "g2", "--type", "refresh-request",
    "--field", "seam=g2", "--field", "why_ref=w-1")
rc, out, err = cli(d, "start", "g2")                                   # RELEASED -> tl-2
assert rc == 0, (rc, out, err)
rc, out, err = cli(d, "advance", "g2", "--why",
                   "the offender's own close, the gate its own HARD advisory told it to close")
assert rc == 0, (rc, out, err)                                         # the offender's own close
D_OUT = seam_current(d)

cl = json.loads(d.read_text(encoding="utf-8"))
total_on_disk = len(cl.get("trip_ledger") or [])

print("================ WORLD H (compliant) -- `current` at the seam ================")
print(H_OUT)
print("================ WORLD D (runaway, offender's own close) -- `current` at the seam ================")
print(D_OUT)

print("================ VERDICT ================")
print(f"H == D (byte-identical)? {H_OUT == D_OUT!r}")
print(f"total over-the-line begins on disk in World D: {total_on_disk}")
print(f"'TRIP HISTORY' in D_OUT: {'TRIP HISTORY' in D_OUT}")
print(f"str(total) in D_OUT: {str(total_on_disk) in D_OUT}")
assert H_OUT != D_OUT, "REGRESSION: the two worlds are still identical at the seam"
assert "TRIP HISTORY" in D_OUT, "REGRESSION: the historical line did not render in World D"
assert str(total_on_disk) in D_OUT, "REGRESSION: D's rendered line does not name the true total"
assert "TRIP HISTORY" not in H_OUT, "World H spuriously rendered a historical line"
print("\nPASS: H and D differ at the seam, and D names the true total.")
