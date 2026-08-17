"""Windows simulation for #609 lane F g1 blocker B1.

The reviewer's B1: `tests/test_spine_rail.py`'s six assertions compare the
derivation's return against `str(worktree)` -- a PLATFORM-INHERITED expectation.
The derivation returns a `normcase`-folded path, so on Windows (where `normcase`
lowercases and rewrites separators) the two differ for every `tmp_path`.

This harness runs BOTH copies of the derivation with `os.path` swapped to
`ntpath`, against a realistic Windows `tmp_path`, and compares each derived
answer against the two candidate expectations:

  inherited   : str(worktree)                              -- what the test did
  constructed : normcase(normpath(str(worktree)))          -- what the fix does

It exits 0 only when the simulation demonstrates the whole of B1:
  * the INHERITED expectation fails, on all six of the test's comparisons,
    through both copies (that is the blocker reproducing), and
  * the CONSTRUCTED expectation passes, on all six, through both copies
    (that is the fix being correct by construction), and
  * `tests/test_worktree_derivation.py`'s `_expected()` construction -- which
    the reviewer confirmed correct -- agrees with the constructed form.

It reads the two implementations, never the test file's text, so the same
command is meaningful before and after the fix. Native (POSIX) mode is run too:
there `normcase` is the identity, so both expectations agree and the harness
proves the fix is a no-op on this host rather than a platform swap.

Usage: py .agent-work/<work-id>/evidence/g1-windows-sim.py
"""

import importlib.util
import ntpath
import os
import posixpath
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


class _FakeOS:
    """`os` with a substituted `os.path`. Everything else delegates.

    Both derivations reach the filesystem-naming layer only through `os.path`
    (`isabs`, `normcase`, `normpath`, `dirname`, `split`), so swapping `.path`
    is the whole of the platform simulation.
    """

    def __init__(self, path_module):
        self.path = path_module

    def __getattr__(self, name):
        return getattr(os, name)


def _load(name, relative, path_module):
    """Import a script by file path, with its `os` rebound to a fake.

    Rebinding AFTER `exec_module` is deliberate and sufficient: module-level
    functions resolve `os` from module globals at CALL time, so every later
    `os.path.normcase(...)` inside the derivation reaches `path_module`.
    """
    spec = importlib.util.spec_from_file_location(name, _REPO_ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    module.os = _FakeOS(path_module)
    return module


def _implementations(tag, path_module):
    engine = _load(f"engine_{tag}", "scripts/checklist_engine.py", path_module)
    hook = _load(f"hook_{tag}", "scripts/hooks/spine_rail.py", path_module)
    return {
        "engine.worktree_from_spine_path": engine.worktree_from_spine_path,
        "hook._worktree_from_spine": hook._worktree_from_spine,
    }


def _simulate(tag, p, tmp_root):
    """Reproduce the six comparisons the target test makes, under `p`."""
    impls = _implementations(tag, p)

    worktree = p.join(tmp_root, "worktree")
    sandbox = p.join(worktree, ".agent-work", "archive", "ep", "workspace")

    # The six comparisons, in the order the test makes them:
    # 1 the one-level shape, 2-5 the four newly-accepted paths, 6 the sandbox.
    comparisons = [
        (p.join(worktree, ".agent-work", "run1", "checklist.json"), worktree),
        (p.join(worktree, ".agent-work", "run1", "crew-handoffs", "g1",
                "PLAN.json"), worktree),
        (p.join(worktree, ".agent-work", "archive", "ep", "harvest", "i",
                "spine.json"), worktree),
        (p.join(worktree, ".agent-work", "checklist.json"), worktree),
        (p.join(worktree, ".agent-work", "run1", "checklist.txt"), worktree),
        (p.join(sandbox, ".agent-work", "run1", "spine.json"), sandbox),
    ]

    rows = []
    for impl_name, derive in sorted(impls.items()):
        for index, (spine, expected_dir) in enumerate(comparisons, start=1):
            got = derive(spine)
            inherited = expected_dir                              # str(worktree)
            constructed = p.normcase(p.normpath(expected_dir))    # the fix
            # The sibling table's own helper, spelled exactly as it is there.
            sibling = p.normcase(p.normpath(p.join(expected_dir)))
            rows.append({
                "impl": impl_name,
                "n": index,
                "got": got,
                "inherited": inherited,
                "constructed": constructed,
                "inherited_ok": got == inherited,
                "constructed_ok": got == constructed,
                "sibling_agrees": constructed == sibling,
            })
    return rows


def _report(title, rows, expect_inherited_ok):
    print(f"--- {title} " + "-" * max(0, 60 - len(title)))
    sample = rows[0]
    print(f"    derived     : {sample['got']}")
    print(f"    inherited   : {sample['inherited']}")
    print(f"    constructed : {sample['constructed']}")
    inherited_ok = sum(r["inherited_ok"] for r in rows)
    constructed_ok = sum(r["constructed_ok"] for r in rows)
    sibling_ok = sum(r["sibling_agrees"] for r in rows)
    total = len(rows)
    print(f"    inherited expectation  : {inherited_ok}/{total} comparisons pass")
    print(f"    constructed expectation: {constructed_ok}/{total} comparisons pass")
    print(f"    sibling _expected()    : {sibling_ok}/{total} agree")

    failures = []
    want_inherited = total if expect_inherited_ok else 0
    if inherited_ok != want_inherited:
        failures.append(
            f"{title}: inherited expectation passed {inherited_ok}/{total}, "
            f"expected {want_inherited}")
    if constructed_ok != total:
        failures.append(
            f"{title}: constructed expectation passed {constructed_ok}/{total}")
    if sibling_ok != total:
        failures.append(f"{title}: sibling _expected() disagrees")
    return failures


def main():
    failures = []

    # A realistic Windows tmp_path, in pytest's own shape.
    windows_tmp = ntpath.join(
        "C:\\", "Users", "Tommy", "AppData", "Local", "Temp",
        "pytest-of-Tommy", "pytest-1", "test_Worktree0")
    failures += _report(
        "SIMULATED WINDOWS (ntpath)",
        _simulate("nt", ntpath, windows_tmp),
        # The blocker: on Windows the inherited expectation must match NOTHING.
        expect_inherited_ok=False,
    )

    posix_tmp = posixpath.join(
        "/tmp", "pytest-of-tommy", "pytest-1",
        "test_worktree_from_spine_walk0")
    failures += _report(
        "NATIVE POSIX (posixpath)",
        _simulate("posix", posixpath, posix_tmp),
        # Here `normcase` is the identity, so both forms agree -- which is why
        # the bug is invisible on this host and why the fix changes nothing here.
        expect_inherited_ok=True,
    )

    print()
    if failures:
        for line in failures:
            print(f"FAIL: {line}")
        return 1
    print("OK: B1 reproduces under ntpath (inherited 0/12), and the constructed "
          "expectation is exact under BOTH platforms (12/12 each).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
