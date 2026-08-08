"""Does the shipped sentence 'Closing this gate does not clear the record' hold?

The engine renders exactly one compliance line, and it ends with that sentence.
This probe runs the natural runaway the gate exists to catch and reads the line
back after each step. Nothing is mocked: real spine file, real gauge sidecar
stamped from the clock, real CLI.
"""
import json, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
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


d = tempfile.mkdtemp(); f = Path(d) / "spine.json"
ts = {f"g{i}": gate(f"g{i}", "in-progress" if i == 1 else "pending") for i in range(1, 5)}
E.save(f, {"work_id": "runaway", "type": "gated", "config": {"rework_cap": 3},
           "items": list(ts), "tasks": ts, "consolidation": None,
           "triage_candidates": [], "blockers": []})
(Path(d) / "gauge.json").write_text(json.dumps(
    {"schema_version": 1, "fill_fraction": OVER, "model": MODEL,
     "observed_at": datetime.now(timezone.utc).isoformat()}), encoding="utf-8")


def show(step):
    rc, out, err = cli(f, "current")
    cl = json.loads(f.read_text(encoding="utf-8"))
    line = next((l for l in out.splitlines() if "TRIP LEDGER" in l), None)
    # #467 B1 REWORK, mechanical edit to keep this probe running against the new
    # strings: the historical line added by the rework deliberately does NOT share
    # the "TRIP LEDGER" substring with the live line (so `grep 'TRIP LEDGER'
    # scripts/` still finds the render site once) -- it is labelled "TRIP HISTORY".
    # Without this line the probe would silently stop seeing the fix and every
    # "RENDERED LINE" below would still read None at the seam, which is no longer
    # true. No other line in this function was changed.
    hist_line = next((l for l in out.splitlines() if "TRIP HISTORY" in l), None)
    print(f"\n[{step}]")
    print(f"    active gate      : {E.active_id(cl)}")
    print(f"    why_trail        : {[w['id'] for w in cl.get('why_trail', [])]}")
    print(f"    ledger on disk   : {[(e['id'], e['outcome'], e['why_ref']) for e in cl.get('trip_ledger') or []]}")
    print(f"    SIGNAL (selector): {len(E.begin_over_line_records(cl))}")
    print(f"    HIST (selector)  : {len(E.begin_over_line_records_historical(cl))}")  # #467 B1 rework
    print(f"    RENDERED LINE    : {line}")
    print(f"    RENDERED HISTORY : {hist_line}")  # #467 B1 rework
    return line


print(f"hard={HARD}, gauge parked at {OVER} for the whole run (fresh, from the clock)")
print("\nThe HARD advisory tells the agent: close THIS gate carrying your handoff and STOP;")
print("do not begin work at another gate. The runaway below ignores that.")

cli(f, "advance", "g1", "--why", "closing g1 as instructed")
cli(f, "start", "g2")                       # REFUSED -> tl-1
l1 = show("after the refused BEGIN at g2 -- the mark is live")

cli(f, "attach", "g2", "--type", "refresh-request",
    "--field", "seam=g2", "--field", "why_ref=w-1")
rc, out, _ = cli(f, "start", "g2")          # RELEASED -> tl-2
print(f"\n    (`start g2` after attaching a request: rc={rc} -> {out.strip().splitlines()[-1]})")
l2 = show("after the RELEASED begin at g2 -- work is now proceeding over the line")

rc, out, _ = cli(f, "advance", "g2", "--why", "did the g2 work anyway")
print(f"\n    (`advance g2 --why ...`: rc={rc} -> {out.strip().splitlines()[-1]})")
l3 = show("after the SAME agent closed g2 -- the gate its own line told it about")

cli(f, "start", "g3")
l4 = show("after a further refused BEGIN at g3 -- the signal re-arms, but only for g3")

print("\n================ VERDICT ON THE SHIPPED SENTENCE ================")
print(f"  the line said: ...{(l1 or '')[-60:]}")
print(f"  after closing that gate, the line is: {l3!r}")
print(f"  => 'Closing this gate does not clear the record' is "
      f"{'TRUE' if l3 else 'FALSE for the rendered signal'}")
cl = json.loads(f.read_text(encoding="utf-8"))
print(f"  total over-the-line begins on disk across the runaway: {len(cl['trip_ledger'])}")
print(f"  most the rendered line ever claimed at once            : "
      f"{max(int(l.split('TRIP LEDGER: ')[1].split(' ')[0]) for l in (l1, l2, l4) if l)}")
