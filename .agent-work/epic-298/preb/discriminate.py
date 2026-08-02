#!/usr/bin/env python
"""The DISCRIMINATED measures — reading the map vs orienting by it.

These, not the naive ordering measure, are the ones that matter, and they are what PRE-B
has to be comparable to on the POST side. Derived entirely from artifacts already written
by the FROZEN `extract_ordering.py` (`ordering.json`) plus the transcript's final answer.
The extractor is not modified and the rubric is not touched.

DEFINITIONS ARE STATED HERE BECAUSE PRE-A's WERE NOT MECHANISED
    The PRE-A addendum reports the same four discriminators, but two of its columns
    (`map-sourced cues in plan`, `src precision`) were HAND-derived and cannot be
    reproduced from the archived arrays by any single rule. Rather than reverse-engineer a
    judgement call, this script fixes an explicit mechanical definition for each and
    applies the SAME code to PRE-A and PRE-B, so the recomputed PRE-A column is published
    alongside the addendum's published one and the divergence is visible instead of hidden.

    Consequence, and it is load-bearing: **compare PRE-B's numbers to POST's computed by
    this script.** Do not compare them to the addendum's published columns.

  1. `read_at_bootstrap` - first map access at tool-call index < 3, i.e. before any
     task-driven crawl could have begun. Strict on purpose: the question is whether the
     map was the STARTING POINT, and any looser threshold blurs "started there" into
     "got there early".
  2. `map_before_src` - taken verbatim from the frozen extractor. Not recomputed.
  3. `returned_to_map_after_src` - at least one map access at an index greater than the
     first source access. This is the signal that a read is USE rather than ritual: a
     ritual read is one touch and never again.
  4. `map_cues_in_plan` - of the distinct map artifacts the run ACTUALLY READ, how many
     are cited by name in the final answer. Reported `cited/read`, so a run that read
     little and cited all of it is not flattered by a raw count.
  5. `src_precision` - `named/opened`: distinct extension-bearing `src/...` paths in the
     final `FILES I WOULD CHANGE` list, over distinct extension-bearing `src/...` paths
     the run opened.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BOOTSTRAP_WINDOW = 3
NO_MAP_READ = "NO-MAP-READ"
NO_SRC_READ = "NO-SRC-READ"
NOT_CAPTURED = "NOT-CAPTURED"

# Negative lookbehind on word characters and dots, NOT on `/`. Two bugs were found here
# against real data and both are worth the comment:
#   * a delimiter WHITELIST silently drops a path in backticks, the commonest form a plan
#     actually uses - that cost 3 of PRE-A's 5 numerators;
#   * including `/` in the lookbehind silently drops every ABSOLUTE path
#     (`C:/Programs/f1bwt/pb698/src/physics/x.py`) - PRE-A's subjects happened to use
#     relative paths, PRE-B's Commander-driven subjects use absolute ones, and that cost
#     run-698 its entire opened-file count until it was caught.
# The guard's only real job is to exclude corpus paths, which is done explicitly below,
# and for the `opened` count is already done by the frozen extractor's `src` bucket.
SRC_FILE_RE = re.compile(r"(?<![\w.\-])(src/[\w/.-]*\.\w+)")
CORPUS_SRC_RE = re.compile(r"\.claude/skills[\w/.-]*?/(src/[\w/.-]*\.\w+)")


def _src_paths(text: str) -> set[str]:
    """Extension-bearing `src/...` paths in `text`, minus any that live under a corpus."""
    norm = text.replace("\\", "/")
    return set(SRC_FILE_RE.findall(norm)) - set(CORPUS_SRC_RE.findall(norm))
PLAN_HEADING_RE = re.compile(r"FILES I WOULD CHANGE", re.IGNORECASE)


def final_answer(stream: Path) -> str:
    text = ""
    if not stream.is_file():
        return text
    for line in stream.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "result":
            text = str(ev.get("result") or "")
    return text


def discriminate(run_dir: Path) -> dict:
    order_p = run_dir / "ordering.json"
    if not order_p.is_file():
        return {"run": run_dir.name, "status": NOT_CAPTURED}
    order = json.loads(order_p.read_text(encoding="utf-8"))
    if not order.get("captured"):
        return {"run": run_dir.name, "status": NOT_CAPTURED}

    calls = order["calls"]
    map_idx = [c["index"] for c in calls if "map" in c["buckets"]]
    src_idx = [c["index"] for c in calls if "src" in c["buckets"]]
    first_map = map_idx[0] if map_idx else None
    first_src = src_idx[0] if src_idx else None

    answer = final_answer(run_dir / "stream.ndjson")
    norm_answer = answer.replace("\\", "/")

    # 4 - map cues.
    read_artifacts: list[str] = []
    for c in calls:
        for mp in c.get("map_paths", []):
            if mp not in read_artifacts:
                read_artifacts.append(mp)
    # A bare `docs/architecture/` directory touch is not a citable artifact.
    citable = [a for a in read_artifacts if a.rstrip("/") != "docs/architecture"]
    cited = [a for a in citable
             if a in norm_answer or Path(a).name in norm_answer]

    # 5 - src precision.
    opened: set[str] = set()
    for c in calls:
        if "src" not in c["buckets"]:
            continue
        opened |= _src_paths(c.get("target", ""))

    m = None
    for m in PLAN_HEADING_RE.finditer(norm_answer):
        pass
    named = _src_paths(norm_answer[m.start():]) if m else set()

    return {
        "run": run_dir.name,
        "status": "ok",
        "tool_call_count": order["tool_call_count"],
        "first_map_read_index": order["first_map_read_index"],
        "first_src_read_index": order["first_src_read_index"],
        "map_before_src": order["map_before_src"],
        "map_call_count": len(map_idx),
        "map_call_indices": map_idx,
        "read_at_bootstrap": (
            NO_MAP_READ if first_map is None else first_map < BOOTSTRAP_WINDOW
        ),
        "returned_to_map_after_src": (
            NO_MAP_READ if first_map is None
            else NO_SRC_READ if first_src is None
            else any(i > first_src for i in map_idx)
        ),
        "map_artifacts_read": read_artifacts,
        "map_cues_in_plan": f"{len(cited)}/{len(citable)}",
        "map_cues_cited": sorted(cited),
        "plan_heading_present": bool(m),
        "src_precision": (
            "n/a" if not opened and not named else f"{len(named)}/{len(opened)}"
        ),
        "src_named_in_plan": sorted(named),
        "src_opened": sorted(opened),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dirs", nargs="+")
    p.add_argument("--out", default=None, help="write the collected rows to this JSON file")
    args = p.parse_args()

    rows = [discriminate(Path(d)) for d in args.run_dirs]
    hdr = (f"{'run':<12} {'calls':>5} {'boot':>6} {'m<s':>6} {'return':>7} "
           f"{'mapcalls':>8} {'cues':>7} {'srcprec':>8}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if r["status"] != "ok":
            print(f"{r['run']:<12} {r['status']}")
            continue
        print(f"{r['run']:<12} {r['tool_call_count']:>5} "
              f"{str(r['read_at_bootstrap']):>6} {str(r['map_before_src']):>6} "
              f"{str(r['returned_to_map_after_src']):>7} {r['map_call_count']:>8} "
              f"{r['map_cues_in_plan']:>7} {r['src_precision']:>8}")

    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
        print(f"\nwritten: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
