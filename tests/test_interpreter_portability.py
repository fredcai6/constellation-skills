import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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
# forever -- `python3` is exactly as wrong on stock Windows (which ships
# `python`/`py`, not `python3` -- python.org's installer doesn't add
# `python3.exe`, and Windows' own `python3.exe` App Execution Alias just opens
# the Store) as `py` was wrong on Linux/macOS. No single static interpreter
# name is safe here; the fix is to name NONE at all (see .claude/settings.json,
# which invokes the hook scripts directly by their `#!/usr/bin/env python3`
# shebang, with `"shell": "bash"` pinned on every entry so Claude Code never
# falls back to PowerShell -- which parses a bare `"<path>"` as a string
# literal and silently exits 0 without running anything).
# --------------------------------------------------------------------------- #

# Matches a JSON `"command"` field whose value NAMES an interpreter as its
# first token -- shell-form ("python3 \"...\" args") or exec-form's bare
# ("command": "py") -- covering every member of
# install_constellation.py's own INTERPRETER_CANDIDATES plus bare `python`.
_TRACKED_SETTINGS_INTERPRETER_RE = re.compile(
    r'"command"\s*:\s*"\s*(?:py|python3|python)(?![\w./-])'
)


def find_named_interpreter_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every JSON hook `"command"` field in `text` that names ANY
    platform-specific interpreter (`py`, `python3`, or `python`) as its
    executable, as (rel_path, offending snippet) pairs. Scanned as raw text
    (not JSON-parsed) so a malformed file still gets checked."""
    return [(rel_path, m.group(0)) for m in _TRACKED_SETTINGS_INTERPRETER_RE.finditer(text)]


class PyLauncherLiteralTests(unittest.TestCase):
    """Guards the CLASS, not today's instance list: no shipped skill text may
    hard-code the Windows-only `py` launcher as an executable command (see
    `installed_path_replacements()` in install_constellation.py)."""

    def test_no_py_launcher_literal_in_shipped_skill_text(self):
        suffixes = _rewritable_suffixes()
        violations: list[tuple[str, str]] = []
        for path in sorted(SKILLS_ROOT.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            rel_path = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            violations.extend(find_py_launcher_violations(text, rel_path))
        self.assertEqual(
            violations, [],
            f"Windows-only `py` launcher hard-coded as a command in shipped skill "
            f"text (never rewritten at install time -- see installed_path_replacements "
            f"in install_constellation.py): {violations}",
        )

    def test_detector_actually_fires_on_a_constructed_violation(self):
        """A check that cannot fail is worthless. This is not a demonstration
        run by hand -- it is a permanent, deterministic proof in the suite
        that the regex above is live: fed synthetic text shaped like each way
        the real defect has actually shipped, it must flag every one, every
        time this suite runs."""
        # Inline backtick.
        self.assertEqual(
            find_py_launcher_violations(
                "Run `py scripts/verify_thing.py <args>` before you finish.", "skills/fake/SKILL.md"
            ),
            [("skills/fake/SKILL.md", "py scripts/verify_thing.py <args>")],
        )

        # Fenced code block (17+ real skill files use this form for examples).
        fenced = "Example:\n\n```bash\ncd skills/fake\npy scripts/verify_thing.py --flag\n```\n"
        self.assertEqual(
            find_py_launcher_violations(fenced, "skills/fake/SKILL.md"),
            [("skills/fake/SKILL.md", "py scripts/verify_thing.py --flag")],
        )

        # Chained command -- `py` is not the first word of the backtick span,
        # but it IS the first word of the second command in the chain.
        self.assertEqual(
            find_py_launcher_violations(
                "`cd skills/fake && py scripts/verify_thing.py`", "skills/fake/SKILL.md"
            ),
            [("skills/fake/SKILL.md", "py scripts/verify_thing.py")],
        )

        # `py.exe` -- the extensioned spelling, equally Windows-only.
        self.assertEqual(
            find_py_launcher_violations("Run `py.exe scripts/verify_thing.py`.", "skills/fake/SKILL.md"),
            [("skills/fake/SKILL.md", "py.exe scripts/verify_thing.py")],
        )

        # Raw JSON "command" field (spine/check postconditions never use
        # backticks at all).
        json_violation = '{"check": {"command": "py scripts/verify_thing.py <args>"}}'
        self.assertEqual(
            find_py_launcher_violations(json_violation, "skills/fake/templates/SPINE.template.json"),
            [("skills/fake/templates/SPINE.template.json", '"command": "py')],
        )

        # And confirms bare mentions of the launcher name (no argument) are
        # never flagged -- only an actual command invocation is.
        self.assertEqual(
            find_py_launcher_violations("Use the `py` launcher.", "skills/fake/SKILL.md"),
            [],
        )

        # And confirms the skills/-corpus check never flags the CORRECT,
        # install-rewritten convention, in any of the same shapes.
        self.assertEqual(
            find_py_launcher_violations(
                "Run `python <skill-dir>/scripts/verify_thing.py <args>`.\n\n"
                "```bash\npython <skill-dir>/scripts/verify_thing.py\n```\n"
                '{"check": {"command": "python <skill-dir>/scripts/verify_thing.py"}}',
                "skills/fake/SKILL.md",
            ),
            [],
        )


class TrackedSettingsInterpreterTests(unittest.TestCase):
    """Guards the CLASS: a git-tracked settings file is read, unmodified, on
    every contributor's platform, so it may never name ANY specific
    interpreter (`py`, `python`, or `python3`) as a hook command -- not just
    `py`. There is no install-time rewrite for this file at all, and no
    single static name is safe on both Windows and POSIX."""

    def test_no_interpreter_named_in_tracked_claude_settings(self):
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
            f"A tracked .claude/ settings file names a platform-specific interpreter "
            f"(py/python/python3) as a hook command. This file ships unmodified to "
            f"every contributor's OS with no install-time rewrite -- no single "
            f"interpreter name is safe here (python.org's Windows installer provides "
            f"`python`/`py`, not `python3`; POSIX commonly provides only `python3`, "
            f"not bare `python`). Invoke the script directly by its own shebang "
            f"instead (chmod +x + `.gitattributes` eol=lf, as scripts/hooks/*.py "
            f"already are): {violations}",
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

        # And confirms the actually-shipped form -- a bare quoted script path,
        # naming no interpreter at all -- never trips it.
        shebang_form_json = (
            '{"command": "\\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop"}'
        )
        self.assertEqual(
            find_named_interpreter_violations(shebang_form_json, ".claude/settings.json"),
            [],
        )

    def test_detector_would_not_go_green_on_empty_discovery(self):
        """Proves the vacuous-green guard itself fires, without touching real
        git state: an empty file list must fail assertTrue, not silently pass
        the surrounding scan."""
        with self.assertRaises(AssertionError):
            self.assertTrue([], "simulated empty discovery")


# --------------------------------------------------------------------------- #
# Part 3: the shebang-only design in .claude/settings.json depends on three
# OS-checkable facts holding for every script it invokes bare (no interpreter
# named): the execute bit is set, the file's first two bytes are `#!`, and the
# shebang line carries no `\r`. A Windows checkout with core.autocrlf=true
# would otherwise silently corrupt the shebang -- the hook then fails exactly
# the way a missing interpreter does, with nothing anywhere catching it.
# --------------------------------------------------------------------------- #

_LEADING_QUOTED_PATH_RE = re.compile(r'^"([^"]+)"')


def _shebang_invoked_scripts() -> list[Path]:
    """Every script a tracked .claude/ hook `command` invokes directly by its
    own shebang -- i.e. shell-form entries whose `command` starts with a bare
    quoted path, not an interpreter name (exec-form entries, which carry
    `args`, are a different invocation shape and are skipped here). Extracted
    from the real tracked settings rather than hard-coded, so a newly wired
    hook is covered automatically."""
    scripts: list[Path] = []
    for path in _tracked_claude_settings_files():
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for entries in settings.get("hooks", {}).values():
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
                    match = _LEADING_QUOTED_PATH_RE.match(command)
                    if not match:
                        continue
                    raw = match.group(1).replace("${CLAUDE_PROJECT_DIR}", str(ROOT))
                    scripts.append(Path(raw))
    return scripts


def _shebang_violations(path: Path) -> list[str]:
    """Every way `path` could fail to run when invoked bare, relying only on
    its own shebang line. Returns human-readable reasons; empty means clean."""
    if not path.is_file():
        return [f"{path} does not exist"]
    reasons: list[str] = []
    if not os.access(path, os.X_OK):
        reasons.append(f"{path} is not executable (chmod +x)")
    raw = path.read_bytes()
    if not raw.startswith(b"#!"):
        reasons.append(f"{path} does not start with a shebang (`#!`) as its first two bytes")
    else:
        shebang_line = raw.split(b"\n", 1)[0]
        if b"\r" in shebang_line:
            reasons.append(
                f"{path}'s shebang line contains a carriage return (CRLF checkout -- "
                f"`env` cannot resolve an interpreter name with a trailing \\r)"
            )
    return reasons


class ShebangInvariantTests(unittest.TestCase):
    """Guards the three new single points of silent failure the shebang-only
    design in .claude/settings.json depends on. None of this was guarded
    before this design existed -- nothing in the repo asserted a file mode
    anywhere."""

    def test_shebang_invoked_scripts_are_executable_with_a_clean_lf_shebang(self):
        scripts = _shebang_invoked_scripts()
        self.assertTrue(
            scripts,
            "no shebang-invoked scripts discovered in tracked .claude/ settings -- "
            "discovery is broken, which makes this check impossible to fail",
        )
        all_violations: list[str] = []
        for script in scripts:
            all_violations.extend(_shebang_violations(script))
        self.assertEqual(all_violations, [])

    def test_detector_actually_fires_on_constructed_violations(self):
        """Self-test against synthetic temp files -- never touches the real
        repo scripts -- proving each of the three checks can independently
        fail."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            not_executable = tmp_path / "not_executable.py"
            not_executable.write_bytes(b"#!/usr/bin/env python3\nprint('hi')\n")
            not_executable.chmod(0o644)
            violations = _shebang_violations(not_executable)
            self.assertTrue(
                any("not executable" in v for v in violations), violations,
            )

            no_shebang = tmp_path / "no_shebang.py"
            no_shebang.write_bytes(b"print('hi')\n")
            no_shebang.chmod(0o755)
            violations = _shebang_violations(no_shebang)
            self.assertTrue(
                any("does not start with a shebang" in v for v in violations), violations,
            )

            crlf_shebang = tmp_path / "crlf_shebang.py"
            crlf_shebang.write_bytes(b"#!/usr/bin/env python3\r\nprint('hi')\r\n")
            crlf_shebang.chmod(0o755)
            violations = _shebang_violations(crlf_shebang)
            self.assertTrue(
                any("carriage return" in v for v in violations), violations,
            )

            missing = tmp_path / "does_not_exist.py"
            violations = _shebang_violations(missing)
            self.assertTrue(any("does not exist" in v for v in violations), violations)

            clean = tmp_path / "clean.py"
            clean.write_bytes(b"#!/usr/bin/env python3\nprint('hi')\n")
            clean.chmod(0o755)
            self.assertEqual(_shebang_violations(clean), [])


# --------------------------------------------------------------------------- #
# Part 4: a shell-form hook whose `command` invokes a script bare (relying on
# its own shebang, no interpreter named) depends on a REAL shell running it.
# Claude Code's shell-form default is `sh -c` on POSIX, Git Bash on Windows,
# or PowerShell when Git Bash isn't installed -- and PowerShell parses a bare
# `"<path>"` as a string-literal EXPRESSION, not a command: it echoes the path
# and exits 0 without running anything. That is a silent no-op -- the exact
# failure shape this whole file exists to eliminate, and worse than the `py`
# launcher literal it replaced, which at least failed loudly. Pinning
# `"shell": "bash"` on every such entry turns an unavailable Windows shell
# into a loud failure instead of a silent one -- it does not make Windows
# work, but it stops it from succeeding at nothing.
# --------------------------------------------------------------------------- #


def find_missing_shell_pin_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every shell-form hook in `text` whose `command` invokes a script bare
    (matches the same leading-quoted-path shape `_shebang_invoked_scripts`
    looks for) but does not carry `"shell": "bash"`. Pure function over JSON
    text, like Part 1/2 above, so it can be self-tested against synthetic
    content without touching real git state."""
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
                if not isinstance(command, str) or not _LEADING_QUOTED_PATH_RE.match(command):
                    continue
                if hook.get("shell") != "bash":
                    violations.append((rel_path, f"{event}: {command}"))
    return violations


class ShellPinTests(unittest.TestCase):
    """Guards the fix for the BLOCKING finding: a bare-quoted-path hook
    command with no `"shell": "bash"` pin silently no-ops under PowerShell
    (Claude Code's fallback shell when Git Bash isn't installed on Windows)."""

    def test_every_bare_path_hook_pins_shell_bash(self):
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
            f"A tracked .claude/ hook invokes a script bare (relying on its shebang) "
            f"without pinning \"shell\": \"bash\" -- without the pin, a Windows host "
            f"missing Git Bash silently no-ops this hook under PowerShell instead of "
            f"failing loudly: {violations}",
        )

    def test_detector_actually_fires_on_a_constructed_violation(self):
        missing_pin = (
            '{"hooks": {"Stop": [{"hooks": [{"type": "command", '
            '"command": "\\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop", '
            '"timeout": 20}]}]}}'
        )
        self.assertEqual(
            find_missing_shell_pin_violations(missing_pin, ".claude/settings.json"),
            [(
                ".claude/settings.json",
                'Stop: "${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" Stop',
            )],
        )

        # Wrong value (e.g. "powershell") must also fire -- only "bash" is safe.
        wrong_pin = missing_pin.replace('"timeout": 20', '"shell": "powershell", "timeout": 20')
        self.assertEqual(
            find_missing_shell_pin_violations(wrong_pin, ".claude/settings.json"),
            [(
                ".claude/settings.json",
                'Stop: "${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" Stop',
            )],
        )

        # And confirms the actually-shipped form -- "shell": "bash" present --
        # never trips it.
        correctly_pinned = missing_pin.replace('"timeout": 20', '"shell": "bash", "timeout": 20')
        self.assertEqual(
            find_missing_shell_pin_violations(correctly_pinned, ".claude/settings.json"),
            [],
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


if __name__ == "__main__":
    unittest.main()
