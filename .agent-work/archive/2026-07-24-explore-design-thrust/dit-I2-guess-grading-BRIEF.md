# Design-it-twice Brief: `I2 guess-grading schema`

## The one thing being designed twice

The **fixedness-grading schema for plan/spec decisions**: the markup and semantics by which a planning artifact (commander plan, admiral launch order, design spec) encodes, per decision, (a) its fixedness tier — settled vs working-guess vs placeholder, (b) why it holds that tier (provenance: human-ruled / measured / inherited constraint), and (c) for guesses: the cheapest experiment that would settle it (guess ledger). Consumers: the *executing agent* deciding mid-run whether revisiting is free or needs a reopen; the *reviewer* checking the plan graded honestly; a future *pre-flight linter* (batched plan-conflict check) hunting ungraded or contradictory decisions.

Evidence base (read these): `.agent-work/explore-design-thrust/IDEAS_BOARD.md` (ideas 6, 7, 10, 29; package C context: rolling-wave, plan-expiry, regenerate-don't-reread; the human's framing: "this part is settled" vs "current guess, revisit allowed" must be a normal distinction, revisiting a guess a normal move not a plan violation). Note the recorded fork: superpowers holds plans static-fine-grained; our bet is graded fixedness + rolling detail — the schema must serve OUR bet.

## Count and panel — a surfaced choice

**N=3 (panel).** Load-bearing: every planning skill writes it, every executor reads it; a bad schema becomes corpus-wide ceremony (the exact failure this exploration exists to avoid).

## The constraints (one per agent, each distinct and named)

1. **minimal-interface** — smallest markup that changes executor behavior; bias toward one inline tag and nothing else; every extra field must name the decision it changes downstream, else it's ceremony.
2. **max-flexibility** — richest coherent schema: arbitrary provenance kinds, confidence gradations, per-slice scoping, machine-parseable ledger; then state honestly what the minimum viable subset is.
3. **common-caller-first** — design outward from the two consuming moments: (a) an executor mid-gate hits a decision that contradicts observed reality — what does it need to read, right there, to know whether to proceed/revisit/escalate; (b) a reviewer/linter asks "is anything load-bearing still a guess?" — what query answers that.

## Compared on

- **Depth** — does the schema carry real decision-changing meaning, or is it labels for labels' sake?
- **Locality** — does grading live with the decision it grades (one place to update), or scatter (tag here, ledger there, drift between them)?
- **Seam placement** — does it sit where plans are already written/read (templates, launch orders), needing no new artifact type?
- **Testability** — can "executor treats guess vs fixed differently" and "linter finds ungraded load-bearing decisions" be exercised and falsified?

## Output — a recommendation, never a menu

Each agent returns ONE candidate schema in deep-module terms (the markup, its invariants, who writes/reads each field, error/degradation modes when a plan is partially graded) + self-scores on the four axes. The orchestrator synthesizes.

## Untaken-road record — loud skips

(maintained by the orchestrator in the spec)

## Panel-vs-single record

Panel of 3 — corpus-wide writer/reader surface.
