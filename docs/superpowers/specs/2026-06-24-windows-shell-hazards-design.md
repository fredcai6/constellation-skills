# Windows Shell Hazards — Design

**Issue:** [#35](https://github.com/fredcai6/constellation-skills/issues/35) — Windows
shell hazards: prescribe `gh pr create -F file`, and make engine command-checks
cmd.exe-safe

**Date:** 2026-06-24

## Problem

The 2026-06-24 feedback harvest surfaced two **independent** Windows shell hazards
that keep biting fleets. They share a root cause — Windows runs a different shell
than the POSIX one every author assumes — but they bite in different places, so
each gets its own fix.

### Hazard A — PowerShell PR bodies (story_time, 3×, recurred epic-1 → epic-2)

On Windows PowerShell, two ways of passing a multi-line PR body to `gh pr create`
**both fail**: a bash-style heredoc, and a PowerShell `@'...'@` here-string fed to
`--body`. Only writing the body to a file and using `gh pr create -F <file>` (a.k.a.
`--body-file`) is reliable. Each fresh fleet rediscovers this by hand because no
shipped template prescribes it. A subtle trap compounds it: `@'...'@` here-strings
*do* work for `git commit -m`, so an author who learned the here-string trick for
commits wrongly assumes it also fixes PR bodies.

### Hazard B — engine `command`-checks run under cmd.exe (f1Brainz)

The checklist engine runs `command`-kind postcondition/precondition checks via
`subprocess.run(chk["command"], shell=True, ...)` ([checklist_engine.py:316](../../../scripts/checklist_engine.py)).
On Windows `shell=True` invokes **cmd.exe**, not a POSIX shell. A check authored in
POSIX form — `cd '...' && pytest ... | grep -qE ...` — silently **false-FAILs**:
cmd.exe has no `grep`, and its `&&` / quoting semantics differ. The failure is
latent (it only bites a check that uses pipes, `&&`, or POSIX tools) and silent (the
check just reports a non-zero exit, indistinguishable from a real test failure). A
crew's RED-phase bash checks failed this way and had to be hand-rewritten cmd-safe.

A grounding fact that bounds the blast radius and de-risks the fix: **every check
the framework itself ships is a `python <skill-dir>/scripts/....py <args>`
invocation** — cmd- and bash-safe in both shells. The checks that bite are
**authored** test/verify commands dropped into the `c1` "`<exact test command>`"
slots of `EXECUTE_PLAN.template.json` / `IMPLEMENTER_PLAN.template.json`. So routing
*all* command checks through a POSIX shell fixes the hazard and breaks **zero**
existing framework checks.

## Strategy

**Hazard A — prescribe the reliable form in doctrine + templates.** Pure
documentation; no code. State the rule (write the body to a file, use
`gh pr create -F <file>`) and correct the here-string misconception, where the
agents that open PRs will read it.

**Hazard B — route command-checks through a POSIX shell (the real fix).** Stop
running POSIX-form checks under cmd.exe. The engine finds a POSIX shell (on Windows,
Git for Windows bundles `bash` — and Constellation already requires git) and runs
`[bash, "-c", command]` instead of `cmd.exe /c command`. Authored `grep` / `&&` /
pipe checks then work, and — the larger win — a check behaves **identically** on
Windows and on Mac/Linux instead of being a cross-platform coin-flip.

This is deliberately *not* the issue's alternative ("document that checks must be
cmd-safe + lint plan snippets for shell-isms"). That alternative permanently
constrains every check author to cmd.exe's lowest common denominator — the
"confirmed into a permanent workaround instead of fixed" pattern this fold-back arc
exists to kill. Routing through bash fixes the mechanism instead.

**Honest about the ceiling.** On the rare Windows box with no bash (git installed
without Git for Windows — e.g. a WSL-only git), the engine **falls back to cmd.exe**
and stamps a `shell: "cmd-fallback"` marker into the check's evidence. This is
strictly better than today: the framework's own `python ...` checks still pass (they
are cmd-safe), and the residual silent-failure risk on an authored bash check
becomes **visible in the evidence** rather than hidden — the same
evidence-in-return-shape honesty #33 used for `--here`. Failing every command check
outright when bash is absent was rejected: it would regress setups that work today
(their cmd-safe python checks included) for a misconfiguration that, given the git
requirement, is rare.

## Behavior

### Component 1 — engine POSIX-shell routing (`scripts/checklist_engine.py`)

One new seam replaces the inline `subprocess.run(chk["command"], shell=True, ...)`
at the `kind == "command"` branch. Three helpers, the first pure and the fiddliest:

- **`_bash_candidates_from_git(git_path: str) -> list[str]`** — *pure*, no
  filesystem access. Given the path to a `git` executable (e.g.
  `C:\Program Files\Git\cmd\git.exe`), return the candidate `bash.exe` paths to
  probe, derived from git's install layout: `bash.exe` under `bin/` and `usr/bin/`
  of git's parent and grandparent directories (Git for Windows ships
  `…\Git\bin\bash.exe` and `…\Git\usr\bin\bash.exe` while `git.exe` is commonly on
  `PATH` only via `…\Git\cmd\git.exe`, so `shutil.which("bash")` alone misses it).
  Returns paths in priority order; performs no existence check. This is the
  bug-prone piece (like #33's `normalize_path`) and is unit-tested directly with a
  sample path, no git install required.

- **`_find_posix_shell() -> str | None`** — locate a POSIX shell, touching the
  filesystem/`PATH`:
  - Non-Windows: `shutil.which("sh")` (POSIX always has `/bin/sh`).
  - Windows: `shutil.which("bash")`; else the first `_bash_candidates_from_git(g)`
    entry that exists on disk, where `g = shutil.which("git")`; else
    `shutil.which("sh")`; else `None`.

- **`_run_check_command(command: str) -> tuple[subprocess.CompletedProcess, str]`**
  — run a check command and report which shell ran it. If `_find_posix_shell()`
  returns a shell, run `subprocess.run([shell, "-c", command], capture_output=True,
  text=True)` and return marker `"posix"`. Otherwise run
  `subprocess.run(command, shell=True, capture_output=True, text=True)` (today's
  cmd.exe path) and return marker `"cmd-fallback"`.

The `kind == "command"` branch calls `_run_check_command` and **stamps the marker
into the evidence payload**, extending the existing `{"cmd": ..., "exit": ...}` to
`{"cmd": ..., "exit": ..., "shell": marker}`. Nothing else in that branch changes:
it still sets `cond["satisfied"]` from `returncode == 0`, appends one
`command-output` evidence item, and sets `satisfied_by` on success.

`_git` ([checklist_engine.py:239](../../../scripts/checklist_engine.py)) is
**untouched** — it already shells out in list form (`shell=False`) and is cmd-safe.
The `artifact` and `git-change-policy` check kinds are untouched.

### Component 2 — doctrine + templates

- **`skills/admiral/references/fleet-doctrine.md`** — a new `## Windows shell
  hazards` section (placed after "Worktree isolation is a harness no-op on Windows"
  and before "Adjudication invariants", keeping the platform-hazard sections
  together), with two parts:
  - **PR bodies (Hazard A):** on Windows, write the PR body to a temp file and run
    `gh pr create -F <file>` (or `--body-file <file>`). A bash heredoc and a
    PowerShell `@'...'@` here-string passed to `--body` both fail for PR bodies.
    `@'...'@` here-strings *do* work for `git commit -m` — do not generalize that to
    `gh pr create --body`.
  - **Command checks (Hazard B):** the engine runs `command`-kind checks under a
    POSIX shell (bash), so authored test/verify commands may freely use `grep`,
    `&&`, and pipes and will behave the same on Windows as on Mac/Linux. On a box
    with no bash the engine falls back to cmd.exe and records `shell: cmd-fallback`
    in the check's evidence — a check that needs bash will visibly fail there rather
    than silently, so treat a `cmd-fallback` marker as "install Git Bash".

- **`skills/admiral/templates/LAUNCH_ORDER.template.md`** — extend the `## Return
  Shape` field (which already names where the verdict gets posted) with the
  operational PR-body rule: when this Commander opens its PR on Windows, write the
  body to a file and use `gh pr create -F <file>` — never a heredoc or `@'...'@`
  here-string `--body` (see fleet-doctrine "Windows shell hazards"). This is the
  Admiral→Commander handoff path, covering the case where the Commander is the
  PR-opener; the Admiral's own copy lives in fleet-doctrine above.

- **`skills/workbench/references/checklist-engine.md`** — the "Evidence shape"
  bullet (`command` postconditions must exit 0) gains a clause: command checks run
  under a POSIX shell (bash); the `command-output` evidence's `shell` field records
  `posix` or `cmd-fallback`.

- **`docs/CHECKLIST_SCHEMA.md`** — the Evidence `payload` note for `command-output`
  records the new `shell` field (`posix` | `cmd-fallback`), and the override-policy
  paragraph's mention of the failed-`command` evidence record stays consistent with
  it.

## Testing

**Component 1 (TDD), in `tests/test_checklist_engine.py`** (mirroring its existing
`PASS_COMMAND` / `FAIL_COMMAND` cross-platform style):

- `_bash_candidates_from_git` returns the expected `bin/bash.exe` and
  `usr/bin/bash.exe` candidates (parent and grandparent) for a sample
  `…\Git\cmd\git.exe` path — pure, no git install, runs on every platform.
- `_find_posix_shell` monkeypatched: with `shutil.which("bash")` returning a path it
  picks that; with all lookups returning `None` on a simulated Windows it returns
  `None`.
- `_run_check_command` with `_find_posix_shell` monkeypatched to `None` returns
  marker `"cmd-fallback"` and still runs the command (cmd path); the
  command-check branch then stamps `shell: "cmd-fallback"` into the evidence.
- A **guarded integration test** (`@unittest.skipUnless` a POSIX shell is found)
  runs a genuinely POSIX-form check, `echo isolated | grep -q isolated`, as a
  `command` postcondition and asserts: it **passes** (exit 0, gate advances) and its
  `command-output` evidence carries `shell: "posix"`. On cmd.exe that same command
  would false-FAIL, so this test is the regression guard for the fix.
- The existing command-check tests (`test_command_postcondition_pass_completes`,
  `…_fail_…`, `test_command_output_records_exit_status_on_failure`, etc.) now
  exercise the routed path unchanged and must stay green — the real-world guard that
  routing broke nothing.

**Component 2** is a documentation edit, gated by **review against this spec**
(mirroring #32/#33, whose doc tasks were reviewed, not unit-tested): the
fleet-doctrine section, the LAUNCH_ORDER `## Return Shape` edit, and the
checklist-engine.md / CHECKLIST_SCHEMA.md edits name `gh pr create -F`, the
here-string-is-for-commits-not-PR-bodies correction, the POSIX-shell routing, and
the `shell` evidence field exactly, with no stale "runs under cmd" or
"here-strings fix PR bodies" wording left behind.

**Full suite:** must remain green (currently 222 passed / 1 skipped on main).

## Out of scope (YAGNI)

- **No lint-for-shell-isms tool.** Routing through bash makes POSIX-form checks
  correct; a linter that flags `grep`/`&&` would be solving the problem the routing
  dissolves.
- **No `--shell` / shell-path config knob.** Auto-detection (bash → cmd-fallback) is
  sufficient; a knob is unneeded surface until the field asks for it.
- **No change to `_git`, `artifact`, or `git-change-policy` checks.** Only
  `kind == "command"` runs author-supplied shell text; the others are list-form or
  internal.
- **No caching of the shell lookup.** `_find_posix_shell` runs per command check;
  the cost (a couple of `which` calls) is negligible against running the check
  itself.
- **No new explicit "open a PR" spine step.** PR-opening authority is Charter-gated
  (ORCHESTRATOR_CONTEXT "Commander may open PRs directly"); the rule rides in
  fleet-doctrine + the LAUNCH_ORDER handoff rather than a new mandated gate.
- **8.3 short-form / `\\?\` UNC git paths** in `_bash_candidates_from_git` are not
  specially canonicalized; `shutil.which` returns normal long paths in practice, and
  the `shutil.which("bash")` / `which("sh")` fallbacks cover odd layouts.
