# Triage candidate: the launch-order Budget slot names a tier for the lane, not for the crews it dispatches

**Status:** not filed. Held to closeout per the epic's standing ruling.

**Found by:** the human, 2026-08-17, asking *"are we using sonnet crew? usage is higher than id
expect."* Measured by the Admiral in response. **Not found by any mechanism.**

**Proposed pairing:** no open issue fits cleanly — likely an **episode**, plus a concrete change
to `templates/LAUNCH_ORDER.template.md`, which is a corpus edit and therefore a human's call.

## Measured

Lane tiers, read from each lane's own gauge file — all correct:

| lane | model |
|---|---|
| D1 | `claude-opus-5` (Admiral's deliberate choice, headline lane) |
| D2, E, F, H | `claude-sonnet-5` |

Crews those lanes dispatched, read from `crew-runs.json`:

| count | model | status |
|---:|---|---|
| 8 | opus | completed |
| **6** | opus | **abandoned** (retried) |
| 1 | opus | running |

**15 spawned crew sessions, every one Opus**, all from lane D1. The other four lanes spawned
none — lane E's implementer ran on the `external` backend, in-process, at the lane's own tier.

## Cause

`run_crew.py` inherits the host's `~/.claude/settings.json` default — here `"model": "opus"` —
whenever `--model` is unset. The launch-order template's Budget section has one model-tier slot,
and it is understood as the tier of **the dispatched Commander**. Nothing in the template, and
nothing in the Admiral doctrine's "pick the least-powerful model that works", reaches the crews
that Commander goes on to dispatch.

So a lane deliberately tiered down to Sonnet silently runs an Opus subtree, and the tier decision
the Admiral believed it had made applied to exactly one process out of sixteen.

## Why the shape matters more than the cost

The Budget slot **reads as** a spend control for the whole dispatch. It is a spend control for one
process. Nothing surfaces the difference: no warning, no summary, and the registry records the
crews' model faithfully but nobody reads it during a run. The Admiral discovered this only because
a human noticed a bill.

The six abandoned-and-retried Opus sessions are the sharpest part: a retry loop at the wrong tier
costs double and is invisible from the lane's own tier setting.

## Recommended remedy shape

Two candidates, both cheap:

1. **A second Budget slot in `templates/LAUNCH_ORDER.template.md`** — "crew model tier" alongside
   "model tier" — so the Admiral has to answer the question rather than inherit an answer.
2. **`run_crew.py` defaults a crew's `--model` to the dispatching session's own model** rather
   than to the host default, so a tier decision propagates down the tree unless overridden.

The second is the mechanism-not-memory answer and fits the epic's own test — it moves work off
agents and into a mechanism. The first is the honest stopgap if the second is contentious.

**Not built here:** both are corpus/template changes outside any wave-2 lane's ownership, and the
standing ruling files no issues mid-run.
