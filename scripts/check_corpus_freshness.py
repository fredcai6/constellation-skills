#!/usr/bin/env python
"""Report whether an installed constellation corpus is current with upstream main.

Reads the CORPUS.json provenance marker the installer stamps into a skills root
(source_commit) and compares it to the HEAD of constellation's main branch on
GitHub. Needs NO local constellation clone: it fetches the remote head with
`gh api` and falls back to a plain HTTPS call to the GitHub REST API, so it runs
inside a cloud session on any consuming repo that carries a project-scope install.

Where check_skill_freshness.py answers "did my customized templates drift from
their baseline?", this answers the coarser, clone-free question "is this whole
corpus behind upstream, and by how much?".

Exit codes:
  0  current      — installed source_commit == upstream main HEAD
  1  behind        — upstream has commits the install does not (count + subjects)
  2  cannot-determine — no/invalid marker, unknown commit, or the remote is
                        unreachable; never a false "current".
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_REPO = "fredcai6/constellation-skills"
DEFAULT_BRANCH = "main"
CORPUS_MARKER = "CORPUS.json"


def _utf8_stdio() -> None:
    """Mirror check_skill_freshness: don't make every call site set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


class FreshnessError(Exception):
    pass


# --------------------------------------------------------------------------- #
# remote seam — gh api, HTTPS fallback; a fake is injected in tests (no network)
# --------------------------------------------------------------------------- #
class GitHubRemote:
    """Fetches upstream facts from the GitHub REST API. Tries `gh api` first
    (inherits the cloud session's auth), then an unauthenticated HTTPS GET. Both
    hit the same REST paths, so a fake with the same two methods stands in for the
    whole class in tests — no network is ever touched under test."""

    def __init__(self, repo: str = DEFAULT_REPO, branch: str = DEFAULT_BRANCH) -> None:
        self.repo = repo
        self.branch = branch

    def _get(self, path: str) -> dict:
        try:
            result = subprocess.run(
                ["gh", "api", path],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            result = None
        if result is not None and result.returncode == 0:
            return json.loads(result.stdout)

        url = f"https://api.github.com/{path}"
        request = urllib.request.Request(
            url, headers={"Accept": "application/vnd.github+json", "User-Agent": "constellation-freshness"}
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            detail = ""
            if result is not None and result.stderr:
                detail = f" (gh: {result.stderr.strip()})"
            raise FreshnessError(f"could not reach GitHub API for {path}: {exc}{detail}") from exc

    def head_commit(self) -> str:
        data = self._get(f"repos/{self.repo}/commits/{self.branch}")
        return data["sha"]

    def compare(self, base: str, head: str) -> dict:
        """GitHub compare of base...head. `ahead_by` is how many commits `head`
        (upstream main) has that `base` (the install) lacks, and `commits` are
        exactly those commits oldest-first."""
        return self._get(f"repos/{self.repo}/compare/{base}...{head}")


# --------------------------------------------------------------------------- #
# pure core
# --------------------------------------------------------------------------- #
def read_marker(skills_root: Path) -> dict:
    marker_path = skills_root / CORPUS_MARKER
    if not marker_path.is_file():
        raise FreshnessError(
            f"no {CORPUS_MARKER} at {marker_path} — run a constellation install into this root first"
        )
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FreshnessError(f"{marker_path} is not valid JSON: {exc}") from exc
    if not isinstance(marker, dict):
        raise FreshnessError(f"{marker_path} is not a JSON object")
    return marker


def _subject(commit: dict) -> str:
    message = commit.get("commit", {}).get("message", "")
    return message.splitlines()[0] if message else "(no subject)"


def evaluate(marker: dict, remote: GitHubRemote) -> tuple[int, str]:
    """Return (exit_code, human report). Raises FreshnessError only for the
    cannot-determine causes the caller maps to exit 2."""
    installed = marker.get("source_commit")
    if not installed or installed == "unknown":
        raise FreshnessError(
            "installed CORPUS.json has no usable source_commit (built outside a git "
            "checkout); cannot determine freshness"
        )

    head = remote.head_commit()
    if installed == head:
        return 0, f"current — corpus is at {head[:12]} (upstream {remote.branch} HEAD)"

    comparison = remote.compare(installed, head)
    # base=install, head=main: the commits main has that the install lacks land in
    # `ahead_by` (head ahead of base), so that is how far behind the install is.
    behind = comparison.get("ahead_by", 0)
    commits = comparison.get("commits", [])
    lines = [
        f"behind — install at {installed[:12]}, upstream {remote.branch} at {head[:12]} "
        f"({behind} commit(s) behind)",
    ]
    for commit in commits:
        sha = commit.get("sha", "")[:12]
        lines.append(f"  {sha}  {_subject(commit)}")
    return 1, "\n".join(lines)


def main(argv: list[str] | None = None, *, remote: GitHubRemote | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-root",
        type=Path,
        required=True,
        help="Installed skills directory carrying the CORPUS.json marker",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"owner/name of the constellation repo (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help=f"upstream branch to compare against (default: {DEFAULT_BRANCH})",
    )
    args = parser.parse_args(argv)

    if remote is None:
        remote = GitHubRemote(repo=args.repo, branch=args.branch)

    try:
        marker = read_marker(args.skills_root)
        exit_code, report = evaluate(marker, remote)
    except FreshnessError as exc:
        print(f"cannot-determine: {exc}", file=sys.stderr)
        return 2

    print(report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
