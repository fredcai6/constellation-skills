# Handoff — cold plan critic, lens `simplicity`

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

## Your lens: **Simplicity / YAGNI — what can be deleted?**

Your lens is SIMPLICITY AND YAGNI. Your default answer is "delete it." Ask:

- Seven check kinds are proposed. The two required role specs (implementer, reviewer) use at most
  five. Which kinds earn their keep in THIS wave, and which are speculative generality? Apply the
  deletion test: delete each kind in imagination — does complexity vanish, or reappear across callers?
- Is TOML earning its keep over JSON, given every template in the corpus is already JSON and the
  generator must read JSON anyway?
- Is the pure/impure module split (two files) earning its keep over one file, or is it indirection
  bought for a test that could be written either way?
- Six gates, four of them crew gates with a cold reviewer each. Is that the right decomposition, or
  are two of them one gate? Which gate boundary proves nothing that the next one would not?
- Is the `claims_rollup` on the terminal gate redundant with the per-gate claim rendering plus the
  auto-injected postcondition — three mechanisms for one property?

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

Write `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/plan-critic-simplicity-result.md`
**before you end your turn** — that write is the delivery. Then return a short message: your lens,
your highest-ranked finding in one sentence, and that path.
