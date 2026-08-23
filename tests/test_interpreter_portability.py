import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
INSTALLER = ROOT / "scripts" / "install_constellation.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("install_constellation", INSTALLER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _rewritable_suffixes() -> set[str]:
    return load_installer().REWRITABLE_TEXT_SUFFIXES


def _tracked_claude_settings_files() -> list[Path]:
    """Every git-tracked file under `.claude/` -- today just settings.json, but
    discovered rather than hard-coded so a future settings.local.json-alike
    that gets committed is picked up automatically."""
    result = subprocess.run(
        ["git", "ls-files", ".claude"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=10, check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


# --------------------------------------------------------------------------- #
# Part 1: shipped skill text may use `py` as a NOUN (naming the launcher) but
# never as a command an agent is told to run -- the portable convention there
# is `python <skill-dir>/...`, which the installer rewrites at install time
# (installed_path_replacements()). `py <script>` matches no rewrite token and
# ships verbatim, which is what broke off Windows.
#
# Covers three command-position shapes, not just an inline backtick starting
# the whole span: an inline backtick (`py scripts/x.py`), a fenced code block
# (```bash\npy scripts/x.py\n```, used by 17+ skill files), and a chained
# command (`cd foo && py scripts/x.py`) -- `py` after `&&`/`||`/`;`/`|` is
# still a command being run, not an argument. Also covers a raw JSON
# `"command"` field (spine/check postconditions), and the `py.exe` spelling.
# --------------------------------------------------------------------------- #

# A `py`/`py.exe` token used as a command: not preceded or followed by an
# identifier character, `.`, or `-` (so it never matches `python`, `python3`,
# or `some-py-thing`).
_PY_WORD = r"py(?:\.exe)?(?![\w./-])"

_BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")
_FENCED_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
_CHAIN_SPLIT_RE = re.compile(r"&&|\|\||[;|]")
_LEADING_PY_COMMAND_RE = re.compile(rf"^{_PY_WORD}\s+\S")
_JSON_COMMAND_PY_RE = re.compile(rf'"command"\s*:\s*"{_PY_WORD}(?=[\s"])')

# Deliberately empty: skills/_shared/windows.md §4 used to document `py` as
# "the portable form" via `py scripts/some_script.py` -- that doctrine was
# ITSELF the generator of the 8 defects this test guards against, so it was
# reworded (the portable form is `python <skill-dir>/...`; `py` is Windows-
# only) rather than carrying a permanent exception for it. Kept as a named,
# empty set -- not deleted -- so a genuinely new, narrow prose exception has
# an obvious place to go without re-deriving this reasoning, and so this
# comment stays next to the mechanism it explains.
_ALLOWED_SPANS: frozenset[tuple[str, str]] = frozenset()


def _command_candidates(span: str) -> list[str]:
    """`span` split on shell chain operators (&&, ||, ;, |), trimmed. A
    command in position 2+ of a chain is still a command being invoked, not
    an argument to the first one."""
    return [piece.strip() for piece in _CHAIN_SPLIT_RE.split(span) if piece.strip()]


def find_py_launcher_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every `py <command>` literal used as a command in `text` -- inline
    backtick, fenced code block, or raw JSON `"command"` field -- this is the
    skills/-corpus check, where `python <skill-dir>/...` is the correct,
    EXPECTED form and must not trip this), minus any documented exception."""
    violations: list[tuple[str, str]] = []

    fenced_blocks = _FENCED_BLOCK_RE.findall(text)
    text_sans_fences = _FENCED_BLOCK_RE.sub("", text)

    candidate_spans = list(_BACKTICK_SPAN_RE.findall(text_sans_fences))
    for block in fenced_blocks:
        candidate_spans.extend(block.splitlines())

    for span in candidate_spans:
        for candidate in _command_candidates(span):
            if _LEADING_PY_COMMAND_RE.match(candidate) and (rel_path, candidate) not in _ALLOWED_SPANS:
                violations.append((rel_path, candidate))

    for match in _JSON_COMMAND_PY_RE.finditer(text):
        if (rel_path, match.group(0)) not in _ALLOWED_SPANS:
            violations.append((rel_path, match.group(0)))

    return violations


# --------------------------------------------------------------------------- #
# Part 2: a git-tracked settings file is never install-rewritten AND is
# shared, unmodified, across every contributor's OS. Unlike skills/ text (where
# `python <skill-dir>/...` is a valid, install-rewritten convention),
# `resolve_interpreter()`'s probe-once-per-run/pin-once model has no analogue
# for a value baked into a file committed once and read on every platform
# forever -- a BARE `python3` is exactly as wrong on stock Windows (which
# ships `python`/`py`, not `python3` -- python.org's installer doesn't add
# `python3.exe`, and Windows' own `python3.exe` App Execution Alias just opens
# the Store) as a bare `py` was wrong on Linux/macOS.
#
# #651 answered this by naming NONE at all -- invoking the hook scripts
# directly by their `#!/usr/bin/env python3` shebang. The owner's #539/#560
# ruling ("I don't buy that anti-tamper for the python executable is
# necessary at all ... is there a simplification we can make?") replaced that
# design: the tracked file now names an interpreter EXPLICITLY, but always
# wrapped as `${CONSTELLATION_PYTHON:-python3}` (see
# `install_constellation.MCP_INTERPRETER_ENV_VAR`, `.mcp.json`'s identical
# convention) rather than a bare literal. A real POSIX shell (pinned via
# `"shell": "bash"`, Part 4 below) resolves that to `python3` when
# `CONSTELLATION_PYTHON` is unset and to the override otherwise -- so it is
# safe on every contributor's OS the same way the shebang-only form was, but
# without depending on the file's execute bit or a clean LF shebang surviving
# checkout (the two things Part 3 used to guard, retired below). What this
# Part still guards is narrower than before: not "no interpreter", but "no
# BARE, unwrapped interpreter" -- the one shape that is NOT safe to commit,
# because it pins ONE platform's spelling into a file every platform reads.
# --------------------------------------------------------------------------- #

# Matches a JSON `"command"` field whose value NAMES a BARE interpreter as its
# first token -- shell-form ("python3 \"...\" args") or exec-form's bare
# ("command": "py") -- covering every member of
# install_constellation.py's own INTERPRETER_CANDIDATES plus bare `python`.
# Deliberately anchored to the START of the value: `${CONSTELLATION_PYTHON:-
# python3}` also contains the substring "python3", but not as the value's
# first token, so it is the safe wrapped form this regex must NOT flag (see
# the self-test below).
_TRACKED_SETTINGS_INTERPRETER_RE = re.compile(
    r'"command"\s*:\s*"\s*(?:py|python3|python)(?![\w./-])'
)


def find_named_interpreter_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every JSON hook `"command"` field in `text` that names a BARE,
    platform-specific interpreter (`py`, `python3`, or `python`) as its
    executable -- i.e. as the value's own first token, not wrapped in
    `${CONSTELLATION_PYTHON:-...}` -- as (rel_path, offending snippet) pairs.
    Scanned as raw text (not JSON-parsed) so a malformed file still gets
    checked."""
    return [(rel_path, m.group(0)) for m in _TRACKED_SETTINGS_INTERPRETER_RE.finditer(text)]


class TrackedSettingsInterpreterTests(unittest.TestCase):
    """Guards the CLASS: a git-tracked settings file is read, unmodified, on
    every contributor's platform, so it may never name a BARE, platform-
    specific interpreter (`py`, `python`, or `python3`) as a hook command --
    not just `py`. There is no install-time rewrite for this file at all, and
    no single static bare name is safe on both Windows and POSIX. Naming an
    interpreter at all is fine -- expected, since #539/#560 -- as long as it
    is wrapped in the portable `${CONSTELLATION_PYTHON:-<default>}` override."""

    def test_no_bare_interpreter_named_in_tracked_claude_settings(self):
        files = _tracked_claude_settings_files()
        # Guards against the check going vacuously green: an empty file list
        # makes `assertEqual(violations, [])` pass trivially without ever
        # having scanned anything -- the exact inert-detector shape the
        # self-tests below exist to catch, one level up (discovery, not
        # matching).
        self.assertTrue(
            files,
            "no tracked .claude/ files found -- file discovery is broken, which makes "
            "this check impossible to fail",
        )
        violations: list[tuple[str, str]] = []
        for path in files:
            rel_path = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            violations.extend(find_named_interpreter_violations(text, rel_path))
        self.assertEqual(
            violations, [],
            f"A tracked .claude/ settings file names a BARE platform-specific "
            f"interpreter (py/python/python3) as a hook command. This file ships "
            f"unmodified to every contributor's OS with no install-time rewrite -- no "
            f"single bare interpreter name is safe here (python.org's Windows "
            f"installer provides `python`/`py`, not `python3`; POSIX commonly "
            f"provides only `python3`, not bare `python`). Name it through the "
            f"portable ${{CONSTELLATION_PYTHON:-<default>}} override instead (see "
            f"install_constellation.build_hook_command): {{violations}}",
        )

    def test_detector_actually_fires_on_a_constructed_violation(self):
        """Self-test: proves the regex is live against synthetic text shaped
        like each of the three ways this defect has actually shipped."""
        for bad_interpreter in ("py", "python", "python3"):
            command_json = (
                '{"command": "%s \\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" '
                'Stop"}' % bad_interpreter
            )
            self.assertEqual(
                find_named_interpreter_violations(command_json, ".claude/settings.json"),
                [(".claude/settings.json", f'"command": "{bad_interpreter}')],
                f"detector failed to fire on a hardcoded {bad_interpreter!r} interpreter",
            )

        # An exec-form bare interpreter name (no shell string) must also fire.
        exec_form_json = '{"command": "py", "args": ["${CLAUDE_PROJECT_DIR}/x.py"]}'
        self.assertEqual(
            find_named_interpreter_violations(exec_form_json, ".claude/settings.json"),
            [(".claude/settings.json", '"command": "py')],
        )

        # And confirms the ACTUALLY-SHIPPED form -- the portable
        # `${CONSTELLATION_PYTHON:-python3}` wrapper -- never trips it, even
        # though "python3" appears in the string: it is not the value's first
        # token.
        wrapped_form_json = (
            '{"command": "${CONSTELLATION_PYTHON:-python3} '
            '\\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop"}'
        )
        self.assertEqual(
            find_named_interpreter_violations(wrapped_form_json, ".claude/settings.json"),
            [],
        )

        # A bare quoted script path with no interpreter at all (the retired
        # #651 shebang-only form) is also still safe, though no longer shipped.
        shebang_form_json = (
            '{"command": "\\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop"}'
        )
        self.assertEqual(
            find_named_interpreter_violations(shebang_form_json, ".claude/settings.json"),
            [],
        )

    def test_detector_would_not_go_green_on_empty_discovery(self):
        """Proves the vacuous-green guard itself fires against REAL discovery
        code, not `unittest.assertTrue` in isolation: `subprocess.run` is
        patched so `_tracked_claude_settings_files()` genuinely returns an
        empty list, then the exact guard the real test above runs
        (`self.assertTrue(files, ...)`) must raise against that real return
        value."""
        empty = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with mock.patch.object(subprocess, "run", return_value=empty):
            files = _tracked_claude_settings_files()
        self.assertEqual([], files)
        with self.assertRaises(AssertionError):
            self.assertTrue(
                files,
                "no tracked .claude/ files found -- file discovery is broken, which makes "
                "this check impossible to fail",
            )


# --------------------------------------------------------------------------- #
# Part 3 (RETIRED by the #539/#560 ruling): this used to guard the three
# single points of silent failure the #651 shebang-only design depended on --
# the execute bit set, a clean two-byte `#!` shebang, and no CRLF corrupting
# it -- because a hook whose `command` invoked its script bare relied on all
# three holding for that script. The tracked .claude/settings.json no longer
# invokes any hook script bare: `build_hook_command` always leads with
# `${CONSTELLATION_PYTHON:-python3}` now (Part 2), so the interpreter comes
# from the command string, not from the OS executing the file directly, and
# none of the three facts this Part checked are load-bearing anymore. Removed
# rather than left green-by-vacuity: `_shebang_invoked_scripts()` would find
# zero bare-invoked entries in the real tracked file today, which is a
# retirement to record, not a check to keep running against nothing.
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# Part 4: a shell-form hook `command` depends on a REAL shell running it.
# Claude Code's shell-form default is `sh -c` on POSIX, Git Bash on Windows,
# or PowerShell when Git Bash isn't installed. Two shapes both silently no-op
# there: the retired #651 bare-quoted-path form (`"<path>"` parses as a
# string-literal EXPRESSION under PowerShell -- it echoes the path and exits 0
# without running anything) and the current `${CONSTELLATION_PYTHON:-...}`
# form (PowerShell/cmd.exe do not perform POSIX `${VAR:-default}` expansion at
# all, so the token is not resolved the way a real shell resolves it -- #651
# shipped this exact gap once already, caught by the three
# `test_*_actually_executes` live-execution tests in test_install_constellation.py
# failing on Windows CI). Pinning `"shell": "bash"` on EVERY shell-form entry
# -- not just bare-quoted-path ones -- turns an unavailable Windows shell into
# a loud failure instead of a silent one; it does not make Windows work, but
# it stops it from succeeding at nothing.
# --------------------------------------------------------------------------- #


def find_missing_shell_pin_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every shell-form hook in `text` (any `command` with no sibling `args`
    key -- exec-form entries ignore `shell` entirely per Claude Code's own
    docs and are skipped) that does not carry `"shell": "bash"`. Broadened
    from "only a bare-quoted-path command" (the #651-era shape) to EVERY
    shell-form command: the current shape (`${CONSTELLATION_PYTHON:-...} "..."`)
    depends on POSIX expansion just as much as the old bare-quoted-path shape
    depended on PowerShell parsing a leading word as a command, and a check
    that only recognised the retired shape would go vacuously green against
    the current one. Pure function over JSON text, like Part 1/2 above, so it
    can be self-tested against synthetic content without touching real git
    state."""
    try:
        settings = json.loads(text)
    except (OSError, ValueError):
        return []
    violations: list[tuple[str, str]] = []
    for event, entries in (settings.get("hooks") or {}).items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for hook in entry.get("hooks") or []:
                if not isinstance(hook, dict) or "args" in hook:
                    continue
                command = hook.get("command")
                if not isinstance(command, str):
                    continue
                if hook.get("shell") != "bash":
                    violations.append((rel_path, f"{event}: {command}"))
    return violations


class ShellPinTests(unittest.TestCase):
    """Guards the fix for the BLOCKING finding: a shell-form hook command
    with no `"shell": "bash"` pin silently no-ops under PowerShell (Claude
    Code's fallback shell when Git Bash isn't installed on Windows)."""

    def test_every_shell_form_hook_pins_shell_bash(self):
        files = _tracked_claude_settings_files()
        self.assertTrue(
            files,
            "no tracked .claude/ files found -- file discovery is broken, which makes "
            "this check impossible to fail",
        )
        violations: list[tuple[str, str]] = []
        for path in files:
            rel_path = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            violations.extend(find_missing_shell_pin_violations(text, rel_path))
        self.assertEqual(
            violations, [],
            f"A tracked .claude/ shell-form hook command has no \"shell\": \"bash\" pin -- "
            f"without it, a Windows host missing Git Bash silently no-ops this hook under "
            f"PowerShell instead of failing loudly (or, for the current "
            f"${{CONSTELLATION_PYTHON:-...}} form, the token is never expanded at all): "
            f"{violations}",
        )

    def test_detector_actually_fires_on_a_constructed_violation(self):
        missing_pin = (
            '{"hooks": {"Stop": [{"hooks": [{"type": "command", '
            '"command": "${CONSTELLATION_PYTHON:-python3} '
            '\\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop", '
            '"timeout": 20}]}]}}'
        )
        self.assertEqual(
            find_missing_shell_pin_violations(missing_pin, ".claude/settings.json"),
            [(
                ".claude/settings.json",
                'Stop: ${CONSTELLATION_PYTHON:-python3} '
                '"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" Stop',
            )],
        )

        # Wrong value (e.g. "powershell") must also fire -- only "bash" is safe.
        wrong_pin = missing_pin.replace('"timeout": 20', '"shell": "powershell", "timeout": 20')
        self.assertEqual(
            find_missing_shell_pin_violations(wrong_pin, ".claude/settings.json"),
            [(
                ".claude/settings.json",
                'Stop: ${CONSTELLATION_PYTHON:-python3} '
                '"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" Stop',
            )],
        )

        # And confirms the actually-shipped form -- "shell": "bash" present --
        # never trips it.
        correctly_pinned = missing_pin.replace('"timeout": 20', '"shell": "bash", "timeout": 20')
        self.assertEqual(
            find_missing_shell_pin_violations(correctly_pinned, ".claude/settings.json"),
            [],
        )

        # The retired #651 bare-quoted-path shape must still be caught too --
        # broadening the check must not have narrowed it.
        bare_path_missing_pin = (
            '{"hooks": {"Stop": [{"hooks": [{"type": "command", '
            '"command": "\\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop", '
            '"timeout": 20}]}]}}'
        )
        self.assertEqual(
            find_missing_shell_pin_violations(bare_path_missing_pin, ".claude/settings.json"),
            [(
                ".claude/settings.json",
                'Stop: "${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" Stop',
            )],
        )

        # An exec-form entry (carries "args") ignores "shell" entirely per
        # Claude Code's own docs and must never be flagged.
        exec_form = (
            '{"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", '
            '"command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/x.py"]}]}]}}'
        )
        self.assertEqual(
            find_missing_shell_pin_violations(exec_form, ".claude/settings.json"),
            [],
        )


# --------------------------------------------------------------------------- #
# Part 5 (#539/#560): the per-machine OVERRIDE still lives in
# MCP_INTERPRETER_ENV_VAR, and the installer can only wire what it has a
# HookSpec for. Two independent failure modes are guarded here.
#
# (a) DRIFT. `install_constellation.HOOK_SPECS` is hand-written from the four
#     entries this repo ships in .claude/settings.json. If somebody adds a
#     fifth hook to that file, or retimes one, the installer silently keeps
#     wiring the old four -- and `--check-readiness` keeps reporting on the
#     old four, so nothing anywhere says the new one is unwired. Held here by
#     comparing the table against the real file.
#
# (b) THE LEADING WORD. Every command the installer can emit must start with
#     a command word, never a quote. A command starting with `"` is the
#     silent-no-op shape from Part 4, and this asserts the EMIT side of what
#     Part 4 asserts on the tracked-file side.
# --------------------------------------------------------------------------- #

TRACKED_SETTINGS = ROOT / ".claude" / "settings.json"

# The first quoted span in a hook `command` -- the script path -- wherever it
# falls. Not anchored to the start: the tracked shape now leads with
# `${CONSTELLATION_PYTHON:-python3} "<path>" <args>` (Part 2), so the quoted
# path is the SECOND token, not the first. A retired #651 bare-quoted-path
# command (`"<path>" <args>`, no interpreter prefix) still matches too, since
# `.search` finds the first quote wherever it is.
_QUOTED_SCRIPT_PATH_RE = re.compile(r'"([^"]+)"')


def _tracked_hook_entries() -> list[tuple[str, str | None, str, tuple[str, ...], int]]:
    """Every hook in the tracked settings.json as
    (event, matcher, script_basename, args, timeout) -- the same five facts a
    HookSpec carries, read straight off the file."""
    settings = json.loads(TRACKED_SETTINGS.read_text(encoding="utf-8"))
    found = []
    for event, entries in (settings.get("hooks") or {}).items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            matcher = entry.get("matcher")
            for hook in entry.get("hooks") or []:
                if not isinstance(hook, dict):
                    continue
                command = hook.get("command")
                if not isinstance(command, str):
                    continue
                match = _QUOTED_SCRIPT_PATH_RE.search(command)
                if not match:
                    continue
                script = Path(match.group(1)).name
                args = tuple(command[match.end():].split())
                found.append((event, matcher, script, args, hook.get("timeout")))
    return sorted(found, key=lambda row: (row[0], str(row[1]), row[2]))


class HookSpecTableMatchesTrackedSettingsTests(unittest.TestCase):
    """The installer's HOOK_SPECS table and this repo's own .claude/settings.json
    describe the same four hooks. Neither is derived from the other at runtime
    (the installer must work in projects that have no settings.json yet), so
    this test is the only thing holding them together."""

    def test_hook_specs_match_the_tracked_settings_json_exactly(self):
        installer = load_installer()
        tracked = _tracked_hook_entries()
        # Guards against vacuous green: with no entries discovered, comparing
        # two empty-ish structures would pass without ever having checked a
        # thing. Same inert-detector shape the self-tests below catch one level
        # down.
        self.assertTrue(
            tracked,
            "no shell-form hook entries discovered in the tracked .claude/settings.json -- "
            "discovery is broken, which makes this check impossible to fail",
        )
        specs = sorted(
            (spec.event, spec.matcher, spec.script, spec.args, spec.timeout)
            for spec in installer.HOOK_SPECS
        )
        self.assertEqual(
            specs, tracked,
            "install_constellation.HOOK_SPECS has drifted from .claude/settings.json. "
            "The installer can only WIRE and only DETECT the hooks in that table, so a "
            "hook present in one and absent from the other is a hook nothing can report "
            "on. Update HOOK_SPECS (or the settings file) so both name the same set.",
        )

    def test_detector_actually_fires_on_a_constructed_drift(self):
        """Self-test: a settings file carrying a fifth hook must not compare
        equal to the four-spec table -- via the REAL `_tracked_hook_entries()`
        reader, pointed (through `mock.patch`) at a constructed temp file that
        carries the real settings PLUS one extra hook, never a hand-built list
        that never touches the reader at all."""
        installer = load_installer()
        specs = sorted(
            (spec.event, spec.matcher, spec.script, spec.args, spec.timeout)
            for spec in installer.HOOK_SPECS
        )
        drifted_settings = json.loads(TRACKED_SETTINGS.read_text(encoding="utf-8"))
        drifted_hooks = dict(drifted_settings.get("hooks") or {})
        drifted_hooks["PreToolUse"] = [{
            "matcher": "*",
            "hooks": [{
                "type": "command",
                "command": '"${CLAUDE_PROJECT_DIR}/scripts/hooks/some_new_hook.py"',
                "timeout": 10,
                "shell": "bash",
            }],
        }]
        drifted_settings["hooks"] = drifted_hooks

        with tempfile.TemporaryDirectory() as tmp:
            drifted_path = Path(tmp) / "settings.json"
            drifted_path.write_text(
                json.dumps(drifted_settings), encoding="utf-8", newline="\n")
            with mock.patch(f"{__name__}.TRACKED_SETTINGS", drifted_path):
                drifted_entries = _tracked_hook_entries()

        # `assertNotEqual(specs, drifted_entries)` alone is trivially true for
        # ANY reader that returns a wrong-length list -- including one broken
        # to return []. Four specs != [] proves nothing about whether the
        # reader read. Assert the reader actually saw the extra hook: the
        # length must be exactly one more, and the extra entry must be the one
        # constructed above.
        self.assertEqual(
            len(drifted_entries), len(specs) + 1,
            "the reader did not see the constructed fifth hook, so a comparison "
            "against it cannot distinguish drift from a reader that read nothing",
        )
        added = sorted(set(drifted_entries) - set(specs))
        self.assertEqual(
            [entry[0] for entry in added], ["PreToolUse"],
            f"the reader's extra entry is not the constructed one: {added!r}",
        )
        self.assertNotEqual(specs, drifted_entries)


class EmittedCommandShapeTests(unittest.TestCase):
    """The installer must never EMIT the silent-no-op shape Part 4 forbids in
    the tracked file: a command whose first character is a quote. Under
    PowerShell that parses as a string-literal expression -- the hook echoes
    its own path and exits 0 without running.

    Naming the interpreter first is safe under every shell Claude Code can
    spawn (`sh`, Git Bash, PowerShell, `cmd` all parse a leading bare word as a
    command), so this invariant does not RELY on the PowerShell parse claim
    being true -- it is the correct form either way."""

    def test_every_hook_spec_builds_a_command_starting_with_the_interpreter(self):
        """The interpreter is written portably (#539 residual):
        `${CONSTELLATION_PYTHON:-python3}`, not bare `python3` -- the same
        env-var knob `.mcp.json` uses (f315d7bf) -- but it is still the
        leading TOKEN of the command, which is what this test actually
        guards."""
        installer = load_installer()
        specs = installer.HOOK_SPECS
        self.assertTrue(
            specs,
            "HOOK_SPECS is empty -- nothing is built, which makes this check "
            "impossible to fail",
        )
        expected_prefix = f"${{{installer.MCP_INTERPRETER_ENV_VAR}:-python3}} "
        for spec in specs:
            command = installer.build_hook_command(
                Path("/some/where/with a space") / spec.script, "python3", spec.args)
            self.assertTrue(
                command.startswith(expected_prefix),
                f"{spec.name}: command does not start with the portable interpreter form "
                f"{expected_prefix!r}: {command!r}",
            )
            self.assertNotIn(
                command[0], "\"'",
                f"{spec.name}: command starts with a quote, which PowerShell parses as a "
                f"string literal and silently no-ops: {command!r}",
            )
            # The script path is still quoted -- just not FIRST -- so a path
            # with a space survives the shell.
            self.assertIn(f'"/some/where/with a space/{spec.script}"', command)

    def test_the_guard_actually_refuses_a_leading_quote_command(self):
        """Self-test: the refusal is live, and fires on exactly the shape the
        tracked settings.json is forced to use (a bare quoted path)."""
        installer = load_installer()
        with self.assertRaises(installer.InstallError) as raised:
            installer.assert_shell_safe_command('"/repo/scripts/hooks/spine_rail.py" Stop')
        self.assertIn("PowerShell", str(raised.exception))
        # A single-quoted leading path is the same trap.
        with self.assertRaises(installer.InstallError):
            installer.assert_shell_safe_command("'/repo/scripts/hooks/spine_rail.py'")
        with self.assertRaises(installer.InstallError):
            installer.assert_shell_safe_command("")
        # Leading whitespace is the same defect wearing a hat: the shell strips
        # it and PowerShell is back to parsing a leading quote.
        with self.assertRaises(installer.InstallError):
            installer.assert_shell_safe_command(' "/repo/scripts/hooks/spine_rail.py"')
        # And the shipped form is accepted.
        installer.assert_shell_safe_command('python3 "/repo/scripts/hooks/spine_rail.py" Stop')


if __name__ == "__main__":
    unittest.main()
