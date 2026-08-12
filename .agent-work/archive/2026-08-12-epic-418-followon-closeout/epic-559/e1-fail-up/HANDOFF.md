# Implementer handoff — E1: a crew that gets stuck must have somewhere to go

**Work id:** `epic-559/e1-fail-up` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/e1-fail-up` (branch `epic-559/e1-fail-up`, off `main`@`90b39e2b`)
**Your spine:** `.agent-work/epic-559/e1-fail-up/IMPLEMENTER_PLAN.json` — five gates, every postcondition a real command. The Admiral ran them all before dispatching you: every substantive one is **red**. Drive it gate by gate.

## The ruling

The human, verbatim: *"crew should fail up. that could eventually reach all the way to me, but I'd
prefer it go one rung at a time."* And: *"we should mechanically provide the parent for cases where
admirals are driving crews directly. having the parent to message seems very useful."*

## Why this is not theoretical

Last night a reviewer hit a check it could not satisfy. It looked for the Commander that dispatched
it, found none named anywhere reachable, and closed its gate with `--authority human` — an authority
it did not hold — because the alternative was to stop dead with nothing delivered. It disclosed that
in its own result, which is the only reason it was recoverable.

The rule said "ask up." Nothing told it who "up" was. Three facts, all verified on `main`@`90b39e2b`
just now:

- No parent is bound or recorded anywhere in `run_crew.py`.
- `CREW_ALLOWED_TOOLS` grants a crew no messaging tool at all.
- `blocked` is not a recorded outcome. A crew that does exactly the right thing — blocks and
  returns — records `failed`, indistinguishable from one that crashed.

That last one matters most: **it makes doing the right thing cost the crew its record.**

## The gate that decides whether this is a mechanism or a record

`f3-can-it-reach`. A crew is a headless `claude -p` subprocess. Whether it can reach the session
that dispatched it is an **empirical question about this harness**, and you must answer it by
dispatching a real crew and trying, not by reading docs and designing around an assumption.

Three rework rounds were spent on this branch's siblings this week, every one of them on a claim
that was reasoned rather than run. Do not add a fourth.

**An honest negative is a complete deliverable here.** If messaging does not reach, say so plainly,
remove the grant, and say why — the durable path is already complete without it: a blocked gate
recorded in the spine, plus the parent recorded in the registry, is a full fail-up record that a
polling parent finds. Do not ship a tool that cannot fire.

## The other four gates

`f1` — `--parent` on `run_crew.py`: recorded in the registry, bound into the crew's environment as
`SPINE_PARENT`, named in the crew prompt on **both** branches (handoff and spine-only). A dispatch
with no `--parent` must still work and must say the parent is unknown. **Never invent one** — that
is precisely the failure this exists to stop.

`f2` — `blocked` as a distinct recorded outcome, naming the gate and the parent being asked, said
plainly in the launcher's own output. `failed` keeps meaning the crew died or produced nothing.
Include the negative control: a spine with no blocked gate must never record `blocked`.

`f4` — one short paragraph in each of `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md`:
a crew that cannot satisfy a check blocks and names its parent, never waives its own gate, never
invents an authority. The launcher does the mechanical half; the text only has to stop a crew
improvising. **Do not mention the engine CLI and do not reintroduce a CLI fallback** — that text was
removed from both files this week for cause, and a crew that reads it reaches for the CLI.

`f5` — suite, map, commit.

## Scope

**In:** `scripts/run_crew.py`, `skills/implementer/SKILL.md`, `skills/reviewer/SKILL.md`, `tests/`,
`map/INDEX.md`.

**Out — hard no-gos:** `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
`settings.json`, `docs/agents/*`, and all spine templates under `skills/*/templates/` — two sibling
crews are working in parallel right now and a change there will collide. No merge or push to `main`.

## Three things that cost your predecessors a rework round

**Commit before you finish.** One crew drove its spine to done and left every change unstaged.
Gate `f5.c2` refuses on a dirty tree.

**Rebuild the map.** `python -m scripts.code_map build --root .` — a crew shipped a stale
`map/INDEX.md` and turned the suite red for the next reviewer.

**A module-scope import must ship where it is used.** `run_crew.py` is bundled into installed
Commander and Explorer skills; an import of a sibling that is not bundled with it breaks every
installed dispatch at import time, before argparse. That happened this week. If you add an import,
check `SCRIPT_RUNTIME_COMPANIONS` in `scripts/install_constellation.py`.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **The goal is a weaker agent than you.** Prose is a liability; put it behind a check.
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.
- **Use the door.** `SPINE_FILE` and `SPINE_SESSION` are bound for you; find `mcp__spine__*` via
  `ToolSearch`. It covers all 18 engine verbs, so there is nothing you need the CLI for. If you
  reach for it anyway, say so and say what made it the natural move — that is useful evidence, not
  a mark against you.

## Deliverable

`.agent-work/epic-559/e1-fail-up/IMPLEMENTER_RESULT.md`, from the implementer skill's template,
including its **Workflow Feedback** section.
