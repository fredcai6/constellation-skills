VERDICT: PASS

Independent review of `ISSUE_SET.json` against the CONFIRMED `DESIGN_SPEC.md`. Read cold; I did not author the cut.

Round 1 raised two BLOCKING findings and five advisories. Round 2 re-read the changed portions of the rebuilt manifest (issues A, C, E, F, G bodies and every `blocks` array). Both blocking fixes are confirmed landed and correct, and all five advisories are discharged. Nothing new surfaced in the changed text.

## Findings

- **BLOCKING — issue A — RESOLVED (confirmed).** The gap was that the spec's stated done-condition ("not 'readings appear' but 'a trip fires from a per-agent reading on a live run'", written in per critic findings IF4 and S3) appeared nowhere in A's acceptance, so A could be marked done without a trip ever firing. The rebuilt A now carries it as acceptance assertion (5), quotes the spec's own contrast between the two conditions, and adds "this issue is not done until that is observed." That closes both the issue-level gap and the Intent's first done-clause ("the engine's trip mechanic acts on them"), which previously had no carrier. Correctly fixed.

- **BLOCKING — issue F (edge) — RESOLVED (confirmed).** The gap was a missing C→F edge: ruling 2's "net always-loaded delta across C and F together" lives only in F, so F held an acceptance criterion it could not perform if it ran before or beside C. The edge set is now A→F, B→C, B→F, C→F, and F's Depends-on line names C with exactly that rationale ("the joint number can only be measured with C's tranche landed"). I checked the new edge set for cycles: it topologically sorts to A and B, then C, then F, with D, E, and G unconstrained — no cycle. B→F is now transitively implied by B→C→F, but it is independently true (verbatim imperative pass-through of the fixed channel) and harmless to keep explicit. Correctly fixed.

- **ADVISORY — issue F — my T17 note, correctly handled as an open question rather than a fix.** Whether C's end-of-tranche tracer must re-run through the production MCP door is unanswered in the confirmed spec, and F now records that as an explicit open question with the instruction to surface it at build rather than decide it silently. That is the right disposition: inventing an answer would have been the invented scope I checked for in round 1, and an AFK agent escalating an unanswered design question upward is legitimate, not a reason to flip F to HITL.

- **ADVISORY — issue E — RESOLVED.** The closeout check now carries an explicit wave constraint: it is the epic's terminal act, running only after every other issue lands, even though E's tracker work may execute earlier. A wave planner reading only the (still empty) inbound edges now has the signal it lacked.

- **ADVISORY — issue G — RESOLVED, and the citation verifies.** The bare "FOUR times" claim is gone. G now states the spec's three recorded hits and cites the fourth to the spine journal at the confirm seam, evidence `e-confirm-2`. I checked the referent rather than taking the description: `.agent-work/archive/2026-08-03-explore-post-phase1/spine.json:369` holds `e-confirm-2` as a `refresh-request` at the confirm seam, and the same spine's blocker text at line 348 records the governor HARD trip that the refresh-request did not clear — which is the refresh-blindness shape being reported. The citation resolves and supports the claim.

- **ADVISORY — issues A, C, F — RESOLVED.** All three now carry a disposal line: delete the prototype worktree once the lift lands, with the commit SHA keeping the code recoverable. That discharges the route gate's obligation under the REJECT of critic finding S11 (worktrees "kept deliberately with a named disposition point") without losing the lift source.

- **ADVISORY — issue C — RESOLVED.** C now states its side of the spec's testing split: its tracer and token measurements are one-shot live evidence kept as runnable scripts, not CI-wired. All five build issues now record which side of that split they fall on.

- **ADVISORY — issue G — RESOLVED.** G now carries the closes-nothing constraint (closes belong to E under batched confirms), which is the principle that justifies G staying AFK while E is HITL, and a tracker-write clearance precondition to check before the wave that runs it.

## Type review (unchanged from round 1: no flips recommended)

Nothing in the round-2 changes alters the type analysis. G remains AFK because its mutations are purely additive and now explicitly barred from closing anything; F remains AFK because both probe branches are pre-decided by the spec and its one genuinely open question is routed to escalation rather than to silent judgment; C remains AFK because the census plus the second independent classification pass bound the judgment to zero new preferences. A's destructive sweep keeps its dry-run and recorded-before-state guards.

## Coverage and invented scope (unchanged from round 1)

Workstreams A–F map one-to-one onto issues A–F with every spec bullet traced into its issue, and all six route-gate triage candidates from Out of scope land in issue G. With A's done-condition restored, no element of the spec's chosen design is unowned. No invented scope in either round: the round-2 additions are all prescriptions from this review, and the one place the manifest could have overreached — settling the T17 question — was deliberately left open instead.
