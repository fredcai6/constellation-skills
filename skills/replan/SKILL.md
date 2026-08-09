---
name: constellation-replan
description: Classify wave evidence and produce one strict advance, repair, replan, or stop transition while preserving launched identities and fixed intent. Use when a launched wave reaches a boundary or material exception and the next planning truth must be explicit. Not to-initial-issues (which makes the first cut), and not Admiral (which owns epic execution).
invoker: both
---

# Constellation Replan

Classify the observed wave evidence, choose one exit, and disposition every
affected or unlaunched item before another wave launches.

**No checklist. Work the evidence pass directly** — a lean offline pass, not a
gated engine. Code validates the strict transition; the agent authors the
planning judgment.

## The rail

`scripts/verify_replan.py` refuses malformed v1 packets, incomplete or duplicate
dispositions, invalid replacements, unstable launched identities, repair drift,
and fixed-boundary changes without typed human escalation. It never chooses the
exit or creates tracker work.

## Steps

1. **Read current truth and evidence.** Start from one exact G1 plan. Record
   completed outcomes, at least one observed-vs-expected evidence entry,
   discrepancies, open launched identities, unlaunched items, and repository
   state in `REPLAN_INPUT`.
2. **Classify every discrepancy.** Use the five classifications in
   `references/contracts.md`; do not turn evidence-only or dropped signals into
   issues.
3. **Choose exactly one exit.** `advance` accepts the next supported truth;
   `repair` holds the current wave and forecast; `replan` revises unlaunched
   truth; `stop` may end with no current wave.
4. **Disposition everything.** Give every discrepancy and unlaunched identity
   exactly one action and reason. Preserve open launched issues. A fixed-intent
   proposal is inapplicable until the named human authority decides it.
5. **Verify and render offline.** Run
   `python scripts/verify_replan.py REPLAN_INPUT.json REPLAN_RESULT.json`. Fix the
   packet rather than weakening the claim.
6. **Hand to independent review.** A fresh reviewer checks exit judgment,
   completion sharpness, negative space, and whether the revised Markdown says
   the current truth without laundering forecast into commitment.

Stop before launching more work if verification fails or a fixed-boundary
proposal lacks human authority. The pass is done only when the verifier clears,
both Markdown surfaces are nonempty, and independent review accepts the result.
