# Rework handoff — A, pass 3: two false positives found by a real dispatch

**Work id:** `epic-559/a-spine-is-the-job` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job` (branch `epic-559/a-spine-is-the-job`)
**Your spine:** `.agent-work/epic-559/a-spine-is-the-job/REWORK2_PLAN.json` — three gates. The Admiral ran every substantive check before dispatching: **all red.** Drive it gate by gate.

## The question you were worried about answered safely

The round-2 reviewer drove real spines into every state and read `spine_terminal` on each.
`checklist_engine.TERMINAL` is `{"complete", "skipped"}`; `blocked` is not in it. A crew that
correctly blocks and asks up is recorded **`failed`**, not `completed`. Your completion-contract
change is sound. Two other things block.

## Blocker 1 — `run_crew.py` is dead on every installed bundle

`2152ded3` added `import install_constellation` at module scope, to reach
`assert_shell_safe_command`. **`install_constellation.py` ships in no bundle that carries
`run_crew.py`.** The reviewer installed real bundles and ran them:

```
$ python /tmp/instsim/skills/constellation-commander/scripts/run_crew.py --help
ModuleNotFoundError: No module named 'install_constellation'
EXIT=1
```

Two-sided against `main`, same install, same invocation: `EXIT=0`. Same for the explorer bundle.
It fails at import, before argparse — so **Commander and Explorer, running from an installed
install, can launch no crew at all.** That is the sanctioned invocation: `global-everyone.md` says
to reference bundled scripts by their absolute installed path.

The repo already documents this exact drift class at `scripts/install_constellation.py:80-88` —
*"if a script reaches a sibling by `sys.path.insert` + a plain import, ship that sibling too, or the
feature silently no-ops wherever the skill is actually installed"* — written down because the last
occurrence left the Context Governor inert in every install since it shipped.

**And the guard written to stop it recurring is blind.** It reads
`SCRIPT_RUNTIME_COMPANIONS.get("checklist_engine.py", ())` — a literal, so it watches one script
and no other. The defect recurred one file over from where it was documented, and the suite stayed
green. Fix the import so an installed bundle works, **and generalize the guard to key on every
declared script**, so the next occurrence is caught rather than documented after the fact.

The `checklist_engine` import from the same commit is clean: stdlib-only top-level imports, no
environment read at module scope, no cycle, and it is already a declared companion of both bundles.
The neighbour is the load-bearing one.

## Blocker 2 — a reviewer that produces no verdict is recorded `completed`

`spine_terminal` answers a **survey** question with `checklist_engine.active_id`, which walks item
statuses and never looks at `consolidation`. Reproduced with a real dispatch:

```
survey  : items {i1: complete/pass, i2: complete/pass}  CONSOLIDATION: None
registry: status=completed  exit_code=0  result=null
```

The Commander is told the review is done. There is no verdict anywhere. This is the false-positive
class landing in the one role whose entire deliverable *is* the verdict — the exact failure
`reviewer/SKILL.md` calls "the single most common failure at this tier."

It is reachable, not theoretical: `--spine` accepts any checklist type, the spine-only prompt is
type-agnostic ("drive it gate by gate ... until it reports done" — a survey has no gates), and
reviewer and interrogator checklists **are** surveys.

Require `consolidation is not None` for `type == "survey"`. `checklist_engine.py` is a hard no-go
here, so the guard lives in `run_crew` for now — note the seam in a comment, because a type-aware
`is_terminal` owned by the engine is the cleaner shape.

**Same function, smaller:** `spine_terminal` returns `True` for `{}` and `{"items": []}`, directly
contradicting its own docstring — *"A missing/unparseable/malformed spine is never terminal --
absence of evidence is not evidence of completion."* Missing and unparseable files correctly return
`False`; valid-JSON-wrong-shape leaks. Fix both, each with a negative control.

## Scope

**In:** `scripts/run_crew.py`, `scripts/install_constellation.py`, `tests/`, `map/INDEX.md`.
**Out:** `checklist_engine.py`, `mcp_spine_server.py`, `settings.json`, `docs/agents/*`, all spine
templates under `skills/*/templates/`. No merge or push to `main`.

## Two things the last passes got wrong that are cheap to avoid

**Commit your work.** The sibling crew on the other branch finished its spine and left everything
uncommitted; the Admiral had to stage it by hand. Gate `x3.c2` refuses on a dirty tree.

**Regenerate the map.** That same crew shipped a stale `map/INDEX.md` and its suite went red on the
next reviewer's machine. `python -m scripts.code_map build --root .` if the entity count drifts.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **The goal is a weaker agent than you.** Prose is a liability; put it behind a check.
- **Honest null:** a measured negative is a complete deliverable.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.
- **Use the door.** `SPINE_FILE` and `SPINE_SESSION` are bound for you; `mcp__spine__*` via
  `ToolSearch`. If you reach for the engine CLI, say so and say what made it the natural move.

## Deliverable

`.agent-work/epic-559/a-spine-is-the-job/IMPLEMENTER_RESULT.md` (passes 1 and 2 are preserved as
`IMPLEMENTER_RESULT.pass1.md` / `.pass2.md`), from the implementer skill's template, including
**Workflow Feedback**.
