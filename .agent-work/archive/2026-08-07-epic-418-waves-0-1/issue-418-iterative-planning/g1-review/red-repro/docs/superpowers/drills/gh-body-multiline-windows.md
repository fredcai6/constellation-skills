# Drill: gh-body-multiline-windows

- **Lesson / doctrine under test:** `skills/_shared/windows.md` §1 — `gh ... --body` with
  multiline content on Windows PowerShell 5.1.
- **Failure it guards:** an agent passes a multiline PowerShell here-string (`@'...'@`) or a
  bash heredoc directly to `gh ... --body`, which fails the PowerShell 5.1 argument parse.
  Recurred across three `story_time` epics *after* being written down (issue #55 motivation).
- **Run by:** commander wave3-55 (worked example; the fresh-context lessons-auditor owns
  this in normal operation).
- **Date:** 2026-07-07
- **Verdict:** PASS — before-arm reproduced the failure; after-arm did not fire. The
  doctrine text changes behavior.

## Scenario

Identical task and pressure in both arms; the **only** variable is the doctrine text the
subagent is armed with. A throwaway subagent on "Windows, PowerShell 5.1" is asked, as a
quick housekeeping step, to post a fixed **multiline** comment to PR #42 using `gh`, and to
output the exact command it would run (dry run, do not execute).

The two arms differ only here:

- **Before-arm doctrine** (the faithful recurrence state): general Windows shell notes that
  say to use `gh` for GitHub ops and that reinforce the *true* fact that `@'...'@`
  here-strings are how you pass a multiline `git commit -m` message — but say **nothing**
  about `gh ... --body` being different. This is the exact gap that let the failure recur:
  the correct `git commit` here-string habit, with no foreclosure of the wrong
  generalization to `gh --body`.
- **After-arm doctrine:** the current `windows.md` §1 verbatim, including the explicit trap
  note ("`@'...'@` here-strings *do* work for `git commit -m` — do not assume they also work
  for `gh ... --body`. They do not.") and the positive recipe (write the body to a temp
  file, use `-F` / `--body-file`).

## Before-arm — failure reproduced (verbatim)

The subagent produced:

```
gh pr comment 42 --body @'
Thanks for the review. Addressed all three findings:
- fixed the off-by-one in the paginator
- added the missing null check
- renamed the ambiguous flag

Merging once CI is green.
'@
```

> "This uses a single-quoted here-string for the multiline `--body`, matching the team's
> `git commit -m @'...'@` pattern; note the closing `'@` must sit at column 0."

This is precisely the documented failure: a multiline here-string passed to `gh ... --body`,
which fails the PowerShell 5.1 argument parse. The agent's own rationalization — "matching
the team's `git commit -m @'...'@` pattern" — is the exact wrong generalization the trap
note is written to counter. The before-arm reproduces the recurrence on demand.

## After-arm — failure did not fire (verbatim)

The subagent produced:

```
gh pr comment 42 --body-file (New-Item -ItemType File -Path (Join-Path $env:TEMP ([guid]::NewGuid().ToString()+'.txt')) -Value @"
Thanks for the review. Addressed all three findings:
- fixed the off-by-one in the paginator
- added the missing null check
- renamed the ambiguous flag

Merging once CI is green.
"@ -Force).FullName
```

> "Per the team notes, the multiline body must go through a temp file rather than being
> passed to `--body` directly; this writes the comment to a temp file and feeds its path to
> `--body-file`."

The load-bearing behavior — *does it pass multiline content directly to `--body`?* — is
**no**. It routes through a temp file and `--body-file`, the reliable form. (The command is
more convoluted than the doctrine's `write to a temp file, then -F <file>` two-step, but it
avoids the failure; a minor legibility note, not a reproduction.)

## What the drill proves

The differentiator between reproduction and non-reproduction is exactly the doctrine text
under test — specifically the explicit foreclosure of the `git commit` → `gh --body`
here-string generalization. The trap note is load-bearing, not decorative: the before-arm,
carrying the correct `git commit` here-string habit without that foreclosure, generalizes it
straight into the failure. This is the process-documentation analogue of a passing
regression test for the doctrine edit.

## Method notes (for the corpus)

- Both arms were run as throwaway subagents, same scenario and pressure, doctrine text as
  the sole variable. Verbatim capture of the before-arm is the evidence.
- Honest-null was on the table: had the before-arm used `--body-file` anyway, that would
  have been a complete finding (the positive recipe alone suffices; the trap note is
  belt-and-suspenders). It did not — the failure reproduced.
