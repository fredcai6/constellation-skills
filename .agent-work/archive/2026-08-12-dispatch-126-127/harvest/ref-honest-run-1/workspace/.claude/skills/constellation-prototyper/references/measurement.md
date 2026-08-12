# Measurement branch

**Question this branch answers:** *"is X actually faster / smaller / better?"* — anything settled by a number.

The mechanism is one you already know: **a scoreboard defines the metric first, each spike implements one mechanism, and the output is a number on the board.** A measurement prototype is one such spike.

**This branch does not restate that doctrine — it inherits it.** The scoreboard → parallel one-mechanism spikes → synthesis pattern is the shared orchestrator doctrine, and it lives in one place:

> **`skills/_shared/global-orchestrator.md`** — the decomposition/sequencing section: *"For open research/exploration: a tested scoreboard gate first, then parallel throwaway worktree spikes (one mechanism each) measured on it, then a synthesis gate that productionizes only the winner … Keep losers as documented negative results."*
>
> (Installed as `references/global-orchestrator.md` inside every orchestrator-tier skill, so the explorer or Commander dispatching this spike is already holding it.)

Read that section for the scoreboard-first sequencing and the keep-losers rule. What this skill adds on top is only the crew-side contract:

- **One spike answers one metric on one mechanism.** If the handoff's question needs two numbers, it needs two spikes.
- **Location: throwaway worktree.** Measurement is agent-driven — nobody eyeballs it live; it emits a number and is torn down (see the driver split in `SKILL.md`).
- **Scoped null:** a mechanism that lost on this metric, this input, this machine lost *there*. Record the number, the conditions, and mark the untested conditions **NOT tested**. A losing spike is a documented negative result on the board, never "X is impossible."
- **Disposition** is still mandatory — a measurement spike is almost always **deleted** once its number is on the board; the number survives in the result, the code does not.
