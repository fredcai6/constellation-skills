# Reviewer handoff — gate `g3-review`: DC2 separation and DC3 inheritance-fails-closed

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g3-review`
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch
order.

## Task statement

Independently verify the two identity acceptance tests for the MCP front door, delivered at
`tests/test_mcp_identity.py`, against **both** done-conditions — not just the one with the trap.

> **DC2** — a parent and a subagent drive **two different spines at once**, each through its **own
> server instance**; leases never collide and each status call returns its own reading.
>
> **DC3** — a subagent dispatched with **no special configuration** gets a refusal or no identity —
> never the parent's lease or the parent's reading.

## How to inspect the diff

```
cd /home/tommy/projects/constellation-skills-wt/f-424
git show --stat 50fb7987      # the deliverable
git show 50fb7987 -- tests/test_mcp_identity.py
git show fda35ec0 -- tests/test_mcp_identity.py   # later rework: DC3 parent rebuilt without gen_mcp_config.py
git diff origin/main -- tests/test_mcp_identity.py   # net state, which is what actually matters
```

The implementer's account, with its exact commands and evidence:
`.agent-work/epic-418-followon/commander-424/crew-handoffs/g3-implementer-result.md`

Note the file has changed since it was first written: gate `g1-integrate` removed
`scripts/gen_mcp_config.py` as redundant, and `DC3InheritanceMechanismTests.setUp` was rewired to
build its parent directly via `ServerInstance`. **Review the net state**, not the first commit alone.
A separate reviewer already approved that rewiring
(`crew-handoffs/g1-reviewer-result-rework.md`); you are not being asked to re-approve it, but if it
weakened a DC2/DC3 guarantee, that is squarely yours to catch and say so.

## Close criteria — verify each yourself, do not take them on report

**DC3 — the positive control genuinely gates the assertion.**

1. "A refusal **or no identity**" is *also* exactly what total non-installation produces. So the
   control must make the DC3 assertion **impossible to pass when the server is absent**. Verify the
   control sits in the **assertion path** — not in prose, not in a comment, not only in setUp
   bookkeeping that a passing test could bypass.
2. Verify it is demonstrated **red-then-green**, not merely asserted: the red state actually
   reproduced, and **proof the manipulation applied** (the claimed cause, not some other failure).
   The implementer claims three distinct red manipulations. Check all three.
3. **Best single check available to you: mutate and watch.** Break the door yourself (hardcode an
   identity, point the server at the wrong spine, make it unreachable) and confirm the DC3 tests go
   red, then restore. A check that cannot fail is indistinguishable from one that passed.

**DC2 — the separation claim is real.**

4. The two instances are **genuinely concurrent**, not sequential. The implementer claims a 25-round
   interleave and a `threading.Barrier(2)` overlap test asserting the wall-clock windows actually
   intersect. Verify the ordering could not be produced by a sequential driver.
5. The two spines are **genuinely different** files, and each status call returns **its own** reading.
6. The **collision scenario is one that could actually have been caught** had leases leaked. The
   implementer claims a control pointing two processes at one shared file that reproduces the leak
   (red) against two separate files that do not (green). Verify the leak really reproduces — if it
   does not, the separation assertions are vacuous.

**Both.**

7. The two mechanisms are kept **explicitly distinct**: the "two spines share one session id"
   observation is a **CLI/engine-lease** fact, **not** DC3. DC3 is about the door — whether a
   subagent with no MCP configuration can reach the *parent's server instance*. Confirm the tests do
   not conflate them, and that **`scripts/checklist_engine.py` has an empty diff** (no engine was
   "fixed" to make a test pass).
8. No fenced file touched: `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
   `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py`.
   `settings.json` untouched at every scope. No issue closed. Nothing promoted into `docs/agents/*`.
9. **No blocking read inside an eager assertion message.** A previous gate on this branch deadlocked
   on `assertTrue(line, f"...{proc.stderr.read()}")`, whose f-string evaluates unconditionally.
   Confirm the pattern is absent, and that the suite does not hang.
10. Full suite **`0 failed`**. Current tree: `2172 passed, 1 skipped, 1061 subtests passed`.

## The live DC3 experiment — verify its scope, and say if it is over-read

The implementer additionally ran a live `claude -p` + Task-tool experiment (scratch evidence, not
committed to `tests/`, matching g1's precedent) and reported the answer to the Commander's named
question as **YES, measured**: an in-session Task-tool subagent inherits its dispatching process's
MCP scope wholesale and reached the parent's exact identity. Evidence:
`.agent-work/epic-418-followon/commander-424/crew-plans/scratch-g3-live/`.

**This verdict was load-bearing** — the Commander acted on it to remove `gen_mcp_config.py`. So:

11. Verify the nonces in `dispatch_stdout.json` / `dispatch2_stdout.json` match `nonce.txt` /
    `nonce2.txt` and the spine imperatives, and that `mcp_calls.jsonl` corroborates the call count
    independently of the model's self-report.
12. The implementer **stated the limit of its own YES** — that it cannot distinguish "reused the same
    server connection" from "independently re-resolved the identical config and got its own process
    bound to the identical identity." **Confirm that limit is honestly stated and that nothing
    downstream over-reads the YES beyond it.** If you think the YES is over-read anywhere, say so
    plainly; that is worth more to me than an approval.

## Verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

## What I want from you, stated plainly

**BLOCK is a fully acceptable outcome and I will act on it rather than override it.** This gate exists
because DC3 has a trap that makes non-installation look like success. If the control is decorative,
if the concurrency is really sequential, if the collision control cannot actually catch a leak, or if
the live experiment's YES is over-read — say so and block. Do not approve because the numbers are
green.

Equally, if it holds, say `APPROVE` cleanly and do not manufacture a hedge.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g3-reviewer-result.md
```

**Write that file before ending your turn — the write is the delivery.** State the verdict as a bare
`APPROVE` or `BLOCK` on its own line so it is machine-readable. Include a `## Workflow Feedback`
section, blunt and specific. Log out-of-scope finds as triage candidates rather than fixing them.
