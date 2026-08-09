# Implementer handoff — gate `g1-implement`, REWORK (attempt 2): remove `scripts/gen_mcp_config.py`

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g1-implement` (rework)
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch
order (`LAUNCH_ORDER-424-continuation.md` §"Then g1-integrate").

## Why you are being returned for rework

`g1-integrate` is **blocked by its own reviewer**, and the BLOCK is on the **justification** for
`scripts/gen_mcp_config.py`, not on its code. The reviewer verified every protected-intent item and
found the code sound. What it falsified was the reason the file says it exists.

That reason has now been measured out of existence. Two measurements, both reproduced:

**M1 — a committed project-scope `.mcp.json` with `${VAR}` expansion already delivers per-dispatch
identity.** (g1 reviewer, re-reproduced by the Commander immediately before writing this handoff.)
Two `claude -p` dispatches, same directory, **no `--mcp-config`, no generated file**, differing only
in `SPINE_FILE`/`SPINE_SESSION` in the caller's environment:

```
$ SPINE_FILE=$PWD/<...>/a/spine.json SPINE_SESSION=varexp-session-a \
    claude -p "Call the MCP tool mcp__spine__spine_status ..." \
    --allowedTools "mcp__spine__spine_status" --output-format json
RESULT: ... ACTIVE g1 [pending] — VAREXP-A::46eaa14f4c1f771b ...

$ SPINE_FILE=$PWD/<...>/b/spine.json SPINE_SESSION=varexp-session-b   (same directory, same config)
RESULT: ... ACTIVE g1 [pending] — VAREXP-B::3df72224c355aeca ...
```

Each arm returned **its own** unguessable nonce, corroborated server-side: each spine directory's own
`mcp_calls.jsonl` recorded exactly one `current` call against **its own** `--file`. Evidence lives at
`.agent-work/epic-418-followon/commander-424/evidence/g1-resolve-varexp/`.

**M2 — an in-session Task-tool subagent inherits its dispatching process's MCP scope wholesale**
(gate g3, reproduced twice with independent nonces plus server-log corroboration; see
`crew-handoffs/g3-implementer-result.md`). A subagent with no configuration of its own reached the
parent's exact spine and identity.

M2 was the last standing hypothesis for keeping generation ("if the subagent shares the parent's
server, `${VAR}` cannot reach it, so per-dispatch generation is required"). **The first half is
confirmed and the second half does not follow.** A generated config is also bound at server-launch,
per process — it can no more give an in-session Task-tool subagent its own identity than `${VAR}`
can. M2 names a case **neither** mechanism solves, so it does not distinguish them.

**Conclusion, and it is the Commander's, not yours to relitigate: per-dispatch config generation is
redundant.** Everything it delivers for identity, the committed `${VAR}` path already delivers.
Nothing in the repo consumes `gen_mcp_config.py` except its own tests — `run_crew.py` has no MCP
wiring at all.

## Task

Remove `scripts/gen_mcp_config.py` and leave the door's tests exercising the mechanism that actually
ships.

1. **Delete `scripts/gen_mcp_config.py`** (`git rm`).
2. **Rewire `tests/test_mcp_spine_server.py`.** It loads the module at `GEN_CONFIG` /
   `load_module("gen_mcp_config", ...)` (around lines 27 and 390). Its docstring also names
   `gen_mcp_config.py`. Drop the generation-specific tests. **Do not simply delete the coverage** —
   whatever those tests were really asserting about the env seam (`SPINE_FILE`/`SPINE_ENGINE`/
   `SPINE_SESSION` binding, the `session_id#agentId` composition being an opaque string to the
   server) must survive against the committed `.mcp.json` `${VAR}` path or against a directly
   env-launched server. Say in your result which assertions you carried over and which you dropped
   as genuinely generation-only.
3. **Rewire `tests/test_mcp_identity.py`.** `DC3InheritanceMechanismTests` builds its "parent" by
   shelling out to `gen_mcp_config.py` (around lines 49, 514, 526, 547). Replace that with a parent
   launched directly from the environment seam — which is what the generated config did anyway, and
   is what the other tests in that file already do. **The DC2 and DC3 guarantees this file proves
   must not weaken**, and specifically:
   - DC3's **positive control stays in the assertion path**, and stays demonstrated red for its
     manipulations and green when correct. If your rewiring makes any control weaker, stop and say so.
   - The **ambient-leak counterfactual** must still prove the no-leak assertion is not vacuous.
4. **Correct the stale rationale in `scripts/mcp_spine_server.py`.** Its `SPINE_SESSION` docstring
   line says "(gen_mcp_config.py composes this key; the server just uses whatever string it is
   handed)". The parenthetical now names a deleted file. Keep the true half — the server treats the
   string as opaque — and re-point the composition to the caller's environment. **Do not** replace it
   with a fresh unmeasured claim.
5. **Rebuild the code map** and commit it: `python -m scripts.code_map build --root .`
   (note: `code_map` discovery enumerates `git ls-files`, so **stage deletions/additions first** or
   the rebuild will not see them).

## What NOT to do

- **Do not re-litigate the removal.** If you find hard evidence the removal is wrong, stop and report
  it as a blocker with the evidence — that is a finding I want. Do not quietly keep the file.
- **Do not** "compensate" by adding a new helper that generates configs under another name. The
  committed `.mcp.json` plus caller-set environment variables is the whole delivery mechanism now.
- **Do not** weaken any DC2/DC3 assertion to make rewiring easier.

## Constraints

- Work only in the worktree above.
- **Do not edit** `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
  `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py` —
  fenced to a concurrent agent.
- **Do not** change `scripts/checklist_engine.py` or engine lease semantics; do not fix engine bugs
  #439, #446, #427, #443. `git diff -- scripts/checklist_engine.py` must stay empty.
- **Never write `settings.json`** at any scope.
- Do not hand-edit any checklist JSON or anything under `episodes/`.
- Do not close any issue; promote nothing into `docs/agents/*`.
- Host is **Linux**. Both `python` and `py` resolve to one venv (3.12.3, pytest 9.1.1).

## Test mode and verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**Baseline is GREEN.** Measured on this tree: `2175 passed, 1 skipped, 1061 subtests passed`, **0
failed**. Your bar is **`0 failed`**, and the pass count will legitimately drop by however many
generation-only tests you remove — state the new number and account for the delta. There is no
"pinned red set"; that pin is retired.

**Watch for hangs.** A previous gate on this branch lost real time to a deadlock: `assertTrue(line,
f"...{proc.stderr.read()}")` evaluates its f-string message **unconditionally**, so a blocking pipe
read runs even on the success path. Never put a blocking read inside an eager assertion message.

## Close criteria

1. `scripts/gen_mcp_config.py` is gone from the tree and from `map/INDEX.md`.
2. No file in the repo references it — including docstrings.
3. Every DC2/DC3 guarantee in `tests/test_mcp_identity.py` still holds, positive control still in the
   assertion path and still demonstrated red and green.
4. Env-seam coverage from `tests/test_mcp_spine_server.py` survives against the shipped `${VAR}`
   path, with the carried-over/dropped split stated explicitly.
5. Full suite `0 failed`, with the pass-count delta accounted for.

## Required evidence to return

Exact commands and real output with exit codes; the full pytest tail for all three commands; the
before/after pass counts with the delta explained; the list of assertions carried over vs. dropped;
`git diff --stat` for the commit; confirmation that `git diff -- scripts/checklist_engine.py` is
empty.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g1-implementer-result-rework.md
```

**Write that file before ending your turn — the write is the delivery.** Include a
`## Workflow Feedback` section, blunt and specific. Report a measured negative as a complete result;
out-of-scope finds go back as triage candidates rather than being fixed silently or dropped.

Commit your work to `epic-418/f-424-mcp-door` as you go.
