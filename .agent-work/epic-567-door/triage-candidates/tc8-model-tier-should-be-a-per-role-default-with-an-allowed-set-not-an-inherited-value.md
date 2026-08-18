# Triage candidate: model tier should be a per-role default with an allowed set, not an inherited value

**Status:** not filed. Held to closeout per the epic's standing ruling.

**Found by:** the human, 2026-08-17 — first by noticing the spend (*"are we using sonnet crew?
usage is higher than id expect"*), then by **rejecting the Admiral's proposed fix** and stating the
design he actually wants. Both halves are his; the measurement below is the Admiral's.

**Proposed disposition:** **episode** for the incident, plus a design change to
`run_crew.py` and `templates/LAUNCH_ORDER.template.md`. Both are corpus edits and therefore a
human's call.

## What happened

Lane tiers, read from each lane's own gauge — all as intended:

| lane | model |
|---|---|
| D1 | `claude-opus-5` (deliberate: headline lane) |
| D2, E, F, H | `claude-sonnet-5` |

Crews those lanes dispatched, read from `crew-runs.json`:

| count | model | status |
|---:|---|---|
| 8 | opus | completed |
| **6** | opus | **abandoned** (retried) |
| 1 | opus | running |

**15 spawned crew sessions, every one Opus**, all from lane D1. `run_crew.py` inherits the host's
`~/.claude/settings.json` default (`"model": "opus"`) whenever `--model` is unset, and the
launch-order Budget slot names a tier for **the dispatched Commander only**. So a lane deliberately
tiered to Sonnet ran an Opus subtree, and the tier decision applied to one process in sixteen.

## The Admiral's first proposal, and why it is wrong

The Admiral proposed: *default a crew's model to the dispatching session's own model.*

**The human rejected it, correctly:**

> wouldn't defaulting a model to its dispatcher lead to opus commanders defaulting to opus crews?

Exactly so. Inheritance does not fix the defect, it launders it — an Opus Admiral would dispatch
Opus Commanders which would dispatch Opus implementers, and every one of those escalations would
look deliberate because it was "inherited". The bug is not *which* value is inherited. It is that a
tier is **inherited at all**, when it should be a property of the **role**.

## What the human wants instead

> i'd really like to get to a world where we breakdown tasks enough that commanders are sonnet and
> crews are haiku or local. we're not there yet, but I really want to have a default expectation per
> role and an allowed choices per role that the dispatcher can choose from with reason

Three separable requirements:

1. **A default expectation per role.** Each role — admiral, commander, implementer, reviewer,
   critic, interrogator, cartographer — carries its own default tier. Unset resolves to *the role's*
   default, never to the host's `settings.json`. **Fail closed toward the cheaper tier**, since the
   failure this candidate records was a silent escalation.
2. **An allowed set per role.** A dispatcher may choose only within that role's permitted tiers.
   This bounds the mistake in both directions: no accidental Opus implementer, and no reckless Haiku
   Commander on design work.
3. **A reason, recorded, whenever the dispatcher deviates from the default.** The registry already
   records each crew's model faithfully; adding the reason turns it into a spend trail that can be
   read after the fact — which is precisely what was missing here, since nothing surfaced the
   escalation during the run.

## Why the shape matters more than the numbers

The Budget slot **reads as** a spend control for the whole dispatch. It is a spend control for one
process. A per-role table with an allowed set makes the direction of travel — *commanders to Sonnet,
crews to Haiku or local* — **a one-line change in one table**, instead of an audit of every launch
order the corpus will ever produce. That is the human's own test for a trade: it moves the work off
agents and into a mechanism.

The six abandoned-and-retried Opus sessions are the sharpest illustration. A retry loop at the wrong
tier costs double, and it is invisible from the lane's own tier setting.

## Sketch, not a design

```
ROLE_TIERS = {
    "admiral":     {"default": "opus",   "allowed": {"opus", "sonnet"}},
    "commander":   {"default": "sonnet", "allowed": {"opus", "sonnet"}},
    "implementer": {"default": "haiku",  "allowed": {"sonnet", "haiku"}},
    "reviewer":    {"default": "sonnet", "allowed": {"sonnet", "haiku"}},
    ...
}
```

- `run_crew.py` resolves `--model` from `ROLE_TIERS[role]["default"]` when unset — **never** from
  the host default.
- A `--model` outside `allowed` is **refused by name**, the way the duplicate-crew guard refuses.
- A `--model` inside `allowed` but not the default **requires `--model-reason`**, recorded in the
  registry entry beside the model.
- The table's values above are illustrative. The human's stated target is commanders at Sonnet and
  crews at Haiku or local, and explicitly *"we're not there yet"* — so the table should ship at
  today's honest tiers and move as task decomposition improves. **The point is that moving it is
  one edit.**

## Evidence this is not hypothetical

This epic's own final task — sweeping four occurrences in two files, with an existing guard as the
acceptance test — was run by a **Sonnet** commander with crews pinned to Sonnet, after the human's
ruling, and completed in minutes. The same lane's earlier gates ran an Opus commander with 15 Opus
crews. Nothing about the work required the difference; only the absence of a role table did.
