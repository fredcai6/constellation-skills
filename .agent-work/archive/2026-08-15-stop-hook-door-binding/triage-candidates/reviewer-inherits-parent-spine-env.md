# Triage Recommendation: `a dispatched reviewer inherits the parent Commander's own SPINE_FILE/SPINE_SESSION, undocumented`

## Classification
`missing doc`

## Source checklist/artifact
- `g1-review`'s Workflow Feedback (`.agent-work/stop-hook-door-binding/crew-handoffs/g1-review-reviewer-result.md`).

## Structural anchor
`references/crew-dispatch.md` (its "MCP door" section); `scripts/run_crew.py`

## Cartographer mismatch class
None.

## Desired behavior
- **Desired:** `crew-dispatch.md` states plainly what a dispatched reviewer's `SPINE_FILE`/`SPINE_SESSION`
  environment actually holds when the Commander dispatch does not pass `--spine` (this gate's dispatch used
  `--handoff`/`--result` only, no `--spine`), so a reviewer does not have to infer it from a mismatch
  between its env and the reference doc.
- **Today instead:** the reviewer inherited the parent Commander's own bound spine
  (`.../spine.json`, `execute` gate) in `SPINE_FILE`/`SPINE_SESSION`, not a fresh reviewer-scoped
  survey/spine. It correctly did NOT drive the MCP door against that inherited binding (doing so would have
  mutated the Commander's own `execute` gate) and fell back to its own CLI-driven survey at the path the
  handoff named -- the reviewer skill's documented fallback for "nothing is bound for me" -- but had to
  reason this out rather than being told directly.
- **Type:** `measured` -- read from the reviewer's own `IMPLEMENTER_RESULT`-sibling report this run
  produced; the reviewer names the exact env values it observed and the fallback path it took.
- **Rev:** as observed 2026-08-15, this run's `g1-review` dispatch (`run_crew.py --handoff ... --result ...`,
  no `--spine`).

## Recommended priority
`low`

**Reason:** no incorrect behavior resulted (the reviewer's fallback was correct and matches documented
doctrine), but a future reviewer without this run's reasoning could plausibly try to drive the door against
the inherited parent binding and corrupt the Commander's own `execute` gate state.

## Related artifacts
- `.agent-work/stop-hook-door-binding/crew-handoffs/g1-review-reviewer-result.md`

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: references/crew-dispatch.md is outside this run's File Ownership fence
(scripts/hooks/spine_rail.py, tests/test_spine_rail.py, the PostToolUse block of .claude/settings.json
only). No tracker-filing authority exercised.`

## Issue creation authority
`issue-ready only`
