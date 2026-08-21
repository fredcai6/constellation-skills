# Candidate A — Actors and Grants

**Lane A. Assigned hypothesis: the dominant root cause is DUPLICATED PLAN STATE.**

**Verdict on the assigned hypothesis: it does not survive. Duplicated plan state
is real, is measurable, and is a genuine amplifier — but it is a *consequence*,
and the evidence shows what it is a consequence of.** The design below is the
one the evidence supports, not the one my seed asked for. Section 2 shows my
work, including the falsification tests I ran against my own premise.

Everything here is read off `/tmp/constellation-20260820-integration` at
`efe92791`, root `map/`, the six issues in full, and the lived-evidence dossier.
Guesses are marked **[GUESS]**.

---

## 1. Headline

The system has three layers that can act on a plan — the engine CLI, the MCP
door, and the harness hooks — and **each layer answers "who may act?" with a
different noun, and the layer with the most power has the fewest guards.** The
engine CLI is unconfined, per-call and self-asserted. The door is tightly
guarded but its unit of authority is a *process bound to one path*, which is
smaller than the work and cannot reach a sibling worktree. The hooks are the
only layer that knows which *agent* is calling, and the only thing they can say
is yes or no to a whole tool. Every one of the six issues is a place where those
three answers fail to compose.

The design replaces the one overloaded noun (`session_id`, which today names a
plan, a lease, an actor and a process binding at once) with three: an **actor**
with an identity that is not derived from any plan, a **grant** that says which
plans an actor may drive, and a **lineage edge** that says which actor dispatched
which. Authority moves out of "do these two strings match?" and into "does the
roster show this actor holding, or standing above, a grant on this plan?" —
enforced at the one choke point that already exists,
`checklist_engine.require_session`, so it cannot become a check nothing calls.

---

## 2. Testing my own hypothesis, and why it failed

The premise I was given: the trouble comes from more than one plan being in play
with no single answer to "which plan am I in?", and #634's "one spine per agent"
is the clearest statement of it.

The strongest version of that reading is genuinely strong, and I want the human
to have it before I take it apart. It goes: `execute.json` and
`interrogation.json` are second plans that no door can reach, so they are driven
through the unguarded CLI under **hand-invented session strings** — #634 measured
two lanes inventing two different formats (`commander-567-d1-execute`,
`constellation/567-e/execute`) for the same thing. #357 then measures the
consequence directly: the lease sits on `spine.json` while **all the gates live
in `execute.json`**, so a force-claim of the spine buys exclusivity over nothing,
and on issue-305, 33 of 34 mutating verbs on the gate plan carried no session at
all. That is a clean causal chain from plan duplication to a lease that protects
nothing, and it is measured twice on live runs. It deserves to be taken
seriously.

I then ran the obvious falsification test: **assume #634 lands in full — one
spine per agent, no second files anywhere — and re-read each piece of lived
evidence.** Four of the five survive untouched.

| evidence | survives "one spine per agent"? | why |
|---|---|---|
| E1 — parent cannot bind a child's spine in a sibling worktree | **survives** | The child has exactly one spine, correctly. The door still refuses it on path, and the refusal is about checkouts, not about counts. |
| E2 — helper inherits the launcher's binding | **survives** | This is the *dual* of duplication: one plan, two agents. Merging files cannot help; the subagent shares the parent's door process. |
| E3 — dead session's lease on a child plan | **survives** | The stranded plan was a dispatched **Reviewer's own spine** in its own worktree — one agent, one spine, already the #634 shape. It is still stranded. |
| E4 — force-claim attribution | **survives** | Attribution is a property of the id, not of how many plans exist. |
| E5 — self-waive handshake | **survives** | A crew waiving its own bound spine's check is a one-plan-one-agent situation. The refusal is correct; the parent still cannot act. |
| E5 — archive-move deadlock | **survives** | One spine, moved. The door's cached absolute path is what breaks. |
| #357 | **partly dissolves** | Gates in the spine means the lease covers the gates. But see below. |

Only #357 moves, and it does not dissolve cleanly. #357's own comment says the
session-less path is the *main* path because **crews** drive the child gate plan,
and crews are separate agents. Under one-spine-per-agent, a crew driving the
Commander's gates is either (a) a second agent on one plan — which is exactly the
E2 violation — or (b) the crew drives its own spine and the Commander closes its
gate on the crew's verdict, which is `advance --from_child`, a seam #634's own
comment insists must survive. So #357 re-forms as a delegation question rather
than dissolving. Duplication was never the thing holding it up.

Then I read #634's own causal direction, and it points the other way from my
seed. Its words: the Commander's `execute.json`, the Interrogator's
`interrogation.json` and an in-session crew's own plan "**reach the engine
outside the door, because a door binds one spine and these are second files**."
The door's unit choice comes first; the second files are the workaround; the
invented ids are the cost of the workaround. Duplication is downstream of the
door's binding unit, and the invented ids are downstream of duplication.

**So: my hypothesis is a middle link in a chain, not the head of it.** I keep
one thing from it, and it is not small — the *specific* damage duplication does
is that it multiplies unattributed drive-surfaces, and that damage is real and
measured. But designing at that link would fix the second files and leave E1,
E2, E3, E4 and both halves of E5 exactly where they are.

### What the evidence actually supports

Read at source, the current authority topology is this:

| layer | knows | unit of authority | guards |
|---|---|---|---|
| `checklist_engine` CLI | nothing about the caller | a `--file` path, per call | `require_session` only, and it **returns early when there is no active lease** (`checklist_engine.py:1140`). `origin_worktree_refusal` was deleted in #609. |
| `mcp_spine_server` door | the bound spine and its derived session | one process, one spine, one path, confined to `<own checkout>/.agent-work/` | ten refusals on `spine_bind` alone, `_identity_violation` asking argparse rather than scanning tokens, per-call `_unbound_refusal` |
| harness hooks (`spine_rail`, the launcher's `PreToolUse`) | **the true acting agent** — `binding_key()` composes `<session_id>#<agent_id>`, and `tests/fixtures/probe_payloads.jsonl` shows two subagents under one session with distinct harness-issued agent ids | one tool name | allow / deny a whole tool |

Three facts follow directly, and each explains issues the duplication reading
cannot:

1. **Identity is derived from the plan, never from the actor.**
   `spine_lifecycle.session_id_for(work_id)` is `f"constellation/{work_id}"` —
   "The ONE definition", pure by design so that binding a spine yields the same
   identity as being launched with it. That property is exactly what makes the
   id name a *plan*. So an agent needing a second scope of work must mint a
   second plan to get a second identity (#634), a successor reusing an id becomes
   indistinguishable from its predecessor (#369), and a door can bind only one
   plan because binding two would mean holding two identities (#638).

2. **Authority has no hierarchy to express itself in.** The human's ruling is a
   hierarchy — *"agent cannot waive itself. I'll allow commander to waive crew,
   admiral to waive commander, human for admiral. always ask up"* — and it is
   implemented, verbatim in `run_crew.py:790`, as a `PreToolUse` hook that denies
   `action=waive` to **every** spawned crew on **every** plan. `checklist_engine.waive()`
   itself has no self-waive check at all; `--authority` is a free string. So the
   rule is simultaneously too broad (a Commander cannot waive its crew's check
   through the door either) and too narrow (an `external`-backend crew or an
   Agent-tool subagent gets no hook and can self-waive freely). E5's five-step
   handshake is what a flat deny plus a per-file lease produces: the only way to
   say "my parent waives for me" is to physically hand the file over.

3. **There are two liveness models, 16× apart, and the engine's is the blind
   one.** `checklist_engine._is_stale` reads `last_heartbeat` only, with
   `DEFAULT_LEASE_STALE_SECONDS = 1800`; the lease record carries **no pid and no
   host**. `run_crew.entry_liveness` is three-state and *pid-corroborated*, with
   `HEARTBEAT_STALE_SECONDS = 28800`. #357's comment lists exactly the death
   signals that are "all consistent with a commander that is still running" — and
   the one signal that is not, a live process, is the one the engine cannot see.

The root, stated in one line: **the system identifies a plan and calls it an
actor, and then asks that one string to answer four different questions —
which plan, who holds it, who acted, and which process is bound.** Duplicated
plan state and missing parent authority are both consequences: the first is what
you get when the only way to mint an identity is to mint a plan; the second is
what you get when there is no actor graph to be a parent in. That is close to
the packet's third option ("an interaction between them"), but sharper: they are
not interacting peers, they are siblings with a common parent.

---

## 3. Boundaries — components and what each owns

Four components, three of which exist today. The dependency direction is chosen
to fit the graph the map actually records (`checklist_engine` at the bottom
importing only stdlib plus `episode_capture`; `mcp_spine_server` and
`spine_lifecycle` above it; `spine_lifecycle` above `run_crew`).

### C1. `run_roster` — **new**, and it must sit at the bottom

A stdlib-only module, importable by `checklist_engine` without creating a cycle.
It owns three record types and nothing else:

- **Actor** — `actor_id`, `role`, `parent_actor_id`, `worktree`, `pid`, `host`,
  `started_at`, `last_seen`, `disposition` ∈ {`live`, `stood-down`,
  `declared-dead`}, and for `declared-dead`: `declared_by`, `declared_at`,
  `reason`.
- **Grant** — `(actor_id, plan_path, work_id, mode)` where mode is `drive` or
  `observe`. A grant is what a lease points at; it is not itself the lease.
- **Lineage** — the parent edge, which is just `parent_actor_id`, but read
  transitively: `is_ancestor(a, b)`.

It also owns **the one liveness predicate**. `run_crew.entry_liveness`'s
three-state, pid-corroborated logic moves down here and both the engine and the
launcher call it. Today the engine and the launcher disagree by 16× about when
an agent is dead; after this they cannot disagree at all.

Store location: the **main checkout**, not the worktree. This is not a new
hazard — `agent_work_root.durable_root()` already redirects durable run records
to the main checkout for linked worktrees, and already scans
`<main>/.agent-work/*/spine.json` cross-worktree to decide something. A
fleet-scope store is an existing shipped pattern here. Writes go through the
advisory-lock transaction `spine_rail._binding_transaction` already implements
for #441 (which was written after a measured file-tearing incident under 16
concurrent writers) — reused, not reinvented.

**What it does not own:** gate state, evidence, verdicts, anything about the
content of work. It is an index of who and where, never of what.

### C2. `checklist_engine` — owns plan state, and stays the only enforcement point

Unchanged in what it owns: gate status, conditions, evidence, `why_trail`,
`amendments`, the hash-chained journal, and the `engine_session` lease record.

One thing changes, in one function. `require_session` stops comparing two
strings and starts asking `run_roster` a three-way question: is this actor the
holder, an authorized ancestor of the holder, or neither? And its
leaseless early return goes (that is #615).

This placement is deliberate and is the single most important constraint on the
whole design. #357 names the trap explicitly: *"do not fix this by adding a check
nothing calls. The isolation rule already exists in prose and already failed. A
guard that lives anywhere other than the verb path inherits exactly the defect
being fixed."* The roster earns its existence only if `require_session` is its
only authority consumer.

### C3. `mcp_spine_server` (the door) — owns the *authenticated* path

The door's binding unit changes from **one process, one plan** to **one actor,
one grant set**. Its three capabilities separate:

- **drive** — as today, plus one new condition: the roster shows a `drive` grant
  for the calling actor on that plan. Path confinement is **kept exactly as it
  is**; #638's own measurement (anchoring at the primary checkout admits 6,102
  candidate spines against 1,014) argues for keeping it and I am not touching it.
- **observe** — new, read-only, roster-scoped rather than path-scoped: an actor
  may read the status of any plan held by a strict descendant, in any worktree.
  No verb, no mutation, no lease effect.
- **supervise** — new, a narrow mutating set an ancestor may exercise on a
  descendant's plan *without binding to it*: `declare-dead`, `waive-for`,
  `release-child`, `revoke-grant`, `adopt`. Each requires the lineage edge, each
  demands a reason, each is journaled **into the child's own journal, attributed
  to the acting ancestor**.

### C4. `run_crew` / `spine_lifecycle` — own dispatch and lifecycle, and become the roster's writers

`run_crew` already carries role, parent, worktree, pid, heartbeat and abandonment
detection in `crew-runs.json`; it keeps that registry and additionally writes the
actor and the lineage edge into the roster at dispatch. `spine_lifecycle`'s
`open_work`/`finish_work` register and retire actors.

The important change is what happens to the environment variables. Today
`crew_env()` assigns `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`/`CREW_SCRATCH_DIR`
correctly and deliberately — the launcher is not the defect. The defect is that
those variables are the *fact*, so any process that inherits them inherits the
authority. Under this design they become a **convenience copy of a roster fact**:
a helper that inherits `SPINE_FILE` and `SPINE_SESSION` but holds no grant is
refused at `require_session`. Nobody has to strip anything.

---

## 4. Ownership and authority — the rules

1. **An actor may drive a plan it holds a `drive` grant on.** One holder at a
   time; the lease record stays where it is, and gains `actor_id`, `pid` and
   `host` so staleness is corroborable rather than guessed.
2. **An actor may observe any plan held by a strict descendant**, in any
   worktree, read-only.
3. **An actor may supervise only a strict descendant.** Never a sibling, never
   an ancestor, never itself. Self-supervision is refused *in the engine*, which
   is where the human's "agent cannot waive itself" ruling belongs. The launcher's
   blanket `PreToolUse` waive-deny is then retired: one rule that is neither too
   broad nor too narrow, and that applies to `external`-backend crews and
   Agent-tool subagents which the hook never reached.
4. **A parent may not do a child's work.** No advancing a child's gate, no
   attesting a child's condition, no authoring a child's evidence. The only route
   from a child's work to a parent's gate remains `advance --from_child`, which
   #634 correctly reads as a legitimate cross-agent verdict seam (and which
   refuses on BLOCK while still attaching the evidence, so a rejection cannot be
   laundered into a pass). It gains exactly one condition: the child must be a
   **declared descendant in the roster**. Today `advance()` will read any JSON
   file with a `consolidation` key, and lineage is enforced only by the door's
   path containment — a live measurement recorded in `_identity_violation`'s own
   docstring shows a `from_child` outside the binding advancing a gate on a
   fabricated APPROVE.
5. **Nobody impersonates.** Passing another actor's id becomes a refusal.
   Today the engine's own refusal text *recommends* it: `require_session` raises
   "pass `--session-id '<the holder's>'` or take over with `claim --force
   --reason`" — and #638 already noticed that **both remedies that message names
   are filed defects** (#632 impersonation, #369 attribution erasure). Fixing
   that sentence is a stage-0 item worth doing whichever architecture wins.

### What authentication this actually buys — stated honestly

The harness issues an `agent_id` that the model never types; it arrives in the
hook payload out of band, and `tests/fixtures/probe_payloads.jsonl` shows two
subagents under one session id carrying distinct ones. So **door calls can be
authenticated**: a `PreToolUse` hook on `mcp__spine__*` sees the real acting
agent, and denies the call when that agent holds no grant on the bound plan.
This satisfies #632's rule — *"stop authenticating lease ownership by a string
readable out of the very file being mutated"* — for the door path.

It does **not** authenticate the CLI path. An agent typing
`python scripts/checklist_engine.py --file X --session-id Y` can assert anything,
and chasing that through a `PreToolUse` hook on `Bash` would be shell-parsing
whack-a-mole — the exact failure `_identity_violation`'s docstring records six
consecutive times ("enumerating spellings is the defect"). So the design does not
promise it. Instead it makes the difference **visible**: every journal entry
records `actor` and `actor_attested: harness | self`, and both fields go into
`_journal_hash`'s key whitelist so the chain actually commits to them. Adding
them outside that whitelist would leave the attribution fix unprotected by the
very chain that exists to prove a run was driven rather than asserted.

Threat posture, adopted from #632 verbatim: *"Framing it as impersonation
invites a defend-the-attacker design."* This is coordination between cooperating
agents. The design's goal is that the **ordinary mistake becomes closed**, not
that a determined actor is stopped.

---

## 5. Failure semantics

**Crash.** The actor's roster entry carries a pid (cli backend) or a heartbeat
(external). Liveness resolves through the one shared three-state predicate:
`active` / `stale` / `unknown`, with `unknown` failing toward active exactly as
`entry_liveness` already does. A crashed actor's grants become *reclaimable*,
never *free*.

**Takeover.** Two sanctioned routes. (a) The same actor re-attaching — the
idempotent resume that already exists. (b) A **roster ancestor** declaring the
holder dead and re-granting. `claim --force` by an unrelated actor stops being
the ordinary route and survives only as a human-authority escape, recorded with
`authority: human`. This gives #369's resume-side obligation a mechanism instead
of an exhortation: the re-grant is refused unless liveness reads corroborated
`stale`, or an ancestor explicitly declares death with a reason.

**Dead session holding a lease — E3's case.** An ancestor calls `declare-dead`
on the descendant actor. Four mechanical effects: the actor's disposition
becomes `declared-dead` with who/when/why; every grant it held is revoked; every
plan it held gains a `superseded` block naming the declaring actor and the
reason, **written into the child plan file itself so the next reader sees it**;
and an entry lands in the child's journal attributed to the ancestor, never to
the dead actor. That is the whole of E3's design obligation.

**Stranded plan with no roster entry.** Real, and unavoidable during migration
and forever after for hand-made plans. Such a plan is **adoptable**: an ancestor
may name it and adopt it into the roster, recorded. Refused if any live actor
holds a grant on it. Without this the design cannot handle the existing corpus.

**Leaseless plan — #615.** `require_session`'s early return goes, but scoped:
a mutating verb on a plan carrying `origin.work_id` with no active grant is
refused and names the remedy; a plan with no `origin` (fixtures, scratch,
templates) stays unguarded. That scoping is what keeps the 3447-test suite
alive, and it is the honest reading of #615's own warning that claim-before-mutate
carries "the biggest blast radius, since every fixture and scratch spine in the
suite drives verbs without claiming."

**A door whose plan file moves underneath it — E5's archive-move deadlock.**
`_bind_process_to` resolves and caches an absolute path. Under this design the
binding is to `(actor, work_id)` and the path is resolved per call from the
roster. The repo already discovered the per-call principle for the adjacent
question — `_unbound_refusal` is documented as "asked per call, never cached"
precisely because "the bound spine's directory can be removed while this process
runs (issue #604)" — and simply did not extend it to the binding itself.

---

## 6. The acceptance tests I cannot skip — E1 through E5

### E1 — the door's binding is fixed to one checkout — **REPLACED**

The workaround was: declare every dispatched crew lane unrailed, and hand-write
the prohibition into each handoff. That goes. Dispatched lanes are
roster-registered actors with their own grants, and the Admiral gets read-only
`observe` across worktrees, so the rail's audit value returns for dispatched work.

**Replaced, not removed**, and here is the residue: an Admiral still cannot
*drive* a child's plan in a sibling worktree. Drive-binding stays confined
exactly as today, because #638's own 1014-vs-6102 measurement is a good argument
and I am not overturning it. A parent that wants something done in a child's
plan supervises it by named verb or dispatches into it — it never becomes the
driver of a run it cannot see.

**One correction to E1's neighbouring claim, offered because the brief prizes
honest findings.** E3 says of the stranded plan "there is no verb that reclaims
it from outside." At the *door* that is exactly right. At the **engine CLI** it
is not: `origin_worktree_refusal` was deleted in #609, `require_session` returns
early with no active lease, and the CLI takes `--file` per call with no
confinement at all. The stranded plan's heartbeat was `02:15:01Z`, so under
`DEFAULT_LEASE_STALE_SECONDS = 1800` its lease read *stale* from `02:45:01Z`
onward and a plain `claim` — not even `--force` — would have taken it from any
directory on the machine. What blocked the Admiral was **doctrine, not
mechanism**: hand-driving the engine is forbidden here, and the CLI is
positioned in the door's own text as "an operator/debug path, not an instruction
aimed at [an agent]". That is the sharpest single statement of this cluster's
real shape — *the guarded path cannot reach the problem and the unguarded path
is held back only by prose* — and any candidate that closes the door-side gap
without narrowing the CLI has moved the hazard rather than removed it.

### E2 — helper agents inherit the launcher's spine — **REMOVED**

No hand-written prohibition clause in any handoff. A helper that inherits
`SPINE_FILE` and `SPINE_SESSION` but holds no roster grant is refused on its
first mutating verb, at `require_session`, with a message naming registration as
the remedy. The failure is closed, not prose-guarded.

Who guarantees it: nobody has to. The dispatcher is not asked to strip four
variables; the variables simply stop being the fact. If a dispatcher forgets
everything, the worst outcome is a helper that gets a clean refusal instead of a
silent hijack — which is the inverse of Lane G's and Lane H's outcomes in #632.

Residue I am *not* claiming to fix: the `CREW_SCRATCH_DIR` leak that reds
`test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
is a test built on ambient `os.environ`. That is a test defect, not an
architecture one, and it should be routed out separately rather than absorbed
into an architecture decision.

### E3 — a dead session's lease on a child plan — **REMOVED**

One call: an ancestor's `declare-dead` on the dead actor. The stranded plan
carries the supersession where the next reader will see it, the journal carries
the ancestor's attribution, and the dead actor's grants are gone. The Admiral's
hand-written "I rule this superseded" in a log stops being the only record.

### E4 — force-claim attribution — **PARTLY REMOVED, and one half deliberately KEPT**

The spine half is, as E4 says, already addressed: `claim --force` records
`previous_session_id` and `takeover_reason` today, verified at
`checklist_engine.py:1246-1258`. The child half closes by the same mechanism as
E3, plus the per-entry `actor` / `actor_attested` fields going into the journal
hash.

**Kept: the narrative channel.** #369's comment is about an orchestrator writing
a close-out note that credits the wrong agent, caught only because the agent
declined credit — "it is not a property the system detects." I propose no
mechanism for that and I do not think one exists. What the design adds is the
*pointer discipline* #369 itself asks for: with `actor` in the chained journal,
a prose attribution becomes resolvable against something. It becomes falsifiable,
not automatic. That is an acceptable place to stop, and pretending otherwise
would be the kind of claim this cluster exists to punish.

### E5 — the prior-run lessons — **BOTH REMOVED**

**Archive-move deadlock: removed.** The door binds `(actor, work_id)` and
resolves the path per call. `git mv` of a bound `spine.json` updates the roster
and the next `release` resolves the new path. No temp-copy-back.

**The five-step handshake: removed, and here is what the sequence becomes.**

Today:
```
child:  spine_lease release
parent: spine_lease claim  (--force, on the child's spine)
parent: spine_evidence waive
parent: spine_lease release
child:  spine_lease claim  (reclaim)
```
Five calls, two agents, a window in which the child holds nothing, and — because
`claim --force` is in the middle of it — an attribution smear on the child's own
journal for a run the child is still executing.

Under this design:
```
parent: spine_supervise waive-for --plan <child's plan> --cond c3 \
        --authority <parent actor> --reason "..."
```
One call. The child never releases and never reclaims; its grant is untouched
and its lease is never disturbed; the parent never becomes the plan's driver,
because `waive-for` is a supervision act rather than a bind. The child's journal
records a `waive` attributed to the parent actor with `on_behalf_of` naming the
child — the first time in this system that "my parent did this for me" is
expressible at all. The child's own self-waive stays refused, which #638
correctly insists is the right refusal; what changes is that the sanctioned
alternative finally has a mechanism instead of a dance.

---

## 7. Issue dispositions

**#634 — *partly closed; its remedy is mis-scoped relative to its own evidence.***
The issue measures four costs: (a) hand-invented session ids on the second-file
path, (b) that path reaching the engine outside the door, (c) an Admiral's
two-wave, nine-lane epic structure living in `ADMIRAL_LOG.md` outside the spine,
(d) `current` not rendering the freeze. This design closes (a) and (b) directly —
one actor holds grants on both `spine.json` and `execute.json`, so there is one
identity and both are reachable through the door — **without merging the files**.
(d) is a small projection fix, unrelated to identity, and should be split out.
(c) is a genuine want that file-merging does serve and my design does not: an
Admiral's waves stay outside the engine. So the disposition is: the *evidence* in
#634 is about identity, and "one spine per agent" is a stronger remedy than the
evidence supports. **One actor per binding** is what the evidence supports.
I want to be blunt that this reverses a deliberate, AST-pinned repo decision
(`decision:one-spine-per-process-stands`, pinned by
`tests/test_mcp_lifecycle.py::OneBinderPinTests`) — see Risks.

**#638 — *partly closed.*** Both named symptoms go: the self-waive escalation
gets a real mechanism (supervision verbs), and the archive-move deadlock goes
with per-call path resolution. Of the three assumptions the issue tabulates, the
design reverses two — one spine per process, and one identity fixed at bind — and
**deliberately preserves the third**, one checkout's work-area tree per drive
binding, because the issue's own measurement is the best argument for keeping it.
What stays open: the CLI's total absence of confinement, which #638 does not
raise but which E1 above shows is the same hazard on the other side.

**#632 — *closed.*** Mechanism replaces prose. The remaining item in the issue
(the `CREW_SCRATCH_DIR` test leak) is a test defect and should be re-routed.

**#357 — *closed at the mechanism level, and its own recommendation was already
half-withdrawn.*** The issue recommends fix #2 (refuse session-less mutating
verbs) as an immediate guard; its own follow-up comment withdraws that, correctly,
on the measurement that the session-less path is the main path — 33 of 34
mutating verbs on issue-305's gate plan. This design implements the issue's
durable option #1, propagation, but as a **grant** rather than an inheritance:
the crew gets its own actor with its own grant on the child plan, so those 33
verbs become 33 attributed verbs by a *different* actor rather than 33 verbs
wearing the Commander's id. That is a better outcome than propagation-as-copying,
which would have re-created #369's attribution smear at the gate layer.

**#369 — *mostly already fixed on one surface; closed on the second; deliberately
left open on the third.*** Surface 1, the spine's own takeover record: already
there, as E4 found. Surface 2, the child plan: closed by the same mechanism as
E3, plus `actor` in the hash-chained journal. Surface 3, the narrative channel:
left open, no mechanism proposed, reasoning in §6/E4. The issue is therefore
smaller than it reads, and I would expect a reconciliation lane to find that its
live half really is E3 in another costume — E4's own suspicion, and I agree with
it.

**#615 — *closed, last, and it is the change I would drop first.*** Its own third
option ("accept it explicitly — document that a leaseless spine is unguarded by
design") is a legitimate cheaper answer. The version here is its second and third
options merged: guard plans that carry an `origin.work_id`, leave origin-less
fixtures alone, document the residue. If only part of this architecture could
land, stage 4c is the piece with the worst benefit-to-blast-radius ratio.

---

## 8. Migration — stages that each leave the system working

**Stage 0 — text and fields, no behavior change.**
Fix `require_session`'s refusal so it stops recommending two filed defects. Add
`actor`, `actor_attested`, `pid` and `host` as additive fields on the lease and
the journal entry, and add the two journal fields to `_journal_hash`'s key
whitelist. *Breaks:* nothing. Old journal entries verify against their own
recorded hashes; the whitelist change affects entries written after it, and the
chain crosses the boundary intact because each entry commits to `prev_hash`
rather than to a schema.

**Stage 1 — one liveness predicate, and a derived roster.**
Move `entry_liveness` down into `run_roster`; have `checklist_engine._is_stale`
call it, so the 1800s and 28800s answers stop disagreeing. Build the roster as a
*derived view* over what already exists: every `crew-runs.json` under the main
checkout plus every `.spine-rail-binding.json`. Ship `spine_observe` on top.
*Breaks:* nothing new is enforced. **This stage alone removes E1's workaround
and pays for itself** — the biggest single change in run-evidence quality, and it
enforces nothing.

**Stage 2 — the roster becomes the writer of record at dispatch.**
`run_crew` and `spine_lifecycle` write actors, edges and grants. Every dispatch
path registers, including the Agent-tool path that today registers only via the
`external` backend marker. Still no refusals. **The measurement this stage
produces is the falsification test for the entire design:** count mutating verbs
arriving on roster-known plans from actors the roster never saw. If that number
is large and does not fall, stage 4 is not viable and the design should be
abandoned at stage 3.

**Stage 3 — supervision verbs, additive.**
`declare-dead`, `waive-for`, `release-child`, `revoke-grant`, `adopt`. Pure
additions: a parent gains a one-call route to what E3 and E5 do by hand, and the
old five-step handshake still works for anyone who prefers it. *Breaks:* nothing.

**Stage 4 — enforcement, one flag at a time, each behind its own switch.**
- 4a. `--from_child` requires a declared descendant. *Breaks:* runs using an
  undeclared child file. Grace: warn for one release, then refuse.
- 4b. Impersonation refused on the attested (door) path only. *Breaks:* nothing
  on the CLI path, which stays unattested by design and says so.
- 4c. #615's leaseless guard, scoped to plans carrying `origin.work_id`.
  *Breaks:* every origin-carrying fixture in the suite that drives without
  claiming. This is the largest blast radius in the whole design and lands last
  for exactly that reason.
- 4d. Self-waive refusal moves from the launcher's `PreToolUse` hook into the
  engine; the hook retires. *Breaks (widening, must be gated on the lineage edge
  existing):* CLI-launched crews that previously could waive **nothing** can now
  waive a descendant's check. *Breaks (tightening, a fix but still a change):*
  `external`-backend crews and Agent-tool subagents that previously could
  self-waive freely now cannot.

**Stage 5 — retire the invented identity, not the second file.**
A Commander holds one actor id across `spine.json` and `execute.json`. No
`commander-567-d1-execute` strings anywhere. This is where #634's real cost is
paid off, and the file count never changes. *Breaks:* any tooling that reads a
plan's driver by parsing a session string — `run_crew.work_id_from_session`
parses `constellation/<work-id>/<gate>/<role>/attempt-<n>` and would need the
roster instead.

---

## 9. Risks — where this is most likely wrong, and what would falsify it

1. **The roster becomes a check nothing calls.** #357's named trap, and the
   thing most likely to kill this design in practice. *Mitigation:*
   `require_session` is the sole authority consumer; if a second authority check
   appears anywhere else, the design has already failed. *Falsifier:* stage 2's
   unregistered-mutation count staying high.

2. **The door may not be able to learn the true actor. [GUESS]** I know from
   `binding_key` and the probe fixtures that the harness supplies `agent_id` in
   *hook* payloads. I do **not** know whether a `PreToolUse` hook on this harness
   can *modify* a tool call's input, only that it can deny one. I have designed
   for deny-only, which is sufficient — the hook refuses a door call whose actor
   holds no grant on the bound plan. If stamping turns out to be available it is
   an optimization, not a load-bearing assumption. Someone should verify this
   before anything is built on it.

3. **Reversing `decision:one-spine-per-process-stands` is the riskiest single
   move here.** That decision is deliberate, documented at length, and pinned by
   an AST test. My argument for reversing it: "one spine per process" was always
   a proxy for "one actor per binding", and it held only while process ≈ actor.
   E2 measures that process ≠ actor on this harness — a subagent shares the
   parent's door — and `spine_rail` has *already* abandoned the proxy, keying
   bindings as `session#agent` and mapping each key to **multiple** spine paths.
   So two subsystems in this repo already disagree about the unit of binding, and
   the door is the one holding the older answer. *Falsifier:* if the door's
   multi-grant selector reintroduces a redirect hazard of the kind
   `_identity_violation` was defeated by six times, the reversal is wrong and the
   proxy should stand.

4. **Fleet-scope store, fleet-scope contention.** The rail's per-work-area store
   already tore into two concatenated JSON documents under 16 concurrent writers
   before #441's lock. A main-checkout store has strictly more writers.
   *Falsifier:* reproduce `test_spawn_binding_transaction_red_green` at fleet
   scope and watch it fail.

5. **Roster ancestry is forgeable in the same way session ids are.** A rogue
   actor could register itself as the Admiral's child. I am explicitly not
   defending against this, per #632's own framing. *Falsifier:* an incident where
   a forged edge, rather than an accident, is the cause.

6. **Where I am most likely wrong overall — the whole thing may be too much
   machinery for this fleet.** The observed concurrency is three to nine lanes.
   A much smaller design would take the door as it is, add exactly three
   supervision verbs that accept a *path* and a *reason*, confine them to the
   main checkout's `.agent-work/` tree, and have **no roster at all** — answering
   "may this actor supervise that plan?" by convention rather than by structure.
   That design removes E3's and E5's workarounds at perhaps a tenth of the cost,
   and fails only on the authority question, which today is answered by prose
   anyway. If the human's real constraint is small-fleet and low-ceremony, I
   would expect it to beat this candidate, and I would not argue hard.

---

## 10. Tests — what would have to pass to believe this landed

| id | claim | test |
|---|---|---|
| T1 | E3 closes | A plan held by a pid-dead actor; an ancestor calls `declare-dead`; the plan on disk carries the supersession with declarer and reason; the child journal has an entry attributed to the ancestor; a later mutating verb under the dead actor's id is refused. |
| T2 | E5's handshake collapses to one call | A crew blocks on its own check; the parent waives it in **one** call without binding; the child's evidence shows `authority: <parent actor>` and `on_behalf_of: <child>`; the child's grant and lease are byte-identical before and after. |
| T3 | E2 closes | A helper process with the parent's `SPINE_FILE`/`SPINE_SESSION` and no grant is refused on its first mutating verb; the parent's plan is unmodified; the refusal names registration. |
| T4 | the drive boundary did not move | An ancestor reads a descendant's gate status across a sibling worktree via `observe`; the same path attempted as a **drive** bind still refuses with today's exact `path-escape` text. |
| T5 | #615 lands without killing the suite | A mutating verb on an `origin`-carrying plan with no active grant is refused; the same verb on an origin-less fixture still exits 0; the ordinary suite stays at its current green. |
| T6 | #357 closes | On any roster-known plan, the count of mutating journal entries with a null actor is **zero**; re-run against a fixture reproducing issue-305's 33-of-34 shape. |
| T7 | attribution is chained, not decorative | Mutate a journal entry's `actor` field by hand; every subsequent hash fails to verify. (This is the test that proves the whitelist change actually landed.) |
| T8 | one liveness answer | A single fixture actor reads the same three-state liveness from the engine and from the launcher; no code path anywhere computes staleness from `last_heartbeat` alone. |
| T9 | E5's archive-move closes | `close_work` moves a work area whose plan is bound and granted; `release` afterwards succeeds with no temp-copy-back and no hand edit. |
| T10 | #634's identity cost is paid | A Commander run produces zero session strings outside `constellation/<work-id>` and `constellation/<work-id>/<gate>/<role>`; `spine_status` renders which gates are frozen. |
| T11 | the negative control | An actor attempts to supervise a **sibling** and an **ancestor**; both refuse. An actor attempts to `waive-for` **itself**; refused, and the refusal names asking up. |

---

## 11. Guesses, collected

- **[GUESS]** That a `PreToolUse` hook can *stamp* a verified actor onto a door
  call. I designed around deny-only for this reason; verify before relying on it.
- **[GUESS]** That the harness supplies `agent_id` on `PreToolUse` as it does on
  `PostToolUse`. The fixtures I read are all `PostToolUse`.
- **[GUESS]** My reading that E3's stranded plan was reachable from the engine
  CLI is derived from source (`origin_worktree_refusal` deleted,
  `require_session` early-returning, the 1800s stale window against the recorded
  `02:15:01Z` heartbeat) — I did not attempt it, because this lane must not touch
  another run's spine. It should be confirmed on a copy before anyone leans on it.
- **[GUESS]** That the roster can live in the main checkout without a new class
  of lock contention. The precedent (`durable_root`) is a *reader*; the roster is
  a writer.
