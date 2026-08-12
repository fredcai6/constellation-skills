Closes #35.

## The finding

Two **independent** Windows shell hazards from the 2026-06-24 dogfooding harvest, one root cause — Windows runs a different shell than the POSIX one every author assumes:

- **A — PowerShell PR bodies (story_time, 3×, recurred epic-1 → epic-2).** A multi-line PR body fails both as a bash heredoc *and* as a PowerShell `@'...'@` here-string passed to `gh pr create --body`. Only writing the body to a file and using `gh pr create -F <file>` is reliable. Each fresh fleet rediscovered it by hand because no template prescribed it — compounded by a trap: `@'...'@` here-strings *do* work for `git commit -m`, so authors wrongly generalized them to PR bodies.
- **B — engine `command`-checks ran under cmd.exe (f1Brainz).** The checklist engine ran `command`-kind checks via `subprocess.run(cmd, shell=True)` = cmd.exe on Windows, so a POSIX-form check (`cd '…' && … | grep -qE …`) silently **false-FAILed**: no `grep`, different `&&`/quoting semantics. Latent and silent — a crew's RED-phase bash checks failed this way and had to be hand-rewritten cmd-safe.

## The strategy — fix the mechanism, don't enshrine the workaround

For B, the issue offered two directions: route checks through a POSIX shell, **or** document that every check must be cmd-safe + lint for shell-isms. The second permanently constrains every check author to cmd.exe's lowest common denominator — the "confirmed into a permanent workaround instead of fixed" pattern this fold-back arc exists to kill. So we **route command-checks through a POSIX shell.** A grounding fact made this safe: every *framework* command check is a `python <skill-dir>/scripts/….py` call (cmd- and bash-safe both); the checks that bite are **authored** test/verify commands. Routing all of them through bash fixes the hazard and breaks zero framework checks.

## The change

**Engine (`scripts/checklist_engine.py`).** Three helpers replace the inline `shell=True` call:

- `_bash_candidates_from_git(git_path)` — *pure*; derives candidate `bash.exe` paths from a git path by walking 4 ancestor levels via `PureWindowsPath`. This is the fiddly piece: a stock `shutil.which("git")` resolves to `…\Git\mingw64\bin\git.exe`, where the Git root is the **great-grandparent** — a naive parent/grandparent walk misses `…\Git\bin\bash.exe`. Verified correct across all three git layouts (`mingw64\bin`, `cmd`, `bin`).
- `_find_posix_shell()` — `shutil.which("bash")` is the **primary** lookup (a stock Git-for-Windows install puts its bash dir on `PATH`); the git-derived candidates are a **backstop**, guarded by `if git:`; falls to `which("sh")`/`None`.
- `_run_check_command(command)` — routes through `[shell, "-c", command]` when a POSIX shell is found (marker `"posix"`), else the **byte-for-byte prior** `subprocess.run(command, shell=True, …)` (marker `"cmd-fallback"`).

The `command-output` evidence payload gains a `shell` field carrying that marker — so on a bash-less box a POSIX-only check **visibly** fails (`shell: cmd-fallback`) rather than silently. `_git`, `artifact`, and `git-change-policy` checks are untouched.

**Doctrine + templates.** A new fleet-doctrine "Windows shell hazards" section states both rules. The PR-body rule (`gh pr create -F <file>`; here-strings are for `git commit -m`, not PR bodies) propagates to the `LAUNCH_ORDER` Return Shape (Admiral-dispatched Commander) **and** the `COMMANDER_SPINE` archive step (the **solo** Commander, which has no LAUNCH_ORDER and would otherwise see neither). `checklist-engine.md` + `CHECKLIST_SCHEMA.md` record the POSIX-shell routing and the `shell` evidence field.

## Enforcement, honestly

The routing is the real fix; the `cmd-fallback` marker is the honest ceiling — when no bash exists the engine can't conjure one, so it falls back and *says so in the evidence* (the same evidence-in-return-shape honesty #33 used for `--here`). Failing every command check outright when bash is absent was rejected: it would regress the cmd-safe `python …` framework checks that work today.

## Testing

- TDD on the engine: pure `_bash_candidates_from_git` (both `mingw64\bin\git.exe` and `cmd\git.exe` inputs resolve to the real bash paths), `_find_posix_shell` monkeypatch branches incl. the `if git:` guard, the `cmd-fallback` marker, and a guarded integration test whose **`shell: "posix"` evidence assertion** is the regression guard (the command's exit code can't discriminate — `grep`/pipes pass under cmd.exe too where Git's `usr\bin` is on `PATH`).
- Existing command-check tests now exercise the routed path unchanged; their backslash Windows-path commands run cleanly under `bash -c` (verified).
- Full suite: **229 passed, 1 skipped** (was 222; +7 new, no regressions).

Built subagent-driven (per-task TDD + spec/quality review + opus whole-branch review: *Ready to merge = Yes*, no Critical/Important — the reviewer ran the 4-ancestor path walk across all three git layouts and confirmed routing through `[shell, "-c", command]` does not widen the injection surface vs the prior `shell=True`). The spec review itself (also subagent) caught two empirical errors — the wrong ancestor depth and a non-discriminating integration test — before they reached the plan.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
