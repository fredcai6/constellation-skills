# Regrade — `decision:existence-verified-resolution`

Recorded after the g2 reviewer's closing precision arrived. Its `settle:` condition was **THIS GATE**
(the two-arm live fire), so it must be regraded rather than left at `guess` — but **not** regraded
flatly, which is the point of this note.

## Ruling

**`@grade: measured` — for the GUESSED-RUNG PATH ONLY. Rungs 0-2 and the g1b disagreement refusal
stay `guess`.**

## What the live arms actually exercised

Exactly two rungs:

- **rung 4 (`git_worktree`) succeeding** — treatment bound the worktree spine with
  `path_source: "git_worktree"`.
- **rung 5 failing** — control fell through to the pre-fix cwd-relative resolution,
  `path_source: null`.

That is the whole of what the two-arm run measured. It is enough to settle the question the gate was
built to answer — *does a worktree-dispatched agent's reading land where the engine reads it* — and
that answer is yes, with a fired trip.

## What remains unmeasured, and must not be laundered by this regrade

- **Told-truth rungs 0-2** (explicit `--worktree`, `cd` target, and the payload-cwd rung when it is
  correct) — unit-tested only. The reviewer's own repro did exercise `cd_target` and the ambiguity
  guard, but **that evidence is the reviewer's, not the harness's**, and it is not re-runnable from
  the acceptance artifact.
- **The g1b disagreement refusal** (two guessed roots naming different existing files → refuse to
  bind) — unit-tested only. No live arm produced that collision.
- **g1-review's tc1 stands unmeasured**: when both main and the worktree hold a real checklist at the
  same relative path and the command carries no `cd` and no absolute `--worktree`, **rung 3 beats
  rung 4** and binds a confident wrong path labelled `payload_cwd`. That reviewer judged it
  non-blocking on evidence (not a regression; the measured 60/64 defect is fixed; it does not reach
  the live configuration). It is nonetheless a live sub-case this gate did **not** settle.

## Why the scoping is the substance of this note

The playbook carries `lesson:grading-a-contested-claim-settled-launders-it`. Writing `measured`
without the qualifier would do precisely that: it would let a two-rung result stand as if the whole
ladder had been proven, and tc1 is a concrete open sub-case that such a grade would bury. The honest
grade is narrow and says what it does not cover.

**Carried up to the Admiral** as part of the return; no separate issue filed, because tc1 is already
recorded in `crew/g1-review/review.json` and this note names it against the anchor.
