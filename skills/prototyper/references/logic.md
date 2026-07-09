# Logic branch

**Question this branch answers:** *"does this state model / data shape feel right?"* — reducers, state machines, event ordering, the shape of the data.

## Shape

An **interactive terminal app over a pure, portable logic module.** Two parts, kept strictly apart:

- **The logic module** — the thing under test. A reducer, state machine, or set of pure functions. **No I/O in the module**: no file reads, no network, no clock, no `stdin`. State transitions only: `(state, action) -> state`. This is the part that might survive.
- **The TUI shell** — throwaway. It reads keypresses, calls the module, and prints. It exists only so a human can drive the module by hand and watch it react.

The split is the whole point. Because the module is pure and portable, a validated one is **liftable straight into real code** — that lift is the `absorbed` disposition. The shell never lifts; it is disposable by construction.

## Rules

- **Surface full state after every action.** Print the entire state object after each keypress — not a summary, the whole thing. The question is whether the shape feels right, and you can only judge that by watching every field move.
- **One command to run.** State it in the result. The human drives it live.
- **No persistence, no tests, no polish.** The module's correctness is judged by the human driving it, not by an assertion suite. If you feel the urge to write a test, that is a signal the module is close to real and should be absorbed, then tested in its real home.
- **Keep I/O at the edges.** Any input parsing or output formatting lives in the shell. If a would-be-pure function needs I/O to answer the question, the data shape is likely wrong — that itself is a finding worth reporting.

## Scoped verdict

Report the answer against the specific interactions you actually drove. A reducer that felt right under sequential single-user edits has been tested *there* — say so, and name concurrency, undo, or large-state behavior as **NOT tested** if you didn't drive them. The default next move after a rough spot is another shape of the same module, not "state machines are wrong for this."

## Surviving module

If the module earned its keep, name it in the result and where it should live in real code. Its disposition is **absorbed** with the commit ref once lifted, or **deleted** if the answer was "this shape is wrong" and nothing survives.
