# Review: dependency edges, slicing, AFK/HITL typing — explore-ref-utilization ISSUE_SET.json

Reviewer stance: independent, did not author the cut. Read ISSUE_SET.json (12 issues, A-L) and
DESIGN_SPEC.md (confirmed spec) only. Repo not modified.

Reconstructed predecessor graph from `blocks` edges, then computed waves by max-predecessor-wave+1:
A,B,D,F (w1) -> C (w2) -> E (w3) -> G (w4) -> H (w5) -> I (w6) -> J (w7) -> K (w8) -> L (w9).
That matches the filer's claimed 9 waves.

## Findings

1. **MAJOR — edge H->I is invented, not a real data dependency.** I's own body (variance
   decomposition, residual split-half replication, channel comparison, composed-sector
   scorecard) never consumes H's join output — it consumes E's reference-lap/observables, G's
   fingerprint cells, and C's segment map/sectors. The actual missing direct input is G, which I
   only reaches today by riding behind H. Fix: drop H->I, add G->I. This moves I from wave 6 to
   wave 5, running in parallel with H instead of after it.

2. **MAJOR — applying finding 1 needs a new H->J edge, or J can start before the join exists.**
   J's acceptance criteria explicitly requires "every GATING check from issues C/D/E/H passes on
   the slice," i.e. J genuinely needs H done, but J's only current predecessor is I. Today H->I->J
   accidentally sequences H before J; that guarantee disappears the moment H->I is removed per
   finding 1. Fix: add H->J directly alongside dropping H->I, so H and I run in parallel in wave 5
   and both still gate J in wave 6.

3. **MAJOR — edge K->L needlessly serializes documentation behind the full season run.** L
   (retire the 5 old lineages, reconcile the architecture map) only needs the pipeline *code* to
   exist (B through I landed) — nothing in L's acceptance criteria touches K's numeric findings or
   the owner's allocation decisions. As cut, L waits at wave 9, trailing a potentially long,
   rate-limited season-scale run (K) for no stated reason. Fix: rewire L to depend on I (or J)
   instead of K, so cartography/documentation proceeds in parallel with the season run rather than
   after it.

4. **MINOR — edges A->H and C->H are redundant.** Both are already implied transitively
   (A->C->E->G->H), so removing them changes no issue's wave — they're pure graph noise. H's own
   body cites no direct input from A or C (only F's verdict, G's cells, and E's time-shares via
   G). Fix: drop them, or if kept intentionally as documentation of "this issue's *domain* touches
   A/C's outputs," say so — as written they read as accidental over-specification.

5. **MINOR — stale cross-reference in H's body.** H's "Out of scope" line says the join-vs-driver-
   overall diagnostic "is a DIAGNOSTIC sizing measurement in issue J," but J's own out-of-scope
   explicitly disclaims sizing ("this slice tests that the machine runs, not what it says"), and
   the actual held-out-weekend comparison is specified in K's body/deliverable. Fix: correct H's
   reference from "issue J" to "issue K."

6. **MINOR — J's pipeline-stage list silently omits the join.** J's "what to build" chain reads
   "tiling -> G -> utilization -> fingerprint-fit smoke -> panel dry-run" with no join step, yet
   J's acceptance criteria require H's gating checks to pass on the slice (see finding 2). Fix: add
   "the join" as an explicit stage between fingerprint-fit smoke and panel dry-run in J's body.

7. **MINOR — possible missing edge C->F (or E->F).** F's synthetic-recovery harness is drawn "to
   match the real 2023 driver×class support profile," but F has zero predecessors (wave 1) — it
   runs before segment classification (C) or utilization observables (E) exist. Either F's
   support-profile numbers come from data outside this pipeline (existing lap counts, published
   corner tallies) and zero predecessors is correct, or F actually needs C's/E's output and is
   missing an edge. As written this is ambiguous; worth a one-line clarification in F's body about
   where the "real profile" figure comes from.

8. **Typing: MAJOR — K is HITL, but only for the back end.** The stated `hitl_reason` covers
   interpreting the panel report and making allocation decisions *after* the season run finishes.
   Nothing requires a human checkpoint *before* kicking off the full 2023-season run itself — the
   exact class of "long run is expensive" work the repo's standing rule flags (real season-scale
   compute, FastF1/jolpica rate-limit stalls per CLAUDE.md's collector notes). Fix: split K's
   hitl_reason (or split the issue) so there's an explicit go/no-go checkpoint before the run
   starts, not only a decision gate after.

9. **Typing: MAJOR — L is AFK but bundles a judgment call with no test.** L asks the implementer
   to give each of the 5 old lineages a disposition of "wired-in, superseded-and-removed, or
   kept-with-a-stated-reason." Deciding that multi-hundred-line, previously-built code (#625
   rollup, #628 pipeline, the ephemeris pilot, apex_obs, segment_classifier.py) is safe to remove
   is exactly the kind of judgment call the review brief flags — not verifiable by any named test,
   and removal is hard to walk back once merged (people forget why old code vanished). L's own
   "out of scope" only protects code with a *live* consumer, which doesn't cover "safe to delete,
   just currently unwired." Fix: keep map-reconciliation/documentation AFK, but require explicit
   human sign-off before any actual deletion — or rescope L to "propose disposition" (AFK) with a
   separate HITL confirm-and-delete step.

10. **Wave shape: MAJOR — 9 waves is over-serialized, and it's the two "glue" issues (I and L)
    that cause it, not the physics-store build chain.** A through G (constants -> map -> grip ->
    reference/utilization -> fingerprint) is a genuinely sequential 4-wave chain — each stage
    consumes the prior stage's actual output, correctly ordered, nothing to parallelize there.
    Applying findings 1-3: I moves from wave 6 to wave 5 (parallel with H), and L moves from
    wave 9 to run alongside J/K instead of trailing the season run — collapsing the sort to
    roughly 7 waves without changing what any issue actually needs as input. Concretely: **I and L
    are the two issues that could safely move earlier.**

## Not flagged (checked, found sound)

- A->C, B->C, C->E, D->E, E->G, F->G, G->H, I->J, J->K are all real, load-bearing edges backed by
  explicit statements in the consuming issue's own body.
- J->K correctly encodes the spec's own S8 ruling (3-circuit tracer bullet before any season-scale
  run) — this is a deliberate, spec-mandated gate, not accidental sequencing.
- A and K's HITL typing is directionally correct (pre-registration commitment; owner allocation
  calls) — see finding 8 for the one gap in K's coverage.
- Slicing: B, C, E, G are each large but cohesive — every sub-part serves one interface/store with
  a genuinely coupled load boundary (e.g. B's labeled-persistence/positional-runtime split exists
  *because* of the "materializes exactly once" conversion, not by accident). Not worth splitting.
- Slicing (minor, not raised to full finding): I bundles 4 instruments that share inputs but
  mostly don't depend on each other (replication and channel-comparison are tightly coupled to
  each other; variance-decomposition and the sector scorecard are independent of both). Once
  finding 1 is applied and I sits in its own wave, there's a secondary opportunity to split I into
  2-3 parallel issues for faster wall-clock — worth considering but not blocking.
