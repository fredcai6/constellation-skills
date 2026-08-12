"""g4-review independent red-repro harness.

For each row of the handoff's broken-input table: apply ONE byte-level mutation to
the real source the fixture installs from, ASSERT it applied (bytes, not text),
run the named selector, capture exit code + output, then restore from the saved
ORIGINAL BYTES and assert byte-identity. `git status --porcelain` is checked for
the mutated path after every restore.

CRLF discipline: everything is read_bytes/write_bytes. No read_text, no
write_text, no newline= anywhere. A literal that does not match is a hard error,
never a silent no-op.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates")
OUT = ROOT / ".agent-work/w5-gates/g4-review/repro"
VERIFIER = ROOT / "scripts/verify_iterative_role_artifacts.py"
SPINE = ROOT / "skills/commander/templates/COMMANDER_SPINE.template.json"

# (id, target, selector, old-bytes, new-bytes, expected-substring-in-output)
CASES = [
    (
        "m1-spine-branch-token",
        SPINE,
        "compose_spine",
        b'\\"$(git -C <repo-root> rev-parse --abbrev-ref HEAD)\\"',
        b"<branch>",
        "archive.c2b",
    ),
    (
        "m2-spine-exit-verdict",
        SPINE,
        "compose_spine",
        b" -gt 0",
        b" -ge 0",
        "no PR at all is not reachable",
    ),
    (
        "m3-verifier-name-test",
        VERIFIER,
        "compose_verifier",
        b'    return (path / "SKILL.md").is_file() and _is_skills_root(path.parent, exclude=path)',
        b'    return path.name.startswith("constellation-")',
        "is not an installed bundle",
    ),
    (
        "m4-verifier-ignores-skills-root",
        VERIFIER,
        "compose_verifier",
        b"    if skills_root is not None:",
        b"    if False:",
        "--skills-root must make the same run resolvable",
    ),
    (
        "m5-terminal-conflation",
        VERIFIER,
        "compose_terminal",
        b'    if decision == "stop":',
        b"    if False:",
        "a verified stop must close prelaunch",
    ),
    (
        "m6-terminal-relaxation-widened",
        VERIFIER,
        "compose_terminal",
        b'    if decision == "stop":',
        b"    if True:",
        "repair must not inherit the stop relaxation",
    ),
]


def git_status(path: Path) -> str:
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--", str(path.relative_to(ROOT).as_posix())],
        cwd=ROOT, capture_output=True, text=True,
    )
    return proc.stdout.strip()


def run_selector(selector: str, tag: str) -> tuple[int, str]:
    log = OUT / f"{tag}.txt"
    with log.open("wb") as fh:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest",
             "tests/test_iterative_planning_doctrine.py", "-q", "-k", selector],
            cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
        )
    return proc.returncode, log.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for case_id, target, selector, old, new, expect in CASES:
        original = target.read_bytes()
        # Baseline hygiene: nothing dirty going in.
        pre_status = git_status(target)
        count = original.count(old)
        if count != 1:
            raise SystemExit(f"{case_id}: literal not unique in {target.name}: count={count}")
        mutated = original.replace(old, new, 1)
        target.write_bytes(mutated)
        try:
            on_disk = target.read_bytes()
            # ASSERT THE MUTATION APPLIED -- bytes, not text.
            applied = (old not in on_disk) and (new in on_disk) and (on_disk != original)
            if not applied:
                raise SystemExit(f"{case_id}: MUTATION DID NOT APPLY")
            dirty = git_status(target)
            code, output = run_selector(selector, case_id)
        finally:
            target.write_bytes(original)
        restored = target.read_bytes()
        byte_identical = restored == original
        post_status = git_status(target)
        report.append({
            "case": case_id,
            "target": target.relative_to(ROOT).as_posix(),
            "selector": selector,
            "pre_git_status": pre_status,
            "mutation_applied": True,
            "git_status_while_mutated": dirty,
            "exit_code": code,
            "expected_fragment": expect,
            "expected_fragment_present": expect in output,
            "tail": "\n".join(output.strip().splitlines()[-30:]),
            "restore_byte_identical": byte_identical,
            "post_git_status": post_status,
        })
        print(f"{case_id}: exit={code} applied=True fragment={expect in output} "
              f"restored_bytes={byte_identical} post_status={post_status!r}", flush=True)
        if not byte_identical:
            raise SystemExit(f"{case_id}: RESTORE FAILED at byte level")
        if post_status:
            raise SystemExit(f"{case_id}: RESTORE LEFT THE TREE DIRTY: {post_status}")
    (OUT / "red-repro-report.json").write_bytes(
        json.dumps(report, indent=2).encode("utf-8")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
