# Implementer Handoff (relaunch — prior attempt-1 died mid-verification, work salvaged)

## Gate
g3 (g3-implement) — end-to-end red/green proof + regression backstop

## What already exists (verify, do not redo)
A prior attempt wrote `tests/test_code_map_precommit_e2e.py` (7 test methods covering all 8
numbered cases from the original handoff at
`.agent-work/w2-reindex/crew-handoffs/g3-implement-handoff.md` — read that file for the full case
specification, it is still the authoritative task description). That prior attempt died only
because it ended its own turn to "wait" for a backgrounded full local `pytest -q` run — the CLI
process exiting killed the background job with it, so no `IMPLEMENTER_RESULT` was ever written. It
did NOT die due to a defect in the test file itself: run `python -m pytest
tests/test_code_map_precommit_e2e.py -q` yourself first — it passes (7 passed, confirmed
independently before this relaunch). Read the original handoff's full case list, confirm the
existing file actually covers everything it specifies (do not just trust the file exists — check
each of the 8 numbered cases against it), then proceed to Close Criteria below.

## Your actual job in THIS relaunch
1. Confirm `tests/test_code_map_precommit_e2e.py` genuinely satisfies every numbered case in the
   original handoff (read both, cross-check). If a case is missing or wrong, fix it — do not
   assume completeness from the fact it exists and passes.
2. Run the full local `pytest -q` suite and the regression checks below.
3. Write the `IMPLEMENTER_RESULT`.

**Do this run of the full suite in the FOREGROUND, polling, never by backgrounding it and ending
your turn.** This is the exact failure that killed the prior attempt. Use this idiom (a single
foreground Bash call that does not return until the suite's own summary line lands):
```bash
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q > /tmp/suite.log 2>&1 &
until grep -qE '^[0-9]+ (passed|failed|error)' /tmp/suite.log; do sleep 15; done
tail -5 /tmp/suite.log
```
The `until` loop itself is the one foreground command your turn waits on. If your own tool harness
still reports this as backgrounded/asynchronous, that is fine — what matters is that YOU do not end
your turn before the loop above returns with the suite's summary line captured. Never end your turn
assuming a result will "come back automatically" — nothing resumes a headless CLI process once its
turn ends.

## Close Criteria
- Every scratch setup in the e2e test file uses `git worktree add` against **one shared scratch
  `.git`** — never `git clone`. Verify this directly by reading the file, not by trusting a
  docstring.
- `git diff -- tests/test_code_map.py` (this actual repo's working tree) is empty.
- Full local suite green at or above `3622 passed, 6 skipped, 0 failed` (base baseline) plus every
  test this plan added across gates 1-3 (gate 1's `test_code_map_precommit.py`, gate 2's
  `GitPreCommitHookWiringTests`, this gate's `test_code_map_precommit_e2e.py`).

## Allowed Scope
`tests/` only — `tests/test_code_map_precommit_e2e.py` specifically (already exists; edit it only
if a case is genuinely missing or wrong, per step 1 above). No production code changes.

## Specific Exclusions
Do not modify `scripts/code_map/`, `scripts/hooks/`, or `scripts/install_constellation.py` — gates
1-2's code is already approved. If a real defect surfaces in that shipped code during your
verification, STOP and return `blocked` with concrete evidence rather than patching it here.

## Required Evidence
```bash
python -m pytest tests/test_code_map_precommit_e2e.py -q
python -m pytest -q     # via the foreground nohup+until idiom above, not a bare backgrounded call
git diff -- tests/test_code_map.py
```
State the exact commit SHA the red-proof (case 1) ran against, and the pass/skip/fail counts
against the `3622 passed, 6 skipped, 0 failed` baseline.

## Suggested Model Tier
stronger — reason: verifying real subprocess git orchestration across multiple scratch worktrees
and confirming the full-suite result correctly (not just launching and hoping) rewards care.

## Stop Conditions
Stop and return if: the existing e2e test file has a genuine gap you cannot close within Allowed
Scope, required evidence cannot be produced, a real defect surfaces in gates 1-2's shipped code, or
a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT to
`.agent-work/w2-reindex/crew-handoffs/g3-implement-implementer-result.md` before ending your turn.
That write is the delivery — do not end your turn believing a background process will produce it
for you.
