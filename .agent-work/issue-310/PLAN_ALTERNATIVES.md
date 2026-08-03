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
