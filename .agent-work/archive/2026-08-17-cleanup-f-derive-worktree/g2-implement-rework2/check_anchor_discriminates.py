"""C5 — the new positive anchor can actually fail.

The anchor exists so the file is not a set of pure absence assertions, which
would pass against an empty engine source. That claim is only worth anything if
removing the anchored construct turns the test RED. So: rename `MUTATING_VERBS`
at its definition in `scripts/checklist_engine.py`, assert the mutation applied,
run the test, restore, assert byte-identical, run it green again.

The mutation is a rename rather than a deletion because deleting the set would
break the engine's import and the test would go red for the wrong reason -- the
question here is whether the ANCHOR discriminates, not whether Python runs.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "scripts" / "checklist_engine.py"
TEST = ("tests/test_spine_origin_isolation.py::"
        "TheEngineTakesNoAmbientReading::"
        "test_the_retired_predicate_and_its_verb_sets_are_gone_from_a_real_engine")
SCRUB = ["env", "-u", "SPINE_FILE", "-u", "SPINE_SESSION", "-u", "SPINE_PARENT",
         "-u", "CREW_SCRATCH_DIR"]


def run() -> subprocess.CompletedProcess:
    return subprocess.run(SCRUB + ["py", "-m", "pytest", "-q", TEST],
                          cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    original = ENGINE.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    failures: list[str] = []

    green = run()
    print(f"[1] anchored test, unmutated: rc={green.returncode} :: "
          f"{green.stdout.strip().splitlines()[-1]}")
    if green.returncode != 0:
        failures.append("the anchored test is not green before the mutation")

    source = original.decode("utf-8")
    mutated = source.replace("MUTATING_VERBS = {", "MUTATING_VERBS_RENAMED = {", 1)
    if mutated == source:
        print("FAIL: the rename matched nothing -- the anchor is not where the "
              "test says it is", file=sys.stderr)
        return 1
    ENGINE.write_text(mutated, encoding="utf-8", newline="")
    print(f"[2] rename applied: `MUTATING_VERBS = {{` present = "
          f"{'MUTATING_VERBS = {' in ENGINE.read_text(encoding='utf-8')}")

    try:
        red = run()
        print(f"[3] with the anchor renamed away: rc={red.returncode}")
        for line in (red.stdout + red.stderr).strip().splitlines()[-3:]:
            print(f"    | {line}")
        if red.returncode == 0:
            failures.append("the anchored test PASSED with the anchor gone -- "
                            "it cannot fail, so it proves nothing")
    finally:
        ENGINE.write_bytes(original)

    after = hashlib.sha256(ENGINE.read_bytes()).hexdigest()
    print(f"[4] restored byte-identical: {before == after} ({after[:12]})")
    if before != after:
        failures.append("the engine was NOT restored byte-identical")

    restored = run()
    print(f"[5] after restore: rc={restored.returncode} :: "
          f"{restored.stdout.strip().splitlines()[-1]}")
    if restored.returncode != 0:
        failures.append("the anchored test is not green after restoring")

    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("\nOK: the anchor discriminates -- green, red without it, green again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
