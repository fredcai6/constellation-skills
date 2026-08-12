#!/usr/bin/env python3
"""g4b's gate check, at the path the frozen plan named.

The plan pre-committed this exact command as g4b-integrate's own postcondition,
before the instrument existed, so that the gate could not later be closed
against whatever check happened to be convenient. The instrument itself lives
with its evidence at `evidence/g4b/`; this is the frozen entry point to it.

Defaults to the ACCEPTED arm. Every arm is scoreable by passing its directory,
and two of the three deliberately REFUSE -- see evidence/g4b/MEASUREMENT.md.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARM = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "evidence" / "g4b" / "arm-mcp-3")
raise SystemExit(subprocess.run(
    [sys.executable, str(HERE / "evidence" / "g4b" / "assert_acceptance.py"), ARM]).returncode)
