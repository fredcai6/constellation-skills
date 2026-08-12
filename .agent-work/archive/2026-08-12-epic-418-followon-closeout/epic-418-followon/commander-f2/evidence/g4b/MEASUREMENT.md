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

## Three arms, and what each one actually measured

| Arm | Role driven | Skill corpus the agent loaded | Door offered? | Door calls | CLI engine calls | Verdict |
|---|---|---|---|---|---|---|
| 1 | implementer | `~/.claude/skills/constellation-implementer` (pre-g4a) | connected, 7 tools | **0** | 21 | REFUSED |
| 2 | implementer | `~/.claude/skills/constellation-implementer` (pre-g4a) — **the same corpus arm 1 loaded** | connected, 7 tools | **0** | 20 | REFUSED |
| 3 | workbench, a role that **owns its process's bound spine** | `~/.claude/skills/constellation-workbench` (pre-g4a) | connected, 7 tools | **9** | **0** | **ACCEPTED** |

Every arm had `{"name": "spine", "status": "connected"}` at session init with all 7
`mcp__spine__*` tools in the offered tool list. That much is measured in all three: the door
was there.

## Correction — arm 2 duplicated arm 1's condition

Arm 2 was launched and reported as "implementer with **freshly installed** skills carrying
the door". That description is wrong. The arms' own records say so:

* Arms 1 and 2 both loaded `~/.claude/skills/constellation-implementer`. Arm 3 loaded
  `~/.claude/skills/constellation-workbench`.
* `~/.claude/skills/CORPUS.json` records `source_commit: a1eab1f1` (2026-08-09), which is
  **before g4a** (`e569350c`, 2026-08-10).
* Files under `~/.claude/skills/` naming the door: **0**.
* A fresh install did run, at 02:11:45 — into the **project-local** `.claude/skills/`,
  which no arm loaded.

**Arm 2 is arm 1 rerun.** It is not an independent second negative; it is one condition
observed twice. Nothing below is allowed to count it as two.

**The block quote that stood here has been deleted, not reworded.** It introduced a sentence
— *"…you share the parent's MCP scope wholesale…"* — with "Reading the freshly installed
instruction shows why", and concluded from it that the agent had obeyed correct doctrine.
`grep -c "share the parent"` returns **0** across all three arms' records: **no agent saw
that sentence.** The conclusion was unsupported by the evidence cited for it, so the claim
is withdrawn. No substitute quotation is offered, because the corpus these agents read
carried no door instruction at all.

The arm-design error that remains true, and is mine: arms 1 and 2 drove the **implementer**,
which by g1's ruling is an in-session dispatched crew member and does not own the process's
bound spine — so it was never the role that could satisfy this criterion. That is a
statement about how the arms were chosen. It is not a statement about what either agent read
or why it went to the CLI, which this run did not measure.

## What this run measured, and what it did not

**All three arms loaded the pre-g4a corpus.** Arm 3 used the door anyway: its record shows
it reaching the tools through `ToolSearch` against the `--allowedTools` list its launcher
passed, not through a role instruction. **So g4a's role-instruction edits were not in the
causal path of any arm.**

* **Criterion 2 — MET, on arm 3.** The basis, stated precisely: *an agent that owns its
  bound spine and is offered the door's tools uses them.* 9 door calls, 0 CLI engine
  invocations, reached `DONE`, released its lease. That is what was measured, and it holds
  without reference to any instruction edit.
* **Criterion 1's causal contribution to adoption — UNMEASURED.** No arm read the g4a
  instructions, so this run says nothing about whether naming the door as the default in a
  role instruction *causes* an agent to use it. **UNMEASURED is not a negative.** It is a
  condition no arm created; there is no reading here to report either way, and writing one
  down as a negative is the exact error this epic exists to stop. Criterion 1's own claim —
  that the instructions now name the door as the default with the CLI kept as the fallback —
  is verified against the repo source by `tests/test_mcp_adoption.py`, and that verification
  stands on its own, independent of this measurement.

Arms 1 and 2 stay in the record for the one thing they do establish: the door was connected
and offered in a run that did not use it, so arm 3's exclusive door use is not an artifact
of the door being the only thing available. Being one condition rather than two does not
change that.

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
