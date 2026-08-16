#!/usr/bin/env python3
"""Blast-radius sweep for the #603-invalidated claim -- AST-aware and
whitespace-normalized, NOT line-based.

Rework 1's sweep was a line-based `git grep`, which cannot see a phrase built
from two adjacent string literals: such a phrase appears on no single line.
This sweep runs two layers over every tracked text file.

  Layer A -- every tracked text file, whitespace collapsed to single spaces, so
             a phrase broken across LINES is visible.
  Layer B -- tracked .py files, via the AST: adjacent string literals are
             ALREADY concatenated by the parser, so a phrase broken across
             LITERALS is visible too. Plus every comment token.

Layer B is the one that sees what grep and Layer A cannot, because a literal
boundary (`"...re-read " "fresh..."`) survives whitespace normalization as
`re-read " "fresh`.

THE INVALIDATED CLAIM. #603 removed `_spine_open`'s `SPINE_FILE` read. Measured
at HEAD by AST: `_spine_open` touches `os.environ` once, for `SPINE_PARENT`;
`_primary_checkout_for_lifecycle`, which yields the repo root, touches it zero
times. So any text saying that `spine_open` derives its checkout from
`SPINE_FILE` is now false. That conjunction -- a trigger word, `SPINE_FILE`,
and `spine_open` in the same claim window -- is what this sweep hunts. A
trigger beside `SPINE_FILE` WITHOUT `spine_open` is a different, still-true
statement (the module binds `SPINE_FILE` at server-launch time; run_crew
dispatch env), and is reported separately rather than counted.

Usage:  py .agent-work/cleanup-a-door/evidence/g3-rework2-sweep.py [--rev REV]
"""
import ast
import io
import re
import subprocess
import sys
import tokenize

TRIGGER = re.compile(r"re-?read\s+fresh|ambient|fresh off|deriv\w+", re.I)
NAMES_FILE = re.compile(r"SPINE_FILE")
NAMES_OPEN = re.compile(r"_?spine_open", re.I)
WINDOW = 200  # chars either side of a trigger that count as one claim

# My allowed scope this rework (handoff: the failure-message string only).
ALLOWED_SCOPE = ("tests/test_mcp_lifecycle.py",)
# Fenced by the handoff: report, never fix.
FENCED = ("scripts/hooks/spine_rail.py",)
# Records that were true when written; not live claims.
HISTORICAL_DIRS = (".agent-work/", "episodes/", "docs/decisions/")
HISTORICAL_FILES = ("notes-",)


def sh(*argv):
    return subprocess.run(argv, capture_output=True, text=True, check=True).stdout


def tracked_files(rev):
    out = sh("git", "ls-tree", "-r", "--name-only", rev) if rev else sh("git", "ls-files")
    return [p for p in out.splitlines() if p]


def read(path, rev):
    if rev:
        r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=False)
        if r.returncode:
            return None
        blob = r.stdout
    else:
        try:
            blob = open(path, "rb").read()
        except OSError:
            return None
    if b"\x00" in blob:
        return None
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError:
        return None


def normalized(text):
    return re.sub(r"\s+", " ", text)


def ast_fragments(text):
    """(lineno, normalized text) for every string constant -- adjacent literals
    already joined by the parser -- and every comment."""
    frags = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return frags
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            frags.append((node.lineno, normalized(node.value)))
        elif isinstance(node, ast.JoinedStr):
            joined = "".join(v.value for v in node.values
                             if isinstance(v, ast.Constant) and isinstance(v.value, str))
            if joined:
                frags.append((node.lineno, normalized(joined)))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                frags.append((tok.start[0], normalized(tok.string)))
    except (tokenize.TokenError, IndentationError):
        pass
    return frags


def claims(haystack):
    """Every trigger occurrence with its claim window, deduplicated by window."""
    seen, out = set(), []
    for m in TRIGGER.finditer(haystack):
        lo = max(0, m.start() - WINDOW)
        window = haystack[lo:m.end() + WINDOW].strip()
        if window in seen:
            continue
        seen.add(window)
        out.append((m.group(0), window))
    return out


def classify(path):
    if path in ALLOWED_SCOPE:
        return "LIVE IN-SCOPE"
    if path in FENCED:
        return "FENCED (report, do not fix)"
    if path.startswith(HISTORICAL_DIRS) or path.split("/")[-1].startswith(HISTORICAL_FILES):
        return "HISTORICAL"
    return "LIVE OUT-OF-SCOPE (report to Commander)"


def main():
    rev = sys.argv[sys.argv.index("--rev") + 1] if "--rev" in sys.argv else None

    scanned_a = scanned_b = 0
    invalidated, near_miss = [], []

    for path in tracked_files(rev):
        text = read(path, rev)
        if text is None:
            continue
        scanned_a += 1
        found = [("A:normalized", 0, c) for c in claims(normalized(text))]
        if path.endswith(".py"):
            scanned_b += 1
            for lineno, frag in ast_fragments(text):
                found += [("B:ast", lineno, c) for c in claims(frag)]
        for layer, lineno, (trigger, window) in found:
            if not NAMES_FILE.search(window):
                continue
            rec = (path, lineno, layer, trigger, classify(path), window)
            (invalidated if NAMES_OPEN.search(window) else near_miss).append(rec)

    # A sweep over an empty set reports clean without looking. Assert the loop.
    assert scanned_a > 0 and scanned_b > 0, "sweep scanned nothing -- not evidence"

    by_class = {}
    for rec in invalidated:
        by_class.setdefault(rec[4], []).append(rec)
    live = by_class.get("LIVE IN-SCOPE", [])

    print(f"REV: {rev or 'working tree'}")
    print(f"FILES SCANNED (layer A, whitespace-normalized, all tracked text): {scanned_a}")
    print(f"FILES SCANNED (layer B, AST strings + comments, tracked .py):     {scanned_b}")
    print(f"INVALIDATED-CLAIM HITS (window names BOTH SPINE_FILE and spine_open): "
          f"{len(invalidated)}")
    for cls in sorted(by_class):
        print(f"    {cls}: {len(by_class[cls])}")
    print(f"NEAR MISSES (name SPINE_FILE but not spine_open -- still-true statements "
          f"about the module's own launch-time binding): {len(near_miss)}")
    print()
    print(f"LIVE IN-SCOPE HITS: {len(live)}")
    print(f"    (in-scope = this rework's allowed scope, {', '.join(ALLOWED_SCOPE)})")
    print()

    print("--- EVERY INVALIDATED-CLAIM HIT, CLASSIFIED ---")
    if not invalidated:
        print("(none)")
    for path, lineno, layer, trigger, cls, window in sorted(invalidated):
        print(f"[{cls}] {path}:{lineno} via {layer} trigger={trigger!r}")
        print(f"    ...{window}...")
        print()

    print(f"--- NEAR MISSES ({len(near_miss)}), not counted: SPINE_FILE without "
          f"spine_open ---")
    for path, lineno, layer, trigger, cls, _w in sorted(near_miss):
        print(f"[{cls}] {path}:{lineno} via {layer} trigger={trigger!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
