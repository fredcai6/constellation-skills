# Gate (b) — role-competence evidence, and two attributable declines

**Issue #310, epic #298.** Measured against `origin/main` and the worktree at branch `epic-298/310`.

---

## GATE-B-N: 0

**Gate (b) was never run. It has n = 0 — not weak evidence, not thin evidence. *No* evidence.**

That is the first sentence because it is the finding, not a caveat on one.

B2's gate (b) asks for *"a role-competence test [showing] an agent operating from
kernel-plus-fragments-plus-artifacts completes a representative mid-spine step as correctly as one
holding the monolith."* Nothing in this run, and nothing in this epic, produced such a comparison.

### The correction that produced this number

An earlier draft of this run's own problem statement — and an instruction from the Admiral — proposed
using this epic's **refresh / cold-start relaunches** as observational gate-(b) evidence. The reasoning
was that a *fresh* agent cold-started from `current` alone, mid-spine, with no handoff document, is
Assumption 1 running in production.

**A cold plan critic showed that is wrong, and it is wrong in an instructive way.**

> *"Every relaunched agent held the **full monolith**; those are monolith-arm datapoints bounding
> Assumption 1 only, contributing zero to (b). Not a missing comparison arm — **the treatment was never
> varied**."*

That is correct and it is accepted. Every relaunch in this epic held the always-loaded surface
**constant**. A study that never varies its independent variable does not have a small sample of the
effect — **it has no sample of it.** The defect is not a missing control arm; it is that there was never
a treatment arm either.

**Consequence, binding on the verdict:** no relaunch count may be entered in the (b) column. Doing so
would convert "we never tested this" into "we tested this a little", which is precisely the laundering
this run's pre-registration exists to prevent.

### What the relaunches *do* bound

They bear on **Assumption 1** (*run artifacts carry accumulated state between steps, so late loading never
means lost understanding*) — the spec's own untested, explicitly gated premise (spec line 126). They are
consistent with artifacts carrying enough state for a cold-started agent to continue. That is a real but
much weaker claim, it is **observational and self-selected** (a relaunch that failed instantly may leave
no artifact), and **it is reported here in its own section precisely so it cannot drift into the (b)
column.**

---

## Decline 1 — the ablation arm. *The impossibility claim is WITHDRAWN.*

This run originally asserted that a competence arm was **impossible**: *"testing kernel-plus-fragments
requires a kernel-plus-fragments decomposition to exist, and building it IS the break."* That claim was
graded `settled/structural` in the mission frame.

**Both the claim and the grade were wrong.**

The cold critic named a cheaper honest arm this run had missed: an **ablation**. Run one representative
mid-spine step **twice** — once with the full monolith, once with named sections *withheld* — and compare
the step's output. This **varies the treatment** and requires **zero authoring of a decomposition**. It
does not build the break, and it does not require the break to exist.

**Regraded `guess/structural`.** Grading a contested claim `settled` is exactly the laundering the
grading mechanism exists to prevent — and this run committed it while writing a document warning about
laundering.

### The arm, specified (so the decline is attributable, not asserted-impossible)

| | |
|---|---|
| **role** | Commander (largest role; the one this epic keeps editing) |
| **step** | a mid-spine step, not a bootstrap step — `plan` or `execute`, where accumulated state is load-bearing |
| **arm A (control)** | full monolith: `SKILL.md` + `commander-core.md` + all named `references/` |
| **arm B (treatment)** | the spine node's imperative + run artifacts only; role doctrine sections withheld |
| **runs** | ≥4 per arm (#307's arms ran 4–5; below that a 0/4→4/4 style signal is unreadable) |
| **scoring** | reuse #307's `discriminate.py` + `RUBRIC.md`; **do not rebuild a scorer** — a rebuilt scorer makes any arm difference two-caused |
| **treatment verification** | assert delivery **against bytes** (#393: `TREATMENT-VERIFIED` proved hop 0 of three) |
| **disposal** | withheld sections restored from git; no corpus change survives the arm |

**Declined because:** (i) **runway** in this run, and (ii) Tommy's ruling that metric work is premature
while the substrate is in flux. **Not because it is impossible.** Escalated by the Admiral to Tommy as a
scope question; **the decision is his and it is already with him.**

---

## Decline 2 — the 184-row corpus census. *Cut by Tommy.*

**Ratifying authority: Tommy, 2026-08-03**, relayed through the epic-298 Admiral:

> *"that seems like we're making our life hard to come up with metrics too early. right now we're just
> reworking the substrate, we're not aiming to idealize any particular metric."*

**This is a different objection from "n is too small."** It says the measurement is **premature in kind**:
the substrate is still being reworked, so a metric built now measures a thing still changing shape
underneath it, and the effort to make it rigorous is effort spent idealizing a number nobody has yet
committed to caring about.

**State of the work when it was stopped** (preserved at `.agent-work/issue-310/trends/`, with
`README-SALVAGE.md`): the walker **passed its blocking external oracle**, reproducing `TREND_SNAPSHOT` §1
at tag `baseline/304-trend-snapshot` exactly on all four figures (100 files, 63,681 words, 19 `SKILL.md`,
15,831 words). It asserted 187 census rows, 234 deletion events, 19 roles, 10 unresolved reference tokens.
It **never completed verification** and **no reviewer ever hand-recomputed a revision against it**, so
`trends.json` is marked **unreviewed** and **the verdict rests on none of it.**

**Nothing was deleted.** Deleting an observation because its gate was cancelled would be the same
laundering this run's pre-registration was written to prevent.

---

## Both declines are filed, not banked

Per the launch order's rule that issue filing is **required, not permitted**, and so that a future run
inherits a spec rather than re-deriving one:

- the **ablation arm** design and cost estimate — filed;
- the **census** design, its oracle-validated partial instrument, and the reason it was cut — filed.

**A decline that is written down with its cost and its ratifying authority is a decision. A decline that
is merely not-done is an omission.** These are the former.
