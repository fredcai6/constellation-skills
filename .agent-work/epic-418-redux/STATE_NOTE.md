# Crash-resume state note — epic-418-redux

> ## FRESH ADMIRAL? DO EXACTLY THIS, IN THIS ORDER. Nothing else, first.
>
> ```
> cd C:/Programs/constellation-skills
> bash .agent-work/epic-418-redux/truth.sh                     # 1. derive reality. never recall it.
> python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current
> ```
>
> **2. Is a Commander alive?** `truth.sh` prints worktree write activity and the lease. **Quiet does
> NOT mean dead** — a Commander waiting on a crew is quiet and alive. The authoritative signal is the
> harness **idle notification**; if you have not received one, it is running. **Do not dispatch.**
>
> **3. If it IS genuinely idle/tripped:** relaunch a fresh Commander into the **same worktree and
> spine file**, told only to read `execute.json current` (**not** `spine.json current` — that one is
> stale by construction). **Wait for the idle notification, STOP the predecessor, then dispatch.** In
> that order. Rule 7 below; it is the only rule that has ever actually caught anything.
>
> **RULE 7 WAS AMENDED 2026-08-08.** A Commander **cannot** stop the crew it dispatched — dispatch runs
> through the Admiral's session and `TaskStop` refuses with "owned by main session." So for a
> **Commander**, the idle determination IS: result written + registry `completed` + `--verify-result`
> fresh + disk unchanged. Ask the Admiral for the stop, keep working, dispatch anyway after ~10 min of
> silence and log it. For the **Admiral**, unchanged. The rule was written by the one tier that can obey
> it, for a tier that cannot. **Do not let a ritual outlive its hazard.**
>
> **4. Then read the NINE rules.** They are the ones I broke *after writing them down*.
>
> **WHERE IT IS RIGHT NOW (2026-08-08, refresh at each launch):** **WAVE 5 — the last wave.** Wave 4
> is merged and closed (#467 via PR #505 at `c875ee23`; #431 dissolved). The boundary `close-to-w5`
> exited **advance**, G2-verified, prelaunch exit 0. **Five crews, 21 issues.** This is the final wave
> of epic #418; closeout follows it, then F (#424) becomes its own effort.
>
> **USE `python`, NEVER `py`.** Under the Bash tool they are different interpreters and `py` has NO
> pytest — `py -m pytest` exits **nonzero** with `No module named pytest`, which reads exactly like a
> red suite when no test ran. `py` is fine for the engine and verifier scripts (stdlib only); it is
> specifically the suite it cannot run. This is #313, live. All five crews were corrected mid-flight.
>
> **COLLAPSE CLAIMS CORRECTED 2026-08-08 — the Admiral's were wrong.** #446 is **NOT** part of the
> `archive.c2b` collapse (its body never mentions `<branch>`; `grep -c` → 0), and #501 ≡ #468 is
> **partial**, not total. Crew 1 refuted both by obeying the confirm-against-the-body rule. **Do not
> re-inherit the original three-way claim from any older document.**
>
> **CREW 1 IS NOW `commander-w5-gates-b`.** The first instance tripped at `plan` on a HARD reading,
> wrote its refresh-request, committed `eff00abf` and stood down — working as designed, not a failure.
>
> **LIVE POSITION @ 23:52Z 2026-08-08 — 2 PRs open, 0 merged.**
>
> | crew | state | evidence |
> |---|---|---|
> | 1 gates | running as `-b-refresh1` | `plan [in-progress]`; MISSION_FRAME, plan-alternatives, `execute.json` authored |
> | 2 readiness | running as `-b` | recovered from the stale-gauge trap; steady writes |
> | 3 addressing | **DONE** | **PR #511**, 4 commits. Real red-then-green after rework. |
> | 4 engine | running as `-b` | driving a 10-item plan its predecessor authored |
> | 5 docs | rework on disk, **not pushed** | **PR #509** green; `m3` pending; suite re-run at 23:43 |
>
> **PR #511 rework, verified by ME against clean main, not accepted on report:** its first acceptance
> test **passed on unmodified main** — a check that cannot fail, in the PR closing an addressing
> defect. Crew 3 responded by adding real doctrine guards: now `2 failed, 2 passed, REAL_EXIT=1` on
> main. **Merge only after CI is green on `bd31f69c`.**
>
> **MERGE BASELINE (use this, do not re-guess it):** main is green at **1867 passed / 2 skipped /
> 829 subtests / real exit 0**, run with `python -m pytest`, exit read **unpiped**. Matches wave 4's
> post-merge figure exactly, which is what makes it a baseline and not just a green.
>
> **NOTHING MERGES UNDER A LIVE CREW.** PR #509 is green and deliberately held: crew 5 finished, but a
> PR being green is not the same as a crew being done, and I have one open review finding on it (it
> deleted a row from a fenced block that is verbatim command output — see the log).
>
> **DO NOT re-poke a quiet crew.** Twice today disk silence looked like death and was reading. The
> authoritative channel is the harness **idle notification**. Ask; never relaunch on an inference.
>
> ## THE CLOSE SEQUENCE — get this order wrong and the epic cannot close. Read before merging crew 1.
>
> `execute.c3` runs **`admiral-prelaunch` from the INSTALLED skill bundle**, not from the repo. Crew 1's
> #506 fix lands in the **repo**. So:
>
> 1. merge crew 1's PR
> 2. **RE-INSTALL** (`python scripts/install_constellation.py --agent claude --scope user --force`)
> 3. **verify the installed verifier actually carries the fix** — `git hash-object` the installed file
>    against the repo blob, do **not** trust the installer's own report
> 4. only then build the `w5-to-close` packet and expect c3 to pass on a `stop` exit
>
> **Skip step 2 and c3 still fails with the OLD logic, on a tree that already contains the fix.** That
> is the corpus-drift trap (#344) and it already bit this run once: at wave-5 launch, **all nine**
> installed bundles were pre-#467 and nothing reported it. Never pass `--wire-hooks` — `settings.json`
> is a hard constraint.
>
> **If #506 does NOT land:** the close needs a `waive` of `execute.c3` **on Tommy's authority**, with
> #506 cited as the defect that forced it. Do not flip the boundary decision from `stop` to `advance`
> to make it green — that is falsifying a verdict to fit a check, forbidden in three launch orders.
>
> **Boundary builder:** copy `C:/Users/fredc/.claude/jobs/*/tmp/build_w5_boundary.py` (the one that
> produced a G2-clean packet on its second try) and edit its content. Do **not** author a fresh
> skeleton — the last pre-staged skeleton reproduced the exact shape error it was built to prevent.
> Contract gotchas already paid for: `entry_conditions` must be an **array**; a `stop`/`later_only`
> disposition maps to `amend_forecast_or_parked`; `record_evidence_only` requires `issue_created=false`;
> a fixed-boundary change requires `applicable=false`.
>
> ## THE TRIP-LOOP — the one that can silently eat this wave. Read before relaunching anything.
>
> **A fresh agent reads its PREDECESSOR'S gauge until its own first tool call lands.** The gauge is
> written per checklist directory by a PostToolUse hook. Verified on crew 2: `gauge.json` said
> `fill_fraction 0.190464, observed_at 23:18:53Z` — **nine minutes before that agent existed.**
>
> So a relaunched agent opens `current`, sees a number over the hard line that is **not its own**,
> hands off, and you relaunch again. **Relaunch → inherit → trip → hand off → relaunch, forever, and
> every cycle looks like correct doctrine being followed.** Four crews were relaunched inside a few
> minutes on 2026-08-08; this was about to happen four times over.
>
> **EVERY relaunch dispatch must say:** the CONTEXT number in your first `current` is your
> predecessor's — make any tool call, re-read, and **never file a refresh-request against a reading
> you did not produce.** Open as #481 (stale reading outlives its session) and #477 (gauge read per
> directory). Neither is fixed.
>
> **And `REFRESH REQUESTED:` is a marker left FOR the successor, not an instruction TO it.** The
> successor **is** the refresh — it proceeds, it does not re-file. Nothing in `current` says whether a
> request was already served (#500), so a fresh agent genuinely cannot tell. Say it in the dispatch.
>
> **#510 (filed 2026-08-08):** a HARD trip at a gate BOUNDARY has no legal verb — `advance` refuses a
> `pending` gate, `start` is what HARD guards — so the refresh-request survives but **the DIGEST
> cannot be written.** Expect boundary-tripped crews to hand off by prose message instead. That is
> them compensating, not the mechanism working.
>
> | Crew | Worktree | Issues | Model |
> |---|---|---|---|
> | 1 bookend gates | `epic418-w5-gates` | #506, #501+#468, #439+#484, #446 | Opus, Commander |
> | 2 readiness (R) | `epic418-w5-readiness` | #458 | Sonnet, Commander |
> | 3 crew addressing | `epic418-w5-addressing` | #507+#370+#413 | Sonnet, implementer |
> | 4 engine internals | `epic418-w5-engine` | #474 #475 #476 #479 #480 #427 #503 #493 #495 | Sonnet, implementer |
> | 5 docs | `epic418-w5-docs` | #496+#411 | Sonnet, implementer |
>
> **LAUNCH ORDERS ARE NOT IN THE WORKTREES — READ THEM FROM THE MAIN CHECKOUT.** I cut the worktrees
> from `ea854471` and committed the orders afterwards at `197ad5b0`, so every dispatch prompt named a
> path that resolves to nothing. They live at
> `C:/Programs/constellation-skills/.agent-work/epic-418-redux/launch-orders/LO-w5-c{1..5}-*.md`,
> read-only for crews. Correction was messaged to crews 2-5; crew 1 found it itself.
> **Fresh Admiral: next time commit the orders BEFORE cutting the worktrees.**
>
> **THE ONE THING THAT CAN VOID THIS WAVE'S DELIVERABLE:** **crew 4 is the sole writer of
> `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` for the whole wave.** Nine of its
> issues live there. If any other crew is given a task that touches those two files, stop and re-cut the
> assignment — do not let two writers into one file and plan to resolve it at merge.
>
> **THE DOGFOOD DEPENDENCY:** **#506 (crew 1) is what lets this epic close its own `execute` gate
> without a waiver against Tommy's name.** Known single point of failure, accepted. It is **not** a
> reason to accept a soft report on #506; if crew 1 misses it, take the waiver honestly.
>
> **Three of the 21 are duplicate collapses, and none is visible from the titles** — #501≡#468 (same
> function, same line), #439≡#484≡#446 (all `archive.c2b`), #507≡#370≡#413 (one defect, three epics).
> **Before closing any of the eight, re-confirm the collapse against the issue BODY.** A title-level
> check here is a check that cannot fail.
>
> **NEVER copy an engine hash forward from any document, including this one.** Pin with
> `git rev-parse HEAD:scripts/checklist_engine.py`, re-derived at the moment of use. Byte-size pins are
> unusable — a predecessor's own trap-6 size matched nothing on disk.
>
> **What this run is:** epic #418 **wave 5**, five crews in five separate worktrees.
> **Never dispatch a second Commander into any one of them.**
> **What is owed to Tommy: NOTHING. Scope is settled** — 2026-08-08 he ruled one more wave, then close,
> with F/C/E as separate efforts afterwards, and then widened crew 4 to include #474–#480. There is no
> open question for him. **Do not stop to ask; run the wave, then closeout, then release the lease last.**
>
> **The Admiral is never asked to stop.** The trip only evaluates on a gated verb, and this role sits
> inside `execute` for the entire epic. I wrote this at **54.9% fill** against a 15% hard line, having
> never been prompted once. Watch it yourself; nothing else will.

> ## THE NINE RULES — the ones I have actually broken. Run rule 2 first.
>
> Everything below this box is reference. **These are the ones that have actually been broken,
> by me, after I wrote them down.** This run's most repeated failure is not ignorance — it is
> *written-down-and-ignored*, the human twin of the done-condition wave 4 is implementing: an
> instruction satisfied or ignored with identical traces gets ignored, including by its author.
>
> **WHY SOME OF THESE WORK AND MOST DO NOT — the one thing to take from this run.**
> Every rule I broke today was one I had to **remember to consult**. The only rule that ever
> *fired* was **rule 7**, and it fired because it **gates an action**: it stands between me and a
> dispatch, so the dispatch cannot happen without passing it. It caught a relaunch that would have
> destroyed a healthy Commander, before I had weighed any evidence at all.
>
> So when you find yourself adding a rule here, ask which kind it is. **A rule phrased "remember
> to X" is a rule that will be read past.** Convert it into a gate on the action it protects — a
> command you must run first, a check that must pass — or expect it to fail exactly when it
> matters. That is DC6's argument turned on its author, and it is the most useful thing this run
> has taught me.
>
> 1. **Do NOT push after every log append.** `ci.yml` has no `paths-ignore`, so an
>    `.agent-work`-only commit burns the full 8-minute suite. Commit locally; push at real
>    boundaries. *(Broken twice: 6 concurrent runs starved PR #490 ~25 min; then 3 more today.)*
> 2. **RUN `bash .agent-work/epic-418-redux/truth.sh` before citing any status.** Do not recall it,
>    do not read it off this file. That script derives gates, lease, fill, liveness, source-touched,
>    branch, forge and CI from their sources in one command. *(Rule 2 was "remember to re-derive"
>    and I broke it 4x — including once while describing that failure, and once understating my own
>    error count when the exact number was one grep away. It is now a command, not a reminder.)*
> 3. **Never act on `REFRESH REQUESTED` alone** — prove the worktree is idle first. A served request
>    reads as live. *(One command from destroying a healthy crew, then its replacement, in a loop.)*
> 4. **Mutation-test every check before you trust it.** If it cannot go red, it is not a check.
>    *(7 instances built by me in the epic about exactly this.)*
> 5. **A piped `$?` is the pipe's exit code.** Redirect to a file or use `${PIPESTATUS[0]}`.
>    *(Read a verifier REFUSAL as exit 0.)*
> 6. **Never pass markdown to `gh` in a double-quoted string** — a backtick runs as command
>    substitution and the post succeeds with the phrase silently deleted. Write a file, use `-F`.
> 7. **NEVER dispatch a successor until the predecessor's IDLE NOTIFICATION has arrived** — not
>    "it said it was going idle". Then STOP it, then dispatch. *(I overlapped two Commanders on one
>    run for 4 minutes. Nothing was lost and that was LUCK: every agent here shares one session id,
>    so `claim` treats a teammate as an idempotent self-resume. **The lease does not exclude.**)*
> 8. **Before ruling that something is BROKEN, run the command that would show it is FINE.**
>    Name the falsifier out loud, then run it. *(I authorised amending FOUR frozen gates on a
>    crew's report that a check was structurally unpassable. It was not — the house vocabulary
>    is `APPROVE`/`BLOCK` in `REVIEWER_HANDOFF.template.md` and the check matched it exactly.
>    One `grep` of the template would have settled it, and I had run exactly that check on a
>    different template an hour earlier. The CREW retracted it; I did not catch it.)*
> 9. **Dispatch implementers on SONNET.** Opus needs a NAMED reason in the dispatch text —
>    open design choice, engine semantics where wrong is invisible, or adversarial review.
>    *(Tommy, wave 4: "we've been going a little hard." The Admiral skill already said
>    least-powerful-that-works; I dispatched five Opus Commanders without once applying it.)*


**WAVE 4 RUNNING: one Commander on #467 (A2, trip semantics). Never dispatch a second into this worktree.**

- **step:** `execute` — in-progress (resumed 2026-08-08 on Tommy's *"keep rolling"*).
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current`
- **wave-4 dispatch:** one Commander, issue **#467**, worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`, branch `epic-418/a2-467-trip-semantics`,
  model **Opus**. Launch order: `launch-orders/LO-467.md`.
  **Now on its FIFTH instance (`commander-w4-467-e`), driving g2.** A, B and C each tripped, each handed off
  cleanly at a seam, **none lost work**. A and B are STOPPED; C went idle with both leases released.
  **The engine journal CANNOT tell the instances apart** — every entry carries the same `session_id`
  (#419's identity problem, live in the journal). Read journal *verbs* and gate states, never the
  lease field, and do not infer which instance did what.
  **The plan is FROZEN** at `<worktree>/.agent-work/issue-467-trip-semantics/execute.json` —
  16 tasks, 5 gates. **6/16 COMPLETE.** g1 (all four: proved the defect at unmodified HEAD) and
  g2-implement + g2-review. **The fix is committed: `38f0b448` — *move the HARD guard off `advance`
  onto `start`/`reopen`; refuse the silent close*.** g2's review returned **APPROVE / 0 blocking**,
  matching the frozen `c3` with no amendment. `g2-integrate` is verifying now; its `c2` is the
  **anti-vacuity check** — *the guard tests must EXIST*, pytest exiting 5 on an empty selector.
  **tc1 pulled into g2's scope:** `docs/agents/GLOSSARY.md:13` still teaches the pre-fix belief;
  fix that one line only.

> ### g1 IS CLOSED. The c3 ruling is APPLIED — do NOT author a second amendment.
>
> `advance g1-integrate` succeeded **11:22:10Z**. **`amendments: 1`** in `execute.json`:
> `retext-check` on `g1-integrate.c3`, kind unchanged, authority Admiral / epic #418 —
> `match: {verdict_class: "ACCEPTED", blocking_findings: "0"}`. **ACCEPT and ACCEPT WITH FINDINGS
> pass; REJECT fails twice over** (verdict_class, and independently blocking_findings, since a
> REJECT always carries at least one). Verify it exists before touching c3; do not re-apply.
>
> **THE BLANKET AMENDMENT AUTHORIZATION IS WITHDRAWN. Do NOT amend g2-g5's c3.** I authorised it,
> then the crew checked the premise and it was wrong: the house vocabulary is `APPROVE`/`BLOCK`
> (`constellation-commander/templates/REVIEWER_HANDOFF.template.md`) and `c3` matches it exactly.
> g1 broke because **that commander's hand-written handoff contradicted its own frozen plan** — a
> one-off slip, not a wave-wide defect. **The g1 amendment stands alone and extends to nothing.**
> Standing correction: *when a gate's `c3` looks unpassable, check the handoff against the template
> before concluding the plan is broken.*
>
> **Root cause, worth more than the fix and not yet fixed:** artifact `match` is **exact equality
> per key** (`all(ev.payload[k] == v ...)`) — **it cannot express "one of."** The original author
> hard-coded a single verdict string because that was the only expressible thing. **Every future
> verdict check has this latent.** General fix is `match` gaining a set/one-of form. Triage.
>
> **Related, already checked so nobody repeats it:** the reviewer force-waived `r6-fowler` c1
> believing no verb could fill its literal `<fowler-pass-record-path>`. **The verb exists** —
> `amend` with a **`retext-check`** op, the survey-only exception, shipped by wave 3's **#465**.
> It is documented in `docs/CHECKLIST_SCHEMA.md` and **nowhere in the reviewer's SKILL.md** (repo
> or installed), so the reviewer could not have found it. Triage candidate; do not re-open the gate
> to tidy it.

> ## READ `execute.json current` — THE SPINE'S DIGEST IS STALE
>
> `spine.json current` still carries **`w-4`, written two agents ago**, instructing work that is
> already done. It would send a successor to redo `start execute`. **Read it only for the reach-up
> flag.** The real DIGEST is:
> ```
> python C:/Programs/constellation-skills/scripts/checklist_engine.py \
>   --file .agent-work/issue-467-trip-semantics/execute.json current
> ```
> **Why it cannot be fixed from inside:** `advance` is the only writer of `why_trail`, and `execute`
> spans all 16 gates with 13 remaining — so **a Commander that trips MID-STEP cannot update the
> spine's cold-start surface at all.** That is the ordinary case: `execute` is where nearly all the
> time goes. Instance A tripped at a *step boundary* and could close a gate to write its handoff;
> instance B tripped mid-step and could not. **#431 in its worst shape.** Not in #467's six
> done-conditions; the frozen plan was correctly NOT amended to work around it.
>
> Also: **`LO-467.md` is reachable from nothing in the spine**, and that is where the environment
> invariants live. A cold successor gets the plan and not the ground rules.
- **expected artifact:** a green, reviewed PR closing #467; then the wave-4 checkpoint to Tommy.

**If it trips again: relaunch the same way.** Fresh Commander, same worktree, same spine file,
told only to run `current` and obey it. **Do not re-brief from your own memory of the run** — DC5
measures exactly whether a cold successor can resume from `current`, and briefing it destroys the
measurement. Its own verdict on the handoff's sufficiency is part of its deliverable.

> ## STOP — DO NOT RELAUNCH ON `REFRESH REQUESTED` ALONE. IT LIES.
>
> **I nearly destroyed a healthy Commander obeying this signal. Read this before you act on it.**
>
> The engine renders `REFRESH REQUESTED:` until the target gate is **started**, and the underlying
> records are **permanent evidence attachments with empty `ts` fields**. So a request that was
> **answered fifteen minutes ago still reads as outstanding** for the whole of the successor's
> startup. Obeying it relaunches a working crew — and then relaunches *that* one, in a loop, each
> cycle destroying work.
>
> Currently pending and **already served**: `e-plan-2` (seam `plan`, `why_ref w-3`) and
> `e-execute-1` (seam `execute`, `why_ref w-4`). Both are the **first** Commander's. Commander B
> answered them at 10:09:35.
>
> **Before relaunching, prove nobody is working:**
> ```
> find <worktree> -newermt "-6 minutes" -type f        # any recent write => SOMEONE IS WORKING
> git -C <worktree> log --oneline main..HEAD           # new commits => working
> <worktree>/.agent-work/issue-467-trip-semantics/gauge.json   # low fill => a FRESH agent, not a tripped one
> ```
> A tripped agent is **idle and high-fill**. A successor is **active and low-fill**. Commander B
> read **6.9%** while the signal screamed refresh.
>
> **The reach-up signal has no notion of being served** — it cannot say who asked, when, or whether
> anyone answered. It is unreadable when it matters (active-gate-keyed, so a compliant handoff
> erases it) and unclearable when it does not. Routed to #467 triage.

## The gauge finding — SETTLED across three agents. Do not re-escalate it.

I logged and told Tommy *"as built, the round trip cannot close — it loops."* **That was an
overclaim and it is retracted.** Instance B downgraded its own finding; instance C independently
re-measured it. Settled statement:

> The gauge is a **single-slot, unowned, undated-in-practice value**. Two failure windows follow: a
> **live overlap** while the outgoing agent is still taking tool calls, and a **stale-value window**
> of at least one tool call at every handoff, **even when nothing else is running**. Both
> **self-clear**. Neither is guarded, and the shape is guaranteed at every trip because trip and
> resume share a spine.

Severity: **real, structural, self-clearing, cost this run nothing.** Triage candidate, **not** a
#467 gate.

**The proposed fix does not cover both windows.** *"The writer should decline to write for an agent
that does not hold the spine lease"* closes the **live overlap** only — a stale value needs no
writer at all. A fix reported as closing both would be the exact defect this wave hunts.

**Do NOT tidy the three accounts into one.** Instances A, B and C disagree *in sequence, on the
record*: a claim made, downgraded by its own author, then independently re-measured by a third party
with no stake. That sequence is the evidence. C was directed to add its own section to
`RESUME_OBSERVATION.md`, never to rewrite its predecessor's.

**Admiral error recorded with it:** I stopped instance A to unblock B, which confounded the
severity measurement — the idleness that cleared the symptom was idleness I caused. C's arrival
reading, taken with both predecessors already stopped, is the uncontaminated run.

**LO-467 CONTAINS AN UNSATISFIABLE INSTRUCTION — do not repeat it in any future launch order.**
It says *"write a `refresh-request` ... make sure your `current` carries the DIGEST ... go idle."*
Both clauses cannot be obeyed: `current` carries the latest live why-record, only `advance` writes
one, and `advance` is the verb the refusal blocks. **`global-everyone.md` §reach-up says the same
thing**, so this is #431 propagating into doctrine, not just my drafting. The move that actually
works, discovered by the first Commander from source: `attach` refresh-request → `advance <gate>
--why "<the handoff>"` → **`attach` a SECOND request at the gate you hand off TO**, because
`REFRESH REQUESTED:` is **active-gate-keyed** and a compliant handoff otherwise erases its own
signal.

**GREEN MAIN BASELINE: `1793 passed, 2 skipped, 683 subtests, exit 0`** — carried from the wave-3
close, re-verified on merged main after PR #499.

## Contract state

**Addendum R2 (2026-08-08)** — refreshed on *"keep rolling"*. Expiry: **epic close, or 72h from
2026-08-08T07:00Z**. Grants: the closeout lessons-auditor dispatch, and wave 4 on #467.
**Still surfaced, NOT granted:** continuing past A2 into F (#424), C (#421), E (#423).

## The correction that set wave 4 — do not re-make this mistake

**A2 was never uncut.** For three waves this note said *"A2 has no issue cut"* and I twice told
Tommy that cutting it was a scope decision I would not take. **#467 is A2**, OPEN, carrying DC1-DC6
verbatim, a `Fixed` list, `Blocks: #424`, and its own evidence protocol. What I had been calling
"cutting A2" was **decomposing an already-cut issue into three**, which is the board clutter he has
warned against twice.

The cause is this epic's own defect family aimed at me: **a claim carried in this note across three
waves and a compaction, never re-derived from the tracker.** A stale note and a true note read
identically. Before relying on any status claim in this file, `gh issue view` it.

## Wave 3 — closed (all merged, closed, reviewed on the forge)

| Issue | PR | Merge | Review |
|---|---|---|---|
| #461 | #490 | `ad149283` | APPROVE, posted |
| #488 | #491 | `8b9330ea` | APPROVE, posted |
| #489 | #491 | `8b9330ea` | APPROVE, posted |
| #465 | #492 | `4da9bc9b` | APPROVE, posted |

Boundary `w3-to-w4` recorded, `decision=replan`, `launch_id=wave4-a2-trip-semantics`,
`admiral-prelaunch` **exit 0**.

## Remaining after wave 4 — CORRECTED against the LIVE skill, 2026-08-08

**My loaded copy of the Admiral skill was STALE for this entire run** — this epic rewrote the skill
it runs under (#447, #460) and my copy predates the rewrite. Re-read the installed copy at
`C:/Users/fredc/.claude/skills/constellation-admiral/SKILL.md`; it matches the repo apart from one
install-time path substitution. **The live closeout has FIVE substeps, not seven:**

1. **Record the epic retrospective as EPISODES — written by ME, no subagent.** One episode per
   distinct thing that happened; not one per wave, not a summary. **An episode is a record, not a
   rule** — write what you observed; a rule for a future agent belongs in `docs/agents/*` and is
   Tommy's call. #460's guard enforces this mechanically. Only write path:
   `apply_episode_delta.py --store-root episodes`. Prove with `verify_episode_captured.py` before
   advancing. Source material: `closeout/RETROSPECTIVE_SOURCE.md` (17 routed candidates).
   **Dogfood sweep: DONE** — `closeout/feedback-sweep-2026-08-08.md`, clean.
2. **Cartographer reconcile** — hand it the epic's net change. **This is the only dispatch closeout
   needs.** Net change computed: base `cbd9aee8`, **106 files, +10,864 / -4,229** excluding
   `.agent-work` and `episodes`.
3. **Harvest before sweep** — for wave 4's worktree only. Everything else is already swept.
4. **Repo hygiene** — worktrees swept (**never `governor-264`**), `ADMIRAL_LOG` archived under
   `.agent-work/archive/`.
5. **Epic summary; user acceptance closes the run.**

Then `advance` closeout, and **`release` the lease as the very last action**.

**The old "durable trio" harvest model is gone.** `episodes/` is a tracked repo-root path, so a
committed episode already survives `git worktree remove`. Verified: **60 episodes tracked**,
including `w3a-465-001..006`.

**Verified, so it is not re-investigated:** the tracked `.agent-work/CONSTELLATION_FEEDBACK.md` has
**no entries after 2026-08-05**, and waves 2-3 added none. **This is not a loss.** The commander
`feedback` gate now requires an **episode** (postcondition c1, checked by
`verify_episode_captured.py`), not that export. And only **one** wave-3 dispatch ran a Commander
spine at all — #465 (`constellation-commander-delegated`); **#461 and #488/#489 were
implementer-with-plan** dispatches per right-sizing doctrine, and implementers have no feedback
gate. Six episodes from one Commander is exactly correct. No gate was skipped.

**Residual defect noted, live doctrine:** Admiral closeout substep 3 still says to harvest a
commander's worktree-local `CONSTELLATION_FEEDBACK.md`, but the commander spine no longer requires
producing one. The retirement propagated to substep 1 and to the commander's gate, and left substep
3 protecting an artifact nothing writes. Closeout candidate.

## Worktrees — sweep verdict

**`C:/Programs/constellation-skills-wt/governor-264` — DO NOT SWEEP.** 3 unmerged commits
(1144 lines, 13 tests) against **#264, still open**; absent from main (`git ls-files | grep
gauge_chain` returns nothing). Holds
`test_ladder_fill_series_is_non_decreasing_and_actually_moves` — the assertion that the gauge is
still *measuring*, the guard that would have caught this epic's dark governor — and
`test_chain_ambiguous_binding_writes_no_gauge_and_flags_every_candidate`, which uses **distinct
parent paths** and so specifies the negative direction #488's fix had to preserve.

**SWEPT 2026-08-08 — 7 worktrees removed, 6 branches deleted.** Gone: `epic418-a-419`,
`epic418-a2-440`, `epic418-b-420`, `epic418-d-422`, `epic418-g-425`, `epic418-h-447`, `verify-w0`.
Harvest output survives at `.agent-work/harvest-418-redux/` (4 files that existed **nowhere in the
git object store**). Nothing further is owed by those trees.

**TWO different hazards need TWO different tests — do not conflate them again.**
- **Uncommitted work** → `h=$(git hash-object <f>); git cat-file -e "$h"` (non-zero = nowhere in git).
- **Committed but UNMERGED work** → `git rev-list --count main..<branch>` + `git diff --name-only
  main...<branch> -- . ':(exclude).agent-work'`.

The first test is **blind to the second hazard** — an unmerged branch's blobs *are* in the object
store, so `cat-file -e` resolves them happily. The harvest test would have waved **governor-264**
straight through. Positive control for the second test: governor-264 reports `ahead=3,
uniquefiles=2` where every swept branch reported `0/0`.

**Order is not optional:** harvest each worktree's durable trio **before** `git worktree remove` —
under an epic lease `durable_root()` returns the **worktree** root, so the trio lands where the
sweep eats it.

**Retained branches, dispositioned not abandoned:** `b-433-render-directives`,
`b-460-episodes-observations`, `b-464-lesson-field-rename`, `d-436-enumeration-falsification` —
the **pre-replant attempts**, superseded and nothing owed, kept because they are the only record of
the abandoned attempt. Routed to the closeout audit.

## CORRECTED wave-2 PR mapping — my ledger named the wrong PRs

The forge says the PRs I had recorded are **CLOSED, merged=null**. All four issues are genuinely
CLOSED; the work was relaunched on fresh ground and landed via **replant** branches.

| Issue | PR I wrongly recorded | PR that actually merged |
|---|---|---|
| #433 | #483 (closed, unmerged) | **#485** |
| #436 | #469 (closed, unmerged) | **#472** |
| #460 | #486 (closed, unmerged) | **#487** |
| #464 | #471 (closed, unmerged) | **#473** |

Cause: PR numbers carried forward from before the relaunch and never re-derived after the merge —
the same root as the A2 error above. **Before citing any PR number from this file, re-derive it
from the forge.**

## Still owed to Tommy at the wave-4 checkpoint

1. **Does the epic continue past A2** into F (#424), C (#421), E (#423)? Three workstreams.
2. **The governor thread as one piece:** #458 (wire the writer into *tracked* settings so it ships
   at all) · #264 (land the 1144 unmerged lines asserting it still measures) · #452 (attribution).
   #488 is done. Measured: tracked `.claude/settings.json` wires `spine_rail.py` only and the gauge
   writer on **nothing** — every governor observation this epic made came from untracked local
   config.
3. **The trip band — MY EVIDENCE WAS RETRACTED. Do not repeat the old claim.**
   I said "crews trip at 17-21%; I ran to 44% with no trip, so the band is role-blind." **The #467
   Commander refuted it and was right:** an orchestrator holding several spines under one binding
   key writes **no reading at all** (`docs/GAUGE_WRITER_HOOK.md` §residuals, **#452**), and an
   Admiral holding an epic spine plus crew spines is exactly that shape. So *no trip at 44%* and
   *no gauge at 44%* are indistinguishable **without an asserted live reading** — #467's own "no
   absence is evidence" rule, aimed at me. The engine had already said so
   (`CONTEXT GAUGE SILENT ... too old to trust as a live reading`) and I read past it.

   **What stands:** the #467 Commander's **19.4%** — asserted, live, single-binding, taken
   pre-implementation while it worked on the trip-band issue itself. That reading carries DC4's
   *"overrides only where a gate has bitten"* on its own; the Admiral comparison is not used.
   Recommendation unchanged in substance: **leave the global band, ship A2** — every trip this epic
   saw cost a relaunch at a seam and lost no work.

4. **DISCLOSURE — a production-template behaviour change is shipping in wave 4.** The #467
   Commander is landing DC4's one mandated override as an absolute-token headroom reserve on the
   **commander spine's `execute` gate**. It is **tighten-only** (can only trip earlier, never
   later), graded `@grade: guess` with a named settle experiment, and it is **not** the global
   default. I approved it as inside the issue's mandate and told the Commander not to wait.
   **It changes behaviour for every future commander run and Tommy may reverse it.**

5. **The installer ships the forbidden interpreter.** `install_constellation.py:349` —
   `return "py" if os.name == "nt" else "python3"`. Installed **admiral** SKILL.md (line 61) and
   **explorer** SKILL.md (3 places) therefore instruct agents to run `py`, which **#454** says never
   to use because it throws a false `HARNESS ERROR` in every agent session. Cheap fix, recommended,
   not done — R2 authorized no second Commander this wave.
4. **#493, #495, #496, #497, #498** — five, not six: **#494 is already CLOSED**. Keep-or-drop is an
   acceptance-time question; the closeout audit produces the evidence.
5. **#460's 22 doctrine candidates**, collected, nothing promoted, at
   `.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4". Promotion is his call.
6. **#439 / #484 — two template-instantiation defects of one family** (`execute.c2`'s relative
   script path; `archive.c2b`'s literal never-substituted `<branch>`). Two in one spine argues for a
   sweep of the class, not two point fixes. Closeout triage candidate.

## Settled — do NOT re-derive

- **The repo-vendored `verify_iterative_role_artifacts.py` REFUSES from this repo** (#468):
  `installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py`.
  Use the **installed** copy at
  `C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py`.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — **never `py`** (#454).
- **A piped command's `$?` is the pipe's exit code.** Use `${PIPESTATUS[0]}`, or redirect to a file.
  This cost a false "verified" once already.
- **Never pass a markdown body to `gh` as a double-quoted bash string** — a backticked code span is
  executed as **command substitution**; the comment posts anyway, silently missing that phrase, with
  every success signal intact. Write to a file, use `-F`. Cost a corrupted comment on #264.
- **`gh issue close -F <file>`** accepts the flag, prints nothing, and does **not** close. Use
  `--comment "$(cat <file>)"`. And `--comment` is **silently discarded** if the issue was already
  closed by a PR body keyword — re-read the issue after closing, or the evidence evaporates.
- **`gh pr merge` can exit 1 on a merge that SUCCEEDED** (`--delete-branch` fails on a worktree-held
  branch). Ask the forge for state; never infer from the exit code.
- **`gh pr review --approve` is REFUSED** — "Can not approve your own pull request", because every
  agent authenticates as the same identity that authored the PR. Substitute:
  `gh pr review <PR> --comment -F <file>` with the verdict on the first line. This is **not**
  reviewer negligence, which is how I misread #470 three times.
- **Never use an ancestry test to decide whether anything merged.** Squash-merge returns the same
  answer for merged and abandoned. Ask the forge. Likewise `git diff origin/main..HEAD` in a
  worktree lists files where *main* is ahead — it reads like your branch reverted them.
- **Liveness has TWO channels; use the right one for the question.** Filesystem writes in the
  worktree say *something* is alive — but a crew's writes look identical to its Commander's, so it
  cannot tell "Commander idle, waiting on a crew" from "Commander dead, crew running on." The
  **harness pushes an idle notification** when a dispatched agent finishes; it fired for instances A
  (`10:12:41Z`) and B (`10:48:51Z`). **Its silence is informative precisely because it has
  demonstrably delivered** — an unproven channel's silence would mean nothing, which is the
  absence-as-evidence trap. Push, never pull: do not go looking for an answer the harness already
  sends you.
- **The lease field is not a liveness signal in either direction** (147 tracked spines, 18 `active`,
  1 live). Nor is the heartbeat: a Commander read 27 minutes stale while actively journaling its
  inner checklist. What discriminates: `find <worktree> -newermt "-6 minutes" -type f`.
- **`git cat-file -e origin/main:<path>` is broken in Git Bash here** — use `git diff --name-only`.
- **`verify_worktree_isolation.py` has two modes.** Bare paths = Admiral pre-wave gate;
  `--here <path>` = the Commander's check, and it tests **cwd**.
- **Batch bookkeeping commits; push at boundaries.** `ci.yml` has no `paths-ignore`, so an
  `.agent-work`-only commit runs the full 8-minute suite. Pushing per log entry put **6 concurrent
  CI runs on main, all mine**, starving a PR's check ~25 minutes.

_Updated: 2026-08-08T07:20:00Z_
