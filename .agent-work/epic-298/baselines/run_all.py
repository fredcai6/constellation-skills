#!/usr/bin/env python
"""Drive all five measured captures (#299), at most 3 concurrent.

Installs the PRE-#304 corpus ONCE and fingerprints it, so every run is measured against
a byte-identical, install-path-invariantly-identified corpus and #307 can prove the post
arm differs from this one only by #304.

Concurrency is capped at 3 per the launch order's budget. Each run gets its OWN pinned
worktree — never two runs in one worktree.
"""
from __future__ import annotations

import importlib.util
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
REPO_ROOT = HERE.parents[2]
ISSUES = [690, 688, 698, 716, 704]
MAX_CONCURRENT = 3
CORPUS_ROOT = Path("C:/Programs/f1bwt/_corpus")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    _eval = _load("run_skill_eval", REPO_ROOT / "scripts" / "run_skill_eval.py")

    marker = CORPUS_ROOT / "skills" / "CORPUS.json"
    if marker.is_file():
        skills_dir = CORPUS_ROOT / "skills"
        corpus_id = json.loads(marker.read_text(encoding="utf-8"))["corpus_id"]
        print(f"[corpus] reusing {skills_dir}")
    else:
        CORPUS_ROOT.mkdir(parents=True, exist_ok=True)
        print(f"[corpus] installing PRE-#304 corpus from {REPO_ROOT} ...")
        skills_dir = Path(_eval.temp_install(str(REPO_ROOT), str(CORPUS_ROOT)))
        corpus_id = _eval.write_stable_corpus_marker(skills_dir, _eval._source_commit())
    print(f"[corpus] id = {corpus_id}")
    print(f"[corpus] source_commit = {_eval._source_commit()}")

    runs_root = HERE / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    pending = list(ISSUES)
    live: list[tuple[int, subprocess.Popen]] = []
    started_at = time.time()

    while pending or live:
        while pending and len(live) < MAX_CONCURRENT:
            n = pending.pop(0)
            out = runs_root / f"run-{n}"
            if (out / "ordering.json").is_file():
                print(f"[#{n}] already captured, skipping")
                continue
            argv = [
                sys.executable, str(HERE / "capture_baseline.py"),
                "--issue", str(n),
                "--worktree", f"C:/Programs/f1bwt/b{n}",
                "--out", str(out),
                "--skills", str(skills_dir),
                "--corpus-id", corpus_id,
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
            ex = subprocess.run(
                [sys.executable, str(HERE / "extract_ordering.py"), str(runs_root / f"run-{n}")],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            print(f"[#{n}] {ex.stdout.strip() or ex.stderr.strip()}")

    print(f"\nall captures done in {time.time() - started_at:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
