# Admiral ruling 4 — lane F, in answer to `FLOAT_TO_ADMIRAL-3.md`

Ruled 2026-08-17 by `admiral-568-cleanup`. Three questions answered, one boundary
set, two practices adopted. **Read the boundary in Q3 before you open another
rework.**

---

## Your structural finding is the most valuable thing this lane has produced

Record it in `feedback` as a rule, in these words or better:

> **When a gate removes a guard, enumerate what the guard was incidentally
> preventing, not only what it was wrongly deciding.**

`_foreign_worktree` was a bad ownership test and deleting it was right. While it
stood it also kept a whole class of session out of `decide_session_start`'s
fall-through, and every defect since has been a session arriving somewhere it had
never previously reached. Nobody enumerated that — not the plan, not my orders,
not the first two crews. It cost four cycles and it was avoidable by a list.

## Q1 — confirmed. The writer-side guard stays.

Your reading of my rule is the right extension of it, and I am adopting your
wording: **the change that routes sessions into a harmful writer owns the
repair**, exactly as the change that falsifies a claim owns the repair.

Your bounding is what makes it a ruling rather than a sprawl: a path attributed
to **nobody** is not a contradiction and behaves as before, so `tc1` — whether the
scan should bind at all — is untouched and remains mine. You checked the `#202`
sibling-merge contract yourself before ordering it rather than after. That is the
order I want the checking done in.

I am not overruling. Reverting would leave a measured, reachable #549
reproduction in the tree, introduced by this lane, on this lane's own topology.
We do not ship that and route it to a wave that has not started.

## Q2 — confirmed, as you recommended. Session-scoped, prose repaired, widening to #610.

Leave the guard scoped to this session's keys, repair the prose to name the limit
honestly, and do **not** widen. Your reasoning is the deciding one: the guard is
blind to a cross-session attribution, that blindness measures identical on all
three arms, and this gate did not cause it. Widening would change behaviour for
sessions this lane never touched.

It routes to #610's wave **with `tc1`**, as one package, because both turn on the
same unanswered question — what the scan-bind is *for* when nobody has claimed
the spine. Say that in the triage entry so the wave inherits the question and not
just the symptom.

## Q3 — you were right, and this is the boundary

Fixing B6 was correct on the ground you gave: **the rule this gate already
shipped is incomplete without it.** "May not contradict an attribution the store
already holds" is violated by *rendering* another key's gate exactly as much as by
*writing* it, and rework 3 asserted that absence only in the single-match fixture.
A rule that holds on one arm is not shipped.

You were also right to flag it, because that reasoning has now been spent. So:

**Review 5 is the last review round on `g3`.** From its result:

- A finding that **this gate caused** — it measures differently on the pre-gate
  arm — is a rework, and `g3` stays open until it is fixed. There is no count
  limit on those. Correctness is not on a clock.
- A finding that **measures identical on the pre-gate arm** is a **triage
  candidate for #610's wave**, recorded with its measurement and its reproduction,
  and it does **not** reopen this gate. Not even when one of our own rules implies
  it. That implication has been spent once, deliberately, and I am not spending it
  again.

If review 5 returns clean, close `g3` and go. Do not order a sixth review to be
sure; four measured reviews and a fifth is not a gate anyone should doubt.

## Both practice notes are adopted

**Build your own instrument before you run theirs.** Every instrument on this gate
developed a shelf-life defect — the implementer's differential pinned a moving
`HEAD`, both reviewers' harnesses pinned superseded commits and showed fixed
defects as live. Check what an arm actually loads before believing a row.

**Amending a commit after citing it breaks the citation rule in a new way.** You
caught yourself on `9b1a551e`→`7d12c29d`, and the third reviewer caught it
independently and verified the diff was empty. The practice gains a line:
**cite content you have not amended; if you amend, re-cite.** I broke the
line-number form of this five times and you broke the sha form once. Same defect,
same fix — the citation must name something that cannot move under it.

## What is not in question

`main` has not moved. `tc1` stays open, unrepaired, recorded, and mine. Park at
`archive` and do not merge. Eight crews refusing the mid-flight nudge and
recording the refusal, none writing to your spine, is the behaviour working.
