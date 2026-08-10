# Reviewer handoff — gate `g2-review` (issue #541, friction capture)

## What was built

The MCP door now records **its own** rejections — unknown tool, unknown multiplexed
`action`, missing required argument — one JSONL record per occurrence to a door-side log
beside the spine, and reports a write failure loudly on **every** occurrence. A real
episode was written under this run's nested work-id via `apply_episode_delta.py` citing
that log as an `artifact-ref`.

Read `.agent-work/epic-418-followon/commander-f2/crew-handoffs/g2-implement-implementer-result.md`
in full, then inspect: `git diff -- scripts/mcp_spine_server.py tests/`.

## Task statement

Verify the capture is real, that it **cannot fail silently**, and that its claims are not
stronger than its evidence.

## Close criteria

1. **One record per rejection**, for each of the three door-own classes. Not one per run.
2. **Fail loud EVERY occurrence.** The test must induce **N≥2** failed writes in one
   process and assert **N separate messages**. Verify that is what it actually does —
   a test inducing one failure and asserting one message proves nothing about "every",
   and coalescing is the exact defect being prevented.
3. **End-to-end.** A real episode under the **nested** work-id `epic-418-followon/commander-f2`,
   written through `apply_episode_delta.py --store-root episodes`, read back, and passing
   `python scripts/verify_episode_captured.py epic-418-followon/commander-f2`. Not a unit
   test that stops at the write call.
4. **A seeded rejection is scored**, proving the instrument *can* score — so a later zero
   is a reading, not a blind spot.
5. **The coverage boundary is stated**: which rejection classes it can and cannot see. A
   **client-side schema rejection never reaches the server process at all** — if the result
   implies otherwise, that is a BLOCK.
6. **Nothing in `episodes/` is phrased as guidance for a future agent.** Read the written
   episode. It is a **record**, past tense, of what happened. An assertion that reads as a
   rule for a future agent fails this gate (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The
   Retired Learning Playbook").

## MANDATORY mutation

Break the real thing and report whether the gate's evidence went **RED**, then restore and
confirm **GREEN**. At minimum: make a rejection write silently swallowed, and confirm the
loud-failure test fails. Then invent one of your own.

Four separate pins were defeated at this run's g1 for being weaker than the claim they
protected. Try hard to make this one the fifth — a capture that can be silenced without a
test noticing is exactly the defect this gate exists to prevent.

## Allowed scope / exclusions

Read-only inspection plus temporary mutation of `scripts/mcp_spine_server.py` (restore and
prove with `git diff`). **Do NOT edit** `scripts/checklist_engine.py`,
`scripts/apply_episode_delta.py`, `scripts/episode_capture.py`, `docs/EPISODE_STORE.md`, or
`scripts/hooks/spine_rail.py` — all outside this run's ownership. Confirm the implementer
did not either.

## Constraints

- **`python -m pytest`**, never `python3 -m pytest` — `/usr/bin/python3` has no pytest here
  and its non-zero exit reads as a red suite and is not one.
- **Never pipe into `head`/`tail` and read the exit code.** Redirect to a file, capture `$?`.
- Avoid backticks and command-looking text inside engine string arguments.
- `episodes/` is written ONLY through `apply_episode_delta.py`. Never hand-edit it.
- Windows writes need `encoding='utf-8', newline='\n'` on every write.
- Work only in this worktree; `/home/tommy/projects/constellation-skills` is fenced read-only.

## Confidence flag

F measured **zero** malformed calls in both DC5 arms. This gate builds an instrument; it
does **not** claim a phenomenon. If the result presents the capture as evidence that fumbles
occur, say so.

## Required evidence from you

Per-criterion verdicts; your mutation evidence with exact test ids and restore proof;
`python -m pytest -q` at 0 failed; and — standing requirement on this run —
**`git status --porcelain` for your worktree**.

## Verdict

`APPROVE` or `BLOCK` with reasoning, plus a `Workflow Feedback` section, to
`.agent-work/epic-418-followon/commander-f2/crew-handoffs/g2-review-reviewer-result.md`.
**That write is the delivery.**
