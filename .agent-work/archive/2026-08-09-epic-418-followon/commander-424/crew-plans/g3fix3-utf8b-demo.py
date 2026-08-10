#!/usr/bin/env python3
"""One-off demonstration for g3fix3 (issue #424, workstream F): prove that
pinning `cli_current_text()`'s subprocess.run to `encoding="utf-8"` is what
matters, by showing the CLI arm's real, unmodified wire bytes decode WRONG
under a non-UTF-8 platform default (BEFORE / simulates the unfixed code path
on an unconfigured Windows box) and RIGHT under an explicit UTF-8 pin (AFTER
/ what the fix now does), compared byte-for-byte against the MCP arm (already
correct, fixed by a prior crew).

Not a permanent test -- not added to tests/test_mcp_imperative_equivalence.py
or any other tracked test file. Run manually, twice: once against the
still-unfixed cli_current_text() (BEFORE only matters -- AFTER is expected to
already match on this box since the real subprocess.run() call is unaffected
here) and once after the fix landed (BEFORE still shows the hazard would have
existed; AFTER matches, confirming the fix is what removes it).

Why decode captured raw bytes directly instead of forcing the parent
process's own locale to cp1252: confirmed empirically (see m0-context) that
(a) PYTHONIOENCODING set in the CLI CHILD's env has no effect on the wire
bytes, because checklist_engine.py's own _utf8_stdio() (line ~43-55) already
reconfigures that child's stdout to UTF-8 unconditionally at import time --
before any PYTHONIOENCODING could matter; and (b) PYTHONIOENCODING set in
the PARENT's (this script's) own env has no effect on subprocess.run(text=
True)'s decode default either -- that default comes from locale.getencoding(),
which is governed by LC_ALL/LANG, not PYTHONIOENCODING. This Linux box has no
cp1252 locale installed (`locale -a` -- only C/C.utf8/POSIX/en_*.utf8), so
forcing the *real* Windows-cp1252-default scenario via env vars alone is not
possible here. Decoding the real captured bytes directly with encoding=
"cp1252" is the honest, directly-controlled stand-in: it answers the exact
question "what would an unconfigured Windows box's default decode do to
THESE bytes" without needing Windows itself -- verified locally that this
produces the literal mojibake shape pasted in the handoff's CI trace.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ENGINE = ROOT / "scripts" / "checklist_engine.py"

sys.path.insert(0, str(ROOT / "tests"))
import test_mcp_imperative_equivalence as teq  # noqa: E402


def active_line(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.startswith("ACTIVE ")]
    assert len(lines) == 1, f"expected exactly one ACTIVE line, got {lines!r}"
    return lines[0]


def main() -> int:
    gates, _ = teq.discover_gates_with_imperative()
    assert gates, "no gates discovered -- cannot demonstrate anything"
    gate = gates[0]
    print(f"Demonstration gate: {gate.template.relative_to(ROOT)}::{gate.gate_id}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        spine_path = root / "spine.json"
        teq.write_spine(spine_path, teq.build_single_gate_spine(gate))

        # CLI arm: the REAL, unmodified checklist_engine.py subprocess, same
        # invocation cli_current_text() makes -- but capture RAW bytes (no
        # text=True) so nothing decodes them yet; we control that step below.
        proc = subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(spine_path), "current"],
            capture_output=True, timeout=30,
        )
        assert proc.returncode == 0, f"CLI current failed: {proc.stderr!r}"
        raw = proc.stdout
        has_multibyte_utf8 = any(b >= 0x80 for b in raw)
        print(f"CLI raw stdout: {len(raw)} bytes, contains non-ASCII bytes: {has_multibyte_utf8}")

        # MCP arm: real, separate mcp_spine_server.py subprocess, already
        # fixed by a prior crew (test_mcp_identity.ServerInstance house
        # pattern, reused not re-implemented). This is the correct reference.
        from test_mcp_identity import ServerInstance
        SERVER = ROOT / "scripts" / "mcp_spine_server.py"
        server = ServerInstance(spine_path, "g3fix3-utf8b-demo", root, engine=ENGINE, server=SERVER)
        try:
            mcp_text = server.status_text(timeout=15)
            assert mcp_text is not None, "MCP door produced no reply"
            mcp_active = active_line(mcp_text)
            print(f"MCP  ACTIVE line (reference, correct): {mcp_active!r}")

            # BEFORE: decode the CLI's real wire bytes with cp1252 -- the
            # platform-default stand-in for an unconfigured Windows box's
            # subprocess.run(text=True) (see module docstring for why this
            # is the honest, directly-controlled proxy on a Linux box).
            before_text = raw.decode("cp1252")
            before_active = active_line(before_text)
            print(f"CLI  ACTIVE line BEFORE (cp1252 decode -- simulated unfixed default): {before_active!r}")

            # AFTER: decode the same real wire bytes with the fix's explicit
            # encoding="utf-8".
            after_text = raw.decode("utf-8")
            after_active = active_line(after_text)
            print(f"CLI  ACTIVE line AFTER  (utf-8 decode -- what the fix pins): {after_active!r}")

            before_matches = before_active == mcp_active
            after_matches = after_active == mcp_active
            print(f"\nBEFORE matches MCP: {before_matches}")
            print(f"AFTER  matches MCP: {after_matches}")

            if before_matches:
                print("UNEXPECTED: BEFORE matched -- cp1252 decode did not diverge for this gate's text "
                      "(no non-ASCII in this imperative?); re-run, a different gate may be needed.")
            if not after_matches:
                print("UNEXPECTED: AFTER did not match -- the fix's utf-8 decode should always match "
                      "the MCP arm's already-utf-8 text for genuine UTF-8 wire bytes.")

            return 0 if (not before_matches and after_matches) else 1
        finally:
            server.close()


if __name__ == "__main__":
    raise SystemExit(main())
