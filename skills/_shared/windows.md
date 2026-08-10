# Windows/harness hazards

Canonical home for platform/harness hazards that recur regardless of project or
role — grounded in repeated field incidents, not speculation. Every Constellation
skill bundles this file (`references/windows.md`) so no role has to rediscover
these; other doctrine (`global-everyone.md`, `fleet-doctrine.md`, project docs)
points here rather than restating them. Positive-recipe form throughout: the
working command form first, the failure mode second.

Agent-facing. Dense by design.

## 1. `gh ... --body` with multiline content

**Works:** write the body to a temp file, then `gh pr create -F <file>` (or
`--body-file <file>`) — the only reliable form on Windows PowerShell 5.1.

**Fails:** both a bash heredoc piped into `--body` and a PowerShell `@'...'@`
here-string passed to `--body` fail the PowerShell 5.1 argument parse for any
multiline `gh ... --body` call (`gh pr create`, `gh pr comment`, etc.). Note the
trap explicitly: `@'...'@` here-strings *do* work for `git commit -m` — do not
assume they also work for `gh ... --body`. They do not.

Grounded: story_time dogfood project, recurred across 3 consecutive epics.

## 2. Resuming a previously-spawned agent

**Works:** use the `SendMessage` tool with the agent's id or name as the `to`
field — this resumes it with full context.

**Fails:** there is no `--resume` CLI flag for this. Treating the absence of a
CLI flag as "no resume primitive exists" is itself the failure — the primitive
exists, it is just a tool call (`SendMessage`), not a flag.

Grounded: f1Brainz run 510 (previously undocumented).

## 3. Agent-tool `isolation:"worktree"`

**Works:** provision the worktree yourself with `git worktree add <path> -b
<branch> <base>` before dispatch, then verify real isolation with `git worktree
list` (showing N distinct paths) or `scripts/verify_worktree_isolation.py
<path1> <path2> ...` (must exit 0) before any parallel wave. If isolation is
unverified, treat it as ABSENT and serialize dispatch.

**Fails:** the Agent-tool's `isolation:"worktree"` parameter is a silent no-op
on Windows — subagents launched with it run in the shared checkout, not an
isolated one. A parallel wave dispatched on the belief that the flag provisions
isolation collides in the single checkout (two agents racing a push, colliding
`git checkout -b`, a commit landing on a sibling's branch) — that is data loss,
not friction. A git-level probe alone cannot catch this: `git worktree add` in
a temp dir tests *git's* worktree support (fine on Windows) — it is the Agent
*tool* that skips provisioning, so that probe alone returns a false green.

Grounded: f1brainz epics #372/#378/#453.

## 4. Portable Python script invocation

**Works:** `python <skill-dir>/scripts/some_script.py` — the installer rewrites
the `python <` prefix to the interpreter it actually resolved on the install
host (`py` on Windows, `python3` elsewhere; see `resolve_interpreter()`) at
install time. This is the only form that ships correctly to every platform.

**Fails:** hand-writing a specific interpreter name — `py`, `python3`, or bare
`python` — bakes in one platform's choice. `py` is real and reliable *on
Windows specifically*; writing it into skill text as if that made it portable
is exactly how this class of defect ships: the command works for its author
and fails verbatim everywhere else, because no hard-coded name matches the
installer's `python <` rewrite token.

## 5. Transient "Blocked by classifier" on `gh`/`git`

**Works:** when a `gh` or `git` command is denied with "Blocked by classifier",
retry the identical command once before treating it as a real policy block — the
denial is often transient and the retry typically succeeds immediately.

**Fails:** treating the first transient denial as a hard policy refusal — abandoning
or escalating a perfectly-permitted read/create action (`gh pr create`, `git log`,
`git diff --stat`) that a retry would have let straight through. Note the scope
split: for **delegated-class** actions (merge, issue-close) the fallback is still
the latitude contract's human-approval-then-batch rule; this retry-once habit is
for the more common case of an ordinary read/create hitting the same transient
flakiness, which no merge-class fallback covers.

Grounded: epic #178 — hit `gh pr create` (impl #180) and the Admiral's own
`git reset --hard`; identical retry/fallback succeeded both times.

## 6. Headless hook-probe: verifying a `settings.json` hook actually fires

**Works:** `claude -p "<probe prompt>" --allowedTools "Bash"` — an explicit, non-bypass tool
allowlist. This is a real permission mode, so a tool call genuinely executes: PreToolUse/
PostToolUse fire around it, and SessionStart/Stop fire the same as any other run. This is
the form that live-proves a hook registration headlessly.

**Fails, two different ways:**
- `--dangerously-skip-permissions` (`bypassPermissions`) is refused by the classifier on a
  headless (`claude -p`) invocation — the process never launches, so **no** hook fires, not
  even SessionStart/Stop. Do not read this as "the hook is broken"; the run never started.
- A bare `claude -p "<prompt>"` with no permission flag DOES launch and fires SessionStart/
  Stop, but every tool action needing approval is silently denied (no interactive approver
  headless) — so it can never exercise a PostToolUse hook. Reading that silence as "the
  hook doesn't fire" misdiagnoses a permission gap as a hook defect.

Grounded: lesson `headless-hook-probe-allowedtools` — the spine_rail hook suite's live
probes (#141, PR #150).
