"""A shipped example must run for the person who installed it.

`examples/` is committed and ships with every clone, so anything it names has to
resolve on a machine that has never heard of this checkout. Issue #605 is what
happens when that stops being true: the demo spine carried six absolute paths
into `/home/tommy/projects/constellation-skills-wt/f-424`, a worktree deleted
during an unrelated closeout, on one machine, which never existed anywhere else.
The demo could not be run as shipped.

Scope is deliberately `examples/` only. This repo legitimately carries absolute
paths elsewhere -- installed skill paths in `.agent-work/` spines, test
fixtures, archived generators -- and a guard that swept those would fail on
legitimate content and be turned off, which is worse than no guard.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
DEMO = EXAMPLES / "mcp-interactive-demo"
DEMO_GENERATOR = DEMO / "make_demo_spine.py"
DEMO_SPINE = DEMO / "spine.json"
ENGINE = ROOT / "scripts" / "checklist_engine.py"

# Every shipped example is expected to be text. Anything that will not decode as
# UTF-8 is not scanned, and is reported so a silently-skipped file cannot hide.
SKIP_DIRS = {"__pycache__", ".git"}

# A floor, not the exact count: the guard must never pass by looping over
# nothing. Kept just below the real number so adding an example does not
# require editing it, while an empty or vanished `examples/` fails loudly.
MIN_SHIPPED_FILES = 3

# `sync-constellation-skills.yml` is a workflow template you drop into a
# CONSUMING repo. Paths like `.github/workflows/...` and `.constellation-src/...`
# deliberately address that repo, not this one, so resolving them here would be
# wrong -- and a guard that flagged them would be flagging correct content.
# Anything added here needs its reason written next to it.
ADDRESSES_ANOTHER_REPO = {"examples/sync-constellation-skills.yml"}

# Split on whitespace and the punctuation that wraps paths in prose, Markdown and
# shell. `{`/`}`/`(`/`)` are included so a shell expansion such as
# `${TMPDIR:-/tmp}/workspace/notes.txt` breaks apart instead of being mistaken
# for one repo-relative path.
TOKEN_SPLIT = re.compile(r"""[\s`"'()\[\]{},<>|]+""")
PATH_SUFFIXES = (".py", ".json", ".md", ".yml", ".yaml", ".toml", ".sh", ".txt", ".cfg", ".ini")
TRAILING_LINE_REF = re.compile(r":\d+$")

MACHINE_SPECIFIC_PATTERNS = (
    (re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+"), "a POSIX user home directory"),
    (re.compile(r"(?<![A-Za-z0-9_.-])/root(?![A-Za-z0-9_-])"), "the root account's home directory"),
    (re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/](?:Users|home)[\\/]", re.IGNORECASE), "a Windows user profile path"),
)


def shipped_example_files() -> list[Path]:
    """Every file that actually ships under `examples/`, sorted for a stable report.

    Tracked-only, via `git ls-files`, because tracked is precisely what "shipped"
    means -- and because the untracked files under `examples/` are the opposite
    of shipped content. Driving the demo makes the engine write its per-run
    side-cars (`spine.json.journal`, `context/`, `mechanical/`) next to the spine,
    and those legitimately embed the driver's own absolute paths. A guard that
    scanned them would fail for anyone who ran the demo, which is how a guard
    gets switched off.
    """
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", str(EXAMPLES.relative_to(ROOT))],
        capture_output=True, text=True, check=True, cwd=str(ROOT),
    ).stdout
    found = []
    for name in filter(None, listed.split("\0")):
        path = ROOT / name
        if not path.is_file() or SKIP_DIRS & set(path.parts):
            continue
        found.append(path)
    return sorted(found)


def load_demo_generator():
    """Import `examples/mcp-interactive-demo/make_demo_spine.py` as a module.

    Bytecode writing is suppressed for the duration: a `__pycache__` under
    `examples/` would drop a .pyc that embeds this checkout's absolute path into
    a shipped directory -- the exact thing this file exists to keep out of there,
    and the stale-bytecode trap of issue #597.
    """
    spec = importlib.util.spec_from_file_location("make_demo_spine", DEMO_GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def read_text_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def machine_specific_hits(text: str, *, checkout_root: str) -> list[tuple[int, str, str]]:
    """Every (line number, matched text, why) a line is machine-specific.

    `checkout_root` catches a path pinned to this working copy even when it sits
    outside a home directory -- a worktree under /srv or /opt reads as portable
    to the pattern list but is just as dead on another machine.
    """
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pattern, why in MACHINE_SPECIFIC_PATTERNS:
            for match in pattern.finditer(line):
                hits.append((lineno, match.group(0), why))
        if checkout_root and checkout_root in line:
            hits.append((lineno, checkout_root, "this checkout's own absolute path"))
    return hits


def repo_top_level_entries() -> set[str]:
    """This repo's own top-level names, from git rather than the filesystem."""
    listed = subprocess.run(
        ["git", "ls-tree", "--name-only", "-z", "HEAD"],
        capture_output=True, text=True, check=True, cwd=str(ROOT),
    ).stdout
    return {name for name in listed.split("\0") if name}


def repo_path_tokens(text: str, *, top_level: set[str]) -> list[str]:
    """Path tokens in `text` that address a file in THIS repo.

    A token qualifies only when it has a directory separator, ends in a suffix we
    recognise, and is rooted at one of this repo's own top-level entries. That
    last rule is what keeps the guard narrow: `.constellation-src/scripts/foo.py`
    names a directory a CI job creates at runtime, not a file here, so it is left
    alone rather than reported as dead.
    """
    tokens = []
    for raw in TOKEN_SPLIT.split(text):
        token = TRAILING_LINE_REF.sub("", raw.strip().rstrip(".,;:"))
        if not token or "/" not in token:
            continue
        if token.startswith(("http://", "https://", "/", "-", "~")) or "$" in token or "*" in token:
            continue
        if not token.endswith(PATH_SUFFIXES):
            continue
        if token.split("/", 1)[0] not in top_level:
            continue
        tokens.append(token)
    return tokens


class ShippedExamplesNameOnlyPathsThatExistTests(unittest.TestCase):
    """A dead relative path is just as broken as a dead absolute one.

    The absolute-path guard cannot see this class at all: when issue #605's demo
    README told you to regenerate the spine with a script under
    `.agent-work/epic-418-followon/...`, the path was perfectly portable and
    perfectly dead -- the generator had moved to `.agent-work/archive/...`. Same
    for `scripts/gen_mcp_config.py`, which the README still recommended after it
    was deleted.
    """

    def test_every_repo_path_a_shipped_example_names_actually_exists(self):
        top_level = repo_top_level_entries()
        self.assertIn("scripts", top_level, "sanity: repo top-level lookup returned nothing useful")

        checked, dead, examined = 0, [], []
        for path in shipped_example_files():
            relative = str(path.relative_to(ROOT))
            if relative in ADDRESSES_ANOTHER_REPO:
                continue
            text = read_text_or_none(path)
            if text is None:
                continue
            examined.append(relative)
            for lineno, line in enumerate(text.splitlines(), start=1):
                for token in repo_path_tokens(line, top_level=top_level):
                    checked += 1
                    if not (ROOT / token).exists():
                        dead.append(f"{relative}:{lineno}: {token!r} does not exist")

        self.assertGreaterEqual(
            len(examined), 2,
            f"guard examined {len(examined)} shipped example file(s); it must not pass on nothing")
        self.assertGreater(
            checked, 0,
            f"guard resolved {checked} repo path(s) across {examined}; a run that resolves "
            "nothing cannot tell a live path from a dead one")
        self.assertEqual(
            [], dead,
            f"resolved {checked} repo path(s) across {len(examined)} shipped example file(s) and "
            f"found {len(dead)} dead:\n  " + "\n  ".join(dead))

    def test_the_another_repo_exemptions_still_exist(self):
        """An exemption for a file that has been deleted is a silent hole."""
        for relative in sorted(ADDRESSES_ANOTHER_REPO):
            self.assertTrue(
                (ROOT / relative).is_file(),
                f"exempted {relative} no longer exists; drop it from ADDRESSES_ANOTHER_REPO")


class ShippedExamplesArePortableTests(unittest.TestCase):
    def test_no_machine_specific_absolute_path_in_a_shipped_example(self):
        """Issue #605. Fails on the pre-fix spine.json with six hits."""
        files = shipped_example_files()
        self.assertGreaterEqual(
            len(files), MIN_SHIPPED_FILES,
            f"guard looped over {len(files)} file(s) under {EXAMPLES}; it must never "
            f"pass by examining nothing (floor {MIN_SHIPPED_FILES})")

        checkout_root = str(ROOT)
        scanned, undecodable, violations = [], [], []
        for path in files:
            text = read_text_or_none(path)
            if text is None:
                undecodable.append(path)
                continue
            scanned.append(path)
            for lineno, hit, why in machine_specific_hits(text, checkout_root=checkout_root):
                violations.append(
                    f"{path.relative_to(ROOT)}:{lineno}: {hit!r} is {why}")

        self.assertEqual([], undecodable, f"unscannable shipped example(s): {undecodable}")
        self.assertGreaterEqual(
            len(scanned), MIN_SHIPPED_FILES,
            f"only {len(scanned)} shipped example file(s) were actually scanned")
        self.assertEqual(
            [], violations,
            f"scanned {len(scanned)} shipped example file(s) under examples/ and found "
            f"{len(violations)} machine-specific path(s); a shipped example must run on a "
            f"machine that has never heard of this checkout:\n  " + "\n  ".join(violations))


class DemoSpineIsGeneratedNotHandEditedTests(unittest.TestCase):
    """The committed spine must stay exactly what its generator produces.

    An absolute-path guard alone only says the current text is clean. This says
    the text is still *derived*, so the six paths cannot be quietly hand-edited
    back to something machine-specific: the generator is the only way to change
    them, and the generator cannot emit one.
    """

    def test_committed_spine_is_exactly_what_the_generator_produces(self):
        generator = load_demo_generator()
        self.assertEqual(
            generator.spine_text(), DEMO_SPINE.read_text(encoding="utf-8"),
            f"{DEMO_SPINE.relative_to(ROOT)} has drifted from its generator; "
            f"regenerate it with `python {DEMO_GENERATOR.relative_to(ROOT)}` "
            "rather than editing it by hand")

    def test_generated_spine_names_no_path_that_needs_a_working_directory(self):
        """Every command check resolves without an ambient cwd.

        `checklist_engine.py` runs command checks with no `cwd`, so a check whose
        path is relative to anything resolves correctly from nowhere.
        """
        generator = load_demo_generator()
        spine = generator.build_spine()
        commands = [
            cond["check"]["command"]
            for task in spine["tasks"].values()
            for cond in task["postconditions"]
            if (cond.get("check") or {}).get("kind") == "command"
        ]
        self.assertGreaterEqual(len(commands), 2, f"expected command checks to inspect; got {commands}")
        for command in commands:
            with self.subTest(command=command):
                path = re.search(r'test -f "([^"]+)"', command)
                self.assertIsNotNone(path, f"unrecognised check shape: {command}")
                expanded = subprocess.run(
                    ["bash", "-c", f'printf %s "{path.group(1)}"'],
                    capture_output=True, text=True, check=True,
                    cwd=tempfile.gettempdir(),
                ).stdout
                self.assertTrue(
                    Path(expanded).is_absolute(),
                    f"check path did not expand to an absolute location: {expanded!r}")


class ShippedDemoDrivesFromAnyDirectoryTests(unittest.TestCase):
    """Issue #605's actual claim: the demo must be drivable where it is installed.

    Driven against a copy, from a working directory unrelated to both the repo
    root and the example directory -- the cwd is the load-bearing variable, since
    that is the one thing a command check does not get told about.
    """

    def drive(self, spine: Path, *args: str, cwd: Path, workspace: Path) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items()
               if k not in ("SPINE_FILE", "SPINE_SESSION", "SPINE_PARENT")}
        env["SPINE_DEMO_WORKSPACE"] = str(workspace)
        return subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(spine), *args],
            capture_output=True, text=True, cwd=str(cwd), env=env,
        )

    def test_a_gate_advances_from_an_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            spine = home / "spine.json"
            shutil.copy(DEMO_SPINE, spine)

            elsewhere = home / "some" / "unrelated" / "cwd"
            elsewhere.mkdir(parents=True)
            demo_home = home / "demo-home"
            (demo_home / "workspace").mkdir(parents=True)
            (demo_home / "workspace" / "notes.txt").write_text("hello\n", encoding="utf-8")

            started = self.drive(spine, "start", "g1", cwd=elsewhere, workspace=demo_home)
            self.assertEqual(0, started.returncode, started.stderr)

            attested = self.drive(spine, "attest", "g1", "--cond", "c2",
                                  "--which", "postconditions", cwd=elsewhere, workspace=demo_home)
            self.assertEqual(0, attested.returncode, attested.stderr)

            advanced = self.drive(spine, "advance", "g1", "--mechanical",
                                  cwd=elsewhere, workspace=demo_home)
            self.assertEqual(
                0, advanced.returncode,
                "g1 would not advance from an unrelated cwd -- its command check could not "
                f"find the workspace:\n{advanced.stdout}\n{advanced.stderr}")

            loaded = json.loads(spine.read_text(encoding="utf-8"))
            self.assertEqual("complete", loaded["tasks"]["g1"]["status"])

    def test_the_command_check_really_fails_when_the_file_is_absent(self):
        """The negative control: the same drive refuses when notes.txt is missing.

        Without this, a check that trivially passed would look identical to one
        that genuinely found the file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            spine = home / "spine.json"
            shutil.copy(DEMO_SPINE, spine)
            elsewhere = home / "elsewhere"
            elsewhere.mkdir()
            demo_home = home / "empty-demo-home"
            (demo_home / "workspace").mkdir(parents=True)

            self.drive(spine, "start", "g1", cwd=elsewhere, workspace=demo_home)
            self.drive(spine, "attest", "g1", "--cond", "c2",
                       "--which", "postconditions", cwd=elsewhere, workspace=demo_home)
            advanced = self.drive(spine, "advance", "g1", "--mechanical",
                                  cwd=elsewhere, workspace=demo_home)
            self.assertNotEqual(
                0, advanced.returncode,
                "g1 advanced with no notes.txt present; the command check is not discriminating")


if __name__ == "__main__":
    unittest.main()
