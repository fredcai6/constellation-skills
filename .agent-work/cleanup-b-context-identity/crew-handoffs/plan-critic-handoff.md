# Cold plan critic — cleanup-b-context-identity

You are a **cold critic**. You have no authoring context and you are not getting
any: do not ask for the exploration record, and do not assume the author had a
good reason for anything. Nothing is sacred; deliberate decisions are attackable.

## What to read, and nothing else

Read exactly these four, in the worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`:

1. `.agent-work/cleanup-b-context-identity/MISSION_FRAME.md`
2. `.agent-work/cleanup-b-context-identity/PLAN_ALTERNATIVES.md`
3. `.agent-work/cleanup-b-context-identity/execute.json`
4. `.agent-work/cleanup-b-context-identity/measurement/probe_cross_key.out`

You **may** read source files to check a specific claim (`scripts/gauge_reader.py`,
`scripts/hooks/gauge_writer_hook.py`, `scripts/checklist_engine.py`,
`scripts/hooks/spine_rail.py`, `tests/`). You may not edit anything.

## The three lenses — cover all three

- **Intent-fit** — does this plan serve the stated point ("a context reading
  belongs to an agent, not a folder")? Where does it serve the *measurement*
  instead of the *problem*?
- **Testability** — can each claim be exercised and falsified? Attack the
  postconditions in `execute.json` specifically: is any of them a check that
  **cannot fail** — vacuous on an empty set, asking a question whose answer is the
  same in the healthy and the broken world, or enumerating only one side of a
  comparison? Name each one you find.
- **Simplicity / YAGNI** — what can be deleted? Is the recommended candidate B
  bigger than the problem measured?

## Questions worth attacking specifically

- `decision:no-shared-file-fallback` removes the read of a shared `gauge.json`. Is
  there a real deployment where that silences a governor that is working today,
  and is the "one tool call" window claim actually true?
- The plan asserts the change can only make the governor **permit** where it
  currently refuses, never the reverse. Is that true on every path? Find a
  counterexample or say you looked and found none.
- `g0-measure`'s `c1` greps the probe output for `CANDIDATE 2 CONFIRMED`. Is that
  a check that can fail? What would it do if the probe silently wrote nothing?
- Is one combined `g1` (writer + reader + engine together) right, or is the
  no-red-window argument covering for a gate that is too big to review?
- Does anything in the plan touch a file the launch order fences
  (`scripts/hooks/spine_rail.py`, `scripts/run_crew.py`,
  `scripts/mcp_spine_server.py`, `.mcp.json`)?

## Stop conditions

Stop and report if the plan is incoherent enough that critique is guesswork, or if
you need context these four documents do not contain. Do not invent the missing
context.

## Return format

Write your findings to
`.agent-work/cleanup-b-context-identity/crew-handoffs/plan-critic-result.md`
**before you end your turn** — that write is the delivery. Structure:

```
# Cold plan critic result

## Verdict
<one line: PROCEED / PROCEED-WITH-CHANGES / REWORK>

## Findings
### F1 — <title>  [lens: intent-fit|testability|simplicity] [severity: high|medium|low]
claim: <what is wrong>
evidence: <file:line or quoted text you actually read>
suggested change: <concrete>

## Checks that cannot fail
<each postcondition you judge vacuous, with why. "none found" is a valid answer
only if you enumerated all of them — state the count you checked.>

## What I did NOT check
<explicit scope of this critique>

## Workflow Feedback
<anything about this handoff or the process that got in your way>
```

Do not self-triage. You raise findings; the Commander disposes of every one.
