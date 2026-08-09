"""g5 REVIEWER independent re-measurement of Finding B.

measure_split.py buckets purely on the page's two rendered inbound lines
(production sites / test sites), never asking whether the entity ITSELF is
defined in a test module. This script adds that one dimension, reading the
page the same way a human would -- through checks.parse_refs/refs_lines and
the page's own title line -- and cross-tabulates:

    bucket (unused / test-only / production) x definer (prod-defined / test-defined)

Independent of measure_split.py: written from scratch, not imported from it,
though it necessarily shares checks.py's own parsing helpers (the same
dependency measure_split.py itself takes) since re-deriving a page parser
would not be a stronger check, only a differently-buggy one.

Usage:
    python .agent-work/issue-456/evidence/g5_reviewer_split_by_definer.py --out <map dir>
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.code_map import checks  # noqa: E402


def measure(out_dir):
    out_dir = pathlib.Path(out_dir)
    table = {
        ("unused", "prod-defined"): 0, ("unused", "test-defined"): 0,
        ("test-only", "prod-defined"): 0, ("test-only", "test-defined"): 0,
        ("production", "prod-defined"): 0, ("production", "test-defined"): 0,
    }
    unreadable = []
    for page in sorted(out_dir.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        lines = checks.refs_lines(text)
        if len(lines) != 2:
            continue  # not an entity page
        by_prefix = {}
        for line in lines:
            stated = checks.parse_refs(line)
            if stated is None:
                unreadable.append(str(page.relative_to(out_dir)))
                by_prefix = None
                break
            by_prefix[checks.refs_prefix_of(line)] = stated
        if by_prefix is None:
            continue
        prod = by_prefix[checks.REFS_PROD_PREFIX].sites
        test = by_prefix[checks.REFS_TEST_PREFIX].sites
        if prod > 0:
            bucket = "production"
        elif test > 0:
            bucket = "test-only"
        else:
            bucket = "unused"

        # own-module classification: title line is "# <module>:<entity>"
        title_line = text.splitlines()[0]
        title = title_line[2:].strip() if title_line.startswith("# ") else title_line
        own_mod = title.split(":", 1)[0] if ":" in title else title
        definer = "test-defined" if checks.is_test_module(own_mod) else "prod-defined"

        table[(bucket, definer)] += 1

    return table, unreadable


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / "map"))
    args = p.parse_args(argv)
    table, unreadable = measure(args.out)
    report = {
        "unused": {"prod-defined": table[("unused", "prod-defined")],
                    "test-defined": table[("unused", "test-defined")]},
        "test-only": {"prod-defined": table[("test-only", "prod-defined")],
                       "test-defined": table[("test-only", "test-defined")]},
        "production": {"prod-defined": table[("production", "prod-defined")],
                         "test-defined": table[("production", "test-defined")]},
        "unreadable_refs_lines": unreadable,
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
