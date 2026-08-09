# Reviewer Handoff

## Gate
g1 (execute.json, work-id issue-458-readiness)

## What Was Implemented
A readiness-check mode added to `scripts/install_constellation.py`: four independent, testable
check functions plus a thin CLI/report layer exposed via a `--check-readiness` flag. It answers
"is this project set up to run Constellation" and refuses (nonzero exit, named per-item reason)
without ever repairing anything or writing `settings.json`.

## How To Inspect The Diff
```bash
cd C:/Programs/constellation-skills-wt/epic418-w5-readiness
git diff scripts/install_constellation.py tests/test_install_constellation.py
```
Only these two files should be touched. The implementer's full IMPLEMENTER_RESULT (files changed,
assumptions, evidence) is at
`.agent-work/issue-458-readiness/crew-handoffs/g1-implement-result.json`.

## Task Statement
Verify the readiness-check mode is correct, reports rather than repairs, never touches
`settings.json`, and is genuinely testable/tested — not that it merely exists.

## Close Criteria
- Four separately-callable check functions exist: engine-runnable (via `sys.executable`, not a
  bare `python`/`py`), skills-installed-and-registered, hooks-wired-in-a-file-that-ships
  (project scope = git-tracked via `git ls-files`, distinct from user scope's
  "is this the file actually read at runtime"), work-area-present (`.git` at root).
- CLI layer reports and refuses (nonzero exit, named reason) on any failing item; exits 0 only
  when all four pass; never writes `settings.json` under any code path, including error paths.
- Engine-runnable check correctly distinguishes "interpreter missing" / "interpreter present but
  no pytest" / "both present and working" — this is the load-bearing distinction the whole gate
  exists to get right (the python-vs-py false-negative case).
- New tests actually exercise each of the four functions independently, plus the CLI mode's
  exit-code/refusal behavior, plus a constructed-unready case for the two environment-scoped
  items (1 and 3).
- No regression in the existing test file.

## Allowed Scope (for your own inspection/verification actions)
Read-only inspection of `scripts/install_constellation.py`, `tests/test_install_constellation.py`,
and running the test suite. Do not edit source; if you find something that needs a fix, that is a
BLOCK finding, not something you patch yourself.

## Specific Exclusions
`scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — out of scope for this gate
entirely (crew 4 owns them this wave); their presence or absence in the diff is itself a check
(they must NOT appear).

## Map Anchors (inbound, from g1-implement)
DEGRADED-NO-MAP repo — substitute is `README.md` ("Repo layout vs. installed layout", "Install",
"Baseline Assumptions"). Constraints: Pre-Ruling 2 (settings.json never touched, any scope, not
overridable) and Pre-Ruling 3 (must be run against a fresh clone and observed to refuse for real,
not overridable — that observation happens at `g1-integrate`, after your review, so you are not
the one producing it, but flag if the code as written looks like it could not actually refuse on
a real fresh clone). Decision: Pre-Ruling 1 resolves toward building the CHECK — do not flag "this
should also wire the hooks" as a finding, that is explicitly declined this run.

## Evidence From IMPLEMENTER_RESULT
See `.agent-work/issue-458-readiness/crew-handoffs/g1-implement-result.json` in full. Headline
claims to independently re-verify, not trust: 25/25 new readiness tests pass; 132/132 full file
passes (380 subtests); `git check-ignore` exits 1 on both edited files (tracked, not ignored);
wiring grep shows real call sites outside each new symbol's own definition/self-test.

## Required Evidence (from you)
- Re-run `python -m pytest tests/test_install_constellation.py -k readiness -q` and
  `python -m pytest tests/test_install_constellation.py -q` yourself; quote the actual output,
  not a restatement of the implementer's claim.
- Confirm `settings.json` does not appear anywhere in the diff and is never written by any new
  code path (read the new functions, don't just grep the diff for the string).
- Confirm the `--agent`/`--scope` decision the implementer made (required for the readiness mode)
  is stated and reasoned in IMPLEMENTER_RESULT, not silently assumed.
- A Fowler code-smell / refactoring pass over the new code, per your own skill's standard scope.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK, findings list, evidence reproduced) as this
gate's `review-result` evidence via the checklist engine's `attach` verb on `g1-review`
(`--type review-result --field verdict=<APPROVE|BLOCK> ...`), or hand the JSON back to your
dispatcher to attach if you cannot reach the engine directly — state which you did.
