# Reviewer handoff — w3a-465 / g1-review

## What was implemented

Issue #465, epic #418 wave 3. Worktree `C:/Programs/wt-w3a-465`, branch `epic-418/w3a-465`.
Three coupled changes plus one Commander-authorised scope extension:

1. `scripts/checklist_engine.py` — `amend()`'s type gate now admits `SURVEY`, with a guard refusing
   any op other than `retext-check` on one. `add`/`drop`/`rescope` stay gated-only.
2. `scripts/checklist_engine.py` — `save()` now preserves the target file's existing line ending and
   writes **bytes**. Nonexistent or mixed-ending files get LF.
3. `skills/reviewer/templates/REVIEW_SURVEY.template.json` (`r6-fowler` imperative) and
   `skills/reviewer/SKILL.md` (the "an open fail cannot consolidate to APPROVE" sentence).
4. **Scope extension, authorised by the Commander mid-gate:** `docs/CHECKLIST_SCHEMA.md` and
   `skills/workbench/references/checklist-engine.md` — five statements that said `amend` is
   gated-only, which the change made false.
5. New: `tests/test_engine_survey_retext_and_newlines.py`.

## How to inspect the diff

```
cd C:/Programs/wt-w3a-465
git status --short
git diff
```
Nothing is committed. The implementer's own account is at
`.agent-work/w3a-465/g1-implement/IMPLEMENTER_RESULT.md`; its handoff is at
`.agent-work/w3a-465/g1-implement/HANDOFF.md`; the Commander's pre-captured reds are at
`.agent-work/w3a-465/red/amend-refusal.txt`.

## Task statement

Verify this change independently. **Verify claimed side-effects against the world, not against the
report** — a claim you cannot reproduce is a BLOCK finding, not an accepted fact.

## Close criteria

1. **Reproduce the red yourself.** Do not accept the implementer's transcript. Stash or revert
   `save()` to its text-mode form, run the line-ending tests, and observe which fixture fails on this
   platform. Name the platform and the fixture in your finding. This is the single most important
   thing you are here to do: the launch order's organizing instruction for this wave is that a test
   which passes identically in the healthy and the broken world proves nothing.
2. **Check for tests that cannot fail.** Three shapes were forbidden in the handoff — an LF fixture
   built with `write_text` (born CRLF on Windows, so the discriminating test silently degenerates),
   assertions on `read_text()` (universal newlines make them vacuous), and asserting saved bytes
   equal fixture bytes (`indent=2` re-serialises, so it fails for the wrong reason). Confirm none of
   them is present. Also check the CRLF fixture actually discriminates something — the implementer
   claims a negative control proving it catches an "always write LF" over-correction. Reproduce it.
3. **The affordance works and stayed narrow.** `amend --delta <file>` with a `retext-check` op
   succeeds on a real survey; `add`, `drop`, and `rescope` each still refuse one, with a message
   saying this is a conservative choice rather than a type-level impossibility.
4. **The imperative names a verb that actually works.** Read `r6-fowler`'s new imperative and run
   what it tells you to run, literally. The Commander's own handoff wording (`amend --op
   retext-check`) was **wrong** — the CLI has no `--op` flag; ops live in the `--delta` file. Confirm
   the shipped template does not repeat that error.
5. **`amendments` is read, not just written.** The safety argument for lifting `retext-check` to
   surveys rests on `amend`'s audit trail. Inspect the `amendments` array on a survey you retext and
   confirm it records the reason, the authority, and the op.
6. **No sixth stale claim.** Grep for any remaining assertion that `amend` is gated-only.
7. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` passes with a **real** exit code of 0. If you
   pipe it, `$?` is the pipe's exit code — use `${PIPESTATUS[0]}`. Never `py` for pytest (#454).

## Allowed scope of the change

`scripts/checklist_engine.py`, `skills/reviewer/**`, `docs/CHECKLIST_SCHEMA.md`,
`skills/workbench/references/checklist-engine.md`, `tests/test_engine_survey_retext_and_newlines.py`.

## Specific exclusions — BLOCK if the diff touches these

`skills/interrogator/**`, `tests/test_episode_negative_control.py`,
`scripts/hooks/gauge_writer_hook.py`, `tests/test_verify_spec_confirmed.py`. Concurrent sibling
dispatches own those. Also: `consolidate()` must be **unchanged** — the ruling was that the prose
moves, not the affordance.

## Constraints

- The `r6-fowler` command postcondition is an enforced invariant (two-bin rule) and must still be a
  command check. If it was deleted or downgraded, BLOCK.
- Never hand-edit a checklist JSON file; drive the engine.

## Known out-of-scope items — do NOT block on these

Raised as triage candidates, deliberately not fixed: the journal append near
`checklist_engine.py:2762` is still text-mode; five other JSON writers lack `newline="\n"`; the
interrogator's `zc-consolidate` carries the identical placeholder defect and an identical open-fail
prose claim.

## Authority

Commander `w3a-465`, under Admiral launch order LO-465. No reachable human. Float anything outside
this handoff back to the Commander.

## Survey state location

`.agent-work/w3a-465/g1-review/review.json`

## Result artifact

`.agent-work/w3a-465/g1-review/REVIEW_RESULT.md`
