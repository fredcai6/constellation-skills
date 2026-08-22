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
import os
import shutil
import sys
from pathlib import Path

def _utf8_stdio() -> None:
    """Per field feedback: don't make every call site set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


class FreshnessError(Exception):
    pass


def _platform_interpreter() -> str:
    """Mirror of install_constellation._platform_interpreter: `py` on Windows,
    `python3` elsewhere. This is the TOTAL-FAILURE fallback only -- used when no
    per-skill sidecar is available to read the interpreter the installer actually
    stamped (see `_resolved_interpreter`). Kept here so freshness normalization can
    still degrade gracefully rather than raising when a skill was never installed."""
    return "py" if os.name == "nt" else "python3"


def _resolved_interpreter(skill: str, skills_root: Path) -> str:
    """The interpreter actually stamped into `skill`'s installed copy.

    install_constellation.py's `resolve_interpreter()` PROBES the host (real
    `<candidate> --version` subprocess calls, in order `py`, `python3`, `python`)
    and RAISES if every candidate fails to invoke -- it has carried no os.name
    fallback since owner ruling #539: a guess drawn from the very candidate set
    the probe in that same run just disproved is guaranteed wrong, so refusing
    beats stamping an unlaunchable name into every installed skill body. The
    probed result is recorded per-skill in `interpreter.json` (a sidecar
    `rewrite_installed_skill_paths` writes next to the installed skill).
    Re-deriving the interpreter via the os.name guess alone
    -- instead of reading what was actually probed -- is wrong whenever the two
    diverge: e.g. a POSIX host where `py` genuinely resolves (a venv shim, an
    alias) probes to `py`, but the guess hardcodes `python3`, so a freshly seeded,
    unedited template compares "py <" against a normalized "python3 <" and reads
    as a phantom edit. Falls back to `_platform_interpreter()`'s guess only when
    the sidecar is missing (skill never installed / already removed) so hashing
    degrades gracefully instead of raising."""
    sidecar = skills_root / skill / "interpreter.json"
    if sidecar.is_file():
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        interpreter = data.get("interpreter")
        if interpreter:
            return interpreter
    return _platform_interpreter()


def _hash(path: Path) -> str:
    """Line-ending-insensitive content hash (CRLF checkouts vs LF writes)."""
    text = path.read_text(encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalized_hash(path: Path, skill: str, skills_root: Path) -> str:
    """Content hash after resolving <skill-dir> / <name-skill-dir> tokens to the
    installed skill dir, so the three sides compare on equal footing.

    A template lives in three forms: the installed skill copy has absolute paths
    (rewritten at install), while the baseline and the project working copy keep
    the portable token form — and a *promoted* baseline (check_skill_freshness
    --update-baseline copies the installed upstream) becomes absolute too.
    Comparing raw hashes would flag a token-form working copy against an
    absolute-form baseline as a phantom edit forever. Normalizing every side to
    the resolved (absolute) form neutralizes the token-vs-absolute difference
    while leaving genuine edits visible. Tokenless templates hash unchanged.

    The installer also rewrites the `python <` interpreter prefix to the ACTUAL
    resolved interpreter (probed live, `py`/`python3`/`python`, not merely the
    os.name guess); the token-form baseline/working-copy keep `python <`. Apply
    the same interpreter rewrite here FIRST (before the `<…-skill-dir>` token
    consumes the trailing `<`) so that rewrite, too, reads as no edit.
    """
    text = path.read_text(encoding="utf-8")
    installed = (skills_root / skill).as_posix()
    short = skill.removeprefix("constellation-")
    text = text.replace("python <", f"{_resolved_interpreter(skill, skills_root)} <")
    text = text.replace("<skill-dir>", installed)
    text = text.replace(f"<{short}-skill-dir>", installed)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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

        # Normalize every side to the resolved form so token-vs-absolute path
        # differences (baseline/working copy in token form, installed upstream and
        # promoted baselines in absolute form) never read as edits — only real
        # content changes do.
        base_n = _normalized_hash(baseline, skill, skills_root) if baseline.is_file() else None
        up_n = _normalized_hash(upstream, skill, skills_root) if upstream.is_file() else None
        local_n = _normalized_hash(local, skill, skills_root) if local.is_file() else None

        if base_n is None:
            status = "baseline-missing"
        elif up_n is None:
            status = "upstream-removed"
        else:
            upstream_changed = up_n != base_n
            local_changed = local_n is not None and local_n != base_n
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
