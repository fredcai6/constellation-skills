#!/usr/bin/env python
"""Enumerate every `command`-kind check in a set of checklist JSON files and
classify its dependence on the process working directory.

Classification:
  ANCHORED   - the command begins with `cd <path> &&` (self-anchoring; cwd-independent)
  ABSOLUTE   - every path-looking token is absolute
  RELATIVE   - references at least one relative path token -> cwd-DEPENDENT
  NOPATH     - no path token at all (e.g. `true`, `test -n "$X"`) -> cwd-independent
"""
import json
import re
import sys
from pathlib import Path

# tokens that look like a path relative to something
REL_HINT = re.compile(
    r"(?<![\w/.-])("
    r"scripts/[\w./-]+"
    r"|tests?/[\w./-]+"
    r"|docs/[\w./-]+"
    r"|skills/[\w./-]+"
    r"|\.agent-work/[\w./-]+"
    r"|episodes/[\w./-]+"
    r"|\./[\w./-]+"
    r"|[\w-]+\.(?:py|json|md|toml|txt|cfg|ini)"
    r")"
)
ABS_HINT = re.compile(r"(?<![\w])(/[\w./-]{4,}|[A-Za-z]:[\\/][\w./\\-]+)")
PLACEHOLDER = re.compile(r"<[a-z][a-z0-9-]*>")


def walk_checks(obj, path, out):
    if isinstance(obj, dict):
        chk = obj.get("check")
        if isinstance(chk, dict) and chk.get("kind") == "command":
            out.append((path, obj.get("id"), chk.get("command", "")))
        for k, v in obj.items():
            walk_checks(v, path, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_checks(v, path, out)


# Scripts whose project root defaults to cwd ("." / Path.cwd()), so invoking them
# WITHOUT an explicit absolute --root makes the check cwd-dependent even when the
# check text contains no relative path token at all. Measured by reading each
# script's argparse default (see notes-1.md).
CWD_DEFAULTING = {
    "init_work_area.py": "--root",
    "verify_state_note.py": "--root",
    "verify_cycles.py": "--root",
    "verify_spec_confirmed.py": "--root",
    "verify_iterative_role_artifacts.py": None,  # hardcoded Path.cwd(), no --root
    "map_orient.py": "--root",
}


def classify(cmd: str) -> str:
    stripped = cmd.strip()
    if re.match(r"^cd\s+\S+\s*&&", stripped):
        return "ANCHORED"
    # R2: invokes a cwd-defaulting script without pinning its root absolutely
    for script, rootflag in CWD_DEFAULTING.items():
        if script in stripped:
            if rootflag is None:
                return "R2-CWD-SCRIPT"
            m = re.search(re.escape(rootflag) + r"\s+(\S+)", stripped)
            if m is None:
                return "R2-CWD-SCRIPT"
            val = m.group(1)
            if not (val.startswith("/") or PLACEHOLDER.fullmatch(val) or re.match(r"^[A-Za-z]:", val)):
                return "R2-CWD-SCRIPT"
    # a bare relative --store-root / --root value is the same defect
    m = re.search(r"--(?:store-)?root\s+([^/\s<][^\s]*)", stripped)
    if m:
        return "R1-RELATIVE"
    # Collapse placeholders to a bare path-segment token so
    # `.agent-work/<work-id>/X.md` still reads as one relative path, while
    # `<skill-dir>/scripts/X.py` reads as rooted at the placeholder.
    probe = PLACEHOLDER.sub("PH", stripped)
    rels = REL_HINT.findall(probe)
    if rels:
        return "R1-RELATIVE"
    if ABS_HINT.search(probe):
        return "ABSOLUTE"
    return "NOPATH"


def main(argv):
    files = [Path(p) for p in argv[1:]]
    rows = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"SKIP (unparseable) {f}: {e}", file=sys.stderr)
            continue
        found = []
        walk_checks(data, f, found)
        for _, cid, cmd in found:
            rows.append((str(f), cid, classify(cmd), cmd))

    counts = {}
    for _, _, kind, _ in rows:
        counts[kind] = counts.get(kind, 0) + 1

    for r in rows:
        print(f"{r[2]:9s} | {r[0]} | {r[1]} | {r[3]}")
    print()
    print(f"TOTAL command checks: {len(rows)}")
    for k in sorted(counts):
        print(f"  {k:9s} {counts[k]}")


if __name__ == "__main__":
    main(sys.argv)
