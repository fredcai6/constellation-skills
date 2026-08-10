---
name: constellation-diagnose
description: Investigate a break (a runtime bug or an intent-vs-execution disconnect) by running one evidence loop until the cause is reproduced, then routing it out. Use when observed behavior disagrees with intent and the mechanism must be found, not guessed. Not triage, not reviewer: diagnose finds the cause, never fixes.
invoker: both
---

# Constellation Diagnose

Find the mechanism behind something breaking; never call a cause *confirmed*
until reproduced. Diagnose does not fix — a real fault routes OUT to triage or
the reviewer, an explained-by-design finding is a note; it owns no durable truth.

**No checklist. Work the loop directly.** A commander or human invokes it,
stamping only intake and output format, never the loop. (A scout feed and
cleanup caller are forward-compatible seams, not built.)

## One loop, two altitudes

A runtime bug and an intent-vs-execution disconnect are the **same object**:
observed behavior disagreeing with intended. The loop is identical; only the
**oracle** (what reproduces it) differs.

| Altitude | The disagreement | The oracle (reproduce step) |
|---|---|---|
| **runtime** | code does the wrong thing | a **test** that fails on the bug |
| **disconnect** | execution drifted from the map/intent | the **map/intent probed** against behavior |

Run the same loop at either altitude: **reproduce** (show the disagreement on
demand through the oracle) → **localize** → **hypothesize** (a mechanism *and its
named falsifier*) → **instrument** (a probe for the falsifier) → **verify** (if
the falsifier fires, loop back; else the cause is reproduced).

## The one rail — reproduce-before-you-claim

`scripts/verify_diagnosis.py` refuses a `confirmed` finding without a named
`falsifier` AND an observed `observed_result` — a cause is never confirmed by
assertion. A trivial one-line cause skips the loop only with the **independent
reviewer's co-sign**: a `rail_exception` carrying `reviewer_cosign` and `log`.
The reviewer, not the author, judges the skip; self-assertion never passes. The
right-mechanism judgment is the reviewer's too.

## Accepted risk — map staleness (disconnect altitude)

For a disconnect the **map/intent is the oracle**; a stale map yields false
verdicts, and that soundness is **not gated** here. Every `disconnect` finding
carries a `map_staleness_caveat` the reviewer weighs; a map itself in doubt
routes to Cartographer.

## Steps

1. **Take intake**; pick the altitude (wrong result → runtime; drift from the
   map/intent → disconnect).
2. **Run the loop** until reproduced or the trail runs cold; record the finding
   with `templates/FINDING.template.json`.
3. **Clear the rail:** `python <skill-dir>/scripts/verify_diagnosis.py <finding.json>` — fix the
   evidence, never lower the claim to pass.
4. **Route out (don't fix).** Confirmed fault → `triage`/`reviewer`;
   explained-by-design → `note`. A fresh-context reviewer checks the cut.

A cold trail is a complete result: report the evidence so far and what breaks
the leading hypothesis, never a guessed cause. Schema: `references/loop.md`.
