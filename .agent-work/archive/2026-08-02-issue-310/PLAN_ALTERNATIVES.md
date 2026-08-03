# Plan alternatives — issue #310 (design-it-twice)

Per `references/design-it-twice-brief.md` and `global-orchestrator.md` §Design-it-twice.
**Count/panel choice, surfaced not silent:** 3 candidates (2 independently authored by cold agents under
distinct constraints, 1 authored by the Commander), plus a cold plan critic on the converged plan.
Panel rather than single because this run's output is evidence that will be used to make an
**architecture-touching decision** — "when in doubt, panel."

**Framing block for the human — NOT A PROPOSAL.** The real design freedom here is narrow: the confirmed
spec names the two evidence gates, and the issue names the verdict document. What is genuinely open is
*how the trend is sampled*, and that choice decides how attackable the resulting numbers are.

---

## Feasibility fact established before converging (measured at `dbd5414`)

| probe | result |
|---|---|
| total commits on branch | **442** |
| commits touching `skills/` | **184** |
| `git ls-tree -r -l HEAD -- skills/` | **100 entries**, wall clock **0.101 s** |
| directories under `skills/` | **20** — of which `_shared/` is not a skill ⇒ **19 skills** |

Two consequences, and they reshape the comparison:

1. **`README.md`'s "The corpus is 19 skills" VERIFIES** against `ls -d skills/*/` (20 dirs − `_shared/`).
   The mission frame flagged that count as unverified prose in a substitute; it is now checked.
2. **Full history is cheap, and the usual objection to it does not apply here.** `git ls-tree -r -l`
   reports **blob sizes directly**, so a whole-history byte series needs **no checkout and no content
   read** — 184 invocations at ~0.1 s ≈ 20 s total. The expensive part is only the *content* parse
   (reading each `SKILL.md` to find which `references/` it names), and that batches through
   `git cat-file --batch`. **Candidate B's cost objection is therefore largely void**, which is exactly
   what running the alternatives was for.

---

## Candidate C (Commander) — hybrid: full-history for bytes, content-parse for bins

**Constraint:** *no hand-chosen revision may be load-bearing.*

- Whole-history byte series for the corpus and for every per-role path, from `ls-tree` sizes alone.
- Content-parse (which `references/` does `SKILL.md` name?) only at a set of revisions, because that is
  the only step whose cost scales badly — and the sampled set is then a *presentation* choice, not the
  measurement, so disputing it cannot move the curve.
- Both bins always separate; the recombination arithmetic published so a reader who rejects the
  always-loaded convention can redo the split without re-running anything.

**Gates:**

| gate | kind | deliverable | close criteria |
|---|---|---|---|
| **g1** | **crew** | trend instrument + dataset: `trends/measure_surface.py`, `trends.json`, `TRENDS.md` | reproducible by one command; 19 skills enumerated **with the count asserted**; both bins separate; every number revision-pinned; 184 skills-touching commits accounted for or the exclusion stated |
| **g2** | reasoning | gate (b): impossibility of the controlled arm stated FIRST, then observational artifact-sufficiency evidence from the epic's own refresh/cold-start record | limitation stated before any evidence; every datapoint traceable to a run artifact; no monolith-arm comparison claimed |
| **g3** | reasoning | `B2_GATE_EVIDENCE.md` — the verdict packet: three outcomes, which the evidence selects, threshold sensitivity handed to Tommy | names one of exactly three outcomes; states the threshold that would flip it; makes no break decision |

g1 is a crew gate because it produces **code whose output is the entire deliverable** — an independent
reviewer re-running the instrument is the highest-value verification in this run. g2 and g3 are reasoning
gates: their deliverables are a diagnosis and a document, the context is already held, and
`commander-core.md` is explicit that a crew on a pure design note is *shallower, not safer*.

**Weakness, stated:** a per-commit curve still does not answer "small enough" — no sampling scheme can,
because the threshold does not exist. C mitigates by making the curve's *shape* (monotone? inflected at
deletion events?) the reported finding, since shape is threshold-free.

---

## Candidates A and B

Authored independently by cold agents under the constraints *sampled-revisions* (A) and
*full-history-mechanical* (B). Their returns are recorded in `PLAN_CRITIQUE.md` alongside the cold plan
critic's findings, and the convergence is recorded there.

---

## Untaken roads (named, per bias-to-yes)

- **A per-role competence arm built by first authoring a throwaway kernel+fragments decomposition of one
  role.** Not taken: it is the break, at prototype scale, and would take the run past its runway; more
  importantly a decomposition authored by the same agent that then grades it is not a controlled arm.
  Named here so the road is visible, not silently skipped.
- **Re-running #307's capture harness against a fragment corpus.** Not taken for the same reason — there
  is no fragment corpus to point it at.
- **Defining the "small enough" threshold ourselves and reporting a pass/fail.** Deliberately refused:
  launch-order rule 9.

---

## Convergence (recorded; ruled by the Admiral)

**Both candidates converged independently on the same hybrid, and the sampling advocate argued against
its own brief to get there** — candidate A, under a *sampled-revision* constraint, wrote: *"the honest
recommendation is: run the census for the series and keep the panel as the interpretation layer."*
Candidate B, under the opposing constraint, said *"census for the series."*

**Ruling: take B's census walker and A's panel-as-interpretation-layer whole. Do not average them.**

**Carried from A, absent from B:** (i) the reviewer **hand-recomputes ≥2 panel revisions with `git show`,
without running the instrument** — the only external check on a walker nobody can hand-audit at 184 rows;
(ii) **gross-add and gross-delete reported separately per interval, never net** — gate (a) asks whether
deletion keeps up with growth, so growth must be measured directly.

**Carried from B, absent from A:** the `(#NNN)` squash-merge join key for deletion attribution; the
regime break at `84fd28f`; the `SKILL_REFERENCE_BUNDLES` resolution path; the finding that #304's one
exactly-arithmetic deletion event landed **entirely on `templates/`** (hypothesis H1).

**Corrections made to the candidates themselves:**
- **A's stale-comment suspicion is wrong**, and wrong in the exact way both candidates warn about. It
  read `curate_corpus.py`'s *"max is docent at 143"* as stale against `admiral` at **17,214 bytes**.
  Verified at `c60f0ad`: `docent` is 143 **lines** (still max); `admiral` is 77 lines / 17,214 bytes.
  `SKILL_LINE_HARD_FLAG` is a **line** flag compared against a **byte** figure. **Bins-conflation in
  miniature, committed by the candidate that spends a page warning about bins-conflation.**
- **B's cost objection to full history is void** — `ls-tree -r --long` carries blob sizes, no checkout.
- **Both inherited an `n` that is not cleanly definable.** The baseline is not an ancestor of `main`
  (squash-merge), so n is **2 or 3** depending on a judgement call about #304's own merge. Neither is
  defensible without saying so; this run picks neither.

**The correction above became the run's strongest finding.** Because the rank order **fully reverses**
between units — `docent` 1st by lines / 5th by bytes, `admiral` 4th by lines / 1st by bytes — a threshold
is meaningless until a **unit** is fixed, and no unit has been chosen anywhere in the corpus.
`curate_corpus.py` already mixes three (words, lines, and this run's bytes) in one file with no stated
relationship. **Tommy is therefore handed the unit question alongside the threshold question**; asking
for one without the other is an unanswerable question.

## Cold plan critic — disposition (all 10 findings)

Panel: 1 critic, 4 BLOCKING + 6 MAJOR + 5 MINOR. **Every finding disposed; none rejected outright.**

| # | finding | disposition |
|---|---|---|
| B1 | outcome 3 unreachable by construction, yet dangled | **ACCEPTED** — break-proceeds declared foreclosed up front; the three-outcome frame resolves to a **two-way call** (no fourth label invented) |
| B2 | "building the decomposition IS the break" overstated, graded `settled` | **ACCEPTED** — claim withdrawn, regraded `guess/structural`; ablation arm declined for **runway**, cost estimate recorded, arm filed |
| B3 | verdict check passed by a fence-sitter | **ACCEPTED** — exactly-one `SELECTED-OUTCOME:` line (already independently self-falsified before the critique landed) |
| B4 | trend check passed by a second baseline that merely *cites* | **ACCEPTED** — replaced with a recompute-and-reconcile instrument check plus a blocking baseline reproduction |
| M1 | no rule distinguishing outcomes (1) and (2) | **ACCEPTED** — 5-row selection table pre-registered **before** any number |
| M2 | the trend may not be computable; n≈3, +0.17% | **ACCEPTED as the likely deliverable** — "is a trend computable at all" is now a required finding |
| M3 | two definitions sharing the label "always-loaded" | **ACCEPTED** — bare term **banned**; `NARROW-`/`WIDE-` required; disagreement forces outcome (1) |
| M4 | g2 varies the wrong variable | **ACCEPTED, and it corrects both this Commander and the Admiral** — gate (b) is **n = 0**, not weak-n |
| M5 | crew on the checkable gate, waived where the failure lives | **ACCEPTED** — one cold read added on the verdict |
| M6 | "§3 verbatim" undefined for this window | **ACCEPTED** — analogue is the deletion-event set, **which may be empty**, count asserted |
| m1 | POSIX relative-path checks on a PowerShell host | **ACCEPTED, urgent** — interpreter pinned, worktree-absolute paths |
| m3 | role growth vs deletion pressure conflated | **ACCEPTED** — roles entering/leaving reported separately; `skills/clean-codebase/` is parked WIP, not counted |
| m2, m4, m5 | fold/repurpose, "(a) decisive" nuance, null checks | **ACCEPTED** — g2 repurposed to spec the cheapest honest arm |

**Two of the four BLOCKING findings were checks that could not fail, sitting in this run's own gate
acceptance criteria.** One of them (`g1-integrate.c1`) was caught by this Commander independently, by
running its own check against a one-line decoy that contained only the keywords — the decoy passed.
