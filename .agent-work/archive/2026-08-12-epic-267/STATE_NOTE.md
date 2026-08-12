# Crash-resume state note — epic-267

Rewritten before each detached wave launch. If this session dies, a fresh agent
resumes from exactly these five lines — no forensics.

- **step:** `execute` · **wave 2 batch 2: #262 DONE-BUT-UNMERGED, #264 still implementing** · **PR #293 is reviewed, green, harvested and CLEARED — the merge command itself was refused by the permission classifier and is waiting on Fred. Do NOT re-review it; do NOT route around the refusal.** · epic-267
- **slug:** `epic-267` · work area `.agent-work/epic-267/` · commander branches `governor/*` · one isolated worktree per Commander
- **next command:** `py scripts/checklist_engine.py --file .agent-work/epic-267/spine.json current --session-id admiral-epic-267` — then read `.agent-work/epic-267/ADMIRAL_LOG.md` bottom-up for the last logged wave launch, and `.agent-work/epic-267/crew-handoffs/` for launch orders and any landed findings.
- **pid:** none — Commanders run as Agent-tool subagents, tracked by the harness, not by OS PID. A dead session loses the notification channel but not the Commander's worktree, branch, or PR; recover by listing `git worktree list` and `gh pr list --head 'governor/*'`.
- **expected artifact:** two PRs off `b69e6c8` — `governor/262-install-wire-hooks` and `governor/264-e2e-assertion`. On green + review: merge sequentially, harvest each closeout trio **from the worktree before sweeping**, then this epic is dispositioned and goes to closeout.

## PICK UP HERE

**Batch 1 is COMPLETE and fully swept.** #269 (`e3f6a5c`), #268 (`d6d25a6`), #265 (`b69e6c8`) — all
merged, harvested, swept. `main` is at `b69e6c8`.

**Do NOT re-harvest batch 1.** Deltas for #269, #268 and #265 are all applied (**tick -> run 37**,
16 lessons active against a cap of 20). Re-applying double-counts.

**Both open decisions are CLOSED — Fred ruled 2026-07-28.** Nothing is blocked on him right now.
1. **#269 part 3 — affirmed: hook code pins to the main checkout.** Anti-tamper doctrine. Affirms current
   behaviour, so no code change was required. #269 is closed.
2. **Batch-2 scope change — DECLINED for this wave, deferred.** Wave 2 stays exactly #262 + #264. The
   proposal (subagent measurement / self-report) is filed as **#284** so it survives this epic.

**Batch 2 is dispatched and running.** Do not dispatch anything else. If you are a fresh session picking
this up, your job is to **adjudicate returns**, not to start work.

## PR #293 (#262) — CLEARED, NOT MERGED. The only thing standing between it and `main` is Fred.

Everything a merge needs is done. **Do not redo any of it.**

- CI **green** (`SUCCESS`); whole repo **1199 passed / 2 skipped** vs 1164 at base.
- Fred's inviolable constraint **independently verified in the worktree**: 32 wiring tests pass; the
  write path (`install_constellation.py:775-830`) bails out on `dry_run` *after* every refusal and
  *before* any write, refuses an unparseable/non-object `settings.json` instead of repairing it, and
  will not create the file without `--wire-hooks`.
- Its disclosed **self-reviewed** post-APPROVE fix is covered: the reviewer's own `%MYTOOLS%` repro is
  the test oracle (`:1882`), `UNDETERMINABLE` beats both confident verdicts (`:1891`, `:1904`).
- **Closeout trio already harvested** to `.agent-work/harvest-267/governor-262/`. Do NOT re-harvest.
- `notes-262.md` posted to issue #262 and never entered git history (#278 fix worked, 2nd time).

**The blocker:** `gh pr merge 293 --squash --delete-branch` was refused by the Claude Code auto-mode
permission classifier — not CI, not review. Escalated to Fred, deliberately **not** routed around.
Same classifier previously refused `git push origin --delete` on merged branches; also not routed
around. If you are resuming and Fred has since approved, just run the merge and proceed to sweep.

**Commander `governor-262` has finished and released its lease.** Do not message it to resume it.

## Live rulings a fresh Admiral must not re-derive (2026-07-28, post-compaction)

**Fred's calibration — the bands are speed bumps, not walls.** HARD refuses `advance` only until a
`refresh-request` exists, then proceeds (`checklist_engine.py:1305-1329`). The goal is catching
yourself, not stopping. I misread it as a refusal band this run and stopped work over it. Do not repeat.

**Fred's design constraint — the reading is PUSHED by the engine on tool use, never PULLED by the
agent.** Any proposal where the agent decides to measure itself is the wrong shape: a context-degraded
agent is the least likely to remember to pull. My #284 "self-report" framing was backwards and is
corrected on the issue.

**The gauge's measurement never failed — its ADDRESSING did.** `gauge_writer_hook.py:434/457` already
computes fill from `transcript_path` on the hook payload; hand-measuring is that same writer run
manually. `resolve_gauge_path` (`:439-448`) asks the binding *where to write*, gets N answers, cannot
choose, fans out sidecars. **#271 + #286 + #287 are one root cause, and it is addressing.**

**The context window does NOT drive the trip verdict — only the displayed percentage.** Verified in
source: `_PROFILES` (`gauge_reader.py:72-85`) holds **absolute** caps in tokens; `thresholds_for`
(`:129-130`) divides by the reader's window; `fill` divides by the writer's. Equal windows cancel, so
`fill >= hard` reduces to `tokens >= hard_cap`. A wrong window corrupts what a human reads, nothing
else. (#252 predates the absolute-cap refactor — that is why it could scale the trip *then*.)

**RULING to governor-264 — render implied tokens AND the model's window, never the cap:**
`CONTEXT 70% (~139,750 of 1,000,000 tokens on claude-opus-5)`. The cap adds no detection value and
would teach the wall-misreading fleet-wide; the window is a model capability fact and would have caught
#252 on sight. Reader computes `fill x reader_window` — its own *interpretation*, which is precisely
what makes writer/reader divergence visible. Pinned-at-clamp was **dropped**: silent at `0.69875` and
`0.126658`, and fires 6.7x too late (clamp at 1,000,000 vs hard at 150,000).

**Open recommendation to Fred, not started:** more push = let the hook speak (PostToolUse
`additionalContext` reaching the model directly, unasked, non-blocking). `additionalContext` is
**unprobed on this harness** — ten-minute check. Must stay advisory; exit-2-with-stderr also reaches
the model but blocks the turn and breaks `decision:fail-open-is-inviolable`.

## Waves — status

| Wave | Issue | Outcome |
|---|---|---|
| 1 | #261 bind on resume | **merged** PR #273 (`2c169a5`), closed |
| 1 | #202 binding single-slot | **merged** same PR, closed with evidence |
| 1 | #258 (unrelated, pre-existing) | merged `2af00d8` |
| 2 | #269 worktree hook isolation | **merged** PR #276 (`e3f6a5c`), harvested, swept, **closed** |
| 2 | #268 dead template path | **merged** PR #279 (`d6d25a6`), harvested, swept |
| 2 | #265 make non-reading visible | **merged** PR #283 (`b69e6c8`), harvested, swept |
| 2 | #262 install + opt-in wiring | **DISPATCHED** — `governor-262`, design-it-twice panel required |
| 2 | #264 end-to-end assertion | **DISPATCHED** — `governor-264` |

Base commit for both batch-2 dispatches: `b69e6c8`.

## Expect the gauge to go blind — this is known, measured, and not a new bug

**Dispatching a Commander blinds the Admiral's gauge (#271).** A subagent inherits the parent
`session_id` (#263); its hooks resolve state paths to the main checkout (#269/#275); a phantom second
spine appears under the Admiral's binding key; the writer cannot choose and fails open. Measured twice —
once by falsifiable prediction — with the gauge dying ~31 seconds after dispatch and staying dead 15–26
minutes.

**One instance failed stale-LOW** (displayed `0.126658`, true fill `0.134497`, cap `0.15`). So a
comfortable number during a dispatch is not evidence of comfort.

**If the gauge stops moving mid-wave:** check `.spine-rail-binding.json` for extra spines under this
session's id *before* believing the number. Removing a phantom entry and re-driving the same writer
restored it last time. #265 (`b69e6c8`) now writes a `gauge-skip.json` sidecar for exactly this cause, so
the ambiguity should at least be **visible** this wave — that is worth checking as a live test of #265.

Backup of the pre-repair state: `.agent-work/harvest-267/governor-269/binding-BEFORE-repair.json`.

## Process fixes now in force — carried into both batch-2 launch orders

1. **Notes** go to `notes-<issue>.md` at the worktree root, get posted as an issue comment, then get
   `git rm`'d in the Commander's final commit. (Fixes #278; worked first try on #279.)
2. **Lesson ids are bare** — no `lesson:` prefix; the validator rejects the colon and the delta is
   all-or-nothing (#277).
3. **Closeout trio is explicitly UNCOMMITTED**, harvested from the worktree. The old "on your PR branch"
   wording was ambiguous and cost a round-trip on #283. Both new orders spell out repo-artifacts vs
   harvest-artifacts.
4. **New this batch:** both orders tell the Commander that its own absent gauge is expected (no writer in
   a worktree) and must not be read as evidence. #262 additionally carries an explicit overload escape
   hatch — the design panel recommendation alone is an acceptable complete deliverable.

## Hygiene / not-done

- Merged remote branches (`governor/261-bind-on-resume`, and the 269/268/265 branches) may still exist on
  origin. `git push origin --delete` was refused by the auto-mode classifier and was not routed around.
- `notes-261.md` and `notes-269.md` are permanently in `main` — launch-order template defect, filed as
  **#278**, cleanup deliberately deferred until the convention is decided.

## Carried to closeout

- **Recurrence-debt: 2 constellation lessons, 2 unfixed recurrences**, plus
  `verify-harness-field-and-drive-real-writer` now at **5 confirmations**. Five is well past the signal to
  stop confirming and fix upstream.
- **Playbook is at 16 active against a cap of 20** — closer than the recurrence-debt discussion assumes.
- My owned over-reach on #263's honest null — a null needs a stated *search* boundary, not just a stated
  *test* boundary. Lesson candidate.
- The `block --authority commander-269` misuse (no `awaiting-subordinate` state exists) — filed to #270.
- Epic-tier `CONSTELLATION_FEEDBACK.md` export decision for the shared-session-id / shared-transcript
  cross-write mechanism.
- The explorer-spine no-shelve-path doctrine gap (carried in from the `explore-shared-understanding` shelve).
- Engine CLI inconsistencies observed this run: `--file` must precede the verb; `--session-id` follows it;
  `block` takes `--blocker` while `resume` takes `--reason`; `current` rejects `--session-id`;
  **`resume` requires the step id as a positional** (`resume execute --reason ...`).
- **#277** — the lessons-delta validator rejects the id format the playbook itself displays.
- **#284** — the deferred subagent-measurement work, with the open caveat that **crew tier has never
  actually been measured**; whoever picks it up should probe before building.
- **#285** — recurrence-debt PAID during this wave. Graduation of
  `verify-harness-field-and-drive-real-writer` (5 confirmations vs a fix-upstream-at-4 doctrine) into a
  testing-conventions doc + the launch-order template. Also records the playbook at **16/20 active**.
- **#286** — found live this wave. #265's skip sidecar is written correctly but **never surfaced for the
  first 30 minutes**, because the advisory is only consulted when the reader returns `None` and
  `DEFAULT_MAX_AGE` is 30 min. #271's own 26-minute incident sits inside that window. Must be fixable
  **without** touching `DEFAULT_MAX_AGE` — that would be a threshold change, ruled out of this epic.

## Spinoff ledger — every issue this epic created, with its intended disposition

Postcondition c1 covers the **in-scope five**. These are spinoffs; none is in scope, and closeout needs a
one-line "deferred with ruling" on each rather than a fresh triage. Pre-written so closeout is mechanical.

| # | What | Intended disposition |
|---|---|---|
| #270 | Stop rail can't tell an Admiral awaiting a Commander from an abandoned run | defer — hit live, no `awaiting-subordinate` state exists |
| #271 | Orchestrator ungauged for the duration of every wave it dispatches | defer — **root mechanism**, reproduced 3x, now self-reporting via #265 |
| #274 | Let a tier retire and relaunch an overloaded subordinate | defer — capability; trigger half blocked on #284 |
| #275 | Hook state-paths cross-write to the main checkout despite real git isolation | defer — confirmed in the wild this wave |
| #277 | Lessons-delta validator rejects the id format the playbook displays | defer — cheap, hit by 3 Commanders |
| #278 | Launch-order convention leaves notes as permanent repo-root files | **needs Fred** — convention call; `notes-261.md`/`notes-269.md` cleanup waits on it |
| #284 | Subagents run unmeasured; crew tier never measured at all | **deferred by Fred to a future wave**, 2026-07-28 |
| #285 | Graduate `verify-harness-field-and-drive-real-writer` (5 confirmations) | defer — recurrence-debt, paid as a filing |
| #286 | Skip sidecar ignored while a frozen reading is inside the 30-min window | defer — must be fixed **without** touching `DEFAULT_MAX_AGE` |
| #287 | #265's fan-out materializes phantom work-area dirs in the main checkout | defer — erodes the #271 diagnostic |
| #288 | Anti-tamper covers hook **code**, not hook **wiring** — an agent can unregister its own judge | **needs Fred** — qualifies the ruling he made 2026-07-28; filed undecided, three directions named, no fix proposed |
| #289 | An inert governor is silence **without** a sidecar — the commonest failure is the one nothing detects | defer — real coverage hole in this epic; found by 264's cold critic, filed on my order rather than routed into #262's frozen gates. Relates #256/#262. |
| #290 | 12 of 19 skills lack an `invoker:` tag — pre-existing, and **masked** by the very defect #262 fixes | defer — filed by commander-262 |
| #291 | Three detector reporting-fidelity gaps surfaced at review | defer — filed by commander-262 |
| #292 | Installer refusal tests assert only non-zero exit, which argparse satisfies without the guard | defer — filed by commander-262; same vacuous-gate family as the `-k` finding |
| #294 | `SendMessage` won't route to the name launch orders assign (`governor-*` vs `commander-*`) | defer — **5 rediscoveries in one wave, 0 filings**, including mine. Cheap fix or a template line. |

Evidence also banked on two out-of-scope issues rather than filed new: **#266** (Trip has now fired on a
correct reading, twice, with two honest limits) and **#263** (closed — answered, carrying the owned
over-reach in its disposition).

## Read your own gauge as a FLOOR for the rest of this wave

The gauge froze at `0.101668` ~80 seconds after dispatch and will stay frozen until both Commanders
finish. Per #286 the engine will keep reporting that frozen number as if live for 30 minutes, with no
flag. Check `.agent-work/epic-267/gauge-skip.json` — if it exists and is newer than `gauge.json`, the
number is stale regardless of what `current` says. It exists right now.

**Correction, measured twice on 2026-07-28: a frozen reading is not a lower bound. It is uncorrelated.**
Same displayed `0.101668` read true `0.171281` (HARD) before a compaction and `0.065391` (below SOFT)
eight minutes after — the error flipped sign with no change in the displayed value.

**Measure by hand instead of guessing.** One command, works during a blind window, no new machinery:
sum `input_tokens + cache_read_input_tokens + cache_creation_input_tokens + output_tokens` from the last
`usage` record in `C:/Users/fredc/.claude/projects/C--Programs-constellation-skills/<session-id>.jsonl`,
divide by the 1M window. Proven twice this wave. This is #284's proposal, already working.

_Updated: 2026-07-28T04:45:00Z — Fred's rulings landed, batch 2 (#262 + #264) dispatched_
