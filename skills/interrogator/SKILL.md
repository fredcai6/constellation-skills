---
name: constellation-interrogator
description: Resolve request or design ambiguity by relentless one-question interrogation. Use when handed a goal and the questions to settle.
---

# Constellation Interrogator

Interview the user relentlessly until the handed-in goal is resolved. You are given a firm context — what you are settling — and a starting question list that may be charter-specific, commander-specific, or empty. Treat the list as a prompt, not a script: decide your own initial question set, and do not let an over-prescribed seed shortcut your framing. Walk the design tree, resolving dependencies one at a time. For each question, give a recommended answer.

Drive the question list as a `survey` from `templates/INTERROGATION.template.json` through the engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): ask one question at a time and wait for the answer; `append` follow-ups and new branches as answers open them; `skip` questions an earlier answer settled; then `consolidate` into the resolved understanding. If a question can be answered from the code, explore the code instead of asking.

## While interrogating

- Challenge terms that conflict with the glossary; propose a precise canonical term for vague or overloaded ones.
- Stress-test domain relationships with concrete edge-case scenarios.
- Cross-check claims against the code and surface contradictions.

Keep going until the goal is resolved or the user says enough, then consolidate the result for the invoker.

Template: `templates/INTERROGATION.template.json`. Reference: workbench `references/checklist-engine.md`.
