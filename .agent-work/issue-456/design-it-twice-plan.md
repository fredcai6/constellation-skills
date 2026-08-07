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

**Status: the panel was RUN but has not DELIVERED.** All three candidates were
dispatched under their named constraints and were sent two rounds of corrections
mid-flight (the corpus baseline, and the retraction of the collision figures).
None has returned a candidate. This is recorded as a fact rather than smoothed
over: the mechanism fired, the deliverable did not arrive.

What that costs, stated plainly: the comparison — which *is* the deliverable of
this contract — did not happen across three independently-generated candidates.
It happened instead between the Commander's own draft and a **cold plan critic**
that did return, in full, with 15 findings of which 4 were blocking and several
were verified against the repo rather than asserted. That is a real adversarial
pass, but it is a critique of one candidate, not a comparison of three.

**The recommendation carried to the approval checkpoint is therefore Shape B**
(see `plan-shape-options.md`), on one axis: it is the only shape in which g1's
checks stay falsifiable through the end of the run. That recommendation comes
from the critic's F1 plus the Commander's own verification, not from a
three-way convergence.

**The human should know the panel arm is missing when weighing it**, and may
reasonably choose to re-run the panel before freezing. If the candidates land
late they will be folded in and this section updated rather than left stale.

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
