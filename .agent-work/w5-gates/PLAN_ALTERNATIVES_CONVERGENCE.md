# Plan-alternatives convergence — w5-gates

Three candidates ran in parallel under three distinct named constraints, per
`PLAN_ALTERNATIVES_BRIEF.md`. Candidates are in `plan-alternatives/`.

| Candidate | Constraint | Gate count | Cut |
|---|---|---|---|
| `candidate-smallest-diff.md` | smallest-diff | **1** | one gate carrying all three fixes |
| `candidate-most-testable.md` | most-testable | **5** | fix C · fix B · fix A golden · fix A mutation floor · integration |
| `candidate-best-seam.md` | best-seam-placement | **3** | location guard · stop-boundary semantics · archive reachability |

## Recommendation — a named hybrid, not a menu

**Take `best-seam`'s three concept gates, weld `most-testable`'s falsifying-input requirement into
every gate's close criteria, and add `most-testable`'s integration gate as a fourth.** Reorder so the
location guard runs first.

Axis by axis:

- **Seam placement — `best-seam` wins outright.** It is the only candidate that read the source
  before cutting, and it found the fact that decides the question: fixes A and B sit in the same file
  but in cleanly separable functions with no shared runtime state. So the file is not the seam; the
  concept is. "Where am I running from" and "what does a `stop` boundary have to prove" are two
  things a reviewer should not have to hold at once. `smallest-diff` concedes this axis explicitly
  and calls itself the worst candidate on it.
- **Testability — `most-testable` wins, and its contribution survives as a requirement rather than as
  gates.** It named a concrete falsifying input for all five of its gates without inventing one,
  which is the direct answer to this epic's central finding. That belongs in every gate's close
  criteria whatever the cut is. But its own weakness is real and it stated it: three of its five
  gates touch the same small file, and its mutation-floor gate's "seam" is not a code boundary at all
  — it is a claim about coverage. Pre-ruling 2 requires the mutation **test**, not a separate gate.
  So the mutation floor lands as its own **postcondition id** inside the fix-A gate — separately
  satisfiable, separately falsifiable, and not satisfiable by the golden-path test — which buys
  everything the split bought without fragmenting the file across three review passes.
- **Locality — `smallest-diff` wins on churn and loses on review load.** Its one-gate claim rests on
  "nothing forces a boundary", which is true of correctness and false of review: one implementer
  handoff carrying a shell-parsing defect, a filesystem-detection defect, and a decision-semantics
  defect is three concepts in one protected intent. Doctrine also requires one gate per file and
  decision-class in the ownership scope, and there are three decision classes here. One gate cannot
  satisfy that.
- **Depth — the integration gate is the one thing all three cuts otherwise miss.** `most-testable`'s
  argument is the deciding one: four green gates do not prove the three fixes compose through the
  real artifact. This run's own spine closes `execute` on
  `verify_iterative_role_artifacts.py commander --work-id w5-gates`, which today **cannot pass from
  this worktree** — that is finding 2. A fourth gate that runs it for real converts the run's own
  closure check from a formality into evidence.

## The one ordering change

`best-seam` sequenced the guard first for "same-file serialization and reviewer locality" and flagged
that ordering as editorial rather than technical. **It is technical.** The guard is what decides
whether `verify_iterative_role_artifacts.py` runs at all from this worktree; until fix B lands, every
command-line verification of fix A from here refuses before reaching the code under test. Guard
first is a real dependency, not narrative preference.

## What each candidate contributed

- `best-seam`: the concept seam, and the source reading that justified it.
- `most-testable`: the falsifying-input requirement, and the integration gate.
- `smallest-diff`: the useful negative — it made the cost of splitting explicit, which is why the
  mutation floor is a postcondition rather than a fourth gate.

## Panel-vs-single record (surfaced at approval)

**Panel of 3, because this is verification machinery the epic's own close depends on.** The approver
may overturn the scaling call. Untaken roads, restated: the interface-menu constraints
(`common-caller-first`, `ports-and-adapters`, `minimal-interface`, `max-flexibility`) were not
assigned — this is a plan-phase run, not an interface-phase one; and a fourth candidate under
"fewest-crew-dispatches" was not generated, because dispatch count is a cost axis already visible in
every candidate's gate count.
