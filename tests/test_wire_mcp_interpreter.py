"""Tests for scripts/wire_mcp_interpreter.py (M2 job 2, widened M2 g4-repair).

`.mcp.json` is git-tracked and must be launchable AS COMMITTED (#539): it now
carries a bare interpreter name (`python3`), not the unresolvable
`<python-interpreter>` placeholder. This script is the one write path that
resolves any rewritable command -- the placeholder, or a bare
`python`/`python3`/`py` name -- to a real, per-machine interpreter, reusing
install_constellation.py's `resolve_interpreter()` rather than a second probe.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
WIRE = ROOT / "scripts" / "wire_mcp_interpreter.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_wire():
    return load_module("wire_mcp_interpreter", WIRE)


def write_mcp_config(path: Path, command: str) -> None:
    path.write_text(json.dumps({
        "mcpServers": {
            "spine": {
                "command": command,
                "args": ["scripts/mcp_spine_server.py"],
                "env": {"SPINE_FILE": "${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"},
            }
        }
    }, indent=2) + "\n", encoding="utf-8")


class RewriteMcpConfigInterpreterTests(unittest.TestCase):
    def test_rewrites_placeholder_command_to_resolved_interpreter(self):
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, wire.MCP_INTERPRETER_PLACEHOLDER)
            interpreter = wire._install.InterpreterResolution("python", ("py", "python3", "python"), "probe")

            changed = wire.rewrite_mcp_config_interpreter(config_path, interpreter)

            self.assertTrue(changed)
            written = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual("python", written["mcpServers"]["spine"]["command"])

    def test_rewrites_a_bare_name_that_differs_from_the_resolved_interpreter(self):
        # The bug this gate exists to fix: a committed bare name (`python3`,
        # `python`, `py`) is not the placeholder, but it is still a name this
        # run may need to resolve to something else on this machine.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, "python3")
            interpreter = wire._install.InterpreterResolution("py", ("py", "python3", "python"), "probe")

            changed = wire.rewrite_mcp_config_interpreter(config_path, interpreter)

            self.assertTrue(changed)
            written = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual("py", written["mcpServers"]["spine"]["command"])

    def test_is_a_noop_when_the_bare_name_already_matches_the_resolved_interpreter(self):
        # Already-correct is a true no-op: rewriting a value onto itself must
        # not report `changed` just because the command was eligible.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, "python")
            before = config_path.read_text(encoding="utf-8")
            interpreter = wire._install.InterpreterResolution("python", ("py", "python3", "python"), "probe")

            changed = wire.rewrite_mcp_config_interpreter(config_path, interpreter)

            self.assertFalse(changed)
            self.assertEqual(before, config_path.read_text(encoding="utf-8"))

    def test_leaves_an_absolute_path_alone(self):
        # A caller who pinned an absolute path meant it -- stomping that is a
        # worse bug than the silent no-op this gate fixes.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, "/usr/bin/python3.12")
            before = config_path.read_text(encoding="utf-8")
            interpreter = wire._install.InterpreterResolution("python3", ("py", "python3", "python"), "probe")

            changed = wire.rewrite_mcp_config_interpreter(config_path, interpreter)

            self.assertFalse(changed)
            self.assertEqual(before, config_path.read_text(encoding="utf-8"))

    def test_leaves_a_different_program_name_alone(self):
        # Not ours to guess at: a wrapper script or another interpreter is a
        # different program, not a bare Python name.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, "uv")
            before = config_path.read_text(encoding="utf-8")
            interpreter = wire._install.InterpreterResolution("python3", ("py", "python3", "python"), "probe")

            changed = wire.rewrite_mcp_config_interpreter(config_path, interpreter)

            self.assertFalse(changed)
            self.assertEqual(before, config_path.read_text(encoding="utf-8"))


class MainHardStopTests(unittest.TestCase):
    def test_hard_stops_and_leaves_the_file_untouched_when_nothing_probes(self):
        # Exercise on a PATH where NEITHER py, python3 NOR python answers --
        # the Windows-shaped failure mode (#539). No fallback name may be
        # stamped; the file must be byte-identical to before the attempt.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, wire.MCP_INTERPRETER_PLACEHOLDER)
            before = config_path.read_text(encoding="utf-8")

            def always_fails(cmd, **kwargs):
                raise FileNotFoundError(f"no such candidate: {cmd[0]}")

            with mock.patch.object(wire._install.subprocess, "run", side_effect=always_fails):
                with self.assertRaises(wire._install.InstallError):
                    wire.main(["--mcp-config", str(config_path)])

            self.assertEqual(before, config_path.read_text(encoding="utf-8"))

    def test_wires_python3_when_only_python3_answers_even_lacking_pytest(self):
        # Exercise on a PATH where python3 IS present but lacks pytest (this
        # host, per #561): resolve_interpreter only ever probes `--version`,
        # never pytest-awareness, so it correctly resolves and wires whatever
        # answers -- the wiring script does not second-guess the probe.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, wire.MCP_INTERPRETER_PLACEHOLDER)

            def only_python3_answers(cmd, **kwargs):
                if cmd[0] == "python3":
                    return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")
                raise FileNotFoundError(f"no such candidate: {cmd[0]}")

            with mock.patch.object(wire._install.subprocess, "run", side_effect=only_python3_answers):
                exit_code = wire.main(["--mcp-config", str(config_path)])

            self.assertEqual(0, exit_code)
            written = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual("python3", written["mcpServers"]["spine"]["command"])

    def test_wires_python_when_python3_is_absent(self):
        # Exercise on a PATH where python3 is absent entirely (py also
        # absent) and only python answers.
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, wire.MCP_INTERPRETER_PLACEHOLDER)

            def only_python_answers(cmd, **kwargs):
                if cmd[0] == "python":
                    return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.x\n", stderr="")
                raise FileNotFoundError(f"no such candidate: {cmd[0]}")

            with mock.patch.object(wire._install.subprocess, "run", side_effect=only_python_answers):
                exit_code = wire.main(["--mcp-config", str(config_path)])

            self.assertEqual(0, exit_code)
            written = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual("python", written["mcpServers"]["spine"]["command"])


if __name__ == "__main__":
    unittest.main()
