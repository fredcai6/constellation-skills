# Triage Recommendation: subprocess-output comparisons decode with the wrong encoding on Windows CI (issue #495 family)

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
- **What's wrong:** Two tests assert `result["refusal"] == expected`, where `result["refusal"]` comes from an in-process capture (`_engine_call`, an `io.StringIO`) and `expected` comes from `_raw_engine_cli` (a real `subprocess.run(..., text=True)` call with no `encoding=` argument). On Windows CI, `subprocess.run(text=True)` with no explicit `encoding=` decodes the child's stdout/stderr bytes using `locale.getpreferredencoding(False)` — a non-UTF-8 codepage (cp1252) on that runner — so a real UTF-8 em-dash (`—`, U+2014; `checklist_engine.py`'s rail text uses it throughout) comes back mis-decoded as mojibake (`â€”`). `PYTHONIOENCODING=utf-8`, set in the child's env, only governs how the CHILD encodes its own writes; it has no effect on how THIS process decodes the bytes it reads back.
- **First diagnosis was wrong, and it is worth recording why:** this observation originally guessed "CRLF vs LF" (a plausible-looking, but incorrect, explanation for two visually-identical strings comparing unequal) and shipped a `\r\n`-normalization fix that did not touch the actual failure — confirmed by re-running Windows CI: the fix left both tests red, with the SAME error. Reading the full pytest diff (not just the truncated summary line) showed the real difference (`â€”` vs `—`), which is a textbook UTF-8-decoded-as-cp1252 signature, not a line-ending one. Corrected by adding `encoding="utf-8"` to the `subprocess.run` call; both tests then pass on the re-run CI. The `\r\n`-normalization is kept (harmless, and a genuine newline difference is a real possibility elsewhere) but was never the actual fix for this specific pair.
- **Expected:** A "byte-identical to the engine's own refusal" assertion should measure textual content the way the engine actually produced it, not be sensitive to which codepage the reading process's locale happens to default to.
- **Conditions:** `windows-latest` CI runner only; the identical assertion passes on Linux, where the default locale encoding is already UTF-8.
- **Type:** `measured` — reproduced directly from two separate Windows CI runs for PR #622: the first showed `assert 'RAIL: This c...e the engine.' == 'RAIL: This c...e the engine.'` with a truncated diff; the second (after the newline-only fix) showed the full diff `-  the JSON â€” use the engine. / +  the JSON — use the engine.`, which is what corrected the diagnosis.
- **Rev:** `feat/567-g-closeout-lease`; wrong fix at one commit, corrected fix at a later commit on the same branch (`_raw_engine_cli` now passes `encoding="utf-8"` to `subprocess.run`).

## Possible fix
Already applied in this lane's own scope. The open question for triage is **whether this same class of gap exists elsewhere** in the repo — any `subprocess.run(..., text=True)` call with no explicit `encoding=` that later compares its output against text containing a non-ASCII character (em-dashes are common in this repo's own rail/doctrine prose) is a candidate for the identical failure, and — as this lane's own experience shows twice over — the wrong-looking fix (newline normalization) can look plausible and still be wrong; only a real non-Linux CI run exposes which one it actually is.

## Open questions
- Is there a repo-wide convention or helper that test authors should reach for by default when capturing subprocess output for comparison (`encoding="utf-8"` always explicit, never left to `locale.getpreferredencoding()`)? Referenced by the Admiral as part of issue #495's family (repo JSON writers/comparisons passing encoding discipline but not newline discipline) — this instance turned out to be encoding discipline specifically, not newline discipline; worth checking whether #495's own scope already names this exact `subprocess.run` pattern or whether it is a distinct, adjacent gap.

## Recommended priority
`medium`

**Reason:** Non-blocking once fixed (this lane's own two occurrences are resolved and CI-confirmed), but the failure mode is invisible on Linux, only surfaces on Windows CI, and — as demonstrated here — is easy to misdiagnose as a newline issue on first read of a truncated pytest diff.

## Related artifacts
- `tests/test_spine_lifecycle.py` — `_raw_engine_cli` (the fix)
- PR #622 Windows CI runs: https://github.com/fredcai6/constellation-skills/actions/runs/32005631083 (first, wrong-fix-still-red), https://github.com/fredcai6/constellation-skills/actions/runs/32007870194 (second, corrected-fix-confirmed)

## Disposition
`recommend-and-defer`

**Detail:** filing authority per `decision:no-issue-filing` — this lane files no issues; recorded here for the Admiral's disposal. The repo-wide sweep (checking for the same gap elsewhere) is out of this lane's scope.

## Issue creation authority
`ask user`
