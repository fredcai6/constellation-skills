# g8 Remediate-4 RESULT

## Gate
`g8` (issue #456): fix hollow test assertions

## Status
**PASSED** — Tests now properly guard the overflow preservation invariant

## Evidence

### Test Selector Baseline
- **Before fix:** 11 tests (all passed)
- **After fix:** 11 tests (all passed)
- **Selector:** `-k 'bom or docstring'`

### Mutation Testing
The tests now properly fail when overflow preservation is broken:

**Mutation: Disable truncation** (comment out summary truncation)
Applied to invariant test with corrected assertions (no gate):
- Shape 3 ("no blank line with overflow"): **FAILED**
  - AssertionError: 226 != 160 (summary not truncated)
- Shape 4 ("blank line with first-para overflow"): **FAILED**
  - AssertionError: 225 != 160 (summary not truncated)

The unconditional assertions now properly fail when truncation is disabled, proving the gate is gone.

### Full Suite
- **Baseline:** 1838 passed, 2 skipped, 701 subtests, 0 failed
- **After fix:** 1838 passed, 2 skipped, 701 subtests, 0 failed
- Duration: 9:46 (586.23s)

### Map Content
- **Build:** Succeeded, no errors
- **Check:** Passed, no errors
- **Git diff:** No changes to map/ (as expected for test-only fix)

## What Changed
Only `tests/test_code_map.py`:

1. **test_long_first_paragraph_with_blank_line_and_body**
   - Removed `if summary and len(summary) == 160:` guard
   - Assert `len(summary) == 160` unconditionally
   - Assert `"character truncation limit"` (overflow text) is in body

2. **test_all_shapes_preserve_complete_content** (Invariant test)
   - **Removed the conditional gate** — was `if len(summary) == 160:` (branch on measurement)
   - **Now branch on SHAPE** — `if description in ("no blank line with overflow", "blank line with first-para overflow"):`
   - For overflow shapes, assert `len(summary) == 160` **unconditionally**
   - Assert overflow text is present in body **unconditionally** for each overflow shape
   - Non-overflow shapes skip the 160-char assertions entirely
   - Extended Shape 3 and 4 test cases to definitely exceed 160 chars

## Key Fix
The distinction: **gates ask "did this happen?" and stay silent when false. Assertions say "this must happen" and fail when it doesn't.** The original test had a gate wearing an assertion's comment. Now assertions branch on known shape (input), not measured length (output).

## Commits
- `18dc643e`: "Fix hollow test assertions in docstring overflow tests" (first pass)
- `8ad32efb`: "Remove conditional gate from invariant test assertions" (corrected fix)
- Files: `tests/test_code_map.py`

## Verdict
The tests now properly guard the invariant: **no docstring content is ever dropped**. The production code (`scripts/code_map/extract.py` _first_paragraph function) remains correct and unmodified.
