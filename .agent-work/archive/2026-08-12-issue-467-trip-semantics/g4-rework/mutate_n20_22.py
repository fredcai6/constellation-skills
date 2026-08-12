"""#467 B1 rework -- mutations N20-N22, sanctioned route.

ADAPTATION NOTE (declared, not silent): the g4 mutation-log method reverts each
mutant with `git checkout --` and asserts `git diff --quiet` against the
COMMITTED baseline, because that implementation had already been committed
before mutating. This rework's implementer does NOT commit (the Commander
does), so `scripts/checklist_engine.py` is genuinely, legitimately dirty in
git the whole time this driver runs. Using `git checkout --` here would
DESTROY the real fix, not just the mutant. So this driver reverts against a
snapshot of the real (uncommitted) implementation taken before any mutation,
and asserts byte-identity against THAT snapshot instead of `git diff --quiet`.
Same discipline (anchor matched exactly once, tests run, revert asserted
clean before the next mutation) -- different revert target, because there is
no clean commit to revert to yet.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
ENGINE = ROOT / "scripts" / "checklist_engine.py"
BASELINE = Path(r"C:/Users/fredc/.claude/jobs/cdcd8db2/tmp/g4rw_baseline_engine.py")

TEST_CMD = [sys.executable, "-m", "pytest", "-q", "tests/test_checklist_engine.py"]

MUTATIONS = [
    {
        "name": "N20",
        "desc": "the new selector dead-coded to `return []`",
        "old": (
            '        if e.get("outcome") not in ("begin-refused", "begin-released"):\n'
            "            continue\n"
            "        out.append(e)\n"
            "    return out\n"
            "\n"
            "\n"
            "def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None,\n"
        ),
        "new": (
            '        if e.get("outcome") not in ("begin-refused", "begin-released"):\n'
            "            continue\n"
            "        out.append(e)\n"
            "    return []\n"
            "\n"
            "\n"
            "def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None,\n"
        ),
        "named_test": "TripLedgerComplianceOnTheHardAdvisory::test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent",
    },
    {
        "name": "N21",
        "desc": "the historical line dropped from the ALREADY-REQUESTED HARD sub-branch",
        "old": (
            '                    f"and stop. A fresh agent picks up from your DIGEST; do not begin "\n'
            '                    f"work at another gate.") + live_note + historical_note\n'
        ),
        "new": (
            '                    f"and stop. A fresh agent picks up from your DIGEST; do not begin "\n'
            '                    f"work at another gate.") + live_note\n'
        ),
        "named_test": "TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_also_rides_the_already_requested_hard_advisory",
    },
    {
        "name": "N22",
        "desc": "the historical selector keyed to the live why-record (made identical to the live one) -- re-creates B1",
        "old": (
            "    out: list[dict] = []\n"
            '    for e in cl.get("trip_ledger", []) or []:\n'
            "        if not isinstance(e, dict):\n"
            "            continue\n"
            '        if e.get("outcome") not in ("begin-refused", "begin-released"):\n'
            "            continue\n"
            "        out.append(e)\n"
            "    return out\n"
            "\n"
            "\n"
            "def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None,\n"
        ),
        "new": (
            "    rec = _latest_why_record(cl)\n"
            '    live = rec["id"] if rec else None\n'
            "    out: list[dict] = []\n"
            '    for e in cl.get("trip_ledger", []) or []:\n'
            "        if not isinstance(e, dict):\n"
            "            continue\n"
            '        if e.get("outcome") not in ("begin-refused", "begin-released"):\n'
            "            continue\n"
            '        if e.get("why_ref") != live:\n'
            "            continue\n"
            "        out.append(e)\n"
            "    return out\n"
            "\n"
            "\n"
            "def _trip_hard_gate(cl: dict, iid: str | None, base_dir: Path | None,\n"
        ),
        "named_test": "TripLedgerComplianceOnTheHardAdvisory::test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent",
    },
]


def run():
    baseline_text = BASELINE.read_text(encoding="utf-8")
    current_text = ENGINE.read_text(encoding="utf-8")
    assert current_text == baseline_text, "engine file is not at the expected pre-mutation baseline"

    results = []
    for m in MUTATIONS:
        text = ENGINE.read_text(encoding="utf-8")
        count = text.count(m["old"])
        assert count == 1, f"{m['name']}: anchor matched {count} times, expected 1"
        mutated = text.replace(m["old"], m["new"], 1)
        assert mutated != text, f"{m['name']}: mutation did not change the file"
        ENGINE.write_text(mutated, encoding="utf-8")

        proc = subprocess.run(TEST_CMD, cwd=str(ROOT), capture_output=True, text=True,
                               env={**__import__("os").environ, "FORCE_COLOR": "", "NO_COLOR": "1"})
        out = proc.stdout + proc.stderr
        failed_lines = [l for l in out.splitlines() if l.startswith("FAILED") or l.startswith("SUBFAILED")]
        summary_line = next((l for l in out.splitlines()[::-1]
                             if "passed" in l or "failed" in l or "error" in l), "")

        # revert against the REAL (uncommitted) baseline, not git
        shutil.copyfile(BASELINE, ENGINE)
        reverted_clean = ENGINE.read_text(encoding="utf-8") == baseline_text

        named_hit = any(m["named_test"] in l for l in failed_lines)
        results.append({
            "name": m["name"], "desc": m["desc"], "rc": proc.returncode,
            "summary": summary_line, "named_test": m["named_test"],
            "named_hit": named_hit, "n_failed_lines": len(failed_lines),
            "reverted_clean": reverted_clean,
        })
        assert reverted_clean, f"{m['name']}: revert left the file dirty relative to the real baseline"
        print(f"[{m['name']}] {m['desc']}")
        print(f"    named test red: {named_hit}  ({m['named_test']})")
        print(f"    summary: {summary_line}")
        print(f"    failed/subfailed lines: {len(failed_lines)}")
        print(f"    reverted_clean: {reverted_clean}")
        print()

    final = ENGINE.read_text(encoding="utf-8") == baseline_text
    print(f"FINAL STATE clean (== real baseline): {final}")
    return results


if __name__ == "__main__":
    run()
