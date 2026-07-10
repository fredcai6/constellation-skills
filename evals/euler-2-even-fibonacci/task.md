# Scenario: Project Euler #2 — Even Fibonacci sum (delegated commander)

You are a **delegated commander** — running from a frozen launch order with no
reachable human — driving one bounded issue end to end using the constellation
skills installed in this project (`.claude/skills/`).

## Mission (bounded issue)

Solve **Project Euler Problem #2**, with tests, as a bounded issue:

> By considering the terms in the Fibonacci sequence whose values do not exceed
> four million, find the sum of the even-valued terms. (The known answer is 4613732.)

## How to run it — a real constellation workflow, not a one-off script

1. Load the **constellation-commander** skill and drive its gated engine spine for
   this bounded issue: `init → context → understand → plan → execute → reconcile →
   triage → review → feedback → archive`. Instantiate `spine.json` from the
   commander spine template and drive it to a **terminal / complete** state
   **through the checklist engine** — this is mandatory, not advisory: every
   step is claimed, started, evidenced, and advanced via engine calls, and a step
   the engine never advanced didn't happen. The engine ships with the installed
   skills; every mutating call goes through it:

   ```
   python .claude/skills/constellation-workbench/scripts/checklist_engine.py      --file .agent-work/<work-id>/spine.json <verb> <step> [--session-id <id>]
   ```

   (verbs: `claim`, `start`, `advance`, `attest`, `attach`, `record`, `release` —
   run `-h` for grammar). In delegated mode, satisfy the human-decision gates
   (`understand`, `plan`, `triage`, `review`) by attaching user-decision evidence
   that cites this launch order.
2. In the **execute** step, produce the solution. Implementation may be **inline**
   in delegated mode — you may write `solution.py` / `test_solution.py` directly.
   Dispatching an **implementer** crew to write the solution and a **reviewer** crew
   to verify it (per the commander's crew-dispatch discipline, never hand-launched)
   is **optional in this dispatch** — inline implementation is sanctioned by this
   launch order. Driving the spine to a **terminal / complete** state through the
   engine is not optional.
3. Produce, in the **workspace root** (not under `.claude/`):
   - `solution.py` — computes and **prints** the answer.
   - `test_solution.py` — a `pytest` test asserting the computed answer equals the
     expected value.
4. Run `pytest` and get it **green**.
5. Reconcile / triage / review / record feedback as the spine requires (a reasoned
   no-op is compliant where an artifact genuinely does not exist).

## Completion

As the **final step**, after the spine is terminal and the tests are green, write
the completion sentinel `work-complete.txt` in the workspace root (any content).
The run is complete only when that file exists.

