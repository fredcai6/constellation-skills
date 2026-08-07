"""Throwaway non-vacuity probe: mutate the shipped writer, prove the new tests go RED,
then restore byte-for-byte. Deleted immediately after the run."""

import io
import subprocess
import sys
from pathlib import Path

SRC = Path("scripts/apply_episode_delta.py")
ORIGINAL = io.open(SRC, encoding="utf-8", newline="").read()

MUTATIONS = {
    "history-line-drops-the-original": (
        'return f"restated — {reason} — original statement was: {original_statement}"',
        'return f"restated — {reason}"',
    ),
    "restate-also-flips-lifecycle-standing": (
        '    original_statement = assertion.statement\n',
        '    original_statement = assertion.statement\n    assertion.lifecycle_standing = "superseded"\n',
    ),
    "restate-also-touches-a-sibling": (
        '    assertion.statement = op["statement"].strip()\n',
        '    assertion.statement = op["statement"].strip()\n'
        '    for sibling in assertions.values():\n'
        '        sibling.strength = "weak"\n',
    ),
    "history-line-appended-twice": (
        "    assertion.history.append(\n"
        "        _restatement_history_line(op[\"history\"].strip(), original_statement)\n"
        "    )\n",
        "    assertion.history.append(\n"
        "        _restatement_history_line(op[\"history\"].strip(), original_statement)\n"
        "    )\n"
        "    assertion.history.append(\n"
        "        _restatement_history_line(op[\"history\"].strip(), original_statement)\n"
        "    )\n",
    ),
    "extra-field-allowlist-removed": (
        "    extra = set(op) - set(RESTATE_ALLOWED_FIELDS)\n    if extra:",
        "    extra = set()\n    if extra:",
    ),
    "unknown-assertion-id-silently-ignored": (
        '        raise EpisodeDeltaError(f"restate-assertion {episode_id}.{assertion_id}: no such assertion")',
        '        return f"restated {episode_id}.{assertion_id} (no-op)"',
    ),
}

# The working tree may legitimately hold CRLF (.gitattributes sets `* text=auto`), so
# anchors written with \n would match nothing. Detect and adapt rather than assume.
EOL = "\r\n" if "\r\n" in ORIGINAL else "\n"
print("detected working-tree line ending:", repr(EOL), flush=True)

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
    restored = io.open(SRC, encoding="utf-8", newline="").read()
    print("restored byte-for-byte:", restored == ORIGINAL, flush=True)

print("mutations probed:", len(MUTATIONS), "| vacuous or unapplied:", failed)
sys.exit(1 if failed else 0)
