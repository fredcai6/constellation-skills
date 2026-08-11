# Implementer handoff — C1: make a check that cannot fail unauthorable

**Work id:** `epic-559/c1-spine-lint` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c1-spine-lint` (branch `epic-559/c1-spine-lint`, off `main`@`90b39e2b`)
**Your spine:** `.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_PLAN.json` — four gates, every postcondition a real command. The Admiral ran them all before dispatching you: every substantive one is **red**. Drive it gate by gate.

## Task

Write `scripts/validate_spine.py`: a checker that reads a spine or a spine template and refuses it,
with a specific message per fault, when the file is malformed or carries a check that cannot fail.

Nothing like this exists — `ls scripts/verify_*.py` returns twenty verifiers and none of them looks
at a spine's own checks.

## Why, with the evidence

This repo keeps authoring checks that cannot fail, and it keeps catching them by hand, late, or not
at all.

- **`check: null` everywhere.** Across 113 archived spines, zero have every postcondition null.
  The Admiral authored five such spines during this epic. So it is authorable, it is real, and it
  is not caught by anything.
- **A selector that collects nothing.** `episodes/active/issue-456-001.md` records its own
  diagnosis: *"the third commander to produce checks that cannot fail from the same templates."*
  The mechanism there was a distinct, gate-specific `pytest -k` selector that collected **zero
  tests** — satisfying a one-proof-per-gate rule while being exactly as vacuous as `check: null`.
- **#562.** A shipped Commander gate stated "IMPLEMENTER_RESULT returned with no unresolved
  blockers" and checked only that an `implementer-result` of some type arrived. The engine's
  `all(... for k, v in want.items())` over an empty `match` is vacuously true, so the gate was
  satisfied by a result reporting the work blocked. Fixed this week; it had shipped in every
  Commander execute plan.
- **A placeholder that never resolved.** `REVIEW_SURVEY.template.json` shipped a check command
  containing `<fowler-pass-record-path>`, a token the resolver does not handle, so the command could
  not run at all. A cold reviewer hit it live. A census had marked that row "already converted, no
  action" — it checked that a check was *present*, never that it *runs*.
- **The wrong top-level key.** The Admiral shipped two spines keyed `gates` where the engine reads
  `items`. `checklist_engine` raised a bare `KeyError` on the first `current` call, before any rail
  text could print, and both crews had to repair the file before they could start.

Every one of those is mechanically detectable. That is your job.

## The four falsifiability faults (gate `g2`)

Each needs its own message — a checker that says "invalid" teaches nothing.

1. A gate whose postconditions are **all** `check: null`.
2. A `command` check whose pytest selector **collects zero tests**.
3. An `artifact` check with **no `match`** whose statement asserts a property rather than mere
   arrival. Note the shipped file gets this right twice and wrong once, which is how you can tell
   the difference: `g1-review.c1` claims only "REVIEW_RESULT returned" and is honest with a bare
   artifact check; `g1-integrate.c2` claims "reviewer verdict is APPROVE" and carries
   `match: {"verdict": "APPROVE"}`.
4. A command check whose text still holds an unresolved `<placeholder>` after instantiation.

**Faults 3 and 4 need judgment about what counts**, so build the repo's proven three-way fixture set
for each: `VIOLATING` cases the lint must catch, `INNOCENT` cases it must not flag, and `ACCEPTED`
exceptions named explicitly. `tests/test_mcp_adoption.py::_cli_only_verb_violations` is the pattern
and it is good — copy its structure, do not invent a new one.

Fault 3 in particular is a heuristic over English. Be conservative: a false positive that refuses a
legitimate spine is worse than a miss, because it blocks real runs. Say in your result where you
drew the line.

## Gate `g3` measures, it does not fix

Run the checker over every gated-or-survey checklist template the repo ships. **Enumerate the
population yourself from each file's own `type` field.** Do not trust the Template set table in
`skills/workbench/references/checklist-engine.md`: a cold reviewer counted twelve real checklists
against that table's six, and two separate crews each picked a different, non-overlapping six from
it in good faith.

If a shipped template fails your lint, **that is the finding** — write it down, fix nothing. A later
wave decides what to do about it. And assert how many templates the sweep examined, so a broken
discovery step cannot read as a clean pass.

## Where this is going, so you build the right shape

A later wave generates spines from a filled-in spec file, so no agent hand-writes spine JSON again.
Your checker is what that generator will refuse to emit past. So make it importable as a module with
a clean function that takes a parsed spine and returns a list of faults — not only a CLI. The CLI
should be a thin wrapper over it.

## Scope

**In:** `scripts/validate_spine.py`, `tests/test_validate_spine.py`, fixtures, `map/INDEX.md`.

**Out — hard no-gos:** `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
`scripts/run_crew.py`, `skills/implementer/*`, `skills/reviewer/SKILL.md` (sibling crews own those
right now), **all spine templates** — `g3` measures them, it does not touch them — `settings.json`,
`docs/agents/*`. No merge or push to `main`.

## Two things that cost your predecessors a rework round

**Commit before you finish** — gate `g4.c2` refuses on a dirty tree. **Rebuild the map** with
`python -m scripts.code_map build --root .`; you are adding modules, so it will drift, and a stale
map turned the suite red for someone else this week.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **The goal is a weaker agent than you.** Prose is a liability; put it behind a check.
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** an independent reviewer will check this.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.
- **Use the door.** `SPINE_FILE` and `SPINE_SESSION` are bound for you; find `mcp__spine__*` via
  `ToolSearch`. It covers all 18 engine verbs. If you reach for the CLI, say so and say what made it
  the natural move.

## Deliverable

`.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_RESULT.md`, from the implementer skill's template,
including its **Workflow Feedback** section.
