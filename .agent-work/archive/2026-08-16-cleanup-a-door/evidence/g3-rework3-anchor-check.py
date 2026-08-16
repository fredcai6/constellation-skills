#!/usr/bin/env python3
"""m1-anchor's check: the module docstring's checkout-anchor claim agrees with
the code that runs.

Not a grep for wording. Three assertions, each measured from the AST:

  A. `_primary_checkout_for_lifecycle` references `SPINE_FILE` zero times --
     this is the FACT the docstring must describe.
  B. that function's anchor expression names `SPINE` -- the binding the old
     text said it used "rather than".
  C. the module docstring contains no surviving claim that the primary
     checkout is derived from `SPINE_FILE`, and does name the helper the code
     actually calls.

It can fail: at HEAD the docstring said "deriving the primary checkout it opens
work from fresh off `SPINE_FILE`", which C rejects. Run with --demo-control to
see C go red against that exact pre-change sentence.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[3] / "scripts" / "mcp_spine_server.py"
HELPER = "_primary_checkout_for_lifecycle"

# The claim class this change invalidated: the primary checkout described as
# derived from SPINE_FILE / ambient launch-time state, rather than from SPINE.
DERIVATION_VERB = r"deriv\w*|derives|fresh off|re-?reads?|reads"
INVALIDATED = re.compile(
    rf"(?:primary\s+)?checkout[^.]{{0,120}}(?:{DERIVATION_VERB})[^.]{{0,60}}SPINE_FILE"
    rf"|(?:{DERIVATION_VERB})[^.]{{0,80}}SPINE_FILE[^.]{{0,120}}checkout",
    re.IGNORECASE,
)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    src = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(src)

    helper = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == HELPER), None,
    )
    if helper is None:
        fail(f"{HELPER} is gone -- the docstring's subject no longer exists")

    # A. the helper reads SPINE_FILE zero times. Its own docstring is EXCLUDED:
    #    it narrates the `os.environ["SPINE_FILE"]` read #603 deleted, and this
    #    assertion is about what executes, not about what the prose recounts.
    body = helper.body[1:] if ast.get_docstring(helper) is not None else helper.body
    names = {n.id for stmt in body for n in ast.walk(stmt) if isinstance(n, ast.Name)}
    consts = {n.value for stmt in body for n in ast.walk(stmt)
              if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    spine_file_hits = sorted(x for x in (names | consts) if "SPINE_FILE" in x)
    if spine_file_hits:
        fail(f"{HELPER} now references SPINE_FILE {spine_file_hits} -- "
             "the corrected docstring would be describing the wrong anchor")

    # B. the anchor expression names SPINE.
    anchor = next(
        (n for n in ast.walk(helper)
         if isinstance(n, ast.Assign)
         and any(isinstance(t, ast.Name) and t.id == "anchor" for t in n.targets)), None,
    )
    if anchor is None:
        fail(f"{HELPER} no longer assigns `anchor` -- re-read it before trusting this check")
    anchor_src = ast.unparse(anchor.value)
    if "SPINE" not in anchor_src:
        fail(f"{HELPER}'s anchor no longer names SPINE: {anchor_src}")

    # C. no surviving SPINE_FILE-derived-checkout claim in the module docstring,
    #    and the helper the code calls is named.
    doc = collapse(ast.get_docstring(tree) or "")
    hit = INVALIDATED.search(doc)
    if hit:
        fail("the module docstring still derives the primary checkout from "
             f"SPINE_FILE: ...{hit.group(0)}...")
    if HELPER not in doc:
        fail(f"the module docstring does not name {HELPER}, the helper the code "
             "actually calls -- it is describing something else")

    print("PASS  anchor claim agrees with the code")
    print(f"  A. {HELPER} references SPINE_FILE 0 times")
    print(f"  B. anchor = {anchor_src}")
    print(f"  C. module docstring: no SPINE_FILE-derived-checkout claim; names {HELPER}")


def demo_control() -> None:
    """Prove C can fail, against the exact pre-change sentence."""
    pre = collapse(
        "`spine_open` never references `SPINE`, `SESSION` or `run_engine` "
        "(checked, not merely claimed -- see `tests/test_mcp_lifecycle.py`), "
        "deriving the primary checkout it opens work from fresh off `SPINE_FILE` "
        "(ambient, server-launch-time state) rather than the module's own `SPINE` binding;"
    )
    hit = INVALIDATED.search(pre)
    if not hit:
        print("CONTROL BROKEN: predicate C did not flag the pre-change sentence")
        sys.exit(1)
    print(f"CONTROL OK: predicate C flags the pre-change sentence -> {hit.group(0)!r}")


if __name__ == "__main__":
    if "--demo-control" in sys.argv:
        demo_control()
    else:
        main()
