# Wave-0 common blocks — epic-418

Every wave-0 launch order embeds these verbatim. This file is the source of truth if they drift.

## Scope discipline — Tommy's standing ruling (MANDATORY; overrides the default rigor posture)

> *"this is not a final step in a process. lets do what we need to do and no more. this doesn't mean
> be sloppy, but i am explicitly allowing you to not chase down every corner case. make the thing
> that needs to work, and if you have any concerns, just note it locally in comments and pass it up
> the chain"*

- Build the thing that needs to work. Do not generalize past your stated obligation, and do not
  harden a corner case your issue did not ask about.
- A corner case you chose **not** to chase is not a defect to hide: put a comment at the code site
  naming it, and float it up in your return. Noting-and-passing-up is the sanctioned exit. Silently
  absorbing it is not, and neither is stopping to fix it.
- **Not sloppy:** your issue's stated acceptance criteria are still the acceptance criteria. This
  ruling licenses narrower *scope*, never weaker *evidence* on what is in scope.
- Where your issue's own text and this ruling disagree about **breadth**, this ruling wins, and you
  say so in your return.

@grade: settled/human

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the
same rigor as a win. Falsification triggers rework of that element — never silent continuation and
never abandonment. Report "this specific check failed", never "this approach is impossible".

## Inherited Latitude

**Delegated to you — decide, log in your own record, proceed:**

- architecture / structural change — *unless* it changes a load-bearing interface shape (the MCP tool
  surface, the gauge binding key, the gate schema), which comes to me
- merge to main — green + reviewed only
- issue **filing** and **commenting**
- fix-now triage (a bounded fix applied immediately)
- model tier for your own crew, within your budget
- **threshold regrade** of a `guess`/`placeholder` threshold you lean on: run its `settle:`
  experiment, log the ruling, regrade
- **pre-build branch points**: record which branch the evidence picked, and act on it

**Float to me (the Admiral) — do not decide these yourself:**

- **Spec deviation** — your issue's stated obligation cannot be met. **Always surfaced.** Do not
  substitute adjacent work for it; that substitution is the **#308 failure shape** this epic exists
  to catch.
- scope change — an issue added, dropped, or re-scoped
- **issue closing** (filing is yours; closing rides a human batch confirm)
- production defaults or user-visible behavior
- design-it-twice convergence (human-only)
- anything fitting none of these classes — **out-of-taxonomy always escalates**, with one line on
  why it fit no class

You cannot reach the human. I am your reachable tier: float decisions to me, and **query** me for
epic-level context your order does not cover. Asking up is always sanctioned and is never a failure.

**Permissions already pre-cleared by Tommy, 2026-08-05 — do not re-ask:** `gh issue create` /
`comment` / `edit`, `gh pr create` / `checks` / `merge`, `git push` on `epic-418/*`, the full test
suite, local commits, and **subagent dispatch at every tier** (you may dispatch crew; your crew may
dispatch cold critics). If the harness permission classifier vetoes something anyway, that is the
**#145 shape** — report it to me as an environmental block, not as a scope problem, and do not
quietly work around it.

## Inherited Context — platform invariants

- **Windows.** PowerShell is primary; a Bash tool is also available for POSIX scripts. Both `py` and
  `python` work.
- **`gh pr create` on Windows:** write the body to a temp file and use `gh pr create -F <file>`.
  Never a heredoc, never a PowerShell here-string for a PR body. (Here-strings *do* work for
  `git commit -m`.)
- **`gh issue create` with a >32K body fails on Windows** (WinError 206 — the adapter passes bodies
  via `--body` on the command line). Workaround: create with a short body, then
  `gh issue edit --body-file`.
- **Gate on real exit codes.** `cmd | tail -5; echo $?` captures `tail`'s exit, not `cmd`'s. Redirect
  to a file, then echo the exit code. This has already cost this epic's Admiral one wrong call.
- **Ask the forge whether a PR merged** (`gh pr view --json state`). Ancestry tests lie under
  squash-merge.
- **Verify claimed side-effects at the source**, not from the claim.
- A `.get()` on a guessed field name returns `None`, and `None` reads as a clean negative — the
  absent-field and false-value cases are indistinguishable at the call site. Read the schema.
- **Editing a shipped compact-format JSON template:** edit the raw **text** surgically. Never
  round-trip through `json.load`/`json.dump` — it reflows the whole file and destroys blame.
  Re-validate with `json.load` afterward.
- **Editing global doctrine:** edit the canonical source `skills/_shared/global-*.md`, **not**
  `skills/<role>/references/global-*.md` — the latter is an install-time copy that
  `install_constellation.py` regenerates, so an edit there is silently overwritten on the next install.
- **Hook code is NOT fenced by worktree isolation.** `CLAUDE_PROJECT_DIR` resolves once at session
  launch and is inherited unchanged by every subagent, so an agent in an isolated worktree still runs
  the **main checkout's** hook code against the **main checkout's** state (issue #269). If your
  mission touches `scripts/hooks/*.py` you **cannot** validate the change from inside the worktree
  that contains it — that is the same process the harness would use to run the unchanged code.
  Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree (a
  headless `claude -p` launched with that value, or a plain subprocess with the env var set), never a
  fixture that hand-injects the value you are trying to prove the harness delivers.
- **Never put two agents in one worktree.** The Agent-tool `isolation:"worktree"` flag is a silent
  no-op on Windows; your worktree was provisioned explicitly for you.
- **No Fable at any tier.** Cap every dispatch at Opus or lower and name the model explicitly on
  every `Agent` call.

## Data Locations

Worktrees do not contain untracked inputs. These live in the **main checkout**,
`C:/Programs/constellation-skills`:

- `.agent-work/` — the durable root, including `LESSONS.md`, `AGENT_FEEDBACK.md`, and this epic's
  work area `.agent-work/epic-418/`
- `.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md` — **the spec of record for this
  epic.** Read your workstream's section. It governs; where it and the tracker issue differ, the spec
  wins and you say so.
- Prototype worktrees to lift from: `C:/Programs/.proto-exc6-governor-subagent-identity` @ `75f684c`,
  `C:/Programs/.proto-exc8-spine-instructions` @ `5a283ad`,
  `C:/Programs/.proto-exc9-mcp-front-door` @ `de6a084`

**Standing constraint, do not violate:** the worktree `C:/Programs/constellation-skills-wt/governor-264`
and its three unmerged commits stay put. Disposal is blocked pending #412's orphan-risk read. Do not
sweep it, do not delete its branch.

## Stop Conditions

Stop and return when: your scope would have to grow beyond the issue; you need a decision outside the
inherited latitude above; your budget is crossed; the required evidence is genuinely impossible to
obtain; or you need **context this order does not cover and cannot safely proceed without**. In the
last case, **return-and-query me** — I answer and continue you. That is a round-trip, not a death.

If your context fills and the governor trips you HARD, do **not** push through: file a
`refresh-request` on your own spine per `global-everyone.md` §reach-up, write your crash-resume state
note first, and go idle. I relaunch a fresh Commander into **this same worktree and spine file**.

## Return Shape

Write your result artifact **before** going idle — an idle notification with no artifact reads as
stalled, not done. I judge completion from what you produced.

Write `RETURN.md` at the root of your worktree containing:

1. **Verdict** — one paragraph, plain English: what you were asked, what you did, what is true now.
   State explicitly whether this is a win or a measured negative.
2. **Evidence** — commands run with their **real** exit codes, the PR number and its
   `gh pr view --json state` result, and the tests that gate the claim.
3. **Isolation proof** — paste the output of
   `py scripts/verify_worktree_isolation.py --here <your worktree path>` (must exit 0).
4. **Scope-discipline report** — every corner case you deliberately did not chase, each with the file
   and line where you left the comment naming it.
5. **Map impact** — what an architecture reconcile would need to know about your net change.
6. **Triage candidates** — defects you found but did not fix.
7. **Workflow feedback** — where the corpus, the engine, or this launch order fought you.
