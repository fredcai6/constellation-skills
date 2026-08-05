# Handoff: recursive self-improvement (skills first)

Seed for a new exploration (suggested work id: `explore-self-improvement`). Descendant of `explore-memory-graph`, closed by split on 2026-08-05. The full record is `IDEAS_BOARD.md` beside this file's parent directory; excursion x2 (two-speed memory, Zhang consolidation evidence) and the Soar discussion are its main evidence base. Nothing here is a confirmed spec — verdicts below were settled by the human during the parent exploration; open threads are genuinely open.

## The point

Improve how agents work — their skills, instructions, and tools — as a recursive loop. This sits right next to memory (the mind map) but is a fundamentally different question: **skills and instructions are procedural memory**, and this exploration is about improving them first, with Soar's chunking as the leading mechanism. The constellation already has feedback machinery (the lessons/feedback loop); this exploration extends it, it does not reinvent it.

## What this exploration owns (settled in the parent)

- **The taxonomy symmetry.** Feedback = procedural memory (skills/instructions); the graph = declarative memory; artifacts/journal/traces = episodic record. The two recursion channels off one observation stream — feedback ("our instructions/setup need improvement") and memory ("our structural knowledge needs updating") — are the two memory types. Strong feedback capture does NOT mean knowledge capture is covered; but this exploration's remit is the feedback half.
- **Soar's chunking lands here.** Chunks are procedural (if-conditions-then-do); so are skills. **Impasse-resolved is the promotion trigger** for skill/instruction lessons: a stuck-then-unstuck pair is the signal. The lesson's applicability conditions are **read off the trace of what the resolution consulted** — dependency capture, not after-the-fact summary — the direct countermeasure to over-general lessons (Soar's overgeneral-chunk problem; Zhang's interference failure). The curator gate stays.
- **Postmortem intake is firmly this exploration's realm, feedback-only for now.** The three-questions split from the parent survives ("how did it go" → feedback; "what did you do" → the code map, which is now algorithmically derived and needs no postmortem; "what did you learn" → journal/mind map), but near-term machinery is built only for the feedback channel.
- **Multi-level observation.** Admiral observes at epic level, Commander at issue level, Crew at task level; each runs its own end-of-workflow postmortem. Severity is judged across levels: something that confused the Crew but the Commander worked around is an instructions problem, not an architecture problem. Marking happens as end-of-task observations at every tier, never as a survey of raw history afterwards.
- **Promotion is gated, additive, episode-preserving** (x2, empirical): unconditional rewriting consolidation degrades performance; promote only what beats what it displaces, keep the raw material, supersede don't delete.

## Shared substrate (inherited by all three descendants)

Markdown/text files in git are the truth; any database is a disposable derived index — files win every disagreement. Statement layers are JSON-lines; prose layers are markdown. Addresses are opaque identity; selection happens on properties. Statements follow the Wikidata shape (qualifiers + references) with a small owned vocabulary. Storage is atomic; views are rendered. The store holds the current view; git holds history; retained history is rationale only. Evidence classes set durability and supersession; the source artifact's class sets update strength. (For this exploration the "statements" are mostly lessons and their conditions; the substrate still applies — a lesson is a statement with provenance and an evidence class.)

## Open threads this exploration takes

1. **What counts as an impasse in our harness.** Soar's impasse is an architectural event; our equivalent needs defining — a retry loop, an escalation, a human unblock, a rework cycle? Detection from traces vs self-report.
2. **The lesson-condition format.** How dependency-traced applicability conditions are written into a skill/instruction lesson so it fires only where it applies.
3. **Adoption by the existing lessons loop.** How the repo's current feedback machinery (feedback inbox, debt-not-trust, delete-not-mark) takes on the impasse trigger and the condition format without a rebuild.
4. **The observation ledger.** Short-term memory's shell — format, lifetime, ceremony level ("keep our thoughts right, right now"; it could just be a ledger of current observations) — parked here because postmortems consume it.
5. **Cross-level triage rule.** The concrete rule for judging severity across Crew/Commander/Admiral observations.
6. **The curator gate for lessons.** Who approves a promoted lesson, and what evidence a promotion must carry (beats-what-it-displaces, per x2).

## Inputs and maintainer

Inputs: postmortems at every tier, traces, incidents, rework/escalation events. Maintainer: the existing lessons/feedback loop, extended; curator-gated promotion; humans rule on contested lessons.

## Interlinks (expected to grow)

- **Mind map:** the declarative counterpart. The same postmortem stream feeds both eventually; near-term only the feedback channel gets machinery. "What did you learn" routes to the journal/mind map, not here.
- **Code map:** none near-term (it derives algorithmically). Later: lessons about *how the map gets used* may come from its traversal traces.
