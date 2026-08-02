# Checklist Engine Design

Status: **design / pre-build**. Captures the model agreed in design discussion. Not yet implemented. Naming is provisional (see Open Questions).

## Problem

Constellation checklists today are **passive documents**: a gate carries status, criteria, and an evidence cell, but nothing enforces the protocol. The agent is trusted to read the table, locate where it is, do the work, and honestly update the cell. That trust is the assumption that breaks on a **less capable model** — a six-months-ago model will not reliably re-scan a 170-line checklist, find the current gate, remember the evidence rule, and resist jumping ahead.

The fix is to embed the *Checklist Manifesto* property into the mechanism: the checklist is **held and gated by something other than the agent doing the work**. We flip the checklist from a document the agent maintains into a **state machine the agent transacts with through a tool**. The deterministic engine owns "where are we," "what's next," and "are you allowed to advance." The model's job shrinks to: *do the one bounded step the tool named, then report evidence back to the tool.* Tool output is itself a prompt — for a weak model it returns an **imperative** ("you are on gate 2; do exactly this; when done run …"), not data.

This is deliberately the **anti-spec-kit** posture: the artifacts are not orphan documents floating on their own. Every checklist node is anchored into the work tree and the project map (see Anchoring).

## Goals

Two goals, co-equal:

1. **Gate less-capable models** (the Checklist Manifesto property): the checklist is held and enforced by the engine, not remembered by the agent, so a weaker model can execute one bounded step at a time without holding the workflow in its head.
2. **Produce a traceable record**: the checklist tree is a complete, authority-stamped, evidence-backed account of how a bounded problem was understood, planned, executed, verified, and reconciled.

**Recoverability is a side effect of traceability, not a primary design driver.** Because the engine externalizes state, a role *can* be resumed — and for small models it may eventually need to be killed and respawned mid-stream — but that falls out of keeping a faithful trace; it is not the reason the engine exists.

**Per-node model selection is a non-goal (for now).** Routing different model strengths to different tiers is too cute to bake into the baseline; the design assumes you may not have a great model *anywhere* and leans on human checkpoints instead of strong-model-at-top. Model-tier routing may return later as an optimization, never a foundation.

## The human is the top tier

The Commander is **not** an autonomous strong reasoner that replaces human effort. It is a **rigor scaffold** — it decomposes the work, tracks it, and **surfaces decisions to the human rather than making them.** The governing principle: **force the human to make the decisions, not obfuscate them.** A human uses the Commander to *be rigorous*, not to *offload effort*.

The human is the **next-higher level of context management** — the one who knows where this issue sits in the system-of-systems. So the operator sits above the Commander in the tier stack:

- The human **clarifies the issue with the Interrogator** before planning.
- The Commander can **pause and hand decisions up for human verification** at its checkpoints — *is the plan good? is this architecture change the intent?* — before proceeding.

This is why the design does **not** depend on having a great model: the hard judgment is escalated to the human at gated checkpoints, not performed by the model. Pausing for human verification is a first-class Commander capability, not an exception path.

The human verifies **Commander-level steps, not Crew-level steps** — phase transitions, the plan, architecture intent — never every implementation gate. Crew-level work is abstracted away unless a checkpoint forces a dig-in; per-gate correctness is the crew's two-tier verification, not the human's. Otherwise rigor decays into rubber-stamping. *Which* checkpoints are mandatory is the project's **rigor level**, set at Charter alongside the caps. And because the engine holds canonical state, a run awaiting a human decision simply **parks**: the operator can return hours later, in a different session, and resume from `current`. Every human gate is a clean suspend/resume boundary.

## Core model: a single-active-leaf tree

Executing a project is **checklists within checklists**. A project decomposes `understand → plan → execute (implement ⇄ review) → clean up`; each of those, pushed on, is itself a checklist. The interrogator's question queue is a checklist. Commander's execute.json is a checklist. They share **one structure**: an ordered set of nodes, each with criteria, status, evidence, and an optional **child checklist**.

The engine manages a **tree** and walks it **one active leaf at a time**. `current` descends to the deepest open leaf. A parent gate does not close until its child checklist closes.

**No parallel branches.** If multiple scopes must progress in parallel, they are **separate execution windows = separate work-ids = separate trees**, not concurrent branches in one tree. Fan-out (e.g. 1 implementer / 3 reviewers) happens *inside a single gate's execution*: the owner spawns probes and **synthesizes one evidence artifact**. The engine only ever sees "one review gate, one synthesized result." Parallelism never reaches the tree.

The spine maps to roles:

```
Commander spine (strict-sequential)
├─ understand   → child: Interrogator question-queue (priority-queue) + Cartographer structural probe
├─ plan         → Commander authors the gate plan (Cartographer probe for structure)
├─ execute      → Commander's execute.json (strict-sequential) → per gate: implement → review → integrate
└─ clean up     → reconciliation (Cartographer) + future work (Triage) + archive/closeout (Workbench)
```

The `kind` changes as you descend (ordered spine and gates; unordered/scattershot questions). A node's child checklist may be a different kind than its parent; the engine does not care.

**Self-similarity is a capability, not a mandate.** The tree *can* nest arbitrarily, but real trees are shallow: a fixed spine (understand → plan → execute → clean up), a single authored layer (the gate plan, produced by planning `execute`), and gates that are usually **primitive** — the crew is handed "implement this thing" and just does it. Decomposition is used only where it is *real* (a genuine "verify these items" checklist becomes a delegated child); it is never forced for uniformity. A primitive task is the terminus *of the parent's plan*: how the crew solves it is the crew's own business — the implementer may keep its **own** `gated` plan (the same skill) to stay organized, but that plan is self-authored, never handed further down, and invisible to the parent, which sees only the returned evidence.

## Two checklist types

Every checklist is an ordered list of items and declares one of two types:

| type | item failure | append | completes when | used by |
|---|---|---|---|---|
| `gated` | **blocks** (rework) | no | every item satisfied or skipped | execution: Commander spine, Commander's execute.json, the implementer's own plan |
| `survey` | **recorded, never blocks** | yes | every item visited, then **consolidated** | inquiry/verification: Interrogator questions, reviewer checks |

A `survey` is handed a *starting* list and told "verify these, and add more based on the context we gave you" — which is why append is inherent to it. The Interrogator and the reviewer are the **same shape**: hit every item, nothing gates anything, consolidate at the end (a resolved understanding; an APPROVE/BLOCK verdict).

## Permissions: structure vs state

Two layers, with a clean split:

- **Structure** (the gates themselves — add / remove / reorder / criteria): **owner-only.**
- **State** (status + evidence on an existing gate): **executors** may write this, and only this.

Consequences:

- An implementer (executor of a Commander-owned plan) can move a gate to complete and attach evidence, but **cannot add a gate.** New work discovered from below does not edit the plan — it **bubbles up as a signal** (existing crew return statuses: `out-of-scope`, "new information: ambiguity | decision | structural change | Triage candidate"). The owner decides whether to amend. A "replan" is an explicit, audited owner operation, not silent drift.
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

## The rail: engine-carried doctrine at decision points (`_rail()`, #140)

The engine doesn't just enforce ordering — it appends a short doctrine block, the **rail**,
to its own output at every decision point, so the enforcement text lives with the mechanism
that decides, not in prose an agent might skip or misremember.

- **Surface.** `_rail(point, cl)` in `checklist_engine.py` supplies the `RAIL: <text>` block for
  the successful output of the six railed verbs (`RAIL_VERBS = {claim, current, start, advance,
  attest, attach}`) and for the REFUSED path in `main()`. The verb functions themselves stay
  pure — their return values are unchanged; the rail rides only the CLI output boundary, so
  existing exact-equality tests keep passing. `gated` checklists only: a `survey` checklist
  (`cl["type"] != GATED`) gets no rail at all.
- **Position on the stream (#227 item 4).** The banner is emitted **first** and the operative
  result/refusal line **last**, via `_rail_prefix()`. It used to be appended as a suffix, which
  meant `tail -1` read the banner and silently hid the operative line — observed twice in the
  live epic-226 run, where a real `REFUSED: … preconditions unmet ['p1']` disappeared behind it.
  Stream assignment is unchanged: success → stdout, refusal → stderr.
- **Five decision-point strings**, keyed by position, held verbatim in `_RAIL_STRINGS`:
  `early` (first gate, not yet worked), `mid-flight` (mid-run, `{n}` gates from done, names
  the next `{imperative}`), `near-terminal` (one gate left before release-eligibility),
  `terminal` (only `release` remains), and `check-failure` (a verb was REFUSED). The first
  four are derived from spine state (`_rail_position`); `check-failure` is the one point NOT
  derived from `items` state.
- **The refusal-path trigger.** `check-failure` cannot be read off `items` state — a failed
  `advance` leaves the spine looking identical to ordinary mid-flight (nothing recorded the
  attempt). Its only deterministic trigger is the `EngineError` raised on the REFUSED path in
  `main()`; that raise, not any state predicate, is what selects the `check-failure` string.
- **Position derivation (`_rail_position`).** `remaining` is the ordered list of not-yet-
  terminal items; `n = len(remaining)`. `n == 0` → `terminal`; `n == 1` → `near-terminal`;
  active gate (`remaining[0]`) is the checklist's first item → `early` (substitutes `{id}`);
  otherwise → `mid-flight` (substitutes `{n}` and `{imperative}`).
- **Canonicality.** This table is the **single canonical enforcement source**; `_shared/
  global-everyone.md` §Completion enforcement elaborates and cites it in prose, but on any
  conflict between the two, the table wins — it is generated from spine/refusal state, not
  hand-maintained prose that can drift. The five strings are **frozen, verbatim** (a
  measurement precondition for #145): do not paraphrase them; `{id}`/`{n}`/`{imperative}` are
  the only substituted tokens.

## Answerability: `current` as a complete briefing, refusals that carry their exit (#227)

The motivating measurement lives in `scripts/measure_overread.py` — a transcript scanner counting
structural reads (spine/cycle JSON, engine source) per run, with its committed fixture corpus and
that corpus's stated limits under `tests/fixtures/overread_corpus/README.md`. It is the instrument
this section's changes were built to move; read it before re-litigating them. Note its scope
honestly: it counts read *events*, not tokens, and a fixed historical corpus cannot move after a
code change — it proves the instrument is deterministic, not that behavior changed.

Agents driving a spine were falling through to reading `spine.json` and the engine source,
because `current` printed the imperative and nothing else and a refusal named no way out. Both
are now answered from engine output, so reading the raw file is unnecessary (and, per
`_shared/global-everyone.md`, a violation).

- **State projection (the port).** `state(cl) -> dict` is a **pure** projection returning a
  `StateView`-shaped dict — active id, status, full imperative, pre/postconditions with their
  ids and kinds, lease, why-digest, legal `next_verbs`, and a `contract` version int.
  `render_human(view) -> str` is the only adapter that ships; `current()` is now exactly
  `render_human(state(cl))`. The shape follows the ratified 3-agent design-it-twice panel. **No
  public `--json` flag ships** — a future conductor adapter is `json.dumps` behind a flag once a
  consumer exists; `contract` is there so it can pin.
- **Purity (INV-2).** The projection reports **recorded** condition state and never re-runs a
  `command`/`git-change-policy` check. Reading is not a probe. The sharp edge, made explicit:
  `satisfied: false` means "not yet recorded as passing", **not** "would fail if run now".
- **Completeness (INV-1).** `current`'s output is a superset of the arguments the caller's next
  verb needs. This is tested against a **hand-authored map derived from the verb bodies**, never
  from argparse: `advance --why` and `attest --evidence` are required at runtime but optional at
  the parser, so an argparse-walked map would omit exactly the two arguments agents most often
  read source to discover.
- **Recovery (INV-3).** Every state-caused refusal names its exact exit, derived from
  `(status, attempted-verb)` by the pure `recovery_for()` — blocked → `resume`, complete →
  `reopen`, unmet condition → the precise `attest` naming the real ids, unknown cond id →
  enumerate the valid ids — closing with `Do not edit the JSON — use the engine.` Recovery is a
  **separate channel** from the five frozen rail strings.
- **Seam.** Recovery composes at the **CLI boundary**, like the rail, so the verb-purity law
  above survives. `EngineError` carries structured attributes (`task_id`, `verb`, `status`,
  `unmet`, `valid_ids`); nothing re-parses message text.
- **Standing hazard, learned the hard way.** Four defects were found here, all identical in
  shape: a recovery naming a command that *refused when run*. None was a careless branch — each
  time the test fixtures could not express the failing state (single-task fixtures hid the
  non-active gate; a hardcoded `pending` guard gate hid the active-gate statuses where the
  advice was wrong). Any change to this surface must be validated by **invoking** the commands
  it prints, over fixtures parameterized on status **and position**, not by string-matching the
  render.

## Context manifest: a second, delivery-shaped projection (#300)

Beside `state(cl) -> StateView` (what the engine believes about condition/lease progress, above)
sits a second, narrower projection: `scripts/context_manifest.py`'s
`build_manifest(checklist, roots, ...) -> {contract, step, files, run}`. Both select the active
unit through the **same** `active_id(cl)` — the manifest producer imports it rather than defining
a second selector, so the two projections can never silently disagree about which task is active.

Where `state()` answers "what is true about this checklist's progress," the manifest answers a
narrower, orthogonal question: **what was made available to the agent running this step, and at
which revision** — delivery, not use. It carries no claim that the agent read anything; it is not
an access trace, and its rows never carry file contents.

Shape: a task may carry an optional ordered `context_refs` list (`{root, path, required}`
entries — see the Task-table row in `docs/CHECKLIST_SCHEMA.md`). Root tokens (`skill` \| `repo` \|
`durable`) are resolved through a caller-supplied mapping, so absolute, environment-varying paths
never reach the manifest content, and the producer never globs or enumerates a directory:
declaration order **is** content, matching doctrine's own reading precedence (inherited global
doctrine, then project deltas). Each row's `rev` is the git blob OID of the LF-normalised bytes,
computed in-process (no `git` subprocess), so tracked, dirty, untracked, gitignored and
out-of-repo files share one code path with no case split; an absent file yields `rev: null` and
keeps its row rather than disappearing.

**The prose is not replaced.** The first real declaration in the corpus,
`COMMANDER_SPINE.template.json`'s `context` step, still carries the substitute-and-record rule and
the sanctioned-degradation rule in its `imperative` — a path list cannot express either.
`scripts/verify_context_declaration.py` is the mechanical lint that keeps the two from drifting
apart: every declared path must appear verbatim in its own task's imperative. The check is
one-directional by design: it catches the declaration naming a path its own prose never mentions;
it cannot catch the reverse — a path quietly dropped from the declaration while the prose still
names it (the declaration narrowing away from the prose) — because prose is not a parseable list.
The lint's own docstring states that same limit, in these same terms.

**No committed artifact ships from #300.** A committed, diffable `CONTEXT_PROJECTION.json`
alongside the run-local manifest was considered and ruled out of this issue's scope.
`scripts/context_manifest.py` therefore ships no CLI verb at all — the manifest is a JSON value a
caller builds and, optionally, writes under `<agent_work_root>/<work-id>/context/<step>.json` via
`produce()`, where `<agent_work_root>` is whatever durable root the caller hands it. A future drift
check comparing canon against a committed artifact is a later issue's territory, not this
substrate's.

**Two-level revision scheme (#300 g5, Tommy's ruling; split in rework 1).** Beside the per-file rows
sits one repo-level content field, `repo_rev: {commit}` — `commit` is `git rev-parse HEAD`, via
`checklist_engine.repo_revision()` (a real git subprocess, deliberately kept out of
`context_manifest.py`'s own source so its no-subprocess guarantee stays literally true, and injected
as a second impure edge, `repo_state`, beside the existing `reader`). It answers a coarser, repo-wide
question than `rev` does — *which commit is canon versioned at* — and does not replace the per-file
blob OID's *which bytes did this agent actually get*, which stays the identity answer for a dirty,
untracked or out-of-repo file that a commit SHA alone cannot cover.

`repo_revision()` also returns `dirty` — is that commit's tree honest right now — and the manifest
does not carry it at all. The original design shipped it beside `commit` inside content, reasoning
that a bare commit SHA needs the caveat to stay honest; a review disproved that (BLOCKER-1, rework 1):
two fresh checkouts at the same commit, delivering byte-identical declared canon, disagreed on
`repo_rev` because `git status --porcelain` is repo-wide and picked up an edit to a file no
declaration named. `commit` is canon-determined (identical for any checkout of that commit) so it is
safe as content; `dirty` describes the working tree that *produced* the manifest, not the bytes it
delivered, so rework 1 moved it into the excluded `run` subtree — a fact about the run, like
`roots`/`host`, not about canon. Neither placement reopens the honesty gap: the per-file blob OID
already answers the "which bytes did this agent actually get" question for a dirty/untracked/out-of-repo
file, which is what `dirty` was really protecting; `repo_rev.commit` only ever had to be the coarse,
human-facing traceability stamp. `repo_revision()`/`default_repo_state()` still return both fields
together, as a general repo-facts primitive not pre-shaped to this one caller's appetite;
`build_manifest` is the one consumer and now takes `commit` only.

**#300's successor, and why the sequencing is deliberate (#305, #327).** #300 shipped this producer
with **no caller**: nothing in the engine's own control flow built a manifest, so the field's runtime
behaviour was unobserved and unobservable. #305 g1 wired the first one — `episode_capture.emit_step_manifest`,
called from the engine's assembly point — and #305 g4 then **removed `dirty` from the manifest
entirely** (#327). Having a caller is what revealed it: `git status --porcelain` is repo-wide, so with
the manifest itself written under a tracked `.agent-work/` the flag reports the run's own bookkeeping
rather than anything a declaration names, and because `build_manifest()` computes it *before*
`write_manifest()` creates the file, each manifest reads its predecessor's tree, not its own. Measured
**on the tree this removal was made on**, over the 49 manifests this producer had written in-tree:
47 `true`, 1 `false`, 1 field-absent. **Both sides are given in full because the count is pinned to
that moment deliberately and keeps growing as this producer runs**: 49 / 47 / 1 / 1 immediately
before the removal, and 56 / 51 / 1 / 4 at the removal commit itself. (On the `epic-298/305` branch
those were `35d2686^` and `35d2686`; the squash-merge does not carry either SHA into `main`, which is
why the numbers rather than the refs are the durable anchor.) The lone `false` is the mechanism in
miniature rather than an exception to it: it is `.agent-work/issue-305/context/g1-implement.json`,
which exists at all only because g1 was **reopened**, and it reports clean because commit `2456130`
cleaned the tree 2m16s before it was generated — that commit is what cleaned it. The manifest
recorded the tree its predecessor `g1-review.json` had been followed by, eight minutes after that
one reported `true`, rather than anything it was itself about to do. Neither reading is available to a
consumer — not a constant to rely on, not a signal to interpret. The field was not an oversight in
#300 and its removal is not a reversal of a mistake; it is what a first real caller made visible.
`CONTENT_KEYS` is unchanged by the removal, because `dirty` was never content.

**Downstream, not yet resolved here.** The manifest is consumed, not produced, by whatever issue
turns out to build on it, and two questions are open across that interface. **Durability:** that
root is gitignored and a linked worktree's copy is destroyed by `git worktree remove`, so a
manifest is not a durable record unless something copies it out. **Cardinality:** one manifest
is produced per spine *step*, not per episode, so a consumer that thinks in episodes has to decide
which step's manifest it means. Neither is settled by this substrate.

## Evidence: gate on type/shape, not quality

The engine does **not** judge whether work is good. A gate declares the **evidence types** required before it can close, and the engine checks **presence and minimal shape** only:

- `command-output` (exit 0)
- `review-result` (verdict = APPROVE, or owner override with reason)
- `file-diff`
- `user-decision`
- `cartographer-verification`

So a "needs review" gate cannot close until a reviewer artifact of verdict APPROVE is attached; a fan-out gate requires N review artifacts plus a synthesis. The engine enforces that **the right kind of check happened**; the crew supplies **whether it is actually good.** That is the honest division of labor between the deterministic script and the agents, and it is fully generic.

## Unified context envelope

The context handed *down* to an executor and the context returned *up* from one are the **same object** — IMPLEMENTER_HANDOFF / REVIEWER_HANDOFF, interrogator-return, REVIEW_RESULT are all instances of a single contract carrying `tier` and `direction`. This kills the per-role artifact sprawl that made spec-kit / OpenSpec / BMAD produce orphan documents.

The boundary contract: **a good manager talks to the employee at the level the employee understands; the employee translates that into its own implementation level, does the work, and synthesizes the result back up into something digestible by the invoker.** Each side translates across the tier line, in its own direction.

Envelope (sketch):

- **down:** compressed context in, bounded task, allowed scope + exclusions, inherited rules (see below), required evidence types, stop conditions.
- **up:** what was done, evidence (by type), deviations (skips / OBE with reasons), assumptions, signals / new-info bubbled up, self-assessed status.

## Context tiering

The Charter context files are **not** read by all roles — they are tiered to match the role tiers, with deliberate overlap but intentional separation:

- `ORCHESTRATOR_CONTEXT` — **high-level** context: architecture and *why*. Read by Commander, Cartographer, Scout.
- `CREW_CONTEXT` — **low-level** context: implementation and *how*. Read by Crew.
- `GLOSSARY` — shared terms only; the one artifact genuinely read by all.

A role receives the context tier it operates at; the high/low split is intentional, not incidental. The envelope a high-tier role hands down is phrased in the *why*; the executor translates it into the *how* of its own tier and synthesizes the result back up.

## Two-tier verification

Verification happens at **two tiers**, which is the robustness story for weak agents:

- **Peer tier** — reviewer crew, *same context* as the implementer → catches code-level / low-level defects.
- **Supervisory tier** — invoker checks the *synthesized packet against intent* → catches "technically done, missed the point."

Even if all low-tier agents are mediocre, the high-tier invoker still checks the **compressed** result against the goal it is the only one holding.

## Roles as context-isolation boundaries

The roles are not a workflow org chart — they are **context-isolation boundaries**. Constellation is a context-budgeting machine; the checklist tree is the spine that routes *which tier of context goes where*. One thing understands the **architecture**; another understands the **no-shit how the code actually works**. We deliberately do not send the high-level role combing through files.

Therefore: **every cross-tier descent is a subagent boundary that returns a compressed artifact.** A high-tier agent that needs dense knowledge **dispatches a probe and gets back a summary, never the raw exploration.** (The Interrogator runs in Commander's context rather than as a subagent precisely because interrogation must reach the human — a subagent cannot. This is the sanctioned exception: same context, separate checklist.)

**Probes span tiers; Crew does not.** This is the distinction between two mechanistically-similar archetypes:

- **Probe-curators** (Interrogator, Cartographer, Scout) are invoked by a high-tier role, **descend into dense/low material, and return compressed truth back up** — they live *across* the high/low boundary, and their purpose *is* to cross it so a high-tier role needn't. They also curate durable truth (glossary, map packets, report).
- **Crew** (implementer, reviewer) lives **entirely at the low tier**: it receives a low-level envelope, works low, returns low-level evidence the Commander integrates. It never crosses the boundary; it *is* the low side.

Both are dispatched and both return packets, but they are distinct archetypes and likely do not share machinery.

### Tier map

```
Human (operator)     where this issue sits in the system-of-systems; verifies plan + intent at checkpoints
Commander            intent + 4-phase spine + produces and executes the gate plan  (never touches code)
  Cartographer            owns structural truth                                     (architecture packets, not code)
    Crew: implementer ‖ reviewer                                                   (code-dense, bounded scope)
  Probe-curators (tier-spanning, dispatched to go-dense / return-compressed): Interrogator, Cartographer, Scout
```

Cartographer appears twice on purpose: it is a mid-tier owner of durable structural truth *and* the probe a higher tier dispatches to read/update that truth.

- **Commander** owns the four-phase spine, produces the gate plan, and drives execute.json gate by gate in the same context. It networks to the Interrogator, Cartographer, and Crew (as dispatcher). It does not touch code.
- **Cartographer** is a peer to Commander's execution; Crew sits below.

### Rule: a role earns its existence

> A role is justified iff it owns a distinct **conversation** — a network of who it talks to and the context that conversation accretes. A distinct tier, a distinct checklist kind, *or* a distinct dispatch network each count; sharing *all* of them means it is one role.

This is the guard against role sprawl while still adding roles for context management (context explosion — especially an architecture diagram crossing multiple file-region boundaries — is the actual enemy).

**Commander and gate execution** share the same conversation: Commander holds the human/planning context and also dispatches and integrates crew results gate by gate. A separate Pilot layer was tried but added a role boundary without a meaningfully distinct conversation — the planning context and the execution context overlapped heavily, and the split hurt visibility. The three-task-per-gate structure in execute.json (implement → review → integrate) makes gate execution visible within Commander's single context without needing a second orchestrator layer.

## Role roster and lifecycle coverage

Every lifecycle stage has exactly one owning role — no gaps, no overlaps. Roles that sit *outside* a single Commander run (Charter, Scout, Cartographer) are cross-cutting **by design**; that they don't fit cleanly in the inner loop is the point. But they must consume the right context tier and stay migrated onto the engine format, so the Workbench changes don't orphan them.

| Role | Archetype | Loop | Produces / owns |
|---|---|---|---|
| Human (operator) | top tier | both | decisions at junctions, issue selection |
| Charter | setup / preflight | bootstrap (out of band) | ORCHESTRATOR_CONTEXT, CREW_CONTEXT, GLOSSARY, rigor + cap config; verifies starting products exist |
| Commander | conductor | inner | phase spine, the gate plan, executed gates, run outcome |
| Crew (impl ‖ review) | worker (low only) | inner | code changes, evidence, review verdict |
| Interrogator | probe-curator | inner (understand) | clarified issue, glossary updates |
| Cartographer | probe-curator + owner | cross-cutting | map packets + index (`struct:<id>` anchors) |
| Scout | probe-curator | outer | ranked architecture-pressure candidates |
| Triage | sink | inner-invoked, outer-consumed | issue-ready future work |
| Workbench | substrate | all | the engine, checklist state, the trace, archive |

**Charter is the preflight.** Before any workflow can start, it verifies the right *products* are populated: the two context tiers, the glossary, the rigor/cap config, and at least a **baseline Cartographer map** so the architecture bookend has something to read at the start. If a starting product is missing, the project isn't ready to be operated by Constellation.

**Cartographer and Scout are the roles most at risk of being left behind** by the engine work, precisely because they don't live inside the inner loop. The migration requirement is explicit: their own checklists conform to the typed-checklist schema; Cartographer's map IDs *are* the anchoring mechanism (`struct:<id>`) the engine references; both speak the unified envelope; and Scout's candidates carry structural anchors so they trace back into the map. Keeping them wired in is a first-class part of the migration, not an afterthought.

## Bounded scope and the architecture bookend

A Commander run handles **one bounded problem** — nominally one top-level issue. The gates are the steps needed to fix *that* problem, not an open-ended program of work. **40-gate plans should not exist**; if the work is that large, it is multiple issues / multiple execution windows. Bounding the problem is the Commander's job, and it is what makes everything downstream tractable.

Architecture is touched at exactly **two bookends of a Commander sequence**, not throughout:

- **At the start (read):** contextualize the ask against the *recorded* architecture (Cartographer packets) — framing the bounded problem in the existing structure.
- **At the end (reconcile / write):** capture the implemented changes back into the map so the *next* effort starts from current truth.

Reconciliation is **recording, not verification** — which is why it is correctly **batched once at cleanup** and does *not* conflict with the "never batch review" rule (review is per-gate correctness; reconciliation is end-of-run map maintenance).

Between the bookends, architecture is **frozen read-only context**: Commander executes against a snapshot of the map packets. If execution reveals the snapshot was wrong or the problem was mis-scoped, that is a **signal that surfaces to the human**, never a mid-flight edit to durable structural truth.

**Commanders get one shot.** There is no mid-run re-plan loop. If a plan is proven wrong, the signal bubbles to the Commander, the issue is **re-interrogated with the human, and the run ends in favor of a fresh issue / fresh Commander run.** One Commander run = one coherent plan = one clean trace. This keeps traceability intact (no plan churn inside a run) and removes the weak-Commander ping-pong failure mode entirely — there is nothing to ping-pong, because re-planning *is* a new run, not an in-run operation.

## Two loops

- **Inner loop** — one Commander run executes **one bounded issue**: understand → plan → execute → clean up. Self-contained, single-shot, one coherent trace.
- **Outer loop** — minting and prioritizing issues *across* runs. Scout audits the current map for architecture pressure; reconciliation surfaces drift; Crew bubbles discovered work. **Triage** packages all of it into issues, and each issue becomes a future inner run.

Both loops pivot on the same durable Cartographer map: the inner loop reads it at the start and writes it back at reconcile; the outer loop reads it to find pressure and mint the next issues. **Scout is purely outer-loop** (its own execution window). **Triage is invoked by the Commander inside the clean-up step** — so candidates found during a run are durably captured before the package closes — but the issues it produces are *consumed* by the outer loop. Invocation is inner; consumption is outer. This is the structural answer to the orphan-document problem: the issue is the quantum of work, and every run reads from and writes back to the same map.

## Rules inherit down the tree

Project- or section-specific quality rules (e.g. "must work with MATLAB Coder," "must be fail-safe") attach to a **node** and **inherit down its subtree.** Project-wide rules live at the root; section-specific rules attach to the relevant subtree. Any leaf gate's **implementer and reviewer both receive the union of inherited rules** in their envelope. The tree we decompose *work* along is the same tree we route *context and rules* along — one structure, both jobs.

## Anchoring (anti-orphan)

Every checklist node is anchored — to a **work-id**, to its **parent gate**, and optionally to a **Cartographer structural anchor** (`struct:<id>`). Nothing lives in isolation; a node knows its place in the work tree *and* in the project map. The Cartographer is what gives a node durable context instead of a doc floating on its own.

## State ownership

The engine owns **structured (JSON) canonical state**. Human-readable markdown, if rendered at all, is a derived courtesy view, never the interface. (Human-readability of the checklist is explicitly not a goal.)

## Engine verb set (provisional)

```
current                         the complete gate briefing: active node, FULL imperative,
                                open pre/postconditions (id/state/kind/statement) with an
                                `n/m met` summary, and the legal next verbs (#227)
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
- Concrete node + envelope JSON: drafted in `CHECKLIST_SCHEMA.md`.
- `accept` vs `advance`: resolved — `accept` folds into `advance`; the proposal/accept duality lives at the handoff between two plans.
- Representation of the frozen plan + architecture **snapshot** (decided: it is a snapshot stored as execute.json; open: how packets are referenced during execution).
- Migration order: which role's checklist conforms to the schema first (lean: conform first, restructure roles later).
