#!/usr/bin/env python
"""Drive the five measured POST captures — the Commander-loaded POST-#304 arm (epic #298).

DERIVED FROM `../preb/run_all_preb.py`, NOT REWRITTEN. It differs in four values and
nothing else: the worktree path template, the runs root, the fingerprint it demands, and
the `--arm POST` label. The capture itself is `../preb/capture_preb.py` unmodified apart
from that label flag, and the three scorers are the PRE-B files invoked in place.

WHY REUSE IS THE METHOD AND NOT A CONVENIENCE
    POST pairs with PRE-B. If POST were scored by new code, a PRE-B/POST difference would
    have two candidate causes — the treatment, or the scorer — and the arm could not tell
    them apart. Rebuilding the instrument would destroy the only comparison the arm exists
    to make.

THE ONE VARIABLE
    PRE-B ran against corpus `74953936` (pre-#304). POST runs against `3595955`, which
    `git merge-base --is-ancestor 5d2585b` proves contains #304 and `9a0cb17` proves
    contains its post-archive fix. Brief bytes, argv, model, pin, task set and env scrub
    are byte-identical. The corpus is the treatment.

Each run gets its OWN pinned worktree, for the same reason PRE-B did: a leftover
`.agent-work/spine.json` would let run N skip the very steps under measurement.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

HERE = Path(__file__).resolve().parent
PREB = HERE.parent / "preb"
BASELINES = HERE.parent / "baselines"
REPO_ROOT = HERE.parents[2]
ISSUES = [690, 688, 698, 716, 704]
MAX_CONCURRENT = 3
WORKTREE = "C:/Programs/f1bwt/post{n}"


def acquire_lock() -> Path:
    """Refuse to start if another driver is already running. EARNED, not precautionary.

    The first POST attempt was launched twice: a shell one-liner whose backgrounded `nohup`
    SUCCEEDED while a later line in the same compound command failed, so the launch *looked*
    like it had failed and was retried. Two drivers then raced into the same run directories
    and the same log. The damage was not subtle and it was not obvious either — three
    transcripts ended up with TWO distinct `session_id`s, TWO `result` events and malformed
    JSON lines apiece, while `meta.json` reported `exit=0` and a plausible elapsed time.

    A capture that two processes wrote is not a capture. `O_CREAT|O_EXCL` makes the second
    driver die loudly at second zero instead of silently corrupting an $57 arm.
    """
    lock = HERE / "run_all_post.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(
            f"REFUSED: {lock} exists — another driver is running (or died holding it).\n"
            f"  Its contents: {lock.read_text(encoding='utf-8', errors='replace').strip()}\n"
            "  Two drivers writing one run directory produce transcripts with two session_ids\n"
            "  and two result events. If you are certain no driver is alive, delete the lock."
        )
    os.write(fd, f"pid={os.getpid()} started={time.strftime('%Y-%m-%dT%H:%M:%S')}\n".encode())
    os.close(fd)
    return lock


def main() -> int:
    lock = acquire_lock()
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
                sys.executable, str(PREB / "capture_preb.py"),
                "--issue", str(n),
                "--worktree", WORKTREE.format(n=n),
                "--out", str(out),
                "--model", "claude-opus-5",
                "--arm", "POST",
            ]
            # PER-RUN CORPUS WITNESS, not just one at the top of the arm.
            #
            # The treatment lives on a MUTABLE GLOBAL (`~/.claude/skills`) that sibling
            # agents in this session are standing-pre-cleared to re-install into. A single
            # BEFORE/AFTER pair cannot tell "stable throughout" from "changed and changed
            # back", and a re-install that rewrites `templates/` or `scripts/` — which is
            # exactly where the contract under test lives — moves no `SKILL.md` at all.
            # Five per-run digests make poolability an assertion instead of a hope.
            out.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [sys.executable, str(PREB / "fingerprint_global_corpus.py"),
                 "--out", str(out / "corpus-at-launch.json")],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
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
            for script in (BASELINES / "extract_ordering.py", PREB / "verify_treatment.py"):
                r = subprocess.run([sys.executable, str(script), d],
                                   capture_output=True, text=True,
                                   encoding="utf-8", errors="replace")
                print(f"[#{n}] {r.stdout.strip() or r.stderr.strip()}")

    print(f"\nall captures done in {time.time() - started_at:.0f}s")
    lock.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
