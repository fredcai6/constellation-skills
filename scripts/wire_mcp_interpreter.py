"""Resolve THIS machine's Python interpreter into `.mcp.json` (M2 job 2).

`.mcp.json` is git-tracked, so by #539's ruling (see install_constellation.py's
`resolve_interpreter`) it may never carry a literal interpreter name: no single
name works on every platform, and stamping one anyway just moves the failure
somewhere later and harder to trace. The committed file therefore carries
`MCP_INTERPRETER_PLACEHOLDER` as each server's `command`; this script is the one
write path that resolves it to a real, working interpreter for the machine it
runs on -- reusing `install_constellation.py`'s `resolve_interpreter()` (the
same probe hook wiring already uses for #539/#540) rather than a second one.
Hard-stops (propagates `InstallError`) when nothing probes; never stamps a
known-broken name.

Run once per machine, in a checkout of this repo:

    python scripts/wire_mcp_interpreter.py
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DEFAULT_MCP_CONFIG = REPO_ROOT / ".mcp.json"


def _load_install_constellation():
    if "install_constellation" in sys.modules:
        return sys.modules["install_constellation"]
    spec = importlib.util.spec_from_file_location(
        "install_constellation", HERE / "install_constellation.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["install_constellation"] = module
    spec.loader.exec_module(module)
    return module


_install = _load_install_constellation()

# Single source of truth lives on install_constellation.py (M2 g3-rework),
# which also calls it automatically from its own CLI entry point. Aliased
# here, never redefined, so this standalone script and the installer's
# automatic wiring can never drift apart.
MCP_INTERPRETER_PLACEHOLDER = _install.MCP_INTERPRETER_PLACEHOLDER
rewrite_mcp_config_interpreter = _install.rewrite_mcp_config_interpreter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mcp-config", type=Path, default=DEFAULT_MCP_CONFIG,
        help="path to the .mcp.json to wire (default: repo root .mcp.json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # RAISES InstallError when no candidate answers (#539 hard-stop) -- never
    # caught here, so a bad host fails visibly instead of writing a guess.
    interpreter = _install.resolve_interpreter()
    changed = rewrite_mcp_config_interpreter(args.mcp_config, interpreter)
    if changed:
        print(f"wired {args.mcp_config}: command -> {interpreter.interpreter!r} (probed)")
    else:
        print(f"{args.mcp_config}: no {MCP_INTERPRETER_PLACEHOLDER!r} command found; nothing to wire")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except _install.InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
