# Worktree-Isolation Real Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace reliance on the Agent-tool `isolation:"worktree"` flag (a silent no-op on Windows) with explicit `git worktree add` provisioning, backed by a small `verify_worktree_isolation.py` helper and the doctrine that drives it.

**Architecture:** A new standalone script `scripts/verify_worktree_isolation.py` with pure decision helpers (unit-tested without git) and a thin git-shelling CLI (one integration test). Then three doctrine/template edits that tell the Admiral to provision worktrees itself, gate the wave on the script, and sweep on the right boundary.

**Tech Stack:** Python 3 stdlib (`argparse`, `os`, `subprocess`), `unittest` tests run under `pytest`. No new dependencies.

## Global Constraints

- The script is `scripts/verify_worktree_isolation.py`, styled exactly like `scripts/verify_state_note.py`: `#!/usr/bin/env python`, `from __future__ import annotations`, a `_utf8_stdio()` helper called at import, `def main(argv: list[str] | None = None) -> int`, and `if __name__ == "__main__": raise SystemExit(main())`.
- Pure helpers with these exact names and signatures: `normalize_path(p) -> str`, `parse_worktree_list(porcelain) -> list[str]`, `check_distinct_real(provisioned_paths, registered, primary) -> tuple[bool, str]`, `check_here(actual_toplevel, expected) -> tuple[bool, str]`. They perform NO filesystem or subprocess I/O (except `normalize_path`, which may call `os.path.realpath`).
- `normalize_path` is exactly `os.path.normcase(os.path.realpath(p))`.
- The primary checkout is found via the parent of `git rev-parse --git-common-dir` — ordering-independent, never "the first `git worktree list` entry".
- Tests use the project convention: `unittest`, the `load(name)` importlib loader, `ROOT = Path(__file__).resolve().parents[1]`. The integration test class is guarded with `@unittest.skipUnless(shutil.which("git") is not None, "git not available")`.
- Test runner is `py -m pytest`. Full suite must stay green (was 205 passed before this work).
- Doc edits must name `verify_worktree_isolation.py` and `git worktree add` literally, and leave no stale "trust the flag / `isolation:\"worktree\"` gives you a worktree" wording behind.
- YAGNI: no `--json` output, no `worktree_pool.py`, no detect-and-serialize fallback.

---

### Task 1: `verify_worktree_isolation.py` + tests

**Model:** cheapest tier — the plan carries the complete code; this is transcription plus testing.

**Files:**
- Create: `scripts/verify_worktree_isolation.py`
- Test: `tests/test_verify_worktree_isolation.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces (Task 2's doctrine references these): a CLI with two modes — `verify_worktree_isolation.py PATH [PATH ...]` (Admiral pre-wave gate, exit 0/1) and `verify_worktree_isolation.py --here EXPECTED` (Commander self-check, exit 0/1). Pure helpers `normalize_path`, `parse_worktree_list`, `check_distinct_real`, `check_here`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_verify_worktree_isolation.py`:

```python
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PORCELAIN = """worktree C:/Programs/main
HEAD abc123
branch refs/heads/main

worktree C:/Programs/wt/c1
HEAD def456
branch refs/heads/issue-33-c1

worktree C:/Programs/wt/c2
HEAD 789abc
detached
"""


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")

    def test_separator_and_case_fold_equal_on_windows(self):
        a = self.m.normalize_path("C:/Programs/Constellation")
        b = self.m.normalize_path("C:\\Programs\\constellation")
        if os.name == "nt":
            self.assertEqual(a, b)
        else:
            # POSIX is case- and separator-sensitive; assert idempotence instead.
            self.assertEqual(a, self.m.normalize_path(a))

    def test_dot_segments_folded(self):
        with tempfile.TemporaryDirectory() as tmp:
            direct = self.m.normalize_path(tmp)
            dotted = self.m.normalize_path(os.path.join(tmp, "sub", ".."))
            self.assertEqual(direct, dotted)

    def test_symlink_or_junction_resolved(self):
        # realpath must resolve a link to its real target; skip where links
        # cannot be created (Windows without privilege / developer mode).
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "target")
            link = os.path.join(tmp, "link")
            os.mkdir(target)
            try:
                os.symlink(target, link, target_is_directory=True)
            except (OSError, NotImplementedError, ValueError):
                self.skipTest("symlink creation not permitted on this platform")
            self.assertEqual(
                self.m.normalize_path(link), self.m.normalize_path(target)
            )


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")

    def test_extracts_only_worktree_paths(self):
        self.assertEqual(
            self.m.parse_worktree_list(PORCELAIN),
            ["C:/Programs/main", "C:/Programs/wt/c1", "C:/Programs/wt/c2"],
        )

    def test_empty_input_is_empty_list(self):
        self.assertEqual(self.m.parse_worktree_list(""), [])


class CheckDistinctRealTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")
        self.registered = ["/repo/main", "/repo/wt/c1", "/repo/wt/c2"]
        self.primary = "/repo/main"

    def test_distinct_registered_nonprimary_pass(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/wt/c1", "/repo/wt/c2"], self.registered, self.primary
        )
        self.assertTrue(ok, reason)
        self.assertEqual(reason, "")

    def test_unregistered_path_fails(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/wt/ghost"], self.registered, self.primary
        )
        self.assertFalse(ok)
        self.assertIn("ghost", reason)
        self.assertIn("not a registered", reason)

    def test_primary_checkout_rejected(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/main"], self.registered, self.primary
        )
        self.assertFalse(ok)
        self.assertIn("main checkout", reason)

    def test_duplicate_provisioned_paths_fail(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/wt/c1", "/repo/wt/c1"], self.registered, self.primary
        )
        self.assertFalse(ok)
        self.assertIn("same worktree", reason)


class CheckHereTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")

    def test_match_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, reason = self.m.check_here(tmp, tmp)
            self.assertTrue(ok, reason)

    def test_mismatch_names_both(self):
        ok, reason = self.m.check_here("/repo/main", "/repo/wt/c1")
        self.assertFalse(ok)
        self.assertIn("/repo/main", reason)
        self.assertIn("/repo/wt/c1", reason)


HAS_GIT = shutil.which("git") is not None


@unittest.skipUnless(HAS_GIT, "git not available")
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self._git("init", "-q")
        self._git(
            "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "--allow-empty", "-m", "init",
        )
        self.wt = Path(self.tmp.name) / "wt-c1"
        self._git("worktree", "add", "-q", "-b", "issue-33-c1", str(self.wt))
        self._cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self._cwd)
        self.tmp.cleanup()

    def _git(self, *args):
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True, capture_output=True, text=True,
        )

    def test_gate_passes_for_real_worktree(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main([str(self.wt)]), 0)

    def test_gate_rejects_main_checkout(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main([str(self.repo)]), 1)

    def test_gate_rejects_missing_path(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main([str(self.repo / "does-not-exist")]), 1)

    def test_here_passes_from_inside_worktree(self):
        os.chdir(self.wt)
        self.assertEqual(self.m.main(["--here", str(self.wt)]), 0)

    def test_here_fails_from_main_checkout(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main(["--here", str(self.wt)]), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `py -m pytest tests/test_verify_worktree_isolation.py -v`
Expected: collection/error or failures — the module `scripts/verify_worktree_isolation.py` does not exist yet (`spec_from_file_location` returns a loader whose `exec_module` raises `FileNotFoundError`).

- [ ] **Step 3: Write the implementation**

Create `scripts/verify_worktree_isolation.py`:

```python
#!/usr/bin/env python
"""Verify git worktree isolation is real before — and inside — a parallel wave.

The Agent-tool `isolation:"worktree"` parameter is a harness primitive that is a
silent no-op on Windows: subagents launched with it share the single checkout and
collide. Constellation's fix is to stop trusting that flag — the Admiral
provisions a real worktree per Commander with `git worktree add` (which works on
Windows) and hands over the absolute path. This script is the mechanical check on
top of that discipline. See `skills/admiral/references/fleet-doctrine.md`,
"Worktree isolation is a harness no-op on Windows".

Two modes:

  verify_worktree_isolation.py PATH [PATH ...]
      The Admiral's pre-wave gate. Every PATH must exist, be a registered git
      worktree, and be distinct from every other PATH and from the primary (main)
      checkout. Exit 0 if isolation is real for the whole wave, else 1.

  verify_worktree_isolation.py --here EXPECTED
      A Commander's first-step self-check: assert this session's
      `git rev-parse --show-toplevel` is EXPECTED — "am I really in my assigned
      worktree, or did I land in the shared checkout?". Exit 0/1.

The gate is the mechanical guarantee; `--here` is owner-side risk-reduction whose
result the Commander pastes into its return report.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def normalize_path(p: str) -> str:
    """Canonicalize a path for comparison: an absolute real path (symlinks and
    Windows junctions resolved by realpath) with drive-case and `/` vs `\\`
    separators folded by normcase. Two strings naming the same location compare
    equal after this."""
    return os.path.normcase(os.path.realpath(p))


def parse_worktree_list(porcelain: str) -> list[str]:
    """The registered worktree paths from `git worktree list --porcelain` output.
    Each record opens with a `worktree <path>` line; the `HEAD`, `branch`, `bare`,
    `detached`, and blank lines that follow are ignored."""
    paths = []
    for line in porcelain.splitlines():
        if line.startswith("worktree "):
            paths.append(line[len("worktree "):].strip())
    return paths


def check_distinct_real(
    provisioned_paths: list[str], registered: list[str], primary: str
) -> tuple[bool, str]:
    """The pure multi-path decision. `provisioned_paths` are the paths the Admiral
    created; `registered` is `parse_worktree_list` output; `primary` is the main
    checkout. Every provisioned path must be registered, none may be the primary,
    and no two may resolve to the same worktree. Returns (ok, reason); reason is
    "" when ok and names the offending path otherwise."""
    registered_norm = {normalize_path(r) for r in registered}
    primary_norm = normalize_path(primary)
    seen: dict[str, str] = {}
    for raw in provisioned_paths:
        norm = normalize_path(raw)
        if norm == primary_norm:
            return False, f"{raw} is the main checkout, not an isolated worktree"
        if norm not in registered_norm:
            return False, f"{raw} is not a registered git worktree"
        if norm in seen:
            return False, f"{raw} and {seen[norm]} resolve to the same worktree"
        seen[norm] = raw
    return True, ""


def check_here(actual_toplevel: str, expected: str) -> tuple[bool, str]:
    """The pure --here decision: is the current worktree the expected one?"""
    if normalize_path(actual_toplevel) == normalize_path(expected):
        return True, ""
    return (
        False,
        f"you are in {actual_toplevel}, not your assigned worktree {expected} — "
        f"run every git operation inside {expected}",
    )


def _git(*args: str) -> str:
    """Run a read-only git command and return its stripped stdout."""
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def registered_worktrees() -> list[str]:
    return parse_worktree_list(_git("worktree", "list", "--porcelain"))


def primary_checkout() -> str:
    """The main checkout: the parent of the common git dir. Ordering-independent,
    unlike trusting the first `git worktree list` entry (undefined for a bare
    repo)."""
    common = _git("rev-parse", "--git-common-dir")
    return os.path.dirname(os.path.abspath(common))


def current_toplevel() -> str:
    return _git("rev-parse", "--show-toplevel")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "paths", nargs="*", help="provisioned worktree paths to verify (gate mode)"
    )
    parser.add_argument(
        "--here", metavar="EXPECTED",
        help="self-check: assert the current worktree is EXPECTED",
    )
    args = parser.parse_args(argv)

    if args.here is not None:
        if args.paths:
            parser.error("--here takes no positional PATH arguments")
        ok, reason = check_here(current_toplevel(), args.here)
        if ok:
            print(f"worktree OK: in {args.here}")
            return 0
        print(f"wrong worktree: {reason}", file=sys.stderr)
        return 1

    if not args.paths:
        parser.error("give one or more worktree paths, or --here EXPECTED")

    missing = [p for p in args.paths if not os.path.isdir(p)]
    if missing:
        for p in missing:
            print(f"worktree path does not exist: {p}", file=sys.stderr)
        return 1

    ok, reason = check_distinct_real(
        args.paths, registered_worktrees(), primary_checkout()
    )
    if ok:
        print(f"worktree isolation verified: {len(args.paths)} distinct worktrees")
        return 0
    print(f"worktree isolation NOT verified: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `py -m pytest tests/test_verify_worktree_isolation.py -v`
Expected: PASS. The `test_symlink_or_junction_resolved` test may report SKIPPED on a Windows box without symlink privilege — that is acceptable; every other test must pass.

- [ ] **Step 5: Run the full suite**

Run: `py -m pytest tests/ -q`
Expected: all prior tests still pass plus the new ones (was 205 passed; now 205 + the new test methods).

- [ ] **Step 6: Commit**

```bash
git add scripts/verify_worktree_isolation.py tests/test_verify_worktree_isolation.py
git commit -m "feat: verify_worktree_isolation.py — gate + --here self-check (#33)"
```

---

### Task 2: Provisioning doctrine + LAUNCH_ORDER + SKILL edits

**Model:** cheapest tier — exact replacement text is given; this is mechanical doc editing.

**Files:**
- Modify: `skills/admiral/references/fleet-doctrine.md` (add one section)
- Modify: `skills/admiral/templates/LAUNCH_ORDER.template.md` (`## Workspace`, `## Return Shape`)
- Modify: `skills/admiral/SKILL.md` (the line-38 dispatch bullet and the line-54 closeout hygiene item)

**Interfaces:**
- Consumes: the Task 1 CLI — `verify_worktree_isolation.py <path>...` (gate) and `verify_worktree_isolation.py --here <path>` (self-check).
- Produces: nothing for later tasks (final task).

- [ ] **Step 1: Add the fleet-doctrine section**

In `skills/admiral/references/fleet-doctrine.md`, insert this new section immediately **after** the "## Recovery drill (no agent-resume on this harness)" section and **before** "## Adjudication invariants (Admiral errors that bit)":

```markdown
## Worktree isolation is a harness no-op on Windows — provision it yourself

The Agent-tool `isolation:"worktree"` parameter is a **harness primitive that
silently does nothing on Windows**: subagents launched with it run in the shared
checkout, not their own worktree. A parallel wave dispatched in that belief
collides in the single checkout — two Commanders racing a push, three crews
colliding on `git checkout -b`, a commit landing on a sibling's branch. That is
data loss, not friction. (A git-level probe cannot catch it: `git worktree add` in
a temp dir tests *git's* worktree support, which is fine on Windows — it is the
Agent *tool* that skips provisioning — so the probe returns a false green.)

**Do not trust the flag — provision the worktree yourself.** `git worktree add`
works fine on Windows. Before a parallel wave:

1. For each Commander, run `git worktree add <path> -b <branch> <base>` from the
   main checkout, and **log that command and its outcome in the ADMIRAL_LOG** — a
   provisioned worktree is a material fleet action.
2. Hand each Commander its **absolute** worktree path in the LAUNCH_ORDER
   `## Workspace` field, with the instruction to run
   `py scripts/verify_worktree_isolation.py --here <path>` as its first step and
   paste the result into its return report.
3. Gate the wave: `py scripts/verify_worktree_isolation.py <path1> <path2> ...`
   must exit 0 (every path a real, registered worktree, distinct from each other
   and from the main checkout) before you launch. A non-zero exit means isolation
   is not real — fix it; do not launch.

The gate is the **mechanical guarantee**; `--here` is the Commander's own
risk-reduction, surfaced as evidence in its report rather than a hard refusal
(Agent-tool dispatch has no engine chokepoint to refuse at).

**Sweep on the right boundary.** Remove a worktree (`git worktree remove <path>`
then `git worktree prune`) only after its Commander's PR is **merged**, or the
Commander is **confirmed dead with no continuation pending** — never while a live
or recovering Commander still holds it. This is the same "confirm dead before you
touch its worktree" rule the recovery drill already applies.
```

- [ ] **Step 2: Upgrade the LAUNCH_ORDER `## Workspace` field**

In `skills/admiral/templates/LAUNCH_ORDER.template.md`, replace:

```markdown
## Workspace
`<worktree path, branch name, base commit — verify main freshness before dispatch>`
```

with:

```markdown
## Workspace
`<absolute worktree path, provisioned for you via "git worktree add" — branch name, base commit, and the exact add command that created it. Verify main freshness before dispatch. Worktrees lack untracked inputs; see Data Locations.>`
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here <absolute worktree path>` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.
```

- [ ] **Step 3: Extend the LAUNCH_ORDER `## Return Shape` field**

In the same file, replace:

```markdown
## Return Shape
`<the required form of the final report: verdict + evidence + map impact + triage candidates + workflow feedback; where the verdict gets posted>`
```

with:

```markdown
## Return Shape
`<the required form of the final report: verdict + evidence + map impact + triage candidates + workflow feedback; where the verdict gets posted. Include your "verify_worktree_isolation.py --here" confirmation (the matched worktree path) as evidence you worked in isolation.>`
```

- [ ] **Step 4: Update the SKILL.md dispatch bullet (line ~38)**

In `skills/admiral/SKILL.md`, replace the bullet:

```markdown
- One Commander per issue, each in an isolated worktree; pick model tier per issue complexity. Never two commanders in one worktree — stop/confirm-dead the original before launching a continuation into its worktree.
```

with:

```markdown
- One Commander per issue, each in its own worktree you **provision explicitly** with `git worktree add` — the Agent-tool `isolation:"worktree"` flag is a silent no-op on Windows — and verify with `verify_worktree_isolation.py` before the wave; pick model tier per issue complexity. Never two commanders in one worktree — stop/confirm-dead the original before launching a continuation into its worktree. See `references/fleet-doctrine.md`, "Worktree isolation is a harness no-op on Windows".
```

- [ ] **Step 5: Update the SKILL.md closeout hygiene item (line ~54)**

In the same file, replace:

```markdown
4. Repo hygiene: branches merged or dispositioned, worktrees swept, ADMIRAL_LOG archived to main under `.agent-work/archive/`.
```

with:

```markdown
4. Repo hygiene: branches merged or dispositioned, worktrees swept (`git worktree remove` + `git worktree prune`, only after merge or confirmed-dead), ADMIRAL_LOG archived to main under `.agent-work/archive/`.
```

- [ ] **Step 6: Grep for stale wording**

Run: `git grep -n -i "isolation" skills/admiral/ docs/`
Expected: every remaining mention of `isolation:"worktree"` frames it as a no-op to NOT rely on (the new doctrine, SKILL bullet, and spec). No surviving text tells an agent the flag gives them a worktree. If any stale "trust the flag" wording remains, fix it.

- [ ] **Step 7: Commit**

```bash
git add skills/admiral/references/fleet-doctrine.md skills/admiral/templates/LAUNCH_ORDER.template.md skills/admiral/SKILL.md
git commit -m "docs: provision worktrees explicitly; gate + sweep doctrine (#33)"
```

---

## Self-Review

**1. Spec coverage:**
- Strategy "provision explicitly + verify helper" → Task 1 (script) + Task 2 Step 1/2 (doctrine).
- Verify script two modes, pure helpers, `normalize_path` primitive, primary-via-git-common-dir → Task 1 Steps 1/3 + Global Constraints.
- Layered enforcement / `--here` as evidence-in-return-shape → Task 2 Steps 1 and 3.
- Sweep lifecycle (merge or confirmed-dead) → Task 2 Steps 1 and 5.
- ADMIRAL_LOG the `git worktree add` → Task 2 Step 1.
- LAUNCH_ORDER `## Workspace` upgrade → Task 2 Step 2.
- SKILL.md line 38 + 54 → Task 2 Steps 4/5.
- Testing: unit (normalize/parse/check_distinct_real/check_here) + guarded integration → Task 1 Step 1.
- Out-of-scope (no `--json`, no `worktree_pool.py`, no detect-and-serialize) → honored; none appear in any task.
- 8.3/UNC + bare repos out of scope → not implemented (correct); bare-repo robustness is why primary uses git-common-dir.

**2. Placeholder scan:** No "TBD"/"handle edge cases"/"similar to Task N". Every code step carries complete code; every command has an expected result.

**3. Type consistency:** `check_distinct_real(provisioned_paths, registered, primary)` and `check_here(actual_toplevel, expected)` signatures match between the test (Task 1 Step 1), the implementation (Step 3), and the Global Constraints. `normalize_path` / `parse_worktree_list` names match across tests, implementation, and doctrine references. The CLI forms named in Task 2's doctrine (`--here <path>`, `<path>...`) match `main()`'s argparse.
