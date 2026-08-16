#!/usr/bin/env python
"""The repaired passages tell one story (close criteria C2, C3, C4).

Runs the same clause set twice:

  * against the WORKING TREE  -- must PASS
  * against the blobs at BASE -- must FAIL

so the check proves it can reach a failing state instead of asserting it. The
base is pinned to an explicit commit, never `HEAD`: this lane commits as gates
close, and a HEAD-pinned check stops reproducing the moment the Commander
commits (the rework-2 reviewer's tc-C).

Six prose segments carry the claim. Each is extracted by its own anchors, so a
sentence in one segment cannot satisfy a clause required of another -- the exact
failure that produced B1, where the module header said the right thing while
`main()` in the same file said the retired one.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "84d949eb"

MARKER = re.compile(r"^\s*(#+|//+|\*|>+)?\s?")


def norm(text: str) -> str:
    """Lowercase, comment markers and emphasis gone, long dashes gone, one space."""
    lines = [MARKER.sub("", ln).strip() for ln in text.splitlines()]
    joined = " ".join(lines)
    joined = joined.replace("—", " ").replace("–", " ").replace("--", " ")
    joined = joined.replace("`", "").replace("*", "")
    return re.sub(r"\s+", " ", joined).lower().strip()


def read(path: str, *, base: str | None) -> str:
    if base is None:
        return (ROOT / path).read_text(encoding="utf-8")
    return subprocess.run(
        ["git", "show", f"{base}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def between(text: str, start: str, end: str, label: str) -> str:
    i = text.find(start)
    if i < 0:
        raise LookupError(f"{label}: start anchor not found: {start!r}")
    j = text.find(end, i)
    if j < 0:
        raise LookupError(f"{label}: end anchor not found: {end!r}")
    return text[i:j]


def module_docstring(text: str, label: str) -> str:
    doc = ast.get_docstring(ast.parse(text))
    if not doc:
        raise LookupError(f"{label}: no module docstring")
    return doc


def func_docstring(text: str, name: str, label: str) -> str:
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            doc = ast.get_docstring(node)
            if doc:
                return doc
    raise LookupError(f"{label}: no docstring on {name}()")


def segments(base: str | None) -> dict[str, str]:
    engine = read("scripts/checklist_engine.py", base=base)
    return {
        "engine-header": between(
            engine,
            "# Stamp-and-compare is RETIRED (#609 g2)",
            "# gauge reader binding",
            "engine-header",
        ),
        "engine-main": between(
            engine,
            "# Nothing stands between `load` and the arming below",
            "# #427: arm `refusals` here",
            "engine-main",
        ),
        "spine_lifecycle.build_origin": func_docstring(
            read("scripts/spine_lifecycle.py", base=base), "build_origin", "spine_lifecycle"
        ),
        "docs/CHECKLIST_SCHEMA.md": between(
            read("docs/CHECKLIST_SCHEMA.md", base=base),
            "**What reads it: nothing that decides anything",
            "## Engine session",
            "CHECKLIST_SCHEMA",
        ),
        "tests/test_spine_origin_isolation.py": module_docstring(
            read("tests/test_spine_origin_isolation.py", base=base), "test_spine_origin_isolation"
        ),
        "tests/test_worktree_derivation.py": module_docstring(
            read("tests/test_worktree_derivation.py", base=base), "test_worktree_derivation"
        ),
    }


# A stale claim in EITHER family, forbidden in every segment.
FORBIDDEN = [
    "the worktree is derived from the spine's own path",
    "a spine's worktree is derived from its path",
    "which is the actual ownership guard",
    "as it always was",
    "removed all three of its consumers",
    "had two consumers when it was written",
]

# R1's narrowed shape, required wherever a segment touches ownership: the
# widening is accepted, it is the leaseless path only, an active foreign lease
# is unchanged, and forgeable is not the same as absent. A hedge fails this.
R1_ENGINE_HEADER = [
    "only where one is actually held",
    "never claimed, or claimed and since released",
    "the leaseless path was widened",
    "that widening is accepted and deliberate",
    "forgeable guard is not the same as no guard",
    "under an active lease held by another session, nothing changed",
]
R1_ENGINE_MAIN = [
    "the lease is the ownership guard only where a lease exists",
    "never claimed, or claimed and since released",
    "widened that path",
    "that widening is accepted and deliberate",
    "forgeable guard is not the same as no guard",
    "under an active lease held by another session, nothing changed",
    "admiral_ruling-1 r1",
]
R1_LIFECYCLE = [
    "ownership is the lease, but only where a lease is actually held",
    "never claimed or claimed and since released",
    "widened the leaseless path",
    "the widening is accepted and deliberate",
    "forgeable guard is not the same as no guard",
    "under an active lease held by another session, nothing changed",
    "admiral_ruling-1 r1",
]
R1_SCHEMA = [
    "ownership is the lease",
    "only once an active lease exists",
    "never claimed, or claimed and since released",
    "widening is accepted",
    "forgeable guard is not the same as no guard",
    "nothing changed",
]
R1_ISOLATION = [
    "ownership is the lease, but only where one is actually held",
    "never claimed, or claimed and since released",
    "the leaseless path was widened",
    "that widening is accepted and deliberate",
    "forgeable guard is not the same as no guard",
    "under an active lease held by another session, nothing changed",
]

# C3: the two passages in scripts/checklist_engine.py must tell ONE story.
NO_LOCATION = "the engine now reads no location at all"

REQUIRED = {
    "engine-header": [NO_LOCATION, "no longer asks the question anywhere"] + R1_ENGINE_HEADER,
    "engine-main": [NO_LOCATION, "no longer asks the question anywhere"] + R1_ENGINE_MAIN,
    "spine_lifecycle.build_origin": [
        "the engine now reads no location at all, ambient or derived",
        "lives only in the stdlib-only hook",
    ] + R1_LIFECYCLE,
    "docs/CHECKLIST_SCHEMA.md": ["the engine reads no location, ambient or derived"] + R1_SCHEMA,
    "tests/test_spine_origin_isolation.py": [
        "the engine now reads no location at all",
    ] + R1_ISOLATION,
    "tests/test_worktree_derivation.py": [
        "there is one lexical rule and one implementation of it",
    ],
}

# The consumer count, told one way. Required in the four segments that state it.
COUNT_SEGMENTS = [
    "engine-header",
    "docs/CHECKLIST_SCHEMA.md",
    "tests/test_spine_origin_isolation.py",
    "tests/test_worktree_derivation.py",
]
COUNT_SENTENCE = re.compile(
    r"it had two consumers.*?a definition nothing calls is not shipped\.", re.S
)


def run(base: str | None, label: str) -> list[str]:
    problems: list[str] = []
    try:
        segs = {name: norm(text) for name, text in segments(base).items()}
    except LookupError as exc:
        return [f"{label}: {exc}"]

    for name, text in segs.items():
        for phrase in FORBIDDEN:
            if norm(phrase) in text:
                problems.append(f"{label}: {name}: STALE claim present: {phrase!r}")
        for phrase in REQUIRED[name]:
            if norm(phrase) not in text:
                problems.append(f"{label}: {name}: missing required clause: {phrase!r}")

    found: dict[str, str] = {}
    for name in COUNT_SEGMENTS:
        m = COUNT_SENTENCE.search(segs[name])
        if not m:
            problems.append(f"{label}: {name}: the canonical consumer-count sentence is absent")
        else:
            found[name] = m.group(0)
    if len(found) == len(COUNT_SEGMENTS) and len(set(found.values())) != 1:
        problems.append(f"{label}: the consumer-count sentence differs between copies: {found}")
    return problems


def main() -> int:
    tree = run(None, "working-tree")
    base = run(BASE, f"base {BASE}")

    print(f"== working tree: {'PASS' if not tree else 'FAIL'} ({len(tree)} problem(s))")
    for p in tree:
        print(f"   {p}")
    print(f"\n== base {BASE} (must FAIL, or this check cannot discriminate): "
          f"{'FAIL as expected' if base else 'PASS -- NOT DISCRIMINATING'} "
          f"({len(base)} problem(s))")
    for p in base:
        print(f"   {p}")

    if tree:
        print("\nRESULT: the working tree still carries a stale or incomplete claim.")
        return 1
    if not base:
        print("\nRESULT: the check passes on the pre-repair base, so it proves nothing.")
        return 1
    print(f"\nRESULT: OK -- red at {BASE}, green on the working tree, "
          f"6 segments x {sum(len(v) for v in REQUIRED.values()) + len(FORBIDDEN) * 6} "
          f"clause assertions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
