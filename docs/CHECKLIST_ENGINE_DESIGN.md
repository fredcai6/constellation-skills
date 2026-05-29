# Checklist Engine Design

Status: **design / pre-build**. Captures the model agreed in design discussion. Not yet implemented. Naming is provisional (see Open Questions).

## Problem

Constellation checklists today are **passive documents**: a gate carries status, criteria, and an evidence cell, but nothing enforces the protocol. The agent is trusted to read the table, locate where it is, do the work, and honestly update the cell. That trust is the assumption that breaks on a **less capable model** — a six-months-ago model will not reliably re-scan a 170-line checklist, find the current gate, remember the evidence rule, and resist jumping ahead.

The fix is to embed the *Checklist Manifesto* property into the mechanism: the checklist is **held and gated by something other than the agent doing the work**. We flip the checklist from a document the agent maintains into a **state machine the agent transacts with through a tool**. The deterministic engine owns "where are we," "what's next," and "are you allowed to advance." The model's job shrinks to: *do the one bounded step the tool named, then report evidence back to the tool.* Tool output is itself a prompt — for a weak model it returns an **imperative** ("you are on gate 2; do exactly this; when done run …"), not data.

This is deliberately the **anti-spec-kit** posture: the artifacts are not orphan documents floating on their own. Every checklist node is anchored into the work tree and the project map (see Anchoring).

## Core model: a single-active-leaf tree

Executing a project is **checklists within checklists**. A project decomposes `understand → plan → execute (implement ⇄ review) → clean up`; each of those, pushed on, is itself a checklist. The interrogator's question queue is a checklist. A pilot's implementation-gate list is a checklist. They share **one structure**: an ordered set of nodes, each with criteria, status, evidence, and an optional **child checklist**.

The engine manages a **tree** and walks it **one active leaf at a time**. `current` descends to the deepest open leaf. A parent gate does not close until its child checklist closes.

**No parallel branches.** If multiple scopes must progress in parallel, they are **separate execution windows = separate work-ids = separate trees**, not concurrent branches in one tree. Fan-out (e.g. 1 implementer / 3 reviewers) happens *inside a single gate's execution*: the owner spawns probes and **synthesizes one evidence artifact**. The engine only ever sees "one review gate, one synthesized result." Parallelism never reaches the tree.

## Typed checklists

One engine, but each checklist declares a `kind` that fixes its policies. Sharing the *structure* is fine; conflating the *semantics* is the trap.

| kind | ordering | executor may append? | "next" is |
|---|---|---|---|
| `strict-sequential` | hard — cannot advance past an open gate | no | the next pending gate |
| `priority-queue` | soft — reorder freely | yes | highest-value open node |
| `unordered-set` | none — all must close | no | any open node |

- Implementation-gate plans and the top-level phase spine are `strict-sequential`.
- The interrogator's question queue is `priority-queue` (questions spawn follow-ups and branches).
- A quality/rule checklist where every item must simply be satisfied is `unordered-set`.

## Permissions: structure vs state

Two layers, with a clean split:

- **Structure** (the gates themselves — add / remove / reorder / criteria): **owner-only.**
- **State** (status + evidence on an existing gate): **executors** may write this, and only this.

Consequences:

- An implementer (executor of a Pilot-owned plan) can move a gate to complete and attach evidence, but **cannot add a gate.** New work discovered from below does not edit the plan — it **bubbles up as a signal** (existing crew return statuses: `out-of-scope`, "new information: ambiguity | decision | structural change | Triage candidate"). The owner decides whether to amend. A "replan" is an explicit, audited owner operation, not silent drift.
- **Append** is the one structural operation an executor may perform, and only on `priority-queue` kinds. The interrogator is both owner and executor of its own queue, which is why it is the exception — not a special case in the engine, just a consequence of owning what it executes.

### Skip / OBE is a state operation, not a structure change

Marking a node "overcome by events" (e.g. question 37 is moot because 13 answered it; or "I didn't need this step, I did it earlier") is **`skipped because <reason>`** — a state transition recording a fact about a node. It is a **universal executor right, even in `strict-sequential`.** The engine does not forbid it. The safety net is not the engine refusing; it is the **invoker reviewing the returned packet** plus the reviewer crew checking the same thing. A bogus skip gets caught on review and bounced back, not prevented by a gate. Fewer engine rules; verification concentrated where judgment lives.

## The three engine moves

The dispatch loop is symmetric and bidirectional:

1. **dispatch** (down): invoker → executor. A compressed context envelope in.
2. **return** (up): executor → invoker. A compressed packet out. The executor's return is a **proposal**, not a fait accompli.
3. **reject / rework** (down again): the invoker may refuse the packet ("rework this item") and **reopen the node with a reason** (`complete → in-progress`, reason required, auditable). Re-dispatch follows.

A "completed" leaf is therefore not frozen until the invoker **accepts** the returned packet. Reopen is an owner-only state transition.

### Bounding rework (engine-enforced, Charter-configured)

The bounce-back has a weak-model failure mode the strong models hide: **rework ping-pong** — invoker rejects, weak executor "fixes," still wrong, repeat, forever. So the engine enforces a **rework cap per node**. On the Nth rejection it **stops re-dispatching and escalates up a tier** (or to the user) instead of looping. The cap is a project setting established at **Charter** (user setup) time and read by the engine; it is not the weak invoker's judgment call, precisely because the weak invoker is the one that would otherwise loop forever.

## Evidence: gate on type/shape, not quality

The engine does **not** judge whether work is good. A gate declares the **evidence types** required before it can close, and the engine checks **presence and minimal shape** only:

- `command-output` (exit 0)
- `review-result` (verdict = APPROVE, or owner override with reason)
- `file-diff`
- `user-decision`
- `cartographer-verification`

So a "needs review" gate cannot close until a reviewer artifact of verdict APPROVE is attached; a fan-out gate requires N review artifacts plus a synthesis. The engine enforces that **the right kind of check happened**; the crew supplies **whether it is actually good.** That is the honest division of labor between the deterministic script and the agents, and it is fully generic.

## Unified context envelope

The context handed *down* to an executor and the context returned *up* from one are the **same object** — CREW_HANDOFF, interrogator-return, REVIEW_RESULT are all instances of a single contract carrying `tier` and `direction`. This kills the per-role artifact sprawl that made spec-kit / OpenSpec / BMAD produce orphan documents.

The boundary contract: **a good manager talks to the employee at the level the employee understands; the employee translates that into its own implementation level, does the work, and synthesizes the result back up into something digestible by the invoker.** Each side translates across the tier line, in its own direction.

Envelope (sketch):

- **down:** compressed context in, bounded task, allowed scope + exclusions, inherited rules (see below), required evidence types, stop conditions.
- **up:** what was done, evidence (by type), deviations (skips / OBE with reasons), assumptions, signals / new-info bubbled up, self-assessed status.

## Two-tier verification

Verification happens at **two tiers**, which is the robustness story for weak agents:

- **Peer tier** — reviewer crew, *same context* as the implementer → catches code-level / low-level defects.
- **Supervisory tier** — invoker checks the *synthesized packet against intent* → catches "technically done, missed the point."

Even if all low-tier agents are mediocre, the high-tier invoker still checks the **compressed** result against the goal it is the only one holding.

## Roles as context-isolation boundaries

The roles are not a workflow org chart — they are **context-isolation boundaries**. Constellation is a context-budgeting machine; the checklist tree is the spine that routes *which tier of context goes where*. One thing understands the **architecture**; another understands the **no-shit how the code actually works**. We deliberately do not send the high-level role combing through files.

Therefore: **every cross-tier descent is a subagent boundary that returns a compressed artifact.** A high-tier agent that needs dense knowledge **dispatches a probe and gets back a summary, never the raw exploration.** Interrogator, Cartographer, and Scout are all "go dense, return compressed" probes that exist to protect a higher context window. (The current interrogator-inside-Pilot arrangement violates this — it crosses tiers in-context — which is why the interrogator becomes a dispatched probe.)

### Tier map

```
Commander            intent + 4-phase spine + produces the gate plan      (never touches code)
  Pilot ‖ Cartographer    executes the gate plan / owns structural truth   (architecture packets, not code)
    Crew: implementer ‖ reviewer                                           (code-dense, bounded scope)
  Probes (dispatched to go-dense, return-compressed): Interrogator, Cartographer, Scout
```

- **Commander** owns only the four-phase split and **produces the gate plan** (leaning on a Cartographer probe for structure). It does not execute.
- **Pilot** is handed a frozen gate plan, holds architecture packets, executes the gates, and interfaces directly to the implementer/reviewer crew.
- **Pilot and Cartographer are peers** under Commander; Crew sits below.

### Rule: a role earns its existence

> A role is justified iff it owns a distinct **(context tier × checklist kind × return artifact)**. If two proposed roles share all three, they are one role.

This is the guard against role sprawl while still adding roles for the sake of context management (context explosion — especially an architecture diagram crossing multiple file-region boundaries — is the actual enemy).

## Rules inherit down the tree

Project- or section-specific quality rules (e.g. "must work with MATLAB Coder," "must be fail-safe") attach to a **node** and **inherit down its subtree.** Project-wide rules live at the root (Charter's `CREW_CONTEXT`); section-specific rules attach to the relevant subtree. Any leaf gate's **implementer and reviewer both receive the union of inherited rules** in their envelope. The tree we decompose *work* along is the same tree we route *context and rules* along — one structure, both jobs.

## Anchoring (anti-orphan)

Every checklist node is anchored — to a **work-id**, to its **parent gate**, and optionally to a **Cartographer structural anchor** (`struct:<id>`). Nothing lives in isolation; a node knows its place in the work tree *and* in the project map. The Cartographer is what gives a node durable context instead of a doc floating on its own.

## State ownership

The engine owns **structured (JSON) canonical state**. Human-readable markdown, if rendered at all, is a derived courtesy view, never the interface. (Human-readability of the checklist is explicitly not a goal.)

## Engine verb set (provisional)

```
current                         which node is active + its imperative description
criteria <node>                 completion criteria + required evidence types for a node
advance <node> --evidence …     attempt close; engine validates ordering + evidence shape, else refuses
skip <node> --reason …          mark OBE (state op; reason required)
block <node> --reason …         blocker + needed authority + next action
append <node> …                 priority-queue kinds only; executor structural add
reopen <node> --reason …        owner-only; rework bounce-back (counts against rework cap)
dispatch <node>                 emit the down-envelope for the active leaf
return <node> …                 attach the up-packet (proposal)
accept <node>                   owner accepts the returned packet; closes the node
```

## Open questions / not yet decided

- **Naming.** "Interrogate a checklist" collides with the existing `constellation-interrogator` role (which questions the *user*). The querying verbs need distinct names. "Workbench" is kept. Cleanup deferred.
- Exact JSON schema for a node and the envelope.
- Whether `accept` and `advance` collapse into one move or stay distinct.
- How the Commander↔Pilot handoff freezes the plan (snapshot vs reference).
- Migration order: which role's checklist conforms to the schema first (lean: conform first, restructure roles later).
</content>
</invoke>
