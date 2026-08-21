# Round 2, Lane D — the read surface

**Bias:** design what an agent *sees*. Round 1 and the cold critic designed the
write surface — who may act, what verbs exist, what a refusal permits. The
central object here is the moment an agent opens or renders a plan.

**Constraints honoured.** Artifact only: no source, test, `map/` or GitHub
change, nothing committed, no `mcp__spine__*` call, Lane E's file unread. Every
number below I measured in this checkout; every command is reproduced inline.

---

## 0. The position in one paragraph

The system has four places where a plan is rendered to an agent, and not one of
them tells the agent whose plan it is or how old that claim is. Three of them
end in an imperative. The engine already holds every fact required to fix this —
the lease record, the journal sidecar, the file's own path — and a seam
(`dispatch()`) where the rail and the trip advisory are already composed from
exactly those facts. So the fix is not a subsystem, a store, or a noun. It is a
**fixed answer order** — *where, whose, when, what, and only then advice* —
applied at four sites that currently answer *advice, what* and nothing else.
The one thing I will not do is let the display issue a liveness verdict, because
I measured that the corroborating fact does not exist for 55 of the 57 plans
that motivated this epic.

---

## 1. What I measured

Reproduced live, `/home/tommy/projects/constellation-skills`, 2026-08-21. A
"plan" is a JSON object carrying both `tasks` and `items`.

```
plans in this checkout                                          775
  engine_session.status == "active"                              57
    under .agent-work/archive/                                   53
    not archived                                                  4
  no active lease (never claimed, or released)                  718
```

**The 718 is the finding nobody in this epic has named.** The whole cluster has
been argued over the 57 leases that lie. The 718 plans that hold no lease render
**no ownership line at all** — and that is not an accident of neglect, it is the
designed shape. `checklist_engine.py:3730-3742`:

> *"a child gate plan is legitimately driven with `engine_session` staying None
> for its ENTIRE life, by design — start/attest/advance/reopen with no lease and
> no `claim` call, ever (the production shape #357 names)."*

The channel experiment measured the same thing from the other side: seven gates
driven to consolidation with `0 claim / 0 release`. So the **majority read case
in this system is a plan with no lease**, and on that case today's read surface
says nothing whatsoever about who is here — while still printing the rail and
the next command. Reproduced, on an archived leaseless plan six days dead:

```
$ python3 scripts/checklist_engine.py --file <copy of archive/2026-08-15-tc1-.../execute.json> current

RAIL: The finish is a sequence, not an announcement. Final `advance` first,
      then `release` — the journal, not your prose, is the proof.

ACTIVE g1-verify [in-progress] — Run `python -m pytest -q ...` ... Commit ...
                                 and push to tc1/worktree-identity.
1/4 met
next: attest g1-verify --cond c2 --which postconditions | attest g1-verify --cond c3 ...
```

No lease line, because there is no lease. An instruction to commit and push to a
branch, and two commands to paste. **The 57 lying leases are the smaller half of
this defect.** Fixing only the lease line leaves 718 plans rendering an
imperative over silence.

### 1.1 The corroborating fact does not exist

The critic's strongest objection to Entry 5 is that a display made authoritative
on a blind signal manufactures seizure. Candidate A's fix was to corroborate
against `run_crew`'s pid. I tested whether that join is available:

```
crew-runs.json files                                            100
registry entries                                                545
  entries carrying a `spine` path                                77
    registry sitting in the same directory as that spine          2
  entries carrying no spine at all                              468

lease session_id of the 57 active-lease plans found in ANY crew-runs.json:  2
```

The registry lives in the **dispatcher's** `.agent-work/<work-id>/`; the crew's
spine lives at the same relative path inside a **different worktree**. Two of 77
are siblings. A renderer standing at a plan cannot reach its registry entry, and
even up-channel the join by session id succeeds 2 times in 57.

**So pid corroboration is unavailable for 96% of the population that motivated
this epic.** This is not an argument for building the join; it is the measured
reason the display must render age and never a verdict. I keep the brief's
constraint, and I keep it for a stronger reason than caution.

### 1.2 A better signal that already exists — the journal sidecar

Every successful mutating verb appends one hash-chained line carrying `ts`,
`verb`, `task` and `session_id` (`append_journal_entry`, `:3648`). It is written
**regardless of whether a lease is held**, which is exactly the case the lease
cannot cover.

```
plans with a readable journal tail                        593 / 775
  tail names a session_id                                 561
of the 718 plans holding no active lease:
  have a journal tail (last verb + timestamp)             542
  that tail names a session_id                            510
```

So for **510 of the 718 leaseless plans the system can already say who last
acted, doing what, and when** — from a file that already exists, using
`_read_journal_tail`, which already exists and is documented never to raise.
Zero new fields, zero new stores, one existing function called from a seam that
already reads files.

Two honest limits. The journal is best-effort and swallows `OSError`, so 176
leaseless plans have none — the render must then say nothing rather than guess.
And 32 plans have a journal whose tail carries `session_id: null` — #357's true
anonymous shape, which no display can fix (§7).

The journal is also not a better *clock* than the heartbeat; it is a different
one. Of the 57 active leases, the journal tail is newer than the heartbeat in
44 cases (by milliseconds — the journal write follows the stamp inside the same
verb) and older in 7. One case is materially divergent and instructive: this
epic's own spine has a heartbeat ~20h newer than its last journaled action,
because a bare `heartbeat` verb refreshes the lease without doing anything.
**The lease clock answers "last said something"; the journal clock answers "last
did something."** Showing both, when they disagree, distinguishes an idle owner
from a working one — still two ages, still no verdict.

### 1.3 The behavioural cost of the lie, measured

```
plans carrying a takeover record (previous_session_id non-null):   25
  takeover_reason == "stale lease reclaimed"  (plain claim)         0
  reasoned / forced takeovers                                      25
```

**In the entire history of this repository, no one has ever reclaimed a stale
lease with a plain `claim`.** Every one of the 25 takeovers was a `--force`.
The engine offers a cheaper path that writes the attribution automatically — and
it has never been taken, because nothing has ever told a reader that a lease was
stale. That is the display lie's cost expressed as behaviour, not as a
complaint, and it is my primary falsifier (§11).

### 1.4 The four read surfaces, and what each currently says

| # | site | source | says whose? | says how old? | ends in an imperative? |
|---|---|---|---|---|---|
| 1 | `current` / door `spine_status` | `_lease_line` `:1300` → `state` `:2381` → `render_human` `:2520` → `dispatch` `:3496` | only if a lease exists, and only as a raw id | no — a raw ISO timestamp | yes: `RAIL: ... Run it.` + `next:` |
| 2 | `require_session` refusal | `:1143-1152`, surfaced by `main()` `:3782` | yes | says "stale", no age | yes — and both remedies are filed defects |
| 3 | Stop hook | `spine_rail.reconstruct_current` `:644` via `decide_stop` `:1751` | duplicates the same lease string | no | yes |
| 4 | SessionStart hook | `reconstruct_current` via `decide_session_start` `:2000` | no | no | **yes, unasked** |

Site 4 is worse than the one in the brief and nobody has cited it. It fires on
`if lease.get("status") != "active": return {}` — the word `active` and nothing
else, no staleness anywhere near it — and injects:

> *"RESUMING an active Constellation spine run after a restart or compaction.
> ENGINE current -> … Pick the run back up at this gate and drive it through
> the engine."*

The `current` case at least required an agent to ask. This one arrives
unrequested, at the start of a session, before the agent has read anything, and
tells it to resume. A binding entry pointing at a spine whose owner died weeks
ago produces that text verbatim.

`_is_stale` (`:1083`) is called at `require_session:1143`, `claim:1222`,
`claim:1236` and `mcp_spine_server:1729`. None of the four sites above.

---

## 2. Boundaries

**In scope.** What a plan renders, at the four sites in §1.4, plus the door tool
description that teaches agents what `spine_status` means.

**Out of scope, deliberately.** Who may act; new verbs; any store; the lease's
mechanics; `_is_stale`'s threshold; cross-worktree drive. This design adds no
noun. An agent that learns nothing new must still read it correctly — that is
the test the whole thing has to pass.

**Two laws I will not break.**

- *Verb functions stay pure and location-blind.* #609 g2 retired every ambient
  location read from the engine. Everything I add lives at the `dispatch()`
  seam, which already composes the rail and already reads files for the trip
  advisory (`_trip_advisory(cl, base_dir)`, `:3502`). `state()` and the verbs
  are untouched by the impure parts.
- *A read never writes.* `current` must never stamp a heartbeat. Today it cannot
  (`_refresh_owner_heartbeat` runs only in the mutating branch), and making the
  read reader-aware (§3.2) is exactly the change that would tempt someone to
  wire it in. It gets its own pinning test.

---

## 3. The design

### 3.1 One rule: the fixed answer order

Every read surface answers, in this order, and stops as soon as it runs out of
facts:

```
1. WHERE   is this file a live work area, or an archive record?      path
2. WHOSE   who holds it — or, with no lease, who last acted?         lease | journal tail
3. WHEN    how long since that                                       age, never a verdict
4. WHAT    the gate, its conditions, the command that would advance  unchanged
5. ADVICE  the rail                                                  only if 2 is not "someone else"
```

Today the order is 5, 2 (partially), 4. Steps 1 and 3 are absent everywhere, and
step 5 runs unconditionally. That sentence is the whole design; the rest is
wording.

**Why this order.** An honest agent's first question on opening a plan is not
"what is next" — the system answers that fine. It is "is this mine to touch."
The system answers that last, or not at all, and then answers the second
question in the imperative mood. Reversing the order costs nothing and is the
entire mistake-prevention mechanism.

### 3.2 Who is reading

`current` takes no `--session-id` (`:3381` — a bare `sub.add_parser("current")`),
so the read surface is reader-blind by construction. One optional argparse line
fixes it; the door already holds `SESSION` and passes it on every mutating call
(`run_engine`, `mcp_spine_server:733-735`), so it can pass it here too.

This adds no concept: `--session-id` already exists on every other verb and
means the same thing. It converts a string comparison the agent must perform in
its head into one the engine performs. An agent that passes nothing gets the
identity-neutral render, which is strictly better than today's.

The obvious objection — an agent could pass someone else's id and be told the
plan is its own — is a no-bad-actors non-problem: `current` mutates nothing, and
a reader lying to itself about its own name is not a mistake the system can
prevent or is obliged to.

### 3.3 The renders

Facts only, one fact per clause, no adjective that implies a judgement. `active`
is replaced everywhere in the render by `HELD`: the stored value means *not
released*, and `active` is a liveness word doing a bookkeeping job. **I change
the word only in the renderer — never the stored data.** Migrating 775 files to
rename a status is machinery, and `_active_lease`, `require_session` and
`decide_session_start` all read the stored string correctly today.

**(a) The owner reads their own plan** — the common case, and it must not get
heavier. One line replaces one line; nothing is added.

```
HELD BY YOU (constellation/567-x/g2/implementer/attempt-1, implementer) — you last spoke 3m ago
ACTIVE g2-implement [in-progress] — …
1/3 met
next: attest g2-implement --cond c1 --which postconditions --evidence <evidence-id>

RAIL: A working solution is the MIDDLE of this run — you are 4 steps from done. …
```

Rail unchanged. Next line unchanged. Net change to the owner's experience: the
raw ISO timestamp becomes an age, and the word "YOU" appears.

**(b) A non-owner reads a plan whose holder has been quiet a long time** — the
brief's case, the 22-day charter plan, rendered under this design:

```
ARCHIVED — this file is under .agent-work/archive/. It records a finished run.
HELD BY charter-refresh-20260728 (charter) — not you; last heartbeat 22d 19h ago,
        last journaled action 22d 19h ago (start orchestrator-context)
ACTIVE orchestrator-context [in-progress] — Write docs/agents/ORCHESTRATOR_CONTEXT.md …
postconditions:
  c1 [unmet] artifact — ORCHESTRATOR_CONTEXT written and confirmed
1/2 met
next (for the holder): attest orchestrator-context --cond c1 --which postconditions --evidence <id>

RAIL: This plan is held by another session and it is not you. You are reading it,
      not running it. Leave it unless you know that session is gone; if you know it
      is, `claim` takes it and records the handover for you.
```

Four changes from today's output, and each earns its line:

- The `ARCHIVED` line is a **path** fact. No clock, no lease, no threshold — it
  cannot be wrong about liveness because it asserts nothing about liveness. It
  covers 53 of the 57 lying leases and every archived leaseless plan besides.
- `not you` is the identity comparison from §3.2.
- Two ages, from the lease and from the journal tail. When they agree (the
  normal case) the render collapses them to one clause; they are shown apart
  only when they disagree, which is the case worth seeing.
- `next (for the holder):` — two words. I considered **withholding** the command,
  which is what `decide_stop` already does for a foreign owner
  (`"(withheld: gate belongs to {})"`, `spine_rail:1758`). I rejected it, and
  the reason is §3.4.

**(c) A reader of a plan with no lease at all** — 718 of 775, and today a blank:

```
UNHELD — no lease has been claimed on this plan.
LAST ACTION constellation/567-d1/g3/reviewer/attempt-2 — record g3-dialect, 4d 2h ago
```

or, when the journal names nobody (32 plans) or is absent (176):

```
UNHELD — no lease has been claimed on this plan.
LAST ACTION record g3-dialect, 4d 2h ago (no session recorded)
```
```
UNHELD — no lease has been claimed on this plan. No journal beside this file.
```

The rail still prints here. This is the point I would defend hardest: **the
main path never claims**, so suppressing advice on unidentified readers would
break every correctly-running crew in the system to protect against a stranger.
Suppression keys off *"held by someone who is not you"*, never off *"you did not
identify yourself."* Getting this backwards is how a display fix becomes a
usability regression, and it is the most likely way to implement this design
wrong.

**(d) A reader of a genuinely live, busy plan** — the critic's 31-minute
Commander:

```
HELD BY constellation/epic-570/g2/commander/attempt-1 (commander) — not you;
        last heartbeat 31m ago, last journaled action 31m ago (start g2-implement)
```

No verdict. A reader who knows that Commander is alive leaves it alone; a reader
who knows it is dead claims it. Under a threshold-rendering design this line
reads `STALE — reclaim with claim`, and that is the seizure the critic warned
about. **The system supplies the age; the reader supplies the verdict; the
wording makes plain whose job is whose.** That is what "render age, never a
verdict" means operationally, and §1.1 is why it is not merely stylistic
caution: the fact that would justify a verdict is missing 55 times in 57.

### 3.4 Push versus pull — the rule that decides how much to show

The two hook sites and the two engine sites differ in one respect that matters
more than anything about ownership: **whether the agent asked.**

> A surface the agent *pulled* (`current`, `spine_status`) may show everything,
> labelled. A surface *pushed* into an agent's context unasked (Stop `reason`,
> SessionStart `additionalContext`) must carry no imperative about a plan it has
> not established belongs to the reader.

This explains and reconciles the two existing behaviours. `decide_stop`'s
withholding is right *because it is pushed* — text an agent did not request is
read as instruction. And it is why I do **not** copy that withholding into
`current`: a parent reading a stuck child's plan is the single most useful
cross-worktree capability the system already has (the critic's §1.3 — it works
today, forbidden only by prose), and hiding the `next:` line from it would
degrade a legitimate use to protect against a mistake the label already
prevents. Relabelling is cheaper than withholding and serves both readers.

Applied to site 4, the SessionStart resume text becomes:

```
RESUMING a Constellation spine run after a restart or compaction. Its lease was
last refreshed 22d 19h ago, by <session>. Check that this is still your run
before driving it. ENGINE current -> <reconstruct_current output>
```

It still resumes. It refuses nothing. It states the age it already has in hand
and moves the imperative behind a check the agent can actually perform.

### 3.5 The refusal texts

A refusal is a read surface — it is what an agent sees at the exact moment it is
about to make the mistake, which makes it the highest-value text in the system.
Both current branches teach an error.

**Branch 1 — held by a session that has not gone quiet** (`:1148-1152`):

```
checklist is owned by active session 'X'; pass --session-id 'X' or take over
with `claim --force --reason ...`
```

The defect is not that it names impersonation. It is that it names it **first,
to everyone, with no condition attached.** Reproducing a predecessor's session
string is legitimate and in fact required for a relaunched crew
(`run_crew.assignment_session_name`). What #632 describes is doing it when you
are *not* that run. The remedy stays; the condition is what was missing.

```
REFUSED: 'Y' cannot mutate this plan. It is held by 'X' (charter), which last
spoke 4m ago.

  If that run is YOU, resuming after a restart — pass --session-id 'X'. You are
  the same run, not borrowing a name. Never pass an id that is not yours.
  If it is still working — leave this plan alone and drive your own.
  If you know it is gone — `claim --session-id 'Y' --claimed-by <role>`. After
  30m of silence a plain claim takes it and records the handover for you. To
  take it sooner, add --force --reason "<what you know that the engine cannot>".
```

`claim --force` is named, deliberately. Correction 2 measured that force writes
both `previous_session_id` and `takeover_reason` — #369's live half is the
*child* plan, not this. Naming force with the condition "when you know something
the engine cannot see" is the honest description of what it is for, and §1.3
shows the real problem is the opposite of over-forcing: it is that nobody has
ever taken the cheap path, because nobody was ever told the lease was cold.

**Branch 2 — the holder has gone quiet past the threshold** (`:1143-1147`):

```
checklist lease 'X' is stale; `claim` it (same id or --force --reason) before mutating
```

Close, but it renders a verdict without its age, and `(same id or --force
--reason)` implies force is needed when it is not — which is plausibly why the
force:plain ratio is 25:0.

```
REFUSED: 'Y' cannot mutate this plan. It is held by 'X' (charter), silent 22d 19h
— longer than the 30m the engine waits before letting anyone else take it.

  `claim --session-id 'Y' --claimed-by <role>` takes it now and records the
  handover automatically (previous holder + "stale lease reclaimed"). No --force,
  no reason required.
```

**A verdict is legitimate here and only here.** On the write path the system must
decide something anyway — permit or refuse — so it must pick a threshold and
should say which one it picked and what age it measured against it. On the read
path it need decide nothing, so it must not pretend to. That is the principle
that reconciles this design with the brief's constraint rather than arguing
against it: *verdicts belong to the write path, ages to the read path.*

**Door tool description** (`mcp_spine_server:1814-1822`). Today `spine_status`
promises "the active gate's id, status and imperative… Read-only, no lease
required" and the word *stale* appears in zero door descriptions. It gains one
sentence: *"It also names who holds this plan and how long since they last
acted, so you can tell your own run from someone else's before you act."* One
string; the door's whole teaching surface is its tool descriptions.

---

## 4. What changes

Ten edits, in four files. No new module, verb, store, permission concept or noun.

| id | site | change | kind |
|----|------|--------|------|
| D1 | `dispatch()` `current` branch, `:3496` | if the plan's own path is under `.agent-work/archive/`, prefix the `ARCHIVED` banner and suppress the rail | seam predicate |
| D2 | `_lease_line` `:1300` | render `HELD BY … — last heartbeat <age>`; add `YOU`/`not you` when a reader id is supplied; `UNHELD` when there is no lease | render |
| D3 | `dispatch()` `current` branch | append `LAST ACTION <session> — <verb> <task>, <age>` from `_read_journal_tail`, when the lease is absent or its clock disagrees | seam read (existing fn) |
| D4 | `_rail_prefix` at `:3537` | held-by-another → the orientation string in §3.3(b) instead of the position rail | render |
| D5 | `render_human` `:2520` | `next:` → `next (for the holder):` when held by another | render |
| D6 | `parse_args` `:3381` | `current` accepts optional `--session-id` | one argparse line |
| D7 | `mcp_spine_server:2193` | `spine_status` passes `SESSION` through to `current` | one argument |
| D8 | `require_session` `:1143-1152` | the two texts in §3.5 | two strings |
| D9 | `spine_rail.reconstruct_current` `:644` | same lease line shape, with the age | render (stdlib duplicate) |
| D10 | `decide_session_start` `:2000` | the resume text carries the age and the check | one string |
| D11 | `mcp_spine_server` `spine_status` description `:1814` | one sentence | one string |

**Where the age is computed.** `state()` is documented as a pure projection and
takes no `config`. Note that **the age needs no config at all** — it is
`now - heartbeat`; only a *verdict* needs the threshold. So the cheap fix is
genuinely cheaper than the verdict fix. It still makes `state()` clock-dependent.
Follow the precedent already in this repository: `run_crew.entry_liveness` takes
a caller-supplied `now` so it stays pure and unit-testable. `_lease_line` and
`state()` take an optional `now` defaulting to `_now()`. No new concept, and
tests stay deterministic.

**Where D1 sits, and the law it brushes.** #609 g2 removed every location read
from the engine. D1 reads a path — honestly, that is a location read. Three
things make it acceptable and one of them is not "it's small":

1. It reads the path **the caller handed in** (`--file`), never ambient cwd. The
   retired read compared a stamp against the process's own location, which a
   `cd` prefix defeated. There is nothing here to forge and nothing to compare.
2. It **refuses nothing.** It changes advice. The retired comparison was a
   refusal, which is why its forgeability mattered.
3. It lives at the `dispatch()` seam, where the engine is already permitted to
   be impure (the rail, and `_trip_advisory`'s file reads). Verb functions stay
   pure and location-blind; the law's actual content is untouched.

I state it as a decision rather than burying it: **the engine may read the path
it was given, at the render seam, to describe — never to refuse.**

---

## 5. Cost

**Machinery.** Four render functions, two seam predicates, five strings, one
argparse line, one tool-description sentence. One existing function
(`_read_journal_tail`) gains a second caller. One optional parameter (`now`)
added to two functions, following an existing pattern. Nothing new to keep in
sync, because nothing new is written.

**Learning burden — the number that should decide this.** Zero new nouns. Zero
new verbs. Zero new permission concepts. An agent that has read nothing about
this change reads the new output correctly, because it is the same output with
its facts in a better order and one word (`active` → `HELD`) that is more
literal, not less. The only thing a *dispatcher* learns is that `current` will
take `--session-id`, and it is optional.

Against that: three of the eleven edits are messages, and messages rot with
nothing testing them — the critic proved it in this very repository, finding two
false load-bearing comments in `run_crew.py`. My answer is that D1–D7, D9 and
D10 are code with pinnable behaviour, not prose; only D8's phrasing and D11 are
text, and both are reachable by a test that asserts a substring. It is a real
residual, and the honest mitigation is §11's mechanical census, which fails if
any surface drifts back to rendering an imperative over silence.

---

## 6. The three questions

### Q1 — What should a plan display to a reader who does not own it?

Answered in full in §3.3: **where it is, whose it is, how long since that, what
the state is, and advice only if the plan is not held by someone else.** The
reader is told the plan is held and by whom, is given the age rather than a
verdict, is shown the gate and its conditions (a parent inspecting a stuck child
is the most valuable already-existing capability in the system and must not be
degraded), is shown the next command *labelled as the holder's*, and is given an
orientation line in place of the mid-flight imperative. On the 718 leaseless
plans it is told `UNHELD` plus the last journaled actor and age, which is 510
plans' worth of ownership information the system holds and has never shown.

### Q2 — Should the lease be demoted to a presence marker?

**Yes on what it claims to be; no on deleting what it does.** And the read
surface sharpens this rather than dodging it.

It is already a presence marker; the display is the only thing pretending
otherwise. The evidence is unanimous — 0 claims on the main path, `require_session`
returning early with no lease, any session id from any directory taking a stale
one with the weakest verb, and nobody across two rounds able to name one mistake
its refusal prevented. `status: "active"` is a display string masquerading as a
fact: it means *not released*, and that is a bookkeeping state wearing a liveness
word. My D2 renames it in the render only.

What it should cost: **nothing to ignore, one call to take, and it must keep
writing the handover record.** The stale-branch refusal is worth keeping, and
not as a guard — it is *the prompt that mints provenance*. `claim` on a stale
lease writes `previous_session_id` and `takeover_reason` automatically
(Correction 2), and that is the only automatic handover record in the system. If
the lease is demoted to a marker that refuses nothing, nobody is ever prompted
to claim, so the record is never written and the corpus loses its only
attribution trail. §1.3 shows this is not theoretical in the wrong direction —
it is already happening: 25 takeovers, 0 of them the cheap recording path.

So: demote the *word*, demote the *claim to authority*, keep the *record* and
keep the one refusal that causes it to be written. This is uncomfortable for my
lane, and I will say why plainly: **a pure display answer cannot deliver Q2's
benefit.** If the lease refused nothing at all, my render would be honest and the
provenance would be gone. The refusal earns its keep as a writer, not as a lock.

### Q3 — Is the lineage edge worth writing at all?

**Not into `origin`, and not as a second copy of a registry fact — but yes as one
displayed string, and only if it is displayed.** Measured:

```
plans carrying an `origin` block at all                40 / 775   (37 spine.json, 2 review.json, 1 IMPLEMENTER_PLAN.json)
plans carrying origin.parent                            0 / 775
registry entries carrying a non-null parent           172 / 545   (32%)
```

Two corrections to the brief, both from measurement. First, the brief says the
registry recorded `parent: null` — true of that one dispatch, but **32% of the
545 registry entries in this checkout do carry a real parent session string.**
The edge is not structurally empty on the `run_crew` channel; it is empty when
`--parent` is not passed. Second, `origin` is not a viable carrier for anything:
95% of plans have no `origin` block at all, and it is written by two code paths
that disagree on its shape (`init_work_area`'s three keys versus
`spine_lifecycle.build_origin`'s seven).

And from §1.1, the registry cannot be reached from where the reader stands: 2 of
77 entries sit beside their spine, 468 name no spine, and the session-id join
lands 2 times in 57. So the fact exists, one third of the time, in a file the
reader cannot open.

Therefore my answer is the one my bias forces me to: **the edge is worth writing
exactly where the reader stands, as a string to print, and worth nothing
anywhere else.** `run_crew` already knows the parent, already sets
`SPINE_PARENT`, already speaks the parent aloud in the crew's prompt
(`_parent_clause`), and already records it in the registry. The one place it does
not put it is the child's own plan — the only artifact that outlives the run and
the only one a later reader opens. One key, one writer, at plan creation, from a
value already in hand.

The discipline that makes it earn its keep, and the reason I would not accept
this from another lane without it: **a field that is not rendered stays empty
forever.** `origin.parent` has existed in the schema across 775 plans and is
populated zero times. Write it only in the same change that prints it, and print
it as text — never as something to resolve, walk, or verify. The moment the edge
becomes a thing the system *follows*, it is a lineage subsystem and it has left
my mandate.

---

## 7. The limits of a display-only answer

Named honestly, with what each would actually need.

**L1 — The 31-minute Commander.** Display cannot distinguish a thinking owner
from a dead one, and §1.1 shows the corroborating fact is missing for 55 of 57
plans. My mitigation is to never claim otherwise. *What would be needed:*
`claim` records `pid` and `host` beside the `worktree` it already records — three
keys, one existing writer, one existing record, no new store — and the render
says "pid 41209 on this host: not running" **only when it can actually check**,
which means same host and a recorded pid. That is Candidate A's one contribution
I would accept. It is still machinery, and it is a cost: it helps only plans
claimed *after* it ships, never the 57 that exist, and it introduces a second
liveness answer beside `_is_stale` unless both are pointed at one predicate.
That is why it is not first, and not in my bill.

**L2 — #357's anonymous plans.** 32 leaseless plans have journals whose tails
carry `session_id: null`. Attribution never written cannot be displayed. My
render says so out loud (`no session recorded`) rather than staying silent, which
is an improvement in honesty and zero improvement in fact. *What would be needed
is the one fix that must not be taken:* defaulting `--session-id` from
`SPINE_SESSION`. That is #632's mistake exactly — the ambient value is the
parent's — and it would stamp the dispatcher's identity onto the child's journal,
manufacturing false attribution that reads as true. Leave it unfixed.

**L3 — The mistake a reader makes without reading.** An agent that acts on a
plan without calling `current` sees nothing I wrote. The `require_session`
refusal (D8) catches it at the moment of action, but only when a lease exists —
which is 57 plans out of 775. On the 718 leaseless plans there is no refusal and
no read, so a display answer is simply absent from that path. *What would be
needed:* the mutating verbs would have to say something unprompted, which is a
write-path change, and #615's answer, and not mine.

**L4 — The archive-move deadlock (E5a).** Untouched. Display substitutes for
nothing there; it needs per-call path resolution.

**L5 — Messages rot.** §5. Mitigated by making nine of eleven edits behavioural
and by §11's census, not eliminated.

I will also say what I do *not* concede: L1 and L3 are frequently used to argue
that a display fix is insufficient and therefore a subsystem is warranted. That
inference does not hold. The mistakes L1 and L3 describe are not prevented by any
candidate on either ballot — A, B and C all leave a dead owner indistinguishable
from a thinking one, and B leaves the corpse rendering `active` by design. A
display answer's incompleteness is not an argument for machinery that is
incomplete in the same places and expensive besides.

---

## 8. Migration

There is none, and that is most of the argument for it.

No stored field changes shape. No file is rewritten. All 775 existing plans
render better the moment the code lands, including the 53 archived corpses and
the 718 leaseless plans, because every fact the new render uses is already in
them. No flag, no stage, no enforcement switch, nothing to roll back except the
diff.

Two compatibility notes. `--session-id` on `current` is optional, so every
existing caller — the door, `run_crew`, the hook, every skill's documented
command — keeps working unchanged and gets the identity-neutral render. And any
test asserting the literal string `LEASE active:` will fail; that is the change
announcing itself, and those assertions are the ones that pinned the lie.

---

## 9. Per-issue dispositions

**#634 — frozen bookends, mutable middle, one spine per agent.** *Untouched, and
I would not touch it.* It is a real want about plan structure with no display
component. My design neither helps nor blocks it. Keep open; it belongs to
whichever round designs the plan's shape, not its rendering.

**#638 — the door's fixed path/identity/spine.** *Reduce to its two real halves
and close the visibility one.* The read half is already solved and no candidate
said so: `current` is non-mutating, `require_session` returns early for
non-mutating verbs, the engine reads no location since #609, and the CLI takes
`--file` per call — so a parent can read any child's plan from anywhere today.
D2/D3 make that read *useful* by naming the holder and the age. What remains is
drive-across-worktrees and the archive-move deadlock; retitle #638 to those and
delete the visibility claim from it.

**#632 — helper agents inherit the launcher's spine.** *Not mine to fix; mine to
stop teaching.* D8 removes the engine's unconditional recommendation to pass the
holder's session id, which is the system actively teaching this bug. The two
mechanisms behind the one number (env inheritance on `run_crew`; the
session-keyed binding file `.agent-work/.spine-rail-binding.json` in-harness, per
the experiment's M1) should be split into two issues before anything is built —
a fix to env stripping closes one and leaves the other. Neither is a display
change.

**#357 — child gate plans carry `engine_session: null`.** *Half closable on
display, and say which half.* The exclusivity complaint is answered by the
corrected threat model: there is nothing to exclude. What is left is that these
plans are unattributed, and D3 recovers the last actor from the journal for 510
of 718 — not from the lease, which by design was never taken. The residual 32
anonymous plans (§7 L2) stay open, with the explicit note that the tempting fix
is forbidden. Retitle to the attribution half and record the 510/32 split as its
scope.

**#369 — resume-side obligations and `claim --force` attribution.** *Mostly
closable.* Correction 2 measured that force writes `previous_session_id` and
`takeover_reason`; the spine half is done. §1.3 adds the finding that the *plain*
reclaim path — which also writes attribution, automatically — has never once been
used in this repository, and D8 is precisely the fix for that. The child half is
#357. Close #369 against the measurement and the string, or reduce it to "the
sanctioned five-step handshake writes no takeover record" (critic §1.4), which is
a separate and smaller thing.

**#615 — a leaseless spine has no ownership guard.** *Reframe from defect to
design, and answer the display half.* Under no-bad-actors a leaseless plan needs
no guard; it needs to stop being silent. Today it renders nothing about
ownership, which reads as "nothing to think about." D2's `UNHELD` and D3's
`LAST ACTION` make the leaseless majority legible for the first time. Close the
guard framing; keep an issue for §7 L3 (nothing speaks on the leaseless mutating
path) if anyone still wants it after seeing the display.

---

## 10. Risks

**R1 — Suppression keyed off the wrong predicate.** If someone implements D4 as
"suppress the rail when the reader did not identify itself," every unleased crew
on the main path — which is *all* of them — loses its rail. This is the single
most likely way to ship this design as a regression. The predicate is
`held by a session that is not you`, and it must be pinned by a test whose name
says so.

**R2 — Age is read as a verdict anyway.** An agent may treat "22d" as
permission. Partly intended (it *is* the signal) and partly unavoidable. The
wording carries the guard — "leave it unless you know that session is gone" puts
the condition on the reader's knowledge — and §11's force-claim ratio is the
measurement that would catch it going wrong.

**R3 — A read that writes.** Making `current` reader-aware invites someone to
refresh the heartbeat on read "since we know who it is." That would make reading
a plan an act of ownership and is strictly worse than today. Pinning test: a
`current` with a matching `--session-id` leaves the file byte-identical.

**R4 — Two renderers drift.** `_lease_line` and `spine_rail.reconstruct_current`
already duplicate the lease string, and the hook is stdlib-only by contract and
cannot import the engine. D9 duplicates the new shape into a second place. The
mitigation is a test that renders one fixture through both and asserts the same
holder and age appear; not identical strings, since the hook's is a deliberate
reconstruction.

**R5 — The archive predicate is wrong about some plan.** A plan under
`.agent-work/archive/` that someone genuinely intends to drive gets an accurate
but discouraging banner. Nothing is refused, so the cost is one line of text, and
the standing recovery doctrine (temp-copy-back, never drive in place) already
agrees with the banner.

**R6 — D1 is read as reopening location-awareness.** Named and bounded in §4. If
the reviewer disagrees, the fallback is to move the archive predicate into the
hook, where lexical path rules already live — but the hook is not the surface
that printed "Run it." to the reader, so this would cost most of the value.

---

## 11. How someone would know it worked

**Mechanical, run against the corpus after the change:**

- `for f in $(all 775 plans): current` — **zero** outputs contain a `RAIL:` or a
  bare `next:` line without an ownership line above it. Today: 775 of 775 fail
  this. It is a shell loop, it is greppable, and it is the census that catches
  message drift later.
- Every one of the 53 archived active-lease plans renders the `ARCHIVED` banner
  and no rail.
- 510 leaseless plans render a `LAST ACTION` line naming a session; 32 render one
  saying `no session recorded`; 176 render `No journal beside this file`. Those
  three numbers are the acceptance test, and they are exact.

**Behavioural, the one I would actually bet on.** Today's ratio of stale-lease
reclaims is **0 plain : 25 forced** (§1.3), across the entire history of the
repository. Prediction: after D8 and D2 ship, plain reclaims appear at all, and
within a few epics they outnumber forced ones. That is directly measurable by
counting `takeover_reason == "stale lease reclaimed"` against reasoned takeovers.

- If the ratio moves toward plain claims and the *total* takeover count stays in
  the same range — the display told the truth and agents took the cheap correct
  path. Shipped correctly.
- If the total count **rises sharply** — the critic's seizure risk is real, the
  age is being read as permission, and D4's wording is too permissive. Falsified;
  the fix is wording, not rollback.
- If the ratio stays 0:N — reading is not where the decision happens, the display
  was not the mechanism, and the remaining candidates are the push surfaces (D10)
  or the write path. That would be the strongest evidence against my whole lane
  and I would want it known.

**Qualitative, per this dossier's own rule.** The workarounds this epic paid for:
the Admiral's hand-written "this stranded plan is superseded" ruling in prose
(E3) is replaced — a reader now sees the age and the archive banner and needs no
ruling. The hand-written "do NOT call `mcp__spine__*`" clause in every handoff
(E2) is **not** replaced; nothing here touches it. E5a is not replaced. Stating
both halves, because silence is not an answer.

---

## 12. What I would ship first, and what survives if only one thing ships

**Ship first (one change, one afternoon):** **D1 + D4 + D5** — the archive banner,
the rail replaced when the plan is held by someone else, and `next (for the
holder):`. This is the recruitment fix. It needs no clock, no threshold, no
identity, no config, and no new argument, because the archive half is a path
predicate and the held-by-other half is a string comparison against a value that
is already printed on the screen.

**If only one thing ever shipped:** **D1 alone — under `.agent-work/archive/`,
print the banner and suppress the rail and the `next:` command.**

The reasoning, and it is the argument I most want tested. The imperative is the
dangerous element, not the lease line: an agent can ignore a stale timestamp, but
"Run it." is an instruction it is trained to obey. D1 removes the imperative from
53 of the 57 lying leases *and* from every archived leaseless plan besides — a
larger population than this entire epic has been arguing about. And alone among
every proposal on either ballot, **it cannot be wrong about liveness, because it
makes no liveness claim.** It reads a path the caller supplied, asserts a fact
about that path, and refuses nothing. There is no 31-minute Commander it can
misjudge and no seizure it can invite.

Everything else I have written is better than the status quo and each piece is
individually defensible. Only D1 is unfalsifiable-by-clock, and under a
criterion whose only adversary is an honest agent making a mistake, that is the
property worth the most.

---

## 13. Where I am most likely wrong

**The strongest case against this lane.** I am arguing that agents make their
mistakes at the moment of reading. It is equally possible they make them at the
moment of *being told* — in a handoff, in a SessionStart injection, in a
launch order — and never call `current` at all. If that is true, D1–D8 are
decoration and only D10 matters, and the epic's real read surface is the prompt,
not the engine. §11's third outcome is the test that would show it, and I would
rather it be measured than argued.

**Second.** `UNHELD` and `LAST ACTION` add two lines to the most common render in
the system, 718 plans' worth. I claim that is worth it because the leaseless
plan is currently silent about ownership. Someone could reasonably say the
leaseless plan is silent *because there is nothing to say*, and that I have added
noise to 718 renders to serve a reader who is rarely there. If the ship-first set
is cut further, D3 is what I would drop next after D2.

**Third.** I may be wrong that relabelling beats withholding (§3.4). The hook
authors chose withholding after a measured leak (#549), and I have chosen the
gentler option on ergonomic grounds without a measurement of my own. If a
relabelled command turns out to be pasted anyway, withholding was right and I
was optimising for a parent-reads-child case that is rarer than the leak.
