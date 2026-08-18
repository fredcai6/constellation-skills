# Launch Order: `cmdr-567-d1` — the complete doctrine sweep and the regrowth guard (#559, with #596 and #526)

Epic **#567** ("the door is the interface"), wave 2, lane **D1**. You are one of five lanes
(D1, D2, E, F and H). You start cold: everything you need is pasted below, not linked.

## Mission

Issue **#559**: *the door is the interface, not a second path — remove the CLI fallback for
agents.* Plus two co-travelers that are the same kind of work in the same files: **#596**
(`CONSTELLATION_FEEDBACK.md` is still mandated in several places after the switch to the
episode ledger) and **#526** (the Commander skill's stock close criteria cite a nonexistent
build script, and there is no survey-reuse convention).

You are the lane that closes the epic's headline issue, and you merge **last** so your guard is
authored and proven against a tree where every other lane has already landed.

**The deliverable is the guard, not the deletion.** #559 is explicit: this text has been
deleted twice and has grown back twice. A branch that removes every clause and lands no failing
guard has **not** closed #559, however clean its diff looks.

Three parts:

1. **The complete sweep.** Every `CLI fallback` clause in your files, and every live
   agent-facing `<engine>` token. Measured at your base commit `f05a3d78`: **15** clauses
   total, of which **2** live in `skills/workbench/**` and belong to lane D2 (which deletes
   their files outright), leaving **13** for you; and **11** `<engine>` tokens across 7 files.
2. **Door vocabulary in `specs/*.spine.toml`.** Measured: **zero** door mentions today, and
   only `implementer` and `reviewer` specs exist.
3. **The regrowth guard.** A test that fails if any of it comes back.

**The human's ruling on scope, given verbatim because it overrode a narrower recommendation
the Admiral had put to him:** *"sweep all possible now, let's do a complete sweep before we're
finished with the epic."* So the target is **all** of it, not all-but-one.

### Your target is live in this wave's own artifacts — measured, not argued

Lane H was dispatched an hour before you, and its spine's very first imperative — the text a
Commander reads at step one — contains this, verbatim:

> claim the engine session lease on this spine […] **CLI fallback: `<engine> claim
> --session-id commander-567-h --claimed-by commander --worktree .`** […] From here on, pass
> `--session-id commander-567-h` on every mutating CLI call against this spine (the door tools
> never take one).

And its `plan` imperative contains `<engine> waive plan --cond c6 --authority human --reason
'...'`.

So **both** halves of your target — an unresolved `<engine>` token and a `CLI fallback` clause —
are being handed to every Commander this epic dispatches, in the first thing it reads. They come
from `skills/commander/templates/COMMANDER_SPINE.template.json`, which is **yours**, and they
reach a live crew through `scripts/init_work_area.py`, which is also yours and which
deliberately never resolves `<engine>`.

Two things follow. First, this is the strongest available evidence that the sweep is worth
doing, and it belongs in your return. Second, it tells you where to check your work: after your
change, instantiate a fresh spine from your edited template and read its `init` and `plan`
imperatives. If a `<engine>` token or a CLI-fallback clause still reaches a Commander there, the
sweep is not done, whatever a grep over the templates says.

## Prior-Wave Verdicts (pasted)

**Lane A (PR #623, merged at `4573ef17`) removed the reason the sweep could not happen.**
Its verdict, in its own words:

> `spine_bind` lets a call name a **spine** (confined to the door's own checkout's work-area
> tree). It still does **not** let a call name an **identity** — the session is derived from the
> spine's own `work_id`, never supplied.

Its own honest weakness, which you should read before you judge your own line count:

> **This lane's net line count goes UP.** ~2.3k insertions across source and tests; 112
> deletions. […] What it actually deletes is **one refusal clause** […] and **the reason the
> epic's 26 fallback clauses and tokens cannot be deleted.** Wave 2 does that deleting; this
> lane removes the blocker.

**The Admiral verified lane A independently before authorizing your lane**, in this session:
`spine_bind` on the epic spine returned `SPINE_SESSION constellation/epic-567-door` with
`already_bound: false` on the first call, and the epic has been driven through the door ever
since with no CLI invocation.

**And the harder question was measured, because it decides whether your sweep is honest.** The
Admiral first found that a lane Commander's door *cannot* bind a spine in a sibling worktree —
the gate refuses it deliberately (`_own_checkout_for_binding`, `mcp_spine_server.py:946`), and
its refusal recommends the CLI. That looked like proof the CLI was still load-bearing, and the
Admiral escalated it to the human as a material exception. **It was the wrong conclusion**, and
the measurement that corrected it is the one you should carry:

> A door launched from the lane's own worktree with `SPINE_FILE` set anchors to **that
> worktree** and binds that lane's spine. `spine_status` returned `isError: False`;
> `spine_lease claim` returned `claimed lease constellation/567-h -> active`.

**The dispatched-crew case is solved by launch, not by bind** — and you are running proof of
it, since your own door is bound to your own spine. So the CLI is not the only path for any
agent-facing case, and a complete sweep states the truth. The remaining gap is the
Agent-tool/`ExternalBackend` path, which builds no environment and which lane B's **#432** work
made *refuse* a spineless success rather than silently accept one (PR #621, merged at
`6668b7ff`).

**Lane C (PR #620, merged at `9e1185af`)** settled that the **Stop hook outranks the
context-trip advisory** (#595). Do not reopen that precedence. Lane C also edited
`skills/commander/references/crew-dispatch.md`, which is why that file now carries an
`<engine>` token it did not carry when the epic began — your target file set moved under wave
1, and the Admiral re-measured it at your base rather than trusting the epic body.

**Lane G (PR #622, merged at `22f9637d`)** shipped `finish_work` (one-verb mechanical closeout,
#574) and made archiving release a run's lease (#552). Both issues are **closed**.

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — **say so when you override
one**, in your return.

### Mission-specific

- `decision:complete-sweep` — **settled/human, and it overrode the Admiral's own
  recommendation.** Sweep **all** the clauses in your files, not all-but-one. The Admiral had
  recommended keeping one narrowly-scoped clause for the dispatch path it believed had no door;
  the measurement above showed that path does have one, and the human ruled: *"sweep all
  possible now, let's do a complete sweep before we're finished with the epic."*
  `@grade: settled/human · leans d1`
- `decision:guard-is-the-deliverable` — a deletion with no **failing-guard demonstration** does
  not close #559. Red-proof it: reintroduce a clause and an `<engine>` token on a scratch
  branch, show the guard fails, remove them, show it passes. The guard must assert against the
  text's **absence** in a way a reintroduction trips — never against a description of the rule.
  `@grade: settled/doctrine · leans d1`
- `decision:two-engine-sites-are-not-targets` — of the 11 `<engine>` sites, two are **not**
  agent-facing instruction and must survive:
  `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` (a historical plan
  record) and `scripts/init_work_area.py:24` (a comment documenting the placeholder convention
  itself, naming `<engine>` as an example of a token the script deliberately never resolves).
  **Read both before deciding.** Classify all 11 and report the classification; do not silently
  skip. `@grade: settled/doctrine · leans d1`
- `decision:the-cli-still-exists-for-operators` — the epic removes the CLI as an **agent-facing
  path**, not as a tool. Operator and debug use stays. Your replacement wording should name the
  real agent path — a dispatched crew is launched with its spine bound
  (`run_crew.py --backend cli --spine`), and the Agent-tool path binds nothing and is refused
  (#432) — rather than simply deleting a sentence and leaving a reader with no answer.
  `@grade: settled/doctrine · leans d1`
- `decision:guard-scope-is-yours-to-design` — how the guard expresses "agent-facing" without
  either exempting the whole corpus or catching historical records is the wave's load-bearing
  unknown, and it is yours. One warning from evidence: the episode-observation guard's
  exception list already carries **11** entries across five prior runs, which is what an
  exception-list-shaped answer decays into.
  `@grade: guess · leans d1 · settle: red-proof the guard against both a reintroduction and a
  legitimate historical mention`
- `decision:526-may-be-stale` — the Admiral grepped `skills/commander/` for the nonexistent
  build script #526 names and found **no match**, so the issue may already be stale or may
  describe different wording. Verify it reproduces before fixing it; an evidenced "no longer
  reproduces" is a complete disposition. `@grade: guess · leans d1 · settle: read #526 at
  source and grep for its actual strings`

### Standing, this epic

- `decision:reduce-complexity` — judge a change by whether it reduces complexity, and in
  particular by the human's test for trades of this kind: **does this choice reduce work on
  agents by moving it into mechanisms?** Removing a redundant path counts even when your own
  line count rises. Do not over-engineer; note simplification opportunities rather than
  building for them. `@grade: settled/human · leans all lanes`
- `decision:no-net-deletion-rule` — there is **no** rule that every lane must end with
  something deleted. It was withdrawn on 2026-08-17 by the human, who never set it: *"I never
  said that every lane needs to end with something deleted, or at least never intended that."*
  Wave 1 enforced it on four launch orders under his name and it was the Admiral's
  mis-recording. Do not reintroduce it, and do not pad a return with a deletion to satisfy it.
  `@grade: settled/human · leans all lanes`
- `decision:honest-null-is-complete` — a measured negative on the stated question is a
  complete, successful deliverable, reported with the same rigor as a win.
  `@grade: settled/human · leans all lanes`
- `decision:no-issue-filing-mid-run` — **you file no issue.** Stage every triage candidate as
  a file under `.agent-work/567-d1/triage-candidates/`. The human's reason: *"we've been
  ballooning out tracking."* At epic closeout each candidate is paired onto an **open** issue
  as a comment, or recorded as an episode. A lane that wants to file is not floating a
  decision — the answer is already ruled. `@grade: settled/human · leans all lanes`
- `decision:no-doctrine-promotion` — you may not promote an observation into `docs/agents/*`.
  That is the human's call. Record the observation and say so.
  `@grade: settled/project · leans all lanes`
- `decision:records-are-not-instruction` — `docs/superpowers/plans/**` and
  `docs/superpowers/specs/**` are **historical records**. Editing them to make a sweep count
  come out right falsifies the record. Leave them, and say in your return that you did.
  `@grade: settled/doctrine · leans all lanes`
- `decision:in-session-hook-observation-is-not-evidence` — hooks execute from the **main
  checkout** regardless of worktree (`CLAUDE_PROJECT_DIR` resolves once at session launch,
  #269). Validate engine, door or hook behaviour in a **fresh process** with explicit paths. An
  in-session observation after an edit is struck from any gate that would accept it.
  `@grade: settled/project · leans all lanes`
- `decision:map-index-is-admiral-owned` — **do not regenerate or hand-edit `map/INDEX.md`**
  (#544: it is generated, committed and freshness-tested, so every parallel branch stales it
  and two regenerating lanes conflict by construction — in wave 1 it blocked three of four
  lanes plus a concurrent session in one afternoon). Your branch is accepted green **except**
  `tests/test_code_map.py::MapTreeFreshnessTests`. The Admiral regenerates once on the final
  merged main and re-verifies there. `@grade: settled/doctrine · leans all lanes`
- `decision:no-fork-for-design` — if you dispatch any helper for candidate generation or
  design, use a **fresh** agent, never a `fork`. A fork inherits its dispatcher's full context
  and therefore believes it *is* the Commander: in wave 1 a lane-G fork rewrote its
  sole-writer notes file in the first person and drove its `spine.json` under the identical
  lease id, and lane G halted a delivering run believing its worktree was compromised. Your
  process has no `Agent` tool, so a helper means a fresh `claude -p` through Bash — which is a
  genuinely cold process and therefore the better instrument anyway.
  `@grade: settled/doctrine · leans all lanes`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it
with the same rigor as a win, with the evidence that establishes it. Do not substitute your own
judgement for a measurement your mission calls for and present the result as measured — a lane
that does that has failed while appearing to succeed.

## Inherited Latitude

| Class | Your disposition |
|---|---|
| Implementation choices inside your own files | **yours** |
| Replacement wording for each clause | **yours** |
| The guard's mechanism and scope expression | **yours** |
| How `specs/*.spine.toml` express door vocabulary | **yours** |
| Reopening #595's advisory precedence | **forbidden** — settled by lane C |
| Architecture / structural change | **float to the Admiral** |
| Scope change (issue added, dropped, re-scoped) | **float to the Admiral** |
| Production defaults / user-visible behaviour | **float to the Admiral** |
| Issue filing | **ruled: none.** Stage candidates locally |
| Promoting an observation into `docs/agents/*` | **forbidden** — human's call |
| Fix-now triage inside your own worktree | **yours** |
| Spend / model tier | **yours** within the budget below |
| Anything that fits no class above | **float**, with one line on why it fit none |

Float by writing your question into your return artifact **and** ending your turn with it
stated plainly. The Admiral answers and continues you. Asking up is always sanctioned.

## File Ownership

**You are the sole writer this wave of:** `skills/**` **except** `skills/workbench/**`; `specs/**`; `scripts/init_work_area.py`; `scripts/collect_feedback.py`; `scripts/agent_work_root.py`; `docs/**` **except** `docs/agents/CREW_CONTEXT.md` and **except** `docs/superpowers/**`; `tests/test_retirement_guard.py` plus any new guard test file.

**Fenced — do not edit, another lane owns it this wave:**

| Path | Owner |
|---|---|
| `skills/workbench/**`; `scripts/install_constellation.py`; `scripts/verify_skill_registered.py`; `scripts/measure_overread.py`; `docs/agents/CREW_CONTEXT.md` | lane D2 |
| `scripts/mcp_spine_server.py`; `episodes/**` | lane E |
| `scripts/run_crew.py` | lane F |
| `scripts/checklist_engine.py` | lane H |
| `map/INDEX.md` | the Admiral |
| `.agent-work/epic-567-door/**` except your own results file | the Admiral |

If your mission genuinely needs a file another lane owns, **float it**. Wave 1 had two lanes
write one path and it cost a merge.

Your working-notes file, sole writer, is `.agent-work/567-d1/notes-1.md`. Name it exactly that —
**never** `findings-<n>.md`: the harness `Write` tool refuses any path whose basename contains
"findings", a guard aimed at unprompted report-dumping that cannot tell this file was
deliberately assigned. Three agents hit it in one epic and each worked around it with a shell
heredoc. The guard is not ours to change; the word is.

## Workspace

- **Spine (yours, already provisioned):**
  `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard/.agent-work/567-d1/spine.json`
- **Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
- **Branch:** `feat/567-d1-doctrine-sweep-guard` · **Base commit:** `f05a3d78`
- **Created by:** `git worktree add -b feat/567-d1-doctrine-sweep-guard .worktrees/567-d1-doctrine-sweep-guard f05a3d78`
- **Main freshness verified before dispatch:** `origin/main` at `f05a3d78`, full suite **3352
  passed, 6 skipped, 1219 subtests passed, 0 failed, 0 SUBFAILED** on Linux in a clean detached
  worktree.
- **Merge position:** this lane merges **last** in the wave. You merge last because your regrowth guard must be authored and proven against a tree where every other lane has landed — including lane E's change to the door's own refusal text, which your guard would otherwise fail on. Expect to rebase on the merged main before your final gate.

Your first command is to `claim` the engine lease on the spine above.

**Your door is bound to your own spine, and this is the first wave where that is true.** Call
the `spine_lease` MCP tool with `action=claim, claimed_by=commander, worktree=.` — no CLI, no
`spine_bind`, no environment surgery. Your process was launched by
`run_crew.py --backend cli --spine`, which assigned `SPINE_FILE` to your spine and an
assignment-keyed `SPINE_SESSION` into your environment, and started you with your worktree as
cwd. Your door therefore resolved to your own spine at startup. This was measured before the
wave launched, not assumed: a door launched this way anchors to its own worktree and returned
`spine_status` and `spine_lease claim` cleanly.

**This matters to your mission and to the epic.** The epic's definition of done includes *"a
dispatched crew drives its own spine through the door end to end."* You are that crew. Drive
every gate through the MCP verbs. If you ever find yourself reaching for
`scripts/checklist_engine.py` on the command line, stop and float it — you have found either a
verb gap or a defect, and either one is worth more to this epic than the workaround.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not
a local merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved
once, at session launch, so a Commander in an isolated worktree still executes the **main
checkout's** hook code against the **main checkout's** state, even while every git operation
stays correctly fenced (#269). If your change touches anything the hooks read, you cannot
validate it from inside the process that would run the unchanged code. Validate in a **fresh
process** with explicit paths — never a fixture that hand-injects the value you are trying to
prove the harness delivers.

## Inherited Context

- **A bare `cd` may not persist between Bash calls.** Wave 1's lane A ran 47 minutes and wrote
  **zero bytes** stuck on exactly this; its dying words were *"the bash cwd resets between
  calls."* Use a **single compound call** — `cd /abs/path && <command>` — or absolute paths
  everywhere. Your process's cwd starts in your own worktree.
- **The merge gate is the full suite green on Linux**, run in a **clean detached worktree of
  your branch**, never in your working copy. Wave 1's Admiral authored that exact defect four
  times: *a check that runs against your own working copy is not a check on the world.* The
  shape is `git worktree add --detach <tmp> <your-branch-sha>` then run the suite there.
  Windows CI is red on a pre-existing ~122-failure path-casing baseline and is **not** the
  yardstick (#575 is deferred).
- **A failing subtest is now greppable.** The repo-root `conftest.py` (PR #626) restates each
  failed subtest as a line beginning `FAILED `, with a `[subtest …]` marker. Before that,
  `grep '^FAILED'` returned nothing for a failing subtest, because `SUBFAILED` cannot match
  `FAILED ` — the next character is `(`, not a space — and wave 1's Admiral shipped a merge
  gate with that hole and reported "120 tests fixed" from an empty failure list. Grep for
  `^FAILED` and trust it.
- **`episodes/` has exactly one write path**, `scripts/apply_episode_delta.py`, always with
  `--store-root episodes`. Never hand-edit it. To reword an assertion use its
  `restate-assertion` op. If your run touches the store, the order is **write → `git add` →
  suite → commit**: `test_canon_episode_store_untouched` is worktree-vs-index only, so running
  the suite between the write and the stage trips it with a message that reads like store
  corruption.
- **The episode-observation guard cannot tell a past-tense verb from an imperative** ("read",
  "grep"). Rephrase to remove the bare verb; **do not** add to the exception list, which
  already carries 11 entries across five prior runs.
- **GitHub has been returning intermittent 503s all day.** `gh pr create` and `gh pr merge`
  need retrying — up to six attempts in wave 1. **Gate each retry on whether the world
  actually changed** (`git rev-parse origin/main`, `gh pr view`), never on the command's own
  output.
- **A concurrent session works this repo.** `origin/main` moved under wave 1's Admiral twice,
  once breaking it with 9 Linux failures from a pair of individually-green PRs. Check
  `git rev-parse origin/main` before you assume your base is current. Do **not** touch
  `.worktrees/issue-610-stand-up-work-area` — not yours.
- **`.agent-work/` is tracked deliberately** (11,188 files). Your run artifacts, verdict and
  triage candidates are committed on your branch and reach `main` at merge.

## Pre-empted Steps

- **Work-area stand-up is done.** Your worktree, `.agent-work/567-d1/`, and `spine.json`
  were provisioned by the Admiral per `skills/_shared/stand-up-work-area.md`. You do not
  scaffold, and your `init` step means exactly one thing: claim the lease.
- **The `--here` arrival check is retired as an instruction** (#610). Do not run
  `verify_worktree_isolation.py --here`. Isolation was gated by the Admiral across all five
  worktrees before dispatch: `worktree isolation verified: 5 distinct worktrees`, exit 0.
- **Your door-binding was pre-verified** — see Workspace.
- **The wave's replan transition is done and verified.** `.agent-work/epic-567-door/transitions/w2/`
  carries the `REPLAN_INPUT`/`REPLAN_RESULT` pair, `admiral-prelaunch` exited 0, and
  `CURRENT_TRUTH.md` plus `WAVE_REVIEW.md` are rendered from it. You do not replan; you deliver.

## Data Locations

Everything your mission needs is tracked and present in your worktree. There are no untracked
inputs. The main checkout is `/home/tommy/projects/constellation-skills` — readable if you need
it, **never** writable by you.

## Local Unknowns

Named so you do not mistake them for settled:

- Whether the guard belongs with the retirement-guard family in
  `tests/test_retirement_guard.py` or as its own module.
- How the guard expresses "agent-facing" without exempting the corpus or catching historical
  records. **This is the wave's load-bearing unknown.**
- Whether `specs/*.spine.toml` need new keys or only new prose, given only `implementer` and
  `reviewer` specs exist.
- Whether #526 still reproduces at all.

## Budget

- **Model tier (required):** **Opus**.
- **Compute/time, session-window:** One extended session. This is the epic's headline lane and the widest diff; the guard is worth more of your budget than the deletions are.

## Stop Conditions

Stop and return when: scope is exceeded; a decision outside your inherited latitude is needed;
budget is crossed; the evidence your mission demands is impossible to obtain; or you need
**context this order does not cover and cannot safely proceed without** — return-and-query the
Admiral, which answers and continues you. Asking up is always sanctioned and is never counted
against you.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token
cap, not a share of your window, so a Commander that has loaded its skill, references,
templates and this order can be over it on turn one having done no work. The engine refuses
only the verbs that BEGIN work at a gate (`start`, `reopen`), and only until a refresh-request
exists for that gate. The legal sequence is: **attach the refresh-request against the current
why-record, then `start`, then do the work.** Attaching first sends the guard down its release
path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to
`advance --why` and hand off on turn one. A fresh agent that closes its gate before doing the
gate's work produces an infinite handoff chain — each successor arrives over the band, reads
the same line, and hands off again, with the gate's postconditions never met and no deliverable
ever written. Hand off when you have actually spent the context, not when you inherit the
reading.

**Do not end your turn with an engine gate open.** The Stop hook refuses it and is
authoritative over the context-trip advisory — wave 1's lane C settled that precedence (#595).
The sanctioned exit is the engine's `block` verb (`spine_halt` with `action=block`) naming what
you cannot satisfy and the next action.

## Return Shape

Write your result to
**`.agent-work/epic-567-door/results/lane-d1-RETURN.md`** — that exact path, inside
your own worktree, committed on your branch. **Not** `RETURN.md` at your worktree root: that
path is tracked, and in wave 1 four lanes collided add/add on `main` the moment the first one
merged.

Write the artifact and send your verdict **before** going idle. An idle notification with no
artifact reads as stalled, not done — the Admiral judges completion from what you produced, not
from a message that arrives after you have gone quiet.

Include, in this order:

1. **Verdict** — delivered, or an evidenced honest null.
2. **The sweep table** — every clause and token site, what you did to it, and why. All 11
   `<engine>` sites classified, including the two that survive.
3. **The guard, red-proofed** — the exact commands showing it fails on a reintroduced clause
   and a reintroduced token, and passes without them. This is the item that closes #559.
4. **`specs/*.spine.toml`** — before and after, with the door vocabulary you added.
5. **#596 and #526** — what you found and what you did, including an evidenced "no longer
   reproduces" if that is the answer.
6. **Suite result** — the full suite on Linux in a **clean detached worktree of your branch**,
   with the tally and the `^FAILED` grep output. `MapTreeFreshnessTests` may fail; nothing else
   may. State the commit sha you verified.
7. **Touched paths** — every file you wrote, so the Admiral can sequence merges. Name any file
   you wanted to touch but did not because another lane owns it.
8. **Map impact** — whether your change touches indexed source. Do not act on it.
9. **Triage candidates** — as files under `.agent-work/D1/triage-candidates/`, listed in
   the return. None filed as issues.
10. **Workflow feedback** — what helped, what got in the way, and **your own mistakes**. Wave
    1's single most useful output was a lane's honest account of its own errors; the Admiral's
    was its account of authoring the epic's own defect four times while holding the doctrine.
11. **PR** — opened against `main` from `feat/D1-567-d1`, with the number and the head
    sha.

On Windows, write the PR body to a temp file and use `gh pr create -F <file>` — never a heredoc
or a PowerShell here-string for a PR body. You are on Linux, so a heredoc is fine.

---

# ADMIRAL ADDENDUM — 2026-08-17, for the Commander resuming this lane

Your predecessor reached the context HARD band with `init`→`plan` complete and filed a
`refresh-request` against `execute`. It did **not** close `execute` to hand off, which was the
right call and is why you have a real gate to start rather than an empty one. Its measurements,
plan and design-rigor artifacts are committed at `bd677d7c` and are **not** to be re-derived —
`.agent-work/567-d1/{notes-1.md, MISSION_FRAME.md, execute.json, plan-rigor/CONVERGENCE.md}`.

It floated three things. All three are answered here so you do not have to float them again.

## RULING on F-1 — the three "second-checklist" sites: sweep all 13, reword those 3. APPROVED.

Your predecessor measured, in a fresh process, that a door **cannot** bind a second checklist
while it holds its own lease, and that releasing the lease to do so breaks `archive`'s own
requirement that the lease cover every journaled action. So for a Commander's `execute.json`, an
Interrogator's `interrogation.json`, and an in-session crew's own plan, **the CLI is the only
path there is.**

This is confirmed independently by the Admiral, three times over: lanes **F** and **H** each
drove their `execute.json` under a hand-supplied CLI session id (`commander-567-{f,h}-execute`),
and lane **E**'s implementer drove `IMPLEMENTER_PLAN.json` the same way. Every child plan in this
system is driven off-door. It is not one gate type and it is not improvisation.

**So: sweep all 13. No `CLI fallback` clause survives in your files.** For the three
second-checklist sites, replace the clause with a statement of the measured truth — that this
checklist is not the one your door is bound to, and naming the path that actually works. Do not
delete an agent's only path and leave it with nothing; that trades a documentation problem for a
hidden-fallback problem, and "fail visibly, no hidden fallback" outranks a clause count.

**Your predecessor's framing is correct and worth carrying into the wording:** *"'CLI fallback'
is the wrong word, because a fallback implies a working primary."* There is no primary here.

This does **not** relitigate the human's `decision:complete-sweep`. That ruling said *"sweep all
**possible** now"*, and it overrode an Admiral recommendation about the **dispatched-crew** path —
which a re-measurement showed does have a door, because a crew launched by
`run_crew.py --backend cli --spine` is its own process bound to its own spine. The
second-checklist path is a different one the ruling never considered. **The Admiral has surfaced
this to the human as an overridable call**; proceed as above unless a further addendum appears.

## RULING on F-2 — ownership of the mandating tests. GRANTED.

`tests/test_mcp_adoption.py` and `tests/data/store_mentions.approved.txt` were in no lane's
sole-writer list and no lane's fence table — an omission in the original order, mine. **You are
now their sole writer for this wave.** No other lane touches them, so there is no collision risk.
The sweep is impossible without them, since they are the mechanism that mandates the text.

## RULING on F-3 — a durable home for the ruling. HELD TO THE HUMAN, mitigation accepted.

Promoting the ruling into `docs/agents/*` is the human's call and no lane may take it. Your
predecessor's mitigation is accepted and should stand: **the guard quotes the ruling verbatim**,
so it is self-contained and deleting the guard destroys its reason along with it. The Admiral has
put the question to the human; do not wait on it.

## What your predecessor found that changes the job — carry it

**The regrowth has a mechanism and it is a test.** `tests/test_mcp_adoption.py::TestTier1ImperativeFields::test_field_still_carries_cli_fallback`
asserts each of 7 imperative fields still carries its exact CLI command line, and fails with
*"the CLI door must stay, never be removed or discouraged."* **That is why this text has been
deleted twice and grown back twice**: a lane deleted it, the suite went red on a test whose own
message said the CLI must stay, and the lane put it back. The blast radius is **nine** mandating
assertions, not one — `:737`, `:784`, `:834`, `:950`, `:954`, `:1132`, `:1149`, and
`TestCLIStaysAvailableNotDeprecated`'s `:1324` and `:1345`.

**And the counterweight is already in-tree:** `tests/test_mcp_adoption.py:838`
(`TestTier2SpineAlreadyBoundForDispatchedCrews`) already asserts *absence* for two files and
quotes the human verbatim — *"the agents should not know about the CLI. period."* Your guard is
therefore a **generalization of an existing precedent from 2 files to the whole corpus**, not a
new invention. Land it that way and say so.

**Three surface forms**, measured: `CLI fallback:` ×10, `CLI fallback,` ×4, `CLI fallback ` ×1. A
colon-only pattern is blind to a third of them.

## Two hazards your predecessor paid for — do not re-pay them

1. **A headless `claude -p` launched inside this worktree inherits `SPINE_*` and the session's
   Stop hook**, and your predecessor's probe agent began trying to drive **this lane's spine**
   before permissions stopped it. **Strip `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT` (and
   `CREW_SCRATCH_DIR`) from every helper you launch.** This is not hypothetical: lane H had a
   cold subject read its dispatcher's session id off disk and drive the live run under it.
2. `claude -p` helpers hit `Warning: no stdin data received in 3s` and one died with a bare
   `Execution error`. `< /dev/null` fixes it.

**Also inherited from lane F, and it will bite your suite run:** a dispatched crew's own
`CREW_SCRATCH_DIR` leaks into `fake_launch`'s `os.environ` base and reds
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
— a test your change does not touch. Reproduced by the Admiral. Unset those four variables for
your suite run. **Do not "fix" `run_crew.py` to satisfy it**; that would be a real regression
introduced to silence a false one.

## Unchanged

Everything above the addendum still binds: file ownership (plus F-2's grant), no issue filing, no
`docs/agents/*` promotion, `map/INDEX.md` is Admiral-owned, the return path, and the merge
position — **you merge last**, so rebase on the merged `main` before your final gate. Lane F is
already merged (`e3b2d41a`).

---

# ADMIRAL ADDENDUM 2 — 2026-08-17, for the Commander finishing this lane

Your predecessor delivered nearly all of #559 and its work is committed and rebased. **One thing
remains, it is small, and it is now unblocked by your predecessor's own change.**

## Your predecessor's residual, and the fact it got wrong

Its return says the guard is green everywhere except `skills/workbench/SKILL.md` and
`skills/workbench/references/checklist-engine.md` — *"both D2's, which D2 deletes."*

**Lane D2 has merged, and it did not delete them.** PR **#629** is in `main` (and in your
branch's history — verified). D2 **trimmed** the teaching half from 289 lines to 124 and kept
those two files, because deleting them outright broke two pre-existing suites that pin specific
sections as the corpus's sole written authority for content the door does not restate. D2 was
right to keep them, and it was structurally unable to remove the clauses: the paragraph carrying
them was pinned by `test_mcp_adoption.py`'s Tier2 test — **your file**, which your predecessor has
now inverted. Its own comment records the consequence: *"`skills/workbench/SKILL.md` came OFF this
list with the inversion."*

So the text is free to sweep for the first time, and only you can do it.

## RULING — `skills/workbench/**` is YOURS. The fence is lifted.

File ownership in this wave was a **concurrency control**, not a permanent boundary: one writer
per file *at a time*. D2 is finished and merged, so there is no second writer. The Admiral's
fence was the thing that made this residual unreachable — that error is mine, not yours and not
D2's.

**Scope, exactly:** the four `CLI fallback` occurrences in those two files (2 in each), which
your predecessor counted as 10 addresses. Nothing else in `skills/workbench/**` is in scope —
D2's trimming decisions stand, and every section it retained is retained because a named test
pins it. **Do not re-delete what D2 kept.**

**Two of those occurrences carry a sentence that is TRUE**, and this matters for the wording:

> *"CLI fallback, always available, and the only path for an in-session dispatched crew member
> driving its own plan or survey"*

#565 calls both halves of that sentence false. **They are not.** This wave measured four
independent times that a child plan — a Commander's `execute.json`, an Interrogator's
`interrogation.json`, an in-session crew's own plan — **cannot** be driven through the door: your
predecessor proved a door refuses to bind a second checklist while holding its own lease and that
releasing the lease breaks `archive`'s own requirement; lanes F and H drove their `execute.json`
under hand-supplied CLI session ids; lane E's implementer did the same with `IMPLEMENTER_PLAN.json`.

So apply the same disposition your predecessor's **F-1 ruling** already got for its three
second-checklist sites: **the phrase goes, the true content stays.** "Fallback" is the wrong word
because a fallback implies a working primary and there is none. State the real constraint plainly.
Deleting an agent's only path and leaving nothing behind trades a documentation problem for a
hidden-fallback problem.

## Acceptance

Your predecessor already proved the residual is the whole of it: with `skills/workbench/` removed
in a scratch copy, the guard is **fully green, 19 passed**. So the bar is simply that the guard is
fully green **on the real tree**, with no scratch copy and no exclusion.

Then: full suite in a clean detached worktree of your branch (`env -u SPINE_FILE -u SPINE_SESSION
-u SPINE_PARENT -u CREW_SCRATCH_DIR`), push, and open the PR. Append to the existing
`results/lane-d1-RETURN.md` rather than rewriting it — your predecessor's account of the sweep,
the guard and its own mistakes is the epic's most valuable single artifact and must survive intact.

## BUDGET — crews run at Sonnet. This is a human ruling and it is not discretionary.

**Pass `--model sonnet` on every `run_crew.py` dispatch you make.** Your predecessor spawned
**15** crew sessions and every one ran on **Opus**, because `run_crew.py` inherits this host's
`settings.json` default (`"model": "opus"`) when `--model` is unset — so a Sonnet-tiered lane
silently ran an Opus subtree. Six of those 15 were abandoned and retried, which is pure waste.
The human raised the spend directly and ruled Sonnet for all remaining work. That error was the
Admiral's: the launch order named a tier for the lane and said nothing about the crews the lane
dispatches.

**You are running at Sonnet yourself**, for the same reason — what remains is a bounded, fully
specified text change, not design work.

Given the size of this task, consider whether it needs a crew dispatch at all. A four-occurrence
edit in two files, with an existing guard as the acceptance test, may be smaller than the
machinery of dispatching for it. Right-sizing down is explicitly sanctioned.

## Unchanged

Everything above still binds, including Addendum 1's rulings (F-1 wording, your ownership of
`tests/test_mcp_adoption.py`, `tests/data/store_mentions.approved.txt` and the
`.agent-work/templates/` overlay, and the baseline-repair landmine — never
`--update-baseline --skills-root ~/.claude/skills`, always a shadow root built from repo source).
