# Candidate B — seeded hypothesis: missing parent authority

Author: Lane B. Artifact only. Nothing here was implemented, committed, or chosen.
Read at integration base `efe92791` (`/tmp/constellation-20260820-integration`), plus
`.agent-work/` history in the main checkout for the measurements in §2.

---

## 1. Verdict on the seed, first, because it changes how to read the rest

**My hypothesis half survives. It is not the dominant root, and the way it is
usually stated is wrong.**

What survives: authority between plans genuinely does not exist as a nameable
relation. A parent cannot declare a child dead, cannot answer a child's request
for a waiver, and cannot be asked. That hole is real, it is systemic rather than
anecdotal (§2 measures 39 live instances of it sitting in this repository right
now), and E3 is a fair witness for it.

What does not survive: the framing "a parent cannot **reach** a child's plan."
That framing wants a downward remote control, and the evidence argues against
building one. The same dossier records lane H — a cold subagent that read a
session id out of a journal, drove a live gate, amended four downstream gates and
advanced a spine, leaving a journal that shows one session and no anomaly. A
capability that lets one agent drive another's plan is precisely the capability
lane H exercised by accident. **Adding parent reach without an authenticated
actor makes #632 worse, not better.** Any candidate that proposes "the parent may
drive the child" should be asked what stops lane H from being that parent.

What the evidence actually supports is narrower and, I think, better:

> The system has exactly one relation — *this process is bound to this path* —
> and it is being asked to carry four different jobs: **identity**, **reach**,
> **custody**, and **authority**. Parent authority is missing because authority is
> not a separate concept in this design; it is a side effect of binding. You
> cannot say "P may decide something about C" when P is not a thing, only a path.

That reading demotes my seed from root to consequence, and it also demotes the
competing "duplicated plan state" reading in the same move: the second plan file
exists because the door mints identity only where it reaches, so a Commander's
`execute.json` needs a hand-invented id (#634's own measurement). Duplication is a
symptom of the same collapse. My design therefore keeps duplication and fixes the
relation, which is what my seed predicted, but for a different reason than the
seed gave.

**And there are two roots here, not one.** The cluster splits cleanly:

| root | issues and evidence |
|---|---|
| **R1 — authority is not a named relation** | #357, #615, #369, E3, E4, the self-waive half of #638, the handshake half of E5, and the missing identity behind #634's second file |
| **R2 — the process boundary is not closed** | #632, the fixed-path half of #638, E1, E2, the archive-move half of E5 |

I designed R1, because that is my lane. **I recommend R2 be sequenced first**, and
§10 says why: this run's own three dispatches all went through the Agent tool,
not through `run_crew`, and R1 buys those dispatches almost nothing.

---

## 2. What I measured, before designing anything

All figures from `.agent-work/**` in the main checkout on 2026-08-21, 732 plan
files (a plan = a JSON object carrying both `tasks` and `items`).

**(a) The second file is the normal case, not the exception.** 593 of 732 plans
(81%) are not named `spine.json`. Child gate plans, crew plans, review plans and
survey plans outnumber spines four to one. Any design that treats a second plan
file as a defect to be eliminated is proposing to delete the majority shape.

**(b) Stranded custody is the steady state.** 56 plans currently hold an
`engine_session` with `status: active`. 52 of them sit under
`.agent-work/archive/` — finished work whose lease was never released. Excluding
paths that look like fixtures, probes and evidence scratch, **39 remain**. E3 is
not one unlucky reviewer. It is what the system does every time a run ends
without `close_work` reaching every plan.

**(c) The upward edge exists in the schema and is empty on every plan on disk.**
`spine_lifecycle.build_origin` (`scripts/spine_lifecycle.py:163-195`) writes
`origin.parent`. Of 732 plans, 40 carry an `origin` block at all, and every one of
those 40 carries exactly `{work_id, worktree, opened_by}` with
`opened_by: "init_work_area"` — including the newest ones (`567-j`, `567-l`,
`epic-567-door/cmdr-c`, and this epic's own spine). **No plan in this repository's
history carries `origin.parent`.** The field's own docstring says why it does not
matter today: *"This is PROVENANCE and nothing else... read by nothing that
decides anything."*

That is the single sharpest fact I found. The parent edge is already in the
design, already written by one code path, and deliberately inert.

**(d) One real parent capability already ships, at exactly one moment.**
`spine_lifecycle._release_child_plans` (`:838-993`) releases every declared child
plan's lease at closeout. It has the three properties a general authority
mechanism needs, already stated and already tested:

1. lineage, not directory proximity — a child is a plan some task names in
   `child_checklist`, never merely a neighbouring file;
2. honest non-owner action — released as `release --force --reason` under the
   **parent's** session id, never by echoing the child's id back, because that
   would make the ownership check tautological;
3. escape refusal — every candidate resolved and refused unless strictly inside
   the work directory.

So parent authority is not conceptually missing. It is **implemented once, for one
verb, in one direction, at one lifecycle moment, and never generalised.**

**(e) The lineage it depends on is mostly undeclared.** Only 60 of 449 plans with
tasks declare any `child_checklist` at all (13%). `generate_spine.py:677` defaults
the field to `None`. So even the one shipped parent capability usually finds
nothing to act on, and reports the rest as `unclaimed_active`.

**(f) #357's shape, current.** 85 `execute.json` plans; 49 (58%) carry
`engine_session: null`. The engine documents this as intended
(`checklist_engine.py:3744-3752`: "a child gate plan is legitimately driven with
`engine_session` staying None for its ENTIRE life, by design"). So #357 is not
describing a bug the engine is unaware of; it is disputing a decision the engine
made on purpose.

---

## 3. The design in one rule

> **Authority resolves upward at the point of use. Nothing drives downward.**

A plan does not store who may act on it. It stores who made it. When someone tries
to act, the engine walks the immutable parent edge upward and asks the ancestors
what is currently true: who holds custody, whether this plan has been superseded,
and whether any decision has been recorded that this plan is entitled to apply.

A parent never writes into a child's file. It writes decisions into **its own**
plan, and the child reads them. That single inversion is what makes the design
work across worktrees, because the only cross-checkout access it needs is a
**read** of one file whose path the reader's own immutable lineage names — not a
write, not a bind, not an identity swap.

Everything below is an elaboration of that sentence.

---

## 4. Boundaries — components and what each owns

**C1. `checklist_engine` — plan state and gate mechanics.**
Owns: the canonical state of one plan file, gate transitions, evidence, the
journal, and now *custody resolution*. Unchanged in kind: it still writes exactly
one file, the one named by `--file`. New responsibilities: consult the lineage
resolver on every mutating verb of a lineage-bearing plan; carry `actor` alongside
`session_id` on journal entries; implement the four new verbs in §5.

**C2. `lineage` — a new small stdlib-only module (~150 lines), the new seam.**
Owns: the answer to "what is this plan's chain, and what does the chain currently
say about it." Given a plan path, it resolves `origin.parent_spine` upward with a
bounded depth, read-only, refusing a cycle, refusing an unreadable link, and
returning a `Chain` record: the ordered ancestors, the live custodian (the nearest
ancestor holding an active, non-stale lease), any supersession addressed to this
plan, and any pending decisions addressed to this plan's `work_id`.
Pure except for reads. Imported by the engine, the door, the lifecycle module and
the rail — one definition, four consumers, which is the property the cartographer
result shows this cluster does not currently have.

**C3. `mcp_spine_server` — the door: identity, reach, and the process binding.**
Owns: which spine this process drives, which identity it drives it under, and what
paths it may address. **The confinement is unchanged.** A door still cannot bind a
sibling worktree's spine, and #638's own measurement (1,014 candidate spines
versus 6,102) is the reason I keep it. Two changes: the binding is keyed by
`work_id` and resolved to a path per call through the binding store rather than
frozen as an absolute path at process start; and four new tools wrap the four new
verbs. The identity a door confers stays the spine's own, never the caller's —
`IDENTITY_TRADE.md` §3 Option B ("any string it can supply, it can supply its
parent's") is a ruling I am not reopening.

**C4. `spine_lifecycle` — creation, closeout, and the sole writer of lineage.**
Owns: work areas, worktrees, branches, and the lineage edge. `open_work` becomes
the only thing that writes `origin.parent_spine` and `origin.parent_work_id`, and
it writes the matching `child_checklist`/`child_spine` declaration into the
parent at the same moment, so the edge is created in one transaction from both
ends or not at all. `_release_child_plans` is generalised into `custody_sweep`
and shared with the new `supersede` path rather than duplicated.

**C5. `run_crew` — process launch and the minting of actors.**
Owns: the environment a launched agent starts in. It is the only component that
can authenticate an actor, because it is the only thing outside the agent that
controls the agent's environment. It already does most of this: `crew_env`
assigns rather than inherits `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/
`CREW_SCRATCH_DIR` when a binding is given (`run_crew.py:1180-1228`). It gains one
thing: a minted `SPINE_ACTOR` nonce per launched process, written into the launch
registry, which the engine records on journal entries.

**C6. `hooks/spine_rail` — turn-end honesty and the session→spine binding store.**
Owns: refusing a dishonest turn-end and maintaining the binding. It gains two
duties: refuse a turn-end while this agent has an unanswered escalation it never
reported, and record when a process drives a spine under an actor the launch
registry never minted. The second is detection, not prevention (§10).

Dependency direction stays as the cartographer recorded it: `checklist_engine`
underneath, `mcp_spine_server` and `spine_lifecycle` above it, `run_crew` beside.
`lineage` goes underneath all four. Nothing new points downward into the engine.

---

## 5. Ownership and authority

### The four things that are one thing today

| concept | what it answers | where it lives in my design |
|---|---|---|
| **identity** | who is acting | actor minted by the launcher (C5); session derived from the spine (unchanged) |
| **reach** | what this process may address | the door's path confinement (unchanged) plus one read exception (§6) |
| **custody** | who may mutate this plan now | the lease, resolved upward through lineage |
| **authority** | who may decide something about this plan | the lineage chain, resolved at point of use |

### Custody, stated completely

A plan is in exactly one of four custody states, and for the first time all four
are defined:

- **unclaimed** — no lease ever. Today: unguarded (#615). Mine: unguarded **if
  the plan carries no lineage**, guarded if it does. That scoping is the whole
  answer to #615's blast-radius problem — every fixture and scratch spine in the
  suite drives verbs without claiming, and none of them carry lineage, so none of
  them change behaviour.
- **held** — an active lease. Unchanged.
- **released** — today read as absent, so unguarded. Mine: on a lineage-bearing
  plan, a mutating verb refuses and names `claim` as the remedy. This is #615's
  "claim-before-mutate" option, made affordable by the lineage scoping.
- **superseded** — new. Terminal. Declared by an ancestor. Every mutating verb
  refuses, naming who declared it, when, why, and what supersedes it.

**Custody is resolved, not stored, for child plans.** A child plan does not copy
its parent's session id at creation and then go stale when the parent is taken
over. It resolves upward: *the custodian of this plan is the custodian of the
nearest ancestor holding an active lease.* So when an Admiral force-claims an epic
spine, it acquires custody over every declared descendant in the same instant,
without a single downward write. That is precisely the guarantee #357 says a
force-claim wrongly does not buy.

### What a parent may do to a child

- **Create it**, with a lineage edge written at both ends in one transaction.
- **Read it.** Reads were never the problem.
- **Answer it** — grant or refuse an escalation the child raised, recorded in the
  parent's own plan under the parent's own authority.
- **Supersede it** — one terminal declaration, recorded in the parent's own plan,
  naming a reason and optionally a successor.
- **Release its lease at closeout** — the one existing downward write, kept (§6).

### What a parent may not do to a child

- Drive its gates: no `start`, `advance`, `attest`, `attach`, `consolidate`.
- Amend its plan, waive its conditions directly, or author its evidence.
- Pass the child's session id, ever, on any path (`_release_child_plans` already
  refuses to; the rule becomes general).
- Bind the child's spine into the parent's door.

The asymmetry is deliberate and it is the design's main safety claim: **a parent
gains the power to decide and to end, never the power to do.** An agent that has
been compromised into acting as a parent (lane H) can therefore stop a child's run
and can grant it a waiver — both loud, both recorded, both attributed — but cannot
silently produce work in the child's name, which is exactly what lane H did.

### Escalation and adjudication — the four new verbs

- `escalate --ask waive|amend|reach --target <gate>[.<cond>] --reason <text>`
  Run by the **child on its own plan**. Extends the existing `block`
  (`checklist_engine.py:2770`), which already takes a blocker, an authority and a
  next action; this adds a machine-readable ask and an id. The gate goes to
  `blocked` as it does today. The child keeps its lease.
- `adjudicate --request <id> --grant|--refuse --authority <who> --reason <text>`
  Run by the **parent on its own plan**. Writes a decision record into the
  parent's plan: `{request, child_work_id, verdict, authority, reason, ts}`.
  Touches no other file. Refuses if the named request does not resolve to a
  declared descendant.
- `apply-decision --request <id>`
  Run by the **child on its own plan**. Resolves upward, finds the decision
  addressed to its own `work_id`, and applies it locally — a granted waive lands
  through the existing `waive()` path with the **parent's** authority string and a
  pointer to the parent's decision record. Refuses if no matching decision
  resolves upward, so a child cannot fabricate a grant.
- `supersede --child <work_id> --reason <text> [--successor <path>]`
  Run by the **parent on its own plan**. Declares a descendant dead.

Note what is absent: there is no verb by which a parent writes into a child's
file. `adjudicate` and `supersede` both write only to the plan the caller is
already bound to.

---

## 6. Reach — the one boundary change, stated plainly

For upward resolution to work when the child lives in a sibling worktree — which
is the normal case, and E1's case — the child's process must be able to **read**
its parent's spine, which may be outside its own checkout.

I widen reach by exactly one predicate:

> A process may read the single file its own plan's immutable `origin.parent_spine`
> names, and, recursively, that file's own parent, to a bounded depth. Read-only.
> No write, no bind, no identity derived from it. Only decision, custody and
> supersession records addressed to the reader's own `work_id` are consumed.

Why this is a small widening and not the door's confinement in disguise:

- It is **read-only**. #638's measured refusal is about what a door may *drive*.
- It is **not caller-supplied**. The path comes from the reader's own lineage,
  written by `open_work` at creation. A model cannot name it; that is the same
  property `spine_bind` protects by deriving identity from the spine.
- It is **self-limiting**. Following it from a plan reaches the plan's own
  ancestors and nothing else. The 6,102-versus-1,014 reach delta #638 measured
  does not apply: the chain is one path, not a search.
- There is already a precedent for exactly one confined foreign read:
  `spine_advance --from_child` reads a child's `consolidation`
  (`checklist_engine.py:2633-2650`, confined by `_identity_violation`). Mine is
  the same idea pointed the other way, and confined by lineage instead of by
  directory containment — which, per §2(d) property 1, is the stronger predicate.

**The one downward write I keep.** `_release_child_plans` at closeout stays. It is
terminal, attributed to the parent, touches no gate and no evidence, and exists
because an archive must be able to claim zero active leases. I am not going to
pretend the rule is "never write downward" when one write survives. The rule is:
**authority never drives downward; exactly one terminal, attributed custody
release does.**

---

## 7. Failure semantics

**Child crashes.** Its lease goes stale by heartbeat, exactly as today. A respawn
under the same assignment session name reclaims it (`run_crew.assignment_session_name`
already guarantees a respawn reproduces the string, and `spine_bind` R9 already
allows it once stale). If no respawn is coming, an ancestor supersedes it.

**Parent crashes.** Children keep working — they hold their own leases and their
gates are unaffected. Their escalations queue unanswered. The child's `current`
shows "escalation e-1 pending, no live custodian above you," which today is
indistinguishable from silence. A successor claims the parent spine (existing
force-claim, now with `actor` recorded) and finds every pending ask in its own
`current`. **Today a dead parent loses the ask entirely; this is the clearest
day-one improvement in the design.**

**Both die (E3 exactly).** The child sits with an active lease and a dead session,
as it does now. The difference is what the next actor can do: any agent that can
claim any live ancestor of that plan can supersede it. There is always exactly
one place to go, and it is named by the plan itself.

**Takeover.** Unchanged on the spine. New: custody over declared descendants moves
with it, by resolution rather than by writing.

**Stranded plan whose ancestors are all archived.** The chain terminates in a
closed spine. That is a definition, not a puzzle: **a plan whose nearest live
ancestor is closed is dead.** The 39 stranded active leases in §2(b) all fall
under this rule and would read as dead the moment anyone touched them, with no
migration and no sweep.

**Honest residual.** All of this is resolved *at the point of use*. A superseded
child's own file still says `status: active` until someone runs a verb on it. A
human opening the JSON sees a live-looking lease. The supersession is visible in
the parent's plan and in `current` on the child, but not in the child's raw file.
This is the design's weakest point and §10 treats it as such.

---

## 8. The lived-evidence dossier — remove, keep, or replace

**E1 — the door cannot bind a sibling worktree, so every dispatched lane ran
unrailed. → REPLACED for one dispatch path, KEPT for the other. Split answer,
and the split is the honest part.**

My design does not let a parent bind a child's spine, deliberately. What replaces
the rail for dispatched work is: the child is railed *by its own door, in its own
worktree, under its own minted actor*, and the parent gets visibility through the
lineage channel — escalations arrive in the parent's `current`, consolidations
already arrive through `advance --from_child`, and supersession is the parent's to
declare. For work dispatched through `run_crew`, "unrailed by decree" is replaced
by "railed in its own process, legible upward."

For work dispatched through the harness's Agent tool — which is what this run
actually used for all three lanes — **the workaround survives**, because those
subagents are not separate processes with their own doors and there is nothing for
my design to attach to. That is a real gap and it is R2's, not R1's.

**E2 — the hand-written "do not call any `mcp__spine__*` tool" clause in every
handoff. → KEPT by my design. Closed only by R2 work I do not own.**

My design does nothing to stop an inherited `SPINE_FILE`/`SPINE_SESSION` from
letting a subagent drive the parent's spine, because the inherited session *is*
the lease holder and the engine cannot tell two processes apart under one id.
What my design adds is one thing: with `actor` minted per process and recorded per
journal entry, lane H's drive would have been **visible** afterwards instead of
indistinguishable. That is #357's option 3 and #369's ask, and it is detection,
not prevention. I would rather state that flatly than dress it up.

**E3 — the stranded dead child plan the Admiral ruled "superseded" in prose.
→ REMOVED.**

`supersede --child ... --reason ... --successor ...` in the Admiral's own spine.
The child then refuses every mutating verb with the declaration, the reason, and
the successor path. Nothing is written into the stranded file, nothing is bound
across the worktree boundary, and the record lives where the next reader is
already looking. The residual named in §7 applies: the corpse's own bytes still
read `active` until someone runs a verb.

**E4 — force-claim attribution present on the spine, absent on the child.
→ REMOVED, and the issue is already half-closed without me.**

The spine half already works: `claim()` records `previous_session_id` and
`takeover_reason` (`checklist_engine.py:1250-1259`). The child half comes from
custody resolution — the child has no stale copy of the session to be wrong about
— plus `actor` on journal entries, which separates *which job* from *which agent*
in exactly the terms #369 asked for.

**E5a — the archive-move deadlock (`git mv` on a bound spine). → REMOVED, and it
is not an authority fix.**

The door binds a `work_id` and resolves it to a path per call through the binding
store. Moving the directory does not strand the binding. I include it because the
design touches the same module, and I flag it as belonging to R2: no amount of
parent authority would have helped here. A run moving its own files is a *self*
operation.

**E5b — the five-step handshake (release → parent claims → parent waives →
parent releases → child reclaims). → REMOVED. Here is what it becomes.**

Today: 5 calls, 2 lease transitions on the child, and a cross-worktree bind that
the door refuses anyway — which is why it was performed by hand over messages.

Mine: 3 calls, 0 lease transitions, 0 binds.

1. child: `escalate --ask waive --target g4.c2 --reason "..."` — on its own plan;
   the gate blocks; the child keeps its lease.
2. parent: `adjudicate --request e-1 --grant --authority "human:tommy" --reason "..."`
   — on its own plan; writes a decision record; touches nothing else.
3. child: `apply-decision --request e-1` — on its own plan; the waiver lands
   through the existing `waive()` path carrying the parent's authority string and a
   pointer to the parent's decision record.

The child never releases. The parent never claims. Neither ever holds the other's
identity. It works across worktrees because step 3 is a read of one file the
child's own lineage names.

---

## 9. Issue dispositions

**#634 — partly closes, and I contradict one of its own stated remainders.**
The freeze shipped and the mutable middle already existed. Under my design the
"one spine per agent" goal is met by a different move: **duplication is fine, and
the `execute.json` migration named in remainder 2 becomes optional rather than
required.** What was wrong with the second file was never that it was second; it
was that it had a hand-invented identity and no declared parent. Give it lineage
and it inherits identity, custody, and authority from the spine above it. §2(a)
supports this — 81% of all plans are second files, and collapsing them means
deleting the majority shape. Remainders 1 (crew half) and 4 (`current` does not
render the freeze) survive as small work and I would keep them. Remainder 3
(freeze protects completion, not acceptance) is a rigor-dial decision my design
does not touch.

**#638 — partly closes, and is revealed as two issues that should be split.**
The authority half (symptom 1, the unwalkable escalation path) closes completely
via §8 E5b. The path half (symptom 2, archive-move) closes via the `work_id`
binding, which is unrelated work in the same file. The identity half — one
identity fixed at bind — I **deliberately keep refused**, and I think the issue's
proposal to let a door "re-target identity under a named authority" is the one
part of it that should be rejected outright: it is a request to make impersonation
legal, and lane H is the argument against.

**#632 — leaves open.** My design does not close it and I will not claim
otherwise. It converts the failure from invisible to visible (per-entry `actor`),
which is worth having and is not what the issue asks for. Its remedy shape —
"a helper should start with an environment chosen for it" — is R2 work in
`run_crew` and the harness dispatch path, and it should be done first.

**#357 — closes.** Custody resolution puts the lease exactly where the gates are.
The issue's own comment shows why the obvious fix fails: refusing session-less
mutating verbs outright "would break every crew-driven gate in the fleet," and
58% of `execute.json` plans on disk carry a null session today (§2(f)). Resolution
rather than propagation solves that without a migration: a lineage-bearing child
resolves its custodian upward; a lineage-free legacy child behaves exactly as it
does now, forever. The issue's own trap warning is respected — the guard sits in
`require_session`, on the verb path, not in a new checker nothing calls.

**#369 — mostly already fixed; the live remainder is E3 in another costume, and
one half should be closed as doctrine rather than architecture.**
The spine-level attribution complaint is already addressed (E4). The child-level
half closes with custody resolution and `actor`. The narrative-channel half — an
orchestrator misattributing a commit in prose — the issue itself says is "not a
system property, it is a disposition." I agree, and I would close that half by
adopting its own modest proposal (attribution in prose carries a resolvable
pointer) as doctrine, not by building anything. Recommend re-scoping the issue to
"actor field on journal entries plus child custody," and closing the rest.

**#615 — closes, with an explicit ruling on the question it leaves open.**
The question it asks — "should driving a leaseless spine require anything at
all?" — gets a two-part answer: **yes if the plan carries lineage** (claim before
mutate, released is not a free-for-all, and a superseded plan refuses outright),
**no if it does not** (documented as unguarded by design, which is the issue's own
third option). That combination is the only one I can find that does not detonate
the suite, since every fixture and scratch spine is lineage-free.

---

## 10. Risks, and what would falsify this

**R1. The strongest evidence against my own lane is in this run's own conduct.**
All three of this epic's wave-2 dispatches went through the Agent tool, not
`run_crew`. My design's benefits attach to processes that `run_crew` launches and
that own their own door. If the fleet's real dispatch mix is mostly in-harness
subagents, then R2 dominates and my whole design is second-order.
*Falsifier, cheap:* count the next twenty dispatches by path. If fewer than half
go through `run_crew`, build R2 first and revisit this.

**R2. Upward reads may not be available when they are needed.** The child must be
able to read the parent's spine file. A pruned worktree, a different machine, a
permissions boundary, or an archived-and-moved parent all break it.
*Falsifier:* take the last ten real crew dispatches and test whether the child
process could `open()` its parent's spine at the moment it was running. If a
material fraction could not, upward resolution is the wrong shape and the design
needs a broker instead of a file read.

**R3. Point-of-use resolution does not mark the corpse.** §7's residual. A
superseded plan's own bytes keep saying `active`. If the human's real requirement
is "a reader opening the child file must see it is dead," then upward resolution
is wrong for the dead case specifically, and a downward stamp is needed after all
— which would reopen the "never drive downward" rule I built the design on.
*Falsifier:* ask the human whether E3's fix has to be visible in the file or
visible at the next use. My design answers "next use." I am not certain that is
the answer they want.

**R4. The actor nonce is not a boundary.** An agent can read and set its own
environment. A launcher-minted `SPINE_ACTOR` makes the default right and makes
deviation visible; it does not stop a determined forgery. #632 argues that is the
correct target ("why this is not a security issue"), and I lean on that argument,
which means if the human disagrees with #632's framing, this part of the design
is under-built.
*Falsifier:* one attempt to forge an actor in a probe. It will succeed. The
question is whether that matters.

**R5. Resolution cost and depth.** Every mutating verb on a lineage-bearing plan
pays one to N file reads. Depth is bounded and N is 2-3 in practice, but this puts
filesystem reads back on the verb path that #609 just finished taking off it. That
is a direction the project has recently moved *away* from, and someone should say
whether re-crossing it is acceptable.

**R6. Lineage is hand-forgeable, like everything else here.** If a spine's
`origin.parent_spine` can be edited, authority can be pointed anywhere. The
mitigation is that hand-editing spines is already forbidden and already caused a
lease deadlock in this project. That is a norm, not a mechanism.
*Falsifier:* find one plan in the archive whose lineage block was not written by
`open_work`.

**Guesses, marked as such:** that the journal's hash chain can take an additive
`actor` field with a version marker without invalidating existing chains (I read
`append_journal_entry` at `:3660` and the field ordering feeds `_journal_hash`, but
I did not test a mixed-version verification); that `episode_capture` and the gauge
reader do not treat `engine_session.session_id` as the actor in a way that breaks
when `actor` diverges from it; and that no test asserts the exact key set of
`origin`.

---

## 11. Tests — what would have to pass to believe this landed

**Custody**
1. A lineage-bearing child plan, no lease, mutating verb from any session:
   REFUSED, naming `claim`. The same file with the lineage block removed: exit 0.
   (Proves #615's scoping is real and the suite's fixtures are untouched.)
2. Parent force-claims the spine; a verb on the declared child from the previous
   custodian's session: REFUSED. From the new custodian's: exit 0. No write to
   the child file occurred between the two — assert its mtime is unchanged.
   (Proves #357 closes by resolution, not propagation.)
3. The 49 real `execute.json` plans with `engine_session: null` and no lineage
   drive exactly as they do today. Byte-identical outcomes.

**Authority**
4. E5b as a three-call integration test, with the child in a sibling worktree and
   the parent in the main checkout. Assert: three calls, no `claim`, no `release`,
   no `spine_bind`, and the resulting waiver on the child names the parent's
   authority string and carries a pointer to the parent's decision record.
5. A parent attempts `start`, `advance`, `attest`, `attach` and `amend` on a
   declared child. All five REFUSED, each naming the same rule.
6. A child calls `apply-decision` for a request the parent never granted:
   REFUSED. A child fabricates a decision record in its own plan and calls
   `apply-decision`: REFUSED (the record must resolve upward, not locally).

**Death**
7. E3, replayed on the exact stranded plan: an Admiral supersedes it from its own
   spine; the next mutating verb on the stranded plan is REFUSED with the reason
   and successor; `current` on the stranded plan renders the declaration.
8. A plan whose nearest live ancestor is a closed spine reads as dead with no
   verb having been run against it. Assert against three of the 39 real stranded
   leases in `.agent-work/archive/`.

**Reach**
9. A process may read the one file its lineage names and nothing else: a plan
   whose `origin.parent_spine` points outside its checkout resolves; a plan
   pointing at an arbitrary sibling spine that no lineage names does not.
10. Cycle and depth: a self-referencing lineage and a 50-deep chain both refuse
    cleanly rather than hanging. Fail-open on an unreadable link, matching the
    rail's own contract.

**Attribution**
11. Journal entries from two processes under one session id are distinguishable
    by `actor`. Replay lane H's sequence and assert the anomaly is visible in the
    journal, which is the property the incident report says was absent.

**Migration**
12. Every stage in §12 leaves `python -m pytest -q` green at 3447 passed / 6
    skipped / 1222 subtests, or names the exact tests it changes and why.

---

## 12. Migration — stages that each leave the system working

**Stage 0 — lineage, write-only.** `open_work` writes `origin.parent_spine` and
`origin.parent_work_id`, and writes the reciprocal `child_checklist` declaration
into the parent in the same call. Nothing reads either. *Breaks:* nothing. *Note:*
§2(c) shows no plan on disk carries `origin.parent` today, and §2(c) also shows no
plan on disk was minted by `open_work` at all — every `origin` block came from
`init_work_area`. So stage 0 must land in `init_work_area` too, or it lands in a
path this repository does not use. **That is the first thing to check and it is
easy to get wrong.**

**Stage 1 — the `lineage` module, plus `current` rendering.** Read-only, decides
nothing. Ships with tests 9 and 10. *Breaks:* nothing.

**Stage 2 — `actor` on journal entries.** Additive field with a chain version
marker; legacy entries verify under v1 rules. *Breaks:* anything that hashes or
schema-validates journal lines. Check `verify_*` scripts and `episode_capture`
before this lands.

**Stage 3 — `supersede` and upward death resolution.** The first stage that
refuses something that used to pass, and the blast radius is deliberately tiny:
only a plan an ancestor has explicitly declared dead. Ships tests 7 and 8. This is
the stage that closes E3, and it is worth landing early because it is the highest
value per line in the whole design.

**Stage 4 — `escalate` / `adjudicate` / `apply-decision`.** Purely additive verbs
plus four door tools. Ships tests 4, 5, 6. Closes E5b and #638's symptom 1.

**Stage 5 — custody resolution in `require_session`.** The stage with real risk.
Only lineage-bearing plans are affected, which after stages 0-4 means only plans
minted since stage 0. Ships tests 1, 2, 3. *Breaks:* any post-stage-0 run that
drove a released child plan without reclaiming. Expect fallout in Commander runs
specifically.

**Stage 6 — `work_id` binding with per-call path resolution.** Independent of
everything above; closes E5a. *Breaks:* anything asserting `SPINE_FILE` is stable
for a process's lifetime.

**Recommended sequencing against the other root:** R2 (closed launch environment;
harness-dispatch actor minting) should go **before** stage 5 and arguably before
stage 3. It is the root this run actually tripped over three times in one session,
and it is the one my lane does not own.
