# Handoff — cold plan critic, lens `intent-fit`

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

## Your lens: **Intent-fit — does this design serve the stated point?**

Your lens is INTENT-FIT. The stated point is in the mission frame and the plan's own opening: a
check is a shell string typed from memory, and a wrong one does not announce itself. Ask, relentlessly:

- Does this design actually remove that failure mode, or does it relocate it? Where exactly does an
  author's mistake still reach JSON unchallenged?
- The launch order's second non-optional property is the human's verbatim rule: *"as a general rule,
  judgement should be highlighted and brought to the higher level. greater claim requires greater
  review."* Does the auto-injected escalation postcondition actually cause greater review, or does it
  only cause one more artifact to be attached by the same agent that made the claim? Who attaches a
  `user-decision` in practice, and is that a higher tier or the same one?
- The first non-optional property is that every gate carries a *place to record beliefs, concerns and
  open questions*, and that a crew with something to hand back has a gate to hand it back at. Does a
  rendered `directives.handback` block give a crew somewhere to actually GO, or is it a label on a
  door with no room behind it? What does a crew literally do with it?
- Is anything in the plan a check that cannot fail — identical output in the healthy and the defective
  world?

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

Write `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/plan-critic-intent-fit-result.md`
**before you end your turn** — that write is the delivery. Then return a short message: your lens,
your highest-ranked finding in one sentence, and that path.
