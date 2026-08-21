# Cold critic comparison — five entries, scored against the corrected criterion

**Critic lane.** I wrote none of these candidates. Artifact only: no source, test,
`map/` or GitHub change, nothing committed, no `mcp__spine__*` call.

Read at `/tmp/constellation-20260820-integration` (`efe92791`) and the main
checkout's `.agent-work/`. Everything I assert about source I read or ran myself;
where I ran something, the command and its output are here.

---

## 0. The criterion I am scoring against

The human's ruling, which post-dates all three candidates:

> There are no bad actors. The only adversary is an honest agent about to make a
> mistake. Ease of use for agents is the success criterion. Added machinery is a
> COST that must be earned back in mistakes prevented.

All three candidates were written in an authority/permission frame. I judge the
design, not the author's compliance with a rule that did not exist. But I apply
the rule without discount, because the human will.

The frame change does more damage than it first appears. In an adversarial frame,
"who is allowed" is the question and a mechanism that answers it is the deliverable.
In this frame, **a permission check prevents a mistake only when an honest agent
would otherwise have done the wrong thing believing it was right.** Every refusal
that a well-intentioned agent would never have tripped is pure cost: one more
concept to learn, one more surface to keep in sync, one more refusal to route
around. That test deletes large parts of A, B and C — including, in C's case, the
argument its author calls the design's central bet.

---

## 1. Four corrections to the dossier, measured

The brief told me not to trust any candidate's characterization, including the
Admiral's. Four things needed checking. Three of them move the ballot.

### 1.1 The count discrepancy is not a discrepancy. All of them are stale.

Lane B reported 56 active leases / 52 archived / 39 after excluding fixtures. The
Admiral reported 58 active / 54 archived. I scanned the main checkout myself
(a plan = a JSON object carrying both `tasks` and `items`):

```
775 plans   57 with engine_session.status == "active"
            53 of those under .agent-work/archive/
            17 in fixture/probe/scratch/evidence paths -> 40 remain
```

39, 40, 56, 57, 58 are the same population measured minutes apart while this epic
was itself writing plan files. Lane B's "39" is a filtered subset of its own 56,
not a competing total. **There is nothing unexplained here; the lanes agree.**

The number that actually matters is one nobody reported:

```
of the 57 active leases:  stale 57   fresh 0
```

Every single lease in this repository that presents as `active` is stale by the
engine's own predicate. Not most. All of them.

### 1.2 The display does not merely fail to warn. It instructs.

I copied one archived plan whose owner last breathed on 2026-07-29 into scratch
and read it with the shipped read verb, from `/tmp`, outside any checkout:

```
$ python3 scripts/checklist_engine.py --file <copy> current

RAIL: A working solution is the MIDDLE of this run — you are 7 steps from done.
      Next: the ACTIVE line above. Run it.

LEASE active: charter-refresh-20260728 (by charter, heartbeat 2026-07-29T17:52:38+00:00)
ACTIVE orchestrator-context [in-progress] — ...
next: attest orchestrator-context --cond c1 ...
```

Twenty-three days dead. The system says `LEASE active`, tells the reader it is
seven steps from done, and hands it the next command to type. Under the corrected
criterion this is the single worst artifact in the epic: it is not a missing lock,
it is the system **actively recruiting an honest agent into a mistake.**

The mechanism is small and I read it. `_lease_line`
(`scripts/checklist_engine.py:1300-1308`) formats the raw `last_heartbeat` and
never calls `_is_stale`. `_is_stale` (`:1083-1098`) is called in exactly four
places in the whole repo — `require_session:1143`, `claim:1222`, `claim:1236`, and
`mcp_spine_server:1730` — and **never in any rendering path.** The door inherits
the blindness: `spine_status` is a verbatim pass-through of `current`, and the word
"stale" appears in zero door tool descriptions.

### 1.3 E1's parent-visibility half is already solved, and no candidate says so.

E1 says the door's binding stops a parent inspecting its own children. Correction 1
narrowed that to the dispatch channel. It is narrower still.

The run above is the proof: `current` is non-mutating, `require_session` returns
early for non-mutating verbs (`:1136-1137`), the engine reads no location at all
since #609, and the CLI takes `--file` per call. **A parent can read any child's
plan, in any worktree, on any path, today, with zero new machinery.** What stops it
is doctrine — hand-driving the engine is forbidden here — not mechanism.

All three candidates build a cross-worktree read surface. C's `spine_child
action=status` is stage 1 and is called "the first cross-worktree reach in the
system." A's `observe` capability is the same thing. B's upward read is the same
thing pointed the other way. **Each of them is proposing to build, as new
architecture, a capability that already exists and is merely forbidden by prose.**
That is the clearest single instance of the adversarial frame producing waste.

### 1.4 The five-step handshake is worse than the dossier says, in a way that helps.

I traced the sequence through `claim`/`release` (`:1155-1264`, `:1282-1297`). When
the child releases and the parent then claims, the lease is *released*, not stale
and not force-claimed — so neither branch at `:1229-1238` fires, and
`previous_session_id` and `takeover_reason` are both written **null**. The
sanctioned five-step dance leaves no takeover record at all.

Meanwhile `waive` itself (`:3310-3355`) has no session, lease or self-waive check
whatsoever. `--authority` is a free string it records verbatim. **The refusal that
forces the five steps is not in the engine at all** — it is a ten-line inline
`PreToolUse` hook string in the crew launcher (`run_crew.py:824-832`) that denies
`action == "waive"` unconditionally, installed only on `run_crew`-spawned crews.

So the handshake exists to satisfy a hook that could ask a better question, and the
handshake's own output is less honest than the thing it replaces. That is not an
architecture problem.

---

## 2. The five entries

### Entry 1 — Candidate A, "Actors and Grants"

**What it fixes.** Everything, on paper: E1 (replaced), E2, E3, E5a and E5b
(removed), E4 (half). The diagnosis underneath it is the best single paragraph
produced by this epic — `session_id` is one string asked to answer four questions
(which plan, who holds it, who acted, which process is bound), and duplicated plan
state and missing parent authority are siblings under it, not competitors. A's
falsification table (assume #634 lands in full; four of five reproductions survive)
is real work and it is right.

A is also the only lane that found the thing that makes every display fix honest:
two liveness models 16x apart (`_is_stale` at 1800s, heartbeat-only, no pid;
`entry_liveness` at 28800s, three-state, pid-corroborated), with the engine holding
the blind one. Nobody else noticed.

**Machinery cost.** The largest on the ballot by a distance. A new bottom-layer
module (`run_roster`) with three record types; a fleet-scope mutable store in the
main checkout with its own lock discipline; three new door capabilities; five new
supervision verbs; four new fields in the hash-chain whitelist; six migration
stages with four independently-switched enforcement flags; and the reversal of
`decision:one-spine-per-process-stands`, which is deliberate, documented at length,
and pinned by an AST test.

**Learning burden.** Three new nouns every future agent must hold — actor, grant,
lineage — plus the distinction between drive, observe and supervise, plus the fact
that `SPINE_FILE` is now "a convenience copy of a roster fact" rather than the
fact. The roster is a second source of truth that can disagree with the filesystem.

**What it leaves open.** The CLI stays unattested by design and A says so. #369's
narrative half. #634's item (c), the Admiral's waves outside the spine.

**Where it is most likely wrong.** Its own §9.6, which I would promote to the
headline: *"the whole thing may be too much machinery for this fleet."* A then
describes, in five lines, a design at a tenth of the cost — three supervision verbs
taking a path and a reason, no roster — and says it would expect that to win. Under
the corrected criterion A is arguing against itself and it is right.

Second: A's roster is a new file to keep in sync, and A's own falsifier for it
(stage 2's unregistered-mutation count) concedes the design dies if agents keep
arriving off-roster. In a fleet of three to nine lanes where the only adversary is
forgetfulness, an index of who-is-where that must be maintained by every dispatch
path is exactly the artifact forgetfulness destroys.

**Score.** Highest diagnostic value on the ballot; worst machinery-to-mistakes
ratio. Almost all of the value is in stages 0 and 1, which enforce nothing and are
substantially Entry 5.

### Entry 2 — Candidate B, "authority resolves upward, nothing drives downward"

**What it fixes.** E3 and E5b (removed, 3 calls), E4, E5a. #357 by custody
resolution, #615 with lineage scoping, #369's mechanical half.

B did the best measurement work of the three: 732 plans, 81% of plans are not
`spine.json`, `origin.parent` exists in the schema and is empty on every plan in
the repository's history, only 13% of plans declare any `child_checklist`, 49 of 85
`execute.json` carry a null session. B is also the only lane that noticed
`_release_child_plans` is a shipped parent-authority mechanism with three good
properties that was never generalised, and the only one to catch that its own
stage 0 would land in `open_work` when the repository actually mints work areas
through `init_work_area`.

**Machinery cost.** A new `lineage` module with four consumers; four new verbs
(`escalate`, `adjudicate`, `apply-decision`, `supersede`) plus four door tools; a
minted `SPINE_ACTOR` nonce; a new terminal custody state; filesystem reads back on
the verb path that #609 just finished removing.

**Learning burden.** The highest on the ballot, and this is what sinks it. B asks
every agent to internalise that a plan's custody is **not in the plan** — it is
resolved by walking upward at the moment of use. To answer "who owns this?" you
must read the chain. That is a harder mental model than any of the others and it
makes the cheapest possible action, opening the file, less informative than it is
today.

**What it leaves open.** #632, explicitly and by its own statement. E1 and E2's
in-session halves, explicitly. B also states plainly that its design "buys nothing"
on the channel this epic actually used.

**Where it is most likely wrong — and it already knows.** §7's residual: *"A
superseded child's own file still says `status: active` until someone runs a verb
on it."* B chooses that consciously, to preserve "never write downward."

Under the corrected criterion this is close to disqualifying. Question 1 of the
ruling is *does the system tell the truth?* Section 1.2 above shows what the
current lie already costs. B adds four verbs and a module and leaves the corpse
saying `active`. Its own R3 asks the human the right question — must the fix be
visible in the file, or at next use — and answers "next use," while admitting it is
not certain that is what the human wants. It is not.

Also: E5b at three calls is worse ergonomics than C's one call and worse than
Entry 5's one call, and the three calls span two agents with a wait in the middle.
On a criterion whose name is ease of use, that is the wrong direction.

**Score.** Best evidence, worst ergonomics, and it declines the corrected
criterion's first question on purpose.

### Entry 3 — Candidate C, "the interaction seam"

**What it fixes.** E1's visibility half, E3, E5a, E5b (one call), #632's subprocess
half, #615 with a discriminator that has no blast radius. C is the most surgical
of the three and the only one whose central move — split DRIVE from SUPERVISE
because *drive needs isolation and supervise needs reach, and they have been
sharing an answer* — survives translation into the corrected frame intact.

C also did the most source verification and it is the lane that caught the
Admiral's E1 error from source, correctly, and put it on the record as partly
falsifying its own seed. Its §9.5 experiment — run one wave entirely through
`run_crew --backend cli` and count which of E1-E5 recur — is the cheapest and most
decision-relevant proposal anywhere in this epic. Its §11 closing paragraph
recommends starting with two cheap independent changes and the experiment, which is
most of Entry 5.

**Machinery cost.** Moderate: a `lineage` block on every plan, a `plan_id`, a
`supersede` verb, one new door tool (`spine_child`), and a new plan registry file
under `durable_root()` — for which C names, and does not bury, the fact that
`durable_root` deliberately declines the main-checkout redirect under an active
Admiral lease, which is exactly the epic case.

**Learning burden.** Two new nouns (plan_id, the lineage edge) and one new
distinction (drive vs supervise). Materially lighter than A or B.

**Where the corrected frame hurts it.** C's own "central bet" is that a **mutual**
lineage edge — both halves must agree — is strong enough to justify re-admitting
cross-worktree reach. It asks the cold critic to attack that joint first. I decline,
because under the corrected criterion the joint is not load-bearing. Mutual
declaration exists to stop one party forging a relationship. There are no bad
actors. Delete the forgery defence and the edge's remaining job is *finding the
child*, and the parent already knows where the child is: it dispatched it, and
`run_crew`'s registry already records work_id, role, parent, worktree and pid.

So C's design, re-scored honestly, is: a registry so a parent can name a child it
already knows, plus a verb to end a child's claim, plus a display of who is where.
That is a good design. It is also perhaps a third of the artifact C wrote, and the
other two thirds are paid to an adversary who does not exist.

**What it leaves open.** #632's in-session half, which C correctly says cannot be
closed from inside this repository. #634's remainders 3 and 4. #369's narrative
half.

**Where it is most likely wrong.** Its own §9.2, and I think C under-rates it: if
`SUPERVISE` includes `waive`, and enough gates have fully waivable postconditions,
a supervisor can close a child's gate without ever calling `advance` — and the
split is cosmetic. C proposes the count as the first thing to run and has not run
it. It should be run before anything is built.

**Score.** The best of the three as written, and the only one whose author's own
closing recommendation is approximately the winner.

### Entry 4 — Status quo

Not a straw man. It has to be beaten, and it costs real money.

**What it costs, measured.** 57 plans in this checkout render `LEASE active` while
every one of them is stale, and the read verb urges the reader onward (§1.2). The
engine's own non-owner refusal recommends two remedies that are both filed defects
(`:1148-1152`; #632's impersonation and #369's attribution erasure) — the system
teaching the next error. The five-step handshake happened twice in one wave, by
hand over messages, and leaves no takeover record (§1.4). Every handoff in this
epic carries a hand-written "do not call any `mcp__spine__*` tool" clause. This
epic ran every crew lane unrailed and paid for it in Admiral re-verification, which
the dossier correctly says does not scale.

**What it buys.** No new concepts, no new files, no migration, no blast radius,
and a suite that stays green at 3447 passed. In a fleet of three to nine lanes, that
is worth more than it looks.

**Where it is most likely wrong.** The display lie is not stable. It gets worse
monotonically: every completed run adds another corpse that says `active`, because
closeout's sweep only releases *declared* children and only 13% of plans declare
any. Doing nothing is not holding still.

**Score.** Beats any design whose added machinery does not fix §1.2. It does not
beat a design that fixes §1.2 for the price of a few strings.

### Entry 5 — Minimal intervention (constructed here)

Only messages, defaults, and what the system displays. No new module, no new verb,
no new permission concept, no new file, no new noun for an agent to learn.

**M1 — the lease line tells the truth.** `_lease_line` renders staleness and age
instead of a raw timestamp:

```
LEASE active: <id> (by <who>, heartbeat <ts>)
->  LEASE STALE: <id> — owner silent 23d (last heartbeat <ts>); reclaim with `claim`
```

Reaches the door's `spine_status` for free, since it is a pass-through. Fixes all
57 corpses at once and every future one.
*Honest cost, not zero:* `state(cl)` takes no `config` and is pinned as a pure
projection, so either the staleness threshold is read from
`DEFAULT_LEASE_STALE_SECONDS` at the render site or `config` is threaded one level.
Small, and it makes a time-dependent value visible in a projection documented as
pure. Someone should decide which, deliberately.

**M2 — the trip advisory stops recruiting.** The `RAIL:` line that says "you are 7
steps from done, run it" is suppressed or inverted when the lease is stale. Display
only.

**M3 — `require_session`'s two refusals stop naming filed defects.** The stale
branch is already close. The active branch (`:1148-1152`) must stop saying "pass
`--session-id '<the holder's>'". Replacement names the honest options in order: if
you are that run resuming, claim under the same id; if you are not, this plan
belongs to someone else — say so and ask up; if the holder is dead the lease goes
stale 30 minutes after its last heartbeat and `claim` then records the takeover for
you automatically. Two strings. The dossier calls this the cheapest high-value fix
in the epic and I agree.

**M4 — `crew_env` clears run-scoped variables unless explicitly passed.** Today,
with no `--spine`, the dispatcher's own `SPINE_FILE`/`SPINE_SESSION` pass through
to the child untouched and deliberately (`run_crew.py:1239-1246`). Making the safe
thing the default closes #632's subprocess half mechanically. This is C's stage 5
and it is a default change, not a subsystem. *Breaks:* the Admiral's own bootstrap
caller, which relies on inheritance and must become explicit. Named, not hidden.

**M5 — the waive hook asks a better question.** The `PreToolUse` hook
(`run_crew.py:824-832`) denies `action == "waive"` unconditionally. Change the
predicate to deny a waive whose `--authority` is absent, or names the crew itself;
allow one that names someone else and carries a reason. The engine already takes
`--authority` and already records it verbatim.

The five-step handshake becomes: the crew asks its parent over the message channel
(which is what physically happens today anyway), the parent answers, the crew calls
waive with `--authority "<parent>" --reason "granted by <parent>, <when>"`. One
call, no lease transitions, no identity swap, and — per §1.4 — a *better* record
than the sanctioned dance produces today.
*This is the one member that stretches the mandate*, because it changes a rule and
not just a string. It adds no concept: `--authority` already exists, is already
required, and is already journaled. It is also the only entry-5 item that widens
rather than narrows, so it is the one to argue about.

**M6 — two message fixes, free.** (a) Doctrine: railed work is dispatched through
`run_crew --backend cli`; the in-session Agent tool is for unrailed research only.
Per Correction 1 this dissolves E1 and E2 for railed work with zero code. (b)
`spine_bind` exists, lets a door rebind mid-process within its own checkout, and
**no skill mentions it** — while `skills/implementer/SKILL.md:30` and
`skills/reviewer/SKILL.md:26` still tell a crew its spine is bound for it, which is
false on the external backend. A capability the system has and nobody is taught.

**M7 — closeout stops leaving corpses.** `_release_child_plans` releases only
*declared* children, and only 13% of plans declare any; 53 of the 57 stale leases
are in the archive. Widen the default to release plans under the work dir whose own
lease is **stale**, and report the fresh ones as it already reports
`unclaimed_active`. Uses the existing function and the existing predicate.

**Total bill.** Roughly four string edits, three predicate edits, one doctrine
paragraph, one skill correction. Zero new modules, verbs, files, permission
concepts or nouns.

**What it fixes against the dossier.** E1: the visibility half is revealed as
already available (§1.3) and the rail half is answered by dispatch channel; the
*drive*-across-worktrees half is untouched. E2: subprocess half removed (M4);
in-session half replaced by a cheaper doctrine, not removed — nothing in this
repository can remove it. E3: the workaround is removed in the only way the
corrected frame says matters — the stranded plan stops lying to the next reader,
and reclaiming it already works and already records attribution. E4: nothing to do;
already fixed on the spine, and the child half is display. E5a: **kept.** Entry 5
does nothing about the archive-move deadlock; that needs per-call path resolution
and there is no message that substitutes. E5b: removed (M5).

**What it leaves unfixed, and whether that matters.**
- **#357 — left open, and this matters most.** Child gate plans driven with
  `engine_session: null` stay anonymous. Display cannot fix attribution that was
  never written. The tempting cheap fix — default `--session-id` from
  `SPINE_SESSION` — is exactly the E2 mistake and must not be taken.
- **#634 — untouched entirely.** Frozen bookends, mutable middle, and an Admiral's
  waves living in `ADMIRAL_LOG.md` outside the spine are real wants that no
  message fixes.
- **#615 — deliberately unfixed.** A leaseless plan stays unguarded. Under
  no-bad-actors that is only a hazard when the display lies about who is on it, and
  M1 fixes the lying part.
- **Cross-worktree supervise.** A parent still cannot end a child's claim in one
  call from another worktree. It can read it, and after M1 it can see it is dead.
- **Liveness quality.** M1's honesty is only as good as `_is_stale`, which is
  heartbeat-only, 1800s, no pid. See §4.

**Score.** The best mistakes-prevented-per-unit-of-machinery on the ballot, by an
order of magnitude, on the specific mistake the evidence most supports.

---

## 3. Ranking

| # | entry | one-line justification |
|---|---|---|
| 1 | **Entry 5 — minimal intervention** | It fixes the one defect the corrected criterion names first — the system lying to an honest reader — for the price of a few strings, and buys the one-call waiver and #632's subprocess half on the way. |
| 2 | **Candidate C** | The only candidate whose central move survives the frame change, the lightest of the three, and its own closing advice is roughly Entry 5 plus an experiment — but a third of its machinery is paid to an adversary who does not exist. |
| 3 | **Status quo** | Costs 57 lying leases, a refusal that teaches two filed bugs, and an unrailed epic — but it adds nothing, and it beats any design that spends a subsystem without fixing the lie. |
| 4 | **Candidate A** | The best diagnosis on the ballot attached to the worst bill: a new bottom-layer module, a fleet-scope store, five verbs, four enforcement flags and the reversal of an AST-pinned decision — and its own §9.6 says a design at a tenth the cost would beat it. |
| 5 | **Candidate B** | Best measurement, hardest mental model, three calls where others need one, closes #632 not at all by its own statement, and deliberately leaves the corpse reading `active` — which is the corrected criterion's first question answered "no". |

**The ranking is of the five entries as written and taken whole.** It is not a
verdict on their parts. A's stage 0-1, C's stages 1-2 and stage 5, and #369's
per-entry `actor` field each beat status quo comfortably, and each is close to
Entry 5. If the human reads this as "reject A and B," I have mis-served them: read
it as "A and B are priced as wholes and should be bought as parts."

---

## 4. The strongest argument against my own top pick

**Entry 5 makes the display authoritative while the signal underneath it stays a
guess, and that can manufacture a new class of mistake that today does not exist.**

`_is_stale` reads `last_heartbeat` alone, against a 1800-second default, with no
pid and no host on the lease record. `run_crew.entry_liveness` — for the same
question, in the same repository — is three-state and pid-corroborated at 28800
seconds. They disagree by 16x, and the engine holds the blind one. Candidate A
found this; Entry 5 depends on it and does not fix it.

So after M1, a Commander that has been thinking hard for thirty-one minutes renders
`LEASE STALE — owner silent 31m; reclaim with claim`, to an honest agent that has
been taught to believe the display. Today that agent reads `LEASE active` and,
being honest, leaves it alone. The current lie is biased toward inaction; M1's
error is biased toward seizure. **A display that is confidently wrong in the
direction of action is worse than one that is quietly wrong in the direction of
caution**, and #357's own comment is the precedent: it lists the death signals that
were "all consistent with a commander that is still running," and the one signal
that is not — a live process — is the one the engine cannot see.

The mitigation is inside Entry 5's rules: render the **age**, not a verdict, and
never render an imperative. "owner silent 31m" invites a judgement; "STALE, reclaim
it" issues an instruction. But this is a real cost and it is the reason Entry 5
should not ship alone: recording `pid` and `host` on the lease and pointing both
liveness answers at one predicate is A's contribution, it is small, and Entry 5's
honesty depends on it.

Second-strongest argument, which I will state and then answer: **messages rot and
nothing tests them.** This is not speculation — the repository proves it. In
`run_crew.py` alone I found two comments that are now false: `:758-762` claims the
door raises `KeyError` on unset `SPINE_FILE`/`SPINE_ENGINE` (removed by #603) and
`:782-783` claims the external backend refuses `--spine` (it accepts and records
it). Both are load-bearing explanations for decisions in that file. So a
messages-and-defaults design decays in exactly the way a structural one does not.
The answer is that M1-M2 and M4-M5 and M7 are **code with tests**, not prose; only
M6 is prose, and M6 is doctrine that would be needed under every other candidate
too. But the point stands against M6 specifically and it should be tracked.

---

## 5. What all five have in common that none of them questions

### 5.1 The convergence on identity/naming: real insight in the diagnosis, shared blind spot in the remedy

Three lanes with three different seeds landed on the same underlying defect, each
citing independent source evidence: A on `session_id_for` making identity a function
of the plan; B on `origin.parent` present in the schema and empty on all 732 plans;
C on the child plan having "no identity of its own, only a path." That is genuine
convergence from different directions on a verifiable fact, and I believe the
diagnosis: **the child plan has no name, and `session_id` is doing four jobs.**

The remedy is a shared blind spot, and I think the frame caused it. All three moved
from *"the child has no name"* straight to *"therefore build a naming subsystem"* —
a roster, a lineage module, a plan registry. None asked the intermediate question:
**what mistake does the missing name cause, and is there already a carrier for the
same information?**

There is. The session string already encodes work-id, gate, role and attempt
(`constellation/<work-id>/<gate>/<role>/attempt-<n>`, parsed by
`run_crew.work_id_from_session`). `crew-runs.json` already records role, parent,
worktree, pid, heartbeat and abandonment. `origin` already carries work_id,
worktree and opened_by. The information is largely present. **It is not read, and it
is not displayed.**

The reason all three built structure instead of reading what exists is the
adversarial frame: if the risk is forgery, an identity must be *unforgeable*, and
unforgeable identity requires a registry a caller cannot write. If the risk is
honest error, an identity only has to be *legible*, and legible identity is a
display. Three lanes independently built a forgery-resistant naming layer for a
threat model the human has since deleted. C names its own version as "the design's
central bet"; B names its actor nonce as "not a boundary"; A says outright it is
"explicitly not defending against this." All three knew, and all three built it
anyway, because that is what the brief asked for.

**Verdict: the convergence on the diagnosis is real insight and should be kept. The
convergence on a structural remedy is a shared blind spot induced by the frame, and
round two should not inherit it.**

### 5.2 The bigger thing none of the five questions: whether the lease should be a guard at all

Every entry, including mine, treats the lease as the primitive and argues about how
to extend it — grants (A), custody resolution (B), a terminal state (C), a better
render (5). Nobody asks whether mutual exclusion is the right job for it.

Look at what the lease has actually bought, measured in this epic: 57 corpses that
present as owned; a five-step handshake to work around it; a refusal message that
routes into two filed bugs; an attribution smear in `claim --force`; and, at the
gate layer where the work actually lives, #357 measures that it protects nothing —
four mutating verbs from a session-less caller, accepted, on a plan whose parent had
just been force-claimed. In this whole corpus I cannot find one mistake the lease's
refusal prevented.

The alternative nobody put on the ballot: **demote the lease from a guard to a
presence marker.** It records who is here, when they last acted, and with what pid.
It refuses nothing. Everything the corrected criterion asks for — the system tells
the truth, the easy path is the correct path, refusals teach, failing closed is
cheap — is served better by an honest presence marker than by an exclusion
primitive that excludes nobody. #615 stops being a defect and becomes the design.
#357 stops being a defect and becomes a display problem. Large parts of A, B and C
dissolve.

I am not proposing this as a sixth entry; it is unscoped and I have not tested it.
I am naming it as the question all five of us walked past.

### 5.3 Two smaller unquestioned assumptions

- **That both dispatch channels should carry railed work.** All five design around
  the Agent-tool/`run_crew` difference. Nobody proposes the zero-machinery answer:
  railed work goes down one channel only. C's §9.5 comes closest and files it as an
  experiment rather than as a design.
- **That the archive is a place plans live rather than a place they end.** 53 of
  57 corpses are archived. Nobody proposed that a plan under `.agent-work/archive/`
  is terminal by definition — which is a one-predicate answer to most of the
  population that motivated three architectures.

---

## 6. Three questions to seed the second design round

**Q1. What mistake does the lease's refusal actually prevent — name one, from the
corpus?** If the honest answer is "none we can find," then the design target is a
presence marker and a truthful display, not an authority model, and A, B and C are
each solving a problem that the corrected threat model retired. This question is
cheap to answer and it invalidates or vindicates half the ballot on its own.

**Q2. What is the true liveness signal, and what may a display assert without it?**
Two answers to "is this owner alive" differ by 16x in one repository; the engine's
is heartbeat-only with no pid. Entry 5's whole value, and B's supersession and A's
`declare-dead`, all rest on this predicate. Settle it first: one predicate, pid- and
host-corroborated, and a rendering rule that shows age rather than issuing a verdict.
Every other design decision downstream gets easier once this is fixed.

**Q3. Should railed work be dispatched through one channel only — and what does one
wave through `run_crew --backend cli` actually reproduce?** This is C's §9.5 and it
is the cheapest decision-relevant experiment available: it costs a dispatch
convention and no code. If E1 and E2 stop recurring and E3 and E5b persist, the
authority work is earned and round two knows its scope. If E3 and E5b also stop,
this entire cluster was a dispatch convention, and three architectures were priced
against a channel nobody had to use. **Run this before round two designs anything.**

A fourth, if there is room: *what should an agent see when it opens a plan it does
not own?* All five entries designed the write surface. Nobody designed the read
surface, and under a criterion whose only adversary is an honest agent, the read
surface is where mistakes are made.
