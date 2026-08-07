# ActiveGraph Comparison

Research date: 2026-07-30

## Short answer

ActiveGraph independently validates several of the strongest structural ideas in this exploration: typed objects and relations, a current graph separated from append-only history, bounded context views for agents, explicit frames, proposal/approval seams, and isolated possibility branches. The important difference is purpose.

ActiveGraph is an **execution substrate**: its graph is the current world state of a running agent system, behaviors react to changes, and the event log is canonical. The network being explored here is first a **navigation and understanding substrate**: its current map represents high-level reality so a human or agent can locate the right seam before spending context on underlying material. It need not be reactive, and its history need not universally reconstruct every current relationship.

ActiveGraph is therefore a useful reference architecture and a plausible future runtime plane, but not evidence that the near-term Markdown map should become an ActiveGraph installation.

## Conceptual mapping

| This exploration | ActiveGraph analogue | Alignment and difference |
|---|---|---|
| Current-only navigation map | Working graph projected from the event log | Strong alignment on a clean present-state surface. Our map is curated semantic orientation; ActiveGraph's graph is computed run state. |
| Separate history plane | Append-only event log and causal trace | Strong alignment on availability without ordinary graph inclusion. ActiveGraph history is operational causality and replay truth; our history may also contain human decisions and intellectual genealogy. |
| Separate possibility plane | Frames for short-lived parallel hypotheses; forks for durable branches; fork-test-promote | Strong mechanical analogue. Our possibilities may be informal ideas that never warrant executable branching. |
| High-level named connections | Typed relation objects with ids and optional data | Strong alignment. ActiveGraph additionally permits logic on a relation type, while our default connections are passive semantic routing. |
| Frames as overlapping semantic contexts | Frames as run-local behavior-dispatch contexts | Terminology collision. ActiveGraph frames isolate event dispatch inside one run; our frames classify and structure overlapping knowledge subnetworks. They should not be treated as the same primitive. |
| Context routing from a map | Per-behavior bounded graph views | Very strong alignment. ActiveGraph explicitly scopes views by center and depth because smaller views reduce LLM context and cost. Our map serves the earlier routing decision: which implementation or source context should be loaded at all. |
| Human/epistemic authority | Policies, proposed patches, approvals, promote gates | Architectural rhyme, but domain semantics remain ours. ActiveGraph supplies mechanisms; it does not define human belief, ratification, or current architectural truth. |
| Distilled current necessity | Domain-specific typed objects/relations | Possible to represent, but not a built-in ActiveGraph distinction. Its causal trace answers what produced an object, not automatically why an architectural element must exist now. |

## The strongest shared through-lines

1. **Graph as world state, not control flow.** ActiveGraph explicitly says facts and entities live on the graph while behaviors live alongside it. This matches the direction that an architecture map describes what exists rather than mixing current structure with procedure, history, or proposed change.

2. **Current surface separate from history.** ActiveGraph's graph is a deterministic projection of an append-only event log; the log itself is not on the graph. This is almost exactly the street-map distinction reached here, although ActiveGraph makes event sourcing universal for runtime soundness.

3. **Context must be deliberately scoped.** ActiveGraph views center on an object and bound relation depth, and the documentation names prompt size and cost as the reason. This strongly supports defining network quality by correct orientation per unit of context.

4. **Connections can be semantic seams.** ActiveGraph relations are identified typed edges. Most are passive; some can carry deterministic or LLM-backed behavior when coordination semantically belongs to the relationship. This resembles Constellation's progression from named architecture relationships toward seams that may eventually enforce policy.

5. **Possibilities should be isolated before promotion.** ActiveGraph frames and forks keep alternative work from silently mutating the parent; fork-test-promote adopts only a tested delta and records the promotion. That is a concrete execution analogue for a separate possibility layer with explicit promotion into current reality.

## Load-bearing differences

1. **Navigation versus execution.** Our near-term question is whether high-level Markdown maps let agents find seams before reading code. ActiveGraph begins after that representational question: it supplies the runtime in which behaviors observe and change shared state.

2. **Curated truth versus derived truth.** In ActiveGraph, current state is mechanically derived from every accepted event. Our architecture map is a curated statement of what is, verified against code. Requiring every edit, code change, or knowledge connection to originate as an event would be an additional system with substantial authoring and integration cost.

3. **History has different semantics.** ActiveGraph gives excellent causal lineage (`caused_by`, replay, trace). Architectural and intellectual history also needs reasons, rejected alternatives, and changing interpretations. An event log can carry those only when someone models them explicitly; causality is not the same as genealogy or explanation.

4. **Identity is run-local.** ActiveGraph-generated object and relation ids are unique within a run. A durable cross-project knowledge network needs identities that survive runs, tools, repositories, and possibly representations.

5. **Traversal is supporting machinery, not the primary product.** ActiveGraph has relation filters, a Cypher subset for subscriptions, and scoped views; its documentation explicitly says views are not a query language. Rich navigation across high-level knowledge is our central capability, not merely an input to reactive behavior.

6. **Reactivity is optional for us.** Logic-bearing edges are powerful when a relationship should coordinate runtime work. Most conceptual and architecture connections should remain passive. Making every connection active would confuse representation with execution.

## What to borrow now

- Keep current state, history, and possibility mechanically and conceptually distinct.
- Treat typed relations as the main unit of high-level meaning.
- Make context reads bounded and inspectable; later, measure which map nodes and edges an agent used to select code context.
- Preserve explicit proposal, approval, and promotion boundaries.
- Keep domain vocabularies local while maintaining a small shared kernel.

## What to watch for later

ActiveGraph becomes directly relevant if Constellation needs a persistent live world in which multiple agents coordinate through shared state, react to graph changes, resume after interruption, or test alternate runtime histories. At that point it should be evaluated as an execution plane beneath or beside the current-only knowledge map, not assumed to replace it.

## Tested / NOT tested

Tested through current official documentation, repository README/status, and the project's May 2026 paper. The comparison covers stated data model, event sourcing, behaviors, relations, frames, views, replay/fork/promotion, persistence shape, and current project scope.

NOT tested: ActiveGraph was not installed or executed; no quickstart, replay, fork, persistence, context-read tracing, FalkorDB backend, packs, coding-agent example, or performance behavior was runtime-verified. No claim is made that ActiveGraph could or could not satisfy the navigation use case after domain-specific implementation.

## Primary sources

- [ActiveGraph repository and current status](https://github.com/yoheinakajima/activegraph)
- [Graph concept](https://docs.activegraph.ai/concepts/graph/)
- [Events](https://docs.activegraph.ai/concepts/events/)
- [Behaviors](https://docs.activegraph.ai/concepts/behaviors/)
- [Relations](https://docs.activegraph.ai/concepts/relations/)
- [Views](https://docs.activegraph.ai/concepts/views/)
- [Frames](https://docs.activegraph.ai/concepts/frames/)
- [Forking](https://docs.activegraph.ai/concepts/forking/)
- [Fork, test, promote](https://docs.activegraph.ai/guides/fork-test-promote/)
- [The Log is the Agent](https://arxiv.org/abs/2605.21997)
