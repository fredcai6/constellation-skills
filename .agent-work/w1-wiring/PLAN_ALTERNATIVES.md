# Plan Alternatives: w1-wiring

## The one thing being designed twice

The gate-plan shape for w1-wiring: how many gates, and where the reasoning/document work ends and
the code-producing disposition (deletions or a lint) begins.

## Count and panel — a surfaced choice

**N=2, single pass, not a panel.** This plan is not architecture-touching in the sense the panel
trigger means (no new interface, no new module family) — it is an investigation-then-bounded-action
run. Two candidates under distinct constraints is enough to see the real tradeoff (bundled vs.
split gates); a 3-lens panel would mostly re-litigate the same axis.

**Deviation, recorded:** the contract calls for **N≥2 agents in parallel**. This dispatched context
has no Task/Agent tool on its surface (Bash, Read, Write, Edit, WebFetch, WebSearch, Skill only) —
`run_crew.py`'s `external` backend requires dispatching a synchronous Agent-tool subagent, which is
unavailable here. Both candidates above were authored sequentially, by the same agent, in the same
context — not by independent parallel authors. This weakens the "structure no single pass sees"
property design-it-twice exists for; it does not remove the comparison itself. Reported again in
Workflow Feedback.

## The constraints (one per candidate)

- **smallest-diff** — `.agent-work/w1-wiring/plan-candidate-smallest-diff.md` — minimize gate count
  and total diff; fold disposition into the census gate.
- **most-testable** — `.agent-work/w1-wiring/plan-candidate-most-testable.md` — maximize
  independently-falsifiable gates; separate reasoning findings from the code-producing gate.

## Compared on

| Axis | smallest-diff | most-testable |
|---|---|---|
| Depth | One document, low overhead | Higher ceremony, each finding isolated |
| Locality | Two commits total | Disposition isolated from reasoning gates |
| Seam placement | Lint (if any) at cheapest seam, same gate as its own decision | Same, but decided in a separate gate from the census |
| Testability | Verification named per-gate but findings bundled | Verification command named per-gate, findings separable |

## Framing block (presented before authoring, for the record)

- **Constraints in play**: smallest-diff (ceremony cost) vs. most-testable (falsifiability cost).
  Both hold fixed: census comes first, disposition follows from it, `checklist_engine.py`/
  `validate_spine.py` stay untouched (fence).
- **Dependencies**: both need the same evidence — a full `scripts/` census, `generate_spine.py`
  caller trace, `#368`/`#444` field counts. Neither changes what is measured, only how the measuring
  and the acting are grouped into gates.
- **Illustrative sketch — NOT a proposal**: "one big census gate, one disposition gate" is the rough
  shape either candidate could collapse to; not the recommendation below, offered only to prime the
  comparison.

## Output — recommendation

**Hybrid, closer to most-testable's separation but trimmed to four gates, not five.** Keep g1
(census), g2 (`generate_spine.py` disposition), g3 (#368/#444 re-measurement) as **separate reasoning
gates** — most-testable's case that each is independently citable and feeds a different downstream
consumer (wave 2 for g2, the human's own field-group question for g3) is correct, and the mission's
Return Shape section literally itemizes these as separate required contents, so splitting them
matches what the artifact must report anyway. Collapse most-testable's g4 (disposition) and g5 (map
impact) into **one final gate, g4**, per smallest-diff's case that ceremony should track real risk —
map impact here is "report a finding" (no live map to reconcile against, per the Mission Frame's Map
Confidence section), not a genuine Cartographer-shaped reconciliation, so it does not earn a fifth
gate. g4 covers: disposition (delete dead scripts, or author+wire+prove a lint, or both), and the
map-impact report.

**Axis-by-axis reason**: most-testable wins on Testability and Locality (separating g1-g3 keeps each
Return-Shape item independently checkable); smallest-diff wins on Depth for the map-impact half
specifically, because that half has no real reconciliation work to isolate this run (the map is
absent, not stale — nothing to reconcile against). The hybrid takes each candidate's win on its own
axis rather than forcing one candidate to dominate.

## Untaken-road record

- **A 3-lens critic panel** — not run; this plan is not architecture-touching, single critic pass
  judged sufficient (see `PLAN_CRITIC.md`).
- **True parallel dispatch of the two candidates** — not available (no Task/Agent tool in this
  dispatched context); both authored sequentially by this agent instead. See deviation note above.
- **A fifth gate splitting disposition from map-impact** — most-testable's original shape; folded
  into one gate because the map-impact half is a report, not independent work.

## Panel-vs-single record

Single critic, not a panel: this run's gate plan touches no new interface or architecture, and the
central decision (mechanism vs. deletion) is the census's own evidence, not a design choice a panel
would sharpen. Restated at plan approval below.
