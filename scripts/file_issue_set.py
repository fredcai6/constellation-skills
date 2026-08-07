#!/usr/bin/env python
"""File only the runnable current wave from a verified initial issue set."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_issue_set import IssueSetError, render_epic_body, verify_issue_set  # noqa: E402,F401


KEY_PREFIX = "constellation-key"


class CrashInjected(Exception):
    """Test-only crash at one entity/window, e.g. ``issue:A:after-receipt``."""


def _short(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def manifest_key(manifest: dict) -> str:
    return f"manifest:{_short(_canonical(manifest))}"


def epic_key(manifest: dict) -> str:
    epic = manifest["epic"]
    return f"epic:{_short(epic['spec_path'] + chr(0) + epic['title'])}"


def issue_key(ekey: str, issue_id: str) -> str:
    return f"issue:{_short(ekey)}:{issue_id}"


def key_marker(key: str) -> str:
    return f"<!-- {KEY_PREFIX}: {key} -->"


def current_issues(manifest: dict) -> list[dict]:
    """The sole actionable collection. Forecast is deliberately unreachable."""
    return manifest["current_wave"]["issues"]


def wave_order(manifest: dict) -> list[list[dict]]:
    issues = {issue["id"]: issue for issue in current_issues(manifest)}
    deps = {iid: set() for iid in issues}
    for issue in current_issues(manifest):
        for target in issue["blocks"]:
            deps[target].add(issue["id"])
    waves: list[list[dict]] = []
    placed: set[str] = set()
    while len(placed) < len(issues):
        ready = sorted(iid for iid in issues if iid not in placed and deps[iid] <= placed)
        if not ready:
            raise IssueSetError("dependency cycle in current_wave.issues blocks edges")
        waves.append([issues[iid] for iid in ready])
        placed.update(ready)
    return waves


def build_epic_body(manifest: dict, ekey: str) -> str:
    return render_epic_body(manifest).rstrip() + "\n\n" + key_marker(ekey) + "\n"


def build_issue_body(issue: dict, ikey: str) -> str:
    lines = [
        issue["desired_outcome"], "",
        f"Useful now: {issue['useful_now']}",
        f"Appetite: {issue['appetite']}",
        f"Acceptance or falsification evidence: {issue['acceptance_or_falsification_evidence']}",
        f"Implementation latitude: {issue['implementation_latitude']}",
        "", key_marker(ikey), f"type: {issue['type']}",
    ]
    if issue["type"] == "HITL":
        lines.append(f"hitl_reason: {issue['hitl_reason']}")
    return "\n".join(lines).strip() + "\n"


class FilingAdapter:
    def find_epic(self, key: str) -> str | None:  # pragma: no cover
        raise NotImplementedError

    def create_epic(self, epic: dict, body: str, key: str) -> str:  # pragma: no cover
        raise NotImplementedError

    def find_issue(self, key: str) -> str | None:  # pragma: no cover
        raise NotImplementedError

    def create_issue(self, issue: dict, body: str, key: str) -> str:  # pragma: no cover
        raise NotImplementedError


class MarkdownAdapter(FilingAdapter):
    def __init__(self, path: Path):
        self.path = Path(path)

    def _text(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def _append(self, section: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(section)

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

    def count_epics(self) -> int:
        return sum(line.startswith("# EPIC: ") for line in self._text().splitlines())

    def count_issues(self) -> int:
        return sum(line.startswith("## ISSUE: ") for line in self._text().splitlines())


class GitHubAdapter(FilingAdapter):
    def __init__(self, repo: str | None = None, labels: tuple[str, ...] = ()):
        self.repo = repo
        self.labels = labels

    def _gh(self, args: list[str]) -> str:
        cmd = ["gh", *args]
        if self.repo:
            cmd += ["--repo", self.repo]
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode != 0:
            raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{result.stderr.strip()}")
        return result.stdout.strip()

    def _find(self, key: str) -> str | None:
        output = self._gh([
            "issue", "list", "--state", "all", "--search", f'"{key_marker(key)}" in:body',
            "--json", "url", "--limit", "1",
        ])
        try:
            hits = json.loads(output or "[]")
        except json.JSONDecodeError:
            return None
        return hits[0]["url"] if hits else None

    def _create(self, title: str, body: str, labels: tuple[str, ...]) -> str:
        args = ["issue", "create", "--title", title, "--body", body]
        for label in (*self.labels, *labels):
            args += ["--label", label]
        return self._gh(args)

    def find_epic(self, key: str) -> str | None:
        return self._find(key)

    def create_epic(self, epic: dict, body: str, key: str) -> str:
        return self._create(epic["title"], body, ("epic",))

    def find_issue(self, key: str) -> str | None:
        return self._find(key)

    def create_issue(self, issue: dict, body: str, key: str) -> str:
        return self._create(issue["title"], body, (issue["type"].lower(),))


def build_adapter(tracker: str, dest: str | None, repo: str | None) -> FilingAdapter:
    tracker = "github" if tracker == "auto" else tracker
    if tracker == "markdown":
        if not dest:
            raise IssueSetError("--tracker markdown requires --dest <tracker.md>")
        return MarkdownAdapter(Path(dest))
    if tracker == "github":
        return GitHubAdapter(repo=repo)
    if tracker == "gitlab":
        raise IssueSetError("gitlab adapter is not built; only github and markdown ship")
    raise IssueSetError(f"unknown tracker {tracker!r}")


def _load_receipt(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IssueSetError(f"cannot read receipt: {exc}") from exc
    if not isinstance(receipt, dict):
        raise IssueSetError("receipt must be a JSON object")
    return receipt


def _write_receipt(path: Path, receipt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")


def _entry(entry: object, path: str, expected_key: str) -> dict:
    if not isinstance(entry, dict) or set(entry) != {"key", "ref"}:
        raise IssueSetError(f"{path} must contain exactly key and ref")
    if entry["key"] != expected_key:
        raise IssueSetError(f"{path}.key does not match the current manifest")
    if not isinstance(entry["ref"], str) or not entry["ref"].strip():
        raise IssueSetError(f"{path}.ref must be a nonempty string")
    return entry


def _validated_receipt(receipt: dict, manifest: dict) -> dict:
    if not receipt:
        return {"manifest_key": manifest_key(manifest), "issues": {}}
    unknown = set(receipt) - {"manifest_key", "epic", "issues"}
    if unknown:
        raise IssueSetError(f"receipt has unknown field(s): {', '.join(sorted(unknown))}")
    if receipt.get("manifest_key") != manifest_key(manifest):
        raise IssueSetError("receipt.manifest_key does not match the current manifest")
    if "issues" not in receipt or not isinstance(receipt["issues"], dict):
        raise IssueSetError("receipt.issues must be an object")
    ekey = epic_key(manifest)
    if "epic" in receipt:
        _entry(receipt["epic"], "receipt.epic", ekey)
    expected = {issue["id"]: issue_key(ekey, issue["id"]) for issue in current_issues(manifest)}
    for iid, entry in receipt["issues"].items():
        if iid not in expected:
            raise IssueSetError(f"receipt.issues has unknown current issue {iid!r}")
        _entry(entry, f"receipt.issues.{iid}", expected[iid])
    return receipt


def _crash(crash_at: str | None, entity: str, point: str) -> None:
    if crash_at == f"{entity}:{point}":
        raise CrashInjected(f"{entity}:{point}")


def file_issue_set(
    manifest: dict,
    brief: dict,
    adapter: FilingAdapter,
    receipt_path: Path,
    *,
    crash_at: str | None = None,
) -> dict:
    """Verify, validate the receipt, and idempotently file the current wave."""
    verify_issue_set(manifest, brief)
    receipt_path = Path(receipt_path)
    receipt = _validated_receipt(_load_receipt(receipt_path), manifest)
    ekey = epic_key(manifest)

    epic_ref = receipt.get("epic", {}).get("ref")
    if epic_ref is None:
        epic_ref = adapter.find_epic(ekey)
        if epic_ref is None:
            _crash(crash_at, "epic", "before-file")
            epic_ref = adapter.create_epic(manifest["epic"], build_epic_body(manifest, ekey), ekey)
            _crash(crash_at, "epic", "after-file-before-receipt")
        receipt["epic"] = {"key": ekey, "ref": epic_ref}
        _write_receipt(receipt_path, receipt)
        _crash(crash_at, "epic", "after-receipt")

    for issue in current_issues(manifest):
        iid = issue["id"]
        ikey = issue_key(ekey, iid)
        ref = receipt["issues"].get(iid, {}).get("ref")
        if ref is None:
            ref = adapter.find_issue(ikey)
            if ref is None:
                _crash(crash_at, f"issue:{iid}", "before-file")
                ref = adapter.create_issue(issue, build_issue_body(issue, ikey), ikey)
                _crash(crash_at, f"issue:{iid}", "after-file-before-receipt")
            receipt["issues"][iid] = {"key": ikey, "ref": ref}
            _write_receipt(receipt_path, receipt)
            _crash(crash_at, f"issue:{iid}", "after-receipt")
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="path to initial issue-set JSON")
    parser.add_argument("--brief", required=True, help="path to confirmed shaped-brief JSON")
    parser.add_argument("--tracker", choices=("auto", "github", "gitlab", "markdown"), default="auto")
    parser.add_argument("--dest", help="markdown tracker path")
    parser.add_argument("--repo", help="owner/name for GitHub")
    parser.add_argument("--receipt", help="receipt path (default: <manifest>.receipt.json)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        verify_issue_set(manifest, brief)
        if args.dry_run:
            print(f"DRY RUN: would file {len(current_issues(manifest))} current issue(s) via {args.tracker}")
            return 0
        adapter = build_adapter(args.tracker, args.dest, args.repo)
        receipt_path = Path(args.receipt) if args.receipt else Path(str(args.manifest) + ".receipt.json")
        receipt = file_issue_set(manifest, brief, adapter, receipt_path)
    except (OSError, json.JSONDecodeError, IssueSetError, RuntimeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(f"filed: epic {receipt['epic']['ref']} + {len(receipt['issues'])} current issue(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
