# Closing Handoff — gate `g0`, finding B3

Issue #456. The `g0` re-review returned BLOCK on one finding, **B3**. This is the
last thing standing between `g0` and closed. It is small. Read all of it anyway —
the reasoning is the point, and getting the reasoning wrong here re-ships the
defect.

Full finding: `.agent-work/issue-456/crew-handoffs/g0-rereview-RESULT.md`,
section B3.

## What is wrong

`tests/test_code_map.py:127-131` carries a docstring that says, in substance:

> `pages` in the render report has to be a number that can be **WRONG**.
> Counting `write_text()` calls cannot be wrong … The count has to come from
> the tree.

**The middle clause is true. The first and last are false**, and they are false
in the one gate whose entire subject is checks that cannot fail.

`render.py:436` now computes `npages = sum(1 for _ in out.rglob("*.md"))`. That
is a count *of the tree it describes*, so it is tautologically true of that tree
and can reveal nothing about it. Coming from the tree is exactly what makes it
unable to be wrong. The re-reviewer proved this by mutation rather than by
reading — each of these leaves **all 17 tests green**:

| mutation | the defective world it creates |
|---|---|
| delete every second entity page right after writing it | 25% of the tree gone |
| never write any module `INDEX.md` | 112 pages, the whole navigation layer, gone |
| write every entity page flat into `map/` | the documented layout destroyed |

The test stays green through all three because it computes its expected value
with **the same `rglob("*.md")` expression as the implementation under test**
(`tests/test_code_map.py:142` against `render.py:436`).

## Your task — one docstring, nothing else

Rewrite that docstring so it states **honestly and specifically** what the test
actually guards: the counting **method**. It is a real regression guard — restore
the write-call counter and it goes red — and it is nothing more than that. It
does **not** detect a lost page, and it must stop claiming to.

Say plainly, in the docstring, that a count derived from the tree cannot detect
anything about that tree, and name where the check that *can* fail lives (below).
The next reader must not re-derive this.

## Explicitly NOT yours — read this twice

- **Do NOT change `scripts/code_map/render.py`.** The Commander ruled `g0` closes
  without a `render.py` change. Counting the tree stays for now.
- **Do NOT add the invariant assertion to `g0`.** The falsifiable check already
  exists in the artifact and nothing asserts it: `pages - 1 - modules` = **3535**
  against `entity_pages` = **3536**, contradicting itself by exactly the lost
  `Verdict` page. It is real, and **it would be RED the moment you asserted it**,
  because the page genuinely is lost and `g2` owns the rename that fixes it. It
  is assigned to `g1` together with `tc17`. Reference it in your docstring; do
  not implement it.
- **Do NOT "fix" `entity_pages`.** Same reason — `g1`, per `tc18` as corrected by
  `tc24`.
- No other defect fixes, no schema changes.

## Constraints

- Stdlib only. No timings in any run report.
- **Full suite green at the boundary: `1709 passed, 2 skipped, 0 failed.`** Your
  change is a docstring, so this number must not move at all. If it does, stop
  and say so.
- **Do NOT `git add -A`.** The untracked 3,635-page `map/` tree is staged at `gs`,
  deliberately last. Stage explicit paths.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.
- **Three environment traps, all confirmed real on this run.** `FORCE_COLOR=3` is
  exported — pass `--color=no` whenever you intend to grep pytest output.
  `PYTHONIOENCODING=utf-8:surrogateescape` is exported — clear it for an honest
  suite number. And **use `python`, never `py`** — `py` has no pytest, so
  `py -m pytest` dies with "No module named pytest" and reads as a silently green
  run. That third one already reached three command postconditions in another
  crew's plan before it was caught.

## Return format

Write `IMPLEMENTER_RESULT` to
`.agent-work/issue-456/crew-handoffs/g0-close-RESULT.md`: the old and new
docstring text, the full-suite number, and anything you found that I did not ask
about. Commit with **explicit paths** before you finish.

**Return thin, write fat.**
