# Admiral Log — `epic-418-redux`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Contract: `.agent-work/epic-418-redux/LATITUDE_CONTRACT.md` · Plan: _pending latitude; spec of record is `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`_

The run's audit trail and the closeout retrospective's primary input. Append entries **as they
happen** — an unlogged ruling didn't happen. Own errors in the open: an ADMIRAL ERROR
entry that names the mistake and the fix is a closeout asset, not a liability.

Entry grammar (one line of date + tag, then the substance):

- `RULING` — an adjudication inside delegated latitude: what was decided, under which decision class, and why.
- `WAVE` — a wave launched: commanders, issues, worktrees, key launch-order terms (pre-rulings, fences, budgets).
- `INCIDENT` — a commander/crew death, stall, collision, or environmental kill: what died, autopsy, recovery action.
- `MERGE` — a PR merged: checks gated on exit code, diff verified in-fence, merge style and why.
- `ADMIRAL ERROR` — a mistake you own: what happened, cost, immediate fix, lesson candidate.
- `CHECKPOINT` — a contract checkpoint reached: what was presented, what the human decided.
- `ESCALATION` — a surfaced or out-of-taxonomy decision sent to the human, and the answer.
- `TRANSITION` — a replan boundary exit (`advance` / `repair` / `replan` / `stop`), verified.

## Predecessor run

This is a **relaunch**, not a fresh epic. The predecessor Admiral run (`epic-418`, 2026-08-05
to 2026-08-07) completed waves 0 and 1 and stopped clean before wave 2, after Tommy confirmed a
revised spec. Its artifacts are archived at `.agent-work/archive/2026-08-07-epic-418-waves-0-1/`.
What carries forward, and must not be re-derived:

| Fact | Source |
|---|---|
| Wave 0 (#419 #420 #422 #425) and wave 1 (#440 #447) merged and closed | predecessor STATE_NOTE, verified against the tracker |
| Spec of record is the REVISED_SPEC, CONFIRMED 2026-08-07 | `verify_spec_confirmed.py` exits 0 on `--phase review` and `--phase confirm` |
| Execution order: B extended → A2 → F → C → E; A-remainder and D-debt off-chain | REVISED_SPEC |
| `python -m pytest`, never `py`; `FORCE_COLOR=` and `NO_COLOR=1` or you get false reds | #454, fixed; `_COMMON.md` |
| Spine rail misattributes a descendant's gate to its ancestor — never obey a rail naming another spine | #457, live defect, 10 firings last session |

## Rulings & events

- `2026-08-07` — `RULING`: **Relaunch as `epic-418-redux` rather than resuming the predecessor spine.**
  Tommy's instruction was to archive the prior work and start fresh, and the predecessor's latitude
  contract had already expired by its own terms (expiry: the wave-1 checkpoint, which passed). A
  fresh spine plus a fresh contract is the honest state, and it is what the expiry clause demands.
  Decision class: out-of-taxonomy under the expired contract, resolved by the human's direct
  instruction in session.

- `2026-08-07` — `ADMIRAL ERROR` (caught before it cost anything): **the installed Admiral skill is
  stale against this repo, and I loaded the stale copy.** `Skill(constellation-admiral)` served
  `C:/Users/fredc/.claude/skills/constellation-admiral/`, which diverges from the repo's own
  `skills/admiral/` in two load-bearing places:
  1. `execute` — the repo's version carries the **iterative replan** loop (`NEXT_WAVE.json`,
     `transitions/<boundary-id>/` REPLAN_INPUT/RESULT packets, `TRANSITION` log lines, and a
     blocking `verify_iterative_role_artifacts.py admiral-prelaunch` check before any launch).
     The installed copy has none of it.
  2. `closeout` — the repo replaced the LESSONS-inbox model with **episodes**
     (`apply_episode_delta.py`, `verify_episode_captured.py`). The installed copy still runs the
     lessons auditor and `verify_agent_feedback.py`.

  This is the exact hazard `checklist-engine.md` warns about under dogfooding: nothing in the
  Skill-tool invocation flags which copy governs. **Fix applied:** the spine was instantiated from
  the repo's `skills/admiral/templates/ADMIRAL_SPINE.template.json` with
  `--skill-dir C:/Programs/constellation-skills`, so every check command resolves to the repo's
  vendored `scripts/`. Verified: the spine's three command checks point at
  `C:/Programs/constellation-skills/scripts/`. **Open risk carried:** Commanders I dispatch will
  load the *installed* crew skills, which may be stale the same way. Resolved before wave 1 — see
  the install-sync entry below.

- `2026-08-07` — `RULING`: **staleness quantified before asking Tommy to act on it** — I had one
  example and a recommendation resting on it, which is not evidence. Enumerated by command
  (`diff -q` per skill, repo `skills/<n>/` vs `~/.claude/skills/constellation-<n>/`): **12 skills
  diverge**, 6 of them in `SKILL.md` itself — `admiral`, `commander-delegated`, `docent`,
  `explorer`, `workbench`, `write-a-skill` — plus template drift in `cartographer`, `charter`,
  `commander`, `interrogator`, `reviewer`, and a script diff in `replan`. The load-bearing one for
  this run is **`commander-delegated`**: that is the skill every Commander I dispatch will load, and
  `workbench` carries the engine reference and spine templates underneath all of them. This turns
  decision 1 from a tidiness question into a correctness one. Decision class: out-of-taxonomy
  (mutates the human's global skills directory) — surfaced, not self-ruled.

- `2026-08-07` — `ESCALATION`: **latitude gate blocked on Tommy's confirmation** (engine: `latitude ->
  blocked`, bubbled to parent). Postcondition c2 is a `user-decision` artifact and cannot be
  self-satisfied; waiving it would be me deciding for the human, which is the one thing the bookend
  exists to prevent. Draft contract written; five decisions put to him in session:
  1. Re-run `install_constellation.py` to sync the stale installed corpus before wave 1? (recommended yes)
  2. Wave 1 shape — #433 + #460 as Commanders, #461/#464/#465 as implementers, #436 optionally riding along
  3. Run-ahead checkpoints vs stop-and-wait at each wave boundary (recommended run-ahead)
  4. Expiry — wave-2 boundary or 72h (recommended)
  5. Close #447 with evidence, and correct #418's stale spec pointer — both `surfaced` by class

- `2026-08-07` — `RULING`: **predecessor archived, revised spec carried forward rather than archived.**
  The spec is the live plan, so `spec-revision/` moved to `.agent-work/epic-418-redux/`; everything else
  from the `epic-418` run went to `.agent-work/archive/2026-08-07-epic-418-waves-0-1/`. Epic #418's body
  still points at the old spec path, so a breadcrumb sits at `.agent-work/epic-418/README.md` until the
  tracker pointer is corrected (queued as decision 5 — tracker edits wait for the contract).

- `2026-08-07` — `RULING`: **green-main baseline established for the wave, pinned to its revision.**
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` at `ca0e36a` (= `origin/main`, tree clean of
  source changes): **1721 passed, 4 skipped, 643 subtests, exit 0**, 309s. Real exit code captured,
  not inferred from the summary line.

  Recorded as a **discrepancy, not reconciled**: the predecessor's own STATE_NOTE carries two
  different figures — "1723 passed, 2 skipped" as the wave-1 green, and "main green at 1764 passed"
  for the #440 merge. Neither matches this run's 1721/4 (same total of 1725 collected as the first;
  two tests moved passed → skipped). I am not re-deriving where their numbers came from — the
  baseline any wave-1 PR is judged against is **this** one, at this SHA. Skips are environment-
  conditional, which is the likely cause and is cheap to confirm if a wave-1 review ever leans on it.

- `2026-08-07` — `ADMIRAL ERROR`: I deleted the `
- `2026-08-07` — **PR #472 merged** (`7bc3f8c2`), squash. #436's enumeration falsification, replanted
  onto current main after the squash orphaned its base. Gated on the check exit code (0 non-SUCCESS)
  and verified at the forge (`state=MERGED`). #469 closed as superseded, with a comment making clear
  it was my squash and not their work.

  **What #436 actually proved**, which is the point of the issue: it introduced a genuinely new
  second worktree-entering entry and observed the check **refuse** — `1 of 2 worktree-entering
  template(s) checked failed`, exit 1 — then reverted it. The discrimination logic needed no fix,
  which is an **honest null on the "does it work" question**, and the debt is closed by evidence
  rather than argued closed. It also found and fixed one real gap test-first: the failure path
  listed offenders without stating what it had enumerated. *A guard that loops must assert what it
  looped over* — that is the doctrine, and the check was violating it on its own failure path.

- `2026-08-07` — `RULING`: **the squash-orphan now costs a replant per wave-2 PR, and that cost is
  mine.** #471 (#464) is CONFLICTING for the same reason #469 was. The replant recipe is written
  into the STATE_NOTE so it is mechanical rather than rediscovered. No commander is asked to redo
  anything — their diffs are taken verbatim against their real base and replanted onto main.

  Root cause worth carrying to closeout as an episode: I cut four worktrees from a commit, then
  squash-merged a branch containing that commit. Squash-merge does not preserve the base, so every
  branch cut from it is orphaned at once. The cheaper order was to merge the fix first and cut the
  worktrees from the result.


- `2026-08-07` — **PR #473 merged** (`0b4a11a7`), squash. #464's `Lesson` → `Episode` rename,
  replanted onto main after the same squash-orphan. Gated on check exit code (0 non-SUCCESS),
  verified MERGED at the forge. #471 closed as superseded with the reason stated.

  Two deliberate non-changes in it are the interesting part, and both are right: the collector keeps
  a fallback to the `lesson` key because **other repos' exported files literally say "Lesson"** and
  we cannot rename another project's file content; and the internal hash prefix stays the literal
  string `lesson:` because it is an **opaque identity tag, not a display label** — renaming it would
  orphan every fingerprint already recorded and cause duplicate re-filing. The implementer found
  both before touching anything, and did the enumeration by command rather than memory.

  **Flagged on the PR, not fixed:** the template's line 3 still opens "Lessons scoped
  `constellation` …". It predates the change and reads as ordinary English, but the standing
  post-#447 rule is no lesson-vocabulary revival, and that is exactly the kind of line that keeps
  the old frame alive quietly. Out of the issue's scope, so it is a flag rather than a silent fix.

- `2026-08-07` — `RULING`: **#436 and #464 are NOT closed on the tracker, deliberately.** Their work
  is merged, but **issue closing is a `surfaced` class** in this contract and Tommy has not been
  asked. They are queued for the next checkpoint with their evidence rather than closed on my own
  authority. Merging is delegated; closing is not, and the two are easy to conflate once the PR is in.


- `2026-08-07` — `INCIDENT`: **second HARD trip for both #433 and #460, this time at the `execute`
  gate** (18% and 17% fill). Third dispatch each. Distinct from the first round in one way that
  matters: **neither filed its refresh-request before stopping**, so `current` showed the DIGEST with
  no `REFRESH REQUESTED:` line — which is the signature of a *crash*, not a governed handoff. The
  recovery is identical either way (fresh agent, same worktree, same spine), but the diagnosis cost
  me a round-trip, so the third-dispatch orders now say to file the request *first*, then stop.

  Neither had lost work: #433 carried 3 commits, #460 carried 4 plus a completed reviewer/rework
  cycle. The relaunch orders carry each one's settled findings forward explicitly and tell both to
  **prioritise shipping over polishing** — a third dispatch that keeps refining is a fourth dispatch.

  **Running cost of the trip band, measured rather than estimated: 3 dispatches per Commander-sized
  issue.** #436 and #464 (implementer-sized, Sonnet) needed 2 and 1. This is the single largest
  drag on the wave, and it is a governor-tuning question for Tommy — not something I retune mid-wave.

- `2026-08-07` — `RULING`: **third-dispatch orders instruct Commanders to open their PR even though
  it will report CONFLICTING.** The squash-orphan is mine, the replant is mechanical and proven
  twice, and a Commander that stops to rebase would burn its remaining context on my mistake. So the
  order states the conflict is expected, tells them not to rebase, and takes the replant onto me.


- `2026-08-07` — **PR #485 merged** (`538d5fd7`), squash. **#433 is done — the wave's chain head.**
  Replant of #483; gated on check exit code (0 non-SUCCESS), verified MERGED at the forge.

  What it actually shipped, and why the Opus tier was right: the naive fix — un-excluding
  `directives` from the existing `TaskFieldCompleteness` property — **would have been a check that
  cannot fail**, because `_flatten` returns `[]` for the nested-dict shape every populated block in
  the corpus carries. It would have reported clean while rendering nothing. The inventory that
  settled render-vs-delete was an **enumeration, not an assumption**: 2955 gates scanned, 8 populated
  `directives` blocks found. And the golden asserts against the **shipped** Commander spine's execute
  gate rather than a synthetic fixture, so it fails if the real template stops carrying the field.

  Epic done-condition 2 — "`current` carries each instruction exactly once and renders every
  populated gate block" — moves from *not met* to substantially met with this.

- `2026-08-07` — `INCIDENT`: **#460 tripped a THIRD time** (21%, `execute` gate again). Fourth
  dispatch. 9 commits and a completed reviewer/rework cycle already banked. Its fourth order strips
  the mission to one instruction — **finish and open the PR** — and explicitly rules that a partial
  rewrite with an honest count of what was and was not done is a **complete deliverable**, while a
  fifth dispatch is not. That is the honest-null clause applied to effort rather than to a result.

- `2026-08-07` — `RULING`: **#433's three new episode records are not a fence violation.** Its PR
  writes `episodes/active/b433-render-directives-00{1,2,3}.md` — its own closeout records under its
  own work-id prefix — while #460 is rewriting the existing canon records. New files, distinct names,
  no overlap. Flagged to #460 so any guard it ships tolerates them, but not treated as a collision
  and not held against either commander. The fence was written to stop two writers editing the same
  records, and that did not happen.


- `2026-08-07` — **PR #487 merged** (`476e044d`), squash. **#460 done — WAVE 2 IS COMPLETE.**
  Gated on check exit code (0 non-SUCCESS), verified MERGED at the forge.

  This is the wave's best result and it earned its four dispatches. The guard it ships was
  **observed failing**, not merely observed passing: on its first live run against merged main it
  caught **four real offenders** — the three episode records #433 had added after this branch was
  cut, whose statements read *"Do the gate work…"*, *"Pair every negation postcondition…"*, *"State
  doc postconditions as…"*. Those are prescriptions, in the store that exists to hold observations.

  **I ruled against the cheap fix.** The guard carries an exception list for records that predate
  it, and adding these four would have turned CI green in one line. I sent it back to the Commander
  to **restate** them instead: the list is for what predates the guard, and grandfathering records
  written *during the same wave* is precisely the erosion this issue exists to stop. Final scan:
  274 statements examined, 11 excepted, **0 unlisted offenders**.

  It also closes the gap I left open when I closed #447 with its fourth done-condition marked
  PARTIAL. That partial is now paid.

- `2026-08-07` — `RULING`: **#461 confirmed first-hand during the merge, and left open.** The
  replant's full suite failed on `test_canon_episode_store_untouched` — the negative control asserts
  `git status --porcelain episodes/` is empty, so it fails for any run that legitimately changes the
  store **between `git add` and `git commit`**. Committing made it pass. That is exactly what #461
  reports, reproduced by accident rather than by design. Recorded as evidence on the issue; **not
  fixed here** — #461 is held to the wave's second half and fixing it in passing would have been
  scope I was not given.

- `2026-08-07` — `WAVE`: **wave 2 "B extended" COMPLETE.** #433, #436, #460, #464 all merged; no open
  PRs. Cost, measured rather than estimated: **4 issues, 10 Commander/implementer dispatches, 5
  replants, 1 self-inflicted CI outage.** The trip band accounts for 6 of the 10 dispatches and the
  squash-orphan for all 5 replants — both of those are mine or the governor's, not the crews'.


- `2026-08-07` — `RULING`: **green main verified once on the final merged tree, not per PR.** The
  sanctioned batched pattern: `476e044d` → **1782 passed, 2 skipped, 683 subtests, exit 0** (353s,
  real exit code). Against the corrected `1723/2` baseline that is **+59 tests** from the wave, with
  skips unchanged at 2.

- `2026-08-07` — `ESCALATION`: **the latitude contract has EXPIRED by its own terms and I am
  stopping.** Its expiry clause reads *"the wave-2 boundary (after the B-extended wave's PRs merge),
  or 72 hours, whichever comes first"*, and wave 2's PRs are now all merged. The contract's own words
  are that crossing it **forces a contract-refresh decision before further dispatch**.

  So I am not launching wave 3, and I have deliberately **not** written the `w2-to-w3` replan packet
  either — its content is a question for Tommy (what the next wave should be), and authoring it now
  would be me answering a question the expiry just handed to him. The engine gate is blocked on this
  rather than left open, so the state is honest rather than merely paused.

  Everything is merged, pushed, and green. Nothing is in flight; no worktree holds unmerged work.


- `2026-08-07` — `INCIDENT`: **#457 fired on me, and I refused it.** After blocking my own `execute`
  gate on the contract expiry, the stop rail ordered me to work an `execute` gate whose lease was
  **`commander-r418-460-b`** and whose work-id was **`r418-460`** — the #460 Commander's spine, which
  lives inside that Commander's worktree, not mine. The imperative it handed me was a Commander's
  (drive `execute.json` gate by gate, dispatch crew via `run_crew.py`).

  Verified before deciding, rather than reasoning about it: my own spine
  (`.agent-work/epic-418-redux/spine.json`) reports `LEASE admiral-epic-418-redux` and
  `ACTIVE execute [blocked]`, `next: resume execute`. Exactly where I left it. The rail was
  describing someone else's spine.

  **Obeying it would have meant a second agent driving a live-leased spine** — the thing the epic
  forbids outright. The predecessor run recorded ten firings of this and warned that the
  three-strike escape hatch cannot save you, because `spine_rail.py:897` resets the counter on the
  *watched* spine's progress: the better a descendant works, the more relentlessly its ancestor is
  nudged. This firing is consistent with that and adds a detail worth having — it fired **after** the
  descendant's work was fully merged and its Commander was gone, so a dead descendant's stale spine
  still captures its ancestor's rail. Evidence added to #457.


- `2026-08-07` — `RULING`: **wave-2 worktrees harvested and swept; the #457 capture surface removed
  at its source.** Harvest first, then remove, per the mandated order. Result: **nothing to harvest**
  — each worktree's `CONSTELLATION_FEEDBACK.md` was *behind* main rather than ahead (they carried the
  pre-#464 `Lesson:` wording, main has `Episode:`), and no new `staged-feedback/<work-id>/` dirs
  existed for this epic. Verified by diff before deleting anything, not assumed.

  `r418-433`, `r418-436`, `r418-460`, `r418-464` removed and pruned. Before removing `r418-460` I
  **released its orphaned lease** (`commander-r418-460-b`) — its Commander had finished and exited
  without releasing, leaving an `execute [in-progress]` gate with a live lease. That orphan was what
  captured my rail.

  **The survey turned the #457 diagnosis into something more useful than "descendants capture
  ancestors".** Every remaining spine in the tree was checked: the six predecessor epic-418
  worktrees had all **released** cleanly, but `governor-264` still holds a **live lease with a
  heartbeat from 2026-07-28** — over ten days stale, gate still `in-progress`, from an abandoned
  Commander on an unrelated issue. So the capture surface is *any* orphaned in-progress spine with an
  unreleased lease, and those accumulate precisely because nobody is left to release them. Left
  `governor-264` alone — it is outside this epic — and filed the analysis on #457 with the two places
  the evidence points (stale-lease ineligibility; refusing to name a spine the caller does not own).

## Merges` heading while appending the baseline
  ruling — my replacement text dropped the heading it was anchored on. Caught when the next edit
  could not find it. No data lost (the section was empty); heading restored below. Cost: one
  round-trip. The lesson is the ordinary one about anchored edits, not worth doctrine.

- `2026-08-07` — `RULING`: **install corpus synced before dispatch, under Tommy's pre-clearance.**
  `install_constellation.py --agent claude --scope user --force`, exit 0, repo left clean.
  Verified after, not assumed: the two that gate dispatch (`commander-delegated` SKILL.md,
  `workbench` templates) are byte-identical to the repo. Seven paths still differ, and all seven
  are the installer's own transformations — absolute-path resolution of `<skill-dir>` tokens and a
  `python` → `py` launcher rewrite. Confirmed benign by normalizing both and diffing: **zero
  non-launcher differences**, and `py` resolves to Python 3.12.13 and runs corpus scripts fine.
  I did **not** pass `--wire-hooks`: the installer reports the Context Governor hook UNWIRED, which
  is #458's own deliverable, and `settings.json` is out of bounds by the spec.

- `2026-08-07` — `RULING`: **#447 closed with a per-done-condition accounting** (surfaced class,
  authorized by Tommy). Conditions 1–3 MET with evidence at the tree; **condition 4 stated as
  PARTIALLY met** — the read path is retired but #460 shows the obligation leaking back at the
  authoring end. Closing anyway is defensible only because the remainder is tracked and *scheduled*
  (#460 heads this wave), which is exactly what #308 lacked. Had I written "done" over condition 4
  I would have reproduced the failure #447 was filed to catch.

- `2026-08-07` — `RULING`: **epic #418's body pointer corrected** to
  `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`, plus a relaunch status note.
  Verified at source: 1 occurrence of the new path, 0 of the old. My first attempt failed on a
  cp1252 decode of `gh`'s output and wrote nothing — no partial edit landed; re-run with explicit
  UTF-8 decoding.

- `2026-08-07` — `TRANSITION`: boundary `w1-to-w2`, decision **replan**, applicable. Wave 1 exit
  criteria met and nothing left open, so the wave was re-cut rather than advanced as forecast. Five
  discrepancies dispositioned: D1–D3 evidence-only (install staleness resolved, #447 closed, test
  baseline recorded-not-reconciled), **D4 revise_plan** — #460 pulled into the current wave rather
  than left to E, because every wave that runs meanwhile writes more records into the store — and
  D5 amend-forecast (#458 stays off-chain). Packets at `transitions/w1-to-w2/`.

- TRANSITION | boundary=w1-to-w2 | decision=replan | verified

- `2026-08-08` — `ADMIRAL ERROR`: **I reported releasing `r418-460`'s orphaned lease. I did not,
  and it could not have worked.** `.agent-work/r418-460/spine.json` in the main checkout still reads
  `LEASE active: commander-r418-460-b` / `execute [in-progress]`. I released the copy under the
  *worktree* and then swept the worktree; the copy in main is a **different file that arrived via
  the merge of PR #487** (`git log -- .agent-work/r418-460/spine.json` → exactly one commit,
  `476e044d`). My release never addressed it. Cost: nothing operationally — but I stated a
  remediation as done in both the state note and my checkpoint report to Tommy, and it was not.
  Both corrected in place. The reason I believed it is worth naming: I verified the *action*
  (release exited 0) instead of re-running the *observation* that had prompted it. Re-reading the
  spine after the sweep would have shown the lease still active in one command.

- `2026-08-08` — `RULING` (evidence-only; supersedes my own earlier #457 comment): **the lease field
  read from disk is not a liveness signal, in either direction.** Enumerated by command, not memory:
  of 147 tracked plan/spine files, **18 carry `engine_session.status == "active"` and exactly one is
  a live run** — mine. Fifteen are deliberate records (`/archive/`, `/harvest/`, eval corpora under
  `epic-298/{post,preb}/runs/`); three sit in live work areas and two of those three are fossils.
  A Commander that commits its own spine to its PR branch ships a mid-run snapshot into main on
  merge — `r418-460`'s is frozen 90 seconds into a multi-hour run — and git then preserves an active
  lease and an `in-progress` gate forever. This **compounds with cmd-460's finding from the other
  direction**: it read `lease: null`, concluded the run was abandoned, and raced a live Commander
  (its own `770f3e06` landed 44s behind the real work), because a crew that releases between gates
  produces exactly that reading. So `null` does not mean dead and `active` does not mean alive. Same
  family as **a check that cannot fail**: the signal's value is identical in both worlds. My earlier
  #457 comment blamed abandoned agents leaving leases behind — that is a symptom; the defect is that
  liveness was never encoded, only a snapshot of it. **What does discriminate, and needs no fix:**
  match the lease's `session_id` against your own — presence proves nothing, ownership proves
  everything. That is what let me refuse #457's rail twice. **Not filed as an issue:** filing is a
  delegated class and the contract granting it expired at the wave-2 boundary. Surfaced to Tommy.

## Merges

Logged chronologically above, not here — see the `2026-08-07` entries for #470, #472/#469, #473,
#485, #487. All five gated on check exit code and verified `state=MERGED` at the forge.

## Closeout

- _pending_

- `2026-08-08` — `RULING` (correction of my own checkpoint report): **#470's independent review did
  land, after the merge, and both reviewers approved.** I told Tommy the review never landed. True
  at the time; superseded now. Two reviewers returned `APPROVE`, each having re-derived the result
  by running it rather than reading it — glob resolution executed, corrupted-fixture controls
  confirmed to raise `SpecVerificationError`, full suite re-run in an isolated worktree pinned to
  the PR's exact commit (one reviewer caught that its own first run was invalidated when another
  agent switched HEAD mid-run in the shared checkout, and redid it — the kind of self-catch that
  makes the verdict worth more than the merge it arrived after). **Neither posted to the forge**:
  `gh pr view 470 --json reviews` and `--json comments` are both empty, so these verdicts exist only
  as session messages and would be invisible to anyone reading the PR. Worth its own fix; not filed
  (delegated class, contract expired). **Both independently flagged the same non-blocking gap** —
  `matches[0]` at `tests/test_verify_spec_confirmed.py:252` silently picks the alphabetically-first
  match with no signal a second existed. One match exists today, so the test is not vacuous. Left
  unfixed: it is a change to main under an expired contract. One line.

- `2026-08-08` — `RULING` (evidence-only): **one defect family accounted for three of this wave's
  findings**, discovered independently in three subsystems by three different agents — (a) #433,
  where the naive fix would have been a check that cannot fail; (b) the engine lease, which
  indicates liveness in neither direction; (c) `matches[0]`, which cannot signal ambiguity. The
  shared shape: a signal whose value is identical in the healthy and the defective world. This is
  what #418 is fundamentally about, and it is a candidate organizing theme for wave 3 rather than a
  ruling I can make — wave composition is delegated, but the contract granting it has expired.

- `2026-08-08` — `RULING`: **#460's 22 doctrine candidates verified present in main**, at
  `.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4" (60KB, harvested).
  I swept that worktree, so I checked rather than assumed: they survived because #487's merge
  carried them in — the same mechanism that stranded the fossil lease preserved the deliverable.
  The mission's hard boundary held: nothing in `docs/agents/*`, no file created to park them in.

- `2026-08-08` — `RULING` (evidence-only; a new defect, and a correction of my own first guess):
  **the Admiral's context governor goes dark for the rest of any run that does its latitude bookend
  properly.** I first assumed the `r418-460` fossil lease was capturing the gauge binding. Wrong —
  I checked instead of asserting. The binding registry (`.agent-work/.spine-rail-binding.json`) has
  my session key bound to **two** checklists, both mine and both legitimate:
  `epic-418-redux/spine.json` and `epic-418-redux/latitude-interrogation.json` — the Interrogator
  survey the spine's `latitude` step *requires* me to drive.
  **Both resolve to the identical gauge path** `.agent-work/epic-418-redux/gauge.json`. But
  `resolve_gauge_path` (`scripts/hooks/gauge_writer_hook.py:257-264`) appends one candidate per
  binding **without dedup**, and the caller treats `2+ candidates` as ambiguous and writes nothing.
  So the count is of *bindings*, not of *distinct gauge paths*.
  The skip's own rationale (`:530-541`, #261) is about misattribution — "two genuinely different
  top-level agents share one session_id... cannot tell whose activity produced the latest usage
  record." That rationale is **vacuous when both candidates are the same file**: there is no
  whose-reading-is-it question when either answer writes to one place.
  Measured consequence: my last real reading is `2026-08-07T20:58:07Z`; `gauge-skip.json` says
  `{"reason":"ambiguous-binding","candidate_count":2}`, refreshed live at 02:49:41Z. I have run this
  entire wave — every dispatch, merge, and adjudication — with **no governor coverage at all**,
  while simultaneously reporting the governor's trip band as the wave's largest drag on my crews.
  Exact onset not pinned (the survey file predates the last successful write by ~40m, so the second
  binding registered later); the mechanism is proven regardless.
  **Fourth instance of this wave's defect family**, and the sharpest: a guard that cannot distinguish
  "two different agents" from "one agent counted twice" is a check whose value is identical in the
  healthy and defective worlds. Likely one line (`len(set(candidates))`), but it is a change to main
  under an expired contract. Not filed, not fixed. Surfaced.

- `2026-08-08` — `CONTRACT REFRESH` (blocker cleared; Tommy in session): the expired latitude
  contract is refreshed as **Addendum R1**. Verbatim: *"you can keep running, you're compacted.
  close the complete issues, and get on into wave 3. 461 & 465 is good"*.
  Three deltas: issue closing becomes **delegated for #433/#436/#460/#464 only**; **wave 3 = #461 +
  #465**, no additions; new expiry at the **wave-3 boundary or 72h**.
  **What he did NOT rule on, and what I am therefore NOT doing:** the governor trip band, and the
  three one-line fixes from wave 2's findings. I offered the defect-family theme as an alternative
  wave-3 shape; he named the two held issues instead. That is an answer, so the theme stays a
  candidate. Widening wave 3 to carry those fixes would be me converting a scoped instruction into
  a mandate — they go back to him at the wave-3 checkpoint.

- `2026-08-08` — `RULING` (contract amendment, Tommy in session, minutes after the refresh above):
  **wave 3 widens to #461 + #465 + #488 + #489.** Verbatim: *"woah, feel free to add easy or useful
  fixes to wave 3. id rather not clutter the issue board or delay fixes that are easy to just knock
  out now"*.
  This reverses my own hold. I had just filed #488 (gauge writer counts bindings, not distinct
  paths) and #489 (`matches[0]` cannot signal a second match) as findings, deliberately deferred on
  the reading that Tommy's wave-3 scope named two issues and I should not widen it. He corrected the
  reading: filing a cheap fix instead of doing it is the thing he does not want.
  **The standing preference to carry forward: a genuinely cheap fix gets done now, not filed and
  deferred.** The board is for what needs deciding, not for what needs typing.
  **Not folded in, deliberately:** #457's lease-liveness defect. It is the third wave-2 finding and
  the amendment says *easy* — this one is not. Both readings of the field are uninformative, so
  fixing it means deciding how liveness is encoded at all, which ends at a load-bearing interface.
  Evidence posted to #457; it stays a design question.
  Also still surfaced: the governor trip band, a production default and a threshold question.

- `2026-08-08` — `RULING` (dispatch shape, delegated: wave composition + model tier):
  three parallel dispatches, not four, chosen against file overlap — verified disjoint:
  | Dispatch | Issue(s) | Shape | Tier | Touches |
  |---|---|---|---|---|
  | W3-A | #465 | full Commander | Opus | reviewer template, `checklist_engine.py`, reviewer SKILL.md |
  | W3-B | #461 | implementer-with-plan | Sonnet | `tests/test_episode_negative_control.py` |
  | W3-C | #488 + #489 | implementer-with-plan | Sonnet | `scripts/hooks/gauge_writer_hook.py`, `tests/test_verify_spec_confirmed.py` |
  **Departure from the contract's model table, logged as the table requires:** it lists #465 as an
  implementer/Sonnet carried finding. I am raising it to a full Commander on Opus because the issue
  contains a genuine design choice with two valid answers (remove the shipped placeholder, or add an
  engine verb that fills it and name that verb in the imperative), plus a doctrine contradiction to
  settle in the same pass (`SKILL.md` says an open fail cannot consolidate to APPROVE; the engine
  ships `--override-reason` for exactly that). That is not implementer work.
  W3-C bundles two issues into one dispatch because both are one-line guard hardenings of the same
  defect family in non-overlapping files — cheaper as one crew than two.
  **Budget: two dispatches per issue** — every wave-2 agent tripped the governor at the plan seam.
- TRANSITION | boundary=w2-to-w3 | decision=replan | verified

- `2026-08-08` — `WAVE LAUNCH` — **wave 3, three dispatches, four issues.** Boundary `w2-to-w3`
  recorded, `decision=replan`, `verify_iterative_role_artifacts.py admiral-prelaunch` **exit 0**
  (installed copy, per #468). Isolation gate on all three worktrees: exit 0, "3 distinct worktrees".
  | Dispatch | Issue(s) | Worktree | Tier | Owns |
  |---|---|---|---|---|
  | W3-A | #465 | `C:/Programs/wt-w3a-465` | Opus, full Commander | reviewer skill + `checklist_engine.py` |
  | W3-B | #461 | `C:/Programs/wt-w3b-461` | Sonnet, implementer | `tests/test_episode_negative_control.py` |
  | W3-C | #488 + #489 | `C:/Programs/wt-w3c-488-489` | Sonnet, implementer | `gauge_writer_hook.py`, `tests/test_verify_spec_confirmed.py` |
  Fences verified disjoint before launch, not asserted.
  **One instruction is in all three orders and it is wave 2's lesson turned into a method: build the
  defective world and observe the current code getting it wrong BEFORE fixing.** For all four issues
  green is what the broken version already does, so green alone is not evidence. Each order names the
  specific defective world to construct and demands the before-state pasted.
  **The verifier refused this boundary four times before passing** — an out-of-plan `blocks` target;
  string `completed_outcomes` where objects are required; #470 in completed outcomes when it was never
  a wave-2 issue (caught by the exact-partition rule); string `material_changes`. All four were my
  shape errors, all recorded in the state note so the next boundary costs one attempt instead of five.
  **Also caught: I captured `tail`'s exit code instead of the verifier's** on the first run and read a
  refusal as `VERIFY_EXIT=0`. Same defect as the wave-2 push. Redone with output to a file.

- `2026-08-08` — `RULING` (evidence-only, found while surveying stale worktrees for closeout; **not
  acted on, deliberately**): **there is finished, unmerged work on this wave's exact theme sitting in
  a worktree, and its issue is still open.**
  Branch `governor/264-e2e-assertion`, worktree `C:/Programs/constellation-skills-wt/governor-264`,
  **3 commits, 211 behind main, absent from main** (`git ls-files | grep gauge_chain` returns
  nothing). Issue **#264 is OPEN**: *"governor: no end-to-end assertion that a live run produces a
  sane reading — 8 days of 1.0s raised nothing"*.
  It is **1144 lines** of end-to-end gauge test, 13 tests, traversing a real writer process to a real
  Trip verdict. Two of them matter to us right now:
  - `test_ladder_fill_series_is_non_decreasing_and_actually_moves` — the anti-vacuity assertion for
    *"8 days of 1.0s raised nothing"*. **This is the guard that would have caught my dark governor**,
    and it has existed, written and unmerged, the whole time I ran blind.
  - `test_chain_ambiguous_binding_writes_no_gauge_and_flags_every_candidate` — which at first read
    looked like it would **lock in the #488 defect**, since it asserts an ambiguous binding writes no
    gauge. **It does not.** I checked rather than assumed: it builds `_ambiguous_work_trees(tmp_path)`
    and asserts `not (spine.parent / "gauge.json").exists()` **per spine**, so its candidates have
    *distinct parents*. That is exactly the **negative direction #488's fix must preserve** —
    genuinely different paths still skip — specified independently, months before #488 was found.
    So it corroborates W3-C's mission instead of contradicting it.
  **Not acted on, three reasons.** (1) Landing it is a **scope change**, which the contract marks
  `surfaced`. (2) It would shift ground under a running Commander — W3-C owns
  `gauge_writer_hook.py` right now, and doctrine is stop-and-relaunch on fresh ground, never steer
  mid-flight. (3) 211 commits behind: whether it still runs is an open question, not an assumption.
  **Surfaced to Tommy at the wave-3 boundary**, with a recommendation to land it.
  Sweeping that worktree would have destroyed it. This is the harvest-before-sweep rule earning its
  place: the survey was routine closeout hygiene and it turned up the wave's most useful artifact.

- `2026-08-08` — `ADMIRAL ERROR` (caught, corrected, verified): posting the #264 comment, I passed the
  body as a **double-quoted bash string containing a markdown code span**. Bash executed the
  backticked contents as **command substitution**: `len(set(candidates))` became a syntax error and
  the phrase was **silently deleted from the posted comment**, which still posted successfully.
  Exit status was fine. The forge accepted it. Only re-reading the posted body found it.
  Corrected via `gh api -X PATCH ... -F body=@<file>` and **verified by re-reading the comment**, not
  by trusting the PATCH's exit code — the same discipline whose absence produced the false
  lease-release claim earlier in this run.
  **This is a platform hazard, not a one-off.** Every launch order already carries *"PR bodies via
  `gh pr create -F <file>`, never a heredoc or here-string"*. This is the same trap one door over:
  **`gh issue comment --body "..."` with any backtick in it**. Markdown code spans are exactly what
  a well-written comment is full of, so the hazard fires on good writing.
  It also has the wave's signature shape: **the failure is invisible at the point of failure.**
  Non-zero exit went to stderr while the comment posted anyway, so every success signal said success.
  Carried as a triage candidate for closeout; the fix is to extend the existing `-F <file>` rule to
  cover issue comments, not just PR bodies.

- `2026-08-08` — `RULING` (closeout substep executed early, delegated: repo hygiene): **harvest before
  sweep, done — and it was not a formality.** Four files in the predecessor run's stale worktrees
  exist **nowhere in the git object store**, and `git worktree remove` would have destroyed them:
  `RETURN.md` from `b-420` (10 KB), `d-422` (10 KB) and `g-425` (7.5 KB), plus **`h-447`'s 261 KB
  `AGENT_FEEDBACK.md`**. Collected to `.agent-work/harvest-418-redux/`, verified byte-identical with
  `cmp`.
  **How they were identified, and why filename survey would have been wrong.** I did not judge by
  name or by `git status` alone. For each candidate: `h=$(git hash-object <file>); git cat-file -e
  "$h"` — a non-zero exit means that exact content exists in no commit, on no branch, anywhere.
  That check **spared one file**: `h-447/.agent-work/LESSONS.md` looked identical in kind to its
  sibling and is **already in git**, so it was deliberately not copied. Five candidates by name, four
  genuinely at risk. The name-based survey would have been a check that cannot fail — it returns
  "at risk" for saved and unsaved content alike.
  **The one worth pausing on:** `h-447` is the workstream that *retired* `AGENT_FEEDBACK.md`. Its own
  run wrote a 261 KB retrospective into the very file it was deleting — worktree-local, untracked,
  under the epic lease that makes `durable_root()` return the worktree rather than the main checkout.
  The retirement landed; its own record came within one `git worktree remove` of not existing.
  **Disposition deliberately NOT settled.** These are pre-retirement formats and `episodes/` is the
  store now. Whether they convert to episodes or are dropped with a reason is the lessons audit's
  call at closeout. Collecting is reversible; deciding is not, and the sweep was the only clock.
  **Nothing swept.** `governor-264` is untouched and flagged DO NOT SWEEP.

- `2026-08-08` — `ADMIRAL ERROR` + `RULING` (correction to my own framing, and a material correction
  to something I have been surfacing to Tommy):
  **1. I filed #488 as a fresh discovery. The symptom was already recorded.** The revised spec's
  critic finding **F2**, dated 2026-08-07, says: *"multi-spine attribution silences it for exactly the
  role that runs epics (this epic's Admiral ran a full day with the gauge silent)."* Written down
  before I hit it. What was genuinely new is the **mechanism** — binding count vs distinct-path count.
  I should have read the spec's own findings before claiming novelty; the epic had already seen this.
  **2. The spec also already carries the accepted fix for the whole class**, in finding **F8**, whose
  ruling calls it *"the purest check-that-cannot-fail in the document"*: **no absence is evidence —
  assert a reading EXISTS before any claim about trip behaviour**, because a silent governor and a
  governor with headroom are otherwise indistinguishable. That is precisely what #264's unmerged
  `test_ladder_fill_series_is_non_decreasing_and_actually_moves` implements. **#264 is F8's
  implementation, already written, sitting unmerged.**
  **3. MATERIAL — the governor does not ship, and I have been asking Tommy to rule on a band measured
  from configuration that does not exist for anyone else.** Measured, not assumed: tracked
  `.claude/settings.json` wires `spine_rail.py` on `Stop`, `SessionStart` and `PostToolUse`, and wires
  `gauge_writer_hook.py` on **nothing**. `git ls-files .claude/` returns `settings.json` **only** —
  `settings.local.json` is untracked. So every governor observation this epic has made, including the
  17–21% trip band, came from **machine-local config**. The band question presumes the governor
  reaches ordinary sessions; on a fresh clone it reaches none of them.
  F2's accepted ruling already says what to do — *"wire gauge_writer_hook into the TRACKED project
  settings so the governor ships like spine_rail already does"* — and that is **#458**, off-chain.
  **Four parts, one thread:** #458 (ships at all) · #264 (asserts it is measuring — written, unmerged)
  · #488 (stops it silencing itself — in flight) · #452 (attribution proper). Three of the four are
  written or one-line. **Not acted on:** #458 is out of wave 3's scope and touching settings wiring
  mid-wave would shift ground under the crew editing that file. Surfaced at the boundary, and the
  trip-band question goes back to Tommy re-framed rather than as I first put it.

- `2026-08-08` — `RULING` (A2 preparation; **deliberately NOT a cut**): read A2's section to be ready
  when its turn comes. **Holding the cut**, because my own pre-ruling
  `decision:a2-cut-at-its-turn` says A2 is cut against *what B extended actually leaves behind*, and
  B extended does not complete until wave 3 merges. Cutting now would be cutting against a forecast.
  **Shape, for when the turn comes:** six done-conditions, not one issue. DC1-3 are the refusal→
  instruction conversion and #431's dissolution; DC4 is the per-gate override mechanism *exercised
  at least once*; DC6 is the compliance signal; DC5 is the full round trip (trip → handoff → refresh
  → resume, verified against what the tripped agent was mid-way through). DC5 and DC6 were both added
  by critics (F11, F33/F21) precisely because DC1-3 are satisfiable while the thing A2 exists for
  never happens. Provisionally **three issues**, with DC5 last because it tests the whole.
  **The finding that matters more than the cut — the defect family is the spec's own organizing
  concern, not a lens I noticed.** A2's DC6 states it as an explicit design cost, in the spec's own
  words: *"a refusal is self-enforcing and self-recording, while an instruction is satisfied or
  ignored with **identical traces**. Converting HARD from a refusal into a sentence removes the only
  mechanism that could register an agent ignoring it."* That is the family stated exactly — a signal
  whose value is identical in the healthy and defective worlds — and the spec pays for it deliberately
  rather than tripping over it.
  So the pattern now has **three independent sources** in this epic: the spec's F8 ruling (*"the
  purest check-that-cannot-fail in the document"*), A2's DC6 as a priced design cost, and wave 2's
  four field findings across four subsystems. It is not a theme I proposed and Tommy declined; it is
  the thing #418 has been about since the spec was written. **That changes what I recommend at the
  wave-3 boundary:** not "make the defect family a wave", but "the epic already has this as its
  spine — the governor thread (#458/#264/#488/#452) is the instance where three of four parts are
  already written." Recorded, not acted on.

- `2026-08-08` — `RULING` (delegated: wave mechanics): **pre-wrote the wave-3 review brief** at
  `.agent-work/epic-418-redux/launch-orders/REVIEW-BRIEF-w3.md`, to be instantiated per PR the moment
  a crew returns. Directly targets a wave-2 failure I own: **PR #470 was merged on self-verified
  evidence because no reviewer artifact had landed**, and the two reviewers who later returned APPROVE
  **posted to neither the PR nor the issue** — `gh pr view 470 --json reviews` is still empty. Good
  review, invisible forever.
  Three things the brief makes non-negotiable: (1) the reviewer **runs the new test against the
  unfixed code and confirms it goes red**, because for all four wave-3 issues green is what the
  broken version already does — accepting the crew's pasted evidence as proof of itself would ship a
  check that cannot fail *inside the fix for checks that cannot fail*; (2) the **negative direction**
  is verified, especially #488, where a fix that merely stops skipping is a regression no green run
  reveals; (3) the verdict is **posted to the forge with `-F <file>`**, both because a session-only
  verdict is what went wrong on #470 and because a backticked code span in a quoted `gh` argument is
  executed as command substitution and posts silently truncated — which happened to me on #264 today.

- `2026-08-08` — `RULING` (measurement started, and an independent corroboration of #488): **the wave-3
  crews' own gauges are writing, and mine is not — which is #488's mechanism observed from the other
  side.** W3-A and W3-C each hold exactly **one** binding and both produce readings; I hold **two**
  bindings that resolve to **one** path and produce none. Same hook, same machine, same session
  minute. That is the cleanest possible confirmation that the skip is triggered by binding *count*
  and not by any real ambiguity, and it arrived without my constructing anything.
  First live readings, 05:10Z: **W3-A (#465, Opus) 11.6%** · **W3-C (#488/#489, Sonnet) 15.5%**.
  W3-C is inside a whisker of the 17–21% band with five files dirty, so a trip before it commits is
  likely; I am positioned to relaunch rather than to discover it afterwards.
  **Now recording a series** to `.agent-work/epic-418-redux/evidence/w3-gauge-series.tsv`
  (`observed_at · dispatch · model · fill`, sampled each minute). Wave 2's trip-band evidence was
  four dispatch counts and no fill numbers at all, taken while the orchestrator was blind. This is
  the first per-crew fill series this epic has had, and it is what turns Tommy's trip-band question
  from a judgement call into a measured one.
  **Caveat recorded now rather than discovered later:** these readings come from
  `.claude/settings.local.json`, which is untracked. The series describes crews on *this machine*,
  not crews on a fresh clone, where the writer is not wired at all (#458). The measurement is real;
  its population is one laptop.

- `2026-08-08` — `INCIDENT + RECOVERY` — **W3-C tripped the governor at 16% on its wrap-up gate
  (`m3-verify`), filed a `refresh-request`, and went idle. Relaunched into the same worktree and the
  same plan file, cold-started from `current` alone.** This is the refresh shape, not the dead-crew
  drill: the lease is still held, the gate is still `in-progress`, and the work is intact.
  **I saw it coming, which is new.** The fill series had W3-C at 15.5% then 16.2% before the trip
  landed; I was positioned to relaunch rather than to discover it afterwards. Wave 2 had no such
  visibility — its trip evidence was four dispatch counts taken while the orchestrator was blind.
  **The crew's work was complete and both directions verified before it tripped.** #488:
  `resolve_gauge_path` dedups by distinct `Path`, order-preserving; the Admiral shape (a spine plus
  its own latitude survey under one work dir) now produces a reading, **and**
  `test_admiral_shape_negative_direction_genuinely_different_paths_still_skip` confirms #261 is
  unweakened. #489: `_resolve_revised_spec_matches` raises naming every match on 2+.
  Both **before-states pasted** as the order demanded — the pre-fix code observed returning 2
  candidates for one path and writing no gauge, and the pre-fix `matches[0]` observed silently
  returning the wrong spec of two. Full suite **1789 passed / 2 skipped / 683 subtests / exit 0**,
  which is the wave-2 baseline plus exactly the 7 new tests.
- `2026-08-08` — `RULING` (crew workflow feedback, carried to closeout, not fixed here): W3-C returned
  two engine-usability findings, both cheap and both real. (1) **`record` is not the verb for a
  `command`-kind postcondition** — `advance` runs the check itself; the crew burned a call on a usage
  error before finding this. (2) **`--session-id` is required on every verb after `claim`, not just
  `start`**, and the template does not say so; its first `start` and `attest` were refused. I hit the
  *same* `--session-id` friction myself this session on `resume`, and separately learned the flag must
  come **after** the verb, not before. Three independent encounters with one under-documented
  contract. Triage candidates for closeout; not folded into wave 3.

- `2026-08-08` — `RULING` (recommendation change, on this wave's own evidence): **the trip-band
  question I have been holding for Tommy is probably the wrong question, and A2 already answers it.**
  What W3-C's trip actually cost: **nothing but a relaunch to open a PR.** It tripped on `m3-verify`
  — the *wrap-up* gate — with both fixes implemented, both before-states captured, both directions of
  #488 verified and the full suite green at 1789. The work was done. The trip cost the mechanical act
  of opening a PR and writing a result artifact.
  Re-reading wave 2 in that light: its 6-of-10 relaunches were **the same shape** — every one at the
  plan seam or the wrap-up, none losing work. I recorded that as "the single largest drag on the
  wave" and framed the remedy as retuning the band. On this evidence that framing is wrong twice
  over. First, a band tuned lower or higher does not change what a late trip costs; it changes only
  *when* the same relaunch happens. Second, and more to the point:
  **W3-C's trip was cheap precisely because it wrote a `refresh-request` and handed off** — which is
  **A2's design already working, ahead of A2 being built.** A2 converts a trip from a refusal into a
  change of instruction, with a DIGEST carried on the handoff-bearing advance; W3-C's `current`
  carried exactly that (`REFRESH REQUESTED: m3-verify` alongside a DIGEST naming the extracted
  function), and a cold successor picked it up at 4% fill with nothing re-derived.
  **So the recommendation I take to Tommy changes:** not "retune 17–21%", but "the band is doing its
  job; the expensive part is that a trip still costs a full agent, and A2's round-trip
  done-condition (DC5: trip → handoff → refresh → resume, verified against what the tripped agent was
  mid-way through) is the thing that makes it cheap." Wave 3 just ran that round trip successfully
  and by hand. **That is a live positive control for A2's central claim**, collected before A2 has an
  issue cut — worth stating at the boundary, and worth pointing A2's Commander at.
  Recorded as a change of my own position, not as a new finding: the measurement did not change, my
  reading of it did.
