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
        # Added 2026-08-23 (epic 569 closeout): the first five skips CI has ever
        # actually SEEN. The Skip guard step ran on every prior build but the
        # suite step failed ahead of it, so this guard has been unreached rather
        # than passing -- a check that never ran reads exactly like a check that
        # passed. All five are honest conditional skips that predate wave 3.
        (
            "tests.test_mcp_adoption.TestTier3CLIOnlyVerbsStayCLI",
            "test_the_cli_only_rule_itself_is_present",
            "CLI_ONLY_VERBS is empty -- no CLI-only-verb doctrine sentence is "
            "required while there is nothing CLI-only to document (issue #559: "
            "the door reaches all 18 engine verbs). Reactivates the moment "
            "CLI_ONLY_VERBS is non-empty.",
        ),
        (
            "tests.test_mcp_adoption.TestTier3CLIOnlyVerbsStayCLI",
            "test_verb_still_documented[NOTSET]",
            "got empty parameter set for (verb)",
        ),
        (
            "tests.test_spine_lifecycle.TestWorktreePathForRealWorktree",
            "test_reproduces_this_runs_real_worktree",
            "this checkout is not directly inside the default worktree root; "
            "only applies to a worktree following the <wt_root>/<work-slug> convention",
        ),
        (
            "tests.test_verify_spec_confirmed.ConfirmPhaseRegressionOnALiveSpec",
            "test_live_revised_spec_also_passes_review",
            "no epic REVISED_SPEC.md under .agent-work/*/spec-revision/",
        ),
        (
            "tests.test_verify_spec_confirmed.ConfirmPhaseRegressionOnALiveSpec",
            "test_live_revised_spec_still_passes_confirm",
            "no epic REVISED_SPEC.md under .agent-work/*/spec-revision/",
        ),
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
        # Added 2026-07-25: this test shadows PATH to a python-but-no-py
        # directory to prove the probe falls through past `py`. That premise is
        # host-dependent -- Windows CreateProcess also searches the Windows and
        # System32 directories, and an all-users Python launcher lives in
        # C:\Windows, so on the GitHub Actions windows runner `py` still
        # resolves and the fall-through cannot be induced at all. The test now
        # verifies its own premise and skips when it fails, rather than
        # asserting the opposite of the state it set up (which is what made CI
        # red on every run from the moment the gate landed).
        (
            "tests.test_install_constellation.InterpreterProbeTests",
            "test_probe_falls_through_to_next_candidate_when_py_is_unresolvable",
            "py resolves outside PATH on this host, so py-unresolvable cannot "
            "be genuinely induced",
        ),
        # Added 2026-08-09: `_same_path` folds case and separators only where
        # `os.path.normcase` does, which is Windows. The behaviour is therefore
        # asserted twice, once per platform, and exactly ONE of the pair runs on
        # any given host -- so its opposite necessarily skips and needs a tuple.
        #
        # This pair is deliberately NOT the usual "we cannot test it here" shape,
        # and the distinction matters for a guard whose whole job is refusing
        # silent skips. No assertion is given up: on Windows the folding case runs
        # and the POSIX case skips; on Linux the reverse. There is no host on which
        # the behaviour goes unasserted, which is what makes two allow-tuples
        # honest here rather than two holes. Delete either test and the other's
        # tuple becomes a hole -- they are only safe as a pair.
        #
        # The Windows tuple's message was measured from a real --junitxml report on
        # a Linux host, not transcribed from the source. The POSIX tuple's message
        # cannot be measured here -- it only skips on Windows, which is where CI
        # runs -- so it is the `reason=` string joined exactly as Python
        # concatenates its two source literals.
        (
            "tests.test_spine_rail",
            "test_same_path_windows_normcase_sep_equivalence",
            "ntpath's normcase (lowercase + backslash/forward-slash folding) "
            "only applies on Windows",
        ),
        (
            "tests.test_spine_rail",
            "test_same_path_posix_case_and_backslash_are_significant",
            "posixpath's normcase is identity and backslash is not a separator "
            "-- covered by the Windows-only case above instead",
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
