# Plan-alternatives (design-it-twice, plan-phase) — issue #300 gate plan

Distinct from the **interface** design-it-twice at `.agent-work/300/DIT-COMPARISON.md`. One brief
designs one thing: that one compared *manifest interfaces*; this one compares *gate plans* for the
already-chosen interface.

## Panel-vs-single record

**N = 3 (two independent authors plus the Commander's own candidate), lightweight.** Rationale: the
interface panel already ran at full weight and its recommendation heavily constrains the gate plan,
so the remaining design space is sequencing and evidence placement, not shape. `lesson:lightweight-
critic-catches-real-findings-on-bounded-issues` says even a light pass on a bounded issue earns its
keep — and it did here. Surfaced for overturn: an Admiral who wants a full panel on the gate plan
too can say so.

| Candidate | Constraint | Author |
|---|---|---|
| seam-first | (Commander's own) cut at the run-time / ahead-of-time / doctrine seams | this context |
| smallest-diff | minimise files touched and total churn | subagent, Sonnet |
| most-testable | every gate boundary falsifiable in isolation; hardest evidence earliest | subagent, Sonnet |

Artifacts: `.agent-work/300/plan-alt/ALT-smallest-diff.md`, `.agent-work/300/plan-alt/ALT-most-testable.md`.

## Untaken roads

- **`best-seam-placement` as a fourth constraint** — not generated. Reason: the interface panel
  already settled seam placement (reuse `active_id()`; producer beside the engine's projection
  port), so a gate plan authored under that constraint would restate a settled decision rather than
  contrast with anything.

## What each candidate contributed, and the convergence

**Taken from `most-testable`:** its central move — prove cross-environment determinism *as early as
it can possibly be proved* rather than at the end. I did not take its literal ordering (a standalone
core module before any schema exists), but I took the principle, and the converged plan proves
determinism in **g1**, on the run manifest, rather than deferring it into the contingent gate.
This mattered more than it looked: the cold plan critic independently reached the same conclusion
by a different route (its B5 — the pre-ruled acceptance test was sitting inside the one gate an
Admiral ruling could delete). Two independent sources converging on the same defect is the strongest
signal this pass produced.

**Rejected from `most-testable`:** core-first ordering (rev-identity module before the declaration
schema). Its own author named the cost honestly — synthetic fixtures instead of real spines breaks
"drive the real writer, not a hand-built fixture", and a later schema change reopens an already-closed
core. Schema-first surfaces that surprise in design rather than in code.

**Taken from `smallest-diff`:** its observation that under a minimal cut, #300 ships a generator that
has never generated a real diff for a human to look at — the substrate's stated purpose proven by
tests but never demonstrated. That is a genuinely useful framing of what the floated convergence
choice is actually about, and it has been relayed to the Admiral.

**Rejected from `smallest-diff`:** collapsing to four gates with the whole substrate in one dispatch.
Two reasons. (1) Any single failing postcondition reopens resolver, verb, docs and lint together —
the rework blast radius is the whole issue. (2) It folds the required full cold panel into the
ordinary review step; `decision:full-cold-panel` makes panel depth the floor for #300, and a folded
panel is a light pass wearing a panel's name. Its author flagged this interpretive risk rather than
assuming it away, which was the right call.

**Kept from the Commander's own candidate:** the three-way seam (run-time half / ahead-of-time half /
doctrine) — because it is what isolates the contingency. Exactly one gate depends on the floated
convergence choice, and after the critic's B5 fix, deleting that gate leaves issue #300 whole.

## Converged plan

`.agent-work/300/execute.json` — 11 items: `e0-context`, g1 (run-time half: identity, `context_refs`
declaration, producer, run manifest, the first real declaration, cross-environment determinism),
g2 (contingent: the committed artifact and its generator), g3 (doctrine, lint, #301 obligations),
`g4-cold-panel`.

This is a recommendation, not a menu: one plan, with the reasons each rejected element was rejected
recorded above rather than handed back for re-comparison.
