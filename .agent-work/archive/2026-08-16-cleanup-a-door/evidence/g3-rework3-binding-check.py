#!/usr/bin/env python3
"""m2-binding's check: no "bound at server-launch time" claim survives where
`_bind_process_to` said none may.

`_bind_process_to`'s own docstring is the requirement, quoted in the code:
"the module docstring's 'bound at server-launch time' is now 'bound at launch
OR at `spine_open`', and nothing may be left describing the previous spine."

Two assertions, both over AST string constants (so implicit concatenation is
already joined by the parser) plus comment runs, whitespace-collapsed (so a
claim broken across lines is still visible):

  A. `_bind_process_to` still exists and still assigns both identity roots --
     the FACT that makes "bound at launch OR at spine_open" true. Without it
     the corrected prose would be the new lie.
  B. neither scripts/mcp_spine_server.py nor tests/test_mcp_identity.py carries
     a surviving launch-time-ONLY binding claim: "bound at server-launch time"
     not immediately qualified by a spine_open/rebind mention within the same
     sentence.

It can fail: --demo-control runs predicate B against both exact pre-change
sentences.
"""
from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGETS = (ROOT / "scripts" / "mcp_spine_server.py",
           ROOT / "tests" / "test_mcp_identity.py")
BINDER = "_bind_process_to"

# "bound at (server-)launch time", where the same sentence does NOT go on to
# name the second binding moment. `[^.]` keeps it inside one sentence.
#
# `\b` on every alternative is load-bearing, and the control is what found it:
# an unanchored `OR at` matches inside "the d[oor at] a different spine", so the
# lookahead fired on the pre-change sentence and the predicate reported clean at
# HEAD -- a check that could not fail, caught by running it against the text it
# was written to catch.
STALE = re.compile(
    r"bound at (?:server-)?launch[- ]time(?![^.]{0,200}"
    r"(?:\bspine_open\b|\bOR at\b|\brebind\w*\b|\bre-bind\w*\b|\b_bind_process_to\b))",
    re.IGNORECASE,
)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def prose_of(path: Path) -> list[tuple[str, str]]:
    """Every string constant and comment run in a file, whitespace-collapsed.

    Strings come from the AST, so `"a " "b"` is already one constant. Comments
    come from the tokenizer, joined into runs so a claim spanning several `#`
    lines reads as one sentence -- a line-based grep cannot see either.
    """
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
    # A. the binder that makes the corrected prose true.
    tree = ast.parse(TARGETS[0].read_text(encoding="utf-8"))
    binder = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == BINDER), None)
    if binder is None:
        fail(f"{BINDER} is gone -- 'bound at launch OR at spine_open' would be false")
    assigned = {t.id for stmt in binder.body for n in ast.walk(stmt)
                if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    missing = {"SPINE", "SESSION"} - assigned
    if missing:
        fail(f"{BINDER} no longer assigns {sorted(missing)} -- a door bound on only one "
             "root cannot claim, so the corrected prose would overstate what happens")

    # B. no surviving launch-time-only claim.
    scanned = 0
    for path in TARGETS:
        for where, text in prose_of(path):
            scanned += 1
            hit = STALE.search(text)
            if hit:
                fail(f"{path.relative_to(ROOT)} {where} still carries a launch-time-only "
                     f"binding claim: ...{text[max(0, hit.start() - 60):hit.end() + 90]}...")
    if scanned == 0:
        fail("scanned 0 prose fragments -- an empty sweep reports clean without looking")

    print("PASS  no launch-time-only binding claim survives")
    print(f"  A. {BINDER} assigns both identity roots: {sorted(assigned & {'SPINE', 'SESSION'})}")
    print(f"  B. {scanned} prose fragments scanned across "
          f"{', '.join(str(p.relative_to(ROOT)) for p in TARGETS)}; 0 stale claims")


def demo_control() -> None:
    pre = {
        "scripts/mcp_spine_server.py:30": collapse(
            "Ambient state is bound at server-launch time from the environment, NOT "
            "exposed as tool arguments (so a model cannot point the door at a different "
            "spine or identity mid-conversation):"),
        "tests/test_mcp_identity.py:547": collapse(
            "DC3, at the seam `mcp_spine_server.py`'s own module docstring names: "
            "'Ambient state is bound at server-launch time from the environment ... "
            "that is the seam identity rides on.' This class measures whether a process"),
    }
    bad = [k for k, v in pre.items() if not STALE.search(v)]
    if bad:
        print(f"CONTROL BROKEN: predicate B did not flag {bad}")
        sys.exit(1)
    for k, v in pre.items():
        print(f"CONTROL OK: predicate B flags {k} -> {STALE.search(v).group(0)!r}")


if __name__ == "__main__":
    if "--demo-control" in sys.argv:
        demo_control()
    else:
        main()
