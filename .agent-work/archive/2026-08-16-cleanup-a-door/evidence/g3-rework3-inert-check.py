#!/usr/bin/env python3
"""m3-inert-write's check: the inverted comment and the write it justified are
gone, and the fact they misdescribed still holds.

Three assertions:

  A. `_spine_open`'s executable body reads `os.environ` exactly once, for
     `SPINE_PARENT`. This is the FACT. The deleted comment claimed the opposite
     -- that `_spine_open` deliberately re-reads `SPINE_FILE` at call time and
     never the module's bound `SPINE`.
  B. the escaping-work_id test's own body contains no assignment to
     `os.environ["SPINE_FILE"]` -- the write that comment justified.
  C. no prose in tests/test_mcp_lifecycle.py claims `_spine_open` reads
     `SPINE_FILE`, over AST string constants and comment runs, collapsed.

It can fail: --demo-control runs predicate C against the exact deleted comment
and predicate B against the exact deleted line.
"""
from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "scripts" / "mcp_spine_server.py"
TEST = ROOT / "tests" / "test_mcp_lifecycle.py"
TESTNAME = "test_spine_open_refuses_before_open_work_ever_runs_when_the_worktree_would_escape"

# "_spine_open (or spine_open) ... reads/re-reads ... SPINE_FILE", either order,
# within one sentence.
CLAIM = re.compile(
    r"_?spine_open[^.]{0,120}(?:re-?reads?|reads|re-?reading|reading)[^.]{0,60}SPINE_FILE"
    r"|(?:re-?reads?|reads|re-?reading|reading)[^.]{0,60}SPINE_FILE[^.]{0,120}_?spine_open",
    re.IGNORECASE,
)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def prose_of(path: Path) -> list[tuple[str, str]]:
    src = path.read_text(encoding="utf-8")
    out: list[tuple[str, str]] = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append((f"string@{node.lineno}", collapse(node.value)))
    run: list[str] = []
    start = 0
    prev = -2
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            if tok.start[0] != prev + 1 and run:
                out.append((f"comment@{start}", collapse(" ".join(run))))
                run = []
            if not run:
                start = tok.start[0]
            run.append(tok.string.lstrip("#").strip())
            prev = tok.start[0]
    if run:
        out.append((f"comment@{start}", collapse(" ".join(run))))
    return out


def environ_writes(fn: ast.FunctionDef, *, ignore_restores: bool = False) -> list[str]:
    """Assignments of the form `os.environ[...] = ...` inside `fn`.

    `ignore_restores` skips a write whose VALUE is a bare `saved_*` name. The
    deleted line set an environment variable to a computed value, which is
    setup; a restore hands back a value read at the top of the same function,
    which is teardown and cannot make a stale claim about what the code reads.
    The distinction is not cosmetic -- this gate's allowed scope is the setup
    write alone, and the save/restore pair around it stays (see the result's
    out-of-scope observations: it is now a no-op saving and restoring the same
    value, real dead scaffolding, but removing it is a logic change this gate's
    stop conditions forbid).
    """
    hits = []
    body = fn.body[1:] if ast.get_docstring(fn) is not None else fn.body
    for stmt in body:
        for n in ast.walk(stmt):
            if not isinstance(n, ast.Assign):
                continue
            if (ignore_restores and isinstance(n.value, ast.Name)
                    and n.value.id.startswith("saved_")):
                continue
            for t in n.targets:
                if isinstance(t, ast.Subscript) and "os.environ" in ast.unparse(t.value):
                    hits.append(ast.unparse(t))
    return hits


def environ_reads(fn: ast.FunctionDef) -> list[str]:
    """Every `os.environ` read inside `fn`, as the key it names."""
    keys = []
    body = fn.body[1:] if ast.get_docstring(fn) is not None else fn.body
    for stmt in body:
        for n in ast.walk(stmt):
            if isinstance(n, ast.Subscript) and "os.environ" in ast.unparse(n.value):
                keys.append(ast.unparse(n))
            elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr in ("get", "pop")
                  and "os.environ" in ast.unparse(n.func.value)):
                keys.append(ast.unparse(n))
    return keys


def find(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    return next((n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == name), None)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    # A. the fact the deleted comment misdescribed.
    fn = find(ast.parse(MODULE.read_text(encoding="utf-8")), "_spine_open")
    if fn is None:
        fail("_spine_open is gone")
    reads = environ_reads(fn)
    if len(reads) != 1 or "SPINE_PARENT" not in reads[0]:
        fail(f"_spine_open's environment reads are now {reads} -- expected exactly one, "
             "for SPINE_PARENT; the deleted comment's claim may have become true again")

    # B. the write the comment justified is gone.
    test_tree = ast.parse(TEST.read_text(encoding="utf-8"))
    tfn = find(test_tree, TESTNAME)
    if tfn is None:
        fail(f"{TESTNAME} is gone -- the test whose setup line this gate deleted")
    writes = [w for w in environ_writes(tfn, ignore_restores=True) if "SPINE_FILE" in w]
    if writes:
        fail(f"{TESTNAME} still writes {writes}")

    # C. no surviving prose claim in the whole test file.
    scanned = 0
    for where, text in prose_of(TEST):
        scanned += 1
        hit = CLAIM.search(text)
        if hit:
            fail(f"tests/test_mcp_lifecycle.py {where} still claims spine_open reads "
                 f"SPINE_FILE: ...{hit.group(0)}...")
    if scanned == 0:
        fail("scanned 0 prose fragments -- an empty sweep reports clean without looking")

    print("PASS  the inverted comment and its inert write are gone")
    print(f"  A. _spine_open reads os.environ once: {reads[0]}")
    print(f"  B. {TESTNAME} writes no SPINE_FILE")
    print(f"  C. {scanned} prose fragments scanned in tests/test_mcp_lifecycle.py; 0 stale claims")


def demo_control() -> None:
    deleted_comment = collapse(
        "`_spine_open` deliberately RE-READS `SPINE_FILE` from the environment "
        "at call time (never the module's own bound `SPINE` -- that is the "
        "whole point of the identity pin above), so it must still be set now, "
        "not merely during `_load_module`'s own import (which already "
        "restored the surrounding environment by the time this line runs).")
    hit = CLAIM.search(deleted_comment)
    if not hit:
        print("CONTROL BROKEN: predicate C did not flag the deleted comment")
        sys.exit(1)
    print(f"CONTROL OK: predicate C flags the deleted comment -> {hit.group(0)!r}")

    # Run B exactly as main() runs it -- ignore_restores=True -- so the control
    # tests the narrowed predicate, not a looser one that main() never uses.
    probe = ast.parse(
        "def f():\n"
        "    saved_spine_file = os.environ.get('SPINE_FILE')\n"
        "    os.environ['SPINE_FILE'] = str(bound_spine)\n"
        "    os.environ['SPINE_FILE'] = saved_spine_file\n")
    writes = [w for w in environ_writes(find(probe, "f"), ignore_restores=True)
              if "SPINE_FILE" in w]
    if len(writes) != 1:
        print(f"CONTROL BROKEN: predicate B flagged {writes} -- expected exactly the "
              "deleted setup write, with the restore correctly ignored")
        sys.exit(1)
    print(f"CONTROL OK: predicate B flags the deleted setup write and ignores the "
          f"restore beside it -> {writes}")


if __name__ == "__main__":
    if "--demo-control" in sys.argv:
        demo_control()
    else:
        main()
