"""Independent silencing-attempt probe for the g4 B1 rework's HISTORICAL line.

Question: with at least one over-the-line begin on trip_ledger, can ANY legal
sequence make the TRIP HISTORY line stop rendering while the checklist still
has an active gate to advise about? (Once every gate is complete there is no
active gate at all -- _trip_advisory returns "" for ANY reason at that point,
which is pre-existing behavior unrelated to #467 and out of this fix's scope;
that case is checked and reported separately, not conflated with silencing.)
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


def gate(i, status, why_exempt=False):
    return {"id": i, "title": i, "imperative": f"do {i}", "preconditions": [],
            "postconditions": [{"id": "c1", "statement": "ok",
                                "check": {"kind": "command", "command": PASS_CMD},
                                "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": status, "status_detail": {}, "result": None, "finding": None,
            "evidence": [], "rework_count": 0, "why_exempt": why_exempt}


def cli(f, *a):
    p = subprocess.run([sys.executable, str(ENGINE), "--file", str(f), *a],
                       capture_output=True, text=True, cwd=str(ROOT))
    return p.returncode, p.stdout, p.stderr


def new_spine(work_id, n=4, why_exempt_gates=()):
    d = tempfile.mkdtemp()
    f = Path(d) / "spine.json"
    ts = {f"g{i}": gate(f"g{i}", "in-progress" if i == 1 else "pending",
                        why_exempt=(f"g{i}" in why_exempt_gates)) for i in range(1, n + 1)}
    E.save(f, {"work_id": work_id, "type": "gated", "config": {"rework_cap": 3},
               "items": list(ts), "tasks": ts, "consolidation": None,
               "triage_candidates": [], "blockers": []})
    (Path(d) / "gauge.json").write_text(json.dumps(
        {"schema_version": 1, "fill_fraction": OVER, "model": MODEL,
         "observed_at": datetime.now(timezone.utc).isoformat()}), encoding="utf-8")
    return f


def hist_line(f):
    rc, out, _ = cli(f, "current")
    return next((l for l in out.splitlines() if l.startswith("TRIP HISTORY")), None)


def arm_runaway(f, gate_id, why_ref_hint):
    """Trip a refused+released begin at gate_id (must be the active gate)."""
    cli(f, "start", gate_id)  # refused
    cli(f, "attach", gate_id, "--type", "refresh-request", "--field", f"seam={gate_id}",
        "--field", f"why_ref={why_ref_hint}")
    cli(f, "start", gate_id)  # released


results = {}

# 1. reopen (rework) the gate that was closed after the runaway.
f = new_spine("silence-reopen")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
cli(f, "advance", "g2", "--why", "close g2 (the runaway gate)")
before = hist_line(f)
rc, out, err = cli(f, "reopen", "g2", "--reason", "trying to bury it")
after = hist_line(f)
results["reopen"] = (before, rc, out.strip().splitlines()[-1] if out.strip() else err.strip(), after)

# 2. block / resume the gate.
f = new_spine("silence-block")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
before = hist_line(f)
rc, out, err = cli(f, "block", "g2", "--blocker", "x", "--authority", "human", "--next", "y")
rc2, out2, err2 = cli(f, "resume", "g2", "--reason", "unblock")
after = hist_line(f)
results["block+resume"] = (before, (rc, rc2), after)

# 3. skip the gate (survey-only per docs, but try on gated too).
f = new_spine("silence-skip")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
before = hist_line(f)
rc, out, err = cli(f, "skip", "g2", "--reason", "obe")
after = hist_line(f)
results["skip"] = (before, rc, (out.strip() or err.strip()).splitlines()[-1] if (out.strip() or err.strip()) else "", after)

# 4. waive + advance --mechanical (does NOT count as --why; should still be REFUSED
#    at/over hard per no-silent-close, but try it to see if it slips through and
#    whether that path clears anything).
f = new_spine("silence-mechanical")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
before = hist_line(f)
rc, out, err = cli(f, "advance", "g2", "--mechanical")
after = hist_line(f)
cl = json.loads(f.read_text(encoding="utf-8"))
results["advance --mechanical (expect REFUSED)"] = (before, rc, (out.strip() or err.strip()), after,
                                                      f"g2 status now: {cl['tasks']['g2']['status']}")

# 5. amend (retext-check on a pending gate) -- try amending g2's text; does not
#    touch trip_ledger by contract (amend ops are add/drop/rescope/retext-check on
#    gate metadata, never ledger entries).
f = new_spine("silence-amend")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
before = hist_line(f)
delta = {"ops": [{"op": "retext-check", "id": "g2", "field": "imperative", "value": "do g2, amended"}]}
delta_path = Path(tempfile.mkdtemp()) / "delta.json"
delta_path.write_text(json.dumps(delta), encoding="utf-8")
rc, out, err = cli(f, "amend", "--delta", str(delta_path), "--reason", "test", "--authority", "human")
after = hist_line(f)
results["amend retext-check"] = (before, rc, (out.strip() or err.strip()).splitlines()[-1] if (out.strip() or err.strip()) else "", after)

# 6. attach arbitrary evidence to g2 (does attaching evidence to the CLOSED gate
#    change anything about the historical read?).
f = new_spine("silence-attach")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
cli(f, "advance", "g2", "--why", "close g2")
before = hist_line(f)
rc, out, err = cli(f, "attach", "g2", "--type", "note", "--field", "x=y")
after = hist_line(f)
results["attach after close"] = (before, rc, after)

# 7. --dry-run on advance/current, if the CLI even accepts the flag.
f = new_spine("silence-dryrun")
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
before = hist_line(f)
rc, out, err = cli(f, "advance", "g2", "--why", "close g2", "--dry-run")
after = hist_line(f)
results["--dry-run flag"] = (before, rc, (out.strip() or err.strip())[:200], after)

# 8. why_exempt gate -- runaway happens at a gate marked why_exempt (live selector
#    matches None==None per docstring; historical selector doesn't care about
#    why_ref at all).
f = new_spine("silence-why-exempt", why_exempt_gates=("g1", "g2"))
arm_runaway(f, "g1", None)  # g1 is active and why_exempt, no why_trail ever created
before_current = cli(f, "current")[1]
live_exempt = next((l for l in before_current.splitlines() if l.startswith("TRIP LEDGER")), None)
hist_exempt = next((l for l in before_current.splitlines() if l.startswith("TRIP HISTORY")), None)
rc, out, err = cli(f, "advance", "g1", "--mechanical")  # why_exempt gates may close mechanically
after = hist_line(f)
cl = json.loads(f.read_text(encoding="utf-8"))
results["why_exempt gate, no why_trail ever"] = (
    f"live={live_exempt!r} hist={hist_exempt!r}", rc, (out.strip() or err.strip()).splitlines()[-1] if (out.strip() or err.strip()) else "",
    after, f"g1 status: {cl['tasks']['g1']['status']}", f"why_trail: {cl.get('why_trail')}")

# 9. Whole checklist completed (every gate closed) -- no active gate at all.
#    Not a "silencing" of the compliance FACT (nothing is asking anymore), but
#    check it explicitly and report it as its own category, not conflated with #1-8.
f = new_spine("silence-all-closed", n=2)
cli(f, "advance", "g1", "--why", "close g1")
arm_runaway(f, "g2", "w-1")
cli(f, "advance", "g2", "--why", "close g2 (last gate)")
rc, out, err = cli(f, "current")
after_all_closed = next((l for l in out.splitlines() if l.startswith("TRIP HISTORY")), None)
results["ALL GATES CLOSED (no active gate -- separate category)"] = (out.strip().splitlines()[:3], after_all_closed)

for k, v in results.items():
    print(f"\n--- {k} ---")
    print(v)
