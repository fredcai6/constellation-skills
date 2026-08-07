#!/usr/bin/env python
"""Guard the #403 retirement: scan the tracked tree and NAME what is still wrong.

Issue #308 declared this retirement done and it came back — two commanders wrote to the
"retired" playbook three commits later. The previous cut is unverifiable: nothing in the
repository can be run to say whether the retirement holds. This module is that runnable
thing, and it was authored BEFORE any retirement work existed so it could be falsified
against the real disease rather than against a synthetic decoy.

**`scan()` returns a list of named legs, never a bool and never a bare exit code.** A
non-zero exit is produced identically by an import error, a collection error and an empty
test selection, so a boolean verdict cannot support a discriminating proof — "something
failed" is indistinguishable from "the thing I meant failed". The archetype is
`tests/test_episode_negative_control.py`'s `compare_fields`, which returns field NAMES for
exactly this reason. Naming the leg is what lets a per-leg red-proof assert
`[v.leg for v in scan(decoy)] == [LEG_X]`.

**Surfaces are enumerated from `git ls-files`, never `Path.rglob`.** Two failure modes, in
opposite directions: a file deleted from the working tree but still in the index would
vanish from an rglob walk while remaining perfectly committed, and every scratch file,
build artifact and untracked note in the tree would produce phantom violations. The index
is the shipped set; the working tree is not.

**Exactly four legs.** An earlier eight-leg design was cut by a cold panel that measured
four of them already green on the untouched tree, catching none of five plausible
regressions. Do not reintroduce bundle-asymmetry, episode-address-regex, or schema-kind
pinning: a leg that is green before the disease is cured is a leg that never had to fire.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


def _utf8_stdio() -> None:
    """The details below quote real repository lines, which are not all ASCII (the
    glossary tables carry en-dashes). Windows' default console encoding would raise
    UnicodeEncodeError mid-report and turn a violation list into a crash."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


class Violation(NamedTuple):
    """One named failure. `leg` is the invariant that broke, `path`/`line` locate it, and
    `detail` says what a reader must do about it.

    `path` is load-bearing rather than decorative: the per-leg red-proofs assert the leg
    AND the offending path, so a leg that fires for the wrong reason is caught rather than
    passing as "something failed". `line` is 0 for a leg whose subject is a whole file or
    a missing file — there is no honest line number for an absence."""

    leg: str
    path: str
    line: int
    detail: str


# --- the four legs -----------------------------------------------------------------

LEG_RETIRED_PATH = "retired-path-still-tracked"
LEG_STORE_MENTION = "unapproved-store-mention"
LEG_REPLACEMENT = "replacement-absent"
LEG_RETIRED_NAME = "retired-name-on-shipped-surface"

#: The roster. `tests/test_retirement_guard.py` pins an INDEPENDENT literal copy of this
#: and asserts set equality, so a leg added without a red-proof fails and a leg quietly
#: deleted fails. That census is the anti-rot invariant; this tuple alone is not.
LEGS = (LEG_RETIRED_PATH, LEG_STORE_MENTION, LEG_REPLACEMENT, LEG_RETIRED_NAME)


# --- what is being retired ---------------------------------------------------------

#: Paths that must not be TRACKED. "Tracked", not "exists", and that is deliberate: this
#: retirement untracks with `git rm --cached` rather than deleting, so the files stay in
#: the working tree as local records while leaving the shipped set. A guard phrased as
#: "does not exist" would fire on a correct retirement and be switched off.
#:
#: This is also the ONLY leg that catches a future agent re-committing
#: `.agent-work/LESSONS.md` verbatim, and it cannot be paraphrased around. That file
#: advertises its own read path IN ITS OWN PREAMBLE, so a verbatim re-commit adds zero new
#: mentions anywhere else in the tree — every content-based leg stays green while the
#: playbook is fully back. Path identity is the only signal that survives.
RETIRED_PATHS = (
    ".agent-work/LESSONS.md",
    ".agent-work/AGENT_FEEDBACK.md",
    "scripts/apply_lessons_delta.py",
    "scripts/verify_lessons_applied.py",
    "scripts/verify_agent_feedback.py",
)

#: Names that must not appear on the shipped surface at all — the content half of the same
#: retirement. Bare substrings rather than anchored patterns: a mention is a mention
#: whether it arrives as a path, a prose reference, a bundle entry or a skill directory.
RETIRED_NAMES = (
    "LESSONS.md",
    "AGENT_FEEDBACK.md",
    "apply_lessons_delta",
    "verify_lessons_applied",
    "verify_agent_feedback",
    "lessons-auditor",
)


# --- what counts as the shipped surface ---------------------------------------------

#: Roots that hold RECORDS rather than instructions. Every entry carries a REQUIRED
#: non-empty reason (see `_require_reasons`) so nobody can add a silent exclusion — an
#: unexplained exclusion is how a guard's coverage quietly shrinks to nothing.
RECORD_ONLY_ROOTS: dict[str, str] = {
    "docs/superpowers/": "historical plans, specs and drills: records of past work, not instructions",
    "tests/fixtures/": "recorded transcripts; editing them would falsify a recording",
    ".agent-work/": "run records and archives",
    "episodes/": "the store itself",
}

#: Scope choices rather than record-only roots — a different rationale, so a different
#: constant, held to the same required-reason rule. A key ending in `/` is a directory
#: prefix; every other key is an EXACT path. No globs: an exclusion whose extent is a
#: pattern grows silently as the tree does, and the reviewer's finding on this file was
#: exactly that class of drift.
#:
#: THE GUARD EXCLUDES ITSELF, and this is the same principle `tests/test_retirement_guard.py`
#: states in its docstring: a guard cannot be inside the set it guards. This module must
#: spell every retired name and every store pattern in order to search for them, so once it
#: is committed it matches its own constants — 12 `retired-name-on-shipped-surface` hits and
#: 6 `unapproved-store-mention` hits, measured against a staged index at rework. Left
#: unexcluded, the tree would still report 18 violations after the retirement completes,
#: `test_canon_is_clean` could never XPASS, and its `xfail(strict=True)` marker would
#: outlive the work it exists to end. `tests/fixtures/` stays enumerated above on purpose —
#: its reason is independently true, so it survives if the `tests/` choice is ever narrowed.
SCOPE_EXCLUSIONS: dict[str, str] = {
    "tests/": "the guard's own tests live here and must spell the forbidden strings to test for them",
    "scripts/verify_retirement.py": (
        "the guard itself: its constants ARE the forbidden strings, so a guard that scanned "
        "itself could never report a clean tree"
    ),
}

#: Root-level run notes, ENUMERATED rather than globbed.
#:
#: The g1 handoff names four record-only roots and does not name these, yet its stated
#: store-mention census is "~18 lines" — 37 with the run notes on the surface, exactly 18
#: with them off it, so the handoff's own acceptance number only reconciles with them
#: excluded. They are the same class as `docs/superpowers/`: records of what a past issue
#: found, not instructions. Ruled on by the Commander at rework and narrowed from a
#: `notes-*.md` glob to these SEVEN tracked files — the glob removed every future
#: `notes-*.md` too, an unbounded exclusion that would have grown without review.
_RUN_NOTES_REASON = "root-level run notes: a record of what a past issue found, not instructions"
RUN_NOTES: dict[str, str] = {
    name: _RUN_NOTES_REASON
    for name in (
        "notes-261.md",
        "notes-269.md",
        "notes-301.md",
        "notes-304.md",
        "notes-308.md",
        "notes-309.md",
        "notes-b420.md",
    )
}

# RETURN.md is the same class and is added by name for the same reason, but its reason is
# written out rather than shared because the case is worth stating once: a Commander's
# RETURN.md is its report TO its Admiral about a finished run. It is tracked (workstream A
# committed one at cbd9aee, so every worktree off that base inherits it), and a retirement
# report necessarily names what it retired — this one names the retired files ~17 times and
# the store ~9. Approving those line by line in the census would be approving a document
# that is rewritten wholesale by every run that touches this path, so the census would
# describe nothing durable. Classifying it is the honest call; approving it would have been
# the convenient one. If a RETURN.md ever starts telling a future agent what to do, the
# defect is that it stopped being a report, and no leg here would catch it either way.
RUN_NOTES["RETURN.md"] = (
    "a Commander's return report on a finished run: a record of what this issue did, "
    "addressed to the Admiral, never a surface an agent is instructed by"
)

# KNOWN BYPASSES, ACCEPTED AND NOT CHASED (reviewer-measured, Commander-ruled at rework).
# Recorded because an honest limit is worth more than a bigger guard, and because the next
# agent should not rediscover them as though they were oversights:
#   * case — a file named `lessons.md` is not matched by `LESSONS.md`; the match is
#     case-sensitive on purpose, since lowering it would make `lessons` collide with
#     ordinary prose everywhere;
#   * a NEW root-level note, e.g. `notes-999.md`, is on the shipped surface until someone
#     adds it to RUN_NOTES above — which is the deliberate cost of enumerating rather than
#     globbing, and the review step that buys;
#   * a prescription split across two lines escapes every leg here, because all matching is
#     line-scoped. Closing that means a paragraph-level parse this gate does not need.


def _require_reasons(mapping: dict[str, str], label: str) -> None:
    """An exclusion without a reason must RAISE, not quietly widen the guard.

    Checked at import so the failure arrives when the file is loaded rather than on the one
    later run whose result it would have changed."""
    empty = sorted(key for key, reason in mapping.items() if not reason.strip())
    if empty:
        raise ValueError(
            f"{label}: {', '.join(empty)} carries an empty reason. Every exclusion must "
            "say why the surface it removes is not shipped; an unexplained exclusion is "
            "an unreviewable hole in the guard."
        )


_require_reasons(RECORD_ONLY_ROOTS, "RECORD_ONLY_ROOTS")
_require_reasons(SCOPE_EXCLUSIONS, "SCOPE_EXCLUSIONS")
_require_reasons(RUN_NOTES, "RUN_NOTES")


def is_shipped(path: str) -> bool:
    """Is this tracked path part of the surface an agent is instructed by?

    One predicate, used by both content legs, so the two cannot drift apart about what
    "shipped" means. Every exclusion is either a directory prefix (trailing `/`) or an exact
    path — there is no pattern here whose extent could change on its own."""
    for prefix in RECORD_ONLY_ROOTS:
        if path.startswith(prefix):
            return False
    for key in SCOPE_EXCLUSIONS:
        if path == key or (key.endswith("/") and path.startswith(key)):
            return False
    return path not in RUN_NOTES


# --- enumeration --------------------------------------------------------------------


def tracked_paths(root: Path) -> list[str]:
    """Every path in the INDEX, as forward-slash strings relative to `root`.

    `git ls-files -z`, so a path containing a newline or a quote cannot split one entry
    into two. A repository with no index (or no git at all) raises rather than answering
    `[]` — "nothing is tracked" and "I could not ask" must not read the same, which is the
    same silent-omission trap `apply_episode_delta._require_store_layout` exists to close.
    """
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git ls-files failed in {root}: {proc.stderr.strip()} — the shipped surface "
            "is the index, so a guard that cannot read the index must refuse rather than "
            "report an empty, all-green tree."
        )
    return [entry for entry in proc.stdout.split("\0") if entry]


def _read_lines(root: Path, path: str) -> list[str] | None:
    """The working-tree text of one tracked shipped file.

    **An unreadable file must not read as a clean file.** A decode failure used to return
    None and both content legs skipped it in silence, which is a hidden fallback of exactly
    the class this repository refuses elsewhere: `apply_episode_delta._require_store_layout`
    raises on a missing store rather than answering "0 episodes", because "there is nothing
    wrong here" and "I could not look" must never be the same answer. So a shipped file that
    is not UTF-8 text now REFUSES the whole scan and says what to do about it. There are
    none in this tree today; the point is that adding one cannot quietly shrink the guard's
    coverage.

    Exactly ONE skip survives, and it is named rather than incidental: a path staged for
    deletion is still in the index but has no working-tree content. It counts for the path
    legs (which ask the index) and has no lines for the content legs to read. Reading blobs
    through `git cat-file --batch` would close even that, at the cost of a batch-read path
    this gate does not need.

    Read as text with universal newlines rather than as bytes: `.gitattributes` sets
    `* text=auto`, so a checkout may legitimately hold CRLF where the blob holds LF, and a
    byte-level comparison would be silently wrong on Windows."""
    try:
        with (root / path).open(encoding="utf-8", errors="strict") as handle:
            return handle.read().splitlines()
    except FileNotFoundError:
        return None  # the one named skip: staged for deletion, so there is no content
    except (UnicodeDecodeError, IsADirectoryError, OSError) as exc:
        raise RuntimeError(
            f"unreadable shipped file {path}: {exc}. The guard refuses rather than skipping "
            "it — a file it cannot read is a file it cannot clear, and silently passing over "
            "one would let a retired name ship inside it. Either make the file UTF-8 text, "
            "or, if it is legitimately binary, exclude it in SCOPE_EXCLUSIONS with a reason."
        ) from exc


def normalize(line: str) -> str:
    """Collapse a source line to the form the approval census stores.

    Whitespace-insensitive on purpose: re-indenting a table row or reflowing a paragraph
    must not read as a new, unapproved mention, and CRLF must not either."""
    return " ".join(line.split())


# --- leg: retired-path-still-tracked --------------------------------------------------


def _leg_retired_path(root: Path, tracked: set[str]) -> list[Violation]:
    """WHY THIS LEG ASKS THE INDEX AND NOT THE FILESYSTEM — the measurement, recorded at
    the place that enforces it (#447 g4).

    The retirement untracks with `git rm --cached` and deliberately leaves both files in
    the working tree. That is not a preference; it was measured. `scripts/agent_work_root.py`
    (`durable_root()`, lines 136-140) redirects the durable root to the WORKTREE whenever an
    active Admiral epic lease exists, and epic #418 held one while this retirement ran — so
    the retiring run's OWN `feedback`/`archive` closeout gate read the copy of
    `.agent-work/AGENT_FEEDBACK.md` sitting in its own worktree. Deleting the working-tree
    copy would have stranded that closeout, whose only two exits are recreating a retired
    file — literally #308's failure shape, the one this whole guard exists to catch — or a
    human override in a run with no reachable human.

    Untracking removes the path from the INDEX, and the index is what "shipped" means. The
    on-disk copies survive the run and die with the worktree, which is the whole design."""
    return [
        Violation(
            LEG_RETIRED_PATH,
            path,
            0,
            f"{path} is still tracked. Untrack it with `git rm --cached {path}` — the "
            "file may remain in the working tree as a local record, but a tracked path "
            "ships. This is the only leg that catches a verbatim re-commit of a retired "
            "playbook, because such a file advertises its own read path in its own "
            "preamble and adds no new mention anywhere else.",
        )
        for path in RETIRED_PATHS
        if path in tracked
    ]


# --- leg: retired-name-on-shipped-surface ---------------------------------------------
#
# A SECOND FROZEN APPROVAL CENSUS, in the same format as the store-mention one above and
# read through the same parser. It exists because this leg could not otherwise reach zero
# and was never going to: `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` is a June-2026 design
# RECORD whose ~33 sites must survive untouched (rewriting it to describe a system it never
# described would falsify history), the commander spine's `archive.c4` deny-globs keep both
# retired path strings as a RE-STAGING BLOCK. (`scripts/stage_feedback.py` also named them
# eight times and survived #447 by explicit ruling; it was deleted under #463 once it was
# shown orphaned — a stager whose consumer #447 had removed.) With no approval mechanism at all,
# `test_canon_is_clean`'s `xfail(strict=True)` could never XPASS and the scaffolding would
# outlive the work it exists to end — the exact defect g1's own review caught once already.
#
# NOT a pattern allowlist, and the difference is the whole value: the census names EXACT
# sites, so anything new still has to be looked at by a human and given a reason. A glob
# would make the leg decorative.
#
# THE BRIGHT LINE, stated where it is enforced: a reason amounting to "an agent is still
# told to use the retired thing" is NOT approvable — fix the surface instead. Approvable
# reasons look like: a frozen historical record; a deny-glob re-staging block; a survivor
# script naming what it stages; a tombstone naming the retired files in order to forbid
# them; a comment recording why the retirement was untrack-not-delete.

RETIRED_NAME_CENSUS_PATH = "tests/data/retired_names.approved.txt"

RETIRED_NAME_DETAIL = (
    "a shipped surface still names the retired {name!r}: {line}. If it TELLS an agent to "
    "use the retired thing, fix the surface. If it is a frozen record, a re-staging block, "
    "or a tombstone, approve it in " + RETIRED_NAME_CENSUS_PATH + " with a reason for that "
    "exact line."
)


def _leg_retired_name(root: Path, shipped: list[str]) -> list[Violation]:
    """Both halves of "appears on the shipped surface": the PATH string and the CONTENT.

    The path half was missing at first review, and its absence was invisible because the
    constant's own comment claimed coverage of "a skill directory" while nothing tested a
    path. Re-adding `skills/lessons-auditor/` — a whole directory deleted at g4 — was
    therefore missed entirely: a restored skill can be perfectly innocent line by line and
    still be the retired thing, because what identifies it is where it sits.

    **Only the CONTENT half is approvable.** The census is keyed on `(path, normalized
    line)` and there is no honest line to key a path violation on — but the real reason is
    stronger than the mechanical one: a restored file or skill directory whose *name* is the
    retired thing IS the retirement undone, and there is no record, block or tombstone that
    needs to sit at such a path. Leaving the path half unapprovable keeps the one leg that
    catches a verbatim re-commit (see `_leg_retired_path`) impossible to write a reason
    around. Named here rather than left implicit, because "the census did not cover it" and
    "the census must never cover it" read the same in code and mean opposite things."""
    approved = {(entry.path, entry.mention) for entry in load_approved(root, RETIRED_NAME_CENSUS_PATH)}
    out: list[Violation] = []
    for path in shipped:
        named = next((name for name in RETIRED_NAMES if name in path), None)
        if named is not None:
            out.append(
                Violation(
                    LEG_RETIRED_NAME,
                    path,
                    0,
                    f"the PATH itself names the retired {named!r}. A restored file or skill "
                    "directory is the retired thing whatever its contents say — line 0 "
                    "because the whole path is the violation, not any line in it. This half "
                    "is deliberately NOT approvable by census.",
                )
            )
        lines = _read_lines(root, path)
        if lines is None:
            continue
        for number, line in enumerate(lines, start=1):
            hit = next((name for name in RETIRED_NAMES if name in line), None)
            if hit is None:
                continue
            mention = normalize(line)
            if (path, mention) in approved:
                continue
            out.append(
                Violation(
                    LEG_RETIRED_NAME,
                    path,
                    number,
                    RETIRED_NAME_DETAIL.format(name=hit, line=mention[:160]),
                )
            )
    return out


# --- leg: unapproved-store-mention -----------------------------------------------------
#
# A FROZEN APPROVAL CENSUS, not a pattern allowlist. The census names the exact sites that
# exist today; anything new has to be looked at by a human and given a reason. The point is
# not that naming the store is forbidden — the write path has to be named somewhere — but
# that `constraint:episodes-are-not-prescriptions` is easy to break by accident: a doc that
# tells an agent to READ the store and condition its behaviour on what it finds rebuilds
# the playbook under a new name, which is exactly how #308's retirement came back.

STORE_MENTION_PATTERNS = ("episodes/", "episode store", "query_episodes", "apply_episode_delta")

#: The store's own module and its own spec. Excluded because a store is allowed to be about
#: itself; the census is about everything ELSE that learned to name it. Reasons required for
#: the same reason the roots above carry them.
STORE_OWN_FILES: dict[str, str] = {
    "scripts/apply_episode_delta.py": "the store's only write path — its own module",
    "scripts/query_episodes.py": "the store's read primitives — its own module",
    "docs/EPISODE_STORE.md": "the store's own spec",
}

_require_reasons(STORE_OWN_FILES, "STORE_OWN_FILES")

APPROVED_CENSUS_PATH = "tests/data/store_mentions.approved.txt"

#: Stated verbatim, because the discriminator is the whole value of this leg: the question a
#: reviewer must answer is not "is this mention allowed" but "does this mention make the
#: store PRESCRIPTIVE".
STORE_MENTION_DETAIL = (
    "a new shipped site now names the episode store: {locator}. If this is a WRITE path, "
    "approve it with a reason. If it tells an agent to READ the store and condition "
    "behaviour on it, it violates constraint:episodes-are-not-prescriptions."
)


class ApprovedEntry(NamedTuple):
    path: str
    mention: str  # the normalized line, as `normalize()` produces it
    reason: str


def store_mention_sites(root: Path, shipped: list[str]) -> list[tuple[str, int, str]]:
    """Every shipped `(path, line number, normalized line)` that names the store.

    One code path, used by the leg AND by whatever seeds the census, so an approval can
    never be written in a form the guard would not recognize."""
    sites: list[tuple[str, int, str]] = []
    for path in shipped:
        if path in STORE_OWN_FILES:
            continue
        lines = _read_lines(root, path)
        if lines is None:
            continue
        for number, line in enumerate(lines, start=1):
            if any(pattern in line for pattern in STORE_MENTION_PATTERNS):
                sites.append((path, number, normalize(line)))
    return sites


def parse_approved(text: str, census_path: str = APPROVED_CENSUS_PATH) -> list[ApprovedEntry]:
    """Parse a census. Each entry is `<path>:<normalized line>` on its own line, directly
    beneath a `#` comment line that is its REASON.

    `partition(":")` on the FIRST colon: a path never contains one, a quoted source line
    routinely does. An entry with no reason directly above it raises rather than being
    accepted — an approval nobody justified is an approval nobody can review.

    `census_path` names the file being read and appears in every refusal, so a malformed
    entry says WHICH census to go and fix. There is exactly ONE parser for both censuses on
    purpose: a second implementation is how two files that look alike start disagreeing
    about what an approval is."""
    entries: list[ApprovedEntry] = []
    reason = ""
    for raw in text.splitlines():
        if not raw.strip():
            reason = ""  # a blank line ends a reason's reach
            continue
        if raw.lstrip().startswith("#"):
            reason = raw.lstrip().lstrip("#").strip()
            continue
        path, separator, mention = raw.strip().partition(":")
        if not separator or not mention.strip():
            raise ValueError(
                f"{census_path}: malformed entry {raw!r} — an entry is "
                "`<path>:<normalized line>`."
            )
        if not reason:
            raise ValueError(
                f"{census_path}: entry {raw.strip()!r} has no reason. Put a "
                "one-line `# <why this mention is approved>` directly above it."
            )
        entries.append(ApprovedEntry(path, mention.strip(), reason))
        reason = ""  # one reason approves exactly one entry
    return entries


def load_approved(root: Path, census_path: str = APPROVED_CENSUS_PATH) -> list[ApprovedEntry]:
    """A census as it exists in `root`, or empty when the file is absent.

    Absent-means-empty is safe in the only direction that matters: with no approvals every
    mention is unapproved, so the guard fires MORE, never less. A decoy repository built in
    `tmp_path` carries no census, and that is the correct reading for it."""
    census = root / census_path
    if not census.is_file():
        return []
    with census.open(encoding="utf-8") as handle:
        return parse_approved(handle.read(), census_path)


def _leg_store_mention(root: Path, shipped: list[str]) -> list[Violation]:
    approved = {(entry.path, entry.mention) for entry in load_approved(root)}
    return [
        Violation(
            LEG_STORE_MENTION,
            path,
            number,
            STORE_MENTION_DETAIL.format(locator=f"{path}:{number}"),
        )
        for path, number, mention in store_mention_sites(root, shipped)
        if (path, mention) not in approved
    ]


# --- leg: replacement-absent -----------------------------------------------------------
#
# THE PRESENCE HALF, and it is not optional. `tests/test_prose_deletions.py` states the
# rule this leg exists to honour: "An absence-only suite would pass just as happily on a
# template that had deleted everything." Three legs above assert that things are GONE; on
# their own they would score a perfect green on a repository someone had emptied. This one
# asserts that the thing which replaces the retired playbook is actually WIRED — named in
# both spine imperatives, carried by both install bundles, and present on disk.
#
# AT g1 THIS LEG IS LEGITIMATELY RED and stays red until g3 ships the replacement. That is
# the correct reading, not a bug: the replacement genuinely is absent right now, and a leg
# that went green before the work was done would be measuring nothing.

REPLACEMENT_COMMAND = "verify_episode_captured.py"
REPLACEMENT_SCRIPT_PATH = f"scripts/{REPLACEMENT_COMMAND}"

#: The two spines that must name the capture command in an imperative. Both, not either:
#: a replacement wired into one tier only leaves the other tier with nothing, which is the
#: shape the retired playbook filled.
SPINE_TEMPLATES = (
    "skills/commander/templates/COMMANDER_SPINE.template.json",
    "skills/admiral/templates/ADMIRAL_SPINE.template.json",
)

#: The two install bundles that must carry it. A skill whose spine names a script that does
#: not travel with it fails mid-run at the gate that needed it.
REPLACEMENT_BUNDLES = ("commander", "admiral")

INSTALLER_PATH = "scripts/install_constellation.py"
BUNDLES_SYMBOL = "SKILL_SCRIPT_BUNDLES"


def _spine_names_replacement(root: Path, spine_path: str) -> bool:
    """Does any task imperative in this spine name the capture command?

    The IMPERATIVE specifically — the sentence an agent is told to act on — not the file's
    raw text. A script named only in a postcondition's check command is wired but unspoken,
    and this retirement is about what the agent is instructed to do."""
    path = root / spine_path
    if not path.is_file():
        return False
    try:
        with path.open(encoding="utf-8") as handle:
            spine = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return False
    tasks = spine.get("tasks", {})
    if not isinstance(tasks, dict):
        return False
    return any(
        REPLACEMENT_COMMAND in (task.get("imperative") or "")
        for task in tasks.values()
        if isinstance(task, dict)
    )


def installed_bundles(root: Path) -> dict[str, tuple[str, ...]]:
    """`SKILL_SCRIPT_BUNDLES` read out of the installer's SOURCE, via `ast`.

    Parsed rather than imported: importing the installer to ask it a question runs its
    module-level code, and a decoy repository built in `tmp_path` would have to carry a
    working installer rather than a four-line stand-in. Parsed rather than regexed because
    a regex over a dict whose entries are interleaved with paragraphs of comments is a
    guess about formatting, and the entries here are.

    Returns `{}` when the file, the symbol, or a literal value is missing — the leg reads
    that as "not in the bundle", which is the safe direction."""
    path = root / INSTALLER_PATH
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            tree = ast.parse(handle.read())
    except (SyntaxError, OSError):
        return {}
    for node in ast.walk(tree):
        targets = (
            [node.target] if isinstance(node, ast.AnnAssign) else getattr(node, "targets", [])
        )
        if not any(isinstance(t, ast.Name) and t.id == BUNDLES_SYMBOL for t in targets):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            return {}
        if isinstance(value, dict):
            return value
    return {}


def _leg_replacement(root: Path) -> list[Violation]:
    """One violation per UNMET requirement, each carrying the path that should have
    satisfied it — so a red-proof can assert which half of the wiring is missing rather
    than only that the leg fired."""
    out: list[Violation] = []

    for spine_path in SPINE_TEMPLATES:
        if not _spine_names_replacement(root, spine_path):
            out.append(
                Violation(
                    LEG_REPLACEMENT,
                    spine_path,
                    0,
                    f"no task imperative in this spine names {REPLACEMENT_COMMAND}. The "
                    "retired playbook is not replaced until BOTH spines tell their agent "
                    "to run the capture command.",
                )
            )

    bundles = installed_bundles(root)
    for skill in REPLACEMENT_BUNDLES:
        if REPLACEMENT_COMMAND not in tuple(bundles.get(skill, ())):
            out.append(
                Violation(
                    LEG_REPLACEMENT,
                    INSTALLER_PATH,
                    0,
                    f"{BUNDLES_SYMBOL}[{skill!r}] does not carry {REPLACEMENT_COMMAND}. A "
                    "spine that names a script the skill does not install fails at the "
                    "gate that needed it.",
                )
            )

    if not (root / REPLACEMENT_SCRIPT_PATH).is_file():
        out.append(
            Violation(
                LEG_REPLACEMENT,
                REPLACEMENT_SCRIPT_PATH,
                0,
                "the capture command does not exist on disk. Absence-only legs would score "
                "a perfect green on a repository that had deleted everything; this is the "
                "presence half that stops them.",
            )
        )
    return out


# --- the scan -------------------------------------------------------------------------


def scan(root: Path) -> list[Violation]:
    """Every violation in `root`, sorted deterministically by (leg, path, line).

    Deterministic order is what lets a red-proof compare the whole list rather than a set,
    and what keeps the captured transcript stable across runs and platforms."""
    tracked = tracked_paths(root)
    tracked_set = set(tracked)
    shipped = [path for path in tracked if is_shipped(path)]

    violations: list[Violation] = []
    violations += _leg_retired_path(root, tracked_set)
    violations += _leg_store_mention(root, shipped)
    violations += _leg_replacement(root)
    violations += _leg_retired_name(root, shipped)
    return sorted(violations, key=lambda v: (v.leg, v.path, v.line))


# --- CLI --------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the #403 retirement holds.")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to scan (default: this script's repository)",
    )
    args = parser.parse_args(argv)
    root = args.root if args.root is not None else Path(__file__).resolve().parent.parent

    violations = scan(root)
    # TAB-separated with the leg FIRST, so `cut -f1 | sort -u` answers "which invariants
    # are broken" without parsing prose. Details never carry a tab or a newline.
    for violation in violations:
        print(f"{violation.leg}\t{violation.path}\t{violation.line}\t{violation.detail}")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
