"""gate g5 evidence: measure the three-way production/test caller split over
a BUILT map tree, crossed with the ONE dimension the original version of this
script omitted -- whether the entity ITSELF is defined in a test module.

Reads each entity page's two rendered inbound lines the same way a human
reader would -- through `checks.parse_refs` / `checks.refs_lines`, never
through the renderer's in-memory state -- and buckets the entity by what
those two lines say:

  unused      production sites == 0 AND tests sites == 0
  test-only   production sites == 0 AND tests sites  > 0
  production  production sites  > 0 (tests may or may not also be > 0)

The g5 review found that the "unused" bucket alone conflates two very
different facts: a page whose OWN entity is test-defined reads `none found`
on both lines as its NORMAL, expected state (see `render.TEST_NOTE`), not as
a dead-code finding. A naive headline built from the three buckets above
("unused: 2428, 64.7%") reproduces exactly that conflation -- the defect this
gate exists to remove. Crossing each bucket with the entity's own definer
(prod-defined vs test-defined), read off the page's own title line the same
way `checks.is_test_module` classifies a caller module, is what makes the
number a reader actually wants -- genuinely unused PRODUCTION code -- visible
on its own.

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

    unused_prod = table[("unused", "prod-defined")]
    unused_test = table[("unused", "test-defined")]
    unused_total = unused_prod + unused_test
    naive_pct = round(100 * unused_test / unused_total, 1) if unused_total else 0.0
    headline = (
        f"genuinely unused production code: {unused_prod} "
        f"(not the naive {unused_total} -- {unused_test}/{unused_total}, "
        f"{naive_pct}%, of that bucket is test-defined, where zero callers "
        f"is the normal expected state, not a finding)")

    report = {
        "unused_prod_defined": unused_prod,
        "unused_test_defined": unused_test,
        "test_only_prod_defined": table[("test-only", "prod-defined")],
        "test_only_test_defined": table[("test-only", "test-defined")],
        "production_prod_defined": table[("production", "prod-defined")],
        "production_test_defined": table[("production", "test-defined")],
        "headline": headline,
        "unreadable_refs_lines": unreadable,
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
