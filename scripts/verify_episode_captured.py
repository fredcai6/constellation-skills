#!/usr/bin/env python
"""Capture gate: refuse to advance until THIS run left an episode in the store.

The write-side replacement for the retiring `.agent-work/LESSONS.md` /
`.agent-work/AGENT_FEEDBACK.md` machinery (issue #447). It answers exactly one
question — *did this run capture an episode?* — and nothing else.

CLI: `verify_episode_captured.py <work-id> [--store-root PATH] [--phase feedback|archive]`

Exit codes:
  0  at least one episode in <store-root>/active records `- run: <work-id>`
  1  BLOCKED — the store is readable and holds no such episode (or, under
     `--phase archive`, holds one that git does not track)
  2  REFUSED — the store could not be read at all: a missing root, a missing
     `active/`, or a malformed record. Refused, not answered.

THE VALVE — the load-bearing design property, not an implementation detail
--------------------------------------------------------------------------
Episodes are a RECORD of what happened, not a playbook. The human's constraint,
2026-08-06: *"we shouldn't be reading the episodes like lessons, it's a store for
things that happened to replace both feedback and lessons."*

So this gate parses ONLY two things: the `<!-- episode-state: -->` header line and
the `- run:` mechanical line. It does not parse, store, or emit any assertion
`statement`, and it does not import `query_episodes`. **Ids and counts out;
statements never.** That is the mechanical difference between a capture gate and a
read path — a gate that can surface episode content is one refactor away from being
the playbook again. `scan_episode()` stops reading at the `## Agent-supplied`
heading, so statement text is never even read into memory, and
`tests/test_verify_episode_captured.py::ValveTests` proves the absence with a
sentinel plus its own red proof.

It asserts capture only: no ripeness, no apply-or-defer, no dormancy, no counters.
Those are playbook concepts and they retire with the playbook. Do not port them here.

Windows: every read passes `encoding="utf-8", newline=""`, matching the store's own
byte discipline (`apply_episode_delta.read_text_exact`).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# The store's layout, named literally rather than imported: importing the writer would
# pull the whole record parser — including the assertion `statement` field — into this
# module's namespace, which is the read path the valve above exists to prevent. Two
# directory names are a cheaper coupling than that.
ACTIVE_DIR = "active"

HEADER_RE = re.compile(r"<!--\s*episode-state:\s*(?P<fields>[^>]*?)\s*-->")
RUN_LINE_RE = re.compile(r"^-\s*run:\s*(?P<run>\S.*?)\s*$")
AGENT_SUPPLIED_HEADING = "## Agent-supplied"

# The writer's run grammar, named literally here for the same reason ACTIVE_DIR is:
# importing apply_episode_delta would pull the record parser — statements included —
# into this module, which is the read path the valve exists to prevent. Keep the two
# in step: `apply_episode_delta.RUN_RE`.
#
# A run is a work-id, and a work-id may NEST (`epic-418-followon/commander-424`, the
# epic/commander convention). Each `/`-separated segment is flat kebab, so `..`, an
# empty segment and an absolute path are excluded.
#
# This gate checks the grammar so that a work-id the WRITER could never record is
# REFUSED rather than BLOCKED. The two answers are not interchangeable: BLOCKED says
# "capture one with apply_episode_delta.py", and following that advice against an
# ungrammatical id fails forever with no hint why. That contradiction — the writer
# forbidding exactly what the gate demanded — is what made this closeout step
# impossible to complete, so the gate now states the shared grammar out loud instead
# of discovering the disagreement as a missing record.
_RUN_SEGMENT = r"[a-z0-9][a-z0-9-]*"
RUN_RE = re.compile(rf"{_RUN_SEGMENT}(?:/{_RUN_SEGMENT})*")

EXIT_CAPTURED = 0
EXIT_BLOCKED = 1
EXIT_REFUSED = 2


class StoreRefusal(Exception):
    """The store could not be read, so the question was not answered."""


def _header_fields(text: str) -> dict[str, str]:
    fields = {}
    for token in text.split():
        key, sep, value = token.partition("=")
        if sep:
            fields[key] = value
    return fields


def scan_episode(path: Path) -> tuple[str | None, str | None]:
    """Return `(episode_id, run)` for one episode file — and NOTHING else.

    This is the whole read surface of the gate, and it is deliberately tiny. The scan
    breaks at the `## Agent-supplied` heading, which is where assertion statements
    begin: statement text is therefore never read, never held in a local, and never
    reachable by any caller. Anything that widens this function widens the valve.
    """
    episode_id: str | None = None
    run: str | None = None
    with path.open(encoding="utf-8", newline="") as handle:
        for raw in handle:
            line = raw.strip()
            if line.startswith(AGENT_SUPPLIED_HEADING):
                break  # statements start here — stop before reading any of them
            if episode_id is None:
                match = HEADER_RE.search(line)
                if match:
                    episode_id = _header_fields(match.group("fields")).get("id")
            if run is None:
                match = RUN_LINE_RE.match(line)
                if match:
                    run = match.group("run")
            if episode_id is not None and run is not None:
                break
    return episode_id, run


def matched_episodes(root: Path, work_id: str) -> tuple[list[tuple[str, Path]], int]:
    """Every active episode whose `- run:` line equals `work_id`, plus the number of
    files scanned to find them.

    The scanned count is returned rather than discarded because a loop that reports
    clean without ever examining an interesting item is the failure this gate is here
    to catch — the count goes into both the pass and the block message.
    """
    if not RUN_RE.fullmatch(work_id):
        raise StoreRefusal(
            f"ungrammatical run id {work_id!r}: the store's write path "
            f"(apply_episode_delta.py) can never record it, because a run must match "
            f"{RUN_RE.pattern} — flat kebab segments, optionally nested with '/' as a "
            "work-id is (e.g. 'epic-418-followon/commander-424'). Refused rather than "
            "BLOCKED: 'capture one with apply_episode_delta.py' is advice that cannot "
            "be followed for this id, and a block that can never be cleared reads as a "
            "missing record instead of a mismatched id."
        )
    if not root.is_dir():
        raise StoreRefusal(
            f"missing store: {root} is not a directory. Enumerating a store that is not "
            "there returns an empty candidate set, which reads exactly like an empty "
            "store — so this is refused rather than answered. Check --store-root."
        )
    active = root / ACTIVE_DIR
    if not active.is_dir():
        raise StoreRefusal(
            f"missing store layout: {active} is absent. An absent directory is not an "
            "empty one; git does not track empty directories, so a layout that was "
            "never committed arrives here. Refused rather than answered."
        )

    # `retired/` is deliberately NOT searched. Ordinary retrieval globs active/ only
    # (episodes/README.md), and this gate is ordinary retrieval. Named corner case, not
    # chased: a run that captured an episode and then retired it inside the same run
    # would read here as uncaptured. Nothing retires an episode mid-run today, and
    # chasing it would mean teaching the capture gate to reach into the archive — the
    # exact widening the valve above exists to prevent.
    matches: list[tuple[str, Path]] = []
    scanned = 0
    for path in sorted(active.glob("*.md")):
        if not path.is_file():
            continue
        scanned += 1
        episode_id, run = scan_episode(path)
        if episode_id is None or run is None:
            missing = "episode-state header" if episode_id is None else "`- run:` line"
            raise StoreRefusal(
                f"malformed episode {path}: no {missing}. A record this gate cannot "
                "read is refused, not skipped — skipping is how a real record becomes "
                "invisible to the gate that is supposed to require it."
            )
        if run == work_id:
            matches.append((episode_id, path))
    return matches, scanned


def _git_tracked(path: Path) -> tuple[bool, str]:
    """Is `path` known to git? `git ls-files --error-unmatch` is the question.

    Anything non-zero — untracked, or not a repository at all — answers "not durable",
    which is the answer the archive phase acts on either way; the git message is
    carried through so the two are distinguishable in the log. git echoes paths and
    its own diagnostics, never file content, so this cannot leak a statement.

    The path is RESOLVED first, and that is not cosmetic. git interprets a relative
    pathspec against its own cwd, and this call sets cwd to the episode's directory so
    the question reaches the repository the store actually lives in. Passing the
    caller's relative path (`--store-root episodes`) through unresolved made git look
    for `episodes/active/episodes/active/<id>.md` and answer "untracked" for 25 of 25
    genuinely committed episodes — a false BLOCK, caught only by running the gate
    against the real store instead of against absolute temp paths alone.
    """
    path = path.resolve()
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        cwd=str(path.parent),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return True, ""
    detail = (proc.stderr or proc.stdout).strip().splitlines()
    return False, detail[0] if detail else f"git exited {proc.returncode}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture gate for the episode store.")
    parser.add_argument("work_id", help="the run id an episode must record (`- run:`)")
    parser.add_argument(
        "--store-root",
        type=Path,
        default=None,
        help="episode store root (default: the repo's tracked episodes/ — but see below)",
    )
    parser.add_argument(
        "--phase",
        choices=("feedback", "archive"),
        default="feedback",
        help="archive additionally requires each matched episode to be tracked by git",
    )
    args = parser.parse_args(argv)

    # The default carries the SAME hazard as apply_episode_delta.store_root(), named at
    # that function: on a copy installed under ~/.claude/skills/<role>/ this resolves to
    # the skill install directory, not the project repo. Spine commands must pass
    # --store-root explicitly (wired at g3). The resolved root is printed on every
    # outcome below so a wrong root is visible in the gate log rather than silent.
    root = args.store_root if args.store_root is not None else Path(__file__).resolve().parent.parent / "episodes"

    try:
        matches, scanned = matched_episodes(root, args.work_id)
    except StoreRefusal as exc:
        print(f"episode capture: REFUSED — {exc}", file=sys.stderr)
        return EXIT_REFUSED

    if not matches:
        print(
            f"episode capture: BLOCKED — no episode in {root / ACTIVE_DIR} records "
            f"run '{args.work_id}' ({scanned} episode(s) scanned). Capture one with "
            "scripts/apply_episode_delta.py before advancing.",
            file=sys.stderr,
        )
        return EXIT_BLOCKED

    if args.phase == "archive":
        untracked = []
        for episode_id, path in matches:
            tracked, detail = _git_tracked(path)
            if not tracked:
                untracked.append((episode_id, detail))
        if untracked:
            print(
                f"episode capture: BLOCKED — {len(untracked)} of {len(matches)} episode(s) "
                f"for run '{args.work_id}' are not tracked by git, so they do not survive "
                "this worktree. Run `git add episodes/`.",
                file=sys.stderr,
            )
            for episode_id, detail in untracked:
                print(f"  - {episode_id}: {detail}", file=sys.stderr)
            return EXIT_BLOCKED

    print(
        f"episode capture: {len(matches)} episode(s) recorded for run '{args.work_id}' "
        f"in {root / ACTIVE_DIR} ({scanned} scanned, phase {args.phase})"
    )
    for episode_id, _path in matches:
        print(f"  - {episode_id}")
    return EXIT_CAPTURED


if __name__ == "__main__":
    raise SystemExit(main())
