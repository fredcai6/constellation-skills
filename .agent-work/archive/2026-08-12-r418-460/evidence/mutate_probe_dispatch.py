"""Throwaway non-vacuity probe for the DISPATCH-SITE guards: reproduce the exact defect
the gate exists to prevent (an op registered at only one dispatch site; a dispatch chain
with no else) and prove the new tests go RED. Restores the source byte-for-byte."""

import io
import subprocess
import sys
from pathlib import Path

SRC = Path("scripts/apply_episode_delta.py")
ORIGINAL = io.open(SRC, encoding="utf-8", newline="").read()
EOL = "\r\n" if "\r\n" in ORIGINAL else "\n"

DRY_RUN_BRANCH = (
    '        elif kind == "restate-assertion":\n'
    "            log.append(_apply_restate_assertion(tx, op))\n"
    '        elif kind == "retire":\n'
    "            log.append(_apply_retire(tx, op))\n"
    "        else:\n"
    '            raise EpisodeDeltaError(_unhandled_op_kind_message(kind, "_dry_run_log"))\n'
)
APPLY_ELSE = (
    "        else:\n"
    '            raise EpisodeDeltaError(_unhandled_op_kind_message(kind, "apply_delta"))\n'
)
DRY_RUN_ELSE = (
    "        else:\n"
    '            raise EpisodeDeltaError(_unhandled_op_kind_message(kind, "_dry_run_log"))\n'
)

MUTATIONS = {
    # The original defect, exactly: registered at apply_delta, absent from _dry_run_log.
    "restate-not-registered-in-dry-run": (
        DRY_RUN_BRANCH,
        '        elif kind == "retire":\n'
        "            log.append(_apply_retire(tx, op))\n"
        "        else:\n"
        '            raise EpisodeDeltaError(_unhandled_op_kind_message(kind, "_dry_run_log"))\n',
    ),
    "apply_delta-else-removed": (APPLY_ELSE, ""),
    "dry_run-else-removed": (DRY_RUN_ELSE, ""),
}

failed = []
try:
    for name, (old, new) in MUTATIONS.items():
        old, new = old.replace("\n", EOL), new.replace("\n", EOL)
        count = ORIGINAL.count(old)
        if count != 1:
            print(f"MUTATION NOT APPLIED ({name}): anchor matched {count} times", flush=True)
            failed.append(name)
            continue
        mutated = ORIGINAL.replace(old, new)
        assert mutated != ORIGINAL, name
        io.open(SRC, "w", encoding="utf-8", newline="").write(mutated)
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q",
             "tests/test_episode_store.py::RestateAssertionTests"],
            capture_output=True, text=True,
        )
        tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
        verdict = "RED (good)" if proc.returncode != 0 else "GREEN (VACUOUS!)"
        print(f"{name}: exit={proc.returncode} {verdict} :: {tail}", flush=True)
        if proc.returncode == 0:
            failed.append(name)
finally:
    io.open(SRC, "w", encoding="utf-8", newline="").write(ORIGINAL)
    print(
        "restored byte-for-byte:",
        io.open(SRC, encoding="utf-8", newline="").read() == ORIGINAL,
        flush=True,
    )

print("mutations probed:", len(MUTATIONS), "| vacuous or unapplied:", failed)
sys.exit(1 if failed else 0)
