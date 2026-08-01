# x1 designer A — constraint: minimal-interface (response-text only)

Read `.agent-work/explore-138/crew-handoffs/x1-shared-core.md` FIRST — it holds the question, ground
truth, hard constraints, and deliverable shape. This file only assigns your constraint and result path.

## Your named constraint

**Minimal-interface / response-text only.** The engine's existing stdout responses are your ONLY
channel: no hooks, no new verbs, no schema change, no conductor. The smallest diff to
`checklist_engine.py` output strings that carries the doctrine at each decision point — next-step
imperative + one-line why + distance-to-terminal on `advance`/`current`; the scoped-null/ask-up
interceptor line on check-FAILURE; the release-ordering reminder near terminal. Plain text a cheap
model reads because it arrives exactly when it's deciding.

Push austerity hard: every line must earn its place; say what you refused to add and why the refusal
is safe. Where response text alone CANNOT reach the agent (post-compaction, turn-end), say so honestly
in the failure-shade table — do not stretch the channel to fake coverage.

## Result path (write the design doc here)

`C:/Programs/constellation-skills/.agent-work/explore-138/evidence/x1-designer-a.md`
