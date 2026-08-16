#!/usr/bin/env python
"""Both ruling citations survive the repair (close criterion C8).

Counted against the blobs at an explicit base commit, never `HEAD`.

  * the **2026-08-15 worktree-identity** supersession citation must survive
    everywhere it appeared -- per file, the tree must carry at least as many
    occurrences as the base;
  * the **2026-08-16 worktree-is-location** citation, outside `.agent-work/`
    and `map/`, must still be exactly **one** -- the reviewer verified that
    count at base, and one is the number to keep.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "84d949eb"

SUPERSESSION = re.compile(r"2026-08-15\s+worktree-identity", re.I)
LOCATION = re.compile(r"2026-08-16\s+worktree-is-location", re.I)

SUFFIXES = {".py", ".md", ".json", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".sh", ".ps1"}
EXCLUDE_PREFIXES = (".agent-work/", "map/")


def tracked(rev: str | None) -> list[str]:
    cmd = ["git", "ls-files"] if rev is None else ["git", "ls-tree", "-r", "--name-only", rev]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if Path(p).suffix.lower() in SUFFIXES]


def content(rel: str, rev: str | None) -> str:
    if rev is None:
        try:
            return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
    r = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


MARKER = re.compile(r"^\s*(#+|//+|\*|>+)?\s?")


def flatten(text: str) -> str:
    """Comment markers off, whitespace collapsed -- a citation that wraps across
    two comment lines is one string again, which is how it reads."""
    return re.sub(r"\s+", " ", " ".join(MARKER.sub("", ln).strip() for ln in text.splitlines()))


def counts(pattern: re.Pattern, rev: str | None, *, exclude: bool) -> Counter:
    c = Counter()
    for rel in tracked(rev):
        if exclude and rel.startswith(EXCLUDE_PREFIXES):
            continue
        n = len(pattern.findall(flatten(content(rel, rev))))
        if n:
            c[rel] = n
    return c


def main() -> int:
    problems: list[str] = []

    base_s = counts(SUPERSESSION, BASE, exclude=True)
    tree_s = counts(SUPERSESSION, None, exclude=True)
    print(f"2026-08-15 worktree-identity supersession citation (outside {EXCLUDE_PREFIXES}):")
    for rel in sorted(set(base_s) | set(tree_s)):
        mark = "ok" if tree_s[rel] >= base_s[rel] else "LOST"
        print(f"  {rel}: {BASE}={base_s[rel]} tree={tree_s[rel]}  {mark}")
        if tree_s[rel] < base_s[rel]:
            problems.append(f"supersession citation lost in {rel}")
    print(f"  totals: {BASE}={sum(base_s.values())} tree={sum(tree_s.values())}")
    if not base_s:
        problems.append("no supersession citation found at base -- the pattern cannot be matching")

    base_l = counts(LOCATION, BASE, exclude=True)
    tree_l = counts(LOCATION, None, exclude=True)
    print(f"\n2026-08-16 worktree-is-location citation (outside {EXCLUDE_PREFIXES}):")
    for rel in sorted(set(base_l) | set(tree_l)):
        print(f"  {rel}: {BASE}={base_l[rel]} tree={tree_l[rel]}")
    total_base, total_tree = sum(base_l.values()), sum(tree_l.values())
    print(f"  totals: {BASE}={total_base} tree={total_tree}")
    if total_base != 1:
        problems.append(f"base count is {total_base}, not the 1 the reviewer measured")
    if total_tree != 1:
        problems.append(f"tree count is {total_tree}, not 1")

    if problems:
        print("\nFAIL:")
        for p in problems:
            print(f"  {p}")
        return 1
    print("\nOK: every supersession citation survives, and worktree-is-location is still exactly one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
