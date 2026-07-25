#!/usr/bin/env python
"""Verify no undocumented pytest skip slipped into a run's --junitxml report.

The CI gate (`.github/workflows/ci.yml`) runs the full `tests/` suite and writes
a `--junitxml` report. A silently-skipped test is a regression hiding in plain
sight — e.g. `GitChangePolicyCollectorIntegration` quietly skipping its real
end-to-end coverage on a runner where `git` is unexpectedly absent from PATH.
This script REFUSES (non-zero exit) unless every `<skipped>` testcase in the
report matches a documented allow-tuple.

The allow-tuple is **(classname, name, message)** — all three fields, not
message text alone. A message-only allowlist is spoofable: a future unrelated
test could reuse an allowed message string (e.g. "not available on this
platform") and sneak an unexpected skip past the guard. Keying on the full
nodeid (classname + name) *and* the message closes that gap.

The allow-tuples below are exactly the two pre-existing, non-git skips
measured on this suite (see `.agent-work/issue-229/evidence/g1/`):
  - `VerifySpecConfirmedTests.test_live_design_spec_passes_default_phase`
    (issue-58 DESIGN_SPEC.md not present in this checkout — untracked artifact)
  - `NormalizeTests.test_symlink_or_junction_resolved`
    (symlink creation not permitted on this platform)
Anything else — including the git-unavailable skip in
`GitChangePolicyCollectorIntegration` — is NOT on this list and fails the guard.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

# (classname, name, message) triples. A skipped testcase must match ALL THREE
# fields exactly to be allowed through the guard.
ALLOWED_SKIPS: frozenset[tuple[str, str, str]] = frozenset(
    {
        (
            "tests.test_verify_spec_confirmed.VerifySpecConfirmedTests",
            "test_live_design_spec_passes_default_phase",
            "issue-58 DESIGN_SPEC.md not present in this checkout (untracked artifact)",
        ),
        (
            "tests.test_verify_worktree_isolation.NormalizeTests",
            "test_symlink_or_junction_resolved",
            "symlink creation not permitted on this platform",
        ),
    }
)


class SkipGuardError(Exception):
    """Raised when the junit report cannot be parsed."""


def iter_skips(report_root: ET.Element) -> Iterator[tuple[str, str, str]]:
    """Yield (classname, name, message) for every <testcase> that carries a
    <skipped> child, across the whole report regardless of <testsuite> nesting."""
    for testcase in report_root.iter("testcase"):
        skipped = testcase.find("skipped")
        if skipped is None:
            continue
        classname = testcase.get("classname", "")
        name = testcase.get("name", "")
        message = skipped.get("message", "") or ""
        yield classname, name, message


def find_disallowed_skips(report_root: ET.Element) -> list[tuple[str, str, str]]:
    """Return every skip whose (classname, name, message) triple is not on the
    allow-tuple list. Empty means the report is clean."""
    return [triple for triple in iter_skips(report_root) if triple not in ALLOWED_SKIPS]


def _load_report(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise SkipGuardError(f"could not parse junit report {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", type=Path, help="path to a pytest --junitxml report")
    args = parser.parse_args(argv)

    try:
        root = _load_report(args.report)
    except SkipGuardError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    disallowed = find_disallowed_skips(root)
    if disallowed:
        print(
            f"REFUSED: {len(disallowed)} skip(s) not on the documented allow-tuple list:",
            file=sys.stderr,
        )
        for classname, name, message in disallowed:
            print(f"  - classname={classname!r} name={name!r} message={message!r}", file=sys.stderr)
        return 1

    total = sum(1 for _ in iter_skips(root))
    print(f"skip guard ok: {total} skip(s) in report, all match documented allow-tuples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
