# Launch Order: `impl-w5-docs` — two documentation corrections (#496 + #411)

Epic #418, wave 5 (the final wave). **Implementer-with-plan.** Small, deliberately carved out.

## Mission

Two documentation defects, each a correction against a named authority.

| Issue | Defect |
|---|---|
| **#496** | `docs/CREW_CONTEXT.md`'s **always-pass-newline** rule does not name `save()`'s **byte-faithful exception**, so a reader following the rule literally would break `save()`. |
| **#411** | `docs/TREND_SNAPSHOT.md` §2 lists `_shared` as a **20th role**. The installer says it is not a skill. **The error is built to propagate to every successor** that reads the snapshot as ground truth. |

**Read both bodies before planning** — `gh issue view <n> --json body`. The table above is titles plus
my reading of them, and I have not verified the details of either against source.

## Why this is its own crew

**Purely to prevent a file collision.** Crew 4 is the sole writer of `scripts/checklist_engine.py`
and `tests/test_checklist_engine.py` this wave, and #496 is *about* `save()`, which lives there.
Your job is the **documentation** correction; if you conclude the code also needs changing, that is a
**float to the Admiral**, not an edit.

## Pre-Rulings

1. **NOT OVERRIDABLE — you do not write `scripts/checklist_engine.py` or
   `tests/test_checklist_engine.py`.** Crew 4 owns both. #496 is a doc fix even though its subject is
   code.
2. **Correct against the authority, not against your reading of it.** For #411, the authority is the
   installer's own behaviour — run it or read it, and quote what it actually says about `_shared`.
   For #496, the authority is `save()`'s actual bytes-handling. **Quote the source in your return.**
3. **#411 says the error is built to propagate.** A fix that corrects the count but leaves the
   propagation path intact fixes one instance of a recurring defect. Say whether anything stops it
   recurring — and if nothing does, say that plainly rather than implying the fix is complete.
4. **Do not expand scope into a docs sweep.** Two issues. If you find a third, file or report it.

## Honest-Null Clause

**A measured negative is a complete deliverable.** If either issue turns out not to hold against
source, say so with the quote and close it as refuted. That is a good outcome, not a failure.

## Inherited Latitude

You may: edit the two documents; add or adjust any check that guards them; open and push your PR;
comment on and close both issues. You may **not**: touch any file another crew owns; edit
`skills/<role>/references/global-*.md` (install-time copies that `install_constellation.py`
regenerates — the canonical source is `skills/_shared/global-*.md`); or promote an observation into
`docs/agents/*` doctrine.

## File Ownership

**Yours alone this wave:** `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md`.

**Explicitly not yours:** `scripts/checklist_engine.py`, `tests/test_checklist_engine.py`,
`docs/CHECKLIST_SCHEMA.md` (crew 4); `scripts/verify_iterative_role_artifacts.py`,
`COMMANDER_SPINE.template.json` (crew 1); `scripts/install_constellation.py` (crew 2); crew handoff
templates (crew 3).

Working notes: `notes-1.md`. **Never `findings-1.md`** — the harness `Write` tool refuses that basename.

## Workspace

- **Worktree:** `C:/Programs/constellation-skills-wt/epic418-w5-docs` — **provisioned and verified.**
- **Branch:** `epic-418/w5-docs`, based on `ea854471`.

## Inherited Context

- Epic #418's central finding is **a check that cannot fail** — a signal identical in the healthy and
  the defective world. #411 is a documentation instance: a snapshot that is wrong and that nothing
  checks, read by every successor as ground truth.
- **NEVER read an exit code from a piped command.** `cmd | head` reports `head`'s exit.

## Budget

- **Model tier: Sonnet.** Two single-point corrections.

## Stop Conditions

Stop and float if: either fix needs a file you do not own; either issue fails to hold against source
(report it refuted, do not invent a fix); or #496's correction turns out to require a code change.

## Return Shape

Per issue: **fixed / refuted / blocked**, with **the source quote you corrected against**. For #411,
whether anything now stops the error propagating — and say plainly if nothing does. PR number.
Anything you did not do.
