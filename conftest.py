"""Repo-wide pytest configuration.

Currently one job: make a failing subtest **greppable**.

A test whose body raises inside `self.subTest(...)` is reported by pytest as
`PASSED`, and its failure is printed on a separate line that begins `SUBFAILED`.
The exit code is still non-zero, so CI already fails — the hole is not the build,
it is the reading. `SUBFAILED` does not match a search for `FAILED ` (the next
character is `(`, not a space), so every habit and tool that looks for `FAILED`
reports a clean run:

    $ python -m pytest -q probe.py
    SUBFAILED(i=1) probe.py::Probe::test_body_raises - RuntimeError: boom 1
    2 failed, 1 passed

    $ python -m pytest -q probe.py | grep '^FAILED'
    (nothing)

Measured during epic #567: an Admiral's own merge gate extracted failure sets
with `grep -oE "FAILED [^ ]+"` and was therefore blind to this whole class, while
reporting confidently on four lanes. The repo carries 169 `subTest` call sites
across 25 files, so the exposure is real rather than theoretical.

The fix moves the work off the reader and into the mechanism: restate each failed
subtest as a line that starts with `FAILED `, so one search word is enough. The
`[subtest ...]` marker keeps it distinguishable from a whole-test failure, and
the count is stated so a silent truncation cannot look like a clean run.
"""

from __future__ import annotations

# The failed-subtest reports seen this session, as (nodeid, description).
_subtest_failures: list[tuple[str, str]] = []


def _is_subtest_report(report: object) -> bool:
    """Whether ``report`` is pytest's own subtest report.

    Imported lazily and by duck type rather than at module scope: `_pytest.subtests`
    is a builtin plugin in pytest 9 but a separate `pytest-subtests` distribution
    earlier, and a hard import would turn a missing plugin into a collection error
    for the whole suite. A report that answers to `_sub_test_description` is the
    thing we mean, whichever provides it.
    """
    return callable(getattr(report, "_sub_test_description", None))


def pytest_runtest_logreport(report) -> None:
    if getattr(report, "when", None) != "call":
        return
    if not getattr(report, "failed", False):
        return
    if not _is_subtest_report(report):
        return
    try:
        description = report._sub_test_description()
    except Exception:  # pragma: no cover - a description is cosmetic, never fatal
        description = ""
    _subtest_failures.append((report.nodeid, description.strip()))


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    if not _subtest_failures:
        return
    terminalreporter.write_sep("=", "failed subtests, restated as FAILED")
    terminalreporter.write_line(
        f"{len(_subtest_failures)} failed subtest(s). Each is a real failure that "
        "pytest reports on a SUBFAILED line while marking its test PASSED; the "
        "lines below exist so a search for 'FAILED' finds them."
    )
    for nodeid, description in _subtest_failures:
        marker = f"[subtest {description}]" if description else "[subtest]"
        terminalreporter.write_line(f"FAILED {nodeid} {marker}")
