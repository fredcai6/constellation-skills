# Reviewer Handoff — g2: bind the door to an existing spine

## Gate
`g2-review` (epic-567-door/cmdr-a, lane A of epic #567)

Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
Branch: `feat/567-a-spine-identity`. **The shell's working directory does not
persist between tool calls** — use absolute paths or a single `cd <abs> && ...`.

## Task statement (what the implementer was asked to do)

Add one MCP door tool, `spine_bind(spine_file)`, binding this door process to a
spine file that **already exists**, so an agent whose door launched with no
`SPINE_FILE` can drive its own spine through the door instead of the CLI.

Read, in order:
1. `.agent-work/epic-567-door/cmdr-a/DESIGN_CONVERGENCE.md` — the governing design.
2. `.agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-implementer-handoff.md` — the
   handoff, which carries the close criteria you are judging against.
3. `.agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-implement-implementer-result.md`
   — what the implementer claims it did.

## How to inspect the diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  git diff 3e4b0e20..HEAD -- scripts/ tests/ && git status --short
```

`3e4b0e20` is the pre-implementation commit. **New test files are untracked until
staged**, so check `git status` as well as `git diff` — a file missing from the diff
is not a file missing from the change.

`.agent-work/` is **not** gitignored in this repo, so the implementer's own result
file appears in the diff too. That is expected.

## Your primary job, stated first because it is the one that gets skipped

**Attack the isolation property. Do not merely confirm the tests pass.**

`decision:isolation-not-fencing` is graded `guess/admiral`, and its recorded
`settle:` condition is literally *"name the property in the design doc and have the
reviewer attack it."* You are that reviewer. The property to attack, from
`DESIGN_CONVERGENCE.md`:

> One spine per process, decided at launch, at mint, **or by one confined binding to
> a spine that already exists inside this door's own checkout, whose session identity
> the spine itself dictates.**

Concretely, try to break it. Each of these is a finding if it succeeds:

- Bind a spine **outside** the containment root. Absolute path, relative path with
  `../` traversal, a symlink pointing outside, a path with a trailing slash. Does
  every form refuse, and does the refusal name the boundary?
- Bind something that is **not a spine** — a directory, an empty file, `[]`, a JSON
  object with no `work_id`, a JSON object with a `work_id` but no gates.
- Bind a spine that **another process holds an active lease on**. Does it refuse? Is
  the refusal about identity, or does it silently let two agents share one session
  id? (That last case is lane G's live incident this wave — its own crew and its own
  fork drove one spine under one lease id and the lane could not tell its writes
  from an attacker's.)
- After binding, try to point any of the **nine pass-through tools** at a different
  spine. `_identity_violation` should still refuse. Try `--file=X` one-token form and
  the `--fil`/`--fi=` argparse prefix abbreviations — that function's docstring
  records six guards defeated by spellings they had not enumerated, so confirm the
  parser-based check still holds after the change.
- Bind, then bind again with a **different** path while holding a lease. Does
  `_rebind_refusal` still refuse rather than orphaning the lease?
- Bind twice with the **same** path. Is it an idempotent success, or does it wrongly
  refuse the caller for rebinding to where it already is?

## Close criteria you are verifying

- The **two-door round trip** works and is real: door 1 mints via `spine_open`; door
  2, launched unbound, binds the same spine and drives it; door 2's `SPINE`/`SESSION`
  are byte-identical to door 1's. **Re-run it yourself.**
- A **reach-delta negative test exists** — a path outside the boundary refused, with
  the boundary named in the refusal. If this test does not exist, that is
  **blocking**, regardless of how green the suite is. A green suite is not evidence
  that reach did not widen.
- The session is derived as `origin.work_id` when present, **else the spine's
  top-level `work_id`**. This is the correction the whole gate turns on. Verify by
  measurement, not by reading the code: confirm a spine with **no** `origin` block
  but a top-level `work_id` binds successfully. If it refuses, the implementation
  reverted to the candidate's original design and **fails the mission's two named
  cases** (`.agent-work/epic-567-door/spine.json`, the Admiral's own spine, and
  `IMPLEMENTER_PLAN.json`, the file #559 is about) — both have `origin: None`.
- A spine with **neither** field refuses, and the refusal explains that a door bound
  with no session cannot `claim`.

## The four pins — confirm by command, and confirm the controls

This is where a lazy review passes a weakened guard. For each, run it **and** check
that its positive control still fails when its regression is planted.

1. `tests/test_mcp_lifecycle.py:137` — `call_lifecycle_tool` returns only calls to
   names in `ALLOWED`. `ALLOWED` was `{"_spine_open", "_spine_close"}` and is expected
   to gain **one** name. Judge the argument in the handoff: adding a third *named
   dispatch function* to an allow-list preserves the property "this function only
   delegates, never synthesizes content", so it widens an allow-list without
   loosening a ban. **The positive control at `:156` must still fail on a
   mutate-then-return.** If it now passes, something was weakened — blocking.
2. `tests/test_mcp_lifecycle.py:194` — `SPINE`, `SESSION`, `run_engine` must not
   appear in `_spine_open`'s own source. Should be untouched. Confirm byte-identical.
3. `tests/test_mcp_lifecycle.py:563` — the module-wide pin: assignments to
   `SPINE`/`SESSION` are exactly `{<module>, _bind_process_to}`. The new dispatch
   function **must not** assign either. Confirm.
4. `tests/test_mcp_identity.py:817` — no tool property whose name contains `spine`,
   `session`, `engine`, `checklist_file`, `identity`. `spine_bind.spine_file`
   violates this **by design**, and the pin's own failure text says the fix is a
   documented exemption **plus** an `IDENTITY_TRADE.md` amendment in the same change,
   "so that cannot happen silently."

   Verify three things here, all of them findings if wrong: the exemption is
   **tool-scoped** (a `spine_file` property on `spine_advance` would still be
   caught); the amendment to `IDENTITY_TRADE.md` actually exists in the diff; and
   **the argument was not renamed** to `work_file`/`plan_path`/similar to dodge the
   pin. That rename is the specific dishonest fix this handoff forbids — it is the
   spelling game `_identity_violation` records losing six times, turned against the
   author's own test.

## Constraints the change must respect

- **`scripts/checklist_engine.py` is out of scope for g2** — a parallel crew owns it
  for #613's atomicity half. If the g2 diff touches it, that is a scope finding.
- **`scripts/hooks/*` untouched.** Hooks execute from the main checkout for every
  live session.
- No new environment variable. No caller-supplied session. No widening of the
  containment root beyond "this door's own checkout".
- `_identity_violation`'s semantics unchanged.

## Required evidence from you

- Every attack above, with the command and its actual output — including the ones
  that correctly refused. A refusal you did not try is not a refusal you verified.
- The four pins run, with their positive controls checked. Paste both results.
- The two-door round trip, re-run in your hands, not quoted from the implementer.
- The full suite:
  ```bash
  cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
    py -m pytest tests/ -q 2>&1 | tail -25
  ```
  Derive any failure distribution mechanically
  (`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), never from a
  glance at the tail. Failures confined to `tests/test_checklist_engine*.py` are
  probably the **parallel** g3 crew's, not g2's — say so rather than attributing them.

## Verdict

`APPROVE` or `BLOCK`, with reasons tied to specific evidence.

Do not soften a `BLOCK` into an approval with notes. Out-of-scope defects you notice
are **triage candidates**, listed in your result, not reasons to block and not things
to fix yourself. **File no issues** — this run is under `decision:no-issue-filing`.

Write `REVIEW_RESULT` to
`.agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md`
**before ending your turn** — that write is the delivery. Include a `Verdict:` line
whose value is exactly `APPROVE` or `BLOCK`, and a `Workflow Feedback` section.
