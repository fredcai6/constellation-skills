"""B2, measured: do the case/separator rows discriminate, and from which cwd?

The reviewer's finding is that `_assert_one_answer_for_every_stamp` was called
with `self.foreign` and `self.nogit` only, and that from a foreign cwd NO stamp
can match -- so a stamp-reading decision refuses every row identically and the
`the same path, wrong case` row proves nothing the plain `a foreign tree` row
does not. The rows separate only from the spine's OWN worktree.

This reproduces that under the reviewer's mutant (a stamp-reading refusal:
`normcase(stored) != normcase(cwd)` -> refuse), driving `start`, from both
cwds. It asserts the mutation actually applied before running it -- a replace
that matches nothing leaves a green suite that reads exactly like a passing
guard (CREW_CONTEXT, Verification Discipline) -- and restores the tree
byte-identical afterwards, proving it by hash.

Run: py .agent-work/<work-id>/g2-implement-rework/measure_b2.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import contextlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "scripts" / "checklist_engine.py"
TESTFILE = ROOT / "tests" / "test_spine_origin_isolation.py"

ANCHOR = """    cl = load(path)
"""
MUTANT = """    cl = load(path)
    _stored = (cl.get("origin") or {}).get("worktree") or ""
    if _stored and os.path.normcase(str(_stored)) != os.path.normcase(os.getcwd()):
        print(f"REFUSED: {args.verb} refused: stamp mismatch", file=sys.stderr)
        return 1
"""

_ABSENT = object()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamps(worktree: Path) -> dict:
    """The shipped table, with its three run-time rows filled in."""
    return {
        "the spine's own worktree": worktree.as_posix(),
        "a foreign tree": "/nonexistent/some/other/tree",
        "a sibling sharing a name prefix": worktree.as_posix() + "-2",
        "not a path at all": "not-a-path",
        "an empty string": "",
        "a number": 7,
        "worktree key absent": _ABSENT,
        "a Windows-shaped path": "C:\\W\\REPO",
        "the same path, wrong case": worktree.as_posix().upper(),
    }


def load_engine():
    spec = importlib.util.spec_from_file_location("engine_b2_probe", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["engine_b2_probe"] = mod
    spec.loader.exec_module(mod)
    return mod


def write_spine(spine_path: Path, stamp) -> None:
    origin = {"work_id": "w1", "opened_by": "init_work_area"}
    if stamp is not _ABSENT:
        origin["worktree"] = stamp
    spine_path.write_text(json.dumps({
        "work_id": "w1", "type": "gated", "items": ["g1"],
        "origin": origin,
        "tasks": {"g1": {
            "id": "g1", "title": "g1", "imperative": "do g1",
            "preconditions": [], "postconditions": [],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }},
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }, indent=2), encoding="utf-8")
    journal = spine_path.parent / "spine.json.journal"
    if journal.exists():
        journal.unlink()


def drive_start(engine, spine_path: Path, stamp, cwd: Path, home: str) -> tuple[int, bool]:
    """Drive `start` for one stamp from `cwd`. Returns (exit code, refused?)."""
    write_spine(spine_path, stamp)
    os.chdir(cwd)
    try:
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = engine.main(["--file", str(spine_path), "start", "g1"])
        return code, "REFUSED:" in err.getvalue()
    finally:
        os.chdir(home)


def table(engine, label: str, cwd: Path, worktree: Path, spine_path: Path, home: str) -> dict:
    print(f"\n--- {label}")
    rows = {}
    for name, stamp in stamps(worktree).items():
        code, refused = drive_start(engine, spine_path, stamp, cwd, home)
        rows[name] = (code, refused)
        print(f"    {name:<34} exit={code} refused={refused}")
    return rows


def separates(rows: dict) -> bool:
    """Does `the same path, wrong case` behave differently from the own-worktree
    row? That difference IS the row's discriminating power."""
    return rows["the spine's own worktree"] != rows["the same path, wrong case"]


def probe(tag: str) -> tuple[dict, dict]:
    engine = load_engine()
    home = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp).resolve()
        worktree, foreign = base / "wt", base / "elsewhere"
        (worktree / ".agent-work" / "w1").mkdir(parents=True)
        foreign.mkdir()
        for d in (worktree, foreign):
            subprocess.run(["git", "init", "-q"], cwd=d, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        spine_path = worktree / ".agent-work" / "w1" / "spine.json"
        print(f"\n{'=' * 74}\n{tag}\n{'=' * 74}")
        own = table(engine, "the spine's OWN worktree (the cwd the shipped test never drove)",
                    worktree, worktree, spine_path, home)
        fgn = table(engine, "a FOREIGN cwd (the only kind the shipped test drove from)",
                    foreign, worktree, spine_path, home)
    return own, fgn


def pytest_on_testfile(tag: str) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("SPINE_FILE", "SPINE_SESSION", "SPINE_PARENT")}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(TESTFILE)],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    tail = (proc.stdout or "").strip().splitlines()
    print(f"\n{tag}: rc={proc.returncode} | {tail[-1] if tail else '(no output)'}")
    return proc.returncode, proc.stdout


def main() -> int:
    original = ENGINE.read_bytes()
    before_hash = sha(ENGINE)
    print(f"scripts/checklist_engine.py sha256 BEFORE: {before_hash}")

    failures: list[str] = []
    try:
        # ---------- UNMUTATED ----------
        own_u, fgn_u = probe("UNMUTATED — nothing reads the stamp, so every row is accepted")
        if not all(v == (0, False) for v in own_u.values()):
            failures.append("unmutated: some row was refused from the spine's own worktree")
        if not all(v == (0, False) for v in fgn_u.values()):
            failures.append("unmutated: some row was refused from a foreign cwd")

        rc_clean, _ = pytest_on_testfile("UNMUTATED test file (incl. the added self.worktree call)")
        if rc_clean != 0:
            failures.append("unmutated: the test file is not green")

        # ---------- APPLY THE MUTANT, AND ASSERT IT APPLIED ----------
        text = original.decode("utf-8")
        occurrences = text.count(ANCHOR)
        print(f"\nmutation anchor occurrences: {occurrences}")
        if occurrences != 1:
            print(f"ABORT: anchor matched {occurrences} times, expected exactly 1", file=sys.stderr)
            return 2
        mutated = text.replace(ANCHOR, MUTANT, 1)
        if mutated == text:
            print("ABORT: replace changed nothing", file=sys.stderr)
            return 2
        ENGINE.write_text(mutated, encoding="utf-8", newline="\n")
        applied = sha(ENGINE) != before_hash and "stamp mismatch" in ENGINE.read_text(encoding="utf-8")
        print(f"MUTATION APPLIED (asserted, not assumed): {applied}  sha256={sha(ENGINE)}")
        if not applied:
            print("ABORT: mutation did not apply", file=sys.stderr)
            return 2

        # ---------- MUTATED ----------
        own_m, fgn_m = probe("MUTATED — a stamp-reading refusal: normcase(stored) != normcase(cwd)")

        print("\n--- B2, the finding, stated as a measurement")
        own_sep, fgn_sep = separates(own_m), separates(fgn_m)
        own_key = "the spine's own worktree"
        case_key = "the same path, wrong case"
        print(f"    from the spine's OWN worktree: '{case_key}' separates = {own_sep}"
              f"   ({own_m[own_key]} vs {own_m[case_key]})")
        print(f"    from a FOREIGN cwd:            '{case_key}' separates = {fgn_sep}"
              f"   ({fgn_m[own_key]} vs {fgn_m[case_key]})")
        # Scope: `an empty string` and `worktree key absent` carry no stamp, so
        # the mutant's `if _stored` guard never reads them and they stay
        # accepted from BOTH cwds. They are inert by construction under this
        # mutant, which is why the reviewer's own table lists only the rows
        # holding a real path. The collapse claim is about those rows.
        read_rows = {n for n, s in stamps(Path("/unused")).items()
                     if s is not _ABSENT and s != ""}
        distinct_foreign = {fgn_m[n] for n in read_rows}
        print(f"    from a FOREIGN cwd, the {len(read_rows)} rows carrying a stamp "
              f"collapse to: {distinct_foreign}")
        unread = {n: fgn_m[n] for n in fgn_m if n not in read_rows}
        print(f"    (not read by the mutant at all, so inert from both cwds: {unread})")

        if not own_sep:
            failures.append("mutated: the wrong-case row did NOT separate from the spine's own worktree")
        if fgn_sep:
            failures.append("mutated: the wrong-case row separated from a foreign cwd (unexpected)")
        if distinct_foreign != {(1, True)}:
            failures.append("mutated: the stamp-carrying rows did not all refuse identically "
                            f"from a foreign cwd (got {distinct_foreign})")

        rc_mut, out_mut = pytest_on_testfile("MUTATED test file")
        if rc_mut == 0:
            failures.append("mutated: the test file stayed GREEN — the guard does not guard")
        added = "test_provenance_the_stamp_is_not_a_decision_input_from_the_spines_own_worktree"
        print(f"    the ADDED test is named in the mutated failure output: {added in out_mut}")
        if added not in out_mut:
            failures.append("mutated: the added self.worktree test did not appear in the failure set")

    finally:
        # ---------- RESTORE, AND PROVE IT ----------
        ENGINE.write_bytes(original)
        after_hash = sha(ENGINE)
        print(f"\nscripts/checklist_engine.py sha256 AFTER RESTORE: {after_hash}")
        print(f"RESTORED BYTE-IDENTICAL: {after_hash == before_hash}")
        if after_hash != before_hash:
            failures.append("tree was NOT restored byte-identical")

    rc_restored, _ = pytest_on_testfile("RESTORED test file")
    if rc_restored != 0:
        failures.append("restored: the test file is not green")

    print()
    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("B2 MEASURED: the rows are inert from a foreign cwd and discriminate from the "
          "spine's own worktree; the added call is green unmutated and red under the mutant; "
          "tree restored byte-identical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
