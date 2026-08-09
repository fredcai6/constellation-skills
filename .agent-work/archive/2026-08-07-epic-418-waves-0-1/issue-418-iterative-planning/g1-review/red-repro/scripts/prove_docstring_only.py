#!/usr/bin/env python3
"""Decide — not assert — whether a Python file's change is docstring-only.

"Docstring-only, behaviour unchanged" is normally *asserted* by whoever made the
edit and taken on trust by whoever reads the diff. No amount of reading a diff
can establish it: a diff shows text moved, not whether meaning moved with it.

This turns it into a decidable three-way result, where each leg rules out a
different way of being wrong:

    raw bytes differ            -> the edit actually applied (not a no-op)
    full AST differs            -> the docstring genuinely changed
    docstring-stripped AST same -> no behaviour changed

All three must hold. Any two of them are satisfiable by a change that is *not*
docstring-only:

  * bytes differ + stripped-AST same, but full AST also same -> the change was
    whitespace or comments, not a docstring; the claim is mislabelled.
  * bytes differ + full AST differs, but stripped-AST differs too -> real code
    moved. This is the case the check exists to catch.

Stripping is applied to every module, class and function body, so a docstring
edit anywhere in the file is covered, not just the module header.

Written for #305 g4 (#327), where the claim under test was that
`scripts/checklist_engine.py` — the engine every gate in the fleet drives —
changed by docstring only. Kept as a tool rather than a scratch script because
the claim recurs whenever prose recording a decision is corrected in place.

    python scripts/prove_docstring_only.py <before-rev> <after-rev> <path>
    python scripts/prove_docstring_only.py 35d2686^ 35d2686 scripts/context_manifest.py
    python scripts/prove_docstring_only.py HEAD WORKTREE scripts/context_manifest.py

`WORKTREE` in place of a revision reads the file on disk. It is spelled without
leading dashes on purpose: `--worktree` would be parsed as an option, not as the
positional it stands in for.

Exits 0 when the change is proven docstring-only, 1 otherwise. The failure
message names WHICH leg failed, because "not docstring-only" and "no change at
all" are different problems.

A note on instruments: comparing raw bytes across a CRLF worktree and an LF
`git show` manufactures false results (see #319). This compares parsed ASTs, so
line endings cannot affect the verdict.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path


def source_at(rev: str, path: str) -> str:
    """File contents at `rev`, or the file on disk when rev is `WORKTREE`."""
    if rev == "WORKTREE":
        return Path(path).read_text(encoding="utf-8")
    out = subprocess.run(
        ["git", "show", f"{rev}:{path}"], capture_output=True, check=True
    ).stdout
    return out.decode("utf-8")


def strip_docstrings(tree: ast.AST) -> ast.AST:
    """Drop the leading string-constant expression from every body that has one.

    Bodies emptied by the strip get an explicit `Pass` so the tree stays valid;
    `Pass` is inserted on both sides whenever it is inserted at all, so it can
    never make two differing trees compare equal.
    """
    holders = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    for node in ast.walk(tree):
        if not isinstance(node, holders):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            node.body = body[1:] or [ast.Pass()]
    return tree


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("before", help="git revision before the change")
    parser.add_argument("after", help="git revision after it, or WORKTREE for the file on disk")
    parser.add_argument("path", help="repo-relative path to the .py file")
    args = parser.parse_args()

    before = source_at(args.before, args.path)
    after = source_at(args.after, args.path)

    bytes_differ = before != after
    full_differ = ast.dump(ast.parse(before)) != ast.dump(ast.parse(after))
    stripped_same = ast.dump(strip_docstrings(ast.parse(before))) == ast.dump(
        strip_docstrings(ast.parse(after))
    )

    print(f"file                        : {args.path}")
    print(f"{args.before} -> {args.after}")
    print(f"raw bytes differ            : {bytes_differ}   (edit applied)")
    print(f"full AST differs            : {full_differ}   (docstring changed)")
    print(f"docstring-stripped AST same : {stripped_same}   (behaviour unchanged)")

    if bytes_differ and full_differ and stripped_same:
        print("\nPROVEN: docstring-only, behaviour byte-unchanged.")
        return 0

    print("\nNOT PROVEN. Failing leg(s):")
    if not bytes_differ:
        print("  - the two revisions are byte-identical; there is no change to classify")
    if not full_differ:
        print("  - no docstring changed; the edit was whitespace or comments")
    if not stripped_same:
        print("  - CODE CHANGED. This is not a docstring-only change.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
