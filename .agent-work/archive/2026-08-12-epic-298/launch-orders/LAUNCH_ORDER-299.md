# Launch Order: `commander-299 — issue #299, dogfood corpus + baseline capture`

You start cold. Everything you need is pasted below; nothing is behind a link you must resolve.

## Mission

Issue #299: **capture the pre-change baseline arm for the B3 map-first measurement.**

Epic #298 is testing whether a *canonical* architecture-map entrypoint changes what a Commander does when it has to find the right seam in an unfamiliar codebase. Issue #304 will land that contract (canonical entrypoint + degraded mode + tripwired prose deletion). **Once #304 merges, the pre-change arm is unrecoverable.** Your job is to capture it first, cleanly, with a frozen grading rubric, so #307 can pair pre and post and Tommy can rule on the pathway.

Your deliverable is **the captured baseline and its rubric — not the verdict.** The verdict is #307's, and it is Tommy's to make. Do not score the pathway. Do not conclude that map-first does or does not help. Capture, archive, and stop.

**Deliverable set:**
1. Five measured runs, transcripts archived, one per task in the frozen task set below.
2. A **pre-registered grading rubric**, written and frozen **before you look at any run's output**, committed as its own artifact. This is the credibility of the whole measurement — a rubric written after seeing results grades the results.
3. A baseline record stating, per run: the tool-call ordering evidence, the seam the run identified, and the rubric score — with the scoring done blind to nothing yet (single arm), but by a **separate grader agent that never saw this launch order**.
4. A PR into `constellation-skills` carrying the archive, the rubric, and the record.

## Frozen task set — and why it changed

Corpus: **f1Brainz** (`C:/Programs/f1Brainz`), ruled by Tommy. It is the only candidate that is large enough that "just read everything" is not free (5,928 tracked files), has a genuinely current actively-maintained map (`docs/architecture/`, 37 files, reconciled 2026-07-27 for epic #659 closeout at base main `5f802731`), is under live development right now, and has a backlog of individually-bounded issues at Commander grain.

**Five tasks, all verified OPEN and unassigned on 2026-08-01:**

| # | Task | Role in the instrument |
|---|---|---|
| **#690** | *Reconcile #664 G σ⁺ band scale (whole-lap pace σ) with per-class deficit units* | **Real test.** Cross-module reconciliation between the grip baseline (D) and per-class deficit units (E). The boundary between two components is exactly what a map states explicitly and code-crawling has to reverse-engineer. |
| **#688** | *Grip-fit rain exclusion too aggressive: 'any wet sample' drops ~55% of weekends* | **Real test — probably the cleanest single one.** The title names the symptom, not the file. Locating where rain exclusion lives inside `grip_baseline` requires either reading the physics packet or crawling source. |
| **#698** | *#666 follow-on hardening: store-API primitive-obsession, script .pth path, gitignore* | **Real test, scored on seam-finding ONLY.** Ignore its packaging/hygiene sub-concerns entirely — they are noise for this measurement. The question is which component owns the store API. |
| **#716** | *constellation: work_id-with-slash parsing breaks run_crew.py + verify_agent_feedback.py* | **Coverage probe.** A cross-cutting tooling bug inside f1Brainz that the physics-oriented map probably does not cover. Measures what happens **today** when the map has nothing to say: silent crawl, or acknowledged miss? That is the pre-contract behaviour #304's degraded mode is meant to replace. |
| **#704** | *#668 cleanup: dedup axis-grouping helper in instrument_panel/replication.py* | **NEGATIVE CONTROL.** Single file, function-level, named in the issue title. A map should **not** help here. If map-first shows the same lift on this as on the real tests, the instrument is measuring something other than map value and the task set needs re-cutting. |

**This set differs from the one recorded in the latitude contract, and the change is mine to own.** The contract named #710, #715, #698, #704. Recon then established that **#710 already lists the exact three files to repoint** (`segment_map/{store,identity,derivation/derive}.py`) and **#715 names the exact private helpers and both files involved.** I picked them on grain — multi-file, boundary-ownership questions — which is a real property, but it is not the property being measured. #304's contract is about **orientation**: where do I start looking. A task that hands you its files has no orientation left to measure. Keeping them would have given the instrument **three negative controls and one real test**, which would have gutted it.

Rejected from the recon's own recommendation for the opposite reason: **#696** is roadmap/epic grain (it confounds map value with task size, and it has already graduated into `docs/architecture/decisions/builds-2-3-forward-roadmap.md`, so a map read would be near-tautological), and **#717** is design investigation rather than navigation.

**Do not re-cut this set.** If you believe a task is wrong, float it — do not substitute.

## Method — the part that determines whether this is worth anything

**Each measured run stops at plan stage. Nothing lands in f1Brainz.**

This is deliberate and it solves three problems at once. (a) These are real, live backlog items on another project's roadmap; letting a measurement run implement and merge them spends f1Brainz's actual backlog on #298's schedule. (b) If the baseline run lands the change, the task no longer exists for the post-#304 arm — **there would be no pre/post pair on identical tasks**, which is the entire point. (c) `gh` write operations against `fredcai6/f1Brainz` are **not pre-cleared** in the latitude contract; a read-only, never-pushed run needs no such clearance.

So each measured run: **understand + plan, then return the plan.** No implementation, no commit, no push, no PR, no issue comment on f1Brainz. If a measured run tries to push or open a PR against f1Brainz, that is a stop condition — kill it and log it.

**Pin the window.** Every measured run works from a worktree at f1Brainz commit **`3541d292`** (`3541d2929b19de37107ae13e56776b7162d07255`, 2026-08-01 09:52 -0700). f1Brainz is actively developed and its map has a demonstrated reconcile cadence; a baseline spread over days against a moving map would be measuring different things run to run. The post-#304 arm must use this same pin. Record it prominently — it is the single most load-bearing number in the archive.

**Each measured run gets its own f1Brainz worktree.** Never two runs in one worktree — that is data loss, not friction.

**The measured runs must not know they are being measured.** Give each one the ordinary task brief and nothing about epic #298, nothing about map-first, nothing about what is being observed. An agent told its map-reading is under observation will read the map. Their brief is: here is issue #N in this repo, understand the problem and produce a plan naming the files you would change and why. That is all.

**What to record per run**, since this is what #307 consumes:
- The full tool-call sequence.
- **The ordering measure**: the index of the first read under `docs/architecture/*` and the index of the first read under `src/*`. If no `docs/architecture/*` read occurs, record that explicitly — an absent map read is a *finding*, not a missing datum, and must be visibly distinct from a datum that was never collected.
- Which map files were read, by path.
- The seam claimed: the exact file list the plan says it would change, in the plan's own words.
- Wall-clock and token cost of the run.

## The rubric — freeze it first

Write the grading rubric **before any measured run produces output**, and commit it in its own commit so the git history proves the ordering. It must state, in advance and falsifiably:

- What counts as **correct seam identification** for each of the five tasks, resolved against the actual repo at `3541d292` — you determine ground truth by reading the code yourself, before the runs, and you write it down.
- The scoring scale, and what a partial credit looks like.
- **What result would falsify map value**, stated up front. Specifically: what pattern across these five would mean the map did not help. If you cannot state a losing condition, the rubric is not a measurement.

Then a **separate grader agent** — one that has never seen this launch order and does not know which task is the negative control — scores each run's claimed seam against the frozen ground truth. You do not grade your own runs.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- decision:corpus-is-f1brainz — f1Brainz is the dogfood corpus. Tommy's ruling.
  `@grade: settled/human · leans #299,#307`
- decision:baselines-before-f-merge — this baseline is captured before #304's map-input contract change merges; the comparison arm must be pre-change.
  `@grade: settled/human · leans wave-0,#304,#307`
- decision:baseline-task-set — the five above, with #704 as the deliberate negative control and #716 as the coverage probe.
  `@grade: settled/human · leans #299,#307 · settle: if the negative control shows the same lift as the real tests, the instrument is measuring something else and the task set needs re-cutting`
- decision:plan-stage-only — measured runs stop at plan; nothing is implemented, committed, pushed, or merged in f1Brainz.
  `@grade: settled/human · leans #299 · settle: if a plan-stage transcript turns out to lack the ordering signal #307 needs, extend to implementation on ONE task and compare`
- decision:baseline-artifacts-live-here — archives land in `constellation-skills` at `.agent-work/epic-298/baselines/`, **not** in f1Brainz's own `.agent-work/`. They serve epic #298, `.agent-work/` is tracked in this repo as of #326, and a cross-repo absolute-path reference rots the moment either checkout moves.
  `@grade: settled/human · leans #299,#307`
- decision:rubric-frozen-before-runs — the rubric and ground truth are written and committed before any measured run executes.
  `@grade: settled/human · leans #299 · settle: none — this one is not up for revision; a rubric written after the results grades the results`
- decision:baseline-is-informal-map-not-no-map — **never describe this baseline as "no map."** Today's `commander-core.md` and its templates already reference `docs/architecture`, so the current Commander is not map-blind. The correct label is **"scattered prose, no canonical entrypoint, no degraded-mode contract."** #304 formalizes and consolidates map-reading; it does not invent it from zero. A report that says "no map" will be read as a stronger claim than the evidence supports.
  `@grade: settled/human · leans #299,#307`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. The epic spec says so explicitly: *"if deletion alone suffices, the break is not taken — that outcome is success, not failure."*

This applies with unusual force here. If the baseline shows Commanders already orient well without a canonical entrypoint, that is a real and useful result — it would mean #304 is cheaper than assumed, not that your run failed. **Do not shade the capture toward a result.** You are building the instrument, not the answer.

Also scoped: a negative result kills that specific test, never the idea class. If one measured run fails to produce a usable transcript, report "run #N's transcript was unusable because X" — never "transcript capture is not feasible."

## Inherited Latitude

**Delegated to you** — adjudicate and log, do not ask:
- Architecture/structural choices inside your own deliverable (archive layout, rubric shape, how you instrument the runs).
- Issue filing and closing on `fredcai6/constellation-skills` (`gh issue create/comment/close` are pre-cleared). File findings to the tracker directly; **never bank them worktree-locally for someone to harvest.**
- Fix-now triage: bounded fixes applied immediately; full test suite; `git push` to `epic-298/*` branches.
- Merge to main: green + reviewed only, gated on the CI check exit code.
- Model tier for your sub-dispatches, within the Budget section below.

**Must float to me** — do not decide these yourself:
- Any change to the task set, the corpus, or the pin.
- Any scope change to #299.
- Production defaults or user-visible behavior.
- Two-bin routing rulings and pathway verdicts — those are **Tommy's, always**. You are capturing evidence for one; you are not issuing one.
- Anything that fits none of the above: escalate with one line on why it fit no class.

**Explicitly NOT pre-cleared:** any `gh` write against `fredcai6/f1Brainz`. Read-only there. If you conclude you need a write, stop and float.

## File Ownership

Your working notes: **`notes-299.md`**, in your worktree. Sole writer.

> Name it `notes-299.md`, **never** `findings-299.md`. The harness `Write` tool refuses any path whose basename contains "findings" ("Subagents should return findings as text, not write report files") — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. Three agents hit this in one epic and each worked around it with a shell heredoc. The guard is not ours to change; the word is.

## Workspace

**Your worktree, already provisioned for you:**
```
C:/Programs/constellation-skills-wt/e298-299
branch: epic-298/299
base:   c2e16a87fcb0371d6b1a3cdaf639dab26d7dad54  (origin/main, "chore: track .agent-work/ — run history is project history (#326)")
created by: git worktree add "C:/Programs/constellation-skills-wt/e298-299" -b epic-298/299 c2e16a8
```

**First step, before any git operation:** run
```
py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/e298-299"
```
from **inside** that worktree. It must exit 0. Paste its output into your return report. (Run from anywhere else and it correctly refuses — that is the check working, not a bug.)

**Do not touch `C:/Programs/constellation-skills` (the main checkout).** It carries Tommy's own uncommitted work — `scripts/install_constellation.py` and `tests/test_write_a_skill.py` — which a branch checkout there would destroy. This already happened once this epic and cost a recovery. Everything you do happens in your worktree.

**f1Brainz worktrees:** provision one per measured run, at the pin, with **absolute paths only** — a relative `git worktree add ../foo` issued from inside a worktree resolves somewhere you did not intend, and this epic already created a stray worktree inside the main checkout that way. Suggested shape:
```
git worktree add "C:/Programs/f1Brainz-wt/base-690" -b baseline/298-690 3541d2929b19de37107ae13e56776b7162d07255
```
Sweep them when done (`git worktree remove` + `git worktree prune`), and delete the local branches — none of them are ever pushed.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

## Inherited Context

Platform and process invariants that have already cost this epic real time. These are pasted, not pointed at, deliberately — and note that this is the **last epic** in which a launch order carries lessons this way. Tommy ruled the lessons playbook a dead end; #308 moves consolidated doctrine into `docs/agents/` and cuts live agents off from the lessons inbox entirely.

**Python and CI (this one caused 39 CI failures on PR #320):**
- On this machine `py` resolves to **3.12.13**, which matches what CI pins. `python` resolves to **3.14.3**, which is ahead of CI. Use `py`, not `python`, for anything whose result you will trust. Issue #313 documents the docs prescribing the wrong one.
- **Gate every merge on the CI check exit code read at source** (`gh pr checks` exit status, re-run at merge time), never on a locally-reported green and never on a human-readable summary. Never chain a merge onto a watch command.
- `Path.read_text(newline=...)` is 3.13+. It will pass locally on `python` and fail on CI.

**Windows:**
- Write files with explicit `encoding='utf-8', newline='\n'`. The default is the ANSI codepage and it silently corrupts non-ASCII — this epic lost a harvested JSON delta to `UnicodeDecodeError: byte 0x97`.
- MAX_PATH is real. Paths over ~180 characters break `git worktree add` with "Filename too long" on windows-latest. PR #326 failed CI on exactly this after I had measured file count and size but not path length.
- PR bodies: write to a temp file and use `gh pr create -F <file>`. A heredoc or a PowerShell `@'...'@` here-string **fails for PR bodies**. Here-strings work for `git commit -m` only — and if you are in the Bash tool, PowerShell here-string syntax is not available at all; this epic shipped a commit subject literally beginning `@ ` that way.
- `core.autocrlf` means working-tree bytes can differ across worktrees for the same committed content (issue #319). If you compare files, compare normalized content or blob OIDs, never raw working-tree bytes.

**Engine:**
- Never hand-edit a spine or survey JSON. The engine owns that state and stamps the provenance.
- Engine `--finding` text containing backticks is **shell-mangled and silently drops words** from the journal. For a provenance system that is worse than a refusal. Avoid backticks in findings.
- On a **survey**-type checklist, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only. A reviewer hit this across five rounds in one issue and found it only by being refused.
- Command postconditions inherit the launcher's cwd (`_run_check_command` passes no `cwd=`, unlike `_git`) — issue #315. Relative paths in check commands resolve against the wrong root.

**Method invariants this epic has paid for:**
- **A check that cannot fail is indistinguishable from one that passed.** #300's single acceptance test survived two independent reviewer rounds while being structurally unable to falsify its own property — it re-encoded both children's artifacts through the *parent's* encoder. The cold panel found it with 45 deliberate mutations (34 killed, 11 survivors, and the survivors were the map of the blindness). Before you trust any check you write, mutate the thing it guards and confirm it goes red.
- **A reviewer given a handoff checks conformance to that handoff.** No handoff asked "can this test fail?", so no reviewer asked it. If you want that question answered, you must ask it explicitly.
- **Verify launch-order claims against the code.** This order states facts about f1Brainz, about the pin, and about what issues contain. Four confirms in this repo's history say orders carry stale or wrong claims. If something here does not match what you find, **the code wins** — say so in your return.
- **Derive distribution claims from a command.** "All N failures are in file X" must come from a `uniq -c`, never from reading a pytest tail. Under-inclusive attribution cost a rework round-trip.
- **A round-trip test proves the parser, not the artifact.** If you serialize and deserialize with the same code, you have tested a fixpoint, not correctness.
- **A non-reading is not a low reading.** If a measured run produced no map access, that must be visibly distinct in the archive from a run whose map access was never captured.

## Pre-empted Steps

Already done by me; cite this order rather than redoing them:
- **Corpus selection.** Ruled by Tommy: f1Brainz. Do not re-survey candidates.
- **Task-set selection.** Frozen above, with reasoning. Do not re-cut.
- **Recon.** A full candidate-corpus and candidate-task survey exists at `.agent-work/epic-298/prep-299-report.md`, tracked on main. Read it for context — but note its §2/§4 recommended a **different** task set, and the Mission section above supersedes it with the reasoning for the change.
- **Worktree provisioning** for your own workspace (above). You provision the f1Brainz ones.

## Data Locations

- Corpus: `C:/Programs/f1Brainz` — a real git repo, HEAD `3541d292` as of 2026-08-01 09:52 -0700. **Read-only.** Provision pinned worktrees from it; never push, never merge, never comment on its issues.
- Its map: `C:/Programs/f1Brainz/docs/architecture/` — `index.md`, `MAP_BUILD.md`, `decisions/`, `overlays/`, `packets/` (16 domain packets), `reference/`. 37 files. Last reconciled 2026-07-27 at base main `5f802731`. **Note there are commits after that reconcile** — the map is 5 days old against a live repo, which is realistic and is part of what you are measuring, not a defect to correct.
- Recon report: `.agent-work/epic-298/prep-299-report.md` (in your worktree).
- Your archive destination: `.agent-work/epic-298/baselines/` (create it).

## Budget

- **Model tier (required):** **Opus** for you (the orchestration and the ground-truth reading are the hard parts). **Opus** for each measured run as well — the measured configuration must be the *standard* one, because a cheapened baseline is not the baseline. **Sonnet** for the grader agent. **No Fable subagents, at any tier, ever** — name the model explicitly on every dispatch; an unnamed model has defaulted upward before.
- **Compute/time, session-window:** Five plan-stage Opus runs against a 5,928-file repo is the dominant cost — real, but far below five full implement-and-merge runs, which is exactly why plan-stage-only was chosen. **At most 3 concurrent measured runs.** If a usage-limit reset is near, defer the remaining runs past it rather than launching into it and losing them mid-flight.
- Before any detached or multi-hour dispatch, write your crash-resume state note. Rewrite it before **each** new detach — the PID changes every time.

## Stop Conditions

Stop and return when:
- A measured run attempts to push, merge, or comment on f1Brainz — kill it, log it, and report.
- You conclude the task set, corpus, or pin needs changing.
- The rubric cannot be written falsifiably — i.e. you cannot state a condition that would show the map did not help. **That is a genuine stop**, not something to paper over; a rubric with no losing condition is not a measurement and I would rather know before the runs than after.
- Budget crossed, or evidence is impossible to obtain.
- You need context this order does not cover and cannot safely proceed without — **return-and-query me; I answer and continue you.** Asking up is always sanctioned and always legitimate. I would much rather field a query than read a guess. This epic has one logged Admiral error where a commander's float went unanswered and it merged on its own reading — that failure was mine, not the commander's, and I would like this one to go differently.

## Return Shape

Write your result artifact and send your verdict **before** going idle. An idle notification with no artifact reads as stalled, not done — deliver first. I judge completion from what you produced, not from a message that arrives after you have gone quiet.

Your return must contain:
1. **Verdict**: baseline captured, or an honest null with what blocked it.
2. **The pin**, restated, and confirmation that all five runs used it.
3. **Per-run evidence**: ordering measure (first `docs/architecture/*` read index vs first `src/*` read index, or an explicit "no map read"), map files read, claimed seam, rubric score, cost.
4. **The frozen rubric**, plus the git evidence that it was committed before the runs.
5. **The negative control's result called out separately** — #704 is the instrument's own check, and if it behaves like the real tests, say so loudly rather than burying it in a table.
6. **Map impact**: does this change constellation-skills' own architecture map.
7. **Triage candidates**: anything you found that should be an issue — filed to the tracker directly, with numbers listed here.
8. **Workflow feedback**: what this launch order got wrong, what the engine or tooling made harder than it needed to be. Blunt is useful.
9. Your `verify_worktree_isolation.py --here` output.
10. **PR number and its CI check exit code**, read at source.

**Do not issue the pathway verdict.** #307 pairs the arms and Tommy rules. Capture and stop.
