"""Behavioural check: the lessons writer no longer refuses an add at 20 active entries.

Why this is not a grep. The refusal message is built by an f-string
(`f"add {lesson_id}: active cap {book.cap} reached ..."`), so the literal
`cap [0-9]+ reached` NEVER appears in the source. A grep for it exits 0 whether or
not the cap exists -- a check that cannot fail, which this epic has now found six
times. So this drives the real writer against a frozen 20-entry fixture instead.

Exit 0 = the add succeeded (cap gone). Exit 1 = it was refused, or refused for a
reason that is not the cap (a schema error would otherwise masquerade as a pass at
the wrong end -- see notes-308.md, where exactly that happened while measuring the
cap in the first place).

Run from the repo root.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIXTURE = ROOT / ".agent-work/issue-308/fixtures/LESSONS-at-cap.md"
WRITER = ROOT / "scripts/apply_lessons_delta.py"

DELTA = {
    "work_id": "issue-308-capcheck",
    "ops": [{
        "op": "add",
        "id": "cap-removal-behavioural-check",
        "scope": "project",
        "task_class": "testing",
        "statement": "Probe entry proving the writer accepts an add at 20 active entries. Not a real lesson.",
        "grounding": "issue-308 g3 acceptance check, fixture frozen at 20/20",
        "bank_reason": "probe only",
    }],
}


def main() -> int:
    if not FIXTURE.exists():
        print(f"FAIL: fixture missing at {FIXTURE}")
        return 1

    # Assert the fixture really is at the cap; a fixture that drifted below 20
    # would let this check pass without ever exercising the cap.
    import re
    text = FIXTURE.read_text(encoding="utf-8")
    active = text.split("## Active", 1)[1]
    n = len(re.findall(r"^### lesson:", active, re.M))
    if n < 20:
        print(f"FAIL: fixture holds {n} active entries, expected >= 20 — it cannot exercise the cap")
        return 1

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        target = tmp / "LESSONS.md"
        shutil.copyfile(FIXTURE, target)
        delta = tmp / "delta.json"
        delta.write_text(json.dumps(DELTA, indent=2), encoding="utf-8", newline="\n")

        proc = subprocess.run(
            [sys.executable, str(WRITER), "--file", str(target), str(delta)],
            capture_output=True, text=True,
        )
        out = (proc.stdout + proc.stderr).strip()

        if proc.returncode == 0:
            print(f"PASS: add accepted at {n} active entries — the cap is gone")
            return 0

        if "cap" in out and "reached" in out:
            print(f"FAIL: the cap still refuses the add at {n} entries:\n{out}")
        else:
            print(f"FAIL: add refused, but NOT by the cap — this check did not reach "
                  f"the condition it exists to test:\n{out}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
