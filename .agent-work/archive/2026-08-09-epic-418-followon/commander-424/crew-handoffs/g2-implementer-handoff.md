# Implementer handoff — gate g2: DC4, same-gate equivalence as a property

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g2-implement`
**Worktree (work only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch order.

## Task

Prove **DC4** of workstream F, mechanically and as a **property**:

> The CLI projection and the MCP tool result carry the **same imperative text** for **every gate that
> has one**.

Deliverable: `tests/test_mcp_imperative_equivalence.py`.

## Why this gate exists, and the trap it is built to avoid

The spec is explicit (critic finding F42): **one gate matching once establishes nothing.** Drift
happens later, and at a gate nobody sampled. So this is not "pick a gate, compare the strings". It is
a property over the whole population of gates carrying an imperative, across the shipped spine and
plan templates.

g1 already shipped a byte-identity check for a single gate, and the g1 reviewer confirmed that check
can genuinely fail. **That is the sample. This gate is the population.** Do not simply re-run or
rename the existing check.

## What "every gate that has one" means concretely

Enumerate the gates from the shipped templates — at minimum the commander spine template and the
execute-plan template, plus any other role spine/survey templates the corpus ships that carry
`imperative` fields. Find them by walking the installed/committed template tree rather than by
hand-listing paths, so a template added later is covered automatically rather than silently missed.

For each such gate: render the CLI projection's imperative and the MCP tool result's imperative, and
assert they are **byte-identical**.

## The three verification rules this gate is graded on

These come from `docs/agents/CREW_CONTEXT.md` and they are the difference between an accepted change
and a reworked one here.

1. **A check that cannot fail is indistinguishable from one that passed.** Demonstrate the red state:
   mutate one imperative, watch the property go red, **assert the mutation actually applied** (a
   `sed` that silently matched nothing leaves a green suite that reads exactly like a passing guard),
   then restore. Include the evidence of that red run in your result.
2. **Any guard that loops must assert what it looped over.** A glob or comparison over a set that
   turns out empty reports clean without ever examining an interesting item. **Assert the gate count
   is non-zero and report the number.** If the count is suspiciously small, say so rather than
   passing quietly.
3. **Assert against behaviour, never against text that describes it.** Compare rendered output, not
   docstrings or `description=` fields.

## Constraints

- Work only in the worktree above.
- **Do not edit** `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
  `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py` —
  fenced to a concurrent agent.
- **Do not fix** engine bugs #439, #446, #427, #443 — held constant across a later gate's two
  measurement arms.
- Do not modify `scripts/mcp_spine_server.py` to make the property pass. If the property finds a real
  divergence, that is a **finding** and it goes in your result — the door changing its output to
  match a test is exactly the drift this DC exists to detect. Report it; do not paper over it.
- Do not hand-edit any checklist JSON or anything under `episodes/`.
- If rebuilding is needed because you added source files, note that this repo has a code map at
  `map/` with a freshness test (`tests/test_code_map.py`); rebuild with
  `python -m scripts.code_map build --root .` and commit, or the suite goes red.
- Host is **Linux**. Corpus text assuming Windows is stale; both `python` and `py` resolve to one
  venv (3.12.3, pytest 9.1.1).

## Test mode and verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_imperative_equivalence.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**BASELINE CORRECTED — the pinned red set is retired.** An earlier draft of this handoff listed six
pre-existing failures owned by a concurrent agent. That pin is gone: #531 merged to main and this
branch merged origin/main at `05b35a2e`. Measured by the Commander on this exact tree immediately
before dispatching you:

```
$ cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2172 passed, 1 skipped, 1061 subtests passed   # 0 failed
```

**Your gate is `0 failed`, not "the set has not grown."** Any failure is yours or a real regression —
do not wave one through as pre-existing.

**Two other things changed under this handoff since it was drafted, so do not be surprised:**

- `scripts/gen_mcp_config.py` **no longer exists.** It was removed at `g1-integrate` as redundant:
  the committed project-scope `.mcp.json` uses `${VAR:-default}` expansion, so identity comes from
  each caller's own environment at server launch. If your test needs to launch the door, launch it
  from that environment seam — do not resurrect a generator.
- `tests/test_mcp_identity.py` now exists (gate g3, DC2/DC3) and is **not yours to edit**. Read it for
  the house pattern: its `ServerInstance` helper is this repo's current example of driving a real
  server subprocess over JSON-RPC, including bounded reads that avoid the deadlock described below.

## Close criteria

1. `tests/test_mcp_imperative_equivalence.py` asserts byte-identity over **every** gate carrying an
   imperative in the shipped templates, discovered by walking the tree rather than a hand-maintained
   list.
2. The gate count is asserted non-zero and reported.
3. The property was demonstrated able to fail, with the mutation asserted as applied.
4. The test passes and the full suite ends **`0 failed`**. (Superseded: the old "pinned red set has
   not grown" bar — see the corrected baseline above.)
5. Any real divergence found is reported as a finding, not silently accommodated.

## Required evidence to return

The exact commands and their real output including exit codes; the gate count your property covered;
the red-state demonstration (the mutation, proof it applied, the failing output, and the restore);
the full pytest tail for `tests/` (must read `0 failed`).

**Watch for hangs.** A previous gate on this branch lost real time to a deadlock: `assertTrue(line,
f"...{proc.stderr.read()}")` evaluates its f-string message **unconditionally**, so a blocking pipe
read runs even on the success path. Never put a blocking read inside an eager assertion message.

**One more thing, and it is the thing I care about most in this gate.** If the property turns up a
**real divergence** between the CLI projection and the MCP tool result, that is a **complete,
successful deliverable** — report it as a finding and stop. Do not change the door to make the
property green; the door bending to match a test is precisely the drift DC4 exists to catch. And do
not soften a divergence into a caveat.

Equally: if you cannot put the property in a state where it would have caught a divergence, that is
**UNMEASURED**, not a pass. Say UNMEASURED and say exactly what stopped you. An unmeasured condition
reported as a pass is the one outcome I cannot use.

## Specific exclusions

The tracer/measurement (later gate). The DC2/DC3 identity tests (later gate). Fixing the six pinned
red tests. Touching `settings.json`. Closing any issue. Promoting anything into `docs/agents/*`.

## Reporting

Write your `IMPLEMENTER_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g2-implementer-result.md
```

**Write that file before ending your turn — the write is the delivery.** Include a
`## Workflow Feedback` section: where the skills, this handoff, or the engine cost you attention. Be
specific and blunt. Report a measured negative as a complete result; anything real but out of scope
goes back as a triage candidate rather than being fixed silently or dropped.

Commit your work to `epic-418/f-424-mcp-door` as you go.
