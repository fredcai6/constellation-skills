# scripts.verify_skip_guard
scripts/verify_skip_guard.py, 125 lines, 2 holes

Verify no undocumented pytest skip slipped into a run's --junitxml report.

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

imports stdlib: __future__.annotations, argparse, pathlib.Path, sys, typing.Iterator, xml.etree.ElementTree
imported by: none found

```python
ALLOWED_SKIPS: frozenset[tuple[str, str, str]] = frozenset({('tests.test_verify_spec_confirmed.VerifySpecConfirmedTests', 'test_live_des...
```

- [SkipGuardError](SkipGuardError.md) class: Raised when the junit report cannot be parsed.
- [iter_skips](iter_skips.md) function: Yield (classname, name, message) for every <testcase> that carries a
- [find_disallowed_skips](find_disallowed_skips.md) function: Return every skip whose (classname, name, message) triple is not on the
- [_load_report](_load_report.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
