"""Prove this rework changed ZERO executable content under `scripts/`.

The handoff asks me to re-run the reviewer's grep against base `9ff86f2d`. That
command was authored before `main` was merged into this branch at `6a4035d2`,
so `9ff86f2d` now sweeps up lanes A and E as well and the command no longer
isolates this lane. It is also a *shape* argument: its filter strips `#`
comments and blank lines but NOT docstring bodies, so "it leaves only docstring
text" is an eyeball judgement about the surviving lines.

This makes the same claim mechanically and about the right base. For every
changed file under `scripts/`, it parses the HEAD version and the working-tree
version, strips every docstring (the leading string statement of a module,
class or function), and compares the ASTs. Identical ASTs mean the change is
comment and docstring prose only -- no statement, no expression, no early
return, no verb-set edit -- which is the property the handoff actually wants
kept true.

The grep is reported alongside it, for continuity with the reviewer's record.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "HEAD"  # this rework is uncommitted; HEAD is the tree I started from


def strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            node.body = body[1:] or [ast.Pass()]
    return tree


def normalized(source: str) -> str:
    return ast.dump(strip_docstrings(ast.parse(source)), annotate_fields=True)


def changed_files() -> list[str]:
    out = subprocess.run(["git", "diff", "--name-only", BASE, "--", "scripts/"],
                         cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.split("\n") if line.strip()]


def head_source(path: str) -> str:
    out = subprocess.run(["git", "show", f"{BASE}:{path}"],
                         cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout


def main() -> int:
    files = changed_files()
    # "Any guard that loops must assert what it looped over" (CREW_CONTEXT).
    print(f"files changed under scripts/ vs {BASE}: {len(files)} -> {files or '(none)'}")
    if not files:
        print("NOTE: no file under scripts/ differs from HEAD at all.")

    failures = []
    for name in files:
        if not name.endswith(".py"):
            failures.append(f"{name}: not a .py file; AST comparison does not apply")
            continue
        before = normalized(head_source(name))
        after = normalized((ROOT / name).read_text(encoding="utf-8"))
        same = before == after
        print(f"  {name}: executable AST identical (docstrings stripped) = {same}")
        if not same:
            failures.append(f"{name}: executable content CHANGED")

    # The reviewer's own grep, on this rework's diff, reported for continuity.
    grep = subprocess.run(
        "git diff HEAD -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' "
        "| grep -vE '^[[:space:]]*#' | grep -vE '^[[:space:]]*$'",
        cwd=ROOT, shell=True, capture_output=True, text=True,
    )
    surviving = [l for l in grep.stdout.split("\n") if l.strip()]
    print(f"\nreviewer's grep on THIS rework's diff (vs HEAD): {len(surviving)} surviving lines")
    for line in surviving:
        print(f"    | {line}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("\nOK: zero executable change under scripts/ — comment and docstring prose only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
