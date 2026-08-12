#!/usr/bin/env python3
"""Build one measurement arm's scratch directory for gate g4 (DC5), issue #424.

Both arms get a BYTE-IDENTICAL spine so the only difference between them is the
interface the driving agent reaches the engine through. The spine is a real role
spine: it is instantiated from the shipped
`skills/implementer/templates/IMPLEMENTER_PLAN.template.json` -- same `type`,
same `config`, same task field shape -- with five concrete gates whose actions
are trivial file writes, because this gate measures SPINE-MANAGEMENT cost, not
engineering cost.

Usage:
    python3 make_arm.py <arm-dir> [--gauge FILL]
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
TEMPLATE = REPO / "skills" / "implementer" / "templates" / "IMPLEMENTER_PLAN.template.json"

GATES = [
    ("m0-context", "Read this line and attest c1. There is no file to write for this gate.", None),
    ("m1", "Create step1.txt in this spine's own directory, containing exactly STEP1", "step1.txt"),
    ("m2", "Create step2.txt in this spine's own directory, containing exactly STEP2", "step2.txt"),
    ("m3", "Create step3.txt in this spine's own directory, containing exactly STEP3", "step3.txt"),
    ("m4", "Create step4.txt in this spine's own directory, containing exactly STEP4", "step4.txt"),
]


def build_spine(arm_dir: Path) -> dict:
    tpl = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    proto = copy.deepcopy(next(iter(tpl["tasks"].values())))

    tasks = {}
    for tid, imperative, artifact in GATES:
        t = copy.deepcopy(proto)
        t.update({
            "id": tid,
            "title": tid,
            "imperative": imperative,
            "preconditions": [],
            "constraints": [],
            "status": "pending",
            "status_detail": {},
            "result": None,
            "finding": None,
            "evidence": [],
            "rework_count": 0,
        })
        if artifact is None:
            t["postconditions"] = [
                {"id": "c1", "statement": "this gate's imperative was read", "check": None,
                 "satisfied": False}
            ]
        else:
            t["postconditions"] = [
                {"id": "c1", "statement": f"{artifact} exists with the right contents",
                 "check": {"kind": "command",
                           "command": f"test \"$(cat {(arm_dir / artifact).as_posix()})\" = "
                                      f"\"{artifact[:5].upper()}\""},
                 "satisfied": False}
            ]
        t.pop("child_checklist", None)
        t["child_checklist"] = None
        tasks[tid] = t

    return {
        "work_id": "dc5-" + arm_dir.name,
        "type": tpl["type"],
        "config": tpl.get("config", {"rework_cap": 3}),
        "items": [g[0] for g in GATES],
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "tasks": tasks,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arm_dir")
    ap.add_argument("--gauge", type=float, default=None,
                    help="seed a gauge.json with this fill_fraction (DC6 arm only)")
    args = ap.parse_args()

    arm = Path(args.arm_dir).resolve()
    if arm.exists():
        shutil.rmtree(arm)
    arm.mkdir(parents=True)

    (arm / "spine.json").write_text(
        json.dumps(build_spine(arm), indent=2) + "\n", encoding="utf-8")

    if args.gauge is not None:
        (arm / "gauge.json").write_text(json.dumps({
            "schema_version": 1,
            "fill_fraction": args.gauge,
            "model": "claude-opus-4-8",
            "observed_at": datetime.now(timezone.utc).isoformat(),
        }) + "\n", encoding="utf-8")

    print(f"arm ready: {arm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
