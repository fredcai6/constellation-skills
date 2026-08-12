#!/usr/bin/env python
"""Reusable validation harness for a candidate spine_completed.py.

Runs the check (whichever copy is passed) against the three kept round-2 workspaces
and the two grandfathered ref-honest runs, and reports PASS/FAIL + reason for each.
Also prints the terminal-completion tally. Pure over kept workspaces (no re-runs).

Usage: py validate_check.py [path-to-spine_completed.py]
Default check: evals/euler-1-multiples/checks/spine_completed.py in the worktree.
"""
import importlib.util, json, sys
from pathlib import Path

CHECK = sys.argv[1] if len(sys.argv) > 1 else \
    "C:/Programs/constellation-wt-129/evals/euler-1-multiples/checks/spine_completed.py"
spec = importlib.util.spec_from_file_location("sc", CHECK)
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)

TMP = "C:/Users/fredc/AppData/Local/Temp"
HARV = "C:/Programs/constellation-skills/.agent-work/dispatch-126-127/harvest"
SUBJECTS = [
    ("A 6lcnbis9 (terminal-reaching)", f"{TMP}/constellation-eval-6lcnbis9/run-0", "expect-PASS-if-fixed"),
    ("B g6o67i9t (terminal-reaching)", f"{TMP}/constellation-eval-g6o67i9t/run-0", "expect-PASS-if-fixed"),
    ("C iricdfpb (genuine 9/10)",      f"{TMP}/constellation-eval-iricdfpb/run-0", "expect-FAIL"),
    ("REF1 (grandfathered)", f"{HARV}/ref-honest-run-1", "expect-PASS"),
    ("REF2 (grandfathered)", f"{HARV}/ref-honest-run-2", "expect-PASS"),
]

def run(run_dir):
    # capture main()'s stdout line + exit
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = sc.main(str(run_dir))
    return rc, buf.getvalue().strip()

terminal = 0
for label, rd, expect in SUBJECTS:
    if not Path(rd).is_dir():
        print(f"[{label}] MISSING dir {rd}"); continue
    rc, line = run(rd)
    verdict = "PASS" if rc == 0 else "FAIL"
    if "terminal-reaching" in label or "genuine" in label:
        if rc == 0: terminal += 1
    flag = "OK" if expect.endswith(verdict) or (expect=="expect-PASS-if-fixed" and verdict in ("PASS","FAIL")) else "??"
    print(f"[{label}] {verdict} :: {line}")
print(f"\nTerminal-completion tally over the 3 round-2 subjects: {terminal}/3")
