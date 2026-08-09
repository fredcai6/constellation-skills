#!/usr/bin/env python3
"""Generate a per-dispatch MCP config for one agent (issue #424, workstream F).

Why this exists, not just a project-scope .mcp.json (measured, MISSION_FRAME.md
"Why per-dispatch config generation"): a fresh project-scope .mcp.json is not
picked up by a live session, and on a fresh process the server sits in
'Pending approval' forever with no human present to approve it -- so it cannot
deliver the door to a cold or headless agent at all. The path that DOES work,
verified end to end against the real server:

    claude -p "<task>" --mcp-config <generated>.json --strict-mcp-config \\
        --allowedTools "mcp__<server>__<tool>"

`--strict-mcp-config` ignores all other MCP configuration (project/user scope,
any other dispatch's config), which is exactly what gives EACH agent its own
server instance rather than a shared ambient one -- the per-dispatch identity
constraint (`.mcp.json` at project scope stays the interactive-only door, see
that file's own comment).

This script emits exactly the JSON that flag consumes: one `mcpServers` entry
whose `env` block binds SPINE_FILE / SPINE_ENGINE / SPINE_SESSION -- the same
three variables mcp_spine_server.py reads at launch. SPINE_SESSION is composed
as `<session_id>#<agent_id>` so a session dispatching several concurrent
subagents against the same spine gives each one a distinguishable identity
(the engine's own --session-id is a free-text string; this is the composition
convention this door commits to, not an engine-enforced format).

No third-party dependencies; stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVER = Path(__file__).resolve().parent / "mcp_spine_server.py"
DEFAULT_ENGINE = Path(__file__).resolve().parent / "checklist_engine.py"


def build_config(
    spine_file: Path,
    session_id: str,
    agent_id: str,
    engine: Path = DEFAULT_ENGINE,
    server: Path = DEFAULT_SERVER,
    server_name: str = "spine",
    python: str = sys.executable,
) -> dict:
    """Build the --mcp-config JSON: one server entry keyed `server_name`, with
    an env block binding this one agent's ambient state. `session_id#agent_id`
    is composed into SPINE_SESSION -- see module docstring."""
    if "#" in session_id or "#" in agent_id:
        raise ValueError(
            f"session_id and agent_id must not contain '#' (it is the composition "
            f"separator): session_id={session_id!r} agent_id={agent_id!r}"
        )
    spine_session = f"{session_id}#{agent_id}"
    return {
        "mcpServers": {
            server_name: {
                "command": python,
                "args": [str(Path(server).resolve())],
                "env": {
                    "SPINE_FILE": str(Path(spine_file).resolve()),
                    "SPINE_ENGINE": str(Path(engine).resolve()),
                    "SPINE_SESSION": spine_session,
                },
            }
        }
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spine-file", required=True, help="the checklist JSON file this dispatch drives")
    p.add_argument("--session-id", required=True, help="the dispatching session's id")
    p.add_argument("--agent-id", required=True, help="this dispatch's agent id, unique within the session")
    p.add_argument("--engine", default=str(DEFAULT_ENGINE), help="path to checklist_engine.py (default: this repo's own vendored copy)")
    p.add_argument("--server", default=str(DEFAULT_SERVER), help="path to mcp_spine_server.py (default: this repo's own vendored copy)")
    p.add_argument("--server-name", default="spine", help="the mcpServers key / MCP server name (default: spine)")
    p.add_argument("--python", default=sys.executable, help="interpreter to launch the server with (default: the one running this script)")
    p.add_argument("--out", required=True, help="path to write the generated config JSON")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = build_config(
        spine_file=Path(args.spine_file),
        session_id=args.session_id,
        agent_id=args.agent_id,
        engine=Path(args.engine),
        server=Path(args.server),
        server_name=args.server_name,
        python=args.python,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
