# Candidate C — the interaction seam

**Lane C.** Assigned hypothesis: the dominant root is the *interaction* between
plan multiplicity and authority, and the job is to design the seam where they
meet rather than either side.

Written against `/tmp/constellation-20260820-integration`
(`afk/20260820-deficiency-integration`, base `efe92791`). Artifact only: no
source, test, `map/` or GitHub change, nothing committed, no `mcp__spine__*`
call.

---

## 0. Verdict on the assigned hypothesis, up front

**The interaction framing survives, but it is asymmetric, and one of the two
halves I was handed is misnamed.**

Three claims, in the order I would want them attacked:

1. **Authority dominates.** Every hand workaround in the dossier is a missing
   authority verb standing in as prose: E3 is "the Admiral ruled a plan dead in
   the log," E5-b is "the parent did five calls to perform one act of
   authority," E2 is "the dispatcher wrote a prohibition by hand." If you could
   only fix one thing, fix authority.

2. **The second variable is not multiplicity. It is anonymity.** Plan
   multiplicity — `spine.json` plus `execute.json` — is load-bearing, not a
   defect. #634's own reconciliation defends `spine_advance --from_child` as a
   *cross-agent verdict seam* and states the rule as "one agent drives one
   spine, never no spine may reference another." `spine_lifecycle._release_child_plans`
   is a shipped parent-authority mechanism that exists **only because** the
   parent/child plan pair exists to hang it on. Collapse the pair and you delete
   the two places authority already lives. What is actually broken is that the
   child plan has **no identity of its own**: `engine_session: null` on the main
   path (#357), no back-reference to the parent that dispatched it, no id — only
   a path, and a path in a directory the parent may not be allowed to reach.

3. **Therefore the interaction is real but not symmetric.** Authority is the
   thing to build; anonymity is the precondition that makes it buildable. A lane
   that reports "just add parent authority" ships a verb with nothing safe to
   scope it to — which is precisely the seed's E2 warning, a mechanism for one
   run to corrupt another. A lane that reports "just collapse the plans" makes
   E1 worse, because after the collapse a child's plan is *definitively* in
   another worktree and both `from_child` and `_release_child_plans` stop
   resolving.

**Restated honestly, my hypothesis in its corrected form:** *the dominant root
is missing parent authority; plan anonymity is why every attempt to add that
authority has had nowhere safe to attach, and the seam where the two meet is the
dispatch moment, not the bind moment.*

**And one thing the seed got wrong that I have to say plainly.** The brief
pointed me at `spine_bind` / process start / env inheritance / worktree
confinement as "the binding moment where identity and authority are jointly
decided." I went there and found the seam is one step earlier and in a different
module. See §2. E1's conclusion — "no crew dispatched from this harness can be
engine-railed at all" — is **not primarily a door defect**. It is a
dispatch-channel defect, and the railed channel already exists and works.

**What would falsify me.** Named concretely in §8; the sharpest is §8.5, which
is a one-wave experiment that could show most of this cluster dissolving without
any of my design.

---

## 1. The evidence I am designing from, read at source

Five things I verified in the tree rather than took from the issues. They are
the load-bearing inputs to everything below.

**(a) The human's own ruling is a lineage-scoped authority ladder, and half of
it has no mechanism.** `scripts/run_crew.py:790`, verbatim in a comment:

> "agent cannot waive itself. I'll allow commander to waive crew, admiral to
> waive commander, human for admiral. always ask up."

The first rung is *mechanically enforced*: `crew_settings_json()` installs a
`PreToolUse` hook on `mcp__spine__spine_evidence` that denies `action=waive`,
and the denial text names the escalation path. The second rung — *commander
waives crew* — has **no mechanism at all**. It is the five-step handshake in
E5-b. The reason it has no mechanism is that the system cannot express "crew" as
a relation: a crew is a separate spine, in a separate worktree, under a separate
lease, with nothing recording that it is *this* commander's crew. **That is the
interaction, in the human's own words, in the repo's own source.**

**(b) The lineage edge already exists, declared from both ends, and nothing
reads it as authority.**

- Child → parent: `spine_lifecycle.build_origin` writes `origin.parent`, "the
  dispatching session." Its own docstring says this block "is PROVENANCE and
  nothing else."
- Parent → child: `tasks[<gate>].child_checklist`, compiled by
  `generate_spine._compile_gate` (`:677`).

Both are inert. The single place the edge is read as authority is
`spine_lifecycle._release_child_plans` (`:856`), and it is reachable only from
`finish_work` — at closeout, once, for one verb (`release`), and only for
children **whose resolved path is strictly inside the parent's own `work_dir`**.

**(c) That containment predicate is the same assumption as the door's
confinement predicate, and both are proxies for the same missing relation.**
`_release_child_plans` says "a child is a JSON file inside my work_dir that one
of my gates names." `mcp_spine_server._own_checkout_for_binding` says "a spine I
may bind is one inside my own checkout's `.agent-work/`." Both encode
*proximity implies relationship*. E3's stranded plan
(`/tmp/constellation-20260820-613/.agent-work/20260820-issue-613/repair-reviewer-plan.json`)
is a real child of a real parent and is outside both predicates, because the
dispatch model puts children in sibling worktrees. **Proximity stopped implying
relationship the day work moved into per-lane worktrees, and no predicate was
updated.**

**(d) The railed dispatch channel exists and works.** `build_crew_argv`
(`run_crew.py:902`) spawns a real `claude -p` process; `_crew_door_env` /
`crew_env` (`:1170`) **assign** — not `setdefault` — `SPINE_FILE`,
`SPINE_SESSION`, `SPINE_PARENT`, `CREW_SCRATCH_DIR` whenever `--spine` is given,
with a docstring recording the exact hijack that assignment closed; the prompt
tells the crew "your spine is already bound"; `CREW_ALLOWED_TOOLS` grants the
door and the waive-deny hook is installed. A crew dispatched this way has its
**own** door bound to its **own** spine, in its own process, with none of the
parent's identity. #632's four-variable leak is, on this path, **already fixed**.
It is not fixed on the in-session Agent-tool path — because on that path there
is no environment to fix. The subagent shares the parent's door *process*.

**(e) The door genuinely cannot tell parent from subagent, and the Stop hook
can.** `mcp_spine_server` holds `SPINE` and `SESSION` as module globals
(`:243-244`), assigned in exactly one function (`_bind_process_to`), and
`call_tool` receives only `(name, arguments)` — no caller discriminator exists
in an MCP tool call. `scripts/hooks/spine_rail.py` **does** receive one: the
harness hands it `agent_id`, and `binding_key` (`:476`) keys the binding store
`sid#agent_id`; `spine_rail.py:1818` states the premise outright — "Agent-tool
subagents SHARE their parent's session_id." So the harness exposes per-agent
identity at the hook seam and not at the MCP seam. That asymmetry is the whole
of E2's in-session half, and it is **outside this repository's control**.

---

## 2. The seam, located

The brief expected the seam at `spine_bind`. It is one step earlier.

At the binding moment, the door decides **two** things from **one** input pair:

| decided at bind | from | governs |
|---|---|---|
| which plan this process addresses | `SPINE_FILE` | plan identity |
| under whose name it may mutate it | `SPINE_SESSION` | authority |

They are set together, from the same source, by the same call, and neither can
be re-decided per call. That is a real collapse of two concerns into one
variable pair — and it is also, as `IDENTITY_TRADE.md` §3 argues at length and I
agree, **the right collapse**. Splitting it (Option A, per-call `--file`;
Option B, caller-supplied identity) buys nothing: a subagent that can name its
own spine can name its parent's, and a string it can supply, it can supply its
parent's. The CLI already *is* the per-call door.

So the door is not where the fumble is. The fumble is that **the relationship
between two plans is never written down at the moment it is created**, and every
consumer downstream is therefore forced to guess it from location. The moment it
is created is **dispatch** — `run_crew.CliBackend.dispatch`, which already
computes `(work_id, gate, role, parent, spine, scratch_dir)`, already assigns
four environment variables from that tuple, and already refuses a dispatch it
cannot describe. It writes the relationship into the *child's environment*, which
is a channel that dies with the process, is invisible to a later reader, and is
unavailable to a parent trying to recover.

**The seam is: the dispatch moment must write a durable, mutual lineage edge,
and every authority question downstream must be scoped by that edge instead of
by a path.**

That is a genuinely joint design. It is not "give parents authority" (which
without an edge means any door may act on any plan). It is not "one plan per
agent" (which deletes the edge). It is: *make the relation first-class, then
hang authority on the relation.*

---

## 3. Boundaries — what exists and what each owns

Five components. Four exist; one is new and small.

### 3.1 `scripts/checklist_engine.py` — plan state and the actor-authority gate

**Owns:** gate status, evidence, the journal, the lease, `require_session`.
Judges mechanism, never quality. Unchanged in kind.

**Gains one data block and one verb.**

`lineage`, a new top-level block on every plan — spine and child gate plan
alike:

```json
"lineage": {
  "plan_id":        "<derived, never model-supplied>",
  "parent_plan_id": "<the plan whose gate dispatched this one>" | null,
  "parent_session": "<the session that dispatched it>"          | null,
  "declared_at":    "<iso8601>",
  "declared_by":    "run_crew.dispatch" | "open_work" | "spine_bind"
}
```

`plan_id` is **derived**, on the same posture `spine_lifecycle.session_id_for`
already establishes for session ids: identity is a function of the plan, never
of a caller-supplied string. `IDENTITY_TRADE.md` §3 Option B settled that a
caller-supplied identity buys nothing, and that settlement carries here
unchanged.

`supersede`, a new verb: sets a lease to a new terminal status `superseded`,
recording `superseded_by` (the acting session), `reason`, and timestamp. It is
the missing counterpart of `release` — `release` says "I am done with this,"
`supersede` says "someone else has determined this is dead." E3's stranded plan
needs the second and only has the first.

`require_session` gains exactly one clause, stated as a rule rather than a
patch: **a plan that carries a lineage block requires a session for mutating
verbs, whether or not a lease is active.** A plan with no lineage block behaves
exactly as it does today. This is §5.5's answer to #615 and it is the reason
that answer has no blast radius.

### 3.2 `scripts/run_crew.py` — the dispatch moment

**Owns:** process spawn, the child's environment, the recovery registry, and —
new — **authorship of the lineage edge**. It is the only component that knows
both ends of the relation at the instant the relation comes into existence.

Two changes:

- Before spawning, write both halves of the edge: `lineage` into the child plan,
  `child_plan_id` into the dispatching gate. Refuse the dispatch if either write
  fails. A crew that cannot be described cannot be launched.
- `crew_env` stops leaving the inherited route untouched when no `--spine` is
  given. Run-scoped variables (`SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT`,
  `CREW_SCRATCH_DIR`) are **cleared** unless explicitly passed. The environment
  a helper starts in is chosen for it, which is #632's own stated remedy shape.

### 3.3 `scripts/mcp_spine_server.py` — the door

**Owns:** one bound plan per process, and the confinement of every path a tool
can steer.

`decision:one-spine-per-process-stands` stands. `_identity_violation` is
untouched. `spine_bind` is untouched. The nine pass-through tools gain no path
and no session argument.

**Gains one tool, with a different confinement predicate:** `spine_child`,
actions `status | release | waive | supersede`, taking a `child_plan_id`.

### 3.4 `scripts/spine_lifecycle.py` — open, close, and the existing child sweep

**Owns:** work-area creation and archival, and `_release_child_plans`.
`_release_child_plans` is re-expressed on the lineage predicate, keeping the
`work_dir` containment predicate as a fallback for un-lineaged children so the
migration is additive. Its three shipped safety properties (structural lineage,
honest non-owner release, escape refusal) are exactly the properties the new
surface needs; this is not a new design, it is that design given reach.

### 3.5 The plan registry — new, small

A single file at `agent_work_root.durable_root()`, mapping
`plan_id → {path, checkout, work_id, status}`. Written by `open_work`,
`close_work` and `run_crew.dispatch`. Read by `spine_child` (to resolve a child
in another worktree) and by the door (to follow a work area that moved — E5-a).

`durable_root` already exists, already resolves to the main checkout from any
linked worktree, and already never raises. There is a precedent for the
ownership discipline a shared store needs: `spine_rail`'s binding store, keyed
and hardened under #441. **Caveat, and I am flagging it rather than burying it:**
`durable_root` deliberately *declines* the main-checkout redirect when an active
Admiral epic lease fences main read-only. For a feedback file that is correct;
for a registry that must be singular, it is not. The registry needs its own root
predicate. See §8.3.

---

## 4. Ownership and authority

### 4.1 The two capabilities, and why one predicate cannot serve both

This is the design's central move.

Today, one question — *which plan may this process touch?* — is answered by one
predicate (path containment, decided at bind) for **all** capabilities. Split it
by capability:

| capability | verbs | confined by | reach | decided |
|---|---|---|---|---|
| **DRIVE** | start, advance, attest, attach, record, consolidate, skip, block, resume, reopen, append, flag-candidate, amend, claim, heartbeat, release, waive **on one's own plan** | path: `<own checkout>/.agent-work/`, equality against `SPINE` | one plan, one process | at bind |
| **SUPERVISE** | status, release, waive, supersede **on a declared child** | a validated mutual lineage edge from the bound plan | any checkout of this repo | per call |

**Drive needs isolation. Supervise needs reach. They are different questions and
they have been sharing an answer.** Splitting them is what lets the isolation
property stay exactly as tight as it is today while the authority problem gets
solved at all.

### 4.2 What validates an edge

A parent may supervise a child **iff both halves agree**:

- the child's `lineage.parent_plan_id` equals the bound plan's `plan_id`, **and**
- some gate of the bound plan carries `child_plan_id` equal to the child's `plan_id`.

A one-sided claim is not an edge. Neither party can unilaterally invent the
relation. This is the anti-corruption property the assigned premise demands: it
is exactly what stops "parent authority" from becoming "any run may reach into
any other."

### 4.3 What a parent may do to a child, and what it may not

**May:** read its status; release its lease; waive one of its conditions;
declare it superseded. All four are recorded in the child's own journal with the
supervising session as actor, and mirrored onto the parent's dispatching gate.

**May not — and this is the line that makes the split honest:** start, advance,
attest, attach, amend, consolidate, or close any of the child's gates. **A
supervisor cannot do the child's work. It can only end the child's claim on it.**

That distinction is what keeps `SUPERVISE` from being `DRIVE` under another
name. It is also the design's most attackable point, because `waive` is a
partial exception — see §8.2, where I give the runnable experiment that decides
it.

### 4.4 The ladder enforces itself

The human's ruling — *commander waives crew, admiral waives commander, human for
admiral, always ask up* — becomes structural rather than configured. A crew has
no declared children, so `spine_child` is **inert in a crew's hands**: there is
no edge for it to validate. A commander has crews and can supervise exactly
those. An admiral has commanders. Nobody can supervise itself, because a plan is
never its own child.

The `PreToolUse` waive-deny hook in `crew_settings_json` stays, because it
guards a different thing (self-waive on one's *own bound* plan through
`spine_evidence`). But the second rung stops being prose.

### 4.5 Who owns a leaseless plan

A plan carrying a lineage block is *declared work*, and declared work is owned
work: mutating it needs a session even with no active lease. A plan with no
lineage block — a fixture, a scratch plan, a hand-built test spine — is
undeclared and stays exactly as unguarded as it is today.

---

## 5. Failure semantics

### 5.1 Crash of the plan's own agent

The lease goes stale by heartbeat, as now. A **declared parent** may `supersede`
or `release` a stale child without `--force` — its authority comes from the edge,
not from seizure — and the act is attributed. A non-parent still needs
`claim --force --reason`, unchanged.

### 5.2 Takeover

`claim --force` keeps `previous_session_id` and `takeover_reason` (already
shipped; E4 confirms them present and working on the spine surface). The child
now has the equivalent: `supersede` records `superseded_by` and `reason` in the
child plan itself.

The remaining half of #369 — that journal entries after a takeover carry the
predecessor's session id — is answered by recording `actor` per journal entry
alongside `session_id`, so the chain answers *which job* and *which agent*
separately. That is #369's own proposal and I adopt it unchanged. It is
independent of everything else here and could ship first.

### 5.3 A dead session holding a lease on a child — E3, exactly

Today: nothing reclaims it and nothing guards it; it sits `active`, owned by a
process that no longer exists, and the only record that it is dead is prose in an
Admiral's log.

Under this design: the parent calls
`spine_child action=supersede child=<plan_id> reason=...`. One call. The child
plan's lease goes to `superseded`, naming the Admiral's session and the reason;
the parent's dispatching gate records that its child was superseded; the registry
marks the plan terminal. **The next reader of that file learns it is dead from
the file**, which is the specific thing E3 says is missing.

Worktree does not enter into it. The child in E3 is in
`/tmp/constellation-20260820-613/`, outside the Admiral's checkout and outside
the Admiral's `work_dir`. Under lineage that is irrelevant; under either of
today's containment predicates it is fatal.

### 5.4 A stranded child plan with a *broken* edge

Deliberately named, because it is where the design fails safe rather than open.
If the child's `parent_plan_id` is missing or does not match, no parent may
supervise it. It is reported by `spine_child action=status` on the parent as
`undeclared_active` — the same honest category `_release_child_plans` already
reports today — and a human decides. **Widening the predicate to reach it would
be re-admitting exactly the corruption risk the mutual edge exists to prevent**,
and `_release_child_plans`'s own docstring already refuses to make that call
("releasing it would seize a lease a different, still-working agent genuinely
holds"). I keep that refusal.

### 5.5 A leaseless plan

Answered structurally: lineage-bearing plans need a session, undeclared plans do
not. This resolves #615's stated dilemma — its three candidate shapes (claim-
before-mutate, terminal-refuses-reopen, accept-it-explicitly) all keyed on
*whether a lease exists*, and the issue itself names the blast radius that
follows ("every fixture and scratch spine in the suite drives verbs without
claiming"). **The discriminator was wrong, not the intent.** The right question
is not "is there a lease?" but "does this plan belong to a run?"

### 5.6 A work area that moves mid-run — E5-a

`close_work` already refuses while a lease is active and already moves the spine
last, so the deadlock arises only from a hand `git mv`, which doctrine already
forbids and which has already cost this project a recovery. With a registry the
door resolves its bound plan through `plan_id` and follows the move; a
still-bound door whose plan moved re-resolves instead of deadlocking.

---

## 6. Migration — seven stages, each leaving the system working

Each stage is independently revertible. Stages 0–3 are purely additive.

**Stage 0 — write the edge, read nothing.** `lineage` written by `open_work`,
`run_crew.dispatch` and `generate_spine._compile_gate`; registry populated.
Consumed by nothing. Exactly the posture `origin.parent` has today.
*Breaks:* nothing. Suite delta is new fields in fixtures.

**Stage 1 — `spine_child action=status`, read-only.** The first cross-worktree
reach in the system. Nothing mutates.
*Breaks:* nothing. *Buys:* the resume-side artifact #369 half 1 asks for and the
parent visibility E1 lost.

**Stage 2 — `supersede` + `spine_child action=supersede|release`.** Closes E3.
`_release_child_plans` gains the lineage predicate, keeps containment as
fallback.
*Breaks:* nothing existing. New terminal lease status; anything switching
exhaustively on lease status needs the new arm — grep target is
`_lease_line`/`_active_lease` and their readers.

**Stage 3 — `spine_child action=waive`.** Closes E5-b.
*Breaks:* `WAIVE_DENY_REASON`'s text, which currently names a path that has no
mechanism; it now names one. Crew-side doctrine prose in the commander and
admiral skills changes with it.

**Stage 4 — `require_session` honours lineage on leaseless plans.** Closes #615.
**This is the first stage that breaks something.** Any real run's plan driven
from the CLI without `--session-id` now refuses. Fixtures and scratch plans are
untouched *because they carry no lineage* — which is precisely why stage 0 must
land long enough ahead for the discriminator to be trustworthy. If any suite
fixture acquires a lineage block by accident, this stage reds it; that is the
intended alarm, not a regression.

**Stage 5 — `crew_env` clears run-scoped variables by default.** Closes #632's
subprocess half mechanically.
*Breaks:* every dispatcher relying on inheritance. The named case is the
Admiral's own bootstrap, which passes `base_env` with no `--spine` and today
keeps the inherited route on purpose — `crew_env`'s docstring says so. That
caller must become explicit.

**Stage 6 — registry-backed path resolution in the door.** Removes E5-a.
*Breaks:* nothing, if the registry is advisory (fall back to the literal path
when the registry is unreadable). It must be advisory — a door that cannot read a
registry must not become a door that cannot run, the same rule
`_standing_in_the_bound_spines_worktree` already follows.

**Ordering constraint.** Stage 4 must not precede stage 0 by less than one full
epic, because it converts a data field written by an untested path into a
refusal. Stage 5 is independent of 0–4 and could ship first or last.

---

## 7. Issue dispositions

**#634 — partly closes; one of its four remainders is mis-scoped, and I disagree
with it.**
Remainder 1 (the crew half: `generate_spine._compile_gate` carrying `bookend`
through) closes incidentally — I am already changing that function to carry
`child_plan_id`, and the field is one line plus a spec key by the issue's own
account. Remainder 3 (freeze protects completion, not acceptance) and remainder
4 (`current` does not render the freeze) are untouched and stay open; they are a
plan-mutability concern, not this cluster.
**Remainder 2 — the `execute.json` migration to "one spine per agent" — I read as
mis-scoped.** The issue's own reconciliation already narrowed "one spine per
agent" to "one agent drives one spine, never no spine may reference another,"
and my design depends on that narrower reading: the parent/child plan pair is
the structure authority hangs on. Collapsing it deletes `from_child` and
`_release_child_plans`. The right remainder is not "collapse the pair" but "give
the child plan an identity," which is stage 0. I recommend the issue be
re-scoped rather than closed.

**#638 — closes symptom 1; replaces symptom 2's workaround with a registry; and
takes a deliberate bite out of one of its stated constraints.**
Symptom 1 (the sanctioned escalation has no mechanism) is exactly §4.4, closed
at stage 3. Symptom 2 (a run cannot move its own work area) is stage 6.
The constraint I break: the issue states that `spine_bind`'s refusal of a
sibling worktree "was measured to be worth keeping" — 6,102 candidates against
1,014. I keep that refusal **for drive** and deliberately break it **for
supervise**, gated on a mutual edge. That is the design's central bet and §8.1
is where I make the case that it is a bet rather than a mistake.
The issue's own one-defect framing is right and my design honours it: one
mechanism addresses both symptoms.

**#632 — partly closes. The subprocess half is close to fixed already; the
in-session half cannot be fixed from inside this repository.**
Subprocess: `crew_env`/`_crew_door_env` already assign all four variables when
`--spine` is given, with the hijack they closed documented at the call site.
Stage 5 extends that to the no-`--spine` case, which is the remaining leak.
In-session: the door's container is the OS process; the harness does not
separate Agent-tool subagents at that granularity; and an MCP tool call carries
no caller discriminator, unlike a Stop-hook payload, which carries `agent_id`.
`IDENTITY_TRADE.md` §1's rule applies unchanged — *a seam below its container's
separating granularity fails closed* — but the door cannot detect the case in
order to fail closed on it. The available in-repo remedy is **configuration, not
code**: check in crew agent definitions under `.claude/agents/` whose tool grant
excludes `mcp__spine__*`, and lint that every dispatched-role definition does
so. That replaces a prose clause re-written per handoff with one checked-in
artifact and a test. *(Guess, marked: that this harness version's agent-definition
tool grant reliably excludes MCP tools. The repo has no `.claude/agents/`
directory today, so this is unmeasured here.)*
The honest residue: an in-session subagent can still call the door and drive its
parent's spine, and nothing in the journal distinguishes it. **That is a harness
property, and a design that claims to close it is claiming something it cannot
deliver.**

**#357 — closes, with one correction to its own recommended fix.**
The issue's second comment measures the real shape: 33 of 34 mutating verbs on
one child gate plan carry no session, and "the session-less path is the *main*
path." It withdraws the refuse-session-less-verbs guard as unviable (correctly —
it would break every crew-driven gate in the fleet) and recommends session
propagation instead.
My correction: **do not propagate the parent's session down.** Echoing the
parent's id onto the child's verbs recreates #369's exact defect — a session id
that no longer identifies an actor — one layer lower, and `_release_child_plans`
already refuses to do this for the same reason ("echoing the child's id back
would make the ownership check tautological"). Propagate the **edge** instead:
the child gets its own derived identity, and its verbs carry *that*, under a
declared parent. The 33 anonymous verbs become 33 attributed ones and the
attribution is true rather than borrowed. Grace path is stage 0's absence rule.

**#369 — mostly already fixed on the spine surface; its live mechanical half is
E3 in another costume; its narrative half stays open by construction.**
E4 verified `previous_session_id` and `takeover_reason` present and working on
the epic spine. Half 2's remaining piece is the per-entry `actor` field (§5.2),
which I adopt as-is from the issue.
Half 1 (the resume-side obligation) is **doctrine, not mechanism**, and I do not
close it. What I supply is the artifact it needs: today a resuming agent is told
to "verify aloneness from artifacts," and the artifacts named — filesystem
mtimes, journal session ids, crew registry entries — are exactly the
point-in-time reads the issue's own comment says failed as a concurrency guard
("a pre-dispatch safety check is the worst available place for a check that
cannot fail"). `spine_child action=status` answers "is any declared child of
mine live" from a durable record instead. The obligation to ask still lives in
prose.
The comment's narrative channel — misattribution propagating into summaries and
close-out notes — is untouched. Its own conclusion is that the only demonstrated
correction is an agent answering honestly, which is a disposition, not a system
property. I agree and claim nothing there.

**#615 — closes, and reveals all three of its candidate shapes as keyed on the
wrong discriminator.**
Claim-before-mutate, terminal-refuses-reopen, and accept-it-explicitly all ask
"does a lease exist?" and the first one's rejection turns on blast radius —
"every fixture and scratch spine in the suite drives verbs without claiming."
Lineage separates production plans from fixtures cleanly, so claim-before-mutate
becomes viable at zero fixture cost. This is the disposition I am most confident
in and the cheapest to test: it is stage 4 and its whole risk is measurable by
running the suite.

---

## 8. E1–E5 — remove / keep / replace

### E1 — the door's binding is fixed to one checkout, so a parent cannot inspect its children

**REMOVES the workaround for the parent-visibility half. And I dispute the
finding's framing.**

The workaround was: declare every crew lane unrailed, hand-write the prohibition
into each handoff. `spine_child action=status` removes the parent-visibility
half at stage 1 — a parent can read its declared children wherever they live,
which is what "inspect its own children" means.

But E1's stated consequence — *"No crew dispatched from this harness can be
engine-railed at all, because every crew's spine is by construction in another
worktree"* — **is true of the Agent-tool channel and false of the `run_crew
--backend cli` channel.** A crew dispatched through `run_crew` gets its own
process, its own door, its own `SPINE_FILE`/`SPINE_SESSION` assigned from
`--spine`, a prompt telling it its spine is bound, the door in its allowed
tools, and the waive-deny hook installed. It is railed. The door's sibling-
worktree refusal never enters into it, because that crew's door is *inside* that
crew's worktree.

So E1 is, in significant part, **a dispatch-channel choice, not a door defect**.
The Admiral dispatched in-session subagents — which cannot be railed, for #632's
reasons — and read the resulting unrailedness as a property of the door. This
does not make E1 a non-finding: the *parent's* inability to see its children is
real, and the cost E1 describes (Admiral re-verification instead of engine
evidence) is real. It relocates the fix.

*I want this on the record as partly falsifying my own assigned seed, which
cited E1 as proof that collapsing plan identity without parent authority makes
dispatched work unauditable. The auditability loss here came from the dispatch
channel, not from plan identity.*

### E2 — helper agents inherit the launcher's spine

**REPLACES, twice over, and does not remove.**

Subprocess path: replaced with a mechanism (stage 5 clears by default). The
guarantor is the launcher, and if a dispatcher forgets, there is nothing to
forget — inheritance is no longer the default.

In-session path: replaced with a *cheaper and checkable* workaround — a
checked-in agent definition whose tool grant excludes the door, plus a lint —
instead of a hand-written prose clause per handoff. **Not removed.** The door
cannot distinguish a subagent from its parent, and no code in this repository can
make it. Saying otherwise would be the seductive-and-unfalsifiable move my brief
warned me about.

### E3 — a dead session's lease on a child plan is unreclaimable and unguarded

**REMOVES.** One call: `spine_child action=supersede child=<plan_id>
reason="prior session dead, plan superseded"`. Cross-worktree by lineage, not
proximity. Attributed to the acting session. Recorded in the child plan, the
child's journal, the parent's dispatching gate, and the registry — four places
the next reader will look, versus today's zero.

This is the strongest case for my corrected hypothesis: it is an authority
failure, and the reason no authority verb reaches it is that the only two
predicates the system has for "is this mine?" are both about location, and the
plan is in another worktree.

### E4 — force-claim attribution preserved on the spine, absent on the child

**Confirms mostly-fixed; my design closes the child half with E3.** The spine
half needs nothing. The child half is `superseded_by`. #369's remaining
mechanical piece is the per-entry `actor` field, which I adopt from the issue
and which is independent enough to ship on its own.

### E5-a — archive-move deadlock

**REMOVES at stage 6**, via registry-backed path resolution: a bound door
re-resolves its plan by `plan_id` and follows a move. Worth noting that
`close_work` already refuses while a lease is active and already moves the spine
last, so the sanctioned path never hits the deadlock; the lesson is a hand
`git mv` hazard. The registry removes the hazard rather than restating the rule.

### E5-b — the five-step handshake

**REMOVES.** The sharpest test, and the design's cleanest answer.

Today:
```
child releases → parent claims → parent waives → parent releases → child reclaims
```
Five calls, two identity swaps, an unheld lease in the middle of it, undocumented
anywhere, performed by hand over messages, twice in one wave.

Under this design:
```
parent: spine_child action=waive child=<plan_id> condition=<id> reason=... 
```
One call. The child keeps its lease throughout — nothing is ever unheld. The
parent never rebinds — `_rebind_refusal` is never consulted because no rebind
happens. The waiver is recorded in the child's journal with the parent's session
as `authority`, which is what `checklist_engine.waive` already takes as an
argument and already records; it has simply never had a caller who could
truthfully supply it.

And it makes the human's ruling structural: *commander waives crew* is now a
thing the system can express, because "crew" is now a thing the system can name.

---

## 9. Risks — where I am most likely wrong, and what would falsify me

### 9.1 The central bet: mutual declaration is strong enough to justify the reach

I re-admit cross-worktree reach — the measured 5,088 sibling-worktree files that
`spine_bind`'s root deliberately excludes — for a supervise-only surface, gated
on a bidirectional edge.

**Falsified by:** a demonstration that one party can forge both halves. And there
is a real path: a crew running in a worktree that also contains its parent's plan
file can write both `lineage.parent_plan_id` in its own plan and `child_plan_id`
in the parent's gate. Today that is precisely the Commander/`execute.json` shape
— parent and child in the same directory.

Partial mitigation: the parent's half is written by `run_crew` before the child
exists, and a dispatching gate's `child_plan_id` can be covered by #634's shipped
bookend freeze so it is immutable once written. Whether that is *sufficient* is a
guess. **This is the weakest joint in the design and I would want a cold critic
pointed here first.**

### 9.2 SUPERVISE may be DRIVE wearing a smaller verb list

`waive` is the exception in my own §4.3 line: a supervisor cannot do a child's
work, but it can waive the conditions that define the work. If enough gates have
fully waivable postconditions, a supervisor can close a child's gate without ever
calling `advance` — and then the split is cosmetic.

**Falsifiable, cheaply and mechanically:** enumerate every gate in the corpus's
role spine templates and archived runs; count those where every postcondition
carries `override_policy.allowed: true`. If that set is non-trivial, `SUPERVISE`
is `DRIVE` and the split must be re-drawn — most likely by making `spine_child
action=waive` refuse a waiver that would by itself satisfy a gate's last unmet
postcondition. I have not run this count and it is the first thing I would run.

### 9.3 The registry is a new single point of truth

New shared mutable state, with the ownership problems shared mutable state
always has. Two specific hazards: `durable_root`'s deliberate main-checkout
*declination* under an active Admiral lease would make the registry non-singular
in exactly the epic case; and a registry that disagrees with the filesystem is
worse than no registry. Mitigation is that it must be **advisory** — every reader
falls back to the literal path — which keeps it from becoming load-bearing but
also weakens the E5-a claim from "removed" to "removed when the registry is
readable."

### 9.4 The amendment may not be the human's to make

`IDENTITY_TRADE.md` §7 records, unratified, that `spine_bind` already amended the
§2 confinement property and that *whether that property is amendable at all* is
"the one the design run most wanted ruled, and it is still open." My design
widens the same property further. **If the human rules the property un-amendable,
the supervise surface is dead as written** and the design reduces to stages 4–5
plus #369's `actor` field. That reduced form is still worth having, and I would
rather name that fallback than pretend the ruling is settled.

### 9.5 The design may be over-built — the experiment that would show it

The honest dominance question: *if every crew dispatch went through `run_crew
--backend cli` and no railed work ran in an in-session subagent, how much of this
cluster remains?*

My estimate: E1 and E2 largely dissolve; #357, #615 and E5-b remain, because they
are about child-plan anonymity and parent capability rather than about dispatch
channel. But that is an estimate.

**The experiment:** run one wave with all crew dispatched via `run_crew --backend
cli --spine`, with the Agent tool used only for genuinely unrailed research
lanes, and count which of E1–E5 recur. If E1 and E2 do not recur and E3/E5-b do,
my §0 verdict is confirmed and stages 0–3 are the right build. If E3 and E5-b
also stop recurring, **this design is over-built and the true fix was a dispatch
convention.** That would be an excellent outcome and I would want it known before
anyone writes stage 0.

### 9.6 The dossier is one privileged run

Per the brief: an Admiral is the most privileged actor in the system, and it hit
four of six. My design's biggest beneficiary is a *parent*, which is the role
this evidence over-samples. A crew-shaped or human-shaped sample might rank #615
or #634 far higher and this whole cluster lower. I have not corrected for that
and cannot from the evidence I was given.

---

## 10. Tests — what would have to pass to believe this landed

Grouped by the property each proves, with the module each belongs beside.

**The edge is mutual and cannot be forged from one side**
(`tests/test_mcp_identity.py`, beside `IdentityBindingPinTests`)
- A child whose `parent_plan_id` names a plan that does not name it back is not
  supervisable — refused, with the refusal naming which half is missing.
- A parent whose gate names a `child_plan_id` whose plan does not name it back is
  likewise refused.
- **The positive control matters more than the negative:** a mutated edge that
  *should* validate must be watched failing, per this repo's own standing rule
  that an assertion nobody has watched fail is not evidence.

**SUPERVISE is not DRIVE** (`tests/test_mcp_spine_bind.py` or a sibling)
- Every drive verb is refused through `spine_child` for every action, enumerated
  from `checklist_engine.MUTATING_VERBS` rather than hand-listed, so a verb added
  later is refused by default rather than admitted by omission.
- The §9.2 count as a *test*, not a one-off: a gate whose last unmet
  postcondition is waivable cannot be closed by a supervisor's waive alone.

**Drive isolation is unchanged** (`tests/test_mcp_identity.py`, existing)
- `IdentityBindingPinTests` stays green untouched. If adding `spine_child`
  requires editing that pin, the split has leaked and the change is wrong.
- The `spine_bind` sibling-worktree refusal still refuses, with the same
  measured reach.

**E5-b in one call** (`tests/test_mcp_lifecycle.py`)
- End to end: parent dispatches child, child blocks on an unsatisfiable check,
  parent waives through `spine_child`, child resumes — with an assertion that the
  child's lease was **never** released and the parent **never** rebound. Those two
  negatives are the test; the waive succeeding is the easy part.

**E3 across worktrees** (`tests/test_spine_lifecycle.py`)
- A child plan in a *sibling worktree* with a stale active lease is superseded by
  its declared parent in one call, and the child file afterwards states it is
  superseded, by whom, and why. The sibling-worktree placement is the whole
  point — a same-directory fixture would pass under today's containment predicate
  and prove nothing.

**#357's real shape** (`tests/test_checklist_engine.py`)
- A crew-driven child gate plan records the **crew's own** identity on all its
  mutating verbs, not the commander's, and not null. The negative control is the
  #369 defect: a test that fails if the parent's session appears on a child's
  verbs.

**#615 without blast radius** (whole suite)
- Stage 4 lands and `3447 passed, 6 skipped, 1222 subtests` holds. The suite
  staying green **is** the test: every fixture drives verbs without claiming, and
  they must all still work because they carry no lineage. A single red fixture
  means the discriminator leaked.

**#632's subprocess half** (`tests/test_crew_launcher.py`)
- A dispatch with no `--spine` produces a child environment with all four
  run-scoped variables **absent**, and the existing `ScratchDirResumeTests`
  failure that #632 names — the one that reds inside a dispatched crew on an
  untouched base commit — stops reproducing.

**Negative control on the whole design**
- One archived run's plans, replayed unmodified with no lineage block anywhere,
  behaves byte-identically to today. If stage 0 changes behaviour on a plan that
  has no lineage, the additive claim is false.

---

## 11. What I would tell the human in one paragraph

Build the lineage edge and hang authority on it, but do not start there. Start
with the two stages that are cheap, independent, and defensible on their own —
#369's per-entry `actor` field, and `run_crew` clearing run-scoped variables by
default — and run one wave with every crew dispatched through `run_crew --backend
cli` rather than through in-session subagents. That wave is the experiment in
§9.5, and it costs nothing beyond a dispatch convention. If E3 and the five-step
handshake still recur under it, the lineage design has earned its keep and stages
0–3 are the build. If they do not, this candidate was over-built and the real
finding was that the fleet has a working railed dispatch channel and was not
using it.
