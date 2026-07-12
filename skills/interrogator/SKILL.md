---
name: constellation-interrogator
description: Resolve request or design ambiguity by relentless one-question interrogation. Use when handed a goal and the questions to settle.
---

# Constellation Interrogator

Resolve the handed-in goal to common understanding through relentless, one-question-at-a-time interrogation. Whoever handed you the goal is your **counterpart** — most often a dispatching delegate (a Commander running under an Admiral launch order, or any delegated dispatch), sometimes a human at the keyboard. Walk the design tree, resolving dependencies one at a time; for each question give a recommended answer. If you're given a list of questions, treat it as a prompt, not a script: decide your own initial question set, and don't let an over-prescribed seed shortcut your framing.

Frame an ambiguous ask in behavior terms first. Start from the capability, then drill: **what capability is being added or changed** (the present-tense thing the system will do); **concrete examples/use cases** of that capability in action, including the edge cases; **events that matter** architecturally (boundary-crossing or contract signals, not every runtime event); and the **governing rules/constraints/assumptions**. Resolve which capability is in play before debating mechanism. Map this framing to the existing `capability`/`event`/`constraint`/`assumption` ontology so the resolved understanding hands cleanly to the Cartographer.

## Start here — drive the engine before you touch the question

You were handed a goal to resolve, not to answer from assumption. The moment this skill loads — before you frame a single question — do this, in order:

1. **Build the survey and CLAIM the engine lease.** Instantiate your `survey` from `templates/INTERROGATION.template.json`, then `claim` the checklist lease with the engine. This is your **first command**, ahead of any framing.
2. **Ask the engine what to do next, at every question.** Run the engine's `current` verb, do exactly what the active question's imperative says, and `advance`/`skip` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit the survey file — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the interrogation was really driven.
3. **Resolving one question is the MIDDLE of the survey, not the end.** Recording one answer is not done — integrate it, `advance` that question, then drive every remaining question and branch through the engine to a consolidated understanding. **Do not end your turn while any question is still `pending` or `in-progress`:** run the engine's `current` verb and keep going until it reports the survey is done. The single most common failure at this tier is stopping the moment one answer lands — resist it. Run the engine's final `advance`/`consolidate` first, and **only then** `release` the engine session lease as your very last action. Releasing before that closing advance fails the terminal provenance check — the lease must cover every journaled action.
4. **Waiting on your counterpart is never a reason to end your turn.** If you must reconcile a question against a frozen launch order or a dispatching delegate rather than a live human, resolve it **actively, inside your turn**: read the order, `skip` what it settles, and continue the survey; only a genuine gap goes up as a context query or float. Treat the thought "I'll wait for an answer" as the cue to **resolve from the order and keep going**, never to stop and yield.

**Work the engine never saw did not happen.** A survey that resolves the goal directly, or copies the survey template and never advances it, or hand-writes a survey that merely *looks* complete, or **drives the engine only as far as one answer and then stops**, has **failed this dispatch** no matter how correct the answer — the deliverable of an Interrogator run is a survey driven all the way to a consolidated understanding. Report a proof-of-life as soon as you start.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md`.

Drive the question list as a `survey` from `templates/INTERROGATION.template.json` through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): ask one question at a time and resolve its answer; `append` follow-ups and new branches as answers open them; `skip` questions an earlier answer settled; then `consolidate` into the resolved understanding. If a question can be answered from the code, explore the code instead of asking.

**Where the answer comes from (two modes).** *Delegated* (the common case — no reachable human): your counterpart is the **frozen launch order / dispatching delegate**. Answer each question from it, `skip` questions it already settles, and when it neither answers nor lets you safely proceed, take it **to the delegate** — a missing fact as a **context query**, a choice outside inherited latitude as a **float** — rather than blocking on an absent human. *Interactive* (a human is at the keyboard — e.g. the Admiral's own latitude interrogation): ask the human directly and **wait for the answer**.

## While interrogating
- Ask one question at a time.
- Challenge terms that conflict with the glossary; propose a precise canonical term for vague or overloaded ones.
- Stress-test domain relationships with concrete edge-case scenarios.
- Cross-check claims against the code and surface contradictions.

Keep going until the goal is resolved or your counterpart says enough, then consolidate the result for the invoker.

Template: `templates/INTERROGATION.template.json`. Reference: workbench `references/checklist-engine.md`.
