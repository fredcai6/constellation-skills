---
name: constellation-interrogator
description: Question unresolved request/design ambiguity with a traceable queue. Use when Charter or Pilot needs deeper problem interrogation before decisions.
---

# Constellation Interrogator

Interrogate relentlessly, but narrowly: one highest-value unresolved decision question at a time. Prefer repo/docs inspection over asking. Stop when the blocking ambiguity is resolved or the user says enough.

If code/docs can answer, inspect them instead of asking.

First review the request and relevant code/docs. Create/update `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md`. Keep it light: question list, status, answer, follow-ups.

Before each question:

- pick highest-value remaining question
- skip if prior answers made it irrelevant
- ask with possible answers and recommendation
- after answer, update the question list with follow-ups

Keep going until user says enough or design is resolved.
