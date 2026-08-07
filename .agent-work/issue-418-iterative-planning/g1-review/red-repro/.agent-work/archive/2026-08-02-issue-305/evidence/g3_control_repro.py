#!/usr/bin/env python
"""One-command repro of #305 gate g3's negative control, printing the MISMATCHED
FIELD NAMES per lease topology.

    python .agent-work/issue-305/evidence/g3_control_repro.py

This exists **in addition to** the in-suite control (`tests/test_episode_negative_control.py`),
never instead of it — a discriminating test belongs in `tests/` (Admiral ruling, g2).
Its job is to make the red-proof legible in one line of output: mutate a derivation in
`scripts/episode_capture.py`, run this, and read which field the control names.

Exit code 0 = both topologies match their independent expectation. Exit 1 = at least
one field mismatched, and the field is NAMED on stdout. **The exit code is not the
evidence — the named field is.** An import error, a collection error and an empty test
selection all exit non-zero too, so a wrapper that mapped any non-zero to RED would
report red for all of them and prove nothing.

It reuses the suite's own harness rather than reimplementing it, so a repro that passes
while the suite fails is impossible by construction.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tests"))

from test_episode_negative_control import (  # noqa: E402
    _ControlRun,
    _git,
    _plan,
    _write_json,
    compare_fields,
)


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="g3-repro-"))
    repo = root / "mechanical-control-repo"
    repo.mkdir()
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "control@example.invalid"], repo)
    _git(["config", "user.name", "control"], repo)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8", newline="\n")
    _git(["add", "seed.txt"], repo)
    _git(["commit", "-qm", "seed"], repo)

    staged = ["changed_by_the_run.txt"]
    (repo / staged[0]).write_text("x\n", encoding="utf-8", newline="\n")
    _git(["add", staged[0]], repo)

    ok_flag = root / "ok.flag"
    agent_work = repo / ".agent-work"
    parent_path = agent_work / "ctl-parent" / "spine.json"
    child_path = agent_work / "ctl-child" / "execute.json"
    _write_json(parent_path, _plan("ctl-parent", ok_flag, child="ctl-child"))
    _write_json(child_path, _plan("ctl-child", ok_flag, child=None))

    parent = _ControlRun(parent_path, repo, "ctl-parent", role="commander")
    child = _ControlRun(child_path, repo, "ctl-child", role=None)
    parent.drive(ok_flag)
    ok_flag.unlink()
    child.drive(ok_flag)

    failed = False
    for label, run in (("(a) claimed parent spine", parent),
                       ("(b) unclaimed child gate-plan", child)):
        expected = run.expectations(staged)
        mismatches = compare_fields(expected, run.compose())
        if mismatches:
            failed = True
            print(f"RED  {label}: MISMATCHED FIELDS -> {mismatches}")
            for name in mismatches:
                want = expected[name].value
                actual = run.compose().get(name, "<absent>")
                print(f"       {name}: expected {want!r} (source: {expected[name].source})")
                print(f"       {name}: actual   {actual!r}")
        else:
            print(f"GREEN {label}: MISMATCHED FIELDS -> [] (all 10 fields match)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
