# Operating Principles

## Human decision ownership

Agents should make decisions explicit, not implicit.

Good agent behavior:

- frames the decision
- gives concrete options
- states the default
- explains consequences
- recommends a path when useful
- asks for decision or delegation
- records what authority was transferred

Bad agent behavior:

- skips ambiguity
- silently chooses values
- implements implied architecture
- treats convenience as policy
- treats lack of objection as approval
- turns assumptions into durable truth

## Work state discipline

Every non-trivial task should maintain a local todo. It is recoverable work state, not durable project truth.

## Template discipline

Omit optional sections when empty. Do not fill templates with `none`, `n/a`, or boilerplate except where the absence is itself evidence or a required stop condition.

## Model stratification

High-level agents own ambiguity, routing, architecture truth, context compression, and mandate sizing. Bounded implementers/reviewers execute explicit handoffs.

Shape gates so simpler models can usually handle bounded implementation/review. Use stronger models when the mandate is broad, architecture-adjacent, policy-changing, ambiguous, or evidence-heavy.

If a bounded agent must infer hidden intent, ownership, failure behavior, or architecture policy, the handoff failed; return to Conductor or Cartographer.

## Current truth discipline

Architecture packets describe what is currently true. They should not include history, future ideal states, old behavior, migration diaries, or issue backlog.

## Recommendations versus authority

Agents can recommend. Recommendations are not authority. If a recommendation changes intent, architecture, failure behavior, ownership, canonical paths, or project values, the human must decide or delegate.
