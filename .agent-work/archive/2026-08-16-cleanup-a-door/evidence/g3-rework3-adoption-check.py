#!/usr/bin/env python3
"""m4-adoption's check: the falsified import-time-KeyError rationale is gone,
and the reason that replaced it is true.

Three assertions:

  A. LIVE MEASUREMENT, not text: import scripts/mcp_spine_server.py in a
     subprocess with SPINE_FILE and SPINE_ENGINE both REMOVED. It must succeed
     and leave `SPINE = None`. This is the fact that falsifies the old claim,
     re-measured every run rather than quoted from a report.
  B. no prose in tests/test_mcp_adoption.py still claims the door raises at
     import without those variables (AST string constants + comment runs,
     whitespace-collapsed).
  C. the replacement rationale is TRUE: the door's module scope really does
     bind SPINE/SESSION from the environment and really does insert into
     sys.path -- so the new text is not a second wrong reason.

It can fail: --demo-control runs predicate B against the exact deleted sentence.
"""
from __future__ import annotations

import ast
import io
import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "scripts" / "mcp_spine_server.py"
TEST = ROOT / "tests" / "test_mcp_adoption.py"

# "raises KeyError / dies / fails ... at import ... without both set", in either
# order, inside one sentence.
KEYERROR_CLAIM = re.compile(
    r"(?:KeyError|raises?|dies|fails)[^.]{0,120}\bIMPORT\b"
    r"|\bIMPORT\b[^.]{0,120}(?:KeyError|raises?\b|dies\b|fails\b)",
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


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    # A. live measurement in a clean subprocess.
    env = {k: v for k, v in os.environ.items()
           if k not in ("SPINE_FILE", "SPINE_ENGINE", "SPINE_SESSION", "SPINE_PARENT")}
    probe = (
        "import importlib.util, os\n"
        "assert 'SPINE_FILE' not in os.environ and 'SPINE_ENGINE' not in os.environ\n"
        f"s = importlib.util.spec_from_file_location('probe', r'{MODULE}')\n"
        "m = importlib.util.module_from_spec(s)\n"
        "s.loader.exec_module(m)\n"
        "print('SPINE=', m.SPINE)\n"
    )
    proc = subprocess.run([sys.executable, "-c", probe], env=env,
                          capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0:
        fail("importing the door with SPINE_FILE and SPINE_ENGINE both unset FAILED -- the "
             f"old rationale may have become true again:\n{proc.stderr.strip()}")
    if "SPINE= None" not in proc.stdout:
        fail(f"import succeeded but SPINE is not None: {proc.stdout.strip()}")

    # B. no surviving import-time-KeyError claim.
    scanned = 0
    for where, text in prose_of(TEST):
        scanned += 1
        hit = KEYERROR_CLAIM.search(text)
        if hit:
            fail(f"tests/test_mcp_adoption.py {where} still claims an import-time failure: "
                 f"...{text[max(0, hit.start() - 70):hit.end() + 70]}...")
    if scanned == 0:
        fail("scanned 0 prose fragments -- an empty sweep reports clean without looking")

    # C. the replacement rationale is true.
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    top = [ast.unparse(n) for n in tree.body
           if not isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))]
    binds = [s for s in top if re.match(r"(SPINE|SESSION)\b.*=", s)]
    syspath = [s for s in top if "sys.path.insert" in s]
    if not binds:
        fail("the door no longer binds SPINE/SESSION at module scope -- the replacement "
             "rationale would now be as false as the one it replaced")
    if not syspath:
        fail("the door no longer inserts into sys.path at module scope -- same problem")

    print("PASS  the import-time-KeyError rationale is gone and its replacement is true")
    print(f"  A. measured: import with both vars unset -> {proc.stdout.strip()}")
    print(f"  B. {scanned} prose fragments scanned in tests/test_mcp_adoption.py; 0 stale claims")
    print(f"  C. module scope really does: {binds}; {syspath}")


def demo_control() -> None:
    deleted = collapse(
        "Hand-typed here on purpose, not imported at module scope -- `mcp_spine_server` "
        "reads SPINE_FILE/SPINE_ENGINE from the environment at IMPORT time and raises "
        "KeyError without both set (its own module docstring says so), so importing it "
        "here would make collecting this file itself require a bound spine.")
    hit = KEYERROR_CLAIM.search(deleted)
    if not hit:
        print("CONTROL BROKEN: predicate B did not flag the deleted rationale")
        sys.exit(1)
    print(f"CONTROL OK: predicate B flags the deleted rationale -> {hit.group(0)!r}")


if __name__ == "__main__":
    if "--demo-control" in sys.argv:
        demo_control()
    else:
        main()
