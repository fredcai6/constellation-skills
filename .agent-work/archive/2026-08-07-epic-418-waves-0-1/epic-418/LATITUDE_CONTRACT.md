# Latitude Contract: `epic-418`

**CONFIRMED by Tommy, 2026-08-05.** The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Scope discipline — Tommy's standing ruling, 2026-08-05

> *"this is not a final step in a process. lets do what we need to do and no more. this doesn't
> mean be sloppy, but i am explicitly allowing you to not chase down every corner case. make the
> thing that needs to work, and if you have any concerns, just note it locally in comments and
> pass it up the chain"*

This **overrides the default rigor posture** wherever the two pull against each other, and it is a
mandatory clause in every launch order this epic issues. Concretely:

- Build the thing that needs to work. Do not generalize past the stated obligation, and do not
  harden a corner case the issue did not ask about.
- A corner case you chose not to chase is **not** a defect to hide — put a comment at the code site
  naming it, and float it up in the return. Noting-and-passing-up is the sanctioned exit; silently
  absorbing it is not, and neither is stopping to fix it.
- **Not sloppy:** the acceptance criteria each issue states are still the acceptance criteria. This
  ruling licenses narrower *scope*, never weaker *evidence* on what is in scope.
- Where an issue's own text and this ruling disagree about breadth, this ruling wins and the
  commander says so in its return.

@grade: settled/human · leans wave-0,wave-1,wave-2,closeout

## Epic Intent

Post-phase-1 mechanisms + cleanup. Make the frame hold, then clean the decks, plus a deliberate
first-round MCP front door. Six workstreams:

| Issue | Workstream | Done looks like |
|---|---|---|
| #419 | A — governor per-agent identity | **a trip fires from a per-agent reading on a live run** (not merely "readings appear") |
| #420 | B — engine channel fixes | `current` carries the imperative exactly once; every populated gate field renders; completeness property test in the suite |
| #421 | C — spine-instruction relocation, first tranche | Commander `execute`+`plan` text rides the gate; `commander-core.md` shrinks ≥40% (placeholder); tracer 3/3 vs 0/3; per-run delivered tokens do not grow |
| #422 | D — wire the prose-only invariants | #329 + #328's two conversions refuse instead of hoping; enumeration check catches a template left out; deliberate-breakage negative test passes |
| #423 | E — backlog consolidation + closeout debts | every surviving open issue labelled to a stratum or a reproduced defect, by one `gh issue list` sweep; closeout-debt filings owned |
| #424 | F — MCP front door | cold agent drives a real role spine to done with zero malformed calls; separation, inheritance-fail-closed, and same-gate-equivalence all pass |
| #425 | G — file the triage-candidate defects | one tracker ref per candidate, each linking the spec's Out of scope section |

Outcome that must not be violated: the spec of record
(`.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md`) governs. A workstream that
cannot meet its stated obligation says so and surfaces — it does not substitute adjacent work for
it. That is the **#308 failure shape**, and E's closeout check exists to catch it.

## Success Shape

All seven issues dispositioned. **A measured negative is a complete, successful deliverable** —
carried from the spec's own "if deletion alone suffices, the break is not taken; that outcome is
success, not failure." B explicitly puts "delete the two vestigial fields" on the table as a
legitimate smaller fix. Falsification triggers rework of that element, never silent continuation
and never abandonment. Every threshold in the spec is graded; `guess`/`placeholder` grades are
revisable per the `@grade` doctrine.

## Checkpoint Protocol

**CONFIRMED.** Stop-and-present at every wave boundary; run ahead freely
between boundaries. What reaches Tommy at a checkpoint: plain-English summary, decision asks,
changed reads of the epic; evidence on demand.

**#423 (E) is the one HITL issue.** The Admiral assembles all of E's evidence — the five
uncontested closes with their evidence comments, plus the proposed cluster boundaries — and
presents them as **one batch** at the wave-0 checkpoint. Tommy's single confirm executes the batch.
Nothing in E closes without it.

## Decision Classes

**CONFIRMED.** Table carried from the epic-298 contract and adjusted:

| Class | Disposition |
|---|---|
| Architecture / structural change | delegated *(surfaced if it changes a load-bearing interface shape — the MCP tool surface, the gauge binding key, the gate schema)* |
| Scope change (issue added / dropped / re-scoped) | **surfaced** |
| Merge to main | delegated *(green + reviewed only)* |
| Issue filing / closing | delegated for **filing and commenting**; **closing is surfaced** and rides E's batch confirm |
| Fix-now triage (bounded fix applied immediately) | delegated |
| Spend / budget / model tier | delegated *(within the table below)* |
| Production defaults / user-visible behavior | **surfaced** |
| **Spec deviation** — a build cannot meet its workstream's stated obligation | **surfaced — always** (the #308 shape) |
| **Threshold regrade** — a `guess`/`placeholder` threshold the build leans on | delegated: run the `settle:` experiment, log the ruling, regrade. **Two exceptions, surfaced:** E's cluster boundaries and C's tranche boundary — the spec names both as costly to revert |
| **Pre-build branch points** (A's hook-payload probe, F's `.mcp.json` pickup) | delegated to record and act on. **"Neither shape" on A's probe is out-of-taxonomy — stop and escalate**, per the spec's own instruction |
| **Design-it-twice convergence** | **surfaced — always** (convergence is human-only). None expected: A/C/F are satisfied by exc-6/8/9, B/D/E are recorded trivial-skips |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated; logged as RULINGs in ADMIRAL_LOG; constellation
  lessons always exported, never silently confirmed. A graduation into project doctrine (`.md` /
  `.template.*`) still carries `authority=human` on its apply op.

## Permission prerequisites

**CONFIRMED — every row pre-cleared.** A `delegated` disposition settles who decides, not what the harness
permission classifier lets through. All rows below are pre-cleared by Tommy, 2026-08-05:

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Issue filing / commenting (G #425, E #423 filings) | `gh issue create`, `gh issue comment`, `gh issue edit` | **pre-clear** — grounded: #145, plus the gh-issue-create gap recurring a 4th time; #425 names it as its own precondition |
| Issue closing (E #423) | `gh issue close` | **pre-clear the capability**, but each close still rides Tommy's batch confirm — the clearance removes the classifier veto, not the human gate |
| Merge to main | `gh pr create`, `gh pr checks`, `gh pr merge`, `git push` to `epic-418/*` branches | **pre-clear** for green+reviewed; fallback: one human approval in the moment, rest batched to the next checkpoint |
| **A #419 live-fire mechanics** | dispatching ≥2 subagents; reading `~/.claude/projects/**` transcripts; **mutating the live gauge binding store** (the one-time sweep retires 47 real bindings); deleting the sweeper after its run | **pre-clear** — dry-run with before-state recorded first, then the real run |
| **C #421 measurement mechanics** | 6 cold-agent tracer dispatches (n=3 × 2 arms); **corpus surgery** — editing `COMMANDER_SPINE.template.json` and `commander-core.md`; re-running `install_constellation.py` | **pre-clear** — this is the mission's core loop; leaving it unlisted vetoes the mission at execute time (#145) |
| **D #422 negative test** | deliberate invariant breakage in a scratch run/worktree | **pre-clear** — the breakage is reverted by the same issue that induces it |
| **F #424 door mechanics** | writing project-scope `.mcp.json`; starting an MCP server process; per-dispatch config generation; subagent dispatch for the separation and inheritance tests | **pre-clear**. `settings.json` is never touched — that boundary is in the spec |
| Fix-now triage | full test suite (`py -m pytest`), local commits | **pre-clear** |
| Spend / model tier | dispatching subagents at the tiers below | **pre-cleared** |
| **Subagent dispatch (all tiers)** | this Admiral dispatching Commanders; Commanders dispatching crew; crew dispatching cold critics/tracer agents | **pre-cleared explicitly by Tommy 2026-08-05**: *"you and all your sub agents are officially allowed to use agents because im telling you to use skills that use agents"* |

## Float-Up Routing

A Commander floats a **decision**: adjudicate inside delegated classes and log a RULING; escalate
surfaced classes and out-of-taxonomy to Tommy. A Commander floats a **context query**: answer from
epic knowledge and continue it. A Commander files a **refresh-request**: relaunch a fresh Commander
into the same worktree and spine file, cold-starting from `current` alone.

Per-class nuance: any **spec-deviation** question goes to Tommy always — that is the guard this
epic was built with. So does A's "neither payload shape" branch, which the spec instructs to stop on.

## Comms

Plain English by default; technical depth on demand. No invented project dialect in anything
user-facing. Decision asks in plain text, never question dialogs.

## Budget / Model Parameters

**CONFIRMED.**

| Issue | Dispatch shape | Tier |
|---|---|---|
| A #419 | full Commander | Opus |
| B #420 | full Commander | Sonnet |
| D #422 | full Commander | Sonnet |
| G #425 | implementer-with-plan (small, bounded — the right-size rule) | Sonnet |
| E #423 | Admiral + Tommy, no Commander | — |
| C #421 | full Commander | Opus |
| F #424 | full Commander | Opus |

No Fable at any tier. Wave 0 proposed **four-wide** (A, B, D, G concurrent), sized to the account
usage pool; if a limit reset is near, the next wave waits past the reset rather than launching into it.

## Pre-Rulings

- decision:prototype-lifts — lift A from `.proto-exc6-governor-subagent-identity` @ 75f684c, C from `.proto-exc8-spine-instructions` @ 5a283ad, F from `.proto-exc9-mcp-front-door` @ de6a084; delete each worktree once its lift lands, the commit SHA keeps the code recoverable.
  @grade: settled/human · leans wave-0,wave-1,wave-2
- decision:honest-null — a measured negative is a complete, successful deliverable; every verdict states what was tested and what was not.
  @grade: settled/inherited · leans wave-0,wave-1,wave-2
- decision:b-vestigial-fields — if B's inventory finds `anchors`/`constraints` vestigial across the corpus, deleting the two fields is the accepted smaller fix; B's commander decides on its own inventory evidence.
  @grade: guess · leans #420 · settle: inventory what the corpus's gates actually carry in those blocks
- decision:a-probe-branch — A's commander picks the re-key or matcher branch from the real hook payload and records it; the third outcome ("neither shape") stops and escalates.
  @grade: settled/human · leans #419
- decision:wave-0-is-four-wide — A, B, D, G launch concurrently; E runs with Tommy at the checkpoint.
  @grade: guess · leans wave-0 · settle: watch the usage pool through wave 0's first hour
- decision:e-splits — E's tracker work executes in wave 0 on the batch confirm; E's closeout obligation check is the epic's terminal act, after every other issue lands.
  @grade: settled/human · leans #423,closeout

## Expiry

**CONFIRMED.** **The wave-1 checkpoint** (after wave 0's PRs merge), or 72
hours, whichever comes first. Crossing it forces a contract-refresh decision before further dispatch.

## Confirmation

2026-08-05 — confirmed by Tommy in session, recorded as `user-decision` evidence on the `latitude` step. He agreed the contract as drafted and added the scope-discipline ruling at the head of this document, plus explicit subagent-dispatch authority for this Admiral and every commander and crew it dispatches.
