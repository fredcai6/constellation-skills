# Crash-resume state note — epic-298

Rewrite this **before** launching any detached or multi-hour process, and again before **each** new detach. If this session dies, a fresh agent resumes from exactly this — no forensics.

> **Authoring rule, learned three times in this file:** this note is rewritten only at detach boundaries while the ADMIRAL_LOG is written as rulings happen, so the artifact read in a disaster goes stale fastest. **Carry pointers, never copies**, for anything another agent keeps writing to.

> **REBUILT 2026-08-02 after being destroyed.** `.agent-work/` was gitignored at `b69e6c8`; fast-forwarding local `main` to `4cec87a` (where #326 made it tracked) overwrote this file and `ADMIRAL_LOG.md` with main's wave-0 versions. The log was recovered (292 entries; scratchpad + session transcript) and **committed at `3595955`**. This note was rewritten from live state, not recovered. **Both files are TRACKED now, so a future clobber shows in `git status`.**

- **step:** `execute` · **10 of 12 issues CLOSED.** Remaining: **#308** (commander-308b LIVE at g5, migration verified done), **#310** (not started; **launch order written and committed**), then `closeout`.

**#307 CLOSED — Tommy ruled PASS (`cfa2c40`).** `map_before_src` **PRE-B 0/4 → POST 4/4** (per task, first map/first source: #690 36/23→17/25 · #688 27/23→21/37 · #698 57/25→29/46 · #704 23/7→19/22 · #716 a literal row in both arms). **`read_at_bootstrap` 0/4 in BOTH arms** — first map reads land at calls 17/21/29/19 because the spine runs `init` before `context`; **"map-first" as delivered means FIRST-AMONG-CONTENT, not first-among-actions**, and Tommy accepted that as the win ("before source was intent"). **Limitation stated first:** manipulation was `74953936`→`3595955`, **8 days and +31 files, not #304 alone** — containment proven, exclusivity not. Record: `post/POST_RECORD.md`.

**CARRY INTO #310 (filed to the issue 2026-08-02):** #304's result is **evidence for B2's fragment thesis** — the map contract lives *only* in per-task spine imperatives (`context` 2210ch/9 mentions, `plan` 3393ch/11) and **`skills/commander/SKILL.md` has ZERO** occurrences; per-task delivery moved a number that always-loaded delivery could not. **Bounds:** it measures *placement*, not *decomposition*, and the commander is already split on the **mode** axis (`1e8043a`/#107), which is a different axis from B2's content split.
- **slug:** epic-298 · main checkout `C:/Programs/constellation-skills`, local `main` at **`cfa2c40`**.
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-298/spine.json current`
- **pid:** harness-tracked Agent dispatches, no OS pid. **LIVENESS = filesystem mtime under the worktree, never the engine heartbeat.**
- **expected artifact:** #307's paired evidence package (HITL — Tommy adjudicates); #308's consolidation + playbook retirement (HITL — Tommy rules the two-bin routing); then #310.

## Live worktrees

| path | branch | state |
|---|---|---|
| ~~`e298-307`~~ | — | **SWEPT.** PR #398 merged `19667a3d`; #307 closed PASS. |
| `../constellation-skills-wt/e298-308` | `epic-298/308` | **commander-308b LIVE** — at g5, 3 commits (`e33b933`). **Liveness confirmed by mtime, NOT by the engine heartbeat, which read 42 min stale while the spine was 18 s fresh.** |
| ~~`e298-305`~~ | — | **SWEPT.** The earlier `Permission denied` had already unregistered it; `prune` finished the job. **Its two stranded commits were recovered via PR #391, merged `8ab0173e` — `scripts/prove_docstring_only.py` is on `main`, verified.** |
| `governor-262`, `governor-264` | — | stale, from abandoned epic-267. **Not mine to sweep** |

## Tommy's WIP — AWAITING HIS CALL

**Preserved at `f704273` on branch `wip/clean-codebase`.** Was uncommitted working-tree state in the main checkout; committed there before the fast-forward so it is a real ref rather than loose state. Contents: the `clean-codebase` skill (`SKILL.md`, `references/`, `templates/`), its two bundle keys in `install_constellation.py`, the `SKILL_INDEX.md` row, the `test_write_a_skill.py` delta. **Open question with him: land it as a PR, or leave it parked?** Prior assessment: complete, suite-green, rail-clearing; its review died mid-run at r6 (7/12 passed, zero blockers, lease never released).

## Standing authority from Tommy

- **Corpus re-installs: PRE-CLEARED**, no escalation. *"Clear for any other future re-installs, do it when its convenient for us."* **Install ONLY — never `--wire-hooks`; `settings.json` is his (#180).**
- **Updating local `main`: authorized.**
- Latitude contract: merges / issue filing / fix-now-triage / model tiers delegated. Two-bin rulings, pathway verdicts, design convergences and scope changes **escalate**.

**Corpus installed at user scope from `4cec87a`** — `sha256:7ed370bd…`. Fingerprints: `.agent-work/epic-298/baselines/CORPUS_FINGERPRINT_{PRE,POST}_INSTALL.json` (those pin the earlier `9a0cb17` install).

## Rules earned this epic — carry into EVERY dispatch

- **Sort by what survives your death: PUSH → FILE → gates → PR.** Unpushed commits and unfiled findings do not survive; engine state does. Three commanders died on #305; **only committed, pushed, or filed work reached me.**
- **Issue filing is REQUIRED, not permitted** (LAUNCH_ORDER-305:92). Framing it as permission invites weighing it.
- **Bind PER-BLOB, never per-tree** — `.agent-work/` commits change the tree without touching a source blob.
- **Pin every number in prose to a revision AND the PR number** — this repo squash-merges, so SHAs vanish from `main`.
- **Assert against behaviour, never against text describing behaviour.**
- **Any guard or comparison that loops must assert what it looped over.** I committed this defect **four times in one day** — install delta, governor root cause, harvest check, and the fast-forward that destroyed this file. Each reported clean without enumerating the interesting items.
- **A null that cannot discriminate is not a result.** The honest-null clause protects a *measured* negative, never an *unattributable* one.
- **The context gauge has been SILENT the whole run (#383)** — subagents inherit the parent session_id, so every crew claim adds a binding. **Now 35 for this session** (was 30 when filed — it grows per dispatch). `gauge.json` last written `2026-08-01T05:36`. **The #265/#283 announce-blindness fix DOES fire** — `current` prints a distinct silent-gauge line — so reporting works and reading does not. **No number is coming; watch your own context.**
- **#390, corrected 2026-08-02 — the earlier framing was too broad.** Plans **are** editable: `amend` carries `add`/`drop`/`rescope`/`retext-check`, journaled, authority-ratified; 308b used it. The real gap is one line wide: **`imperative` is assigned only in the `add` op (engine:1937), so no op edits an EXISTING task's imperative** — a clause of a gate's rationale measured false by the gate itself cannot be superseded without dropping the task and losing its attestations.

## Closeout obligations

Lessons audit with fresh context (brief at `LESSONS_RUN_BRIEF.md`, routing at `BACKLOG_ROUTING.md`) · epic retrospective in `.agent-work/AGENT_FEEDBACK.md` (**verify content, not exit code** — the invariant check now exits 0 regardless) · cartographer reconcile · `collect_feedback.py` dogfood sweep · **harvest before sweep** for 307/308 worktrees (**both** `staged-feedback/<id>/` and the worktree-root trio) · sweep `e298-305` · archive the log · epic summary for Tommy.

**ARCHIVE MECHANISM:** copy `.agent-work/epic-298/` into a fresh worktree off `origin/main` and open a PR. **Do not branch-checkout in the main checkout** — that is what destroyed this file.

_Updated: 2026-08-02T21:20:00Z_
