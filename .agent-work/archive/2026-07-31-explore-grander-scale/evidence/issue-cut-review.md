# Independent review — Grander Scale cut 1 (B1+B3) issue set

Reviewer: fresh-context, not the author of this cut.
Inputs: `DESIGN_SPEC.md` (CONFIRMED, Tommy, 2026-07-31) and `issue-set.json` (12 issues, A–L; 4 HITL, 8 AFK).
Date: 2026-07-31

## Verdict

**GO-WITH-EDITS.**

The cut is faithful. Both named deliverables are covered, all eight Testing-pathway exercises map to issues, the conditional-B2 gates are correctly staged behind the B3 evidence rather than assumed, B4 and the idea-substrate are correctly absent, and Stratum A is correctly not cut. The spec's two mechanical obligations on the cut — a design-it-twice checklist item in each load-bearing-interface issue, and a per-element Stratum-A foreclosure check — both pass (see Notable calls). No issue commits work the spec does not direct.

Six edits are needed before an Admiral runs it. One of them (G's acceptance criterion) is a genuine circular dependency that will stall the issue; the rest are ownership and ordering gaps.

## Coverage gaps

**1. No issue owns the projection generation machinery that B, F, and H all presuppose. (spec B2, "Ahead-of-time generation" and "Per-run assembly")**
B2's projection substrate is *not* the conditional part — only the kernel-plus-fragments break is conditional. The spec directs "a versioned script builds the projection, so every doctrine change produces a reviewable diff," and per-run deterministic recipes keyed by the active spine node. Issue **B** builds the manifest (a byproduct of assembly), **F** speaks of the contract being "projected into Commander context/plan," and **H** regenerates "each committed projection from current canon" and diffs it. All three presume a generator exists; none builds it and none declares it pre-existing. If the spine's gate-note loading already is this mechanism (Assumption 5 calls it "partially grounded"), the cut should say so explicitly in B or H so H's acceptance has a defined subject. If it does not exist, this is an unowned deliverable sitting under three issues.

**2. The B3 success verdict has no owning issue. (spec B3 "Success criterion (human-owned)"; Testing pathways: map-first)**
Issue **I** correctly compiles paired evidence and correctly refuses to self-adjudicate. But the spec makes the verdict itself a deliverable with consequences: "Tommy adjudicates the verdict... Falsification triggers rework of the element — revisit the contract, the map content, or the measurement." Nothing in the set owns that adjudication or the rework branch. **L** is HITL but is scoped to the B2 break decision, not the B3 verdict. Either retype I as HITL (its terminal act is a human call) or add a short HITL adjudication issue between I and L.

**3. The tripwired-deletion pathway is only half-exercised. (spec Testing pathways: tripwired deletion; B1 "Pre-learning makes deletion safe")**
The pathway requires three things: real simplifications with filed predictive lessons, *running the affected workflows* afterward, and the git-derived corpus-size / per-role-surface trend as the standing aggregate measure. Issue **F** delivers the first (deletions with tripwire lessons) and stops there — its acceptance is "deletions filed with tripwire lessons," with no run of the affected workflows and no check that a tripwire surfaces and connects back. The git trend appears only inside **L**, framed as B2 gate (a) rather than as B1's standing measure, and L sits at the very end of the dependency chain. Since the spec stages the whole cut as "B3 and tripwired deletion run first," having the deletion pathway's evidence arrive only at L inverts that. Suggest either extending F's acceptance to cover the post-deletion workflow runs, or adding a small AFK issue that computes the trend early and repeats it (it "costs nothing to compute," per the spec).

**4. Minor — projection determinism's second half is implicit.** The pathway is "rebuild from a clean checkout in a second environment... *and* by making one doctrine change and confirming the projection diff is reviewable and complete." **H** covers the clean-checkout rebuild and the exclusion set explicitly; the "one doctrine change → reviewable, complete diff" half is only implied by H's induced-drift test. Inducing drift and confirming a diff is reviewable are not quite the same check. One added acceptance line in H closes it.

Everything else in cut scope maps cleanly:

| Spec commitment | Issue |
|---|---|
| B1 episode record + durable store + retirement + assertion non-foreclosure | C |
| B1 mechanical capture, negative control, cross-run retrieval | G |
| B1 consolidation on a collated cluster (Intent's "done" requirement) | J |
| B1 Curator coherence sweep, seeded defects, proposals-not-mutations | K |
| B3 map-input contract + canonical entrypoint + degraded mode | F |
| B3 observability: manifest | B |
| B3 observability: transcript ordering, paired evidence, baselines | A, I |
| B3/B2 drift check (catastrophic-class, mechanism-owned day one) | H |
| B0 two-bin routing | J |
| B0 invariant inventory (named early task, Tommy owner, Assumption 6) | D |
| Confirm-gate refusal exercise | E |
| Conditional B2 gates (a) trend + (b) role-competence test | L |
| Design-it-twice on the two load-bearing interfaces | B, C |

## Invented scope

**None found.** I checked every issue against the spec and every issue traces to directed work. Two placements are worth naming but are not invention:

- **H** absorbs the B2 projection-determinism pathway (clean-checkout rebuild, exclusion set) into the drift-check issue. Both operate on projections, so the bundling is sensible; the work is spec-directed either way.
- **L** correctly refuses to build the break: "If the break proceeds... the break gets its own cut." It also correctly carries forward the human-readable whole-role projection as a requirement *of that later cut*, not of this one. That is exactly right per B2 and the IF06 disposition.

No issue touches B4, the idea-substrate, federation, a graph backend, a query language, ontology expansion, or assertion-strength mechanics.

## Edge problems

**E1 — G's acceptance criterion is circular against its own outgoing edge. (blocking-quality)**
**G** is `blocks: [J]`, so G must complete before J. But G's body sets as acceptance: "Cross-run retrieval exercised: seed episodes across runs, confirm rhyme-search finds them *after a consolidation*." The consolidation is issue **J**. As written G cannot satisfy its acceptance until J has run, and J cannot start until G is done. The spec's episode-capture pathway does bundle a consolidation into this exercise ("seed episodes across several runs, consolidate one cluster, and confirm the store still finds rhymes involving consolidated episodes' neighbors"), so the requirement is real — but it needs to be either (a) satisfied inside G with a throwaway/synthetic consolidation over seeded episodes, stated explicitly, or (b) moved to J, whose acceptance already touches the retirement marking. Option (a) is better: it keeps G's negative-control and retrieval evidence together and keeps J free to be the real first consolidation.

**E2 — Missing edge: D should block J.**
**D** (invariant inventory, Tommy-owned) currently blocks nothing. **J** routes a cluster through the two-bin rule. The spec makes D the check on Assumption 6 and states that "discovering a third bin would be a design change requiring rework of B0.3." If D finds a non-mechanizable catastrophic invariant, the routing rule J applies changes underneath it. Running J's first-ever two-bin ruling before the inventory that could invalidate the rule is the wrong order, and D is cheap and explicitly a *named early* task. Add `D blocks J`.

**E3 — Soft: H blocks I is defensible but under-argued.**
The drift check is not strictly a prerequisite for running measurement tasks. The real argument for the edge — that a drifted projection makes the manifest lie about what was delivered, corrupting I's evidence — is sound but nowhere stated. Keep the edge; consider a clause in I so a Commander does not read it as arbitrary sequencing and try to shortcut it.

All other edges check out as real orderings: A→I (baselines are the comparison arm), B→G (manifest is the episode's context field), B→H and F→H (drift check needs projections and the contract), C→G (record shape before capture wiring), C→K (findings land in the store as predictive episodes), F→I (measure against the new contract), G→J (consolidation needs an accumulated store), I→L and J→L (the B2 gates need B3 evidence and demonstrated deletion pressure). E, K, L correctly terminate.

## Type problems

**T-a — I is typed AFK but terminates in a human verdict.** Covered under Coverage gap 2. The AFK agent's own work (run tasks, extract ordering, compile the package) is genuinely AFK, so this is not a *risky* AFK in the safety sense — the issue explicitly forbids self-adjudication, which is the right guardrail. It is a completeness problem: nothing is typed to receive the verdict. Retype I as HITL or insert an adjudication issue.

**T-b — F is the borderline AFK worth a human's eyes, and the spec technically permits it.** F changes Commander's map-input contract *and deletes existing doctrine prose*. Under B0.4 a human-facing contract change earns "the full cold panel," which is agentic review — so AFK-with-cold-panel is spec-compliant, and F's body correctly invokes it. I am not calling this a type error. I am surfacing it: F is the single highest-consequence content change in the cut, the whole tracer's validity rests on the contract text and on which prose was judged superseded, and the spec puts human eyes on a sliding scale rather than a gate. Recommend Tommy reads the contract text and the deletion list even though nothing forces it.

**T-c — Review depth is stated in F only.** B, C, G, H all build or change mechanisms, which B0.4 also routes to the full cold panel. Only F says so. Either state the review class per issue or state it once in the epic body so a delegated Commander does not default to a light pass on a mechanism change.

The four HITL types are all correctly assigned and each carries a sound `hitl_reason`: A (corpus choice is Tommy's, spec-named as the first implementing decision), D (bin adjudication, spec names Tommy as owner), J (first two-bin ruling plus a landed doctrine change), L (architectural break decision). None of the eight AFK issues requires an intent, architecture, or adjudication decision mid-flight — B and C in particular are correctly AFK because Tommy explicitly delegated the concrete interface shapes as "implementation details to try something on."

## Notable calls worth surfacing to the human

**The two mechanical obligations the spec placed on this cut both pass.**
- *Design-it-twice transfer* (spec "Load-bearing interfaces", disposition T18): the checklist item is present and specific in both **B** and **C** — "3+ parallel interface designs under distinct constraints, compared on depth/locality/seam/testability, before fixing the schema." Correctly absent from every other issue; the traversal-recipe surface is correctly not treated as load-bearing, matching the S19 disposition.
- *Per-element Stratum-A foreclosure check* (disposition T22): I ran it. **C** is the only element that could foreclose Stratum A, and it carries the requirement verbatim — "records must remain expressible as assertions under the Stratum A truth model (non-foreclosure)" — which is exactly the IF05 fix landing in the issue rather than staying in the spec. **B**'s manifest is scoped generically ("anything deterministically assembled into agent context") rather than being hard-bound to the spine, which preserves the IF04 scoping. No other element in the cut creates a durable store or a load path that a future non-spine frame or the assertion model would have to be built alongside.

**Hazard in K: seeded defects have no stated cleanup.** **K** seeds "known incoherences into a bounded corpus slice" and dispatches adversarial subagents. The body never says the slice is a copy, nor that the seeding is reverted. Deliberately introducing incoherence into the live doctrine corpus without a stated revert is how a test artifact becomes canon. Add an explicit "operate on a copied slice, or revert the seeding as an acceptance condition" line. Low cost, real risk.

**The staging inversion Tommy should be aware of.** The spec is emphatic that "B3 and tripwired deletion run **first**" and that the B2 break is earned by their evidence. The issue set honors this for B3 (F and I are early-to-middle) but the deletion pressure's aggregate measure lands only in L, at the end of the chain, and only one issue (F) actually deletes anything. If the intent is that gate (a) — "deletion alone is not getting the always-loaded role surface small enough" — be a real measurement rather than a formality, this cut produces roughly one deletion event before the gate is evaluated. That may be exactly what Tommy wants for cut 1 (the spec does say evidence accumulates over repeated instances and one instance cannot falsify an aggregate). But it means L will likely be decided on thin trend data, and it is worth deciding now whether L belongs in cut 1 at all or in a follow-on cut after more deletions have accumulated.

**Epic body carries the full spec verbatim.** Good call — the issue set stays readable after the working directory is gone.
