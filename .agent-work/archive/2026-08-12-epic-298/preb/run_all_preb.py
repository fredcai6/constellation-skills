#!/usr/bin/env python
"""Drive the five measured PRE-B captures, at most 3 concurrent.

Installs NOTHING. PRE-B measures the global corpus AS INSTALLED (issue #332: the global
copy shadows any worktree install, so a pinned install does not deliver a pin — it only
makes the treatment look controlled). The corpus is witnessed by fingerprint before the
first run and after the last, by `fingerprint_global_corpus.py`, and this driver refuses
to start unless the BEFORE fingerprint is already on disk.

Each run gets its OWN pinned worktree. Never two runs in one worktree: under the Commander
treatment a leftover `.agent-work/spine.json` would let run N skip the very steps under
measurement.

After each capture: the FROZEN extractor writes `ordering.json`, then `verify_treatment.py`
writes `treatment.json`. A run whose treatment did not verify is a FAILED CAPTURE and is
reported as one — it is not silently retried. Retrying until you get the result you want is
not measurement.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

HERE = Path(__file__).resolve().parent
BASELINES = HERE.parent / "baselines"
REPO_ROOT = HERE.parents[2]
ISSUES = [690, 688, 698, 716, 704]
MAX_CONCURRENT = 3
WORKTREE = "C:/Programs/f1bwt/pb{n}"


def main() -> int:
    before_fp = HERE / "corpus-fingerprint-BEFORE.json"
    if not before_fp.is_file():
        raise SystemExit(f"missing {before_fp} — take the BEFORE fingerprint first")
    fp = json.loads(before_fp.read_text(encoding="utf-8"))
    print(f"[corpus] BEFORE {fp['skillmd_concat_sha256'][:16]} "
          f"({fp['constellation_skill_count']} skills, "
          f"source_commit {(fp['corpus_marker'] or {}).get('source_commit', '?')[:8]})")

    runs_root = HERE / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    pending = list(ISSUES)
    live: list[tuple[int, subprocess.Popen]] = []
    started_at = time.time()

    while pending or live:
        while pending and len(live) < MAX_CONCURRENT:
            n = pending.pop(0)
            out = runs_root / f"run-{n}"
            if (out / "treatment.json").is_file():
                print(f"[#{n}] already captured, skipping")
                continue
            argv = [
                sys.executable, str(HERE / "capture_preb.py"),
                "--issue", str(n),
                "--worktree", WORKTREE.format(n=n),
                "--out", str(out),
                "--model", "claude-opus-5",
            ]
            print(f"[#{n}] launching  ({time.strftime('%H:%M:%S')})")
            live.append((n, subprocess.Popen(argv, cwd=str(REPO_ROOT))))

        time.sleep(5)
        for n, proc in list(live):
            if proc.poll() is None:
                continue
            live.remove((n, proc))
            print(f"[#{n}] capture exited rc={proc.returncode} "
                  f"(+{time.time() - started_at:.0f}s)")
            d = str(runs_root / f"run-{n}")
            for script in (BASELINES / "extract_ordering.py", HERE / "verify_treatment.py"):
                r = subprocess.run([sys.executable, str(script), d],
                                   capture_output=True, text=True,
                                   encoding="utf-8", errors="replace")
                print(f"[#{n}] {r.stdout.strip() or r.stderr.strip()}")

    print(f"\nall captures done in {time.time() - started_at:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
