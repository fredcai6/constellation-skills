# Cold plan critic — findings and my disposition

Critic: fresh Sonnet agent, no authoring context, read only `MISSION_FRAME.md`, `execute.json` and
`DESIGN_COMPARISON.md`. Full text: `.agent-work/567-k/crew-handoffs/critic-result.md`.

Panel-vs-single: **single critic**, not a 3-lens panel. Surfaced as a named choice, not a silent
one. Reason: the artifact under critique is a *gate plan for one issue*, and the design panel that
feeds it already ran three independent adversarial authors. Doctrine says "when in doubt, panel" —
I was not in doubt about the plan, and the critic was in fact given all three lenses to cover in
one pass. **Untaken road: a 3-lens panel on the plan itself.** If the Admiral wants it, it is cheap.

I triaged every finding. In delegated mode the launch order is the triaging authority; anything
beyond my latitude is floated rather than decided.

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | `g3-proof`'s two postconditions were `check: null` — unfalsifiable | blocking | **Fixed.** Both are now `command` checks. Proven to fail today (exit 1) and to pass only once the guard ships. |
| 2 | `specs/` claimed in scope but no gate touches it; `generate_spine.py` drops unknown keys | blocking | **Accepted; scope narrowed and floated.** Verified at `generate_spine.py:669-684`. `specs/` and the crew template are struck from this wave. |
| 3 | `g2` never checked *which* gates got the flag | should-fix | **Fixed.** `g2-integrate.c2` now asserts the exact bookend id set per template, mechanically. Proven to fail today. |
| 4 | The plan freezes but does not make replanning legible — the human's second half | should-fix | **Accepted as a measured limitation, stated plainly.** Not silently fixed: the remedy is role prose, and prose promotion is the human's call (`decision:no-doctrine-promotion`). Recorded in the return and in `g3-proof`'s constraints. |
| 5 | The "immediate protection or backward compat" trilemma is false | (in §5) | **Accepted and corrected in `DESIGN_COMPARISON.md`.** Added candidate **D** (positional opening + declared closing), credited to the critic, and attached the ship-time-retrofit escape to my recommendation. |
| 6 | I silently closed the `retext-check` question the comparison called open | overclaim | **Accepted.** Now an explicit, reasoned decision in `g1-implement`'s constraints, with candidate A's counter-argument named and the override justified. Surfaced as a decision candidate. |
| 7 | Reviewer absent from "every planning role" with no stated reasoning | overclaim | **Accepted.** Reasoning now written into `g1-implement`'s constraints: a survey's `amend` is already `retext-check`-only (`:3013-3029`), so a survey needs no bookend. |
| 8 | "Swapping the declaration form is one function" undercounts spec/compiler sync | overclaim | **Accepted.** True once `generate_spine.py` is in play. The claim is now scoped to the engine helper and the spec cost is named. |
| 9 | Crew's no-closing-bookend quietly opts crews out of a property every other role keeps | consider | **Accepted as a named trade-off**, now moot for this wave since the crew half is fenced out. Carried into the float so the Admiral sees it when ruling on `generate_spine.py`. |

**Nothing was rejected.** That is not deference — I checked findings 1, 2 and 3 myself before
accepting them, and finding 2 I verified twice (the compiler's field list, and the repo's own
recorded prior incident of the same divergence).

## What the critic did not catch, and I did

Re-reading my own file-ownership grant while triaging finding 2, I found that
`skills/implementer/templates/IMPLEMENTER_PLAN.template.json` never matched my ownership pattern
(`*SPINE*.template.json`) in the first place. My original `g2` would have written a file I was
never granted. The critic reached the same place by a different road — the compiler — but the
ownership error was mine and predates its read.
