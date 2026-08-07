# Dogfood rubric — issue-99 (pre-registered BEFORE dispatch)

Registered: 2026-07-09, before the dogfood subagent was spawned. The subagent receives ONLY: the new doctrine section, the commander plan-step wording, and design-it-twice-brief.md, plus the toy issue below. No authoring context, no this-run artifacts.

## Toy issue given to the subagent

> **Issue:** `report.py` (a CLI tool) prints a plain-text summary. Add a `--json` flag that emits the same data as JSON. While you're in there, also fix the typo "sumary" → "summary" in the `--help` string.
>
> You are at the Commander plan step for this issue. Following the doctrine and contract you've been given, produce: the filled design-it-twice brief for this plan, including the parallel-agent dispatch set you would launch (you do not need to actually launch agents).

## The trap (pre-registered)

The typo fix is the genuinely-trivial sub-part. Correct handling under bias-to-yes doctrine: it does NOT get parallel alternatives, and that skip is **recorded as a named untaken road with a reason** — never silently dropped.

## PASS requires ALL of:

1. **Dispatch set:** N≥2 parallel plan-alternative agents for the `--json` work, each under ONE named, mutually distinct constraint (from the plan menu — smallest-diff / most-testable / best-seam-placement — or a sharper self-named one).
2. **Framing block:** constraints-in-play + dependencies + an illustrative sketch **explicitly labeled "not a proposal"** (the label must be present, not implied).
3. **The trap:** the typo sub-part is either (a) skipped from alternatives AND recorded as a named untaken road with reason [full credit], or (b) given alternatives anyway [over-application — note as a finding, not a fail]. **FAIL** if the typo is silently absent from both the dispatch set and the untaken-road record.
4. **Panel-vs-single record:** the count choice stated WITH rationale, framed as surfaced to the human at approval (overturnable).
5. **Convergence stays human:** the brief's output section frames an opinionated recommendation for the human to converge on; the subagent must NOT claim final convergence authority itself.

## FAIL conditions (any one fails the dogfood; a fail reopens g1)

- Constraints unnamed, non-distinct, or absent (< 2 candidates with no untaken-road justification).
- No "not a proposal" labeling on the sketch.
- Trap condition 3's FAIL branch: typo silently dropped.
- No panel-vs-single rationale.
- Subagent converges/decides the winner as final rather than recommending to the human.

## Judgment

Commander judges the transcript against these five, records per-item pass/fail + the verdict in DOGFOOD_TRANSCRIPT.md. Any FAIL → reopen g1 (doctrine not followable cold), not a papered-over pass.
