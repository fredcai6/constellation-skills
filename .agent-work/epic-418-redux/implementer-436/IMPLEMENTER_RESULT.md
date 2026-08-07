# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
Issue #436 — "Confirm worktree-precondition enumeration check catches a real second worktree-entering template" (epic #418, wave 2, `LO-436`)

## Completed slice
Proved `scripts/verify_worktree_precondition_coverage.py`'s enumeration loop actually discriminates a genuinely new second worktree-entering (template, gate) entry, not just the one entry it has always known — both as a live, reverted deliberate-breakage demo and as a permanent regression test — and closed the one real gap found (enumerated count missing from the failure-path output).

## Scope
**Files changed:**
- `scripts/verify_worktree_precondition_coverage.py` — failure path now states `N of M worktree-entering template(s) checked failed:` before listing offenders (was: bare list, no count)
- `tests/test_worktree_precondition_wiring.py` — added `EnumerationGeneralizesPastOneEntry` (two tests: refuses+names a genuinely new second entry without naming the known-good one; passes once that entry is fixed) and `EnumerationStatesCountOnFailure` (one test, the TDD-red test for the count fix)

**Specific exclusions touched:** no — did not touch `scripts/checklist_engine.py`, `episodes/`, `scripts/apply_episode_delta.py`, or `scripts/collect_feedback.py`.

## Behavior changed
Yes — `verify_coverage()`'s `CoverageError` message now leads with the enumerated-vs-failed count on every failure, not just implicitly via the problem list. No change to the discrimination logic itself; it was already correct (see Verdict below).

## Map Impact
- **Capabilities added/changed/affected:** the enumeration check's failure output now states its loop count (`N of M ... checked failed`), mirroring what the success path already stated (`M ... checked`) — closes the asymmetry pre-ruling decision:count-is-part-of-the-output flagged.
- **Claims/evidence produced:** `verify_coverage()`'s discrimination logic is now backed by a permanent test against a genuinely new (never-before-enumerated) second entry, not only the original single known entry — the falsification debt #436 named is closed with evidence, not just argued closed.
- **Triage candidates:** `WORKTREE_ENTERING_GATES` is still hand-maintained with exactly one *real* entry (Commander `init`); the first real second role dispatched into a worktree should reuse this issue's pattern when it lands, rather than re-deriving it.

## Test mode
**Required:** `test-first` (TDD) for the count fix; `evidence-only` for the discrimination proof (no code defect found there — see Verdict).
**Satisfied:** yes — red observed for the count fix (`assertIn("1 of 1 worktree-entering template", ...)` failing pre-fix, 4/5 other tests already green pre-fix), green after; the discrimination tests were evidence-only by design since the loop needed no fix.

## Evidence

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**Result:** pass — `1724 passed, 4 skipped, 643 subtests passed in 648.07s (0:10:48)`, exit 0. (LO-436 baseline at main `ca0e36a`: `1721 passed, 4 skipped, 643 subtests`, exit 0 — delta is exactly the 3 new tests added this wave, zero regressions.)

Live CLI demo (see notes-436.md for verbatim capture): refusal `1 of 2 worktree-entering template(s) checked failed: skills/scoutbot/templates/SCOUTBOT_SPINE.template.json: gate 'init' does not wire ... 'verify_worktree_isolation.py'`, exit 1 — reverted, re-run confirms `worktree-precondition coverage OK: 1 worktree-entering template(s) checked`, exit 0.

## TDD evidence, if required

- Failing test observed: `EnumerationStatesCountOnFailure::test_failure_output_states_enumerated_count` — `AssertionError: '1 of 1 worktree-entering template' not found in "worktree-precondition coverage FAILED:\n..."` (1 failed, 4 passed)
- Passing test observed: `tests/test_worktree_precondition_wiring.py`: `5 passed in 1.28s`
- Refactor while green: no — single minimal addition (a header line), no refactor needed

## Docs/contracts touched
- none — the module docstring's description of `WORKTREE_ENTERING_GATES` as hand-maintained is unchanged and still accurate; no `docs/agents/*` doctrine promoted (out of latitude per LO-436)

## Assumptions
- The order's phrase "genuinely new worktree-entering template" permits a throwaway fixture role (`scoutbot`), per LO-436's explicit latitude ("Yours to decide: how the new template is introduced; whether it lives as a test fixture or a scratch file"). Both a one-time live CLI demo (matching the order's evidence language literally) and a permanent in-process regression test (so the proof doesn't evaporate after this session) were produced — the live demo is the required evidence artifact; the permanent test is the durable code deliverable that keeps it proven going forward.

## Stop conditions hit
- none — issue was small and bounded as scoped; no decision outside latitude was needed

## Out-of-scope observations
- none beyond the one triage candidate above (hand-maintained list still has only one real entry)

## Workflow Feedback

- **Handoff gaps:** none — LO-436 was complete (task, prior-wave verdicts, pre-rulings with grades, latitude, fences, test command, budget, stop conditions, return shape all present).
- **Context rediscovered:** none — the existing `tests/test_worktree_precondition_wiring.py` and script docstring gave enough context to identify the exact gap (list has always had exactly 1 entry) without digging elsewhere.
- **Instructions improvised around:** the engine's `advance` verb, when the active gate's postcondition is a `command` check that legitimately runs long (the full suite, ~11 minutes), itself exceeds the Bash tool's 2-minute default and 10-minute max timeouts — because `advance` runs the check synchronously as part of the verb. Backgrounded the `advance` invocation itself (`nohup ... &`, poll for process death, then read the log) rather than the underlying test command, since the engine call was the thing running long, not just the test. `references/checklist-engine.md` doesn't currently name this pattern for a long-running command-check gate.
- **What would have made this easier:** a documented recipe (in `checklist-engine.md` or `windows.md`) for "advance whose command-check legitimately runs past tool timeouts — background the advance call itself."

## Return status
`complete`
