#!/usr/bin/env python
"""Sweep consuming projects' CONSTELLATION_FEEDBACK.md exports into one report.

Reads `.agent-work/CONSTELLATION_FEEDBACK.md` from each project root, collects
entries appended since the `<!-- collected: ... -->` marker, deduplicates by a
semantic fingerprint (normalized observed+proposal text), and groups recurring
candidates across projects — cross-project recurrence is the validation signal.
With --mark, advances each project's collected marker. Issue filing stays
human-gated: this script only produces the report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

MARKER_RE = re.compile(r"<!--\s*collected:\s*(.*?)\s*-->")
ENTRY_HEADING_RE = re.compile(r"^## .+$", re.MULTILINE)
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*`?(.*?)`?\s*$")

def _utf8_stdio() -> None:
    """Per field feedback: don't make every call site set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def parse_entries(text: str) -> list[dict[str, str]]:
    markers = list(MARKER_RE.finditer(text))
    tail = text[markers[-1].end() :] if markers else text

    entries: list[dict[str, str]] = []
    headings = list(ENTRY_HEADING_RE.finditer(tail))
    for i, match in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(tail)
        block = tail[match.start() : end]
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


def mark_collected(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    stamp = f"<!-- collected: {date.today().isoformat()} -->"
    path.write_text(text.rstrip("\n") + "\n\n" + stamp + "\n", encoding="utf-8")


def collect(project_roots: list[Path]) -> dict[str, list[tuple[str, dict[str, str]]]]:
    by_fingerprint: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for root in project_roots:
        feedback = root / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
        if not feedback.is_file():
            continue
        for entry in parse_entries(feedback.read_text(encoding="utf-8")):
            by_fingerprint.setdefault(fingerprint(entry), []).append((root.name, entry))
    return by_fingerprint


def render_report(by_fingerprint: dict[str, list[tuple[str, dict[str, str]]]]) -> str:
    lines = [f"# Constellation Feedback Sweep — {date.today().isoformat()}", ""]
    if not by_fingerprint:
        lines.append("No uncollected entries found.")
        return "\n".join(lines) + "\n"

    recurring = {fp: hits for fp, hits in by_fingerprint.items() if len({p for p, _ in hits}) > 1}
    singles = {fp: hits for fp, hits in by_fingerprint.items() if fp not in recurring}

    lines.append(
        f"{sum(len(h) for h in by_fingerprint.values())} entr(ies), "
        f"{len(by_fingerprint)} distinct candidate(s), "
        f"{len(recurring)} recurring across projects."
    )
    lines.append("")
    for title, group in (("Recurring (validated by cross-project recurrence)", recurring),
                         ("Single-project (scope tag is a claim, verify)", singles)):
        if not group:
            continue
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
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projects", nargs="*", type=Path, help="Project roots to sweep")
    parser.add_argument(
        "--config", type=Path, help="JSON file with a list of project root paths"
    )
    parser.add_argument("--out", type=Path, help="Write the report here instead of stdout")
    parser.add_argument(
        "--mark", action="store_true", help="Advance each swept project's collected marker"
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

    report = render_report(collect(roots))
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"report written: {args.out}")
    else:
        print(report, end="")

    if args.mark:
        for root in roots:
            feedback = root / ".agent-work" / "CONSTELLATION_FEEDBACK.md"
            if feedback.is_file():
                mark_collected(feedback)
                print(f"marked collected: {feedback}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
