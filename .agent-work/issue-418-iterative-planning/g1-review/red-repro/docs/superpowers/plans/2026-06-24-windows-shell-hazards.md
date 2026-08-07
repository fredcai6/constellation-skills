# Windows Shell Hazards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the checklist engine run `command`-kind checks under a POSIX shell on Windows (with an honest cmd.exe fallback), and prescribe the reliable `gh pr create -F <file>` form in doctrine + templates.

**Architecture:** One new seam in `scripts/checklist_engine.py` (three helpers + a two-line change to the `kind == "command"` branch) routes check commands through bash when found, else falls back to cmd.exe and stamps a visible `shell` marker into the evidence. A second, doc-only task adds a "Windows shell hazards" doctrine section and propagates the PR-body rule to the templates that govern PR creation.

**Tech Stack:** Python 3 (stdlib `subprocess`, `shutil`, `os`, `pathlib.PureWindowsPath`); `unittest` tests run via `py -m pytest`; Markdown + JSON template docs.

**Spec:** `docs/superpowers/specs/2026-06-24-windows-shell-hazards-design.md`

## Global Constraints

- The two shell marker values are **exactly** the string literals `"posix"` and `"cmd-fallback"` — identical in `scripts/checklist_engine.py`, `skills/workbench/references/checklist-engine.md`, and `docs/CHECKLIST_SCHEMA.md`.
- `shutil.which("bash")` is the **primary** shell lookup on Windows; the git-derived candidates are a **backstop** reached only when `which("bash")` fails. Guard `_bash_candidates_from_git` behind `if git:` — never call it with `None`.
- `_bash_candidates_from_git` is **pure** (no filesystem access) and uses `pathlib.PureWindowsPath` so it parses Windows paths identically on any host OS; it walks **4 ancestor levels** of the git path (covering `…\Git\mingw64\bin\git.exe`, `…\Git\cmd\git.exe`, and `…\Git\bin\git.exe`).
- The cmd-fallback branch is byte-for-byte today's call: `subprocess.run(command, shell=True, capture_output=True, text=True)`.
- Do **not** touch `_git`, the `artifact` check kind, or the `git-change-policy` check kind — only the `kind == "command"` branch changes.
- Adding the `shell` key to the `command-output` payload must stay backward-compatible (all consumers use keyed access; no exhaustive key-set assertion).
- The full suite must stay green. Baseline on this branch's merge-base: **222 passed, 1 skipped** (the 1 skip is the unrelated symlink-permission test in `test_verify_worktree_isolation.py`).
- Unit tests must run on any platform with no real git/bash install; the one integration test is guarded by `@unittest.skipUnless(E._find_posix_shell(), ...)`.

---

### Task 1: Engine POSIX-shell routing

**Files:**
- Modify: `scripts/checklist_engine.py` (imports near lines 12-18; insert three helpers before `_check_condition` at line 301; edit the `kind == "command"` branch at lines 315-330)
- Test: `tests/test_checklist_engine.py` (add `from unittest import mock` near the top imports; add a new `PosixShellRoutingTests` class)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces (relied on by the tests, and named in Task 2's docs):
  - `_bash_candidates_from_git(git_path: str) -> list[str]` — pure; candidate `bash.exe` paths.
  - `_find_posix_shell() -> str | None` — the shell path, or `None`.
  - `_run_check_command(command: str) -> tuple[subprocess.CompletedProcess, str]` — `(proc, marker)` where `marker` is `"posix"` or `"cmd-fallback"`.
  - The `command-output` evidence payload gains a `"shell"` key carrying that marker.

- [ ] **Step 1: Write the failing tests**

Add `from unittest import mock` to the import block at the top of `tests/test_checklist_engine.py` (it currently imports `copy, importlib.util, json, sys, tempfile, unittest` and `from pathlib import Path`). Then append this class to the file:

```python
class PosixShellRoutingTests(unittest.TestCase):
    def test_bash_candidates_from_mingw64_git(self):
        # which("git") on a stock box resolves to the mingw64 copy; Git root is the
        # great-grandparent, so a parent/grandparent-only walk would miss bash.
        cands = E._bash_candidates_from_git(r"C:\Program Files\Git\mingw64\bin\git.exe")
        self.assertIn(r"C:\Program Files\Git\bin\bash.exe", cands)
        self.assertIn(r"C:\Program Files\Git\usr\bin\bash.exe", cands)

    def test_bash_candidates_from_cmd_git(self):
        cands = E._bash_candidates_from_git(r"C:\Program Files\Git\cmd\git.exe")
        self.assertIn(r"C:\Program Files\Git\bin\bash.exe", cands)
        self.assertIn(r"C:\Program Files\Git\usr\bin\bash.exe", cands)

    def test_find_posix_shell_prefers_which_bash(self):
        with mock.patch.object(E.os, "name", "nt"), \
             mock.patch.object(E.shutil, "which",
                               side_effect=lambda n: r"X:\bash.exe" if n == "bash" else None):
            self.assertEqual(E._find_posix_shell(), r"X:\bash.exe")

    def test_find_posix_shell_guards_none_git(self):
        # which() returns None for everything: git is None, so the if-guard must
        # prevent _bash_candidates_from_git(None) from ever being called.
        with mock.patch.object(E.os, "name", "nt"), \
             mock.patch.object(E.shutil, "which", return_value=None), \
             mock.patch.object(E, "_bash_candidates_from_git",
                               side_effect=AssertionError("called with None git")):
            self.assertIsNone(E._find_posix_shell())

    def test_run_check_command_cmd_fallback_marker(self):
        with mock.patch.object(E, "_find_posix_shell", return_value=None):
            proc, marker = E._run_check_command(PASS_COMMAND)
        self.assertEqual(marker, "cmd-fallback")
        self.assertEqual(proc.returncode, 0)

    def test_command_evidence_stamps_cmd_fallback_marker(self):
        with mock.patch.object(E, "_find_posix_shell", return_value=None):
            cl = gated(g1=gate("g1", "in-progress", command=PASS_COMMAND))
            E.advance(cl, "g1")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["payload"]["shell"], "cmd-fallback")

    @unittest.skipUnless(E._find_posix_shell(), "no POSIX shell found")
    def test_posix_routing_runs_pipe_and_marks_evidence(self):
        # The shell:"posix" assertion is the real guard — it proves the command was
        # routed through bash. (The command's pass/fail alone does not discriminate:
        # where Git's usr\bin is on PATH, grep/pipes also pass under cmd.exe.)
        cl = gated(g1=gate("g1", "in-progress", command="echo isolated | grep -q isolated"))
        E.advance(cl, "g1")
        self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
        ev = cl["tasks"]["g1"]["evidence"][-1]
        self.assertEqual(ev["payload"]["shell"], "posix")
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `py -m pytest tests/test_checklist_engine.py::PosixShellRoutingTests -v`
Expected: errors/failures — `AttributeError: module 'checklist_engine' has no attribute '_bash_candidates_from_git'` (and `_find_posix_shell` / `_run_check_command`), and the evidence tests fail because the payload has no `shell` key.

- [ ] **Step 3: Add the imports**

In `scripts/checklist_engine.py`, the import block is currently:

```python
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
```

Change it to add `os` and `shutil`, and `PureWindowsPath`:

```python
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
```

- [ ] **Step 4: Add the three helpers**

In `scripts/checklist_engine.py`, immediately **before** the `def _check_condition(` definition (currently line 301), insert:

```python
def _bash_candidates_from_git(git_path: str) -> list[str]:
    """Candidate bash.exe paths derived from a git executable path. Windows
    backstop for when `git` is on PATH but its bash directory is not.

    `shutil.which("git")` resolves git to varying depths — `…\\Git\\mingw64\\bin\\git.exe`
    (Git root = great-grandparent), `…\\Git\\cmd\\git.exe` (grandparent), or
    `…\\Git\\bin\\git.exe` (parent) — while bash always lives at `…\\Git\\bin\\bash.exe`
    and `…\\Git\\usr\\bin\\bash.exe`. Walk up 4 ancestor directories and, for each,
    emit both bash locations. Pure: no filesystem access (the caller filters by
    existence). Uses PureWindowsPath so it parses Windows paths the same on any host
    OS — this helper only runs on Windows but its unit tests run anywhere."""
    candidates: list[str] = []
    d = PureWindowsPath(git_path).parent
    for _ in range(4):
        candidates.append(str(d / "bin" / "bash.exe"))
        candidates.append(str(d / "usr" / "bin" / "bash.exe"))
        d = d.parent
    return candidates


def _find_posix_shell() -> str | None:
    """Locate a POSIX shell to run `command` checks under: bash on Windows, sh on
    POSIX. Returns the shell path, or None if none is found. On Windows
    `shutil.which("bash")` is the primary lookup (Git for Windows usually puts its
    bash dir on PATH); the git-derived candidates are a backstop for when git is on
    PATH but bash is not."""
    if os.name != "nt":
        return shutil.which("sh")
    found = shutil.which("bash")
    if found:
        return found
    git = shutil.which("git")
    if git:
        for cand in _bash_candidates_from_git(git):
            if os.path.isfile(cand):
                return cand
    return shutil.which("sh")


def _run_check_command(command: str) -> tuple[subprocess.CompletedProcess, str]:
    """Run a `command`-kind check. Route it through a POSIX shell when one is found
    (so authored grep/&&/pipe checks behave the same on Windows as on POSIX);
    otherwise fall back to the platform shell (cmd.exe on Windows) and flag that in
    the marker. Returns (completed process, marker) where marker is "posix" or
    "cmd-fallback"."""
    shell = _find_posix_shell()
    if shell:
        proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
        return proc, "posix"
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    return proc, "cmd-fallback"
```

- [ ] **Step 5: Route the command branch through the helper**

In `scripts/checklist_engine.py`, the `kind == "command"` branch of `_check_condition` is currently:

```python
    if kind == "command":
        proc = subprocess.run(chk["command"], shell=True, capture_output=True, text=True)
        cond["satisfied"] = proc.returncode == 0
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "command-output",
                "payload": {"cmd": chk["command"], "exit": proc.returncode},
                "produced_by": "engine",
                "ts": "",
            }
        )
        if cond["satisfied"]:
            cond["satisfied_by"] = eid
        return cond["satisfied"]
```

Replace the first two lines and the payload so it reads:

```python
    if kind == "command":
        proc, shell_marker = _run_check_command(chk["command"])
        cond["satisfied"] = proc.returncode == 0
        eid = _new_evidence_id(t)
        t.setdefault("evidence", []).append(
            {
                "id": eid,
                "type": "command-output",
                "payload": {"cmd": chk["command"], "exit": proc.returncode, "shell": shell_marker},
                "produced_by": "engine",
                "ts": "",
            }
        )
        if cond["satisfied"]:
            cond["satisfied_by"] = eid
        return cond["satisfied"]
```

- [ ] **Step 6: Run the new tests to verify they pass**

Run: `py -m pytest tests/test_checklist_engine.py::PosixShellRoutingTests -v`
Expected: PASS for all 7 methods (the `test_posix_routing_runs_pipe_and_marks_evidence` integration test passes where a POSIX shell exists — e.g. a Windows box with Git Bash or any POSIX host — and is skipped otherwise).

- [ ] **Step 7: Run the full suite to verify no regression**

Run: `py -m pytest -q`
Expected: the existing command-check tests (`test_command_postcondition_pass_completes`, `…_fail_…`, `test_command_output_records_exit_status_on_failure`, etc.) still pass — they now route through `_find_posix_shell` and run `PASS_COMMAND`/`FAIL_COMMAND` (a backslash-bearing Windows python path) under `bash -c`, which is verified-safe. Net: previous total **+7** new tests, with **0** regressions (one of the 7 may report skipped if no POSIX shell is present in the runner).

- [ ] **Step 8: Commit**

```bash
git add scripts/checklist_engine.py tests/test_checklist_engine.py
git commit -m "feat: route engine command-checks through a POSIX shell (#35)

shell=True ran command-kind checks under cmd.exe on Windows, silently
false-FAILing authored grep/&&/pipe checks. Route them through bash when found
(_find_posix_shell), falling back to cmd.exe with a visible shell:cmd-fallback
evidence marker when not. _bash_candidates_from_git is the Windows backstop for
git-on-PATH-but-bash-not.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Doctrine + templates

Documentation only — no automated tests (mirrors #32/#33, whose doc tasks were review-gated). The reviewer checks each edit against the spec: the strings below appear, and no stale "runs under cmd" or "here-strings fix PR bodies" wording remains.

**Files:**
- Modify: `skills/admiral/references/fleet-doctrine.md` (insert a section after the "Worktree isolation…" section ending at line 114, before "## Adjudication invariants" at line 116)
- Modify: `skills/admiral/templates/LAUNCH_ORDER.template.md` (the `## Return Shape` field, lines 40-41)
- Modify: `skills/commander/templates/COMMANDER_SPINE.template.json` (the `archive` step `imperative`, line 116)
- Modify: `skills/workbench/references/checklist-engine.md` (the "Evidence shape" bullet, line 83)
- Modify: `docs/CHECKLIST_SCHEMA.md` (the override-policy paragraph, line 176; the Evidence `payload` row, line 204)

**Interfaces:**
- Consumes from Task 1: the marker literals `"posix"` / `"cmd-fallback"` and the `command-output` payload's `shell` field — the docs must name them identically.
- Produces: nothing code depends on.

- [ ] **Step 1: Add the fleet-doctrine section**

In `skills/admiral/references/fleet-doctrine.md`, insert this section between the end of the "Worktree isolation is a harness no-op on Windows" section (line 114) and the "## Adjudication invariants (Admiral errors that bit)" heading (line 116):

```markdown
## Windows shell hazards (PR bodies and command-checks)

Two Windows shell traps bit fleets repeatedly; both come from Windows running a
different shell than the POSIX one every author assumes.

**PR bodies — use `gh pr create -F <file>`.** On Windows PowerShell, a multi-line PR
body fails both as a bash heredoc and as a PowerShell `@'...'@` here-string passed to
`--body`. Write the body to a temp file and run `gh pr create -F <file>` (or
`--body-file <file>`) — the only reliable form. Note the trap: `@'...'@` here-strings
*do* work for `git commit -m`, so do not assume they also work for
`gh pr create --body`. They do not.

**Command-checks run under bash.** The checklist engine runs `command`-kind checks
(postconditions/preconditions) under a POSIX shell, so an authored test/verify
command may freely use `grep`, `&&`, and pipes and will behave the same on Windows as
on Mac/Linux. On a box with no bash on `PATH` (git installed without Git for Windows)
the engine falls back to cmd.exe and stamps `shell: cmd-fallback` into the check's
evidence — a check that needs bash then visibly fails rather than silently
false-FAILing, so read a `cmd-fallback` marker as "install Git Bash, then re-run".
```

- [ ] **Step 2: Extend the LAUNCH_ORDER `## Return Shape` field**

In `skills/admiral/templates/LAUNCH_ORDER.template.md`, the `## Return Shape` section is currently:

```markdown
## Return Shape
`<the required form of the final report: verdict + evidence + map impact + triage candidates + workflow feedback; where the verdict gets posted. Include your "verify_worktree_isolation.py --here" confirmation (the matched worktree path) as evidence you worked in isolation.>`
```

Append one line after the placeholder so it reads:

```markdown
## Return Shape
`<the required form of the final report: verdict + evidence + map impact + triage candidates + workflow feedback; where the verdict gets posted. Include your "verify_worktree_isolation.py --here" confirmation (the matched worktree path) as evidence you worked in isolation.>`
When you open the PR on Windows, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc or a PowerShell `@'...'@` here-string `--body` (both fail for PR bodies; here-strings work for `git commit -m` only). See `references/fleet-doctrine.md`, "Windows shell hazards".
```

- [ ] **Step 3: Add the PR-body rule to the COMMANDER_SPINE archive step**

In `skills/commander/templates/COMMANDER_SPINE.template.json`, the `archive` step's `imperative` (line 116) begins:

> `Commit all remaining work, including the appended .agent-work/AGENT_FEEDBACK.md entry. Push the branch to remote. Move .agent-work/<work-id>/ to ...`

Insert the PR-body sentence after `Push the branch to remote.` so that substring becomes:

> `Push the branch to remote. When you open a PR on Windows, write the body to a temp file and use gh pr create -F <file> — a bash heredoc and a PowerShell @'...'@ here-string both fail for gh pr create --body (here-strings work for git commit -m, not PR bodies). Move .agent-work/<work-id>/ to ...`

This is a single JSON string value — use no double-quotes or backticks in the inserted text (as above) so the JSON stays valid. After editing, verify the file still parses:

Run: `py -c "import json; json.load(open(r'skills/commander/templates/COMMANDER_SPINE.template.json', encoding='utf-8'))"`
Expected: no output, exit 0 (valid JSON).

- [ ] **Step 4: Extend the checklist-engine.md "Evidence shape" bullet**

In `skills/workbench/references/checklist-engine.md`, the bullet at line 83 is currently:

```markdown
- **Evidence shape** — `command` postconditions must exit 0; `artifact` postconditions need a matching evidence item present. Quality is judged by the reviewer/human, not the engine.
```

Replace it with:

```markdown
- **Evidence shape** — `command` postconditions must exit 0; `artifact` postconditions need a matching evidence item present. Quality is judged by the reviewer/human, not the engine. `command` checks run under a POSIX shell (bash) so authored `grep`/`&&`/pipe checks behave the same on every platform; the `command-output` evidence's `shell` field records which shell ran it — `posix`, or `cmd-fallback` on a Windows box with no bash (where a POSIX-only check visibly fails rather than silently false-FAILing).
```

- [ ] **Step 5: Record the `shell` field in CHECKLIST_SCHEMA.md**

In `docs/CHECKLIST_SCHEMA.md`, the override-policy paragraph (line 176) currently contains the clause:

> `... and a failed \`command\` check leaves a \`command-output\` evidence record with its exit status.`

Extend that clause to:

> `... and a failed \`command\` check leaves a \`command-output\` evidence record with its exit status and a \`shell\` field naming the shell that ran it (\`posix\`, or \`cmd-fallback\` on a bash-less Windows box). \`command\` checks run under a POSIX shell so authored \`grep\`/\`&&\`/pipe checks are portable.`

Then the Evidence `payload` table row (line 204) is currently:

```markdown
| `payload` | object | command output, diff ref, decision text, verdict, packet ref; for `waiver`: `{cond, authority, reason, forced}`; for `artifact-policy`: `{mode, violations, files_checked}` (the violations a `git-change-policy` check found, so a later waiver records which rule was bypassed) |
```

Replace it with (adds the `command-output` shape up front):

```markdown
| `payload` | object | command output, diff ref, decision text, verdict, packet ref; for `command-output`: `{cmd, exit, shell}` where `shell` is `posix` or `cmd-fallback` (which shell ran the check); for `waiver`: `{cond, authority, reason, forced}`; for `artifact-policy`: `{mode, violations, files_checked}` (the violations a `git-change-policy` check found, so a later waiver records which rule was bypassed) |
```

- [ ] **Step 6: Verify no stale wording and consistent markers**

Run: `py -m pytest -q`
Expected: full suite still green (no code changed in Task 2; this confirms the JSON edit didn't break the template-loading tests).

Then scan for stale/contradictory wording and confirm the marker literals are consistent:

```bash
git grep -n "here-string" -- skills docs            # must NOT claim here-strings fix PR bodies / gh pr create --body
git grep -n "cmd-fallback" -- scripts skills docs   # appears in checklist_engine.py, fleet-doctrine.md, checklist-engine.md, CHECKLIST_SCHEMA.md
git grep -n "posix" -- scripts skills docs           # same set carries the "posix" marker
```
Expected: every `here-string` mention ties the here-string to `git commit -m` (never to `gh pr create --body`); `cmd-fallback` and `posix` appear with identical spelling in the engine code and all three doc files.

- [ ] **Step 7: Commit**

```bash
git add skills/admiral/references/fleet-doctrine.md skills/admiral/templates/LAUNCH_ORDER.template.md skills/commander/templates/COMMANDER_SPINE.template.json skills/workbench/references/checklist-engine.md docs/CHECKLIST_SCHEMA.md
git commit -m "docs: Windows shell hazards — gh pr create -F + command-checks under bash (#35)

Fleet-doctrine 'Windows shell hazards' section (PR bodies use gh pr create -F;
@'...'@ here-strings fix git commit -m, not PR bodies). PR-body rule propagated to
LAUNCH_ORDER Return Shape and the COMMANDER_SPINE archive step (covers the solo
Commander). checklist-engine.md + CHECKLIST_SCHEMA.md record the POSIX-shell routing
and the new shell evidence field.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- Component 1 `_bash_candidates_from_git` / `_find_posix_shell` / `_run_check_command` / evidence marker → Task 1 Steps 3-5. ✓
- 4-ancestor walk + both-input test → Task 1 Step 1 (`test_bash_candidates_from_mingw64_git` + `…_cmd_git`) and Step 4. ✓
- `which("bash")` primary, `if g:` guard → Step 4 helper + `test_find_posix_shell_prefers_which_bash` / `…_guards_none_git`. ✓
- cmd-fallback preserves today's call + visible marker → Step 4 (`_run_check_command` else-branch) + `test_run_check_command_cmd_fallback_marker` / `…_stamps_cmd_fallback_marker`. ✓
- Integration test asserts `shell:"posix"` as the guard → `test_posix_routing_runs_pipe_and_marks_evidence`. ✓
- Component 2 fleet-doctrine / LAUNCH_ORDER / COMMANDER_SPINE / checklist-engine.md / CHECKLIST_SCHEMA.md → Task 2 Steps 1-5. ✓ (COMMANDER_SPINE covers the solo-Commander reach.)
- `_git`/`artifact`/`git-change-policy` untouched → not modified by any step. ✓

**2. Placeholder scan:** No TBD/TODO/"handle edge cases"/"similar to". The `<file>` / `<work-id>` / `…` tokens are literal template/CLI placeholders quoted from the real files, not plan gaps.

**3. Type consistency:** `_bash_candidates_from_git(str) -> list[str]`, `_find_posix_shell() -> str | None`, `_run_check_command(str) -> tuple[CompletedProcess, str]`, and the `"shell"` payload key are spelled identically in Steps 3-5, the tests (Step 1), and Task 2's docs. Marker literals `"posix"` / `"cmd-fallback"` are identical everywhere.
