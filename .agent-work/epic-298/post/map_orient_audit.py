#!/usr/bin/env python
"""The SECOND WITNESS: did the #304 contract actually fire, and did it fire before source?

WHY THIS EXISTS, AND WHY IT IS NOT A RESCORING
    The frozen extractor's call-level corpus rule credits any call touching `.claude/skills`
    as `skill-corpus` AND NOTHING ELSE. The #304 contract is discharged by invoking
    `~/.claude/skills/constellation-commander/scripts/map_orient.py` — so **the mandated act
    is invisible to the frozen extractor by construction.** That is a property of the
    treatment, not a bug in the extractor, and the extractor is NOT modified.

    So the primary outcome stays exactly what PRE-B measured: `map_before_src`, the boolean
    over genuine `docs/architecture/*` reads, computed by the frozen extractor and reported
    by `discriminate.py`. This script only ADDS a column the primary measure cannot see.

WHY IT RUNS OVER BOTH ARMS
    A column computed only for POST is not comparable to anything. The same code is run over
    PRE-B's archived transcripts, where it should report zero invocations by construction
    (that corpus predates `map_orient.py` entirely). PRE-B is therefore this script's own
    negative control: a non-zero PRE-B count would mean the script is matching noise, and the
    POST column would have to be thrown out with it.

WHAT IT DECIDES
    The pre-registered three-way needs to separate *insufficient* (contract loaded, order did
    not move) from *irrelevant* (contract never reached the agent). `verify_treatment.py`
    proves the Commander LOADED. This proves the contract's own instrument RAN, and whether
    it ran before the first source read — the anchor #304 is built on.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAP_ORIENT_RE = re.compile(r"map_orient(?:\.py)?\b")
SUBCOMMAND_RE = re.compile(r"map_orient(?:\.py)?[^\n]*?\b(orient|verify-orientation|verify-frame)\b")
VERDICT_RE = re.compile(r"\b(RESOLVED|DEGRADED-NO-MAP|DEGRADED-EMPTY-MAP|DEGRADED-UNPARSEABLE|"
                        r"UNRESOLVABLE-ROOT|FRAME-OK|FRAME-MISSING|FRAME-REFUSED)\b")

NO_MAP_ORIENT = "NO-MAP-ORIENT-CALL"
NO_SRC_READ = "NO-SRC-READ"


def events(path: Path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except ValueError:
            continue


def audit(run_dir: Path) -> dict:
    stream = run_dir / "stream.ndjson"
    if not stream.is_file():
        return {"run": run_dir.name, "status": "NOT-CAPTURED", "reason": "no transcript"}

    calls: list[dict] = []
    invocations: list[dict] = []
    verdicts: list[str] = []
    pending: dict[str, int] = {}

    for ev in events(stream):
        if ev.get("type") == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                idx = len(calls)
                blob = json.dumps(b.get("input") or {})
                calls.append({"index": idx, "tool": b.get("name")})
                if MAP_ORIENT_RE.search(blob):
                    sub = SUBCOMMAND_RE.search(blob)
                    invocations.append({
                        "index": idx,
                        "tool": b.get("name"),
                        "subcommand": sub.group(1) if sub else "unknown",
                        "excerpt": blob[:300],
                    })
                    if b.get("id"):
                        pending[b["id"]] = idx
        elif ev.get("type") == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_result":
                    continue
                if b.get("tool_use_id") not in pending:
                    continue
                text = json.dumps(b.get("content"))
                for m in VERDICT_RE.finditer(text):
                    verdicts.append(f"call{pending[b['tool_use_id']]}:{m.group(1)}")

    # `first_src_read_index` comes from the FROZEN extractor, never recomputed here — the
    # whole point is that this column sits alongside the frozen measure on the same axis.
    order_p = run_dir / "ordering.json"
    first_src = None
    first_map = None
    captured = False
    if order_p.is_file():
        order = json.loads(order_p.read_text(encoding="utf-8"))
        captured = bool(order.get("captured"))
        fs = order.get("first_src_read_index")
        fm = order.get("first_map_read_index")
        first_src = fs if isinstance(fs, int) else None
        first_map = fm if isinstance(fm, int) else None

    orient_calls = [i for i in invocations if i["subcommand"] in ("orient", "unknown")]
    first_orient = orient_calls[0]["index"] if orient_calls else None

    if first_orient is None:
        before_src = NO_MAP_ORIENT
    elif first_src is None:
        before_src = NO_SRC_READ
    else:
        before_src = first_orient < first_src

    return {
        "run": run_dir.name,
        "status": "ok" if captured else "NOT-CAPTURED",
        "tool_call_count": len(calls),
        "map_orient_invocation_count": len(invocations),
        "map_orient_indices": [i["index"] for i in invocations],
        "map_orient_subcommands": [i["subcommand"] for i in invocations],
        "map_orient_verdicts": verdicts,
        "first_map_orient_index": first_orient if first_orient is not None else NO_MAP_ORIENT,
        "first_src_read_index": first_src if first_src is not None else NO_SRC_READ,
        "first_map_read_index": first_map if first_map is not None else "NO-MAP-READ",
        "map_orient_before_src": before_src,
        "invocations": invocations,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dirs", nargs="+")
    p.add_argument("--out", default=None)
    p.add_argument("--expect-zero", action="store_true",
                   help="negative-control mode: exit 1 if ANY run shows a map_orient call")
    args = p.parse_args()

    rows = [audit(Path(d)) for d in args.run_dirs]

    # RULE: a guard that loops must assert WHAT IT LOOPED OVER. Without this line a typo in
    # a glob that expands to nothing prints a clean table and reports success over zero runs.
    print(f"enumerated {len(rows)} run dir(s): {', '.join(r['run'] for r in rows)}")
    if not rows:
        print("REFUSED: zero run dirs enumerated — there is nothing to audit")
        return 1

    hdr = (f"{'run':<12} {'calls':>5} {'mo_calls':>8} {'first_mo':>18} "
           f"{'first_src':>11} {'mo<src':>18} {'verdicts':<40}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if r["status"] == "NOT-CAPTURED":
            print(f"{r['run']:<12} NOT-CAPTURED")
            continue
        print(f"{r['run']:<12} {r['tool_call_count']:>5} "
              f"{r['map_orient_invocation_count']:>8} "
              f"{str(r['first_map_orient_index']):>18} "
              f"{str(r['first_src_read_index']):>11} "
              f"{str(r['map_orient_before_src']):>18} "
              f"{','.join(r['map_orient_verdicts'])[:40]:<40}")

    total = sum(r.get("map_orient_invocation_count", 0) for r in rows)
    print(f"\ntotal map_orient invocations across {len(rows)} run(s): {total}")

    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
        print(f"written: {args.out}")

    if args.expect_zero and total:
        print(f"NEGATIVE CONTROL FAILED: expected 0 map_orient invocations, found {total} — "
              "this script is matching noise and its POST column cannot be trusted")
        return 1
    if args.expect_zero:
        print(f"negative control PASSED: 0 invocations across {len(rows)} pre-#304 run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
