#!/usr/bin/env python
"""Sweep consuming projects' CONSTELLATION_FEEDBACK.md exports into one report.

Reads `.agent-work/CONSTELLATION_FEEDBACK.md` from each project root and tracks
per-entry state in a sidecar (`CONSTELLATION_FEEDBACK.collected.json`): entries
are deduplicated by a semantic fingerprint (normalized observed+proposal text)
and each fingerprint is independently `collected` (ingested by a sweep) and
later `resolved` (acted on upstream). Collected-but-unresolved candidates stay
visible in every report until resolved — collected never means fixed. Recurring
candidates are grouped across projects: cross-project recurrence is the
validation signal. Issue filing stays human-gated: this script only reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ENTRY_HEADING_RE = re.compile(r"^## .+$", re.MULTILINE)
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*`?(.*?)`?\s*$")
SIDECAR_NAME = "CONSTELLATION_FEEDBACK.collected.json"


def _utf8_stdio() -> None:
    """Per field feedback: don't make every call site set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    headings = list(ENTRY_HEADING_RE.finditer(text))
    for i, match in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[match.start() : end]
        heading = match.group(0).lstrip("# ").strip()
        if heading.startswith("`<date>`"):
            continue  # template placeholder entry
        entry = {"heading": heading}
        for line in block.splitlines():
            field = FIELD_RE.match(line.strip())
            if field:
                entry[field.group(1).strip().lower()] = field.group(2).strip()
        entries.append(entry)
    return entries


def fingerprint(entry: dict[str, str]) -> str:
    basis = (entry.get("observed", "") + "|" + entry.get("proposal", "")).lower()
    basis = re.sub(r"[^a-z0-9|]+", " ", basis)
    basis = re.sub(r"\s+", " ", basis).strip()
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]


def _sidecar_path(root: Path) -> Path:
    return root / ".agent-work" / SIDECAR_NAME


def load_sidecar(root: Path) -> dict:
    path = _sidecar_path(root)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"collected": {}, "resolved": {}}


def save_sidecar(root: Path, state: dict) -> None:
    _sidecar_path(root).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


Hits = dict[str, list[tuple[str, dict[str, str]]]]


def collect(project_roots: list[Path]) -> tuple[Hits, Hits]:
    """Return (new, open_unresolved) candidate groups keyed by fingerprint."""
    new: Hits = {}
    open_unresolved: Hits = {}
    for root in project_roots:
        feedback = root / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
        if not feedback.is_file():
            continue
        state = load_sidecar(root)
        for entry in parse_entries(feedback.read_text(encoding="utf-8")):
            fp = fingerprint(entry)
            if fp in state["resolved"]:
                continue
            bucket = open_unresolved if fp in state["collected"] else new
            bucket.setdefault(fp, []).append((root.name, entry))
    return new, open_unresolved


def mark_collected(root: Path) -> int:
    """Record every current entry fingerprint as collected; returns count newly marked."""
    feedback = root / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
    if not feedback.is_file():
        return 0
    state = load_sidecar(root)
    today = date.today().isoformat()
    marked = 0
    for entry in parse_entries(feedback.read_text(encoding="utf-8")):
        fp = fingerprint(entry)
        if fp not in state["collected"]:
            state["collected"][fp] = today
            marked += 1
    save_sidecar(root, state)
    return marked


def mark_resolved(root: Path, fp: str, note: str) -> bool:
    state = load_sidecar(root)
    if fp in state["resolved"]:
        return False
    state["resolved"][fp] = {"date": date.today().isoformat(), "note": note}
    state["collected"].setdefault(fp, date.today().isoformat())
    save_sidecar(root, state)
    return True


def _render_group(lines: list[str], title: str, group: Hits) -> None:
    if not group:
        return
    lines.append(f"## {title}")
    lines.append("")
    for fp, hits in sorted(group.items(), key=lambda kv: -len(kv[1])):
        first = hits[0][1]
        projects = sorted({p for p, _ in hits})
        lines.append(f"### {first.get('candidate', fp)} ({fp})")
        lines.append(f"- projects: {', '.join(projects)} ({len(hits)} entr(ies))")
        for key in ("observed", "cost", "proposal", "grounding", "template vintage", "confidence"):
            if first.get(key):
                lines.append(f"- {key}: {first[key]}")
        lines.append("")


def render_report(new: Hits, open_unresolved: Hits) -> str:
    lines = [f"# Constellation Feedback Sweep — {date.today().isoformat()}", ""]
    if not new and not open_unresolved:
        lines.append("No new or open candidates.")
        return "\n".join(lines) + "\n"

    recurring = {fp: hits for fp, hits in new.items() if len({p for p, _ in hits}) > 1}
    singles = {fp: hits for fp, hits in new.items() if fp not in recurring}

    lines.append(
        f"{len(new)} new candidate(s) ({len(recurring)} recurring across projects), "
        f"{len(open_unresolved)} previously collected and still unresolved."
    )
    lines.append("")
    _render_group(lines, "New — recurring (validated by cross-project recurrence)", recurring)
    _render_group(lines, "New — single-project (scope tag is a claim, verify)", singles)
    _render_group(lines, "Open — collected earlier, not yet resolved", open_unresolved)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projects", nargs="*", type=Path, help="Project roots to sweep")
    parser.add_argument(
        "--config", type=Path, help="JSON file with a list of project root paths"
    )
    parser.add_argument("--out", type=Path, help="Write the report here instead of stdout")
    parser.add_argument(
        "--mark", action="store_true", help="Record current entries as collected (per entry)"
    )
    parser.add_argument(
        "--resolve",
        metavar="FINGERPRINT",
        help="Mark one candidate resolved across the given projects",
    )
    parser.add_argument(
        "--note", default="", help="Resolution note for --resolve (e.g. 'fixed in PR #19')"
    )
    args = parser.parse_args(argv)

    roots = list(args.projects)
    if args.config:
        try:
            roots.extend(Path(p) for p in json.loads(args.config.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: bad --config: {exc}", file=sys.stderr)
            return 2
    if not roots:
        print("error: no project roots given (args or --config)", file=sys.stderr)
        return 2

    if args.resolve:
        if not args.note.strip():
            print("error: --resolve requires --note (what resolved it)", file=sys.stderr)
            return 2
        for root in roots:
            if mark_resolved(root, args.resolve, args.note.strip()):
                print(f"resolved {args.resolve} in {root.name}: {args.note.strip()}")
        return 0

    new, open_unresolved = collect(roots)
    report = render_report(new, open_unresolved)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"report written: {args.out}")
    else:
        print(report, end="")

    if args.mark:
        for root in roots:
            marked = mark_collected(root)
            if marked:
                print(f"marked {marked} entr(ies) collected in {root.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
