#!/usr/bin/env python
"""File a cut-work issue set to a tracker — the constellation-to-issues FILER.

Ports-and-adapters (DESIGN_SPEC Section A): a tracker-agnostic issue-set
manifest is filed through ONE swappable adapter seam. Two adapters ship this
epic — `github` (the real, GitHub-first default) and `markdown` (the offline
test fixture / portability proof). A `gitlab` seam is deliberately NOT built
(the seam exists; only github + markdown ship). GitHub-first, seam-pluggable,
not GitHub-only.

Two safeties, both cheap and both load-bearing:

  * THE RAIL RUNS FIRST. `verify_issue_set` (verify_issue_set.py) gates every
    filing; a malformed set raises before ANY tracker write, so a malformed
    manifest can never reach a tracker.

  * IDEMPOTENT VIA A RECEIPT + KEY-EXISTENCE CHECK. Every epic/issue carries a
    deterministic idempotency key embedded in its filed body. A crash mid-file
    re-runs without a duplicate epic: the receipt is the fast path, and when the
    receipt is missing an entry (the crash landed between the tracker write and
    the receipt write) the adapter re-finds the already-filed item BY KEY and
    adopts it. Correctness holds at all three crash-injection points
    (before-file / after-file-before-receipt / after-receipt; TF7).

Downstream seam: the epic body is the wave-ordered task list (a topological
sort of the `blocks` edges) with AFK/HITL labels — the Admiral's intake
consumes it. Standard library only (the github adapter shells out to `gh`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_issue_set import verify_issue_set, IssueSetError  # noqa: F401 (re-exported)

KEY_PREFIX = "constellation-key"


class CrashInjected(Exception):
    """Test-only: raised at a named crash-injection point to prove idempotency."""


# --------------------------------------------------------------------------- #
# Idempotency keys — deterministic from the manifest, embedded in filed bodies.
# --------------------------------------------------------------------------- #
def _short(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def epic_key(manifest: dict) -> str:
    epic = manifest["epic"]
    seed = f"{epic.get('spec_path', '')}\0{epic['title']}"
    return f"epic:{_short(seed)}"


def issue_key(ekey: str, issue_id: str) -> str:
    return f"issue:{_short(ekey)}:{issue_id}"


def key_marker(key: str) -> str:
    """The hidden marker embedded in a filed body so an adapter can find the
    item again by key after a crash (before the receipt recorded it)."""
    return f"<!-- {KEY_PREFIX}: {key} -->"


# --------------------------------------------------------------------------- #
# Wave ordering — topological sort of the `blocks` edges into ordered waves.
# --------------------------------------------------------------------------- #
def wave_order(manifest: dict) -> list[list[dict]]:
    """Kahn-style layering: wave 0 = issues nothing blocks-into (no unmet
    dependency), then peel. `A blocks B` means A must precede B. A cycle raises
    (the rail already rejects dangling edges; a cycle is the remaining hazard)."""
    issues = {i["id"]: i for i in manifest["issues"]}
    # deps[x] = set of issues that must come before x (i.e. that block x).
    deps: dict[str, set[str]] = {iid: set() for iid in issues}
    for i in manifest["issues"]:
        for target in i.get("blocks", []):
            deps[str(target)].add(i["id"])

    waves: list[list[dict]] = []
    placed: set[str] = set()
    while len(placed) < len(issues):
        ready = [iid for iid in issues if iid not in placed and deps[iid] <= placed]
        if not ready:
            raise IssueSetError("dependency cycle in blocks edges; cannot wave-order")
        ready.sort()
        waves.append([issues[iid] for iid in ready])
        placed.update(ready)
    return waves


def build_epic_body(manifest: dict, ekey: str) -> str:
    """The downstream seam: wave-ordered task list + AFK/HITL labels + the
    idempotency marker."""
    lines = [manifest["epic"].get("body", "").strip(), "", "## Waves", ""]
    for w, wave in enumerate(wave_order(manifest)):
        lines.append(f"### Wave {w}")
        for issue in wave:
            label = issue.get("type", "?")
            reason = f" — {issue['hitl_reason']}" if issue.get("type") == "HITL" else ""
            lines.append(f"- [ ] **[{label}]** {issue['id']}: {issue['title']}{reason}")
        lines.append("")
    lines.append(key_marker(ekey))
    return "\n".join(lines).strip() + "\n"


def build_issue_body(issue: dict, ikey: str) -> str:
    body = issue.get("body", "").strip()
    label = issue.get("type", "?")
    tail = [key_marker(ikey), f"type: {label}"]
    if issue.get("type") == "HITL":
        tail.append(f"hitl_reason: {issue['hitl_reason']}")
    return (body + "\n\n" + "\n".join(tail)).strip() + "\n"


# --------------------------------------------------------------------------- #
# Adapter seam — the ONE port every tracker plugs into.
# --------------------------------------------------------------------------- #
class FilingAdapter:
    """The port. An adapter finds an item by its idempotency key (crash
    recovery) and creates it if absent. `find_*` returns a tracker ref or None."""

    def find_epic(self, key: str) -> str | None:  # pragma: no cover - interface
        raise NotImplementedError

    def create_epic(self, epic: dict, body: str, key: str) -> str:  # pragma: no cover
        raise NotImplementedError

    def find_issue(self, key: str) -> str | None:  # pragma: no cover - interface
        raise NotImplementedError

    def create_issue(self, issue: dict, body: str, key: str) -> str:  # pragma: no cover
        raise NotImplementedError


class MarkdownAdapter(FilingAdapter):
    """Offline fixture / portability proof: the 'tracker' is a single markdown
    file. Find-by-key scans the file for the embedded key marker; create appends
    a section. Faithful to the idempotency contract without any network."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _text(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def _append(self, section: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(section)

    def _find(self, key: str) -> str | None:
        return f"md:{key}" if key_marker(key) in self._text() else None

    def find_epic(self, key: str) -> str | None:
        return self._find(key)

    def create_epic(self, epic: dict, body: str, key: str) -> str:
        self._append(f"\n# EPIC: {epic['title']}\n\n{body}\n")
        return f"md:{key}"

    def find_issue(self, key: str) -> str | None:
        return self._find(key)

    def create_issue(self, issue: dict, body: str, key: str) -> str:
        self._append(f"\n## ISSUE: {issue['title']}\n\n{body}\n")
        return f"md:{key}"

    # Test/inspection helpers.
    def count_epics(self) -> int:
        return sum(1 for line in self._text().splitlines() if line.startswith("# EPIC: "))

    def count_issues(self) -> int:
        return sum(1 for line in self._text().splitlines() if line.startswith("## ISSUE: "))


class GitHubAdapter(FilingAdapter):
    """The shipped, GitHub-first adapter. Shells out to `gh`; finds an existing
    item by searching for its embedded key marker so a crash re-run adopts
    rather than duplicates. Not exercised by the offline test suite (no
    network); the markdown adapter proves the idempotency contract."""

    def __init__(self, repo: str | None = None, labels: tuple[str, ...] = ()):
        self.repo = repo
        self.labels = labels

    def _gh(self, args: list[str]) -> str:
        cmd = ["gh", *args]
        if self.repo:
            cmd += ["--repo", self.repo]
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{result.stderr.strip()}")
        return result.stdout.strip()

    def _find(self, key: str) -> str | None:
        out = self._gh(["issue", "list", "--state", "all", "--search",
                        f"\"{key_marker(key)}\" in:body", "--json", "url", "--limit", "1"])
        try:
            hits = json.loads(out or "[]")
        except json.JSONDecodeError:
            return None
        return hits[0]["url"] if hits else None

    def _create(self, title: str, body: str, extra_labels: tuple[str, ...]) -> str:
        args = ["issue", "create", "--title", title, "--body", body]
        for label in (*self.labels, *extra_labels):
            args += ["--label", label]
        return self._gh(args)

    def find_epic(self, key: str) -> str | None:
        return self._find(key)

    def create_epic(self, epic: dict, body: str, key: str) -> str:
        return self._create(epic["title"], body, ("epic",))

    def find_issue(self, key: str) -> str | None:
        return self._find(key)

    def create_issue(self, issue: dict, body: str, key: str) -> str:
        return self._create(issue["title"], body, (issue.get("type", "").lower(),))


def build_adapter(tracker: str, dest: str | None, repo: str | None) -> FilingAdapter:
    resolved = "github" if tracker == "auto" else tracker
    if resolved == "markdown":
        if not dest:
            raise IssueSetError("--tracker markdown requires --dest <tracker.md>")
        return MarkdownAdapter(Path(dest))
    if resolved == "github":
        return GitHubAdapter(repo=repo)
    if resolved == "gitlab":
        raise IssueSetError("gitlab adapter is not built this epic (the seam exists; only github + markdown ship)")
    raise IssueSetError(f"unknown tracker {tracker!r}")


# --------------------------------------------------------------------------- #
# Receipt — the durable record of what has been filed, keyed by idempotency key.
# --------------------------------------------------------------------------- #
def _load_receipt(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _write_receipt(path: Path, receipt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def _crash(crash_at: str | None, point: str) -> None:
    if crash_at == point:
        raise CrashInjected(point)


def file_issue_set(
    manifest: dict,
    spec_text: str,
    adapter: FilingAdapter,
    receipt_path: Path,
    *,
    crash_at: str | None = None,
) -> dict:
    """File the set idempotently, returning the receipt. Runs the rail first.

    `crash_at` is a test-only injection point: one of "before-file",
    "after-file-before-receipt", "after-receipt". Each re-run after a crash
    yields no duplicate epic.
    """
    # THE RAIL — refuse a malformed set before touching the tracker.
    verify_issue_set(manifest, spec_text)

    receipt_path = Path(receipt_path)
    receipt = _load_receipt(receipt_path)
    receipt.setdefault("issues", {})

    ekey = epic_key(manifest)

    # --- Epic (the crash-window under test) ---
    epic_ref = receipt.get("epic", {}).get("ref")
    if epic_ref is None:
        # Receipt has no epic: either first run, or we crashed after filing but
        # before recording. Ask the tracker by key before creating (dupe guard).
        epic_ref = adapter.find_epic(ekey)
    if epic_ref is None:
        _crash(crash_at, "before-file")
        epic_ref = adapter.create_epic(manifest["epic"], build_epic_body(manifest, ekey), ekey)
        _crash(crash_at, "after-file-before-receipt")
    receipt["epic"] = {"key": ekey, "ref": epic_ref}
    _write_receipt(receipt_path, receipt)
    _crash(crash_at, "after-receipt")

    # --- Issues ---
    for issue in manifest["issues"]:
        iid = issue["id"]
        ref = receipt["issues"].get(iid, {}).get("ref")
        if ref is None:
            ikey = issue_key(ekey, iid)
            ref = adapter.find_issue(ikey)
            if ref is None:
                ref = adapter.create_issue(issue, build_issue_body(issue, ikey), ikey)
            receipt["issues"][iid] = {"key": ikey, "ref": ref}
            _write_receipt(receipt_path, receipt)

    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="path to the issue-set manifest JSON")
    parser.add_argument("--spec", required=True, help="path to the confirmed DESIGN_SPEC.md")
    parser.add_argument("--tracker", choices=("auto", "github", "gitlab", "markdown"), default="auto")
    parser.add_argument("--dest", help="markdown tracker file (for --tracker markdown)")
    parser.add_argument("--repo", help="owner/name for the github adapter (default: current repo)")
    parser.add_argument("--receipt", help="receipt path (default: <manifest>.receipt.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="run the rail and print the plan; do not file")
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        spec_text = Path(args.spec).read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED: cannot read inputs: {exc}", file=sys.stderr)
        return 1

    try:
        verify_issue_set(manifest, spec_text)  # rail first, always
        if args.dry_run:
            waves = wave_order(manifest)
            print(f"DRY RUN: would file epic {manifest['epic']['title']!r} + "
                  f"{len(manifest['issues'])} issue(s) in {len(waves)} wave(s) via --tracker {args.tracker}")
            return 0
        adapter = build_adapter(args.tracker, args.dest, args.repo)
        receipt_path = Path(args.receipt) if args.receipt else Path(str(args.manifest) + ".receipt.json")
        receipt = file_issue_set(manifest, spec_text, adapter, receipt_path)
    except IssueSetError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"FILING ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"filed: epic {receipt['epic']['ref']} + {len(receipt['issues'])} issue(s); "
          f"receipt {receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
