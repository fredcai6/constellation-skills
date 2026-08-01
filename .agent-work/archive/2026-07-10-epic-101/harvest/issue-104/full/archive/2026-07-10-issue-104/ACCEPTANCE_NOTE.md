# G5 — Two-sided acceptance (T5)

## Side 1 — own run (`py scripts/curate_corpus.py --root skills`, exit 0)
Full table pasted in the run log. 63 findings, 49 flagged, exit 0. Curator's own row
is clean (invoker=ok, exclusion=info, size=ok).

**Flag-category scoping (per plan, critic C3):** only the DUPLICATION-cluster rows are
acceptance-relevant. The ~15 `missing invoker tag` rows and the size/description-lint
rows on the OTHER skills are EXPECTED first-run noise that seeds the convention — NOT
defects, NOT fixed this run (retro-tagging is fenced).

**Duplication clusters flagged (mechanical):**
- 10-skill cluster "compliance engine drive rule inherited see references global" — the
  shared one-line POINTER to global-everyone.md.
- engine-invocation variants across charter/implementer/interrogator/lessons-auditor/
  reviewer/workbench.
- commander,commander-delegated — 33 shared shingles ("context understand plan execute
  reconcile triage review feedback ...").
- implementer,reviewer — 35 shared shingles ("instruction that was ambiguous missing or
  improvised around ...").
- smaller: admiral/lessons-auditor (6), admiral/commander-delegated (5), explorer/
  prototyper (2), lessons-auditor/reviewer (3), charter/scout (1), etc.

The detector is NOT near-quiet. Per the launch order this is necessary-not-sufficient
and, per the Honest-Null Clause, a FINDING to route — not a failure of the curator work.
The script is mechanical (T7): it clusters shared shingles; it does NOT judge
pointer-vs-doctrine. That judgment is side 2's / the human mend pass's job.

## Side 2 — independent fresh-context sweep (sonnet, given NEITHER the script NOR the fix list)
Prompt was only "survey skills/ for duplication clusters of doctrine text across SKILL.md,
command-derived." It built its own grep/awk pipeline and judged each cluster
pointer-vs-doctrine:
- **Real doctrine prose worth consolidating (2):**
  1. 5-skill engine-invocation restatement (charter, implementer, interrogator,
     lessons-auditor, reviewer) — re-states the absolute-path rule inline rather than
     pointing at its canonical statement in workbench/SKILL.md.
  2. implementer/reviewer "Workflow Feedback" paragraph — near-verbatim (one word
     differs); a candidate to hoist into a shared crew-tier doctrine file. (+ the shorter
     implementer/reviewer "proof-of-life" instruction, same two files.)
- **Judged intentional POINTERS / healthy (not defects):** the 10-skill compliance line;
  scoped-nulls & delegate-not-replacement "see references/..." lines; the
  commander/commander-delegated shared preamble (says "lives once" and points at
  commander-core.md — low risk).
- **Overall verdict:** corpus is MOSTLY single-sourced; two outlier prose-duplication
  clusters remain.

## Comparison (divergence = finding, not failure)
The two sides CONVERGE on the finding SET — the independent sweep, with no knowledge of
curate_corpus.py, found the same clusters the script flagged. The only differences are
SEMANTIC pointer-vs-doctrine judgments the script deliberately does NOT make (T7):
- commander/commander-delegated: script's single biggest cluster (33); the human-style
  sweep judges it a benign shared preamble/pointer. This is the DESIGNED division of
  labor (script shortlists, human judges), not a divergence-as-failure.
- The sweep promoted the 5-skill engine-invocation and implementer/reviewer clusters from
  "flagged shingles" to "real doctrine worth consolidating" — the mechanical detector bit;
  the fresh-context judgment confirmed which bites are actionable.

This is a clean T5 pass: detector and fresh-context sweep independently agree, and the
detector's mechanical/semantic honesty is exactly why the independent judgment adds value
rather than merely echoing the script.

## Routing
The two genuinely-actionable residual clusters are pre-existing corpus conditions (the
curator's first real run would surface them), NOT defects introduced by this issue. Routed
as triage candidates tc3 + tc4 (recommend-and-defer) — the epic routes them; this issue
ships the tooling that found them.
