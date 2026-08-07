# Design-it-twice Brief: `<short title>`

The shared parallel-alternatives contract. Run **N≥2 agents in parallel**, each producing ONE candidate under **one named distinct constraint**, then converge to a single recommendation. One brief designs **one thing twice** — if two decisions are in play, write two briefs. The point is to surface the structure no single pass sees.

Used two places for the same reason: explorer's excursion `design-it-twice` type is this contract in its **design-phase** form (comparing a module's *interface* before any issue exists); a plan step runs it in its **plan-phase** form (comparing gate *plans* for a confirmed issue). Same mechanism, filled once per run.

**Bias to yes.** Run it by default. Skip only a genuinely-trivial case — and a skip is never silent: it is recorded as a named **untaken road** (below) and surfaced at the approval checkpoint. **Convergence is human-only:** the agents generate and compare; the human picks the winner or the hybrid.

## The one thing being designed twice

`<the ONE interface or plan these candidates are alternatives for. Not a topic — a single load-bearing decision with a shape N agents can each realize differently.>`

## Count and panel — a surfaced choice

`<N, and why. Scale by weight: a load-bearing interface or an architecture-touching plan → a panel (3+); a fairly-easy call → 2, or a single with the alternatives named as untaken roads. "When in doubt, panel." State the count AND its rationale — this scaling choice is surfaced to the human at the approval checkpoint, not made silently, and the human may overturn it.>`

## The constraints (one per agent, each distinct and named)

Each agent designs the SAME thing under exactly ONE constraint. The menus are starting points — a run may name its own constraint when it sharpens the contrast.

- **For an interface:** minimal-interface · max-flexibility · common-caller-first · ports-and-adapters
- **For a plan:** smallest-diff · most-testable · best-seam-placement

`<the N constraints actually assigned, one per agent — each named, each distinct>`

## Compared on

Every candidate is scored on the same axes so the comparison is like-for-like:

- **Depth** — `<does it hide the right complexity behind the seam, or leak it upward?>`
- **Locality** — `<is the change contained, or does it fan out across the codebase?>`
- **Seam placement** — `<is the boundary drawn where the caller and the tests actually want it?>`
- **Testability** — `<can each pathway be exercised and falsified on its own?>`

## Framing block — presented to the human WHILE the agents run

So the human reasons in parallel with the fan-out instead of waiting on it. Present, before any candidate lands:

- **Constraints in play** — the N named constraints and why each was chosen.
- **Dependencies** — what each candidate will have to touch or assume, and what is held fixed for all of them.
- **Illustrative sketch — explicitly marked "not a proposal".** A rough shape of one plausible direction, offered only to prime parallel thinking. It is **not a proposal** and **not a recommendation**: it must not anchor the outcome and carries zero weight at convergence. Label it as such in the presentation so no reader mistakes it for the intended answer.

## Output — a recommendation, never a menu

`<the opinionated pick, or a named hybrid ("candidate B's seam with candidate A's caller signature"), plus the axis-by-axis reason it won. Handing back a menu of options for the human to re-compare from scratch is a failed run — the comparison IS the deliverable. Convergence stays the human's; this brief hands them a defended recommendation, not the raw candidate pile.>`

## Untaken-road record — loud skips

Every alternative NOT generated is named here with its reason, and surfaced at the approval checkpoint. A skip is never silent:

- `<the constraint, candidate, or whole run that was skipped — and why it was judged genuinely-trivial / not worth a parallel candidate. One row per untaken road.>`

## Panel-vs-single record

`<the count/panel decision and its rationale, restated for the approval checkpoint so the human sees — and can overturn — the scaling call: "single, because fairly-easy"; "panel, because it touches architecture"; etc.>`
