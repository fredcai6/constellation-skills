"""#597 — a bytecode cache built in a different tree must be named, not suffered.

THE FAILURE THIS CATCHES, measured during epic 568 (ADMIRAL_LOG, INCIDENT
2026-08-14). `tests/test_episode_negative_control.py::test_every_field_has_a_
named_independent_source` failed in one worktree and passed on `main` with the
test file BYTE-IDENTICAL on both sides. It was attributed by falsification, not
inspection: reverting the lane's `run_crew.py` did not fix it, removing the
lane's episode files did not fix it, moving `.agent-work` aside did not fix it.

The cause was in the bytecode. The `.pyc` embedded
`/home/tommy/projects/constellation-skills-wt/epic-568-codex-tier-routing` — the
PRE-relocation worktree path — so `inspect.getsource` resolved to a dead file and
raised `OSError: could not get source code`, four thousand lines from anything
the lane had touched. Clearing `__pycache__` passed.

Two things make it worth a check rather than a habit. It does not announce
itself: it surfaces as one specific unrelated assertion failing, which is exactly
the shape that gets blamed on the lane's own diff — three separate falsification
attempts were spent before the cache was suspected. And the response so far has
been procedural: a gate procedure whose FIRST step is "clear `__pycache__` before
every measurement", plus an Admiral ruling that every gate measured in a
relocated worktree before a given date was suspect and had to be re-measured.
That is a rule a human has to remember, protecting a signal an agent reads as a
defect.

This gets more likely, not less, now that `.worktrees/` is the owned layout
(#585) and worktrees are created and destroyed per lane.

WHY A TEST AND NOT A CONFTEST HOOK. Aborting collection would replace one
confusing failure with a different confusing failure. A named test fails
alongside whatever the stale cache is corrupting, so the diagnosis arrives next
to the symptom rather than instead of it.
"""

from __future__ import annotations

import importlib.util
import marshal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# 3.7+ layout: magic (4) + bit field (4) + mtime-or-hash (4) + source size (4).
_PYC_HEADER_LEN = 16

# Trees whose caches are not this checkout's business. `.worktrees/` holds other
# lanes' checkouts -- their `.pyc` files are correct FOR THEM, and their embedded
# paths are nested under this root anyway, so scanning them buys nothing and
# costs a walk of every concurrent lane.
_SKIP_DIRS = {".git", ".worktrees", "node_modules"}

FOREIGN_ROOT = "foreign-root"
DEAD_SOURCE = "dead-source"


def embedded_source_path(pyc: Path) -> str | None:
    """The source path recorded INSIDE `pyc`, or None if this file cannot speak
    for itself.

    None -- never a guess -- when the magic number is not this interpreter's (a
    staleness class Python already handles by recompiling), when the file is
    truncated, or when the payload will not unmarshal. Every one of those is a
    cache this check has no opinion about; only a readable code object whose
    embedded path disagrees with the tree is evidence of anything.
    """
    try:
        data = pyc.read_bytes()
    except OSError:
        return None
    if len(data) <= _PYC_HEADER_LEN:
        return None
    if data[:4] != importlib.util.MAGIC_NUMBER:
        return None
    try:
        code = marshal.loads(data[_PYC_HEADER_LEN:])
    except Exception:
        return None
    name = getattr(code, "co_filename", None)
    return name if isinstance(name, str) else None


def cache_offenders(root: Path, pycs) -> list[tuple[Path, str, str]]:
    """The pure decision: `(pyc, embedded_path, reason)` for every cache file
    that cannot have been built from THIS tree.

    Two reasons, and both were live in the incident above:

    `foreign-root` -- the embedded path is absolute and outside `root`. The cache
    was compiled in another checkout, so `inspect.getsource` and every traceback
    built from it point at a file this tree does not own.

    `dead-source` -- the embedded path is inside `root` but nothing is there. The
    source moved or was deleted while its cache survived, which produces the same
    `OSError: could not get source code` from a path that merely LOOKS local.

    A relative embedded path is not judged: it resolves against the caller's cwd,
    so it names no tree and cannot contradict this one.
    """
    offenders: list[tuple[Path, str, str]] = []
    root_resolved = root.resolve()
    for pyc in pycs:
        embedded = embedded_source_path(pyc)
        if embedded is None:
            continue
        source = Path(embedded)
        if not source.is_absolute():
            continue
        try:
            inside = source.resolve().is_relative_to(root_resolved)
        except (OSError, ValueError):
            continue
        if not inside:
            offenders.append((pyc, embedded, FOREIGN_ROOT))
        elif not source.exists():
            offenders.append((pyc, embedded, DEAD_SOURCE))
    return offenders


def _repo_pycs(root: Path):
    for pyc in root.rglob("*.pyc"):
        if any(part in _SKIP_DIRS for part in pyc.relative_to(root).parts):
            continue
        yield pyc


def _write_pyc(path: Path, source_path: str, *, magic: bytes | None = None) -> Path:
    """A real `.pyc` whose code object records `source_path`. Built by compiling
    with that filename rather than by patching bytes, so what the reader sees is
    what CPython would have written."""
    code = compile("x = 1\n", source_path, "exec")
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (magic or importlib.util.MAGIC_NUMBER) + b"\x00" * 12
    path.write_bytes(header + marshal.dumps(code))
    return path


class TestThisCheckoutsCachesAreItsOwn:
    """The live assertion. This is the one that fires during a real run."""

    def test_no_cache_in_this_tree_was_built_somewhere_else(self):
        offenders = cache_offenders(ROOT, _repo_pycs(ROOT))
        if offenders:
            lines = [
                f"  {pyc.relative_to(ROOT)}\n      built from: {embedded}  [{reason}]"
                for pyc, embedded, reason in offenders
            ]
            pytest.fail(
                "Stale bytecode: {n} cache file(s) in this checkout record a source "
                "path this checkout does not own. Any failure in this run may be an "
                "artifact of that, not of the code under test -- an inherited cache "
                "raises `OSError: could not get source code` from wherever it is "
                "read, which is usually nowhere near the change being measured.\n\n"
                "{lines}\n\n"
                "Clear it and measure again:\n"
                "  find . -name __pycache__ -type d -not -path './.git/*' "
                "-exec rm -rf {{}} +".format(n=len(offenders), lines="\n".join(lines))
            )


class TestTheCheckItself:
    """Without these, "report nothing" passes the live assertion above and the
    check is decoration."""

    def test_a_cache_from_another_checkout_is_named(self, tmp_path):
        """THE INCIDENT, reconstructed: a cache carrying the pre-relocation
        worktree path while sitting in the current tree."""
        here = tmp_path / "repo"
        (here / "pkg").mkdir(parents=True)
        pyc = _write_pyc(
            here / "pkg" / "__pycache__" / "mod.cpython.pyc",
            "/home/tommy/projects/constellation-skills-wt/epic-568-codex-tier-routing/pkg/mod.py",
        )
        offenders = cache_offenders(here, [pyc])
        assert [(o[0], o[2]) for o in offenders] == [(pyc, FOREIGN_ROOT)]

    def test_a_cache_whose_source_is_gone_is_named(self, tmp_path):
        here = tmp_path / "repo"
        here.mkdir()
        pyc = _write_pyc(
            here / "__pycache__" / "mod.cpython.pyc", str(here / "mod.py")
        )
        offenders = cache_offenders(here, [pyc])
        assert [(o[0], o[2]) for o in offenders] == [(pyc, DEAD_SOURCE)]

    def test_a_healthy_cache_is_not_named(self, tmp_path):
        """The control. A cache built here, whose source is still here, is
        exactly what a clean tree looks like."""
        here = tmp_path / "repo"
        here.mkdir()
        source = here / "mod.py"
        source.write_text("x = 1\n", encoding="utf-8")
        pyc = _write_pyc(here / "__pycache__" / "mod.cpython.pyc", str(source))
        assert cache_offenders(here, [pyc]) == []

    def test_a_cache_from_another_interpreter_is_skipped_not_flagged(self, tmp_path):
        """A different magic number means a different Python, which CPython
        already handles by recompiling. Judging it here would fail runs for a
        condition that fixes itself, so it must read as no opinion at all."""
        here = tmp_path / "repo"
        here.mkdir()
        pyc = _write_pyc(
            here / "__pycache__" / "mod.cpython.pyc",
            "/somewhere/else/mod.py",
            magic=b"\x00\x00\x00\x00",
        )
        assert embedded_source_path(pyc) is None
        assert cache_offenders(here, [pyc]) == []

    def test_a_truncated_cache_yields_no_opinion(self, tmp_path):
        pyc = tmp_path / "__pycache__" / "mod.cpython.pyc"
        pyc.parent.mkdir(parents=True)
        pyc.write_bytes(importlib.util.MAGIC_NUMBER + b"\x00" * 4)
        assert embedded_source_path(pyc) is None
        assert cache_offenders(tmp_path, [pyc]) == []

    def test_a_relative_embedded_path_is_not_judged(self, tmp_path):
        """A relative co_filename resolves against the caller's cwd, so it names
        no tree and cannot contradict this one. Flagging it would make the check
        fire on where pytest happened to be launched from."""
        here = tmp_path / "repo"
        here.mkdir()
        pyc = _write_pyc(here / "__pycache__" / "mod.cpython.pyc", "pkg/mod.py")
        assert cache_offenders(here, [pyc]) == []
