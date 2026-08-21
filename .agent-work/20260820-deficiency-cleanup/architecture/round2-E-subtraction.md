# Round 2 — Lane E: subtraction

**Bias assigned:** removal. Every other lane has proposed adding. Under a
criterion where added machinery is a cost and ease of use is the goal, deletion
is the only move that pays before it is used.

**Constraints honoured.** Artifact only. No source, test, `map/` or GitHub
change; nothing committed; no `mcp__spine__*` call; Lane D's file unread. Every
line number below I opened myself in this checkout; every count I ran.

---

## 0. Position, in one paragraph

The lease is not a guard and never has been on the path that matters — but it is
not useless either, and the "demote it to a presence marker" framing is one step
short of the truth. **The lease is already a presence marker.** Eleven consumers
read `engine_session`. Exactly one of them refuses a *work* verb on the strength
of it — the one whose docstring calls itself "the actor-authority gate." The
other ten either govern the lease and the door binding themselves, or read the
field as "someone is here." That one prevents no mistake I can find in this
corpus, and it
*causes* the five-step handshake, because `waive` is in `MUTATING_VERBS`. So the
subtraction is not "delete the lease." It is: delete the pretence that the lease
is a permission, delete the ceremony an agent must perform to create one, and
delete every assertion the read surface makes that the data does not support.
What is left is smaller than what ships today, and the one guard in the system
that genuinely fires — the Stop hook's mid-flight block — gets *stronger*,
because it stops depending on an optional call that the main path has quietly
stopped making.

---

## 1. Method: what counts as a deletion here

A deletion is a line, a set member, a default, a required call, or a sentence of
doctrine that leaves the repository and takes a concept with it. Three things
that look like deletions and are not, and I will not count them:

- Replacing a check with a different check.
- Moving a concept from the engine into a hook.
- Deleting a field and adding a display that reconstructs it.

And one rule I applied to myself: **a deletion that breaks a fixture, a shipped
doctrine, or a decision another gate already spent is not a saving.** Section 6
is the list of things I tried to delete and could not, and it is longer than I
expected when I started.

---

## 2. What is the lease for? The measured answer

I stopped reading the arguments and enumerated the consumers of
`engine_session` in this checkout. There are eleven, and they fall into three
groups. Only the first group is a permission over work, and it has one member.

**Group 1 — refuses a work verb on the strength of the lease.**

| # | Consumer | Reads | Decides |
|---|---|---|---|
| 1 | `checklist_engine.require_session` (`:1124-1153`) | active lease + caller's `session_id` | refuses any `MUTATING_VERBS` member from a non-matching id |

**Group 2 — the lease and the binding governing themselves.** These refuse
lease/bind operations, not work.

| # | Consumer | Decides |
|---|---|---|
| 2 | `mcp_spine_server._spine_bind` R9 (`:1717-1742`) | refuses a second door binding a spine whose lease is live under the identity this bind would assume |
| 3 | `mcp_spine_server._rebind_refusal` (`:1352-1385`) | refuses a rebind that would orphan this door's own lease |
| 4 | `checklist_engine.heartbeat` / `release` (`:1267-1297`) | refuse a non-owner |
| 5 | `spine_lifecycle.closeout_refusal` (`:201-226`) | `close_work` refuses unless `status == "released"` |
| 6 | `spine_lifecycle._active_engine_session_spine` (`:300-331`) → `open_work` (`:431`) | refuses to open new work while a spine under that work id holds an active lease |

**Group 3 — read as presence or provenance; refuse nothing.**

| # | Consumer | Reads | Decides |
|---|---|---|---|
| 7 | `hooks/spine_rail._entry_mid_flight_view` (`:1644-1676`) | `status == "active"` | blocks a Stop while a gate is open |
| 8 | `hooks/spine_rail._reap_binding_entries` (`:311-364`) | `status == "released"` | prunes the binding store |
| 9 | `agent_work_root._active_epic_lease` (`:77-107`) | `status == "active"` and `claimed_by == "admiral"` | routes durable output away from a fenced main checkout |
| 10 | `checklist_engine._checklist_owner` (`:1471-1499`) → `gauge_reader.owner_key` and `_reading_predates_claim` (`:1617-1646`) | `session_id`, `claimed_at` | which gauge file the context governor reads, and whether a reading predates this session |
| 11 | `episode_capture._lease_role` (`:267-276`) | `claimed_by` | the episode's `role` field |

Plus two things that are not decisions but matter to this design:
`hooks/spine_rail.reconstruct_current` (`:644-670`) re-renders the engine's own
`LEASE active:` line from the state file — a second copy of the display lie, in
a file the engine never touches — and `run_crew._parent_lease_heartbeat`
(`:1498-1545`) keeps a blocked dispatcher's lease fresh from a daemon thread.

The shape of that census is the finding. **The lease refuses work in exactly one
place. Everywhere else it either polices its own lifecycle or answers "is anyone
here?"** An honest reading is that the system already treats it as a presence
marker and has one vestigial permission bolted to the front.

### 2.1 Consumer 1 cannot distinguish actors on the door path

`spine_lifecycle.session_id_for` (`:127-149`) is a pure function of the spine's
`work_id`: `constellation/<work_id>`. The door derives its session that way at
bind, and `mcp_spine_server` (`:593-599`) *refuses* any call that resolves
`--session-id` to anything else. So on the door path the caller's identity is a
restatement of the file's own name. Two different agents binding the same spine
present the same string, `require_session` compares them by plain string
equality, and both pass.

**The engine's actor-authority gate cannot tell two actors apart on the channel
the system ships.** That is not a weak guard. It is a guard whose input carries
no information.

Where it *does* fire is where an id was hand-supplied: `run_crew` claims under
`assignment_session_name` (`constellation/<work-id>/<gate>/<role>`,
`run_crew.py:198-206`), a human types one at the CLI, and the E3 corpse holds
`repair-reviewer-613-20260820`. So the population `require_session` refuses is
exactly the population using the *other* naming scheme — and the remedy it names
is unconditional (`claim` takes any stale lease from any directory under any id,
measured in Correction 2). It refuses, then tells you how to stop being refused,
in one call. That is a toll booth, not a gate.

### 2.2 The engine already ships the leaseless mode, deliberately and tested

This is the piece I had not seen argued anywhere, and it is decisive.
`checklist_engine.py:3733-3743`:

> Gated to `args.verb == "claim"` (#357 g1 review carry-over): a child gate plan
> is legitimately driven with `engine_session` staying None for its **ENTIRE**
> life, by design — start/attest/advance/reopen with no lease and no `claim`
> call, ever (the production shape #357 names).

There is a negative-control test asserting that a leaseless plan's `refusals`
key is structurally absent. So leaselessness is not drift and not an edge case:
it is a *named production shape* with a test defending it. The `run_crew`
experiment did not discover a hole; it exercised the shape the engine already
documents. Demoting the lease is not a change of direction. It is finishing a
direction the engine took two issues ago and never propagated to the door's tool
descriptions, the skills, or the display.

### 2.3 The one mistake the lease prevents — and it is not a refusal

Consumer 4 is the answer to the cold critic's Q1, and it is not in the engine.

`_entry_mid_flight_view` returns `None` — *allow the Stop* — when the bound
spine's lease is not `active`. A never-claimed spine has `engine_session: None`,
so `lease.get("status")` is `None`, so the Stop hook allows. **A leaseless run
is not Stop-guarded.** The reviewer crew in the channel experiment drove seven
gates with the anti-abandonment guard inert for the whole run. It happened to
finish, so nothing was observed — but "quiet abandonment" is one of the two
forbidden exits in the engine's own check-failure rail, and the mechanism that
catches it was switched off by an omission nobody noticed.

So: **the lease's refusal prevents nothing; the lease's record is what arms the
one guard that fires.** That inverts the design target. The problem with the
lease is not that it is too weak to exclude. It is that the thing worth having —
presence — is optional, and the thing not worth having — permission — is
mandatory. Both are backwards.

---

## 3. The deletion ledger

Each entry: what leaves, the mechanism, what breaks, who depends, verdict.

### D1 — Delete `"current"` from `RAIL_VERBS`. **Ship this first.**

`checklist_engine.py:457`. One token in a set literal.

**What it removes.** The single worst artifact in the epic. A 23-day-dead plan
today renders `RAIL: A working solution is the MIDDLE of this run — you are 7
steps from done. Next: the ACTIVE line above. Run it.` `current` is the only
railed verb that a **non-owner** routinely calls: `claim`, `start`, `advance`,
`attest`, `attach` are all things you call *after* you have decided this plan is
yours. `current` is what you call to find out. Rail on `current` is doctrine
addressed to an owner, delivered to a reader who may be a stranger, with no way
for the engine to tell which — because `current` declares no `--session-id` at
all (`mcp_spine_server.py:536`).

**Why this is the honest fix and not a suppression.** #420 already found this
from the other side: it special-cased the mid-flight rail on `current` because
`render_human`'s `ACTIVE` line *already prints the imperative*, so the rail was
duplicating it (`:504-521`). The rail on `current` was already known to be
carrying no information; #420 shortened it instead of removing it. The owner
loses nothing: they still get the rail on every verb they actually run.

**What breaks.** `tests/test_checklist_engine.py:2040-2048`
(`test_rail_verbs_set_is_exact`) pins the set verbatim — one assertion, a
deliberate edit. Every other `_rail("current", cl)` in that file calls `_rail`
directly, which does not consult `RAIL_VERBS`, so they pass unchanged.
`tests/test_mcp_imperative_equivalence.py:196-210` explicitly tolerates the rail
being present *or* absent (it scans every line for `ACTIVE`), and its docstring
would need one sentence updated. The five `_RAIL_STRINGS` stay byte-identical,
so #145's frozen-string measurement precondition is untouched — I am changing
*when* doctrine is delivered, never *what it says*.

**Who depends on it.** Nobody I can find who is not the owner. `RAIL_VERBS`
appears in exactly two source places (`:457`, `:3539`).

### D2 — Delete `"waive"` from `MUTATING_VERBS`. This is the five-step handshake.

`checklist_engine.py:72-77`. One token in a second set literal.

**The handshake's actual mechanism, traced.** The standing lesson says "the
engine refuses a crew waiving its own bound spine's check; recover via
release → parent claims → parent waives → parent releases → child reclaims."
The cold critic found `waive` (`:3303-3348`) has no session, lease or self-waive
check and concluded the refusal "is not in the engine at all." **Both are half
right, and the missing half is the whole fix.** `waive` is in `MUTATING_VERBS`,
so `require_session` gates it before `waive` is ever entered. The parent cannot
waive a child's condition while the child holds a fresh lease — so the child
must release, and the parent must claim, and then unwind. Every one of the five
steps exists to satisfy consumer 1.

Take `waive` out of the set and the sequence is: the crew calls `spine_halt
action=block` (which is what the deny hook already tells it to do), the parent
answers, the parent runs one CLI `waive --authority "<parent>" --reason "..."`
against the child's file. **One call.** No lease transitions, no identity swap,
and — per the critic's §1.4 — a *better* record than the sanctioned dance, which
writes `previous_session_id: null` and `takeover_reason: null` because the lease
was released rather than seized.

**Why this loses nothing.** `waive` is the one verb that already carries its own
attribution: it refuses an empty `--authority` (`:3325-3326`), refuses an empty
`--reason` where policy requires it, refuses entirely unless
`override_policy.allowed` or an explicit `--force`, and journals a `waiver`
evidence record naming the authority verbatim. It is the *most* self-attributing
verb in the engine. Session-gating it adds a second, weaker attribution on top
of a strong one and charges four extra calls for it.

**What breaks.** The `MUTATING_VERBS` set is read at `:1136`, `:3531`, `:3788`.
`:3788` decides whether to append a journal entry — so removing `waive` from the
set would *also* stop journaling waives, which is unacceptable. **This is the
one place D2 needs care: split the set, or exempt `waive` inside
`require_session` rather than removing it from `MUTATING_VERBS`.** Exempting
inside `require_session` is one line and preserves journaling; it is the form I
would ship. I flag it because a naive one-token edit here silently deletes the
waiver audit trail, which is the opposite of the intent.

**Who depends on the refusal.** Nothing automated. The five-step dance is
performed by hand, over messages, by agents.

### D3 — Delete the verdict from the lease display; keep the facts.

`checklist_engine._lease_line` (`:1300-1308`) formats `LEASE active: <id> (by
<who>, heartbeat <ts>)` and never calls `_is_stale` — which is called in exactly
four places in the repo and none of them is a rendering path.

**What leaves.** The word `active` as an assertion about the present, and the
raw ISO timestamp as the only liveness information offered. What replaces them
is *not* a better verdict. It is the same facts with the arithmetic done:

```
LEASE constellation/20260728-charter-refresh — held by charter,
      last heartbeat 2026-07-29T17:52:38Z (23d 4h ago)
```

**Why age and not a staleness verdict.** The cold critic's §4 is right and it is
the strongest argument against Entry 5: `_is_stale` is heartbeat-only at 1800s
while `run_crew.entry_liveness` answers the same question pid-corroborated at
28800s — 16x apart, and the engine holds the blind one. A rendered verdict makes
the display authoritative on a signal that is a guess, and biases the honest
agent toward *seizure*. A Commander thinking hard for 31 minutes would render
STALE.

Rendering age sidesteps this entirely, and — this is the part I did not expect —
**it is cheaper than Entry 5's version.** Entry 5's M1 has a real, named cost:
`state(cl)` takes no `config` and is pinned as a pure projection, so a staleness
threshold has to be read at the render site or `config` threaded one level. Age
needs no threshold at all. There is nothing to keep in sync with
`entry_liveness`, nothing to disagree by 16x, and no number for a future issue
to tune. **The two liveness models stop needing to be reconciled on the read
path, because the read path stops asking the question.**

**The purity point, handled by a second deletion.** `state()` currently projects
`lease_line` as a **pre-formatted English string** (`:2426`) and `render_human`
just prefixes it (`:2536`). That is prose inside a pure projection, and it is
why age is awkward to add. Delete the pre-formatted string; project the lease's
fields, and format at the adapter where the clock already lives. The projection
gets smaller and more honest, and `_lease_line` — a formatting function inside
the leasing section of the engine — disappears.

**What breaks.** Anything asserting on the exact `LEASE active:` text.
`hooks/spine_rail.reconstruct_current` (`:644-670`) hand-reproduces the same
line and must be edited in lockstep or it becomes a second, divergent lie —
name it in the change, do not discover it later. `state()`'s
`_STATE_CONTRACT_VERSION` should bump.

### D4 — Delete the two remedies `require_session` recommends.

`checklist_engine.py:1148-1152` tells a non-owner to *"pass `--session-id '<the
holder's>'` or take over with `claim --force --reason ...`"* — impersonation
(#632's hazard) and attribution erasure (#369). The dossier calls this the
cheapest high-value fix in the epic and I agree, but as a *subtraction* it is
sharper than the dossier frames it: **the refusal does not need to recommend
anything.** It needs to say who holds the plan and how long they have been
silent. An honest agent that is told "this plan is held by `<id>`, last heartbeat
23d ago" will do the right thing without being handed a verb. Every verb the
message names today is a verb it should not have named.

Minimal form: state the holder, state the age, stop. If one sentence of guidance
survives, it should be *ask the holder*, not *take it*.

### D5 — Delete `--parent`'s optionality in `run_crew`.

`run_crew.py:2169` makes `--parent` optional; `_normalize_parent` (`:743-751`)
collapses absent/blank to `None`; `:1289` writes `"parent": None` into
`crew-runs.json`. The channel experiment measured exactly that: `parent: null`
on a real parent dispatching through the channel built for it.

This is not a missing mechanism. It is a missing *argument*, on a flag the
dispatcher always knows the value of. Making it required deletes a default and
nothing else. It does not conflict with #559's fail-up doctrine: "never invent
one" binds the *crew*, which must not guess a parent it was not given; it does
not excuse the *dispatcher*, which is the one party that always knows. A
dispatcher with genuinely no parent types `--parent unknown` and says so on the
record.

See §5.3 for why this is the whole of the lineage answer.

### D6 — Delete closeout's false "the lease is still active."

`spine_lifecycle.closeout_refusal` (`:201-226`):

```python
session = spine.get("engine_session")
status = session.get("status") if isinstance(session, dict) else None
if status != "released":
    return "close refused: the lease is still active"
```

A spine that **never had a lease** has `engine_session: None`, so `status` is
`None`, so it is refused — and told that a lease it does not have is active. The
sanctioned leaseless production shape (§2.2) can therefore never be closed, and
the message sends the agent looking for an owner who does not exist.

Under the corrected criterion's question 3 — *do refusals teach?* — this is the
same class of defect as `require_session`'s two-filed-defects remedy, and I did
not find it named anywhere in this epic. Delete the false assertion: distinguish
"no lease was ever taken" (which should not refuse at all, or should say so)
from "a lease is open and must be released."

This is why D7 matters beyond tidiness: once presence is always stamped, `status`
is never `None`, the branch becomes reachable only when it is true, and the
message stops being a lie. Either fix works; doing neither leaves a refusal that
cannot be satisfied and does not say so.

### D7 — Delete the required `claim`, not the lease.

This is the largest item and the one that answers Q2 properly.

The door's `spine_lease` description (`:1826-1832`) says *"'claim' once before
any other mutating tool."* `require_session` says the opposite: *"with no active
lease a missing `--session-id` is fine."* The launcher prompt says a third
thing — *"Call `spine_status` first: your spine is already bound. Drive it gate
by gate"* (`run_crew.py:813-819`) — and never mentions claiming. The crew in the
experiment followed the launcher, not the door, and drove seven gates with zero
claims. **Three surfaces, three contracts, and the one the agent actually reads
is the one that omits it.**

Under the criterion, the fix is not to align the three by teaching harder. It is
to delete the step. The engine already has every ingredient: `claim` on a plan
with no lease simply *creates* the record (`:1240-1253`, no refusal path), and
`_refresh_owner_heartbeat` already maintains it. So: **when a mutating verb
arrives with a session id and there is no active lease, stamp presence.** No new
concept, no new field, no new verb — the writer already exists and is already
called. What leaves is a mandatory ceremony and, with it, the entire class of
mistake that is "forgot to claim."

**What this buys, concretely.** Consumer 4 — the Stop hook's mid-flight block —
starts working on the main path, where §2.3 shows it is currently inert.
**#615 closes without a guard**: a plan with no active lease stops existing,
which is a stronger answer than adding an ownership check to one.

**What breaks — three things, and they are real.** #427/#357 deliberately gated
`refusals`
arming to an explicit `claim` verb precisely so that the leaseless child-gate
shape carries no `refusals` key, and `tests/test_episode_negative_control.py`
asserts that absence is *structural*. Auto-stamping presence must therefore
**not** arm `refusals` — keep that gated to an explicit `claim`. If the negative
control asserts on `engine_session is None` rather than on the `refusals` key,
it breaks and the trade must be taken deliberately: I read the arming code and
the comment but did not open that test, and I am not going to assert what it
checks. **Verify before shipping.** This is the one item in the ledger with an
unresolved dependency.

**Second cost.** Presence-stamping writes on a path that previously did not
write a lease, and three refusals key off `engine_session` existing:
`spine_bind` R9 (§6.2) refuses a bind against a live lease under the derived
identity; `open_work` refuses while a spine under that work id holds an active
lease (`spine_lifecycle:300-331`, `:431`); and `closeout_refusal` requires
`status == "released"`. So after D7 a spine that used to be freely bindable and
freely closable while leaseless becomes bind-refused while a run is live and
**requires an explicit `release` before it can close**. The first two are the
correct behaviour (they are exactly "two agents on one plan"); the third is a
new obligation on a population that did not have one. All three are behaviour
changes on previously-open paths and belong in the migration note, not in a
later bug report.

**Third cost.** `evals/euler-{1,2,5}/checks/spine_completed.py` pins the lease
record's exact eight-field tuple and a monotonic
`claimed_at ≤ last_heartbeat ≤ released_at`. Auto-stamped presence must write
the same eight fields `claim` writes (it will, if it reuses `claim`'s writer) —
but any temptation to write a lighter "presence" record with fewer fields breaks
three eval anti-fabrication checks at once. Reuse the writer; do not invent a
second shape.

### D8 — Delete `spine_lease`'s "claim once before any other mutating tool."

Follows from D7. The sentence is false today and would be unnecessary after.
One string in one tool description. Listed separately because it is worth
shipping even if D7 is rejected.

And it is not merely unenforced — it is **contradicted by the other surviving
teaching surface**. `skills/workbench/references/checklist-engine.md:52` says:
*"A checklist with **no lease** behaves exactly as before: mutating verbs work
without `--session-id`. Only claim a lease when your workflow wires it."* #565
already retired most lease teaching from that file on the grounds that the door's
tool descriptions now carry it — and the description it handed off to says the
opposite of the paragraph it kept. Two surfaces, two contracts, and the agent
reads whichever it happens to open.

### D9 — Delete four docstrings describing a guard that was deleted in #609.

`origin_worktree_refusal` and its two verb sets were removed by #609 g2. Five
files still describe it as live:

- `scripts/mcp_spine_server.py:18-19` — *"worktree guard
  (`checklist_engine.origin_worktree_refusal`) compares a spine's…"*
- `scripts/mcp_spine_server.py:647-653` and `:1077`
- `scripts/run_crew.py:1002-1003` — *"`checklist_engine.origin_worktree_refusal`
  compares a spine's stamped `origin.worktree` against the engine's ambient
  cwd"*
- `scripts/init_work_area.py:161-163`

These are load-bearing explanations for decisions in those files, and they
describe a mechanism that does not exist. This is the literal form of the
brief's "a ceremony that exists because something used to need it" — the
ceremony survived as prose after the code left. The cold critic found two
already-false comments in `run_crew.py` and used them to argue that a
messages-and-defaults design decays; here are four more, all pointing at the
same deleted predicate. Deleting them is free and it removes the most likely
source of the next lane's wrong mental model.

---

## 4. What this costs

**Machinery.** Net negative in every unit I can count.

| Unit | Before | After |
|---|---|---|
| New modules | — | 0 |
| New verbs | — | 0 |
| Verbs removed | — | 0 (I tried; see §6.6) |
| Verbs made optional | — | 1 (`claim`) |
| New permission concepts | — | 0 |
| Permission concepts removed | — | 1 (the lease as authority over work) |
| New files/stores | — | 0 |
| New nouns to learn | — | 0 |
| Set members deleted | — | 2 (`current` from `RAIL_VERBS`; `waive` exempted) |
| Pure-projection strings deleted | — | 1 (`lease_line` prose) |
| False assertions deleted | — | 7 (2 remedies, 1 lease verdict, 1 closeout message, 4 stale docstrings — `mcp_spine_server` holds 3) |
| Doc surfaces edited | — | 2 (the door's `spine_lease` description, the workbench paragraph it contradicts) |
| Tests to edit | — | 1 pinned set + `reconstruct_current` coverage + closeout refusal text + the negative control (verify) |

**Learning burden.** Downward, though less than I first claimed. Today an agent
must hold: claim before mutating (except that a leaseless plan is fine, except
that the door says otherwise); the lease can refuse you; if it refuses, pass the
holder's id or force it; and if you need a waiver you cannot waive yourself, so
release and let your parent claim, waive, release, then reclaim. After: your
presence is recorded when you act; if you cannot satisfy a check, `block` and
ask up; the reader of a plan is told who is on it and how long ago they spoke.
`heartbeat` stays, and stays taught, because §6.6 shows it is real.

**Four rules become three, one contradiction is resolved, and none of the three
has a special case** — which matters more than the count. Every rule I removed
was a rule with an exception attached.

**What it leaves open, honestly.**

- **#634 entirely.** Frozen bookends, mutable middle, and an Admiral's waves
  living in `ADMIRAL_LOG.md` outside the spine are real wants and no deletion
  touches them.
- **The archive-move deadlock (E5a).** Needs per-call path resolution. No
  deletion substitutes for it.
- **#632's in-session half.** The session-keyed binding file
  (`.agent-work/.spine-rail-binding.json`) is how in-harness subagents resolve
  to the parent's spine (M1). Nothing inside this repository can change how the
  harness assigns session ids. Doctrine is the only lever, and doctrine is what
  the critic's M6 already proposes.
- **Liveness quality.** D3 dodges the 16x disagreement rather than resolving it.
  If any future consumer needs a verdict rather than an age, the two predicates
  must be unified and `pid` recorded — and that is an addition, correctly out of
  my lane.
- **Cross-worktree *drive*.** A parent still cannot end a child's claim in one
  call from another worktree. It can read the plan today (the critic's §1.3
  proves it), and after D3 it can see how long the owner has been silent, and
  after D2 it can waive in one call. It cannot release. I did not find a
  deletion that grants that, and I do not think one exists.

---

## 5. The three questions, answered explicitly

### 5.1 Q1 — What should a plan display to a reader who does not own it?

This is the question my bias makes uncomfortable, so I will take it head on: the
honest answer is *not* "less." It is **fewer assertions and more facts**, and the
two are not the same thing.

The engine cannot tell who is reading. `current` declares no `--session-id`
(`mcp_spine_server.py:536`), and on the door path an id would carry no
information anyway (§2.1). **So do not branch on the reader.** Every proposal to
render differently for a non-owner needs an identity the read path does not have
and cannot get cheaply. Render one thing, and make it true for both.

What that means concretely, as three deletions and no additions:

1. **Delete the imperative** (D1). "Run it" is the only sentence in the output
   addressed to a specific person. It is the sentence that recruited the honest
   agent into the mistake. It survives on the five verbs whose caller has just
   demonstrably acted.
2. **Delete the verdict** (D3). `LEASE active` asserts a present-tense fact
   nothing checked. `last heartbeat … (23d 4h ago)` asserts only what the file
   says. The reader draws the conclusion; the system does not draw it for them,
   in either direction. This is the critic's own mitigation — *render age, not a
   verdict, and never render an imperative* — and I am adopting it as a rule
   rather than an option, because the 16x liveness disagreement means the system
   is not entitled to a verdict.
3. **Delete the assumption that "next" is addressed to the reader.** The
   `ACTIVE <id> [<status>] — <imperative>` line is a fact about the plan and
   should stay. It reads as an instruction only because the rail directly beneath
   it says "Run it." Deleting the rail (D1) fixes the framing without touching
   the line.

The residual after those three deletions:

```
ACTIVE orchestrator-context [in-progress] — <imperative>
LEASE constellation/20260728-charter-refresh — held by charter,
      last heartbeat 2026-07-29T17:52:38Z (23d 4h ago)
next: attest orchestrator-context --cond c1 ...
```

A stranger reads that and asks who `charter` is and whether they are coming
back. That is exactly the thought we want. An owner reads it and continues,
losing nothing.

**Where my bias is genuinely wrong on this question.** One thing is missing from
that display and no deletion supplies it: the plan does not say *what it is* —
which work, which role. The identity is in the session string
(`constellation/<work-id>`), which happens to be legible here, and in the file
path, which the engine deliberately does not read (#609). If a reader needs
"this is the reviewer plan for 613," subtraction cannot give it to them and one
line of addition can. I will not pretend otherwise. It is the smallest addition
anyone in this round has proposed and I would not fight it.

### 5.2 Q2 — Should the lease be demoted to a presence marker?

**It already is one, in ten of its eleven consumers. The demotion is a deletion of
one docstring's claim about itself, not a redesign.** `require_session` calls
itself "the actor-authority gate"; on the door path it compares a string to a
derived copy of itself (§2.1) and cannot fail, and where it can fail it names a
remedy that always works. Meanwhile the Stop hook, the binding reaper,
`durable_root`, the gauge owner key and episode capture all read the same field
as "someone is here" and none of them asks permission; and the refusals that
remain — bind, rebind, `open_work`, closeout — police the lease's own lifecycle
rather than the work.

So the answer is yes — with three corrections to how the question is usually
put:

- **Not "the lease refuses nothing, so delete it."** It powers the one guard in
  the corpus that genuinely fires (§2.3, and §6.2's bind refusal). Deleting the
  record breaks the Stop hook.
- **What should be deleted is the permission reading and the ceremony**, not the
  record: `require_session`'s gate on `waive` (D2), its two recommended remedies
  (D4), and the mandatory `claim` (D7). **Not `heartbeat`** — I tried, and §6.6
  shows a live machine caller keeping a blocked dispatcher's lease honest.
- **What it should cost is nothing.** A presence marker an agent must remember
  to create is worse than no marker, because it is absent exactly when the agent
  was distracted — which is the same moment the Stop guard was most needed. The
  cost of presence should be zero calls, which is D7.

Two things I want on the record against my own position. First, the bind
refusal (§6.2) is a real exclusion that fires and I would keep it — so "the
lease excludes nobody" is not literally true, and anyone repeating that line is
overstating. Second, `require_session` *is* the last standing ownership check
after #609 deleted `origin_worktree_refusal` explicitly on the grounds that
"ownership is the lease." Deleting it wholesale would complete a chain #609 did
not intend. That is why the ledger narrows it rather than removing it, and it is
the sharpest reason I have for not going further.

### 5.3 Q3 — Is the lineage edge worth writing at all?

**`origin.parent`: no. And the deciding edge already exists, is already
enforced, and nobody in this epic has mentioned it.**

I ran the corpus: 791 plans, 40 carry an `origin` block, and **`origin.parent`
is meaningful on zero of them.** `spine_lifecycle.build_origin` (`:165-196`)
says outright that the block "is PROVENANCE and nothing else" and that
`origin.worktree` in particular is "written here and read by nothing that
decides anything." `tests/test_spine_origin_isolation.py` pins that pairing.
Adding a *read* to `origin.parent` would reverse a property two issues (#568,
#609) worked to establish.

Now the part that changes the answer. `scripts/verify_declared_dispatch.py`
exists. `generate_spine.py` injects one `command`-kind postcondition per declared
`[[gate.dispatch]]`, and that oracle **refuses to advance the gate unless a
non-abandoned `crew-runs.json` entry for the declared gate/role carries the
declared parent and model** (`check_declared_dispatch`, `:36-60`). That is a
lineage edge that is written, read, and enforced at a gate, shipping today.

The channel experiment measured `parent: null` in the registry — not because the
carrier is missing but because the dispatch was ad-hoc (no `[[gate.dispatch]]`
to verify against) and `--parent` was omitted (D5). **The edge is not absent. It
is optional and undeclared.**

So:

- **Do not write `origin.parent` as an authority.** Nothing should read it.
- **Do not build a `lineage` block, a `plan_id`, or a plan registry.** Candidates
  B and C each propose a carrier for information that `crew-runs.json` already
  holds and `verify_declared_dispatch` already checks. The critic's §5.1 is
  right that this convergence is a frame artifact; the registry oracle is the
  evidence that makes it concrete.
- **Delete `--parent`'s optionality** (D5) so the enforced carrier stops
  recording null.
- **Keep `origin` as provenance** and keep `parent` in it if it is free — a
  spine can travel in a pushed worktree without its parent's `crew-runs.json`,
  and then the block is the only record of where it came from. That is
  `build_origin`'s own defence and I tested it against my bias and it holds.
  Fill it from the value `run_crew` already has; read it from nowhere.

**Answer in one sentence: the lineage edge is worth writing exactly once, in the
carrier that already decides something, and the work is deleting an optional
flag's default — not writing a second edge on the spine.**

---

## 6. What I tried to delete and could not

The exercise is only honest if this section is real. Six things survived the
attempt, and one of them — §6.6 — was already written into my ledger with a
clean-looking argument before a dependency check refuted it. That one is the
most useful entry here, because it shows what this lane's bias costs when it
runs unchecked.

### 6.1 The `PreToolUse` waive-deny hook — **keep, unchanged**

`run_crew.py:652-694`. Ten lines of inline Python denying
`spine_evidence action=waive` on `run_crew`-spawned crews.

The critic's M5 proposes making its predicate smarter (allow a waive naming
someone else). I cannot support that, and the reason is directly above the code:

> Ruling (human, verbatim): "agent cannot waive itself. I'll allow commander to
> waive crew, admiral to waive commander, human for admiral. always ask up."

This is a recorded human ruling, and the hook is the only mechanism implementing
it — `--authority` is a free string the engine records verbatim without
judgement (`:3320`), so a smarter predicate would be checking a field the caller
writes. Under "no bad actors" that is not a forgery worry; it is that an honest
agent under pressure will type its parent's name in good faith and believe it
has asked up. The hook's value is that it makes *asking* the only path, and its
denial message already names the one-step remedy (`spine_halt action=block`).

The five-step handshake is not this hook's fault (D2 shows it is
`require_session`'s), so fixing the handshake does not require touching the
hook. **After D2 this hook becomes the entire mechanism instead of the trigger
of a dance, and it gets better without changing.** That is the outcome I would
want and it costs nothing.

One thing worth fixing without deleting: the hook is installed **only on
`run_crew`-spawned crews**. In-harness subagents share the parent's door and
never see it — so the ruling binds exactly the channel that is already the
safest. Not my lane to fix; worth filing.

### 6.2 `spine_bind`'s R9 identity-held refusal — **keep**

`mcp_spine_server.py:1720-1740`. Refuses a bind when the target spine holds a
live lease under the identity this bind would assume.

This is the one place in the corpus where the lease's refusal prevents a named
mistake I can state concretely: *two door processes driving one spine under one
derived session id, indistinguishable to the engine.* Because the identity is
derived (§2.1), once both are bound the engine has no way to tell them apart —
so the refusal must happen at bind or it cannot happen at all. It is
staleness-gated, so a genuine respawn after a dead predecessor still works
(`tests/test_mcp_spine_bind.py:1026` documents exactly that). **This answers the
cold critic's Q1 in the affirmative, and it is not `require_session`.**

I tried to argue it away under no-bad-actors and could not: two honest agents on
one plan is precisely an honest-mistake failure, and it is the failure the
`_crew_door_env` comment records as already having happened once ("the child
claimed the DISPATCHER's lease instead of its own").

### 6.3 `_rebind_refusal` — **keep**

`mcp_spine_server.py:1367-1385`. Refuses a rebind that would leave this door's
own active lease held by nobody. It is scoped to a lease *this* process holds,
fails open in three directions, and reuses `_active_lease` rather than
re-deriving. It manufactures orphans if deleted, and orphans are the corpses
this whole epic is about. Deleting it would create the defect we are fixing.

### 6.4 `require_session` in full — **cannot justify; narrow it instead**

I wanted this one. Three things stopped me.

1. **#609 already spent it.** The module header (`:88-110`) records that
   `origin_worktree_refusal` was deleted on the reasoning that it "was never a
   boundary" and that "under an active lease held by another session, nothing
   changed (`ADMIRAL_RULING-1` R1)." The lease refusal is the guard that
   deletion leaned on. Removing it now completes a chain that ruling did not
   authorise. Deleting a check whose predecessor was deleted *because this one
   exists* is not subtraction; it is a delayed second deletion nobody voted for.
   The dependency is not only prose: `tests/test_spine_origin_isolation.py`
   pins `MUTATING_VERBS` explicitly because it is *"the surviving SIBLING of the
   two verb sets asserted absent"* and *"`require_session` gates exactly this
   set — so it cannot quietly disappear."* A test exists whose stated job is to
   stop exactly this deletion happening quietly. It should stay.
2. **`spine_lifecycle._advance_and_release` depends on it.**
   `tests/test_spine_lifecycle.py:1605-1626` pins two behaviours — a non-owner's
   advance is refused before any release is attempted, and a non-owner's release
   reports `stage: release`. That is closeout's contract, and it would silently
   widen.
3. **The CLI path is the one place identity carries information.** A human or a
   parent typing `--session-id` supplies a string that is *not* derived from the
   file. That is the only channel where "you are not the holder" is a real fact.
   It is also where the E3 corpse lives.

**Minimal remaining form:** exempt `waive` (D2) and delete the two recommended
remedies (D4). Everything else stays. That is roughly two lines, and it removes
the handshake and the two-filed-defects message without touching the contract
#609 and closeout both rest on.

### 6.5 `origin.worktree` — **keep**

Read by nothing that decides. I tried the obvious argument — `crew-runs.json`
records the worktree, so the spine's copy is redundant — and it fails: a spine
travels in a pushed worktree without the dispatcher's registry, and then the
block is the only record. `build_origin` says exactly this and it is right.
Provenance that nothing reads is not dead weight if it is the only copy that
travels.

### 6.6 The `heartbeat` verb — **I drafted this deletion and it is wrong**

I had `heartbeat` in the ledger. The argument was: `_refresh_owner_heartbeat`
(`:1109-1122`) already stamps after every successful mutating verb, so
`heartbeat` serves only a genuine idle gap — and an agent in a genuine idle gap
is not making tool calls, so the verb can only be called by an agent that did
not need it. A concept in nine documents serving a case that cannot occur.

**The case occurs, and the system already handles it.**
`run_crew._parent_lease_heartbeat` (`:1498-1545`, issue #607) is a context
manager that reads the *dispatcher's* own `SPINE_FILE`/`SPINE_SESSION` and beats
its lease from a background daemon thread for exactly the duration of a blocking
`launch(...)`. A Commander that dispatches a crew blocks foreground and issues no
mutating verb of its own while it waits — *"a healthy, still-blocked parent's
lease can go stale purely from being blocked, even though it is very much
alive."* It is used at `:1676` and `:1751` and pinned by
`tests/test_crew_launcher.py::ParentLeaseHeartbeatTests`.

My premise — that a live agent in an idle gap cannot call the verb — is exactly
false: the agent is blocked, and a *thread* calls it. This is also the
counter-example to the cold critic's §4 worry in its strongest form: the
long-silent-but-alive owner is real, it is the common case for any dispatching
parent, and #607 already solved it. `heartbeat` earns its keep, and nine
documents teaching it are teaching something true.

Two things follow that I would not have seen otherwise. First, the fix is
*asymmetric*: only the dispatcher's lease is beaten, so a **Commander thinking
hard without dispatching** still goes silent, which is precisely the false-STALE
case — one more reason D3 renders age rather than a verdict. Second, this is the
best single argument that the lease is worth keeping as a record: someone
already spent an issue making it stay honest under blocking.

### 6.7 One idea I rejected before proposing it

"A plan under `.agent-work/archive/` is terminal by definition" (the critic's
§5.3) is a one-predicate answer to 53 of the 57 corpses, and it is tempting. It
cannot live in the engine: **the engine reads no location at all**, ambient or
derived (#609 g2), and reintroducing a path read to answer a display question
would undo that on the cheapest possible pretext. It could live in closeout or
in the hook, which do read paths. Not a deletion either way, so out of my lane —
but worth recording that the appealing version of it is doctrinally blocked.

I also checked whether the 57 corpses harm anything besides readers. They do
not: `agent_work_root._active_epic_lease` and the hook's session-start scan both
glob `.agent-work/*/spine.json`, which does not reach `.agent-work/archive/`. So
the archived corpses are a **read-surface problem only** — which strengthens D1
and D3 and weakens any proposal to sweep them.

---

## 7. Migration

Ordered so each step is independently revertible and no step depends on a later
one.

1. **D1** (`current` out of `RAIL_VERBS`) + the one pinned test line. Ship
   alone. No state change, no migration, no file touched twice.
2. **D4** (delete the two recommended remedies). Strings only.
3. **D3** (lease display: facts + age; delete `lease_line` prose from `state()`;
   update `reconstruct_current` in the same change; bump
   `_STATE_CONTRACT_VERSION`). No plan file changes.
4. **D2** (exempt `waive` inside `require_session`, **not** by removing it from
   `MUTATING_VERBS` — journaling at `:3788` reads that set). One line + a test.
5. **D9** (delete four stale docstrings). Comments only; no behaviour. Cheap
   enough to ride with any of the above.
6. **D5** (`--parent` required). Breaks any caller that omits it — the Admiral's
   own bootstrap is the likely one; it becomes explicit, which is the point.
7. **D6** (closeout's false "the lease is still active"). One branch, one
   message, one test.
8. **D8** (the door's claim-first sentence, and the workbench paragraph it
   contradicts). Two doc surfaces; settle which one is true first.
9. **D7** (presence stamped instead of claimed). Last, because it is the only
   item with a behaviour change on three refusal paths. **Verify
   `tests/test_episode_negative_control.py` first**; keep `refusals` arming
   gated to explicit `claim`; reuse `claim`'s eight-field writer so the eval
   checks hold; state the `spine_bind` R9, `open_work` and `closeout_refusal`
   consequences in the change description. If D7 is dropped, D6 becomes
   mandatory rather than optional — one of the two must fix the leaseless
   close.

**No plan-file migration anywhere.** Nothing in this design rewrites the 791
existing plans, and the 57 corpses stop lying the moment D1 and D3 land, without
being touched.

---

## 8. Per-issue dispositions

| Issue | Disposition |
|---|---|
| **#634** — frozen bookends, mutable middle, one spine per agent | **Untouched. Leave open.** No deletion addresses it and I will not pretend one does. It is the only issue in the cluster that survives the corrected frame fully intact and it should be designed on its own terms, not as a rider on the lease. |
| **#638** — door's fixed path/identity/spine | **Split and mostly close.** The *read* half is already solved and no candidate said so: `current` is non-mutating, `require_session` returns early for non-mutating verbs (`:1136-1137`), and the engine reads no location — a parent can read any child's plan today. What blocks it is doctrine, not mechanism. The *drive* half stays open and is genuinely hard (E5a's archive-move deadlock is its sharp edge). Retitle to the drive half; close the read half on evidence. |
| **#632** — helper agent inherits the launcher's spine | **Two mechanisms under one number; split it.** The subprocess half is a default change in `crew_env` (the critic's M4) — real, cheap, out of my lane since it changes a default's direction rather than deleting one. The in-harness half is the session-keyed binding file (M1) and **cannot be closed from inside this repository**; it is a doctrine item. Filing them as one issue is why three lanes designed for the wrong mechanism. |
| **#357** — the lease does not protect the gates | **Reframe, then close by D7.** The issue is written as "the lease buys no exclusivity." Correct, and after this design it is not supposed to. What #357 actually wants is that a child gate plan record who is on it, and D7 gives it that without a guard. Note the irony on the record: `checklist_engine.py:3733-3743` cites #357's own review as the reason leaseless plans are *sanctioned*. The issue and its own fix already disagree. |
| **#369** — resume-side obligations, `claim --force` erases attribution | **Mostly closable now.** E4 measured that the spine surface already records `previous_session_id` and `takeover_reason`, and Correction 2 measured that a plain stale-lease `claim` writes `takeover_reason: "stale lease reclaimed"` automatically. The remaining half is the child plan, which D7 closes by making the record exist. D4 removes the message that recommends `--force` in the first place, which is the erasure path #369 complains about. Recommend closing with the measurement attached. |
| **#615** — a spine with no active lease has no ownership guard | **Closes, and not the way it asks.** #615 asks for a guard on the leaseless path. The answer is that the leaseless path stops existing (D7): presence is recorded because you acted, not because you remembered. No guard is added. Close as "resolved by making the case unreachable," with the note that the *deliberate* leaseless shape (`:3733`) is what this supersedes — which is a decision a human should ratify, not a mechanical closure. |

---

## 9. Risks

1. **D7 collides with a deliberate design and I could not fully verify it.**
   The leaseless child-gate shape is documented in the engine and defended by a
   negative-control test I did not open. If that test asserts on
   `engine_session is None` rather than on the `refusals` key, D7 breaks it and
   the trade must be taken explicitly. **This is the item most likely to be
   wrong.**
2. **D1 deletes doctrine delivery at the highest-traffic verb.** #138 shipped
   the rail to put doctrine at every decision point. Reading a plan *is* a
   decision point, and I am removing the doctrine from it. My defence is that
   the doctrine delivered there is addressed to someone who may not be the
   reader, and #420 already found it redundant with the `ACTIVE` line. If the
   fleet measures a drop in rail-driven behaviour after this, I am wrong and it
   should be reverted — it is one token.
3. **Rendering age rather than a verdict pushes judgement onto the agent.** A
   verdict is easier to act on, and I am deliberately making the display less
   actionable. The critic's §4 argues that is the right direction (today's lie
   biases toward inaction; a confident wrong verdict biases toward seizure), and
   I agree — but it is a bet on agents reading "23d ago" and drawing the
   conclusion. If they read it and act anyway, a verdict would have been better.
4. **My own subtraction instinct produced one wrong deletion in this document.**
   I drafted "delete `heartbeat`" with a clean argument and it was refuted by a
   single function I had not read (§6.6). The bias I was assigned is productive
   and it is also exactly the bias that skips the dependency check. Anyone
   adopting this ledger should re-run the census against each item rather than
   trusting the reasoning, including mine.
5. **Corpse harm is narrower than the epic assumes, which cuts both ways.**
   `_active_epic_lease` and the hook's session-start scan glob
   `.agent-work/*/spine.json`, which does not reach `.agent-work/archive/`, so
   the 53 archived corpses mislead readers and nothing else. But
   `_active_engine_session_spine` rglobs `*.json` under one work id, so a stale
   child plan *inside a live work dir* can refuse `open_work`. Narrow, real,
   and not addressed here.
6. **`_crew_door_env` writes the assignment-keyed session while `spine_bind`
   derives `constellation/<work_id>`.** Two naming schemes for one lease
   identity. Nothing in my ledger fixes it, and D7 makes leases *more* common,
   so it makes the collision more likely, not less. A crew launched with
   `SPINE_SESSION=constellation/<w>/<g>/<r>` that later calls `spine_bind` gets a
   different identity for the same spine. **Filing candidate, and a risk this
   design increases.**
7. **Messages rot and nothing tests them** (the critic's §4, second argument).
   D9 is four instances of exactly this, and deleting them does not stop the
   fifth. D1–D7 are code with tests; D8 and D9 are prose and will decay again.
   The honest response is that a prose fix is still worth making — but nobody
   should score it as durable.

---

## 10. How someone would know it worked

Falsifiable, measurable on this checkout, no new instrumentation.

1. **The corpse test.** Copy any archived plan whose owner died weeks ago into
   scratch, run `current` from `/tmp`. Success: no `RAIL:` line, no `Run it`, no
   `LEASE active`, and an age in days. Failure: any imperative survives. This is
   the exact reproduction in the critic's §1.2 and it is a one-command check.
2. **The handshake count.** Count message round-trips for the next waiver a crew
   needs. Today: five engine calls across two agents with a wait in the middle.
   Success: one `spine_halt block`, one message, one `waive`. Failure: any lease
   verb appears in the sequence.
3. **The verb census, re-run.** Repeat the channel experiment's journal census on
   the next `run_crew` dispatch. Today: `0 claim / 0 release`. After D7, success
   is a lease record present on the plan at completion **with zero `claim` calls
   in the journal** — presence without ceremony. If `claim` calls reappear, D7
   did not land where intended.
4. **The Stop guard, directly.** Kill a `run_crew` crew mid-gate. Today the Stop
   hook allows (§2.3, leaseless ⇒ `_entry_mid_flight_view` returns `None`).
   Success: it blocks. **This is the only test that measures a mistake actually
   prevented, and it is the one I most want run — including before any change,
   because if it already blocks then §2.3 is wrong and D7's main justification
   goes with it.**
5. **The registry edge.** After D5, every `crew-runs.json` entry carries a
   non-null `parent`. `verify_declared_dispatch` then has something to verify.
   Today: null on the one real dispatch we measured.
6. **The leaseless close.** Drive a spine with no lease to fully terminal and
   call `close_work`. Today it refuses with *"close refused: the lease is still
   active"* about a lease that never existed. Success: it closes, or it refuses
   with a sentence that is true. This one is worth running **before** any
   change, because if it already closes then D6 is wrong.
7. **The negative one.** Count new `active` corpses per completed run. This
   design does not sweep them and does not stop them being created — it stops
   them lying. If a future reader is still misled after D3, the fix failed and
   the sweep (the critic's M7) is needed after all.

---

## 11. Ship first, and the one thing

**Ship first: D1 — delete `"current"` from `RAIL_VERBS`.**

One token. It removes the sentence that recruits an honest agent into the
mistake, on the verb a stranger is most likely to call, for every one of the 57
corpses and every future one, with no state change, no migration, no new
concept, and one test line to edit. Nothing else on any lane's ballot has that
ratio.

**If I could ship only one thing: still D1.**

D3 is more complete and D7 is more consequential, but D1 is the only item that
is a strict removal with no replacement to design, no threshold to choose, no
purity question to settle, and no test to verify first. Under a criterion that
prices added machinery as a cost, the change that adds literally nothing and
deletes the specific string that caused the specific documented harm is the one
to take.

**And the honest counterweight**, because a lane that only argues its own bias is
useless: D1 alone leaves `LEASE active` on the corpse. The reader is no longer
*instructed* into the mistake, but they are still *told a falsehood*. D3 is what
makes the display true, and it should follow immediately. I am naming D1 first
because it is unarguable, not because it is sufficient.

---

## 12. Summary of the ledger

| | Deletion | Size | Verdict |
|---|---|---|---|
| D1 | `"current"` from `RAIL_VERBS` | 1 token + 1 test line | **ship first** |
| D2 | session-gating on `waive` | 1 line (inside `require_session`, not the set) | ship |
| D3 | the `active` verdict + `lease_line` prose from `state()` | render path + `reconstruct_current` | ship |
| D4 | the two remedies `require_session` recommends | 2 strings | ship |
| D5 | `--parent`'s optionality | 1 flag default | ship |
| D6 | closeout's false "the lease is still active" | 1 branch + 1 message | ship |
| D7 | the mandatory `claim` | presence stamped on first mutating verb | **verify the negative control first** |
| D8 | `spine_lease`'s "claim once before any other mutating tool" | 1 string + the paragraph contradicting it | ship |
| D9 | four docstrings describing `origin_worktree_refusal` as live | comments only | ship |
| — | the `PreToolUse` waive-deny hook | — | **keep** (human ruling; improves under D2 without changing) |
| — | `spine_bind` R9 identity-held | — | **keep** (the one refusal that prevents a named mistake) |
| — | `_rebind_refusal` | — | **keep** (deleting it manufactures corpses) |
| — | `require_session` in full | — | **keep, narrowed** (#609 already spent it; closeout depends on it) |
| — | `origin.worktree` | — | **keep** (the only provenance copy that travels) |
| — | the `heartbeat` verb | — | **keep — I was wrong** (§6.6; `_parent_lease_heartbeat` is a live machine caller) |
