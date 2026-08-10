# g4b — acceptance measurement (#542 criterion 2)

**Claim under test:** *a real dispatched agent drives a real role spine to done through the
door alone, measured from its own call record.*

Counted from the driving agent's own `--output-format stream-json` record, never the server
log (`decision:count-from-the-call-record`). Scored with F's archived `score_arm.py`,
reused rather than reinvented. `assert_acceptance.py` refuses unless **both**
`reached_done` **and** zero CLI engine invocations — because `reached_done` alone is
one-sided and would pass an agent that hit a wall on a door tool, dropped to the CLI, and
finished.

**Bash was deliberately ALLOWED in every arm.** F's own MCP arm withheld it, which made
"zero CLI invocations" true by construction. Adoption is a claim about what an agent
*chooses* when both doors are open, so all three arms opened both.

## Three arms, and the two negatives are the control

| Arm | Role driven | Door offered? | Door calls | CLI engine calls | Verdict |
|---|---|---|---|---|---|
| 1 | implementer, **stale** installed skills | connected, 7 tools | **0** | 21 | REFUSED |
| 2 | implementer, **freshly installed** skills carrying the door | connected, 7 tools | **0** | 20 | REFUSED |
| 3 | a role that **owns its process's bound spine** (workbench) | connected, 7 tools | **9** | **0** | **ACCEPTED** |

Every arm had `{"name": "spine", "status": "connected"}` at session init with all 7
`mcp__spine__*` tools in the offered tool list. So arms 1 and 2 are **measured negatives,
not unmeasured conditions** — the door was there and went unused.

## Why arms 1 and 2 went to the CLI, measured rather than guessed

Arm 1's agent loaded the **installed** `constellation-implementer`, which at that moment
had **zero** door mentions — the g4a edits were in the repo `skills/` source, and a
dispatched agent reads the installed corpus. That is the mechanism, and it is why criterion
3 (the installer) is not cosmetic.

Arm 2 removed that explanation by installing first, and **still measured zero door calls**.
Reading the freshly installed instruction shows why, and it is not a defect:

> *"as an in-session dispatched crew member you almost always do NOT own it — you share the
> parent's MCP scope wholesale, and the door stays bound to the Commander's `spine.json`,
> never to your own `IMPLEMENTER_PLAN.json` — so drive your own plan through the CLI
> fallback instead"*

**The agent obeyed correct doctrine.** g1 ruled that a seam below its container's separating
granularity must not take identity from it, and g4a wrote that ruling into the implementer
role. The implementer is precisely the role the fleet now tells to use the CLI.

**So arms 1 and 2 measured the wrong role, and that error was mine.** It is recorded rather
than deleted because the two negatives are what make arm 3 meaningful: they show the door
being available and declined, so arm 3's exclusive use is a choice and not an artifact of
the door being the only thing on offer.

## Arm 3 — the accepted run

```
reached_done:            true
invocation_attempts:     9
mcp_invocations:         9
cli_engine_invocations:  0
shape_errors:            0
absorbable_fumbles:      0
```

A top-level dispatched agent, owning its own bound spine, drove a real shipped role template
(`skills/workbench/templates/DEFAULT.template.json`) to `DONE: no open items` using the door
and nothing else, and released its lease.

## Door-own friction on the accepted run: ZERO

**Reported as measured.** `zero-is-a-result`: no friction was manufactured to demonstrate
g2's capture, and zero is **not** read as proof the capture works. What proves the capture
can score is g2's seeded-rejection control and its dedup mutation, not this run. F likewise
measured zero malformed calls in both DC5 arms, so zero is the expected reading rather than
a surprise.

## The three adoption counts, re-measured

| # | Count | Wave boundary | Now |
|---|---|---|---|
| 1 | files under `skills/` referencing the door's tools | 0 | **13** |
| 2 | MCP references in `scripts/install_constellation.py` | 0 | **0 — UNCHANGED** |
| 3 | agents actually driving through it | 0 | **1, measured** |

Count 2 is unchanged because **g3 was deferred by Admiral ruling**. It is reported as an
open criterion, not as a pass.

## Verb coverage, checked before dispatching rather than discovered after

The happy path needs `claim`, `current`, `start`, `attest`, `advance`, `release` — all six
door-covered. None of the five CLI-only verbs (`skip`, `reopen`, `append`, `amend`,
`flag-candidate`) is on the path, so the claim was reachable by construction before any
agent was launched.
