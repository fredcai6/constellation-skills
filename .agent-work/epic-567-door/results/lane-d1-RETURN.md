# Lane D1 — `STATUS: INCOMPLETE · REFRESH REQUESTED AT execute`

> **This is not a completion return.** The lane reached the context HARD band with `init` →
> `plan` complete and `execute` **pending, never started**. A `refresh-request` (`e-execute-1`)
> is filed against `execute`. Per reach-up doctrine the Admiral relaunches a **fresh** Commander
> that cold-starts from this spine's `current` (`DIGEST:` + the `execute` imperative) — same job
> file, different agent. **No deliverable of #559 has landed yet: the sweep has not run and the
> guard does not exist.**
>
> Resume state: `.agent-work/567-d1/STATE_NOTE.md`. Plan frozen at `bd677d7c`.

## 1. Verdict

**Incomplete — handed off mid-run, with the lane's hard analytical work done and committed.**
What exists is the plan and the measurements it rests on; what does not exist is the sweep, the
guard, the specs work, and the #596/#526 dispositions.

I did not close `execute` to hand off. The engine's context advisory instructed
`start execute` → `advance execute --why` → stop, but `execute`'s postconditions are genuinely
unmet, and the launch order names that exact move as the infinite-handoff failure: each
successor arrives over the band, reads the same line, hands off again, and no deliverable is
ever written. `execute` is left **pending** — no gate is open, so the Stop hook is satisfied.

## 2. The sweep table — measured at `f05a3d78`, nothing swept yet

Baseline **matches the launch order exactly**: 15 `CLI fallback` clauses (13 mine, 2 lane D2's),
11 `<engine>` tokens across 7 files. Verified by command, not by memory.

Census refinement that matters for the guard: the clause has **three surface forms** —
`CLI fallback:` ×10, `CLI fallback,` ×4, `CLI fallback ` ×1. A colon-only pattern misses a third
of them. (A design candidate that pinned only the colon form would have shipped a guard blind to
5 of 15 occurrences.)

### The 13 clauses, and the split the measurement forced

| # | Site | Kind | Planned disposition |
|---|---|---|---|
| 1 | `skills/admiral/templates/ADMIRAL_SPINE.template.json:10` | bound-spine | sweep, name the real path |
| 2 | `skills/admiral/templates/ADMIRAL_SPINE.template.json:52` | bound-spine | sweep |
| 3 | `skills/charter/SKILL.md:12` | bound-spine | sweep |
| 4 | `skills/commander/references/commander-core.md:127` | bound-spine | sweep |
| 5 | `skills/commander/templates/COMMANDER_SPINE.template.json:10` | bound-spine | sweep |
| 6 | `skills/commander/templates/COMMANDER_SPINE.template.json:49` | bound-spine | sweep |
| 7 | `skills/commander/templates/COMMANDER_SPINE.template.json:123` | bound-spine | sweep |
| 8 | `skills/explorer/SKILL.md:31` | bound-spine | sweep |
| 9 | `skills/explorer/templates/EXPLORER_SPINE.template.json:12` | bound-spine | sweep |
| 10 | `skills/explorer/templates/EXPLORER_SPINE.template.json:78` | bound-spine | sweep |
| 11 | `skills/interrogator/SKILL.md:26` | **second-checklist** | reword to the measured truth |
| 12 | `skills/write-a-skill/templates/gated-engine-SKILL.template.md:15` | **second-checklist** | reword |
| 13 | `skills/write-a-skill/templates/survey-SKILL.template.md:11` | **second-checklist** | reword |

Not mine: `skills/workbench/references/checklist-engine.md:5`, `skills/workbench/SKILL.md:37`
(lane D2, which deletes those files outright).

### All 11 `<engine>` sites classified, including the two that survive

| # | Site | Class |
|---|---|---|
| 1 | `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` | **SURVIVES** — historical plan record. Read it: it is a dated record of the delegated-commander design, not instruction. Editing it to make a count come out right would falsify the record |
| 2 | `scripts/init_work_area.py:24` | **SURVIVES** — a comment naming `<engine>` as an example of a token the resolver *deliberately never resolves*. Deleting it would delete the documentation of the convention itself |
| 3–4 | `skills/admiral/templates/ADMIRAL_SPINE.template.json:10,52` | target |
| 5 | `skills/commander/references/commander-core.md:127` | target |
| 6 | `skills/commander/references/crew-dispatch.md:35` | target — arrived in **wave 1** via lane C; the target set moved under this epic |
| 7–9 | `skills/commander/templates/COMMANDER_SPINE.template.json:10,49,123` | target |
| 10–11 | `skills/explorer/templates/EXPLORER_SPINE.template.json:12,78` | target |

## 3. The evidence the launch order asked me to carry

**The target reached this Commander in the first thing it read.** My own spine's `init`
imperative, verbatim from `spine_status`:

> …this is your own spine…, so the door needs no session id argument. **CLI fallback:
> `<engine> claim --session-id commander-567-d1 --claimed-by commander --worktree .`** … From
> here on, pass `--session-id commander-567-d1` on every mutating CLI call against this spine.

Note the asymmetry: `init_work_area.py` resolved `<commander-session-id>` → `commander-567-d1`
but left `<engine>` unresolved, so the agent is handed a command line it cannot run.

**And the door worked.** Every gate of this run was driven through the MCP verbs — `spine_lease`,
`spine_status`, `spine_start`, `spine_evidence`, `spine_advance` — with **no CLI invocation at
any point**. The epic's definition-of-done item "a dispatched crew drives its own spine through
the door end to end" is satisfied for `init` → `plan`.

## 4. THE FINDING: the regrowth has a mechanism, and it is a test

`tests/test_mcp_adoption.py` **mandates the text #559 deletes.**
`TestTier1ImperativeFields::test_field_still_carries_cli_fallback` asserts each of 7 imperative
fields still carries its exact CLI command line, failing with:

> *"lost its exact CLI command line … the CLI door must stay, never be removed or discouraged"*

**That is why the text has been deleted twice and grown back twice.** A lane deleted the clauses,
the suite went red on a test whose failure message says the CLI must stay, and the lane restored
the text believing it had broken a rule. The deletion was never the hard part.

Measured blast radius: **nine** mandating assertions, not one — `:737`, `:784`, `:834`, `:950`,
`:954`, `:1132`, `:1149`, and `TestCLIStaysAvailableNotDeprecated`'s `:1324` and `:1345`.
A sweep that inverted only the obvious one would have left eight red.

**The counterweight, also in-tree:** `tests/test_mcp_adoption.py:838`
(`TestTier2SpineAlreadyBoundForDispatchedCrews`) already asserts *absence* for two files and
quotes the human verbatim — *"the agents should not know about the CLI. period."* **The guard is
a generalization of an existing precedent from 2 files to the whole corpus, not a new
invention.** That is a materially stronger thing to land, and it is the shape I planned.

## 5. Floats to the Admiral — three, none blocking

### F-1. The door provably cannot reach a *second checklist* — bears on `decision:complete-sweep`

Measured in a **fresh process** with explicit paths (per the Dogfooding rule), on two
engine-materialized spines:

| Step | Result |
|---|---|
| `spine_lease claim` on own spine | OK |
| `spine_bind` to a second checklist, **lease held** | **REFUSED** — *"this door still holds an active lease … one door drives one spine at a time. Rebinding this door now would leave that lease held by nobody."* |
| release lease, then `spine_bind` | succeeds |

The escape is unavailable to the agents in question: `COMMANDER_SPINE.archive` requires the lease
to "cover every journaled action", so a Commander that released its lease to bind `execute.json`
fails its own closeout.

So for a Commander's `execute.json`, an Interrogator's `interrogation.json`, and an in-session
crew's own plan, **the CLI is the only path** — and "CLI *fallback*" is the wrong word, because a
fallback implies a working primary.

**Why this is not relitigating the human's ruling.** The ruling was *"sweep all **possible** now"*,
and it overrode an Admiral recommendation about the **dispatched-crew** path — which the
re-measurement correctly showed *does* have a door (a crew launched by
`run_crew.py --backend cli --spine` is its own process, bound to its own spine). My finding is a
**different** path the ruling never considered. I therefore still sweep all 13 — **no `CLI
fallback` clause survives anywhere in my files** — but reword those 3 to state the measured truth
rather than delete an agent's only path, which would violate "fail visibly; no hidden fallback."
Replacement wording is explicitly my latitude. Flagging because it touches a `settled/human` line.

### F-2. Ownership gap: `tests/test_mcp_adoption.py` belongs to no lane

It is in **no** lane's sole-writer list and **no** lane's fence table, and **the sweep is
impossible without editing it** (it mandates the text). Same for
`tests/data/store_mentions.approved.txt`, which holds verbatim copies of two imperatives under
edit. No other lane owns them, so there is no collision risk. Proceeding; flagging per "anything
that fits no class above — float, with one line on why."

### F-3. The ruling has no durable home

The guard's failure message should tell a future agent why the text must not return. But this
lane may not write `docs/agents/*` (human's call) and files no issue, and `.agent-work/` is
scratch — so any pointer dangles. **Mitigation taken:** the guard quotes the ruling *verbatim*,
so it is self-contained and deleting the guard destroys the reason with it. **Ask:** whether the
ruling should get a durable home in `docs/agents/ORCHESTRATOR_CONTEXT.md`, which only the human
can authorize.

## 6. Not yet done

`specs/*.spine.toml` door vocabulary (measured: **zero** door mentions today; both specs also set
`config_ref = docs/agents/engine-config.json`, **which does not exist in this repo**), #596, #526,
the sweep itself, the guard, the red-proof, and the full-suite run. All are planned as gates
g1–g5 in `.agent-work/567-d1/execute.json`.

## 7. Touched paths

Only this lane's own work area, plus this file:

- `.agent-work/567-d1/{notes-1.md, MISSION_FRAME.md, decision-anchors.md, execute.json, STATE_NOTE.md, map-orientation.json}`
- `.agent-work/567-d1/plan-rigor/` (briefs, two design candidates, the cold critique, `CONVERGENCE.md`)
- `.agent-work/epic-567-door/results/lane-d1-RETURN.md` (this file — my own results file, the one exception to the Admiral's fence)

**No source file has been modified.** Nothing another lane owns was touched.

## 8. Map impact

No indexed source touched yet. Separately: **this repo has no architecture map at all** —
`map_orient` returns `DEGRADED-UNPARSEABLE` (`docs/architecture` absent, `map/INDEX.md` carries no
citable anchor id, `map/ids.jsonl` **empty**), so `map_orient` can never RESOLVE here for *any*
lane. Discharged with five hash-pinned substitutes; escalated, not acted on, since `map/INDEX.md`
is Admiral-owned.

## 9. Triage candidates

Staged as files, none filed as issues: the `verify-frame` vs decision-grading conflict (under
DEGRADED the frame check refuses the very `decision:<id>` bullets doctrine requires); `map/ids.jsonl`
empty; `docs/agents/engine-config.json` referenced by both specs and by `execute.json` but absent;
`docs/agents/GLOSSARY.md` has no entry for **door**, the term this epic makes load-bearing;
per-task `anchors` duplication in `execute.json`.

## 10. Workflow feedback, including my own mistakes

**My mistakes.**
1. **I authored the defect this epic is about.** My first gate plan had four world-facing
   postconditions and the cold critic proved **three could not fail** — a `| tail -5` swallowing
   pytest's exit code (so the gate delivering #559 would close green when the guard *did not
   exist*), a `test -d` that passed before the run began, and a specificity proof over
   directories the guard structurally cannot read. A fourth was passable only by violating a
   fence. I wrote all four while holding the doctrine that names this exact failure, in a lane
   whose subject *is* checks that cannot fail. I now run every command postcondition against the
   pre-work tree and require non-zero before freezing a plan; all five in the revision do.
2. **I nearly shipped a guard blind to a third of its targets.** I measured "15 clauses" and
   moved on without measuring the *shape* of the string. Only a candidate's self-attack made me
   census it: three surface forms.
3. **I under-measured the blast radius** — I found one mandating test and treated it as the
   mechanism; there are nine.

**What helped.** The cold `claude -p` critic was the highest-value spend of the run by a wide
margin. The design-it-twice pair earned its keep in an unexpected way: not by producing a design I
adopted wholesale, but because both candidates were required to attack *themselves*, and their
self-attacks were where the real findings were.

**What got in the way.** (a) The `verify-frame` / decision-grading conflict above — I had to move
graded decisions out of the frame to satisfy a check, which is compliance shaped like a
workaround. (b) A headless `claude -p` launched in this worktree **inherits the session's Stop
hook and `SPINE_*`**, and my probe agent began trying to drive *this* lane's spine before
permissions stopped it; I stripped `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` for every
subsequent dispatch, and that should be the documented default. (c) Two `claude -p` helpers hit
`Warning: no stdin data received in 3s` and one died with a bare `Execution error`; `< /dev/null`
fixed it.

## 11. PR

**None opened.** No source change exists to review.
