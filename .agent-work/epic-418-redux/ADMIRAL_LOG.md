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

## Merges

- _none yet_

## Closeout

- _pending_
