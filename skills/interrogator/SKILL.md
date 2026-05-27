---
name: constellation-interrogator
description: Grill user on unresolved request/design ambiguity with a traceable queue.
---

# Constellation Interrogator

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

A shared understanding means: problem statement fully written, use cases defined and clarified, technical basis solidified, size of change scoped, implementation detailed.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Question Process

1 - Review topic and relevant code/docs. Refer to `docs/agents/GLOSSARY.md` to understand established code base language. Refer to `docs/agents/architecture/index.md` to guide architecture crawl
2 - Create/update `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md`. If given a template, start there. It must include: question list, status, answer, follow-ups.
3 - Enter question loop:
3a - Pick highest value remaining question
3b - Update question in context of previous answers. Skip question if no long relevant 
3c - Ask with possible answers and a recommendation
3d - Accomodate a short conversation with user for clarifications
3e - Update GLOSSARY.md as needed
3f - Update question list with response and spawn follow ups or new branches
4 - When question list is complete, consider if design is truly resolved. If not, spawn new questions and return to step 3
5 - When you think you are truly finished, ask the user if there are any unresolved or problem points. If so, address those questions. Spawn a new branch of questions and return to step 3 if relevant. 

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `GLOSSARY.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update GLOSSARY.md inline

When a term is resolved, update `GLOSSARY.md` right there. Don't batch these up — capture them as they happen. 

`GLOSSARY.md` should be totally devoid of implementation details. Do not treat `GLOSSARY.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

Keep going until user says enough or design is resolved.
