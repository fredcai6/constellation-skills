"""C3 — the deletion test, applied by hand, in both directions.

The claim: `_require` + `IMPLEMENTATIONS` still fail the WHOLE file loudly if the
surviving implementation disappears, rather than quietly shrinking the
parametrization. A table that silently stopped checking its one copy would be
the check-that-cannot-fail it exists to prevent.

So: excise `spine_rail._worktree_from_spine` outright, assert the excision
actually applied, show collection of `tests/test_worktree_derivation.py` FAIL
with `_require`'s own message, restore, assert the file is byte-identical again,
and show it green. A mutation that silently matched nothing would leave a green
run reading exactly like a passing guard, so the excision is asserted before the
measurement, not after.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / "scripts" / "hooks" / "spine_rail.py"
TARGET = "tests/test_worktree_derivation.py"
PYTEST = ["py", "-m", "pytest", "-q", TARGET]
SCRUB = ["env", "-u", "SPINE_FILE", "-u", "SPINE_SESSION", "-u", "SPINE_PARENT",
         "-u", "CREW_SCRATCH_DIR"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(extra: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(SCRUB + PYTEST + extra, cwd=ROOT,
                          capture_output=True, text=True)


def excise(source: str) -> str:
    """Remove the whole `_worktree_from_spine` definition, top-level def to def."""
    lines = source.splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines) if l.startswith("def _worktree_from_spine("))
    end = next(i for i, l in enumerate(lines[start + 1:], start + 1) if l.startswith("def "))
    return "".join(lines[:start] + lines[end:])


def main() -> int:
    original = HOOK.read_bytes()
    before = digest(HOOK)
    failures: list[str] = []

    green = run([])
    print(f"[1] unmutated collection+run: rc={green.returncode} :: {green.stdout.strip().splitlines()[-1]}")
    if green.returncode != 0:
        failures.append("the table is not green BEFORE the mutation")

    mutated = excise(original.decode("utf-8"))
    if "def _worktree_from_spine(" in mutated:
        print("FAIL: the excision did not apply", file=sys.stderr)
        return 1
    HOOK.write_text(mutated, encoding="utf-8", newline="")
    print(f"[2] excision applied: `def _worktree_from_spine(` present = "
          f"{'def _worktree_from_spine(' in HOOK.read_text(encoding='utf-8')}")

    try:
        red = run(["--collect-only"])
        tail = (red.stdout + red.stderr).strip().splitlines()
        print(f"[3] collection with the implementation deleted: rc={red.returncode}")
        for line in tail[-6:]:
            print(f"    | {line}")
        if red.returncode == 0:
            failures.append("collection SUCCEEDED with the implementation deleted")
        if "must drive EVERY implementation it names" not in (red.stdout + red.stderr):
            failures.append("collection failed, but not through _require's own message")
    finally:
        HOOK.write_bytes(original)

    after = digest(HOOK)
    print(f"[4] restored byte-identical: {before == after} ({after[:12]})")
    if before != after:
        failures.append("the hook was NOT restored byte-identical")

    restored = run([])
    print(f"[5] after restore: rc={restored.returncode} :: "
          f"{restored.stdout.strip().splitlines()[-1]}")
    if restored.returncode != 0:
        failures.append("the table is not green AFTER restoring")

    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("\nOK: green -> red on deletion -> green on restore, tree byte-identical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
