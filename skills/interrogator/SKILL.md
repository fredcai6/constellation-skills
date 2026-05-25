---
name: constellation-interrogator
description: Grill the user relentlessly about a request, plan, or design while keeping a traceable question queue. Use when Constellation needs problem interrogation, doctrine interrogation, or design stress-testing before decisions.
---

# Constellation Interrogator

Interview relentlessly until shared understanding. Walk each design branch, resolve dependencies one by one. Ask one question at a time. For each question, give possible answers and recommendation.

If code/docs can answer, inspect them instead of asking.

First review the request and relevant code/docs. Create/update `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md`. Keep it light: question list, status, answer, follow-ups.

Before each question:

- pick highest-value remaining question
- skip if prior answers made it irrelevant
- ask with possible answers and recommendation
- after answer, update the question list with follow-ups

Keep going until user says enough or design is resolved.
