#!/usr/bin/env python
"""Refuse to advance a gate whose declared `[[gate.dispatch]]` (LIFECYCLE_CONTRACT.md
section 5) was not actually recorded.

`scripts/generate_spine.py` injects one `command`-kind postcondition per declared
dispatch entry, and this is the oracle it shells out to: it reads `crew-runs.json`
(via `scripts/run_crew.py`'s OWN registry loading and `is_abandoned` -- never a
second parse of that JSON) and refuses unless a non-abandoned entry for the
declared gate/role carries the declared parent and model.

    python scripts/verify_declared_dispatch.py --root . --work-id <id> \
        --gate <gate-id> --role <role> --parent <parent> --model <model>

Exit 0 and a message naming the matching entry when satisfied; exit 1 and a
message naming the offending or missing entry otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_crew import is_abandoned, load_registry, registry_path  # noqa: E402


def find_candidates(entries: list[dict], *, gate: str, role: str) -> list[dict]:
    """Every NON-ABANDONED entry for this gate/role, in registry order.
    PURE -- no filesystem, no subprocess."""
    return [
        e for e in entries
        if e.get("gate") == gate and e.get("role") == role and not is_abandoned(e)
    ]


def check_declared_dispatch(entries: list[dict], *, gate: str, role: str, parent: str, model: str) -> tuple[bool, str]:
    """Whether some non-abandoned entry for `gate`/`role` carries the declared
    `parent` and `model`, plus a human-readable message naming the matching
    entry (satisfied) or the offending/missing entries (not satisfied). PURE."""
    candidates = find_candidates(entries, gate=gate, role=role)
    if not candidates:
        return False, (
            f"no non-abandoned crew-runs.json entry for gate={gate!r} role={role!r} -- "
            f"the declared dispatch (parent={parent!r}, model={model!r}) was never recorded"
        )
    for entry in candidates:
        if entry.get("parent") == parent and entry.get("model") == model:
            name = entry.get("crew_id") or entry.get("session_name") or "?"
            return True, f"{name} matches declared dispatch (gate={gate!r} role={role!r} parent={parent!r} model={model!r})"
    mismatches = "; ".join(
        f"{e.get('crew_id') or e.get('session_name') or '?'} "
        f"(parent={e.get('parent')!r}, model={e.get('model')!r})"
        for e in candidates
    )
    return False, (
        f"gate={gate!r} role={role!r} declared parent={parent!r} model={model!r}, but no "
        f"non-abandoned entry matches -- found: {mismatches}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--parent", required=True)
    parser.add_argument("--model", required=True)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    entries = load_registry(registry_path(args.work_id, root))
    ok, message = check_declared_dispatch(
        entries, gate=args.gate, role=args.role, parent=args.parent, model=args.model,
    )
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
