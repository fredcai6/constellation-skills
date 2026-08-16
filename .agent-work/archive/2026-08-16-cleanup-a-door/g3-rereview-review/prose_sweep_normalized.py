"""Blast-radius sweep for INVALIDATED CLAIMS, immune to source line-splitting.

The implementer's sweep ran `git grep -n 're-read fresh'` and reported 0 hits.
That grep is line-oriented, and CREW_CONTEXT.md warns about exactly this: a
message assembled from adjacent string literals never contains the phrase on any
single line. tests/test_mcp_lifecycle.py:200-201 splits it as `"...re-read "`
`"fresh)..."`, so the phrase is invisible to grep while being plainly present to
a reader.

This sweep normalizes each file -- joins adjacent Python string literals, then
collapses all whitespace -- before searching, so a split phrase is found.
"""

import re
import subprocess
import sys

# Claims that 4e1f22cb invalidated, and what makes each one false now.
CLAIMS = {
    "re-read fresh": "spine_open no longer re-reads SPINE_FILE fresh; that read was the KeyError #603 removed",
    "binds exactly one file at import time": "bind-on-open means binding can now change at runtime",
    'SPINE = Path(os.environ["SPINE_FILE"]).resolve()': "that expression was deleted by 4e1f22cb",
    "SPINE = Path(os.environ['SPINE_FILE']).resolve()": "same expression, single-quoted form",
}

# Dated records: statements about the tree as it stood when written, correctly pinned.
DATED = re.compile(r"^(\.agent-work/|notes-[a-z]\.md|episodes/retired/)")


def tracked_text_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\n") if p.strip()]


def normalized(path):
    """File text with adjacent string literals joined and whitespace collapsed."""
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except (IsADirectoryError, FileNotFoundError):
        return None
    # Join adjacent Python string literals:  "...abc "\n   "def..."  ->  "...abcdef..."
    joined = re.sub(r'"\s*\n\s*"', "", raw)
    joined = re.sub(r"'\s*\n\s*'", "", joined)
    return re.sub(r"\s+", " ", joined)


def main():
    files = tracked_text_files()
    print(f"tracked files swept: {len(files)}")

    live, dated = [], []
    for path in files:
        text = normalized(path)
        if text is None:
            continue
        for claim in CLAIMS:
            probe = re.sub(r"\s+", " ", claim)
            if probe in text:
                (dated if DATED.match(path) else live).append((path, claim))

    print(f"\nhits in DATED RECORDS (history, correctly pinned): {len(dated)}")
    for path, claim in dated:
        print(f"  {path}: {claim!r}")

    print(f"\nLIVE hits -- prose asserting something no longer true: {len(live)}")
    for path, claim in live:
        print(f"  {path}: {claim!r}\n      why false: {CLAIMS[claim]}")

    # Prove the normalization is what finds the split phrase, not a coincidence.
    print("\n--- control: does a plain line-oriented grep see them? ---")
    for claim in sorted({c for _, c in live}):
        r = subprocess.run(["git", "grep", "-c", "-F", claim, "HEAD"],
                           capture_output=True, text=True)
        n = len([l for l in r.stdout.splitlines() if l.strip()])
        print(f"  grep -F {claim!r}: {n} file(s) -- normalized sweep found "
              f"{len([1 for _, c in live if c == claim])}")

    print(f"\nRESULT: {len(live)} live invalidated claim(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
