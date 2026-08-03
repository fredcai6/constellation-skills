"""PROTOTYPE (throwaway) -- exc-6 harness.

One command to run:

    python proto_governor/proto_bind.py claim   --work-id <id>
    python proto_governor/proto_bind.py gauge   --work-id <id>
    python proto_governor/proto_bind.py release --work-id <id>
    python proto_governor/proto_bind.py dump

Stands in for the two production writers so the identity question can be
answered without wiring any hook:
  * `claim`/`release` do what spine_rail.py's PostToolUse binding writer does,
    but keyed on the ACTING AGENT's identity instead of the shared session_id.
  * `gauge` does what gauge_writer_hook.py does, but reads the acting agent's
    OWN transcript.

Per prototyper doctrine every subcommand dumps the COMPLETE binding state,
not a summary.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_identity import resolve, read_fill  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BINDING = ROOT / ".agent-work" / ".proto-binding.json"


def _load() -> dict:
    try:
        return json.loads(BINDING.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    BINDING.parent.mkdir(parents=True, exist_ok=True)
    tmp = BINDING.with_name(BINDING.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, BINDING)


def _probe() -> str:
    """A distinctive slice of our own command line, as it appears verbatim in
    the acting agent's transcript tool_use record."""
    return "proto_bind.py " + " ".join(sys.argv[1:])


def _identity(args):
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return sid, resolve(
        session_id=sid,
        project_dir=Path(args.project_dir),
        probe=_probe(),
        declared_agent_id=args.agent_id or "",
        structured=(args.variant != "a"),
    )


def _dump_state(note: str) -> None:
    data = _load()
    print(f"\n===== FULL BINDING STATE ({note}) =====")
    print(json.dumps(data, indent=2))
    print(f"distinct identity keys: {len(data)}")
    for key, entry in data.items():
        print(f"  {key}  -> {len(entry)} binding(s): {list(entry)}")
    print("=" * 46)


def cmd_claim(args) -> int:
    sid, ident = _identity(args)
    if ident is None:
        print("UNRESOLVED identity -- refusing to bind (skip-on-uncertainty)")
        _dump_state("after unresolved claim")
        return 1
    print("RESOLVED IDENTITY:", json.dumps(ident.as_dict(), indent=2))
    data = _load()
    entry = dict(data.get(ident.identity_key) or {})
    entry[args.work_id] = {
        "work_id": args.work_id,
        "spine": str(ROOT / ".agent-work" / args.work_id / "spine.json"),
        "session_id": sid,
        "agent_id": ident.agent_id,
        "method": ident.method,
    }
    data[ident.identity_key] = entry
    _save(data)
    (ROOT / ".agent-work" / args.work_id).mkdir(parents=True, exist_ok=True)
    print(f"CLAIMED {args.work_id} under identity_key={ident.identity_key}")
    _dump_state("after claim")
    return 0


def cmd_gauge(args) -> int:
    sid, ident = _identity(args)
    if ident is None:
        print("UNRESOLVED identity -- writing no gauge (skip-on-uncertainty)")
        return 1
    data = _load()
    bound = data.get(ident.identity_key) or {}
    if len(bound) != 1:
        print(f"AMBIGUOUS/absent: identity holds {len(bound)} bindings -- no write")
        return 1
    work_id = next(iter(bound))
    record = read_fill(ident)
    if record is None:
        print("no usable usage record -- no write")
        return 1
    out = ROOT / ".agent-work" / work_id / "gauge.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"GAUGE WRITTEN for identity_key={ident.identity_key}")
    print(f"  path : {out}")
    print(f"  record: {json.dumps(record)}")
    return 0


def cmd_release(args) -> int:
    sid, ident = _identity(args)
    if ident is None:
        print("UNRESOLVED identity -- cannot release")
        _dump_state("after unresolved release")
        return 1
    data = _load()
    entry = dict(data.get(ident.identity_key) or {})
    removed = entry.pop(args.work_id, None)
    if entry:
        data[ident.identity_key] = entry
    else:
        data.pop(ident.identity_key, None)
    _save(data)
    print(f"RELEASED {args.work_id} (was bound: {removed is not None}) "
          f"under identity_key={ident.identity_key}")
    _dump_state("after release")
    return 0


def cmd_dump(args) -> int:
    _dump_state("on demand")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["claim", "gauge", "release", "dump"])
    ap.add_argument("--work-id", default="")
    ap.add_argument("--agent-id", default="")
    ap.add_argument("--variant", choices=["a", "b"], default="b",
                    help="a = naive substring probe (measured to fail); "
                         "b = structured Bash tool_use match (default)")
    ap.add_argument("--project-dir", default="C:/Programs/constellation-skills")
    args = ap.parse_args()
    return {
        "claim": cmd_claim,
        "gauge": cmd_gauge,
        "release": cmd_release,
        "dump": cmd_dump,
    }[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
