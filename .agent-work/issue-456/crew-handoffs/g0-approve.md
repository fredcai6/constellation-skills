# Review Handoff — gate `g0`, closing pass (verdict required)

Issue #456. This is the **third** review pass at `g0` and the last one. Your job
is to return a verdict — **APPROVE** or **BLOCK** — on gate `g0` as a whole. The
gate cannot close without an APPROVE on the record, and you are the only one who
can put it there. Do not soften a BLOCK to be helpful, and do not withhold an
APPROVE to be safe. Say what is true.

## What `g0` was

Put the code-map prototype behind a real entrypoint: a package, a CLI that runs
`extract -> render` end to end on this repo, and a discovery layer that
enumerates exactly the mappable corpus with `.agent-work/` excluded, asserted by
a test that fails if the exclusion is removed. The bundling question (vendored
here vs. shipped from a skill) had to be **resolved on the record, not deferred**.

## What has already happened — do not redo any of it

Two prior review passes, three findings, all three closed:

| id | finding | closed by |
|---|---|---|
| **B1** | entity-page headers carried a source line number that `D1` already proves is off | human ruling *"strip the line numbers"*; header now `path, N lines` |
| **B2** | the render report's `pages` counted `write_text()` calls, so a silently-lost page was invisible in it | `render.py:436` now counts the tree |
| **B3** | **the B2 fix RELOCATED the tautology** — a count of the tree is tautologically true of that tree, so it still cannot fail | docstring at `tests/test_code_map.py:127` rewritten to state honestly what the test guards |

Prior artifacts, read them rather than re-deriving:
`crew-handoffs/g0-review-RESULT.md`, `crew-handoffs/g0-remediate-RESULT.md`,
`crew-handoffs/g0-rereview-RESULT.md`.

## The one thing NOBODY has reviewed

**B3's fix was written by the Commander, not by a crew, and no reviewer has ever
looked at it.** That is the specific gap you are here to close. It is commit
`853be2bc` — a docstring, nothing else.

Read it at `tests/test_code_map.py:127`. It must be **true**, **specific**, and
**not misleading to the next reader**. Concretely, judge:

1. Does it correctly say the test guards the counting **method** and is a real
   regression guard (restore the write-call counter → RED)?
2. Does it correctly say the count **cannot detect a lost page**, and not imply
   otherwise anywhere?
3. Does it point the next reader at where the check that *can* fail lives?
4. **Is any sentence in it false?** Verify the claims, do not read them
   charitably. In particular it asserts three mutations leave the suite GREEN
   (delete every second entity page; never write a module `INDEX.md`; write every
   page flat into `map/`). **Check at least one of those yourself by actually
   running it**, on a byte-exact-restore harness, and report which one and what
   you saw.

## Attack it — this is the standing lesson of this gate

The Commander accepted a bad fix **twice** at `g0` by reproducing the falsifier
the crew itself had designed. Reproducing a probe its author chose only proves
that probe works. So:

- **Attack every check `g0` ships with a mutation its author did NOT choose.**
- If you find a fourth cannot-fail sibling, that is a **BLOCK**, and it is exactly
  what this pass is for.

## Also confirm, by command not by reading

- The full suite in a **cleared environment**: expected `1709 passed, 2 skipped,
  0 failed`. If your number differs, that is the headline of your report.
- `python -m pytest tests/test_code_map.py -k "discovery or cli" -q` — expected
  `14 passed`.
- The `.agent-work/` exclusion test genuinely fails when the exclusion is removed
  (mutate it, don't trust the name).
- **The bundling question is resolved on the record.** Find where, quote it, and
  say whether it is a resolution or a deferral wearing a resolution's clothes. If
  it was deferred, that is a BLOCK — it was an explicit gate requirement.

## Explicitly NOT yours

- **Do NOT add the `pages - 1 - modules` vs `entity_pages` invariant.** It is the
  real falsifiable check (3535 vs 3536, differing by exactly the lost
  `Verdict`/`verdict` page), it would be **RED today** because the page really is
  lost, and `g2` owns the rename that fixes it. It is assigned to `g1` with
  `tc17`. Noting that it is still absent is fine; adding it is not.
- **Do NOT "fix" `entity_pages`** — `g1`, per `tc18` as corrected by `tc24` (the
  root is `sizes`, which feeds three fields, and counting the tree again is NOT
  the fix).
- **Do NOT change `scripts/code_map/render.py`.** `g0` closes without one, by
  ruling.
- No scope widening into `g1`–`gs`. Log anything else as an out-of-scope
  candidate in your report.

## Constraints

- Stdlib only. No timings in any run report.
- **Do NOT `git add -A`.** The untracked 3,635-page `map/` tree is staged at `gs`,
  deliberately last. Stage explicit paths only.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- **Three environment traps, all confirmed real on this run.** `FORCE_COLOR=3` is
  exported — pass `--color=no` whenever you intend to grep pytest output.
  `PYTHONIOENCODING=utf-8:surrogateescape` is exported — clear it for an honest
  suite number. And **use `python`, never `py`** — `py` has no pytest, so
  `py -m pytest` dies with "No module named pytest" and reads as a silently green
  run. That third one already reached three command postconditions in another
  crew's plan before it was caught.
- Restore anything you mutate, byte-exact, and prove you did (`git status` clean
  on `scripts/` and `tests/` at the end).

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g0-approve-RESULT.md`. First line must be
the verdict, alone: `VERDICT: APPROVE` or `VERDICT: BLOCK`. Then: the mutation
you ran and what you saw, the suite numbers, your judgement on the B3 docstring
clause by clause, the bundling-question quote, and any out-of-scope candidates.

**Return thin, write fat.**
