# Handoff — plan alternative A: `smallest-diff`

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `plan` · **Role:** `plan-alt-a` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander. Ask up to
it, not past it.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/plan-alt-a-result.md`

## What you are

One of two parallel plan-alternative authors in a design-it-twice run. You are **not** implementing
anything. You produce **one candidate gate plan** under **one named constraint**, and you argue it.
Another agent is writing the competing candidate under a different constraint; you never see it. The
Commander converges.

**Do not edit any file except your result artifact.** No source edits, no test edits, no commits.

## Read these first, in this order

1. `.agent-work/epic-559/c3-lifecycle/LAUNCH_ORDER.md` — the frozen principal. Its hard constraints bind
   your candidate absolutely.
2. `.agent-work/epic-559/c3-lifecycle/PROBLEM_STATEMENT.md` — the ask, and six re-measured baseline
   claims.
3. `.agent-work/epic-559/c3-lifecycle/MISSION_FRAME.md` — eight structural measurements your plan rests
   on. Re-run any you doubt; say so if one fails.
4. `.agent-work/epic-559/c3-lifecycle/DESIGN_IT_TWICE_BRIEF.md` — the contract you are executing.
5. `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` — the generator's frozen contract from
   last wave.

Then read the code the plan touches: `scripts/mcp_spine_server.py`, `scripts/generate_spine.py`,
`scripts/agent_work_root.py`, `scripts/verify_worktree_isolation.py`, `scripts/run_crew.py`,
`/home/tommy/.claude/skills/constellation-commander/scripts/init_work_area.py`, and
`tests/test_mcp_identity.py`.

## Your constraint — `smallest-diff`

**The least new structure that satisfies every required property.** No new module unless a property
genuinely cannot be met otherwise. Reuse `init_work_area.py` and `generate_spine.py` as libraries and
treat the new code as glue. Extend files that already exist rather than adding files. Prove the
properties, add nothing else.

Design honestly *under* this constraint — that is the point of the exercise. Where the constraint hurts,
**say where and how much**, in its own section. A candidate that quietly abandons its constraint is
worthless to the comparison; a candidate that names its own cost is what makes the comparison real.

## The thing being designed

Where the open/close lifecycle operation lives, and what the door tool is a client of. Everything else
in the plan falls out of that.

**Open** must: create branch + worktree + scaffolded work area + compiled spine + the crew-binding
environment in one operation; verify its own result with `scripts/verify_worktree_isolation.py` rather
than trusting `git`'s exit code; **refuse rather than half-succeed** and roll back; **record where it
opened**; **never silently reuse a worktree another crew is in**, refusing with a legible reason; and be
**reachable through the MCP door**.

**Close** must, in this fixed order — this ordering is NOT your latitude: satisfy the closeout gate's
postconditions → final `advance` → `release` the lease → **then** move `.agent-work/<work-id>/` to
`.agent-work/archive/<work-id>/` with the spine file **last** → commit the move, staged **by name** →
report a readiness verdict naming branch, commit, and what remains ("ready to PR"). It never opens a PR,
never removes a worktree, never judges the work good.

**The declared dispatch**: a spec declares the crews a gate dispatches, and the generator emits the
dispatch with `parent` and `model` already in it, refusing a declared dispatch missing either.

**Two carried findings**: `cond.get("not_yet_written")` bare truthiness in `scripts/generate_spine.py`
(add an `isinstance` guard and a VIOLATING fixture); and `DESIGN_NOTE.md` §4, §7, §10 reconciled to
shipped behaviour or the stale claims deleted.

## Hard constraints — a candidate that violates one is void

`scripts/checklist_engine.py`'s on-disk format is not changed · the close ordering above is fixed ·
close never opens a PR and never removes a worktree · stage by name, never `git add -A` ·
`settings.json`, `.mcp.json` and `docs/agents/*` untouched · `skills/**` untouched (a different crew owns
it; float it, never take it) · never run `scripts/install_constellation.py` · no merge or push to `main`
· never two crews in one worktree.

Note what `.mcp.json` being untouchable means: you **cannot register a new MCP server**. Anything
reachable through the door is reachable through the already-registered `spine` server or it is not
reachable at all.

## What your result must contain

1. **Your candidate, one paragraph.** The shape, stated so a reader knows immediately how it differs
   from any other candidate.
2. **The gate plan.** An ordered gate list. For each gate: id, title, the imperative in one or two
   sentences, close criteria as **checkable** postconditions (name the actual command where a command
   can check it), the required evidence, and whether it is a crew gate or a reasoning gate with the
   crew-waiver reason. Sequence so the test suite is **green at every gate boundary** — a deliberately
   red window across gates is a plan smell.
3. **The violating fixtures.** For every guard your plan ships, name the VIOLATING case it must catch
   and the INNOCENT case it must not. A guard exercised only on the happy path measures the mechanism,
   not the boundary. House style is `tests/test_mcp_adoption.py::_cli_only_verb_violations`.
4. **Your four answers**, argued not asserted: (a) how open is reachable through a door that binds one
   spine at import and whose `call_tool` is AST-pinned to two return shapes; (b) where the worktree
   record lives; (c) whether the declared dispatch is data the engine consults or prose a crew retypes;
   (d) one lifecycle tool or two, and why.
5. **Where your constraint hurts.** Named, specific, with the property it strains.
6. **Scoring.** Rate your own candidate on depth, locality, seam placement, testability — and say what
   it would lose to a candidate built the other way.
7. **Anything you measured that contradicts the mission frame.** Re-run and report. A frame measurement
   that turns out wrong is more valuable than a candidate that assumes it.

## Stop conditions

- A hard constraint would have to be violated for your candidate to work → say so plainly; that is a
  complete and useful result.
- You cannot read a file the plan depends on → say which, and continue with what you can.
- Never invent a measurement. Run the command or say you did not.

## Return format

Write the result artifact at the path named above **before ending your turn** — that write is the
delivery. Then return a short pointer: your candidate in one line, the gate count, and the path. Return
thin, write fat. Finish with a short **Workflow Feedback** section in the artifact: what in this handoff
helped, what got in your way.
