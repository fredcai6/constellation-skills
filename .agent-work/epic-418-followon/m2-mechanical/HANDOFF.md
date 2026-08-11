# Implementer handoff — M2: make the mechanical things mechanical

**Worktree:** `/home/tommy/projects/constellation-skills-wt/m2-mechanical`, branch `epic-418/m2-mechanical` off `main`@`27a5adf5`.
**Your spine:** `.agent-work/epic-418-followon/m2-mechanical/IMPLEMENTER_PLAN.json`. Drive it gate by gate through the `mcp__spine__*` tools — your door is bound to it. If the tools are not available to you, say so in your result; that is a finding.

## The human's ruling, verbatim

> granting permissions as part of the launcher makes sense. make the mechanical things mechanical.
> the goal is as little thought for running things as possible.

> we just need to make sure our work is as os agnostic as possible, so try to keep entry
> definitions configurable.

Two jobs follow.

## Job 1 — the launcher grants what a crew needs

`build_crew_argv` (`scripts/run_crew.py`) builds `[claude, -p, prompt] (+ --model)`. It passes **no
`--allowedTools` and no `--permission-mode`**, so a spawned crew starts with default headless
permissions and cannot do a crew's work. Every dispatch in this epic worked around it by hand-writing
a gitignored `.claude/settings.local.json` into the worktree first — including the one that launched
you. That is the defect: an operator must remember something the tool should do.

Make the launcher self-sufficient. A dispatch into a worktree with **no** hand-written settings file
must complete crew work end to end.

Evidence that counts: a control that **fails first** without your change — dispatch into a clean
worktree with no settings file and show the crew unable to work — then the same dispatch succeeding.
Note honestly what you could and could not observe; you do not have to spawn a full crew if a
narrower observation is the honest unit, but say which you used.

## Job 2 — no literal interpreter in any shipped path

`.mcp.json` hardcodes `"command": "python3"`. On this host `/usr/bin/python3` is the interpreter
**without** pytest; on the repo owner's Windows box `python3` is not a command at all. Entry
definitions must resolve per machine.

**Reuse the per-machine interpreter resolution `scripts/install_constellation.py` already carries
from #539/#540** rather than inventing a second one. It hard-stops when nothing probes rather than
stamping a known-broken name — keep that property. Exercise it on a PATH where `python3` is absent,
and on one where it is present but lacks pytest.

This is deliberately **not** a Windows workstream. The human parked that. It is a constraint on how
entry points are written.

## Hard no-gos

`checklist_engine.py::claim`; `_identity_violation` / `from_child` confinement in
`mcp_spine_server.py`; `settings.json`; `docs/agents/*`. No merge or push to `main`. Commit locally
on your branch — a prior crew claimed it had committed when the branch had zero commits.

## Test mode

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
Use `python`, not `python3` (#561: `/usr/bin/python3` has no pytest here). Baseline: 2494 passed, 1 skipped.

## Stop conditions

Either control failing to reproduce; needing to touch a no-go; the engine refusing a gate you cannot
honestly satisfy. Report rather than widen. An honest partial is a complete deliverable.

## Deliverable

`.agent-work/epic-418-followon/m2-mechanical/IMPLEMENTER_RESULT.md`, with Workflow Feedback. A cold
reviewer will read it.
