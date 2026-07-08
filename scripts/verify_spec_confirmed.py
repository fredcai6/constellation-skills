#!/usr/bin/env python
"""Verify a shaped-design spec's Confirmation block and findings table.

Wired as the explorer spine's `review`/`confirm` step command checks and as
the Commander understand-step intake check: "no work is cut from an
unconfirmed design" must be mechanically enforceable, not prose. See
DESIGN_SPEC.md, headline doctrine 3.

Phases:
  review  -- PASS iff a findings table exists and no Disposition cell is
             empty. Status may still be DRAFT.
  confirm -- (default) PASS iff Status is CONFIRMED, Confirmed-by and Date
             are non-empty, AND no Disposition cell is empty.

Any phase: a loud `UNCONFIRMED -- DO NOT CUT` marker line (em-dash or hyphen)
FAILs with a named refusal. A spec with no findings table FAILs both phases
-- a critical review is mandatory; absence must not pass silently.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_CONFIRMATION_HEADING_RE = re.compile(r"^##\s+Confirmation\s*$", re.MULTILINE)
_ANY_H2_RE = re.compile(r"^##\s+\S", re.MULTILINE)
_STATUS_RE = re.compile(r"^-\s*\*\*Status:\s*(.*?)\*\*\s*$", re.MULTILINE)
_CONFIRMED_BY_RE = re.compile(r"^-\s*Confirmed by:\s*(.*)$", re.MULTILINE)
_DATE_RE = re.compile(r"^-\s*Date:\s*(.*)$", re.MULTILINE)

# Either em-dash or hyphen variant of the marker.
_UNCONFIRMED_MARKER_RE = re.compile(r"UNCONFIRMED\s+[—-]\s+DO NOT CUT")


class SpecVerificationError(Exception):
    """Raised when the design-spec confirmation invariant is broken."""


def _confirmation_section(text: str) -> str | None:
    """Return the ``## Confirmation`` section body, or None if absent."""
    match = _CONFIRMATION_HEADING_RE.search(text)
    if match is None:
        return None
    start = match.end()
    tail = _ANY_H2_RE.search(text, start)
    end = tail.start() if tail else len(text)
    return text[start:end]


def parse_confirmation(text: str) -> dict[str, str | None]:
    """Pull Status / Confirmed-by / Date out of the Confirmation section.

    Any field not found is None (missing, not merely blank).
    """
    section = _confirmation_section(text)
    if section is None:
        return {"status": None, "confirmed_by": None, "date": None}

    def _find(pattern: re.Pattern) -> str | None:
        m = pattern.search(section)
        return m.group(1).strip() if m else None

    return {
        "status": _find(_STATUS_RE),
        "confirmed_by": _find(_CONFIRMED_BY_RE),
        "date": _find(_DATE_RE),
    }


def _split_row(line: str) -> list[str]:
    cells = line.strip().split("|")
    # A well-formed "| a | b |" row has an empty leading/trailing split segment.
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


def _is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells) if cells else False


def find_findings_table(text: str) -> list[str] | None:
    """Return the list of Disposition cell values (one per data row), or None
    if no findings table is present.

    A findings table is any Markdown pipe-table whose header row contains an
    ``ID`` column and both a ``Disposition`` and a ``Reason`` column (exact
    names, tolerant of the Lens(es)/Lens and Sev/Severity header variants).
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and line.endswith("|"):
            header = _split_row(line)
            if (
                i + 1 < len(lines)
                and _is_separator_row(_split_row(lines[i + 1]))
                and "ID" in header
                and "Disposition" in header
                and "Reason" in header
            ):
                disposition_idx = header.index("Disposition")
                dispositions: list[str] = []
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|") and lines[j].strip().endswith("|"):
                    row = _split_row(lines[j])
                    cell = row[disposition_idx] if disposition_idx < len(row) else ""
                    dispositions.append(cell)
                    j += 1
                return dispositions
        i += 1
    return None


def _unconfirmed_marker_hit(text: str) -> str | None:
    """Return the offending line if the marker appears as a status/header
    line (not merely mentioned in prose), else None.
    """
    for line in text.splitlines():
        stripped = line.strip()
        # Strip markdown heading/list/bold/code decoration to expose the bare content.
        bare = stripped.lstrip("#").strip()
        bare = re.sub(r"^[-*]\s*", "", bare)
        bare = bare.strip("*`").strip()
        if _UNCONFIRMED_MARKER_RE.fullmatch(bare):
            return stripped
    return None


def verify_spec_confirmed(text: str, phase: str) -> None:
    marker_line = _unconfirmed_marker_hit(text)
    if marker_line is not None:
        raise SpecVerificationError(
            f"REFUSED: shaped-design spec is marked UNCONFIRMED -- DO NOT CUT: {marker_line!r}"
        )

    dispositions = find_findings_table(text)
    if dispositions is None:
        raise SpecVerificationError(
            "no findings table found: a critical review is mandatory; its absence must not pass silently"
        )

    empty_rows = [idx + 1 for idx, cell in enumerate(dispositions) if cell.strip() == ""]
    if empty_rows:
        raise SpecVerificationError(
            f"findings table has empty Disposition cell(s) at data row(s) {empty_rows}"
        )

    if phase == "review":
        return

    fields = parse_confirmation(text)
    errors = []
    if fields["status"] != "CONFIRMED":
        errors.append(f"Status is not CONFIRMED (found {fields['status']!r})")
    if not fields["confirmed_by"]:
        errors.append("Confirmed by is missing or empty")
    if not fields["date"]:
        errors.append("Date is missing or empty")
    if errors:
        raise SpecVerificationError("; ".join(errors))


def resolve_target(target: str, root: Path) -> Path:
    """Resolve the CLI target: a path if it exists, else a work-id form."""
    path = Path(target)
    if path.is_file():
        return path
    work_id_path = root / ".agent-work" / target / "DESIGN_SPEC.md"
    if work_id_path.is_file():
        return work_id_path
    raise SpecVerificationError(
        f"spec not found: neither a file at {path} nor a work-id spec at {work_id_path}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="path to DESIGN_SPEC.md, or a work-id")
    parser.add_argument("--root", default=".", type=Path, help="project root (for the work-id form)")
    parser.add_argument("--phase", choices=("review", "confirm"), default="confirm")
    args = parser.parse_args(argv)

    try:
        path = resolve_target(args.target, args.root)
        text = path.read_text(encoding="utf-8")
        verify_spec_confirmed(text, args.phase)
    except SpecVerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"spec confirmation ok ({args.phase}): {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
