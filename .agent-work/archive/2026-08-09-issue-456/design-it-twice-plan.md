# Design-it-twice Brief: the issue-456 gate plan

Plan-phase form of the shared parallel-alternatives contract. Filled once for
this run.

## The one thing being designed twice

**The gate plan for issue #456** — how the ten gates are bounded, sequenced, and
seamed inside `scripts/code_map/`. One load-bearing decision: the decomposition
and order that everything else in the run inherits. Not the tool's behavior
(that is confirmed in the spec and is not up for redesign) — only the plan for
building it.

## Count and panel — a surfaced choice

**N = 3 (panel).** Rationale: this run stands up a new package in a repo whose
42 tooling scripts are flat, and commits to a ten-gate sequence that later gates
cannot cheaply undo. That is architecture-touching, and the brief's own rule is
"when in doubt, panel." A 2-candidate run was considered and rejected: the
smallest-diff/most-testable pair alone would have left the module-boundary
question — the one a later gate cannot walk back — unexamined by anyone.

Surfaced to the human at plan approval, and overturnable there.

## The constraints (one per agent, each distinct and named)

- **smallest-diff** — fewest moving parts, files, and touched lines; fold gates
  together where they touch the same line; resist abstraction a later gate would
  have to justify.
- **most-testable** — every gate can go red on its own from a falsifier that
  exists before the fix does; name the fixture or corpus that makes each test
  fail TODAY. More gates and more scaffolding are acceptable costs.
- **best-seam-placement** — draw the module boundaries where the callers and the
  tests want them and let the gate sequence follow; identify the pure decision
  layer (no filesystem, no subprocess, no clock) first, because a wrong seam is
  what later gates cannot cheaply undo.

## Compared on

- **Depth** — does it hide the right complexity behind the seam, or leak it up?
- **Locality** — is the change contained, or does it fan out?
- **Seam placement** — is the boundary where the caller and the tests want it?
- **Testability** — can each pathway be exercised and falsified on its own?

## Framing block — presented to the human WHILE the agents ran

Presented before any candidate landed, so the human reasoned in parallel with
the fan-out rather than waiting on it:

- **Constraints in play** — the three above, with the reason each was chosen.
- **Dependencies / held fixed for all three** — stdlib-only (CI installs only
  pytest and coverage); the human's four rulings; positions out of the committed
  store; the live 5-file/9-line skills integration must keep working.
- **Illustrative sketch, explicitly marked NOT a proposal** — gate 0 CLI →
  gate 1 checks → gates 2/3 as one line → 4 schema merge → 5-9. This is the
  issue's own ordering, offered only to prime parallel thinking. Zero weight at
  convergence; it must not anchor the outcome.

## Output — a recommendation, never a menu

**Status: DELIVERED, 2 of 3.** `smallest-diff` and `most-testable` both returned
complete candidates. `best-seam-placement` went idle without delivering — its
constraint is therefore an **untaken road in practice**, and both delivered
candidates independently named the same thing they would have stolen from it (a
`Page` value the renderer builds and the checker reads, replacing a
provenance-tagged line builder), which is some evidence of what that arm would
have said.

**The panel earned its cost twice over, in ways the cold critic did not reach.**

1. **`most-testable` independently re-derived the D2 truth** — same 4 collisions,
   same closure-in-method mechanism, from its own script, having contested the
   probe rather than trusting it. Independent convergence on a fact that three
   prior passes got wrong.
2. **It then found an arm nobody else had.** `astx.py:visit_ClassDef` has *no*
   enclosing-chain branch, so a class defined inside a function is emitted as
   `mod:Name` as if module-level. **Verified: 0 occurrences on this corpus**
   (`reference/d2_arms.txt`). So that arm cannot go red here at any threshold and
   needs a purpose-built fixture, exactly like BOM — and a gate closing on
   "4 → 0" would ship it unwritten. This is folded into g2.
3. **Both candidates independently found that g4's top-index falsifier cannot
   fire here** — 103 modules over three directories makes a flat index ~115
   lines, so no size threshold distinguishes before from after. `smallest-diff`
   put it sharpest: it refused to propose a threshold that would have passed
   before the change. Folded in as a stated non-firing falsifier.

**Convergence.** `most-testable` is the stronger candidate and is the
recommendation. Its port-defective-then-fix mechanism (port the defect, capture
the RED, fix, then commit a mutation entry proving the test kills it) is the
only proposal here that makes "the check can fail" checkable rather than
asserted, and it reuses this repo's existing `test_mutation_floor.py` idiom
rather than inventing one.

**Named hybrid, not a wholesale pick.** Take `most-testable`'s mechanism, its
two-arm g2, and its grading of every falsifier as A (reproduces on real input
today) or B (red-by-absence, where the negative control *is* the falsifier).
Take from `smallest-diff`: thresholds as annotated module constants rather than
a committed JSON file, following `scripts/curate_corpus.py`'s precedent; the
check stage reaching CI by being a test rather than a workflow step; and its
refusal to stage the ~3,500-file map tree until the final gate, which keeps six
intermediate gate diffs reviewable. Both agreed to steal the same seam from the
arm that never delivered; that seam is worth adopting on their joint word.

**One thing both candidates said that outranks the plan itself:** the risk that
baselines self-certify — a number derived from the tool's own output cannot
disagree with the tool. It fired twice today inside the artifacts built to
prevent it. The rule to hold: every committed count derives from an independent
source (`git ls-files`, a deliberately naive second scanner), and any rule used
as an oracle must first be shown to agree with the rule under test on a
hand-labelled case. Where no independent derivation exists, the entry is
labelled an observation with a tolerance and a direction — not an oracle.

## Untaken-road record — loud skips

- **ports-and-adapters and max-flexibility as constraints** — not generated.
  Both are interface-shape constraints from the menu's interface half; this is a
  plan-phase run and the tool's interface is already confirmed in the spec, so a
  candidate under either would have redesigned a settled thing.
- **common-caller-first** — not generated. The primary caller (a dispatched crew
  agent being handed starting pages) is already built and live in the skills
  integration, so this constraint has no room to produce contrast here.
- **A no-crew / single-author candidate** — not generated. The human ruled crews
  on for this run; a candidate under a constraint the human already closed would
  be a re-litigation, not an alternative.

## Panel-vs-single record

**Panel of 3, because it touches architecture** — a new package layout plus a
ten-gate sequence with real ordering pressure between them. Stated here so the
human sees and can overturn the scaling call at plan approval.
