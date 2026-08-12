#!/usr/bin/env python
"""Snapshot the five measured issues ONCE, before any run (#299).

The pin freezes the code; this freezes the brief. If an issue is edited between the PRE
and POST arms the two arms silently receive different inputs, and since the brief is
where every path give-away lives, that difference lands squarely on the measure. Both
arms MUST read this file rather than `gh` live.

READ-ONLY against f1Brainz: `gh issue view` only, never a write.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

# These issue titles carry non-ASCII (sigma-plus, arrows). Console stdout defaults to the
# ANSI codepage on Windows, which cannot encode them — reconfigure rather than lose the
# run to a print statement.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

REPO = "fredcai6/f1Brainz"
ISSUES = [690, 688, 698, 716, 704]
PIN = "3541d2929b19de37107ae13e56776b7162d07255"
OUT = Path(__file__).resolve().parent / "issues.frozen.json"


def main() -> int:
    snap = {
        "repo": REPO,
        "pin": PIN,
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "note": "Both arms of the epic-298 measurement MUST read briefs from this file, "
                "never live from gh, or the arms can diverge on their shared input.",
        "issues": {},
    }
    for n in ISSUES:
        proc = subprocess.run(
            ["gh", "issue", "view", str(n), "--repo", REPO,
             "--json", "number,title,body,state,updatedAt"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
        )
        if proc.returncode != 0:
            raise SystemExit(f"gh issue view #{n} failed: {proc.stderr}")
        d = json.loads(proc.stdout)
        if d["state"] != "OPEN":
            raise SystemExit(f"issue #{n} is {d['state']}, expected OPEN")
        snap["issues"][str(n)] = d
        print(f"froze #{n}: {d['title'][:70]} (updated {d['updatedAt']})")

    OUT.write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
