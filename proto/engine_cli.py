#!/usr/bin/env python3
"""Transparent logging pass-through to the checklist engine's CLI door.

Identical surface, identical stdout/stderr, identical exit code -- the only
addition is one JSONL line per call so the CLI arm is counted exactly the same
way the MCP arm is (the MCP server logs its own calls). Without this the CLI
arm's exit codes would have to be scraped out of a model transcript.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path

ENGINE = Path(os.environ["SPINE_ENGINE"]).resolve()
CALLLOG = Path(os.environ["SPINE_CALLLOG"])
sys.path.insert(0, str(ENGINE.parent))
import checklist_engine  # noqa: E402

argv = sys.argv[1:]
out, err = io.StringIO(), io.StringIO()
try:
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = checklist_engine.main(argv)
except SystemExit as exc:
    code = int(exc.code or 0)
except Exception as exc:  # noqa: BLE001
    code = 1
    err.write(f"{type(exc).__name__}: {exc}")

verb = next((a for a in argv if not a.startswith("-")), "?")
with CALLLOG.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps({"verb": verb, "argv": argv, "code": code,
                         "stdout": out.getvalue(), "stderr": err.getvalue()},
                        ensure_ascii=False) + "\n")

sys.stdout.write(out.getvalue())
sys.stderr.write(err.getvalue())
sys.exit(code)
