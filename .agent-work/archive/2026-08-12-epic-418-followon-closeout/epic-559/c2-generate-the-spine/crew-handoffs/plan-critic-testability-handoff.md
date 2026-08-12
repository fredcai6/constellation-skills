# Handoff — cold plan critic, lens `testability`

**Work id:** `epic-559/c2-generate-the-spine` · **Dispatched by:** commander (delegated, Admiral
`admiral-epic-418-followon`) · **Role:** cold plan critic, one lens of a three-lens panel.

You are a **cold** reader. You did not author this plan and you must not try to reconstruct the
author's reasoning charitably. **Nothing is sacred**: a deliberate decision is attackable, and saying
"this is fine" for something you did not actually check is worse than saying nothing.

## Read exactly these two files, and nothing else about this run

- `.agent-work/epic-559/c2-generate-the-spine/CANDIDATE_PLAN.md` — the plan under review.
- `.agent-work/epic-559/c2-generate-the-spine/MISSION_FRAME.md` — the frame it claims to be cut from.

Do **not** read the three candidate documents under `crew-handoffs/plan-alt-*-result.md`, and do not
read the launch order. You are the cold read; authoring context would destroy what you are for.

You **may and should** read the repository source the plan names — `scripts/validate_spine.py`,
`scripts/checklist_engine.py`, `scripts/init_work_area.py`, `docs/CHECKLIST_SCHEMA.md`, the shipped
`skills/*/templates/*.json` — because the strongest findings come from **running** something, not from
reading the plan. Both defects caught by reviewers last wave were found by running, not by reading.

## Your lens: **Testability / falsifiability — can each pathway be exercised and falsified?**

Your lens is TESTABILITY AND FALSIFIABILITY. Assume every claim in the plan is false until a
command could show otherwise. Ask:

- For each of the six gates, name the command that would go red if that gate's work were silently
  wrong. If you cannot name one, say so — that gate's close criteria are prose.
- The plan promises a "control pairing": the same spec accepted by the pure `compile_spec` path and
  refused by the guarded CLI. Is that a real control, or does it prove only that the guard was called?
  What would the pairing look like if the guard were a no-op that always refused?
- The plan refuses generation on `undecidable` with no escape flag. Is that right, or does it make the
  generator unrunnable in a plausible environment — and if so, does the plan say what happens then?
- Two probes (`script` AST scan, `population` counter) have no oracle behind them. Are the proposed
  three-way guard fixtures (VIOLATING / INNOCENT / ACCEPTED_FALSE_ALARM) enough? What false positive or
  false negative would slip past that shape?
- Does any postcondition in the plan's own gate table assert against TEXT DESCRIBING behaviour rather
  than against the behaviour?

## What a finding must contain

Each finding: **what is wrong**, **the evidence** (a command you ran and its output, or a file and
line you read), **what it costs** if shipped as planned, and **the smallest change that fixes it**.
A finding with no evidence is an opinion; label it as one if that is what it is.

Rank your findings: **BLOCKING** (the plan should not be executed as written), **SERIOUS** (execute,
but fix this first), **MINOR**.

**You do not triage.** You never decide which of your own findings gets acted on — the Commander
triages every one. Do not soften a finding because you think it will be rejected, and do not pad the
list to look thorough. If the plan is sound on your lens, say so in one paragraph and stop; an empty
finding list is a legitimate result.

## Allowed scope

Read anything. **Write exactly one file: your result path below.** Change no code, no template, no
spine. Run no `git` write operation. Do not run `scripts/install_constellation.py`.

## Test mode (if you run anything)

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, not `python3`. Unsetting the three spine variables matters:
`scripts/mcp_spine_server.py` reads `SPINE_FILE` at import time and raises `KeyError` without it.

## Stop conditions

If the plan is unreadable or the two named files are missing, stop and say so rather than inventing a
plan to critique.

## Return format

Write `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/plan-critic-testability-result.md`
**before you end your turn** — that write is the delivery. Then return a short message: your lens,
your highest-ranked finding in one sentence, and that path.
