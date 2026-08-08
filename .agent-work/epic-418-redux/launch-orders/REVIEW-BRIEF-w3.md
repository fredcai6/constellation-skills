# Wave-3 review brief — instantiate per PR

Pre-written so a review dispatches the moment a crew returns. Wave 2 merged PR #470 on
self-verified evidence because no reviewer artifact had landed; two independent reviewers then
returned APPROVE *after* the merge, and **neither posted to the forge**, so
`gh pr view 470 --json reviews` is empty to this day. That is the failure this brief exists to stop.

Substitute `<PR>`, `<ISSUE>`, `<BRANCH>`, `<WORKTREE>` per dispatch.

---

You are an independent reviewer for epic #418, wave 3. Load `constellation-reviewer` and drive the
review survey through the engine. Claim your lease as your first engine command.

**Review PR #`<PR>` (issue #`<ISSUE>`, branch `<BRANCH>`).**

## The one thing this review is for

Every wave-3 issue is a **guard that could not register its own failure**. So the question that
matters is not "does the code look right" and not "is the suite green" — **green is what the broken
version already does for all four of these issues.**

The question is: **would this change actually fail in the defective world?**

Concretely, for whichever issue you are reviewing:

| Issue | The defective world the guard must catch |
|---|---|
| #461 | a stray unstaged write, and a stray untracked file, under `episodes/active/` — while a staged legitimate capture passes |
| #465 | a text-mode writer rewriting CRLF in an engine state file; and an imperative naming a verb that does not exist |
| #488 | two bindings on **one** gauge path (must now READ) vs two on **different** paths (must still SKIP) |
| #489 | two fixture matches present (must fail and name both) |

**Re-derive this empirically. Do not accept the crew's pasted evidence as proof of itself.** Run the
new test against the *unfixed* code — `git stash` the source change, or check out the pre-fix blob —
and confirm it goes **red**. A test that passes on both sides of the fix is the exact defect this
epic exists to find, and shipping one inside the fix for it would be the funniest possible outcome.

## Also check

- **The negative direction is preserved.** #488 especially: a fix that merely stops skipping is a
  regression no green run will reveal. Confirm genuinely-different gauge paths still skip and the
  silence is still flagged at every candidate.
- **Fences held.** The crew touched only its owned files. Three ran concurrently:
  #465 owns `skills/constellation-reviewer/**` + `scripts/checklist_engine.py`;
  #461 owns `tests/test_episode_negative_control.py`;
  #488/#489 own `scripts/hooks/gauge_writer_hook.py` + `tests/test_verify_spec_confirmed.py`
  (and `tests/test_gauge_writer.py`, its own test file).
- **Scope discipline.** Tommy's standing ruling: do what needs doing and no more. Flag expansion.
- **Docstring and predicate agree** where the issue asked for it (#461 explicitly).

## Non-negotiable on delivery

**Post your verdict to the forge**, not only to your dispatcher:
`gh pr review <PR> --approve|--request-changes -F <file>`. A verdict that exists only as a session
message is invisible to everyone who later asks the repo what happened — that is precisely what went
wrong on #470.

**Write the body to a file and pass `-F`.** Never pass markdown to `gh` as a double-quoted bash
string: a backticked code span is executed as **command substitution**, and the review posts anyway
with that phrase silently deleted and every success signal intact. That happened on #264 this session.

## Environment

- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`** (#454). Capture the **real**
  exit code; if you pipe it, `$?` is the pipe's, so use `${PIPESTATUS[0]}`.
- Review in your **own** worktree at the PR's head commit. Another agent switching HEAD mid-run
  invalidates your run — one wave-2 reviewer caught exactly this and redid the whole suite.
- **Never use an ancestry test to decide whether anything merged.** Squash-merge makes it return the
  same answer for merged and abandoned. Ask the forge.
- A **BLOCK is a complete deliverable**, and so is an APPROVE with non-blocking findings. Both #470
  reviewers independently flagged `matches[0]` as non-blocking; that finding became #489 and is being
  fixed this wave. Non-blocking findings are worth writing down.

## Return

Verdict; the **red you observed** running the new test against unfixed code; the negative-direction
check; fences; test command and real exit code; the **forge URL of your posted review**.
