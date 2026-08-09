import importlib.util
import re
import subprocess
import sys
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
# --------------------------------------------------------------------------- #

# A `py` token used as a command: not preceded or followed by an identifier
# character, `.`, or `-` (so it never matches `python`, `python3`, or
# `some-py-thing`).
_PY_WORD = r"py(?![\w./-])"

# Backtick spans in markdown/JSON prose: `py scripts/x.py ...`. Requires an
# argument after `py` (whitespace then more content) -- a bare `` `py` `` is a
# NOUN (naming the launcher), not a command, and must not trip this.
_BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")
_LEADING_PY_COMMAND_RE = re.compile(rf"^{_PY_WORD}\s+\S")

# One deliberate, narrow exception: skills/_shared/windows.md documents the
# Windows-specific fact that `py` is the reliable launcher THERE, contrasted
# against bare `python` being unreliable on Windows PATH. The example is
# illustrative prose ("e.g. ...") pointing at a placeholder script name that
# does not exist anywhere in this repo -- never a command an agent is told to
# run. Keyed by exact text, not by filename: if this line's wording changes,
# the entry silently stops matching and any genuinely new violation in that
# file is still caught.
_ALLOWED_SPANS = frozenset({
    ("skills/_shared/windows.md", "py scripts/some_script.py"),
})


def find_py_launcher_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every `py <command>` literal used as a command in `text` (backtick
    spans only -- this is the skills/-corpus check, where `python
    <skill-dir>/...` is the correct, EXPECTED form and must not trip this),
    minus the one documented prose exception."""
    violations: list[tuple[str, str]] = []
    for span in _BACKTICK_SPAN_RE.findall(text):
        stripped = span.strip()
        if _LEADING_PY_COMMAND_RE.match(stripped) and (rel_path, stripped) not in _ALLOWED_SPANS:
            violations.append((rel_path, stripped))
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
# shebang -- scripts/hooks/*.py are executable (chmod +x) and pinned to LF via
# .gitattributes so the shebang survives a Windows checkout with
# core.autocrlf=true).
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
        that the regex above is live: fed synthetic text shaped exactly like
        the real defect, it must flag it every time this suite runs."""
        markdown_violation = "Run `py scripts/verify_thing.py <args>` before you finish."
        self.assertEqual(
            find_py_launcher_violations(markdown_violation, "skills/fake/SKILL.md"),
            [("skills/fake/SKILL.md", "py scripts/verify_thing.py <args>")],
        )

        # Confirms the exception is narrow: it must not blanket-suppress every
        # `py` command in the allowlisted file, only the one exact documented
        # line.
        self.assertEqual(
            find_py_launcher_violations(
                "Also run `py scripts/other_thing.py` here.", "skills/_shared/windows.md"
            ),
            [("skills/_shared/windows.md", "py scripts/other_thing.py")],
        )

        # And confirms bare mentions of the launcher name (no argument) are
        # never flagged -- only an actual command invocation is.
        self.assertEqual(
            find_py_launcher_violations("Use the `py` launcher.", "skills/_shared/windows.md"),
            [],
        )

        # And confirms the skills/-corpus check never flags the CORRECT,
        # install-rewritten convention.
        self.assertEqual(
            find_py_launcher_violations(
                "Run `python <skill-dir>/scripts/verify_thing.py <args>`.", "skills/fake/SKILL.md"
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
        violations: list[tuple[str, str]] = []
        for path in _tracked_claude_settings_files():
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


if __name__ == "__main__":
    unittest.main()
