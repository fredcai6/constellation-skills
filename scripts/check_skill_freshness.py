#!/usr/bin/env python
"""Report template drift for a project against its installed-skill baseline.

Three-way status per template:
  baseline (pristine copy at install)  vs  upstream (installed skill source)
  baseline                             vs  local (project working copy)

Statuses: up-to-date | upstream-changed | project-customized | both-changed
(reconcile!) | upstream-removed. The script never merges; conflicts are for a
human (or Charter) to adjudicate — `git merge-file local baseline upstream` is
the suggested tool. --update-baseline promotes the current upstream to the new
baseline AFTER reconciliation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


class FreshnessError(Exception):
    pass


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest(templates_root: Path) -> dict:
    manifest_path = templates_root / "TEMPLATES_MANIFEST.json"
    if not manifest_path.is_file():
        raise FreshnessError(
            f"no TEMPLATES_MANIFEST.json at {manifest_path} — run a project-scope install first"
        )
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def check(project_root: Path, skills_root: Path) -> list[dict[str, str]]:
    templates_root = project_root / ".agent-work" / "templates"
    baseline_root = templates_root / ".baseline"
    manifest = _load_manifest(templates_root)

    rows: list[dict[str, str]] = []
    for entry in manifest.get("templates", []):
        skill, name = entry["skill"], entry["template"]
        baseline = baseline_root / skill / name
        upstream = skills_root / skill / "templates" / name
        local = templates_root / name

        baseline_hash = _hash(baseline) if baseline.is_file() else None
        upstream_hash = _hash(upstream) if upstream.is_file() else None
        local_hash = _hash(local) if local.is_file() else None

        if baseline_hash is None:
            status = "baseline-missing"
        elif upstream_hash is None:
            status = "upstream-removed"
        else:
            upstream_changed = upstream_hash != baseline_hash
            local_changed = local_hash is not None and local_hash != baseline_hash
            if upstream_changed and local_changed:
                status = "both-changed"
            elif upstream_changed:
                status = "upstream-changed"
            elif local_changed:
                status = "project-customized"
            else:
                status = "up-to-date"
        rows.append({"skill": skill, "template": name, "status": status})
    return rows


def update_baseline(project_root: Path, skills_root: Path) -> int:
    templates_root = project_root / ".agent-work" / "templates"
    baseline_root = templates_root / ".baseline"
    manifest = _load_manifest(templates_root)

    updated = 0
    for entry in manifest.get("templates", []):
        upstream = skills_root / entry["skill"] / "templates" / entry["template"]
        if not upstream.is_file():
            continue
        target = baseline_root / entry["skill"] / entry["template"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(upstream, target)
        entry["sha256"] = _hash(upstream)
        updated += 1
    manifest["baseline_origin"] = "baseline-promoted"
    (templates_root / "TEMPLATES_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument(
        "--skills-root",
        type=Path,
        required=True,
        help="Installed skills directory containing constellation-* skill folders",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Promote current upstream templates to the new baseline (run AFTER reconciling)",
    )
    args = parser.parse_args(argv)

    try:
        if args.update_baseline:
            updated = update_baseline(args.project, args.skills_root)
            print(f"baseline promoted for {updated} template(s)")
            return 0
        rows = check(args.project, args.skills_root)
    except (FreshnessError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    needs_attention = 0
    for row in rows:
        marker = " " if row["status"] in ("up-to-date", "project-customized") else "!"
        if marker == "!":
            needs_attention += 1
        print(f"{marker} {row['status']:<20} {row['skill']}/{row['template']}")

    if needs_attention:
        print(
            f"\n{needs_attention} template(s) need reconciliation. For both-changed: "
            "git merge-file <local> <baseline> <upstream>, adjudicate conflicts, "
            "then rerun with --update-baseline."
        )
        return 1
    print("\nall templates fresh against baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
