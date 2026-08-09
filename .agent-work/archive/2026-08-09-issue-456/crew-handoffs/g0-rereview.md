# Re-Review Handoff — gate `g0`, the remediation delta

Issue #456. The first `g0` review returned **BLOCK** on two findings. Both are
now fixed. **This is a scoped re-review of the delta only**, not a repeat of the
full review — that one passed all five close criteria and every constraint but
one, and its evidence stands.

## What to inspect

```bash
cd C:/Programs/constellation-skills/.claude/worktrees/issue-456
git diff b14ff3ff~1..HEAD -- scripts/ tests/
```

Two files, +191/-7: `scripts/code_map/render.py`, `tests/test_code_map.py`.

Read first:
- `.agent-work/issue-456/crew-handoffs/g0-review-RESULT.md` — findings B1, B2.
- `.agent-work/issue-456/crew-handoffs/g0-remediate-RESULT.md` — the fix.

## The two blockers and what was ruled

**B1 — pages carried a source position**, against the confirmed ruling *"nothing
committed carries a position"* (the disposition of SY1, a BLOCKING critic
finding). The human answered directly: **"strip the line numbers."** I ruled the
detail:

- **REMOVE** the `:<line>` — the cross-page churn SY1 measured (~450
  position-bearing lines rewritten per 3-line source edit).
- **KEEP** the bare file path — changes only when the file moves, so no churn.
- **KEEP** `, N lines` — an entity's size changes only its own page, which is
  correct behavior.

No position cache was built and none should be: `.code-map/statements.jsonl`
already carries per-statement `{file, line, col}` and is already gitignored.

Fix: `render.py:184`, `loc()`, whose only call site is `entity_page()`
(`render.py:274`).

**B2 — the page count could not go wrong.** `npages` counted `write_text()`
calls, so the report read 3636 against 3635 files on disk. Fix: `render.py:436`,
`npages = sum(1 for _ in out.rglob("*.md"))`, read off the tree after writing.

**Deliberately NOT fixed, do not raise as findings:** the `Verdict`/`verdict`
collision (filed `tc17`, assigned to `g1`; `g2` owns renaming) and the identical
`entity_pages` defect (filed `tc18`, also `g1`). After the fix the report
correctly reads 3635 **with the `Verdict` page still lost**. That is the intended
outcome.

## Evidence already reproduced — check it again, do not take it on trust

I reproduced all of this myself in a script that asserts each mutation applied
before running. Reproduce it independently and then look for what I did not.

| claim | figure |
|---|---|
| full suite, cleared environment | `1709 passed, 2 skipped, 0 failed` (boundary was 1706) |
| B1 mutated — line number put back | RED on `RenderedPageFormatTests::test_no_rendered_page_carries_a_source_line_number` |
| B2 mutated — write-call count restored | RED on `RenderReportTests::test_render_report_page_count_equals_the_files_on_disk` |
| restored | 17 passed, working tree byte-identical |
| entity-page headers carrying `.py:<line>` over the real corpus | **0** of 3522 |
| headers that kept the path / kept the size | 3522 / 3522 |
| `MUTATION PROBE` strings left in `render.py` | **0** |

## What I most want your eyes on

1. **Is there a THIRD sibling of the cannot-fail shape?** Two have now been found
   in the same function (`pages`, and `entity_pages` which is still open). Sweep
   `render.py`'s reported fields and the new tests for a count, flag, or
   assertion whose value is identical in the healthy and the defective world.
2. **Do the three new tests hold under a different mutation than the one they
   were built against?** A test tuned to exactly one probe can still be narrow.
   Try mutating a *neighbouring* behavior and see whether anything notices.
3. **Did stripping the position break anything that consumed it?** Grep for
   readers of the page header format — `checks.py`, any test, the module index.
4. **Is `, N lines` still correct after the change?** `loc()` no longer reads
   `e['line']` for the header, but the `end_line - line + 1` arithmetic that
   produces the size is unchanged. Confirm it is neither broken nor silently
   fixed — the line-base defect D1 belongs to `g3` and must survive intact.

## Constraints still binding

Stdlib only. No timings in any run report. Full suite green at the boundary
(`1709 / 2 / 0`). **Do NOT `git add -A`** — the untracked 3,635-page `map/` tree
is staged at `gs`, deliberately last; stage explicit paths.
`C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.

**Three environment traps, all confirmed real on this run:**
`FORCE_COLOR=3` is exported (pass `--color=no` whenever you intend to grep pytest
output); `PYTHONIOENCODING=utf-8:surrogateescape` is exported (clear it for an
honest suite number); and **use `python`, never `py`** — `py` has no pytest, so
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run. The third already reached three command postconditions in a crew's own plan
before it was caught.

## Return format

Write `REVIEW_RESULT` to
`.agent-work/issue-456/crew-handoffs/g0-rereview-RESULT.md`: verdict
(`APPROVE` / `BLOCK`), findings with severity and `file:line`, the evidence you
reproduced with real output, and anything out of scope worth filing.

**Return thin, write fat.** A `BLOCK` remains a welcome outcome — this is still
the first of eleven gates and everything downstream builds on it.
