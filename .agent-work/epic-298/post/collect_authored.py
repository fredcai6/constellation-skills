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

SCOPE IS DECLARED — AND THE FIRST VERSION DID NOT DECLARE IT. That cost 15,456 files.
    f1Brainz TRACKS `.agent-work/`, so a worktree at the pin already contains ~13 work areas
    belonging to unrelated issues (`623-headless-deadlock`, `601-stage1-pregrease`, ...). The
    first version copied EVERY directory under `.agent-work/`, so each run archived the whole
    work area it happened to be sitting in — handoffs, implementer plans and verification JSON
    for issues this arm never touched. One file, `verify_prefix.json`, is 60,716 lines and
    landed five times. **None of that is evidence about map ordering; it is the debris of the
    repository the subject was working in.**

    PRE-B's archive holds 62 files for the same five runs. This one held 15,456. **The entire
    difference is undeclared scope** — not a different measurement, just a collector that took
    everything it could see.

    So the subject's OWN work area is now identified POSITIVELY: it is the directory that did
    not exist at the pin, which `git status --porcelain` reports as untracked. Everything else
    belongs to the host repo and is not this arm's to archive. **A capture with no declared
    scope is the collection-side twin of an assertion with no declared subject.**
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
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
        present = sorted(d for d in aw.iterdir() if d.is_dir()) if aw.is_dir() else []

        # DECLARED SCOPE: only what this subject CREATED. Untracked == did not exist at the
        # pin == authored by the run. Everything else is the host repo's own tracked content.
        untracked = subprocess.run(
            ["git", "-C", str(wt), "status", "--porcelain", "--", ".agent-work"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stdout
        authored_names = {
            line[3:].strip().strip('"').replace("\\", "/").split("/")[1]
            for line in untracked.splitlines()
            if line.startswith("??") and "/" in line[3:]
        }
        work_dirs = [d for d in present if d.name in authored_names]

        row["agent_work_dirs_present"] = len(present)
        row["agent_work_dirs_authored"] = [d.name for d in work_dirs]
        row["agent_work_dirs_skipped_as_host_content"] = len(present) - len(work_dirs)

        # THE WITNESS IS SCOPED TO THE SUBJECT'S OWN DIRECTORIES, and the first version was
        # NOT — it rglob'd the whole `.agent-work/`, which at this pin already contains 113
        # `spine.json`, 98 `execute.json` and 35 `MISSION_FRAME.md` belonging to the HOST repo.
        # So `spine_materialized` was `bool(81 paths)` on every run no matter what the subject
        # did: **a check that could not fail**, sitting inside the instrument built to detect
        # delivery failures. It is this epic's own costume family, aimed at the measuring rig.
        #
        # `map-orientation.json` is the exception and the reason the arm survived it: there are
        # ZERO at the pin, so that field could only ever have been produced by the subject. It
        # is the one witness here that was load-bearing as originally written.
        def _own(pattern: str) -> list[str]:
            hits: list[str] = []
            for d in work_dirs:
                hits += [str(s.relative_to(wt)).replace("\\", "/") for s in d.rglob(pattern)]
            return sorted(hits)

        spines = _own("spine.json")
        row["spine_json_paths"] = spines
        row["spine_materialized"] = bool(spines)
        row["frame_written"] = bool(_own("MISSION_FRAME.md"))
        row["execute_json_written"] = bool(_own("execute.json"))
        row["map_orientation_receipt"] = _own("map-orientation.json")
        # Recorded so a future reader can see the check is scoped rather than trust that it is.
        row["host_files_excluded_from_witness"] = {
            "spine.json": len(list(aw.rglob("spine.json"))) - len(spines) if aw.is_dir() else 0,
        }

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
