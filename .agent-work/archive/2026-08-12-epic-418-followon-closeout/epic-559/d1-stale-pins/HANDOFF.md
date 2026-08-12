# Implementer handoff — D1: two tests assert facts that are no longer true

**Work id:** `epic-559/d1-stale-pins` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/d1-stale-pins` (branch `epic-559/d1-stale-pins`, off `main`@`90b39e2b`)
**Your spine:** `.agent-work/epic-559/d1-stale-pins/IMPLEMENTER_PLAN.json` — two gates. The Admiral ran the checks before dispatching you: every substantive one is **red**. Drive it gate by gate.

## Task

`tests/test_mcp_adoption.py` holds two constants that were true when written and are false now.

```python
CLI_ONLY_VERBS = ("skip", "reopen", "append", "amend", "flag-candidate")
```

All five became reachable through the MCP door when it grew to cover all 18 engine verbs.
`spine_halt` now carries `block | resume | skip | reopen`, `spine_capture` carries
`append | flag-candidate`, and `spine_amend` covers `amend`.

```python
DOOR_TOOL_NAMES = (...)   # seven entries
```

The door ships nine — `spine_capture` and `spine_amend` were added.

A pin asserting a false fact is worse than no pin: it reads as coverage while guaranteeing nothing,
and it will fight the next person who tries to change the thing it names. Three separate crews
flagged this and each correctly left it alone as out of their scope. It is your scope, and it is
the whole of it.

## Do not restate — tie

The repo's verb surface is currently hand-restated in **eight** places with no tie to
`checklist_engine.py`'s argparse registry, which is the actual source of truth. A fifth hand-typed
copy is not an acceptable fix.

- `DOOR_TOOL_NAMES` should derive from or be pinned against `mcp_spine_server.TOOL_NAMES`.
  `scripts/run_crew.py` already solved this exact problem this week — its `CREW_ALLOWED_TOOLS` is
  tied by a test that imports `mcp_spine_server` with a scratch environment and goes red on
  divergence. Read that first; the same shape probably fits here.
- The CLI-only set should derive from the engine's own verb registry rather than a hand-typed list.

**If deriving proves genuinely awkward, say why in your result and add a test that goes red when the
lists diverge.** That is an acceptable answer. Silently retyping the correct values is not — they
will be wrong again within a month, which is exactly how they got wrong this time.

Watch the import trap: `mcp_spine_server` reads `SPINE_FILE` and `SPINE_ENGINE` from the environment
at **import time** and raises `KeyError` without both set, which is why `run_crew.py` does not
import it at module scope. Import it inside a test with a scratch environment.

## Preserve what this file does well

`_cli_only_verb_violations` pins its own false-positive and false-negative boundary with
`VIOLATING` / `INNOCENT` / `ACCEPTED_FALSE_ALARM` fixtures. That is the best guard-authoring pattern
in this repo and two other crews were told to copy it this week. **Keep that structure intact.** You
are correcting the facts it asserts, not replacing the machinery.

## Scope

**In:** `tests/test_mcp_adoption.py`, whatever fixture or helper it needs, `map/INDEX.md`.

**Out — hard no-gos:** `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
`scripts/run_crew.py`, `skills/implementer/*`, `skills/reviewer/SKILL.md` (sibling crews own those
right now), all spine templates, `settings.json`, `docs/agents/*`. No merge or push to `main`.

If correcting the pins reveals a genuine defect in the door or the engine, **write it in your result
and do not fix it** — that is a finding, and fixing it here would put you in a file a sibling crew
is editing.

## Two things that cost your predecessors a rework round

**Commit before you finish** — gate `h2.c2` refuses on a dirty tree. **Rebuild the map** with
`python -m scripts.code_map build --root .` if it drifts.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."* This one is genuinely
  small. Resist growing it.
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.
- **Use the door.** `SPINE_FILE` and `SPINE_SESSION` are bound for you; find `mcp__spine__*` via
  `ToolSearch`. If you reach for the CLI, say so and say what made it the natural move.

## Deliverable

`.agent-work/epic-559/d1-stale-pins/IMPLEMENTER_RESULT.md`, from the implementer skill's template,
including its **Workflow Feedback** section.
