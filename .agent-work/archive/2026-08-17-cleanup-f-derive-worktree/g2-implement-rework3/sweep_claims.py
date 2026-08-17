#!/usr/bin/env python
"""Claim-level sweep for #609 g2 rework 3 (close criterion C1).

Sweeps for the CLAIM, not for the symbol. Every grep written on this gate so
far -- in both handoffs and in the reviewer's own C1 -- keyed on the name
`worktree_from_spine_path`, and the two stale passages the rework-2 review
found do not contain it. This sweep never mentions that name.

Two families:

  derive     -- prose saying a worktree is derived/computed/resolved FROM a
                spine's (or a checklist's) path. Stale iff the sentence
                attributes the derivation to the engine or to the codebase
                generally, because as of 84d949eb the engine derives nothing
                anywhere; the rule lives only in `spine_rail._worktree_from_spine`.

  ownership  -- prose asserting that the lease IS / ALWAYS WAS the ownership
                guard. Stale iff unqualified: ADMIRAL_RULING-1 R1 declared that
                false as written and narrowed it to "only where a lease exists".

Matching is done on a whitespace-normalized, comment-marker-stripped rendering
of each file, so a claim that wraps across two comment lines or two docstring
lines is still one sentence to the patterns. Every hit reports the line the
match STARTS on.

Prints the number of files scanned and the number of hits per family: a sweep
that looped over nothing must not read like a clean sweep.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Text-ish files only; the sweep is over prose.
SUFFIXES = {".py", ".md", ".json", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".sh", ".ps1"}

# A claim may wrap across comment or docstring lines; strip the leading marker
# so `# path` continues the sentence started on the line above.
MARKER = re.compile(r"^\s*(#+|//+|\*|>+)?\s?")

DERIVE = [
    # "...worktree is derived from the spine's own path...", any direction.
    re.compile(r"deriv\w*.{0,160}?worktree", re.I | re.S),
    re.compile(r"worktree.{0,160}?\bderiv\w*", re.I | re.S),
    # the same claim without the word "derive"
    re.compile(r"worktree.{0,80}?\b(computed|resolved|inferred|read)\b.{0,40}?\bfrom\b.{0,60}?\b(spine|checklist)\b.{0,40}?\bpath\b", re.I | re.S),
    re.compile(r"\bfrom\b.{0,40}?\bspine's own path\b", re.I | re.S),
]

OWNERSHIP = [
    re.compile(r"ownership guard", re.I),
    re.compile(r"ownership is the lease", re.I),
    re.compile(r"\blease\b.{0,60}?\b(is|was|remains)\b.{0,40}?\bownership\b", re.I | re.S),
    re.compile(r"\bownership\b.{0,40}?\bis\b.{0,20}?\bthe lease\b", re.I | re.S),
    re.compile(r"as it always was", re.I),
]

FAMILIES = {"derive": DERIVE, "ownership": OWNERSHIP}


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    paths = []
    for rel in out.split("\0"):
        if not rel:
            continue
        p = ROOT / rel
        if p.suffix.lower() in SUFFIXES and p.is_file():
            paths.append(p)
    return paths


def render(path: Path) -> tuple[str, list[int]]:
    """Return (normalized text, char-index -> line-number map)."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", []
    buf: list[str] = []
    lines: list[int] = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        stripped = MARKER.sub("", line).strip()
        chunk = stripped + " "
        buf.append(chunk)
        lines.extend([lineno] * len(chunk))
    return "".join(buf), lines


def main() -> int:
    files = tracked_files()
    hits: dict[str, list[tuple[str, int, str]]] = {name: [] for name in FAMILIES}
    for path in files:
        text, lines = render(path)
        if not text:
            continue
        for family, patterns in FAMILIES.items():
            seen: set[int] = set()
            for pat in patterns:
                for m in pat.finditer(text):
                    lineno = lines[m.start()] if m.start() < len(lines) else 0
                    if lineno in seen:
                        continue
                    seen.add(lineno)
                    excerpt = re.sub(r"\s+", " ", m.group(0))[:190]
                    hits[family].append(
                        (str(path.relative_to(ROOT)).replace("\\", "/"), lineno, excerpt)
                    )

    print(f"files scanned: {len(files)}")
    total = 0
    for family in FAMILIES:
        rows = sorted(hits[family])
        total += len(rows)
        print(f"\n=== family: {family} -- {len(rows)} hit(s) ===")
        for rel, lineno, excerpt in rows:
            print(f"{rel}:{lineno}: {excerpt}")
    print(f"\ntotal hits across both families: {total}")

    if not files:
        print("FAIL: scanned no files -- a sweep over nothing is not a clean sweep.")
        return 1
    if total == 0:
        print("FAIL: zero hits over both families -- the patterns cannot be matching.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
