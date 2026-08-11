# Design-it-twice Brief: the spec → spine seam, and the gate plan that builds it

Plan-phase form of the shared parallel-alternatives contract, run at the `plan` step of
`epic-559/c2-generate-the-spine`.

## The one thing being designed twice

**Where the seam sits between "what an author writes" and "the spine JSON the engine reads" — and
therefore what the gate plan has to prove, in what order.**

This is one decision, not a topic. Every candidate answers the same question: *given that a check is
the thing that breaks, what does the author hand the generator, and what does the generator refuse?*
The gate plan falls out of that answer, which is why one brief covers both.

Held fixed for every candidate (settled, not up for redesign):

- `checklist_engine.py`'s on-disk format does not change.
- `scripts/validate_spine.py` is the acceptance oracle and its fault set does not move.
- Beliefs / concerns / open questions ride in `constraints` / `directives`, never a new field.
- No shipped template is edited to make generator output validate.

## Count and panel — a surfaced choice

**Panel of 3.** This introduces a **load-bearing interface** — a spec format other authors will write
against, and whose weakness would reproduce the very defect the mission exists to remove. The
contract's own rule is "a load-bearing interface or architecture-touching plan runs a panel; when in
doubt, panel." Surfaced to the Admiral at plan approval and overturnable there.

## The constraints (one per agent, each distinct and named)

- **A — smallest-diff.** Fewest new files and least new machinery that can still emit implementer and
  reviewer spines the lint accepts.
- **B — most-testable.** Maximize what the generator can *falsify at generation time*; prefer a
  design where a wrong spec fails loudly in the generator rather than quietly at a gate.
- **C — best-seam-placement.** Put the boundary where the author and the tests actually want it, even
  if that costs more machinery — judged by what the author must type and what the tests can reach.

## Compared on

Depth · Locality · Seam placement · Testability — same four axes for all three.

## Framing block — presented to the Admiral WHILE the agents run

- **Constraints in play:** smallest-diff, most-testable, best-seam-placement. Chosen because the real
  tension in this mission is between shipping a thin thing that works and building a vocabulary rich
  enough that no author ever types a shell string.
- **Dependencies:** all three touch `scripts/validate_spine.py` (read-only), the resolver-owned token
  regex in `scripts/init_work_area.py`, and `checklist_engine.py`'s `_render_directive_lines`
  rendering contract (read-only). All three must express the corpus's self-checking pytest idiom.
- **Illustrative sketch — NOT A PROPOSAL, carries zero weight at convergence.** One plausible shape:
  a TOML spec whose checks are named kinds with typed fields (`tests = {selector, min}`,
  `script = {path, args}`, `artifact = {type, match}`, `qualitative = {because}`), compiled by a
  module that runs `validate()` before it writes anything. Offered only to prime parallel thinking.

## Output — a recommendation, never a menu

Recorded in "Convergence" below once the candidates land: one opinionated pick or a named hybrid,
defended axis by axis.

## Untaken-road record — loud skips

- **A fourth candidate under `max-flexibility`** (a spec that can express anything, including raw
  shell) was **not** generated. Reason: it is the null hypothesis of this mission — a spec that
  accepts a raw command is the hand-authored check with extra steps, and the launch order already
  names that outcome as the honest-null to report, not a design to fund a candidate on. It is
  instead carried as the **settling question** every candidate must answer.
- **No interface-phase (`design-it-twice` excursion) run.** Reason: the interface being chosen *is*
  the plan's first gate here, so the plan-phase form covers it without a second brief.

## Panel-vs-single record

Panel of 3, because the run introduces a load-bearing interface that other authors write against.
Surfaced here for the Admiral to overturn at plan approval.

## Convergence

All three candidates landed. **Recommendation: candidate C's seam, carrying candidate B's vocabulary
and escalation mechanism, with C's static AST guard in place of B's live-import probe.** Defended axis
by axis in `CANDIDATE_PLAN.md`; the short form:

- **Seam placement → C.** A pure translation function separated from every I/O act, at function
  granularity. It is also what makes the mission's required control pairing constructible: the same
  spec's translation completes on the pure path and is refused by the guarded entry point.
- **Vocabulary and depth → B.** Typed check kinds each carrying a generation-time probe keyed to one
  of the four historical defects. A's two kinds were smaller and A's own settling-question answer
  conceded why they were not enough: an argv list closes the shell-tokenization class and leaves the
  wrong-invocation class open.
- **Judgment carried up → B.** A large claim mechanically changes what the gate needs to close,
  rather than only rendering a note.
- **Probing a named script → C over B.** B imports the author-named module and runs its import-time
  code inside the generator, which is defect 2's own shape one layer up — a risk B itself named. C
  reads the target with `ast.parse` and never imports it.
- **A loses on the axis it optimized for.** A is the most readable and its `git-change-policy`
  omission is honestly costed, but smallest-diff optimizes for less typing when the mission is about
  making the wrong check impossible to author.

One finding was adopted from C outright and is not cosmetic: the engine passes `command` checks no
`cwd`, so every emitted check is anchored `cd <repo-root> && …`. `<repo-root>` is resolver-owned —
verified: `_RESOLVER_OWNED_TOKEN_RE.fullmatch("<repo-root>")` is true.

**Then the cold critic panel cut it further.** Two BLOCKING findings (both found by running the
engine) and seven SERIOUS/MINOR ones changed the design materially — the handback arrays were deleted
as unwritable, the escalation was re-pointed at a checked `review-result` verdict, the module became
one file, two gates merged into one, and two check kinds were cut. Every finding and its disposition
is in `plan-critic.md`; the executable result is `execute.json`.
