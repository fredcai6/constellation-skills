#!/usr/bin/env python
"""DC1/DC2 close-side probe: at/over hard the engine refuses the SILENCE, not the
close. Runs the BRANCH engine as a subprocess against a throwaway spine.

Three moves at one and the same over-the-line reading:
  1. `start q2`      -> REFUSED   (a BEGIN is not allowed over the line)
  2. `advance q1 --mechanical` -> REFUSED (closing in silence is not allowed)
  3. `advance q1 --why "..."`  -> ALLOWED (closing WITH the handoff is the point)

Exit 0 = all three behaved as stated. The reading is asserted to have been READ
before any claim is made about it (no-absence-is-evidence).
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = WT / "scripts" / "checklist_engine.py"
FILL = 0.05


def gate(gid):
    return {"id": gid, "title": gid, "imperative": "probe",
            "context_headroom_tokens": 149000,
            "preconditions": [],
            "postconditions": [{"id": "c1", "statement": "trivially true",
                                "check": {"kind": "command",
                                          "command": "true"},
                                "satisfied": False}],
            "constraints": [], "anchors": {},
            "directives": None, "child_checklist": None, "status": "pending",
            "status_detail": {}, "result": None, "finding": None, "evidence": [],
            "rework_count": 0}


def run(spine, *args):
    p = subprocess.run([sys.executable, str(ENGINE), "--file", str(spine), *args],
                       capture_output=True, text=True,
                       env={**os.environ, "NO_COLOR": "1", "FORCE_COLOR": ""})
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / ".agent-work" / "close-probe"
        work.mkdir(parents=True)
        spine = work / "spine.json"
        spine.write_text(json.dumps({
            "work_id": "close-probe", "type": "gated", "items": ["q1", "q2"],
            "tasks": {"q1": gate("q1"), "q2": gate("q2")},
            "consolidation": None, "triage_candidates": [], "blockers": [],
            "why_trail": [], "refusals": [], "engine_session": None, "amendments": [],
        }), encoding="utf-8")
        (work / "gauge.json").write_text(json.dumps({
            "schema_version": 1, "fill_fraction": FILL, "model": "claude-sonnet-5",
            "observed_at": datetime.datetime.now(
                datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}),
            encoding="utf-8")

        run(spine, "claim", "--session-id", "close-probe")
        # pre-attach a request for q1 so the agent can BEGIN q1 at all
        run(spine, "attach", "q1", "--type", "refresh-request", "--field", "seam=q1",
            "--field", "why_ref=probe", "--session-id", "close-probe")
        run(spine, "start", "q1", "--session-id", "close-probe")

        ok = True

        # reading-exists assertion FIRST -- no claim about trip behaviour before it
        _, cur = run(spine, "current")
        if ">= hard" not in cur:
            print("FAIL: the engine printed no HARD advisory, so no reading is shown to "
                  "have been read. Nothing below can be claimed.")
            print(cur[-500:])
            return 1
        band = [ln for ln in cur.splitlines() if ">= hard" in ln][0]
        print(f"READING EXISTS -- the engine's own words:\n  {band[:180]}\n")

        rc, out = run(spine, "start", "q2", "--session-id", "close-probe")
        print(f"1. start q2                  -> exit {rc}")
        print(f"   {out.splitlines()[-1][:170]}")
        if rc == 0 or "hard limit" not in out:
            print("   FAIL: a BEGIN over the line was not refused")
            ok = False

        rc, out = run(spine, "advance", "q1", "--mechanical", "--session-id", "close-probe")
        print(f"\n2. advance q1 --mechanical   -> exit {rc}")
        print(f"   {out.splitlines()[-1][:170]}")
        if rc == 0 or "cannot be closed silently" not in out:
            print("   FAIL: a SILENT close over the line was not refused")
            ok = False

        rc, out = run(spine, "advance", "q1", "--why",
                      "the handoff-carrying close, which is the whole point",
                      "--session-id", "close-probe")
        print(f"\n3. advance q1 --why '...'    -> exit {rc}")
        print(f"   {out.splitlines()[-1][:170]}")
        if rc != 0 or "q1 -> complete" not in out:
            print("   FAIL: the handoff-carrying close was refused -- #431 is NOT dissolved")
            ok = False

        cl = json.loads(spine.read_text(encoding="utf-8"))
        digest = (cl.get("why_trail") or [{}])[-1].get("why")
        print(f"\n   digest after the close: {digest!r}")
        if digest != "the handoff-carrying close, which is the whole point":
            print("   FAIL: the digest did not become the understanding written AT this gate")
            ok = False

        print("\nPASS: over the line, a BEGIN is refused, a SILENT close is refused, and "
              "the handoff-carrying close completes and freshens the digest."
              if ok else "\nPROBE FAILED")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
