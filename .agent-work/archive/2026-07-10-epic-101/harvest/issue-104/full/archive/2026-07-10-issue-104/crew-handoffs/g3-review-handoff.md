# Reviewer Handoff

Concise. Paste, don't point.

## Gate
`g3-review` (issue #104, constellation-curator)

## What was implemented
`tests/test_curate_corpus.py` (new, untracked) — 18 tests over fixture corpora proving
each `curate_corpus.py` detector bites and that flags-never-gates holds. Implementer
report: `.agent-work/issue-104/crew-handoffs/g3-implement-result.md`.

## How to inspect
Worktree `C:\Programs\constellation-wt-104`. Read `tests/test_curate_corpus.py` and
`scripts/curate_corpus.py`. Reproduce the runs.

## Close criteria to verify (yes/no + reproduced evidence)
1. **Fixtures provably authentic (T6):** the planted DUPLICATION passages are the verbatim
   pre-#108 text from commit 2696769 — confirm by running
   `git show 2696769:skills/implementer/SKILL.md | grep "misfit is compliance"` etc. and
   matching the string constants in the test (COMPLIANCE_BOILERPLATE / EMPHATIC_BANNER /
   ENGINE_INVOCATION). Invented (non-authentic) duplication text = BLOCK.
2. **Every detector has a BITING assertion:** duplication, size, invoker (both directions),
   description (person-shortlist, when-to-use, exclusion for a confusable name), reference-
   TOC, parse. Confirm each has a test asserting the exact `flagged`/`shortlist`/`info`/`ok`
   status and check name.
3. **Flags-never-gates falsification is REAL and meaningful:** a maximally-flagged fixture
   asserts `main([...]) == 0` (not a comment). Confirm the fixture actually triggers every
   detector BEFORE asserting exit 0 (so it can't pass vacuously).
4. **Falsification spot-check (do this yourself):** temporarily break ONE detector in a
   throwaway COPY of curate_corpus.py (or monkeypatch a threshold) and confirm a golden
   assertion REDS — i.e. the tests actually depend on the tool's behavior, not tautologies.
   Do NOT leave the tool modified; describe what you did and revert. (If you prefer, flip
   one expected status string in a throwaway copy of the TEST and show it reds — either
   direction proves non-tautology.)
5. **Green:** `py -m pytest tests/test_curate_corpus.py -v` all pass; `py -m pytest tests/ -q`
   whole suite green.
6. **Scope:** only `tests/test_curate_corpus.py` added; `curate_corpus.py` and real skills
   untouched (`git status --short`).

## Verification commands
```bash
cd C:/Programs/constellation-wt-104
git show 2696769:skills/implementer/SKILL.md | grep -n "misfit is compliance"
py -m pytest tests/test_curate_corpus.py -v
py -m pytest tests/ -q
git status --short
```

## Suggested Model Tier
`simple bounded — reproduce + one non-tautology spot-check`

## Stop Conditions
Return BLOCK with the specific failing criterion + reproduction if any fails (esp. if a
"biting" test would still pass with the detector disabled — that is a tautology BLOCK).

## Return Format
Return REVIEW_RESULT with an explicit `verdict: APPROVE` or `verdict: BLOCK` token, the
per-criterion findings with reproduced evidence (including your non-tautology spot-check
and the revert), out-of-scope observations, workflow feedback. Keep it focused. WRITE the
full REVIEW_RESULT as your final message AND to the given result path before going idle.
