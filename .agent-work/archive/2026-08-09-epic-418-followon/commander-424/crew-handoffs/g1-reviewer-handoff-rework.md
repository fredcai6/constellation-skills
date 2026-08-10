# Reviewer handoff — gate `g1-review`, REWORK (attempt 2)

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g1-review` (rework)
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch
order.

## What happened, and what you are being asked to do

You (attempt 1) returned **BLOCK** on this gate. **You were right, you were not overridden, and the
BLOCK was not waived.** Your finding — that the stated justification for `scripts/gen_mcp_config.py`
did not hold, because a committed project-scope `.mcp.json` serves a cold headless agent and can key
identity per agent through documented `${VAR}` expansion — was reproduced by the Commander and then
acted on.

Your attempt-1 result said this "does **not** mean `gen_mcp_config.py` should be deleted," on the
grounds that protected-intent item 5 (each agent gets its own instance keyed `session_id#agentId`) is
a real requirement a single shared config cannot satisfy. **That specific reasoning is what the new
evidence overturns**, and you should check that claim hardest of all:

- **M1** — re-reproduced by the Commander: two `claude -p` dispatches, **same directory, no
  `--mcp-config`, no generated file**, differing only in `SPINE_FILE`/`SPINE_SESSION` in the caller's
  environment, each returned **its own** unguessable nonce; each spine directory's own
  `mcp_calls.jsonl` recorded exactly one `current` against its own `--file`. Evidence:
  `.agent-work/epic-418-followon/commander-424/evidence/g1-resolve-varexp/`. So a single shared
  `.mcp.json` **does** give per-dispatch identity — item 5 is satisfied without generation.
- **M2** — gate g3, reproduced twice with independent nonces and server-log corroboration
  (`crew-handoffs/g3-implementer-result.md`): an in-session Task-tool subagent inherits its
  dispatching process's MCP scope wholesale and reaches the parent's exact identity with no config of
  its own. This was the last hypothesis for keeping generation. It does not survive: a generated
  config is also bound at server launch, per process, so it cannot give an in-session subagent its own
  identity either. **M2 names a case neither mechanism solves, so it does not distinguish them.**

On that evidence the Commander decided to **remove** `scripts/gen_mcp_config.py`. The implementer has
done so (attempt 2). Review that change.

## The change to review

Commit `fda35ec0` — *"remove scripts/gen_mcp_config.py, rewire tests onto the shipped ${VAR} path"*.

```
cd /home/tommy/projects/constellation-skills-wt/f-424
git show --stat fda35ec0
git show fda35ec0
```

Implementer's own account, with its exact commands and evidence:
`.agent-work/epic-418-followon/commander-424/crew-handoffs/g1-implementer-result-rework.md`

Also in scope as the standing gate deliverable: `scripts/mcp_spine_server.py`, `.mcp.json`,
`tests/test_mcp_spine_server.py`, `tests/test_mcp_identity.py`.

## Close criteria — verify each yourself, do not take them on report

1. `scripts/gen_mcp_config.py` is gone from the tree and from `map/INDEX.md`, and **no file in the
   repo's shipped surface** (`scripts/`, `tests/`, `map/`, `.mcp.json`) still references it —
   including docstrings. (Historical `.agent-work/` handoffs and results legitimately still name it;
   those are records, not code.)
2. **Coverage was not silently deleted.** The implementer reports dropping `GenMcpConfigTests` (4
   tests) and adding `McpJsonVarExpansionLaunchTests` (1). Check the carried-over/dropped split in its
   result against the actual diff. Anything the dropped tests asserted about the env seam
   (`SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION` binding; `SPINE_SESSION` reaching the engine as an
   opaque `#`-composed string) must still be asserted somewhere.
3. **No DC2 or DC3 guarantee weakened** in `tests/test_mcp_identity.py`. Specifically: DC3's positive
   control is still **in the assertion path**, still demonstrated red for its manipulations and green
   when correct; the ambient-leak counterfactual still proves the no-leak assertion is not vacuous.
   Diff `DC3InheritanceMechanismTests.setUp` against attempt 1's version and say whether the new
   `ServerInstance`-built parent is equivalent to the generated-config parent it replaced.
4. The new `McpJsonVarExpansionLaunchTests` actually exercises the **committed `.mcp.json`'s own**
   `command`/`args`/`env`, not a hand-rolled copy of them. A test that re-implements the config it
   claims to verify proves nothing about the shipped file.
5. `git diff -- scripts/checklist_engine.py` is **empty**; engine lease semantics untouched; engine
   bugs #439/#446/#427/#443 not "fixed"; `settings.json` untouched at every scope; nothing promoted
   into `docs/agents/*`; no issue closed.
6. Full suite **`0 failed`**. Baseline before this change was `2175 passed, 1 skipped, 1061 subtests`;
   the implementer reports `2172 passed, 1 skipped, 1061 subtests`, a -3 delta it accounts for as 4
   dropped + 1 added. **Verify that arithmetic against the actual diff**, and confirm no test was
   quietly skipped, xfailed, or padded to make a number work.

## Verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

## What I want from you, stated plainly

**Do not rubber-stamp this because the Commander asked for it.** You blocked this gate once on a real
finding and that is exactly why the gate is where it is. If the removal is wrong, or the rewiring
weakened a guarantee, or the evidence I cited does not reproduce in your hands, **BLOCK again** and
say so — a second BLOCK is a fully acceptable outcome of this review and I will act on it rather than
override it.

Equally: if it holds, say **APPROVE** and say it cleanly. Do not manufacture a hedge.

If you re-run M1 yourself and it does not reproduce, that is the single most valuable thing you could
return.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g1-reviewer-result-rework.md
```

**Write that file before ending your turn — the write is the delivery.** State the verdict as a bare
`APPROVE` or `BLOCK` on its own line so it is machine-readable. Include a `## Workflow Feedback`
section, blunt and specific. Log out-of-scope finds as triage candidates rather than fixing them.
