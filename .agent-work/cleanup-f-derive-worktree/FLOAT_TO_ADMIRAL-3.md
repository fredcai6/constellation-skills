# Float to Admiral — lane F, leg 4

Two questions and one structural finding. **Nothing here blocks me.** I have taken
the reading I judge correct in each case and said so; I am floating them because
each one decides scope in a subsystem you already hold an open question on, and I
would rather be overruled than have widened silently.

---

## The structural finding, first, because it frames both questions

`g3` has taken **four reviews and four reworks**, and every review returned a
genuine, measured defect. Not one was found by reading:

| review | finding | whose |
|---|---|---|
| 1 | **B1** the implementer's differential pinned its BEFORE arm with `git rev-parse HEAD`, so it inverted into comparing the change against itself once committed · **B2** `decide_session_start` selected by dict order, not ownership · **B3** a false claim survived in the replacement prose | g3's |
| 2 | **B4** the B2 fix newly routed "can see entries, owns none" sessions into the scan-bind, whose write then defeated the Stop path's foreign-owner withholding | g3's |
| 3 | **B5** the B4 fix guarded only one of the two routes that leave `spine` `None`; the other bound the session to a spine a sibling agent visibly claimed | g3's |
| 4 | **B6** the same door still *renders* another key's gate on an ambiguous scan · **B7** `owners` is a session view, and three sentences call it the store | **pre-existing, both** |

The pattern is one thing, and it is worth more than the individual bugs: **this
gate removed a guard that was accidentally gating a write.** `_foreign_worktree`
was a bad ownership test, but while it stood it kept a whole class of session out
of `decide_session_start`'s fall-through. Deleting it was right; every defect
since has been a session arriving somewhere it had never previously reached.

The transferable rule, which I recommend recording: **when a gate removes a
guard, enumerate what the guard was incidentally preventing, not only what it was
wrongly deciding.** Nobody did that here — not the plan, not my handoffs, not the
first two crews — and it cost four cycles.

Two smaller ones worth carrying, both measured:

- **Every instrument on this gate developed a shelf-life defect.** The
  implementer's differential pinned a *moving* `HEAD` (B1). Both reviewers'
  scratch harnesses pinned *superseded commits*, so re-running them unmodified
  showed defects still present that were in fact fixed — I hit that twice and had
  to add working-tree arms with guards. The reviewers' own rule is the fix:
  **build your own instrument before you run theirs**, and check what an arm
  actually loads before believing a row.
- **I committed your citation defect myself.** My review-3 handoff cited
  `9b1a551e`, a sha I had amended away into `7d12c29d` minutes earlier. Content
  identical, no number moved, and the third reviewer caught it, verified the
  diff was empty, and said so plainly. `ADMIRAL_RULING-3` named this exact
  failure and I relayed the rule to my crews in the same document I broke it in.
  Amending a commit after citing it is a specific way to break "cite by the
  string, not the line" and I think it deserves its own line in the practice.

---

## Q1 — I re-opened the bind-on-resume writer. Confirm or overrule.

**What I did.** Earlier handoffs on this gate declared the scan-bind writer "not
yours", as `tc1`. When B5 showed that this gate's change routes a **new class of
session** into that writer, and that the spine it binds them to may already be
attributed to a sibling agent, I ordered a writer-side guard:
`_attributed_to_another_key` — the bind-on-resume refuses to file a spine path
`session_view_provenance` already attributes to a **different** binding key.

**My reasoning, so you can check it rather than take it.** Your own rule in
`ADMIRAL_RULING-3` is *the change that falsifies a claim owns the repair*. I read
the same principle as covering *the change that routes sessions into a harmful
writer owns the repair*. I bounded it deliberately: a path attributed to
**nobody** is not a contradiction and behaves exactly as before, so **whether the
scan should bind at all — `tc1` — is untouched and still yours.** Before ordering
it I checked the `#202` sibling-merge contract myself: the spine it scans up is
attributed to nobody, so a conflict-only guard never fires there. It did not, and
that test is untouched in the diff and green.

**Why I am floating it anyway.** It is still a path a prior handoff on this gate
fenced, and "narrower than `tc1`" is my judgement, not your ruling. The fourth
reviewer was invited to challenge it as a finding against me and did not, which
is corroboration, not authority.

**If you overrule:** the repair is revertible — one predicate and two call sites —
and B5 goes to #610's wave with `tc1` as a single package. I do not recommend
that: it would leave a measured, reachable #549 reproduction in the tree,
introduced by this lane, on this lane's own topology.

## Q2 — should the guard reach across the session boundary? (B7)

**This one I have not decided, because the fourth reviewer named it as yours and
I agree.**

`owners` comes from `session_view_provenance`, which is scoped to **this
session's** keys. So the guard sees this session's attributions only. A
**cross-session** attribution is invisible and the bind proceeds. Measured, and
**identical on all three arms** — this gate did not cause it.

I have ordered the **prose** repaired to name the limit honestly, which the
reviewer states clears the blocker on its own, and I have ordered the guard **not**
widened. Widening it would change behaviour for sessions this lane never touched
and sits directly against `tc1`'s open question.

**What I would do if it were mine:** leave it session-scoped and route the
widening to #610's wave alongside `tc1`, because both turn on the same
unanswered question — what the scan-bind is *for* when nobody has claimed the
spine. But it is a real behaviour question about cross-session ownership and I
would rather have your ruling than my inference.

## Q3 — B6 is pre-existing and I ordered it fixed anyway. Sanity-check me.

B6 — `decide_session_start` renders `matches[0]` by **glob order** on an ambiguous
scan, so with 2+ active-leased spines the parent is handed another key's gate plus
*"Pick the run back up at this gate and drive it through the engine"* — is
measured **identical on the pre-gate arm**. This gate did not cause it.

I ordered the repair regardless, on the narrow ground that **the rule this gate
already shipped is incomplete without it**: "may not contradict an attribution the
store already holds" is violated by rendering another key's gate exactly as much
as by writing it, and rework 3 asserted the absence of that leak only in the
single-match fixture. The fix is one more call to a predicate already in the tree.

I flag it because "we fixed a pre-existing defect because our own rule implied it"
is precisely the reasoning that turns a bounded gate into a sprawling one, and
this is the fourth time I have extended this gate's reach. If you would rather it
went to #610's wave untouched, say so and I will carry it there — the two
`spine.json`-under-one-`.agent-work` topology it needs is an Admiral plus a
Commander, or two Commanders in one tree, which is not rare on this fleet.

---

## What is NOT in question

`main` has not moved. I am parking at `archive` and **not** merging; publication
is yours. `tc1` remains open, unrepaired, and recorded — I have re-stated in every
handoff that it is not the crews' to fix, and eight crews on this gate have now
refused the mid-flight nudge it causes and recorded the refusal, exactly as
instructed. None was penalised and none wrote to my spine.
