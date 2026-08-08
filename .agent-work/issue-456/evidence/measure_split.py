"""gate g5 evidence: measure the three-way production/test caller split over
a BUILT map tree.

Reads each entity page's two rendered inbound lines the same way a human
reader would -- through `checks.parse_refs` / `checks.refs_lines`, never
through the renderer's in-memory state -- and buckets the entity by what
those two lines say:

  unused      production sites == 0 AND tests sites == 0
  test-only   production sites == 0 AND tests sites  > 0
  production  production sites  > 0 (tests may or may not also be > 0)

Usage:
    python .agent-work/issue-456/evidence/measure_split.py --out <map dir>

Stdlib only. Prints one JSON object to stdout; no timings (this report is
committed as run evidence and a timing field would make it churn on every
re-run for no informational reason)."""
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
    unused = test_only = production = 0
    unreadable = []
    for page in sorted(out_dir.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        lines = checks.refs_lines(text)
        if len(lines) != 2:
            continue  # not an entity page (e.g. a module index or the top index)
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
            production += 1
        elif test > 0:
            test_only += 1
        else:
            unused += 1
    total = unused + test_only + production
    share = (lambda n: round(100 * n / total, 1) if total else 0.0)
    return {
        "total_entity_pages": total,
        "unused": {"count": unused, "share_pct": share(unused)},
        "test_only": {"count": test_only, "share_pct": share(test_only)},
        "production": {"count": production, "share_pct": share(production)},
        "unreadable_refs_lines": unreadable,
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / "map"))
    args = p.parse_args(argv)
    report = measure(args.out)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
