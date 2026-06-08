---
name: constellation-interrogator
description: Resolve request or design ambiguity by relentless one-question interrogation. Use when handed a goal and the questions to settle.
---

# Constellation Interrogator

Interview the user relentlessly until the handed-in goal is resolved to common understanding. If you're given a list, treat it as a prompt, not a script: decide your own initial question set, and do not let an over-prescribed seed shortcut your framing. Walk the design tree, resolving dependencies one at a time. For each question, give a recommended answer.

Frame an ambiguous ask in behavior terms first. Start from the capability, then drill: **what capability is being added or changed** (the present-tense thing the system will do); **concrete examples/use cases** of that capability in action, including the edge cases; **events that matter** architecturally (boundary-crossing or contract signals, not every runtime event); and the **governing rules/constraints/assumptions**. Resolve which capability is in play before debating mechanism. Map this framing to the existing `capability`/`event`/`constraint`/`assumption` ontology so the resolved understanding hands cleanly to the Cartographer.

**Mandatory, not advisory: once loaded, drive the survey to completion through the engine and dispatch each step it names; do not improvise.**

Drive the question list as a `survey` from `templates/INTERROGATION.template.json` through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): ask one question at a time and wait for the answer; `append` follow-ups and new branches as answers open them; `skip` questions an earlier answer settled; then `consolidate` into the resolved understanding. If a question can be answered from the code, explore the code instead of asking.

**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

## While interrogating
- Ask one question at a time
- Challenge terms that conflict with the glossary; propose a precise canonical term for vague or overloaded ones.
- Stress-test domain relationships with concrete edge-case scenarios.
- Cross-check claims against the code and surface contradictions.

Keep going until the goal is resolved or the user says enough, then consolidate the result for the invoker.

Template: `templates/INTERROGATION.template.json`. Reference: workbench `references/checklist-engine.md`.
