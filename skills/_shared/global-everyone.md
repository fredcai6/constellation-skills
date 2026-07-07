# Global doctrine — everyone

Inherited platform and engine doctrine for **every** Constellation role, bundled with the skill at
install. This is the baseline the whole fleet shares; a project never restates it, only departs from it.
Project orientation is the local overlay — read `docs/agents/AGENT_GUIDE.md` (repo map) and
`docs/agents/GLOSSARY.md` if they exist.

Agent-facing. Dense by design.

## Engine verbs

- Artifact postconditions (`kind: artifact` — `user-decision`, `review-result`, …): **attach** the evidence;
  you cannot **attest** them. An APPROVE `review-result` attaches to BOTH `gN-review` and `gN-integrate`.
- A postcondition whose `check` is `null` is confirmed by **attest** (your manual verification); `attach`
  won't satisfy it. Never hand-edit the checklist JSON to mark a condition satisfied — use `attest` /
  `attach` / `waive`.
- Re-claiming a stale lease with the **same** session id is idempotent and safe (not a takeover); only a
  different id is a takeover. On a long step, heartbeat or expect a stale-lease refusal on the next mutating
  verb — recovery is a same-id re-claim, free.
- `command` postconditions run under a POSIX shell — author `grep` / `&&` / pipe checks in POSIX form; they
  then behave the same on every platform (a Windows box without bash fails such a check **visibly** rather
  than silently passing).

## Windows shell hazards

- A multiline `gh … --body` (`gh pr create`, `gh pr comment`, any `gh … --body`) FAILS the PowerShell 5.1
  argument parse. Write the body to a temp file and use `-F <file>` / `--body-file`, or route the call
  through the Bash tool. `@'…'@` here-strings fix `git commit -m`, NOT `gh … --body`.
- Bash tool for POSIX command sequences; PowerShell for cmdlets. Don't feed heredocs to PowerShell.

## Parallel dispatch and worktrees

- Agent-tool `isolation:"worktree"` does NOT reliably create distinct working dirs on every harness. Before
  any parallel dispatch, verify `git worktree list` shows N distinct paths; if unverified, treat isolation as
  ABSENT and **serialize**. Never launch a continuation into a possibly-sleeping agent's worktree.

## Detached and long work

- The result/deliverable file IS the task. Run verification and sweeps to completion **in-context** (poll,
  don't idle); an idle turn-end with the result unwritten strands the gate with no error signal — finish,
  then rest.
- Detach genuinely long jobs at the OS level (e.g. `Start-Process -WindowStyle Hidden`). Write the
  crash-resume state note (step / slug / next-cmd / PID / expected-artifact) BEFORE detaching; arm ONE
  completion notify (output-exists OR process-death), never a per-progress-line watcher.

## Universal posture

- Fail visibly rather than emit plausible wrong output; no hidden fallback.
- One canonical path; no speculative abstraction.
- Keep Constellation context and architecture docs current when their meaning changes.
- `/compact` is user-level; most harnesses don't expose it to agents. Treat context headroom as
  opportunistic (compact if available, else rely on auto-compaction) folded into the step that needs it,
  not as its own checkable gate — a step whose only sanctioned path is "skip" is ceremony, not gate.
- Reference bundled scripts and references by their absolute installed path; don't resolve `scripts/` from the
  target repo unless it vendors them.
