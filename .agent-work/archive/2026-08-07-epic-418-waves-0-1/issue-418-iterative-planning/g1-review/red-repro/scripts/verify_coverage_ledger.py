#!/usr/bin/env python
"""Verify the removability coverage ledger against the installed-externals manifest.

This is the mechanical rail behind epic-164's done-condition (#11): "superpowers +
Pocock are removable" must be *checkable*, not asserted. Before the human uninstalls
the external skills, this script proves the coverage ledger
(``docs/removability_ledger.json``) actually accounts for every installed external
(``docs/installed_externals_manifest.json``) and makes no false coverage claim.

It REFUSES (non-zero exit) when any of:
  (a) a ``new`` row (new/changed work THIS epic, the "*" rows) — or any covered row —
      names a constellation ``home_skill`` that does not exist in the corpus (a home
      that isn't really shipped is a false coverage claim);
  (b) an external in the captured installed-inventory manifest is ABSENT from the
      ledger (an unmapped external = an uncovered capability the ledger silently missed);
  (c) a ``declined`` row carries no reason (a declination with no rationale is not a
      recorded decision).

It also rejects a structurally malformed ledger (unknown status, declined row that
still names a home, non-declined row with no home). Quality of the mapping is the
independent reviewer's judgment; this rail only proves the ledger is grounded,
complete, and internally honest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_VALID_STATUS = {"new", "covered", "declined"}


class CoverageLedgerError(Exception):
    """Raised when the coverage ledger fails a mechanical rail check."""


def manifest_externals(manifest: dict) -> list[str]:
    """Flatten every installed external skill name across all sources."""
    names: list[str] = []
    for source in manifest.get("sources", {}).values():
        names.extend(source.get("skills", []))
    return names


def skill_exists(home_skill: str, skills_root: Path) -> bool:
    """A home is real iff a skill directory of that name exists in the corpus."""
    return (skills_root / home_skill).is_dir()


def verify_coverage_ledger(ledger: dict, manifest: dict, skills_root: Path) -> None:
    """Raise CoverageLedgerError on the first rail violation; return None if clean."""
    rows = ledger.get("ledger")
    if not isinstance(rows, list):
        raise CoverageLedgerError("ledger has no 'ledger' array")

    errors: list[str] = []

    # Structural + per-row checks (a) and (c).
    ledger_externals: set[str] = set()
    for row in rows:
        ext = row.get("external", "<unnamed>")
        ledger_externals.add(ext)
        status = row.get("status")
        home = row.get("home_skill")
        reason = row.get("reason")

        if status not in _VALID_STATUS:
            errors.append(f"{ext}: unknown status {status!r} (want one of {sorted(_VALID_STATUS)})")
            continue

        if status == "declined":
            # (c) a declined row must carry a reason and must NOT claim a home.
            if not (reason and str(reason).strip()):
                errors.append(f"{ext}: declined row has no reason")
            if home:
                errors.append(f"{ext}: declined row must not name a home_skill (got {home!r})")
            continue

        # status is 'new' or 'covered' -> must name a home that really exists (a).
        if not home:
            errors.append(f"{ext}: status {status!r} must name a home_skill")
            continue
        if not skill_exists(home, skills_root):
            errors.append(
                f"{ext}: {status} home_skill {home!r} does not exist under {skills_root} "
                f"(false coverage claim)"
            )

    # (b) every installed external must appear in the ledger.
    missing = [name for name in manifest_externals(manifest) if name not in ledger_externals]
    if missing:
        errors.append(f"installed externals absent from ledger: {sorted(set(missing))}")

    if errors:
        raise CoverageLedgerError("REFUSED: coverage ledger failed:\n  - " + "\n  - ".join(errors))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=repo_root / "docs" / "removability_ledger.json")
    parser.add_argument(
        "--manifest", type=Path, default=repo_root / "docs" / "installed_externals_manifest.json"
    )
    parser.add_argument("--skills-root", type=Path, default=repo_root / "skills")
    args = parser.parse_args(argv)

    try:
        ledger = _load_json(args.ledger)
        manifest = _load_json(args.manifest)
        verify_coverage_ledger(ledger, manifest, args.skills_root)
    except (CoverageLedgerError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    n_ext = len(manifest_externals(manifest))
    n_new = sum(1 for r in ledger["ledger"] if r.get("status") == "new")
    n_declined = sum(1 for r in ledger["ledger"] if r.get("status") == "declined")
    print(
        f"coverage ledger ok: {n_ext} installed externals all mapped "
        f"({n_new} new/*, {n_declined} declined); every new/covered home exists"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
