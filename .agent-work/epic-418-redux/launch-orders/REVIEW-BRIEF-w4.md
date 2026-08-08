# Wave-4 review brief — instantiate when the Commander returns

Pre-written so a review dispatches the moment #467's PR lands. Wave 2 merged PR #470 with no
reviewer artifact on the forge; wave 3 fixed that by pre-staging the brief. Keeping the habit.

Substitute `<PR>`, `<BRANCH>` per dispatch. Worktree: provision a fresh one.

---

You are an independent reviewer for epic #418, wave 4. Load `constellation-reviewer` and drive the
review survey through the engine. Claim your lease as your first engine command.

**Review PR #`<PR>` — issue #467, workstream A2, branch `<BRANCH>`.**

## What this change is

The context governor's HARD limit currently expresses itself as a **refusal**, and that refusal
deadlocks: HARD blocks `advance`, and `advance` is the verb that writes the DIGEST the forced
handoff depends on (#431). This work converts a trip into a **change of instruction** — the agent
still advances, the DIGEST still gets written, #431 dissolves rather than being patched.

## The one thing this review is for

**#467's DC6 is the reason this review exists, and it is the hardest thing in the diff to check.**
Verbatim from the issue:

> *"a refusal is self-enforcing and self-recording, while an instruction is satisfied or ignored
> with identical traces. Converting HARD from a refusal into a sentence removes the only mechanism
> that could register an agent ignoring it."*

The change **deletes a self-enforcing mechanism on purpose.** So the question is not "does the code
look right" and not "is the suite green" — the question is:

**What, mechanically, would now register an agent that is told to wrap up and doesn't?**

Find that mechanism in the diff, then **break it and confirm it goes red.** #467 names its expected
shape: *the engine can see whether a handoff artifact appeared before the next advance at an
over-threshold gate.* If you cannot find a mechanical signal, or if the only thing standing between
compliance and non-compliance is prose in an imperative, **that is a BLOCK** — it is the exact
defect this whole epic exists to find, shipped inside the fix for it.

## Check each done-condition against the diff, not against the crew's summary

| DC | What must be true | The failure to look for |
|---|---|---|
| 1 | An at/over-threshold gate **changes what the agent is told**, not refuses its verb | prose changed, behaviour unchanged |
| 2 | The engine **distinguishes** an advance carrying a handoff from one starting new work, and refuses only the second. *#467 says it cannot express this today* | one direction tested, not both |
| 3 | The DIGEST is written on the handoff-carrying advance; **#431 dissolves** | asserted, not demonstrated |
| 4 | Per-gate thresholds: one graded default **plus an override mechanism existing and exercised at least once** — one gate demonstrably overridden, its neighbours unchanged | a default shipped and no per-gate mechanism; or 68 hand-authored ungraded placeholders |
| 5 | **The round trip completes**: trip → handoff → refresh → resume, resumed work verified against what the tripped agent was mid-way through | DC1-3 green while every handoff is useless — #467 says so explicitly |
| 6 | Non-compliance is **mechanically** observable | see above; this is the one |

**DC5 is the point.** #467: *"Conditions 1-3 are all satisfiable while every tripped agent produces
a useless handoff or none at all, because none of them look at the far end. Continuity across a trip
is the only thing this redesign is for."* A partial return that lands DC1-3+DC6 honestly and floats
DC4/DC5 is acceptable. A return that lands DC1-3 and *claims* the round trip is not.

## Two things not to mis-flag

1. **The RED leaves no residue, by design.** #467 mandates reproducing #431's deadlock RED first —
   but the deadlock is a property of the refusal path this work *deletes*, so it is unreproducible
   afterwards **by construction** and cannot stand as a regression test. Its absence from the test
   suite is correct. What must be permanent is **DC6's compliance observable + DC2's two-way test**.
2. **The crew was authorized to cite one specific override for DC4.** Field data from this epic:
   crews trip at 17-21% fill, the Admiral ran to 44% with no trip, same machine and hook and hour.
   DC4's *"overrides only where a gate has bitten"* is satisfied by that. The crew was **not**
   authorized to retune the global default — if the diff moves it, flag it.

## Also check

- **No absence is evidence.** #467's protocol: *assert a reading exists* before any claim about trip
  behaviour, and a run observing no trip must say **which of the two** it observed. Verify the crew
  actually did this rather than reasoning from a quiet log. This epic ran nine hours with a silent
  governor reading as healthy (#488, now fixed).
- **The `Fixed` list held**: a missing or failed reading never forces a handoff (fail-safe
  survives); HARD means "wrap up", never "you are unsafe"; the reading is **pushed** by the engine
  on tool use, never fetched by the agent.
- **Fences.** The crew must not have written `.agent-work/epic-418-redux/**` (the Admiral's area) or
  tracked `.claude/settings.json` (#458 — it was told to float, not edit).
- **Scope discipline.** Tommy's standing ruling: do what needs doing and no more. No new issues were
  authorized this wave. Flag expansion.
- **Baseline.** Main is `1793 passed, 2 skipped, 683 subtests, exit 0`. Any delta is the crew's to
  explain.

## Non-negotiable on delivery

**Post your verdict to the forge**, not only to your dispatcher. `gh pr review <PR> --approve` is
**REFUSED** here — "Can not approve your own pull request", because every agent authenticates as the
same identity that authored the PR. This is a platform block, **not** reviewer negligence. The
substitute is:

```
gh pr review <PR> --comment -F <file>
```

with your verdict (`APPROVE` / `REQUEST CHANGES` / `BLOCK`) as the **first line**.

**Write the body to a file and pass `-F`.** Never pass markdown to `gh` as a double-quoted bash
string: a backticked code span is executed as **command substitution**, and the review posts anyway
with that phrase silently deleted and every success signal intact. That happened on #264 this epic.

## Environment

- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`** (#454). Capture the **real**
  exit code; a pipe's `$?` is the pipe's, so use `${PIPESTATUS[0]}` or redirect to a file.
- Review in your **own** worktree at the PR's head commit. Another agent moving HEAD mid-run
  invalidates your suite run — a wave-2 reviewer caught exactly this and redid the whole thing.
- **Never use an ancestry test to decide whether anything merged.** Squash-merge returns the same
  answer for merged and abandoned. Ask the forge.
- A **BLOCK is a complete deliverable**, and so is an APPROVE with non-blocking findings. Both #470
  reviewers independently flagged `matches[0]` as non-blocking; that finding became #489 and shipped
  in wave 3. Non-blocking findings are worth writing down.

## Return

Verdict; **the mechanical non-compliance signal you located and the red you saw when you broke it**;
per-DC assessment; the `Fixed`-list check; fences; test command and real exit code; the **forge URL**
of your posted review.
