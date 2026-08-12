# Cold reviewer handoff — C1: the falsifiability lint

**Work id:** `epic-559/c1-spine-lint` · **Gate:** `g5-review` · **Role:** reviewer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c1-spine-lint` (branch `epic-559/c1-spine-lint`)
**Under review:** `303b7f19` and `9aa094dd` against `main`@`90b39e2b`, plus `IMPLEMENTER_RESULT.md`.
**Your spine:** `.agent-work/epic-559/c1-spine-lint/REVIEW_SURVEY.json` — drive it item by item.

You are **cold**. You did not plan this and you are not here to agree with it.

## What was built

`scripts/validate_spine.py` — a checker that refuses a spine or template that the engine cannot read,
or that carries a check which cannot fail. 484 lines of production, 539 of tests, plus fixtures.

Four falsifiability faults, each with its own message: a gate where every postcondition is
`check: null`; a `command` check whose pytest selector collects zero tests; an `artifact` check with
no `match` whose statement asserts a property rather than mere arrival; and a command check still
holding an unresolved `<placeholder>`.

Every one of those has really shipped here. The `match` fault is #562, which sat in every Commander
execute plan. The zero-collecting selector is `episodes/active/issue-456-001.md`, whose own diagnosis
reads *"the third commander to produce checks that cannot fail from the same templates."* The
Admiral authored five all-null spines during this epic.

## The question that decides the verdict

**How many legitimate spines does this lint refuse?**

A lint that refuses good spines is worse than no lint. It blocks every real run, and the first thing
anyone does is switch it off. Fault 3 is a heuristic over English — it reads a statement and decides
whether it asserts a property — so that is where false positives live.

Run it over everything: the shipped templates, and every archived spine under `.agent-work/` across
the repo. There are well over a hundred. Report the refusal rate, then **read a sample of the
refusals by hand** and decide one at a time whether each is a true fault or a false positive.

If it refuses spines that are fine, that is a `BLOCK`, and it is the most valuable thing you can
find here. Item `v1` owns it.

## The rest

`v2` — break a shipped template four ways and confirm each fault is caught with a message that names
it specifically. A checker that says only "invalid" teaches nothing. Confirm the unmutated original
passes clean.

`v3` — two checks the Admiral authored this week that could never *pass*: one with an unquoted
`-k Door or Tie or Registry` selector the shell splits into something else, and one whose `python -c`
body imports `mcp_spine_server`, which reads `SPINE_FILE` at import and raises without it. That is a
distinct fault class from a check that cannot fail — safe in direction, useless and blocking in
effect. Run the lint against both, say whether it catches them, and give your judgment on whether it
should. **An argued no is a fine answer**; this is a scope question, not a defect.

`v4` — a later wave generates spines from a spec file and refuses to emit anything this lint rejects,
so check the seam: a clean function over a parsed spine returning structured faults, a CLI that is a
thin wrapper, and an import with no side effects and no environment requirement.

`v5` — verify the corpus count yourself. The crew was told to enumerate from each file's own `type`
field rather than trust the Template set table in `checklist-engine.md`, because a reviewer counted
twelve real checklists against that table's six.

Standard items `r1`–`r6` still apply.

## What the Admiral already verified — do not redo

Every postcondition on the crew's own spine passes when run independently; the tree is committed;
the suite is green; the map was rebuilt. Note the crew corrected one of the Admiral's own broken
checks through the engine's `amend` verb with a proper delta rather than hand-editing its spine —
that is the sanctioned path and it left the delta behind as a record.

## Hard no-gos the change was under

`checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `skills/implementer/*`,
`skills/reviewer/SKILL.md`, **all spine templates** (gate `g3` measures them, it does not touch
them), `settings.json`, `docs/agents/*`. No push to `main`. Confirm each.

## Test mode

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`

Use `python`, not `python3`.

## Drive your own spine through the door

`SPINE_FILE` and `SPINE_SESSION` are bound for you; find `mcp__spine__*` via `ToolSearch`. The door
covers all 18 verbs. If you reach for the CLI, say so and say what made it the natural move.

**Do not dispatch a subagent and then end your turn to wait for it.** A crew died that way tonight —
its entire final output was "I'll pause here and wait for the background dispatch to finish."
Nothing resumes a headless crew. If you start anything in the background, poll it inside your turn.

## Verdict

`APPROVE` or `BLOCK`, with the evidence you personally ran. An honest partial is acceptable; a silent
gap is not. Write to `.agent-work/epic-559/c1-spine-lint/REVIEWER_RESULT.md`, including Workflow
Feedback, before ending your turn — that write is the delivery.
