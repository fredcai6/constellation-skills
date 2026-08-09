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


# `py` is the Windows Python launcher. It does not exist on Linux or macOS, and
# the installer never rewrites it: `installed_path_replacements()` (see
# install_constellation.py) only rewrites the literal token `"python <"`, so a
# hard-coded `py <script>` ships verbatim to every platform and fails off
# Windows. This guards the CLASS of defect, not the fixed instances: it scans
# every file the installer actually ships (same suffix set it rewrites,
# `REWRITABLE_TEXT_SUFFIXES`) plus the tracked project `.claude/` settings
# (never install-rewritten at all), and fails on ANY new `py <something>`
# command literal -- in a backtick-quoted command or a JSON hook `"command"`
# field -- regardless of which file it turns up in.

# A `py` token used as a command: not preceded or followed by an identifier
# character, `.`, or `-` (so it never matches `python`, `python3`, or
# `some-py-thing`).
_PY_WORD = r"py(?![\w./-])"

# Backtick spans in markdown/JSON prose: `py scripts/x.py ...`. Requires an
# argument after `py` (whitespace then more content) -- a bare `` `py` `` is a
# NOUN (naming the launcher), not a command, and must not trip this.
_BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")
_LEADING_PY_COMMAND_RE = re.compile(rf"^{_PY_WORD}\s+\S")

# A JSON hook/check `"command"` field naming `py` as the executable, either as
# the whole value (Claude Code hook "exec form") or as the first word of a
# shell string. Scanned as raw text (not JSON-parsed) so a malformed file still
# gets checked, matching how the installer's own text rewrite treats these
# files -- bytes in, bytes out, no structural assumptions.
_JSON_COMMAND_PY_RE = re.compile(rf'"command"\s*:\s*"{_PY_WORD}(?=[\s"])')

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


def find_py_launcher_violations(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Every `py <command>` literal in `text`, as (rel_path, offending snippet)
    pairs, minus the one documented prose exception."""
    violations: list[tuple[str, str]] = []
    for span in _BACKTICK_SPAN_RE.findall(text):
        stripped = span.strip()
        if _LEADING_PY_COMMAND_RE.match(stripped) and (rel_path, stripped) not in _ALLOWED_SPANS:
            violations.append((rel_path, stripped))
    for match in _JSON_COMMAND_PY_RE.finditer(text):
        violations.append((rel_path, match.group(0)))
    return violations


class PyLauncherLiteralTests(unittest.TestCase):
    """Guards the CLASS: no shipped skill text or tracked project settings file
    may hard-code the Windows-only `py` launcher as an executable command. See
    `installed_path_replacements()` in install_constellation.py -- the
    portable convention is `python <skill-dir>/...`, rewritten at install
    time; `py ...` matches no rewrite token and ships verbatim."""

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

    def test_no_py_launcher_literal_in_tracked_claude_settings(self):
        violations: list[tuple[str, str]] = []
        for path in _tracked_claude_settings_files():
            rel_path = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            violations.extend(find_py_launcher_violations(text, rel_path))
        self.assertEqual(
            violations, [],
            f"Windows-only `py` launcher hard-coded as a hook command in a tracked "
            f".claude/ settings file (never install-rewritten at all): {violations}",
        )

    def test_detector_actually_fires_on_a_constructed_violation(self):
        """A check that cannot fail is worthless. This is not a demonstration
        run by hand -- it is a permanent, deterministic proof in the suite
        that the regexes above are live: fed synthetic text shaped exactly
        like the real defect, they must flag it every time this suite runs."""
        markdown_violation = "Run `py scripts/verify_thing.py <args>` before you finish."
        self.assertEqual(
            find_py_launcher_violations(markdown_violation, "skills/fake/SKILL.md"),
            [("skills/fake/SKILL.md", "py scripts/verify_thing.py <args>")],
        )

        json_violation = '{"command": "py \\"${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py\\" Stop"}'
        self.assertEqual(
            find_py_launcher_violations(json_violation, ".claude/settings.json"),
            [(".claude/settings.json", '"command": "py')],
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


if __name__ == "__main__":
    unittest.main()
