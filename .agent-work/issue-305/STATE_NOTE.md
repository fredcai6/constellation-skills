# Crash-resume state note — issue-305

- **step:** execute · gate **`g1-integrate` — HELD at a BLOCK verdict, waiting on an Admiral ruling**
- **slug:** issue-305 · branch `epic-298/305` · worktree `C:/Programs/constellation-skills-wt/e298-305` · base `967493c`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** none — foreground
- **expected artifact:** the Admiral's ruling on issue **#362** (packaging), then either a g1 rework dispatch or `advance g1-integrate`

**Everything is committed.** Latest: `epic-298/305` at the "scope the unskippability claim" commit. Nothing is at risk from a `git clean`.

## Engine leases

Spine + gate plan lease: **`commander-305-e298`** — pass `--session-id commander-305-e298` on every
mutating call against `spine.json`. (The gate plan `execute.json` has accepted calls without it.)
Spine: `.agent-work/issue-305/spine.json` · Gate plan: `.agent-work/issue-305/execute.json`.

**Drive the WORKTREE `scripts/checklist_engine.py`, never the installed copy.** This run modifies the
engine; mixing binaries is the hazard.

## Where the run actually is

`plan` is **complete and frozen** (4 crew gates). Spine is at `execute [in-progress]`.

- `g1-implement` — **complete.** Seam wired at `start()` and `reopen()`.
- `g1-review` — **complete.** Verdict **BLOCK**.
- `g1-integrate` — **HELD.** See below.
- `g2` / `g3` / `g4` — pending. `g2-implement` and `g2-review` were **amended** (`--authority admiral`)
  to carry the refusals ruling and the independent-mutation bar.

## Why g1-integrate is held — read this before doing anything

The reviewer returned **BLOCK** on two blockers. One is fixed; one needs a ruling.

**Blocker 1a — NOT FIXED, floated, filed as #362.** `install_constellation.SKILL_SCRIPT_BUNDLES` ships
`checklist_engine.py` to nine skills and `episode_capture.py`/`context_manifest.py` to **none**. The
engine's `except ImportError` no-op therefore runs in production, so **the seam is inert everywhere it
ships, silently**. Confirmed: the installed commander skill has the engine and neither sidecar.

Floated because it is production packaging **and** because `C:/Programs/constellation-skills` has
**uncommitted local changes to `scripts/install_constellation.py`** (Tommy's live work) — a real
collision. My recommendation to the Admiral: scope it in, add the two files to every engine-carrying
bundle, plus a test asserting the companion invariant.

**Blocker 1b — FIXED.** `record()` has no `in-progress` guard, so surveys consolidate from `pending`
and never emit. D1's argument is sound but scoped to gated spines; the module docstring overreached.
Corrected in `scripts/episode_capture.py` to state the real scope and name surveys as outside it.
Covering surveys is a survey-lifecycle design change — filed as **#359**, deliberately not done here.

## Rulings in force (do not reopen)

Seam is `start()`+`reopen()`, write-if-absent. `refusals` **is in scope** (additive only;
`docs/CHECKLIST_SCHEMA.md` in the same PR; prove the counter can be wrong *and* that the test can fail
on the specific assertion; state the #344 latency). **Mechanical snapshot, not auto-created episodes**;
`docs/EPISODE_STORE.md:781` is a defect to correct. #327 (`run.dirty`) stays in scope. Refuse, never
fabricate. Read `PLAN_CRITIC_DISPOSITION.md` **before** `CONVERGENCE.md` — the disposition wins.

## Two corrections to the record a successor should not re-derive

- **m3's "nothing else" postcondition was vacuous**: the check was `git diff --stat -- scripts/checklist_engine.py`,
  which exits 0 whatever the diff contains. It could not fail. The engine diff was verified by reading it.
- **The `reopen` plumbing justification was wrong.** `reopen` refuses anything not `complete`, and a
  complete gate necessarily passed `start`, so its manifest exists and write-if-absent returns early —
  **`reopen`'s emit is a no-op on every reachable production path.** The two lines stay (free, symmetric,
  and they do fire for a pre-#305 spine), but not for the reason originally given.

## Issues filed this run

**#362** packaging (the blocker) · **#359** surveys bypass the seam · **#360** phantom manifest
directories for sub-checklists · **#361** unguarded `work_id` in the path + duplicated place-and-write.

## Evidence standing

Full suite **1435 passed, 2 skipped, 410 subtests**, reproduced independently by me. Reviewer ran six
mutants (five outside the implementer's set), all killed. The seam dogfooded itself: `start g1-review`
emitted `.agent-work/issue-305/context/g1-review.json`.

**Branch status: PENDING.** Nothing pushed, no PR.

_Updated: 2026-08-02T03:05:00Z_
