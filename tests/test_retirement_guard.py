"""Red-proofs for `scripts/verify_retirement.py` — the #403 retirement guard.

A guard nobody has watched fail is a guard nobody knows can fail. Issue #308 declared this
same retirement done and it came back within three commits, and #403's whole point is that
the previous cut left nothing runnable behind. So every leg here is falsified against a
decoy that plants EXACTLY ONE violation, and each red-proof asserts the leg AND the
offending path — not merely that "something failed". A leg that fires for the wrong reason
is a leg that will one day fail to fire for the right one.

**`tests/` is deliberately outside the shipped surface, and this file is why.** The guard
searches for literal strings like `LESSONS.md` and `apply_lessons_delta`; a test that
proves the search works has to spell them. A guard cannot be inside the set it guards
without either weakening itself or making its own test unwritable. That is a principled
scope choice, stated here rather than buried in a constant — it is not a dodge, and the
boundary is drawn at `tests/` precisely so that everything an agent is actually instructed
by stays inside the guard's reach.

**`test_canon_is_clean` carries `xfail(strict=True)` on purpose.** The tree is deliberately
still dirty at this gate — no retirement has happened yet — so the assertion is expected to
fail and the suite stays green. Strict xfail also means an XPASS FAILS: the moment the tree
really goes clean, this scaffolding breaks the build and has to be removed. #447 g6 removes
the marker. Scaffolding that cannot outlive the work is the only kind worth leaving in.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import verify_retirement as vr  # noqa: E402

#: The leg roster, pinned as an INDEPENDENT literal rather than imported from the module
#: under test. Importing `vr.LEGS` and comparing it to itself would pass on any roster at
#: all. Spelled out here, a leg added to the guard without a red-proof fails the census
#: below, and a leg quietly deleted from the guard fails it too.
LEG_ROSTER = frozenset(
    {
        "retired-path-still-tracked",
        "unapproved-store-mention",
        "replacement-absent",
        "retired-name-on-shipped-surface",
    }
)

#: Populated by `@red_proof` at import. Its whole job is to be compared against the roster.
_REGISTERED: set[str] = set()


def red_proof(leg: str):
    """Mark a test as THE red-proof for one leg, and register it.

    A decorator rather than a hand-maintained list, because a hand-maintained list is the
    thing that rots: registration happens at the definition site or it does not happen."""

    def decorate(func):
        _REGISTERED.add(leg)
        return func

    return decorate


# --------------------------------------------------------------------------- #
# decoy repositories
# --------------------------------------------------------------------------- #
def _git(args: list[str], cwd: Path) -> None:
    proc = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8"
    )
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"


def _write(path: Path, text: str) -> None:
    """Every write is explicit about both axes. On Windows the default encoding is not
    UTF-8 and the default newline translation produces CRLF, either of which would make a
    decoy's content depend on which machine built it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def healthy_repo(tmp_path: Path) -> Path:
    """A minimal repository on which ALL FOUR legs are green.

    The baseline has to satisfy `replacement-absent` explicitly, because that leg is a
    PRESENCE check: an empty repository fails it, so a decoy built on bare `git init` would
    fire two legs and could never assert `== [LEG_X]`. Everything here is the least wiring
    that makes the presence half true — the capture command on disk, named in both spine
    imperatives, carried by both install bundles.

    Nothing written here spells a retired name or names the episode store, so the two
    content legs are green with nothing excluded and the decoys below are the only source
    of a violation."""
    repo = tmp_path / "decoy-repo"
    repo.mkdir()
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "guard@example.invalid"], repo)
    _git(["config", "user.name", "guard"], repo)

    _write(repo / "README.md", "A tree on which the retirement already holds.\n")
    _write(
        repo / vr.REPLACEMENT_SCRIPT_PATH,
        "#!/usr/bin/env python\n\"\"\"Stand-in for the capture command.\"\"\"\n",
    )
    for spine_path in vr.SPINE_TEMPLATES:
        _write(
            repo / spine_path,
            json.dumps(
                {
                    "work_id": "decoy",
                    "tasks": {
                        "closeout": {
                            "id": "closeout",
                            "imperative": (
                                f"At closeout run `python scripts/{vr.REPLACEMENT_COMMAND}` "
                                "and attach its output."
                            ),
                        }
                    },
                },
                indent=2,
            )
            + "\n",
        )
    bundle_rows = "".join(
        f"    {skill!r}: ({vr.REPLACEMENT_COMMAND!r},),\n" for skill in vr.REPLACEMENT_BUNDLES
    )
    _write(
        repo / vr.INSTALLER_PATH,
        f"{vr.BUNDLES_SYMBOL}: dict[str, tuple[str, ...]] = {{\n{bundle_rows}}}\n",
    )

    _git(["add", "-A"], repo)
    return repo


def legs_and_paths(root: Path) -> tuple[list[str], list[str]]:
    violations = vr.scan(root)
    return [v.leg for v in violations], [v.path for v in violations]


def test_healthy_baseline_is_clean(tmp_path):
    """The fixture's own premise, asserted rather than assumed.

    Without this, every `== [LEG_X]` below could be passing because the baseline happens to
    produce that one violation on its own. A decoy is only a decoy if the tree it is planted
    in was clean first."""
    assert vr.scan(healthy_repo(tmp_path)) == []


# --------------------------------------------------------------------------- #
# one decoy red-proof per leg — asserting the LEG and the PATH
# --------------------------------------------------------------------------- #
@red_proof("retired-path-still-tracked")
def test_red_proof_retired_path_still_tracked(tmp_path):
    """Re-commit the retired playbook VERBATIM. Only the path-based leg can see it.

    This is the regression #308 actually suffered, and the reason this leg cannot be
    paraphrased into a content check: `.agent-work/LESSONS.md` advertises its own read path
    in its own preamble, and `.agent-work/` is a record-only root, so its content is never
    scanned. Every content leg stays green while the playbook is fully back. Tracking is
    the only signal left."""
    repo = healthy_repo(tmp_path)
    _write(
        repo / ".agent-work" / "LESSONS.md",
        "# Lessons\n\nRead this file at the start of every run.\n",
    )
    _git(["add", "-A"], repo)

    legs, paths = legs_and_paths(repo)
    assert legs == ["retired-path-still-tracked"]
    assert paths == [".agent-work/LESSONS.md"]


@red_proof("unapproved-store-mention")
def test_red_proof_unapproved_store_mention(tmp_path):
    """A new shipped doc starts naming the episode store, with no approval for it.

    The decoy carries no census at all, which is the correct reading for a fresh tree: with
    nothing approved, every mention is unapproved. The failure detail must carry the
    discriminator, because "is this mention allowed" is the wrong question and
    "does this make the store prescriptive" is the right one."""
    repo = healthy_repo(tmp_path)
    _write(
        repo / "docs" / "note.md",
        "Before planning, read the records under episodes/active/ and follow them.\n",
    )
    _git(["add", "-A"], repo)

    violations = vr.scan(repo)
    assert [v.leg for v in violations] == ["unapproved-store-mention"]
    assert [v.path for v in violations] == ["docs/note.md"]
    assert violations[0].line == 1
    assert "constraint:episodes-are-not-prescriptions" in violations[0].detail


@red_proof("replacement-absent")
def test_red_proof_replacement_absent(tmp_path):
    """Remove the capture command while every absence-half leg stays perfectly green.

    This is the case `tests/test_prose_deletions.py` warns about in as many words: "An
    absence-only suite would pass just as happily on a template that had deleted
    everything." Here the retirement is flawless and the replacement is gone, and only the
    presence half notices."""
    repo = healthy_repo(tmp_path)
    _git(["rm", "-q", "--cached", vr.REPLACEMENT_SCRIPT_PATH], repo)
    (repo / vr.REPLACEMENT_SCRIPT_PATH).unlink()

    legs, paths = legs_and_paths(repo)
    assert legs == ["replacement-absent"]
    assert paths == ["scripts/verify_episode_captured.py"]


@red_proof("retired-name-on-shipped-surface")
def test_red_proof_retired_name_on_shipped_surface(tmp_path):
    """A shipped doc starts telling an agent to read the retired playbook.

    The file itself is new and innocuously named; what is wrong is one line of prose. Note
    the mirror image of the first red-proof: here the retired NAME is present and the
    retired PATH is not tracked, so the path leg is blind and only this one sees it. Each
    leg catches what the other cannot."""
    repo = healthy_repo(tmp_path)
    _write(
        repo / "docs" / "note.md",
        "Consult .agent-work/LESSONS.md before you plan.\n",
    )
    _git(["add", "-A"], repo)

    violations = vr.scan(repo)
    assert [v.leg for v in violations] == ["retired-name-on-shipped-surface"]
    assert [v.path for v in violations] == ["docs/note.md"]
    assert violations[0].line == 1


@red_proof("retired-name-on-shipped-surface")
def test_red_proof_retired_name_on_a_path_string(tmp_path):
    """Re-add the retired SKILL DIRECTORY, with contents that name nothing at all.

    `skills/lessons-auditor/` is deleted wholesale at g4, and restoring it is a real
    regression path. The file below is innocent line by line — what is retired is *where it
    sits*. At first review this leg scanned only line content, so this case was missed
    entirely while the constant's own comment claimed to cover "a skill directory": the
    comment was true of the intent and false of the code."""
    repo = healthy_repo(tmp_path)
    _write(
        repo / "skills" / "lessons-auditor" / "SKILL.md",
        "# Lessons Auditor\n\nDistil scoped, grounded candidates from run artifacts.\n",
    )
    _git(["add", "-A"], repo)

    violations = vr.scan(repo)
    assert [v.leg for v in violations] == ["retired-name-on-shipped-surface"]
    assert [v.path for v in violations] == ["skills/lessons-auditor/SKILL.md"]
    # Line 0: the whole path is the violation, not any line inside it.
    assert violations[0].line == 0


def test_an_undecodable_shipped_file_is_refused_not_skipped(tmp_path):
    """Fail visibly. A file the guard cannot read is a file it cannot clear.

    Before rework this returned `None` and both content legs skipped it without a word, so a
    latin-1 file was indistinguishable from a clean one and the guard's coverage could
    shrink one file at a time with nothing reporting it. This repository's doctrine is the
    opposite: `apply_episode_delta._require_store_layout` refuses a missing store rather
    than answering "0 episodes", for precisely this reason."""
    repo = healthy_repo(tmp_path)
    legacy = repo / "docs" / "legacy.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_bytes(b"caf\xe9 latin-1, not utf-8\n")
    _git(["add", "-A"], repo)

    with pytest.raises(RuntimeError, match="unreadable shipped file docs/legacy.md"):
        vr.scan(repo)


def test_the_guard_is_not_inside_the_set_it_guards():
    """The scanner must exclude itself, or the tree can never go clean.

    This module's own constants ARE the forbidden strings. Committed and unexcluded, the
    guard scored 12 `retired-name-on-shipped-surface` and 6 `unapproved-store-mention` hits
    against itself; `test_canon_is_clean` could then never XPASS and the
    `xfail(strict=True)` marker below would outlive the work it exists to end. Asserted here
    rather than left to a constant, so re-including the file fails loudly."""
    assert not vr.is_shipped("scripts/verify_retirement.py")
    assert not vr.is_shipped("tests/test_retirement_guard.py")
    assert not vr.is_shipped("tests/data/store_mentions.approved.txt")
    # ...and the exclusion is narrow: everything else under scripts/ is still guarded.
    assert vr.is_shipped("scripts/install_constellation.py")


def test_every_exclusion_is_bounded_and_reasoned():
    """No globs, and no unexplained holes.

    A `notes-*.md` pattern removed seven tracked files AND every future one — unbounded, and
    growing without review. Enumeration is what makes adding the eighth a decision somebody
    takes rather than one that happens."""
    for mapping in (vr.RECORD_ONLY_ROOTS, vr.SCOPE_EXCLUSIONS, vr.RUN_NOTES):
        for key, reason in mapping.items():
            assert "*" not in key and "?" not in key, f"unbounded exclusion: {key}"
            assert reason.strip(), f"exclusion without a reason: {key}"
    assert len(vr.RUN_NOTES) == 7
    with pytest.raises(ValueError, match="empty reason"):
        vr._require_reasons({"docs/x.md": "   "}, "PROBE")


# --------------------------------------------------------------------------- #
# the census — the anti-rot invariant
# --------------------------------------------------------------------------- #
def test_every_leg_has_a_red_proof():
    """Both directions, against a roster this module owns.

    A leg added to the guard without a decoy fails here. A leg quietly deleted from the
    guard fails here. And because `LEG_ROSTER` is an independent literal, a guard that
    renamed every leg at once would fail here too — which importing `vr.LEGS` and comparing
    it to itself could never catch."""
    assert set(vr.LEGS) == LEG_ROSTER
    assert set(vr.LEGS) == _REGISTERED
    assert len(vr.LEGS) == 4, "exactly four legs: a fifth was cut by a cold panel"


def test_every_approved_entry_exists_verbatim():
    """A stale approval must not silently widen the guard.

    An entry whose line has since been edited or deleted still suppresses nothing real, but
    it survives in the census as a licence nobody reviewed. Matching is done over NORMALIZED
    lines — `.gitattributes` sets `* text=auto`, so a Windows checkout may legitimately hold
    CRLF where the blob holds LF, and a raw byte comparison would be wrong there rather than
    strict."""
    approved = vr.load_approved(REPO_ROOT)
    assert approved, "the census is empty; this check would be vacuous"

    by_path: dict[str, set[str]] = {}
    for entry in approved:
        if entry.path not in by_path:
            lines = vr._read_lines(REPO_ROOT, entry.path)
            assert lines is not None, f"approved path is unreadable: {entry.path}"
            by_path[entry.path] = {vr.normalize(line) for line in lines}
        assert entry.mention in by_path[entry.path], (
            f"stale approval: {entry.path} no longer contains {entry.mention!r}. Remove the "
            "entry — an approval for a line that is gone is an unreviewed licence."
        )
        assert entry.reason.strip(), f"approval without a reason: {entry.path}"


def test_an_approval_without_a_reason_is_refused():
    """The required reason is required. A census entry nobody justified is one nobody can
    review, so the parser refuses it rather than accepting a silent widening."""
    with pytest.raises(ValueError, match="has no reason"):
        vr.parse_approved("docs/note.md:names episodes/active/\n")


@pytest.mark.xfail(
    strict=True, reason="#447 g6 removes this marker — the tree is deliberately still dirty"
)
def test_canon_is_clean():
    """The acceptance surface for the whole of #447, red until the work is done.

    Strict, so it fails on XPASS: when the tree really goes clean this test starts failing
    and forces the marker off. The scaffolding cannot outlive the work."""
    assert vr.scan(REPO_ROOT) == []
