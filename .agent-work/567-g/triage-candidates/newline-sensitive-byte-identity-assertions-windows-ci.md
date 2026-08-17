# Triage Recommendation: byte-identical assertions are newline-sensitive on Windows CI (issue #495 family)

## Classification
`bug`

## Source checklist/artifact
- Admiral's CI adjudication on PR #622 (Windows CI run, `windows-latest`), Group 2 of 3 reported regressions

## Structural anchor
`tests/test_spine_lifecycle.py` — `_raw_engine_cli`, `TestAdvanceAndRelease::test_violating_unmet_postcondition_passes_the_refusal_through_unchanged`, `TestAdvanceAndReleaseHardBand::test_the_refusal_is_byte_identical_to_the_engines_own`

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** Two tests assert `result["refusal"] == expected`, where `result["refusal"]` comes from an in-process capture (`_engine_call`, an `io.StringIO`, never touching a platform pipe) and `expected` comes from `_raw_engine_cli` (a real `subprocess.run(..., text=True)` call). On Windows CI, the subprocess's output picks up CRLF at the OS/CRT layer that the in-process capture never introduces, so two strings that print identically compare unequal.
- **Expected:** A "byte-identical to the engine's own refusal" assertion should measure textual content, not line-ending convention — the intent is "did the engine actually say this," not "does this platform's pipe agree with `io.StringIO` on `\r\n` vs `\n`."
- **Conditions:** `windows-latest` CI runner only; the identical assertion passes on Linux, where the discrepancy cannot arise (Linux subprocess pipes never introduce CRLF).
- **Type:** `measured` — reproduced directly from the Windows CI run's failure log for PR #622: `AssertionError: assert 'RAIL: This c...e the engine.' == 'RAIL: This c...e the engine.'` (identical-looking strings, unequal).
- **Rev:** `feat/567-g-closeout-lease` at the commit PR #622's Windows CI ran against (pre-fix); fixed in a later commit on the same branch (`_raw_engine_cli` now returns `.replace("\r\n", "\n")`).

## Possible fix
Already applied in this lane's own scope: `_raw_engine_cli` normalizes `\r\n` to `\n` before returning, so both call sites are fixed at the single source rather than needing two separate normalize-before-compare edits. The open question for triage is **whether this same class of gap exists elsewhere** in the repo — any other byte-identical or exact-string assertion that compares a subprocess-captured value against an in-process-captured (or hand-written) one is a candidate for the identical failure, and would only surface on a non-Linux CI runner, exactly as this one did.

## Open questions
- Is there a repo-wide convention or helper (e.g. a `normalize_output()` utility) that test authors should reach for by default when comparing subprocess output, so this doesn't have to be independently rediscovered per test file? Referenced by the Admiral as part of issue #495's family (repo JSON writers/comparisons passing encoding discipline but not newline discipline) — worth checking whether #495's own scope already covers this test-assertion variant or whether it's a distinct, adjacent gap.

## Recommended priority
`medium`

**Reason:** Non-blocking once fixed (this lane's own two occurrences are resolved), but the failure mode is invisible on Linux and only surfaces on Windows CI — exactly the kind of gap that recurs silently until a non-Linux runner exists to catch it, per the Admiral's own framing.

## Related artifacts
- `tests/test_spine_lifecycle.py` — `_raw_engine_cli` (the fix)
- PR #622 Windows CI run: https://github.com/fredcai6/constellation-skills/actions/runs/32005631083

## Disposition
`recommend-and-defer`

**Detail:** filing authority per `decision:no-issue-filing` — this lane files no issues; recorded here for the Admiral's disposal. The repo-wide sweep (checking for the same gap elsewhere) is out of this lane's scope.

## Issue creation authority
`ask user`
