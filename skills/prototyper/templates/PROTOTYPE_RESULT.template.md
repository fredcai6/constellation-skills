# Prototype Result: `<short title>`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`GLOSSARY.md`).

## Question
`<the one named question, copied from the handoff>`

## Verdict
`answered-yes | answered-no | not-immediately-right`

**Answer:** `<the scoped answer. Direct — yes / no / this variant, under these conditions. Not a hedge, not a recommendation for more process.>`

**Revive condition (not-immediately-right only):** `<the named condition that would make this question answerable again — a dependency lands, a tool becomes available, a variant becomes worth trying. not-immediately-right parks the question with a name; it is never a silent drop, and it is never a substitute for answered-no when the run actually got a negative result.>`

## What was tested AND what was NOT tested
- **Tested:** `<the exact interactions / variants / inputs / conditions you actually exercised>`
- **NOT tested:** `<what this run did not cover — concurrency, scale, other inputs, other variants. A null with an empty NOT-tested line is unfinished. Scoped nulls: a negative result kills THIS test under THESE conditions, never the idea class.>`
- **Next variant (if null):** `<the default move after a negative result is another variant — name it, or state why the class is genuinely exhausted with class-spanning evidence>`

## What it taught beyond the question
`<anything the prototype surfaced that the question did not ask — a shape problem, a hidden edge case, a better question to ask next>`

## Surviving pure module
`<logic branch: the validated module and where it should live in real code | none>`

## Disposition
`deleted | absorbed | parked-with-owner | captured-to-worktree`

**Detail:** `<deleted: answer is captured above, code is gone | absorbed: commit ref of the lift | parked-with-owner: owner name + why it stays alive | captured-to-worktree: worktree path + branch + owning issue pointer; kept until the human disposes it (re-affirm or dispose at epic close — accumulation cap)>`

## One command to run (if not yet deleted)
`<the single command, for anyone re-running before closeout>`
