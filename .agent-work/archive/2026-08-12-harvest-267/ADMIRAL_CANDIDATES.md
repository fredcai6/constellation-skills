# Epic-267 — Admiral-tier lesson candidates, with evidence

Written mid-wave while the evidence is fresh. **These are candidates, not proposals.** The playbook is
at **16 active against a cap of 20**; anything added here must displace something or justify the slot.
Recorded so closeout adjudicates from evidence rather than from memory.

---

## C1 — A cold critic on a frozen plan paid for itself twice in one wave. Cost never measured.

**Evidence, 2026-07-28, both batch-2 Commanders, independently:**

- `governor-262`'s critic found **three gates that could close green while proving nothing**: the only
  machine check was a whole-file `pytest` run over 61 pre-existing tests, so new code needed no
  coverage to pass; a review gate lacking independent reproduction of a *silently* degrading failure;
  and a `check: null` bare attestation standing in for the epic's only fresh-process proof.
- `governor-264`'s critic invalidated the **headline deliverable**: the pinned-at-clamp falsifier is
  mute at `0.69875` (#252's own reading) and at `0.126658` (#271's stale-low), and fires 6.7x too late
  (clamp at 1,000,000 tokens; hard cap at 150,000).

**Neither Commander found its own.** Both accepted the catch and sharpened it — 262 converted a named-
test assertion into a structurally ungameable exit-5 gate; 264 surfaced the invalidation itself and
came to me with three options rather than quietly shipping a weak deliverable.

**Why this is a candidate and not a proposal.** Two data points on the same day is a pattern, not a
measurement. The unmeasured quantity is **cost**: neither critic's token spend was recorded, and this
fleet has no baseline for what a cold-critic gate is worth per wave. Before this displaces a playbook
slot, run one wave that **records critic cost alongside catch count**. A mechanism that catches real
defects can still be the wrong 17th of 20.

**The transferable shape, if it survives:** the critic must be *cold* (no participation in authoring
the plan) and must run *before the plan freezes*, not before the PR. Both catches were pre-code. A
critic at PR time would have found the same defects after they were expensive.

---

## C2 — Before celebrating a reproduction, check the behaviour you reproduced was actually wrong.

**Evidence:** `governor-264` reproduced 5,000,000 tokens -> `fill 1.0` -> REFUSED and reported it as
"the eight-days failure, on demand." It was not. 5,000,000 exceeds a 150,000 hard cap by 33x — **the
block was correct.** It reproduced a true positive and labelled it the pathology. The cap was in the
table it had already read; one division would have caught it.

**Same shape, twice more in the same epic, from two different agents:** its own ratio-vs-denominator
inference (a clamped reading proves `tokens >= window`, which indicts the *ratio* — it cannot
distinguish a too-small denominator from a too-large numerator), and my own #263 honest null, which
stated a *test* boundary and then drew a conclusion needing a *search* boundary.

**Candidate form:** a reproduction is not evidence of a defect until you have shown the reproduced
behaviour violates a stated contract. Name the contract and the comparison, in the same breath as the
repro. Three instances, three agents, one epic — this is the strongest recurrence signal in #267.

---

## C3 — "It works when I run it by hand" can be the existing mechanism, not a new one.

**Evidence:** I hand-measured true context fill twice during gauge blind windows and reported it as a
proven self-report mechanism worth packaging (#284). It was neither. `gauge_writer_hook.py:434/457`
already takes `transcript_path` off the hook payload and runs the same computation — **my hand-run was
the shipped writer, executed manually.** Same source, same arithmetic, zero new capability.

Worse as a proposal: it inverts Fred's design constraint (the reading is **pushed** by the engine on
tool use, never **pulled** by the agent) and fails exactly when needed, since a context-degraded agent
is the least likely to remember to pull.

**What the hand-run actually proved, and this is the useful part:** it worked only because printing a
number needs no destination. **The measurement never failed; the addressing did.** That collapses
#271, #286 and #287 into one root cause nobody was looking at.

**Candidate form:** before proposing a manual procedure as a mechanism, diff it against the automated
path. If the arithmetic is identical, you have found where the automated path *breaks*, not a
replacement for it. Corrected on the issue.

---

## C4 — Closeout discipline: a merged, harvested, swept issue can still be OPEN.

**Evidence:** #265 was merged (PR #283, `b69e6c8`), harvested and swept — and stayed **open** for the
rest of the wave because the PR carried no closing keyword and nobody checked. My log said "complete";
the state note said "complete"; **neither was the source of truth.** Found by accident.

**Candidate form:** the sweep step must query the tracker for issue state rather than assert it from
the Admiral's own notes. Cheap: one `gh issue view --json state` per swept issue. Not a new lesson so
much as a missing postcondition on an existing step — check whether it belongs in the sweep gate
rather than the playbook.

---

## Not candidates — logged so closeout does not re-litigate them

- **My HARD-band misreading** (read a speed bump as a wall, announced I was past it, recommended
  stopping). Behavioural, corrected by Fred, saved to durable memory. Not a playbook lesson — the
  engine already behaves correctly; only I did not.
- **Recurrence-debt carried in:** 2 constellation lessons, 2 unfixed recurrences, plus
  `verify-harness-field-and-drive-real-writer` at **5 confirmations** against a fix-upstream-at-4
  doctrine. Filed as **#285**. Paying it is a filing, not a lesson.
