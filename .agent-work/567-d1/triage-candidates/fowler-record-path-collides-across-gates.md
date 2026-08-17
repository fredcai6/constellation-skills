# Triage candidate — the Fowler record path is per-work-id, so a second reviewer overwrites the first gate's audit evidence

**Found at:** `g1b-review`, lane D1, epic #567 wave 2. Reported by the g1b reviewer, which hit it
and repaired around it.

**What was found.** The review survey template hard-codes the Fowler-pass record at
`.agent-work/<work-id>/FOWLER_PASS.json`. That path is per **work-id**, not per **gate**. A run with
more than one reviewed gate has more than one reviewer writing it, and the second silently destroys
the first gate's audit evidence.

This lane has four reviewed gates. The `g1` reviewer's record was already sitting at that path when
the `g1b` reviewer arrived.

**Why it matters.** The default outcome is silent evidence loss, and it is loss of exactly the
artifact a later audit would reach for — the record of what the *previous* gate's reviewer judged.
Nothing fails; the file is simply different from what it was.

**What the g1b reviewer did instead**, which is the behaviour to keep: it moved its own record to
`.agent-work/567-d1/g1b-review/FOWLER_PASS.json` **through the engine's sanctioned repair path** — an
`amend --delta` with a single `retext-check` op, authority and reason recorded — rather than
hand-editing the survey or overwriting the sibling.

**Candidate fix.** Default the record to the survey's own directory rather than the work-id root, so
the per-gate path is the path a reviewer gets without having to notice the collision first.

**Why it is a candidate and not a fix.** The survey template is shipped doctrine
(`skills/reviewer/templates/REVIEW_SURVEY.template.json` and its overlay copies); changing a
template's default path is a doctrine change, and this lane's mission does not cover it. Recorded
rather than taken.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.
