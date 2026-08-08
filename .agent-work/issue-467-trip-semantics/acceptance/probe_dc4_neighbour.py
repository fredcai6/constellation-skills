#!/usr/bin/env python
"""DC4 probe: a per-gate context_headroom_tokens override changes ITS gate's
behaviour and NOT its neighbour's, at one and the same reading.

Two gates, identical in every way except that `p1` declares an override and `p2`
does not. One planted reading of 0.05 -- BELOW the shipped hard line of 0.15, so
neither gate would trip on the shipped default. Runs the BRANCH engine as a
subprocess against a throwaway spine. Exit 0 = the override discriminated.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import datetime
from pathlib import Path

WT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = WT / "scripts" / "checklist_engine.py"
FILL = 0.05


def gate(gid, headroom):
    t = {"id": gid, "title": gid, "imperative": "probe", "preconditions": [],
         "postconditions": [{"id": "c1", "statement": "trivially true",
                             "check": {"kind": "command", "command": "true"},
                             "satisfied": False}],
         "constraints": [], "anchors": {}, "directives": None,
         "child_checklist": None, "status": "pending", "status_detail": {},
         "result": None, "finding": None, "evidence": [], "rework_count": 0}
    if headroom:
        t["context_headroom_tokens"] = headroom
    return t


def run(spine, *args):
    p = subprocess.run([sys.executable, str(ENGINE), "--file", str(spine), *args],
                       capture_output=True, text=True,
                       env={**os.environ, "NO_COLOR": "1", "FORCE_COLOR": ""})
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / ".agent-work" / "dc4-probe"
        work.mkdir(parents=True)
        spine = work / "spine.json"
        spine.write_text(json.dumps({
            "work_id": "dc4-probe", "type": "gated", "items": ["p1", "p2"],
            "tasks": {"p1": gate("p1", None), "p2": gate("p2", 149000)},
            "consolidation": None, "triage_candidates": [], "blockers": [],
            "why_trail": [], "refusals": [], "engine_session": None, "amendments": [],
        }), encoding="utf-8")
        (work / "gauge.json").write_text(json.dumps({
            "schema_version": 1, "fill_fraction": FILL, "model": "claude-sonnet-5",
            "observed_at": datetime.datetime.now(
                datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}),
            encoding="utf-8")

        run(spine, "claim", "--session-id", "dc4-probe")
        # p1 has NO override: begin it, then close it, so p2 becomes legally startable
        # and the ONLY thing left that can refuse p2 is the governor.
        rc1, out1 = run(spine, "start", "p1", "--session-id", "dc4-probe")
        run(spine, "advance", "p1", "--mechanical", "--session-id", "dc4-probe")
        rc2, out2 = run(spine, "start", "p2", "--session-id", "dc4-probe")

        print(f"planted fill = {FILL} (BELOW the shipped hard line 0.15)\n")
        print(f"--- start p1  (declares NO override)                   -> exit {rc1}")
        print("    " + out1.strip().splitlines()[-1][:200])
        print(f"\n--- start p2  (declares context_headroom_tokens=149000) -> exit {rc2}")
        print("    " + out2.strip().splitlines()[-1][:200])

        ledger = json.loads(spine.read_text(encoding="utf-8")).get("trip_ledger", [])
        print(f"\ntrip_ledger: {json.dumps(ledger)}")

        ok = True
        if rc1 != 0:
            print("\nFAIL: p1 (NO override) was refused at 0.05 -- the override leaked "
                  "to a neighbour")
            ok = False
        if rc2 == 0 or "hard limit" not in out2:
            print("\nFAIL: p2 (with the override) was NOT refused at 0.05")
            ok = False
        gates_in_ledger = {e.get("gate") for e in ledger}
        if gates_in_ledger != {"p2"}:
            print(f"\nFAIL: ledger names {gates_in_ledger}, expected only p2")
            ok = False
        if ok:
            print("\nPASS: at one and the same reading of 0.05, the gate carrying the "
                  "override tripped and its neighbour did not.")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
