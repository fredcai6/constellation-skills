# Triage candidate — the `.agent-work/templates/.baseline/` mirror doubles every doctrine target, with no named reconciler

**Found at:** `g1b`, lane D1, epic #567 wave 2. Reported by the g1b implementer.

**What was found.** `.agent-work/templates/` is a tracked overlay of the skills templates, and it
carries a second tracked copy of itself under `.agent-work/templates/.baseline/<skill-name>/`. Both
are byte-identical to their `skills/` sources today, verified with `git hash-object` across all five
doctrine-carrying files.

So every doctrine target in this epic exists in **three** places: the `skills/` source, the overlay,
and the baseline mirror. Nine of the eighteen overlay violation addresses the guard reports are
`.baseline/` copies.

**Why it matters beyond this lane.** Whatever mechanism reconciles the overlay and promotes the
baselines has to re-run after any doctrine edit, or the two copies drift from the source silently —
and the copy an agent actually instantiates is the overlay, not the source. The most recent
reconciliation was manual and recorded as such: commit `f05a3d78`, *"reconcile 7 overlay templates
from repo source, promote 56 baselines."* This lane found the drift only because it extended a guard
to walk the overlay; nothing else in the repo reads it.

**The general shape:** a derived copy with no automatic reconciler and no freshness check is the
same failure class as a stale generated file, and this one carries doctrine.

**Why it is a candidate and not a fix.** This lane sweeps all three copies, so the immediate drift is
closed for #559's text. But *automating* the reconciliation, or putting a freshness test on the
overlay, is new machinery — architecture, which `Inherited Latitude` routes to the Admiral, and
scope this lane was not given.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.
