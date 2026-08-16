#!/usr/bin/env python
"""Zero executable change under `scripts/` (close criterion C5).

Two measurements, both pinned to the explicit base commit -- never `HEAD`,
because this lane commits as gates close and a HEAD-pinned check stops
reproducing the moment the Commander commits (the rework-2 reviewer's tc-C).

  1. The handoff's own pipeline, run verbatim, output reported verbatim
     including when empty. Every line it prints must be docstring text: this
     rework edits one docstring (`spine_lifecycle.build_origin`) as well as
     comments, and a docstring line is not a `#` line, so the pipeline prints
     it by construction.

  2. The stronger property the pipeline only samples: for every changed file
     under `scripts/`, the module AST with EVERY docstring blanked is identical
     between base and working tree. Comments never enter an AST, so what
     survives this comparison is exactly the executable content -- if one
     statement, argument or constant had moved, it would differ.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "84d949eb"

PIPELINE = (
    f"git diff {BASE} -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' "
    r"| grep -vE '^\s*#' | grep -vE '^\s*$'"
)


def sh(cmd: str) -> str:
    return subprocess.run(
        cmd, cwd=ROOT, shell=True, capture_output=True, text=True
    ).stdout


def blank_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None)
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body[0].value.value = "<docstring>"
    return tree


def docstring_texts(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                out.append(doc)
    return "\n".join(out)


def main() -> int:
    print(f"$ {PIPELINE}")
    printed = sh(PIPELINE)
    print(printed if printed else "(empty)")
    print()

    changed = [
        p for p in sh(f"git diff --name-only {BASE} -- scripts/").split() if p.endswith(".py")
    ]
    print(f"changed files under scripts/: {changed or '(none)'}")

    problems: list[str] = []

    # (1) every printed line must be docstring text in the file it belongs to.
    docs = {p: docstring_texts(ROOT / p) for p in changed}
    for line in printed.splitlines():
        text = line.strip()
        if not text:
            continue
        if not any(text in body for body in docs.values()):
            problems.append(f"added line is NOT docstring text: {line!r}")
    print(f"lines printed by the pipeline: {len(printed.splitlines())} "
          f"-- all docstring text: {not problems}")

    # (2) executable content identical, docstrings blanked.
    for rel in changed:
        base_src = subprocess.run(
            ["git", "show", f"{BASE}:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
        tree_src = (ROOT / rel).read_text(encoding="utf-8")
        a = ast.dump(blank_docstrings(ast.parse(base_src)))
        b = ast.dump(blank_docstrings(ast.parse(tree_src)))
        same = a == b
        print(f"  {rel}: AST with docstrings blanked, {BASE} == working tree: {same}")
        if not same:
            problems.append(f"{rel}: executable content changed")

    if not changed:
        problems.append("no changed file under scripts/ -- this check looped over nothing")

    if problems:
        print("\nFAIL:")
        for p in problems:
            print(f"  {p}")
        return 1
    print("\nOK: zero executable change under scripts/; every added non-comment line is docstring text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
