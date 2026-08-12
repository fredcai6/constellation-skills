# Cold reviewer handoff — M1: per-dispatch door binding + derived assignment-keyed identity

**Work id:** `epic-418-followon/m1-door-binding` · **Gate:** `g2-review` · **Role:** reviewer
**Worktree:** `/home/tommy/projects/constellation-skills-wt/m1-door-binding` (branch `epic-418/m1-door-binding`)
**Under review:** the diff on that branch against `main`@`e8d3b862`, plus
`.agent-work/epic-418-followon/m1-door-binding/IMPLEMENTER_RESULT.md`.

You are **cold**. You did not plan this change and you are not here to agree with it. The human's
standing ruling is that every implementer gets an independent reviewer, and it exists because two
review rounds on a sibling PR were each green through a real user-scope write.

## What the change was supposed to do

`scripts/run_crew.py` should hand every dispatched crew:

1. `SPINE_FILE` bound to **that crew's own spine**, and
2. `SPINE_SESSION` = `constellation/<work-id>/<gate>/<role>` — the assignment identity, **derived**
   from existing minting, **without** the `attempt-<n>` tail.

Nothing else. It is deliberately one wire between two constructs that already existed.

## Review criteria — check each, and say which you actually exercised

1. **Does a control reproduce the defect before the fix?** The implementer was required to produce
   two red controls first. Re-run them yourself. A command that fails for the wrong reason looks
   exactly like a guard working — that specific error has already been made once in this epic.
2. **Is the identity derived, or re-typed?** If the change introduces a second name builder rather
   than reusing `session_name`'s minting and validation, that is a finding: a second rendering path
   is the failure mode this whole epic exists to stop. Check `validate_work_id` and
   `_validate_session_component` still gate it.
3. **Is the `attempt-<n>` tail genuinely absent from the lease identity?** Present it, and every
   respawn becomes a recorded force-takeover. Prove it by claiming, then re-claiming as attempt 2,
   and confirming an idempotent `resumed lease` with **no** `previous_session_id` and **no**
   `takeover_reason` written.
4. **Does an explicit caller-supplied `SPINE_FILE`/`SPINE_SESSION` still win?** `setdefault`
   semantics must hold — the Admiral bootstraps through exactly that, and clobbering it would have
   broken the dispatch that produced this very change.
5. **Were the hard no-gos respected?** `checklist_engine.py::claim` semantics unmodified;
   `_identity_violation` and the `from_child` path confinement in `mcp_spine_server.py` not
   weakened; no per-call spine addressing opened; `settings.json` and `docs/agents/*` untouched;
   no merge or push to `main`.
6. **Do the new tests fail without the change?** Revert the production hunk in a scratch copy and
   confirm red. A test that passes both ways is not evidence.
7. **Full suite**, with real counts: `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`.
   Use `python`, **not** `python3` — `/usr/bin/python3` on this host has no pytest and fails with a
   misleading `No module named pytest` (#561).

## Context you should have, so you do not rediscover it

- The door was never broken. `mcp_spine_server.py` binds `SPINE_FILE` at launch and refuses
  redirection by design. `grep -rln SPINE_FILE scripts/` returned exactly one file — the server that
  only reads it. That is the entire defect.
- Confirmed doctrine (human, 2026-08-10): a spine belongs to a **task**; agents are assigned one at
  a time; the lease keys on the **assignment**, not the process instance; identity is **derived**,
  never typed; conflicts use the existing refuse-or-force-with-reason construct and are
  **deliberately not foolproof**.
- Live evidence from the dispatch that produced this change: the implementer drove its own spine
  through the door — `mcp_server_started` pointed at its own `IMPLEMENTER_PLAN.json`, 9 door calls,
  lease `constellation/epic-418-followon/m1-door-binding/g1-implement/implementer` active. The
  mechanism was proven working *before* the code landed, via the environment bootstrap. **That is
  not a substitute for reviewing the code that productionizes it.**

## What is explicitly NOT in scope

Do not require: per-call spine addressing, a `run_crew.py` permission/tool grant (queued separately
as decision 3), Windows launch (#555, parked), or `docs/agents/*` corrections (#561, the human's
call). Finding them is fine; blocking on them is not.

## Verdict

`APPROVE` or `BLOCK`, with the evidence you personally ran. **An honest partial is acceptable and a
silent gap is not** — say which criteria you exercised and which you only read. If you approve
something you did not test, say that too.

Write your verdict to
`.agent-work/epic-418-followon/m1-door-binding/REVIEWER_RESULT.md`, including its Workflow Feedback
section, before ending your turn — that write is the delivery.
