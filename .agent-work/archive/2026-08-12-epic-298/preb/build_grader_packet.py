#!/usr/bin/env python
"""Assemble the PRE-B blind-grading packet.

The grader is a separate agent that has NEVER seen the launch order, does not know which
task is the negative control, and does not know that a treatment is under test at all. It
receives the FROZEN rubric's §1-§3 verbatim and the five claimed seams, and nothing else.
The author does not grade the runs.

THE RUBRIC IS NOT EDITED. §1-§3 are sliced out of `../baselines/RUBRIC.md` by heading, byte
for byte, under an assertion that the headings are still where they were. A rubric changed
after an arm exists grades that arm, and that prohibition does not weaken when the change
would be convenient.

`claimed_seam.txt` is the final answer from the last `FILES I WOULD CHANGE` heading to the
end. When the heading is missing the WHOLE final answer is used and the run is flagged
`heading_missing` in the packet, so the grader is never handed a silently truncated claim.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINES = HERE.parent / "baselines"
RUBRIC = BASELINES / "RUBRIC.md"
ISSUES = [690, 688, 698, 716, 704]

SECTION_1 = "## 1. Ground truth"
SECTION_4 = "## 4. Ordering measure"


def rubric_sections() -> str:
    text = RUBRIC.read_text(encoding="utf-8")
    start, end = text.find(SECTION_1), text.find(SECTION_4)
    if start < 0 or end < 0 or end <= start:
        raise SystemExit(
            "RUBRIC.md headings moved - refusing to slice. The grader must receive "
            "sections 1-3 verbatim and the rubric must not be edited to make that work."
        )
    body = text[start:end]
    # The grader sees the scale, not the marginalia about which tier may rule on what.
    return body.rstrip() + "\n"


def final_answer(stream: Path) -> str:
    out = ""
    for line in stream.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "result":
            out = str(ev.get("result") or "")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--runs", default=str(HERE / "runs"))
    p.add_argument("--out", default=str(HERE / "GRADER_PACKET-PREB.md"))
    args = p.parse_args()

    runs = Path(args.runs)
    parts = [
        "# Grading packet\n",
        "You are grading five independent planning outputs against frozen ground truth.\n",
        "Score each one and return, per task: the score, and the quoted words from the\n",
        "claim that decided it. Grade the claimed file list **as written**.\n\n",
        rubric_sections(),
        "\n---\n\n# The five claimed seams, verbatim\n\n",
    ]

    flags: list[str] = []
    for n in ISSUES:
        d = runs / f"run-{n}"
        stream = d / "stream.ndjson"
        if not stream.is_file():
            flags.append(f"#{n}: NO TRANSCRIPT")
            parts.append(f"## Task #{n}\n\n`NOT-CAPTURED` - no transcript.\n\n")
            continue
        answer = final_answer(stream)
        (d / "final_answer.txt").write_text(answer, encoding="utf-8", newline="\n")

        m = None
        for m in re.finditer(r"FILES I WOULD CHANGE", answer, re.IGNORECASE):
            pass
        if m:
            claim = answer[m.start():]
        else:
            claim = answer
            flags.append(f"#{n}: heading_missing - whole final answer used")
        (d / "claimed_seam.txt").write_text(claim, encoding="utf-8", newline="\n")

        note = "" if m else " (no `FILES I WOULD CHANGE` heading; full answer shown)"
        parts.append(f"## Task #{n} - claimed file list, in the plan's own words{note}\n\n"
                     "```\n" + claim.strip() + "\n```\n\n")

    Path(args.out).write_text("".join(parts), encoding="utf-8", newline="\n")
    print(f"written: {args.out}")
    for f in flags:
        print(f"  FLAG {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
