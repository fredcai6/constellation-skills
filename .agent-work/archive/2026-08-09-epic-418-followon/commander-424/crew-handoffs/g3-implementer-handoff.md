# Implementer handoff — gate g3: DC2 separation and DC3 inheritance-fails-closed

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g3-implement`
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch order.

## Task

Build the two identity acceptance tests for the MCP front door. Deliverable:
`tests/test_mcp_identity.py`.

### DC2 — separation

> A parent and a subagent drive **two different spines at once**, each through its **own server
> instance**; leases never collide and each status call returns its own reading.

Genuinely concurrent, not sequential. Two different spine files. Two server instances, each bound to
its own `SPINE_FILE` / `SPINE_SESSION` via `scripts/gen_mcp_config.py`. Prove that a `spine_status`
through instance A returns A's gate and A's lease, and through instance B returns B's — at the same
time. The collision scenario must be one that **could actually have been caught** had leases leaked;
say how you know that.

### DC3 — inheritance fails closed

> A subagent dispatched with **no special configuration** gets a refusal or no identity — never the
> parent's lease or the parent's reading.

**This is the one with the trap, and the trap is the whole reason this gate exists.**

## The positive control — read this before writing a line of DC3

"A refusal **or no identity**" is *also* exactly what you get when the server never started, the
config never delivered, or the door is absent entirely. **As written, DC3 passes most loudly under
total non-installation of the thing it tests.** This is the same shape as A2's *no absence is
evidence*.

So: **prove the door is up and serving before a no-identity result is allowed to count as failing
closed.** The positive control must sit in the assertion path — if the control is only described in
prose or only checked by a reviewer, it is decorative and the gate fails.

Hold DC3's control to the same bar gate g2 sets for its property check: **demonstrate the red
state.** Show the DC3 assertion going **red** when the server is unreachable, and **green** once it
responds, and assert the manipulation actually applied. A check that cannot fail is
indistinguishable from one that passed.

## Mechanism disambiguation — do not conflate these two things

There is a live, real observation in this run: **two spines currently carry the same session id**
(`86708414-f5d3-40d3-8c9a-2f96d1ccdc14`), differing only in a free-text `claimed_by` field. It is
tempting to treat that as DC3 failing. **It is a different mechanism.**

- That observation is a **CLI-door / engine-lease** fact: the engine accepts a claim carrying an
  inherited session id and distinguishes the two spines only by free text.
- **DC3 is about the door:** whether a subagent dispatched with no MCP configuration can reach the
  *parent's server instance*, and through it the parent's lease and reading.

F's scope is the door, not the engine's lease-identity semantics. So **DC3's gate may legitimately go
green while the engine-side observation stays red**, and fixing the engine-side one is **not** in F's
scope. Do not manufacture the defect, and do not "fix" the engine to make a test pass.

If you find the test as written cannot separate the two mechanisms, **say so and stop** — report it
as a blocker rather than forcing a green. That is a finding I want, not a failure.

## Constraints

- Work only in the worktree above.
- **Do not edit** `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
  `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py` —
  fenced to a concurrent agent.
- **Do not fix** engine bugs #439, #446, #427, #443, and do not change engine lease semantics — all
  held constant across a later gate's two measurement arms.
- Do not hand-edit any checklist JSON or anything under `episodes/`.
- Adding source files makes `map/INDEX.md` stale and turns `tests/test_code_map.py` red. Rebuild with
  `python -m scripts.code_map build --root .` and commit.
- Host is **Linux**. Both `python` and `py` resolve to one venv (3.12.3, pytest 9.1.1).

## Relevant context

- `scripts/mcp_spine_server.py` binds its ambient state (`SPINE_FILE`, `SPINE_ENGINE`,
  `SPINE_SESSION`) from the environment at import time — that is the seam identity rides on.
- `scripts/gen_mcp_config.py` generates a per-dispatch config keyed `session_id#agentId`.
- A headless dispatch reaches a server as:
  `claude -p "<task>" --mcp-config <file> --strict-mcp-config --allowedTools "mcp__<server>__<tool>"`.
  `--strict-mcp-config` ignores all other MCP configuration, which is what makes an instance private.
- **Known and already corrected at g1:** a plain project-scope `.mcp.json` *does* serve a cold
  headless agent when `--allowedTools` is passed. Do not re-derive this; it is settled. It matters
  here because it is precisely how a subagent could accidentally inherit a door — which is what DC3
  must rule out.

## Test mode and verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_identity.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**BASELINE CORRECTED — the pinned red set is retired.** An earlier draft of this handoff named a
pre-existing set of six failures owned by a concurrent agent. That pin is gone: #531 merged to main
and this branch has merged origin/main at `05b35a2e`. Measured by the Commander on this exact tree
immediately before dispatching you:

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2163 passed, 1 skipped, 1061 subtests passed in 95.34s (0:01:35)
```

**Your gate is `0 failed`, not "the set has not grown."** If you see any failure, it is either yours
or a real regression — do not wave it through as pre-existing.

**Watch for hangs.** A previous gate on this branch lost real time to a deadlock: `assertTrue(line,
f"...{proc.stderr.read()}")` evaluates its f-string message **unconditionally**, so a blocking pipe
read runs even on the success path. Never put a blocking read inside an eager assertion message.

## Close criteria

1. DC2 proven with genuinely concurrent instances on two different spines, each returning its own
   reading, leases never colliding.
2. DC3 proven, with a positive control **in the assertion path** that has been demonstrated red when
   the server is unreachable and green when it responds.
3. The two mechanisms above are kept distinct, explicitly.
4. `python -m pytest -q tests` ends **`0 failed`**. (Superseded: the old "pinned red set has not
   grown" bar — see the corrected baseline above.)

## Required evidence to return

Exact commands and real output including exit codes; the concurrency evidence for DC2 (how you know
it was simultaneous); the red/green demonstration for DC3's positive control with proof the
manipulation applied; the full pytest tail (must read `0 failed`).

**Plus one named answer the Commander needs to resolve a blocked gate. Report it under a heading
`## DC3 verdict: does an in-session subagent share its parent's server?`:**

> Does an in-session Task-tool subagent share its parent's already-launched MCP server?

Answer it **as measured**, in one of exactly three forms, and label which:

- **YES, measured** — a subagent dispatched with no MCP configuration reached the parent's server
  instance (and through it the parent's lease/reading). Show the reaching.
- **NO, measured** — it demonstrably could not, *with the positive control green* proving the door
  was up and serving at the time. A no-identity result without a green control is **not** a
  measured no.
- **UNMEASURED** — you could not put the question in a state where either answer would have shown.
  Say exactly what stopped you.

**A measured negative is a complete, successful deliverable here. An UNMEASURED condition is not a
negative — never dress one up as the other.** If the honest answer is UNMEASURED, say UNMEASURED;
that is the answer I will act on, and reporting it accurately is worth more to me than a green gate.

Why it matters (context, not a thumb on the scale): if YES, `${VAR}` expansion in a shared
`.mcp.json` cannot reach that case and `scripts/gen_mcp_config.py` is necessary. If NO, per-dispatch
generation is redundant and the committed `${VAR}` path is the whole answer, and the script may be
removed. **Both outcomes are fine.** Do not shade the measurement toward either.

## Specific exclusions

The tracer/measurement (later gate). Same-gate equivalence (previous gate). Fixing the six pinned red
tests. Changing engine lease semantics. Touching `settings.json`. Closing any issue. Promoting
anything into `docs/agents/*`.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g3-implementer-result.md
```

**Write that file before ending your turn — the write is the delivery.** Include a
`## Workflow Feedback` section, blunt and specific. Report a measured negative as a complete result;
out-of-scope finds go back as triage candidates rather than being fixed silently or dropped.

Commit your work to `epic-418/f-424-mcp-door` as you go.
