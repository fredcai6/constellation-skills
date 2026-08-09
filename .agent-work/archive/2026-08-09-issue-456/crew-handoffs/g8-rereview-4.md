# Reviewer Handoff — g8, attempt 4 (re-verification of the test-only remediation)

## Assigned gate
`g8` — two code defects split out of the old grab-bag (critic F10): (1) BOM-prefixed files rejected by `ast.parse`, and (2) D3, the wrapped-docstring summary/body split.

You have reviewed this gate three times. Attempts 1 and 2 found the production code wrong. Attempt 3 found the production code **right** and the tests **hollow**. This pass verifies only the repair to attempt 3's finding.

## What was implemented since your last pass

Two commits, **test-only**:

- `18dc643e` — "Fix hollow test assertions in docstring overflow tests"
- `8ad32efb` — "Remove conditional gate from invariant test assertions"

`git diff --stat 1f2b57ab 8ad32efb -- scripts/` is **empty**. `scripts/code_map/extract.py` and `scripts/code_map/render.py` are byte-identical to the `1f2b57ab` state you already verified as correct. The only source change is `tests/test_code_map.py` (+45/-27 across both commits, mixed with unrelated `.agent-work/` bookkeeping in the same range).

Your three recommendations from attempt 3 were adopted as written: the `if summary and len(summary) == 160:` gate removed, `len(summary) == 160` asserted unconditionally, the overflow text itself asserted present in `body`, and no production change.

## How to inspect

```
git diff 1f2b57ab..8ad32efb -- tests/test_code_map.py
git diff 1f2b57ab..8ad32efb -- scripts/
```

The second must be empty. If it is not, that alone is a finding — the remediation was scoped test-only.

## The task for this pass

**Re-run your own two mutations from attempt 3 and report whether each now bites.** These are the exact two you used to prove the tests hollow, so they are the only mutations that directly falsify or confirm the repair:

1. **Mutation 1** — revert the whole fix to the remediation-2 shape: the blank-line branch no longer preserves its own overflow (attempt-2's exact finding). Previously: all 11 selector tests green.
2. **Mutation 2 (surgical)** — keep the 160-char truncation but drop only the overflow from `body` (`body = post_blank_body`, discarding the prepended overflow). Previously: only the older remediation-2 test caught it, by accident; both blank-line-overflow tests stayed green.

For each: report the exact selector line, which test ids go RED, and confirm the revert is byte-clean. Use `git diff --quiet -- <path>` for the revert check, **not** `git status --porcelain` — this repo runs `core.autocrlf=true` with `text=auto` in `.gitattributes` and porcelain false-negatives on line-ending-only differences.

## What I already measured — do not take it on trust, but do not spend the pass reproducing it either

I ran a third mutation of my own, distinct from both of yours: replace `paragraph = paragraph[:160]` in `_first_paragraph` with `pass`, removing truncation entirely. Result: **4 tests RED**, including both of the two you named as hollow (`test_dense_paragraph_over_160_chars_no_blank_line` and `test_long_first_paragraph_with_blank_line_and_body`). The identical mutation left all 11 green before the repair. Revert byte-clean.

I also confirmed by grep that `if len(summary) == 160` now appears **zero** times in the test file, with three unconditional `assertEqual(len(summary), 160)` in its place.

**Reproducing a falsifier its author already ran proves only that the probe works.** My third mutation is mine; yours are yours. The value of this pass is that your two independent probes — designed before the fix existed, against a shape you chose — now bite. If you can find a fourth mutation neither of us picked that still slips through, that is the most useful thing you could return.

## Close criteria
- Both of your attempt-3 mutations turn the selector RED, with named failing tests.
- No production-code change in the range (`git diff 1f2b57ab..8ad32efb -- scripts/` empty).
- Full suite green: expect **1838 passed, 2 skipped, 701 subtests, 0 failed**.
- Selector `-k 'bom or docstring'`: expect **11 passed, 4 subtests** (gate baseline 4 subtests).
- `python scripts/code_map/build.py` then `python scripts/code_map/check.py`: 7/7, exit 0.

## Allowed scope
`tests/test_code_map.py` inspection and temporary mutation of `scripts/code_map/*.py` for probing, always reverted byte-clean. Read-only on everything else.

## Specific exclusions
- **Do not fix anything.** This is a verdict pass. If you find a defect, BLOCK and describe it; do not edit.
- Do not re-litigate the D3 definition, the alias-over-retire ruling from g7, or the summary-truncation design question — the last is already filed to triage as `tc1`.
- Do not touch `map/`, `.agent-work/`, or any file outside this worktree. `C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY corpora.
- The duplicated BOM-strip line you flagged as non-blocking in attempts 1–3 stays non-blocking; carry it forward unchanged rather than re-deriving it.

## Constraints
- stdlib-only.
- The full suite must be green at this gate boundary (critic F6).
- Never `git add -A` in this worktree — the untracked `map/` tree is staged deliberately at a later gate.

## Inbound map anchors
- structural: `scripts/code_map/` extractor
- structural: `tests/fixtures/` — BOM fixture
- capability: derive structure from source
- constraint: stdlib-only
- evidence: extraction correctness
- Map entry point: `map/INDEX.md`

## Evidence from IMPLEMENTER_RESULT
`.agent-work/issue-456/crew-handoffs/g8-remediate-4-RESULT.md` (engine artifact `e-g8-implement-1`), no unresolved blockers.

## Required evidence in your result
Named test ids going RED under each of your two mutations, the selector's exact tail line in each case, byte-clean revert confirmation per mutation, and the four close-criteria numbers re-run by you.

## Authority
Verdict authority: `APPROVE` or `BLOCK`, yours alone. No edit authority this pass.

## Return
Write `.agent-work/issue-456/crew-handoffs/g8-rereview-4-RESULT.md` — **exactly that path**; a result at any other path fails the Commander's close step. Return status `complete`.
