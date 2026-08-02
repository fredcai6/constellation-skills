#!/usr/bin/env python
"""Archive each subject's own `.agent-work/<work-id>/` into its run dir as `authored/`.

Two reasons, and the second is the load-bearing one.

1. ARCHIVE PARITY with PRE-B, whose `runs/run-<N>/authored/` holds the mission frame,
   `execute.json` and spine the subject wrote. Without it the arms are not comparable as
   archives even when they are comparable as measurements.

2. FILESYSTEM WITNESS FOR HOP 1 (#393). The `contract_delivered` column in
   `map_orient_audit.py` reads the transcript. This reads the worktree. They are independent
   oracles for the same question — did a spine actually get materialized, i.e. did the #304
   contract text ever reach this subject — and an agreement between two independent oracles
   is worth much more than either alone. A `spine.json` on disk cannot be produced by a
   subject that only talked about spines.

The worktrees are swept at archive, so this must run BEFORE the sweep. It copies; it never
moves, and it never writes into the worktree.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ISSUES = [690, 688, 698, 716, 704]
WORKTREE = "C:/Programs/f1bwt/post{n}"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--runs-root", default=str(HERE / "runs"))
    p.add_argument("--out", default=str(HERE / "spine-materialization.json"))
    args = p.parse_args()

    runs_root = Path(args.runs_root)
    rows = []
    print(f"enumerating {len(ISSUES)} worktree(s): {ISSUES}")
    for n in ISSUES:
        wt = Path(WORKTREE.format(n=n))
        run_dir = runs_root / f"run-{n}"
        row: dict = {"issue": n, "worktree": str(wt), "worktree_exists": wt.is_dir()}

        aw = wt / ".agent-work"
        work_dirs = sorted(d for d in aw.iterdir() if d.is_dir()) if aw.is_dir() else []
        row["agent_work_dirs"] = [d.name for d in work_dirs]

        spines = sorted(str(s.relative_to(wt)).replace("\\", "/")
                        for s in aw.rglob("spine.json")) if aw.is_dir() else []
        row["spine_json_paths"] = spines
        # THE WITNESS: a spine on disk means the template was materialized, so the contract
        # text reached this subject. Absent, hop 1 did not happen and a zero map_orient count
        # means "never delivered", not "delivered and ignored".
        row["spine_materialized"] = bool(spines)
        row["frame_written"] = bool(list(aw.rglob("MISSION_FRAME.md"))) if aw.is_dir() else False
        row["execute_json_written"] = bool(list(aw.rglob("execute.json"))) if aw.is_dir() else False
        row["map_orientation_receipt"] = sorted(
            str(s.relative_to(wt)).replace("\\", "/")
            for s in aw.rglob("map-orientation.json")) if aw.is_dir() else []

        if run_dir.is_dir() and work_dirs:
            dest = run_dir / "authored"
            if dest.exists():
                shutil.rmtree(dest)
            dest.mkdir(parents=True)
            for d in work_dirs:
                shutil.copytree(d, dest / d.name)
            row["archived_to"] = str(dest)
        else:
            row["archived_to"] = None

        print(f"  post{n}: work_dirs={row['agent_work_dirs']} "
              f"spine={row['spine_materialized']} frame={row['frame_written']} "
              f"execute={row['execute_json_written']} "
              f"receipts={len(row['map_orientation_receipt'])}")
        rows.append(row)

    # A guard that loops must assert what it looped over.
    print(f"enumerated {len(rows)} of {len(ISSUES)} expected worktrees")
    if len(rows) != len(ISSUES):
        print("REFUSED: did not enumerate the full task set")
        return 1
    materialized = sum(1 for r in rows if r["spine_materialized"])
    receipts = sum(1 for r in rows if r["map_orientation_receipt"])
    print(f"spine materialized (hop 1, filesystem witness): {materialized} of {len(rows)}")
    print(f"map-orientation receipt on disk (hop 2 witness): {receipts} of {len(rows)}")

    Path(args.out).write_text(json.dumps(rows, indent=2) + "\n",
                              encoding="utf-8", newline="\n")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
