"""tc34, verified independently by the reviewer.

1. Builds the REAL corpus fresh into a scratch --artifacts/--out (never touches
   the committed map/ or .code-map/).
2. Re-derives, from git history, the body-only descent the DELETED
   supplement.walk actually used (confirmed byte-for-byte against
   `git show 0d821d6f~1:scripts/code_map/supplement.py`), and diffs it against
   the fresh store -- an independent re-measurement of the implementer's "8
   definitions gained" claim, not a re-run of their script.
3. Picks ONE of the gained definitions and confirms directly, by reading the
   source, that it sits inside a `with` / `try` / `if` / `for` block -- and
   confirms a page exists for it in the freshly rendered tree.
"""
import ast
import json
import pathlib
import subprocess
import sys
import tempfile
import os

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.code_map.discovery import discover_corpus  # noqa: E402


def mod_of(rel):
    parts = rel.split("/")
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def old_body_only_descent():
    old = set()
    for rel in discover_corpus(ROOT):
        rel = rel.replace("\\", "/")
        try:
            tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        except Exception:
            continue
        modname = mod_of(rel)

        def walk(node, prefix):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qual = f"{prefix}.{child.name}" if prefix else child.name
                    old.add((f"{modname}:{qual}", rel, child.lineno))
                    walk(child, qual)

        walk(tree, "")
    return old


def main():
    scratch = tempfile.mkdtemp(prefix="g3rev-tc34-")
    artifacts = pathlib.Path(scratch) / "artifacts"
    out = pathlib.Path(scratch) / "out"
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    b = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build",
         "--root", str(ROOT), "--artifacts", str(artifacts), "--out", str(out)],
        cwd=str(ROOT), capture_output=True, text=True, env=env)
    print("fresh build exit:", b.returncode)
    if b.returncode != 0:
        print(b.stdout[-2000:], b.stderr[-2000:])
        return 1

    old = old_body_only_descent()
    old_syms = {sym for sym, _, _ in old}

    new = set()
    with open(artifacts / "statements.jsonl", encoding="utf-8") as f:
        for line in f:
            st = json.loads(line)
            if st["p"] == "contains":
                new.add(st["o"])

    gained = sorted(new - old_syms)
    lost = sorted(old_syms - new)
    print("body-only descent (re-derived from git history) :", len(old_syms), "definitions")
    print("fresh one-schema store                            :", len(new), "definitions")
    print("gained (removed stage could not see)              :", len(gained))
    for s in gained:
        print("   +", s)
    print("lost (store misses what the old rule found)       :", len(lost), lost)

    # Pick the first gained symbol and prove it independently: page exists,
    # AND it sits inside a with/try/if/for block in the source.
    if gained:
        target = gained[0]
        modname, qual = target.split(":", 1)
        # find its source location among 'old' candidates is wrong (it's NOT
        # in old); instead scan the store for its recorded line.
        with open(artifacts / "statements.jsonl", encoding="utf-8") as f:
            line_no = None
            file_rel = None
            for line in f:
                st = json.loads(line)
                if st["p"] == "contains" and st["o"] == target:
                    line_no = st["q"]["line"]
                    file_rel = st["q"]["file"]
                    break
        print(f"\nchecking {target}: recorded at {file_rel} store-line {line_no}")
        src_lines = (ROOT / file_rel).read_text(encoding="utf-8").splitlines()
        # store line is 0-based (LINE_BASE=0); physical source line is store_line+1
        phys = src_lines[line_no] if line_no is not None else None
        print("source text at that line:", repr(phys))
        # walk upward to find the nearest enclosing compound statement keyword
        indent = len(phys) - len(phys.lstrip()) if phys else None
        enclosing = None
        for i in range(line_no - 1, -1, -1):
            cand = src_lines[i]
            cand_indent = len(cand) - len(cand.lstrip())
            if cand.strip() and cand_indent < indent:
                enclosing = cand.strip()
                break
        print("nearest shallower enclosing line:", repr(enclosing))

        # page existence: title-match search across the fresh tree
        found_pages = []
        for p in out.rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            first = text.splitlines()[0] if text.splitlines() else ""
            if first.startswith("# ") and first[2:].strip() == target:
                found_pages.append(p.relative_to(out).as_posix())
        print("page(s) titled exactly this symbol:", found_pages)

    return 0


if __name__ == "__main__":
    sys.exit(main())
