#!/usr/bin/env python
"""Read out the PROBE-331 question from a captured transcript.

The frozen `extract_ordering.py` is NOT touched — it is the #299 instrument and this
probe reuses it verbatim for the ordering measure. This script answers only the three
questions `extract_ordering.py` was never built to answer:

  1. Was `Skill` invoked at all, and at what tool-call index?
  2. WHICH corpus copy served each invocation (issue #332)?
  3. Did the run write anything, anywhere?

On (2), two independent witnesses are reported and required to agree:

  * `base_dir`  — Claude Code prefixes loaded skill content with a literal
    `Base directory for this skill: <absolute path>` line. This names the serving copy
    outright and is the primary readout. It was discovered while validating the sentinel
    and is strictly better than it: it is emitted by the harness rather than planted, so
    it cannot be defeated by content truncation.
  * `sentinel`  — the planted token, present ONLY in the worktree corpus copy. Absent
    from a loaded body means a copy without the token served it.

On (3), a worktree-scoped `git status` proves nothing about writes OUTSIDE the worktree
(BASELINE_RECORD.md states this correction explicitly). The load-bearing evidence is that
no file-writing tool was invoked at all, anywhere, and that no forbidden git/gh operation
appears in any call. Both are counted here across the full transcript.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WRITE_TOOLS = ("Write", "Edit", "NotebookEdit", "MultiEdit")
FORBIDDEN = (
    re.compile(r"\bgit\s+push\b"),
    re.compile(r"\bgh\s+pr\s+create\b"),
    re.compile(r"\bgh\s+issue\s+(comment|create|edit)\b"),
    re.compile(r"\bgit\s+commit\b"),
)
BASE_DIR_RE = re.compile(r"Base directory for this skill:\s*(.+)")


def events(path: Path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue


def analyze(stream: Path, sentinel: str) -> dict:
    raw = stream.read_text(encoding="utf-8", errors="replace")
    calls: list[dict] = []
    skill_calls: list[dict] = []
    write_calls: list[dict] = []
    forbidden: list[dict] = []
    init_skills: list[str] = []
    served_by: list[str] = []
    truncated = not raw.endswith("\n") and bool(raw)

    for ev in events(stream):
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            init_skills = ev.get("skills") or []
        if ev.get("type") == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                rec = {"index": len(calls), "tool": b.get("name"), "input": b.get("input")}
                calls.append(rec)
                if rec["tool"] == "Skill":
                    skill_calls.append(rec)
                if rec["tool"] in WRITE_TOOLS:
                    write_calls.append(rec)
                blob = json.dumps(b.get("input") or {})
                if any(p.search(blob) for p in FORBIDDEN):
                    forbidden.append(rec)
        if ev.get("type") == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "text":
                    m = BASE_DIR_RE.search(b.get("text") or "")
                    if m:
                        served_by.append(m.group(1).strip())

    from collections import Counter
    con = [s for s in init_skills if s.startswith("constellation-")]
    dupes = {k: v for k, v in Counter(con).items() if v > 1}

    return {
        "transcript_complete": not truncated,
        "tool_call_count": len(calls),
        "skill_invocations": len(skill_calls),
        "skill_calls": [{"index": c["index"], "input": c["input"]} for c in skill_calls],
        "served_by_base_dir": served_by,
        "sentinel_occurrences_in_transcript": raw.count(sentinel),
        "init_constellation_entries": len(con),
        "init_duplicated_names": len(dupes),
        "write_tool_calls": len(write_calls),
        "write_tool_detail": [{"index": c["index"], "tool": c["tool"]} for c in write_calls],
        "forbidden_operations": [{"index": c["index"], "tool": c["tool"]} for c in forbidden],
        "tool_histogram": dict(Counter(c["tool"] for c in calls).most_common()),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    p.add_argument("--sentinel", required=True)
    args = p.parse_args()
    run = Path(args.run_dir)
    out = analyze(run / "stream.ndjson", args.sentinel)
    (run / "probe_readout.json").write_text(json.dumps(out, indent=2) + "\n",
                                            encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
