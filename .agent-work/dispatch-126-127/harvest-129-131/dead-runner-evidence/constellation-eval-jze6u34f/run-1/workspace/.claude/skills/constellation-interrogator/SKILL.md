---
name: constellation-interrogator
description: Resolve request or design ambiguity by relentless one-question interrogation. Use when handed a goal and the questions to settle.
---

# Constellation Interrogator

Resolve the handed-in goal to common understanding through relentless, one-question-at-a-time interrogation. Whoever handed you the goal is your **counterpart** — most often a dispatching delegate (a Commander running under an Admiral launch order, or any delegated dispatch), sometimes a human at the keyboard. Walk the design tree, resolving dependencies one at a time; for each question give a recommended answer. If you're given a list of questions, treat it as a prompt, not a script: decide your own initial question set, and don't let an over-prescribed seed shortcut your framing.

Frame an ambiguous ask in behavior terms first. Start from the capability, then drill: **what capability is being added or changed** (the present-tense thing the system will do); **concrete examples/use cases** of that capability in action, including the edge cases; **events that matter** architecturally (boundary-crossing or contract signals, not every runtime event); and the **governing rules/constraints/assumptions**. Resolve which capability is in play before debating mechanism. Map this framing to the existing `capability`/`event`/`constraint`/`assumption` ontology so the resolved understanding hands cleanly to the Cartographer.

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
