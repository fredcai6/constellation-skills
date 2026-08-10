#!/usr/bin/env python3
"""Positive controls for the scorer itself (gate g4, issue #424).

Every counter in `score_arm.py` that reports ZERO in the real arms is exercised
here on a synthetic record built to make it fire. A counter that cannot fire
reports zero for a reason that has nothing to do with the arms, and its zero
would mean nothing -- the same argument DC3's positive control rests on.

Run: python3 control_scorer.py   (exits non-zero if any control fails)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_arm import score  # noqa: E402

ENGINE = "python3 scripts/checklist_engine.py"


def rec(events: list[dict]) -> Path:
    d = Path(tempfile.mkdtemp())
    (d / "record.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    return d


def use(uid: str, name: str, inp: dict) -> dict:
    return {"type": "assistant",
            "message": {"content": [{"type": "tool_use", "id": uid,
                                     "name": name, "input": inp}]}}


def res(uid: str, text: str, is_error: bool = False) -> dict:
    return {"type": "user",
            "message": {"content": [{"type": "tool_result", "tool_use_id": uid,
                                     "is_error": is_error, "content": text}]}}


CONTROLS: list[tuple[str, list[dict], str, int]] = [
    (
        "shape_error fires on an argparse rejection",
        [use("a", "Bash", {"command": f"{ENGINE} advance --file x"}),
         res("a", "usage: checklist_engine.py\nerror: unrecognized arguments: --file")],
        "shape_errors", 1,
    ),
    (
        "shape_error fires on a client-side schema rejection (MCP arm)",
        [use("a", "mcp__spine__spine_advance", {"task_id": 7}),
         res("a", "Input validation error: task_id is not a valid string", True)],
        "shape_errors", 1,
    ),
    (
        "far_side fires when a Bash inspection follows a failed attempt",
        [use("a", "Bash", {"command": f"{ENGINE} advance --file x"}),
         res("a", "usage: checklist_engine.py\nerror: argument bad"),
         use("b", "Bash", {"command": "cat spine.json"}),
         res("b", "{...}")],
        "far_side_recoveries", 1,
    ),
    (
        "far_side fires when a Read inspection follows a failed attempt",
        [use("a", "mcp__spine__spine_start", {}),
         res("a", "Input validation error: required property task_id", True),
         use("b", "Read", {"file_path": "spine.json"}),
         res("b", "{...}")],
        "far_side_recoveries", 1,
    ),
    (
        "the loop correction counts runtime invocations, not static text",
        [use("a", "Bash", {"command": "for c in claim start advance; do "
                                      f"{ENGINE} $c --help; done"}),
         res("a", "usage: checklist_engine.py claim\nusage: checklist_engine.py start\n"
                  "usage: checklist_engine.py advance")],
        "invocation_attempts", 3,
    ),
    (
        "a state refusal is NOT scored as a fumble",
        [use("a", "Bash", {"command": f"{ENGINE} --file x start m1"}),
         res("a", "REFUSED: m1: preconditions unmet ['p1']")],
        "absorbable_fumbles", 0,
    ),
    (
        "reached_done fires only on the engine's own done line",
        [use("a", "mcp__spine__spine_status", {}),
         res("a", "DONE: no open items.")],
        "reached_done", True,
    ),
]


def main() -> int:
    failures = []
    for name, events, field, expected in CONTROLS:
        got = score(rec(events))[field]
        ok = got == expected
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {field}={got} (expected {expected})")
        if not ok:
            failures.append(name)
    if failures:
        print(f"\n{len(failures)} control(s) FAILED", file=sys.stderr)
        return 1
    print(f"\nall {len(CONTROLS)} scorer controls fire: every counter that reports "
          f"zero in the real arms is capable of reporting non-zero")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
