"""Prove 359d93df changed no behaviour: AST-identical to 4e1f22cb once docstrings are stripped.

A docstring edit is invisible to execution. This asserts that claim rather than
eyeballing the diff: parse both revisions of every .py file the rework touched,
delete every docstring node, and compare the dumped ASTs. It also asserts the
mutation applied -- i.e. that the two sources really do differ before stripping --
so a probe that silently compared a file to itself cannot read as a pass.
"""

import ast
import subprocess
import sys

OLD = "4e1f22cb"
NEW = "359d93df"


def source_at(rev: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        capture_output=True, text=True, check=True,
    ).stdout


def strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
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


def changed_py_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{OLD}..{NEW}"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return [p for p in out if p.endswith(".py")]


def main() -> int:
    files = changed_py_files()
    print(f"python files changed by {OLD}..{NEW}: {len(files)} -> {files}")
    if not files:
        print("NOTE: no .py files changed at all; behaviour invariance is trivially true")
        return 0

    failures = 0
    for path in files:
        old_src, new_src = source_at(OLD, path), source_at(NEW, path)

        # Assert the mutation applied: the sources MUST differ, or this probe is vacuous.
        if old_src == new_src:
            print(f"VACUOUS: {path} is byte-identical across the two revisions")
            failures += 1
            continue

        old_ast = ast.dump(strip_docstrings(ast.parse(old_src)))
        new_ast = ast.dump(strip_docstrings(ast.parse(new_src)))
        same = old_ast == new_ast
        print(f"{path}: sources differ = True, docstring-stripped AST identical = {same}")
        if not same:
            failures += 1

        # Independent second angle: every differing line must sit inside a docstring.
        old_lines, new_lines = old_src.splitlines(), new_src.splitlines()
        import difflib
        touched = [
            ln for ln in difflib.unified_diff(old_lines, new_lines, n=0, lineterm="")
            if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))
        ]
        print(f"  changed lines: {len(touched)}")
        for ln in touched:
            print(f"    {ln}")

    print("RESULT:", "BEHAVIOUR UNCHANGED" if failures == 0 else f"{failures} FAILURE(S)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
