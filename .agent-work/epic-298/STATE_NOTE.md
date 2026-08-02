# Crash-resume state note — epic-298

Rewrite this **before** launching any detached or multi-hour process, and again before **each** new detach. If this session dies, a fresh agent resumes from exactly this — no forensics.

> **Authoring rule, learned three times in this file:** this note is rewritten only at detach boundaries while the ADMIRAL_LOG is written as rulings happen, so the artifact read in a disaster goes stale fastest. **Carry pointers, never copies**, for anything another agent keeps writing to.

> **REBUILT 2026-08-02 after being destroyed.** `.agent-work/` was gitignored at `b69e6c8`; fast-forwarding local `main` to `4cec87a` (where #326 made it tracked) overwrote this file and `ADMIRAL_LOG.md` with main's wave-0 versions. The log was recovered (292 entries; scratchpad + session transcript) and **committed at `3595955`**. This note was rewritten from live state, not recovered. **Both files are TRACKED now, so a future clobber shows in `git status`.**

- **step:** `execute` · **9 of 12 issues CLOSED.** Remaining: **#307** (commander live), **#308** (commander live), **#310** (not started, final B2 gate), then `closeout`.
- **slug:** epic-298 · main checkout `C:/Programs/constellation-skills`, local `main` now **== `origin/main` (`4cec87a`)** plus the log-recovery commit.
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-298/spine.json current`
- **pid:** harness-tracked Agent dispatches, no OS pid. **LIVENESS = filesystem mtime under the worktree, never the engine heartbeat.**
- **expected artifact:** #307's paired evidence package (HITL — Tommy adjudicates); #308's consolidation + playbook retirement (HITL — Tommy rules the two-bin routing); then #310.

## Live worktrees

| path | branch | state |
|---|---|---|
| `../constellation-skills-wt/e298-307` | `epic-298/307` | **commander-307 LIVE** — POST measurement arm |
| `../constellation-skills-wt/e298-308` | `epic-298/308` | **commander-308 LIVE** — collation + playbook retirement |
| `../constellation-skills-wt/e298-305` | `epic-298/305` | **DONE, merged.** Trio verified byte-identical to main — **do NOT re-harvest.** `worktree remove` fails `Permission denied` (file lock); retry at closeout |
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
- **The context gauge has been SILENT the whole run (#383)** — subagents inherit the parent session_id, so every crew claim adds a binding (30+). **No warning is coming; watch your own context.**
- **A frozen gate imperative can be measured false by the work it authorises, with no supersede mechanism (#390).**

## Closeout obligations

Lessons audit with fresh context (brief at `LESSONS_RUN_BRIEF.md`, routing at `BACKLOG_ROUTING.md`) · epic retrospective in `.agent-work/AGENT_FEEDBACK.md` (**verify content, not exit code** — the invariant check now exits 0 regardless) · cartographer reconcile · `collect_feedback.py` dogfood sweep · **harvest before sweep** for 307/308 worktrees (**both** `staged-feedback/<id>/` and the worktree-root trio) · sweep `e298-305` · archive the log · epic summary for Tommy.

**ARCHIVE MECHANISM:** copy `.agent-work/epic-298/` into a fresh worktree off `origin/main` and open a PR. **Do not branch-checkout in the main checkout** — that is what destroyed this file.

_Updated: 2026-08-02T19:55:00Z_
