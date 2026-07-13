#!/usr/bin/env python
"""Refuse a malformed cut-work issue set — the constellation-to-issues RAIL.

This is the single mechanically-enforced rail for the `constellation-to-issues`
skill (DESIGN_SPEC Section A). The skill emits ONE tracker-agnostic manifest
(the issue-set artifact); this script is the gate that manifest must clear
before the skill may emit or file it. `file_issue_set.py` runs this first and
refuses to file anything if it fails, so a malformed set can never reach a
tracker.

It exits NON-ZERO (and raises `IssueSetError`) on any of the four locked
refusals, plus the structural basics a well-formed manifest needs:

  1. UNCONFIRMED SPEC — re-runs the existing verify_spec_confirmed.py confirm
     gate against the spec the manifest was cut from. "No work is cut from an
     unconfirmed design" is enforced here, not merely asserted in prose.
  2. NO DEPENDENCY EDGE — an issue set with zero `blocks` edges across every
     issue is refused (a wave-ordered epic needs at least one edge to order).
     A `blocks` target that names no known issue id is also refused (a dangling
     edge would break the downstream topological sort).
  3. UNTYPED ISSUE — every issue must be typed HITL or AFK; an untyped issue,
     or one carrying any other type value, is refused.
  4. HITL WITHOUT REASON — a HITL issue must carry a non-empty `hitl_reason`.

Everything else about the cut (coverage vs spec, invented scope, whether a
risky AFK should be HITL) is the INDEPENDENT reviewer's judgment — deliberately
NOT gated here (DESIGN_SPEC Section A: the manifest is evidence, never a review
gate; well-formed != well-cut). Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Resolve the sibling verify_spec_confirmed module whether this file is run as a
# script (its dir is already sys.path[0]) or imported by a test loader (which
# does not add scripts/ to the path). Both scripts are bundled side-by-side into
# the installed skill's scripts/ dir, so this import holds there too.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_spec_confirmed import verify_spec_confirmed, SpecVerificationError

VALID_TYPES = ("HITL", "AFK")


class IssueSetError(Exception):
    """Raised when the issue-set manifest is malformed — the rail's refusal."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IssueSetError(message)


def verify_manifest_shape(manifest: object) -> dict:
    """Structural basics of the one manifest: an epic with a title and a
    non-empty list of issues, each with a unique id and a title."""
    _require(isinstance(manifest, dict), "manifest is not a JSON object")
    assert isinstance(manifest, dict)

    epic = manifest.get("epic")
    _require(isinstance(epic, dict), "manifest.epic missing or not an object")
    assert isinstance(epic, dict)
    _require(bool(str(epic.get("title", "")).strip()), "manifest.epic.title is missing or empty")

    issues = manifest.get("issues")
    _require(isinstance(issues, list) and len(issues) > 0, "manifest.issues missing or empty")
    assert isinstance(issues, list)

    seen: set[str] = set()
    for idx, issue in enumerate(issues):
        _require(isinstance(issue, dict), f"issue #{idx} is not an object")
        iid = str(issue.get("id", "")).strip()
        _require(bool(iid), f"issue #{idx} is missing an id")
        _require(iid not in seen, f"duplicate issue id {iid!r}")
        seen.add(iid)
        _require(bool(str(issue.get("title", "")).strip()), f"issue {iid!r} is missing a title")
    return manifest


def verify_edges(manifest: dict) -> None:
    """Rule 2: at least one dependency edge across the set, and every edge
    target names a known issue id (no dangling edge)."""
    issues = manifest["issues"]
    ids = {str(i["id"]).strip() for i in issues}
    total_edges = 0
    for issue in issues:
        blocks = issue.get("blocks", [])
        _require(isinstance(blocks, list), f"issue {issue['id']!r}: blocks must be a list")
        for target in blocks:
            target = str(target).strip()
            _require(
                target in ids,
                f"issue {issue['id']!r}: blocks target {target!r} names no known issue id",
            )
            total_edges += 1
    _require(
        total_edges > 0,
        "issue set has no dependency edges (blocks); a wave-ordered epic needs at least one",
    )


def verify_types(manifest: dict) -> None:
    """Rules 3 and 4: every issue typed HITL/AFK; HITL requires a hitl_reason."""
    for issue in manifest["issues"]:
        iid = issue["id"]
        itype = issue.get("type")
        _require(
            itype in VALID_TYPES,
            f"issue {iid!r} is untyped or invalid: type={itype!r}, expected one of {'/'.join(VALID_TYPES)}",
        )
        if itype == "HITL":
            _require(
                bool(str(issue.get("hitl_reason", "")).strip()),
                f"issue {iid!r} is HITL but carries no hitl_reason",
            )


def verify_issue_set(manifest: object, spec_text: str) -> None:
    """Raise IssueSetError on any malformed condition; return None if the set is
    well-formed. `spec_text` is the DESIGN_SPEC the set was cut from.

    Order is deliberate: the spec-confirmation gate (rule 1) runs first — an
    unconfirmed spec is refused before the manifest is even inspected.
    """
    try:
        verify_spec_confirmed(spec_text, "confirm")
    except SpecVerificationError as exc:
        raise IssueSetError(f"spec is not confirmed — refusing to cut: {exc}") from exc

    manifest = verify_manifest_shape(manifest)
    verify_edges(manifest)
    verify_types(manifest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="path to the issue-set manifest JSON")
    parser.add_argument("--spec", required=True, help="path to the DESIGN_SPEC.md the set was cut from")
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED: cannot read manifest: {exc}", file=sys.stderr)
        return 1
    try:
        spec_text = Path(args.spec).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"REFUSED: cannot read spec: {exc}", file=sys.stderr)
        return 1

    try:
        verify_issue_set(manifest, spec_text)
    except IssueSetError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    print(f"issue set ok: {args.manifest} ({len(manifest['issues'])} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
