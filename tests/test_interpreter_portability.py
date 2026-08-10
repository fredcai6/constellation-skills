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


def _git_index_mode(path: Path) -> str | None:
    """The mode git's index records for `path` (e.g. "100755"), or None if
    `path` is not tracked. Read from git's own data model, not the
    filesystem: `os.access(path, os.X_OK)` returns True for every EXISTING
    file on Windows -- there is no real POSIX execute bit there -- so it
    silently never fires the "not executable" branch on the exact platform
    this whole PR protects. Caught in Windows CI by this file's own
    anti-vacuity self-test refusing to pass on an inert detector. Git's
    recorded mode is what a POSIX checkout actually receives (git chmods to
    match it on checkout) and is what a reviewer/CI diffs -- durable and
    platform-independent, unlike asking the local filesystem."""
    result = subprocess.run(
        ["git", "ls-files", "-s", str(path)],
        cwd=str(ROOT), capture_output=True, text=True, timeout=10,
    )
    line = result.stdout.strip()
    if not line:
        return None
    return line.split()[0]


def _mode_violation(mode: str | None) -> str | None:
    """Pure: given a git index mode (or None for untracked), the violation
    reason if it isn't the executable 100755, else None. Split out from any
    file/git access so it is unit-testable with synthetic values --
    deterministic on every OS the suite runs on, unlike a chmod()+os.access()
    round-trip against a real file."""
    if mode is None:
        return "is not tracked by git -- cannot verify its committed mode"
    if mode != "100755":
        return f"is tracked with git mode {mode}, not 100755 (chmod +x)"
    return None


def _shebang_byte_violations(path: Path) -> list[str]:
    """The shebang as `path`'s first two bytes, and no `\r` corrupting it --
    read from `path`'s actual byte content, so this is platform-independent
    by construction: it never asks the OS anything, unlike the git-tracked-
    mode check above."""
    raw = path.read_bytes()
    reasons: list[str] = []
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


def _shebang_violations(path: Path) -> list[str]:
    """Every way `path` could fail to run when invoked bare, relying only on
    its own shebang line. Returns human-readable reasons; empty means clean."""
    if not path.is_file():
        return [f"{path} does not exist"]
    reasons: list[str] = []
    mode_problem = _mode_violation(_git_index_mode(path))
    if mode_problem:
        reasons.append(f"{path} {mode_problem}")
    reasons.extend(_shebang_byte_violations(path))
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

    def test_mode_violation_detector_fires_on_constructed_values(self):
        """Pure unit test of the executable-bit check, decoupled from the
        filesystem entirely: the original self-test here used
        `chmod(0o644)` + `os.access(path, os.X_OK)` against a real temp
        file, which is inert on Windows -- there is no real POSIX execute
        bit there, so `os.access(..., os.X_OK)` returns True for every
        existing file regardless of chmod, the constructed violation
        produced no violations, and the detector went quietly inert on
        exactly the platform this PR protects. Caught by this very
        self-test refusing to pass in Windows CI (`False is not true: []`)
        -- the anti-vacuity discipline working as intended. Tested here
        against synthetic git-index mode strings instead, so the assertion
        is deterministic on every OS the suite runs on."""
        self.assertIsNotNone(_mode_violation("100644"))
        self.assertIsNotNone(_mode_violation(None))
        self.assertIsNone(_mode_violation("100755"))

    def test_byte_violation_detector_fires_on_constructed_violations(self):
        """Self-test against synthetic temp files -- never touches the real
        repo scripts -- proving the shebang-presence and CRLF checks can
        independently fail. These two, unlike the mode check above, read
        `path`'s actual byte content rather than asking the OS about it, so
        they are genuinely platform-independent and a real tempfile
        round-trip is the right test shape."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            no_shebang = tmp_path / "no_shebang.py"
            no_shebang.write_bytes(b"print('hi')\n")
            violations = _shebang_byte_violations(no_shebang)
            self.assertTrue(
                any("does not start with a shebang" in v for v in violations), violations,
            )

            crlf_shebang = tmp_path / "crlf_shebang.py"
            crlf_shebang.write_bytes(b"#!/usr/bin/env python3\r\nprint('hi')\r\n")
            violations = _shebang_byte_violations(crlf_shebang)
            self.assertTrue(
                any("carriage return" in v for v in violations), violations,
            )

            clean = tmp_path / "clean.py"
            clean.write_bytes(b"#!/usr/bin/env python3\nprint('hi')\n")
            self.assertEqual(_shebang_byte_violations(clean), [])

    def test_shebang_violations_reports_a_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does_not_exist.py"
            violations = _shebang_violations(missing)
            self.assertTrue(any("does not exist" in v for v in violations), violations)


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


# --------------------------------------------------------------------------- #
# Part 5 (#539): the tracked settings.json cannot name an interpreter, so the
# per-machine wiring must -- and the installer can only wire what it has a
# HookSpec for. Two independent failure modes are guarded here.
#
# (a) DRIFT. `install_constellation.HOOK_SPECS` is hand-written from the four
#     entries this repo ships in .claude/settings.json. If somebody adds a
#     fifth hook to that file, or retimes one, the installer silently keeps
#     wiring the old four -- and `--check-readiness` keeps reporting on the
#     old four, so nothing anywhere says the new one is unwired. Held here by
#     comparing the table against the real file.
#
# (b) THE LEADING QUOTE. Every command the installer can emit must start with
#     a command word. A command starting with `"` is the silent-no-op shape
#     from Part 4, and this asserts the EMIT side of what Part 4 asserts on
#     the tracked-file side.
# --------------------------------------------------------------------------- #

TRACKED_SETTINGS = ROOT / ".claude" / "settings.json"


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
                match = _LEADING_QUOTED_PATH_RE.match(command)
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

        self.assertNotEqual(
            specs, drifted_entries,
            "the comparison cannot distinguish a five-hook file from a four-spec table, "
            "which makes this check impossible to fail",
        )


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
        installer = load_installer()
        specs = installer.HOOK_SPECS
        self.assertTrue(
            specs,
            "HOOK_SPECS is empty -- nothing is built, which makes this check "
            "impossible to fail",
        )
        for spec in specs:
            command = installer.build_hook_command(
                Path("/some/where/with a space") / spec.script, "python3", spec.args)
            self.assertTrue(
                command.startswith("python3 "),
                f"{spec.name}: command does not start with the interpreter: {command!r}",
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
