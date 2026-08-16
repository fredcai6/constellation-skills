"""Independent blast-radius sweep for 4e1f22cb, measured at HEAD.

Derives the identifier list FROM THE COMMIT -- every name the commit removed at a
definition or assignment site -- then asks, word-bounded, what still references each
one at HEAD. Word-bounding matters: an unbounded grep for CALLLOG also hits the
surviving env var SPINE_CALLLOG, which this change deliberately preserves.

Prints the count at every stage, per CREW_CONTEXT.md "any guard that loops must
assert what it looped over".
"""

import re
import subprocess
import sys

COMMIT = "4e1f22cb"


def run(*cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode not in (0, 1):  # grep-family: 1 == no match
        raise SystemExit(f"command failed: {cmd}\n{r.stderr}")
    return r.stdout


def removed_identifiers() -> set[str]:
    """Names this commit removed at a def/class/CONSTANT-assignment site."""
    diff = run("git", "show", COMMIT, "-U0")
    names = set()
    for line in diff.splitlines():
        if not line.startswith("-") or line.startswith("---"):
            continue
        body = line[1:].strip()
        m = re.match(r"(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", body)
        if m:
            names.add(m.group(1))
            continue
        m = re.match(r"([A-Z][A-Z0-9_]{2,})\s*(?::[^=]+)?=", body)
        if m:
            names.add(m.group(1))
    return names


def still_defined_at_head(name: str) -> bool:
    """A name re-bound elsewhere at HEAD was moved, not stranded."""
    out = run("git", "grep", "-nwE", rf"(def|class)\s+{re.escape(name)}\b|^{re.escape(name)}\s*=",
              "HEAD", "--", "*.py", check=False)
    return bool(out.strip())


DATED_RECORD = re.compile(r"^HEAD:(\.agent-work/|notes-[a-z]\.md|episodes/)")


def main() -> int:
    removed = sorted(removed_identifiers())
    print(f"identifiers removed by {COMMIT}: {len(removed)}")
    for n in removed:
        print(f"  - {n}")

    stranded_candidates = [n for n in removed if not still_defined_at_head(n)]
    survived = [n for n in removed if n not in stranded_candidates]
    print(f"\nre-bound elsewhere at HEAD (moved, not stranded): {len(survived)} -> {survived}")
    print(f"genuinely gone at HEAD: {len(stranded_candidates)} -> {stranded_candidates}")

    print("\n--- live references at HEAD, word-bounded, whole tree ---")
    live, dated = [], []
    for name in stranded_candidates:
        out = run("git", "grep", "-nw", name, "HEAD", check=False)
        for line in out.splitlines():
            (dated if DATED_RECORD.match(line) else live).append((name, line))

    print(f"references in DATED RECORDS (history, correctly pinned -- not drift): {len(dated)}")
    for name, line in dated:
        print(f"  [{name}] {line[:150]}")

    print(f"\nLIVE references still naming a deleted identifier: {len(live)}")
    for name, line in live:
        print(f"  [{name}] {line[:200]}")

    # Second angle: the prose claim the commit invalidated WITHOUT renaming anything.
    print("\n--- prose claims invalidated without a rename ---")
    for probe in ("re-read fresh", r"os\.environ\[.SPINE_FILE.\]"):
        out = run("git", "grep", "-nE", probe, "HEAD", "--",
                  ":!.agent-work", ":!*notes-*.md", check=False)
        hits = [l for l in out.splitlines() if l.strip()]
        print(f"  {probe!r}: {len(hits)} hit(s)")
        for h in hits:
            print(f"    {h[:200]}")

    print(f"\nRESULT: {len(live)} live stranded reference(s) at HEAD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
