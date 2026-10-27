"""JSON transport for the existing Constellation engine; no workflow logic lives here."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys


def handle(request: dict) -> dict:
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    for key in ("source", "file", "cwd", "sessionId", "verb"):
        if not isinstance(request.get(key), str) or not request[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    args = request.get("args", [])
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        raise ValueError("args must be an array of strings")
    if any(arg.split("=", 1)[0] in ("--file", "--session-id") for arg in args):
        raise ValueError("file and session identity are bound by the adapter")
    source = Path(request["source"]).resolve()
    script = source / "scripts" / "checklist_engine.py"
    if not script.is_file():
        raise ValueError(f"Constellation engine not found: {script}")
    os.chdir(request["cwd"])
    path = Path(request["file"]).resolve()
    spec = importlib.util.spec_from_file_location("constellation_engine", script)
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    if request["verb"] == "state":
        return {"ok": True, "output": "", "state": engine.state(engine.load(path))}
    argv = ["--file", str(path), request["verb"], *args]
    if request["verb"] != "current":
        argv.extend(["--session-id", request["sessionId"]])
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            code = engine.main(argv)
        except SystemExit as exc:
            code = exc.code
    return {"ok": code == 0, "output": output.getvalue().strip(),
            "state": engine.state(engine.load(path))}


def main() -> None:
    # Capture imports too, keeping stdout a single JSON document.
    captured = io.StringIO()
    try:
        request = json.load(sys.stdin)
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            result = handle(request)
    except Exception as exc:
        result = {"ok": False, "output": f"{type(exc).__name__}: {exc}", "state": None,
                  "error": "bridge"}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
