"""One shared table of cases, pinning the TWO worktree-derivation copies equal.

#609 lane F gate g1. A spine's owning worktree is a property of WHERE THE SPINE
IS: walk up to the NEAREST `.agent-work` ancestor and take its parent, at
arbitrary depth; no `.agent-work` ancestor at all means unowned (`None`). The
derivation answers LOCATION only -- never "is this mine".

There are deliberately two implementations of that one rule:

- `scripts/checklist_engine.py:worktree_from_spine_path` -- the definition the
  engine consumes (first engine consumer lands in g2).
- `scripts/hooks/spine_rail.py:_worktree_from_spine` -- the hook's own copy.

They are duplicated because the single-definition placement is closed in BOTH
directions: `spine_rail.py` is stdlib-only by design (a hook that fails takes the
turn with it) and has no `SCRIPT_RUNTIME_COMPANIONS` entry, so it may gain no
import; and moving the definition the other way would need an installer entry
this lane may not write. `CASES` below is what stops that duplication from
drifting: every case runs through EVERY implementation in `IMPLEMENTATIONS`, so a
divergence between the two copies is a test failure here, not an observation a
reviewer has to make by eye.

**Why this table cannot silently stop checking one copy.** `IMPLEMENTATIONS` is
built with `getattr` at module import and `_require` raises on a missing symbol,
so deleting either implementation fails COLLECTION of this whole file rather than
quietly shrinking the parametrization to the surviving one. Applying the deletion
test by hand: delete either function and every case in this file goes red.

Normalization is LEXICAL ONLY -- `os.path.normcase` + `os.path.normpath`, never
`realpath`. Symlink resolution stays OUTSIDE the derivation on every side; the
hook's `_is_valid_claim_target` depends on that (it checks lexically, then
re-checks the RESOLVED path, and that second check has to stay able to fail).
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    """Import a script by file path -- neither module is on a package."""
    path = _REPO_ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


_ENGINE = _load("checklist_engine_for_derivation", "scripts/checklist_engine.py")
_HOOK = _load("spine_rail_for_derivation", "scripts/hooks/spine_rail.py")


def _require(module, attr: str):
    """Resolve an implementation, failing LOUDLY at import if it is gone.

    A plain `getattr(module, attr, None)` would let a deleted implementation drop
    out of `IMPLEMENTATIONS` and leave this file green against the survivor --
    exactly the check-that-cannot-fail this table exists to prevent.
    """
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover -- the deletion test's path
        raise AssertionError(
            f"{module.__name__}.{attr} is missing: the shared derivation table "
            f"must drive BOTH copies, so a missing one fails the whole file "
            f"rather than silently checking only the other."
        ) from exc


# The two copies of the one rule. Keyed by the name that appears in test ids.
IMPLEMENTATIONS = {
    "engine": _require(_ENGINE, "worktree_from_spine_path"),
    "hook": _require(_HOOK, "_worktree_from_spine"),
}


# An absolute root to build cases under. `abspath` supplies the drive on Windows
# (a bare "\\proj" is not absolute to `Path.is_absolute`) and is the identity on
# POSIX; the paths themselves are never touched on disk -- the rule is lexical,
# so nothing here needs to exist.
_ROOT = os.path.abspath(os.sep + "proj")

# Whether THIS platform folds case in paths, asked of `normcase` itself rather
# than of `sys.platform`. On Linux `normcase` is the identity function, so the
# `.AGENT-WORK` case below asserts `None` here and asserts the fold on Windows --
# the expectation is derived from the predicate the implementations actually
# apply, never from a hand-maintained platform list.
_FOLDS_CASE = os.path.normcase(".AGENT-WORK") == ".agent-work"


def _path(*parts: str) -> str:
    return os.path.join(_ROOT, *parts)


def _expected(*parts: str) -> str:
    """A derived worktree, in the normalized form the rule returns."""
    return os.path.normcase(os.path.normpath(os.path.join(_ROOT, *parts)))


# --- the one shared table ----------------------------------------------------
#
# (case id, spine path, expected worktree or None). Every entry runs through
# every implementation in IMPLEMENTATIONS.

CASES = [
    # --- the six the handoff requires ---
    (
        "spine-at-the-project-root",
        _path(".agent-work", "w1", "spine.json"),
        _expected(),
    ),
    (
        "spine-in-a-worktree",
        _path(".worktrees", "cleanup-f", ".agent-work", "w1", "spine.json"),
        _expected(".worktrees", "cleanup-f"),
    ),
    (
        "crew-area-nested-under-a-commanders",
        _path(".agent-work", "w1", "crew-handoffs", "g1-implement",
              "IMPLEMENTER_PLAN.json"),
        _expected(),
    ),
    (
        "deep-archived-case",
        _path(".agent-work", "archive", "2026-07-10-epic-101", "harvest",
              "issue-102", "full", "issue-102", "spine.json"),
        _expected(),
    ),
    (
        # NEAREST, never outermost: the inner `.agent-work` belongs to a nested
        # sandbox project rooted at `workspace/`. Taking the outermost would
        # derive the real repo as the root of a spine that is the sandbox's.
        "nested-sandbox-double-agent-work-derives-the-inner-root",
        _path(".agent-work", "archive", "2026-07-10-epic-101", "workspace",
              ".agent-work", "w1", "spine.json"),
        _expected(".agent-work", "archive", "2026-07-10-epic-101", "workspace"),
    ),
    (
        "no-agent-work-ancestor-at-all-is-unowned",
        _path("scripts", "checklist_engine.py"),
        None,
    ),

    # --- arbitrary depth includes depth zero, which flips ---
    (
        # `<wt>/.agent-work/checklist.json`: no work-id segment. The old
        # fixed-shape rule returned None; arbitrary depth necessarily accepts it.
        # The narrow claim layout is re-imposed at `_is_valid_claim_target`, not
        # here -- see tests/test_spine_rail.py.
        "depth-zero-spine-directly-in-agent-work",
        _path(".agent-work", "checklist.json"),
        _expected(),
    ),

    # --- preconditions that moved OUT of the derivation to its callers ---
    (
        # `.json` suffix is a checklist-shape question, not a location question.
        "non-json-leaf-still-has-a-location",
        _path(".agent-work", "w1", "notes.md"),
        _expected(),
    ),
    (
        "dotfile-leaf-still-has-a-location",
        _path(".agent-work", "w1", ".json"),
        _expected(),
    ),

    # --- preconditions that stayed IN the derivation ---
    (
        # A relative path has no derivable location. Deriving one would mean
        # reading the ambient cwd, and the whole point is that there is no
        # ambient reading to forge.
        "relative-path-is-unowned",
        os.path.join(".agent-work", "w1", "spine.json"),
        None,
    ),
    (
        "empty-string-is-unowned",
        "",
        None,
    ),
    (
        "non-string-is-unowned",
        None,
        None,
    ),

    # --- lexical normalization, and what it must NOT match ---
    (
        "redundant-separators-and-dot-segments-normalize",
        _path(".", ".agent-work", "", "w1", "..", "w1", "spine.json"),
        _expected(),
    ),
    (
        # `.agent-work` is a whole path SEGMENT, never a substring.
        "segment-merely-containing-agent-work-does-not-match",
        _path("not-.agent-work-really", "w1", "spine.json"),
        None,
    ),
    (
        # The rule walks ANCESTORS. A leaf that is itself named `.agent-work`
        # is not its own ancestor.
        "leaf-named-agent-work-is-not-its-own-ancestor",
        _path("somewhere", ".agent-work"),
        None,
    ),
    (
        # Case folding, asked of `normcase` rather than assumed: unowned where
        # paths are case-sensitive, derived where they fold.
        "case-folded-agent-work-segment",
        _path(".AGENT-WORK", "w1", "spine.json"),
        _expected() if _FOLDS_CASE else None,
    ),
]

_CASE_IDS = [case[0] for case in CASES]


def test_the_table_is_not_empty_and_has_unique_ids():
    """A parametrized guard over an empty or duplicate-keyed table reports clean
    without examining anything. Assert what is looped over."""
    assert len(CASES) >= 16
    assert len(set(_CASE_IDS)) == len(_CASE_IDS)
    assert set(IMPLEMENTATIONS) == {"engine", "hook"}


@pytest.mark.parametrize("impl_name", sorted(IMPLEMENTATIONS))
@pytest.mark.parametrize("case_id,spine_path,expected",
                         CASES, ids=_CASE_IDS)
def test_derivation(impl_name, case_id, spine_path, expected):
    """Every case, through every implementation, from the one table."""
    derive = IMPLEMENTATIONS[impl_name]
    assert derive(spine_path) == expected


@pytest.mark.parametrize("case_id,spine_path,expected", CASES, ids=_CASE_IDS)
def test_the_two_copies_agree(case_id, spine_path, expected):
    """The drift detector proper: the copies must return the SAME value, not
    merely each satisfy the table. Stated separately from `test_derivation` so a
    divergence reads as drift rather than as one copy being wrong."""
    answers = {name: derive(spine_path) for name, derive in IMPLEMENTATIONS.items()}
    assert len(set(answers.values())) == 1, f"copies disagree: {answers}"


@pytest.mark.parametrize("impl_name", sorted(IMPLEMENTATIONS))
def test_derivation_is_lexical_not_realpath(impl_name, tmp_path):
    """Symlink resolution stays OUTSIDE the derivation.

    `_is_valid_claim_target` checks lexically and then re-checks the RESOLVED
    path as a symlink-escape guard; if the derivation resolved symlinks itself,
    both checks would return the same value and the second could never fail.
    A `realpath` here would also make `origin_worktree_refusal` impure while its
    purity test -- which reads only that predicate's own `__code__.co_names`, and
    is not transitive -- stayed green.
    """
    derive = IMPLEMENTATIONS[impl_name]
    real = tmp_path / "real-worktree"
    (real / ".agent-work" / "w1").mkdir(parents=True)
    spine = real / ".agent-work" / "w1" / "spine.json"
    spine.write_text("{}", encoding="utf-8")

    link = tmp_path / "linked-worktree"
    try:
        link.symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):  # pragma: no cover -- Windows w/o privilege
        pytest.skip("symlinks unavailable on this host")

    through_link = str(link / ".agent-work" / "w1" / "spine.json")
    # Lexical: the answer follows the path you were GIVEN, not the path on disk.
    assert derive(through_link) == os.path.normcase(os.path.normpath(str(link)))
    assert derive(through_link) != os.path.normcase(os.path.normpath(str(real)))


@pytest.mark.parametrize("impl_name", sorted(IMPLEMENTATIONS))
def test_derivation_never_raises(impl_name):
    """Both copies sit on fail-open paths -- the hook's whole contract is that it
    never crashes a turn. Hostile input returns None, it does not raise."""
    derive = IMPLEMENTATIONS[impl_name]
    for hostile in (None, 0, [], {}, object(), b"/proj/.agent-work/w1/spine.json"):
        assert derive(hostile) is None
