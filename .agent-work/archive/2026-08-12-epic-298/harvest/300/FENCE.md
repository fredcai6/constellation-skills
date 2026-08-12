# Fence citation — why this trio is staged rather than written to the durable root

`LAUNCH_ORDER-300.md` §Data Locations:

> `.agent-work/` durable root at the main checkout: `C:/Programs/constellation-skills/.agent-work/`
> — **read-only to you** while the Admiral's epic lease is active.

and §Return Shape:

> Also stage your durable trio worktree-locally at `.agent-work/staged-feedback/300/`
> (lessons-delta, `AGENT_FEEDBACK.md` entry, `CONSTELLATION_FEEDBACK.md` exports) so the Admiral can
> harvest it before the worktree is swept.

The complete trio is present in this directory:

- `lessons-delta.json` — 3 confirms + 2 adds. **Validated** against the real playbook with
  `py scripts/apply_lessons_delta.py --dry-run --file C:/Programs/constellation-skills/.agent-work/LESSONS.md`
  (exit 0; reports 18 active, cap 20). Not applied — the durable root is fenced.
- `AGENT_FEEDBACK.md` — the run retrospective entry, ready to append.
- `CONSTELLATION_FEEDBACK.md` — two constellation-scoped exports, both already filed to the tracker
  (#315, #316) so the finding is not trapped in this worktree.

**Harvest before sweeping.** `lesson:harvest-before-sweep-enforcement-gap` records that a staged trio
passing its own Commander's gate looks identical from the outside to one already merged into the
durable log, and that a prior epic came within one human catch of losing six of them.

**Note on run state:** this run stopped at the spine's `execute` step on the launch order's own named
stop condition (the floated convergence choice), so the `feedback` and `archive` steps have not run.
This trio is therefore staged *early*, deliberately, so nothing is lost if the worktree is swept
before the run is continued. A continuing Commander should treat it as a starting point to extend,
not as a finished record.

## If the cap binds at harvest — my ordering, so the harvester does not have to guess

This delta takes the playbook to **19 of 20** on its own, and #301's staged delta carries 8 more ops.
Both cannot simply be applied. The cap forcing graduate-or-retire decisions is the mechanism
working, not a problem — but the harvester should not have to reconstruct which of *my* ops matter
most. Ordered, most to least worth a slot:

**1. `bash-negation-postcondition-must-wrap-the-thing-that-must-fail` — apply, but expect it to be
short-lived.** It is the only op here with a live, already-open destination (#311) and a paired
success case from #303 in the same wave. It should **graduate into #311's inline template
documentation and be retired**, not held. If #311 lands before the audit, skip the add entirely and
go straight to the documentation edit — a lesson whose destination already exists does not need a
playbook slot to get there.

**2. `delegated-commander-as-teammate-cannot-spawn-named-or-background-subagents` — almost certainly
a CONFIRM, not an add.** See the sibling-fork note on the op. If #301's delta carries an equivalent,
this consumes **no** slot. Check that before counting it against the cap. And read the confirm
correctly: constellation scope means it accrues **recurrence debt, not trust** — #294 already records
5 rediscoveries and 0 filings, so the honest disposition is "fix upstream at #314", not "confirm
again".

**3. `panel-convergence-can-be-inheritance-not-evidence` — the one to drop if something must go.**
It is the most interesting finding here and the weakest claim on a slot, and those are not in
tension. Its ratified disposition is already *act now, document later*: the two mitigations run on
every panel as a convergence step regardless of whether this lesson is banked, and the write-up waits
for a third instance from a different epic. A lesson whose practice is already in effect does not
need the playbook to hold it — banking it buys a reminder, nothing more. **If the cap forces a
choice, drop this one.** Losing it costs a note; losing #1 or #2 costs a graduation path.

The three **confirms** (cold-critic-mandatory, round-trip-tests-prove-artifacts-not-parsers,
verify-launch-order-claims-against-code) consume no cap and should all land — each carries grounding
this run produced, and two of them carry a *new* failure mode rather than a repeat, which is the
part that makes a counter mean something.

## Harvest ordering — the delta is split into TWO files, and the order matters

Discovered by running it, not by reasoning about it. `apply_lessons_delta.py` is **all-or-nothing**:
one invalid op rejects the whole delta. The Admiral's closeout ruling converts #300's panel lesson
from an `add` into a **confirm** against #301's surviving identity
(`a-panel-inherits-what-it-was-not-told-to-vary`) — but a confirm against a lesson that has not been
added yet fails validation, and would have taken **all six** of my ops down with it, silently losing
five unrelated and perfectly valid ones.

So it is split:

1. **`lessons-delta.json`** — applies **standalone, in any order**. 3 confirms + 2 adds.
   Verified: `--dry-run` exit 0.
2. **`lessons-delta-AFTER-301.json`** — the single ordering-dependent op. Apply **only after**
   #301's `add` of `a-panel-inherits-what-it-was-not-told-to-vary` has landed. Verified to fail with
   `no such lesson` if applied first — which is the correct, loud failure, not a silent one.

Cap arithmetic, updated: converting that op from an add to a confirm **frees a slot**. #300 now
costs **2 adds**, not 3, so the §"If the cap binds" ordering above is less likely to bind at all —
and if it still does, the op nominated to drop first is already gone by a better route than dropping.

---

## THE CAP HAS ACTUALLY BOUND — this supersedes the ordering section above

The section above was written when the playbook had room and my delta carried 3 adds. It does not
any more. **`LESSONS.md` is at 20 active against a cap of 20.** I discovered this by running the
delta, not by reasoning about it: `apply_lessons_delta.py` refused with
`active cap 20 reached — retire before adding`, and because the delta is all-or-nothing that refusal
would have taken three perfectly valid confirms down with it.

So the trio is now **three** files, and the split is the point:

1. **`lessons-delta.json`** — **3 confirms, 0 adds. Applies standalone, today, in any order.**
   Verified `--dry-run` exit 0. Confirms consume **no cap**, so nothing about the cap blocks them.
2. **`lessons-delta-AFTER-301.json`** — one confirm against #301's surviving identity
   (`a-panel-inherits-what-it-was-not-told-to-vary`). Apply **after** #301's add lands; it fails
   loudly with `no such lesson` if applied first.
3. **`lessons-delta-WHEN-CAP-ALLOWS.json`** — one add,
   `contract-review-and-cold-panel-catch-different-classes`. Apply when a retirement frees a slot.

### Which of my adds I dropped, and why — my own criterion, applied to my own work

I had three adds. Two are **gone from the delta entirely**, and deliberately, because they are
already held somewhere more durable than a transitory inbox:

- `delegated-commander-as-teammate-cannot-spawn-named-or-background-subagents` → held by **#314**,
  open, carrying my comment with the background-subagent half and the working dispatch contract.
- `bash-negation-postcondition-must-wrap-the-thing-that-must-fail` → held by **#311**, open,
  carrying my comment with both the failure and success examples.

That is the rule I argued for earlier in this run, now applied against my own findings rather than
someone else's: **the cap binds on adds, so the cheapest relief is a named destination at filing
time.** Both of those had tracker homes, so banking them in the playbook would have bought a
reminder and cost a slot. Neither stops happening if the slot is gone.

The one I **kept** is the one that fails that test: `contract-review-and-cold-panel-catch-different-classes`
has **no tracker home**. It is a doctrine observation about review-class design, not a code fix, so
there is no issue to hold it. If its slot is gone, it is gone. That is why it is the survivor, and it
is why it is worth a retirement at the audit rather than being quietly dropped.

### What I did NOT do

I did not retire anyone else's lesson to make room. Retirement is a graduate-or-delete judgment over
the whole playbook, which belongs to the audit with all deltas in view — not to one Commander who
happens to arrive when the counter is full and wants its own entry in.
