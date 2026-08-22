"""Tests for scripts/wire_mcp_interpreter.py (M2 job 2, widened M2 g4-repair).

`.mcp.json` is git-tracked and must be launchable AS COMMITTED (#539). This
script is the one write path that resolves a rewritable command -- the
placeholder, or a bare `python`/`python3`/`py` name -- to a real, per-machine
interpreter, reusing install_constellation.py's `resolve_interpreter()` rather
than a second probe.

Two things changed when #553/#575 were closed, and both are pinned below:

1. A GIT-TRACKED target is REFUSED. A probed interpreter is a fact about one
   machine; a tracked `.mcp.json` ships. Writing one into the other is the
   field defect that reopened this (an install run rewrote the repo's tracked
   `python3` to `py`, which on that host was the operator's own
   `~/.local/bin/py` shim). The refusal existed once on PR #555 and was lost
   when that branch was closed as superseded rather than repealed.
2. The portable `${CONSTELLATION_PYTHON:-python3}` form is NOT rewritable --
   it is already machine-neutral and launchable, so resolving it to this
   host's name would downgrade it. This repo's own `.mcp.json` now carries
   that form, which makes wiring a no-op here BY CONSTRUCTION as well as by
   the tracked refusal -- belt and braces, deliberately.
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


class GitTrackedRefusalTests(unittest.TestCase):
    """The guard restored from PR #555. `is_git_tracked` runs `git ls-files` for
    real, so these build actual repos rather than mocking the predicate -- the
    thing under test is precisely whether the write path consults it."""

    def _repo(self, tmp: str, *, track: bool) -> Path:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "t@e.st"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
        config_path = root / ".mcp.json"
        write_mcp_config(config_path, "python3")
        if track:
            subprocess.run(["git", "add", ".mcp.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "add"], cwd=root, check=True)
        return config_path

    def test_refuses_to_wire_a_git_tracked_mcp_json(self):
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = self._repo(tmp, track=True)
            before = config_path.read_bytes()
            interpreter = wire._install.InterpreterResolution("py", ("py",), "probe")

            with self.assertRaises(wire._install.InstallError) as ctx:
                wire.rewrite_mcp_config_interpreter(config_path, interpreter)

            self.assertIn("git-tracked", str(ctx.exception))
            self.assertEqual(before, config_path.read_bytes(),
                             "the tracked file was written anyway")

    def test_the_refusal_names_the_portable_form_so_the_caller_is_not_stranded(self):
        """A refusal that does not say what to do instead just moves the
        problem. The message must name the env-var knob."""
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = self._repo(tmp, track=True)
            interpreter = wire._install.InterpreterResolution("py", ("py",), "probe")
            with self.assertRaises(wire._install.InstallError) as ctx:
                wire.rewrite_mcp_config_interpreter(config_path, interpreter)
        self.assertIn(wire._install.MCP_INTERPRETER_ENV_VAR, str(ctx.exception))

    def test_the_same_run_wires_an_untracked_mcp_json(self):
        """The control. The guard must key on TRACKED, not on 'is in a repo' --
        otherwise it is a blanket refusal wearing a specific name."""
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = self._repo(tmp, track=False)
            interpreter = wire._install.InterpreterResolution("py", ("py",), "probe")

            self.assertTrue(wire.rewrite_mcp_config_interpreter(config_path, interpreter))

            written = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual("py", written["mcpServers"]["spine"]["command"])

    def test_this_repos_own_mcp_json_is_refused(self):
        """The field defect, end to end, against the real file. This is the
        exact call an install run makes, and it must not write."""
        wire = load_wire()
        before = (ROOT / ".mcp.json").read_bytes()
        interpreter = wire._install.InterpreterResolution("py", ("py",), "probe")
        with self.assertRaises(wire._install.InstallError):
            wire.rewrite_mcp_config_interpreter(ROOT / ".mcp.json", interpreter)
        self.assertEqual(before, (ROOT / ".mcp.json").read_bytes())


class PortableVarFormIsNotRewritableTests(unittest.TestCase):
    """`${VAR:-default}` is the answer wiring exists to produce; wiring must not
    consume it."""

    def test_the_var_form_is_not_rewritable(self):
        wire = load_wire()
        self.assertFalse(wire.is_rewritable_mcp_command("${CONSTELLATION_PYTHON:-python3}"))
        self.assertFalse(wire.is_rewritable_mcp_command("${CONSTELLATION_PYTHON:-py}"))

    def test_bare_names_and_the_placeholder_are_still_rewritable(self):
        """Control: the var-form exemption must not have blunted the predicate."""
        wire = load_wire()
        for command in ("python3", "python", "py", wire.MCP_INTERPRETER_PLACEHOLDER):
            with self.subTest(command=command):
                self.assertTrue(wire.is_rewritable_mcp_command(command))

    def test_an_untracked_config_on_the_var_form_is_left_alone(self):
        """Even where writing IS permitted, the var form survives untouched."""
        wire = load_wire()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".mcp.json"
            write_mcp_config(config_path, "${CONSTELLATION_PYTHON:-python3}")
            before = config_path.read_bytes()
            interpreter = wire._install.InterpreterResolution("py", ("py",), "probe")

            self.assertFalse(wire.rewrite_mcp_config_interpreter(config_path, interpreter))
            self.assertEqual(before, config_path.read_bytes())


class ExpandMcpVarTests(unittest.TestCase):
    """The MEASURED expansion rule (Claude Code 2.1.234). The `:-` spelling does
    NOT carry POSIX `:-` semantics: a name that is PRESENT wins even when its
    value is empty, and the default applies only when the name is ABSENT.
    Measured 3/3 reproducibly against `claude mcp get`'s health-check, and
    contrasted against a real POSIX shell, which disagrees. Pinned here because
    the difference is invisible until it silently fails to launch a door."""

    def test_default_applies_only_when_the_name_is_absent(self):
        expand = load_wire()._install.expand_mcp_var
        self.assertEqual("python3", expand("${CP:-python3}", {}))

    def test_a_present_but_empty_name_wins_over_the_default(self):
        """The trap, and the reason this is not `os.path.expandvars` or a shell
        call. POSIX `${CP:-python3}` yields `python3` here; the harness yields
        the empty string and the server does not start."""
        expand = load_wire()._install.expand_mcp_var
        self.assertEqual("", expand("${CP:-python3}", {"CP": ""}))

    def test_a_present_name_is_used(self):
        expand = load_wire()._install.expand_mcp_var
        self.assertEqual("py", expand("${CP:-python3}", {"CP": "py"}))

    def test_a_bare_reference_with_no_default_expands_to_empty_when_unset(self):
        """Not to the literal `${CP}` -- which is what `os.path.expandvars`
        would leave behind, and which would read as a launchable command."""
        expand = load_wire()._install.expand_mcp_var
        self.assertEqual("", expand("${CP}", {}))

    def test_a_plain_string_is_returned_unchanged(self):
        expand = load_wire()._install.expand_mcp_var
        self.assertEqual("python3", expand("python3", {"CP": "py"}))


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
