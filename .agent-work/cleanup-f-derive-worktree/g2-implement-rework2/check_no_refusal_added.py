"""C9 — no refusal is added anywhere, and the scripts/ diff only subtracts.

R2 withdrew the fail-closed refusal: an unowned spine path yields no derived
worktree and today's behaviour. So the check that matters is not "did the tests
pass" but "did anything get ADDED to the engine at all".

Three claims, each measured:

  1. Zero non-comment lines added under `scripts/` versus HEAD. A refusal has to
     be executable, so a diff with no added executable line cannot contain one.
  2. At AST level, `checklist_engine.py` lost exactly `worktree_from_spine_path`
     and `AGENT_WORK_DIR` and gained nothing; every other top-level node is
     byte-for-byte the same tree.
  3. The engine's refusal vocabulary is unchanged in count -- the same number of
     `REFUSED` strings, `EngineError` raises and `sys.exit` calls as HEAD.

Exit 0 = pure deletion. Exit 1 = something was added.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENGINE = "scripts/checklist_engine.py"
EXPECTED_REMOVED = {"worktree_from_spine_path", "AGENT_WORK_DIR"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def top_level(source: str) -> dict[str, str]:
    """Every top-level name in the module, mapped to its dumped AST."""
    out: dict[str, str] = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = ast.dump(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = ast.dump(node)
    return out


def main() -> int:
    failures: list[str] = []

    # 1. added lines under scripts/
    diff = git("diff", "HEAD", "--", "scripts/")
    added = [l[1:] for l in diff.split("\n")
             if l.startswith("+") and not l.startswith("+++")]
    executable = [l for l in added if l.strip() and not l.strip().startswith("#")]
    removed = [l for l in diff.split("\n")
               if l.startswith("-") and not l.startswith("---")]
    print(f"[1] scripts/ diff vs HEAD: {len(added)} added line(s), "
          f"{len(removed)} removed; {len(executable)} added line(s) are not comments")
    for line in executable:
        print(f"    +| {line}")
    if executable:
        failures.append(f"{len(executable)} executable line(s) ADDED under scripts/")
    if len(removed) <= len(added):
        failures.append("the diff does not shrink scripts/")

    # 2. what the engine lost, at AST level
    before = top_level(git("show", f"HEAD:{ENGINE}"))
    after = top_level((ROOT / ENGINE).read_text(encoding="utf-8"))
    gone = set(before) - set(after)
    new = set(after) - set(before)
    changed = {n for n in set(before) & set(after) if before[n] != after[n]}
    print(f"[2] {ENGINE} top-level names: {len(before)} -> {len(after)}; "
          f"removed={sorted(gone)}, added={sorted(new)}, otherwise-changed={sorted(changed)}")
    if gone != EXPECTED_REMOVED:
        failures.append(f"removed set is {sorted(gone)}, expected {sorted(EXPECTED_REMOVED)}")
    if new:
        failures.append(f"new top-level name(s) appeared: {sorted(new)}")
    if changed:
        failures.append(f"other top-level node(s) changed: {sorted(changed)}")

    # 3. the refusal vocabulary, counted
    head_src = git("show", f"HEAD:{ENGINE}")
    work_src = (ROOT / ENGINE).read_text(encoding="utf-8")
    for token in ("REFUSED", "raise EngineError", "sys.exit"):
        b, a = head_src.count(token), work_src.count(token)
        print(f"[3] {token!r}: HEAD {b} -> working tree {a}")
        if a > b:
            failures.append(f"{token!r} occurrences grew from {b} to {a}")

    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("\nOK: pure deletion under scripts/ — nothing added, no refusal introduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
