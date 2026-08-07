# scripts.verify_interrogation
scripts/verify_interrogation.py, 196 lines, 3 holes

Refuse a self-answered or unsigned interrogation — the interrogator RAIL.

This is the mechanically-enforced rail for the `constellation-interrogator`
sharpening (DESIGN_SPEC Section D1). The interrogator drives a survey to a joint
understanding; this script is the gate the interrogation RECORD must clear before
that understanding may be called consolidated. It enforces the two locked
behaviors in code, so neither can rest on the agent's self-assertion:

  * FACTS-VS-DECISIONS SPLIT. Every question is typed `fact` or `decision`. A
    `fact` is a question the agent may resolve by exploring the codebase; a
    `decision` is a genuine choice that must block on the human/counterpart.
      - A `decision` marked `resolved` MUST carry a non-empty `human_answer` —
        a decision is NEVER self-answered by the agent (the DECISION-BLOCK).
      - A `fact` marked `resolved` MUST carry non-empty `code_evidence` — a
        resolved fact is grounded in code/docs, not asserted (the split's other
        edge). A resolved fact needs NO human answer; that is what "allowed" means.

  * NO-QUIT-EARLY FINISH GATE. A record marked `consolidated: true` MUST carry a
    joint-understanding `signoff` — a real human exchange with a non-empty `by`
    AND `statement` — AND no question may still be `open`. Loop termination is not
    the gate; the explicit sign-off that questioning is complete is. Absent it,
    consolidation is REFUSED.

A defended exception to the finish gate (e.g. an async counterpart) requires a
`rail_exception` carrying a non-empty `reviewer_cosign` (the INDEPENDENT reviewer,
never the author) AND a non-empty `log` entry — self-assertion never passes. The
exception covers the finish gate ONLY; it never excuses a self-answered decision.

Everything else — whether the questioning actually dug deep, whether the recorded
understanding is right — is the INDEPENDENT reviewer's judgment (DESIGN_SPEC TF8),
deliberately NOT gated here. Standard library only.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, sys
imported by: none found

```python
VALID_MODES = ('delegated', 'interactive')
VALID_KINDS = ('fact', 'decision')
VALID_STATUSES = ('resolved', 'open', 'skipped')
```

- [InterrogationError](InterrogationError.md) class: Raised when an interrogation record fails the rail — the refusal.
- [_require](_require.md) function: HOLE: no docstring
- [_nonempty](_nonempty.md) function: HOLE: no docstring
- [verify_structure](verify_structure.md) function: The record's basic shape: a goal, a mode, and a non-empty typed question
- [verify_split](verify_split.md) function: The facts-vs-decisions split, enforced per resolved question.
- [_exception_cosigned](_exception_cosigned.md) function: True only when an INDEPENDENT reviewer co-signed the finish-gate exception
- [verify_finish_gate](verify_finish_gate.md) function: The no-quit-early finish gate: a consolidated record needs the joint-
- [verify_interrogation](verify_interrogation.md) function: Raise InterrogationError on any failed rule; return None if the record
- [main](main.md) function: HOLE: no docstring
